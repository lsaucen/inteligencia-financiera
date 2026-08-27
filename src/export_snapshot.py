"""Export a Parquet snapshot of the analytical tables for the deployed app."""

from pathlib import Path

import pandas as pd

from src.db import get_engine

OUT = Path(__file__).resolve().parent.parent / "data" / "snapshots"

QUERIES = {
    "prices": "SELECT ticker, date, adj_close, ret FROM v_daily_returns",
    "monthly": (
        "SELECT ticker, month_end, adj_close_eom, monthly_ret FROM v_monthly_returns"
    ),
    "macro": "SELECT series_id, date, value FROM fact_macro_value",
    "assets": (
        "SELECT ticker, name, asset_type, sector, first_date, last_date FROM dim_asset"
    ),
}


def export_snapshot() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, q in QUERIES.items():
        pd.read_sql(q, get_engine()).to_parquet(OUT / f"{name}.parquet", index=False)
        print(f"wrote {name}.parquet")


if __name__ == "__main__":
    export_snapshot()
