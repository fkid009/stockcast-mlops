# ──────────────────── dags/preprocess_stock_dag.py ────────────────────
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

with DAG(
    dag_id="preprocess_stock_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,          # 트리거 전용
    catchup=False,
    tags=["stockcast", "prep"],
) as dag:

    preprocess = BashOperator(
        task_id="run_preprocessing",
        bash_command="python /opt/airflow/scripts/preprocess_stock.py",
    )

    trigger_train = TriggerDagRunOperator(
        task_id="trigger_train",
        trigger_dag_id="train_model_dag",
        wait_for_completion=False,
    )

    preprocess >> trigger_train
