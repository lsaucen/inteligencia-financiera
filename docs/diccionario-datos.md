# Diccionario de datos

Base de datos PostgreSQL `finanzas`. Fuentes: Yahoo Finance (precios y dividendos, vía yfinance) y FRED (series macro, vía CSV público). Todas las tablas se pueblan con procesos idempotentes: re-ejecutar la ingesta o el ETL no duplica filas.

## Tablas de aterrizaje (raw)

### raw_prices

Precios diarios tal como llegan de Yahoo Finance, sin transformar.

| Columna | Tipo | Descripción |
|---|---|---|
| ticker | TEXT | Símbolo del activo (PK compuesta con date) |
| date | DATE | Fecha de la sesión |
| open, high, low, close | DOUBLE PRECISION | Precios de la sesión sin ajustar |
| adj_close | DOUBLE PRECISION | Cierre ajustado por splits y dividendos |
| volume | BIGINT | Volumen negociado |
| loaded_at | TIMESTAMPTZ | Momento de carga (auditoría) |

### raw_dividends

| Columna | Tipo | Descripción |
|---|---|---|
| ticker | TEXT | Símbolo del activo (PK compuesta con date) |
| date | DATE | Fecha ex-dividendo |
| amount | DOUBLE PRECISION | Monto por acción en USD |
| loaded_at | TIMESTAMPTZ | Momento de carga |

### raw_macro

| Columna | Tipo | Descripción |
|---|---|---|
| series_id | TEXT | Identificador FRED (PK compuesta con date) |
| date | DATE | Fecha de la observación |
| value | DOUBLE PRECISION | Valor; las marcas "." de FRED se descartan en la ingesta |
| loaded_at | TIMESTAMPTZ | Momento de carga |

## Esquema estrella

### dim_asset

Dimensión de activos. Fuente: `config/assets.yml` + rangos calculados por el ETL.

| Columna | Tipo | Descripción |
|---|---|---|
| asset_id | SERIAL | Clave sustituta (PK) |
| ticker | TEXT | Símbolo único |
| name | TEXT | Nombre del instrumento |
| asset_type | TEXT | etf_core, etf_sector, etf_intl, etf_bond, commodity, stock |
| sector | TEXT | Sector GICS aproximado (solo sectoriales y acciones) |
| first_date, last_date | DATE | Rango de precios disponible (mantenido por el ETL) |

### fact_price_daily

Hechos de precio diario. Grano: activo x día. Se excluyen filas sin adj_close.

| Columna | Tipo | Descripción |
|---|---|---|
| asset_id | INT | FK a dim_asset (PK compuesta con date) |
| date | DATE | Fecha de la sesión |
| open, high, low, close | DOUBLE PRECISION | Precios sin ajustar |
| adj_close | DOUBLE PRECISION | Cierre ajustado (NOT NULL); base de todos los retornos |
| volume | BIGINT | Volumen |

### fact_dividend

Grano: activo x fecha ex-dividendo.

| Columna | Tipo | Descripción |
|---|---|---|
| asset_id | INT | FK a dim_asset (PK compuesta con date) |
| date | DATE | Fecha ex-dividendo |
| amount | DOUBLE PRECISION | USD por acción |

### dim_macro_series / fact_macro_value

Catálogo y valores de las series FRED.

| Serie | Nombre | Frecuencia |
|---|---|---|
| CPIAUCSL | CPI All Urban Consumers (índice 1982-84=100) | Mensual |
| FEDFUNDS | Tasa efectiva de fondos federales (%) | Mensual |
| DGS10 | Treasury a 10 años, vencimiento constante (%) | Diaria |
| UNRATE | Tasa de desempleo (%) | Mensual |

## Vistas analíticas

| Vista | Grano | Columnas clave | Técnica SQL |
|---|---|---|---|
| v_daily_returns | activo x día | ret, log_ret | LAG sobre ventana particionada |
| v_rolling_metrics | activo x día | ma_50, ma_200, vol_63d_ann | Window frames ROWS BETWEEN |
| v_drawdown | activo x día | cum_max, drawdown | MAX acumulado OVER |
| v_monthly_returns | activo x mes | adj_close_eom, monthly_ret | CTE de fin de mes + LAG |

Detalle de cada técnica en `sql/analysis/README.md`. La equivalencia entre estas vistas y los cálculos en pandas se verifica en `tests/test_sql_vs_pandas.py` con tolerancia 1e-9.

## Convenciones

- **Retornos**: simples salvo indicación; `adj_close` como proxy de retorno total (dividendos reinvertidos).
- **Anualización**: 252 días hábiles; volatilidad mensual x raíz de 12.
- **Sin look-ahead**: ningún cálculo usa información posterior a la fecha de cada fila.
