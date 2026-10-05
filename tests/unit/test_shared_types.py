"""Shared value objects: enums, profile, context factors and market estimates."""

import numpy as np
import pytest

from ai.shared import (
    CATEGORY_ORDER,
    CategoryId,
    ContextFactors,
    HorizonLabel,
    MarketEstimates,
    RiskProfile,
    UserProfile,
)


def _corr(rho: float = 0.3) -> np.ndarray:
    corr = np.full((5, 5), rho)
    np.fill_diagonal(corr, 1.0)
    return corr


def test_category_order_is_canonical() -> None:
    assert [c.value for c in CATEGORY_ORDER] == ["stocks", "mixed", "debt", "bonds", "term"]
    assert CategoryId("bonds") is CategoryId.BONDS


def test_enums_accept_their_string_values() -> None:
    assert RiskProfile("muy_conservador") is RiskProfile.MUY_CONSERVADOR
    assert HorizonLabel("largo") is HorizonLabel.LARGO
    assert len(RiskProfile) == 5


def test_context_factors_default_to_zero() -> None:
    factors = ContextFactors()
    assert factors.political == 0.0 and factors.macro == 0.0


@pytest.mark.parametrize("political, macro", [(-1.1, 0.0), (0.0, 1.5)])
def test_context_factors_out_of_range_raise(political: float, macro: float) -> None:
    with pytest.raises(ValueError):
        ContextFactors(political=political, macro=macro)


def test_user_profile_requires_positive_amount() -> None:
    with pytest.raises(ValueError):
        UserProfile(amount=0, horizon_years=3, risk_profile=RiskProfile.MODERADO)


def test_user_profile_accepts_label_only() -> None:
    profile = UserProfile(
        amount=5000, horizon_label=HorizonLabel.LARGO, risk_profile=RiskProfile.MODERADO
    )
    assert profile.horizon_years is None
    assert profile.total_savings is None


def test_market_estimates_valid() -> None:
    est = MarketEstimates(mu=np.zeros(5), sigma=np.ones(5), correlation=_corr(), trend=np.zeros(5))
    assert est.correlation.shape == (5, 5)


def test_market_estimates_are_read_only() -> None:
    est = MarketEstimates(mu=np.zeros(5), sigma=np.ones(5), correlation=_corr(), trend=np.zeros(5))
    with pytest.raises(ValueError):
        est.mu[0] = 1.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mu": np.zeros(4)},
        {"sigma": -np.ones(5)},
        {"correlation": np.eye(4)},
        {"correlation": _corr() + np.triu(np.full((5, 5), 0.1), 1)},
        {"correlation": _corr() + 0.1 * np.eye(5)},
        {"trend": np.zeros((5, 1))},
    ],
)
def test_market_estimates_invalid_raise(kwargs: dict) -> None:
    base = {"mu": np.zeros(5), "sigma": np.ones(5), "correlation": _corr(), "trend": np.zeros(5)}
    base.update(kwargs)
    with pytest.raises(ValueError):
        MarketEstimates(**base)
