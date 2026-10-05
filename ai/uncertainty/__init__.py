"""Reasoning under uncertainty module.

- Fuzzy logic (``ai.uncertainty.fuzzy``): the investment horizon is evaluated
  with a zero-order Sugeno system (multiplier ``m_H`` for the risk aversion
  used in the fitness) and the loss-absorption capacity with a Mamdani system
  whose aggregated output set feeds the chromosome gene ``c``.
- Bayesian estimation (``ai.uncertainty.bayesian``): conjugate normal-normal
  updates of the market estimates (expected return, volatility, trend).
"""


def ping() -> dict:
    """Check that the module responds (used by the connectivity test)."""
    return {
        "module": "uncertainty",
        "status": "ok",
        "components": ["fuzzy_logic", "bayesian_estimation"],
    }
