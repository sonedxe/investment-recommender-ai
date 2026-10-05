# Investment Recommender AI — InvestWise

Software inteligente para el curso de **Software Inteligente**: un recomendador
de inversiones del mercado peruano que integra, en una única aplicación con
interfaz gráfica, los tres componentes exigidos por el enunciado:

1. **IA generativa** (`ai/generative`) — conexión a una API de LLM (OpenAI o
   compatible) para interpretar la solicitud del usuario en lenguaje natural
   (con loop de clarificación) y explicar los resultados en lenguaje simple.
   Si no hay clave de API, opera en modo **offline** determinista.
2. **Algoritmo heurístico** (`ai/heuristic`) — algoritmo genético que optimiza
   la distribución del portafolio entre 5 categorías de inversión.
3. **Razonamiento bajo incertidumbre** (`ai/uncertainty`) — inferencia
   bayesiana (retorno, riesgo, covarianza y tendencia por categoría), lógica
   difusa tipo Sugeno (horizonte temporal y capacidad de absorción) y reglas
   de contexto (panorama político, estabilidad macroeconómica, tendencia).

La especificación completa está en `docs/Informe_Tecnico_InvestWise_v1.1.txt`;
la trazabilidad informe ↔ código, en `docs/README.md`.

## Estructura

```
├── ai/                     # Módulos de inteligencia
│   ├── generative/         #   M1: IA generativa (API LLM + fallback offline)
│   ├── heuristic/          #   M3: algoritmo genético
│   ├── uncertainty/        #   M2 bayesiano · M4 lógica difusa · M5 contexto
│   └── reference_data.py   #   Anexos A y C del informe técnico
├── backend/                # API REST con FastAPI (orquestador del flujo)
│   └── app/
├── frontend/               # Interfaz gráfica: React + Vite + TypeScript
├── docs/                   # Entregables: manuales + informe técnico
└── tests/                  # 43 pruebas unitarias y de integración
```

## Puesta en marcha

### 1. Backend

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env            # opcional: añade OPENAI_API_KEY
uvicorn backend.app.main:app --reload --port 8000
```

Verifica:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/ping   # consulta los 3 módulos de IA
```

API (Swagger interactivo): http://localhost:8000/docs

| Endpoint | Descripción |
|---|---|
| `GET /health` | Verificación de vida |
| `GET /api/ping` | Conectividad con los 3 módulos de IA |
| `GET /api/categories` | Categorías y parámetros de referencia |
| `POST /api/interpret` | Interpreta el texto del usuario (loop de clarificación) |
| `POST /api/recommend` | Flujo completo: bayesiano → difuso → contexto → genético → explicación |

### 2. Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173  (hace proxy de /api → :8000)
```

### 3. Pruebas automatizadas

```bash
pytest                        # desde la raíz del repositorio (43 pruebas)
```

## Modo API vs. modo offline de la IA generativa

- **Modo `api`**: se activa al configurar `OPENAI_API_KEY` en `.env` (compatible
  con cualquier proveedor con protocolo OpenAI: Azure, Groq, Ollama, etc.).
- **Modo `offline`**: sin clave (o ante cualquier fallo de la API), un parser
  léxico y un explicador por plantillas cumplen el mismo contrato, de forma
  determinista. La aplicación nunca se queda sin responder.

> **Aviso:** proyecto académico. Las recomendaciones usan promedios históricos
> de referencia y no constituyen asesoría financiera real.
