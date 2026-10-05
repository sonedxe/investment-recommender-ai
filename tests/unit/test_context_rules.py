"""Context rule base RC1-RC7 and its trace."""

import numpy as np
import pytest

from ai.context import RULES, evaluate_rules
from ai.shared import ContextFactors
from ai.shared.parameters import load_parameters


@pytest.fixture(scope="module")
def ctx():
    return load_parameters().context


def _ids(evaluation) -> list[str]:
    return [entry.rule_id for entry in evaluation.trace]


def test_rule_base_is_explicit_data() -> None:
    assert [rule.id for rule in RULES] == [f"RC{i}" for i in range(1, 8)]
    assert all(rule.condition and rule.effect for rule in RULES)


def test_missing_factors_fire_rc1_and_stay_neutral(ctx) -> None:
    evaluation = evaluate_rules(None, np.zeros(5), ctx)
    assert _ids(evaluation) == ["RC1", "RC2"]
    np.testing.assert_allclose(evaluation.c, ctx.b)
    np.testing.assert_allclose(evaluation.sigma_multiplier, 1.0)


def test_neutral_factors_only_apply_structural_precedent(ctx) -> None:
    evaluation = evaluate_rules(ContextFactors(), np.zeros(5), ctx)
    assert _ids(evaluation) == ["RC2"]


def test_adverse_politics_fires_rc3_with_numeric_effect(ctx) -> None:
    evaluation = evaluate_rules(ContextFactors(political=-1.0), np.zeros(5), ctx)
    assert _ids(evaluation) == ["RC2", "RC3"]
    rc3 = evaluation.trace[1]
    np.testing.assert_allclose(rc3.delta_mu, -ctx.beta_pol)
    np.testing.assert_allclose(rc3.delta_sigma_factor, ctx.gamma_pol)
    assert "adverso" in rc3.condition


def test_favorable_politics_fires_rc4_without_risk_change(ctx) -> None:
    evaluation = evaluate_rules(ContextFactors(political=0.5), np.zeros(5), ctx)
    rc4 = evaluation.trace[1]
    assert rc4.rule_id == "RC4"
    np.testing.assert_allclose(rc4.delta_mu, 0.5 * ctx.beta_pol)
    np.testing.assert_allclose(rc4.delta_sigma_factor, 0.0)


@pytest.mark.parametrize("macro, raises_risk", [(-0.5, True), (0.5, False)])
def test_macro_rule_is_asymmetric(ctx, macro, raises_risk) -> None:
    evaluation = evaluate_rules(ContextFactors(macro=macro), np.zeros(5), ctx)
    rc5 = evaluation.trace[1]
    assert rc5.rule_id == "RC5"
    np.testing.assert_allclose(rc5.delta_mu, macro * ctx.beta_mac)
    expected = 0.5 * ctx.gamma_mac if raises_risk else np.zeros(5)
    np.testing.assert_allclose(rc5.delta_sigma_factor, expected)


def test_trend_rule_applies_per_category(ctx) -> None:
    trend = np.array([1.0, 0.0, -1.0, 0.0, 0.0])
    evaluation = evaluate_rules(ContextFactors(), trend, ctx)
    rc6 = evaluation.trace[-1]
    assert rc6.rule_id == "RC6"
    np.testing.assert_allclose(rc6.delta_mu, ctx.beta_tend * trend)


def test_clipping_rule_records_the_cut(ctx) -> None:
    evaluation = evaluate_rules(ContextFactors(political=-1.0, macro=-1.0), np.full(5, -1.0), ctx)
    rc7 = evaluation.trace[-1]
    assert rc7.rule_id == "RC7"
    # stocks: 0.005 - 0.03 - 0.01 - 0.015 = -0.05 -> -0.03, cut of +0.02
    assert rc7.delta_mu[0] == pytest.approx(0.02)
    assert evaluation.c[0] == pytest.approx(-ctx.c_max)
