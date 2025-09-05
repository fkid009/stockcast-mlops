INSERT INTO ohlcv_daily
    (ticker_id, dt, open, high, low, close, adj_close, volume, source)
VALUES %s
ON CONFLICT (ticker_id, dt) DO NOTHING;