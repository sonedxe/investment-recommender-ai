"""Rule representation, fuzzification and firing strength shared by both engines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping, TypeVar

from ai.uncertainty.fuzzy.membership import MembershipSpec, membership

Consequent = TypeVar("Consequent")
Variables = Mapping[str, Mapping[str, MembershipSpec]]
Memberships = Mapping[str, Mapping[str, float]]


class FuzzyInferenceError(ValueError):
    """Inference cannot produce an output (e.g. no rule fires)."""


@dataclass(frozen=True)
class FuzzyRule:
    """IF var1 is set1 <op> var2 is set2 ... THEN consequent.

    ``consequent`` is a crisp value for Sugeno and an output-set name for Mamdani.
    AND is evaluated with min and OR with max.
    """

    id: str
    antecedents: tuple[tuple[str, str], ...]
    consequent: float | str
    operator: Literal["and", "or"] = "and"

    def __post_init__(self) -> None:
        if not self.antecedents:
            raise ValueError(f"rule {self.id} needs at least one antecedent")
        if self.operator not in ("and", "or"):
            raise ValueError(f"rule {self.id}: operator must be 'and' or 'or'")

    def firing_strength(self, memberships: Memberships) -> float:
        degrees = [memberships[var][fuzzy_set] for var, fuzzy_set in self.antecedents]
        return float(min(degrees) if self.operator == "and" else max(degrees))


def fuzzify(inputs: Mapping[str, float], variables: Variables) -> dict[str, dict[str, float]]:
    """Membership degree of each crisp input in every set of its variable."""
    missing = set(variables) - set(inputs)
    if missing:
        raise ValueError(f"missing crisp inputs: {sorted(missing)}")
    return {
        var: {name: float(membership(spec, inputs[var])) for name, spec in sets.items()}
        for var, sets in variables.items()
    }
