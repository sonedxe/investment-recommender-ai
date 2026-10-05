"""Explainer: scenarios in code, number validation, retry and template fallback."""

from __future__ import annotations

import pytest

from ai.generative.explainer import (
    build_explanation_input,
    compute_scenarios,
    explain,
    find_invalid_numbers,
    validate_explanation,
)
from ai.generative.offline import template_explanation
from ai.shared.types import CategoryId as C
from tests.unit._fake_llm import FakeLLM

ALLOCATION = [
    (C.STOCKS, "Fondos de acciones", 0.02, 100.0),
    (C.MIXED, "Fondos mixtos", 0.0, 0.0),
    (C.DEBT, "Fondos de deuda", 0.18, 900.0),
    (C.BONDS, "Bonos soberanos (BTP)", 0.40, 2000.0),
    (C.TERM, "Depósito a plazo fijo", 0.40, 2000.0),
]


@pytest.fixture
def explanation_input():
    return build_explanation_input(
        amount=5000, allocation=ALLOCATION, expected_return=0.052, sigma=0.04, risk_profile="conservador",
        horizon_years=3, m_h=1.2, absorption_level=0.5, assumptions=["Se asumió un panorama político neutral."],
    )


def valid_llm_answer(explanation_input) -> dict:
    data = template_explanation(explanation_input)
    data["resumen"] = "Tu dinero va sobre todo a inversiones predecibles: 40 % en bonos, S/ 2,000.00."
    return data


def test_scenarios_use_the_one_sided_normal_quantile() -> None:
    bad, normal, good = compute_scenarios(5000, 0.052, 0.04)
    assert bad.amount == round(5000 * (0.052 - 1.65 * 0.04), 2) == -70.0
    assert normal.amount == 260.0
    assert good.amount == 590.0


def test_template_passes_its_own_validator(explanation_input) -> None:
    result = explain(explanation_input)
    assert result.source == "offline" and result.validation.passed
    assert 3 <= len(result.paragraphs) <= 6
    assert [s.amount for s in result.scenarios] == [-70.0, 260.0, 590.0]
    assert "S/ 2,000.00" in result.paragraphs[0]
    assert "puedes ajustar" in result.assumptions[0]


def test_number_validator_tolerates_rounding_and_formats() -> None:
    allowed = [5000, 2000, 12.47, 40]
    assert find_invalid_numbers("S/ 5,000.00 y S/ 2,000.00, 12.5 % y 40 %", allowed) == []
    assert find_invalid_numbers("12,5 %", allowed) == []
    assert find_invalid_numbers("ganarías S/ 7,000.00", allowed) == ["7,000.00"]


def test_valid_llm_explanation_is_accepted(explanation_input) -> None:
    llm = FakeLLM(valid_llm_answer(explanation_input))
    result = explain(explanation_input, llm=llm)
    assert result.source == "llm" and result.prompt_version == "explain.v1"
    assert result.validation.attempts == 1 and result.validation.passed


def test_invented_number_is_retried_with_the_error_then_template(explanation_input) -> None:
    bad = valid_llm_answer(explanation_input)
    bad["parrafos"][1] = "Podrías ganar S/ 9,999.00 en un año, con un 15 % de rendimiento y S/ 9,999.00."
    llm = FakeLLM(bad, bad)
    result = explain(explanation_input, llm=llm)
    assert len(llm.calls) == 2
    assert "9,999.00" in llm.calls[1]["messages"][-1]["content"]
    assert result.source == "offline" and result.validation.fallback
    assert any("9,999.00" in e for e in result.validation.errors)


def test_retry_can_recover(explanation_input) -> None:
    bad = valid_llm_answer(explanation_input)
    bad["resumen"] = "Ganarás S/ 123.00 seguro."
    llm = FakeLLM(bad, valid_llm_answer(explanation_input))
    result = explain(explanation_input, llm=llm)
    assert result.source == "llm" and result.validation.attempts == 2


def test_validator_flags_money_format_percent_without_amount_and_missing_assumptions(explanation_input) -> None:
    data = valid_llm_answer(explanation_input)
    data["parrafos"][0] = "Ponemos 40 % en bonos."
    data["parrafos"][2] = "Son S/ 2000 en bonos."
    data["supuestos"] = []
    errors = " | ".join(validate_explanation(data, explanation_input))
    assert "porcentaje sin monto" in errors
    assert "formato de moneda" in errors
    assert "faltan supuestos" in errors


def test_altered_scenario_amount_is_rejected(explanation_input) -> None:
    data = valid_llm_answer(explanation_input)
    data["escenarios"][1]["amount"] = 300
    assert any("escenario" in e for e in validate_explanation(data, explanation_input))
