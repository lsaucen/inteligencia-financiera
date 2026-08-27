"""Download macro series from FRED public CSV endpoint (no API key)."""

import io

import pandas as pd
import requests
import yaml
from sqlalchemy import text

from src.db import get_engine
from src.ingest.yahoo import _upsert

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"


def parse_fred_csv(csv_text: str, series_id: str) -> pd.DataFrame:
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = ["date", "value"]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")  # "." -> NaN
    df = df.dropna(subset=["value"])
    df["series_id"] = series_id
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df[["series_id", "date", "value"]]


def fetch_series(series_id: str) -> pd.DataFrame:
    resp = requests.get(FRED_CSV.format(sid=series_id), timeout=60)
    resp.raise_for_status()
    return parse_fred_csv(resp.text, series_id)


def ingest_macro(config_path: str = "config/assets.yml") -> int:
    with open(config_path, encoding="utf-8") as f:
        series = yaml.safe_load(f)["macro_series"]
    total = 0
    with get_engine().begin() as conn:
        for s in series:
            conn.execute(
                text(
                    "INSERT INTO dim_macro_series (series_id, name, unit, frequency) "
                    "VALUES (:series_id, :name, :unit, :frequency) "
                    "ON CONFLICT (series_id) DO UPDATE SET name=EXCLUDED.name"
                ),
                s,
            )
    for s in series:
        df = fetch_series(s["series_id"])
        total += _upsert(df, "raw_macro", ["series_id", "date"])
        print(f"{s['series_id']}: {len(df)} rows")
    return total


if __name__ == "__main__":
    print(f"macro rows: {ingest_macro()}")
