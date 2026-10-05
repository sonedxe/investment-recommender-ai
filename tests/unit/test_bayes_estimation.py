"""Sample estimation, conjugate update and trend signal."""

import math
from pathlib import Path

import numpy as np
import pytest

from ai.uncertainty.bayesian.estimation import (
    MonthlySeries,
    composite_returns,
    monthly_returns,
    overlap_correlation,
    rate_returns,
    read_series,
    sample_stats,
    yield_returns,
)
from ai.uncertainty.bayesian.normal_update import normal_update
from ai.uncertainty.bayesian.trend import trend_signal


def write_series(path: Path, returns, start: str = "2020-01") -> Path:
    first = np.datetime64(start, "M")
    values = 100.0 * np.cumprod(np.concatenate([[1.0], 1.0 + np.asarray(returns, dtype=float)]))
    lines = ["date,value"] + [f"{first + np.timedelta64(i, 'M')}-01,{v:.10f}" for i, v in enumerate(values)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_annualization(tmp_path: Path) -> None:
    returns = np.array([0.01, 0.03] * 12)
    stats = sample_stats(monthly_returns(read_series(write_series(tmp_path / "s.csv", returns))))
    assert stats.months == 24
    assert stats.annual_mean == pytest.approx(0.02 * 12)
    assert stats.annual_sigma == pytest.approx(returns.std(ddof=1) * math.sqrt(12))


def test_gaps_produce_no_return(tmp_path: Path) -> None:
    path = tmp_path / "gap.csv"
    path.write_text("date,value\n2020-01-01,100\n2020-02-01,110\n2020-04-01,121\n2020-05-01,133.1\n")
    returns = monthly_returns(read_series(path))
    assert returns.values == pytest.approx([0.1, 0.1])


def months(start: str, n: int) -> np.ndarray:
    return np.datetime64(start, "M") + np.arange(n)


def test_yield_to_return_hand_computed() -> None:
    # y: 6.0 % -> 6.5 % with D = 7: carry 6.0/1200 = 0.005, price -7 * 0.5/100 = -0.035 -> -0.030.
    # y: 6.5 % -> 6.3 %: carry 6.5/1200 = 0.0054167, price -7 * (-0.2)/100 = +0.014 -> 0.0194167.
    series = MonthlySeries(months("2024-01", 3), np.array([6.0, 6.5, 6.3]))
    returns = yield_returns(series, 7.0)
    assert returns.values == pytest.approx([-0.030, 6.5 / 1200 + 0.014])
    assert list(returns.months) == list(months("2024-02", 2))


def test_yield_and_rate_skip_gaps() -> None:
    series = MonthlySeries(np.array(["2024-01", "2024-02", "2024-04"], dtype="datetime64[M]"), np.array([4.8, 6.0, 3.6]))
    assert yield_returns(series, 0.0).values == pytest.approx([4.8 / 1200])
    assert rate_returns(series).values == pytest.approx([4.8 / 1200])


def test_rate_to_return_is_accrued_interest() -> None:
    series = MonthlySeries(months("2024-01", 3), np.array([4.8, 6.0, 3.6]))
    assert rate_returns(series).values == pytest.approx([0.004, 0.005])


def test_composite_uses_common_months() -> None:
    a = MonthlySeries(months("2024-01", 4), np.array([0.01, 0.02, 0.03, 0.04]))
    b = MonthlySeries(months("2024-03", 3), np.array([0.10, 0.20, 0.30]))
    mixed = composite_returns([(a, 0.5), (b, 0.5)])
    assert list(mixed.months) == list(months("2024-03", 2))
    assert mixed.values == pytest.approx([0.065, 0.12])


def test_index_returns_reject_non_positive_levels() -> None:
    with pytest.raises(ValueError):
        monthly_returns(MonthlySeries(months("2024-01", 2), np.array([0.0, 1.0])))


def test_overlap_correlation(tmp_path: Path) -> None:
    rng = np.random.default_rng(0)
    r = rng.normal(0.01, 0.05, 40)
    a = monthly_returns(read_series(write_series(tmp_path / "a.csv", r)))
    b = monthly_returns(read_series(write_series(tmp_path / "b.csv", 2 * r, start="2020-01")))
    late = monthly_returns(read_series(write_series(tmp_path / "c.csv", r[:10], start="2030-01")))
    assert overlap_correlation(a, b, 24) == pytest.approx(1.0)
    assert overlap_correlation(a, late, 24) is None


def test_update_with_infinite_data_variance_returns_prior() -> None:
    posterior = normal_update(0.05, 0.02, 0.30, math.inf, 100)
    assert (posterior.mean, posterior.sd) == (0.05, 0.02)


def test_update_with_large_n_tends_to_sample_mean() -> None:
    posterior = normal_update(0.05, 0.02, 0.30, 0.2, 10**9)
    assert posterior.mean == pytest.approx(0.30, abs=1e-6)
    assert posterior.sd < 1e-5


def test_update_analytic_equal_precision() -> None:
    # tau0^2 = s^2 / n -> equal weights: posterior mean is the average, sd = tau0 / sqrt(2).
    posterior = normal_update(0.0, 0.1, 0.2, 0.1 * math.sqrt(4), 4)
    assert posterior.mean == pytest.approx(0.1)
    assert posterior.sd == pytest.approx(0.1 / math.sqrt(2))


def test_trend_clipping_and_short_series() -> None:
    assert trend_signal([0.05] * 12, mu=0.10, sigma=0.20) == 1.0
    assert trend_signal([-0.05] * 12, mu=0.10, sigma=0.20) == -1.0
    r12 = 1.01**12 - 1
    assert trend_signal([0.0] * 6 + [0.01] * 12, mu=0.10, sigma=0.20) == pytest.approx((r12 - 0.10) / 0.20)
    assert trend_signal([0.05] * 11, mu=0.10, sigma=0.20) == 0.0
