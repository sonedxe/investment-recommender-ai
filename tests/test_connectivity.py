"""Pruebas de conectividad del esqueleto.

Verifican que el backend arranca y que sus tres módulos de IA responden.
"""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_ping_raises_all_modules() -> None:
    res = client.get("/api/ping")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert set(body["modules"]) == {"generative", "heuristic", "uncertainty"}
    for info in body["modules"].values():
        assert info["status"] == "ok"


def test_ping_generative_reports_mode() -> None:
    res = client.get("/api/ping")
    mode = res.json()["modules"]["generative"]["mode"]
    assert mode in {"api", "offline"}

def test_ping_heuristic_reports_implemented_components() -> None:
    heuristic = client.get("/api/ping").json()["modules"]["heuristic"]
    assert heuristic["components"] == ["genetic_algorithm"]
    assert "planned" not in heuristic
