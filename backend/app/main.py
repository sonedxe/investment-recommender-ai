"""Backend FastAPI — esqueleto de conectividad.

Expone endpoints mínimos para comprobar que el backend responde y que
los tres módulos de IA (`ai.generative`, `ai.heuristic`, `ai.uncertainty`)
quedan conectados a la aplicación. La lógica completa se implementará después.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai import generative, heuristic, uncertainty
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