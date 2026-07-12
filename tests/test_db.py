from sqlalchemy import inspect

from src.db import get_engine, run_sql_file

EXPECTED_TABLES = {
    "raw_prices",
    "raw_dividends",
    "raw_macro",
    "dim_asset",
    "fact_price_daily",
    "fact_dividend",
    "dim_macro_series",
    "fact_macro_value",
}


def test_schema_creates_all_tables():
    run_sql_file("sql/01_schema.sql")
    tables = set(inspect(get_engine()).get_table_names())
    assert EXPECTED_TABLES <= tables
