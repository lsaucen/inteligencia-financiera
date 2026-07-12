"""Download OHLCV prices and dividends from Yahoo Finance into raw tables."""

import sys

import pandas as pd
import yaml
import yfinance as yf
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert

from src.db import get_engine


def load_universe(config_path: str = "config/assets.yml") -> list[dict]:
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)["assets"]


def _upsert(df: pd.DataFrame, table_name: str, keys: list[str]) -> int:
    if df.empty:
        return 0
    meta = MetaData()
    table = Table(table_name, meta, autoload_with=get_engine())
    rows = df.to_dict(orient="records")
    stmt = insert(table).values(rows)
    update_cols = {
        c.name: stmt.excluded[c.name]
        for c in table.columns
        if c.name not in keys + ["loaded_at"]
    }
    stmt = stmt.on_conflict_do_update(index_elements=keys, set_=update_cols)
    with get_engine().begin() as conn:
        conn.execute(stmt)
    return len(rows)


def upsert_prices(df: pd.DataFrame) -> int:
    return _upsert(df, "raw_prices", ["ticker", "date"])


def upsert_dividends(df: pd.DataFrame) -> int:
    return _upsert(df, "raw_dividends", ["ticker", "date"])


def ingest_prices(tickers: list[str]) -> int:
    total = 0
    for t in tickers:
        hist = yf.Ticker(t).history(period="max", auto_adjust=False)
        if hist.empty:
            print(f"WARN no data for {t}", file=sys.stderr)
            continue
        df = hist.reset_index()
        df["ticker"] = t
        df["date"] = pd.to_datetime(df["Date"]).dt.date
        df = df.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )
        cols = ["ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]
        total += upsert_prices(df[cols].dropna(subset=["adj_close"]))
        print(f"{t}: {len(df)} rows")
    return total


def ingest_dividends(tickers: list[str]) -> int:
    total = 0
    for t in tickers:
        div = yf.Ticker(t).dividends
        if div.empty:
            continue
        df = div.reset_index()
        df.columns = ["date", "amount"]
        df["ticker"] = t
        df["date"] = pd.to_datetime(df["date"]).dt.date
        total += upsert_dividends(df[["ticker", "date", "amount"]])
    return total


if __name__ == "__main__":
    universe_tickers = [a["ticker"] for a in load_universe()]
    print(f"prices rows: {ingest_prices(universe_tickers)}")
    print(f"dividend rows: {ingest_dividends(universe_tickers)}")
