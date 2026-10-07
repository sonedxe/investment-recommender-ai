"""Recommendation use case: stages 3-7 of the flow for a complete profile.

market estimates (cached) -> horizon (lambda_eff) -> absorption (mu_CA) ->
context adjustment -> genetic algorithm -> explanation, assembled into one
JSON-ready response with the technical detail the GUI shows.

Switches (ablation): ``fuzzy=False`` uses m_H = 1 (lambda_eff = lambda_base)
and disables the volatility penalty and the kappa reward; ``context=False``
uses c = 0 and sigma' = sigma.
"""

from __future__ import annotations

import math
import secrets
from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any

import numpy as np

from ai.context.adjustment import ContextAdjustment, adjust
from ai.generative.explainer import ExplanationResult, build_explanation_input, explain
from ai.generative.port import LanguageModel
from ai.heuristic.fitness import FitnessInputs
from ai.heuristic.report_fitness import report_fitness
from ai.heuristic.genetic_algorithm import GAResult, run_ga
from ai.shared.parameters import Parameters, load_parameters
from ai.shared.types import CATEGORY_ORDER, ContextFactors, UserProfile
from ai.uncertainty.bayesian.market import MarketReport, build_market_estimates
from ai.uncertainty.fuzzy.absorption import AbsorptionResult, evaluate_absorption
from ai.uncertainty.fuzzy.horizon import HorizonResult, evaluate_horizon
from ai.uncertainty.fuzzy.sugeno_absorption import evaluate_absorption_sugeno
from ai.uncertainty.fuzzy.membership import membership

HORIZON_CURVE_MAX_YEARS, HORIZON_CURVE_STEP = 15.0, 0.25
ABSORPTION_CURVE_POINTS = 101
NEUTRAL_CONTEXT_ASSUMPTION = "Se asumió un panorama político y macroeconómico neutral."
PRIOR_DATA_ASSUMPTION = "Para {names} usamos valores de referencia históricos, no datos de mercado recientes."
_HORIZON_EFFECTS = {"corto": "más cautela", "mediano": "cautela base", "largo": "menos cautela"}


@dataclass(frozen=True)
class Switches:
    fuzzy: bool = True
    context: bool = True


@lru_cache(maxsize=1)
def get_parameters() -> Parameters:
    return load_parameters()


@lru_cache(maxsize=1)
def get_market_report() -> MarketReport:
    return build_market_estimates(get_parameters())


def allocate_amounts(weights: np.ndarray, amount: float) -> list[float]:
    """Amounts in soles rounded to cents that add up exactly to ``amount`` (largest remainder)."""
    total_cents = int(round(amount * 100))
    raw = np.asarray(weights, dtype=float) / float(np.sum(weights)) * total_cents
    cents = np.floor(raw).astype(int)
    for index in np.argsort(-(raw - cents))[: total_cents - int(cents.sum())]:
        cents[index] += 1
    return [c / 100 for c in cents.tolist()]


def _finite(value: float | None) -> float | None:
    return None if value is None or not math.isfinite(value) else float(value)


def _horizon_block(params: Parameters, horizon: HorizonResult, enabled: bool) -> dict[str, Any]:
    x = np.arange(0.0, HORIZON_CURVE_MAX_YEARS + 1e-9, HORIZON_CURVE_STEP)
    return {
        "enabled": enabled,
        "years": horizon.years,
        "label": None if horizon.label is None else horizon.label.value,
        "memberships": dict(horizon.memberships),
        "curves": [
            {"label": name, "points": [{"x": float(a), "y": float(b)} for a, b in zip(x, membership(spec, x))]}
            for name, spec in params.fuzzy.horizon.sets.items()
        ],
    }


