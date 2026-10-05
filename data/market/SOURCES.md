# Fuentes de datos de mercado (decisión D3, revisada en W14)

Las cinco categorías se estiman con series reales mensuales en soles. `manifest.json` describe cada
serie (archivo, fuente, código, título publicado, tipo, duración, periodo y fecha de descarga) y lo
escribe `scripts/fetch_market_data.py`. Cada CSV tiene columnas `date,value` (primer día del mes) con
el valor **tal como se publica**: nivel de índice o tasa en % anual. `ai/uncertainty/bayesian/` solo
lee estos archivos locales y los convierte en retornos mensuales según su tipo.

Descarga: 2026-10-05, ventana pedida 2010-01 a 2026-10; el mes en curso (aún abierto) se descarta.

| Categoría | Archivo | Serie (BCRP) | Tipo | Transformación a retorno mensual | Periodo (meses) | Advertencias |
|---|---|---|---|---|---|---|
| Acciones (`stocks`) | `acciones__bcrp_indice_general_bvl.csv` | `PN01142MM` Bolsa de Valores de Lima – Índice General BVL (base 31/12/91 = 100) | `index` | `r_t = P_t / P_{t−1} − 1` | 2010-01 .. 2026-08 (200) | Índice de precios: excluye dividendos, así que subestima levemente el retorno total. Es el mercado, no un fondo (sin comisiones). |
| Fondos mixtos (`mixed`) | — (se calcula) | Compuesto a partir de series reales: 0.5 × acciones (Índice General BVL) + 0.5 × bonos (BTP 10 años, D = 7) | `composite` | `r_t = 0.5 · r_acciones,t + 0.5 · r_bonos,t` en los meses comunes | 2010-02 .. 2026-08 (199 retornos) | El BCRP no publica retornos de fondos mutuos; los fondos mixtos peruanos combinan renta variable y bonos. Los pesos 50/50 son un supuesto del equipo. Su correlación con acciones es 0.97 (la σ de acciones domina) y con bonos 0.54. |
| Fondos de deuda (`debt`) | `deuda__bcrp_tasa_saldo_cd_bcrp.csv` | `PN06503OM` Tasa de interés del saldo de Certificados de Depósito del BCRP (CD BCRP) | `yield` | `r_t ≈ y_{t−1}/1200 − D·(y_t − y_{t−1})/100`, D = 0.5 años | 2010-01 .. 2026-08 (200) | Sustituto de corto plazo (ver nota 1). D = 0.5 es una aproximación. |
| Bonos soberanos (`bonds`) | `btp__bcrp_rendimiento_10a.csv` | `PD31895MM` Rendimiento del Bono del gobierno peruano a 10 años (en S/) | `yield` | Igual, con D = 7.0 años | 2010-01 .. 2026-09 (201) | La duración modificada de un BTP a 10 años varía con la tasa; 7.0 es una aproximación. Fórmula de primer orden (sin convexidad). |
| Depósito a plazo (`term`) | `deposito__bcrp_tasa_pasiva_181_360d.csv` | `PN07814NM` Tasa pasiva promedio de la banca en MN, plazo 181–360 días (términos efectivos anuales) | `rate` | `r_t = tasa_{t−1}/1200` (interés devengado) | 2010-08 .. 2026-08 (193) | Promedio del sistema bancario; la σ medida es la variación del nivel de tasa en el tiempo, no un riesgo de pérdida. |

## Notas

1. **Serie de deuda.** Las candidatas iniciales eran tasas de emisión: `PN01113MM` (bonos privados en
   S/ hasta 3 años) tiene 0.0 en 146 de 200 meses y `PN01124MM` (Bonos del Tesoro hasta 5 años) en
   118 de 188 meses (meses sin emisiones), insuficientes para retornos mensuales. El BCRP no publica
   rendimientos soberanos de corto plazo mensuales (su grupo de bonos del gobierno solo trae el de
   10 años en S/ y en US$). Se usa la tasa del saldo de CD BCRP, publicada todos los meses: representa
   renta fija en soles de corto plazo, similar a la cartera de un fondo de deuda conservador.
2. **Ceros como faltantes.** En las series de tasas (`yield`, `rate`) el BCRP escribe 0.0 en meses
   sin operaciones; el script los omite. "n.d." y celdas vacías también se omiten. Un hueco no genera
   retorno para ese mes.
3. **Rendimiento ≠ retorno.** Para las series `yield` el retorno se aproxima por el devengo
   (`y/12`) más el efecto precio de primer orden (`−D·Δy`). Es una aproximación declarada.
4. **Correlaciones.** Se estiman con los meses comunes de cada par de categorías con datos (mínimo
   `min_months` = 24 en `data/parameters/bayes.json`). Si la matriz no es semidefinida positiva se
   repara (recorte de autovalores y diagonal unitaria); con los datos actuales el autovalor mínimo
   era −1.5·10⁻⁷, así que la reparación es despreciable.
7. **Composición de los mixtos.** Una primera versión usaba 0.5 × acciones + 0.5 × deuda, que era una
   copia escalada de acciones (correlación 0.9996). Se cambió a acciones + bonos, más fiel a la cartera
   de un fondo mixto.
5. **Respaldo Yahoo.** `python scripts/fetch_market_data.py --stocks-source yahoo` reemplaza la serie
   de acciones por el ETF `EPU` (iShares MSCI Peru, USD, cierre ajustado por dividendos) convertido a
   soles con `PEN=X`, en `acciones__yahoo_epu_en_soles.csv` (requiere `yfinance`). No se usa en la
   versión actual.
6. **Acceso al BCRP.** La API JSON del BCRP está protegida por un desafío anti-bot; la vista HTML
   pública se carga con Chromium sin interfaz (`--headless=new --dump-dom`), que ejecuta el desafío.
   El script hace una sola petición por serie (como máximo un reintento). Si una categoría no tiene
   archivo o tiene menos de 24 retornos, vuelve al prior del Anexo A.
