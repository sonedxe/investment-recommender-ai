"""Horizon Sugeno system (report v1.1 section 4.5.1)."""

import pytest

from ai.shared import HorizonLabel
from ai.shared.parameters import load_parameters
from ai.uncertainty.fuzzy.horizon import evaluate_horizon


@pytest.fixture(scope="module")
def horizon_params():
    return load_parameters().fuzzy.horizon


def test_report_example_two_and_a_half_years(horizon_params) -> None:
    result = evaluate_horizon(horizon_params, lambda_base=2.0, years=2.5)
    assert result.memberships["corto"] == pytest.approx(0.25)
    assert result.memberships["mediano"] == pytest.approx(0.1667, abs=1e-4)
    assert result.memberships["largo"] == 0.0
    assert result.m_h == pytest.approx(1.30, abs=0.01)
    assert result.lambda_eff == pytest.approx(2.6, abs=0.02)


def test_label_largo(horizon_params) -> None:
    result = evaluate_horizon(horizon_params, lambda_base=1.0, label=HorizonLabel.LARGO)
    assert result.memberships == {"corto": 0.0, "mediano": 0.0, "largo": 1.0}
    assert result.m_h == pytest.approx(0.7)
    assert result.lambda_eff == pytest.approx(0.7)


def test_label_accepts_plain_string(horizon_params) -> None:
    assert evaluate_horizon(horizon_params, 1.0, label="corto").m_h == pytest.approx(1.5)


def test_years_beyond_universe_are_clipped(horizon_params) -> None:
    assert evaluate_horizon(horizon_params, 1.0, years=45).m_h == pytest.approx(0.7)


@pytest.mark.parametrize("kwargs", [{}, {"years": 3.0, "label": "corto"}, {"years": -1.0}, {"label": "eterno"}])
def test_invalid_inputs_raise(horizon_params, kwargs) -> None:
    with pytest.raises(ValueError):
        evaluate_horizon(horizon_params, 1.0, **kwargs)
