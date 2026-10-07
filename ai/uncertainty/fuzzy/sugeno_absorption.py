"""Strict report-v1.1 absorption: zero-order Sugeno over RA1-RA6.

Report sections 4.5.2 and C.2 define six rules with crisp consequents
Baja = 0.20, Media = 0.50, Alta = 0.85, AND implemented with min and
``CA = sum(w_k * z_k) / sum(w_k)``. ``sigma_max = sigma_piso + a * CA``
with ``sigma_piso = 3 %`` and ``a = 13 %`` (taken from the loaded
parameters so the code stays driven by ``data/parameters/fuzzy.json``).

This is the computation a line-by-line reviewer expects from the report.
The shipped product extends it with a Mamdani system whose aggregated set
``mu_CA`` is evaluated at the evolved gene ``c``
(see ``ai/uncertainty/fuzzy/absorption.py`` and
``docs/analisis/04-propuesta-difusa-cromosoma.md``); both share the same
input memberships and rule activations, so the Sugeno value below is the
reference the extension must stay close to (report example: 0.54).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from ai.shared.parameters import AbsorptionParameters
from ai.uncertainty.fuzzy.absorption import (
    ASSUMPTION_MEDIUM_CAPACITY,
    EMERGENCY,
    RATIO,
)
from ai.uncertainty.fuzzy.inference import fuzzify

# Annex C.2, report v1.1: crisp consequents of RA1-RA6 by output label.
SUGENO_CA_CONSEQUENTS: dict[str, float] = {
    "baja": 0.20,
    "media": 0.50,
    "alta": 0.85,
}


@dataclass(frozen=True)
class SugenoAbsorptionResult:
    r: float | None
    e: float | None
    ratio_memberships: Mapping[str, float]
    emergency_memberships: Mapping[str, float]
    activations: Mapping[str, float]
    ca: float
    sigma_max: float
    assumed: bool
    assumptions: tuple[str, ...] = ()


def evaluate_absorption_sugeno(
    params: AbsorptionParameters,
    amount: float,
    total_savings: float | None,
    emergency_months: float | None,
) -> SugenoAbsorptionResult:
    """Sugeno CA for the user; missing data falls back to Media (0.50)."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    if total_savings is not None and total_savings <= 0:
        raise ValueError("total_savings must be positive")
    if emergency_months is not None and emergency_months < 0:
        raise ValueError("emergency_months must be non-negative")

    if total_savings is None or emergency_months is None:
        return SugenoAbsorptionResult(
            r=None,
            e=None,
            ratio_memberships={},
            emergency_memberships={},
            activations={},
            ca=SUGENO_CA_CONSEQUENTS["media"],
            sigma_max=params.sigma_floor + params.sigma_amplitude * SUGENO_CA_CONSEQUENTS["media"],
            assumed=True,
            assumptions=(ASSUMPTION_MEDIUM_CAPACITY,),
        )

    r = float(np.clip(amount / total_savings, *params.ratio_universe))
    e = float(np.clip(emergency_months, *params.emergency_universe))
    memberships = fuzzify(
        {RATIO: r, EMERGENCY: e},
        {RATIO: params.ratio_sets, EMERGENCY: params.emergency_sets},
    )
    activations: dict[str, float] = {}
    for rule in params.rules:
        degrees = [memberships[var][name] for var, name in ((RATIO, rule.ratio), (EMERGENCY, rule.emergency))]
        activations[rule.id] = float(min(degrees))
    total = sum(activations.values())
    if total <= 0:
        raise ValueError("no Sugeno absorption rule fires")
    weighted = sum(
        activations[rule.id] * SUGENO_CA_CONSEQUENTS[rule.output] for rule in params.rules
    )
    ca = weighted / total
    return SugenoAbsorptionResult(
        r=r,
        e=e,
        ratio_memberships=dict(memberships[RATIO]),
        emergency_memberships=dict(memberships[EMERGENCY]),
        activations=activations,
        ca=ca,
        sigma_max=params.sigma_floor + params.sigma_amplitude * ca,
        assumed=False,
    )
