# Inteligencia financiera del mercado bursátil

Sistema de análisis de riesgo, comparación y asignación de activos construido con Python y PostgreSQL: pipeline ETL idempotente, capa analítica en SQL con window functions, cinco preguntas de investigación contrastadas con rigor estadístico, dashboard interactivo en Streamlit y reporte Power BI.

**Metodología**: CRISP-DM + diseño hipotético-deductivo. Cinco hipótesis formuladas a priori; tres confirmadas y dos refutadas por los datos.

## Hallazgos principales

1. **El riesgo sectorial extra no se paga.** Entre los sectores del S&P 500, más volatilidad correlacionó con peor retorno ajustado (Spearman rho = -0.85, p = 0.004). Salud y consumo básico ofrecieron el mejor Sharpe; financieras y energía, el peor.
2. **Los bonos protegen solo cuando la inflación es baja.** La correlación SPY-TLT pasa de -0.28 (inflación baja) a +0.09 (alta), y llegó a +0.54 en 2021-2023 (Fisher z = 3.18, p = 0.0015). El pilar defensivo del 60/40 se debilita exactamente cuando más se necesita.
3. **El destino pesa más que el momento.** Aportando 100 USD/mes, la elección del activo importó 4-10 veces más que la fecha de inicio. Ninguna ventana histórica de 20 años (SPY, QQQ, oro o 60/40) terminó perdiendo dinero nominal.
4. **"Ganarle al mercado" fue posible solo concentrándose en tecnología.** QQQ superó a SPY en el 84% de las ventanas de 5 años y XLK en el 76% (sobreviven Bonferroni y bootstrap en bloques); ningún otro activo del universo lo logró de forma consistente.
5. **La rotación sectorial por momentum no funcionó**: -1.1% anual antes de costos en 27 años, con IC que incluye al cero en todas las variantes probadas.

<p align="center">
  <img src="docs/img/rq1_vol_sharpe.png" width="46%" alt="Volatilidad vs Sharpe por sector">
  <img src="docs/img/rq3_dca_windows.png" width="46%" alt="Múltiplo DCA por fecha de inicio">
</p>

Informe completo con métodos, robustez y limitaciones: [docs/informe-ejecutivo.md](docs/informe-ejecutivo.md).

## Arquitectura

```mermaid
flowchart LR
    A[Yahoo Finance<br/>yfinance] --> C[raw_prices<br/>raw_dividends]
    B[FRED<br/>CSV publico] --> D[raw_macro]
    C --> E[ETL SQL idempotente]
    D --> E
    E --> F[(Esquema estrella<br/>PostgreSQL)]
    F --> G[Vistas SQL<br/>window functions]
    G --> H[Notebooks RQ0-RQ5<br/>hipotesis + bootstrap]
    G --> I[Snapshot Parquet]
    G --> J[Dashboard Streamlit]
    I --> J
    F --> K[Reporte Power BI]
```

- **Ingesta** (`src/ingest/`): descarga con upserts idempotentes (`ON CONFLICT`).
- **ETL** (`src/etl/`): transformación raw a estrella en SQL puro.
- **Capa SQL** (`sql/`): retornos, medias móviles, drawdown y agregación mensual con window functions, documentadas en [sql/analysis/README.md](sql/analysis/README.md) y validadas contra pandas (1e-9) en tests.
- **Análisis** (`notebooks/`): un notebook por pregunta, con hipótesis a priori, IC bootstrap en bloques, robustez por subperiodos y conclusiones.
- **App** (`app/`): Streamlit con acceso dual (Postgres en local, Parquet desplegada).
- **Diccionario de datos**: [docs/diccionario-datos.md](docs/diccionario-datos.md).

## Stack

Python 3.12, PostgreSQL 16, SQLAlchemy, pandas, scipy, matplotlib, plotly, Streamlit, pytest, Power BI. Versiones exactas en `requirements.txt`.

## Reproducir

Requiere PostgreSQL local con una base `finanzas` (conexión configurable vía `FINZ_DB_URL`; default `postgresql+psycopg2://postgres:postgres@localhost:5432/finanzas`).

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
psql -U postgres -c "CREATE DATABASE finanzas;"
.venv/Scripts/python -c "from src.db import run_sql_file; run_sql_file('sql/01_schema.sql'); run_sql_file('sql/02_views.sql')"
.venv/Scripts/python -m src.ingest.yahoo && .venv/Scripts/python -m src.ingest.fred
.venv/Scripts/python -m src.etl.load_star
.venv/Scripts/python -m pytest tests/
.venv/Scripts/streamlit run app/streamlit_app.py
```

Los notebooks corren de punta a punta con `jupyter nbconvert --execute`. Bootstrap con semilla fija: los IC del informe son regenerables.

## Descargo

Proyecto de análisis de datos con fines demostrativos. No constituye recomendación de inversión.
