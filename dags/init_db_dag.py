from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator


from utils.utils import load_sql
from utils.dag_utils import insert_backfilled

DEFAULT_ARGS = {
    "retries": 1,
    "retry_delay": timedelta(minutes = 2)
}
CONN_ID = "postgres"

with DAG(
    dag_id = "init_db_dag",
    description="Initialize tables",
    start_date = datetime(2025, 9, 4),
    schedule_interval = None,
    catchup = False,
    default_args = DEFAULT_ARGS,
) as dag:
    
    create_core = SQLExecuteQueryOperator(
        task_id = "create_tables",
        conn_id = "postgres",
        sql = load_sql("create_table.sql")
    )

    insert_backfill = PythonOperator(
        task_id = "backfill_initial_recent",
        python_callable = insert_backfilled,
        op_kwargs = {
            "years": 3,
            "conn_id": CONN_ID
        }
    )

create_core >> insert_backfill