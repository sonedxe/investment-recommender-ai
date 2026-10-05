"""Heuristic optimization module.

Implements the genetic algorithm that searches the extended chromosome
``[w1..w5 | c]``: five portfolio weights (sum 1, capped per category) plus the
fuzzy absorption gene ``c``, evaluated with the extended fitness function.
"""


def ping() -> dict:
    """Check that the module responds (used by the connectivity test)."""
    return {
        "module": "heuristic",
        "status": "ok",
        "planned": ["genetic_algorithm"],
    }
