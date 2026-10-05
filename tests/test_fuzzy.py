"""Pruebas del módulo difuso contra los ejemplos numéricos del informe v1.1."""

import pytest

from ai.reference_data import SIGMA_MAX_SIN_DIFUSO
from ai.uncertainty import fuzzy


def test_horizonte_ejemplo_informe_h_2_5() -> None:
    """Sección 4.5.1: H = 2.5 años -> m_H ≈ 1.30 y lambda_ef = 2 * 1.3 = 2.6."""
    memb = fuzzy.membresias_horizonte(2.5)
    assert memb["corto"] == pytest.approx(0.25)
    assert memb["mediano"] == pytest.approx(0.1667, abs=1e-3)
    assert memb["largo"] == 0.0
    m_H = fuzzy.multiplicador_horizonte(memb)
    assert m_H == pytest.approx(1.30, abs=1e-2)

    res = fuzzy.evaluar_perfil(lambda_base=2.0, horizonte_anios=2.5)
    assert res.lambda_ef == pytest.approx(2.6, abs=1e-2)


def test_horizonte_etiqueta_cualitativa() -> None:
    """Sección 4.5.1: una etiqueta asigna pertenencia 1 a su conjunto."""
    res = fuzzy.evaluar_perfil(lambda_base=1.0, horizonte_etiqueta="largo")
    assert res.pertenencias["horizonte"] == {"corto": 0.0, "mediano": 0.0, "largo": 1.0}
    assert res.m_H == pytest.approx(0.7)
    assert res.lambda_ef == pytest.approx(0.7)


def test_capacidad_absorcion_ejemplo_informe() -> None:
    """Sección 4.5.2: r = 0.25 y E = 3 -> CA ≈ 0.54 y sigma_max ≈ 10%."""
    memb_r = fuzzy.membresias_r(0.25)
    assert memb_r["bajo"] == pytest.approx(0.75)
    assert memb_r["medio"] == pytest.approx(0.1667, abs=1e-3)
    memb_E = fuzzy.membresias_E(3.0)
    assert memb_E["insuficiente"] == pytest.approx(1 / 3, abs=1e-3)
    assert memb_E["adecuada"] == pytest.approx(0.25)

    ca = fuzzy.capacidad_absorcion(memb_r, memb_E)
    assert ca == pytest.approx(0.54, abs=1e-2)

    res = fuzzy.evaluar_perfil(
        lambda_base=1.0,
        horizonte_anios=10,
        monto_invertir=5000,
        ahorro_total=20000,
        cobertura_emergencia_meses=3,
    )
    assert res.CA == pytest.approx(0.54, abs=1e-2)
    assert res.sigma_max == pytest.approx(0.10, abs=1e-2)
    assert not res.ca_asumida


def test_capacidad_absorcion_asumida_cuando_faltan_datos() -> None:
    """Sección 4.2: si el usuario declina responder, CA = Media y se declara."""
    res = fuzzy.evaluar_perfil(lambda_base=1.0, horizonte_anios=5)
    assert res.CA == pytest.approx(0.50)
    assert res.ca_asumida
    assert res.r is None and res.E is None


def test_interruptor_difuso_desactivado() -> None:
    """Sección 4.7: difuso OFF -> m_H = 1 y sigma_max = 8 (sin penalización)."""
    res = fuzzy.evaluar_perfil(
        lambda_base=2.0, horizonte_anios=1, difuso_activo=False
    )
    assert res.m_H == 1.0
    assert res.lambda_ef == 2.0
    assert res.sigma_max == SIGMA_MAX_SIN_DIFUSO


def test_pertenencias_en_rango_valido() -> None:
    for H in [0, 1, 2.5, 5, 8, 10, 30]:
        for v in fuzzy.membresias_horizonte(H).values():
            assert 0.0 <= v <= 1.0
    for r in [0, 0.2, 0.35, 0.5, 0.7, 1.0]:
        for v in fuzzy.membresias_r(r).values():
            assert 0.0 <= v <= 1.0
    for E in [0, 1, 3, 6, 12, 24]:
        for v in fuzzy.membresias_E(E).values():
            assert 0.0 <= v <= 1.0
