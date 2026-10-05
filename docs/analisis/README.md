# Análisis del proyecto InvestWise

Análisis previo a la implementación: consolida el enunciado, los entregables del equipo (semanas 3 y 5), el feedback del docente, el contenido de las clases y el estado del repositorio.

> Fecha: 2026-10-04 · Rama: `feature/parcial-v1` · El plan derivado de este análisis está en [`../plan/`](../plan/README.md).

## Índice

| Archivo | Contenido |
|---|---|
| [01-trazabilidad-y-enunciado.md](01-trazabilidad-y-enunciado.md) | Evolución del proyecto y cumplimiento del enunciado |
| [02-feedback-docente.md](02-feedback-docente.md) | Qué pidió el docente y la brecha de la v1.1 |
| [03-teoria-del-curso.md](03-teoria-del-curso.md) | Lógica difusa, algoritmos genéticos, proyectos y otras clases: implicaciones |
| [04-propuesta-difusa-cromosoma.md](04-propuesta-difusa-cromosoma.md) | Diseño propuesto: un conjunto difuso en el fitness y otro en el cromosoma |
| [05-hallazgos-tecnicos.md](05-hallazgos-tecnicos.md) | Problemas del modelo, datos, reglas de contexto y repositorio |
| [06-decisiones-pendientes.md](06-decisiones-pendientes.md) | Decisiones que bloquean la implementación |
| [07-feedback-explicado.md](07-feedback-explicado.md) | El feedback del docente explicado: jurado (fitness) frente a ADN (cromosoma) |
| [08-horizonte-temporal.md](08-horizonte-temporal.md) | Qué es el horizonte temporal, de qué teoría viene y cómo se modela con lógica difusa |
| [09-fuentes-de-datos.md](09-fuentes-de-datos.md) | Fuentes de datos de mercado (BCRP, Yahoo Finance, SMV/AAFMP) y decisión D3 |
| [10-decisiones-d1-d2-d5.md](10-decisiones-d1-d2-d5.md) | Detalle de D1 (validación con el docente), D2 (tope de concentración) y D5 (escala de λ) |

## Resumen ejecutivo

| # | Hallazgo | Severidad | Dónde |
|---|---|---|---|
| 1 | La v1.1 **no cumple el feedback del docente**: ambos conjuntos difusos actúan sobre el fitness; ninguno forma parte del cromosoma. | 🔴 Crítica | [02](02-feedback-docente.md), [04](04-propuesta-difusa-cromosoma.md) |
| 2 | Con los datos del Anexo A el AG produce **portafolios degenerados** (100 % acciones o ~90 % depósito). Verificado numéricamente. | 🔴 Crítica | [05 §1](05-hallazgos-tecnicos.md#1--portafolios-degenerados-verificado) |
| 3 | El repositorio es **solo un esqueleto** y sus docstrings describen técnicas que no están en el informe. | 🟠 Alta | [05 §7](05-hallazgos-tecnicos.md#7-estado-del-repositorio) |
| 4 | Falta definir la **matriz de correlaciones**, la **fuente de datos** y el **mapeo texto → λ_base**. | 🟠 Alta | [05 §2–4](05-hallazgos-tecnicos.md) |
| 5 | Ambos sistemas difusos usan Sugeno-0; el docente desarrolla en detalle **Mamdani**. | 🟡 Media | [03 §1](03-teoria-del-curso.md#1-lógica-difusa) |
| 6 | Las reglas de contexto son fórmulas, no una base de reglas SI–ENTONCES explícita. | 🟡 Media | [05 §6](05-hallazgos-tecnicos.md#6-reglas-de-contexto) |
