from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    "preprocess_stock_dag",
    start_date=datetime(2023,1,1),
    schedule_interval=None,
    catchup=False,
) as dag:

    preprocess = BashOperator(
        task_id="run_preprocessing",
        bash_command="python /opt/airflow/scripts/preprocess_stock.py"
    )
