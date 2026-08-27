# Inteligencia financiera del mercado bursátil: informe ejecutivo

## Resumen

Este proyecto construye un sistema de análisis de riesgo, comparación y asignación de activos sobre 24 instrumentos (ETFs núcleo, sectoriales, internacionales, renta fija, oro y acciones de referencia) y 4 series macroeconómicas, con hasta 64 años de historia. Siguiendo CRISP-DM y un diseño hipotético-deductivo, se formularon cinco hipótesis a priori y se contrastaron con métodos estadísticos que cuantifican la incertidumbre (bootstrap en bloques, tests no paramétricos, corrección por comparaciones múltiples). Tres hipótesis se confirmaron y dos se refutaron. Los hallazgos centrales: el riesgo sectorial extra no se paga en términos ajustados; los bonos pierden su poder diversificador justo cuando la inflación aprieta; la elección del destino de inversión pesó entre 4 y 10 veces más que el momento de entrada; solo la apuesta tecnológica (QQQ/XLK) superó consistentemente al S&P 500; y la rotación sectorial por momentum no generó valor en 27 años.

## Metodología

- **Marco**: CRISP-DM completo, del entendimiento del problema al despliegue (dashboard Streamlit y reporte Power BI).
- **Datos**: precios diarios y dividendos de Yahoo Finance; CPI, tasa de la Fed, Treasury 10 años y desempleo de FRED. Pipeline ETL idempotente hacia un esquema estrella en PostgreSQL; capa analítica en vistas SQL con window functions, validada contra pandas con tolerancia 1e-9.
- **Diseño**: una pregunta de investigación por notebook (RQ0-RQ5), con hipótesis registrada antes de calcular, método definido a priori, robustez por subperiodos y limitaciones explícitas.
- **Rigor**: sin look-ahead en ninguna señal; ventanas móviles exhaustivas en lugar de fechas elegidas; IC 95% por bootstrap en bloques (respeta autocorrelación); Bonferroni donde hay comparaciones múltiples; semillas fijas y entorno pineado para reproducibilidad.

## Resultados por pregunta

### RQ1. ¿El mayor riesgo sectorial se compensa? — H1 CONFIRMADA

Entre los 9 sectores del S&P 500 (1999-2026), la volatilidad correlaciona positivamente con el retorno bruto (rho = 0.67) pero negativamente con el Sharpe (rho = -0.85, p = 0.004). En ningún subperiodo la relación fue positiva. Salud y consumo básico pagaron el mejor retorno por unidad de riesgo; financieras y energía, el peor.

### RQ2. ¿Qué protege según el régimen macro? — H2 CONFIRMADA (con matiz)

La correlación SPY-TLT fue -0.28 con inflación baja y +0.09 con inflación alta (Fisher z = 3.18, p = 0.0015), sobreviviendo al rezago de publicación del CPI. El matiz: el cambio de signo lo domina la era post-2015 (en el episodio 2021-2023 llegó a +0.54). Los bonos cortos conservaron mejor su papel diversificador; el oro se mantuvo neutral en ambos regímenes.

### RQ3. ¿Qué habría pasado con 100 USD al mes? — H3a y H3b CONFIRMADAS

Sobre todas las ventanas históricas disponibles: el destino importó 4 veces más que la fecha de inicio a 10 años y 10 veces más a 20 (Friedman p < 1e-11). Medianas a 20 años: QQQ 6.4x lo aportado, SPY 2.7x, 60/40 2.6x; ninguna ventana de 20 años perdió dinero nominal. Frente a la suma única, el DCA cedió retorno mediano (1.66x vs 2.28x a 10 años) a cambio de reducir la dispersión a menos de la mitad.

### RQ4. ¿Algún ETF supera consistentemente al S&P 500? — H4 REFUTADA

QQQ ganó a SPY en el 84% de las ventanas de 5 años (IC bootstrap 0.70-0.96) y XLK en el 76%; ambos sobreviven Bonferroni y fueron los únicos en ganar las dos décadas 2005-2015 y 2015-2025. Pero ambos son la misma apuesta (tecnología): fuera de ella, nada superó consistentemente al índice (VEA: 0% de ventanas ganadoras; bonos: 22-27%). La outperformance consistente existió solo como concentración sectorial persistente.

### RQ5. ¿El momentum sectorial persiste? — H5 REFUTADA

Comprar mensualmente el tercil sectorial con mejor momentum a 6 meses y vender el peor rindió -1.1% anual antes de costos (IC 95% de la media mensual: -0.47% a +0.29%). El resultado se repite con formación a 3 y 12 meses. La rotación mecánica no generó valor; la elección estructural del destino (RQ3) dominó a la táctica.

## Limitaciones

1. **Sesgo de supervivencia**: el universo son activos que existen hoy; los niveles de retorno de largo plazo tienen sesgo optimista.
2. **Sin costos ni impuestos**: los backtests excluyen comisiones, spreads y fiscalidad. La dirección del efecto se declara en cada análisis (penaliza más al DCA y al momentum).
3. **Solo USD y mercado estadounidense** como núcleo.
4. **Comparaciones múltiples y ventanas solapadas**: mitigadas con Bonferroni y bootstrap en bloques, no eliminadas.
5. **El pasado no garantiza el futuro**: este proyecto describe regularidades históricas; no constituye recomendación de inversión.

## Conclusiones

Para un inversionista de largo plazo, la evidencia de esta muestra apunta a tres decisiones de primer orden: elegir bien el destino estructural (domina sobre el timing), entender que la protección de los bonos es condicional al régimen de inflación, y desconfiar tanto de la promesa de "ganarle al mercado" (solo la concentración tecnológica lo logró de forma persistente, con su riesgo asociado) como de las tácticas de rotación. Metodológicamente, el proyecto muestra que dos hipótesis razonables (H4, H5) no sobrevivieron al contacto con los datos: registrar hipótesis antes de calcular es lo que separa el análisis de la narrativa.
