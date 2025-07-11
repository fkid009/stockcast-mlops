# ──────────────────── dags/predict_stock_price_dag.py ────────────────────
from datetime import datetime, timedelta
import json, logging, numpy as np, pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from path import ProjectPath

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s",
)

ENGINE    = create_engine(ProjectPath.DB_URI)
PRED_DIR  = ProjectPath.DATA_DIR / "predictions"
PRED_DIR.mkdir(parents=True, exist_ok=True)


def predict():
    """모델로드 → 오늘 데이터로 1‑step 예측 → DB + CSV 저장"""
    with open(ProjectPath.MODELS_DIR / "latest" / "best_model_meta.json") as f:
        meta = json.load(f)

    X_inf = np.load(ProjectPath.PROCESSED_DATA_DIR / "X_inf.npy")

    if meta["type"] == "ridge":
        import joblib
        model = joblib.load(ProjectPath.MODELS_DIR / "latest" / "best_model.pkl")
        pred = model.predict(X_inf)
    else:  # xgb
        import xgboost as xgb
        bst = xgb.Booster()
        bst.load_model(ProjectPath.MODELS_DIR / "latest" / "best_model.json")
        pred = bst.predict(xgb.DMatrix(X_inf))

    price_pred = float(pred[0])
    logging.info(f"[PREDICT] AAPL next‑day close = {price_pred:.2f}")

    today = datetime.utcnow().date().isoformat()
    out = pd.DataFrame(
        [{"date": today, "ticker": "AAPL",
          "pred_close": price_pred, "model": meta['type']}]
    )

    out.to_sql("stock_pred", ENGINE, if_exists="append", index=False)
    csv_path = PRED_DIR / f"pred_{today}.csv"
    out.to_csv(csv_path, index=False)
    logging.info(f"[PREDICT] Saved → {csv_path}")


default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

with DAG(
    dag_id="predict_stock_price_dag",
    default_args=default_args,
    schedule_interval=None,          # 트리거 전용
    catchup=False,
    tags=["stockcast", "predict"],
) as dag:
    PythonOperator(
        task_id="daily_predict",
        python_callable=predict,
    )
