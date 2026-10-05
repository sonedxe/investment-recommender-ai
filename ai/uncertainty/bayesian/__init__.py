"""Bayesian market estimation: sample moments, conjugate normal update of mu, trend signal."""

from ai.uncertainty.bayesian.market import CategoryEstimate, MarketReport, build_market_estimates
from ai.uncertainty.bayesian.normal_update import NormalPosterior, normal_update
from ai.uncertainty.bayesian.trend import trend_signal

__all__ = [
    "CategoryEstimate",
    "MarketReport",
    "NormalPosterior",
    "build_market_estimates",
    "normal_update",
    "trend_signal",
]
