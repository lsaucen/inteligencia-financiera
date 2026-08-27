# Capa SQL analítica

Las vistas de `sql/02_views.sql` calculan las métricas base directamente en PostgreSQL con window functions. Este documento explica la técnica detrás de cada una.

## v_daily_returns: retornos con LAG

El retorno diario es el cambio porcentual respecto al cierre anterior del mismo activo. `LAG(adj_close) OVER (PARTITION BY asset_id ORDER BY date)` obtiene el precio previo sin necesidad de self-join, y la cláusula `WINDOW` nombrada evita repetir la definición de la ventana para el retorno simple y el logarítmico. La primera fila de cada activo queda en NULL por diseño: no existe día anterior.

## v_rolling_metrics: ventanas móviles con frames

Las medias móviles de 50 y 200 días y la volatilidad rolling de 63 días usan frames explícitos (`ROWS BETWEEN 49 PRECEDING AND CURRENT ROW`). La distinción entre `ROWS` y el default `RANGE` importa: `ROWS` cuenta filas exactas (días de mercado), que es la semántica correcta para indicadores técnicos. La volatilidad se anualiza multiplicando por la raíz de 252 días hábiles.

## v_drawdown: máximo acumulado

El drawdown es la caída desde el máximo histórico hasta la fecha. `MAX(adj_close) OVER (PARTITION BY asset_id ORDER BY date)` sin frame explícito usa el default (desde el inicio de la partición hasta la fila actual), que es exactamente el "máximo hasta hoy". El drawdown es entonces `precio / máximo_acumulado - 1`, siempre menor o igual a cero.

## v_monthly_returns: agregación a fin de mes

Un CTE identifica el último día hábil de cada mes por activo (`MAX(date)` agrupado por `date_trunc('month', ...)`), y un join de vuelta a los datos diarios recupera el precio de ese día. Sobre esa serie mensual, `LAG` produce el retorno mensual. Esta vista alimenta el backtest DCA y los análisis de ventanas rolling largas, donde la granularidad diaria solo agrega ruido.

## Validación

Estas vistas no se aceptan por inspección: `tests/test_sql_vs_pandas.py` recalcula retornos y drawdown en pandas desde los mismos precios y exige coincidencia a 1e-9. La lógica SQL y la lógica Python se verifican mutuamente.
