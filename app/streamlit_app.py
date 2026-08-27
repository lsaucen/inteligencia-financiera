"""Interactive dashboard: asset explorer, risk comparison, DCA simulator, correlations."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.data_access import DataAccess
from src import metrics
from src.backtest import simulate_dca_from_prices

st.set_page_config(page_title="Inteligencia financiera", layout="wide")


@st.cache_data(show_spinner="Cargando datos...")
def load_data():
    da = DataAccess()
    prices = da.prices()
    prices["date"] = pd.to_datetime(prices["date"])
    monthly = da.monthly()
    monthly["month_end"] = pd.to_datetime(monthly["month_end"])
    assets = da.assets()
    return prices, monthly, assets, da.use_snapshot


prices, monthly, assets, from_snapshot = load_data()
wide_prices = prices.pivot(index="date", columns="ticker", values="adj_close")
wide_monthly = monthly.pivot(index="month_end", columns="ticker", values="monthly_ret")

st.title("Inteligencia financiera del mercado bursátil")
st.caption(
    "Riesgo, comparación y asignación de activos sobre 24 activos y 25+ años de datos. "
    f"Fuente: {'snapshot Parquet' if from_snapshot else 'PostgreSQL local'}. "
    "Metodología y análisis completos en el repositorio."
)

tab_exp, tab_cmp, tab_dca, tab_corr = st.tabs(
    ["Explorador", "Comparador de riesgo", "Simulador DCA", "Correlaciones"]
)

with tab_exp:
    col1, col2 = st.columns([1, 3])
    with col1:
        tk = st.selectbox(
            "Activo",
            sorted(wide_prices.columns),
            index=None,
            placeholder="Elige un activo",
        )
        if tk:
            info = assets.set_index("ticker").loc[tk]
            st.metric("Nombre", info["name"])
            st.metric("Tipo", info["asset_type"])
    if tk:
        p = wide_prices[tk].dropna()
        years = st.slider(
            "Años hacia atrás",
            1,
            max(int(len(p) / 252), 1),
            min(10, max(int(len(p) / 252), 1)),
        )
        p = p.iloc[-years * 252 :]
        r = p.pct_change()
        dd = p / p.cummax() - 1
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=p.index, y=p, name="Precio ajustado"))
            fig.update_layout(
                height=300, margin=dict(t=30, b=0), title=f"{tk}: precio ajustado"
            )
            st.plotly_chart(fig, use_container_width=True)
            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=dd.index,
                    y=dd * 100,
                    fill="tozeroy",
                    line_color="crimson",
                    name="Drawdown",
                )
            )
            fig2.update_layout(
                height=220, margin=dict(t=30, b=0), title="Drawdown desde máximo (%)"
            )
            st.plotly_chart(fig2, use_container_width=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Retorno anualizado", f"{metrics.annualized_return(p):.1%}")
        c2.metric("Volatilidad anualizada", f"{metrics.annualized_vol(r):.1%}")
        c3.metric("Sharpe", f"{metrics.sharpe(r):.2f}")
        c4.metric("Máximo drawdown", f"{metrics.max_drawdown(p):.1%}")

with tab_cmp:
    sel = st.multiselect(
        "Activos a comparar",
        sorted(wide_prices.columns),
        default=["SPY", "QQQ", "TLT", "GLD"],
    )
    if sel:
        rows = []
        for t in sel:
            p = wide_prices[t].dropna()
            r = p.pct_change()
            rows.append(
                {
                    "ticker": t,
                    "retorno_anual": metrics.annualized_return(p),
                    "volatilidad": metrics.annualized_vol(r),
                    "sharpe": metrics.sharpe(r),
                    "sortino": metrics.sortino(r),
                    "max_drawdown": metrics.max_drawdown(p),
                }
            )
        tbl = pd.DataFrame(rows).set_index("ticker")
        st.dataframe(
            tbl.style.format(
                "{:.2%}", subset=["retorno_anual", "volatilidad", "max_drawdown"]
            ).format("{:.2f}", subset=["sharpe", "sortino"])
        )
        fig = px.scatter(
            tbl.reset_index(),
            x="volatilidad",
            y="retorno_anual",
            text="ticker",
            size=[20] * len(tbl),
            labels={
                "volatilidad": "Volatilidad anualizada",
                "retorno_anual": "Retorno anualizado",
            },
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(
            height=420, title="Riesgo vs retorno (historia completa de cada activo)"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Nota: cada activo usa su historia completa; los inicios difieren (ver notebook RQ0)."
        )

with tab_dca:
    c1, c2, c3 = st.columns(3)
    monto = c1.number_input("Aporte mensual (USD)", 10, 10000, 100, step=10)
    tk_dca = c2.selectbox(
        "Destino",
        sorted(wide_monthly.columns),
        index=sorted(wide_monthly.columns).index("SPY"),
    )
    eom = (
        monthly[monthly["ticker"] == tk_dca]
        .set_index("month_end")["adj_close_eom"]
        .dropna()
    )
    yrs = c3.slider(
        "Duración (años)", 1, max(len(eom) // 12, 1), min(20, max(len(eom) // 12, 1))
    )
    window = eom.iloc[-yrs * 12 :]
    res = simulate_dca_from_prices(window, monto)
    final, contrib = res["value"].iloc[-1], res["contributed"].iloc[-1]
    st.subheader(
        f"{monto} USD/mes en {tk_dca} durante los últimos {yrs} años: "
        f"{final:,.0f} USD (aportaste {contrib:,.0f})"
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=res.index, y=res["value"], name="Valor de la cartera"))
    fig.add_trace(
        go.Scatter(
            x=res.index,
            y=res["contributed"],
            name="Aportado acumulado",
            line=dict(dash="dash"),
        )
    )
    fig.update_layout(height=400, margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Dividendos reinvertidos (precios ajustados). Ventana = últimos N años; "
        "el notebook RQ3 analiza TODAS las ventanas históricas, no solo la más reciente."
    )

with tab_corr:
    yrs_c = st.slider("Ventana (años)", 2, 25, 10)
    cutoff = wide_monthly.index.max() - pd.DateOffset(years=yrs_c)
    sub = wide_monthly[wide_monthly.index > cutoff]
    corr = sub.corr()
    fig = px.imshow(
        corr,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        text_auto=".2f",
        aspect="auto",
    )
    fig.update_layout(
        height=650, title=f"Correlación de retornos mensuales (últimos {yrs_c} años)"
    )
    fig.update_traces(textfont_size=8)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("El análisis por régimen de inflación está en el notebook RQ2.")
