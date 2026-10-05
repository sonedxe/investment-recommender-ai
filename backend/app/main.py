"""Backend FastAPI — Investment Recommender AI (InvestWise).

Expone la API REST que orquesta los módulos de IA del sistema:

- `GET  /health`                  : verificación de vida.
- `GET  /api/ping`                : conectividad con los 3 módulos de IA.
- `GET  /api/categories`          : categorías de inversión y datos de referencia.
- `POST /api/interpret`           : Módulo 1 (IA generativa) — interpreta el
                                    texto del usuario y, si falta información,
                                    devuelve una pregunta de aclaración.
- `POST /api/recommend`           : flujo completo (etapas 3-7 de la sección
                                    4.1): bayesiano -> difuso -> contexto ->
                                    genético -> explicación.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai import generative, heuristic, uncertainty
from ai.reference_data import (
    A_TEND,
    C_MAX,
    CATEGORIAS,
    CONTEXT_PARAMS,
    DESCRIPCIONES_SIMPLES,
    MU_REF,
    NOMBRES,
    SIGMA_REF,
)
from backend.app.core import config
from backend.app.schemas import InterpretRequest, RecommendRequest
from backend.app.services.pipeline import run_pipeline

app = FastAPI(
    title="Investment Recommender AI",
    description=(
        "Software inteligente: IA generativa + algoritmo genético + razonamiento "
        "bajo incertidumbre (bayesiano, lógica difusa y reglas de contexto)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": "investment-recommender-ai"}


@app.get("/api/ping")
def ping() -> dict:
    """Prueba de conectividad: el backend responde y consulta los 3 módulos de IA."""
    return {
        "status": "ok",
        "modules": {
            "generative": generative.ping(),
            "heuristic": heuristic.ping(),
            "uncertainty": uncertainty.ping(),
        },
    }


@app.get("/api/categories")
def categories() -> dict:
    """Datos de referencia de las 5 categorías y parámetros de contexto."""
    return {
        "categorias": [
            {
                "id": cat,
                "nombre": NOMBRES[cat],
                "descripcion": DESCRIPCIONES_SIMPLES[cat],
                "mu_referencia": MU_REF[cat],
                "sigma_referencia": SIGMA_REF[cat],
                "parametros_contexto": CONTEXT_PARAMS[cat],
            }
            for cat in CATEGORIAS
        ],
        "parametros_globales": {"a_tend": A_TEND, "c_max": C_MAX},
    }


@app.post("/api/interpret")
def interpret(req: InterpretRequest) -> dict:
    """Interpreta el texto del usuario (Módulo 1, entrada).

    Si falta información crítica, devuelve `completo=false` y una pregunta de
    aclaración (loop de clarificación, requisito formal de la sección 4.2).
    El frontend vuelve a llamar a este endpoint con la conversación acumulada.
    """
    return generative.interpret(req.texto).a_dict()


@app.post("/api/recommend")
def recommend(req: RecommendRequest) -> dict:
    """Ejecuta el flujo completo y devuelve la recomendación explicada."""
    return run_pipeline(
        perfil=req.perfil,
        contexto=req.contexto,
        interruptores=req.interruptores,
        seed=req.seed,
    )
