from datetime import timedelta


DEFAULT_ARGS = {
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}
CONN_ID = "postgres"