-- Raw landing tables (as-downloaded, replace-per-run)
CREATE TABLE IF NOT EXISTS raw_prices (
    ticker      TEXT NOT NULL,
    date        DATE NOT NULL,
    open        DOUBLE PRECISION,
    high        DOUBLE PRECISION,
    low         DOUBLE PRECISION,
    close       DOUBLE PRECISION,
    adj_close   DOUBLE PRECISION,
    volume      BIGINT,
    loaded_at   TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (ticker, date)
);

CREATE TABLE IF NOT EXISTS raw_dividends (
    ticker      TEXT NOT NULL,
    date        DATE NOT NULL,
    amount      DOUBLE PRECISION NOT NULL,
    loaded_at   TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (ticker, date)
);

CREATE TABLE IF NOT EXISTS raw_macro (
    series_id   TEXT NOT NULL,
    date        DATE NOT NULL,
    value       DOUBLE PRECISION,
    loaded_at   TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (series_id, date)
);

-- Star schema
CREATE TABLE IF NOT EXISTS dim_asset (
    asset_id    SERIAL PRIMARY KEY,
    ticker      TEXT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    asset_type  TEXT NOT NULL,
    sector      TEXT,
    first_date  DATE,
    last_date   DATE
);

CREATE TABLE IF NOT EXISTS fact_price_daily (
    asset_id    INT NOT NULL REFERENCES dim_asset(asset_id),
    date        DATE NOT NULL,
    open        DOUBLE PRECISION,
    high        DOUBLE PRECISION,
    low         DOUBLE PRECISION,
    close       DOUBLE PRECISION,
    adj_close   DOUBLE PRECISION NOT NULL,
    volume      BIGINT,
    PRIMARY KEY (asset_id, date)
);

CREATE TABLE IF NOT EXISTS fact_dividend (
    asset_id    INT NOT NULL REFERENCES dim_asset(asset_id),
    date        DATE NOT NULL,
    amount      DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (asset_id, date)
);

CREATE TABLE IF NOT EXISTS dim_macro_series (
    series_id   TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    unit        TEXT,
    frequency   TEXT
);

CREATE TABLE IF NOT EXISTS fact_macro_value (
    series_id   TEXT NOT NULL REFERENCES dim_macro_series(series_id),
    date        DATE NOT NULL,
    value       DOUBLE PRECISION,
    PRIMARY KEY (series_id, date)
);

CREATE INDEX IF NOT EXISTS idx_price_date ON fact_price_daily(date);
