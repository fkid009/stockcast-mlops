from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging

import yfinance as yf
from curl_cffi import requests

def fetch_stock_price():
    # TLS 우회 세션 생성
    session = requests.Session(impersonate="chrome")
    
    # 데이터 요청
    ticker = yf.Ticker("AAPL", session=session)
    data = ticker.history(period="1d")

    if data.empty:
        logging.warning("No data returned for AAPL.")
    else:
        logging.info(f"Downloaded {len(data)} rows for AAPL")
        # 예: DB 저장 로직 (생략 가능)
        print(data)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'fetch_stock_price_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_stock_price',
        python_callable=fetch_stock_price,
    )
