"""Interpreter: the code decides completeness, question order, assumptions and lambda_base."""

from __future__ import annotations

from ai.generative.interpreter import interpret
from ai.generative.port import LanguageModelError
from ai.generative.schema import FIELD_AMOUNT, FIELD_EMERGENCY, FIELD_HORIZON, FIELD_RISK, FIELD_SAVINGS
from ai.shared.types import RiskProfile
from tests.unit._fake_llm import FakeLLM

COMPLETE = (
    "Tengo S/ 5000 de mis S/ 20000, no me gusta arriesgar y no los necesito en unos 3 años; "
    "tengo 4 meses de colchón"
)


def user(text: str) -> dict:
    return {"role": "user", "content": text}


def asked(field: str) -> dict:
    return {"role": "assistant", "content": "pregunta", "field": field}


def test_complete_text_is_complete_offline_with_lambda_from_parameters() -> None:
    result = interpret([user(COMPLETE)])
    assert result.complete and result.question is None
    assert result.source == "offline"
    assert result.profile.risk_profile is RiskProfile.CONSERVADOR
    assert result.profile.lambda_base == 2.0
    assert result.missing == ()


def test_questions_follow_the_priority_order() -> None:
    conversation = [user("hola, quiero aprender a invertir")]
    assert interpret(conversation).question.field == FIELD_AMOUNT
    conversation += [asked(FIELD_AMOUNT), user("5000")]
    assert interpret(conversation).question.field == FIELD_HORIZON
    conversation += [asked(FIELD_HORIZON), user("unos 3 años")]
    assert interpret(conversation).question.field == FIELD_RISK
    conversation += [asked(FIELD_RISK), user("conservador")]
    assert interpret(conversation).question.field == FIELD_SAVINGS
    conversation += [asked(FIELD_SAVINGS), user("20 mil")]
    assert interpret(conversation).question.field == FIELD_EMERGENCY
    conversation += [asked(FIELD_EMERGENCY), user("4")]
    final = interpret(conversation)
    assert final.complete
    assert (final.profile.amount, final.profile.horizon_years, final.profile.emergency_months) == (5000, 3, 4)


def test_contradiction_asks_for_risk_with_options() -> None:
    result = interpret([user("Quiero invertir S/ 5000 por 3 años, quiero máxima ganancia pero no puedo perder nada")])
    assert result.question.field == FIELD_RISK
    assert len(result.question.options) == 5
    assert result.profile.risk_profile is None and result.contradictions


def test_latest_answer_resolves_a_contradiction() -> None:
    result = interpret([
        user("Quiero invertir S/ 5000 por 3 años, máxima ganancia pero no puedo perder nada"),
        asked(FIELD_RISK),
        user("moderado"),
    ])
    assert result.profile.risk_profile is RiskProfile.MODERADO
    assert result.contradictions == ()


def test_absorption_field_is_asked_once_then_assumed_media() -> None:
    base = [user("Quiero invertir S/ 5000 por 3 años, no me gusta arriesgar")]
    assert interpret(base).question.field == FIELD_SAVINGS
    after = interpret(base + [asked(FIELD_SAVINGS), user("no sé bien")])
    assert after.complete
    assert after.absorption_assumed
    assert after.assumptions == ("Como no indicaste tu ahorro total, asumimos una capacidad media para absorber pérdidas.",)


def test_refusal_assumes_media_without_asking_absorption() -> None:
    result = interpret([user("Quiero invertir S/ 5000 por 3 años, no me gusta arriesgar. Prefiero no decir cuánto tengo ahorrado")])
    assert result.complete and result.absorption_assumed
    assert result.rejected == (FIELD_SAVINGS,)


def test_golden_refusal_alone_still_asks_amount_and_declares_assumption() -> None:
    result = interpret([user("Prefiero no decir cuánto tengo ahorrado")])
    assert result.question.field == FIELD_AMOUNT
    assert result.assumptions


LLM_JSON = {
    "monto_invertir": 5000, "horizonte_anios": 3, "horizonte_etiqueta": None, "perfil_riesgo": "conservador",
    "ahorro_total": 20000, "cobertura_emergencia_meses": 4,
    "evidencia": {"monto_invertir": "S/ 5000", "horizonte": "unos 3 años", "perfil_riesgo": "no me gusta arriesgar",
                  "ahorro_total": "de mis S/ 20000", "cobertura_emergencia_meses": "4 meses de colchón"},
    "rechazos": [], "contradicciones": [],
}


def test_llm_extraction_is_used_at_temperature_zero() -> None:
    llm = FakeLLM(LLM_JSON)
    result = interpret([user(COMPLETE)], llm=llm)
    assert result.source == "llm" and result.prompt_version == "interpret.v2"
    assert result.complete and result.profile.lambda_base == 2.0
    assert llm.calls[0]["temperature"] == 0


def test_invalid_json_is_retried_once_then_falls_back_offline() -> None:
    llm = FakeLLM({"monto_invertir": "cinco mil"}, LanguageModelError("not JSON"), LLM_JSON)
    result = interpret([user(COMPLETE)], llm=llm)
    assert len(llm.calls) == 2
    assert result.source == "offline"
    assert result.complete and result.profile.amount == 5000
    assert len(result.errors) == 2


def test_llm_value_without_evidence_is_dropped_and_asked() -> None:
    data = dict(LLM_JSON, evidencia={k: v for k, v in LLM_JSON["evidencia"].items() if k != "monto_invertir"})
    llm = FakeLLM(data, {"pregunta": "¿Cuánto quieres invertir?", "ayuda": "Por ejemplo: S/ 3,000."})
    result = interpret([user(COMPLETE)], llm=llm)
    assert result.profile.amount is None
    assert result.question.field == FIELD_AMOUNT and result.question.text == "¿Cuánto quieres invertir?"


def test_llm_risk_label_is_mapped_by_code_not_by_the_model() -> None:
    data = dict(LLM_JSON, perfil_riesgo="muy_agresivo")
    result = interpret([user(COMPLETE)], llm=FakeLLM(data))
    assert result.profile.lambda_base == 0.2


def test_horizon_evidence_keyed_by_its_json_field_is_accepted() -> None:
    # Real Claude output keys horizon evidence as "horizonte_anios" instead of "horizonte".
    data = {**LLM_JSON, "evidencia": {**LLM_JSON["evidencia"]}}
    data["evidencia"]["horizonte_anios"] = data["evidencia"].pop("horizonte")
    result = interpret([user(COMPLETE)], llm=FakeLLM(data))
    assert result.source == "llm" and result.complete
    assert result.profile.horizon_years == 3
    assert result.evidence[FIELD_HORIZON] == "unos 3 años"
