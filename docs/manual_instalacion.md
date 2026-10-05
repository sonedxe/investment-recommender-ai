# Manual de Instalación — InvestWise (Recomendador de Inversión con IA)

Este manual describe cómo instalar y ejecutar el sistema en una computadora
local (Windows, macOS o Linux), con o sin conexión a una API de IA generativa.

---

## 1. Requisitos previos

| Software | Versión mínima | Verificación |
|---|---|---|
| Python | 3.11+ (probado en 3.14) | `python --version` |
| Node.js | 18+ (probado en 24) | `node --version` |
| npm | 9+ | `npm --version` |
| Git | cualquiera | `git --version` |

No se requiere GPU ni ningún servicio externo obligatorio. La clave de API de
IA generativa (OpenAI o compatible) es **opcional**: sin ella, el sistema opera
en modo *offline* con un interpretador y un explicador deterministas.

## 2. Obtener el código

```bash
git clone https://github.com/sonedxe/investment-recommender-ai.git
cd investment-recommender-ai
```

## 3. Backend (API REST — FastAPI)

### 3.1. Crear el entorno virtual e instalar dependencias

**Windows (PowerShell / CMD):**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencias instaladas: `fastapi`, `uvicorn`, `python-dotenv`, `numpy`,
`pytest` y `httpx` (esta última también sirve de cliente de la API de LLM).

### 3.2. Configurar variables de entorno (opcional)

```bash
cp .env.example .env
```

Sin clave de API, el sistema opera en modo **offline**. Para activar el modo
**API** de IA generativa, la opción recomendada es **Groq (capa gratuita,
sin tarjeta de crédito)**:

1. Cree una cuenta en <https://console.groq.com> (email o Google/GitHub).
2. Abra **API Keys → Create API Key** y copie la clave `gsk_...` (se muestra
   una sola vez).
3. Péguela en `OPENAI_API_KEY` de su archivo `.env` (la URL y el modelo ya
   vienen preconfigurados para Groq en `.env.example`).
4. Reinicie el backend y verifique:

```bash
python scripts/test_groq.py
# debe terminar con: "OK: la API de IA generativa responde correctamente."
```

Capa gratuita de Groq: ~30 solicitudes/minuto y ~14,400/día (de sobra para
este sistema, que hace 1-2 llamadas por consulta).

| Variable | Descripción | Por defecto |
|---|---|---|
| `OPENAI_API_KEY` | Clave del proveedor de LLM. Vacío = modo offline. | *(vacío)* |
| `OPENAI_BASE_URL` | Endpoint compatible con OpenAI. Groq: `https://api.groq.com/openai/v1` | Groq |
| `OPENAI_MODEL` | Modelo de la capa gratuita de Groq (verificados oct-2026): `openai/gpt-oss-120b` (recomendado), `openai/gpt-oss-20b` (más rápido) o `qwen/qwen3.8-27b`. Lista vigente: `GET https://api.groq.com/openai/v1/models` con su clave. | `openai/gpt-oss-120b` |
| `CORS_ORIGINS` | Orígenes permitidos (separados por coma). | `http://localhost:5173,...` |

> **Importante:** los modelos gratuitos de Groq cambian con el tiempo. Si el
> log del backend muestra un `404` al llamar la API, consulte la lista vigente
> con `curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer
> <su_clave>"` y actualice `OPENAI_MODEL`.

> **Nota:** con cualquier error de la API (red, clave inválida, formato), el
> sistema hace *fallback* automático al modo offline: la aplicación nunca se
> queda sin responder.

### 3.3. Arrancar el backend

Desde la raíz del repositorio, con el entorno virtual activado:

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Verificación (en otra terminal):

```bash
curl http://localhost:8000/health
# {"status":"ok","app":"investment-recommender-ai"}

curl http://localhost:8000/api/ping
# {"status":"ok","modules":{"generative":...,"heuristic":...,"uncertainty":...}}
```

Documentación interactiva de la API (Swagger): <http://localhost:8000/docs>

## 4. Frontend (interfaz gráfica — React + Vite)

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Abrir en el navegador: <http://localhost:5173>

El servidor de desarrollo de Vite redirige automáticamente las llamadas
`/api/*` al backend en el puerto 8000 (configurado en `frontend/vite.config.ts`),
por lo que **ambos procesos deben estar encendidos a la vez**.

## 5. Pruebas automatizadas

Desde la raíz del repositorio, con el entorno virtual activado:

```bash
pytest
```

Se ejecutan 43 pruebas: unidades de cada módulo de IA (con verificación
numérica contra los ejemplos del informe técnico v1.1) e integración de la
API de punta a punta (texto del usuario → recomendación explicada).

Para la compilación de producción del frontend:

```bash
cd frontend
npm run build
```

## 6. Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| `uvicorn: no se reconoce` | Entorno virtual no activado o scripts fuera del PATH | Active `.venv` o use `python -m uvicorn ...` |
| Frontend muestra "¿Está el backend encendido?" | El backend no está corriendo | Arranque el backend (paso 3.3) antes de usar la interfaz |
| `npm install` falla con scripts bloqueados | Política de *postinstall* del entorno | `npm install-scripts approve <pkg>` o `npm config set ignore-scripts false` |
| Puerto 8000 ocupado | Otro proceso usa el puerto | `uvicorn ... --port 8001` y ajuste el `proxy` en `frontend/vite.config.ts` |
| Modo API no se activa pese a tener clave | El `.env` no se cargó | Verifique que `.env` esté en la **raíz** del repositorio y reinicie el backend |

## 7. Estructura del proyecto (referencia)

```
├── ai/                     # Módulos de inteligencia
│   ├── generative/         #   M1: IA generativa (interpretación + explicación)
│   ├── heuristic/          #   M3: algoritmo genético
│   ├── uncertainty/        #   M2 bayesiano · M4 lógica difusa · M5 contexto
│   └── reference_data.py   #   Anexos A y C del informe técnico
├── backend/app/            # API REST (FastAPI) + orquestador del flujo
├── frontend/src/           # Interfaz gráfica (React + TypeScript)
├── tests/                  # 43 pruebas unitarias y de integración
└── docs/                   # Entregables: manuales e informe técnico
```
