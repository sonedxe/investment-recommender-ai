"""JSON schemas sent to the language model and a minimal validator for them.

Only the subset of JSON Schema used here is supported: ``type`` (single or a
list including ``"null"``), ``enum``, ``properties``, ``required``, ``items``,
``minItems``/``maxItems``, ``minLength`` and ``additionalProperties: false``.
"""

from __future__ import annotations

from typing import Any

from ai.shared.types import HorizonLabel, RiskProfile

FIELD_AMOUNT = "monto_invertir"
FIELD_HORIZON = "horizonte"
FIELD_RISK = "perfil_riesgo"
FIELD_SAVINGS = "ahorro_total"
FIELD_EMERGENCY = "cobertura_emergencia_meses"
CRITICAL_FIELDS = (FIELD_AMOUNT, FIELD_HORIZON, FIELD_RISK)
ABSORPTION_FIELDS = (FIELD_SAVINGS, FIELD_EMERGENCY)
ALL_FIELDS = CRITICAL_FIELDS + ABSORPTION_FIELDS

_NUMBER_OR_NULL = {"type": ["number", "null"]}

INTERPRET_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "monto_invertir", "horizonte_anios", "horizonte_etiqueta", "perfil_riesgo",
        "ahorro_total", "cobertura_emergencia_meses", "evidencia", "rechazos", "contradicciones",
    ],
    "properties": {
        "monto_invertir": _NUMBER_OR_NULL,
        "horizonte_anios": _NUMBER_OR_NULL,
        "horizonte_etiqueta": {"type": ["string", "null"], "enum": [h.value for h in HorizonLabel] + [None]},
        "perfil_riesgo": {"type": ["string", "null"], "enum": [p.value for p in RiskProfile] + [None]},
        "ahorro_total": _NUMBER_OR_NULL,
        "cobertura_emergencia_meses": _NUMBER_OR_NULL,
        "evidencia": {"type": "object"},
        "rechazos": {"type": "array", "items": {"type": "string", "enum": list(ALL_FIELDS)}},
        "contradicciones": {"type": "array", "items": {"type": "string"}},
    },
}

CLARIFY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["pregunta", "ayuda"],
    "properties": {"pregunta": {"type": "string", "minLength": 5}, "ayuda": {"type": ["string", "null"]}},
}

EXPLAIN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["resumen", "parrafos", "escenarios", "supuestos"],
    "properties": {
        "resumen": {"type": "string", "minLength": 1},
        "parrafos": {"type": "array", "minItems": 3, "maxItems": 6, "items": {"type": "string", "minLength": 1}},
        "escenarios": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "required": ["label", "text", "amount"],
                "properties": {"label": {"type": "string"}, "text": {"type": "string"}, "amount": {"type": "number"}},
            },
        },
        "supuestos": {"type": "array", "items": {"type": "string"}},
    },
}

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
}


def _is_type(value: Any, name: str) -> bool:
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, _TYPES[name])


def validate(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Return the list of violations of ``schema`` (empty when ``value`` is valid)."""
    types = schema.get("type")
    if types is not None:
        allowed = types if isinstance(types, list) else [types]
        if not any(_is_type(value, t) for t in allowed):
            return [f"{path}: expected {'/'.join(allowed)}"]
    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: {value!r} is not one of {schema['enum']}"]
    errors: list[str] = []
    if isinstance(value, dict):
        props = schema.get("properties", {})
        errors += [f"{path}.{key}: required" for key in schema.get("required", []) if key not in value]
        if schema.get("additionalProperties") is False:
            errors += [f"{path}.{key}: not allowed" for key in value if key not in props]
        for key, sub in props.items():
            if key in value:
                errors += validate(value[key], sub, f"{path}.{key}")
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: needs at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: allows at most {schema['maxItems']} items")
        for i, item in enumerate(value):
            errors += validate(item, schema.get("items", {}), f"{path}[{i}]")
    elif isinstance(value, str) and len(value.strip()) < schema.get("minLength", 0):
        errors.append(f"{path}: too short")
    return errors
