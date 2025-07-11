# ────────────────────────  dags/evaluate_prediction_dag.py  ─────────────────────
"""
매일 예측 결과와 실제 종가를 비교‑평가하여 stock_pred_eval 테이블에 저장합니다.

● 선행 DAG : predict_stock_price_dag
   - 예측 DAG 이 성공적으로 종료된 뒤 trigger(권장) or @daily(독립 스케줄)
● 주요 로직
   1) stock_pred  (예측값) 에서 오늘 날짜의 row 로드
   2) stock_price (실제값) 에서 동일 날짜 row 로드
   3) 두 값을 비교해 절대오차 / RMSE 등을 계산
   4) 결과를 stock_pred_eval 테이블에 upsert
"""

from datetime import datetime, timedelta
import logging
import pandas as pd
from sqlalchemy import create_engine, text

from airflow import DAG
from airflow.operators.python import PythonOperator

# ─────────── 프로젝트 전역 경로 & DB URI
from path import ProjectPath

ENGINE = create_engine(ProjectPath.DB_URI)          # postgres 연결
TABLE_PRED   = "stock_pred"
TABLE_PRICE  = "stock_price"
TABLE_EVAL   = "stock_pred_eval"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s"
)

# ──────────────────────────────── Core Logic ──────────────────────────────────
def evaluate_prediction(exec_date: str = None) -> None:
    """
    exec_date: Airflow execution_date(ISO) ‑ DAG 트리거 시점의 날짜
               - None 이면 today(UTC) 로 처리
    """
    date_str = (exec_date or datetime.utcnow().date()).isoformat()
    logging.info(f"📊 Evaluating prediction for {date_str}")

    with ENGINE.begin() as conn:
        # 1) 예측값
        pred_sql = text(f"""
            SELECT date, ticker, pred_close, model
            FROM {TABLE_PRED}
            WHERE date = :d AND ticker = 'AAPL'
            LIMIT 1
        """)
        pred_df = pd.read_sql(pred_sql, conn, params={"d": date_str})

        if pred_df.empty:
            logging.warning("❗ 예측 데이터가 없습니다. 평가 스킵")
            return

        # 2) 실제값
        price_sql = text(f"""
            SELECT date, close
            FROM {TABLE_PRICE}
            WHERE date = :d AND ticker = 'AAPL'
            LIMIT 1
        """)
        price_df = pd.read_sql(price_sql, conn, params={"d": date_str})

        if price_df.empty:
            logging.warning("❗ 실제 종가가 없습니다. 평가 스킵")
            return

        true_close = price_df.loc[0, "close"]
        pred_close = pred_df.loc[0, "pred_close"]
        abs_err    = abs(true_close - pred_close)

        eval_row = {
            "date"       : date_str,
            "ticker"     : "AAPL",
            "pred_close" : float(pred_close),
            "true_close" : float(true_close),
            "abs_error"  : float(abs_err),
            "model"      : pred_df.loc[0, "model"],
        }

        # 3) 결과 upsert (충돌 시 갱신)
        upsert_sql = text(f"""
            INSERT INTO {TABLE_EVAL} (date, ticker, pred_close, true_close,
                                      abs_error, model)
            VALUES (:date, :ticker, :pred_close, :true_close, :abs_error, :model)
            ON CONFLICT (date, ticker)
            DO UPDATE SET
                pred_close = EXCLUDED.pred_close,
                true_close = EXCLUDED.true_close,
                abs_error  = EXCLUDED.abs_error,
                model      = EXCLUDED.model;
        """)
        conn.execute(upsert_sql, **eval_row)

    logging.info(f"✅ Saved evaluation (abs_error={abs_err:.4f}) to {TABLE_EVAL}")

# ──────────────────────────────── Airflow DAG ─────────────────────────────────
default_args = {
    "owner"        : "airflow",
    "retries"      : 1,
    "retry_delay"  : timedelta(minutes=5),
    "start_date"   : datetime(2023, 1, 1),
}

with DAG(
    dag_id="evaluate_prediction_dag",
    default_args=default_args,
    schedule_interval="@daily",        # 실거래일 종료 후 00:05 UTC 등으로 조정 가능
    catchup=False,
    tags=["stockcast", "eval"],
) as dag:

    evaluate = PythonOperator(
        task_id="evaluate_prediction",
        python_callable=evaluate_prediction,
    )

# (선택) predict_stock_price_dag 에서 TriggerDagRunOperator 로 연결
# or   >>>  dag dependency :  predict -> evaluate
