"""Build the market estimates (mu, sigma, rho, s_tend) from local series and Annex A priors.

``data/market/manifest.json`` names each category's CSV and its kind (index,
yield, rate or a composite of other categories); ``manifest.category_returns``
converts it into monthly simple returns. A category's data is used when it
yields at least ``min_months`` monthly returns:

- mu: conjugate normal update of the Annex A mu (prior sd from ``bayes.json``)
  with the sample mean, done in monthly units and annualized (x 12);
- sigma: sample volatility, annualized (x sqrt(12));
- s_tend: last ``trend_window_months`` compounded return vs. posterior mu.

Otherwise the category keeps the Annex A prior (mu, sigma) and a neutral trend.
Correlations are estimated for every pair of data-backed categories with at
least ``min_months`` overlapping returns; every other pair keeps the documented
``default_correlation``. Mixing sources can break positive semi-definiteness,
so the matrix is repaired by clipping negative eigenvalues and rescaling to a
unit diagonal (the nearest-in-spirit valid correlation, not the exact nearest).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Mapping

import numpy as np

from ai.shared.parameters import Parameters
from ai.shared.types import CATEGORY_ORDER, CategoryId, MarketEstimates
from ai.uncertainty.bayesian.estimation import MONTHS_PER_YEAR, MonthlySeries, overlap_correlation, sample_stats
from ai.uncertainty.bayesian.manifest import SeriesSpec, category_returns, load_manifest
from ai.uncertainty.bayesian.normal_update import normal_update
from ai.uncertainty.bayesian.trend import trend_signal

DEFAULT_MARKET_DIR = Path(__file__).resolve().parents[3] / "data" / "market"
EIGENVALUE_FLOOR = 1e-10


@dataclass(frozen=True)
class CategoryEstimate:
    """Provenance of one category's estimates (annual decimals)."""

    source: Literal["data", "prior"]
    months: int
    prior_mean: float
    prior_sd: float
    data_mean: float | None
    data_sigma: float | None
    posterior_mean: float
    posterior_sd: float
    sigma: float
    trend: float
    provider: str | None = None  # BCRP | Yahoo | composite (from the manifest), None without data
    series_code: str | None = None
    kind: str | None = None


@dataclass(frozen=True)
class MarketReport:
    estimates: MarketEstimates
    categories: Mapping[CategoryId, CategoryEstimate]
    estimated_pairs: tuple[tuple[CategoryId, CategoryId], ...]
    psd_repaired: bool


def nearest_correlation(corr: np.ndarray) -> tuple[np.ndarray, bool]:
    """Return a PSD correlation matrix (eigenvalue clipping + unit-diagonal rescale) and whether it changed."""
    sym = (corr + corr.T) / 2.0
    values, vectors = np.linalg.eigh(sym)
    if values.min() >= -1e-12:
        return sym, False
    clipped = (vectors * np.maximum(values, EIGENVALUE_FLOOR)) @ vectors.T
    scale = 1.0 / np.sqrt(np.diag(clipped))
    repaired = clipped * np.outer(scale, scale)
    repaired = (repaired + repaired.T) / 2.0
    np.fill_diagonal(repaired, 1.0)
    return np.clip(repaired, -1.0, 1.0), True


def _category_estimate(
    returns: MonthlySeries | None,
    prior_mean: float,
    prior_sigma: float,
    prior_sd: float,
    params: Parameters,
    spec: SeriesSpec | None = None,
) -> CategoryEstimate:
    months = 0 if returns is None else len(returns.values)
    if returns is None or months < params.bayes.min_months:
        return CategoryEstimate("prior", months, prior_mean, prior_sd, None, None, prior_mean, prior_sd, prior_sigma, 0.0)
    stats = sample_stats(returns)
    posterior = normal_update(
        prior_mean / MONTHS_PER_YEAR, prior_sd / MONTHS_PER_YEAR, stats.monthly_mean, stats.monthly_sd, months
    )
    mu = posterior.mean * MONTHS_PER_YEAR
    trend = trend_signal(returns.values, mu, stats.annual_sigma, params.bayes.trend_window_months)
    return CategoryEstimate(
        source="data",
        months=months,
        prior_mean=prior_mean,
        prior_sd=prior_sd,
        data_mean=stats.annual_mean,
        data_sigma=stats.annual_sigma,
        posterior_mean=mu,
        posterior_sd=posterior.sd * MONTHS_PER_YEAR,
        sigma=stats.annual_sigma,
        trend=trend,
        provider=None if spec is None else spec.source,
        series_code=None if spec is None else spec.series_code,
        kind=None if spec is None else spec.kind,
    )


def build_market_estimates(params: Parameters, data_dir: Path | str = DEFAULT_MARKET_DIR) -> MarketReport:
    directory = Path(data_dir)
    cat = params.categories
    specs = load_manifest(directory)
    returns = category_returns(specs, directory)
    estimates: dict[CategoryId, CategoryEstimate] = {}
    for i, category in enumerate(CATEGORY_ORDER):
        estimates[category] = _category_estimate(
            returns[category],
            float(cat.mu[i]),
            float(cat.sigma[i]),
            float(params.bayes.prior_mean_sd[i]),
            params,
            specs.get(category),
        )

    corr = np.array(cat.default_correlation, dtype=float)
    pairs = []
    for i, a in enumerate(CATEGORY_ORDER):
        for j in range(i + 1, len(CATEGORY_ORDER)):
            b = CATEGORY_ORDER[j]
            if estimates[a].source != "data" or estimates[b].source != "data":
                continue
            rho = overlap_correlation(returns[a], returns[b], params.bayes.min_months)
            if rho is not None:
                corr[i, j] = corr[j, i] = rho
                pairs.append((a, b))
    corr, repaired = nearest_correlation(corr)

    ordered = [estimates[c] for c in CATEGORY_ORDER]
    market = MarketEstimates(
        mu=np.array([e.posterior_mean for e in ordered]),
        sigma=np.array([e.sigma for e in ordered]),
        correlation=corr,
        trend=np.array([e.trend for e in ordered]),
    )
    return MarketReport(market, MappingProxyType(estimates), tuple(pairs), repaired)
