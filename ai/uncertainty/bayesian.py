"""Módulo 2 — Razonamiento bajo incertidumbre (bayesiano).

Estima, para cada una de las 5 categorías de inversión del mercado peruano:
- el retorno esperado anual (mu) y el riesgo anual (sigma),
- la matriz de covarianza entre categorías,
- un indicador de tendencia reciente s_tend en [-1, +1] (sección 4.3).

El componente "bayesiano" consiste en una actualización conjugada sobre un
modelo normal: la estimación previa (prior, tomada del Anexo A) se combina
con los datos históricos de forma ponderada, en vez de mantener valores fijos
indefinidamente. Cuando llega una observación nueva (`bayesian_update`), la
estimación se desplaza hacia el dato nuevo con un peso proporcional a la
confianza acumulada.

Datos históricos: el sistema incluye series anuales de referencia (10 años,
2015-2024) construidas de forma documentada para reproducir exactamente las
medias y desviaciones del Anexo A (ver `_build_historial`). Son datos de
trabajo reemplazables por series reales (AAFMP, BCRP) sin tocar el código del
módulo: basta pasar otro `historial` a `estimate()`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ai.reference_data import CATEGORIAS, MU_REF, SIGMA_REF

# Años de las series de referencia (el último año representa los "últimos
# 12 meses" para el indicador de tendencia).
ANIOS_HISTORIAL: list[int] = list(range(2015, 2025))

# Patrones de desviaciones estandarizadas (media muestral 0) por categoría.
# Se normalizan en `_build_historial` para que su desviación muestral sea 1 y
# luego se escalan con mu/sigma de referencia; así la media y el riesgo de
# cada serie coinciden exactamente con el Anexo A por construcción.
_Z_PATTERNS: dict[str, list[float]] = {
    "fondos_acciones": [-1.4, -0.8, -0.3, 0.1, 0.4, 0.6, -0.5, 0.9, 1.2, -0.2],
    "fondos_mixtos": [-1.0, -0.6, -0.2, 0.2, 0.3, 0.5, -0.3, 0.6, 0.8, -0.3],
    "fondos_deuda": [0.3, 0.5, 0.6, 0.2, -0.1, -0.4, -0.6, 0.1, -0.2, -0.4],
    "bonos_soberanos": [0.2, 0.4, 0.5, 0.3, -0.2, -0.5, -0.7, 0.2, 0.1, -0.3],
    "deposito_plazo_fijo": [0.1, 0.2, 0.2, 0.1, 0.0, -0.1, -0.1, -0.2, -1.0, 0.9],
}

# Confianza del prior expresada como número de observaciones equivalentes.
# Con n0 = n_datos, el posterior es el promedio simple entre prior y datos.
N0: float = 10.0


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


def _build_historial() -> dict[str, list[float]]:
    """Construye las series anuales de referencia (2015-2024).

    Cada serie es mu_ref + sigma_ref * z, con z normalizado a media 0 y
    desviación muestral 1; por tanto, la media y la desviación muestral de la
    serie reproducen exactamente los valores del Anexo A.
    """
    historial: dict[str, list[float]] = {}
    for cat in CATEGORIAS:
        z = np.asarray(_Z_PATTERNS[cat], dtype=float)
        z = z - z.mean()
        z = z / z.std(ddof=1)
        serie = MU_REF[cat] + SIGMA_REF[cat] * z
        historial[cat] = [round(float(v), 6) for v in serie]
    return historial


# Historial de referencia cargado una sola vez (reemplazable vía `estimate`).
HISTORIAL_REF: dict[str, list[float]] = _build_historial()


def _tendencia(serie: list[float], mu: float, sigma: float) -> float:
    """Indicador de tendencia reciente: s_tend = clip((r_12m - mu)/sigma, ±1).

    Compara el retorno de los últimos 12 meses (último dato de la serie) con
    el promedio histórico. Si no hay datos suficientes, devuelve 0 (neutral).
    """
    if len(serie) < 2 or sigma <= 0:
        return 0.0
    r_12m = float(serie[-1])
    return float(np.clip((r_12m - mu) / sigma, -1.0, 1.0))


def estimate(historial: dict[str, list[float]] | None = None) -> EstimacionMercado:
    """Estima mu, sigma, covarianza y tendencia de las 5 categorías.

    Actualización bayesiana conjugada (modelo normal con media desconocida):
        mu_post = (n0 * mu_prior + n * media_datos) / (n0 + n)
    donde mu_prior es el valor del Anexo A y n0 la confianza del prior. Como
    las series de referencia tienen media igual al prior, por defecto
    mu_post coincide exactamente con el Anexo A. El riesgo se toma de la
    desviación muestral de los datos (que incluyen ya al prior por
    construcción), y la covarianza se calcula sobre las series completas.
    """
    hist = historial if historial is not None else HISTORIAL_REF
    activos: list[EstimacionActivo] = []
    series: list[np.ndarray] = []

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
        series.append(datos)

    covarianza = np.cov(np.vstack(series), ddof=1).tolist()
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
