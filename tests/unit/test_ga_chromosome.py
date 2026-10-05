"""Chromosome repair and initialization invariants (D2 cap 0.40)."""

import numpy as np
import pytest

from ai.heuristic.chromosome import GENES, random_population, repair, repair_weights

CAP = 0.40
TOL = 1e-9


def _assert_feasible(individuals: np.ndarray, cap: float = CAP) -> None:
    w, c = individuals[:, :5], individuals[:, 5]
    assert np.all(w >= 0)
    assert np.allclose(w.sum(axis=1), 1.0, atol=TOL)
    assert np.all(w <= cap + TOL)
    assert np.all((c >= 0) & (c <= 1))


def test_repair_invariants_on_random_vectors() -> None:
    rng = np.random.default_rng(0)
    raw = np.vstack(
        [
            rng.normal(0.0, 1.0, size=(4000, GENES)),
            rng.uniform(-0.5, 2.0, size=(4000, GENES)),
            rng.exponential(1.0, size=(2000, GENES)) * (rng.random((2000, GENES)) < 0.3),
        ]
    )
    assert len(raw) == 10_000
    _assert_feasible(repair(raw, CAP))


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
