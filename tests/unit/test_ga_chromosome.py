"""Chromosome repair and initialization invariants (D2: cap 0.40, floor 0.05)."""

import numpy as np
import pytest

from ai.heuristic.chromosome import GENES, check_bounds, random_population, repair, repair_weights

CAP = 0.40
FLOOR = 0.05
TOL = 1e-9


def _assert_feasible(individuals: np.ndarray, cap: float = CAP, floor: float = 0.0) -> None:
    w, c = individuals[:, :5], individuals[:, 5]
    assert np.all(w >= floor - TOL)
    assert np.allclose(w.sum(axis=1), 1.0, atol=TOL)
    assert np.all(w <= cap + TOL)
    assert np.all((c >= 0) & (c <= 1))


def _random_vectors(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = np.vstack(
        [
            rng.normal(0.0, 1.0, size=(4000, GENES)),
            rng.uniform(-0.5, 2.0, size=(4000, GENES)),
            rng.exponential(1.0, size=(2000, GENES)) * (rng.random((2000, GENES)) < 0.3),
        ]
    )
    assert len(raw) == 10_000
    return raw


def _repair_cap_only_reference(w: np.ndarray, cap: float) -> np.ndarray:
    """Pre-W16 cap-only repair, kept verbatim as the min_weight=0 regression oracle."""
    weights = np.atleast_2d(np.clip(np.array(w, dtype=float), 0.0, None))
    totals = weights.sum(axis=1, keepdims=True)
    weights = np.where(totals > 0, weights / np.where(totals > 0, totals, 1.0), 1.0 / 5)
    for _ in range(5):
        over = weights > cap
        if not over.any():
            break
        excess = np.where(over, weights - cap, 0.0).sum(axis=1, keepdims=True)
        weights = np.where(over, cap, weights)
        under = weights < cap
        base = np.where(under, weights, 0.0)
        base_sum = base.sum(axis=1, keepdims=True)
        count = under.sum(axis=1, keepdims=True)
        share = np.where(base_sum > 0, base / np.where(base_sum > 0, base_sum, 1.0), under / np.maximum(count, 1))
        weights = weights + excess * share
    return np.minimum(weights, cap)


def test_repair_invariants_on_random_vectors() -> None:
    _assert_feasible(repair(_random_vectors(), CAP))


def test_repair_invariants_with_floor_on_random_vectors() -> None:
    _assert_feasible(repair(_random_vectors(1), CAP, FLOOR), floor=FLOOR)


def test_zero_floor_reproduces_cap_only_repair_exactly() -> None:
    raw = _random_vectors(2)[:, :5]
    expected = _repair_cap_only_reference(raw, CAP)
    assert np.array_equal(repair_weights(raw, CAP), expected)
    assert np.array_equal(repair_weights(raw, CAP, 0.0), expected)


def test_floor_raises_zeros_and_takes_deficit_from_slack() -> None:
    w = repair_weights([0.4, 0.4, 0.0, 0.2, 0.0], CAP, FLOOR)
    # Deficit 0.10 is taken from the slack above the floor (0.35, 0.35, 0.15), proportionally.
    assert w == pytest.approx([0.4 - 0.1 * 0.35 / 0.85, 0.4 - 0.1 * 0.35 / 0.85, 0.05, 0.2 - 0.1 * 0.15 / 0.85, 0.05])
    assert repair_weights([1, 0, 0, 0, 0], CAP, FLOOR) == pytest.approx([0.4, 0.15, 0.15, 0.15, 0.15])


def test_repair_with_floor_keeps_feasible_weights_unchanged() -> None:
    w = np.array([0.4, 0.3, 0.05, 0.15, 0.1])
    assert repair_weights(w, CAP, FLOOR) == pytest.approx(w, abs=1e-15)


def test_floor_equal_to_uniform_forces_uniform() -> None:
    assert repair_weights([0.9, 0.1, 0, 0, 0], CAP, 0.2) == pytest.approx([0.2] * 5)


@pytest.mark.parametrize(("floor", "cap"), [(-0.01, 0.4), (0.21, 0.4), (0.3, 0.25), (0.0, 0.19), (0.05, 1.01)])
def test_infeasible_bounds_raise(floor: float, cap: float) -> None:
    with pytest.raises(ValueError):
        check_bounds(floor, cap)
    with pytest.raises(ValueError):
        repair_weights([0.2] * 5, cap, floor)


def test_repair_single_individual_and_degenerate_inputs() -> None:
    assert repair_weights([1, 0, 0, 0, 0], CAP) == pytest.approx([0.4, 0.15, 0.15, 0.15, 0.15])
    assert repair_weights([-1, -2, 0, 0, 0], CAP) == pytest.approx([0.2] * 5)
    assert repair_weights([0.9, 0.1, 0, 0, 0], CAP) == pytest.approx([0.4, 0.4] + [0.2 / 3] * 3)
    individual = repair([0.2, 0.2, 0.2, 0.2, 0.2, 1.7], CAP)
    assert individual.shape == (GENES,)
    assert individual[5] == 1.0


def test_repair_keeps_feasible_weights_unchanged() -> None:
    w = np.array([0.4, 0.3, 0.1, 0.1, 0.1])
    assert repair_weights(w, CAP) == pytest.approx(w)


def test_infeasible_cap_raises() -> None:
    with pytest.raises(ValueError):
        repair_weights([0.2] * 5, 0.19)


def test_random_population_is_feasible_and_seeded() -> None:
    a = random_population(500, CAP, np.random.default_rng(3))
    b = random_population(500, CAP, np.random.default_rng(3))
    _assert_feasible(a)
    assert np.array_equal(a, b)
    floored = random_population(500, CAP, np.random.default_rng(3), min_weight=FLOOR)
    _assert_feasible(floored, floor=FLOOR)
