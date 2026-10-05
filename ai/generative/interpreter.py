"""Interpretation stage: conversation -> structured profile or one clarification question.

The language model (or the offline extractor) only EXTRACTS fields. The code
decides completeness, which field to ask next, what is assumed and the
lambda_base of the risk label (``params.risk_profiles``, decision D5).

Field ids follow the interpretation schema (``monto_invertir``, ``horizonte``,
``perfil_riesgo``, ``ahorro_total``, ``cobertura_emergencia_meses``); assistant
turns carry the ``field`` they asked for, which is how the code knows that an
absorption field was already asked once.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ai.generative import offline
from ai.generative.offline import Extraction, Question
from ai.generative.port import LanguageModel, LanguageModelError
from ai.generative.prompts import load_prompt
from ai.generative.schema import (
    ABSORPTION_FIELDS,
    ALL_FIELDS,
    CLARIFY_SCHEMA,
    CRITICAL_FIELDS,
    FIELD_AMOUNT,
    FIELD_EMERGENCY,
    FIELD_HORIZON,
    FIELD_RISK,
    FIELD_SAVINGS,
    INTERPRET_SCHEMA,
    validate,
)
from ai.shared.parameters import Parameters, load_parameters
from ai.shared.types import HorizonLabel, RiskProfile

# v2 (W17): vague horizons ("en unos años") stay null so the system asks instead of assuming a long horizon.
INTERPRET_PROMPT_VERSION = 2

logger = logging.getLogger(__name__)

INTERPRET_TEMPERATURE, INTERPRET_MAX_TOKENS = 0.0, 500
CLARIFY_TEMPERATURE, CLARIFY_MAX_TOKENS = 0.3, 150
_FIELD_NAMES = {FIELD_SAVINGS: "tu ahorro total", FIELD_EMERGENCY: "cuántos meses de gastos puedes cubrir"}
_FIELD_ATTR = {
    FIELD_AMOUNT: "amount", FIELD_RISK: "risk_profile",
    FIELD_SAVINGS: "total_savings", FIELD_EMERGENCY: "emergency_months",
}
_JSON_KEYS = {
    "monto_invertir": "amount",
    "horizonte_anios": "horizon_years",
    "ahorro_total": "total_savings",
    "cobertura_emergencia_meses": "emergency_months",
}


@dataclass(frozen=True)
class InterpretedProfile:
    amount: float | None = None
    horizon_years: float | None = None
    horizon_label: HorizonLabel | None = None
    risk_profile: RiskProfile | None = None
    lambda_base: float | None = None
    total_savings: float | None = None
    emergency_months: float | None = None


@dataclass(frozen=True)
class InterpretationResult:
    profile: InterpretedProfile
    evidence: Mapping[str, str]
    missing: tuple[str, ...]
    question: Question | None
    complete: bool
    assumptions: tuple[str, ...]
    rejected: tuple[str, ...]
    contradictions: tuple[str, ...]
    source: str  # "llm" | "offline"
    prompt_version: str
    absorption_assumed: bool = False
    errors: tuple[str, ...] = field(default=())


def _has(extraction: Extraction, field_id: str) -> bool:
    if field_id == FIELD_HORIZON:
        return extraction.horizon_years is not None or extraction.horizon_label is not None
    return getattr(extraction, _FIELD_ATTR[field_id]) is not None


def _merge(turns: Sequence[Extraction]) -> Extraction:
    """Combine per-turn extractions in order: the latest value for each field wins."""
    merged = Extraction()
    for turn in turns:
        for attr in ("amount", "total_savings", "emergency_months", "risk_profile"):
            if getattr(turn, attr) is not None:
                setattr(merged, attr, getattr(turn, attr))
        if turn.horizon_years is not None or turn.horizon_label is not None:
            merged.horizon_years, merged.horizon_label = turn.horizon_years, turn.horizon_label
        merged.evidence.update(turn.evidence)
        touched = {f for f in ALL_FIELDS if _has(turn, f)} | {f for f, _ in turn.contradictions}
        merged.contradictions = [c for c in merged.contradictions if c[0] not in touched] + turn.contradictions
        merged.rejected = [f for f in merged.rejected if not _has(turn, f)]
        merged.rejected += [f for f in turn.rejected if f not in merged.rejected]
    merged.rejected = [f for f in merged.rejected if not _has(merged, f)]
    return merged


def _offline_extraction(conversation: Sequence[Mapping[str, Any]]) -> Extraction:
    turns, asked = [], None
    for turn in conversation:
        if turn.get("role") == "assistant":
            asked = turn.get("field")
            continue
        turns.append(offline.extract(str(turn.get("content", "")), asked))
        asked = None
    return _merge(turns)


def _from_llm_json(data: Mapping[str, Any]) -> Extraction:
    """Convert validated JSON; a non-null field without evidence is dropped (never assumed)."""
    # Models often key horizon evidence by the JSON field that carries the value.
    aliases = {"horizonte_anios": FIELD_HORIZON, "horizonte_etiqueta": FIELD_HORIZON}
    evidence: dict[str, str] = {}
    for key, text in (data.get("evidencia") or {}).items():
        field_id = aliases.get(key, key)
        if field_id in ALL_FIELDS and text and field_id not in evidence:
            evidence[field_id] = str(text)
    out = Extraction(evidence=evidence)
    for key, attr in _JSON_KEYS.items():
        value = data.get(key)
        # Amounts must be positive; a horizon or coverage of 0 is a valid answer.
        if value is not None and (value > 0 or (value == 0 and attr in ("horizon_years", "emergency_months"))):
            setattr(out, attr, float(value))
    if data.get("horizonte_etiqueta"):
        out.horizon_label = HorizonLabel(data["horizonte_etiqueta"])
    if data.get("perfil_riesgo"):
        out.risk_profile = RiskProfile(data["perfil_riesgo"])
    for field_id in ALL_FIELDS:
        if _has(out, field_id) and field_id not in evidence:
            if field_id == FIELD_HORIZON:
                out.horizon_years = out.horizon_label = None
            else:
                setattr(out, _FIELD_ATTR[field_id], None)
    out.evidence = {k: v for k, v in evidence.items() if _has(out, k)}
    out.rejected = [f for f in data.get("rechazos", []) if f in ALL_FIELDS and not _has(out, f)]
    # The schema has no field per contradiction: with a null risk label they are about risk,
    # otherwise they are informative only (e.g. a currency issue already left the amount null).
    tag = FIELD_RISK if out.risk_profile is None else ""
    out.contradictions = [(tag, str(text)) for text in data.get("contradicciones", [])]
    return out


def _llm_messages(conversation: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    return [{"role": str(t["role"]), "content": str(t.get("content", ""))} for t in conversation]


def _llm_extraction(conversation: Sequence[Mapping[str, Any]], llm: LanguageModel) -> tuple[Extraction | None, list[str]]:
    """Two attempts (one retry on invalid output); ``None`` means fall back to offline."""
    prompt = load_prompt("interpret", INTERPRET_PROMPT_VERSION)
    errors: list[str] = []
    for _ in range(2):
        try:
            data = llm.complete_json(
                prompt.text, _llm_messages(conversation), INTERPRET_SCHEMA,
                temperature=INTERPRET_TEMPERATURE, max_tokens=INTERPRET_MAX_TOKENS,
            )
        except LanguageModelError as exc:
            errors.append(f"provider: {exc}")
            continue
        problems = validate(data, INTERPRET_SCHEMA)
        if not problems:
            return _from_llm_json(data), errors
        errors.append("; ".join(problems))
    logger.warning("interpretation fell back to offline after %d invalid attempts", len(errors))
    return None, errors


def _llm_question(field_id: str, context: str, llm: LanguageModel) -> Question | None:
    template = offline.clarification_question(field_id)
    system = load_prompt("clarify").render(campo=field_id, contexto=context or "sin contexto")
    try:
        data = llm.complete_json(
            system, [{"role": "user", "content": context or field_id}], CLARIFY_SCHEMA,
            temperature=CLARIFY_TEMPERATURE, max_tokens=CLARIFY_MAX_TOKENS,
        )
    except LanguageModelError:
        return None
    if validate(data, CLARIFY_SCHEMA) or len(data["pregunta"]) > 300:
        return None
    return Question(field_id, data["pregunta"].strip(), data.get("ayuda") or template.hint, template.options, template.unit)


def _asked_fields(conversation: Sequence[Mapping[str, Any]]) -> set[str]:
    return {str(t["field"]) for t in conversation if t.get("role") == "assistant" and t.get("field")}


def interpret(
    conversation: Sequence[Mapping[str, Any]],
    llm: LanguageModel | None = None,
    params: Parameters | None = None,
) -> InterpretationResult:
    """Interpret the whole conversation (stateless): extract, then decide what is missing or assumed."""
    if not any(t.get("role") == "user" and str(t.get("content", "")).strip() for t in conversation):
        raise ValueError("conversation needs at least one non-empty user turn")
    params = params or load_parameters()

    extraction, errors, source, version = None, [], "offline", offline.OFFLINE_VERSION
    if llm is not None:
        extraction, errors = _llm_extraction(conversation, llm)
        if extraction is not None:
            source, version = "llm", load_prompt("interpret", INTERPRET_PROMPT_VERSION).version
    if extraction is None:
        extraction = _offline_extraction(conversation)

    asked = _asked_fields(conversation)
    contradiction_fields = {f for f, _ in extraction.contradictions}
    missing = tuple(f for f in ALL_FIELDS if not _has(extraction, f))
    pending_critical = [f for f in CRITICAL_FIELDS if f in missing or f in contradiction_fields]

    # Absorption fields are asked once each; a refusal or an unanswered question means "Media".
    absorption_missing = [f for f in ABSORPTION_FIELDS if f in missing]
    refused = [f for f in ABSORPTION_FIELDS if f in extraction.rejected]
    unanswered = [f for f in absorption_missing if f in asked]
    absorption_assumed = bool(refused or unanswered)
    assumptions: list[str] = []
    if absorption_assumed:
        reason = (refused or unanswered)[0]
        assumptions.append(
            f"Como no indicaste {_FIELD_NAMES[reason]}, asumimos una capacidad media para absorber pérdidas."
        )

    next_field = pending_critical[0] if pending_critical else None
    if next_field is None and not absorption_assumed:
        next_field = next((f for f in absorption_missing if f not in asked), None)

    question = None
    if next_field is not None:
        context = "; ".join(t for f, t in extraction.contradictions if f == next_field)
        question = (_llm_question(next_field, context, llm) if llm is not None else None) or (
            offline.clarification_question(next_field)
        )

    risk = extraction.risk_profile if FIELD_RISK not in contradiction_fields else None
    profile = InterpretedProfile(
        amount=extraction.amount,
        horizon_years=extraction.horizon_years,
        horizon_label=extraction.horizon_label,
        risk_profile=risk,
        lambda_base=None if risk is None else float(params.risk_profiles.lambda_base[risk]),
        total_savings=extraction.total_savings,
        emergency_months=extraction.emergency_months,
    )
    return InterpretationResult(
        profile=profile,
        evidence=dict(extraction.evidence),
        missing=missing,
        question=question,
        complete=question is None,
        assumptions=tuple(assumptions),
        rejected=tuple(extraction.rejected),
        contradictions=tuple(t for _, t in extraction.contradictions),
        source=source,
        prompt_version=version,
        absorption_assumed=absorption_assumed,
        errors=tuple(errors),
    )
