# 03 · Estrategia de pruebas

## Niveles

| Nivel | Qué cubre | Dónde | Cuándo corre |
|---|---|---|---|
| Unitarias de referencia | Resultados numéricos conocidos (clase e informe) | `tests/unit/` | Cada commit |
| Propiedades | Invariantes del AG y del difuso | `tests/unit/` | Cada commit |
| Integración | API + flujo completo con LLM offline | `tests/integration/` | Cada commit |
| Golden set de IA generativa | Extracción y clarificación con el LLM real | `tests/llm/` (marcado, opcional) | Manual / antes de entregar |
| Experimentos | Ablación y calibración | `experiments/` | Bajo demanda; resultados versionados |

Se aplica TDD donde existe un resultado esperado claro: escribir primero el test de referencia (rojo), implementar (verde), refactorizar.

## Tests de referencia

| Módulo | Caso | Esperado | Fuente |
|---|---|---|---|
| Mamdani | Propina, servicio 3, comida 8 | P\* = 15.9 % (± 0.1) | Clase de lógica difusa |
| Membresía | `Trap(0,0,2,5)` en x = 3 | 0.667 | Clase |
| Membresía | `Tri(2,5,8)` en x = 3 | 0.333 | Clase |
| Horizonte | H = 2.5 | μ = (0.25, 0.167, 0), m_H ≈ 1.30 | Informe v1.1 §4.5.1 |
| Horizonte | Etiqueta "largo" | μ_Largo = 1, m_H = 0.7 | Informe v1.1 §4.5.1 |
| Absorción | r = 0.25, E = 3 | Pertenencias r = (0.75, 0.167, 0), E = (0.333, 0.25) | Informe v1.1 §4.5.2 |
| Contexto | s_pol = −1, s_mac = 0, s_tend = 0 | Tabla 4.6.4 (p. ej. acciones μ' = 9.7 %, σ' = 28.5 %) | Informe v1.1 §4.6.4 |
| Fitness base | E = 6 %, σ = 10 %, λ = 2 | −0.14 | Informe (en decimales) |

> El centroide de absorción con Mamdani diferirá del 0.54 del Sugeno de la v1.1; su valor de referencia se fija con el primer cálculo verificado a mano y se documenta.

## Propiedades

- **Cromosoma:** `wᵢ ≥ 0`, `Σwᵢ = 1 ± 1e−9`, `wᵢ ≤ tope`, `c ∈ [0, 1]`, después de cualquier operador.
- **AG:** con elitismo, el mejor fitness por generación es no decreciente; misma semilla → mismo resultado.
- **Membresía:** valores en [0, 1]; cobertura sin huecos en cada universo.
- **Interruptores:** difuso y contexto apagados → fitness = `E − λσ`.
- **Covarianza ajustada:** simétrica, semidefinida positiva, conserva ρ.
- **Perfiles:** λ_ef mayor → σ del portafolio óptimo no mayor (monotonía, verificada en promedio sobre semillas).

## Integración

- `POST /api/interpret` con texto incompleto → `completo = false` + pregunta.
- `POST /api/interpret` con texto completo → perfil válido.
- `POST /api/recommend` → contrato completo; montos en S/ suman el total.
- Flujo completo texto → recomendación en modo offline, sin red.

## Golden set de IA generativa

15–20 textos en español peruano coloquial:

| Tipo | Ejemplo | Esperado |
|---|---|---|
| Completo | "Tengo S/ 5000 de mis S/ 20000, no me gusta arriesgar y no los necesito en 3 años; tengo 4 meses de colchón" | Todos los campos; perfil conservador |
| Horizonte cualitativo | "...para dentro de unos añitos" | Etiqueta o pregunta, nunca un número inventado |
| Falta monto | "Quiero invertir sin arriesgar mucho" | Pregunta por el monto |
| Contradictorio | "Quiero máxima ganancia pero no puedo perder nada" | Pregunta aclaratoria |
| Rechaza dar ahorros | "Prefiero no decir cuánto tengo ahorrado" | Absorción "Media" + supuesto declarado |

Métricas: exactitud por campo, porcentaje de ambiguos que generan pregunta (objetivo 100 %), porcentaje de JSON válidos.

## Experimentos de ablación

| Configuración | Difuso | Contexto |
|---|---|---|
| Base | Off | Off |
| Solo difuso | On | Off |
| Solo contexto | Off | On |
| Completo | On | On |

× 3 perfiles (conservador, moderado, agresivo) × 10 semillas. Métricas: pesos, E, σ, fitness, concentración (índice de Herfindahl), `c` frente al centroide, generaciones hasta converger. Salida: CSV en `experiments/results/` + figuras para el informe.
