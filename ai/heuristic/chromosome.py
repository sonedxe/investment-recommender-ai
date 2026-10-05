"""Extended chromosome ``[w1..w5 | c]`` and its feasibility repair.

An individual is a float vector of length 6: five portfolio weights (one per
category, canonical order) followed by the fuzzy absorption gene ``c``.
Feasibility: ``min_weight <= w_i <= max_weight`` (D2: floor 0.05, cap 0.40),
``sum(w) = 1`` and ``c in [0, 1]``. ``min_weight = 0`` is the original cap-only
model. Every function accepts a single individual ``(6,)`` or a
population ``(n, 6)``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from ai.shared.types import N_CATEGORIES

GENES = N_CATEGORIES + 1
C_INDEX = N_CATEGORIES


def check_bounds(min_weight: float, max_weight: float) -> None:
    """Raise unless ``[min_weight, max_weight]`` admits a portfolio.

    Feasible iff ``0 <= min_weight``, ``max_weight <= 1`` and
    ``N * min_weight <= 1 <= N * max_weight`` (which implies ``min_weight <= max_weight``).
    """
    if (
        not 0.0 < max_weight <= 1.0
        or min_weight < 0.0
        or N_CATEGORIES * max_weight < 1.0 - 1e-12
        or N_CATEGORIES * min_weight > 1.0 + 1e-12
        or min_weight > max_weight
    ):
        raise ValueError(
            f"bounds [{min_weight}, {max_weight}] are infeasible for {N_CATEGORIES} categories"
        )


def check_cap(max_weight: float) -> None:
    """Raise unless ``max_weight`` admits a portfolio (``5 * max_weight >= 1``)."""
    check_bounds(0.0, max_weight)


def repair_weights(w: ArrayLike, max_weight: float, min_weight: float = 0.0) -> np.ndarray:
    """Project weights onto the bounded simplex ``min_weight <= w_i <= max_weight``.

    Negatives are clipped to 0 and the vector normalized to sum 1 (all-zero rows
    become uniform). With ``min_weight = 0`` only the cap applies (``_repair_cap``,
    unchanged since D2). With a floor the repair water-fills in both directions:

    1. every category below the floor is raised to it, and the deficit is taken
       from the others proportionally to their slack above the floor;
    2. the cap is then water-filled in that floor-shifted space.

    Both steps run on the slack ``v = w - min_weight`` (rescaled to sum 1), where
    the bounds become ``v >= 0`` and ``v <= cap'`` with
    ``cap' = (max_weight - min_weight) / (1 - N * min_weight)``. Mapping back,
    ``w = min_weight + (1 - N * min_weight) * v`` satisfies both bounds and sums to
    1. Already-feasible weights are returned unchanged (idempotent), so elites
    and copied parents are not pulled toward the uniform portfolio.
    """
    check_bounds(min_weight, max_weight)
    if min_weight == 0.0:
        return _repair_cap(w, max_weight)

    free_mass = 1.0 - N_CATEGORIES * min_weight
    weights = _normalize(w)
    if free_mass <= 1e-12:  # N * min_weight == 1: the uniform portfolio is the only feasible one
        result = np.full_like(weights, 1.0 / N_CATEGORIES)
    else:
        slack = _repair_cap(weights - min_weight, (max_weight - min_weight) / free_mass)
        result = np.clip(min_weight + free_mass * slack, min_weight, max_weight)
    return result[0] if np.ndim(w) == 1 else result


def _normalize(w: ArrayLike) -> np.ndarray:
    """Clip negatives and scale each row to sum 1 (all-zero rows become uniform); always 2-D."""
    weights = np.atleast_2d(np.clip(np.array(w, dtype=float), 0.0, None))
    if weights.shape[-1] != N_CATEGORIES:
        raise ValueError(f"weights must have {N_CATEGORIES} columns, got {weights.shape[-1]}")
    totals = weights.sum(axis=1, keepdims=True)
    return np.where(totals > 0, weights / np.where(totals > 0, totals, 1.0), 1.0 / N_CATEGORIES)


def _repair_cap(w: ArrayLike, max_weight: float) -> np.ndarray:
    """Project weights onto the capped simplex (the D2 cap-only repair).

    After ``_normalize``, the cap is enforced by water-filling: the excess above
    ``max_weight`` is redistributed among the categories still below the cap,
    proportionally to their weights (equally when they are all zero), until no
    category exceeds it. Each pass pins at least one more category at the cap,
    so at most ``N_CATEGORIES`` passes are needed.
    """
    single = np.ndim(w) == 1
    weights = _normalize(w)

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


def repair(individuals: ArrayLike, max_weight: float, min_weight: float = 0.0) -> np.ndarray:
    """Repair weights (see ``repair_weights``) and clip the gene ``c`` to [0, 1]."""
    array = np.array(individuals, dtype=float)
    if array.shape[-1] != GENES:
        raise ValueError(f"individuals must have {GENES} genes, got {array.shape[-1]}")
    repaired = np.empty_like(array)
    repaired[..., :N_CATEGORIES] = repair_weights(array[..., :N_CATEGORIES], max_weight, min_weight)
    repaired[..., C_INDEX] = np.clip(array[..., C_INDEX], 0.0, 1.0)
    return repaired


def random_population(
    size: int,
    max_weight: float,
    rng: np.random.Generator,
    c_universe: ArrayLike | None = None,
    c_weights: ArrayLike | None = None,
    min_weight: float = 0.0,
) -> np.ndarray:
    """Dirichlet(1) weights (uniform on the simplex) repaired to the bounds, plus the gene ``c``.

    ``c`` is uniform on [0, 1] unless ``c_universe``/``c_weights`` are given: then it
    is sampled from the grid with probability proportional to the weights (the
    absorption set mu_CA), so the search starts where the membership is positive
    instead of in a flat zero-membership region. A set with no positive weight
    falls back to uniform.
    """
    if size < 1:
        raise ValueError("size must be positive")
    population = np.empty((size, GENES))
    population[:, :N_CATEGORIES] = rng.dirichlet(np.ones(N_CATEGORIES), size=size)
    population[:, C_INDEX] = _initial_c(size, rng, c_universe, c_weights)
    return repair(population, max_weight, min_weight)


def _initial_c(
    size: int, rng: np.random.Generator, universe: ArrayLike | None, weights: ArrayLike | None
) -> np.ndarray:
    if universe is None or weights is None:
        return rng.uniform(0.0, 1.0, size=size)
    grid = np.array(universe, dtype=float)
    mass = np.clip(np.array(weights, dtype=float), 0.0, None)
    if grid.shape != mass.shape or grid.ndim != 1:
        raise ValueError("c_universe and c_weights must be 1-D arrays of equal length")
    total = mass.sum()
    if not np.isfinite(total) or total <= 0:
        return rng.uniform(0.0, 1.0, size=size)
    return rng.choice(grid, size=size, p=mass / total)
