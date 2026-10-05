"""Módulo de algoritmos heurísticos.

Implementa el algoritmo genético (Módulo 3 del informe técnico) que resuelve
el problema de optimización de portafolio: encontrar los pesos w1..w5 que
maximizan la función de aptitud ampliada (retorno ajustado - aversión*riesgo
- penalización por volatilidad excedida), sujeto a que sumen 100% y sean
no negativos.
"""

from ai.heuristic.genetic import GeneticResult, fitness_portafolio, optimize_portfolio

__all__ = ["GeneticResult", "fitness_portafolio", "optimize_portfolio"]


def ping() -> dict:
    """Verifica que el módulo responde (usado por la prueba de conectividad)."""
    return {
        "module": "heuristic",
        "status": "ok",
        "implemented": ["genetic_algorithm"],
    }
