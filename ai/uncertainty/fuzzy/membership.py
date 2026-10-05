"""Triangular and trapezoidal membership functions (vectorized, shoulder-safe)."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from ai.shared.parameters import MembershipSpec

__all__ = ["MembershipSpec", "membership", "trap", "tri"]


def _rising(x: np.ndarray, a: float, b: float) -> np.ndarray:
    if a == b:  # vertical left edge (left shoulder): full membership from b on
        return np.where(x >= b, 1.0, 0.0)
    return np.clip((x - a) / (b - a), 0.0, 1.0)


def _falling(x: np.ndarray, c: float, d: float) -> np.ndarray:
    if c == d:  # vertical right edge (right shoulder): full membership up to c
        return np.where(x <= c, 1.0, 0.0)
    return np.clip((d - x) / (d - c), 0.0, 1.0)


def _result(values: np.ndarray) -> float | np.ndarray:
    return float(values) if values.ndim == 0 else values


def trap(x: ArrayLike, a: float, b: float, c: float, d: float) -> float | np.ndarray:
    """Trapezoid rising on [a, b], 1 on [b, c], falling on [c, d]; a == b or c == d is a shoulder."""
    xs = np.asarray(x, dtype=float)
    return _result(np.minimum(_rising(xs, a, b), _falling(xs, c, d)))


def tri(x: ArrayLike, a: float, b: float, c: float) -> float | np.ndarray:
    """Triangle with feet a, c and peak b (a degenerate trapezoid with b == c)."""
    return trap(x, a, b, b, c)


def membership(spec: MembershipSpec, x: ArrayLike) -> float | np.ndarray:
    """Evaluate the membership function described by ``spec`` at ``x``."""
    if spec.kind == "tri":
        return tri(x, *spec.params)
    return trap(x, *spec.params)
