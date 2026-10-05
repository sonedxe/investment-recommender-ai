"""Fuzzy set in the FITNESS: investment horizon -> lambda_eff (zero-order Sugeno).

Rules RH1-RH3: IF horizon is corto/mediano/largo THEN m_H = 1.5/1.0/0.7, and
lambda_eff = lambda_base * m_H.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from ai.shared.parameters import HorizonParameters
from ai.shared.types import HorizonLabel
from ai.uncertainty.fuzzy.inference import FuzzyRule
from ai.uncertainty.fuzzy.sugeno import SugenoSystem

HORIZON_VARIABLE = "horizon"


@dataclass(frozen=True)
class HorizonResult:
    memberships: Mapping[str, float]
    m_h: float
    lambda_base: float
    lambda_eff: float
    years: float | None
    label: HorizonLabel | None


def build_horizon_system(params: HorizonParameters) -> SugenoSystem:
    rules = tuple(
        FuzzyRule(f"RH{i}", ((HORIZON_VARIABLE, name),), z)
        for i, (name, z) in enumerate(params.consequents.items(), start=1)
    )
    return SugenoSystem(inputs={HORIZON_VARIABLE: params.sets}, rules=rules)


def evaluate_horizon(
    params: HorizonParameters,
    lambda_base: float,
    years: float | None = None,
    label: HorizonLabel | str | None = None,
) -> HorizonResult:
    """Compute m_H and lambda_eff from a numeric horizon or a qualitative label (exactly one)."""
    if (years is None) == (label is None):
        raise ValueError("provide exactly one of years or label")
    if lambda_base <= 0:
        raise ValueError("lambda_base must be positive")
    system = build_horizon_system(params)

    parsed_label: HorizonLabel | None = None
    if label is not None:
        parsed_label = HorizonLabel(label)  # raises ValueError on unknown labels
        if parsed_label.value not in params.sets:
            raise ValueError(f"label {parsed_label.value!r} has no fuzzy set")
        # A qualitative answer belongs fully to its set and not at all to the others.
        degrees = {name: float(name == parsed_label.value) for name in params.sets}
        result = system.infer({HORIZON_VARIABLE: degrees})
    else:
        if years < 0:
            raise ValueError("years must be non-negative")
        clipped = float(np.clip(years, *params.universe))
        result = system.evaluate({HORIZON_VARIABLE: clipped})

    m_h = result.output
    return HorizonResult(
        memberships=dict(result.memberships[HORIZON_VARIABLE]),
        m_h=m_h,
        lambda_base=lambda_base,
        lambda_eff=lambda_base * m_h,
        years=None if years is None else float(years),
        label=parsed_label,
    )
