# Manual de instalación

InvestWise tiene dos partes que corren por separado: un **backend** en Python (FastAPI, con los módulos de IA) y un **frontend** en React (Vite). En desarrollo, el frontend reenvía las llamadas `/api` al backend.

## 1. Requisitos

| Herramienta | Versión | Nota |
|---|---|---|
| Python | 3.11 o superior | El proyecto se desarrolló y probó con Python 3.14. NumPy 2.3 exige al menos 3.11. |
| Node.js y npm | Node 18 o superior | Probado con Node 26. |
| Git | Cualquiera reciente | Para clonar el repositorio. |
| Clave de API (opcional) | OpenAI o Anthropic | Sin clave, la aplicación funciona completa en modo offline. |

Todos los comandos se ejecutan desde la raíz del repositorio, salvo que se indique otra carpeta.

## 2. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

### Configurar `.env`

| Variable | Valores | Efecto |
|---|---|---|
| `LLM_PROVIDER` | `offline` (por defecto), `openai`, `anthropic` | Proveedor de IA generativa para interpretar el texto y redactar la explicación |
| `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL` | Clave y modelo | Solo con `LLM_PROVIDER=openai` |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `ANTHROPIC_EXPLAIN_MODEL` | Clave y modelos | Solo con `LLM_PROVIDER=anthropic` |
| `CORS_ORIGINS` | Lista separada por comas | Orígenes que pueden llamar a la API (por defecto `http://localhost:5173,http://127.0.0.1:5173`) |

- **Modo offline:** `LLM_PROVIDER=offline` usa un extractor y una plantilla deterministas, sin red ni costo. Es el modo recomendado para evaluar y para la demo de respaldo.
- Si eliges `openai` o `anthropic` pero la clave está vacía, el backend lo registra en el log y sigue en modo offline.
- No subas `.env` al repositorio: contiene tus claves.

### Ejecutar

```bash
uvicorn backend.app.main:app --reload --port 8000
```

## 3. Frontend

```bash
cd frontend
npm install
npm run dev            # http://localhost:5173
```

El servidor de Vite reenvía `/api/*` a `http://localhost:8000`, así que el backend debe estar corriendo. Para una versión de producción: `npm run build` (genera `frontend/dist/`).

## 4. Verificación

| Paso | Comando | Resultado esperado |
|---|---|---|
| Salud del backend | `curl http://localhost:8000/health` | `{"status":"ok","app":"investment-recommender-ai"}` |
| Módulos de IA | `curl http://localhost:8000/api/ping` | Estado de los tres módulos |
| Pruebas del backend | `pytest` (en la raíz, con el entorno activo) | Todas las pruebas pasan |
| Pruebas del frontend | `cd frontend && npm test -- --run` | Todas las pruebas pasan |
| Primera recomendación | Abrir `http://localhost:5173`, pulsar **Usar este ejemplo** y luego **Calcular distribución** | Una pregunta de aclaración o directamente la distribución en soles |

También puedes probar la API sin el frontend:

```bash
curl -s http://localhost:8000/api/recommend -H 'content-type: application/json' \
  -d '{"profile":{"amount":5000,"risk_profile":"moderado","horizon_years":5,"total_savings":20000,"emergency_months":4},"seed":1}'
```

## 5. Herramientas opcionales

No son necesarias para usar la aplicación.

| Herramienta | Instalación | Uso |
|---|---|---|
| Actualizar los datos de mercado | Chromium o Google Chrome instalado (por ejemplo `sudo pacman -S chromium` o `sudo apt install chromium`); `pip install -r requirements-data.txt` solo para el respaldo de Yahoo | `python scripts/fetch_market_data.py` descarga del BCRP (con Chromium sin interfaz, una petición por serie) las series de acciones, deuda, bonos y depósito a plazo desde 2010, reescribe los CSV de `data/market/` y su `manifest.json`. Los fondos mixtos se calculan a partir de acciones y bonos (0.5 y 0.5). `--stocks-source yahoo` usa el ETF EPU en soles como respaldo para acciones. Requiere internet; la aplicación no, porque lee los CSV versionados. Fuentes y advertencias: `data/market/SOURCES.md`. |
| Golden set de IA generativa | — | `python scripts/eval_golden_set.py --provider offline` (o `openai`, `anthropic` con su clave). Escribe el reporte en `experiments/results/golden_<proveedor>.md`. |
| Experimentos de ablación y calibración | `pip install -r requirements-experiments.txt` | `python experiments/ablation.py` (unos 25 segundos). Ver [docs/experimentos](../experimentos/README.md). |

## 6. Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Address already in use` al iniciar | El puerto 8000 o 5173 está ocupado | Cierra el proceso que lo usa o cambia el puerto (`--port 8001`). Si cambias el del backend, ajusta `target` en `frontend/vite.config.ts`. Vite elige otro puerto si 5173 está ocupado; revisa la URL que muestra. |
| El frontend muestra un error de conexión | El backend no está corriendo o está en otro puerto | Inicia `uvicorn` en el puerto 8000 y vuelve a intentar. |
| Error de CORS en la consola del navegador | Abriste el frontend desde un origen no permitido (otro puerto o dominio) | Agrega ese origen a `CORS_ORIGINS` en `.env` y reinicia el backend. Con `npm run dev` y el proxy no hace falta. |
| Aparece "Modo sin conexión" | El backend corre sin modelo de lenguaje (offline o sin clave) | Es el comportamiento esperado. Para usar un modelo real, define `LLM_PROVIDER` y su clave. |
| La clave de API es inválida o el proveedor falla | Error de autenticación o de red | Cada llamada fallida se reintenta una vez y luego cae al generador offline; el log del backend registra la advertencia. La recomendación se calcula igual. |
| `pip install` falla compilando NumPy | Versión de Python antigua o sin ruedas precompiladas | Usa Python 3.11 o superior (probado con 3.14) y actualiza pip: `pip install -U pip`. |
| `ModuleNotFoundError: backend` o `ai` | Comando ejecutado fuera de la raíz | Ejecuta `uvicorn` y `pytest` desde la raíz del repositorio. |
