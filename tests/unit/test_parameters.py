"""Parameter files (Annex A, Annex C, fuzzy sets, GA, risk profiles) and loaders."""

import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from ai.shared import CATEGORY_ORDER, CategoryId, RiskProfile
from ai.shared.parameters import DEFAULT_PARAMETERS_DIR, ParameterError, load_parameters


@pytest.fixture(scope="module")
def params():
    return load_parameters()


def test_categories_match_annex_a(params) -> None:
    cats = params.categories
    assert cats.ids == CATEGORY_ORDER
    np.testing.assert_allclose(cats.mu, [0.122, 0.061, 0.024, 0.065, 0.045])
    np.testing.assert_allclose(cats.sigma, [0.19, 0.09, 0.025, 0.035, 0.005])
    assert cats.names[CategoryId.BONDS] == "Bonos soberanos (BTP)"
    assert cats.names[CategoryId.TERM] == "Depósito a plazo fijo"


def test_default_correlation_assumption(params) -> None:
    corr = params.categories.default_correlation
    assert corr.shape == (5, 5)
    np.testing.assert_allclose(np.diag(corr), 1.0)
    np.testing.assert_allclose(corr, corr.T)
    assert corr[0, 1] == pytest.approx(0.3)
    assert corr[2, 3] == pytest.approx(0.3)
    np.testing.assert_allclose(corr[4, :4], 0.0)


def test_context_matches_annex_c_in_decimals(params) -> None:
    ctx = params.context
    np.testing.assert_allclose(ctx.b, [0.005, 0.003, 0.0, 0.002, -0.003])
    np.testing.assert_allclose(ctx.beta_pol, [0.03, 0.015, 0.005, 0.01, 0.0])
    np.testing.assert_allclose(ctx.beta_mac, [0.01, 0.008, 0.005, 0.005, 0.003])
    np.testing.assert_allclose(ctx.gamma_pol, [0.5, 0.25, 0.1, 0.2, 0.0])
    np.testing.assert_allclose(ctx.gamma_mac, [0.2, 0.1, 0.05, 0.1, 0.0])
    assert ctx.beta_tend == pytest.approx(0.015)
    assert ctx.c_max == pytest.approx(0.03)


def test_fuzzy_sets(params) -> None:
    hz = params.fuzzy.horizon
    assert hz.universe == (0.0, 30.0)
    assert hz.sets["corto"].kind == "trap"
    assert hz.sets["corto"].params == (0.0, 0.0, 1.0, 3.0)
    assert hz.sets["mediano"].params == (2.0, 5.0, 8.0)
    assert hz.consequents == {"corto": 1.5, "mediano": 1.0, "largo": 0.7}

    ab = params.fuzzy.absorption
    assert ab.ratio_universe == (0.0, 1.0)
    assert ab.emergency_universe == (0.0, 12.0)
    assert ab.output_sets["media"].params == (0.25, 0.5, 0.75)
    assert [r.id for r in ab.rules] == ["RA1", "RA2", "RA3", "RA4", "RA5", "RA6"]
    assert (ab.rules[1].ratio, ab.rules[1].emergency, ab.rules[1].output) == (
        "bajo",
        "adecuada",
        "alta",
    )
    assert ab.sigma_floor == pytest.approx(0.03)
    assert ab.sigma_amplitude == pytest.approx(0.13)


def test_optimization_parameters(params) -> None:
    opt = params.optimization
    assert opt.phi == 50 and opt.kappa == pytest.approx(0.03)
    assert opt.max_weight == pytest.approx(0.40)
    assert (opt.population_size, opt.max_generations, opt.patience) == (80, 200, 25)
    assert opt.tournament_size == 3 and opt.elitism == 1
    assert opt.crossover_rate == pytest.approx(0.9)
    assert opt.mutation_rate == pytest.approx(0.1)
    assert opt.mutation_sigma == pytest.approx(0.05)


def test_risk_profiles_lambda_base(params) -> None:
    lam = params.risk_profiles.lambda_base
    assert lam[RiskProfile.MUY_AGRESIVO] == pytest.approx(0.2)
    assert lam[RiskProfile.MODERADO] == pytest.approx(1.0)
    assert lam[RiskProfile.MUY_CONSERVADOR] == pytest.approx(3.0)
    assert set(lam) == set(RiskProfile)


@pytest.fixture
def broken_dir(tmp_path: Path) -> Path:
    target = tmp_path / "parameters"
    shutil.copytree(DEFAULT_PARAMETERS_DIR, target)
    return target


def _edit(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_missing_category_raises(broken_dir: Path) -> None:
    _edit(broken_dir / "categories.json", lambda d: d["categories"].pop("debt"))
    with pytest.raises(ParameterError):
        load_parameters(broken_dir)


def test_negative_sigma_raises(broken_dir: Path) -> None:
    _edit(broken_dir / "categories.json", lambda d: d["categories"]["stocks"].update(sigma=-0.1))
    with pytest.raises(ParameterError):
        load_parameters(broken_dir)


def test_bad_membership_params_raise(broken_dir: Path) -> None:
    def mutate(d: dict) -> None:
        d["horizon"]["sets"]["mediano"] = {"type": "tri", "params": [8, 5, 2]}

    _edit(broken_dir / "fuzzy.json", mutate)
    with pytest.raises(ParameterError):
        load_parameters(broken_dir)


def test_max_weight_out_of_range_raises(broken_dir: Path) -> None:
    _edit(broken_dir / "optimization.json", lambda d: d.update(max_weight=0.1))
    with pytest.raises(ParameterError):
        load_parameters(broken_dir)


def test_missing_risk_profile_raises(broken_dir: Path) -> None:
    _edit(broken_dir / "risk_profiles.json", lambda d: d["lambda_base"].pop("moderado"))
    with pytest.raises(ParameterError):
        load_parameters(broken_dir)


def test_missing_file_raises(broken_dir: Path) -> None:
    (broken_dir / "context.json").unlink()
    with pytest.raises(ParameterError):
        load_parameters(broken_dir)
