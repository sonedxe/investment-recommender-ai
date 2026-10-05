"""Módulo 2 — Razonamiento bajo incertidumbre (bayesiano).

Estima, para cada una de las 5 categorías de inversión del mercado peruano:
- el retorno esperado anual (mu) y el riesgo anual (sigma),
- la matriz de covarianza entre categorías,
- un indicador de tendencia reciente s_tend en [-1, +1] (sección 4.3).

El componente "bayesiano" consiste en una actualización conjugada sobre un
modelo normal: la estimación previa (prior, calibrada con datos reales — ver
`ai/reference_data.py`) se combina con los datos históricos de forma
ponderada, en vez de mantener valores fijos indefinidamente. Cuando llega una
observación nueva (`bayesian_update`), la estimación se desplaza hacia el
dato nuevo con un peso proporcional a la confianza acumulada.

Datos históricos (oct-2026): series REALES documentadas y citables en
`ai/data/market_data.py` — rentabilidades anuales de fondos mutuos por tipo
(AAFMP/SMV 2019-2025), tasa de depósitos (Banco Mundial/FMI-IFS-BCRP y
SBS-BBVA) y rendimiento del bono soberano a 10 años (BCRP vía CEIC/TE; MEF).
Detalle y citas: `docs/FUENTES_DE_DATOS.md`.

La matriz de covarianza se construye como cov_ij = rho_ij * sigma_i * sigma_j,
con rho de la matriz documentada `CORRELACIONES` (bloque de fondos empírico
sobre las series AAFMP; BTP/depósito como parámetros de diseño documentados),
porque las series reales no comparten todos los años calendario.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ai.data import historial_decimal
from ai.reference_data import CATEGORIAS, CORRELACIONES, MU_REF, SIGMA_REF

# Confianza del prior expresada como número de observaciones equivalentes.
# Con n0 ≈ n_datos, el posterior queda cerca del promedio entre prior y datos.
N0: float = 7.0


@dataclass
class EstimacionActivo:
    """Estimación puntual de una categoría de inversión."""

    activo: str
    mu: float          # retorno esperado anual (decimal)
    sigma: float       # riesgo anual (decimal)
    s_tend: float      # tendencia reciente en [-1, +1]
    n_obs: int = 0     # observaciones incorporadas (para futuras actualizaciones)


@dataclass
class EstimacionMercado:
    """Salida del módulo: estimaciones por categoría + covarianza."""

    activos: list[EstimacionActivo]
    covarianza: list[list[float]]  # matriz 5x5 en el orden de CATEGORIAS
    historial: dict[str, list[float]] = field(default_factory=dict)

    def vector_mu(self) -> list[float]:
        return [a.mu for a in self.activos]

    def vector_sigma(self) -> list[float]:
        return [a.sigma for a in self.activos]

    def vector_s_tend(self) -> list[float]:
        return [a.s_tend for a in self.activos]


# Historial real de referencia cargado una sola vez (reemplazable vía
# `estimate(historial=...)` o actualizable con `bayesian_update`).
HISTORIAL_REF: dict[str, list[float]] = historial_decimal()


def _tendencia(serie: list[float], mu: float, sigma: float) -> float:
    """Indicador de tendencia reciente: s_tend = clip((r_12m - mu)/sigma, ±1).

    Compara el retorno más reciente de la serie (equivalente a los últimos
    12 meses) con el promedio histórico. Si no hay datos suficientes,
    devuelve 0 (neutral).
    """
    if len(serie) < 2 or sigma <= 0:
        return 0.0
    r_12m = float(serie[-1])
    return float(np.clip((r_12m - mu) / sigma, -1.0, 1.0))


def estimate(historial: dict[str, list[float]] | None = None) -> EstimacionMercado:
    """Estima mu, sigma, covarianza y tendencia de las 5 categorías.

    Actualización bayesiana conjugada (modelo normal con media desconocida):
        mu_post = (n0 * mu_prior + n * media_datos) / (n0 + n)
    donde mu_prior es el valor calibrado de `MU_REF` y n0 la confianza del
    prior. Como los priors se calibraron con las mismas series de referencia,
    por defecto mu_post coincide con ellas. El riesgo se toma de la desviación
    muestral de los datos, y la covarianza se construye con las correlaciones
    documentadas (`CORRELACIONES`) y las sigmas estimadas.
    """
    hist = historial if historial is not None else HISTORIAL_REF
    activos: list[EstimacionActivo] = []

    for cat in CATEGORIAS:
        datos = np.asarray(hist[cat], dtype=float)
        n = float(datos.size)
        media_datos = float(datos.mean()) if n else MU_REF[cat]
        mu_post = (N0 * MU_REF[cat] + n * media_datos) / (N0 + n) if (N0 + n) else MU_REF[cat]
        sigma_post = float(datos.std(ddof=1)) if n >= 2 else SIGMA_REF[cat]
        s_tend = _tendencia(datos.tolist(), mu_post, sigma_post)
        activos.append(
            EstimacionActivo(activo=cat, mu=mu_post, sigma=sigma_post, s_tend=s_tend, n_obs=int(n))
        )

    # Covarianza: cov_ij = rho_ij * sigma_i * sigma_j con rho documentada.
    sigma_vec = np.asarray([a.sigma for a in activos])
    rho = np.asarray(CORRELACIONES, dtype=float)
    covarianza = (rho * np.outer(sigma_vec, sigma_vec)).tolist()

    return EstimacionMercado(activos=activos, covarianza=covarianza, historial=hist)


def bayesian_update(
    estimacion: EstimacionActivo,
    nueva_observacion: float,
    sigma_observacion: float | None = None,
) -> EstimacionActivo:
    """Incorpora una observación nueva a la estimación de una categoría.

    Actualización conjugada normal-normal sobre la media: la estimación previa
    actúa como prior con peso n0 + n_obs, y el dato nuevo aporta peso 1 (o
    más, si se declara una sigma de observación distinta del sigma estimado).

    Devuelve una NUEVA EstimacionActivo (no muta la recibida).
    """
    peso_prior = N0 + estimacion.n_obs
    if sigma_observacion is not None and sigma_observacion > 0:
        # Pesos por precisión (1/varianza) si se conoce la incertidumbre del dato.
        var_prior = (estimacion.sigma**2) / max(peso_prior, 1.0)
        var_obs = sigma_observacion**2
        mu_post = (estimacion.mu / var_prior + nueva_observacion / var_obs) / (
            1.0 / var_prior + 1.0 / var_obs
        )
    else:
        mu_post = (peso_prior * estimacion.mu + nueva_observacion) / (peso_prior + 1.0)
    return EstimacionActivo(
        activo=estimacion.activo,
        mu=mu_post,
        sigma=estimacion.sigma,
        s_tend=estimacion.s_tend,
        n_obs=estimacion.n_obs + 1,
    )
