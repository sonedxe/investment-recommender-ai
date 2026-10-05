"""Ablation, context, absorption-gene and calibration experiments (F8).

Runs the same pipeline as ``backend.app.services.recommendation.recommend``
(stages 3-6: market estimates -> horizon -> absorption -> context -> genetic
algorithm) without the explanation stage, so lambda_base and the optimization
parameters can be varied freely. Every run is seeded, so the outputs are
reproducible. Results are written as CSV files plus a Markdown summary;
figures are drawn by ``experiments/plots.py`` only when matplotlib is
installed (``requirements-experiments.txt``) and ``--no-plots`` is not given.

Usage::

    python experiments/ablation.py [--seeds 10] [--out experiments/results]
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.context.adjustment import adjust  # noqa: E402
from ai.heuristic.fitness import FitnessInputs  # noqa: E402
from ai.heuristic.genetic_algorithm import GAResult, run_ga  # noqa: E402
from ai.shared.parameters import OptimizationParameters, Parameters, load_parameters  # noqa: E402
from ai.shared.types import CATEGORY_ORDER, ContextFactors, MarketEstimates  # noqa: E402
from ai.uncertainty.bayesian.market import build_market_estimates  # noqa: E402
from ai.uncertainty.fuzzy.absorption import AbsorptionResult, evaluate_absorption  # noqa: E402
from ai.uncertainty.fuzzy.horizon import evaluate_horizon  # noqa: E402

DEFAULT_OUT = ROOT / "experiments" / "results"
CATEGORIES = tuple(c.value for c in CATEGORY_ORDER)
WEIGHT_COLUMNS = tuple(f"w_{c}" for c in CATEGORIES)
AMOUNT = 10_000.0
ADVERSE_CONTEXT = ContextFactors(political=-0.5, macro=0.0)
NEUTRAL_CONTEXT = ContextFactors(political=0.0, macro=0.0)
PENALTY_TOLERANCE = 1e-10
BINDING_TOLERANCE = 0.002  # sigma within 0.2 pp of sigma_max(c) counts as binding
CAP_TOLERANCE = 1e-6


@dataclass(frozen=True)
class Archetype:
    name: str
    lambda_base: float
    horizon_years: float
    total_savings: float
    emergency_months: float
    amount: float = AMOUNT


ARCHETYPES: tuple[Archetype, ...] = (
    Archetype("conservador", 2.0, 2.0, 12_000.0, 1.0),
    Archetype("moderado", 1.0, 5.0, 40_000.0, 4.0),
    Archetype("agresivo", 0.5, 12.0, 100_000.0, 8.0),
)
ARCHETYPE_BY_NAME = {a.name: a for a in ARCHETYPES}

# name -> (fuzzy, context)
CONFIGURATIONS: dict[str, tuple[bool, bool]] = {
    "base": (False, False),
    "solo_difuso": (True, False),
    "solo_contexto": (False, True),
    "completo": (True, True),
}

# Absorption situations for the gene demonstration: (total_savings, emergency_months) for S/ 10,000.
ABSORPTION_LEVELS: dict[str, tuple[float, float]] = {
    "baja": (12_000.0, 1.0),     # r = 0.83, E = 1 -> Baja
    "media": (20_000.0, 4.0),    # r = 0.50, E = 4 -> Media
    "alta": (100_000.0, 8.0),    # r = 0.10, E = 8 -> Alta
}
GENE_LAMBDAS = (0.2, 0.5, 1.0, 2.0)
GENE_HORIZON_YEARS = 5.0  # m_H = 1, so lambda_eff = lambda_base

POLITICAL_LEVELS = (-1.0, 0.0, 1.0)
MACRO_LEVELS = (-1.0, 0.0, 1.0)

CALIBRATION_GRID: dict[str, tuple[float, ...]] = {
    "kappa": (0.01, 0.03, 0.05),
    "phi": (10.0, 50.0, 200.0),
    "max_weight": (0.35, 0.40, 0.50),
}
# Floor sweep (W16): the cost of "no category at 0 %" in expected return and sigma. Kept out of
# CALIBRATION_GRID because the calibration figure plots one panel per entry of that grid.
FLOOR_GRID: dict[str, tuple[float, ...]] = {"min_weight": (0.0, 0.05)}
# Stress case added to the requested moderado/agresivo sweeps: low absorption with a low lambda is the
# only situation where the volatility penalty is active, so it is the one that exercises kappa and phi.
STRESS_ARCHETYPE = Archetype("estres_baja_absorcion", 0.5, 5.0, 12_000.0, 1.0)
CALIBRATION_ARCHETYPES = ("moderado", "agresivo", STRESS_ARCHETYPE.name)


@dataclass(frozen=True)
class Settings:
    seeds: int = 10
    population_size: int | None = None
    max_generations: int | None = None


@dataclass(frozen=True)
class Environment:
    params: Parameters
    market: MarketEstimates

    @classmethod
    def load(cls) -> Environment:
        params = load_parameters()
        return cls(params=params, market=build_market_estimates(params).estimates)

    def optimization(self, settings: Settings, **overrides: Any) -> OptimizationParameters:
        opt = self.params.optimization
        changes: dict[str, Any] = dict(overrides)
        if settings.population_size is not None:
            changes["population_size"] = settings.population_size
            changes["elitism"] = min(opt.elitism, settings.population_size - 1)
        if settings.max_generations is not None:
            changes["max_generations"] = settings.max_generations
            changes["patience"] = min(opt.patience, settings.max_generations)
        return replace(opt, **changes)


@dataclass(frozen=True)
class Case:
    lambda_base: float
    horizon_years: float
    amount: float
    total_savings: float
    emergency_months: float
    fuzzy: bool
    context: bool
    factors: ContextFactors | None


@dataclass(frozen=True)
class Outcome:
    row: dict[str, Any]
    ga: GAResult


def set_mode(absorption: AbsorptionResult) -> float:
    """Centre of the highest plateau of mu_CA (the most plausible capacity)."""
    peak = absorption.mu_ca.max()
    indices = np.flatnonzero(np.isclose(absorption.mu_ca, peak, atol=1e-9))
    return float((absorption.universe[indices[0]] + absorption.universe[indices[-1]]) / 2)


def herfindahl(weights: np.ndarray) -> float:
    return float(np.sum(np.square(weights)))


def run_case(env: Environment, case: Case, opt: OptimizationParameters, seed: int,
             fuzzy_penalty: bool | None = None) -> Outcome:
    """One seeded run; ``fuzzy_penalty=False`` keeps the fuzzy lambda_eff but drops penalty and reward."""
    params = env.params
    horizon = evaluate_horizon(params.fuzzy.horizon, case.lambda_base, case.horizon_years)
    m_h = horizon.m_h if case.fuzzy else 1.0
    absorption = evaluate_absorption(params.fuzzy.absorption, case.amount, case.total_savings, case.emergency_months)
    context = adjust(env.market, case.factors, None, params.context, enabled=case.context)
    abs_params = params.fuzzy.absorption
    fuzzy_enabled = case.fuzzy if fuzzy_penalty is None else fuzzy_penalty
    inputs = FitnessInputs(
        mu=env.market.mu,
        context_adj=context.c,
        cov=context.cov_adj,
        lambda_eff=case.lambda_base * m_h,
        universe=absorption.universe,
        mu_ca=absorption.mu_ca,
        sigma_floor=abs_params.sigma_floor,
        sigma_amplitude=abs_params.sigma_amplitude,
        phi=opt.phi,
        kappa=opt.kappa,
        fuzzy_enabled=fuzzy_enabled,
    )
    ga = run_ga(inputs, opt, seed=seed)
    b = ga.breakdown
    sigma_max_c = abs_params.sigma_floor + abs_params.sigma_amplitude * ga.c
    row: dict[str, Any] = {w: float(v) for w, v in zip(WEIGHT_COLUMNS, ga.weights)}
    row.update(
        expected_return=b.expected_return,
        sigma=b.sigma,
        fitness=b.total,
        herfindahl=herfindahl(ga.weights),
        max_w=float(ga.weights.max()),
        min_w=float(ga.weights.min()),
        n_at_cap=int(np.sum(ga.weights >= ga.max_weight - CAP_TOLERANCE)),
        n_at_floor=int(np.sum(ga.weights <= ga.min_weight + CAP_TOLERANCE)),
        c=ga.c,
        mu_ca_c=absorption.membership_at(ga.c) if fuzzy_enabled else math.nan,
        centroid=absorption.centroid,
        mode=set_mode(absorption),
        sigma_max_c=sigma_max_c if fuzzy_enabled else math.nan,
        penalty_term=b.penalty_term,
        fuzzy_reward=b.fuzzy_reward,
        penalty_active=int(b.penalty_term < -PENALTY_TOLERANCE),
        binding=int(fuzzy_enabled and b.sigma >= sigma_max_c - BINDING_TOLERANCE),
        m_h=m_h,
        lambda_eff=case.lambda_base * m_h,
        generations=ga.generations_run,
        converged=int(ga.converged),
    )
    return Outcome(row=row, ga=ga)


def archetype_case(arch: Archetype, fuzzy: bool, context: bool, factors: ContextFactors | None) -> Case:
    return Case(arch.lambda_base, arch.horizon_years, arch.amount, arch.total_savings, arch.emergency_months,
                fuzzy, context, factors)


# --------------------------------------------------------------------------- experiments

def ablation(env: Environment, settings: Settings) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    histories: dict[str, Any] = {}
    opt = env.optimization(settings)
    for arch in ARCHETYPES:
        for config, (fuzzy, context) in CONFIGURATIONS.items():
            factors = ADVERSE_CONTEXT if context else None
            for seed in range(settings.seeds):
                out = run_case(env, archetype_case(arch, fuzzy, context, factors), opt, seed)
                rows.append({"archetype": arch.name, "config": config, "seed": seed, **out.row})
                if seed == 0:
                    histories[f"{arch.name}/{config}"] = {
                        "best": out.ga.history_best.tolist(), "mean": out.ga.history_mean.tolist()}
    return rows, histories


def context_scenarios(env: Environment, settings: Settings) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    opt = env.optimization(settings)
    arch = ARCHETYPE_BY_NAME["moderado"]
    for macro in MACRO_LEVELS:
        for political in POLITICAL_LEVELS:
            factors = ContextFactors(political=political, macro=macro)
            for seed in range(settings.seeds):
                out = run_case(env, archetype_case(arch, True, True, factors), opt, seed)
                rows.append({"political": political, "macro": macro, "seed": seed, **out.row})
    return rows


def gene_demonstration(env: Environment, settings: Settings) -> list[dict[str, Any]]:
    """Full model per absorption level and lambda; also sigma without the penalty (``sigma_free``)."""
    rows: list[dict[str, Any]] = []
    opt = env.optimization(settings)
    for level, (savings, months) in ABSORPTION_LEVELS.items():
        for lam in GENE_LAMBDAS:
            case = Case(lam, GENE_HORIZON_YEARS, AMOUNT, savings, months, True, True, NEUTRAL_CONTEXT)
            for seed in range(settings.seeds):
                out = run_case(env, case, opt, seed)
                free = run_case(env, case, opt, seed, fuzzy_penalty=False)
                rows.append({"absorption": level, "lambda_base": lam, "seed": seed, **out.row,
                             "sigma_free": free.row["sigma"]})
    return rows


def calibration(env: Environment, settings: Settings) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in CALIBRATION_ARCHETYPES:
        arch = STRESS_ARCHETYPE if name == STRESS_ARCHETYPE.name else ARCHETYPE_BY_NAME[name]
        case = archetype_case(arch, True, True, NEUTRAL_CONTEXT)
        for parameter, values in {**CALIBRATION_GRID, **FLOOR_GRID}.items():
            for value in values:
                opt = env.optimization(settings, **{parameter: value})
                for seed in range(settings.seeds):
                    out = run_case(env, case, opt, seed)
                    rows.append({"archetype": name, "parameter": parameter, "value": value, "seed": seed,
                                 **out.row})
    return rows


# --------------------------------------------------------------------------- aggregation and output

def summarize(rows: Sequence[dict[str, Any]], keys: Sequence[str]) -> list[dict[str, Any]]:
    """Mean and sample sd (ddof=1, 0 for one seed) of every numeric metric, grouped by ``keys``."""
    metrics = [k for k in rows[0] if k not in (*keys, "seed")]
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(tuple(row[k] for k in keys), []).append(row)
    summary = []
    for group_key, members in groups.items():
        out: dict[str, Any] = dict(zip(keys, group_key))
        out["n"] = len(members)
        for metric in metrics:
            values = np.array([m[metric] for m in members], dtype=float)
            finite = values[np.isfinite(values)]
            out[f"{metric}_mean"] = float(finite.mean()) if finite.size else math.nan
            out[f"{metric}_sd"] = float(finite.std(ddof=1)) if finite.size > 1 else (0.0 if finite.size else math.nan)
        summary.append(out)
    return summary


def write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in row.items()})


def _pct(value: float) -> str:
    return "n/d" if not math.isfinite(value) else f"{100 * value:.1f}"


def _num(value: float, digits: int = 3) -> str:
    return "n/d" if not math.isfinite(value) else f"{value:.{digits}f}"


def _pm(row: dict[str, Any], metric: str, fmt=_pct) -> str:
    return f"{fmt(row[metric + '_mean'])} ± {fmt(row[metric + '_sd'])}"


def _table(header: Sequence[str], body: Iterable[Sequence[str]]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(cells) + " |" for cells in body]
    return lines


def ablation_table(summary: Sequence[dict[str, Any]]) -> list[str]:
    header = ["Arquetipo", "Configuración", *(f"{c} %" for c in CATEGORIES), "E %", "σ %", "Fitness",
              "HHI", "c", "μ_CA(c)", "Centroide", "λ_ef", "Gen."]
    body = [[r["archetype"], r["config"], *(_pm(r, w) for w in WEIGHT_COLUMNS), _pm(r, "expected_return"),
             _pm(r, "sigma"), _pm(r, "fitness", lambda v: _num(v, 4)), _pm(r, "herfindahl", _num),
             _pm(r, "c", _num), _pm(r, "mu_ca_c", _num), _num(r["centroid_mean"]), _num(r["lambda_eff_mean"]),
             _pm(r, "generations", lambda v: _num(v, 1))] for r in summary]
    return _table(header, body)


def context_table(summary: Sequence[dict[str, Any]]) -> list[str]:
    neutral = next(r for r in summary if r["political"] == 0 and r["macro"] == 0)
    header = ["Político", "Macro", *(f"{c} %" for c in CATEGORIES), "Δ acciones (pp)", "E %", "σ %", "c"]
    body = [[f"{r['political']:+.0f}", f"{r['macro']:+.0f}", *(_pct(r[w + "_mean"]) for w in WEIGHT_COLUMNS),
             f"{100 * (r['w_stocks_mean'] - neutral['w_stocks_mean']):+.1f}", _pct(r["expected_return_mean"]),
             _pct(r["sigma_mean"]), _num(r["c_mean"])] for r in summary]
    return _table(header, body)


def gene_table(summary: Sequence[dict[str, Any]]) -> list[str]:
    header = ["Absorción", "λ_base", "Moda", "Centroide", "c", "μ_CA(c)", "σ %", "σ_max(c) %",
              "σ sin penalización %", "Penalización activa", "Restricción activa"]
    body = [[r["absorption"], f"{r['lambda_base']:g}", _num(r["mode_mean"]), _num(r["centroid_mean"]), _pm(r, "c", _num),
             _num(r["mu_ca_c_mean"]), _pct(r["sigma_mean"]), _pct(r["sigma_max_c_mean"]),
             _pct(r["sigma_free_mean"]), f"{100 * r['penalty_active_mean']:.0f} %",
             f"{100 * r['binding_mean']:.0f} %"] for r in summary]
    return _table(header, body)


def calibration_table(summary: Sequence[dict[str, Any]]) -> list[str]:
    header = ["Arquetipo", "Parámetro", "Valor", *(f"{c} %" for c in CATEGORIES), "E %", "σ %", "HHI",
              "Pesos en el tope", "Pesos en el piso", "c", "|c − centroide|", "μ_CA(c)", "Penalización activa"]
    body = [[r["archetype"], r["parameter"], f"{r['value']:g}", *(_pct(r[w + "_mean"]) for w in WEIGHT_COLUMNS),
             _pct(r["expected_return_mean"]), _pct(r["sigma_mean"]), _num(r["herfindahl_mean"]),
             _num(r["n_at_cap_mean"], 1), _num(r["n_at_floor_mean"], 1), _num(r["c_mean"]), _num(abs(r["c_mean"] - r["centroid_mean"])),
             _num(r["mu_ca_c_mean"]), f"{100 * r['penalty_active_mean']:.0f} %"] for r in summary]
    return _table(header, body)


def write_readme(out: Path, settings: Settings, env: Environment, tables: dict[str, list[str]],
                 runtime_s: float, figures: Sequence[str]) -> None:
    opt = env.optimization(settings)
    lines = [
        "# Resultados de los experimentos",
        "",
        "Generado por `python experiments/ablation.py`. No editar a mano: se sobrescribe en cada corrida.",
        "",
        f"- Semillas por configuración: {settings.seeds} (0 a {settings.seeds - 1}).",
        f"- AG: población {opt.population_size}, máximo {opt.max_generations} generaciones, "
        f"paciencia {opt.patience}, κ = {opt.kappa:g}, φ = {opt.phi:g}, tope = {opt.max_weight:g}, "
        f"piso = {opt.min_weight:g}.",
        f"- Monto S/ {AMOUNT:,.0f}. Contexto de la ablación con contexto activo: político −0.5, macro 0.",
        f"- Tiempo de ejecución: {runtime_s:.1f} s.",
        "- Valores: media ± desviación estándar muestral entre semillas; pesos, E y σ en %.",
        "",
        "Interpretación: ver `docs/experimentos/`.",
        "",
        "## Archivos",
        "",
        "| Archivo | Contenido |",
        "|---|---|",
        "| `ablation_runs.csv` / `ablation_summary.csv` | Ablación: 4 configuraciones × 3 arquetipos × semillas |",
        "| `ablation_convergence.csv` | Mejor fitness y fitness medio por generación (semilla 0) |",
        "| `context_runs.csv` / `context_summary.csv` | Moderado, modelo completo, político × macro |",
        "| `gene_runs.csv` / `gene_summary.csv` | Gen difuso `c`: absorción × λ_base |",
        "| `calibration_runs.csv` / `calibration_summary.csv` | Barridos de κ, φ, tope y piso |",
        "| `golden_offline.md` | Golden set de IA generativa en modo offline (`scripts/eval_golden_set.py`) |",
        *(f"| `{name}` | Figura |" for name in figures),
        "",
    ]
    titles = {"ablation": "Ablación", "context": "Escenarios de contexto (moderado, modelo completo)",
              "gene": "Gen difuso c", "calibration": "Calibración (contexto neutral)"}
    for key, title in titles.items():
        lines += [f"## {title}", "", *tables[key], ""]
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_convergence(path: Path, histories: dict[str, Any]) -> None:
    rows = []
    for key, curves in histories.items():
        archetype, config = key.split("/")
        for generation, (best, mean) in enumerate(zip(curves["best"], curves["mean"])):
            rows.append({"archetype": archetype, "config": config, "generation": generation,
                         "best": best, "mean": mean})
    write_csv(path, rows)


def run_all(out: Path, settings: Settings, plots: bool = True) -> dict[str, Any]:
    """Run the four experiments, write CSVs, figures (optional) and README; return the summaries."""
    start = time.perf_counter()
    out.mkdir(parents=True, exist_ok=True)
    env = Environment.load()

    ablation_rows, histories = ablation(env, settings)
    context_rows = context_scenarios(env, settings)
    gene_rows = gene_demonstration(env, settings)
    calibration_rows = calibration(env, settings)

    summaries = {
        "ablation": summarize(ablation_rows, ["archetype", "config"]),
        "context": summarize(context_rows, ["political", "macro"]),
        "gene": summarize(gene_rows, ["absorption", "lambda_base"]),
        "calibration": summarize(calibration_rows, ["archetype", "parameter", "value"]),
    }
    for name, rows in (("ablation", ablation_rows), ("context", context_rows), ("gene", gene_rows),
                       ("calibration", calibration_rows)):
        write_csv(out / f"{name}_runs.csv", rows)
        write_csv(out / f"{name}_summary.csv", summaries[name])
    write_convergence(out / "ablation_convergence.csv", histories)

    figures: list[str] = []
    if plots:
        from experiments import plots as plotting  # matplotlib is optional

        figures = plotting.draw_all(out, summaries, histories)
    runtime = time.perf_counter() - start
    tables = {"ablation": ablation_table(summaries["ablation"]), "context": context_table(summaries["context"]),
              "gene": gene_table(summaries["gene"]), "calibration": calibration_table(summaries["calibration"])}
    write_readme(out, settings, env, tables, runtime, figures)
    return {"summaries": summaries, "runtime_s": runtime, "figures": figures}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--population", type=int, default=None, help="override population_size (smoke runs)")
    parser.add_argument("--max-generations", type=int, default=None, help="override max_generations")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--no-plots", action="store_true", help="skip figures (no matplotlib needed)")
    args = parser.parse_args(argv)
    result = run_all(args.out, Settings(args.seeds, args.population, args.max_generations), plots=not args.no_plots)
    print(f"Wrote results to {args.out} in {result['runtime_s']:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
