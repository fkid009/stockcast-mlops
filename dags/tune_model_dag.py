# ──────────────────── dags/tune_model_dag.py ────────────────────
"""주 1회 하이퍼파라미터 튜닝 DAG
   - every Sunday 02:00 UTC  (0 2 * * 0)
   - 실행 스크립트 : train_model.py  --mode tune
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=15),
}

with DAG(
    dag_id="tune_model_dag",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    schedule_interval="0 2 * * 0",        # 매주 일요일 02:00 UTC
    tags=["stockcast", "tune"],
) as dag:

    tune_task = BashOperator(
        task_id="run_tuning",
        bash_command=(
            "python /opt/airflow/scripts/train_model.py "
            "--mode tune --config /opt/airflow/scripts/params.yaml"
        ),
    )

    # ★ 튜닝 후 best_model 교체가 이뤄졌다면 바로 예측 DAG 다시 실행
    trigger_predict = TriggerDagRunOperator(
        task_id="trigger_predict_after_tune",
        trigger_dag_id="predict_stock_price_dag",
        wait_for_completion=False,
    )

    tune_task >> trigger_predict
