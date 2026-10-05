"""build_market_estimates: manifest loading, data vs prior sources, correlation repair, real data smoke test."""

import json
from pathlib import Path

import numpy as np
import pytest

from ai.shared.parameters import load_parameters
from ai.shared.types import CategoryId
from ai.uncertainty.bayesian.manifest import load_manifest
from ai.uncertainty.bayesian.market import build_market_estimates, nearest_correlation
from tests.unit.test_bayes_estimation import write_series

INDEX = {"source": "test", "kind": "index"}


def write_manifest(directory: Path, categories: dict) -> None:
    (directory / "manifest.json").write_text(json.dumps({"categories": categories}), encoding="utf-8")


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


def test_manifest_file_missing_falls_back_to_prior(params, tmp_path: Path) -> None:
    write_manifest(tmp_path, {"stocks": {**INDEX, "file": "absent.csv"}})
    info = build_market_estimates(params, tmp_path).categories[CategoryId.STOCKS]
    assert info.source == "prior" and info.months == 0 and info.provider is None


def test_short_series_falls_back_to_prior(params, tmp_path: Path) -> None:
    write_manifest(tmp_path, {"stocks": {**INDEX, "file": "stocks.csv"}})
    write_series(tmp_path / "stocks.csv", [0.02] * 10)
    info = build_market_estimates(params, tmp_path).categories[CategoryId.STOCKS]
    assert info.source == "prior" and info.months == 10


def test_data_category_is_updated(params, tmp_path: Path) -> None:
    returns = np.random.default_rng(1).normal(0.02, 0.06, 60)
    write_manifest(tmp_path, {"stocks": {**INDEX, "source": "BCRP", "series_code": "X1", "file": "stocks.csv"}})
    write_series(tmp_path / "stocks.csv", returns)
    report = build_market_estimates(params, tmp_path)
    info = report.categories[CategoryId.STOCKS]
    assert info.source == "data" and info.months == 60
    assert (info.provider, info.series_code, info.kind) == ("BCRP", "X1", "index")
    assert info.sigma == pytest.approx(returns.std(ddof=1) * np.sqrt(12))
    low, high = sorted((info.prior_mean, info.data_mean))
    assert low < info.posterior_mean < high
    assert info.posterior_sd < info.prior_sd
    assert report.estimates.mu[0] == pytest.approx(info.posterior_mean)
    assert report.categories[CategoryId.MIXED].source == "prior"


def test_correlation_estimated_for_data_pairs(params, tmp_path: Path) -> None:
    rng = np.random.default_rng(2)
    base = rng.normal(0.01, 0.05, 48)
    write_manifest(tmp_path, {"stocks": {**INDEX, "file": "stocks.csv"}, "mixed": {**INDEX, "file": "mixed.csv"}})
    write_series(tmp_path / "stocks.csv", base)
    write_series(tmp_path / "mixed.csv", 0.5 * base + rng.normal(0, 0.005, 48))
    report = build_market_estimates(params, tmp_path)
    corr = report.estimates.correlation
    assert report.estimated_pairs == ((CategoryId.STOCKS, CategoryId.MIXED),)
    assert corr[0, 1] > 0.9
    assert corr[0, 2] == pytest.approx(0.3)


def test_composite_category_combines_component_returns(params, tmp_path: Path) -> None:
    rng = np.random.default_rng(3)
    stocks, debt = rng.normal(0.01, 0.05, 36), rng.normal(0.003, 0.002, 36)
    write_series(tmp_path / "stocks.csv", stocks)
    write_series(tmp_path / "debt.csv", debt)
    write_manifest(tmp_path, {
        "stocks": {**INDEX, "file": "stocks.csv"},
        "debt": {**INDEX, "file": "debt.csv"},
        "mixed": {"source": "composite", "kind": "composite", "components": ["stocks", "debt"], "weights": [0.5, 0.5]},
    })
    info = build_market_estimates(params, tmp_path).categories[CategoryId.MIXED]
    mixed = 0.5 * stocks + 0.5 * debt
    assert info.source == "data" and info.months == 36 and info.provider == "composite"
    assert info.data_mean == pytest.approx(mixed.mean() * 12)
    assert info.sigma == pytest.approx(mixed.std(ddof=1) * np.sqrt(12))


def test_composite_with_missing_component_keeps_prior(params, tmp_path: Path) -> None:
    write_series(tmp_path / "stocks.csv", np.full(36, 0.01))
    write_manifest(tmp_path, {
        "stocks": {**INDEX, "file": "stocks.csv"},
        "mixed": {"source": "composite", "kind": "composite", "components": ["stocks", "debt"], "weights": [0.5, 0.5]},
    })
    assert build_market_estimates(params, tmp_path).categories[CategoryId.MIXED].source == "prior"


@pytest.mark.parametrize(
    "entry",
    [
        {"source": "x", "kind": "price", "file": "a.csv"},
        {"source": "x", "kind": "yield", "file": "a.csv"},
        {"source": "x", "kind": "index"},
        {"source": "x", "kind": "composite", "components": ["stocks"], "weights": [0.4]},
    ],
)
def test_invalid_manifest_entries_raise(tmp_path: Path, entry) -> None:
    write_manifest(tmp_path, {"mixed": entry})
    with pytest.raises(ValueError):
        load_manifest(tmp_path)


def test_real_manifest_loads_every_category() -> None:
    specs = load_manifest(Path(__file__).resolve().parents[2] / "data" / "market")
    assert set(specs) == set(CategoryId)
    # W15: mixed funds come from the SBS (AFP Fondo 2 valor cuota index), not the composite.
    assert specs[CategoryId.MIXED].kind == "index" and specs[CategoryId.MIXED].source == "SBS"
    assert specs[CategoryId.MIXED].file and not specs[CategoryId.MIXED].components
    assert specs[CategoryId.BONDS].kind == "yield" and specs[CategoryId.BONDS].duration_years > 0


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
    assert all(info.source == "data" for info in report.categories.values())
    assert np.all(report.estimates.sigma > 0)
    mixed = report.categories[CategoryId.MIXED]
    assert (mixed.provider, mixed.kind) == ("SBS", "index") and mixed.months >= 24
