"""Zero-order Sugeno engine."""

import pytest

from ai.uncertainty.fuzzy.inference import FuzzyInferenceError, FuzzyRule
from ai.uncertainty.fuzzy.membership import MembershipSpec
from ai.uncertainty.fuzzy.sugeno import SugenoSystem


def _system() -> SugenoSystem:
    sets = {
        "low": MembershipSpec("trap", (0.0, 0.0, 2.0, 6.0)),
        "high": MembershipSpec("trap", (4.0, 8.0, 10.0, 10.0)),
    }
    return SugenoSystem(
        inputs={"x": sets, "y": sets},
        rules=(
            FuzzyRule("A", (("x", "low"), ("y", "low")), 1.0),
            FuzzyRule("B", (("x", "high"), ("y", "high")), 3.0, operator="or"),
        ),
    )


def test_weighted_average_with_and_or() -> None:
    result = _system().evaluate({"x": 5.0, "y": 3.0})
    # x: low 0.25, high 0.25; y: low 0.75, high 0 -> A = min = 0.25, B = max = 0.25
    assert result.firing == {"A": pytest.approx(0.25), "B": pytest.approx(0.25)}
    assert result.output == pytest.approx(2.0)


def test_zero_total_firing_raises() -> None:
    system = SugenoSystem(
        inputs=_system().inputs, rules=(FuzzyRule("A", (("x", "low"), ("y", "low")), 1.0),)
    )
    with pytest.raises(FuzzyInferenceError):
        system.evaluate({"x": 9.0, "y": 9.0})
