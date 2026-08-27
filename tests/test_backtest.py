import pandas as pd

from src.backtest import simulate_dca_from_prices


def test_dca_flat_price_no_dividends():
    # price constant at 100, 12 monthly buys of 100 USD -> 12 shares, value 1200
    prices = pd.Series(
        [100.0] * 12, index=pd.date_range("2020-01-31", periods=12, freq="ME")
    )
    result = simulate_dca_from_prices(prices, monthly_usd=100)
    assert abs(result["value"].iloc[-1] - 1200) < 1e-9
    assert abs(result["contributed"].iloc[-1] - 1200) < 1e-9


def test_dca_price_doubles():
    # 2 buys: 100 USD at price 100 (1 share), 100 USD at price 200 (0.5 share)
    # final value = 1.5 shares * 200 = 300
    prices = pd.Series(
        [100.0, 200.0], index=pd.date_range("2020-01-31", periods=2, freq="ME")
    )
    result = simulate_dca_from_prices(prices, monthly_usd=100)
    assert abs(result["value"].iloc[-1] - 300) < 1e-9
