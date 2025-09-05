from datetime import datetime, timedelta
from typing import Optional, List

from utils.utils import load_sql, load_yaml
from utils.path import SQL_DIR, UTILS_DIR

import pandas as pd
import yfinance as yf
import psycopg2.extras as extras

from airflow.providers.postgres.hooks.postgres import PostgresHook



# ---------- Internal constants ----------
_OHLCV_COLMAP = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
}
_NUMERIC_COLS = ["open", "high", "low", "close", "adj_close", "volume"]


def _normalize_ohlcv_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize a yfinance OHLCV DataFrame for insertion into `ohlcv_daily`.

    - Flatten MultiIndex columns if present.
    - Drop duplicated column names (keep the first).
    - Rename columns to the canonical lower-case set.
    - Ensure a `Date` column exists and is of `date` type.
    - Fill missing numeric values with 0.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # (1) Flatten potential MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    # (2) Remove duplicated columns (keep first occurrence)
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]

    # (3) Rename to canonical names
    df = df.rename(columns=_OHLCV_COLMAP)

    # (4) Ensure a `Date` column
    df = df.reset_index(names="Date")
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # (5) Fill NaNs and coerce types later
    for c in _NUMERIC_COLS:
        if c not in df.columns:
            df[c] = 0
        df[c] = df[c].fillna(0)

    return df


# ---------- DB I/O ----------
def insert_ticker(
    pg: PostgresHook,
    symbol: str,
    name: Optional[str] = None,
    exchange: Optional[str] = None,
    currency: Optional[str] = None,
) -> int:
    """
    Insert a symbol into `tickers` and return its `ticker_id`.

    Requires `insert_ticker_table.sql` to include:
        ON CONFLICT (symbol) DO NOTHING
    """
    sql = load_sql(SQL_DIR / "insert_ticker_table.sql")
    with pg.get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (symbol, name, exchange, currency))
        conn.commit()
        cur.execute("SELECT ticker_id FROM tickers WHERE symbol = %s;", (symbol,))
        row = cur.fetchone()
        if row is None:
            raise RuntimeError(f"Failed to resolve ticker_id for symbol={symbol!r}")
        return row[0]


def has_rows_for_ticker(pg: PostgresHook, ticker_id: int) -> bool:
    """
    Return True if `ohlcv_daily` already contains any row for the given ticker_id.

    Use this to guard the initial backfill so it runs only once per ticker.
    """
    with pg.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM ohlcv_daily WHERE ticker_id=%s LIMIT 1;", (ticker_id,))
        return cur.fetchone() is not None


def insert_ohlcv(pg: PostgresHook, 
                 ticker_id: int, 
                 df: pd.DataFrame) -> int:
    """
    Initial backfill ONLY: pure INSERT (idempotency recommended at SQL level).

    `insert_ohlcv.sql` should include:
        ON CONFLICT (ticker_id, dt) DO NOTHING;
    """
    df = _normalize_ohlcv_df(df)
    if df.empty:
        return 0

    # Build rows using numpy extraction (robust to Series/DataFrame cases)
    rows = list(
        zip(
            [ticker_id] * len(df),
            df["Date"].tolist(),
            df["open"].to_numpy(dtype=float).tolist(),
            df["high"].to_numpy(dtype=float).tolist(),
            df["low"].to_numpy(dtype=float).tolist(),
            df["close"].to_numpy(dtype=float).tolist(),
            df["adj_close"].to_numpy(dtype=float).tolist(),
            df["volume"].to_numpy(dtype=int).tolist(),
            ["yfinance"] * len(df),
        )
    )

    sql = load_sql(SQL_DIR / "insert_ohlcv.sql")
    with pg.get_conn() as conn, conn.cursor() as cur:
        extras.execute_values(cur, sql, rows, page_size=1000)
        conn.commit()
    return len(rows)


# ---------- DAG-facing entrypoint ----------
def insert_backfilled(*, 
                      years: int = 3, 
                      conn_id: str = "postgres") -> None:
    """
    Initial backfill (INSERT-only) for the last `years` years based on `utils/tickers.yaml`.

    Behavior:
    - Skip a ticker if `ohlcv_daily` already contains data (one-time backfill guard).
    - Use `auto_adjust=False` to keep original OHLCV + Adj Close from yfinance.
    """
    data = load_yaml(UTILS_DIR / "tickers.yaml")
    symbols: List[str] = [str(s).strip() for s in (data.get("tickers") or []) if str(s).strip()]
    if not symbols:
        print("[backfill] No tickers provided. Skip.")
        return

    pg = PostgresHook(postgres_conn_id=conn_id)

    today = datetime.utcnow().date()
    start = today - timedelta(days=365 * years)
    end = today + timedelta(days=1)  # yfinance `end` is effectively exclusive

    total = 0
    for sym in symbols:
        tid = insert_ticker(pg, sym)

        # Guard: run the initial backfill only once per ticker
        if has_rows_for_ticker(pg, tid):
            print(f"[backfill] skip {sym}: already has rows")
            continue

        try:
            df = yf.download(
                sym,
                start=start.isoformat(),
                end=end.isoformat(),
                progress=False,
                auto_adjust=False,  # keep original OHLCV + Adj Close
            )
        except Exception as e:
            print(f"[backfill] {sym}: download error: {e}")
            continue

        n = insert_ohlcv(pg, tid, df)
        print(f"[backfill] {sym}: rows={n}")
        total += n

    print(f"[backfill] total rows={total}")