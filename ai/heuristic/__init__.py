"""Heuristic optimization module.

Implements the genetic algorithm that searches the extended chromosome
``[w1..w5 | c]``: five portfolio weights (sum 1, capped per category) plus the
fuzzy absorption gene ``c``, evaluated with the extended fitness function.
"""

from ai.heuristic.chromosome import random_population, repair, repair_weights
from ai.heuristic.fitness import FitnessBreakdown, FitnessInputs, evaluate, evaluate_population
from ai.heuristic.genetic_algorithm import GAResult, run_ga

__all__ = [
    "FitnessBreakdown",
    "FitnessInputs",
    "GAResult",
    "evaluate",
    "evaluate_population",
    "ping",
    "random_population",
    "repair",
    "repair_weights",
    "run_ga",
]


def ping() -> dict:
    """Check that the module responds (used by the connectivity test)."""
    return {
        "module": "heuristic",
        "status": "ok",
        "planned": ["genetic_algorithm"],
    }
