"""Typed loaders for the JSON parameter files in ``data/parameters/``.

Every loader validates shapes, ranges and category coverage and returns frozen
dataclasses. Rates are decimals; Annex C "pp" values are stored divided by 100.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np

from ai.shared.types import CATEGORY_ORDER, N_CATEGORIES, CategoryId, RiskProfile

DEFAULT_PARAMETERS_DIR = Path(__file__).resolve().parents[2] / "data" / "parameters"


class ParameterError(ValueError):
    """A parameter file is missing, malformed or out of range."""


@dataclass(frozen=True)
class MembershipSpec:
    """Membership function declared in JSON as ``{"type": "tri"|"trap", "params": [...]}``."""

    kind: str
    params: tuple[float, ...]

    def __post_init__(self) -> None:
        expected = {"tri": 3, "trap": 4}.get(self.kind)
        if expected is None:
            raise ParameterError(f"unknown membership type {self.kind!r}")
        if len(self.params) != expected:
            raise ParameterError(f"{self.kind} needs {expected} params, got {len(self.params)}")
        if any(b < a for a, b in zip(self.params, self.params[1:])):
            raise ParameterError(f"{self.kind} params must be non-decreasing: {self.params}")
        if self.params[0] == self.params[-1]:
            raise ParameterError(f"{self.kind} support must have positive width: {self.params}")

    @classmethod
    def from_json(cls, raw: Mapping[str, Any]) -> MembershipSpec:
        try:
            return cls(kind=str(raw["type"]), params=tuple(float(p) for p in raw["params"]))
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, ParameterError):
                raise
            raise ParameterError(f"invalid membership spec {raw!r}") from exc


@dataclass(frozen=True)
class CategoryParameters:
    """Annex A: display names, kinds, expected returns and volatilities."""

    ids: tuple[CategoryId, ...]
    names: Mapping[CategoryId, str]
    kinds: Mapping[CategoryId, str]
    mu: np.ndarray
    sigma: np.ndarray
    default_correlation: np.ndarray
    correlation_note: str


@dataclass(frozen=True)
class ContextParameters:
    """Annex C: context-rule coefficients per category (decimals) and globals."""

    b: np.ndarray
    beta_pol: np.ndarray
    beta_mac: np.ndarray
    gamma_pol: np.ndarray
    gamma_mac: np.ndarray
    beta_tend: float
    c_max: float


@dataclass(frozen=True)
class HorizonParameters:
    """Sugeno horizon system: sets over years and crisp consequents m_H."""

    universe: tuple[float, float]
    sets: Mapping[str, MembershipSpec]
    consequents: Mapping[str, float]


@dataclass(frozen=True)
class AbsorptionRule:
    """Mamdani rule: IF ratio is X AND emergency is Y THEN capacity is Z."""

    id: str
    ratio: str
    emergency: str
    output: str


@dataclass(frozen=True)
class AbsorptionParameters:
    """Mamdani absorption system and the sigma_max(c) = floor + amplitude * c mapping."""

    ratio_universe: tuple[float, float]
    ratio_sets: Mapping[str, MembershipSpec]
    emergency_universe: tuple[float, float]
    emergency_sets: Mapping[str, MembershipSpec]
    rules: tuple[AbsorptionRule, ...]
    output_universe: tuple[float, float]
    output_sets: Mapping[str, MembershipSpec]
    sigma_floor: float
    sigma_amplitude: float


@dataclass(frozen=True)
class FuzzyParameters:
    horizon: HorizonParameters
    absorption: AbsorptionParameters


@dataclass(frozen=True)
class OptimizationParameters:
    """Extended fitness and genetic algorithm settings."""

    phi: float
    kappa: float
    max_weight: float
    population_size: int
    max_generations: int
    patience: int
    tournament_size: int
    crossover_rate: float
    mutation_rate: float
    mutation_sigma: float
    elitism: int
    c_mutation_sigma: float = 0.15


@dataclass(frozen=True)
class RiskProfileParameters:
    lambda_base: Mapping[RiskProfile, float]


@dataclass(frozen=True)
class BayesParameters:
    """Prior sd of each category's expected return (annual) and data requirements."""

    prior_mean_sd: np.ndarray
    min_months: int
    trend_window_months: int


@dataclass(frozen=True)
class Parameters:
    categories: CategoryParameters
    context: ContextParameters
    fuzzy: FuzzyParameters
    optimization: OptimizationParameters
    risk_profiles: RiskProfileParameters
    bayes: BayesParameters


def _read(base_dir: Path, name: str) -> dict[str, Any]:
    path = base_dir / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ParameterError(f"missing parameter file {path}") from exc
    except json.JSONDecodeError as exc:
        raise ParameterError(f"invalid JSON in {path}: {exc}") from exc


def _readonly(array: np.ndarray) -> np.ndarray:
    array.setflags(write=False)
    return array


