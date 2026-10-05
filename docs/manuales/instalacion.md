# Manual de instalación

Este manual explica cómo instalar, configurar, ejecutar y verificar InvestWise en una computadora local con Linux, macOS o Windows. Está dirigido a quien instala o evalúa el proyecto.

InvestWise tiene dos partes que se ejecutan por separado:

- **Backend** en Python (FastAPI). Contiene los módulos de IA (IA generativa, algoritmo genético, lógica difusa, estimación bayesiana y reglas de contexto) y expone la API en el puerto 8000.
- **Frontend** en React con TypeScript (Vite). Es la interfaz web en el puerto 5173. En desarrollo, Vite reenvía las llamadas `/api` al backend.

![Componentes de InvestWise: frontend, API, módulos de IA y datos locales](../arquitectura/01-componentes.png)

La aplicación funciona completa **sin conexión a un modelo de lenguaje** (modo offline). Una clave de API de Anthropic u OpenAI es opcional: mejora la interpretación del texto libre y la redacción de la explicación.

## 1. Requisitos

| Herramienta | Versión | Nota |
|---|---|---|
| Python | 3.12 o superior | El equipo usa Python 3.14. Las versiones actuales de NumPy exigen al menos 3.12. |
| Node.js y npm | Node 20 o superior | Probado con Node 26. npm se instala junto con Node. |
| Git | Cualquier versión reciente | Para clonar el repositorio. |
| Chromium o Google Chrome | Opcional | Solo para descargar de nuevo los datos de mercado (sección 8.1). |
| Clave de API de Anthropic u OpenAI | Opcional | Sin clave, la aplicación corre en modo offline (sección 4). |

Comprueba las versiones instaladas:

```bash
python3 --version     # Windows: py --version
node --version
npm --version
git --version
```

Salvo que se indique otra carpeta, todos los comandos se ejecutan desde la **raíz del repositorio**.

## 2. Obtener el código

```bash
git clone https://github.com/sonedxe/investment-recommender-ai.git
cd investment-recommender-ai
```

Si recibiste el proyecto como archivo comprimido, descomprímelo y abre una terminal en la carpeta resultante.

## 3. Instalar el backend

Crea un entorno virtual de Python, actívalo e instala las dependencias.

### 3.1. Linux y macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2. Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell bloquea la activación con un mensaje sobre la ejecución de scripts, permite los scripts locales solo para tu usuario y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Con el entorno activo, el indicador de la terminal empieza con `(.venv)`. Actívalo de nuevo cada vez que abras una terminal nueva para trabajar con el backend.

`requirements.txt` instala FastAPI, Uvicorn, python-dotenv, NumPy, los SDK de OpenAI y Anthropic, y las herramientas de prueba (pytest y httpx).

## 4. Configurar el archivo `.env`

El backend lee su configuración del archivo `.env` en la raíz. Créalo a partir de la plantilla:

```bash
cp .env.example .env               # Windows (PowerShell): Copy-Item .env.example .env
```

| Variable | Valores | Efecto |
|---|---|---|
| `LLM_PROVIDER` | `offline` (por defecto), `anthropic`, `openai` | Proveedor de IA generativa que interpreta el texto y redacta la explicación |
| `ANTHROPIC_API_KEY` | Clave de Anthropic | Solo con `LLM_PROVIDER=anthropic` |
| `ANTHROPIC_MODEL` | `claude-haiku-4-5-20251001` | Modelo que interpreta el texto y formula las preguntas de aclaración |
| `ANTHROPIC_EXPLAIN_MODEL` | `claude-sonnet-5-5` | Modelo que redacta la explicación del resultado |
| `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL` | Clave, modelo (`gpt-4o-mini`) y URL | Solo con `LLM_PROVIDER=openai`; acepta cualquier servicio compatible con la API de OpenAI |
| `CORS_ORIGINS` | Lista separada por comas | Orígenes del navegador que pueden llamar a la API (por defecto `http://localhost:5173,http://127.0.0.1:5173`) |
| `HOST`, `PORT` | `0.0.0.0`, `8000` | Valores de referencia; el puerto efectivo es el que se pasa a `uvicorn` (sección 6) |

### 4.1. Modo offline

Con `LLM_PROVIDER=offline` (valor de la plantilla) el backend usa un extractor de datos y una plantilla de explicación deterministas: no necesita red ni tiene costo, y ante el mismo texto responde siempre igual. Es el modo recomendado para evaluar el proyecto sin clave y como respaldo en una demostración.

Si eliges `anthropic` u `openai` pero dejas la clave vacía, el backend lo registra en el log y continúa en modo offline; nunca falla al iniciar.

### 4.2. Modo con Anthropic (recomendado por el equipo)

