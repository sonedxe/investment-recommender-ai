"""Zero-order Sugeno inference: output = sum(w_i * z_i) / sum(w_i)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ai.uncertainty.fuzzy.inference import (
    FuzzyInferenceError,
    FuzzyRule,
    Memberships,
    Variables,
    fuzzify,
)


@dataclass(frozen=True)
class SugenoResult:
    memberships: Mapping[str, Mapping[str, float]]
    firing: Mapping[str, float]
    output: float


@dataclass(frozen=True)
class SugenoSystem:
    """Rule base whose consequents are crisp constants z_i."""

    inputs: Variables
    rules: tuple[FuzzyRule, ...]

    def evaluate(self, crisp: Mapping[str, float]) -> SugenoResult:
        return self.infer(fuzzify(crisp, self.inputs))

    def infer(self, memberships: Memberships) -> SugenoResult:
        """Run the rules on already-fuzzified inputs (e.g. a qualitative label)."""
        firing = {rule.id: rule.firing_strength(memberships) for rule in self.rules}
        total = sum(firing.values())
        if total <= 0.0:
            raise FuzzyInferenceError("no Sugeno rule fires: total firing strength is 0")
        weighted = sum(firing[rule.id] * float(rule.consequent) for rule in self.rules)
        return SugenoResult(memberships=memberships, firing=firing, output=weighted / total)
