"""Extended chromosome ``[w1..w5 | c]`` and its feasibility repair.

An individual is a float vector of length 6: five portfolio weights (one per
category, canonical order) followed by the fuzzy absorption gene ``c``.
Feasibility: ``w_i >= 0``, ``sum(w) = 1``, ``w_i <= max_weight`` (D2) and
``c in [0, 1]``. Every function accepts a single individual ``(6,)`` or a
population ``(n, 6)``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from ai.shared.types import N_CATEGORIES

GENES = N_CATEGORIES + 1
C_INDEX = N_CATEGORIES


def check_cap(max_weight: float) -> None:
    """Raise unless ``max_weight`` admits a portfolio (``5 * max_weight >= 1``)."""
    if not 0.0 < max_weight <= 1.0 or N_CATEGORIES * max_weight < 1.0 - 1e-12:
        raise ValueError(f"max_weight={max_weight} is infeasible for {N_CATEGORIES} categories")


def repair_weights(w: ArrayLike, max_weight: float) -> np.ndarray:
    """Project weights onto the capped simplex.

    Negatives are clipped to 0 and the vector normalized to sum 1 (all-zero rows
    become uniform). The cap is enforced by water-filling: the excess above
    ``max_weight`` is redistributed among the categories still below the cap,
    proportionally to their weights (equally when they are all zero), until no
    category exceeds it. Each pass pins at least one more category at the cap,
    so at most ``N_CATEGORIES`` passes are needed.
    """
    check_cap(max_weight)
    weights = np.clip(np.array(w, dtype=float), 0.0, None)
    single = weights.ndim == 1
    weights = np.atleast_2d(weights)
    if weights.shape[-1] != N_CATEGORIES:
        raise ValueError(f"weights must have {N_CATEGORIES} columns, got {weights.shape[-1]}")

    totals = weights.sum(axis=1, keepdims=True)
    weights = np.where(totals > 0, weights / np.where(totals > 0, totals, 1.0), 1.0 / N_CATEGORIES)

    for _ in range(N_CATEGORIES):
        over = weights > max_weight
        if not over.any():
            break
        excess = np.where(over, weights - max_weight, 0.0).sum(axis=1, keepdims=True)
        weights = np.where(over, max_weight, weights)
        under = weights < max_weight
        base = np.where(under, weights, 0.0)
        base_sum = base.sum(axis=1, keepdims=True)
        count = under.sum(axis=1, keepdims=True)
        share = np.where(
            base_sum > 0,
            base / np.where(base_sum > 0, base_sum, 1.0),
            under / np.maximum(count, 1),
        )
        weights = weights + excess * share

    weights = np.minimum(weights, max_weight)
    return weights[0] if single else weights


def repair(individuals: ArrayLike, max_weight: float) -> np.ndarray:
    """Repair weights (see ``repair_weights``) and clip the gene ``c`` to [0, 1]."""
    array = np.array(individuals, dtype=float)
    if array.shape[-1] != GENES:
        raise ValueError(f"individuals must have {GENES} genes, got {array.shape[-1]}")
    repaired = np.empty_like(array)
    repaired[..., :N_CATEGORIES] = repair_weights(array[..., :N_CATEGORIES], max_weight)
    repaired[..., C_INDEX] = np.clip(array[..., C_INDEX], 0.0, 1.0)
    return repaired


def random_population(size: int, max_weight: float, rng: np.random.Generator) -> np.ndarray:
    """Dirichlet(1) weights (uniform on the simplex) repaired to the cap, plus uniform ``c``."""
    if size < 1:
        raise ValueError("size must be positive")
    population = np.empty((size, GENES))
    population[:, :N_CATEGORIES] = rng.dirichlet(np.ones(N_CATEGORIES), size=size)
    population[:, C_INDEX] = rng.uniform(0.0, 1.0, size=size)
    return repair(population, max_weight)
