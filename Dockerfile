FROM apache/airflow:2.8.1

# Install additional Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt