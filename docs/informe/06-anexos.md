# Anexo A. Parámetros del sistema

Todos los parámetros se leen de `data/parameters/` y se validan al iniciar la aplicación. Los porcentajes se expresan en decimales en los archivos (0,005 = 0,5 pp).

## A.1. Lógica difusa

Tabla: {#tab:a-horizonte} Parámetros del sistema difuso del horizonte (fuzzy.json)

| Elemento | Valor |
|---|---|
| Tipo de inferencia | Sugeno de orden cero |
| Universo de H | [0, 30] años |
| Conjuntos | Corto `Trap(0, 0, 1, 3)`; Mediano `Tri(2, 5, 8)`; Largo `Trap(6, 10, 30, 30)` |
| Consecuentes m_H (RH1, RH2, RH3) | 1,5; 1,0; 0,7 |

Tabla: {#tab:a-absorcion} Parámetros del sistema difuso de absorción (fuzzy.json)

| Elemento | Valor |
|---|---|
| Tipo de inferencia | Mamdani: Y = mínimo, implicación por mínimo, agregación por máximo; sin desfuzzificar en el algoritmo genético |
| Proporción r, universo [0, 1] | Bajo `Trap(0, 0, 0.2, 0.4)`; Medio `Tri(0.2, 0.5, 0.8)`; Alto `Trap(0.6, 0.9, 1, 1)` |
| Fondo de emergencia E, universo [0, 12] meses | Insuficiente `Trap(0, 0, 1, 4)`; Adecuada `Trap(2, 6, 12, 12)` |
| Capacidad CA, universo [0, 1] | Baja `Trap(0, 0, 0.15, 0.4)`; Media `Tri(0.25, 0.5, 0.75)`; Alta `Trap(0.6, 0.85, 1, 1)` |
| Reglas | RA1 a RA6 (sección 2.6.2) |
| Resolución del universo de salida | 1001 puntos |
| σ_piso y a de σ_max(c) = σ_piso + a·c | 0,03 y 0,13 |
| Conjunto usado si faltan datos de absorción | Media |

## A.2. Reglas de contexto

Tabla: {#tab:a-contexto} Sensibilidades por categoría de las reglas de contexto (context.json)

| Categoría | bᵢ (pp) | β_pol,i (pp) | β_mac,i (pp) | γ_pol,i | γ_mac,i |
|---|---|---|---|---|---|
| Fondos de acciones | +0,5 | 3,0 | 1,0 | 0,50 | 0,20 |
| Fondos mixtos | +0,3 | 1,5 | 0,8 | 0,25 | 0,10 |
| Fondos de deuda | 0,0 | 0,5 | 0,5 | 0,10 | 0,05 |
| Bonos soberanos (BTP) | +0,2 | 1,0 | 0,5 | 0,20 | 0,10 |
| Depósito a plazo fijo | −0,3 | 0,0 | 0,3 | 0,00 | 0,00 |

Parámetros globales: sensibilidad a la tendencia β_tend = 1,5 pp por unidad de s_tend (igual para todas las categorías) y tope de influencia c_max = 3,0 pp. Criterio de los valores: precedente positivo para las categorías cuyo rendimiento histórico ha superado a su referencia y negativo para el depósito a plazo, cuyo retorno real tiende a ser erosionado por la inflación; mayor sensibilidad β y γ cuanto mayor es la exposición a la renta variable. Son parámetros de diseño; su efecto se midió en los experimentos de contexto (sección 5.4.2).

## A.3. Algoritmo genético y función de aptitud

Los parámetros de `optimization.json` se detallan en la sección 2.9.8: población 80, máximo 200 generaciones, paciencia 25, torneo 3, cruce 0,9, mutación 0,1 (σ 0,05 en los pesos y 0,15 en c), elitismo 1, 0,05 ≤ wᵢ ≤ 0,40, φ = 50 y κ = 0,03.

## A.4. Perfiles de riesgo y estimación bayesiana

Tabla: {#tab:a-perfiles} Escala de perfiles de riesgo (risk_profiles.json)

| Etiqueta | λ_base | Lenguaje típico del usuario |
|---|---|---|
| `muy_agresivo` | 0,2 | «quiero la máxima ganancia, aguanto pérdidas» |
| `agresivo` | 0,5 | «acepto riesgo si gano más» |
| `moderado` | 1,0 | «algo de riesgo, pero no mucho» |
| `conservador` | 2,0 | «no me gusta arriesgar» |
| `muy_conservador` | 3,0 | «no quiero perder nada» |

Tabla: {#tab:a-referencia} Valores de referencia y desviaciones previas (categories.json y bayes.json)

| Categoría | μ de referencia | σ de referencia | τ₀ (desviación previa de μ) |
|---|---|---|---|
| Fondos de acciones | 12,2 % | 19,0 % | 3,0 % |
| Fondos mixtos | 6,1 % | 9,0 % | 2,0 % |
| Fondos de deuda | 2,4 % | 2,5 % | 1,0 % |
| Bonos soberanos (BTP) | 6,5 % | 3,5 % | 1,0 % |
| Depósito a plazo fijo | 4,5 % | 0,5 % | 0,5 % |

Los valores de referencia son los puntos medios del Anexo A del informe de avance (promedios de la Asociación de Fondos Mutuos del Perú y tasas referenciales). Se usan como distribución previa del retorno esperado y, junto con la correlación supuesta de 0,3 entre las cuatro categorías de mercado (0 con el depósito), como respaldo si falta una serie. Otros parámetros: mínimo de 24 retornos por categoría o par y ventana de tendencia de 12 meses.

# Anexo B. Fuentes de datos

Tabla: {#tab:b-fuentes} Series de mercado, procedencia y aproximaciones

| Categoría | Fuente y serie | Periodo | Aproximaciones |
|---|---|---|---|
| Fondos de acciones | BCRP `PN01142MM`, Índice General BVL (base 31/12/91 = 100) | 2010-01 a 2026-08 (200 meses) | Índice de precios: excluye dividendos; representa el mercado, no un fondo |
| Fondos mixtos | SBS B-220932, valor cuota del Fondo Tipo 2 (promedio de Integra, Prima y Profuturo) | 2010-01 a 2026-08 (200 meses) | Fondo de pensiones, no fondo mutuo minorista; 40 a 50 % en el exterior; la comisión no se descuenta del valor cuota (no verificado) |
| Fondos de deuda | BCRP `PN06503OM`, tasa del saldo de CD BCRP | 2010-01 a 2026-08 (200 meses) | Renta fija de corto plazo; duración supuesta de 0,5 años |
| Bonos soberanos (BTP) | BCRP `PD31895MM`, rendimiento del bono a 10 años en S/ | 2010-01 a 2026-09 (201 meses) | Duración modificada supuesta de 7,0 años; fórmula de primer orden |
| Depósito a plazo fijo | BCRP `PN07814NM`, tasa pasiva en moneda nacional, 181 a 360 días | 2010-08 a 2026-08 (193 meses) | La σ mide el cambio de la tasa, no un riesgo de pérdida |

Tabla: {#tab:b-archivos} Archivos de datos de mercado en data/market/

| Categoría | Archivo |
|---|---|
| Fondos de acciones | `acciones__bcrp_indice_general_bvl.csv` |
| Fondos mixtos | `mixtos__sbs_afp_fondo2_promedio.csv` (índice) y `mixtos__sbs_afp_fondo2_valor_cuota.csv` (valor cuota por AFP) |
| Fondos de deuda | `deuda__bcrp_tasa_saldo_cd_bcrp.csv` |
| Bonos soberanos (BTP) | `btp__bcrp_rendimiento_10a.csv` |
| Depósito a plazo fijo | `deposito__bcrp_tasa_pasiva_181_360d.csv` |
| Todas | `manifest.json` (procedencia y tipo de cada serie) y `SOURCES.md` (descripción y advertencias) |

Las series del BCRP se obtienen de la vista web de BCRPData con un navegador sin interfaz, porque su API bloquea los programas automáticos; el archivo de la SBS se descarga directamente. Ambas descargas las hace una sola vez `scripts/fetch_market_data.py` (5 de octubre de 2026). El documento *Evidencia de fuentes de datos* (`docs/evidencia/`) contiene la captura de cada fuente, la conciliación valor por valor y la huella SHA-256 de cada archivo.

# Anexo C. Decisiones de diseño

Tabla: {#tab:c-decisiones} Decisiones de diseño D1 a D5

| ID | Decisión | Alternativas consideradas | Resultado y justificación |
|---|---|---|---|
| D1 | Qué conjunto difuso va en el cromosoma | Horizonte en el cromosoma; genes como etiquetas lingüísticas por categoría; pesos como números difusos; genes que codifiquen las funciones de pertenencia | El horizonte actúa en la función de aptitud (Sugeno, λ_ef) y la capacidad de absorción en el cromosoma (Mamdani sin desfuzzificar, gen c evaluado con μ_CA(c)). La absorción encaja mejor en el cromosoma porque ya produce un conjunto con varias reglas, y el diseño aísla el algoritmo de los módulos difusos para que un cambio posterior quede acotado |
| D2 | Corrección de los portafolios degenerados | Sin corrección; tope de 50 %; término de diversificación en la aptitud; tope de 40 % | Con E − λσ sin restricciones, la solución era 100 % acciones o cerca de 90 % depósito. El término de diversificación no basta y el tope de 50 % deja portafolios de dos activos. Se adoptó un tope duro de 40 % y, después, un piso de 5 % para que ninguna categoría quede en 0 %; el piso cuesta entre 0,0002 y 0,0026 de aptitud. Es una práctica habitual de las políticas de inversión (bandas mínimas y máximas por clase de activo) |
| D3 | Fuente de datos y matriz de correlaciones | Valores supuestos del informe de avance; Yahoo Finance (solo cubre acciones); fondos mixtos minoristas de la SMV (correlación 0,93 a 0,96 con el índice bursátil) | Cinco series reales del BCRP y de la SBS, descargadas una vez y versionadas con manifiesto; correlaciones estimadas con los meses comunes. La demo no depende de servicios externos y todo el equipo calcula con los mismos datos |
| D4 | Proveedor de IA generativa | OpenAI o un proveedor compatible; Anthropic | Anthropic: Claude Haiku 4.5 para interpretar y Claude Sonnet 5.5 para explicar, con modo sin conexión como respaldo automático. OpenAI sigue disponible cambiando `LLM_PROVIDER` |
| D5 | Escala de λ_base | Número libre devuelto por el modelo de lenguaje; escala cerrada | El modelo clasifica en cinco etiquetas con evidencia y el código las traduce a λ_base (0,2 a 3,0). Un número libre no sería reproducible ni auditable; ante señales contradictorias se pregunta en lugar de elegir |
