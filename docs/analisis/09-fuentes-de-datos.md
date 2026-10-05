# 09 · Fuentes de datos de mercado

Fuentes para el módulo bayesiano (μ, σ, ρ y `s_tend` de las 5 categorías). Resuelve la decisión D3.

> Verificado el 2026-10-04; decisión revisada el 2026-10-05 (W14: datos reales para las cinco categorías).

## 1. Hallazgos

### BCRP (Banco Central de Reserva del Perú)

- Tiene series útiles. Ejemplo verificado: `PD31895MM`, rendimiento del bono del gobierno peruano a 10 años en soles, mensual, desde 2005. También publica tasas de interés pasivas (depósitos).
- **La API (`/estadisticas/series/api/<código>/json/<inicio>/<fin>`) no se puede usar**: responde con una protección anti-bots (Incapsula), tanto desde un script como desde el navegador (página en blanco).
- La **vista web** de cada serie (`/estadisticas/series/mensuales/resultados/<código>/html/<inicio>/<fin>`) **sí carga en Chromium sin interfaz** (`chromium --headless=new --dump-dom`), porque el navegador ejecuta el script del desafío. El DOM trae una tabla con filas `periodo` (`Ene24`: mes abreviado en español + año de 2 dígitos) y `dato` (número o "n.d."). Verificado el 2026-10-05.
- Las tasas de emisión de bonos (`PN01113MM` privados en S/ hasta 3 años, `PN01124MM` Tesoro hasta 5 años) tienen 0.0 en la mayoría de meses (sin emisiones): no sirven para retornos mensuales. El grupo de bonos del gobierno solo publica el rendimiento a 10 años (S/ y US$). La tasa del saldo de CD BCRP (`PN06503OM`) sí se publica todos los meses.

### Yahoo Finance (`yfinance`)

- No es una API oficial: `yfinance` lee los datos públicos de Yahoo. Es gratis y no pide clave, pero puede romperse o limitar pedidos sin aviso, y sus términos la restringen a uso personal.
- Prueba realizada (5 años, mensual):

| Ticker | Qué es | Resultado |
|---|---|---|
| `EPU` | ETF iShares MSCI Peru (USD) | ✅ 60 meses |
| `PEN=X` | Tipo de cambio USD/PEN | ✅ 60 meses |
| `BVN.LM`, `CREDITC1.LM` | Acciones en la Bolsa de Lima | ✅ 60 meses |
| `BAP`, `BVN`, `SCCO` | Acciones peruanas en NYSE | ✅ |
| `^SPBLPGPT` | Índice general BVL | ❌ No encontrado |

- **Solo cubre la categoría de acciones.** No tiene fondos mutuos peruanos, bonos BTP ni tasas de depósito.

### SMV y AAFMP

- La SMV publica el valor cuota diario de cada fondo mutuo y tiene un dataset en el portal de datos abiertos.
- La AAFMP publica reportes mensuales de rentabilidad por tipo de fondo (origen de los valores del Anexo A). Son reportes, no una API.

## 2. Decisión (D3, revisada en W14)

**BCRP mediante navegador sin interfaz, descargado una vez y versionado como CSV.** El sistema nunca consulta internet para obtener datos de mercado; solo el script de descarga lo hace.

| Categoría | Fuente | Tipo | Transformación | Respaldo |
|---|---|---|---|---|
| Fondos de acciones | BCRP `PN01142MM` Índice General BVL | Índice | `P_t/P_{t−1} − 1` | Yahoo `EPU` × `PEN=X` (`--stocks-source yahoo`); Anexo A |
| Fondos mixtos | Compuesto: 0.5 × acciones (BVL) + 0.5 × bonos (BTP 10 años) | Compuesto | Suma ponderada de retornos mensuales | Anexo A si falta un componente |
| Fondos de deuda | BCRP `PN06503OM` tasa del saldo de CD BCRP | Rendimiento (D ≈ 0.5) | `y_{t−1}/1200 − D·Δy/100` | Anexo A |
| Bonos soberanos (BTP) | BCRP `PD31895MM` rendimiento a 10 años en S/ | Rendimiento (D ≈ 7.0) | `y_{t−1}/1200 − D·Δy/100` | Anexo A |
| Depósito a plazo | BCRP `PN07814NM` tasa pasiva MN 181–360 días | Tasa | `tasa_{t−1}/1200` | Anexo A |

```
BCRP (vista HTML)  ──  Chromium --headless --dump-dom, una petición por serie
        │  scripts/fetch_market_data.py
        ▼
data/market/<categoria>__<fuente>_<serie>.csv  +  manifest.json  +  SOURCES.md
        │
        ▼
ai/uncertainty/bayesian  (lee el manifiesto y los CSV; sin red)
        │  retornos mensuales por tipo → prior del Anexo A + actualización conjugada de μ,
        │  σ muestral, correlaciones por pares con ≥ 24 meses comunes, s_tend
        ▼
MarketEstimates
```

Los nombres de archivo dicen qué contienen (categoría, fuente y serie) y el manifiesto guarda código, título publicado, tipo, duración, periodo y fecha de descarga. Si un archivo falta o tiene menos de 24 retornos, la categoría usa el prior del Anexo A.

**Por qué:**

- Está dentro del alcance declarado: el informe (2.3) excluye los datos en tiempo real.
- La demo no depende de servicios externos.
- Es reproducible: todo el equipo calcula con los mismos datos.
- `yfinance` queda solo en el script de descarga, no como dependencia de la aplicación.

## 3. Advertencias para el informe

1. **Rendimiento ≠ retorno.** Para bonos y deuda el retorno mensual se aproxima con el devengo (`y/12`) menos la duración por el cambio de rendimiento (`D·Δy`). Es una aproximación de primer orden (sin convexidad) y la duración es un supuesto: 7.0 años para el BTP a 10 años y 0.5 años para el saldo de CD BCRP.
2. **El índice BVL es de precios.** Excluye dividendos, así que el retorno de acciones queda levemente subestimado. Representa el mercado peruano, no un fondo (sin comisiones).
3. **Fondos mixtos compuestos.** El BCRP no publica retornos de fondos mutuos; la categoría se arma como 0.5 × acciones + 0.5 × bonos (BTP 10 años), porque los fondos mixtos peruanos combinan renta variable y bonos. Los pesos son un supuesto del equipo. Resultado: μ 6.8 %, σ 12.3 %, correlación 0.97 con acciones y 0.54 con bonos. Como es una mezcla fija de dos categorías que el optimizador ya puede combinar, aporta poca diversificación propia. Se etiqueta como "compuesto a partir de series reales". (Una primera versión con 0.5 × deuda en lugar de bonos daba correlación 0.9996 con acciones y se descartó.)
4. **Deuda = corto plazo.** La tasa del saldo de CD BCRP representa renta fija en soles de corto plazo; un fondo de deuda real puede tener más duración y riesgo de crédito, así que su σ (0.6 % anual) es un piso.
5. **Depósito a plazo.** Su retorno es la tasa vigente; la σ medida (0.4 % anual) refleja cómo cambia la tasa en el tiempo, no un riesgo de pérdida.
6. **Fuente frágil.** La descarga depende de que la vista HTML del BCRP siga cargando en Chromium. Si deja de hacerlo, los CSV versionados siguen funcionando y para acciones existe el respaldo de Yahoo (`yfinance`, uso personal/académico).
