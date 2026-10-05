"""Módulo 5 — Reglas de contexto, factores ambientales (sección 4.6).

Ajusta las estimaciones bayesianas (mu, sigma, covarianza) con factores del
entorno que los promedios históricos no capturan por sí solos, de forma
acotada, transparente y neutral por defecto. Los factores nunca reemplazan a
los datos históricos: los ajustan como mucho en ±cmax de retorno (regla RC7).

Reglas implementadas (sección 4.6.2):
    RC1  factor global no informado -> se asume 0 (neutral), sin ajuste.
    RC2  siempre: cada categoría suma su precedente estructural b_i.
    RC3  s_pol < 0: baja el retorno y SUBE el riesgo (mayor efecto en renta
         variable).
    RC4  s_pol > 0: sube el retorno; el riesgo NO se reduce (asimetría
         prudente).
    RC5  s_mac análogo con la estabilidad macroeconómica.
    RC6  s_tend,i ajusta el retorno de cada categoría según su tendencia.
    RC7  |c_i| se recorta a c_max.

Fórmulas (sección 4.6.3, todo en decimales):
    c_i   = clip(b_i + a_pol,i*s_pol + a_mac,i*s_mac + a_tend*s_tend,i, ±c_max)
    mu'_i = mu_i + c_i
    s'_i  = s_i * (1 + k_pol,i*max(0,-s_pol) + k_mac,i*max(0,-s_mac))
    S'_ij = rho_ij * s'_i * s'_j     con rho_ij = s_ij / (s_i * s_j)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ai.reference_data import A_TEND, C_MAX, CATEGORIAS, CONTEXT_PARAMS


def _clip_factor(valor: float | None) -> float:
    """Normaliza un factor global al rango [-1, +1]; None -> 0 (RC1)."""
    if valor is None:
        return 0.0
    return float(np.clip(valor, -1.0, 1.0))


@dataclass
class ContextoResult:
    """Salida del módulo de contexto (contrato de la sección 4.7)."""

    c: list[float]                       # ajuste de retorno por categoría
    mu_aj: list[float]                   # retornos ajustados
    sigma_aj: list[float]                # riesgos ajustados
    covarianza_aj: list[list[float]]     # covarianza ajustada (5x5)
    s_pol: float = 0.0
    s_mac: float = 0.0
    activo: bool = True                  # False si el interruptor está apagado
    factores: dict[str, dict[str, float]] = field(default_factory=dict)


def apply_context(
    mu: list[float],
    sigma: list[float],
    covarianza: list[list[float]],
    s_tend: list[float] | None = None,
    s_pol: float | None = None,
    s_mac: float | None = None,
    contexto_activo: bool = True,
) -> ContextoResult:
    """Aplica las reglas de contexto sobre las estimaciones de mercado.

    Con `contexto_activo=False` (interruptor de ablación, sección 4.7):
    c_i = 0 y sigma' = sigma, es decir, las estimaciones pasan sin cambios.
    """
    n = len(mu)
    s_pol_v = _clip_factor(s_pol)
    s_mac_v = _clip_factor(s_mac)
    tend = list(s_tend) if s_tend is not None else [0.0] * n

    mu_arr = np.asarray(mu, dtype=float)
    sigma_arr = np.asarray(sigma, dtype=float)
    cov_arr = np.asarray(covarianza, dtype=float)

    if not contexto_activo:
        return ContextoResult(
            c=[0.0] * n,
            mu_aj=mu_arr.tolist(),
            sigma_aj=sigma_arr.tolist(),
            covarianza_aj=cov_arr.tolist(),
            s_pol=s_pol_v,
            s_mac=s_mac_v,
            activo=False,
        )

    c: list[float] = []
    sigma_aj: list[float] = []
    factores: dict[str, dict[str, float]] = {}

    for i, cat in enumerate(CATEGORIAS[:n]):
        p = CONTEXT_PARAMS[cat]
        # RC2 + RC3/RC4 + RC5 + RC6: ajuste bruto del retorno.
        c_bruto = (
            p["b"]
            + p["a_pol"] * s_pol_v
            + p["a_mac"] * s_mac_v
            + A_TEND * float(np.clip(tend[i], -1.0, 1.0))
        )
        c_i = float(np.clip(c_bruto, -C_MAX, C_MAX))  # RC7
        c.append(c_i)
        # RC3/RC5: el riesgo solo sube con factores adversos (asimetría prudente).
        sigma_i = float(
            sigma_arr[i]
            * (1.0 + p["k_pol"] * max(0.0, -s_pol_v) + p["k_mac"] * max(0.0, -s_mac_v))
        )
        sigma_aj.append(sigma_i)
        factores[cat] = {
            "b": p["b"],
            "aporte_politico": p["a_pol"] * s_pol_v,
            "aporte_macro": p["a_mac"] * s_mac_v,
            "aporte_tendencia": A_TEND * float(np.clip(tend[i], -1.0, 1.0)),
            "c_final": c_i,
        }

    mu_aj = mu_arr + np.asarray(c)

    # Covarianza ajustada preservando las correlaciones: S'_ij = rho_ij s'_i s'_j.
    with np.errstate(divide="ignore", invalid="ignore"):
        denom = np.outer(sigma_arr, sigma_arr)
        rho = np.where(denom > 0, cov_arr / denom, 0.0)
    np.fill_diagonal(rho, 1.0)
    cov_aj = rho * np.outer(sigma_aj, sigma_aj)

    return ContextoResult(
        c=c,
        mu_aj=mu_aj.tolist(),
        sigma_aj=sigma_aj,
        covarianza_aj=cov_aj.tolist(),
        s_pol=s_pol_v,
        s_mac=s_mac_v,
        activo=True,
        factores=factores,
    )
