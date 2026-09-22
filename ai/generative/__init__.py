"""Módulo de IA generativa (en desarrollo).

Aquí se conectará el sistema a una API de LLM (OpenAI o compatible) para
interpretar solicitudes del usuario, generar información de entrada y
explicar los resultados.
"""

import os


def ping() -> dict:
    """Verifica que el módulo responde (usado por la prueba de conectividad)."""
    return {
        "module": "generative",
        "status": "ok",
        "mode": "api" if os.getenv("OPENAI_API_KEY") else "offline",
    }