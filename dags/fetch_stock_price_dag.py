# dags/fetch_stock_price_dag.py
from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator

import pandas as pd
import yfinance as yf
from curl_cffi import requests
from sqlalchemy import create_engine

# ──────────────────────────────────────────────
from path import ProjectPath                 # ← 전역 경로 모음

DB_URI     = ProjectPath.DB_URI              # path.py 에 정의
TABLE_NAME = "stock_price"
TICKER     = "AAPL"
engine     = create_engine(DB_URI)
# ──────────────────────────────────────────────


def fetch_stock_price():
    session = requests.Session(impersonate="chrome")
    df = (
        yf.Ticker(TICKER, session=session)
        .history(period="1d")
        .reset_index()
        .rename(columns={"Date": "date"})
    )

    if df.empty:
        logging.warning(f"No data returned for {TICKER}.")
        return

    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    df["ticker"] = TICKER

    logging.info(f"Fetched {len(df)} rows for {TICKER}")

    with engine.begin() as conn:             # auto‑commit
        df.to_sql(TABLE_NAME, conn,
                  if_exists="append",
                  index=False,
                  method="multi")
    logging.info("Rows inserted into Postgres.")


default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="fetch_stock_price_dag",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["stockcast", "fetch"],
) as dag:
    PythonOperator(
        task_id="fetch_stock_price",
        python_callable=fetch_stock_price,
    )
