"""Dollar-cost-averaging backtests over end-of-month adjusted prices.

Uses adj_close as the total-return proxy: price adjustment already folds in
reinvested dividends. No look-ahead: each buy uses only that month's closing
price.
"""

import pandas as pd

from src.db import get_engine


def simulate_dca_from_prices(prices: pd.Series, monthly_usd: float) -> pd.DataFrame:
    prices = prices.dropna()
    shares = (monthly_usd / prices).cumsum()
    return pd.DataFrame(
        {
            "contributed": monthly_usd * pd.RangeIndex(1, len(prices) + 1),
            "shares": shares,
            "value": shares * prices,
        },
        index=prices.index,
    )


def _eom_prices(ticker: str) -> pd.Series:
    q = (
        "SELECT month_end, adj_close_eom FROM v_monthly_returns "
        "WHERE ticker = %(t)s ORDER BY month_end"
    )
    df = pd.read_sql(q, get_engine(), params={"t": ticker})
    return df.set_index("month_end")["adj_close_eom"]


def dca(ticker: str, monthly_usd: float, start: str, end: str) -> pd.DataFrame:
    prices = _eom_prices(ticker).loc[start:end]
    return simulate_dca_from_prices(prices, monthly_usd)


def lump_sum(ticker: str, usd: float, start: str, end: str) -> float:
    prices = _eom_prices(ticker).loc[start:end]
    return float(usd * prices.iloc[-1] / prices.iloc[0])


def dca_all_windows(ticker: str, monthly_usd: float, years: int) -> pd.DataFrame:
    prices = _eom_prices(ticker)
    months = years * 12
    rows = []
    for i in range(len(prices) - months):
        window = prices.iloc[i : i + months]
        res = simulate_dca_from_prices(window, monthly_usd)
        contributed = res["contributed"].iloc[-1]
        final = res["value"].iloc[-1]
        rows.append(
            {
                "start": window.index[0],
                "end": window.index[-1],
                "contributed": contributed,
                "final_value": final,
                "money_multiple": final / contributed,
            }
        )
    return pd.DataFrame(rows)
