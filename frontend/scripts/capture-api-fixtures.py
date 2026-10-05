"""Capture real backend responses as frontend contract fixtures (offline mode, deterministic seed).

Run from the repository root:  .venv/bin/python frontend/scripts/capture-api-fixtures.py
Writes JSON files to frontend/src/api/__fixtures__/ used by the mapper and container tests.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "frontend" / "src" / "api" / "__fixtures__"
SEED = 42

os.environ["LLM_PROVIDER"] = "offline"
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.main import app  # noqa: E402

client = TestClient(app)

FIRST_TEXT = "Tengo S/ 5000 de mis S/ 20000 de ahorro, no me gusta arriesgar y no los necesito en unos 3 años"


def user(content: str) -> dict:
    return {"role": "user", "content": content}


def assistant(content: str, field: str) -> dict:
    return {"role": "assistant", "content": content, "field": field}


def post(path: str, payload: dict) -> dict:
    res = client.post(path, json=payload)
    if res.status_code != 200:
        raise SystemExit(f"{path} -> {res.status_code}: {res.text}")
    return res.json()


def get(path: str) -> dict:
    res = client.get(path)
    if res.status_code != 200:
        raise SystemExit(f"{path} -> {res.status_code}: {res.text}")
    return res.json()


def save(name: str, data: dict) -> None:
    # Compact, key-sorted JSON: deterministic diffs without one line per array element.
    (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
    print(f"saved {name}.json")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    amount_q = post("/api/interpret", {"conversation": [user("Quiero invertir sin arriesgar mucho")]})
    assert amount_q["question"]["field"] == "monto_invertir", amount_q
    save("interpret-amount-question", amount_q)

    risk_q = post("/api/interpret", {"conversation": [user("Quiero invertir S/ 5000 por 3 años")]})
    assert risk_q["question"]["options"], risk_q
    save("interpret-risk-question", risk_q)

    absorption_q = post("/api/interpret", {"conversation": [user(FIRST_TEXT)]})
    field = absorption_q["question"]["field"]
    assert field in ("ahorro_total", "cobertura_emergencia_meses"), absorption_q
    save("interpret-absorption-question", absorption_q)

    refusal = post("/api/interpret", {"conversation": [
        user(FIRST_TEXT), assistant(absorption_q["question"]["text"], field), user("Prefiero no responder"),
    ]})
    assert refusal["complete"] and refusal["absorption_assumed"], refusal
    save("interpret-refusal-complete", refusal)

    profile = {k: v for k, v in refusal["profile"].items() if v is not None}
    save("recommend-neutral", post("/api/recommend", {"profile": profile, "seed": SEED}))
    save("recommend-adverse-political", post("/api/recommend", {
        "profile": profile, "context": {"political": -1.0, "macro": 0.0}, "seed": SEED,
    }))
    save("recommend-switches-off", post("/api/recommend", {
        "profile": profile, "switches": {"fuzzy": False, "context": False}, "seed": SEED,
    }))
    # Both absorption inputs informed: exposes r, E and the RA activations (not assumed).
    save("recommend-informed-absorption", post("/api/recommend", {
        "profile": {**profile, "emergency_months": 4.0}, "seed": SEED,
    }))

    save("context-defaults", get("/api/context/defaults"))
    save("market-estimates", get("/api/market/estimates"))


if __name__ == "__main__":
    main()
