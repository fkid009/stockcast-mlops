import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging
from pathlib import Path

DB_URI = "postgresql+psycopg2://airflow:airflow@postgres/airflow"
OUTPUT_DIR = Path("/opt/airflow/data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    engine = create_engine(DB_URI)
    query = "SELECT date, open, high, low, close, volume FROM stock_price WHERE ticker='AAPL'"
    df = pd.read_sql(query, engine, parse_dates=["date"])
    logging.info(f"Loaded {len(df)} rows from DB")
    return df

def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").reset_index(drop=True)

    # 이동평균·변동률
    df["ma5"] = df["close"].rolling(window=5).mean()
    df["pct_change_1d"] = df["close"].pct_change()
    df["log_volume"] = np.log1p(df["volume"])

    # 타깃: 다음 날 종가
    df["target"] = df["close"].shift(-1)
    df = df.dropna()

    logging.info(f"After engineering: {df.shape}")
    return df

def split_and_save(df: pd.DataFrame):
    feature_cols = ["open", "high", "low", "close", "volume",
                    "ma5", "pct_change_1d", "log_volume"]
    X = df[feature_cols].values
    y = df["target"].values

    np.save(OUTPUT_DIR / "X.npy", X)
    np.save(OUTPUT_DIR / "y.npy", y)
    logging.info(f"Saved X {X.shape} and y {y.shape} to {OUTPUT_DIR}")

def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s - %(message)s")
    df_raw = load_data()
    df_feat = feature_engineering(df_raw)
    split_and_save(df_feat)

if __name__ == "__main__":
    main()
