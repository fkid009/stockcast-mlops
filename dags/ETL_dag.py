from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from utils.utils import load_sql

DEFAULT_ARGS = {
    "retries": 1, 
    "retry_delay": timedelta(minutes=2)
}
CONN_ID = "postgres"

with DAG(
    dag_id="building_training_dataset_full",
    description="Build full training_dataset_daily from all available ohlcv_daily",
    start_date=datetime(2025, 9, 6),
    schedule_interval=None,     
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["etl", "dataset", "training", "full"],
) as dag:

    rebuild_full = SQLExecuteQueryOperator(
        task_id="build_training_dataset",
        conn_id=CONN_ID,
        sql=load_sql("insert_training_dataset.sql"),
    )
