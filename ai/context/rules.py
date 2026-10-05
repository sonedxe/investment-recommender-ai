"""Explicit context rule base RC1-RC7 (report v1.1 section 4.6.2).

Each rule is data (id, Spanish condition and effect texts) plus a condition
function and an effect function. Rules are evaluated in order over a running
return adjustment ``c`` and a volatility multiplier; every rule that fires
leaves a trace entry with its numeric effect per category.

    c_i = clip(b_i + beta_pol_i*s_pol + beta_mac_i*s_mac + beta_tend*s_tend_i, -c_max, +c_max)
    sigma_multiplier_i = 1 + gamma_pol_i*max(0, -s_pol) + gamma_mac_i*max(0, -s_mac)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import ArrayLike

from ai.shared.parameters import ContextParameters
from ai.shared.types import N_CATEGORIES, ContextFactors

Effect = tuple[np.ndarray, np.ndarray]  # (delta on c, delta on the sigma multiplier)


@dataclass(frozen=True)
class RuleState:
    """Inputs of the rule base plus the adjustment accumulated so far."""

    s_pol: float
    s_mac: float
    factors_informed: bool
    trend: np.ndarray
    params: ContextParameters
    c: np.ndarray


@dataclass(frozen=True)
class ContextRule:
    id: str
    condition: str
    effect: str
    applies: Callable[[RuleState], bool]
    apply: Callable[[RuleState], Effect]


@dataclass(frozen=True)
class RuleTrace:
    """One fired rule: Spanish texts and its numeric effect per category."""

    rule_id: str
    condition: str
    effect: str
    delta_mu: np.ndarray
    delta_sigma_factor: np.ndarray


@dataclass(frozen=True)
class RuleEvaluation:
    c: np.ndarray
    sigma_multiplier: np.ndarray
    trace: tuple[RuleTrace, ...]


def _zeros() -> np.ndarray:
    return np.zeros(N_CATEGORIES)


def _clip_cut(state: RuleState) -> Effect:
    limit = state.params.c_max
    return np.clip(state.c, -limit, limit) - state.c, _zeros()


RULES: tuple[ContextRule, ...] = (
    ContextRule(
        id="RC1",
        condition="Un factor global no fue informado",
        effect="Se asume s = 0 (neutral): no genera ningún ajuste.",
        applies=lambda s: not s.factors_informed,
        apply=lambda s: (_zeros(), _zeros()),
    ),
    ContextRule(
        id="RC2",
        condition="Siempre",
        effect="Cada categoría suma su precedente estructural b_i al ajuste de retorno.",
        applies=lambda s: True,
        apply=lambda s: (s.params.b.copy(), _zeros()),
    ),
    ContextRule(
        id="RC3",
        condition="Panorama político adverso (s_pol < 0)",
        effect="El retorno baja en β_pol,i·|s_pol| y el riesgo sube en un factor γ_pol,i·|s_pol|.",
        applies=lambda s: s.s_pol < 0,
        apply=lambda s: (s.params.beta_pol * s.s_pol, s.params.gamma_pol * -s.s_pol),
    ),
    ContextRule(
        id="RC4",
        condition="Panorama político favorable (s_pol > 0)",
        effect="El retorno sube en β_pol,i·s_pol; el riesgo no se reduce (asimetría prudente).",
        applies=lambda s: s.s_pol > 0,
        apply=lambda s: (s.params.beta_pol * s.s_pol, _zeros()),
    ),
    ContextRule(
        id="RC5",
        condition="Estabilidad macroeconómica distinta de neutral (s_mac ≠ 0)",
        effect=(
            "Si es adversa, el retorno baja en β_mac,i·|s_mac| y el riesgo sube en γ_mac,i·|s_mac|; "
            "si es favorable, solo sube el retorno en β_mac,i·s_mac."
        ),
        applies=lambda s: s.s_mac != 0,
        apply=lambda s: (s.params.beta_mac * s.s_mac, s.params.gamma_mac * max(0.0, -s.s_mac)),
    ),
    ContextRule(
        id="RC6",
        condition="Tendencia reciente de alguna categoría distinta de neutral (s_tend,i ≠ 0)",
        effect="El retorno de esa categoría se ajusta en β_tend·s_tend,i.",
        applies=lambda s: bool(np.any(s.trend != 0)),
        apply=lambda s: (s.params.beta_tend * s.trend, _zeros()),
    ),
    ContextRule(
        id="RC7",
        condition="Algún |c_i| supera c_max",
        effect="El ajuste se recorta a ±c_max para que el contexto nunca domine a los datos históricos.",
        applies=lambda s: bool(np.any(np.abs(s.c) > s.params.c_max)),
        apply=_clip_cut,
    ),
)


def _validate_unit(value: float, name: str) -> float:
    number = float(value)
    if not -1.0 <= number <= 1.0:
        raise ValueError(f"{name} must be in [-1, 1], got {number}")
    return number


def validate_trend(trend: ArrayLike) -> np.ndarray:
    array = np.asarray(trend, dtype=float)
    if array.shape != (N_CATEGORIES,):
        raise ValueError(f"trend must have shape ({N_CATEGORIES},), got {array.shape}")
    if np.any(np.abs(array) > 1.0):
        raise ValueError("trend values must be in [-1, 1]")
    return array


def evaluate_rules(
    factors: ContextFactors | None,
    trend: ArrayLike,
    params: ContextParameters,
    rules: tuple[ContextRule, ...] = RULES,
) -> RuleEvaluation:
    """Fire the rule base in order; ``factors=None`` means the global factors were not informed."""
    informed = factors is not None
    s_pol = _validate_unit(factors.political, "political") if informed else 0.0
    s_mac = _validate_unit(factors.macro, "macro") if informed else 0.0
    state = RuleState(s_pol, s_mac, informed, validate_trend(trend), params, _zeros())
    sigma_multiplier = np.ones(N_CATEGORIES)
    trace: list[RuleTrace] = []

    for rule in rules:
        if not rule.applies(state):
            continue
        delta_mu, delta_sigma = rule.apply(state)
        sigma_multiplier = sigma_multiplier + delta_sigma
        state = RuleState(s_pol, s_mac, informed, state.trend, params, state.c + delta_mu)
        trace.append(RuleTrace(rule.id, rule.condition, rule.effect, delta_mu, delta_sigma))

    return RuleEvaluation(c=state.c, sigma_multiplier=sigma_multiplier, trace=tuple(trace))
