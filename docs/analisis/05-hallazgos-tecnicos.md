# 05 · Hallazgos técnicos

## 1. 🔴 Portafolios degenerados (verificado)

Muestreo de 150 000 portafolios con μ y σ del Anexo A, maximizando `E − λσ` (depósito sin correlación con el resto):

| ρ entre categorías | λ | Acc. | Mixt. | Deuda | BTP | Dep. | E | σ |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.2 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 12.2 % | 19.0 % |
| 0 | 0.5 | 0.15 | 0.09 | 0.00 | 0.76 | 0.00 | 7.3 % | 4.0 % |
| 0 | 1.0 | 0.02 | 0.01 | 0.00 | 0.14 | 0.82 | 5.0 % | 0.7 % |
| 0 | 2.0 | 0.00 | 0.00 | 0.00 | 0.06 | 0.93 | 4.7 % | 0.5 % |
| 0.3 | 0.5 | 0.13 | 0.00 | 0.00 | 0.87 | 0.00 | 7.2 % | 4.4 % |
| 0.3 | 1.0 | 0.01 | 0.00 | 0.00 | 0.11 | 0.88 | 4.8 % | 0.6 % |
| 0.3 | 2.0 | 0.00 | 0.00 | 0.00 | 0.06 | 0.94 | 4.6 % | 0.5 % |

**Causas**

- El depósito a plazo (4.5 %, σ 0.5 %) es casi un activo libre de riesgo: domina para cualquier λ ≥ 1.
- Los fondos de deuda (2.4 %, σ 2.5 %) están dominados por el depósito y los BTP: su gen queda siempre en 0.
- `σ(P)` escala linealmente con los pesos, lo que empuja las soluciones a las esquinas.

**Impacto:** una demo que recomiende "90 % en depósito" o "100 % en acciones" no convence y, como advierte el docente, indica una función de aptitud que "resuelve el problema equivocado".

**Opciones** (decisión D2):

| Opción | Ventaja | Desventaja |
|---|---|---|
| Tope por categoría (`wᵢ ≤ 0.5`) como restricción dura | Simple, explicable, habitual en regulación | Valor arbitrario; hay que justificarlo |
| Término de diversificación (entropía o `−Σwᵢ²`) | Suave y ajustable | Un parámetro más que calibrar |
| Varianza `E − (λ/2)·σ²` (Markowitz) | Estándar en finanzas; soluciones más interiores | Cambia las escalas y los ejemplos del informe |
| Revisar la σ del depósito (riesgo de inflación/reinversión) | Más realista | Necesita una fuente que lo respalde |

## 2. Matriz de correlaciones no definida

El Anexo A trae μ y σ, pero no `ρᵢⱼ`; la covarianza del notebook es de otros activos simulados. Sin `ρ` no se puede calcular `σ(P)`. Opciones: estimarla de series históricas (preferible) o fijarla con criterio documentado.

## 3. Fuente de datos del módulo bayesiano

- No se define de dónde salen las series históricas ni `r_12m` para `s_tend`. Candidatas: BCRP (series estadísticas), SBS, AAFMP.
- La actualización normal-normal con varianza conocida **solo actualiza μ**; σ y la covarianza quedan fijas. Es aceptable, pero hay que declararlo.

## 4. Mapeo texto → λ_base

No se especifica cómo la IA generativa traduce la tolerancia a un número. Propuesta: el LLM devuelve una **etiqueta cerrada** (enum), y el código la mapea:

| Etiqueta | λ_base |
|---|---|
| muy_conservador | 3.0 |
| conservador | 2.0 |
| moderado | 1.0 |
| agresivo | 0.5 |
| muy_agresivo | 0.2 |

## 5. Detalles menores

- **Unidades del ejemplo de fitness:** la v1.1 dice "todo en decimales", pero el ejemplo corregido (−14 / 4) está en puntos porcentuales. En decimales: `0.06 − 2·0.10 = −0.14` y `0.06 − 0.2·0.10 = 0.04`.
- **Notebook:** la celda final muestra `NameError: genetic_algorithm is not defined` (celdas ejecutadas fuera de orden).

## 6. Reglas de contexto

- Diseño completo en la v1.1: RC1–RC7, fórmulas de `cᵢ`, `μ'ᵢ`, `σ'ᵢ`, `Σ'ᵢⱼ`, tope `c_max`, asimetría prudente. El ejemplo 4.6.4 es consistente (p. ej. acciones: `0.5 − 3.0 = −2.5 pp`, `σ' = 19 % · 1.5 = 28.5 %`).
- El docente pidió **reglas**. Recomendación: un motor de reglas explícito (lista `condición → efecto`) que alimente el término contextual `C(P) = Σ wᵢ·cᵢ`; las fórmulas actuales pasan a ser el cuerpo de cada regla.
- Pendiente: calibrar `bᵢ, β, γ, c_max` con fuentes (BCRP, SMV, AAFMP) y presentarlas siempre como supuestos configurables, no como predicciones.

## 7. Estado del repositorio

| Componente | Contenido |
|---|---|
| `backend/app/main.py` | FastAPI con `/health` y `/api/ping` |
| `backend/app/core/config.py` | Carga de `.env`, CORS |
| `ai/generative`, `ai/heuristic`, `ai/uncertainty` | Solo `ping()` |
| `frontend/` | React + Vite + TS básico |
| `tests/test_connectivity.py` | 3 tests de conectividad |
| `.env.example` | Proveedor compatible con OpenAI + **modo offline** sin API key |

**Inconsistencias con el informe** (corregir al implementar):

- `ai/heuristic` menciona *simulated annealing*; el informe solo define el AG.
- `ai/uncertainty` menciona *VaR Monte Carlo* y redes bayesianas; el informe define actualización normal conjugada + lógica difusa.
- El README dice que la IA generativa "genera el universo de inversión"; en el informe las 5 categorías son fijas.

**Aprovechable:** el modo offline (generador determinista sin API) es valioso para tests y para una demo sin conexión.
