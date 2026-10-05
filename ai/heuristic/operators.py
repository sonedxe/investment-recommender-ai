"""Genetic operators for the chromosome ``[w1..w5 | c]``."""

from __future__ import annotations

import numpy as np

from ai.heuristic.chromosome import GENES, N_CATEGORIES, repair


def tournament_selection(
    fitness: np.ndarray, n_select: int, tournament_size: int, rng: np.random.Generator
) -> np.ndarray:
    """Indices of ``n_select`` winners of random tournaments (sampling with replacement).

    Tournament instead of roulette: the fitness subtracts risk and penalty terms
    and is often negative, so fitness-proportional probabilities are undefined.
    Tournaments only compare fitness values, so their sign and scale do not matter.
    """
    if tournament_size < 1:
        raise ValueError("tournament_size must be positive")
    contenders = rng.integers(0, len(fitness), size=(n_select, tournament_size))
    winners = np.argmax(fitness[contenders], axis=1)
    return contenders[np.arange(n_select), winners]


def arithmetic_crossover(
    parents_a: np.ndarray,
    parents_b: np.ndarray,
    rate: float,
    max_weight: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Blend each parent pair with ``alpha ~ U(0, 1)`` over all six genes, then repair.

    Arithmetic (convex) crossover keeps children on the simplex: a convex
    combination of two portfolios still sums to 1 and respects the cap. A
    one-point crossover would splice weights from different parents and break
    ``sum(w) = 1``. Pairs not selected (probability ``1 - rate``) are copied.
    """
    n = len(parents_a)
    alpha = rng.uniform(0.0, 1.0, size=(n, 1))
    alpha = np.where(rng.random((n, 1)) < rate, alpha, 1.0)
    child_a = alpha * parents_a + (1.0 - alpha) * parents_b
    child_b = (1.0 - alpha) * parents_a + alpha * parents_b
    return repair(child_a, max_weight), repair(child_b, max_weight)


def gaussian_mutation(
    population: np.ndarray,
    rate: float,
    sigma: float,
    max_weight: float,
    rng: np.random.Generator,
    c_sigma: float | None = None,
) -> np.ndarray:
    """Add ``N(0, sigma)`` noise to each weight gene and ``N(0, c_sigma)`` to ``c``
    with per-gene probability ``rate``, then repair.

    The gene ``c`` lives on [0, 1] while a single weight is at most ``max_weight``,
    so it gets a wider step (``c_sigma``, default ``2*sigma``) to explore the
    absorption set and leave flat zero-membership regions.
    """
    scales = np.full(GENES, sigma)
    scales[N_CATEGORIES] = 2.0 * sigma if c_sigma is None else c_sigma
    mask = rng.random(population.shape) < rate
    noise = rng.normal(0.0, 1.0, size=population.shape) * scales
    return repair(population + mask * noise, max_weight)


def elite_indices(fitness: np.ndarray, count: int) -> np.ndarray:
    """Indices of the ``count`` best individuals, best first (stable for ties)."""
    if count <= 0:
        return np.empty(0, dtype=int)
    return np.argsort(-fitness, kind="stable")[:count]
