# 09 · Fuentes de datos de mercado

Fuentes para el módulo bayesiano (μ, σ, ρ y `s_tend` de las 5 categorías). Resuelve la decisión D3.

> Verificado el 2026-10-04.

## 1. Hallazgos

### BCRP (Banco Central de Reserva del Perú)

- Tiene series útiles. Ejemplo verificado: `PD31895MM`, rendimiento del bono del gobierno peruano a 10 años en soles, mensual, desde 2005. También publica tasas de interés pasivas (depósitos).
- **La API (`/estadisticas/series/api/<código>/json/<inicio>/<fin>`) no se puede usar**: responde con una protección anti-bots (Incapsula), tanto desde un script como desde el navegador (página en blanco).
- La **vista web** de cada serie (`/estadisticas/series/mensuales/resultados/<código>/html/<inicio>/<fin>`) es la vía candidata para descargar los datos a mano. Pendiente de confirmar que carga.

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

## 2. Decisión (D3)

**Fuentes combinadas, descargadas una vez y versionadas como CSV.** El sistema nunca consulta internet para obtener datos de mercado.

| Categoría | Fuente | Método | Respaldo |
|---|---|---|---|
| Fondos de acciones | Yahoo: `EPU` convertido a soles con `PEN=X` | Script `scripts/fetch_market_data.py` (una vez) | Anexo A |
| Bonos soberanos (BTP) | BCRP `PD31895MM` | Descarga manual desde la vista web | Anexo A |
| Depósito a plazo | BCRP, tasas pasivas (código por elegir) | Descarga manual desde la vista web | Anexo A |
| Fondos mixtos | SMV / AAFMP | Manual, si se consigue | Anexo A + correlaciones supuestas documentadas |
| Fondos de deuda | SMV / AAFMP | Manual, si se consigue | Anexo A + correlaciones supuestas documentadas |

```
Fuentes (Yahoo, BCRP, SMV/AAFMP)
        │  script o descarga manual, una sola vez
        ▼
data/market/<categoria>.csv  +  data/market/SOURCES.md (fuente, fecha, transformación)
        │
        ▼
ai/uncertainty/bayesian  (lee CSV; sin red)
```

**Por qué:**

- Está dentro del alcance declarado: el informe (2.3) excluye los datos en tiempo real.
- La demo no depende de servicios externos.
- Es reproducible: todo el equipo calcula con los mismos datos.
- `yfinance` queda solo en el script de descarga, no como dependencia de la aplicación.

## 3. Advertencias para el informe

1. **Rendimiento ≠ retorno.** La serie del BTP es la tasa de rendimiento del bono, no la ganancia de quien lo tiene (que también depende del precio). Usarla como μ es una simplificación que hay que declarar.
2. **EPU está en dólares.** Hay que convertirlo a soles con `PEN=X`; si no, el riesgo cambiario queda mezclado en el retorno.
3. **EPU es un proxy**, no un fondo mutuo peruano de acciones: replica el mercado peruano, que es lo que representa la categoría.
4. **Fondos mutuos = decenas de fondos.** Si se usan datos de la SMV, la serie de una categoría se arma como el promedio del valor cuota de los fondos de ese tipo (coherente con las "categorías representativas" de la v1.1, sección 2.2).
5. **Cobertura parcial:** si mixtos y deuda quedan con valores del Anexo A, se declara como limitación.
