# Reporte Power BI (finanzas.pbip)

Reporte ejecutivo en formato PBIP (proyecto Power BI en texto, versionable) conectado al mismo PostgreSQL local del proyecto. Complementa al dashboard Streamlit demostrando el modelado semántico y DAX.

## Estructura

- `finanzas.SemanticModel/` — modelo semántico en TMDL:
  - Tablas importadas desde Postgres vía Power Query M: `dim_asset`, `v_monthly_returns`, `v_drawdown`.
  - Relaciones por `ticker` (dim_asset uno a varios).
  - Medidas DAX (carpeta "Métricas"): `Retorno acumulado %`, `Volatilidad anualizada`, `Retorno mensual medio`, `Precio fin de mes`, `Máximo drawdown`.
- `finanzas.Report/` — reporte PBIR con 3 páginas:
  1. **Resumen de mercado**: tarjetas de las medidas clave, línea de precio por activo (con filtro de activo).
  2. **Riesgo y retorno**: dispersión volatilidad vs retorno y tabla de métricas por activo.
  3. **Drawdown y riesgo de caída**: barras de máximo drawdown por activo y evolución temporal filtrable.

## Requisitos para abrirlo

1. Tener poblada la base `finanzas` en PostgreSQL local (ver README raíz: ingesta + ETL + vistas).
2. Power BI Desktop con el conector de PostgreSQL. La primera vez pedirá instalar el proveedor Npgsql; acéptalo.
3. Abrir `finanzas.pbip` en Power BI Desktop y pulsar **Actualizar** para cargar los datos desde Postgres (el proyecto guarda solo metadatos, no datos).

## Notas

- La cadena de conexión M apunta a `localhost:5432`, base `finanzas`. Ajústala en cada partición si tu instancia usa otro host o puerto.
- Validado con `pbir validate --fields`: 3 páginas, 11 visuales, todas las referencias a campos resuelven contra el modelo.
- El tema base `CY24SU10` es un tema integrado de Power BI que Desktop resuelve internamente.
