# 09 · Fuentes de datos de mercado

Fuentes para el módulo bayesiano (μ, σ, ρ y `s_tend` de las 5 categorías). Resuelve la decisión D3.

> Verificado el 2026-10-04; decisión revisada el 2026-10-05 (W14: datos reales para las cinco categorías; W15: fondos mixtos desde la SBS, Fondo 2 de las AFP).

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
- Se revisaron fondos mixtos minoristas de la SMV (2026-10-05) como serie para la categoría de mixtos y se descartaron: los fondos mixtos de Credicorp (Moderado y Crecimiento) tienen correlación 0.93–0.96 con el Índice General BVL, así que repetirían el problema del compuesto; BBVA Equilibrado es un fondo de fondos global con retorno medio de 3.2 % anual, poco representativo de un fondo mixto peruano.

### SBS (Superintendencia de Banca, Seguros y AFP)

- El Boletín del Sistema Privado de Pensiones publica el archivo **B-220932 "Valor Cuota diario por Tipo de Fondo de Pensiones y AFP"**: valor cuota diario en soles por tipo de fondo (0 a 3) y AFP (Habitat, Integra, Prima, Profuturo) desde 1993-08-02. El archivo del último mes trae toda la historia.
- Descarga directa (GET estático; es un .xlsx aunque la extensión sea .XLS): `https://intranet2.sbs.gob.pe/estadistica/financiera/{año}/{Mes}/B-220932-{mm}{año}.XLS`, con `Mes` en español según la SBS (`Setiembre`, no `Septiembre`) y `mm` = en, fe, ma, ab, my, jn, jl, ag, se, oc, no, di. El servidor está detrás de un firewall (Imperva): se envía un User-Agent de navegador y se hace una petición por mes candidato. Verificado el 2026-10-05.
- El **Fondo 2** es el fondo mixto por regulación. Integra, Prima y Profuturo tienen datos sin huecos de 2010-01 a 2026-08; Habitat empieza en 2013-06. Las cuatro AFP tienen correlaciones de 0.97 a 0.995 entre sí.

## 2. Decisión (D3, revisada en W14 y W15)

**BCRP mediante navegador sin interfaz y SBS mediante descarga directa, descargados una vez y versionados como CSV.** El sistema nunca consulta internet para obtener datos de mercado; solo el script de descarga lo hace.

| Categoría | Fuente | Tipo | Transformación | Respaldo |
|---|---|---|---|---|
| Fondos de acciones | BCRP `PN01142MM` Índice General BVL | Índice | `P_t/P_{t−1} − 1` | Yahoo `EPU` × `PEN=X` (`--stocks-source yahoo`); Anexo A |
| Fondos mixtos | SBS B-220932, valor cuota del Fondo 2 de las AFP (promedio Integra, Prima, Profuturo) | Índice (encadenado) | `P_t/P_{t−1} − 1` sobre el índice del promedio simple de retornos mensuales | Si la SBS no responde se conserva el CSV versionado; Anexo A si falta el archivo |
| Fondos de deuda | BCRP `PN06503OM` tasa del saldo de CD BCRP | Rendimiento (D ≈ 0.5) | `y_{t−1}/1200 − D·Δy/100` | Anexo A |
| Bonos soberanos (BTP) | BCRP `PD31895MM` rendimiento a 10 años en S/ | Rendimiento (D ≈ 7.0) | `y_{t−1}/1200 − D·Δy/100` | Anexo A |
| Depósito a plazo | BCRP `PN07814NM` tasa pasiva MN 181–360 días | Tasa | `tasa_{t−1}/1200` | Anexo A |

```
BCRP (vista HTML)  ──  Chromium --headless --dump-dom, una petición por serie
SBS (B-220932 .xlsx) ──  GET directo con User-Agent de navegador (--only sbs)
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
3. **Fondos mixtos = Fondo 2 de las AFP (aproximación).** Desde W15 la categoría usa el valor cuota del Fondo 2 publicado por la SBS: promedio simple de los retornos mensuales de Integra, Prima y Profuturo (valor cuota del último día hábil de cada mes), encadenado como índice con base 100 en 2010-01. Resultado: 199 retornos (2010-02 a 2026-08), μ de los datos 7.1 % (posterior 6.6 %), σ 7.6 %, correlación 0.72 con acciones y 0.44 con bonos. Advertencias:
   - Es un fondo de pensiones, no un fondo mutuo minorista; se etiqueta como "aproximación: Fondo 2 de las AFP".
   - Cerca de 40–50 % de su cartera está en el exterior: el retorno en soles incluye el efecto del tipo de cambio.
   - La comisión de la AFP se cobra fuera del valor cuota (no verificado), así que el retorno no la descuenta.
   - El valor cuota es un precio por cuota: los aportes y retiros no distorsionan el retorno.
   - El script descarta un valor diario que salta más de 50 % frente al anterior y vuelve al día siguiente (error de dato); un salto persistente detiene la descarga para revisarlo. En la descarga actual no se descartó ningún valor.

   **Historia de la decisión.** En W14 la categoría era un compuesto de series reales: primero 0.5 × acciones + 0.5 × deuda (correlación 0.9996 con acciones, descartado) y luego 0.5 × acciones + 0.5 × bonos (μ 6.8 %, σ 12.3 %, correlación 0.97 con acciones y 0.54 con bonos). Como era una mezcla fija de dos categorías que el optimizador ya combina, el AG le asignaba 0 % casi siempre (a lo sumo 0.8 % en la ablación). Con el Fondo 2 los mixtos se eligen en todas las celdas de la ablación (8.3 % a 40.0 %). Los fondos mixtos minoristas de la SMV no se eligieron por las razones de la sección 1. El soporte de compuestos sigue en el código (y en las pruebas), pero el manifiesto real ya no lo usa.
4. **Deuda = corto plazo.** La tasa del saldo de CD BCRP representa renta fija en soles de corto plazo; un fondo de deuda real puede tener más duración y riesgo de crédito, así que su σ (0.6 % anual) es un piso.
5. **Depósito a plazo.** Su retorno es la tasa vigente; la σ medida (0.4 % anual) refleja cómo cambia la tasa en el tiempo, no un riesgo de pérdida.
6. **Fuentes frágiles.** La descarga depende de que la vista HTML del BCRP siga cargando en Chromium y de que el firewall de la SBS acepte la petición. Si alguna deja de responder, los CSV versionados siguen funcionando (con `--only sbs` el script termina con error y no toca el manifiesto) y para acciones existe el respaldo de Yahoo (`yfinance`, uso personal/académico).
