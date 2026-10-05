# Plan de trabajo — InvestWise (semanas 6 y 7)

Plan de implementación derivado del [análisis](../analisis/README.md). Cubre desde las decisiones de diseño pendientes hasta la entrega final y la exposición.

## Índice

| Archivo | Contenido |
|---|---|
| [01-arquitectura.md](01-arquitectura.md) | Capas, estructura de carpetas, contratos entre módulos y API |
| [02-fases-y-tareas.md](02-fases-y-tareas.md) | Backlog por fase con criterios de aceptación y dependencias |
| [03-estrategia-de-pruebas.md](03-estrategia-de-pruebas.md) | Tests de referencia, propiedades, ablación, IA generativa, punta a punta |
| [04-entregables.md](04-entregables.md) | Manuales, informe técnico final, exposición y demo |
| [05-riesgos.md](05-riesgos.md) | Riesgos y mitigaciones |
| [06-frontend.md](06-frontend.md) | Interfaz gráfica: design system, ajustes, integración y tareas |
| [07-prompts-ia-generativa.md](07-prompts-ia-generativa.md) | Prompts, esquemas y validación de la IA generativa |

## Objetivo

Entregar una aplicación con interfaz gráfica que, a partir de un texto libre del usuario, recomiende y explique un portafolio entre 5 categorías de inversión del mercado peruano, integrando de forma coordinada:

1. **IA generativa** (API): interpreta, aclara y explica.
2. **Algoritmo genético**: optimiza un cromosoma `[w1..w5 | c]`.
3. **Razonamiento bajo incertidumbre**: bayesiano (retornos) + lógica difusa (horizonte en el fitness; absorción en el cromosoma).
4. **Reglas de contexto** que ajustan directamente el fitness.

## Principios

| Principio | Aplicación |
|---|---|
| Núcleo primero | La matemática (difuso, contexto, AG, bayes) se construye y se prueba antes que la API y la GUI: es lo que se evalúa. |
| Implementación propia | NumPy puro; sin `scikit-fuzzy`, `DEAP` ni optimizadores de portafolio (el enunciado exige "programar" los módulos). |
| Contratos antes que código | Los tipos y esquemas compartidos se definen en la fase 0 para que los cinco integrantes trabajen en paralelo. |
| Trazabilidad | Cada número del resultado (pertenencias, reglas activadas, desglose del fitness) se expone para la explicación y el panel técnico. |
| Reproducibilidad | Semilla fija en el AG; experimentos con varias semillas y resultados versionados. |
| Modo offline | La app funciona sin API key (generador determinista) para tests y para una demo sin conexión. |

## Fases

```
F0 Decisiones + contratos ──┬─> F1 Difuso ──────┐
                            ├─> F2 Contexto ────┤
                            ├─> F4 Bayesiano ───┼─> F3 AG ─> F5 Orquestación + API ─┬─> F7 GUI ─┐
                            └─> F6a IA gen. (interpretación) ───────────────────────┘           ├─> F8 Experimentos ─> F9 Entregables
                                                 F6b IA gen. (explicación) ─────────────────────┘
```

| Fase | Nombre | Semana |
|---|---|---|
| F0 | Decisiones, contratos y preparación | S6 (inicio) |
| F1 | Lógica difusa | S6 |
| F2 | Reglas de contexto | S6 |
| F3 | Algoritmo genético extendido | S6 |
| F4 | Módulo bayesiano y datos | S6 |
| F5 | Orquestación y API | S6 |
| F6 | IA generativa (a: interpretación, S6 · b: explicación, S7) | S6–S7 |
| F7 | Interfaz gráfica (mínima S6 · completa S7) | S6–S7 |
| F8 | Experimentos: ablación y calibración | S6 (primeras) – S7 |
| F9 | Entregables y exposición | S7 |

## Cronograma

### Semana 6 — meta 60 %

- F0 completa: decisiones D1–D5 cerradas, contratos definidos.
- F1, F2, F3 y F4 completas, con tests de referencia en verde (F4 puede usar el Anexo A como prior si los datos no llegan).
- F5: endpoint `/api/recommend` funcionando de punta a punta.
- F6a: interpretación con loop de clarificación (también en modo offline).
- F7 mínima: entrada de texto, preguntas de aclaración y portafolio resultante.
- Primeras pruebas de ablación (4 configuraciones × 3 perfiles).

### Semana 7 — entrega final

- F6b: explicación en lenguaje simple con validación de cifras.
- F7 completa: convergencia, panel de contexto, detalle técnico.
- F8: ablación completa con varias semillas, calibración de κ, φ y tope.
- F9: manuales, informe técnico final, guion de la demo y ensayo de la exposición.

## Reparto sugerido (5 integrantes)

| Stream | Fases | Perfil |
|---|---|---|
| A — Difuso + contexto | F1, F2 | Matemática y reglas |
| B — Algoritmo genético + experimentos | F3, F8 | Optimización |
| C — Bayesiano + datos + API | F4, F5 | Datos y backend |
| D — IA generativa | F6 | Prompts e integración LLM |
| E — Frontend + manuales | F7, F9 (manuales) | UI y documentación |

El informe técnico final es responsabilidad compartida; cada stream redacta la sección de su módulo.

## Definición de "hecho" (por tarea)

- Código en `feature/*` con tests que pasan (`pytest`).
- Criterio de aceptación de la tarea verificado (ver [02](02-fases-y-tareas.md)).
- Commit con mensaje convencional (`feat:`, `fix:`, `test:`, `docs:`).
- Documentación del módulo actualizada si cambia el contrato.
