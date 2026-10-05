"""Context adjustment of the market estimates (report v1.1 section 4.6.3).

    mu'_i    = mu_i + c_i
    sigma'_i = sigma_i * (1 + gamma_pol_i*max(0, -s_pol) + gamma_mac_i*max(0, -s_mac))
    Sigma'   = rho * outer(sigma', sigma')      (correlations preserved)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from ai.context.rules import RuleTrace, evaluate_rules, validate_trend
from ai.shared.parameters import ContextParameters
from ai.shared.types import N_CATEGORIES, ContextFactors, MarketEstimates


@dataclass(frozen=True)
class ContextAdjustment:
    c: np.ndarray
    mu_adj: np.ndarray
    sigma_adj: np.ndarray
    cov_adj: np.ndarray
    trace: tuple[RuleTrace, ...]
    enabled: bool


def adjust(
    estimates: MarketEstimates,
    factors: ContextFactors | None,
    trend: ArrayLike | None,
    params: ContextParameters,
    enabled: bool = True,
) -> ContextAdjustment:
    """Apply the context rules; ``trend=None`` uses ``estimates.trend``; ``enabled=False`` is the identity."""
    trend_values = validate_trend(estimates.trend if trend is None else trend)
    if enabled:
        evaluation = evaluate_rules(factors, trend_values, params)
        c, multiplier, trace = evaluation.c, evaluation.sigma_multiplier, evaluation.trace
    else:
        c, multiplier, trace = np.zeros(N_CATEGORIES), np.ones(N_CATEGORIES), ()

    sigma_adj = estimates.sigma * multiplier
    return ContextAdjustment(
        c=c,
        mu_adj=estimates.mu + c,
        sigma_adj=sigma_adj,
        cov_adj=estimates.correlation * np.outer(sigma_adj, sigma_adj),
        trace=trace,
        enabled=enabled,
    )
