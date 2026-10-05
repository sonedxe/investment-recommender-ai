"""POST /api/interpret in offline mode."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

COMPLETE = (
    "Tengo S/ 5000 de mis S/ 20000, no me gusta arriesgar y no los necesito en unos 3 años; "
    "tengo 4 meses de colchón"
)


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "offline")


def test_incomplete_text_asks_for_the_amount() -> None:
    res = client.post("/api/interpret", json={"conversation": [{"role": "user", "content": "Quiero invertir sin arriesgar mucho"}]})
    assert res.status_code == 200
    body = res.json()
    assert body["complete"] is False
    assert body["question"]["field"] == "monto_invertir"
    assert body["question"]["free_input"] is True and body["question"]["unit"] == "soles"
    assert (body["mode"], body["provider"], body["source"]) == ("offline", "offline", "offline")


def test_full_text_gives_a_complete_profile() -> None:
    res = client.post("/api/interpret", json={"conversation": [{"role": "user", "content": COMPLETE}]})
    body = res.json()
    assert body["complete"] is True and body["question"] is None
    assert body["profile"] == {
        "amount": 5000.0, "horizon_years": 3.0, "horizon_label": None, "risk_profile": "conservador",
        "lambda_base": 2.0, "total_savings": 20000.0, "emergency_months": 4.0,
    }
    assert body["evidence"]["perfil_riesgo"] == "no me gusta arriesgar"


def test_risk_question_has_five_options() -> None:
    conversation = [{"role": "user", "content": "Quiero invertir S/ 5000 por 3 años"}]
    question = client.post("/api/interpret", json={"conversation": conversation}).json()["question"]
    assert question["field"] == "perfil_riesgo"
    assert [o["value"] for o in question["options"]] == [
        "muy_conservador", "conservador", "moderado", "agresivo", "muy_agresivo",
    ]


def test_unknown_provider_placeholder_still_answers_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    body = client.post("/api/interpret", json={"conversation": [{"role": "user", "content": COMPLETE}]}).json()
    assert body["mode"] == "offline" and body["complete"]


@pytest.mark.parametrize(
    "payload",
    [{}, {"conversation": []}, {"conversation": [{"role": "assistant", "content": "hola"}]},
     {"conversation": [{"role": "user", "content": "x", "field": "edad"}]},
     {"conversation": [{"role": "system", "content": "x"}]}],
)
def test_invalid_input_is_422(payload: dict) -> None:
    res = client.post("/api/interpret", json=payload)
    assert res.status_code == 422
    assert res.json()["detail"]
