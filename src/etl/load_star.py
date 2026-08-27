"""Transform raw landing tables into the star schema. Pure SQL, idempotent."""

from sqlalchemy import text

from src.db import get_engine
from src.ingest.yahoo import load_universe

UPSERT_DIM_ASSET = text("""
    INSERT INTO dim_asset (ticker, name, asset_type, sector)
    VALUES (:ticker, :name, :type, :sector)
    ON CONFLICT (ticker) DO UPDATE
        SET name = EXCLUDED.name, asset_type = EXCLUDED.asset_type,
            sector = EXCLUDED.sector
""")

LOAD_PRICES = text("""
    INSERT INTO fact_price_daily
        (asset_id, date, open, high, low, close, adj_close, volume)
    SELECT a.asset_id, r.date, r.open, r.high, r.low, r.close, r.adj_close, r.volume
    FROM raw_prices r
    JOIN dim_asset a ON a.ticker = r.ticker
    WHERE r.adj_close IS NOT NULL
    ON CONFLICT (asset_id, date) DO UPDATE
        SET adj_close = EXCLUDED.adj_close, close = EXCLUDED.close,
            open = EXCLUDED.open, high = EXCLUDED.high,
            low = EXCLUDED.low, volume = EXCLUDED.volume
""")

LOAD_DIVIDENDS = text("""
    INSERT INTO fact_dividend (asset_id, date, amount)
    SELECT a.asset_id, r.date, r.amount
    FROM raw_dividends r JOIN dim_asset a ON a.ticker = r.ticker
    ON CONFLICT (asset_id, date) DO UPDATE SET amount = EXCLUDED.amount
""")

LOAD_MACRO = text("""
    INSERT INTO fact_macro_value (series_id, date, value)
    SELECT series_id, date, value FROM raw_macro
    ON CONFLICT (series_id, date) DO UPDATE SET value = EXCLUDED.value
""")

UPDATE_DATE_RANGE = text("""
    UPDATE dim_asset a SET
        first_date = s.min_d, last_date = s.max_d
    FROM (SELECT asset_id, min(date) min_d, max(date) max_d
          FROM fact_price_daily GROUP BY asset_id) s
    WHERE s.asset_id = a.asset_id
""")


def run_etl() -> dict:
    eng = get_engine()
    with eng.begin() as conn:
        for asset in load_universe():
            conn.execute(UPSERT_DIM_ASSET, asset)
        conn.execute(LOAD_PRICES)
        conn.execute(LOAD_DIVIDENDS)
        conn.execute(LOAD_MACRO)
        conn.execute(UPDATE_DATE_RANGE)
    with eng.connect() as conn:
        return {
            t: conn.execute(text(f"SELECT count(*) FROM {t}")).scalar()
            for t in [
                "dim_asset",
                "fact_price_daily",
                "fact_dividend",
                "fact_macro_value",
            ]
        }


if __name__ == "__main__":
    for table, n in run_etl().items():
        print(f"{table}: {n}")