def _per_category(raw: Mapping[str, Mapping[str, Any]], field: str, source: str) -> np.ndarray:
    missing = [c.value for c in CATEGORY_ORDER if c.value not in raw]
    if missing:
        raise ParameterError(f"{source}: missing categories {missing}")
    try:
        values = np.array([float(raw[c.value][field]) for c in CATEGORY_ORDER])
    except (KeyError, TypeError, ValueError) as exc:
        raise ParameterError(f"{source}: invalid or missing field {field!r}") from exc
    if not np.all(np.isfinite(values)):
        raise ParameterError(f"{source}: {field} must be finite")
    return _readonly(values)


def _universe(raw: Any, source: str) -> tuple[float, float]:
    try:
        low, high = (float(v) for v in raw)
    except (TypeError, ValueError) as exc:
        raise ParameterError(f"{source}: universe must be [low, high]") from exc
    if not low < high:
        raise ParameterError(f"{source}: universe must satisfy low < high")
    return low, high


def _sets(raw: Mapping[str, Any], universe: tuple[float, float], source: str) -> Mapping[str, MembershipSpec]:
    if not raw:
        raise ParameterError(f"{source}: at least one fuzzy set is required")
    sets = {name: MembershipSpec.from_json(spec) for name, spec in raw.items()}
    for name, spec in sets.items():
        if spec.params[0] < universe[0] or spec.params[-1] > universe[1]:
            raise ParameterError(f"{source}: set {name!r} lies outside the universe {universe}")
    return MappingProxyType(sets)


