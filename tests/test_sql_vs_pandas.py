"""Cross-validate SQL views against pandas computations (spec requirement)."""

import pandas as pd

from src import metrics
from src.db import get_engine


def test_sql_drawdown_matches_pandas():
    sql_dd = pd.read_sql(
        "SELECT min(drawdown) FROM v_drawdown WHERE ticker='SPY'", get_engine()
    ).iloc[0, 0]
    prices = metrics.get_prices(["SPY"])["SPY"]
    assert abs(sql_dd - metrics.max_drawdown(prices)) < 1e-9


def test_sql_returns_match_pandas():
    sql = pd.read_sql(
        "SELECT date, ret FROM v_daily_returns WHERE ticker='SPY' ORDER BY date",
        get_engine(),
    ).set_index("date")["ret"]
    prices = metrics.get_prices(["SPY"])["SPY"].sort_index()
    pd_ret = prices.pct_change()
    diff = (sql - pd_ret).abs().max()
    assert diff < 1e-9
