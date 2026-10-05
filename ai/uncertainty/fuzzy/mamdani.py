"""Mamdani inference: min implication (clipping), max aggregation, centroid."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from ai.uncertainty.fuzzy.inference import (
    FuzzyInferenceError,
    FuzzyRule,
    Memberships,
    Variables,
    fuzzify,
)
from ai.uncertainty.fuzzy.membership import MembershipSpec, membership

DEFAULT_RESOLUTION = 1001


def centroid(universe: np.ndarray, mu: np.ndarray) -> float:
    """Centre of gravity of a discretized fuzzy set."""
    area = np.trapezoid(mu, universe)
    if area <= 0.0:
        raise FuzzyInferenceError("aggregated fuzzy set is empty: centroid undefined")
    return float(np.trapezoid(universe * mu, universe) / area)


@dataclass(frozen=True)
class MamdaniResult:
    memberships: Mapping[str, Mapping[str, float]]
    activations: Mapping[str, float]
    universe: np.ndarray
    aggregated: np.ndarray
    centroid: float


@dataclass(frozen=True)
class MamdaniSystem:
    """Rule base whose consequents are names of fuzzy sets over the output universe."""

    inputs: Variables
    output_universe: tuple[float, float]
    output_sets: Mapping[str, MembershipSpec]
    rules: tuple[FuzzyRule, ...]
    resolution: int = DEFAULT_RESOLUTION

    def __post_init__(self) -> None:
        if self.resolution < DEFAULT_RESOLUTION:
            raise ValueError(f"resolution must be at least {DEFAULT_RESOLUTION} points")
        unknown = {r.consequent for r in self.rules} - set(self.output_sets)
        if unknown:
            raise ValueError(f"rules reference unknown output sets: {sorted(unknown)}")

    def universe(self) -> np.ndarray:
        return np.linspace(*self.output_universe, self.resolution)

    def evaluate(self, crisp: Mapping[str, float]) -> MamdaniResult:
        return self.infer(fuzzify(crisp, self.inputs))

    def aggregate(self, memberships: Memberships) -> tuple[dict[str, float], np.ndarray, np.ndarray]:
        """Steps 1-4 of the FIS: activations and the aggregated output set (no defuzzification)."""
        universe = self.universe()
        activations = {rule.id: rule.firing_strength(memberships) for rule in self.rules}
        aggregated = np.zeros_like(universe)
        for rule in self.rules:
            clipped = np.minimum(activations[rule.id], membership(self.output_sets[rule.consequent], universe))
            aggregated = np.maximum(aggregated, clipped)
        return activations, universe, aggregated

    def infer(self, memberships: Memberships) -> MamdaniResult:
        activations, universe, aggregated = self.aggregate(memberships)
        return MamdaniResult(
            memberships=memberships,
            activations=activations,
            universe=universe,
            aggregated=aggregated,
            centroid=centroid(universe, aggregated),
        )
