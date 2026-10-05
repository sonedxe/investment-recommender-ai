"""Genetic algorithm: reproducibility, elitism, quality, D2 regression, gene c, runtime."""

import time

import numpy as np
import pytest

from ai.heuristic.chromosome import random_population
from ai.heuristic.fitness import FitnessInputs, evaluate_population
from ai.heuristic.genetic_algorithm import run_ga
from ai.heuristic.operators import arithmetic_crossover, gaussian_mutation, tournament_selection
from ai.shared.parameters import load_parameters
from ai.uncertainty.fuzzy.membership import membership

LAMBDAS = (0.2, 0.5, 1.0, 2.0)
UNIVERSE = np.linspace(0.0, 1.0, 1001)


@pytest.fixture(scope="module")
def params():
    return load_parameters()


def annex_inputs(params, lambda_eff: float, output_set: str = "media") -> FitnessInputs:
    """Annex A estimates, neutral context, fuzzy enabled with one absorption output set."""
    cat, ab, opt = params.categories, params.fuzzy.absorption, params.optimization
    return FitnessInputs(
        mu=cat.mu,
        context_adj=np.zeros(5),
        cov=cat.default_correlation * np.outer(cat.sigma, cat.sigma),
        lambda_eff=lambda_eff,
        universe=UNIVERSE,
        mu_ca=membership(ab.output_sets[output_set], UNIVERSE),
        sigma_floor=ab.sigma_floor,
        sigma_amplitude=ab.sigma_amplitude,
        phi=opt.phi,
        kappa=opt.kappa,
        fuzzy_enabled=True,
    )


@pytest.fixture(scope="module")
def d2_results(params):
    return {lam: run_ga(annex_inputs(params, lam), params.optimization, seed=11) for lam in LAMBDAS}


def test_same_seed_gives_identical_result(params) -> None:
    inputs = annex_inputs(params, 1.0)
    a = run_ga(inputs, params.optimization, seed=5)
    b = run_ga(inputs, params.optimization, seed=5)
    assert np.array_equal(a.weights, b.weights) and a.c == b.c
    assert np.array_equal(a.history_best, b.history_best)


def test_history_best_is_non_decreasing_with_elitism(d2_results) -> None:
    for result in d2_results.values():
        assert np.all(np.diff(result.history_best) >= 0)
        assert len(result.history_best) == result.generations_run + 1
        assert len(result.history_mean) == result.generations_run + 1


def test_ga_beats_random_search(params) -> None:
    inputs = annex_inputs(params, 1.0)
    result = run_ga(inputs, params.optimization, seed=2)
    sample = random_population(20_000, params.optimization.max_weight, np.random.default_rng(99))
    assert result.breakdown.total >= evaluate_population(sample, inputs).max() - 1e-4


def test_d2_regression_cap_and_risk_ordering(d2_results) -> None:
    stocks, term, debt, bonds = 0, 4, 2, 3
    for result in d2_results.values():
        assert result.weights.max() <= 0.40 + 1e-9
        assert result.weights.sum() == pytest.approx(1.0)
        assert 0.0 <= result.c <= 1.0
    assert d2_results[0.2].weights[stocks] > d2_results[2.0].weights[stocks]
    conservative = d2_results[2.0].weights
    assert conservative[term] + conservative[debt] + conservative[bonds] >= 0.9


def test_gene_c_follows_absorption_capacity(params) -> None:
    high = run_ga(annex_inputs(params, 1.0, "alta"), params.optimization, seed=4)
    low = run_ga(annex_inputs(params, 1.0, "baja"), params.optimization, seed=4)
    assert high.c > low.c
    assert high.breakdown.membership_at_c == pytest.approx(1.0, abs=1e-3)
    assert low.breakdown.membership_at_c == pytest.approx(1.0, abs=1e-3)


def test_max_weight_override(params) -> None:
    result = run_ga(annex_inputs(params, 0.2), params.optimization, seed=1, max_weight=1.0)
    assert result.max_weight == 1.0
    assert result.weights.max() > 0.40


def test_full_run_is_fast(params) -> None:
    assert params.optimization.population_size == 80
    start = time.perf_counter()
    run_ga(annex_inputs(params, 1.0), params.optimization, seed=0)
    assert time.perf_counter() - start < 2.0


def test_operators_preserve_feasibility() -> None:
    rng = np.random.default_rng(0)
    pop = random_population(200, 0.4, rng)
    a, b = arithmetic_crossover(pop[:100], pop[100:], 1.0, 0.4, rng)
    mutated = gaussian_mutation(np.vstack([a, b]), 0.5, 0.2, 0.4, rng)
    for group in (a, b, mutated):
        assert np.allclose(group[:, :5].sum(axis=1), 1.0)
        assert np.all(group[:, :5] <= 0.4 + 1e-9) and np.all(group[:, :5] >= 0)
        assert np.all((group[:, 5] >= 0) & (group[:, 5] <= 1))


def test_tournament_works_with_negative_fitness() -> None:
    fitness = np.array([-3.0, -0.1, -2.0, -5.0])
    winners = tournament_selection(fitness, 1000, 4, np.random.default_rng(0))
    assert np.bincount(winners, minlength=4).argmax() == 1


def test_c_mutation_uses_its_own_sigma() -> None:
    population = np.tile([0.2, 0.2, 0.2, 0.2, 0.2, 0.5], (4000, 1))
    mutated = gaussian_mutation(population, 1.0, 0.0, 0.4, np.random.default_rng(0), c_sigma=0.15)
    assert np.allclose(mutated[:, :5], 0.2)
    assert np.std(mutated[:, 5]) == pytest.approx(0.15, rel=0.05)


def test_initial_c_is_sampled_from_the_absorption_set() -> None:
    mu_ca = np.interp(UNIVERSE, [0.0, 0.206, 0.4, 1.0], [0.778, 0.778, 0.0, 0.0])
    pop = random_population(500, 0.4, np.random.default_rng(1), c_universe=UNIVERSE, c_weights=mu_ca)
    assert np.all(np.interp(pop[:, 5], UNIVERSE, mu_ca) > 0)
    again = random_population(500, 0.4, np.random.default_rng(1), c_universe=UNIVERSE, c_weights=mu_ca)
    assert np.array_equal(pop, again)


def _conservative_case(seed: int):
    from experiments.ablation import ARCHETYPE_BY_NAME, Environment, Settings, archetype_case, run_case

    env = Environment.load()
    case = archetype_case(ARCHETYPE_BY_NAME["conservador"], fuzzy=True, context=False, factors=None)
    return run_case(env, case, env.optimization(Settings()), seed).row


def test_regression_conservative_seed_7_c_is_not_stranded() -> None:
    # Before the fix this run ended with c = 0.759 and mu_CA(c) = 0 (flat zero-membership region).
    row = _conservative_case(7)
    assert row["mu_ca_c"] > 0


@pytest.mark.parametrize("output_set", ["baja", "media", "alta"])
def test_evolved_c_keeps_positive_membership_across_seeds(params, output_set) -> None:
    inputs = annex_inputs(params, 2.0, output_set)
    for seed in range(12):
        result = run_ga(inputs, params.optimization, seed=seed)
        assert result.breakdown.membership_at_c > 0, seed
