"""Context adjustment (report v1.1 sections 4.6.3 and 4.6.4)."""

import numpy as np
import pytest

from ai.context import adjust
from ai.shared import ContextFactors, MarketEstimates
from ai.shared.parameters import load_parameters


@pytest.fixture(scope="module")
def params():
    return load_parameters()


@pytest.fixture(scope="module")
def estimates(params) -> MarketEstimates:
    cats = params.categories
    return MarketEstimates(
        mu=cats.mu, sigma=cats.sigma, correlation=cats.default_correlation, trend=np.zeros(5)
    )


def test_report_table_4_6_4_adverse_politics(params, estimates) -> None:
    result = adjust(estimates, ContextFactors(political=-1.0), np.zeros(5), params.context)
    np.testing.assert_allclose(result.c, [-0.025, -0.012, -0.005, -0.008, -0.003], atol=1e-12)
    np.testing.assert_allclose(result.mu_adj, [0.097, 0.049, 0.019, 0.057, 0.042], atol=1e-12)
    np.testing.assert_allclose(result.sigma_adj, [0.285, 0.1125, 0.0275, 0.042, 0.005], atol=1e-12)


def test_adjusted_covariance_preserves_correlations(params, estimates) -> None:
    result = adjust(estimates, ContextFactors(political=-1.0, macro=-0.5), np.zeros(5), params.context)
    cov = result.cov_adj
    np.testing.assert_allclose(cov, cov.T)
    assert np.linalg.eigvalsh(cov).min() >= -1e-12
    np.testing.assert_allclose(np.sqrt(np.diag(cov)), result.sigma_adj)
    implied = cov / np.outer(result.sigma_adj, result.sigma_adj)
    np.testing.assert_allclose(implied, estimates.correlation, atol=1e-12)


def test_favorable_context_does_not_lower_risk(params, estimates) -> None:
    result = adjust(estimates, ContextFactors(political=1.0, macro=1.0), np.zeros(5), params.context)
    np.testing.assert_allclose(result.sigma_adj, estimates.sigma)
    assert np.all(result.mu_adj >= estimates.mu)


def test_disabled_switch_is_identity(params, estimates) -> None:
    result = adjust(estimates, ContextFactors(political=-1.0), np.ones(5), params.context, enabled=False)
    np.testing.assert_allclose(result.c, 0.0)
    np.testing.assert_allclose(result.mu_adj, estimates.mu)
    np.testing.assert_allclose(result.sigma_adj, estimates.sigma)
    np.testing.assert_allclose(result.cov_adj, estimates.correlation * np.outer(estimates.sigma, estimates.sigma))
    assert result.trace == ()


def test_adjustment_is_clipped_to_c_max(params, estimates) -> None:
    # stocks: 0.005 + 0.03 + 0.01 + 0.015 = 0.06 -> clipped to 0.03
    result = adjust(estimates, ContextFactors(political=1.0, macro=1.0), np.ones(5), params.context)
    assert result.c[0] == pytest.approx(params.context.c_max)
    assert np.all(np.abs(result.c) <= params.context.c_max + 1e-15)
    assert "RC7" in [entry.rule_id for entry in result.trace]


def test_trend_comes_from_estimates_when_omitted(params, estimates) -> None:
    trending = MarketEstimates(estimates.mu, estimates.sigma, estimates.correlation, np.full(5, 0.5))
    result = adjust(trending, ContextFactors(), None, params.context)
    np.testing.assert_allclose(result.c, params.context.b + 0.5 * params.context.beta_tend)


def test_factor_out_of_range_raises() -> None:
    with pytest.raises(ValueError):
        ContextFactors(political=1.5)


@pytest.mark.parametrize("trend", [np.full(5, 1.2), np.zeros(4)])
def test_invalid_trend_raises(params, estimates, trend) -> None:
    with pytest.raises(ValueError):
        adjust(estimates, ContextFactors(), trend, params.context)
