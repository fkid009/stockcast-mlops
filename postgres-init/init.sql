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

