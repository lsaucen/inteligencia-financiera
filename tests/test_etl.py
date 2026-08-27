from sqlalchemy import text

from src.db import get_engine
from src.etl.load_star import run_etl


def test_etl_populates_star_and_is_idempotent():
    counts1 = run_etl()
    assert counts1["dim_asset"] >= 20
    assert counts1["fact_price_daily"] > 50_000
    counts2 = run_etl()
    assert counts2 == counts1  # idempotent


def test_no_orphan_facts():
    with get_engine().connect() as c:
        orphans = c.execute(
            text(
                "SELECT count(*) FROM fact_price_daily f "
                "LEFT JOIN dim_asset a USING (asset_id) WHERE a.asset_id IS NULL"
            )
        ).scalar()
    assert orphans == 0
