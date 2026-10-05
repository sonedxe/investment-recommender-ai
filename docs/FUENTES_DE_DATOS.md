# Fuentes de Datos del Sistema (datos reales, documentados y citables)

Documento de trazabilidad de los datos históricos que alimentan el módulo
bayesiano (`ai/data/market_data.py`). Recolectado en **octubre de 2026**.
Reemplaza a las series sintéticas de la versión anterior y cumple el pendiente
de calibración con fuentes (BCRP, SMV, AAFMP) señalado en la sección 4.6
("Advertencia de rigor") y 9.2 del informe técnico v1.1.

Cada celda se clasifica como:

- **Observación directa**: valor publicado por la fuente, extraído sin
  transformación (más allá del cambio % → decimal).
- **Estimación documentada**: valor no publicado directamente; se obtiene de
  los datos de la fuente con el método indicado en la nota de la celda.

---

## 1. Fondos mutuos de acciones, mixtos y deuda (3 de las 5 categorías)

**Fuente**: Asociación de Administradoras de Fondos Mutuos del Perú
(AAFMP/FMP), *Boletines mensuales* de diciembre de cada año, tabla
**"Rentabilidades Promedio"** por tipo de fondo (la AAFMP obtiene el dato del
portal de la **SMV**). La rentabilidad es el promedio ponderado por patrimonio
de los fondos de cada categoría, no incluye comisiones de suscripción/rescate
ni impuesto a la renta.
Portal de estadísticas: <https://fondosmutuos.pe/estadisticas/>

Rentabilidad anual (año calendario, **en soles**). Todas las celdas son
**observaciones directas**:

| Año | De Acciones | Mixtos | De Deuda | Boletín (PDF) |
|---|---|---|---|---|
| 2019 | −1.10% | 3.68% | 3.83% | `boletin-diciembre-2019-AAFM-D.pdf` |
| 2020 | −1.60% | 1.60% | 2.46% | `boletin-DIC4.pdf` |
| 2021 | 4.74% | −0.31% | −1.14% | `12-BOLETIN-DIC21.pdf` |
| 2022 | −6.23% | 0.05% | 2.43% | `botetin-diciembre-22.pdf` |
| 2023 | 17.41% | 10.57% | 7.72% | `Diciembre2023-3.pdf` |
| 2024 | 8.13% | 7.89% | 5.11% | `DICIEMBRE-SIN-COMENTARIOS-1.pdf` |
| 2025 | 34.28% | 16.70% | 4.94% | `BOLETIN-FONDOS-MUTUOS-DICIEMBRE-2025.pdf` |

