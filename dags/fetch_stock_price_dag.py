from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import yfinance as yf
import pandas as pd
import psycopg2
import logging

def fetch_and_store():
    ticker = "AAPL"
    logging.info(f"Fetching data for {ticker} from yfinance.")
    df = yf.download(ticker, period="7d", interval="1d")
    logging.info(f"Downloaded {len(df)} rows of data.")

    df.reset_index(inplace=True)
    df["Ticker"] = ticker
    df.rename(columns={
        "Date": "date", "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Adj Close": "adj_close", "Volume": "volume"
    }, inplace=True)

    conn = psycopg2.connect(
        host="postgres", database="stock", user="airflow", password="airflow"
    )
    cur = conn.cursor()
    for _, row in df.iterrows():
        try:
            cur.execute("""
                INSERT INTO stock_price (date, open, high, low, close, adj_close, volume, ticker)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, ticker) DO NOTHING;
            """, tuple(row))
        except Exception as e:
            logging.error(f"Insert error on row {row['date']}: {e}")
    conn.commit()
    cur.close()
    conn.close()
    logging.info("Data stored to stock_price table.")

with DAG(
    dag_id="fetch_stock_price_dag",
    start_date=datetime(2024, 1, 2),
    schedule_interval="@daily",
    catchup=False,
    tags=["fetch", "stock", "postgresql"],
) as dag:
    fetch_task = PythonOperator(
        task_id="fetch_stock_price",
        python_callable=fetch_and_store
    )

    fetch_task
