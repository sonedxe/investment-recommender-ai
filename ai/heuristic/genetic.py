"""Módulo 3 — Algoritmo heurístico: algoritmo genético (sección 4.4).

Resuelve el problema de optimización combinatoria de encontrar los pesos
w1..w5 que maximizan la función de aptitud de la sección 5.2 del informe:

    Fitness'(P) = sum_i w_i * mu'_i
                  - lambda_ef * sigma'(P)
                  - phi * max(0, sigma'(P) - sigma_max)^2

    con sigma'(P) = sqrt( sum_ij w_i w_j S'_ij )

sujeto a las restricciones duras: sum(w) = 1 y w_i >= 0 (sin posiciones
negativas ni apalancamiento).

Conceptos (sección 4.4):
    Gen         = el peso (%) asignado a una categoría de inversión.
    Cromosoma   = un portafolio completo: los 5 genes, sumando 100%.
    Población   = conjunto de portafolios candidatos que compiten entre sí.
    Generación  = una vuelta del ciclo evaluar -> seleccionar -> cruzar -> mutar.

Parámetros por defecto (sección 4.4): población 100, 100 generaciones,
mutación ~10%, selección por torneo, cruce por promedio ponderado con
normalización a 100%, elitismo (los 2 mejores pasan intactos).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ai.reference_data import PHI, SIGMA_MAX_SIN_DIFUSO

N_CATEGORIAS = 5


@dataclass
class GeneticResult:
    """Salida del algoritmo genético (contrato de la sección 4.7)."""

    pesos: list[float]                  # w1..w5 (suman 1)
    fitness: float                      # Fitness' del mejor portafolio
    E_portafolio: float                 # retorno histórico: sum(w_i * mu_i) SIN ajuste contextual
    C_contexto: float                   # término contextual: sum(w_i * c_i)
    sigma_portafolio: float             # riesgo con covarianza ajustada
    penalizacion: float                 # phi * max(0, sigma' - sigma_max)^2
    historial_convergencia: list[float] = field(default_factory=list)
    generaciones: int = 0
    poblacion: int = 0


def _normalizar(w: np.ndarray) -> np.ndarray:
    """Proyecta un cromosoma al simplex: w_i >= 0 y sum(w) = 1."""
    w = np.clip(np.asarray(w, dtype=float), 0.0, None)
    total = w.sum()
    if total <= 0:
        return np.full(N_CATEGORIAS, 1.0 / N_CATEGORIAS)
    return w / total


def fitness_portafolio(
    w: np.ndarray,
    mu_aj: np.ndarray,
    cov_aj: np.ndarray,
    lambda_ef: float,
    sigma_max: float,
    mu_base: np.ndarray | None = None,
    c: np.ndarray | None = None,
    phi: float = PHI,
) -> tuple[float, dict[str, float]]:
    """Evalúa la función de aptitud ampliada (sección 5.2).

    Devuelve (fitness, descomposición) con la descomposición usada por el
    panel técnico: retorno histórico, término contextual, riesgo y
    penalización por exceder la volatilidad tolerable.
    """
    w = np.asarray(w, dtype=float)
    mu_aj = np.asarray(mu_aj, dtype=float)
    cov_aj = np.asarray(cov_aj, dtype=float)

    retorno_aj = float(w @ mu_aj)
    sigma_p = float(np.sqrt(max(w @ cov_aj @ w, 0.0)))
    exceso = max(0.0, sigma_p - sigma_max)
    penalizacion = phi * exceso**2
    fitness = retorno_aj - lambda_ef * sigma_p - penalizacion

    if mu_base is None:
        mu_base = mu_aj
    if c is None:
        c = mu_aj - np.asarray(mu_base, dtype=float)
    detalle = {
        "retorno_historico": float(w @ np.asarray(mu_base, dtype=float)),
        "termino_contextual": float(w @ np.asarray(c, dtype=float)),
        "riesgo": sigma_p,
        "penalizacion": penalizacion,
    }
    return fitness, detalle


def optimize_portfolio(
    mu_aj: list[float],
    cov_aj: list[list[float]],
    lambda_ef: float,
    sigma_max: float = SIGMA_MAX_SIN_DIFUSO,
    mu_base: list[float] | None = None,
    c: list[float] | None = None,
    phi: float = PHI,
    poblacion_size: int = 100,
    generaciones: int = 100,
    tasa_mutacion: float = 0.10,
    torneo_k: int = 3,
    elitismo: int = 2,
    seed: int | None = None,
) -> GeneticResult:
    """Evoluciona una población de portafolios hasta converger.

    Entradas (contrato 4.7): lambda_ef, sigma_max, phi, mu_aj[5],
    sigma_aj[5] (implícita en cov_aj), covarianza_aj[5x5]. `mu_base` y `c`
    solo se usan para reportar la descomposición del fitness (retorno
    histórico vs. término contextual); si no se pasan, se infieren.

    Salida: { pesos, fitness, E_portafolio, C_contexto, sigma_portafolio,
    historial_convergencia }.
    """
    rng = np.random.default_rng(seed)
    mu_aj_arr = np.asarray(mu_aj, dtype=float)
    cov_arr = np.asarray(cov_aj, dtype=float)
    mu_base_arr = np.asarray(mu_base, dtype=float) if mu_base is not None else mu_aj_arr
    c_arr = np.asarray(c, dtype=float) if c is not None else (mu_aj_arr - mu_base_arr)

    # Población inicial: Dirichlet(1) => portafolios uniformes en el simplex.
    poblacion = rng.dirichlet(np.ones(N_CATEGORIAS), size=poblacion_size)

    historial: list[float] = []

    def evaluar(w: np.ndarray) -> float:
        f, _ = fitness_portafolio(
            w, mu_aj_arr, cov_arr, lambda_ef, sigma_max,
            mu_base=mu_base_arr, c=c_arr, phi=phi,
        )
        return f

    for _ in range(generaciones):
        fitnesses = np.apply_along_axis(evaluar, 1, poblacion)
        orden = np.argsort(fitnesses)[::-1]
        historial.append(float(fitnesses[orden[0]]))

        # Elitismo: los mejores pasan intactos a la siguiente generación.
        nueva = [poblacion[i] for i in orden[:elitismo]]

        while len(nueva) < poblacion_size:
            # Selección por torneo: se compara un subgrupo aleatorio y gana
            # el de mayor fitness.
            def torneo() -> np.ndarray:
                idx = rng.choice(poblacion_size, size=torneo_k, replace=False)
                mejor = max(idx, key=lambda i: fitnesses[i])
                return poblacion[mejor]

            p1, p2 = torneo(), torneo()
            # Cruce: promedio ponderado de dos portafolios ganadores.
            alpha = rng.uniform(0.0, 1.0)
            hijo = _normalizar(alpha * p1 + (1.0 - alpha) * p2)
            # Mutación (~10%): perturbación gaussiana con reajuste a 100%.
            if rng.uniform() < tasa_mutacion:
                hijo = _normalizar(hijo + rng.normal(0.0, 0.05, size=N_CATEGORIAS))
            nueva.append(hijo)

        poblacion = np.asarray(nueva)

    fitnesses = np.apply_along_axis(evaluar, 1, poblacion)
    mejor = poblacion[int(np.argmax(fitnesses))]
    fitness_final, detalle = fitness_portafolio(
        mejor, mu_aj_arr, cov_arr, lambda_ef, sigma_max,
        mu_base=mu_base_arr, c=c_arr, phi=phi,
    )

    return GeneticResult(
        pesos=[round(float(v), 6) for v in _normalizar(mejor)],
        fitness=fitness_final,
        E_portafolio=detalle["retorno_historico"],
        C_contexto=detalle["termino_contextual"],
        sigma_portafolio=detalle["riesgo"],
        penalizacion=detalle["penalizacion"],
        historial_convergencia=historial,
        generaciones=generaciones,
        poblacion=poblacion_size,
    )
