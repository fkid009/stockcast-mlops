from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from utils.dag_utils import upsert_ohlcv

DEFAULT_ARGS = {
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}
CONN_ID = "postgres"

with DAG(
    dag_id="yf_ohlcv_daily_upsert",
    description="Daily incremental UPSERT of OHLCV from yfinance into Postgres",
    start_date=datetime(2025, 9, 6),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["yfinance", "ohlcv", "upsert", "daily"],
) as dag:
    
    upsert_daily = PythonOperator(
        task_id="upsert_ohlcv",
        python_callable=upsert_ohlcv,
        op_kwargs={
            "logical_ds": "{{ ds }}",
            "conn_id": CONN_ID,
            "source": "yfinance",
        },
    )