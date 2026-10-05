"""Absorption Mamdani system (report v1.1 section 4.5.2, Mamdani version)."""

import numpy as np
import pytest

from ai.shared.parameters import load_parameters
from ai.uncertainty.fuzzy.absorption import ASSUMPTION_MEDIUM_CAPACITY, evaluate_absorption

# Mamdani reference centroid for r = 0.25, E = 3 (min implication, max aggregation,
# centroid on the 1001-point universe), computed by this engine on 2026-10-04.
# Report v1.1 used Sugeno singletons (0.20 / 0.50 / 0.85) and obtained 0.54.
REFERENCE_CENTROID = 0.5345


@pytest.fixture(scope="module")
def absorption_params():
    return load_parameters().fuzzy.absorption


@pytest.fixture(scope="module")
def reference(absorption_params):
    return evaluate_absorption(absorption_params, amount=5000, total_savings=20000, emergency_months=3)


def test_crisp_inputs(reference) -> None:
    assert reference.r == pytest.approx(0.25)
    assert reference.e == pytest.approx(3.0)
    assert reference.assumed is False


def test_input_memberships(reference) -> None:
    r, e = reference.ratio_memberships, reference.emergency_memberships
    assert (r["bajo"], r["medio"], r["alto"]) == pytest.approx((0.75, 0.1667, 0.0), abs=1e-4)
    assert (e["insuficiente"], e["adecuada"]) == pytest.approx((0.3333, 0.25), abs=1e-4)


def test_rule_activations(reference) -> None:
    expected = (0.3333, 0.25, 0.1667, 0.1667, 0.0, 0.0)
    actual = tuple(reference.activations[f"RA{i}"] for i in range(1, 7))
    assert actual == pytest.approx(expected, abs=1e-4)


def test_centroid_reference_value(reference) -> None:
    assert 0.0 < reference.centroid < 1.0
    assert reference.centroid == pytest.approx(REFERENCE_CENTROID, abs=1e-3)


def test_aggregated_set_and_interpolation(reference) -> None:
    assert reference.universe.size >= 1001
    assert np.all((reference.mu_ca >= 0) & (reference.mu_ca <= 1))
    # Alta is clipped at RA2 = 0.25, Media at max(RA1, RA4) = 0.3333.
    assert reference.membership_at(1.0) == pytest.approx(0.25, abs=1e-6)
    assert reference.membership_at(0.5) == pytest.approx(1 / 3, abs=1e-6)
    assert reference.membership_at(0.0) == pytest.approx(1 / 6, abs=1e-6)


def test_ratio_and_emergency_are_clipped(absorption_params) -> None:
    result = evaluate_absorption(absorption_params, amount=30000, total_savings=20000, emergency_months=40)
    assert result.r == 1.0 and result.e == 12.0


@pytest.mark.parametrize("savings, months", [(None, 3), (20000, None), (None, None)])
def test_missing_data_assumes_medium_capacity(absorption_params, savings, months) -> None:
    result = evaluate_absorption(absorption_params, amount=5000, total_savings=savings, emergency_months=months)
    assert result.assumed is True
    assert result.assumptions == (ASSUMPTION_MEDIUM_CAPACITY,)
    assert ASSUMPTION_MEDIUM_CAPACITY == "Asumimos una capacidad media para asumir pérdidas."
    assert result.centroid == pytest.approx(0.5, abs=1e-6)
    assert result.membership_at(0.5) == pytest.approx(1.0)
    assert result.membership_at(0.1) == 0.0


@pytest.mark.parametrize("amount, savings, months", [(0, 20000, 3), (5000, 0, 3), (5000, 20000, -1)])
def test_invalid_inputs_raise(absorption_params, amount, savings, months) -> None:
    with pytest.raises(ValueError):
        evaluate_absorption(absorption_params, amount=amount, total_savings=savings, emergency_months=months)
