from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
import psycopg2

def init_stock_table():
    logging.info("Starting table initialization.")
    conn = psycopg2.connect(
        host="postgres", database="stock", user="airflow", password="airflow"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_price (
            date DATE,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            adj_close FLOAT,
            volume BIGINT,
            ticker VARCHAR(10),
            PRIMARY KEY (date, ticker)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    logging.info("Table 'stock_price' created or already exists.")

with DAG(
    dag_id="init_stock_table_dag",
    start_date=datetime(2024, 1, 1),
    schedule="@once",
    catchup=False,
    tags=["init", "postgresql"],
) as dag:
    init_task = PythonOperator(
        task_id="init_stock_table",
        python_callable=init_stock_table
    )

    init_task
