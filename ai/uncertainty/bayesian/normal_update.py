"""Conjugate normal-normal update of an expected return with known data variance.

Only the mean ``mu`` is updated. The volatility ``sigma`` is taken from the data
when there is enough history, otherwise from the Annex A prior; it is treated
as known here, which is what makes the normal prior on ``mu`` conjugate.

    posterior_mean = (mu0/tau0^2 + n*xbar/s^2) / (1/tau0^2 + n/s^2)
    posterior_sd   = (1/tau0^2 + n/s^2) ** -0.5

All arguments must share units (e.g. all monthly).
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class NormalPosterior:
    mean: float
    sd: float


def normal_update(prior_mean: float, prior_sd: float, sample_mean: float, data_sd: float, n: int) -> NormalPosterior:
    """Posterior of ``mu`` after ``n`` observations with mean ``sample_mean`` and known sd ``data_sd``.

    ``n = 0`` or ``data_sd = inf`` leaves the prior unchanged.
    """
    if prior_sd <= 0:
        raise ValueError("prior_sd must be positive")
    if n < 0 or data_sd < 0:
        raise ValueError("n and data_sd must be non-negative")
    if n == 0 or math.isinf(data_sd):
        return NormalPosterior(prior_mean, prior_sd)
    if data_sd == 0:
        return NormalPosterior(sample_mean, 0.0)
    prior_precision = 1.0 / prior_sd**2
    data_precision = n / data_sd**2
    precision = prior_precision + data_precision
    mean = (prior_mean * prior_precision + sample_mean * data_precision) / precision
    return NormalPosterior(mean, precision**-0.5)
