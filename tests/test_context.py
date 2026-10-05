"""Pruebas de las reglas de contexto contra el ejemplo 4.6.4 del informe."""

import numpy as np
import pytest

from ai.reference_data import C_MAX
from ai.uncertainty import apply_context

# Valores de referencia del ejemplo 4.6.4 (sigma en el punto medio del Anexo A).
MU_BASE = [0.122, 0.061, 0.024, 0.065, 0.045]
SIGMA_BASE = [0.19, 0.09, 0.025, 0.035, 0.005]
COV_BASE = np.diag([s**2 for s in SIGMA_BASE]).tolist()  # independientes

# Resultados esperados con s_pol = -1, s_mac = 0, tendencias 0.
MU_ESPERADO = [0.097, 0.049, 0.019, 0.057, 0.042]
SIGMA_ESPERADO = [0.285, 0.1125, 0.0275, 0.042, 0.005]
C_ESPERADO = [-0.025, -0.012, -0.005, -0.008, -0.003]


def test_ejemplo_4_6_4_panorama_politico_adverso() -> None:
    ctx = apply_context(MU_BASE, SIGMA_BASE, COV_BASE, s_tend=[0] * 5, s_pol=-1, s_mac=0)
    assert ctx.c == pytest.approx(C_ESPERADO, abs=1e-6)
    assert ctx.mu_aj == pytest.approx(MU_ESPERADO, abs=1e-6)
    assert ctx.sigma_aj == pytest.approx(SIGMA_ESPERADO, abs=1e-6)


def test_factor_no_informado_es_neutral_rc1() -> None:
    """RC1: sin s_pol ni s_mac solo queda el precedente estructural b_i."""
    ctx = apply_context(MU_BASE, SIGMA_BASE, COV_BASE, s_tend=[0] * 5)
    b = [0.005, 0.003, 0.0, 0.002, -0.003]
    assert ctx.c == pytest.approx(b, abs=1e-9)
    assert ctx.sigma_aj == pytest.approx(SIGMA_BASE, abs=1e-9)


def test_asimetria_prudente_rc4() -> None:
    """RC4: contexto favorable sube el retorno pero NO reduce el riesgo."""
    ctx = apply_context(MU_BASE, SIGMA_BASE, COV_BASE, s_tend=[0] * 5, s_pol=1, s_mac=1)
    # El retorno no baja en ninguna categoría y sube en renta variable.
    assert all(m >= b - 1e-12 for m, b in zip(ctx.mu_aj, MU_BASE))
    assert ctx.mu_aj[0] > MU_BASE[0]  # fondos de acciones claramente mejoran
    # La propiedad clave de la asimetría prudente: el riesgo NO se reduce.
    assert ctx.sigma_aj == pytest.approx(SIGMA_BASE, abs=1e-9)


def test_tope_de_influencia_rc7() -> None:
    """RC7: |c_i| nunca supera c_max aun con todos los factores al máximo."""
    ctx = apply_context(
        MU_BASE, SIGMA_BASE, COV_BASE, s_tend=[1] * 5, s_pol=-1, s_mac=-1
    )
    assert all(abs(c) <= C_MAX + 1e-12 for c in ctx.c)


def test_tendencia_ajusta_retorno_rc6() -> None:
    """RC6: tendencia positiva sube el retorno de esa categoría."""
    ctx = apply_context(MU_BASE, SIGMA_BASE, COV_BASE, s_tend=[1, 0, 0, 0, 0])
    # c_acciones = b(0.005) + a_tend(0.015) * 1 = 0.020
    assert ctx.c[0] == pytest.approx(0.020, abs=1e-9)


def test_interruptor_contexto_desactivado() -> None:
    """Sección 4.7: contexto OFF -> c_i = 0 y sigma' = sigma."""
    ctx = apply_context(
        MU_BASE, SIGMA_BASE, COV_BASE, s_tend=[1] * 5, s_pol=-1, contexto_activo=False
    )
    assert ctx.c == [0.0] * 5
    assert ctx.mu_aj == MU_BASE
    assert ctx.sigma_aj == SIGMA_BASE
    assert not ctx.activo


def test_correlaciones_se_preservan() -> None:
    """Sección 4.6.3: el ajuste de covarianza preserva rho_ij."""
    cov = np.array(
        [
            [0.0361, 0.00855, 0.0, 0.0, 0.0],
            [0.00855, 0.0081, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.000625, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.001225, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.000025],
        ]
    )
    ctx = apply_context(MU_BASE, SIGMA_BASE, cov.tolist(), s_tend=[0] * 5, s_pol=-1)
    cov_aj = np.array(ctx.covarianza_aj)
    rho_antes = cov[0, 1] / (SIGMA_BASE[0] * SIGMA_BASE[1])
    rho_despues = cov_aj[0, 1] / (ctx.sigma_aj[0] * ctx.sigma_aj[1])
    assert rho_despues == pytest.approx(rho_antes, abs=1e-6)
