"""Value objects shared by every AI module.

All rates (returns, volatilities, adjustments) are decimals: 12.2 % -> 0.122.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

N_CATEGORIES = 5


class CategoryId(str, Enum):
    """Investment categories, declared in canonical order."""

    STOCKS = "stocks"
    MIXED = "mixed"
    DEBT = "debt"
    BONDS = "bonds"
    TERM = "term"


CATEGORY_ORDER: tuple[CategoryId, ...] = tuple(CategoryId)


class RiskProfile(str, Enum):
    """Closed risk-profile scale; the code maps each label to lambda_base (D5)."""

    MUY_AGRESIVO = "muy_agresivo"
    AGRESIVO = "agresivo"
    MODERADO = "moderado"
    CONSERVADOR = "conservador"
    MUY_CONSERVADOR = "muy_conservador"


class HorizonLabel(str, Enum):
    """Qualitative investment horizon, matching the fuzzy horizon sets."""

    CORTO = "corto"
    MEDIANO = "mediano"
    LARGO = "largo"


@dataclass(frozen=True)
class UserProfile:
    """Structured investor profile produced by the interpretation stage."""

    amount: float
    risk_profile: RiskProfile
    horizon_years: float | None = None
    horizon_label: HorizonLabel | None = None
    total_savings: float | None = None
    emergency_months: float | None = None

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("amount must be positive")
        if self.horizon_years is not None and self.horizon_years < 0:
            raise ValueError("horizon_years must be non-negative")
        if self.total_savings is not None and self.total_savings <= 0:
            raise ValueError("total_savings must be positive")
        if self.emergency_months is not None and self.emergency_months < 0:
            raise ValueError("emergency_months must be non-negative")


@dataclass(frozen=True)
class ContextFactors:
    """Global context factors in [-1, 1]: negative is adverse, positive favorable."""

    political: float = 0.0
    macro: float = 0.0

    def __post_init__(self) -> None:
        for name in ("political", "macro"):
            value = getattr(self, name)
            if not -1.0 <= value <= 1.0:
                raise ValueError(f"{name} factor must be in [-1, 1], got {value}")


def _frozen_array(value: object, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.array(value, dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    array.setflags(write=False)
    return array


@dataclass(frozen=True)
class MarketEstimates:
    """Per-category market estimates in canonical category order."""

    mu: np.ndarray
    sigma: np.ndarray
    correlation: np.ndarray
    trend: np.ndarray

    def __post_init__(self) -> None:
        vector = (N_CATEGORIES,)
        object.__setattr__(self, "mu", _frozen_array(self.mu, vector, "mu"))
        object.__setattr__(self, "sigma", _frozen_array(self.sigma, vector, "sigma"))
        object.__setattr__(self, "trend", _frozen_array(self.trend, vector, "trend"))
        corr = _frozen_array(self.correlation, (N_CATEGORIES, N_CATEGORIES), "correlation")
        object.__setattr__(self, "correlation", corr)
        if np.any(self.sigma < 0):
            raise ValueError("sigma must be non-negative")
        validate_correlation(corr)


def validate_correlation(corr: np.ndarray) -> None:
    """Raise ``ValueError`` unless ``corr`` is symmetric with unit diagonal and |rho| <= 1."""
    if not np.allclose(corr, corr.T, atol=1e-12):
        raise ValueError("correlation must be symmetric")
    if not np.allclose(np.diag(corr), 1.0, atol=1e-12):
        raise ValueError("correlation must have a unit diagonal")
    if np.any(np.abs(corr) > 1.0 + 1e-12):
        raise ValueError("correlation entries must be in [-1, 1]")
