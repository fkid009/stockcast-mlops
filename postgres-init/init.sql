CREATE DATABASE stock;

CREATE TABLE IF NOT EXISTS stock_price (
    date          TIMESTAMP,
    open          NUMERIC,
    high          NUMERIC,
    low           NUMERIC,
    close         NUMERIC,
    volume        BIGINT,
    dividends     NUMERIC,
    stock_splits  NUMERIC,
    ticker        TEXT
);

CREATE TABLE IF NOT EXISTS stock_pred_eval (
    date        DATE,
    ticker      TEXT,
    pred_close  FLOAT,
    true_close  FLOAT,
    abs_error   FLOAT,
    model       TEXT,
    PRIMARY KEY (date, ticker)
);
