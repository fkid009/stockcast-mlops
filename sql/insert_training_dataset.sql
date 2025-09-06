WITH base AS (
  SELECT ticker_id, dt, adj_close, volume
  FROM ohlcv_daily
),
feat AS (
  SELECT
    ticker_id,
    dt AS asof_date,

    -- X: 가격 기반
    LAG(adj_close, 1) OVER w      AS lag_close_1,
    AVG(adj_close)     OVER w5    AS ma_5,
    AVG(adj_close)     OVER w20   AS ma_20,
    STDDEV_SAMP(adj_close) OVER w20 AS std_20,

    -- X: 거래량 기반
    LAG(volume, 1)     OVER w     AS lag_vol_1,
    (volume - AVG(volume) OVER w20) / NULLIF(STDDEV_SAMP(volume) OVER w20, 0) AS vol_z20,

    -- y: 다음 '거래일'의 가격 
    LEAD(adj_close, 1) OVER w     AS y_price_next
  FROM base
  WINDOW
    w   AS (PARTITION BY ticker_id ORDER BY dt),
    w5  AS (PARTITION BY ticker_id ORDER BY dt ROWS BETWEEN 4  PRECEDING AND CURRENT ROW),
    w20 AS (PARTITION BY ticker_id ORDER BY dt ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
)
INSERT INTO training_dataset (
  ticker_id,
  asof_date,
  lag_close_1,
  ma_5,
  ma_20,
  ma_gap,
  std_20,
  lag_vol_1,
  vol_z20,
  y_price_next
)
SELECT
  ticker_id,
  asof_date,
  lag_close_1,
  ma_5,
  ma_20,
  (ma_5 - ma_20) AS ma_gap,
  std_20,
  lag_vol_1,
  vol_z20,
  y_price_next
FROM feat
WHERE y_price_next IS NOT NULL        -- 다음 거래일이 있는 구간만 학습 대상
  AND lag_close_1 IS NOT NULL         -- 최소 히스토리 조건
  AND ma_20 IS NOT NULL               -- 20일 통계가 계산 가능한 구간
ON CONFLICT (ticker_id, asof_date) DO UPDATE
SET lag_close_1 = EXCLUDED.lag_close_1,
    ma_5        = EXCLUDED.ma_5,
    ma_20       = EXCLUDED.ma_20,
    ma_gap      = EXCLUDED.ma_gap,
    std_20      = EXCLUDED.std_20,
    lag_vol_1   = EXCLUDED.lag_vol_1,
    vol_z20     = EXCLUDED.vol_z20,
    y_price_next= EXCLUDED.y_price_next;
