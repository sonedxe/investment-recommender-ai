"""Fuzzy logic: membership functions, Sugeno and Mamdani engines, horizon and absorption systems."""

from ai.uncertainty.fuzzy.absorption import AbsorptionResult, evaluate_absorption
from ai.uncertainty.fuzzy.horizon import HorizonResult, evaluate_horizon
from ai.uncertainty.fuzzy.inference import FuzzyInferenceError, FuzzyRule
from ai.uncertainty.fuzzy.mamdani import MamdaniResult, MamdaniSystem
from ai.uncertainty.fuzzy.membership import MembershipSpec, membership, trap, tri
from ai.uncertainty.fuzzy.sugeno import SugenoResult, SugenoSystem

__all__ = [
    "AbsorptionResult",
    "FuzzyInferenceError",
    "FuzzyRule",
    "HorizonResult",
    "MamdaniResult",
    "MamdaniSystem",
    "MembershipSpec",
    "SugenoResult",
    "SugenoSystem",
    "evaluate_absorption",
    "evaluate_horizon",
    "membership",
    "trap",
    "tri",
]
