import pandas as pd
from sqlalchemy import text

from src.db import get_engine
from src.ingest.yahoo import load_universe, upsert_prices


def _count(table):
    with get_engine().connect() as c:
        return c.execute(text(f"SELECT count(*) FROM {table}")).scalar()


def test_load_universe_reads_config():
    universe = load_universe()
    tickers = [a["ticker"] for a in universe]
    assert "SPY" in tickers and len(tickers) >= 20


def test_upsert_prices_is_idempotent():
    df = pd.DataFrame(
        {
            "ticker": ["TEST"],
            "date": ["2020-01-02"],
            "open": [1.0],
            "high": [1.1],
            "low": [0.9],
            "close": [1.05],
            "adj_close": [1.05],
            "volume": [100],
        }
    )
    try:
        upsert_prices(df)
        n1 = _count("raw_prices")
        upsert_prices(df)  # second run must not duplicate
        assert _count("raw_prices") == n1
    finally:
        with get_engine().begin() as c:
            c.execute(text("DELETE FROM raw_prices WHERE ticker = 'TEST'"))
