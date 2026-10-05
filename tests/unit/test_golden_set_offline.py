"""The offline extractor must not regress below its measured golden-set baseline.

Baseline measured on 2026-10-05 with ``scripts/eval_golden_set.py --provider offline``
(20 cases; see ``experiments/results/golden_offline.md``). Every field is correct since
the extractor parses amounts written as words ("cinco mil", "diez mil"); before that
fix the baseline was 97.1 % overall, 90 % on the asked field and 90 % on the amount.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BASELINE = {
    "overall_field_accuracy": 1.0,
    "complete_accuracy": 1.0,
    "question_field_accuracy": 1.0,
    "ambiguous_with_question": 1.0,
}
FIELD_BASELINE = {
    "monto_invertir": 1.0,
    "ahorro_total": 1.0,
    "horizonte_anios": 1.0,
    "horizonte_etiqueta": 1.0,
    "perfil_riesgo": 1.0,
    "cobertura_emergencia_meses": 1.0,
    "rechazos": 1.0,
}


@pytest.fixture(scope="module")
def summary():
    spec = importlib.util.spec_from_file_location("eval_golden_set", ROOT / "scripts" / "eval_golden_set.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve their module through sys.modules
    spec.loader.exec_module(module)
    cases = module.load_cases()
    assert 15 <= len(cases) <= 20
    return module.evaluate(cases).summary()


def test_offline_baseline_does_not_regress(summary):
    for metric, floor in BASELINE.items():
        assert summary[metric] >= floor - 1e-3, metric
    for name, floor in FIELD_BASELINE.items():
        assert summary["field_accuracy"][name] >= floor - 1e-3, name


def test_offline_reports_no_json_metric(summary):
    assert summary["valid_json"] is None
