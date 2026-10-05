# Investment Recommender AI

Software inteligente para el curso de **Software Inteligente**: un recomendador
de inversiones que integra tres componentes:

1. **IA generativa** (`ai/generative`) — se conecta a una API de LLM para
   interpretar la solicitud del usuario y explicar los resultados (las 5 categorías de inversión son fijas).
2. **Algoritmos heurísticos** (`ai/heuristic`) — optimización/selección de cartera.
3. **Razonamiento bajo incertidumbre** (`ai/uncertainty`) — lógica difusa,
   razonamiento probabilístico / métodos bayesianos.

## Estructura

```
├── ai/                     # Módulos de inteligencia (3 componentes)
│   ├── generative/         #   IA generativa (API LLM)
│   ├── heuristic/          #   Algoritmos heurísticos
│   └── uncertainty/        #   Razonamiento bajo incertidumbre
├── backend/                # API REST con FastAPI (orquestador)
│   └── app/
├── frontend/               # Interfaz gráfica: React + Vite + TypeScript
├── docs/                   # Manuales + informe técnico (entregables)
└── tests/                  # Pruebas de conectividad
```

## Puesta en marcha (esqueleto de prueba)

### 1. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # opcional: añade OPENAI_API_KEY
uvicorn backend.app.main:app --reload --port 8000
```

Verifica:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/ping   # consulta los 3 módulos de IA
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173  (hace proxy a /api → :8000)
```

### 3. Pruebas automatizadas

```bash
pytest                        # desde la raíz del repositorio
```

> El módulo de IA generativa funciona en modo `api` si hay `OPENAI_API_KEY`
> configurada, y en modo `offline` si no. La conexión entre módulos se
> desarrollará en las siguientes iteraciones.