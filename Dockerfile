FROM apache/airflow:2.8.1-python3.8

USER airflow
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
