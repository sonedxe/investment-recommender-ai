"""Offline extractor, clarification templates and Spanish formatting."""

from __future__ import annotations

import pytest

from ai.generative.formatting import format_money, format_percent
from ai.generative.offline import clarification_question, extract, parse_number
from ai.generative.schema import FIELD_AMOUNT, FIELD_EMERGENCY, FIELD_HORIZON, FIELD_RISK, FIELD_SAVINGS
from ai.shared.types import HorizonLabel, RiskProfile

COMPLETE = (
    "Tengo S/ 5000 de mis S/ 20000, no me gusta arriesgar y no los necesito en unos 3 años; "
    "tengo 4 meses de colchón"
)


def test_golden_complete_text_extracts_every_field_with_evidence() -> None:
    out = extract(COMPLETE)
    assert out.amount == 5000
    assert out.total_savings == 20000
    assert out.horizon_years == 3
    assert out.risk_profile is RiskProfile.CONSERVADOR
    assert out.emergency_months == 4
    assert out.evidence[FIELD_AMOUNT] == "S/ 5000"
    assert out.evidence[FIELD_SAVINGS] == "S/ 20000"
    assert out.evidence[FIELD_HORIZON] == "unos 3 años"
    assert out.evidence[FIELD_RISK] == "no me gusta arriesgar"
    for field_id, evidence in out.evidence.items():
        assert evidence in COMPLETE, field_id


def test_golden_vague_horizon_is_never_a_number() -> None:
    out = extract("Para dentro de unos añitos, nada muy arriesgado")
    assert out.horizon_years is None and out.horizon_label is None
    assert out.risk_profile is RiskProfile.CONSERVADOR


def test_golden_missing_amount() -> None:
    out = extract("Quiero invertir sin arriesgar mucho")
    assert out.amount is None
    assert out.risk_profile is RiskProfile.CONSERVADOR


def test_golden_contradiction_leaves_risk_empty() -> None:
    out = extract("Quiero máxima ganancia pero no puedo perder nada")
    assert out.risk_profile is None
    assert [f for f, _ in out.contradictions] == [FIELD_RISK]
    assert "máxima ganancia" in out.contradictions[0][1]


def test_golden_refusal_of_savings() -> None:
    out = extract("Prefiero no decir cuánto tengo ahorrado")
    assert out.rejected == [FIELD_SAVINGS]
    assert out.total_savings is None


@pytest.mark.parametrize(
    ("text", "amount"),
    [("Quiero invertir S/ 5,000", 5000), ("quiero invertir 5 mil", 5000), ("pongo 5000 soles", 5000),
     ("invertir S/. 1,250.50", 1250.5)],
)
def test_amount_formats(text: str, amount: float) -> None:
    assert extract(text).amount == amount


def test_savings_cues() -> None:
    out = extract("tengo ahorrados 20 mil y quiero invertir 5 mil")
    assert (out.amount, out.total_savings) == (5000, 20000)


def test_age_is_not_a_horizon_and_label_phrases_are_horizons() -> None:
    assert extract("Tengo 30 años y quiero invertir S/ 5000").horizon_years is None
    assert extract("lo quiero a largo plazo").horizon_label is HorizonLabel.LARGO
    assert extract("lo necesito pronto").horizon_label is HorizonLabel.CORTO
    assert extract("no lo toco en muchos años").horizon_label is HorizonLabel.LARGO
    assert extract("por un año").horizon_years == 1


@pytest.mark.parametrize(
    ("text", "label"),
    [("no quiero perder nada", RiskProfile.MUY_CONSERVADOR), ("no me gusta arriesgar", RiskProfile.CONSERVADOR),
     ("acepto algo de riesgo", RiskProfile.MODERADO), ("acepto riesgo", RiskProfile.AGRESIVO),
     ("busco la máxima ganancia", RiskProfile.MUY_AGRESIVO), ("no acepto riesgo", None)],
)
def test_risk_keywords(text: str, label: RiskProfile | None) -> None:
    assert extract(text).risk_profile is label


def test_dollars_are_a_currency_contradiction() -> None:
    out = extract("quiero invertir 300 dólares")
    assert out.amount is None
    assert out.contradictions[0][0] == FIELD_AMOUNT


def test_bare_number_answers_the_asked_field() -> None:
    assert extract("3", asked=FIELD_HORIZON).horizon_years == 3
    assert extract("unos 20 mil", asked=FIELD_SAVINGS).total_savings == 20000
    assert extract("6", asked=FIELD_EMERGENCY).emergency_months == 6
    assert extract("prefiero no decir", asked=FIELD_EMERGENCY).rejected == [FIELD_EMERGENCY]


def test_risk_option_labels_round_trip_through_the_extractor() -> None:
    question = clarification_question(FIELD_RISK)
    assert question.options is not None and len(question.options) == 5
    for option in question.options:
        assert extract(option.label, asked=FIELD_RISK).risk_profile.value == option.value
        assert extract(option.value, asked=FIELD_RISK).risk_profile.value == option.value


def test_numeric_questions_are_free_input_with_unit() -> None:
    question = clarification_question(FIELD_AMOUNT)
    assert question.free_input and question.unit == "soles"
    assert question.text == "¿Cuánto dinero quieres invertir, en soles?"


def test_spanish_money_and_percent_formatting() -> None:
    assert format_money(1250) == "S/ 1,250.00"
    assert format_money(-150) == "-S/ 150.00"
    assert format_money(0.004) == "S/ 0.00"
    assert format_percent(0.4) == "40 %"
    assert format_percent(0.125) == "12.5 %"
    assert parse_number("1,250.00") == 1250 and parse_number("12,5") == 12.5 and parse_number("20.000") == 20000
