"""Pruebas del algoritmo genético (secciones 4.4 y 5)."""

import numpy as np
import pytest

from ai.heuristic import fitness_portafolio, optimize_portfolio

MU = [0.122, 0.061, 0.024, 0.065, 0.045]
SIGMA = [0.19, 0.09, 0.025, 0.035, 0.005]
COV = np.diag([s**2 for s in SIGMA]).tolist()


def test_pesos_suman_1_y_son_no_negativos() -> None:
    """Restricciones duras del modelo (sección 5.1)."""
    ga = optimize_portfolio(MU, COV, lambda_ef=1.0, sigma_max=8.0, seed=1)
    assert sum(ga.pesos) == pytest.approx(1.0, abs=1e-6)
    assert all(w >= 0 for w in ga.pesos)


def test_reproducible_con_semilla() -> None:
    a = optimize_portfolio(MU, COV, lambda_ef=1.0, sigma_max=8.0, seed=7)
    b = optimize_portfolio(MU, COV, lambda_ef=1.0, sigma_max=8.0, seed=7)
    assert a.pesos == b.pesos
    assert a.historial_convergencia == b.historial_convergencia


def test_convergencia_mejora_el_fitness() -> None:
    ga = optimize_portfolio(MU, COV, lambda_ef=1.0, sigma_max=8.0, seed=3)
    hist = ga.historial_convergencia
    assert len(hist) == 100
    assert hist[-1] >= hist[0]
    # El fitness reportado es el del mejor individuo de la última generación.
    assert ga.fitness == pytest.approx(hist[-1], abs=1e-9)


def test_perfil_conservador_evita_renta_variable() -> None:
    """Con lambda alto, el riesgo del portafolio debe ser bajo (ejemplo 5.1)."""
    ga = optimize_portfolio(MU, COV, lambda_ef=2.0, sigma_max=8.0, seed=42)
    assert ga.sigma_portafolio < 0.05
    assert ga.pesos[0] < 0.10  # fondos de acciones casi fuera


def test_perfil_agresivo_prefiere_mayor_retorno() -> None:
    ga = optimize_portfolio(MU, COV, lambda_ef=0.2, sigma_max=8.0, seed=42)
    assert ga.E_portafolio > 0.08
    assert ga.pesos[0] > 0.5  # fondos de acciones dominan


def test_penalizacion_por_volatilidad_excedida() -> None:
    """Sección 5.2: la penalización cuadrática limita sigma' cerca de sigma_max."""
    ga = optimize_portfolio(MU, COV, lambda_ef=0.2, sigma_max=0.05, seed=42)
    # Aunque el usuario sea agresivo, el riesgo queda contenido cerca del 5%.
    assert ga.sigma_portafolio < 0.08
    assert ga.penalizacion >= 0.0


def test_descomposicion_del_fitness() -> None:
    """Fitness = retorno_ajustado - lambda*sigma - penalización (sección 5.2)."""
    w = np.full(5, 0.2)
    c = [0.005, 0.003, 0.0, 0.002, -0.003]
    mu_aj = [m + ci for m, ci in zip(MU, c)]
    fitness, det = fitness_portafolio(
        w, mu_aj, COV, lambda_ef=1.0, sigma_max=8.0, mu_base=MU, c=c
    )
    esperado = (
        det["retorno_historico"] + det["termino_contextual"]
        - 1.0 * det["riesgo"] - det["penalizacion"]
    )
    assert fitness == pytest.approx(esperado, abs=1e-9)
    assert det["termino_contextual"] == pytest.approx(np.mean(c), abs=1e-9)
