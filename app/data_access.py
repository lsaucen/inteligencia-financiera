"""Dual data access: Postgres locally, Parquet snapshot when deployed."""

import os
from pathlib import Path

import pandas as pd

SNAP = Path(__file__).resolve().parent.parent / "data" / "snapshots"


class DataAccess:
    def __init__(self, use_snapshot: bool | None = None):
        if use_snapshot is None:
            use_snapshot = (
                os.environ.get("FINZ_USE_SNAPSHOT") == "1" or not self._db_reachable()
            )
        self.use_snapshot = use_snapshot

    @staticmethod
    def _db_reachable() -> bool:
        try:
            from src.db import get_engine

            with get_engine().connect():
                return True
        except Exception:
            return False

    def _load(self, name: str, query: str) -> pd.DataFrame:
        if self.use_snapshot:
            return pd.read_parquet(SNAP / f"{name}.parquet")
        from src.db import get_engine

        return pd.read_sql(query, get_engine())

    def prices(self) -> pd.DataFrame:
        return self._load(
            "prices", "SELECT ticker, date, adj_close, ret FROM v_daily_returns"
        )

    def monthly(self) -> pd.DataFrame:
        return self._load(
            "monthly",
            "SELECT ticker, month_end, adj_close_eom, monthly_ret FROM v_monthly_returns",
        )

    def assets(self) -> pd.DataFrame:
        return self._load(
            "assets",
            "SELECT ticker, name, asset_type, sector, first_date, last_date FROM dim_asset",
        )
