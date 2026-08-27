CREATE OR REPLACE VIEW v_daily_returns AS
SELECT
    f.asset_id, a.ticker, f.date, f.adj_close,
    f.adj_close / LAG(f.adj_close) OVER w - 1              AS ret,
    LN(f.adj_close / LAG(f.adj_close) OVER w)              AS log_ret
FROM fact_price_daily f
JOIN dim_asset a USING (asset_id)
WINDOW w AS (PARTITION BY f.asset_id ORDER BY f.date);

CREATE OR REPLACE VIEW v_rolling_metrics AS
SELECT
    asset_id, ticker, date, adj_close, ret,
    AVG(adj_close) OVER (PARTITION BY asset_id ORDER BY date
        ROWS BETWEEN 49 PRECEDING AND CURRENT ROW)          AS ma_50,
    AVG(adj_close) OVER (PARTITION BY asset_id ORDER BY date
        ROWS BETWEEN 199 PRECEDING AND CURRENT ROW)         AS ma_200,
    STDDEV_SAMP(ret) OVER (PARTITION BY asset_id ORDER BY date
        ROWS BETWEEN 62 PRECEDING AND CURRENT ROW) * SQRT(252) AS vol_63d_ann
FROM v_daily_returns;

CREATE OR REPLACE VIEW v_drawdown AS
SELECT
    asset_id, ticker, date, adj_close,
    MAX(adj_close) OVER (PARTITION BY asset_id ORDER BY date) AS cum_max,
    adj_close / MAX(adj_close) OVER (PARTITION BY asset_id ORDER BY date) - 1
        AS drawdown
FROM v_daily_returns;

CREATE OR REPLACE VIEW v_monthly_returns AS
WITH eom AS (
    SELECT asset_id, ticker,
           date_trunc('month', date)::date AS month_start,
           MAX(date) AS month_end
    FROM v_daily_returns
    GROUP BY asset_id, ticker, date_trunc('month', date)
)
SELECT
    d.asset_id, d.ticker, e.month_end,
    d.adj_close                                             AS adj_close_eom,
    d.adj_close / LAG(d.adj_close) OVER
        (PARTITION BY d.asset_id ORDER BY e.month_end) - 1  AS monthly_ret
FROM eom e
JOIN v_daily_returns d ON d.asset_id = e.asset_id AND d.date = e.month_end;
