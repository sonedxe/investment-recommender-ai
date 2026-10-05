"""FastAPI backend: health checks plus the recommendation flow routes (``/api/...``)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai import generative, heuristic, uncertainty
from backend.app.api.routes import router
from backend.app.core import config

app = FastAPI(
    title="Investment Recommender AI",
    description="Software inteligente: IA generativa + heurística + razonamiento bajo incertidumbre.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


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