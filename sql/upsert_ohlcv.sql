INSERT INTO ohlcv_daily
  (ticker_id, dt, open, high, low, close, adj_close, volume, source)
VALUES %s
ON CONFLICT (ticker_id, dt) DO UPDATE
SET open      = EXCLUDED.open,
    high      = EXCLUDED.high,
    low       = EXCLUDED.low,
    close     = EXCLUDED.close,
    adj_close = EXCLUDED.adj_close,
    volume    = EXCLUDED.volume,
    source    = EXCLUDED.source;