def _in_range(value: Any, low: float, high: float, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ParameterError(f"{name} must be numeric") from exc
    if not low <= number <= high:
        raise ParameterError(f"{name} must be in [{low}, {high}], got {number}")
    return number


def _positive_int(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ParameterError(f"{name} must be a positive integer, got {value!r}")
    return value


def load_categories(base_dir: Path) -> CategoryParameters:
    raw = _read(base_dir, "categories.json")
    cats = raw.get("categories", {})
    mu = _per_category(cats, "mu", "categories.json")
    sigma = _per_category(cats, "sigma", "categories.json")
    if np.any(sigma < 0):
        raise ParameterError("categories.json: sigma must be non-negative")
    try:
        corr = np.array(raw["default_correlation"]["matrix"], dtype=float)
        note = str(raw["default_correlation"]["note"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ParameterError("categories.json: invalid default_correlation") from exc
    if corr.shape != (N_CATEGORIES, N_CATEGORIES):
        raise ParameterError("categories.json: default_correlation must be 5x5")
    if not np.allclose(corr, corr.T) or not np.allclose(np.diag(corr), 1.0) or np.any(np.abs(corr) > 1):
        raise ParameterError("categories.json: default_correlation must be a correlation matrix")
    return CategoryParameters(
        ids=CATEGORY_ORDER,
        names=MappingProxyType({c: str(cats[c.value]["name"]) for c in CATEGORY_ORDER}),
        kinds=MappingProxyType({c: str(cats[c.value]["kind"]) for c in CATEGORY_ORDER}),
        mu=mu,
        sigma=sigma,
        default_correlation=_readonly(corr),
        correlation_note=note,
    )


def load_context(base_dir: Path) -> ContextParameters:
    raw = _read(base_dir, "context.json")
    cats = raw.get("categories", {})
    gamma_pol = _per_category(cats, "gamma_pol", "context.json")
    gamma_mac = _per_category(cats, "gamma_mac", "context.json")
    if np.any(gamma_pol < 0) or np.any(gamma_mac < 0):
        raise ParameterError("context.json: gamma values must be non-negative")
    return ContextParameters(
        b=_per_category(cats, "b", "context.json"),
        beta_pol=_per_category(cats, "beta_pol", "context.json"),
        beta_mac=_per_category(cats, "beta_mac", "context.json"),
        gamma_pol=gamma_pol,
        gamma_mac=gamma_mac,
        beta_tend=_in_range(raw.get("beta_tend"), 0.0, 1.0, "context.json beta_tend"),
        c_max=_in_range(raw.get("c_max"), 0.0, 1.0, "context.json c_max"),
    )


def load_fuzzy(base_dir: Path) -> FuzzyParameters:
    raw = _read(base_dir, "fuzzy.json")
    try:
        return _parse_fuzzy(raw)
    except (KeyError, TypeError) as exc:
        raise ParameterError(f"fuzzy.json: missing or malformed entry ({exc})") from exc


def _parse_fuzzy(raw: Mapping[str, Any]) -> FuzzyParameters:
    hz, ab = raw["horizon"], raw["absorption"]
    inputs, output = ab["inputs"], ab["output"]

    hz_universe = _universe(hz.get("universe"), "fuzzy.json horizon")
    hz_sets = _sets(hz.get("sets", {}), hz_universe, "fuzzy.json horizon")
    consequents = {k: float(v) for k, v in hz.get("consequents", {}).items()}
    if set(consequents) != set(hz_sets):
        raise ParameterError("fuzzy.json: horizon consequents must match its sets")

    ratio_u = _universe(inputs["ratio"]["universe"], "fuzzy.json ratio")
    ratio_sets = _sets(inputs["ratio"]["sets"], ratio_u, "fuzzy.json ratio")
    emerg_u = _universe(inputs["emergency"]["universe"], "fuzzy.json emergency")
    emerg_sets = _sets(inputs["emergency"]["sets"], emerg_u, "fuzzy.json emergency")
    out_u = _universe(output["universe"], "fuzzy.json absorption output")
    out_sets = _sets(output["sets"], out_u, "fuzzy.json absorption output")

    rules = []
    for rule in ab.get("rules", []):
        parsed = AbsorptionRule(
            id=str(rule["id"]), ratio=rule["ratio"], emergency=rule["emergency"], output=rule["output"]
        )
        if parsed.ratio not in ratio_sets or parsed.emergency not in emerg_sets or parsed.output not in out_sets:
            raise ParameterError(f"fuzzy.json: rule {parsed.id} references an unknown set")
        rules.append(parsed)
    if not rules:
        raise ParameterError("fuzzy.json: absorption needs at least one rule")

    return FuzzyParameters(
        horizon=HorizonParameters(hz_universe, hz_sets, MappingProxyType(consequents)),
        absorption=AbsorptionParameters(
            ratio_universe=ratio_u,
            ratio_sets=ratio_sets,
            emergency_universe=emerg_u,
            emergency_sets=emerg_sets,
            rules=tuple(rules),
            output_universe=out_u,
            output_sets=out_sets,
            sigma_floor=_in_range(ab.get("sigma_floor"), 0.0, 1.0, "fuzzy.json sigma_floor"),
            sigma_amplitude=_in_range(ab.get("sigma_amplitude"), 0.0, 1.0, "fuzzy.json sigma_amplitude"),
        ),
    )


def load_optimization(base_dir: Path) -> OptimizationParameters:
    raw = _read(base_dir, "optimization.json")
    population = _positive_int(raw.get("population_size"), "population_size")
    params = OptimizationParameters(
        phi=_in_range(raw.get("phi"), 0.0, float("inf"), "phi"),
        kappa=_in_range(raw.get("kappa"), 0.0, float("inf"), "kappa"),
        # Five categories need max_weight >= 1/5 for a feasible portfolio.
        max_weight=_in_range(raw.get("max_weight"), 1.0 / N_CATEGORIES, 1.0, "max_weight"),
        population_size=population,
        max_generations=_positive_int(raw.get("max_generations"), "max_generations"),
        patience=_positive_int(raw.get("patience"), "patience"),
        tournament_size=_positive_int(raw.get("tournament_size"), "tournament_size"),
        crossover_rate=_in_range(raw.get("crossover_rate"), 0.0, 1.0, "crossover_rate"),
        mutation_rate=_in_range(raw.get("mutation_rate"), 0.0, 1.0, "mutation_rate"),
        mutation_sigma=_in_range(raw.get("mutation_sigma"), 0.0, 1.0, "mutation_sigma"),
        elitism=int(_in_range(raw.get("elitism"), 0, population - 1, "elitism")),
        c_mutation_sigma=_in_range(raw.get("c_mutation_sigma", 0.15), 0.0, 1.0, "c_mutation_sigma"),
    )
    if params.tournament_size > population:
        raise ParameterError("tournament_size cannot exceed population_size")
    return params


def load_risk_profiles(base_dir: Path) -> RiskProfileParameters:
    raw = _read(base_dir, "risk_profiles.json").get("lambda_base", {})
    missing = [p.value for p in RiskProfile if p.value not in raw]
    if missing:
        raise ParameterError(f"risk_profiles.json: missing profiles {missing}")
    lambdas = {p: _in_range(raw[p.value], 0.0, 100.0, f"lambda_base[{p.value}]") for p in RiskProfile}
    if any(v <= 0 for v in lambdas.values()):
        raise ParameterError("risk_profiles.json: lambda_base must be positive")
    return RiskProfileParameters(lambda_base=MappingProxyType(lambdas))


def load_bayes(base_dir: Path) -> BayesParameters:
    raw = _read(base_dir, "bayes.json")
    sds = raw.get("prior_mean_sd", {})
    missing = [c.value for c in CATEGORY_ORDER if c.value not in sds]
    if missing:
        raise ParameterError(f"bayes.json: missing categories {missing}")
    prior_sd = np.array([_in_range(sds[c.value], 0.0, 1.0, f"prior_mean_sd[{c.value}]") for c in CATEGORY_ORDER])
    if np.any(prior_sd <= 0):
        raise ParameterError("bayes.json: prior_mean_sd must be positive")
    return BayesParameters(
        prior_mean_sd=_readonly(prior_sd),
        min_months=_positive_int(raw.get("min_months"), "min_months"),
        trend_window_months=_positive_int(raw.get("trend_window_months"), "trend_window_months"),
    )


def load_parameters(base_dir: Path | str | None = None) -> Parameters:
    """Load and validate every parameter file from ``base_dir`` (default ``data/parameters``)."""
    directory = Path(base_dir) if base_dir is not None else DEFAULT_PARAMETERS_DIR
    return Parameters(
        categories=load_categories(directory),
        context=load_context(directory),
        fuzzy=load_fuzzy(directory),
        optimization=load_optimization(directory),
        risk_profiles=load_risk_profiles(directory),
        bayes=load_bayes(directory),
    )
