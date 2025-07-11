# ────────────────────────  dags/predict_stock_price_dag.py  ─────────────────────
from datetime import datetime, timedelta
import json, logging, numpy as np, pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from path import ProjectPath

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s"
)

ENGINE = create_engine(ProjectPath.DB_URI)
PRED_DIR = ProjectPath.DATA_DIR / "predictions"
PRED_DIR.mkdir(parents=True, exist_ok=True)

def predict():
    # ── ① 모델 로드 ───────────────────────────────
    with open(ProjectPath.MODELS_DIR / "latest/best_model_meta.json") as f:
        meta = json.load(f)

    if meta["type"] == "ridge":
        import joblib
        model = joblib.load(ProjectPath.MODELS_DIR / "latest/best_model.pkl")
        pred  = model.predict(np.load(ProjectPath.PROCESSED_DATA_DIR / "X_inf.npy"))
    else:       # xgb
        import xgboost as xgb
        bst  = xgb.Booster()
        bst.load_model(ProjectPath.MODELS_DIR / "latest/best_model.json")
        Xinf = np.load(ProjectPath.PROCESSED_DATA_DIR / "X_inf.npy")
        pred = bst.predict(xgb.DMatrix(Xinf))

    price_pred = float(pred[0])
    logging.info(f"📈 Prediction for AAPL next close = {price_pred:.2f}")

    # ── ② DB or CSV 저장 ──────────────────────────
    ts  = datetime.utcnow().date().isoformat()
    out = pd.DataFrame([{"date": ts, "ticker": "AAPL",
                        "pred_close": price_pred, "model": meta["type"]}])
    out.to_sql("stock_pred", ENGINE, if_exists="append", index=False)

    csv_path = PRED_DIR / f"pred_{ts}.csv"
    out.to_csv(csv_path, index=False)
    logging.info(f"✔ Saved prediction to {csv_path}")

# ── Airflow DAG ───────────────────────────────────────────────────────
default_args = {
    "owner": "airflow",
    "start_date": datetime(2023,1,1),
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
}

with DAG(
    "predict_stock_price_dag",
    default_args=default_args,
    schedule_interval=None,            # 필요 시 '@daily'
    catchup=False,
    tags=["stockcast","predict"],
) as dag:
    PythonOperator(
        task_id="daily_predict",
        python_callable=predict
    )
