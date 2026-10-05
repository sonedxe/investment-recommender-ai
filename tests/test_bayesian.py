"""Pruebas del módulo bayesiano (sección 4.3)."""

import numpy as np
import pytest

from ai.reference_data import CATEGORIAS, MU_REF, SIGMA_REF
from ai.uncertainty.bayesian import bayesian_update, estimate


def test_estimacion_reproduce_anexo_a() -> None:
    """Las series de referencia reproducen mu y sigma del Anexo A."""
    est = estimate()
    for i, cat in enumerate(CATEGORIAS):
        assert est.activos[i].activo == cat
        assert est.activos[i].mu == pytest.approx(MU_REF[cat], abs=1e-6)
        assert est.activos[i].sigma == pytest.approx(SIGMA_REF[cat], abs=1e-6)


def test_covarianza_es_5x5_simetrica_y_definida_positiva() -> None:
    cov = np.array(estimate().covarianza)
    assert cov.shape == (5, 5)
    assert np.allclose(cov, cov.T)
    # Diagonal = varianza de cada categoría.
    for i, cat in enumerate(CATEGORIAS):
        assert cov[i, i] == pytest.approx(SIGMA_REF[cat] ** 2, rel=1e-3)
    # Toda matriz de covarianza muestral es semidefinida positiva.
    assert np.linalg.eigvalsh(cov).min() >= -1e-12


def test_tendencia_en_rango() -> None:
    est = estimate()
    for a in est.activos:
        assert -1.0 <= a.s_tend <= 1.0


def test_tendencia_detecta_racha_positiva() -> None:
    """Una serie rindiendo sobre su promedio -> s_tend > 0 (fórmula 4.3)."""
    historial = {cat: [0.05] * 11 + [0.20] for cat in CATEGORIAS}
    est = estimate(historial)
    assert all(a.s_tend > 0 for a in est.activos)


def test_actualizacion_bayesiana_se_desplaza_hacia_el_dato() -> None:
    """La actualización conjugada mueve mu hacia la nueva observación."""
    est = estimate()
    acciones = est.activos[0]
    mu_antes = acciones.mu
    actualizado = bayesian_update(acciones, nueva_observacion=0.30)
    assert mu_antes < actualizado.mu < 0.30
    assert actualizado.n_obs == acciones.n_obs + 1
    # Segunda observación en el mismo sentido acerca más.
    actualizado2 = bayesian_update(actualizado, nueva_observacion=0.30)
    assert actualizado2.mu > actualizado.mu


def test_historial_personalizado_desplaza_el_posterior() -> None:
    """Con datos nuevos consistentes, el posterior se aparta del prior."""
    historial = {cat: [MU_REF[cat] + 0.02] * 10 for cat in CATEGORIAS}
    est = estimate(historial)
    for i, cat in enumerate(CATEGORIAS):
        assert est.activos[i].mu > MU_REF[cat]
        assert est.activos[i].mu < MU_REF[cat] + 0.02  # el prior frena el salto
