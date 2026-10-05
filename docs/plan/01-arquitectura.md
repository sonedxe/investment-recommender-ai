# 01 · Arquitectura

## Capas

| Capa | Ubicación | Responsabilidad | Puede depender de |
|---|---|---|---|
| Núcleo de IA | `ai/` | Lógica difusa, bayes, reglas de contexto, AG, interpretación/explicación | NumPy, tipos de `ai/shared` |
| Aplicación | `backend/app/services/` | Orquesta el flujo de 8 etapas | `ai/` |
| Adaptadores de entrada | `backend/app/api/` | HTTP (FastAPI), validación de esquemas | Aplicación |
| Adaptadores de salida | `ai/generative/adapters/` | Proveedor LLM (API compatible con OpenAI) y modo offline | Puerto `LanguageModel` |
| Presentación | `frontend/` | GUI React | API HTTP |

**Reglas de dependencia**

- `ai/` nunca importa FastAPI ni `backend/`.
- `ai/heuristic` no conoce la implementación difusa ni la de contexto: recibe `λ_ef`, la función `μ_CA`, `μ'` y `Σ'` ya calculados. Así cada módulo se prueba aislado.
- El único acceso a red dentro de `ai/` está en `ai/generative/adapters/`, detrás del puerto.

## Estructura de carpetas

Se conserva la división por módulo del curso (`generative`, `heuristic`, `uncertainty`) porque es la que el evaluador busca y la que describe el informe.

```
ai/
├── shared/
│   └── types.py               # Category, UserProfile, MarketEstimates, ContextFactors, Portfolio
├── uncertainty/
│   ├── fuzzy/
│   │   ├── membership.py      # tri(), trap()
│   │   ├── sugeno.py          # motor Sugeno de orden cero
│   │   ├── mamdani.py         # implicación min, agregación max, centroide
│   │   ├── horizon.py         # conjunto en el FITNESS  -> λ_ef
│   │   └── absorption.py      # conjunto en el CROMOSOMA -> μ_CA
│   └── bayesian/
│       ├── estimation.py      # μ, σ, ρ desde series
│       ├── normal_update.py   # actualización conjugada normal-normal
│       └── trend.py           # s_tend
├── context/
│   ├── rules.py               # RC1–RC7 como reglas condición -> efecto, con trazas
│   └── adjustment.py          # μ', σ', Σ' (preserva ρ)
├── heuristic/
│   ├── chromosome.py          # [w1..w5 | c], inicialización, reparación
│   ├── fitness.py             # fitness ampliado con desglose e interruptores
│   ├── operators.py           # torneo, cruce, mutación
│   └── genetic_algorithm.py   # bucle, elitismo, convergencia, historial
└── generative/
    ├── port.py                # Protocol LanguageModel
    ├── interpreter.py         # texto -> perfil + pregunta de aclaración
    ├── explainer.py           # resultado -> explicación + validación de cifras
    ├── prompts/               # plantillas versionadas
    └── adapters/
        ├── openai_compatible.py
        └── offline.py         # determinista, sin red

backend/app/
├── api/
│   ├── routes.py
│   └── schemas.py             # Pydantic: contratos de entrada/salida
├── services/
│   └── recommendation.py      # caso de uso: flujo de 8 etapas
└── core/config.py

data/
├── market/                    # series históricas (CSV versionado)
└── parameters/                # Anexo A, Anexo C, conjuntos difusos (JSON)

experiments/
└── ablation.py                # genera CSV + gráficos para el informe

tests/
├── unit/                      # por módulo
└── integration/               # API + flujo completo en modo offline

frontend/src/
├── components/
│   ├── atoms/                 # Button, Badge, Slider3
│   ├── molecules/             # MessageBubble, FactorSelector, MembershipChart
│   └── organisms/             # Chat, PortfolioResult, ConvergenceChart, ContextPanel, TechnicalDetail
├── containers/                # lógica y llamadas a la API (contenedor-presentacional)
├── api/
└── types/
```

## Flujo de datos (8 etapas)

| Etapa | Módulo | Entrada → Salida |
|---|---|---|
| 1 | GUI | Texto libre del usuario |
| 2 | IA generativa (interpretación) | Texto + historial → perfil estructurado o pregunta de aclaración |
| 3 | Bayesiano | Series → μ, σ, ρ, s_tend (precalculado y cacheado) |
| 4 | Difuso | Horizonte → λ_ef · Absorción → μ_CA (conjunto) + centroide |
| 5 | Contexto | μ, σ, ρ, s_tend + factores → μ', σ', Σ' + reglas activadas |
| 6 | AG | λ_ef, μ_CA, μ', Σ' → mejor `[w | c]` + desglose + historial |
| 7 | IA generativa (explicación) | Todo lo anterior → texto en lenguaje simple |
| 8 | GUI | Portafolio, explicación, convergencia, contexto, detalle técnico |

## Contratos entre módulos

Actualizan la sección 4.7 de la v1.1 con el gen difuso `c`.

| Interfaz | Entrada | Salida |
|---|---|---|
| Interpretación | `texto`, `historial` | `{monto_invertir, horizonte_anios \| horizonte_etiqueta, perfil_riesgo (enum), ahorro_total?, cobertura_emergencia_meses?, completo, pregunta_aclaracion?, supuestos[]}` |
| Bayesiano | `series[5]`, `nueva_observacion?` | `{mu[5], sigma[5], rho[5×5], s_tend[5]}` |
| Difuso: horizonte | `horizonte_anios \| etiqueta`, `lambda_base` | `{pertenencias, m_H, lambda_ef}` |
| Difuso: absorción | `monto_invertir`, `ahorro_total`, `cobertura_emergencia_meses` | `{r, E, pertenencias, activaciones[RA1..RA6], mu_CA (malla), CA_centroide}` |
| Contexto | `mu, sigma, rho, s_tend, s_pol, s_mac, parametros` | `{c[5], mu_aj[5], sigma_aj[5], cov_aj[5×5], reglas_activadas[]}` |
| AG | `lambda_ef, mu_CA, sigma_piso, a, phi, kappa, mu_aj, cov_aj, tope, interruptores, semilla` | `{pesos[5], c, mu_CA_c, fitness, desglose{retorno, contexto, riesgo, penalizacion, recompensa_difusa}, E, sigma, historial}` |
| Explicación | Resultado del AG + perfil + pertenencias + reglas activadas + supuestos | `{texto, cifras_citadas[]}` |

## API HTTP

| Método | Ruta | Uso |
|---|---|---|
| `GET` | `/health` | Estado (ya existe) |
| `POST` | `/api/interpret` | Etapa 2: devuelve perfil o pregunta de aclaración |
| `POST` | `/api/recommend` | Etapas 3–7 con perfil completo, factores e interruptores |
| `GET` | `/api/context/defaults` | Factores y parámetros por defecto para el panel |
| `GET` | `/api/market/estimates` | μ, σ, ρ, s_tend actuales (detalle técnico) |

`/api/ping` se mantiene hasta que los tests de integración lo reemplacen.

## Dependencias nuevas

| Paquete | Uso |
|---|---|
| `numpy` | Núcleo matemático |
| `pydantic` | Esquemas (ya incluido con FastAPI) |
| `openai` | Cliente compatible (o `httpx` directo) |
| `matplotlib` | Solo en `experiments/` para figuras del informe |
| Librería de gráficos en el frontend (p. ej. Recharts) | Portafolio, convergencia, funciones de pertenencia |
