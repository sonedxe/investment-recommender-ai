"""Evaluate the interpretation stage against the golden set (``tests/golden/interpret_cases.json``).

Usage:
    python scripts/eval_golden_set.py --provider offline|openai|anthropic \
        [--out experiments/results/golden_<provider>.md]

Metrics: per-field accuracy over the expected fields of each case, accuracy of
``complete`` and of the asked field, share of ambiguous/contradictory cases that
produced a question (target 100 %), share of valid JSON answers (LLM providers
only) and latency per case. LLM providers need their API key in the environment
(or ``.env``); the offline provider never touches the network.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.generative.interpreter import interpret  # noqa: E402
from ai.generative.port import LanguageModel  # noqa: E402
from ai.generative.schema import validate  # noqa: E402

GOLDEN_PATH = ROOT / "tests" / "golden" / "interpret_cases.json"
_PROFILE_ATTR = {
    "monto_invertir": "amount",
    "horizonte_anios": "horizon_years",
    "horizonte_etiqueta": "horizon_label",
    "perfil_riesgo": "risk_profile",
    "ahorro_total": "total_savings",
    "cobertura_emergencia_meses": "emergency_months",
}


class CountingModel:
    """Wraps a ``LanguageModel`` and counts answers that are valid JSON for their schema."""

    def __init__(self, inner: LanguageModel) -> None:
        self.inner, self.name = inner, inner.name
        self.calls = self.valid = 0

    def complete_json(self, system, messages, schema, *, temperature, max_tokens):
        self.calls += 1
        data = self.inner.complete_json(system, messages, schema, temperature=temperature, max_tokens=max_tokens)
        if not validate(data, schema):
            self.valid += 1
        return data


@dataclass
class CaseResult:
    case_id: str
    field_hits: dict[str, bool]
    complete_ok: bool
    question_ok: bool
    asked: str | None
    latency_s: float
    source: str


@dataclass
class Report:
    provider: str
    cases: list[CaseResult] = field(default_factory=list)
    requires_question: int = 0
    produced_question: int = 0
    json_calls: int = 0
    json_valid: int = 0

    def field_accuracy(self) -> dict[str, float]:
        totals: dict[str, list[bool]] = {}
        for case in self.cases:
            for name, hit in case.field_hits.items():
                totals.setdefault(name, []).append(hit)
        return {name: sum(hits) / len(hits) for name, hits in totals.items()}

    def summary(self) -> dict[str, Any]:
        hits = [h for c in self.cases for h in c.field_hits.values()]
        latencies = [c.latency_s for c in self.cases]
        return {
            "cases": len(self.cases),
            "field_accuracy": self.field_accuracy(),
            "overall_field_accuracy": sum(hits) / len(hits) if hits else 0.0,
            "complete_accuracy": sum(c.complete_ok for c in self.cases) / len(self.cases),
            "question_field_accuracy": sum(c.question_ok for c in self.cases) / len(self.cases),
            "ambiguous_with_question": self.produced_question / self.requires_question if self.requires_question else 1.0,
            "valid_json": None if not self.json_calls else self.json_valid / self.json_calls,
            "latency_mean_s": statistics.fmean(latencies),
            "latency_max_s": max(latencies),
        }


def load_cases(path: Path = GOLDEN_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))["cases"]


def _value(profile: Any, name: str) -> Any:
    value = getattr(profile, _PROFILE_ATTR[name])
    return getattr(value, "value", value)


def _matches(actual: Any, expected: Any) -> bool:
    if expected is None or actual is None:
        return actual is expected
    if isinstance(expected, (int, float)):
        return isinstance(actual, (int, float)) and abs(actual - expected) < 1e-6
    return actual == expected


def evaluate(cases: Sequence[dict[str, Any]], llm: LanguageModel | None = None, provider: str = "offline") -> Report:
    counter = CountingModel(llm) if llm is not None else None
    report = Report(provider)
    for case in cases:
        start = time.perf_counter()
        result = interpret(case["conversation"], llm=counter)
        latency = time.perf_counter() - start
        asked = result.question.field if result.question else None
        hits = {name: _matches(_value(result.profile, name), exp) for name, exp in case["expected"].items()}
        if "expected_rejected" in case:
            hits["rechazos"] = set(case["expected_rejected"]) <= set(result.rejected)
        if case.get("requires_question"):
            report.requires_question += 1
            report.produced_question += asked is not None
        report.cases.append(CaseResult(
            case["id"], hits, result.complete == case["expected_complete"],
            asked == case["expected_question"], asked, latency, result.source,
        ))
    if counter is not None:
        report.json_calls, report.json_valid = counter.calls, counter.valid
    return report


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{100 * value:.1f} %"


def to_markdown(report: Report) -> str:
    s = report.summary()
    lines = [
        f"# Golden set de interpretación — proveedor `{report.provider}`",
        "",
        f"Casos: {s['cases']} · Generado por `scripts/eval_golden_set.py`.",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Exactitud global por campo | {_pct(s['overall_field_accuracy'])} |",
        f"| `complete` correcto | {_pct(s['complete_accuracy'])} |",
        f"| Campo preguntado correcto | {_pct(s['question_field_accuracy'])} |",
        f"| Ambiguos/contradictorios con pregunta (objetivo 100 %) | {_pct(s['ambiguous_with_question'])} |",
        f"| JSON válido (solo LLM) | {_pct(s['valid_json'])} |",
        f"| Latencia media / máxima | {s['latency_mean_s'] * 1000:.1f} ms / {s['latency_max_s'] * 1000:.1f} ms |",
        "",
        "## Exactitud por campo",
        "",
        "| Campo | Exactitud |",
        "|---|---|",
        *[f"| `{name}` | {_pct(acc)} |" for name, acc in sorted(s["field_accuracy"].items())],
        "",
        "## Detalle por caso",
        "",
        "| Caso | Campos fallados | `complete` | Pregunta | Fuente |",
        "|---|---|---|---|---|",
    ]
    for c in report.cases:
        failed = ", ".join(f"`{n}`" for n, ok in c.field_hits.items() if not ok) or "—"
        lines.append(
            f"| {c.case_id} | {failed} | {'ok' if c.complete_ok else 'FALLA'} | "
            f"{c.asked or '—'} ({'ok' if c.question_ok else 'FALLA'}) | {c.source} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--provider", choices=("offline", "openai", "anthropic"), default="offline")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    llm = None
    if args.provider != "offline":
        from dotenv import load_dotenv

        from ai.generative.adapters import build_language_model

        load_dotenv(ROOT / ".env")
        llm = build_language_model(args.provider)
        if llm is None:
            print(f"provider {args.provider} is not available (missing API key or SDK)", file=sys.stderr)
            return 2
    report = evaluate(load_cases(), llm, args.provider)
    markdown = to_markdown(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
