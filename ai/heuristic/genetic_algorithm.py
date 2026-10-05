"""Generational genetic algorithm with elitism and patience-based convergence."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ai.heuristic.chromosome import C_INDEX, N_CATEGORIES, check_cap, random_population
from ai.heuristic.fitness import FitnessBreakdown, FitnessInputs, evaluate, evaluate_population
from ai.heuristic.operators import (
    arithmetic_crossover,
    elite_indices,
    gaussian_mutation,
    tournament_selection,
)
from ai.shared.parameters import OptimizationParameters

IMPROVEMENT_TOLERANCE = 1e-9


@dataclass(frozen=True)
class GAResult:
    """Best individual and run history.

    ``history_best``/``history_mean`` hold one entry per population evaluated:
    index 0 is the initial population, so their length is ``generations_run + 1``.
    """

    weights: np.ndarray
    c: float
    breakdown: FitnessBreakdown
    history_best: np.ndarray
    history_mean: np.ndarray
    generations_run: int
    converged: bool
    seed: int | None
    max_weight: float


def run_ga(
    inputs: FitnessInputs,
    params: OptimizationParameters,
    seed: int | None = None,
    max_weight: float | None = None,
) -> GAResult:
    """Evolve ``[w | c]`` maximizing the extended fitness.

    Stops when the best fitness has not improved by more than 1e-9 for
    ``params.patience`` consecutive generations (``converged=True``) or after
    ``params.max_generations``. ``max_weight`` overrides the cap (ablation).
    """
    cap = params.max_weight if max_weight is None else max_weight
    check_cap(cap)
    rng = np.random.default_rng(seed)
    size = params.population_size
    n_elite = min(params.elitism, size - 1)
    n_children = size - n_elite

    # With fuzzy enabled, c starts on the absorption set (p proportional to mu_CA).
    seed_set = (inputs.universe, inputs.mu_ca) if inputs.fuzzy_enabled else (None, None)
    population = random_population(size, cap, rng, c_universe=seed_set[0], c_weights=seed_set[1])
    fitness = evaluate_population(population, inputs)
    best_index = int(np.argmax(fitness))
    history_best, history_mean = [float(fitness[best_index])], [float(fitness.mean())]
    best_value = history_best[0]
    stale, converged, generations = 0, False, 0

    while generations < params.max_generations:
        elites = population[elite_indices(fitness, n_elite)]
        n_pairs = (n_children + 1) // 2
        parents = tournament_selection(fitness, 2 * n_pairs, params.tournament_size, rng)
        child_a, child_b = arithmetic_crossover(
            population[parents[:n_pairs]], population[parents[n_pairs:]], params.crossover_rate, cap, rng
        )
        children = np.vstack([child_a, child_b])[:n_children]
        children = gaussian_mutation(
            children, params.mutation_rate, params.mutation_sigma, cap, rng, c_sigma=params.c_mutation_sigma
        )

        population = np.vstack([elites, children])
        fitness = evaluate_population(population, inputs)
        generations += 1
        best_index = int(np.argmax(fitness))
        history_best.append(float(fitness[best_index]))
        history_mean.append(float(fitness.mean()))

        if history_best[-1] > best_value + IMPROVEMENT_TOLERANCE:
            stale = 0
        else:
            stale += 1
        best_value = max(best_value, history_best[-1])
        if stale >= params.patience:
            converged = True
            break

    best = population[best_index]
    return GAResult(
        weights=best[:N_CATEGORIES].copy(),
        c=float(best[C_INDEX]),
        breakdown=evaluate(best, inputs),
        history_best=np.array(history_best),
        history_mean=np.array(history_mean),
        generations_run=generations,
        converged=converged,
        seed=seed,
        max_weight=cap,
    )
