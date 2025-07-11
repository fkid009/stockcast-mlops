# scripts/path.py  ─ 수정본
from pathlib import Path


class ProjectPath:
    """
    프로젝트 전역 경로 모음  (컨테이너 내부 기준: /opt/airflow/…)
    """

    # ───────── 최상위
    ROOT        = Path("/opt/airflow")
    SCRIPTS_DIR = ROOT / "scripts"
    DAGS_DIR    = ROOT / "dags"
    DATA_DIR    = ROOT / "data"

    # ───────── 데이터
    RAW_DATA_DIR       = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"

    # ───────── 모델 & 파라미터
    MODELS_DIR         = DATA_DIR / "models"
    MODELS_LATEST_DIR  = MODELS_DIR / "latest"          # ★추가
    PARAMS_DIR         = DATA_DIR / "params"
    PARAM_YAML         = PARAMS_DIR / "params.yaml"

    # ───────── MLflow
    MLRUNS_DIR         = ROOT / "mlruns"                # ★추가
    MLRUNS_DB          = MLRUNS_DIR / "mlruns.db"       # (sqlite 사용 시)

    # ───────── 전처리 산출물
    X_NPY = PROCESSED_DATA_DIR / "X.npy"
    Y_NPY = PROCESSED_DATA_DIR / "y.npy"

    # ───────── DB
    DB_URI = "postgresql+psycopg2://airflow:airflow@postgres/airflow"
