"""HTTP routes of the recommendation flow (stage 2 and stages 3-7)."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException

from ai.generative.interpreter import interpret
from ai.generative.port import LanguageModel
from ai.shared.types import CATEGORY_ORDER, ContextFactors, UserProfile
from backend.app.api.schemas import (
    ContextDefaultsResponse,
    InterpretRequest,
    InterpretResponse,
    MarketEstimatesResponse,
    RecommendRequest,
    RecommendResponse,
)
from backend.app.core.llm import get_language_model, provider_info
from backend.app.services.recommendation import Switches, get_market_report, get_parameters, recommend

router = APIRouter(prefix="/api")

_LEVELS = [
    {"value": -1.0, "label": "Adverso"},
    {"value": 0.0, "label": "Neutral"},
    {"value": 1.0, "label": "Favorable"},
]
_FACTORS = [
    ("political", "Panorama político",
     "Cómo ves la estabilidad política del país en los próximos meses: elecciones, conflictos o cambios de reglas."),
    ("macro", "Estabilidad macroeconómica",
     "Cómo ves la economía: inflación, tipo de cambio y crecimiento."),
]


def _mode(llm: LanguageModel | None) -> dict[str, str]:
    info = provider_info(llm)
    return {"mode": info.mode, "provider": info.provider}


@router.post("/interpret", response_model=InterpretResponse)
def interpret_route(request: InterpretRequest, llm: LanguageModel | None = Depends(get_language_model)) -> dict:
    conversation = [turn.model_dump() for turn in request.conversation]
    result = interpret(conversation, llm=llm, params=get_parameters())
    question = None
    if result.question is not None:
        q = result.question
        question = {
            "field": q.field, "text": q.text, "hint": q.hint, "unit": q.unit, "free_input": q.free_input,
            "options": None if q.options is None else [asdict(o) for o in q.options],
        }
    return {
        **_mode(llm),
        "profile": asdict(result.profile),
        "evidence": dict(result.evidence),
        "missing": list(result.missing),
        "question": question,
        "complete": result.complete,
        "assumptions": list(result.assumptions),
        "absorption_assumed": result.absorption_assumed,
        "rejected": list(result.rejected),
        "contradictions": list(result.contradictions),
        "source": result.source,
        "prompt_version": result.prompt_version,
    }


@router.post("/recommend", response_model=RecommendResponse)
def recommend_route(request: RecommendRequest, llm: LanguageModel | None = Depends(get_language_model)) -> dict:
    p = request.profile
    try:
        profile = UserProfile(
            amount=p.amount, risk_profile=p.risk_profile, horizon_years=p.horizon_years,
            horizon_label=p.horizon_label, total_savings=p.total_savings, emergency_months=p.emergency_months,
        )
        factors = None if request.context is None else ContextFactors(**request.context.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    switches = Switches(**request.switches.model_dump())
    return {**_mode(llm), **recommend(profile, factors, switches, request.seed, llm)}


@router.get("/context/defaults", response_model=ContextDefaultsResponse)
def context_defaults() -> dict:
    params = get_parameters().context
    return {
        "factors": [
            {"id": fid, "label": label, "description": text, "value": 0.0, "levels": _LEVELS}
            for fid, label, text in _FACTORS
        ],
        "c_max": params.c_max,
        "beta_tend": params.beta_tend,
    }


@router.get("/market/estimates", response_model=MarketEstimatesResponse)
def market_estimates() -> dict:
    report, names = get_market_report(), get_parameters().categories.names
    market = report.estimates
    return {
        "categories": [
            {"category": cat.value, "name": names[cat], **asdict(report.categories[cat])} for cat in CATEGORY_ORDER
        ],
        "mu": market.mu.tolist(),
        "sigma": market.sigma.tolist(),
        "correlation": market.correlation.tolist(),
        "trend": market.trend.tolist(),
        "estimated_pairs": [(a.value, b.value) for a, b in report.estimated_pairs],
        "psd_repaired": report.psd_repaired,
    }
