import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging

from path import ProjectPath          # ★ 경로 관리 전용 모듈

DB_URI      = ProjectPath.DB_URI
OUTPUT_DIR  = ProjectPath.PROCESSED_DATA_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    engine = create_engine(DB_URI)
    query  = """
        SELECT date, open, high, low, close, volume
        FROM stock_price
        WHERE ticker = 'AAPL'
    """
    df = pd.read_sql(query, engine, parse_dates=["date"])
    logging.info("Loaded %d rows from DB", len(df))
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").reset_index(drop=True)
    df["ma5"]           = df["close"].rolling(5).mean()
    df["pct_change_1d"] = df["close"].pct_change()
    df["log_volume"]    = np.log1p(df["volume"])
    df["target"]        = df["close"].shift(-1)
    df.dropna(inplace=True)
    logging.info("After engineering: %s", df.shape)
    return df

def split_and_save(df: pd.DataFrame):
    feat_cols = ["open", "high", "low", "close", "volume",
                 "ma5", "pct_change_1d", "log_volume"]

    X_all, y_all = df[feat_cols].values, df["target"].values

    X_train, y_train = X_all[:-1], y_all[:-1]  # 마지막 1행 제외
    X_inf            = X_all[-1:]             # shape (1, n_feat)

    np.save(ProjectPath.PROCESSED_DATA_DIR / "X_train.npy", X_train)
    np.save(ProjectPath.PROCESSED_DATA_DIR / "y_train.npy", y_train)
    np.save(ProjectPath.PROCESSED_DATA_DIR / "X_inf.npy" , X_inf)

    logging.info(
        f"Saved → "
        f"X_train {X_train.shape}, y_train {y_train.shape}, X_inf {X_inf.shape}"
    )
def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s - %(message)s")
    df = load_data()
    df = feature_engineering(df)
    split_and_save(df)

if __name__ == "__main__":
    main()
