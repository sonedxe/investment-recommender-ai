"""Line-by-line compliance with report v1.1 numeric examples.

Pins the exact numbers a reviewer can recompute from the PDF:
- 4.5.1 horizon H = 2.5 -> m_H ~= 1.30, lambda_ef = 2.6 for lambda_base = 2.
- 4.5.2 absorption r = 0.25, E = 3 -> CA ~= 0.54, sigma_max ~= 10.0 %.
- 5.1 base fitness E = 6 %, sigma = 10 %: -14 (lambda = 2), 4 (lambda = 0.2).
- 4.6.4 adverse politics table (ci, mu', sigma').
- 5.2 strict fitness reduces from the extended engine with kappa = 0.
"""

import numpy as np
import pytest

from ai.context import adjust
from ai.heuristic.fitness import FitnessInputs, evaluate
from ai.heuristic.report_fitness import report_fitness
from ai.shared import ContextFactors, MarketEstimates
from ai.shared.parameters import load_parameters
from ai.uncertainty.fuzzy.horizon import evaluate_horizon
from ai.uncertainty.fuzzy.sugeno_absorption import evaluate_absorption_sugeno


@pytest.fixture(scope="module")
def params():
    return load_parameters()


def test_horizon_example_h_2_5(params) -> None:
    horizon = evaluate_horizon(params.fuzzy.horizon, lambda_base=2.0, years=2.5)
    assert dict(horizon.memberships) == pytest.approx(
        {"corto": 0.25, "mediano": 1 / 6, "largo": 0.0}, abs=1e-9
    )
    assert horizon.m_h == pytest.approx(1.30, abs=1e-2)
    assert horizon.lambda_eff == pytest.approx(2.6, abs=1e-2)


def test_absorption_sugeno_example(params) -> None:
    result = evaluate_absorption_sugeno(
        params.fuzzy.absorption, amount=5000, total_savings=20000, emergency_months=3
    )
    assert result.r == pytest.approx(0.25)
    assert result.e == pytest.approx(3.0)
    assert (result.ratio_memberships["bajo"], result.ratio_memberships["medio"]) == pytest.approx(
        (0.75, 1 / 6), abs=1e-4
    )
    assert tuple(result.activations[f"RA{i}"] for i in range(1, 7)) == pytest.approx(
        (1 / 3, 0.25, 1 / 6, 1 / 6, 0.0, 0.0), abs=1e-4
    )
    assert result.ca == pytest.approx(0.54, abs=1e-2)
    assert result.sigma_max == pytest.approx(0.10, abs=1e-3)


def test_absorption_declined_assumes_medium(params) -> None:
    result = evaluate_absorption_sugeno(
        params.fuzzy.absorption, amount=5000, total_savings=None, emergency_months=None
    )
    assert result.assumed is True
    assert result.ca == pytest.approx(0.50)
    assert "media" in result.assumptions[0].lower()


def test_base_fitness_illustrative_example() -> None:
    # Report 5.1 works in percent points (6 - 2*10 = -14); the code uses
    # decimals, so the same case is 0.06 - 2*0.10 = -0.14.
    cov = np.full((5, 5), 0.01)
    conservative = report_fitness([0.2] * 5, np.full(5, 0.06), cov, 2.0, float("inf"))
    aggressive = report_fitness([0.2] * 5, np.full(5, 0.06), cov, 0.2, float("inf"))
    assert conservative.total == pytest.approx(-0.14)
    assert aggressive.total == pytest.approx(0.04)


def test_context_table_4_6_4(params) -> None:
    cats = params.categories
    estimates = MarketEstimates(
        mu=cats.mu, sigma=cats.sigma, correlation=cats.default_correlation, trend=np.zeros(5)
    )
    result = adjust(estimates, ContextFactors(political=-1.0), np.zeros(5), params.context)
    np.testing.assert_allclose(result.c, [-0.025, -0.012, -0.005, -0.008, -0.003], atol=1e-12)
    np.testing.assert_allclose(result.mu_adj, [0.097, 0.049, 0.019, 0.057, 0.042], atol=1e-12)
    np.testing.assert_allclose(
        result.sigma_adj, [0.285, 0.1125, 0.0275, 0.042, 0.005], atol=1e-12
    )


def test_extended_engine_reduces_to_strict_with_kappa_zero(params) -> None:
    absorption = evaluate_absorption_sugeno(
        params.fuzzy.absorption, amount=5000, total_savings=20000, emergency_months=3
    )
    horizon = evaluate_horizon(params.fuzzy.horizon, lambda_base=2.0, years=2.5)
    cats = params.categories
    estimates = MarketEstimates(
        mu=cats.mu, sigma=cats.sigma, correlation=cats.default_correlation, trend=np.zeros(5)
    )
    context = adjust(estimates, None, np.zeros(5), params.context)
    w = np.array([0.25, 0.15, 0.20, 0.25, 0.15])
    strict = report_fitness(
        w,
        context.mu_adj,
        context.cov_adj,
        horizon.lambda_eff,
        absorption.sigma_max,
        mu_base=estimates.mu,
        c=context.c,
        phi=params.optimization.phi,
    )
    universe = np.linspace(0.0, 1.0, 11)
    extended = evaluate(
        list(w) + [absorption.ca],
        FitnessInputs(
            mu=estimates.mu,
            context_adj=context.c,
            cov=context.cov_adj,
            lambda_eff=horizon.lambda_eff,
            universe=universe,
            mu_ca=np.interp(universe, [0.0, 0.5, 1.0], [0.0, 1.0, 0.0]),
            sigma_floor=params.fuzzy.absorption.sigma_floor,
            sigma_amplitude=params.fuzzy.absorption.sigma_amplitude,
            phi=params.optimization.phi,
            kappa=0.0,
            fuzzy_enabled=True,
        ),
    )
    assert extended.total == pytest.approx(strict.total, abs=1e-9)
    assert extended.sigma_max == pytest.approx(strict.sigma_max, abs=1e-12)


def test_live_recommendation_carries_strict_reference() -> None:
    """The production path computes the strict reference live per request."""
    from ai.shared.types import RiskProfile, UserProfile
    from backend.app.services.recommendation import Switches, recommend

    profile = UserProfile(
        amount=5000,
        risk_profile=RiskProfile.CONSERVADOR,
        horizon_years=2.5,
        total_savings=20000,
        emergency_months=3,
    )
    result = recommend(profile, None, Switches(), seed=42)
    absorption = result["technical"]["absorption"]
    assert absorption["sugeno_ca"] == pytest.approx(0.54, abs=1e-2)
    assert absorption["sugeno_sigma_max"] == pytest.approx(0.10, abs=1e-3)
    assert result["technical"]["score"]["strict_total"] is not None


def test_live_strict_reference_mirrors_switches() -> None:
    from ai.shared.types import RiskProfile, UserProfile
    from backend.app.services.recommendation import Switches, recommend

    profile = UserProfile(
        amount=5000,
        risk_profile=RiskProfile.CONSERVADOR,
        horizon_years=2.5,
        total_savings=20000,
        emergency_months=3,
    )
    result = recommend(profile, None, Switches(fuzzy=False, context=False), seed=42)
    assert result["technical"]["score"]["strict_total"] is not None
