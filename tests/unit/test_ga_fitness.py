"""Extended fitness: reference value, breakdown and fuzzy terms."""

import numpy as np
import pytest

from ai.heuristic.fitness import FitnessInputs, evaluate, evaluate_population

UNIVERSE = np.linspace(0.0, 1.0, 11)


def _identical_assets(**overrides) -> FitnessInputs:
    # Five perfectly correlated assets with E = 0.06 and sigma = 0.10: every
    # portfolio has E(P) = 0.06 and sigma(P) = 0.10 (single-asset equivalent).
    values = dict(
        mu=np.full(5, 0.06),
        context_adj=np.zeros(5),
        cov=np.full((5, 5), 0.01),
        lambda_eff=2.0,
        fuzzy_enabled=False,
    )
    values.update(overrides)
    return FitnessInputs(**values)


def test_reference_base_fitness() -> None:
    result = evaluate([0.2] * 5 + [0.5], _identical_assets())
    assert result.total == pytest.approx(-0.14)
    assert result.expected_return == pytest.approx(0.06)
    assert result.sigma == pytest.approx(0.10)
    assert result.sigma_max == np.inf
    assert result.membership_at_c is None
    assert result.penalty_term == 0.0 and result.fuzzy_reward == 0.0


def test_breakdown_terms_sum_to_total() -> None:
    inputs = _identical_assets(
        context_adj=np.array([0.01, 0.0, -0.005, 0.002, 0.0]),
        universe=UNIVERSE,
        mu_ca=UNIVERSE,
        sigma_floor=0.03,
        sigma_amplitude=0.04,
        phi=50.0,
        kappa=0.03,
        fuzzy_enabled=True,
    )
    r = evaluate([0.4, 0.3, 0.1, 0.1, 0.1, 0.25], inputs)
    parts = r.return_term + r.context_term + r.risk_term + r.penalty_term + r.fuzzy_reward
    assert r.total == pytest.approx(parts)
    assert r.context_term == pytest.approx(0.0037)  # 0.4*0.01 - 0.1*0.005 + 0.1*0.002
    assert r.sigma_max == pytest.approx(0.04)
    assert r.penalty_term == pytest.approx(-50.0 * (0.10 - 0.04) ** 2)


def test_penalty_is_zero_within_sigma_max() -> None:
    inputs = _identical_assets(
        universe=UNIVERSE, mu_ca=np.ones(11), sigma_floor=0.05, sigma_amplitude=0.10, phi=50.0, fuzzy_enabled=True
    )
    assert evaluate([0.2] * 5 + [0.6], inputs).penalty_term == 0.0  # sigma_max = 0.11
    assert evaluate([0.2] * 5 + [0.4], inputs).penalty_term < 0.0  # sigma_max = 0.09


def test_kappa_term_uses_interpolated_membership() -> None:
    mu_ca = np.array([0.0, 1.0, 0.0])
    inputs = _identical_assets(
        universe=np.array([0.0, 0.5, 1.0]), mu_ca=mu_ca, sigma_amplitude=1.0, kappa=0.03, fuzzy_enabled=True
    )
    r = evaluate([0.2] * 5 + [0.25], inputs)
    assert r.membership_at_c == pytest.approx(0.5)
    assert r.fuzzy_reward == pytest.approx(0.015)


def test_vectorized_matches_single_evaluation() -> None:
    rng = np.random.default_rng(1)
    pop = np.hstack([rng.dirichlet(np.ones(5), size=20), rng.random((20, 1))])
    inputs = _identical_assets(universe=UNIVERSE, mu_ca=UNIVERSE, phi=50.0, kappa=0.03, fuzzy_enabled=True)
    totals = evaluate_population(pop, inputs)
    assert totals == pytest.approx([evaluate(ind, inputs).total for ind in pop])


def test_fuzzy_requires_membership_grid() -> None:
    with pytest.raises(ValueError):
        _identical_assets(fuzzy_enabled=True)
