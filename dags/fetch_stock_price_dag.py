# ──────────────────── dags/fetch_stock_price_dag.py ────────────────────
from datetime import datetime, timedelta
import logging
import pandas as pd
import yfinance as yf
from curl_cffi import requests
from sqlalchemy import create_engine

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from path import ProjectPath          # 전역 경로 모음

DB_URI     = ProjectPath.DB_URI
TABLE_NAME = "stock_price"
TICKER     = "AAPL"
engine     = create_engine(DB_URI)


def fetch_stock_price():
    """Yahoo Finance → Postgres(AAPL 최근 1일분)"""
    session = requests.Session(impersonate="chrome")
    df = (
        yf.Ticker(TICKER, session=session)
        .history(period="1d")
        .reset_index()
        .rename(columns={"Date": "date"})
    )

    if df.empty:
        logging.warning(f"[FETCH] No data returned for {TICKER}")
        return

    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    df["ticker"] = TICKER
    logging.info(f"[FETCH] Rows fetched: {len(df)}")

    with engine.begin() as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="append", index=False, method="multi")
    logging.info("[FETCH] Inserted into Postgres")


default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="fetch_stock_price_dag",
    default_args=default_args,
    schedule_interval="@daily",      # 매일 1회 실행
    catchup=False,
    tags=["stockcast", "fetch"],
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_stock_price",
        python_callable=fetch_stock_price,
    )

    # ── 다음 단계 DAG 트리거 ─────────────────────
    trigger_preprocess = TriggerDagRunOperator(
        task_id="trigger_preprocess",
        trigger_dag_id="preprocess_stock_dag",
        wait_for_completion=False,
    )

    fetch_task >> trigger_preprocess
