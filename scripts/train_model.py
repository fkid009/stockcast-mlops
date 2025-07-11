# ─────────────────────────────  scripts/train_model.py  ──────────────────────────
"""
• 매일 재학습
• Ridge / XGBoost 둘 다 학습하여 RMSE가 더 낮은 모델 하나만
  data/models/latest/best_model.{pkl|json} 로 저장
• MLflow 로 experiment 기록
"""
import json, logging, yaml, joblib, mlflow, numpy as np
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor
from path import ProjectPath

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s"
)

# 경로
PARAM_YAML  = ProjectPath.PARAM_YAML
X_PATH      = ProjectPath.PROCESSED_DATA_DIR / "X_train.npy"
Y_PATH      = ProjectPath.PROCESSED_DATA_DIR / "y_train.npy"
MODEL_DIR   = ProjectPath.MODELS_DIR / "latest"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

def load_params():
    with open(PARAM_YAML) as f:
        return yaml.safe_load(f)

def train():
    mlflow.set_experiment("daily_training")
    prm = load_params()
    X   = np.load(X_PATH)
    y   = np.load(Y_PATH)

    best = {"rmse": 1e9}

    # ── Ridge ───────────────────────────────────────────────────────
    with mlflow.start_run(run_name="ridge_daily"):
        ridge = Ridge(**prm["ridge"]).fit(X, y)
        rmse  = np.sqrt(((ridge.predict(X) - y) ** 2).mean())
        mlflow.log_metric("rmse", rmse)
        mlflow.sklearn.log_model(ridge, "model")
        logging.info(f"Ridge RMSE: {rmse:.4f}")
        if rmse < best["rmse"]:
            best = {"rmse": rmse, "type": "ridge",
                    "path": MODEL_DIR / "best_model.pkl"}
            joblib.dump(ridge, best["path"])

    # ── XGBoost ─────────────────────────────────────────────────────
    with mlflow.start_run(run_name="xgb_daily"):
        xgb = XGBRegressor(**prm["xgb"]).fit(X, y)
        rmse = np.sqrt(((xgb.predict(X) - y) ** 2).mean())
        mlflow.log_metric("rmse", rmse)
        mlflow.xgboost.log_model(xgb, "model")
        logging.info(f"XGBoost RMSE: {rmse:.4f}")
        if rmse < best["rmse"]:
            best = {"rmse": rmse, "type": "xgb",
                    "path": MODEL_DIR / "best_model.json"}
            xgb.save_model(best["path"])

    # ── 결과 정리 ────────────────────────────────────────────────────
    meta = {"type": best["type"], "rmse": best["rmse"]}
    with open(MODEL_DIR / "best_model_meta.json", "w") as f:
        json.dump(meta, f)

    logging.info(f"◎ Best model: {best['type']}  (RMSE={best['rmse']:.4f})")
    logging.info("✔ Saved best_model and meta.json")

if __name__ == "__main__":
    train()
