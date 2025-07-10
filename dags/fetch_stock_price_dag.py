# dags/fetch_stock_price_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging
import pandas as pd
import yfinance as yf
from curl_cffi import requests
from sqlalchemy import create_engine

# ──────────────────────────────────────────────
DB_CONN = "postgresql+psycopg2://airflow:airflow@postgres/airflow"
engine = create_engine(DB_CONN)
TABLE_NAME = "stock_price"
TICKER = "AAPL"
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

    # ticker 컬럼 추가(스키마에 있다면)
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]
    df["ticker"] = TICKER

    logging.info(f"Fetched {len(df)} rows for {TICKER}")
    # DB INSERT
    with engine.begin() as conn:            # 자동 commit
        df.to_sql(TABLE_NAME, conn,
                  if_exists="append", index=False, method="multi")
    logging.info("Rows inserted into Postgres.")

default_args = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "fetch_stock_price_dag",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["stockcast", "fetch"],
) as dag:
    fetch_task = PythonOperator(
        task_id="fetch_stock_price",
        python_callable=fetch_stock_price,
    )
