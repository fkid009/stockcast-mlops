# streamlit_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from path import ProjectPath

st.set_page_config(page_title="📈 Stock Prediction Dashboard", layout="wide")
st.title("📊 Stock Price Prediction Dashboard")

engine = create_engine(ProjectPath.DB_URI)

@st.cache_data
def load_predictions():
    query = "SELECT * FROM stock_pred WHERE ticker = 'AAPL' ORDER BY date"
    return pd.read_sql(query, engine)

@st.cache_data
def load_actuals():
    query = "SELECT * FROM stock_price WHERE ticker = 'AAPL' ORDER BY date"
    return pd.read_sql(query, engine)

@st.cache_data
def compute_metrics(df):
    df = df.dropna()
    mae = (df["close"] - df["pred_close"]).abs().mean()
    rmse = ((df["close"] - df["pred_close"]) ** 2).mean() ** 0.5
    return mae, rmse

# Load data
pred_df = load_predictions()
actual_df = load_actuals()
pred_df["date"] = pd.to_datetime(pred_df["date"])
actual_df["date"] = pd.to_datetime(actual_df["date"])
merged_df = pd.merge(pred_df, actual_df, on="date", suffixes=("_pred", "_actual"))

# 날짜 필터
date_range = st.date_input("날짜 범위 선택", [])
if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range)
    merged_df = merged_df[(merged_df["date"] >= start_date) & (merged_df["date"] <= end_date)]

# 지표
mae, rmse = compute_metrics(merged_df)
st.metric("📉 MAE (Mean Absolute Error)", f"{mae:.2f}")
st.metric("📉 RMSE (Root Mean Square Error)", f"{rmse:.2f}")

# 시각화
st.line_chart(merged_df[["date", "close", "pred_close"]].set_index("date"))

# 최신 예측
latest = pred_df.sort_values("date").iloc[-1]
st.subheader("🕐 Latest Prediction")
st.write(f"날짜: {latest['date']}")
st.write(f"예측 종가: {latest['pred_close']:.2f}")
st.write(f"사용된 모델: {latest['model']}")
