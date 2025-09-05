INSERT INTO tickers(symbol, name, exchange, currency)
VALUES (%s, %s, %s, %s)
ON CONFLICT (symbol) DO NOTHING;