import pandas as pd

from src.db import get_engine, run_sql_file


def setup_module():
    run_sql_file("sql/02_views.sql")


def test_daily_returns_sane():
    df = pd.read_sql(
        "SELECT * FROM v_daily_returns WHERE ticker='SPY' ORDER BY date", get_engine()
    )
    assert df["ret"].iloc[0] != df["ret"].iloc[0]  # first row is NaN (no prior day)
    assert df["ret"].abs().max() < 0.5  # no absurd daily moves in SPY


def test_drawdown_bounds():
    df = pd.read_sql("SELECT drawdown FROM v_drawdown WHERE ticker='SPY'", get_engine())
    assert df["drawdown"].max() <= 0.0000001
    assert df["drawdown"].min() > -0.70  # SPY never lost 70% peak-to-trough
