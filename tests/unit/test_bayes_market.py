"""build_market_estimates: data vs prior sources, correlation repair, real data smoke test."""

from pathlib import Path

import numpy as np
import pytest

from ai.shared.parameters import load_parameters
from ai.shared.types import CategoryId
from ai.uncertainty.bayesian.market import build_market_estimates, nearest_correlation
from tests.unit.test_bayes_estimation import write_series


@pytest.fixture(scope="module")
def params():
    return load_parameters()


def test_missing_categories_use_annex_a_prior(params, tmp_path: Path) -> None:
    report = build_market_estimates(params, tmp_path)
    assert all(info.source == "prior" for info in report.categories.values())
    assert np.array_equal(report.estimates.mu, params.categories.mu)
    assert np.array_equal(report.estimates.sigma, params.categories.sigma)
    assert np.array_equal(report.estimates.correlation, params.categories.default_correlation)
    assert np.all(report.estimates.trend == 0)


def test_short_series_falls_back_to_prior(params, tmp_path: Path) -> None:
    write_series(tmp_path / "stocks.csv", [0.02] * 10)
    info = build_market_estimates(params, tmp_path).categories[CategoryId.STOCKS]
    assert info.source == "prior" and info.months == 10


def test_data_category_is_updated(params, tmp_path: Path) -> None:
    returns = np.random.default_rng(1).normal(0.02, 0.06, 60)
    write_series(tmp_path / "stocks.csv", returns)
    report = build_market_estimates(params, tmp_path)
    info = report.categories[CategoryId.STOCKS]
    assert info.source == "data" and info.months == 60
    assert info.sigma == pytest.approx(returns.std(ddof=1) * np.sqrt(12))
    low, high = sorted((info.prior_mean, info.data_mean))
    assert low < info.posterior_mean < high
    assert info.posterior_sd < info.prior_sd
    assert report.estimates.mu[0] == pytest.approx(info.posterior_mean)
    assert report.categories[CategoryId.MIXED].source == "prior"


def test_correlation_estimated_for_data_pairs(params, tmp_path: Path) -> None:
    rng = np.random.default_rng(2)
    base = rng.normal(0.01, 0.05, 48)
    write_series(tmp_path / "stocks.csv", base)
    write_series(tmp_path / "mixed.csv", 0.5 * base + rng.normal(0, 0.005, 48))
    report = build_market_estimates(params, tmp_path)
    corr = report.estimates.correlation
    assert report.estimated_pairs == ((CategoryId.STOCKS, CategoryId.MIXED),)
    assert corr[0, 1] > 0.9
    assert corr[0, 2] == pytest.approx(0.3)


def test_nearest_correlation_repairs_non_psd() -> None:
    bad = np.array([[1.0, 0.9, -0.9], [0.9, 1.0, 0.9], [-0.9, 0.9, 1.0]])
    assert np.linalg.eigvalsh(bad).min() < 0
    fixed, repaired = nearest_correlation(bad)
    assert repaired
    assert np.allclose(fixed, fixed.T) and np.allclose(np.diag(fixed), 1.0)
    assert np.linalg.eigvalsh(fixed).min() >= -1e-9


def test_real_market_directory_smoke(params) -> None:
    report = build_market_estimates(params)
    corr = report.estimates.correlation
    assert np.allclose(corr, corr.T) and np.allclose(np.diag(corr), 1.0)
    assert np.linalg.eigvalsh(corr).min() >= -1e-9
    assert np.all(np.abs(report.estimates.trend) <= 1)
    assert report.categories[CategoryId.BONDS].source == "prior"
