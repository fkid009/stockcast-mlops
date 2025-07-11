# ──────────────────── dags/train_model_dag.py ────────────────────
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="train_model_dag",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,          # 트리거 전용
    catchup=False,
    tags=["stockcast", "train"],
) as dag:

    daily_train = BashOperator(
        task_id="daily_train",
        bash_command=(
            "python /opt/airflow/scripts/train_model.py "
            "--mode daily --config /opt/airflow/scripts/params.yaml"
        ),
    )

    trigger_predict = TriggerDagRunOperator(
        task_id="trigger_predict",
        trigger_dag_id="predict_stock_price_dag",
        wait_for_completion=False,
    )

    daily_train >> trigger_predict