Verificación cruzada: el boletín de junio de 2026 reporta, para los mismos
tipos en soles, últimos 12 meses: acciones 50.90%, mixtos 28.96%, deuda
4.18% — coherente con la trayectoria alcista 2025-2026 (BVL/MSCI Perú
+49.9% en 2025, según Moody's Local PE, dic-2025).

**Estadísticos derivados (2019-2025)** — usados como prior del módulo
bayesiano: acciones μ = 7.95%, σ = 13.95%; mixtos μ = 5.74%, σ = 6.30%;
deuda μ = 3.62%, σ = 2.78%.

## 2. Depósito a plazo fijo

**Fuente principal (serie anual)**: Banco Mundial, indicador
**FR.INR.DPST — "Deposit interest rate (%)"**, Perú. La serie reporta la tasa
que pagan los bancos por depósitos; proviene del FMI (*International Financial
Statistics*), que a su vez la recibe del **BCRP**.
Consulta: `https://api.worldbank.org/v2/country/PER/indicator/FR.INR.DPST`

| Año | Tasa | Tipo de celda |
|---|---|---|
| 2019 | 3.67% | Observación directa |
| 2020 | 1.861% | Observación directa |
| 2021 | 0.697% | Observación directa |
| 2022 | 4.821% | Observación directa |
| 2025 | 4.40% | **Estimación documentada** (ver nota) |

**Nota sobre 2023-2025**: el Banco Mundial aún no publica FR.INR.DPST para
esos años. Se usa como observación representativa del periodo más reciente la
**TREA de depósitos a plazo en soles a 1 año del sistema bancario**: BBVA Perú
publica 4.40% TREA (vigente 15–21 setiembre 2026,
<https://www.bbva.pe/personas/productos/inversiones/depositos/deposito-plazo.html>);
la tabla de tasas pasivas de la **SBS** (setiembre 2026) muestra promedios del
sistema en el rango 3.8%–4.6% para plazos de 181-360 días
(<https://www.sbs.gob.pe/app/pp/EstadisticasSAEEPortal/Paginas/TIPasivaDepositoEmpresa.aspx?tip=B>).
Trabajo futuro: completar 2023-2024 con la serie mensual de tasas pasivas de
la SBS/BCRP cuando se obtenga acceso.

**Estadísticos derivados** — μ = 3.09%, σ = 1.75%.

## 3. Bonos soberanos (BTP)

**Concepto medido**: rendimiento (*yield*) del **bono del gobierno peruano a
10 años en soles**. Supuesto documentado: el retorno anual de la categoría se
aproxima con el yield al cierre del año (inversor que mantiene al
vencimiento); los movimientos de precio intra-año quedan fuera del alcance de
esta entrega.

| Punto | Valor | Fuente | Tipo de celda |
|---|---|---|---|
| dic-2020 | 3.633% | BCRP vía CEIC — *mínimo histórico de la serie* (<https://www.ceicdata.com/en/peru/government-bond-yield/government-bond-yield-10-years-pen>) | Observación directa |
| 24-dic-2024 | ≈7.0% | Curva de Bonos del Tesoro al 24/12/2024, gráfico de **Moody's Local PE**, "Evolución de variables de mercado y fondos mutuos en Perú" (dic-2025), fuente BCRP/Investing (<https://moodyslocal.com.pe/wp-content/uploads/2025/12/MOODYS_LOCAL_Research_Fondos.pdf>) | **Estimación documentada** (lectura de gráfico, rango 6.9–7.1%) |
| sep/oct-2025 | ≈5.85% | **Trading Economics**, Peru 10-Year Government Bond Yield: sep-2026 6.33% (+0.45 interanual → sep-2025 ≈ 5.88%); oct-2026 6.35% (+0.54 interanual → oct-2025 ≈ 5.81%) (<https://tradingeconomics.com/peru/government-bond-yield>). Consistente con la emisión soberana **PEN cupón 6.85% 12-ago-2035** colocada por el MEF en jun-2025 | **Estimación documentada** (promedio de dos referencias interanuales) |
| ago-2026 | 6.189% | BCRP vía CEIC (jul-2026: 6.069%) | Observación directa |

**Estadísticos derivados** — μ = 5.67%, σ = 1.44% (4 puntos; muestra pequeña,
marcada para ampliación con la serie mensual completa del BCRP — su portal
estadístico requiere acceso interactivo).

## 4. Matriz de correlaciones

- **Bloque fondos (acciones, mixtos, deuda)**: **empírico**, coeficientes de
  correlación muestral de las series anuales AAFMP 2019-2025 de la sección 1:
  ρ(acciones, mixtos) = 0.934; ρ(acciones, deuda) = 0.496; ρ(mixtos, deuda) =
  0.737.
- **BTP y depósito frente a los fondos y entre sí**: **parámetros de diseño
  documentados** (las series no comparten años calendario completos):
  correlación baja del depósito (tasa fija bancaria) con todo lo demás
  (0.05–0.10); correlación moderada entre instrumentos guiados por tasas de
  interés (BTP↔deuda 0.40; BTP↔depósito 0.30; BTP↔mixtos 0.25; BTP↔acciones
  0.10). La matriz completa (`CORRELACIONES` en `ai/reference_data.py`) es
  semidefinida positiva (verificado en `tests/test_bayesian.py`). Pendiente de
  calibración con series alineadas (trabajo futuro, sección 10 del informe).

## 5. Notas metodológicas

1. **Ventana**: se priorizó la ventana 2019-2025 porque los boletines AAFMP
   con el formato actual de tipologías (De Acciones / Mixtos / De Deuda) son
   consistentes desde 2019; los boletines 2017-2018 usan otra presentación y
   sus archivos ya no están disponibles en el portal.
2. **Moneda**: todas las series están en **soles** y en **decimales** en el
   código (4.94% = 0.0494).
3. **Tendencia (s_tend)**: el indicador de la sección 4.3 del informe se
   calcula con la observación más reciente de cada serie (2025 para fondos y
   depósito; 2026 para BTP).
4. **Acceso a fuentes primarias**: el portal estadístico del BCRP
   (BCRPData) aplica protección anti-bots; los datos BCRP aquí usados se
   obtuvieron vía publicaciones oficiales (boletines AAFMP que citan SMV,
   informes MEF, Banco Mundial/FMI que replica BCRP, CEIC que replica BCRP).
   Se recomienda al equipo descargar manualmente las series BCRPData
   (PD31893DD y tasas pasivas) para ampliar las series 2 y 3.
5. **Parámetros del Anexo C** (sensibilidades de contexto b, a_pol, a_mac,
   k_pol, k_mac y constantes del módulo difuso) se mantienen como parámetros
   de diseño del informe v1.1; su calibración estadística sigue pendiente
   (sección 9.2 del informe).
