# streamlit_app.py
# --------------------------------------------------------------------------
# 📈 Stock Prediction Dashboard  (AAPL)
# --------------------------------------------------------------------------
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from path import ProjectPath   # 전역 경로 모음

st.set_page_config(page_title="📈 Stock Prediction Dashboard",
                   layout="wide")

st.title("📊 Stock Price Prediction Dashboard")

# ───────────────────────────── DB 연결 ─────────────────────────────
engine = create_engine(ProjectPath.DB_URI)

# ──────────────────────── 데이터 로드∙캐싱 ────────────────────────
@st.cache_data(show_spinner=False)
def load_predictions() -> pd.DataFrame:
    q = "SELECT * FROM stock_pred WHERE ticker = 'AAPL' ORDER BY date"
    df = pd.read_sql(q, engine)
    df["date"] = pd.to_datetime(df["date"])
    return df

@st.cache_data(show_spinner=False)
def load_actuals() -> pd.DataFrame:
    q = "SELECT * FROM stock_price WHERE ticker = 'AAPL' ORDER BY date"
    df = pd.read_sql(q, engine)
    df["date"] = pd.to_datetime(df["date"])
    return df

@st.cache_data(show_spinner=False)
def compute_metrics(df: pd.DataFrame):
    df = df.dropna(subset=["close", "pred_close"])
    mae  = (df["close"] - df["pred_close"]).abs().mean()
    rmse = ((df["close"] - df["pred_close"]) ** 2).mean() ** 0.5
    return mae, rmse

# ───────────────────────────── 데이터 처리 ──────────────────────────
pred_df   = load_predictions()
actual_df = load_actuals()

actual_df = actual_df.sort_values("date").reset_index(drop=True)
actual_df["prev_close"] = actual_df["close"].shift(1)

merged_df = pd.merge(
    pred_df,
    actual_df,
    on="date",
    suffixes=("_pred", "_actual"),
    how="outer",
)

# ─────────────────────────── 날짜 범위 필터 ─────────────────────────
min_d, max_d = merged_df["date"].min(), merged_df["date"].max()
st.sidebar.header("📅 Date Range Filter")
date_range = st.sidebar.date_input(
    label      = "Select period",
    value      = (min_d.date(), max_d.date()),
    min_value  = min_d.date(),
    max_value  = max_d.date(),
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    merged_df  = merged_df[(merged_df["date"] >= start) & (merged_df["date"] <= end)]

# ──────────────────────── 성능 지표 출력 ───────────────────────────
mae, rmse = compute_metrics(merged_df)
col1, col2 = st.columns(2)
col1.metric("📉 MAE",  f"{mae:,.2f}")
col2.metric("📉 RMSE", f"{rmse:,.2f}")

# ──────────────────────── 라인 차트 출력 ───────────────────────────
st.subheader("📈 Close Price (Actual vs Predicted)  + Previous-day")
chart_df = (
    merged_df[["date", "prev_close", "close", "pred_close"]]
    .set_index("date")
    .rename(columns={
        "prev_close": "prev_close(-1d)",
        "close": "actual_close",
        "pred_close": "predicted_close",
    })
)
st.line_chart(chart_df)

# ──────────────────── 🔍 Raw 데이터 테이블 확인 ────────────────────
with st.expander("🗂  Show merged raw table ▼", expanded=False):
    st.dataframe(
        merged_df.sort_values("date"),
        use_container_width=True,
        height=min(500, max(300, len(merged_df) * 25))
    )

# ───────────────────────── 최신 예측 카드 ─────────────────────────
latest = pred_df.sort_values("date").iloc[-1]
st.subheader("🕐 Latest Prediction")
st.write(
    f"""
    **날짜:** {latest['date'].date()}  
    **예측 종가:** {latest['pred_close']:.2f}  
    **사용된 모델:** {latest['model']}
    """
)
