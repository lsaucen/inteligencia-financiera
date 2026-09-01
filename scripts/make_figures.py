"""Regenerate the report figures from the Parquet snapshots (no database needed).

Produces, with the shared publication style (src/plotstyle.py):
  docs/img/rq1_vol_sharpe.png   sector risk vs risk-adjusted return
  docs/img/rq3_dca_windows.png  DCA money multiple by start month (SPY, 20y)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import plotstyle  # noqa: E402
from src.backtest import simulate_dca_from_prices  # noqa: E402

plotstyle.apply()
SNAP = ROOT / "data" / "snapshots"
IMG = ROOT / "docs" / "img"
SECTORS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLP", "XLY", "XLU", "XLB"]


def _monthly_wide() -> pd.DataFrame:
    m = pd.read_parquet(SNAP / "monthly.parquet")
    m["month_end"] = pd.to_datetime(m["month_end"])
    return m.pivot(index="month_end", columns="ticker", values="monthly_ret")


def fig_sector_risk() -> None:
    wide = _monthly_wide()
    sec = wide[SECTORS].dropna()
    vol = sec.std(ddof=1) * np.sqrt(12)
    sharpe = sec.mean() / sec.std(ddof=1) * np.sqrt(12)
    rho, p = stats.spearmanr(vol, sharpe)

    fig, ax = plt.subplots(figsize=(8, 5.2))
    fig.subplots_adjust(top=0.80, bottom=0.13, left=0.10, right=0.97)
    ax.scatter(
        vol,
        sharpe,
        s=90,
        color=plotstyle.ACCENT,
        edgecolor="white",
        linewidth=1.1,
        zorder=3,
    )
    for tk in SECTORS:
        ax.annotate(
            tk,
            (vol[tk], sharpe[tk]),
            textcoords="offset points",
            xytext=(8, 4),
            fontsize=9.5,
            color=plotstyle.INK,
        )

    ax.set_xlabel("Volatilidad anualizada")
    ax.set_ylabel("Sharpe anualizado")
    ax.margins(0.12)
    plotstyle.titles(
        fig,
        "Más volatilidad no paga mejor",
        "Sectores del S&P 500 (1999-2026): riesgo vs retorno ajustado por riesgo",
    )
    plotstyle.caption(
        fig,
        f"Correlación de Spearman volatilidad vs Sharpe: rho = {rho:.2f} (p = {p:.2f}).",
    )
    fig.savefig(IMG / "rq1_vol_sharpe.png", bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def fig_dca_windows(years: int = 20, monthly_usd: float = 100) -> None:
    m = pd.read_parquet(SNAP / "monthly.parquet")
    m["month_end"] = pd.to_datetime(m["month_end"])
    spy = (
        m[m["ticker"] == "SPY"]
        .set_index("month_end")["adj_close_eom"]
        .dropna()
        .sort_index()
    )
    months = years * 12

    starts, mult = [], []
    for i in range(len(spy) - months + 1):
        w = spy.iloc[i : i + months]
        res = simulate_dca_from_prices(w, monthly_usd)
        starts.append(w.index[0])
        mult.append(res["value"].iloc[-1] / res["contributed"].iloc[-1])
    s = pd.Series(mult, index=pd.DatetimeIndex(starts))

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    fig.subplots_adjust(top=0.80, bottom=0.14, left=0.09, right=0.97)
    ax.plot(s.index, s.values, color=plotstyle.POSITIVE, linewidth=1.8, zorder=3)
    ax.fill_between(
        s.index,
        1.0,
        s.values,
        where=(s.values >= 1.0),
        color=plotstyle.POSITIVE,
        alpha=0.08,
        zorder=1,
    )
    ax.axhline(
        1.0, color=plotstyle.REFERENCE, linewidth=1.2, linestyle=(0, (4, 3)), zorder=2
    )
    ax.text(
        s.index[2],
        1.02,
        "Capital aportado (1.0x)",
        color=plotstyle.REFERENCE,
        fontsize=9,
        va="bottom",
    )

    ax.set_xlabel("Mes de inicio de la ventana")
    ax.set_ylabel("Valor final / aportado (x)")
    ax.margins(x=0.01)
    plotstyle.titles(
        fig,
        "Invertir $100 al mes en SPY por 20 años",
        "Múltiplo final del capital aportado, según el mes en que se empezó",
    )
    plotstyle.caption(
        fig,
        f"Cada punto: una ventana de {years} años terminando {years} años después de su inicio.",
    )
    fig.savefig(IMG / "rq3_dca_windows.png", bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    fig_sector_risk()
    fig_dca_windows()
    print("figures regenerated in", IMG)
