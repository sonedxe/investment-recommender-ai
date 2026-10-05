"""Extended fitness of the chromosome ``[w | c]`` (docs/analisis/04).

    F = sum(w*mu) + sum(w*c_ctx) - lambda_eff*sigma(P)
        - phi*max(0, sigma(P) - sigma_max(c))^2 + kappa*mu_CA(c)

    sigma(P)    = sqrt(w' Sigma w)
    sigma_max(c) = sigma_floor + sigma_amplitude * c

With ``fuzzy_enabled=False`` there is no volatility penalty (sigma_max = inf)
and no kappa reward, so the gene ``c`` is inert; ``lambda_eff`` is whatever the
caller passes (unmodulated by the horizon in that case). The module knows
nothing about the fuzzy or context implementations: it receives arrays.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from ai.heuristic.chromosome import C_INDEX, GENES
from ai.shared.types import N_CATEGORIES


def _vector(value: ArrayLike, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.array(value, dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    array.setflags(write=False)
    return array


@dataclass(frozen=True)
class FitnessInputs:
    """Everything the fitness needs, already computed by the upstream modules.

    ``universe``/``mu_ca`` is the aggregated absorption set on a grid; it is
    linearly interpolated at ``c``. It may be omitted when fuzzy is disabled.
    """

    mu: np.ndarray
    context_adj: np.ndarray
    cov: np.ndarray
    lambda_eff: float
    universe: np.ndarray | None = None
    mu_ca: np.ndarray | None = None
    sigma_floor: float = 0.0
    sigma_amplitude: float = 0.0
    phi: float = 0.0
    kappa: float = 0.0
    fuzzy_enabled: bool = True

    def __post_init__(self) -> None:
        n = (N_CATEGORIES,)
        object.__setattr__(self, "mu", _vector(self.mu, n, "mu"))
        object.__setattr__(self, "context_adj", _vector(self.context_adj, n, "context_adj"))
        cov = _vector(self.cov, (N_CATEGORIES, N_CATEGORIES), "cov")
        if not np.allclose(cov, cov.T, atol=1e-12):
            raise ValueError("cov must be symmetric")
        object.__setattr__(self, "cov", cov)
        if self.lambda_eff < 0 or self.phi < 0 or self.kappa < 0:
            raise ValueError("lambda_eff, phi and kappa must be non-negative")
        if self.fuzzy_enabled:
            if self.universe is None or self.mu_ca is None:
                raise ValueError("fuzzy_enabled requires universe and mu_ca")
            universe = np.array(self.universe, dtype=float)
            mu_ca = np.array(self.mu_ca, dtype=float)
            if universe.ndim != 1 or universe.shape != mu_ca.shape or universe.size < 2:
                raise ValueError("universe and mu_ca must be 1-D arrays of equal length >= 2")
            if np.any(np.diff(universe) <= 0):
                raise ValueError("universe must be strictly increasing")
            object.__setattr__(self, "universe", _vector(universe, universe.shape, "universe"))
            object.__setattr__(self, "mu_ca", _vector(mu_ca, mu_ca.shape, "mu_ca"))


@dataclass(frozen=True)
class FitnessBreakdown:
    """Signed contributions: ``total = return + context + risk + penalty + fuzzy_reward``.

    ``risk_term`` and ``penalty_term`` are therefore <= 0. ``sigma_max`` is
    ``inf`` and ``membership_at_c`` is ``None`` when fuzzy is disabled.
    """

    return_term: float
    context_term: float
    risk_term: float
    penalty_term: float
    fuzzy_reward: float
    total: float
    expected_return: float
    sigma: float
    sigma_max: float
    membership_at_c: float | None


@dataclass(frozen=True)
class _Terms:
    return_term: np.ndarray
    context_term: np.ndarray
    risk_term: np.ndarray
    penalty_term: np.ndarray
    fuzzy_reward: np.ndarray
    sigma: np.ndarray
    sigma_max: np.ndarray
    membership: np.ndarray | None

    @property
    def total(self) -> np.ndarray:
        return self.return_term + self.context_term + self.risk_term + self.penalty_term + self.fuzzy_reward


def _terms(population: np.ndarray, inputs: FitnessInputs) -> _Terms:
    w = population[:, :N_CATEGORIES]
    c = population[:, C_INDEX]
    variance = np.einsum("ij,jk,ik->i", w, inputs.cov, w)
    sigma = np.sqrt(np.clip(variance, 0.0, None))
    zeros = np.zeros(len(population))
    if inputs.fuzzy_enabled:
        sigma_max = inputs.sigma_floor + inputs.sigma_amplitude * c
        penalty = -inputs.phi * np.maximum(0.0, sigma - sigma_max) ** 2
        membership = np.interp(c, inputs.universe, inputs.mu_ca)
        reward = inputs.kappa * membership
    else:
        sigma_max, penalty, membership, reward = np.full(len(population), np.inf), zeros, None, zeros
    return _Terms(
        return_term=w @ inputs.mu,
        context_term=w @ inputs.context_adj,
        risk_term=-inputs.lambda_eff * sigma,
        penalty_term=penalty,
        fuzzy_reward=reward,
        sigma=sigma,
        sigma_max=sigma_max,
        membership=membership,
    )


def _as_population(individuals: ArrayLike) -> np.ndarray:
    population = np.atleast_2d(np.array(individuals, dtype=float))
    if population.ndim != 2 or population.shape[1] != GENES:
        raise ValueError(f"individuals must have shape (n, {GENES})")
    return population


def evaluate_population(population: ArrayLike, inputs: FitnessInputs) -> np.ndarray:
    """Vectorized fitness totals for an ``(n, 6)`` population."""
    return _terms(_as_population(population), inputs).total


def evaluate(individual: ArrayLike, inputs: FitnessInputs) -> FitnessBreakdown:
    """Fitness of one individual with its full breakdown."""
    population = _as_population(individual)
    if len(population) != 1:
        raise ValueError("evaluate expects a single individual")
    t = _terms(population, inputs)
    return FitnessBreakdown(
        return_term=float(t.return_term[0]),
        context_term=float(t.context_term[0]),
        risk_term=float(t.risk_term[0]),
        penalty_term=float(t.penalty_term[0]),
        fuzzy_reward=float(t.fuzzy_reward[0]),
        total=float(t.total[0]),
        expected_return=float(t.return_term[0] + t.context_term[0]),
        sigma=float(t.sigma[0]),
        sigma_max=float(t.sigma_max[0]),
        membership_at_c=None if t.membership is None else float(t.membership[0]),
    )
