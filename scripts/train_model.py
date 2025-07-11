"""
train_model.py  ‑‑ 매일 실행되는 단순 재학습 스크립트
"""
import logging
import yaml
import joblib
import mlflow
import numpy as np
from pathlib import Path
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor

from path import ProjectPath  # ★ 경로 전역 관리

# ────────────── 경로 상수
PARAM_PATH   = ProjectPath.PARAM_YAML
FEATURE_PATH = ProjectPath.X_NPY
TARGET_PATH  = ProjectPath.Y_NPY
MODEL_DIR    = ProjectPath.MODELS_DIR / "latest"
MLRUNS_URI   = f"file://{ProjectPath.MLRUNS_DIR}"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ────────────── 유틸
def load_params():
    logging.info("Loading parameters from YAML...")
    with open(PARAM_PATH) as f:
        return yaml.safe_load(f)

def load_dataset():
    logging.info("Loading dataset from .npy files...")
    X = np.load(FEATURE_PATH)
    y = np.load(TARGET_PATH)
    logging.info(f"Loaded features shape: {X.shape}, target shape: {y.shape}")
    return X, y

# ────────────── 학습
def train():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    logging.info("Starting training script...")
    
    mlflow.set_tracking_uri(MLRUNS_URI)
    mlflow.set_experiment("daily_training")

    params = load_params()
    X, y   = load_dataset()

    # Ridge
    logging.info("Training Ridge model...")
    with mlflow.start_run(run_name="ridge_daily"):
        ridge = Ridge(**params["ridge"])
        ridge.fit(X, y)
        joblib.dump(ridge, MODEL_DIR / "ridge.pkl")
        logging.info("Ridge model trained and saved.")
        
        rmse = np.sqrt(((ridge.predict(X) - y) ** 2).mean())
        logging.info(f"Ridge RMSE: {rmse:.4f}")

        mlflow.sklearn.log_model(ridge, artifact_path="model")
        mlflow.log_metric("rmse", rmse)

    # XGBoost
    logging.info("Training XGBoost model...")
    with mlflow.start_run(run_name="xgb_daily"):
        xgb = XGBRegressor(**params["xgb"])
        xgb.fit(X, y)
        joblib.dump(xgb, MODEL_DIR / "xgb.json")
        logging.info("XGBoost model trained and saved.")
        
        rmse = np.sqrt(((xgb.predict(X) - y) ** 2).mean())
        logging.info(f"XGBoost RMSE: {rmse:.4f}")

        mlflow.xgboost.log_model(xgb, artifact_path="model")
        mlflow.log_metric("rmse", rmse)

    logging.info("Training script finished successfully.")

if __name__ == "__main__":
    train()
