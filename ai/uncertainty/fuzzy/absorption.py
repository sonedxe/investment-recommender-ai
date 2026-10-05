"""Fuzzy set in the CHROMOSOME: loss-absorption capacity (Mamdani, kept fuzzy).

Inputs are the investment ratio r = amount / total_savings and the emergency
coverage E in months. The aggregated output set mu_CA over [0, 1] is what the
genetic algorithm evaluates at its gene c; the centroid is only used for the
explanation and for comparison with the evolved c.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np

from ai.shared.parameters import AbsorptionParameters
from ai.uncertainty.fuzzy.inference import FuzzyRule
from ai.uncertainty.fuzzy.mamdani import DEFAULT_RESOLUTION, MamdaniSystem, centroid
from ai.uncertainty.fuzzy.membership import membership

RATIO = "ratio"
EMERGENCY = "emergency"
FALLBACK_OUTPUT_SET = "media"
ASSUMPTION_MEDIUM_CAPACITY = "Asumimos una capacidad media para asumir pérdidas."


@dataclass(frozen=True)
class AbsorptionResult:
    r: float | None
    e: float | None
    ratio_memberships: Mapping[str, float]
    emergency_memberships: Mapping[str, float]
    activations: Mapping[str, float]
    universe: np.ndarray
    mu_ca: np.ndarray
    centroid: float
    assumed: bool
    assumptions: tuple[str, ...] = field(default=())

    def membership_at(self, c: float) -> float:
        """mu_CA(c), linearly interpolated on the output grid (c clipped to the universe)."""
        return float(np.interp(c, self.universe, self.mu_ca))


def build_absorption_system(params: AbsorptionParameters, resolution: int = DEFAULT_RESOLUTION) -> MamdaniSystem:
    rules = tuple(
        FuzzyRule(rule.id, ((RATIO, rule.ratio), (EMERGENCY, rule.emergency)), rule.output)
        for rule in params.rules
    )
    return MamdaniSystem(
        inputs={RATIO: params.ratio_sets, EMERGENCY: params.emergency_sets},
        output_universe=params.output_universe,
        output_sets=params.output_sets,
        rules=rules,
        resolution=resolution,
    )


def evaluate_absorption(
    params: AbsorptionParameters,
    amount: float,
    total_savings: float | None,
    emergency_months: float | None,
    resolution: int = DEFAULT_RESOLUTION,
) -> AbsorptionResult:
    """Build mu_CA for the user; missing savings or coverage falls back to the Media set."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    if total_savings is not None and total_savings <= 0:
        raise ValueError("total_savings must be positive")
    if emergency_months is not None and emergency_months < 0:
        raise ValueError("emergency_months must be non-negative")
    system = build_absorption_system(params, resolution)

    if total_savings is None or emergency_months is None:
        universe = system.universe()
        mu_ca = np.asarray(membership(params.output_sets[FALLBACK_OUTPUT_SET], universe), dtype=float)
        return AbsorptionResult(
            r=None,
            e=None,
            ratio_memberships={},
            emergency_memberships={},
            activations={},
            universe=universe,
            mu_ca=mu_ca,
            centroid=centroid(universe, mu_ca),
            assumed=True,
            assumptions=(ASSUMPTION_MEDIUM_CAPACITY,),
        )

    r = float(np.clip(amount / total_savings, *params.ratio_universe))
    e = float(np.clip(emergency_months, *params.emergency_universe))
    result = system.evaluate({RATIO: r, EMERGENCY: e})
    return AbsorptionResult(
        r=r,
        e=e,
        ratio_memberships=dict(result.memberships[RATIO]),
        emergency_memberships=dict(result.memberships[EMERGENCY]),
        activations=dict(result.activations),
        universe=result.universe,
        mu_ca=result.aggregated,
        centroid=result.centroid,
        assumed=False,
    )
