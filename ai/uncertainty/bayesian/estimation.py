"""Sample estimates from monthly series stored as ``date,value`` CSVs.

A series is converted to monthly simple returns according to its kind:

- ``index`` (price index level ``P``): ``r_t = P_t / P_{t-1} - 1``;
- ``yield`` (annual yield ``y`` in %, modified duration ``D`` in years):
  ``r_t = y_{t-1}/1200 - D * (y_t - y_{t-1}) / 100`` (carry minus duration x yield change);
- ``rate`` (deposit rate in % annual): ``r_t = rate_{t-1} / 1200`` (accrued interest);
- composite: weighted sum of the component returns on their common months.

Returns are only computed between consecutive calendar months; a gap in the
series simply produces no return for the missing month. Annualization:
mean x 12, volatility x sqrt(12).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

MONTHS_PER_YEAR = 12


@dataclass(frozen=True)
class MonthlySeries:
    """Values indexed by month (``datetime64[M]``), strictly increasing."""

    months: np.ndarray
    values: np.ndarray

    def __post_init__(self) -> None:
        if self.months.shape != self.values.shape or self.months.ndim != 1:
            raise ValueError("months and values must be 1-D arrays of equal length")
        if np.any(np.diff(self.months).astype(int) <= 0):
            raise ValueError("months must be strictly increasing")


@dataclass(frozen=True)
class SampleStats:
    """Monthly and annualized sample moments of a return series."""

    months: int
    monthly_mean: float
    monthly_sd: float
    annual_mean: float
    annual_sigma: float


def read_series(path: Path | str) -> MonthlySeries:
    """Read a ``date,value`` CSV (dates ``YYYY-MM`` or ``YYYY-MM-DD``); rows are sorted by month."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {"date", "value"} <= set(reader.fieldnames):
            raise ValueError(f"{path}: expected 'date,value' columns")
        rows = [(np.datetime64(row["date"][:7], "M"), float(row["value"])) for row in reader if row["value"]]
    if not rows:
        return MonthlySeries(np.array([], dtype="datetime64[M]"), np.array([], dtype=float))
    rows.sort(key=lambda item: item[0])
    months = np.array([m for m, _ in rows], dtype="datetime64[M]")
    values = np.array([v for _, v in rows], dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{path}: values must be finite")
    return MonthlySeries(months, values)


def _consecutive(series: MonthlySeries, returns: np.ndarray) -> MonthlySeries:
    consecutive = np.diff(series.months).astype(int) == 1
    return MonthlySeries(series.months[1:][consecutive], returns[consecutive])


def monthly_returns(series: MonthlySeries) -> MonthlySeries:
    """Index kind: simple returns ``v_t / v_{t-1} - 1`` for consecutive months; indexed by ``t``."""
    if np.any(series.values <= 0):
        raise ValueError("index levels must be positive")
    return _consecutive(series, series.values[1:] / series.values[:-1] - 1.0)


def yield_returns(series: MonthlySeries, duration_years: float) -> MonthlySeries:
    """Yield kind (% annual): ``y_{t-1}/1200 - D * (y_t - y_{t-1}) / 100`` for consecutive months."""
    if duration_years < 0:
        raise ValueError("duration_years must be non-negative")
    y = series.values
    carry = y[:-1] / (100.0 * MONTHS_PER_YEAR)
    price_effect = -duration_years * np.diff(y) / 100.0
    return _consecutive(series, carry + price_effect)


def rate_returns(series: MonthlySeries) -> MonthlySeries:
    """Rate kind (% annual deposit rate): one month of interest ``rate_{t-1} / 1200``."""
    return _consecutive(series, series.values[:-1] / (100.0 * MONTHS_PER_YEAR))


def composite_returns(parts: list[tuple[MonthlySeries, float]]) -> MonthlySeries:
    """Weighted sum of monthly returns over the months common to every component."""
    if not parts:
        raise ValueError("a composite needs at least one component")
    common = parts[0][0].months
    for returns, _ in parts[1:]:
        common = np.intersect1d(common, returns.months)
    total = np.zeros(len(common), dtype=float)
    for returns, weight in parts:
        index = np.searchsorted(returns.months, common)
        total += weight * returns.values[index]
    return MonthlySeries(common.astype("datetime64[M]"), total)


def sample_stats(returns: MonthlySeries) -> SampleStats:
    """Sample mean and sd (ddof=1) of monthly returns, annualized; needs >= 2 returns."""
    n = len(returns.values)
    if n < 2:
        raise ValueError("at least two returns are required")
    mean = float(returns.values.mean())
    sd = float(returns.values.std(ddof=1))
    return SampleStats(n, mean, sd, mean * MONTHS_PER_YEAR, float(sd * np.sqrt(MONTHS_PER_YEAR)))


def overlap_correlation(a: MonthlySeries, b: MonthlySeries, min_overlap: int) -> float | None:
    """Pearson correlation over the common months, or ``None`` with fewer than ``min_overlap``."""
    common, ia, ib = np.intersect1d(a.months, b.months, return_indices=True)
    if len(common) < max(min_overlap, 3):
        return None
    x, y = a.values[ia], b.values[ib]
    if x.std() == 0 or y.std() == 0:
        return None
    return float(np.clip(np.corrcoef(x, y)[0, 1], -1.0, 1.0))
