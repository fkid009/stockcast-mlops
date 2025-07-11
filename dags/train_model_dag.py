from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="train_model_dag",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    schedule_interval=None,  # 여기선 수동 실행 후 복수 task를 분기할 수 있음
    tags=["training", "ml"],
) as dag:

    daily_train = BashOperator(
        task_id="daily_train",
        bash_command="python /opt/airflow/scripts/train_model.py --mode daily --config /opt/airflow/scripts/params.yaml",
    )

    weekly_tune = BashOperator(
        task_id="weekly_tune",
        bash_command="python /opt/airflow/scripts/train_model.py --mode tune --config /opt/airflow/scripts/params.yaml",
    )

    # 필요 시 의존성 지정
    # daily_train >> weekly_tune
