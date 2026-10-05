"""Módulo de razonamiento bajo incertidumbre.

Agrupa tres componentes (informe técnico v1.1):

- `bayesian` (Módulo 2): estimación bayesiana de retorno, riesgo, covarianza
  y tendencia de las 5 categorías de inversión del mercado peruano.
- `fuzzy` (Módulo 4): lógica difusa (Sugeno de orden cero) para el horizonte
  temporal y la capacidad de absorción de pérdidas del usuario.
- `context` (Módulo 5): reglas de contexto que ajustan las estimaciones con
  factores ambientales (panorama político, estabilidad macro, tendencia).
"""

from ai.uncertainty import bayesian, context, fuzzy
from ai.uncertainty.bayesian import EstimacionActivo, EstimacionMercado, bayesian_update, estimate
from ai.uncertainty.context import ContextoResult, apply_context
from ai.uncertainty.fuzzy import FuzzyResult, evaluar_perfil

__all__ = [
    "bayesian",
    "context",
    "fuzzy",
    "EstimacionActivo",
    "EstimacionMercado",
    "bayesian_update",
    "estimate",
    "ContextoResult",
    "apply_context",
    "FuzzyResult",
    "evaluar_perfil",
]


def ping() -> dict:
    """Verifica que el módulo responde (usado por la prueba de conectividad)."""
    est = estimate()
    return {
        "module": "uncertainty",
        "status": "ok",
        "components": ["bayesian", "fuzzy_logic", "context_rules"],
        "categorias_estimadas": len(est.activos),
    }
