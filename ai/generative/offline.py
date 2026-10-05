"""Deterministic fallbacks used when no language model is configured or it fails.

- ``extract``: rule-based Spanish extractor (regular expressions and keywords)
  that fills the same fields as the interpretation prompt, with the matched
  substring as evidence.
- ``clarification_question``: template question per missing field.
- ``template_explanation``: explanation built only from computed numbers; it
  passes the same validator as the language-model output.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ai.generative.formatting import format_money, format_number, format_percent
from ai.generative.schema import (
    FIELD_AMOUNT,
    FIELD_EMERGENCY,
    FIELD_HORIZON,
    FIELD_RISK,
    FIELD_SAVINGS,
)
from ai.shared.types import HorizonLabel, RiskProfile

if TYPE_CHECKING:
    from ai.generative.explainer import ExplanationInput

OFFLINE_VERSION = "offline.v1"

# ---------------------------------------------------------------- extraction

_FOLD = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunaeiouun")
NUM = r"\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?(?!\d)|\d+(?:[.,]\d+)?"
_WORDS = {
    "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
    "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12, "quince": 15,
    "veinte": 20, "medio": 0.5,
}
WORD_NUM = "|".join(sorted(_WORDS, key=len, reverse=True))

# Spelled-out amounts ("cinco mil", "mil quinientos", "treinta y cinco mil", "un millon").
_UNITS = {
    "un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
    "siete": 7, "ocho": 8, "nueve": 9,
}
_SPELLED_VALUES = {
    **_UNITS,
    "diez": 10, "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
    "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
    "veinte": 20, "veintiun": 21, "veintiuno": 21, "veintiuna": 21, "veintidos": 22, "veintitres": 23,
    "veinticuatro": 24, "veinticinco": 25, "veintiseis": 26, "veintisiete": 27, "veintiocho": 28,
    "veintinueve": 29, "treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70,
    "ochenta": 80, "noventa": 90, "cien": 100, "ciento": 100, "doscientos": 200, "doscientas": 200,
    "trescientos": 300, "trescientas": 300, "cuatrocientos": 400, "cuatrocientas": 400,
    "quinientos": 500, "quinientas": 500, "seiscientos": 600, "seiscientas": 600,
    "setecientos": 700, "setecientas": 700, "ochocientos": 800, "ochocientas": 800,
    "novecientos": 900, "novecientas": 900,
}
_SCALES = {"mil": 1_000, "millon": 1_000_000, "millones": 1_000_000}
_SPELLED_WORD = "|".join(sorted([*_SPELLED_VALUES, *_SCALES], key=len, reverse=True))
_UNIT_WORD = "|".join(sorted(_UNITS, key=len, reverse=True))
_TENS_WORD = "treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa"
# One token is a number word or "tens y unit" ("treinta y cinco"); "y" never joins
# other words, so "cinco mil y tres anos" stops at "mil".
_SPELLED_TOKEN = rf"(?:(?:{_TENS_WORD})\s+y\s+(?:{_UNIT_WORD})|{_SPELLED_WORD})"
SPELLED = rf"\b{_SPELLED_TOKEN}(?:\s+{_SPELLED_TOKEN}\b)*\b"
_QTY = rf"(?P<n>{NUM}|\b(?:{WORD_NUM})\b)"
_APPROX = r"(?:(?:unos|unas|como|aproximadamente|mas o menos|alrededor de)\s+)?"
_EMERGENCY_CUE = r"(?:de\s+)?(?:colchon|gastos|emergencia|ahorros?|reserva)"

_EMERGENCY_PATTERNS = (
    re.compile(rf"{_APPROX}{_QTY}\s*meses\s*{_EMERGENCY_CUE}"),
    re.compile(rf"(?:colchon|reserva|fondo de emergencia)\s+(?:de|para|que cubre|para cubrir)\s+{_APPROX}{_QTY}\s*meses"),
    re.compile(rf"cubrir\s+(?:mis\s+gastos\s+)?(?:por\s+)?{_APPROX}{_QTY}\s*meses"),
)
_YEARS = re.compile(rf"{_APPROX}{_QTY}\s*(?P<unit>anos?|anios?)\b(?P<half>\s+y\s+medio)?")
_HALF_YEAR = re.compile(r"\bmedio\s+ano\b")
_MONTHS_HORIZON = re.compile(rf"(?:en|dentro de|por)\s+{_APPROX}{_QTY}\s*meses\b(?!\s*{_EMERGENCY_CUE})")
_AGE_BEFORE = re.compile(r"(?:tengo|cumplo|cumpli)\s+(?:ya\s+)?$")
_AGE_AFTER = re.compile(r"^\s*(?:de edad|recien cumplidos)")

_HORIZON_LABELS = (
    (HorizonLabel.CORTO, re.compile(r"corto plazo|\bpronto\b|poco tiempo|en breve")),
    (HorizonLabel.MEDIANO, re.compile(r"mediano plazo|plazo medio")),
    (HorizonLabel.LARGO, re.compile(r"largo plazo|muchos anos|mucho tiempo|jubilacion|\bretiro\b")),
)

_MONEY = re.compile(
    rf"(?P<cur>s/\.?|us\$|\$)?\s*(?P<num>{NUM}|{SPELLED})(?P<mil>\s*(?:mil|k)\b)?"
    r"(?:\s*(?P<unit>soles|sol|dolares|dolar|usd)\b)?"
)
_AMOUNT_CUE = re.compile(r"invert\w*|\bmonto\b|\bpongo\b|\bponer\b|\bdestinar\b|\bmeter\b|\bmeto\b")
_SAVINGS_CUE = re.compile(r"de mis|de mi\b|ahorrad\w*|ahorros?|guardad\w*|en total")
_SAVINGS_AFTER = re.compile(r"^\s*(?:de ahorros?|ahorrad\w*|en total|guardad\w*)")

_RISK_PATTERNS: tuple[tuple[RiskProfile, str], ...] = (
    (RiskProfile.MUY_CONSERVADOR, r"no (?:quiero|puedo) perder (?:nada|ni un sol)"),
    (RiskProfile.MUY_CONSERVADOR, r"nada de riesgo|cero riesgo|sin (?:ningun )?riesgo"),
    (RiskProfile.MUY_CONSERVADOR, r"muy[ _]conservador"),
    (RiskProfile.CONSERVADOR, r"no me gusta (?:arriesgar|el riesgo)|poco riesgo|sin arriesgar(?: mucho)?"),
    (RiskProfile.CONSERVADOR, r"nada muy arriesgado|no (?:quiero )?arriesgar mucho|prefiero (?:ir a )?(?:lo )?seguro"),
    (RiskProfile.CONSERVADOR, r"\bconservador"),
    (RiskProfile.MODERADO, r"algo de riesgo|un poco de riesgo|riesgo moderado|\bmoderad[oa]|equilibr\w*"),
    (RiskProfile.MODERADO, r"ni mucho ni poco|lo aceptaria"),
    (RiskProfile.AGRESIVO, r"acepto (?:el |mas )?riesgo|acepto bajas|(?:puedo|me animo a) arriesgar"),
    (RiskProfile.AGRESIVO, r"ganar mas|\bagresivo"),
    (RiskProfile.MUY_AGRESIVO, r"maxim[ao] (?:ganancia|rentabilidad|retorno)|lo maximo posible"),
    (RiskProfile.MUY_AGRESIVO, r"aguanto (?:las )?perdidas|todo el riesgo|muy[ _]agresivo"),
)
_RISK_COMPILED = tuple((label, re.compile(p)) for label, p in _RISK_PATTERNS)
_NEGATION_BEFORE = re.compile(r"\bno\s+$")
_SCALE = tuple(RiskProfile)  # muy_agresivo ... muy_conservador

_REFUSAL = re.compile(
    r"prefiero no (?:decir\w*|responder|contestar|dar\w*|compartir\w*)|"
    r"no (?:quiero|voy a|deseo) (?:decir\w*|responder|contestar|dar\w*|compartir\w*)|no te (?:lo )?(?:voy a )?decir"
)
_REFUSAL_TOPICS = (
    (FIELD_EMERGENCY, re.compile(r"colchon|emergencia|meses|gastos")),
    (FIELD_SAVINGS, re.compile(r"ahorr|guardad|en total")),
    (FIELD_AMOUNT, re.compile(r"invert|monto")),
    (FIELD_HORIZON, re.compile(r"tiempo|plazo|anos")),
    (FIELD_RISK, re.compile(r"riesgo|arriesg")),
)


@dataclass
class Extraction:
    """Fields found in one text (``None`` when not said) with evidence per field id."""

    amount: float | None = None
    horizon_years: float | None = None
    horizon_label: HorizonLabel | None = None
    risk_profile: RiskProfile | None = None
    total_savings: float | None = None
    emergency_months: float | None = None
    evidence: dict[str, str] = field(default_factory=dict)
    rejected: list[str] = field(default_factory=list)
    contradictions: list[tuple[str, str]] = field(default_factory=list)  # (field id, text)


def fold(text: str) -> str:
    """Lowercase and strip Spanish accents keeping the length (evidence slices the original)."""
    folded = text.lower().translate(_FOLD)
    return folded if len(folded) == len(text) else text.translate(_FOLD).lower()


def _parse_spelled(raw: str) -> float | None:
    """Value of a phrase of Spanish number words, or None when a token is not one."""
    tokens = [token for token in fold(raw).split() if token != "y"]
    if not tokens or any(token not in _SPELLED_VALUES and token not in _SCALES for token in tokens):
        return None
    total = current = 0
    for token in tokens:
        if token in _SCALES:
            scale = _SCALES[token]
            if scale == 1_000:
                total += (current or 1) * scale
            else:
                total = (total + (current or 1)) * scale
            current = 0
        else:
            current += _SPELLED_VALUES[token]
    return float(total + current)


def is_spelled_amount(raw: str) -> bool:
    """True for a spelled phrase that carries a scale word ("cinco mil", "un millon")."""
    return _parse_spelled(raw) is not None and any(token in _SCALES for token in fold(raw).split())


def parse_number(raw: str) -> float:
    """Parse ``5000``, ``5,000``, ``20.000``, ``1,250.50``, ``12,5`` or Spanish number words
    (``cinco``, ``mil quinientos``, ``treinta y cinco mil``)."""
    raw = raw.strip()
    if raw in _WORDS:
        return float(_WORDS[raw])
    spelled = _parse_spelled(raw)
    if spelled is not None:
        return spelled
    match = re.fullmatch(r"(\d{1,3}(?:[.,]\d{3})+)(?:[.,](\d{1,2}))?", raw)
    if match:
        integer = re.sub(r"[.,]", "", match.group(1))
        return float(integer + (f".{match.group(2)}" if match.group(2) else ""))
    return float(raw.replace(",", "."))


def try_parse_number(raw: str) -> float | None:
    """``parse_number`` that returns None for malformed numbers (``04.10.2026``, ``1,2,3``)."""
    try:
        return parse_number(raw)
    except ValueError:
        return None


def _overlaps(span: tuple[int, int], taken: list[tuple[int, int]]) -> bool:
    return any(span[0] < end and start < span[1] for start, end in taken)


def _emergency(text: str, folded: str, out: Extraction, taken: list[tuple[int, int]]) -> None:
    for pattern in _EMERGENCY_PATTERNS:
        match = pattern.search(folded)
        if match and not _overlaps(match.span(), taken):
            out.emergency_months = parse_number(match.group("n"))
            out.evidence[FIELD_EMERGENCY] = text[match.start():match.end()].strip()
            taken.append(match.span())
            return


def _horizon(text: str, folded: str, out: Extraction, taken: list[tuple[int, int]]) -> None:
    for match in _YEARS.finditer(folded):
        if _overlaps(match.span(), taken) or _AGE_BEFORE.search(folded[max(0, match.start() - 12):match.start()]):
            continue
        if _AGE_AFTER.match(folded[match.end():]):
            continue
        out.horizon_years = parse_number(match.group("n")) + (0.5 if match.group("half") else 0.0)
        out.evidence[FIELD_HORIZON] = text[match.start():match.end()].strip()
        taken.append(match.span())
        return
    for pattern, scale in ((_HALF_YEAR, None), (_MONTHS_HORIZON, 12.0)):
        match = pattern.search(folded)
        if match and not _overlaps(match.span(), taken):
            out.horizon_years = 0.5 if scale is None else round(parse_number(match.group("n")) / scale, 2)
            out.evidence[FIELD_HORIZON] = text[match.start():match.end()].strip()
            taken.append(match.span())
            return
    for label, pattern in _HORIZON_LABELS:
        match = pattern.search(folded)
        if match:
            out.horizon_label = label
            out.evidence[FIELD_HORIZON] = text[match.start():match.end()]
            return


def _money(text: str, folded: str, out: Extraction, taken: list[tuple[int, int]], asked: str | None) -> None:
    candidates = []  # (kind, value, span, is_dollar)
    previous_end = 0
    for match in _MONEY.finditer(folded):
        if _overlaps(match.span(), taken):
            continue
        cur, unit, mil = match.group("cur"), match.group("unit"), match.group("mil")
        spelled = not match.group("num")[0].isdigit()
        if spelled and not (cur or unit or is_spelled_amount(match.group("num"))):
            continue  # "una parte", "dos fondos": small words are money only with a scale or currency
        window = folded[max(previous_end, match.start() - 35):match.start()]
        previous_end = match.end()
        amount_cue = max((m.end() for m in _AMOUNT_CUE.finditer(window)), default=-1)
        savings_cue = max((m.end() for m in _SAVINGS_CUE.finditer(window)), default=-1)
        if _SAVINGS_AFTER.match(folded[match.end():]):
            savings_cue = len(window) + 1
        is_money = bool(cur or unit or mil) or amount_cue >= 0 or savings_cue >= 0
        if not is_money:
            continue
        kind = None
        if amount_cue >= 0 or savings_cue >= 0:
            kind = FIELD_AMOUNT if amount_cue > savings_cue else FIELD_SAVINGS
        value = parse_number(match.group("num")) * (1000 if mil else 1)
        is_dollar = (cur or "").endswith("$") or (unit or "") in ("dolares", "dolar", "usd")
        span = (match.start("cur") if cur else match.start("num"), match.end())
        candidates.append((kind, value, span, is_dollar))

    cued = {kind for kind, *_ in candidates if kind}
    resolved = []
    for kind, value, span, is_dollar in candidates:
        if kind is None:
            kind = asked if asked in (FIELD_AMOUNT, FIELD_SAVINGS) else None
            if kind is None:
                kind = FIELD_SAVINGS if FIELD_AMOUNT in cued else FIELD_AMOUNT
        resolved.append((kind, value, span, is_dollar))
    for kind, value, span, is_dollar in resolved:
        attr = "amount" if kind == FIELD_AMOUNT else "total_savings"
        if getattr(out, attr) is not None or kind in out.evidence:
            continue
        evidence = text[span[0]:span[1]].strip()
        taken.append(span)
        if is_dollar:
            out.evidence[kind] = evidence
            out.contradictions.append((kind, f'El monto "{evidence}" no está en soles.'))
            continue
        setattr(out, attr, value)
        out.evidence[kind] = evidence
    # Drop evidence kept only for dollar contradictions.
    for kind in (FIELD_AMOUNT, FIELD_SAVINGS):
        attr = "amount" if kind == FIELD_AMOUNT else "total_savings"
        if getattr(out, attr) is None:
            out.evidence.pop(kind, None)


def _risk(text: str, folded: str, out: Extraction) -> None:
    hits = []
    for label, pattern in _RISK_COMPILED:
        for match in pattern.finditer(folded):
            if label in (RiskProfile.AGRESIVO, RiskProfile.MUY_AGRESIVO, RiskProfile.MODERADO):
                if _NEGATION_BEFORE.search(folded[max(0, match.start() - 4):match.start()]):
                    continue
            hits.append((match.start(), match.end(), label))
    hits.sort(key=lambda h: (-(h[1] - h[0]), h[0]))
    kept: list[tuple[int, int, RiskProfile]] = []
    for hit in hits:
        if not _overlaps((hit[0], hit[1]), [(s, e) for s, e, _ in kept]):
            kept.append(hit)
    if not kept:
        return
    kept.sort()
    positions = [_SCALE.index(label) for *_, label in kept]
    if max(positions) - min(positions) >= 2:
        first = min(kept, key=lambda h: _SCALE.index(h[2]))
        last = max(kept, key=lambda h: _SCALE.index(h[2]))
        a, b = sorted((first, last))
        out.contradictions.append(
            (FIELD_RISK, f'Señales opuestas sobre el riesgo: "{text[a[0]:a[1]]}" y "{text[b[0]:b[1]]}".')
        )
        return
    start, end, label = max(kept, key=lambda h: abs(_SCALE.index(h[2]) - 2))
    out.risk_profile = label
    out.evidence[FIELD_RISK] = text[start:end]


def _refusals(folded: str, out: Extraction, asked: str | None) -> None:
    for match in _REFUSAL.finditer(folded):
        sentence_start = max(folded.rfind(c, 0, match.start()) for c in ".;!?\n") + 1
        ends = [i for i in (folded.find(c, match.end()) for c in ".;!?\n") if i >= 0]
        sentence = folded[sentence_start:min(ends) if ends else len(folded)]
        topic = next((f for f, pattern in _REFUSAL_TOPICS if pattern.search(sentence)), asked)
        if topic and topic not in out.rejected:
            out.rejected.append(topic)


def _asked_fallback(text: str, folded: str, out: Extraction, taken: list[tuple[int, int]], asked: str | None) -> None:
    """A bare number answering the last question belongs to the asked field."""
    targets = {
        FIELD_AMOUNT: "amount", FIELD_SAVINGS: "total_savings",
        FIELD_HORIZON: "horizon_years", FIELD_EMERGENCY: "emergency_months",
    }
    attr = targets.get(asked or "")
    if attr is None or getattr(out, attr) is not None or asked in out.rejected:
        return
    if asked == FIELD_HORIZON and out.horizon_label is not None:
        return
    pattern = re.compile(rf"(?P<n>{NUM}|{SPELLED}|\b(?:{WORD_NUM})\b)(?P<mil>\s*(?:mil|k)\b)?")
    for match in pattern.finditer(folded):
        if _overlaps(match.span(), taken):
            continue
        setattr(out, attr, parse_number(match.group("n")) * (1000 if match.group("mil") else 1))
        out.evidence[asked] = text[match.start():match.end()].strip()
        return


def extract(text: str, asked: str | None = None) -> Extraction:
    """Extract every field from one user message; ``asked`` is the field the last question asked for."""
    folded = fold(text)
    out = Extraction()
    taken: list[tuple[int, int]] = []
    _emergency(text, folded, out, taken)
    _horizon(text, folded, out, taken)
    _money(text, folded, out, taken, asked)
    _risk(text, folded, out)
    _refusals(folded, out, asked)
    _asked_fallback(text, folded, out, taken, asked)
    return out


# ------------------------------------------------------------ clarification


@dataclass(frozen=True)
class QuestionOption:
    value: str
    label: str


@dataclass(frozen=True)
class Question:
    """Question for one missing field: either closed ``options`` or a free numeric ``unit``."""

    field: str
    text: str
    hint: str | None
    options: tuple[QuestionOption, ...] | None = None
    unit: str | None = None

    @property
    def free_input(self) -> bool:
        return self.options is None


RISK_OPTIONS: tuple[QuestionOption, ...] = (
    QuestionOption(RiskProfile.MUY_CONSERVADOR.value, "Muy mal: no quiero perder nada"),
    QuestionOption(RiskProfile.CONSERVADOR.value, "Incómodo: prefiero ir a lo seguro"),
    QuestionOption(RiskProfile.MODERADO.value, "Lo aceptaría si luego se recupera"),
    QuestionOption(RiskProfile.AGRESIVO.value, "Tranquilo: acepto bajas para ganar más"),
    QuestionOption(RiskProfile.MUY_AGRESIVO.value, "Bien: busco la máxima ganancia y aguanto pérdidas"),
)

_TEMPLATES: dict[str, tuple[str, str, str | None]] = {
    FIELD_AMOUNT: ("¿Cuánto dinero quieres invertir, en soles?", "Por ejemplo: S/ 3,000.", "soles"),
    FIELD_HORIZON: (
        "¿Por cuánto tiempo aproximadamente no necesitarías este dinero?",
        "Por ejemplo: 3 años, o «a largo plazo».",
        "años",
    ),
    FIELD_RISK: ("Si en un año malo tu inversión bajara un 10 %, ¿cómo te sentirías?", "Elige la opción más cercana.", None),
    FIELD_SAVINGS: (
        "Contando este monto, ¿cuánto tienes ahorrado en total?",
        "Por ejemplo: S/ 20,000. Si prefieres no decirlo, escribe «prefiero no decir».",
        "soles",
    ),
    FIELD_EMERGENCY: (
        "Si dejaras de recibir ingresos, ¿cuántos meses podrías cubrir tus gastos con tus ahorros?",
        "Por ejemplo: 4 meses. Si prefieres no decirlo, escribe «prefiero no decir».",
        "meses",
    ),
}


def clarification_question(field_id: str) -> Question:
    """Template question for ``field_id`` (one of the five interpretation fields)."""
    text, hint, unit = _TEMPLATES[field_id]
    if field_id == FIELD_RISK:
        return Question(field_id, text, hint, options=RISK_OPTIONS)
    return Question(field_id, text, hint, unit=unit)


# --------------------------------------------------------------- explanation

_SCENARIO_LABELS = ("En un año malo", "En un año normal", "En un año bueno")


def _scenario_clause(amount: float) -> str:
    if round(amount, 2) < 0:
        return f"podrías perder {format_money(abs(amount))}"
    return f"podrías ganar {format_money(amount)}"


def _scenario_text(amount: float) -> str:
    clause = _scenario_clause(amount)
    return f"{clause[0].upper()}{clause[1:]}."


def _horizon_phrase(data: ExplanationInput) -> str:
    if data.horizon_years is not None:
        unit = "año" if data.horizon_years == 1 else "años"
        return f"unos {format_number(data.horizon_years)} {unit}"
    return {"corto": "poco tiempo", "mediano": "un tiempo intermedio", "largo": "mucho tiempo"}.get(
        data.horizon_label or "", "el tiempo que indicaste"
    )


def _lower_first(name: str) -> str:
    """``Bonos soberanos (BTP)`` -> ``bonos soberanos (BTP)`` (keeps acronyms)."""
    return name[:1].lower() + name[1:]


def template_explanation(data: ExplanationInput) -> dict:
    """Explanation with the same JSON shape as the language model output (Spanish keys)."""
    lines = sorted((a for a in data.allocation if a.amount >= 0.005), key=lambda a: -a.weight)
    if not lines:
        # Final fallback must never raise: nothing was allocated, so explain only that.
        return {
            "resumen": f"No hay montos para repartir de tus {format_money(data.amount)}.",
            "parrafos": ["No se asignó dinero a ninguna categoría, por lo que no hay un reparto que explicar."],
            "escenarios": [],
            "supuestos": list(data.assumptions),
        }
    top = lines[0]
    summary = (
        f"Repartimos tus {format_money(data.amount)} entre varias inversiones, "
        f"con el mayor peso en {_lower_first(top.name)}."
    )
    parts = [
        f"La mayor parte va a {_lower_first(top.name)}, es decir, {top.description}: "
        f"{format_percent(top.weight)} del total, {format_money(top.amount)}."
    ]
    parts += [
        f"Además, {format_percent(a.weight)} ({format_money(a.amount)}) va a {_lower_first(a.name)}, es decir, {a.description}."
        for a in lines[1:]
    ]
    bad, normal, good = data.scenarios
    scenario_paragraph = (
        "Para que veas cuánto puede variar tu dinero en un año: "
        f"en un año malo, {_scenario_clause(bad.amount)}; "
        f"en un año normal, {_scenario_clause(normal.amount)}; "
        f"y en un año bueno, {_scenario_clause(good.amount)}."
    )
    fuzzy_paragraph = (
        f"Como no necesitarías este dinero por {_horizon_phrase(data)}, {data.horizon_effect}. "
        f"Tu capacidad para absorber pérdidas es {data.absorption_effect}."
    )
    closing = (
        "Estas cifras son estimaciones educativas basadas en datos históricos, no predicciones. "
        "Puedes cambiar tus datos o el contexto y ver cómo cambia el reparto."
    )
    return {
        "resumen": summary,
        "parrafos": [" ".join(parts), scenario_paragraph, fuzzy_paragraph, closing],
        "escenarios": [
            {"label": label, "text": _scenario_text(s.amount), "amount": s.amount}
            for label, s in zip(_SCENARIO_LABELS, data.scenarios)
        ],
        "supuestos": [f"{a} Es un supuesto que puedes ajustar." for a in data.assumptions],
    }
