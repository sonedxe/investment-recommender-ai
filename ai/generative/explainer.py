"""Explanation stage: computed result -> plain-language Spanish text with number validation.

The code builds the input (allocation, scenarios, fuzzy effects as phrases,
assumptions and the list of allowed numbers). The language model only writes;
every number in its text must be one of ``allowed_numbers`` (within rounding
tolerance), otherwise it is retried once with the error and then replaced by
the deterministic template. The educational disclaimer is added by the UI.

Scenarios (gain or loss over one year, in soles):

    bad    = amount * (E - 1.65 * sigma)
    normal = amount * E
    good   = amount * (E + 1.65 * sigma)

1.65 is about the one-sided 5 % quantile of a normal distribution; using it on
annual returns is an educational simplification, not a forecast.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ai.generative import offline
from ai.generative.offline import OFFLINE_VERSION, try_parse_number
from ai.generative.port import LanguageModel, LanguageModelError
from ai.generative.prompts import load_prompt
from ai.generative.schema import EXPLAIN_SCHEMA, validate
from ai.shared.types import CategoryId

logger = logging.getLogger(__name__)

SCENARIO_Z = 1.65
EXPLAIN_TEMPERATURE, EXPLAIN_MAX_TOKENS = 0.3, 1200
SCENARIO_NAMES = ("año malo", "año normal", "año bueno")

CATEGORY_DESCRIPTIONS: Mapping[CategoryId, str] = {
    CategoryId.STOCKS: "inversiones en empresas con más potencial de ganancia y más variabilidad",
    CategoryId.MIXED: "fondos que combinan acciones y deuda para equilibrar ganancia y estabilidad",
    CategoryId.DEBT: "fondos que prestan dinero a empresas o al Estado y suelen moverse poco",
    CategoryId.BONDS: "préstamos al Estado peruano que pagan un interés conocido",
    CategoryId.TERM: "dinero que dejas fijo en un banco por un plazo a cambio de un interés pactado",
}
_RISK_PHRASES = {
    "muy_conservador": "no perder dinero",
    "conservador": "ir a lo seguro",
    "moderado": "aceptar algo de variación",
    "agresivo": "aceptar variación para ganar más",
    "muy_agresivo": "buscar la mayor ganancia posible",
}


@dataclass(frozen=True)
class AllocationLine:
    category: CategoryId
    name: str
    description: str
    weight: float
    amount: float


@dataclass(frozen=True)
class Scenario:
    name: str
    amount: float


@dataclass(frozen=True)
class ExplanationInput:
    amount: float
    allocation: tuple[AllocationLine, ...]
    scenarios: tuple[Scenario, Scenario, Scenario]
    risk_profile: str
    horizon_years: float | None
    horizon_label: str | None
    horizon_effect: str
    absorption_effect: str
    assumptions: tuple[str, ...]
    allowed_numbers: tuple[float, ...]

    def to_payload(self) -> dict[str, Any]:
        """JSON sent to the model, with the Spanish keys of the explanation prompt."""
        return {
            "monto_total": self.amount,
            "portafolio": [
                {"categoria": a.name, "descripcion": a.description, "peso": round(a.weight, 4), "monto": a.amount}
                for a in self.allocation
            ],
            "escenarios": [{"nombre": s.name, "monto": s.amount} for s in self.scenarios],
            "perfil": {
                "perfil_riesgo": self.risk_profile,
                "horizonte_anios": self.horizon_years,
                "horizonte_etiqueta": self.horizon_label,
            },
            "efectos_difusos": {"horizonte": self.horizon_effect, "absorcion": self.absorption_effect},
            "supuestos": list(self.assumptions),
            "cifras_permitidas": list(self.allowed_numbers),
        }


@dataclass(frozen=True)
class ScenarioText:
    label: str
    text: str
    amount: float


@dataclass(frozen=True)
class ExplanationValidation:
    passed: bool
    attempts: int
    errors: tuple[str, ...] = field(default=())
    fallback: bool = False


@dataclass(frozen=True)
class ExplanationResult:
    summary: str
    paragraphs: tuple[str, ...]
    scenarios: tuple[ScenarioText, ...]
    assumptions: tuple[str, ...]
    source: str  # "llm" | "offline"
    prompt_version: str
    validation: ExplanationValidation


def compute_scenarios(amount: float, expected_return: float, sigma: float) -> tuple[Scenario, Scenario, Scenario]:
    """Bad, normal and good year gains in soles, rounded to cents."""
    returns = (expected_return - SCENARIO_Z * sigma, expected_return, expected_return + SCENARIO_Z * sigma)
    return tuple(Scenario(name, round(amount * r, 2)) for name, r in zip(SCENARIO_NAMES, returns))  # type: ignore[return-value]


def describe_horizon(m_h: float | None) -> str:
    """Plain-language effect of the horizon multiplier m_H (``None`` = adjustment disabled)."""
    if m_h is None:
        return "no se aplicó el ajuste por plazo, así que se usó tu nivel de cautela tal cual"
    if m_h > 1.05:
        return "el sistema fue más cauteloso porque el plazo es corto"
    if m_h < 0.95:
        return "el sistema aceptó un poco más de variación porque tienes tiempo para recuperarte"
    return "el sistema mantuvo tu nivel de cautela"


def describe_absorption(level: float | None, assumed: bool) -> str:
    """Plain-language effect of the absorption capacity (``level`` in [0, 1], ``None`` = disabled)."""
    if level is None:
        return "no se tomó en cuenta en este cálculo"
    if assumed:
        return "media, porque faltaban datos; por eso se aceptó una variación moderada"
    if level < 0.4:
        return "baja; por eso se limitó cuánto puede variar el portafolio"
    if level > 0.65:
        return "alta; por eso se aceptó más variación a cambio de más ganancia esperada"
    return "media; por eso se aceptó una variación moderada"


_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


def _allowed(values: Sequence[float]) -> tuple[float, ...]:
    return tuple(sorted({round(abs(v), 2) for v in values}))


def build_explanation_input(
    *,
    amount: float,
    allocation: Sequence[tuple[CategoryId, str, float, float]],
    expected_return: float,
    sigma: float,
    risk_profile: str,
    horizon_years: float | None = None,
    horizon_label: str | None = None,
    m_h: float | None = None,
    absorption_level: float | None = None,
    absorption_assumed: bool = False,
    assumptions: Sequence[str] = (),
) -> ExplanationInput:
    """Assemble the explanation input; ``allocation`` rows are ``(category, name, weight, amount)``."""
    lines = tuple(
        AllocationLine(cat, name, CATEGORY_DESCRIPTIONS[cat], float(w), round(float(a), 2))
        for cat, name, w, a in allocation
    )
    scenarios = compute_scenarios(amount, expected_return, sigma)
    numbers: list[float] = [amount]
    for line in lines:
        numbers += [line.amount, round(line.weight * 100, 1), line.weight * 100]
    numbers += [s.amount for s in scenarios]
    if horizon_years is not None:
        numbers.append(horizon_years)
    for text in assumptions:
        parsed = (try_parse_number(n) for n in _NUMBER.findall(text))
        numbers += [v for v in parsed if v is not None]
    return ExplanationInput(
        amount=round(amount, 2),
        allocation=lines,
        scenarios=scenarios,
        risk_profile=risk_profile,
        horizon_years=horizon_years,
        horizon_label=horizon_label,
        horizon_effect=describe_horizon(m_h),
        absorption_effect=describe_absorption(absorption_level, absorption_assumed),
        assumptions=tuple(assumptions),
        allowed_numbers=_allowed(numbers),
    )


def _number_candidates(raw: str) -> tuple[list[float], int]:
    """Possible values of a written number and its decimals (``1.250`` may be 1250 or 1.25).

    A malformed number (e.g. a dotted date) yields no candidates, so it is reported as
    invalid and handled by the retry/template path instead of raising.
    """
    parsed = try_parse_number(raw)
    candidates = set() if parsed is None else {parsed}
    if re.fullmatch(r"\d+[.,]\d+", raw):
        candidates.add(float(raw.replace(",", ".")))
    decimals = len(re.split(r"[.,]", raw)[-1]) if re.search(r"[.,]\d{1,2}$", raw) else 0
    return sorted(candidates), decimals


def find_invalid_numbers(text: str, allowed: Sequence[float]) -> list[str]:
    """Numbers in ``text`` that do not match any allowed number within rounding tolerance."""
    invalid = []
    for raw in _NUMBER.findall(text):
        candidates, decimals = _number_candidates(raw)
        tolerance = max(0.01, 0.5 * 10 ** (-decimals) + 1e-9)
        if not any(abs(c - a) <= tolerance for c in candidates for a in allowed):
            invalid.append(raw)
    return invalid


_MONEY_OK = re.compile(r"S/ \d{1,3}(?:,\d{3})*\.\d{2}(?!\d)")
_PERCENT = re.compile(r"\d+(?:[.,]\d+)?\s?%")


def validate_explanation(data: Mapping[str, Any], explanation_input: ExplanationInput) -> list[str]:
    """Schema, allowed numbers, money format, percent-with-amount and assumption checks."""
    errors = validate(data, EXPLAIN_SCHEMA)
    if errors:
        return errors
    texts = [data["resumen"], *data["parrafos"], *(s["label"] + " " + s["text"] for s in data["escenarios"])]
    texts += data["supuestos"]
    allowed = explanation_input.allowed_numbers
    for text in texts:
        # Assumptions are given input: quoting one verbatim may repeat its own numbers.
        scanned = text
        for assumption in explanation_input.assumptions:
            scanned = scanned.replace(assumption, "")
        bad = find_invalid_numbers(scanned, allowed)
        if bad:
            errors.append(f"cifras no permitidas: {', '.join(bad)} en «{text[:80]}»")
        if text.count("S/") != len(_MONEY_OK.findall(text)):
            errors.append(f"formato de moneda incorrecto en «{text[:80]}» (usa S/ 1,250.00)")
        for sentence in re.split(r"(?<=[.;:!?])\s+", text):
            if _PERCENT.search(sentence) and "S/" not in sentence:
                errors.append(f"porcentaje sin monto en soles en «{sentence[:80]}»")
    for given, expected in zip(data["escenarios"], explanation_input.scenarios):
        if abs(float(given["amount"]) - expected.amount) > 0.01:
            errors.append(f"monto de escenario alterado: {given['amount']} en lugar de {expected.amount}")
    if len(data["supuestos"]) < len(explanation_input.assumptions):
        errors.append("faltan supuestos: declara cada supuesto recibido")
    return errors


def _to_result(data: Mapping[str, Any], explanation_input: ExplanationInput, source: str, version: str,
               validation: ExplanationValidation) -> ExplanationResult:
    return ExplanationResult(
        summary=data["resumen"].strip(),
        paragraphs=tuple(p.strip() for p in data["parrafos"]),
        scenarios=tuple(
            ScenarioText(s["label"].strip(), s["text"].strip(), expected.amount)
            for s, expected in zip(data["escenarios"], explanation_input.scenarios)
        ),
        assumptions=tuple(a.strip() for a in data["supuestos"]),
        source=source,
        prompt_version=version,
        validation=validation,
    )


def explain(explanation_input: ExplanationInput, llm: LanguageModel | None = None) -> ExplanationResult:
    """Write the explanation with the model (validated, one retry) or with the template."""
    errors: list[str] = []
    attempts = 0
    if llm is not None:
        prompt = load_prompt("explain")
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": json.dumps(explanation_input.to_payload(), ensure_ascii=False)}
        ]
        for _ in range(2):
            attempts += 1
            try:
                data = llm.complete_json(
                    prompt.text, messages, EXPLAIN_SCHEMA,
                    temperature=EXPLAIN_TEMPERATURE, max_tokens=EXPLAIN_MAX_TOKENS,
                )
            except LanguageModelError as exc:
                errors.append(f"provider: {exc}")
                continue
            problems = validate_explanation(data, explanation_input)
            if not problems:
                validation = ExplanationValidation(True, attempts, tuple(errors))
                return _to_result(data, explanation_input, "llm", prompt.version, validation)
            errors.extend(problems)
            messages = messages + [
                {"role": "assistant", "content": json.dumps(data, ensure_ascii=False)},
                {"role": "user", "content": "Corrige estos errores y responde de nuevo: " + " | ".join(problems)},
            ]
        logger.warning("explanation fell back to the template: %s", errors)

    data = offline.template_explanation(explanation_input)
    own_errors = validate_explanation(data, explanation_input)
    if own_errors:  # Built from allowed numbers only; reported instead of hidden if it ever regresses.
        logger.error("template explanation failed its own validation: %s", own_errors)
    validation = ExplanationValidation(not own_errors, attempts, tuple(errors + own_errors), fallback=llm is not None)
    return _to_result(data, explanation_input, "offline", OFFLINE_VERSION, validation)
