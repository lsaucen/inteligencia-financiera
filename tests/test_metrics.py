import numpy as np
import pandas as pd

from src import metrics


def test_max_drawdown_known_case():
    prices = pd.Series([100, 120, 60, 90])  # peak 120 -> trough 60 = -50%
    assert abs(metrics.max_drawdown(prices) - (-0.50)) < 1e-9


def test_annualized_vol_of_constant_is_zero():
    rets = pd.Series([0.01] * 100)
    assert abs(metrics.annualized_vol(rets)) < 1e-12


def test_sharpe_sign():
    up = pd.Series(np.random.default_rng(1).normal(0.001, 0.01, 1000))
    assert metrics.sharpe(up) > 0


def test_bootstrap_ci_contains_point_estimate():
    rets = pd.Series(np.random.default_rng(2).normal(0.0005, 0.01, 2000))
    lo, hi = metrics.block_bootstrap_ci(rets, metrics.sharpe)
    assert lo < metrics.sharpe(rets) < hi


def test_bootstrap_reproducible():
    rets = pd.Series(np.random.default_rng(3).normal(0, 0.01, 500))
    assert metrics.block_bootstrap_ci(
        rets, metrics.sharpe
    ) == metrics.block_bootstrap_ci(rets, metrics.sharpe)
