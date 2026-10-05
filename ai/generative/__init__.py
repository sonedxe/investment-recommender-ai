"""Módulo de IA generativa (Módulo 1 del informe técnico).

Puente en lenguaje natural entre el usuario y los módulos técnicos, en ambos
sentidos:

- `interpret(texto)`: texto libre -> datos estructurados del perfil, con loop
  de clarificación (nunca asume valores en silencio ante información faltante
  o ambigua, salvo declinación explícita del usuario, que se declara).
- `explain(datos)`: portafolio + perfil + contexto -> explicación en lenguaje
  simple siguiendo las reglas de la sección 6.

Modo de operación:
- `api`: si hay OPENAI_API_KEY, usa un LLM compatible con el protocolo
  OpenAI (interpretación y explicación).
- `offline`: parser léxico + explicador por plantillas, determinista.
Ante cualquier fallo de la API se hace fallback al modo offline.
"""

from __future__ import annotations

import logging

from ai.generative import llm_client
from ai.generative.explainer import explicar_offline
from ai.generative.offline_parser import interpretar_offline
from ai.generative.schemas import Interpretacion

__all__ = ["Interpretacion", "interpret", "explain", "ping", "interpretar_offline", "explicar_offline"]

log = logging.getLogger(__name__)


def interpret(texto_usuario: str) -> Interpretacion:
    """Interpreta el texto del usuario (API si hay clave; offline si no)."""
    if llm_client.api_disponible():
        try:
            return llm_client.interpretar_api(texto_usuario)
        except Exception as exc:  # noqa: BLE001 - fallback deliberado
            log.warning("API de IA generativa no disponible (%s); usando modo offline.", exc)
    return interpretar_offline(texto_usuario)


def explain(datos: dict) -> tuple[str, str]:
    """Genera la explicación final. Devuelve (texto, modo_usado)."""
    if llm_client.api_disponible():
        try:
            return llm_client.explicar_api(datos), "api"
        except Exception as exc:  # noqa: BLE001 - fallback deliberado
            log.warning("API de IA generativa no disponible (%s); usando modo offline.", exc)
    return explicar_offline(**datos["offline_kwargs"]), "offline"


def ping() -> dict:
    """Verifica que el módulo responde (usado por la prueba de conectividad)."""
    import os

    return {
        "module": "generative",
        "status": "ok",
        "mode": "api" if os.getenv("OPENAI_API_KEY") else "offline",
    }
