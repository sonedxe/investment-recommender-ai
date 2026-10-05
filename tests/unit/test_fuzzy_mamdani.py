"""Mamdani engine with the class tip exercise (service 3, food 8).

The slides ("TEO-Logica Difusa (1)", slides 32-35) report P* = 15.9 %, but their
piecewise aggregated function uses (15 - P) / 5 on 10 < P < 13.333 without the
2/3 clip of rule R1, which overstates the area (125/9 instead of 245/18). The
exact min/max/centroid result for these sets is (17650/81) / (245/18) = 16.009 %,
which is the value this engine must reproduce.
"""

import numpy as np
import pytest

from ai.uncertainty.fuzzy.inference import FuzzyInferenceError, FuzzyRule
from ai.uncertainty.fuzzy.mamdani import MamdaniSystem
from ai.uncertainty.fuzzy.membership import MembershipSpec


def _s(kind: str, *params: float) -> MembershipSpec:
    return MembershipSpec(kind, tuple(float(p) for p in params))


@pytest.fixture
def tip_system() -> MamdaniSystem:
    return MamdaniSystem(
        inputs={
            "service": {
                "pobre": _s("trap", 0, 0, 2, 5),
                "bueno": _s("tri", 2, 5, 8),
                "excelente": _s("trap", 7, 9, 10, 10),
            },
            "food": {"rancia": _s("trap", 0, 0, 2, 5), "deliciosa": _s("trap", 6, 8, 10, 10)},
        },
        output_universe=(5.0, 25.0),
        output_sets={
            "tacana": _s("trap", 5, 5, 10, 15),
            "promedio": _s("tri", 10, 15, 20),
            "generosa": _s("trap", 15, 20, 25, 25),
        },
        rules=(
            FuzzyRule("R1", (("service", "pobre"), ("food", "rancia")), "tacana", operator="or"),
            FuzzyRule("R2", (("service", "bueno"),), "promedio"),
            FuzzyRule("R3", (("service", "excelente"), ("food", "deliciosa")), "generosa", operator="or"),
        ),
    )


def test_tip_activations(tip_system: MamdaniSystem) -> None:
    result = tip_system.evaluate({"service": 3.0, "food": 8.0})
    assert result.activations["R1"] == pytest.approx(0.667, abs=1e-3)
    assert result.activations["R2"] == pytest.approx(0.333, abs=1e-3)
    assert result.activations["R3"] == pytest.approx(1.0)


EXACT_TIP_CENTROID = (17650 / 81) / (245 / 18)  # 16.0091


def test_tip_centroid_matches_exact_integral(tip_system: MamdaniSystem) -> None:
    result = tip_system.evaluate({"service": 3.0, "food": 8.0})
    assert result.centroid == pytest.approx(EXACT_TIP_CENTROID, abs=1e-3)
    # Within 0.11 of the slides' hand-computed 15.9 % (see module docstring).
    assert abs(result.centroid - 15.9) < 0.11


def test_aggregated_set_is_clipped_union(tip_system: MamdaniSystem) -> None:
    result = tip_system.evaluate({"service": 3.0, "food": 8.0})
    assert result.universe.size >= 1001
    assert result.aggregated.shape == result.universe.shape
    assert result.aggregated.max() == pytest.approx(1.0)
    left = result.aggregated[result.universe <= 7.0]
    np.testing.assert_allclose(left, 2 / 3, atol=1e-3)


def test_zero_firing_raises(tip_system: MamdaniSystem) -> None:
    rules = (FuzzyRule("R2", (("service", "bueno"),), "promedio"),)
    system = MamdaniSystem(tip_system.inputs, tip_system.output_universe, tip_system.output_sets, rules)
    with pytest.raises(FuzzyInferenceError):
        system.evaluate({"service": 9.5, "food": 8.0})
