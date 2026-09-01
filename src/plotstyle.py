"""Publication-quality matplotlib style shared by the project figures.

Recessive axes, generous type, high DPI, colourblind-safe accents, and a
title/subtitle helper that never overlaps the plot.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK = "#12261E"
MUTED = "#5C6B62"
GRID = "#E4E9E2"
ACCENT = "#2A5D8F"  # steel blue
ACCENT2 = "#1D6F42"  # green
POSITIVE = "#1D6F42"
REFERENCE = "#B23A48"  # muted red for reference lines

_BASE = {
    "figure.facecolor": "#FFFFFF",
    "axes.facecolor": "#FFFFFF",
    "savefig.facecolor": "#FFFFFF",
    "savefig.dpi": 220,
    "figure.dpi": 130,
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica", "Segoe UI"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.labelcolor": MUTED,
    "axes.edgecolor": MUTED,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.frameon": False,
    "legend.fontsize": 10,
}


def apply() -> None:
    plt.rcParams.update(_BASE)


def titles(
    fig,
    title: str,
    subtitle: str,
    x: float = 0.04,
    y_title: float = 0.965,
    y_sub: float = 0.915,
) -> None:
    fig.text(
        x,
        y_title,
        title,
        ha="left",
        va="top",
        fontsize=14.5,
        fontweight="bold",
        color=INK,
    )
    fig.text(x, y_sub, subtitle, ha="left", va="top", fontsize=10.5, color=MUTED)


def caption(fig, text: str, y: float = 0.012) -> None:
    fig.text(
        0.5,
        y,
        text,
        ha="center",
        va="bottom",
        fontsize=8.5,
        color=MUTED,
        style="italic",
    )