El equipo comparó ambos proveedores con el *golden set* de interpretación y eligió Anthropic. Para crear la clave:

1. Entra a <https://console.anthropic.com> e inicia sesión (o crea una cuenta).
2. En **Billing**, agrega crédito a la organización. Sin saldo, la API rechaza las llamadas.
3. Ve a **API Keys** y pulsa **Create Key**.
4. Escribe un nombre (por ejemplo, `investwise-local`) y, en **Scope**, elige **Default workspace**. Una clave con alcance de **Organization** no sirve: la API la rechaza con el mensaje *"This API key is not scoped to a workspace"*.
5. Copia la clave en ese momento; la consola no vuelve a mostrarla completa.

Luego edita `.env`:

```dotenv
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<pega aquí tu clave>
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
ANTHROPIC_EXPLAIN_MODEL=claude-sonnet-5-5
```

Reinicia el backend después de cada cambio en `.env`. Una consulta completa hace pocas llamadas al modelo y cuesta centavos de dólar.

### 4.3. Modo con OpenAI

Define `LLM_PROVIDER=openai`, `OPENAI_API_KEY` y, si hace falta, `OPENAI_MODEL` y `OPENAI_BASE_URL` (por ejemplo, para Azure, Groq u Ollama). El resto funciona igual.

### 4.4. Cuidado con las claves

- `.env` está excluido del repositorio por `.gitignore`. **Nunca lo subas** ni pegues la clave en un mensaje, captura o documento.
- Si una clave se expone, revócala en la consola del proveedor y crea otra.
- Las pruebas automáticas fuerzan el modo offline aunque `.env` tenga una clave (`tests/conftest.py`), así que ejecutar `pytest` no consume crédito.

## 5. Instalar el frontend

```bash
cd frontend
npm install
cd ..
```

`npm install` descarga React, Vite, TypeScript y Vitest en `frontend/node_modules`. Las versiones recientes de npm pueden mostrar un aviso `npm warn install-scripts`; no impide ejecutar ni compilar la aplicación.

## 6. Ejecutar la aplicación

Usa dos terminales.

**Terminal 1, backend** (desde la raíz, con el entorno virtual activo):

```bash
uvicorn backend.app.main:app --port 8000
```

Agrega `--reload` si vas a modificar el código del backend y quieres que se reinicie solo.

**Terminal 2, frontend:**

```bash
cd frontend
npm run dev
```

Abre <http://localhost:5173> en el navegador. Vite reenvía `/api/*` a `http://localhost:8000`, así que el backend debe estar corriendo.

Para una versión de producción del frontend, `npm run build` genera la carpeta `frontend/dist/`.

## 7. Verificar la instalación

| Paso | Comando | Resultado esperado |
|---|---|---|
| Salud del backend | `curl http://localhost:8000/health` | `{"status":"ok","app":"investment-recommender-ai"}` |
| Módulos de IA | `curl http://localhost:8000/api/ping` | Los tres módulos con `"status":"ok"`; el módulo `generative` indica `"mode":"api"` si hay un proveedor activo o `"mode":"offline"` si no |
| Pruebas del backend | `pytest` (en la raíz, con el entorno activo) | Todas pasan (303 aprobadas y 3 omitidas al cierre de esta versión) |
| Pruebas del frontend | `cd frontend && npm test -- --run` | 15 archivos y 84 pruebas aprobadas |
| Primera recomendación | Abrir <http://localhost:5173>, pulsar **Usar este ejemplo** y luego **Calcular distribución** | Una pregunta de aclaración o directamente la distribución en soles |

En Windows PowerShell, usa `curl.exe` en lugar de `curl` (o `Invoke-RestMethod http://localhost:8000/health`).

También puedes probar la API sin el frontend:

```bash
curl -s http://localhost:8000/api/recommend \
  -H 'content-type: application/json' \
  -d '{"profile": {"amount": 5000, "risk_profile": "moderado", "horizon_years": 5,
                   "total_savings": 20000, "emergency_months": 4},
       "seed": 1}'
```

La respuesta es un JSON con el modo (`"mode":"offline"` o `"mode":"llm"`), el perfil, la distribución en soles, la explicación, los escenarios y el bloque técnico.

## 8. Herramientas opcionales

Ninguna es necesaria para usar la aplicación.

### 8.1. Actualizar los datos de mercado

La aplicación lee los CSV versionados en `data/market/`; no necesita internet. Para descargarlos de nuevo:

1. Instala Chromium o Google Chrome (por ejemplo `sudo pacman -S chromium` o `sudo apt install chromium`; en Windows y macOS basta Google Chrome).
2. Instala las dependencias de datos: `pip install -r requirements-data.txt` (`openpyxl` lee el archivo de la SBS; `yfinance` solo se usa con `--stocks-source yahoo`).
3. Ejecuta:

