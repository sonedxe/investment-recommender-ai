"""Strict report-v1.1 fitness (section 5.2), no extensions.

    Fitness'(P) = sum_i w_i * mu'_i - lambda_ef * sigma'(P)
                 - phi * max(0, sigma'(P) - sigma_max)^2

    ``sigma'(P) = sqrt(w' Sigma' w)`` with the context-adjusted covariance.
    Constraints are the report's hard ones: ``sum(w) = 1``, ``w_i >= 0``.
    All magnitudes are decimals (12.2 % = 0.122) because the quadratic term
    depends on the units.

    The shipped product extends this with a ``kappa * mu_CA(c)`` reward and a
    ``[w | c]`` chromosome (see ``ai/heuristic/fitness.py`` and
    ``docs/analisis/04-propuesta-difusa-cromosoma.md``). With ``kappa = 0``
    and the gene ``c`` fixed to the Sugeno ``CA``
    (``ai/uncertainty/fuzzy/sugeno_absorption.py``), the extended fitness
    reduces exactly to this strict form, which is what the tests below pin.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike


@dataclass(frozen=True)
class ReportFitnessBreakdown:
    return_term: float
    context_term: float
    risk_term: float
    penalty_term: float
    total: float
    expected_return: float
    sigma: float
    sigma_max: float


def _weights(w: ArrayLike) -> np.ndarray:
    weights = np.array(w, dtype=float)
    if weights.shape != (5,):
        raise ValueError(f"weights must have shape (5,), got {weights.shape}")
    if not np.all(np.isfinite(weights)):
        raise ValueError("weights must be finite")
    if np.any(weights < 0):
        raise ValueError("weights must be non-negative (report 5.1)")
    total = weights.sum()
    if not np.isclose(total, 1.0, atol=1e-9):
        raise ValueError(f"weights must sum to 1, got {total}")
    return weights


def report_fitness(
    w: ArrayLike,
    mu_adj: ArrayLike,
    cov_adj: ArrayLike,
    lambda_eff: float,
    sigma_max: float,
    mu_base: ArrayLike | None = None,
    c: ArrayLike | None = None,
    phi: float = 50.0,
) -> ReportFitnessBreakdown:
    """Strict section-5.2 fitness with its historical/context split."""
    weights = _weights(w)
    mu_adj_arr = np.array(mu_adj, dtype=float)
    cov_arr = np.array(cov_adj, dtype=float)
    if mu_adj_arr.shape != (5,) or cov_arr.shape != (5, 5):
        raise ValueError("mu_adj must have shape (5,) and cov_adj (5, 5)")
    if lambda_eff < 0 or phi < 0:
        raise ValueError("lambda_eff and phi must be non-negative")
    variance = float(weights @ cov_arr @ weights)
    sigma = float(np.sqrt(max(0.0, variance)))
    penalty = -phi * max(0.0, sigma - sigma_max) ** 2
    return_term = float(weights @ mu_adj_arr)
    if mu_base is not None and c is not None:
        mu_base_arr, c_arr = np.array(mu_base, dtype=float), np.array(c, dtype=float)
        hist = float(weights @ mu_base_arr)
        return ReportFitnessBreakdown(
            return_term=hist,
            context_term=float(weights @ c_arr),
            risk_term=-lambda_eff * sigma,
            penalty_term=penalty,
            total=hist + float(weights @ c_arr) - lambda_eff * sigma + penalty,
            expected_return=return_term,
            sigma=sigma,
            sigma_max=sigma_max,
        )
    return ReportFitnessBreakdown(
        return_term=return_term,
        context_term=0.0,
        risk_term=-lambda_eff * sigma,
        penalty_term=penalty,
        total=return_term - lambda_eff * sigma + penalty,
        expected_return=return_term,
        sigma=sigma,
        sigma_max=sigma_max,
    )
