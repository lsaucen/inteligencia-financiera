"""Financial metrics. All functions operate on pandas Series indexed by date."""

import numpy as np
import pandas as pd

from src.db import get_engine

TRADING_DAYS = 252


def get_prices(tickers: list[str] | None = None) -> pd.DataFrame:
    q = "SELECT ticker, date, adj_close FROM v_daily_returns"
    if tickers:
        q += " WHERE ticker IN %(t)s"
    df = pd.read_sql(q, get_engine(), params={"t": tuple(tickers)} if tickers else None)
    return df.pivot(index="date", columns="ticker", values="adj_close")


def annualized_return(prices: pd.Series) -> float:
    prices = prices.dropna()
    years = len(prices) / TRADING_DAYS
    return (prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1


def annualized_vol(returns: pd.Series) -> float:
    return float(returns.dropna().std(ddof=1) * np.sqrt(TRADING_DAYS))


def sharpe(returns: pd.Series, rf_annual: float = 0.0) -> float:
    r = returns.dropna()
    excess = r - rf_annual / TRADING_DAYS
    if excess.std(ddof=1) == 0:
        return 0.0
    return float(excess.mean() / excess.std(ddof=1) * np.sqrt(TRADING_DAYS))


def sortino(returns: pd.Series, rf_annual: float = 0.0) -> float:
    r = returns.dropna()
    excess = r - rf_annual / TRADING_DAYS
    downside = excess[excess < 0].std(ddof=1)
    if downside == 0 or np.isnan(downside):
        return np.nan
    return float(excess.mean() / downside * np.sqrt(TRADING_DAYS))


def max_drawdown(prices: pd.Series) -> float:
    p = prices.dropna()
    return float((p / p.cummax() - 1).min())


def block_bootstrap_ci(
    returns: pd.Series, stat_fn, n_boot: int = 2000, block: int = 21, seed: int = 42
) -> tuple[float, float]:
    """Circular block bootstrap 95% CI, preserves short-range autocorrelation."""
    r = returns.dropna().to_numpy()
    n = len(r)
    rng = np.random.default_rng(seed)
    stats = np.empty(n_boot)
    n_blocks = int(np.ceil(n / block))
    for i in range(n_boot):
        starts = rng.integers(0, n, n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % n
        stats[i] = stat_fn(pd.Series(r[idx[:n]]))
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))
