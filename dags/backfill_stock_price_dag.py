"""
백필용 DAG – AAPL 5년치 일봉 데이터를 stock_price 테이블에 적재
한 번 수동 트리거 후, 성공하면 Disable 하자.
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import yfinance as yf
from curl_cffi import requests
from sqlalchemy import create_engine
import pandas as pd
import logging

# === 설정 ===
TICKERS        = ["AAPL"]            # 👈 단일 종목
PERIOD         = "5y"
TABLE_NAME     = "stock_price"
DB_URI         = "postgresql+psycopg2://airflow:airflow@postgres/airflow"
engine         = create_engine(DB_URI)

def backfill_prices():
    sess = requests.Session(impersonate="chrome")
    total_rows = 0

    for tkr in TICKERS:
        df = yf.download(tkr, period=PERIOD, session=sess, group_by=None)

        # 💡 멀티인덱스 컬럼 제거
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(0)

        df.columns = [c.lower() if isinstance(c, str) else c for c in df.columns]

        if df.empty:
            logging.warning(f"{tkr}: no rows returned")
            continue

        df.reset_index(inplace=True)
        df.columns = [c.lower() if isinstance(c, str) else c for c in df.columns]
        df.rename(columns={"index": "date"}, inplace=True)
        df["ticker"] = tkr

        # 중복 대비 UNIQUE(ticker, date) 인덱스 권장
        df.to_sql(TABLE_NAME,
                  con=engine,
                  if_exists="append",
                  index=False,
                  method="multi")

        logging.info(f"{tkr}: inserted {len(df)} rows")
        total_rows += len(df)

    logging.info(f"✅ Backfill finished – total {total_rows} rows inserted")

with DAG(
    dag_id="backfill_stock_price_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,   # 수동 실행 전용
    catchup=False,
    tags=["one‑off", "backfill"],
) as dag:
    PythonOperator(
        task_id="backfill_prices",
        python_callable=backfill_prices,
    )
