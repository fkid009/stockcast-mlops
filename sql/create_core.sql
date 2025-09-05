CREATE TABLE IF NOT EXISTS tickers (
  ticker_id SERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  name TEXT,
  exchange TEXT,
  currency TEXT,
  UNIQUE (symbol)
);

CREATE TABLE IF NOT EXISTS ohlcv_daily (
  id BIGSERIAL PRIMARY KEY,
  ticker_id INT NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,
  dt DATE NOT NULL,
  open DOUBLE PRECISION,
  high DOUBLE PRECISION,
  low  DOUBLE PRECISION,
  close DOUBLE PRECISION,
  adj_close DOUBLE PRECISION,
  volume BIGINT,
  source TEXT DEFAULT 'yfinance',
  UNIQUE (ticker_id, dt)
);

CREATE TABLE IF NOT EXISTS features_daily (
  id BIGSERIAL PRIMARY KEY,
  ticker_id INT NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,
  dt DATE NOT NULL,
  lag_close_1 DOUBLE PRECISION,
  ma_5        DOUBLE PRECISION,
  ma_20       DOUBLE PRECISION,
  ma_gap      DOUBLE PRECISION,
  std_20      DOUBLE PRECISION,
  lag_vol_1   DOUBLE PRECISION,
  vol_z20     DOUBLE PRECISION,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (ticker_id, dt)
);

CREATE TABLE IF NOT EXISTS predictions_daily (
  id BIGSERIAL PRIMARY KEY,
  ticker_id INT NOT NULL REFERENCES tickers(ticker_id) ON DELETE CASCADE,
  dt DATE NOT NULL,
  target_date DATE NOT NULL,
  y_pred DOUBLE PRECISION NOT NULL,
  model_name TEXT,
  run_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (ticker_id, target_date, model_name)
);
