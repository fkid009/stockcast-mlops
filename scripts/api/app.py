from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import pandas as pd
from scripts.path import ProjectPath

app = FastAPI(title="StockCast API")

# CORS 허용 (Streamlit 등 외부 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine(ProjectPath.DB_URI)


@app.get("/predict")
def get_latest_prediction(ticker: str = "AAPL"):
    query = f"""
        SELECT * FROM stock_pred
        WHERE ticker = '{ticker}'
        ORDER BY date DESC LIMIT 1
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")[0]


@app.get("/history")
def get_prediction_history(
    ticker: str = "AAPL",
    start: str = Query(None),
    end: str = Query(None)
):
    query = f"SELECT * FROM stock_pred WHERE ticker = '{ticker}'"
    if start:
        query += f" AND date >= '{start}'"
    if end:
        query += f" AND date <= '{end}'"
    query += " ORDER BY date"
    df = pd.read_sql(query, engine)
    return df.to_dict(orient="records")
