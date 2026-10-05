# InvestWise

Recomendador educativo de inversiones para el curso de **Software Inteligente**. Una persona describe su situación con sus palabras ("tengo S/ 5,000 de mis S/ 20,000, no me gusta arriesgar…") y recibe una distribución de ejemplo en soles entre cinco tipos de inversión (fondos de acciones, fondos mixtos, fondos de deuda, bonos soberanos y depósito a plazo fijo), con una explicación sencilla, escenarios a un año y los supuestos usados.

> **Aviso educativo.** InvestWise es un proyecto universitario. Sus resultados son ejemplos calculados con supuestos y datos históricos; no constituyen asesoría financiera ni una recomendación de inversión.

## Módulos del curso en el código

| Módulo del curso | Carpeta | Qué hace |
|---|---|---|
| IA generativa | `ai/generative` | Interpreta el texto libre (extrae campos y formula preguntas de aclaración) y redacta la explicación, con validación de que todos los números citados existan. Adaptadores para OpenAI y Anthropic, y un modo offline determinista. |
| Algoritmos heurísticos | `ai/heuristic` | Algoritmo genético con cromosoma `[w₁…w₅ \| c]`: cinco pesos y un gen difuso de capacidad de absorción. Torneo, cruce aritmético, mutación gaussiana, elitismo, tope de 40 % por categoría y parada por convergencia. |
| Razonamiento bajo incertidumbre: lógica difusa | `ai/uncertainty/fuzzy` | Horizonte → multiplicador de aversión m_H (Sugeno, en el fitness). Proporción invertida y fondo de emergencia → conjunto de capacidad de absorción (Mamdani sin desfuzzificar, evaluado en el gen `c`). |
| Razonamiento bajo incertidumbre: bayesiano | `ai/uncertainty/bayesian` | Estimación de retorno y riesgo por categoría con actualización normal–normal sobre datos de mercado (o el prior de referencia cuando no hay datos). |
| Reglas de contexto | `ai/context` | Base de reglas nítidas que ajusta retornos y volatilidades según el panorama político, la estabilidad macroeconómica y la tendencia de mercado. |

Los módulos de `ai/` usan solo NumPy (sin librerías de lógica difusa, algoritmos genéticos ni optimización de portafolios) y no dependen de FastAPI.

## Arquitectura

```
Texto libre ──► IA generativa: interpretar ──► ¿falta algo? ──sí──► pregunta de aclaración (una a la vez)
                                                   │ no
                                                   ▼
      Bayesiano (μ, σ, ρ) ─► Horizonte difuso (λ_ef) ─► Absorción difusa (μ_CA) ─► Reglas de contexto
                                                   │
                                                   ▼
                             Algoritmo genético [w | c] ─► IA generativa: explicar
                                                   │
                                                   ▼
                  Distribución en S/ + escenarios + supuestos + detalle técnico (GUI React)
```

| Capa | Carpeta | Tecnología |
|---|---|---|
| Interfaz | `frontend/` | React 18, TypeScript, Vite; sistema de diseño propio (átomos → pantallas), contenedores y una máquina de estados pura para el flujo |
| API | `backend/app/` | FastAPI: `/api/interpret`, `/api/recommend`, `/api/context/defaults`, `/api/market/estimates`, `/health` |
| Inteligencia | `ai/` | Python + NumPy |
| Parámetros y datos | `data/parameters/`, `data/market/` | JSON con todos los parámetros calibrables; CSV de mercado con sus fuentes |
| Experimentos | `experiments/` | Ablación, contexto, gen difuso y calibración; resultados versionados en `experiments/results/` |

## Inicio rápido

Requisitos: Python 3.11 o superior (probado con 3.14) y Node.js 18 o superior.

```bash
# Backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                        # LLM_PROVIDER=offline funciona sin clave
uvicorn backend.app.main:app --reload --port 8000

# Frontend (otra terminal)
cd frontend && npm install && npm run dev   # http://localhost:5173
```

Detalle, variables de entorno y problemas frecuentes: [manual de instalación](docs/manuales/instalacion.md).

## Pruebas

```bash
pytest                          # unitarias, integración de la API y golden set offline
cd frontend && npm test -- --run
python experiments/ablation.py  # experimentos (requiere requirements-experiments.txt para las figuras)
```

Las pruebas de referencia reproducen los resultados de clase y del informe (por ejemplo, la propina Mamdani P* = 16.009 %, m_H(2.5) ≈ 1.30 y la tabla 4.6.4 de contexto) y verifican las invariantes del AG (Σw = 1, w ≤ 0.40, c ∈ [0, 1], elitismo monótono, reproducibilidad por semilla).

## Documentación

| Carpeta | Contenido |
|---|---|
| [`docs/analisis/`](docs/analisis/README.md) | Análisis del enunciado, feedback docente, teoría del curso, propuesta del gen difuso y decisiones de diseño |
| [`docs/plan/`](docs/plan/README.md) | Arquitectura, fases, estrategia de pruebas, entregables, riesgos, frontend y prompts |
| [`docs/experimentos/`](docs/experimentos/README.md) | Resultados e interpretación de la ablación, el contexto, el gen `c` y la calibración |
| [`docs/manuales/`](docs/manuales/README.md) | Manual de instalación y manual de usuario con capturas |

## Estructura

```
├── ai/                 # Módulos de inteligencia (generative, heuristic, uncertainty, context, shared)
├── backend/app/        # API FastAPI y servicio de orquestación
├── frontend/           # GUI React + Vite
├── data/               # Parámetros (JSON) y datos de mercado (CSV)
├── experiments/        # Experimentos y resultados versionados
├── scripts/            # Descarga de datos de mercado y evaluación del golden set
├── tests/              # unit/, integration/, golden/
└── docs/               # Análisis, plan, experimentos, manuales e informes
```
