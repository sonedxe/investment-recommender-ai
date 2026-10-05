"""Pruebas de integración de la API (flujo de punta a punta, sección 9.2)."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

TEXTO_COMPLETO = (
    "quiero invertir S/ 5000 de mis S/ 20000 de ahorro, no me gusta arriesgar "
    "mucho, no los necesitaré por unos 3 años y tengo un fondo de emergencia "
    "de 4 meses"
)

PERFIL = {
    "monto_invertir": 5000,
    "horizonte_anios": 3,
    "lambda_base": 2.0,
    "ahorro_total": 20000,
    "cobertura_emergencia_meses": 4,
}


def test_interpret_completo() -> None:
    res = client.post("/api/interpret", json={"texto": TEXTO_COMPLETO})
    assert res.status_code == 200
    body = res.json()
    assert body["completo"]
    assert body["monto_invertir"] == 5000
    assert body["lambda_base"] == 2.0


def test_interpret_incompleto_devuelve_pregunta() -> None:
    res = client.post("/api/interpret", json={"texto": "quiero invertir"})
    assert res.status_code == 200
    body = res.json()
    assert not body["completo"]
    assert body["pregunta_aclaracion"]


def test_recommend_flujo_completo() -> None:
    """Etapas 3-7 del flujo: la respuesta trae portafolio, explicación y detalle."""
    res = client.post("/api/recommend", json={"perfil": PERFIL, "seed": 42})
    assert res.status_code == 200
    body = res.json()

    # Portafolio: 5 categorías, pesos válidos.
    assert len(body["portafolio"]) == 5
    pesos = [p["peso"] for p in body["portafolio"]]
    assert sum(pesos) == pytest.approx(1.0, abs=1e-6)
    assert all(w >= 0 for w in pesos)

    # Explicación en lenguaje simple con el cierre obligatorio.
    assert "educativa" in body["explicacion"]
    assert body["modo_explicacion"] in {"offline", "api"}

    # Detalle técnico de todos los módulos.
    assert body["difuso"]["lambda_ef"] > 0
    assert body["resultado"]["sigma_portafolio"] >= 0
    assert len(body["resultado"]["historial_convergencia"]) == 100
    assert len(body["mercado"]["covarianza"]) == 5


def test_recommend_contexto_adverso_desplaza_a_renta_fija() -> None:
    """Efecto esperado de 4.6.4: con política adversa, menos renta variable."""
    base = client.post("/api/recommend", json={"perfil": PERFIL, "seed": 42}).json()
    adverso = client.post(
        "/api/recommend",
        json={"perfil": PERFIL, "contexto": {"s_pol": -1, "s_mac": 0}, "seed": 42},
    ).json()
    rv_base = base["portafolio"][0]["peso"] + base["portafolio"][1]["peso"]
    rv_adv = adverso["portafolio"][0]["peso"] + adverso["portafolio"][1]["peso"]
    assert rv_adv <= rv_base + 1e-6


def test_recommend_ablacion_sin_modulos() -> None:
    """Sección 4.7: con ambos interruptores OFF, fitness = modelo base 5.1."""
    res = client.post(
        "/api/recommend",
        json={
            "perfil": PERFIL,
            "interruptores": {"difuso": False, "contexto": False},
            "seed": 42,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["difuso"]["m_H"] == 1.0
    assert body["difuso"]["sigma_max"] == 8.0
    assert all(p["c_ajuste"] == 0.0 for p in body["portafolio"])


def test_recommend_valida_entrada() -> None:
    """Entrada inválida -> 422 (monto negativo, lambda fuera de rango)."""
    res = client.post(
        "/api/recommend",
        json={"perfil": {**PERFIL, "monto_invertir": -100}},
    )
    assert res.status_code == 422


def test_categories() -> None:
    res = client.get("/api/categories")
    assert res.status_code == 200
    body = res.json()
    assert len(body["categorias"]) == 5
    # mu calibrada con datos reales (AAFMP 2019-2025, ver ai/reference_data.py)
    assert body["categorias"][0]["mu_referencia"] == 0.079471
