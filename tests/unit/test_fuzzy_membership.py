"""Membership functions: class reference values, shoulders and vectorization."""

import numpy as np
import pytest

from ai.uncertainty.fuzzy.membership import MembershipSpec, membership, trap, tri


def test_class_reference_values() -> None:
    assert trap(3, 0, 0, 2, 5) == pytest.approx(0.6667, abs=1e-4)
    assert tri(3, 2, 5, 8) == pytest.approx(0.3333, abs=1e-4)


def test_left_shoulder_is_one_at_the_edge() -> None:
    assert trap(0, 0, 0, 1, 3) == 1.0
    assert tri(0, 0, 0, 4) == 1.0
    assert tri(2, 0, 0, 4) == pytest.approx(0.5)


def test_right_shoulder_is_one_at_the_edge() -> None:
    assert trap(30, 6, 10, 30, 30) == 1.0
    assert tri(4, 0, 4, 4) == 1.0


def test_outside_support_is_zero() -> None:
    assert tri(1, 2, 5, 8) == 0.0
    assert tri(9, 2, 5, 8) == 0.0
    assert trap(5, 0, 0, 2, 5) == 0.0


def test_vectorized_values_stay_in_unit_interval() -> None:
    x = np.linspace(-5, 35, 401)
    for values in (tri(x, 2, 5, 8), trap(x, 0, 0, 1, 3), trap(x, 6, 10, 30, 30)):
        assert values.shape == x.shape
        assert np.all((values >= 0) & (values <= 1))


def test_spec_from_json_evaluates() -> None:
    spec = MembershipSpec.from_json({"type": "tri", "params": [2, 5, 8]})
    assert membership(spec, 5) == 1.0
    np.testing.assert_allclose(membership(spec, np.array([2.0, 3.5, 8.0])), [0.0, 0.5, 0.0])