```bash
python scripts/fetch_market_data.py
```

El script descarga del BCRP (con Chromium sin interfaz, una petición por serie) las series de acciones (Índice General BVL), deuda (tasa de los CD BCRP), bonos soberanos (rendimiento del BTP a 10 años) y depósito a plazo (tasa pasiva de 181 a 360 días) desde 2010, y de la SBS el valor cuota del Fondo 2 de las AFP para los fondos mixtos. Reescribe los CSV de `data/market/` y su `manifest.json`.

| Opción | Efecto |
|---|---|
| `--only bcrp` o `--only sbs` | Descarga solo una fuente y conserva el resto del manifiesto |
| `--stocks-source yahoo` | Usa el ETF EPU convertido a soles como respaldo para acciones |
| `--start 2010-1` | Primer mes de la descarga (formato del BCRP) |

Si la SBS no responde, se conservan los CSV versionados. Las fuentes, transformaciones y advertencias están en `data/market/SOURCES.md` y `docs/analisis/09-fuentes-de-datos.md`.

### 8.2. Evaluar la IA generativa con el *golden set*

```bash
python scripts/eval_golden_set.py --provider offline
python scripts/eval_golden_set.py --provider anthropic    # requiere ANTHROPIC_API_KEY
```

Ejecuta los casos de `tests/golden/` contra el proveedor elegido y escribe el reporte en `experiments/results/golden_<proveedor>.md` (exactitud por campo, JSON válido, preguntas formuladas y latencia). La ejecución con Anthropic consume crédito.

### 8.3. Experimentos de ablación y calibración

```bash
pip install -r requirements-experiments.txt
python experiments/ablation.py
```

Tarda unos 20 segundos, regenera las tablas y figuras de `experiments/results/` y su interpretación está en `docs/experimentos/`.

## 9. Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Address already in use` al iniciar el backend | El puerto 8000 está ocupado (quizá por otra instancia del backend) | Cierra el proceso que lo usa o inicia en otro puerto (`--port 8001`) y ajusta `target` en `frontend/vite.config.ts`. |
| Vite abre en un puerto distinto de 5173 | El puerto 5173 está ocupado | Usa la URL que muestra Vite. Si ese origen no está en `CORS_ORIGINS` y llamas a la API directamente, agrégalo. |
| El frontend muestra "No pudimos conectar con el servicio" | El backend no está corriendo o está en otro puerto | Inicia `uvicorn` en el puerto 8000 y pulsa **Intentar de nuevo**. |
| Error de CORS en la consola del navegador | El frontend se abrió desde un origen no permitido | Agrega ese origen a `CORS_ORIGINS` en `.env` y reinicia el backend. Con `npm run dev` y su proxy no hace falta. |
| Aparecen la etiqueta **Modo sin conexión** y una franja amarilla | El backend corre sin proveedor de IA generativa (`LLM_PROVIDER=offline` o sin clave) | Es el comportamiento esperado. Para usar un modelo, define `LLM_PROVIDER` y su clave y reinicia el backend. |
| Las preguntas y explicaciones salen más esquemáticas aunque configuraste una clave | La clave es inválida, expiró, no tiene saldo o el proveedor no responde | Cada llamada se intenta dos veces y luego usa el generador offline; la recomendación se calcula igual. En este caso no aparece la franja amarilla, porque el proveedor sigue configurado: revisa el log del backend (`fell back to offline` o `fell back to the template`) y corrige la clave. |
| `This API key is not scoped to a workspace` en el log | La clave de Anthropic se creó con alcance de organización | Crea una clave nueva con **Scope: Default workspace** (sección 4.2). |
| `pip install` intenta compilar NumPy y falla | Versión de Python antigua o pip desactualizado, sin ruedas precompiladas | Usa Python 3.12 o superior y actualiza pip: `python -m pip install -U pip`. |
| PowerShell no deja ejecutar `Activate.ps1` | Política de ejecución de scripts restringida | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` (sección 3.2). |
| `ModuleNotFoundError: backend` o `ai` | Comando ejecutado fuera de la raíz o sin el entorno activo | Ejecuta `uvicorn` y `pytest` desde la raíz con el entorno virtual activo. |
| `fetch_market_data.py` no encuentra el navegador o el BCRP devuelve una página de bloqueo | Falta Chromium o el BCRP no superó su verificación anti-bot | Instala Chromium o Chrome y vuelve a intentarlo más tarde. Para acciones puedes usar `--stocks-source yahoo`; la aplicación sigue funcionando con los CSV versionados. |
