"""POST /api/recommend, context and market endpoints, and the full offline flow."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

PROFILE = {"amount": 5000, "risk_profile": "moderado", "horizon_years": 3, "total_savings": 20000, "emergency_months": 4}


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "offline")


def post(**overrides) -> dict:
    payload = {"profile": PROFILE, "seed": 7, **overrides}
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200, res.text
    return res.json()


def test_recommendation_respects_cap_and_amounts() -> None:
    body = post()
    weights = [a["weight"] for a in body["allocation"]]
    assert [a["category"] for a in body["allocation"]] == ["stocks", "mixed", "debt", "bonds", "term"]
    assert all(0 <= w <= 0.40 + 1e-9 for w in weights)
    assert sum(weights) == pytest.approx(1.0)
    assert round(sum(a["amount"] for a in body["allocation"]), 2) == 5000.00
    assert all(round(a["amount"], 2) == a["amount"] for a in body["allocation"])
    assert body["mode"] == "offline" and body["explanation"]["source"] == "offline"
    assert body["explanation"]["validation"]["passed"]


def test_technical_block_is_populated() -> None:
    tech = post()["technical"]
    kinds = {r["kind"] for r in tech["rules"]}
    assert kinds == {"horizon", "absorption", "context"}
    horizon_rules = [r for r in tech["rules"] if r["kind"] == "horizon"]
    assert [r["activation"] for r in horizon_rules] == pytest.approx([0.0, 1 / 3, 0.0])
    assert all(r["activation"] is not None for r in tech["rules"] if r["kind"] == "absorption")
    assert all(r["activation"] is None for r in tech["rules"] if r["kind"] == "context")
    assert len(tech["params"]) == 5 and {"mu_adj", "sigma_adj", "context_adj"} <= set(tech["params"][0])
    curve = tech["horizon"]["curves"][0]["points"]
    assert curve[0]["x"] == 0 and curve[-1]["x"] == 15 and curve[1]["x"] - curve[0]["x"] <= 0.25
    absorption = tech["absorption"]
    assert absorption["r"] == 0.25 and absorption["e"] == 4 and absorption["membership_at_c"] is not None
    assert tech["lambda_eff"] == pytest.approx(tech["lambda_base"] * tech["m_h"])
    convergence = tech["convergence"]
    assert len(convergence["best"]) == convergence["generations"] + 1 and convergence["seed"] == 7
    assert convergence["best"] == sorted(convergence["best"])  # elitism: best never decreases


def test_same_seed_is_reproducible() -> None:
    assert post()["allocation"] == post()["allocation"]


def equity_exposure(body: dict) -> float:
    """Weight in stocks plus mixed funds (the mixed composite holds 50 % equities)."""
    return sum(a["weight"] for a in body["allocation"] if a["category"] in ("stocks", "mixed"))


def test_adverse_political_context_lowers_equity_exposure() -> None:
    neutral = equity_exposure(post(context={"political": 0, "macro": 0}))
    adverse = equity_exposure(post(context={"political": -1, "macro": 0}))
    assert adverse < neutral


def test_switches_off_remove_penalty_and_horizon_modulation() -> None:
    body = post(switches={"fuzzy": False, "context": False}, profile={**PROFILE, "horizon_years": 1})
    tech = body["technical"]
    assert tech["m_h"] == 1.0 and tech["lambda_eff"] == tech["lambda_base"]
    assert tech["score"]["penalty_term"] == 0 and tech["score"]["fuzzy_reward"] == 0
    assert tech["score"]["sigma_max"] is None
    assert all(p["context_adj"] == 0 and p["sigma_adj"] == p["sigma"] for p in tech["params"])
    assert not any(r["kind"] == "context" for r in tech["rules"])


def test_missing_absorption_data_is_declared_as_assumption() -> None:
    body = post(profile={"amount": 5000, "risk_profile": "conservador", "horizon_label": "largo"})
    assert body["technical"]["absorption"]["assumed"] is True
    assert any("capacidad media" in a for a in body["assumptions"])
    assert any("neutral" in a for a in body["assumptions"])


@pytest.mark.parametrize(
    "profile",
    [{**PROFILE, "amount": 0}, {**PROFILE, "risk_profile": "temerario"},
     {**PROFILE, "horizon_label": "largo"}, {k: v for k, v in PROFILE.items() if k != "horizon_years"}],
)
def test_invalid_profile_is_422(profile: dict) -> None:
    assert client.post("/api/recommend", json={"profile": profile}).status_code == 422


def test_context_out_of_range_is_422() -> None:
    res = client.post("/api/recommend", json={"profile": PROFILE, "context": {"political": -2}})
    assert res.status_code == 422


def test_context_defaults_are_neutral_with_spanish_labels() -> None:
    body = client.get("/api/context/defaults").json()
    assert [f["id"] for f in body["factors"]] == ["political", "macro"]
    assert all(f["value"] == 0 for f in body["factors"])
    assert body["factors"][0]["label"] == "Panorama político"


def test_market_estimates_report_sources() -> None:
    body = client.get("/api/market/estimates").json()
    assert [c["category"] for c in body["categories"]] == ["stocks", "mixed", "debt", "bonds", "term"]
    assert {c["source"] for c in body["categories"]} <= {"data", "prior"}
    assert len(body["correlation"]) == 5


def test_full_flow_text_to_recommendation() -> None:
    text = ("Tengo S/ 5000 de mis S/ 20000, no me gusta arriesgar y no los necesito en unos 3 años; "
            "tengo 4 meses de colchón")
    interpreted = client.post("/api/interpret", json={"conversation": [{"role": "user", "content": text}]}).json()
    assert interpreted["complete"]
    profile = {k: v for k, v in interpreted["profile"].items() if k != "lambda_base" and v is not None}
    body = post(profile=profile)
    assert body["technical"]["lambda_base"] == interpreted["profile"]["lambda_base"] == 2.0
    assert round(sum(a["amount"] for a in body["allocation"]), 2) == 5000.00
    assert 3 <= len(body["explanation"]["paragraphs"]) <= 6


def test_interpreted_profile_can_be_posted_as_is() -> None:
    text = "Quiero invertir S/ 8000 a largo plazo, acepto riesgo si gano más. Tengo 30 mil ahorrados y prefiero no decir lo de los meses"
    interpreted = client.post("/api/interpret", json={"conversation": [{"role": "user", "content": text}]}).json()
    assert interpreted["complete"] is True
    res = client.post("/api/recommend", json={"profile": interpreted["profile"], "seed": 3})
    assert res.status_code == 200
    assert sum(a["amount"] for a in res.json()["allocation"]) == pytest.approx(8000.0)