def _absorption_block(absorption: AbsorptionResult, c: float, enabled: bool) -> dict[str, Any]:
    step = max(1, (len(absorption.universe) - 1) // (ABSORPTION_CURVE_POINTS - 1))
    return {
        "enabled": enabled,
        "points": [
            {"x": float(x), "y": float(y)} for x, y in zip(absorption.universe[::step], absorption.mu_ca[::step])
        ],
        "c": c,
        "membership_at_c": absorption.membership_at(c) if enabled else None,
        "centroid": absorption.centroid,
        "r": absorption.r,
        "e": absorption.e,
        "assumed": absorption.assumed,
        "ratio_memberships": dict(absorption.ratio_memberships),
        "emergency_memberships": dict(absorption.emergency_memberships),
        # Strict report-v1.1 reference (Sugeno, section 4.5.2): filled by the
        # caller in recommend(); None when the profile has no absorption data
        # path (kept for schema compatibility with older responses).
        "sugeno_ca": None,
        "sugeno_sigma_max": None,
    }


def _rules(params: Parameters, horizon: HorizonResult, absorption: AbsorptionResult,
           context: ContextAdjustment, switches: Switches) -> list[dict[str, Any]]:
    rules = [
        {
            "kind": "horizon",
            "id": f"RH{i}",
            "condition": f"Si el horizonte es {name}",
            "effect": f"m_H = {z} ({_HORIZON_EFFECTS.get(name, 'ajuste')})",
            "activation": float(horizon.memberships.get(name, 0.0)),
            "applied": switches.fuzzy,
        }
        for i, (name, z) in enumerate(params.fuzzy.horizon.consequents.items(), start=1)
    ]
    rules += [
        {
            "kind": "absorption",
            "id": rule.id,
            "condition": f"Si la proporción invertida es {rule.ratio} y la cobertura de emergencia es {rule.emergency}",
            "effect": f"La capacidad de absorber pérdidas es {rule.output}",
            "activation": None if absorption.assumed else float(absorption.activations.get(rule.id, 0.0)),
            "applied": switches.fuzzy and not absorption.assumed,
        }
        for rule in params.fuzzy.absorption.rules
    ]
    rules += [
        {"kind": "context", "id": t.rule_id, "condition": t.condition, "effect": t.effect, "activation": None,
         "applied": True}
        for t in context.trace
    ]
    return rules


def _assumptions(report: MarketReport, params: Parameters, factors: ContextFactors | None,
                 absorption: AbsorptionResult, switches: Switches) -> list[str]:
    assumptions: list[str] = []
    names = params.categories.names
    if switches.fuzzy and absorption.assumed:
        assumptions.extend(absorption.assumptions)
    if switches.context and factors is None:
        assumptions.append(NEUTRAL_CONTEXT_ASSUMPTION)
    priors = [names[c][:1].lower() + names[c][1:] for c in CATEGORY_ORDER if report.categories[c].source == "prior"]
    if priors:
        names = ", ".join(priors[:-1]) + (" y " if len(priors) > 1 else "") + priors[-1]
        assumptions.append(PRIOR_DATA_ASSUMPTION.format(names=names))
    return assumptions


def _explanation_dict(result: ExplanationResult) -> dict[str, Any]:
    return {
        "summary": result.summary,
        "paragraphs": list(result.paragraphs),
        "scenarios": [asdict(s) for s in result.scenarios],
        "assumptions": list(result.assumptions),
        "source": result.source,
        "prompt_version": result.prompt_version,
        "validation": {**asdict(result.validation), "errors": list(result.validation.errors)},
    }


def recommend(
    profile: UserProfile,
    factors: ContextFactors | None = None,
    switches: Switches = Switches(),
    seed: int | None = None,
    llm: LanguageModel | None = None,
) -> dict[str, Any]:
    """Run stages 3-7; ``factors=None`` means not informed (neutral, declared as an assumption)."""
    params, report = get_parameters(), get_market_report()
    seed = secrets.randbelow(2**31) if seed is None else seed
    market = report.estimates
    lambda_base = float(params.risk_profiles.lambda_base[profile.risk_profile])

    horizon = evaluate_horizon(params.fuzzy.horizon, lambda_base, profile.horizon_years, profile.horizon_label)
    m_h = horizon.m_h if switches.fuzzy else 1.0
    absorption = evaluate_absorption(
        params.fuzzy.absorption, profile.amount, profile.total_savings, profile.emergency_months
    )
    context = adjust(market, factors, None, params.context, enabled=switches.context)

    opt, abs_params = params.optimization, params.fuzzy.absorption
    inputs = FitnessInputs(
        mu=market.mu,
        context_adj=context.c,
        cov=context.cov_adj,
        lambda_eff=lambda_base * m_h,
        universe=absorption.universe,
        mu_ca=absorption.mu_ca,
        sigma_floor=abs_params.sigma_floor,
        sigma_amplitude=abs_params.sigma_amplitude,
        phi=opt.phi,
        kappa=opt.kappa,
        fuzzy_enabled=switches.fuzzy,
    )
    ga: GAResult = run_ga(inputs, opt, seed=seed)
    # Strict report-v1.1 reference (sections 4.5.2 and 5.2), computed live for
    # every recommendation: Sugeno CA and the strict fitness evaluated at the
    # returned weights with kappa = 0. It mirrors the ablation switches so the
    # reference stays comparable (fuzzy off -> no horizon modulation and no
    # volatility cap, exactly like the extended engine's disabled state).
    sugeno = evaluate_absorption_sugeno(
        params.fuzzy.absorption, profile.amount, profile.total_savings, profile.emergency_months
    )
    strict_lambda = lambda_base * m_h if switches.fuzzy else lambda_base
    strict_sigma_max = sugeno.sigma_max if switches.fuzzy else math.inf
    strict = report_fitness(
        ga.weights,
        context.mu_adj,
        context.cov_adj,
        strict_lambda,
        strict_sigma_max,
        mu_base=market.mu,
        c=context.c,
        phi=opt.phi,
    )
    amounts = allocate_amounts(ga.weights, profile.amount)
    names = params.categories.names
    allocation = [
        {"category": cat.value, "name": names[cat], "weight": float(w), "amount": a}
        for cat, w, a in zip(CATEGORY_ORDER, ga.weights, amounts)
    ]

    assumptions = _assumptions(report, params, factors, absorption, switches)
    breakdown = ga.breakdown
    explanation_input = build_explanation_input(
        amount=profile.amount,
        allocation=[(cat, names[cat], float(w), a) for cat, w, a in zip(CATEGORY_ORDER, ga.weights, amounts)],
        expected_return=breakdown.expected_return,
        sigma=breakdown.sigma,
        risk_profile=profile.risk_profile.value,
        horizon_years=profile.horizon_years,
        horizon_label=None if profile.horizon_label is None else profile.horizon_label.value,
        m_h=m_h if switches.fuzzy else None,
        absorption_level=absorption.centroid if switches.fuzzy else None,
        absorption_assumed=absorption.assumed,
        assumptions=assumptions,
    )
    explanation = explain(explanation_input, llm=llm)

    return {
        "amount": round(profile.amount, 2),
        "profile": {
            "amount": profile.amount,
            "risk_profile": profile.risk_profile.value,
            "horizon_years": profile.horizon_years,
            "horizon_label": None if profile.horizon_label is None else profile.horizon_label.value,
            "total_savings": profile.total_savings,
            "emergency_months": profile.emergency_months,
        },
        "allocation": allocation,
        "expected_return": breakdown.expected_return,
        "sigma": breakdown.sigma,
        "c": ga.c,
        "scenarios": [
            {"name": s.name, "amount": s.amount} for s in explanation_input.scenarios
        ],
        "explanation": _explanation_dict(explanation),
        "assumptions": assumptions,
        "switches": asdict(switches),
        "technical": {
            "params": [
                {
                    "category": cat.value,
                    "name": names[cat],
                    "mu": float(market.mu[i]),
                    "sigma": float(market.sigma[i]),
                    "mu_adj": float(context.mu_adj[i]),
                    "sigma_adj": float(context.sigma_adj[i]),
                    "context_adj": float(context.c[i]),
                    "source": report.categories[cat].source,
                }
                for i, cat in enumerate(CATEGORY_ORDER)
            ],
            "lambda_base": lambda_base,
            "m_h": m_h,
            "lambda_eff": lambda_base * m_h,
            "horizon": _horizon_block(params, horizon, switches.fuzzy),
            "absorption": {
                **_absorption_block(absorption, ga.c, switches.fuzzy),
                "sugeno_ca": sugeno.ca,
                "sugeno_sigma_max": sugeno.sigma_max,
            },
            "rules": _rules(params, horizon, absorption, context, switches),
            "score": {
                **{k: _finite(v) for k, v in asdict(breakdown).items()},
                "strict_total": strict.total,
            },
            "convergence": {
                "best": ga.history_best.tolist(),
                "mean": ga.history_mean.tolist(),
                "generations": ga.generations_run,
                "converged": ga.converged,
                "seed": seed,
            },
            "max_weight": ga.max_weight,
        },
    }
