"""Spanish number formatting shared by the explanation and the clarification texts."""

from __future__ import annotations


def format_money(value: float) -> str:
    """Soles with thousands comma and two decimals: 1250 -> ``S/ 1,250.00``; -150 -> ``-S/ 150.00``."""
    sign = "-" if round(value, 2) < 0 else ""
    return f"{sign}S/ {abs(value):,.2f}"


def format_percent(weight: float) -> str:
    """Weight as a percentage with at most one decimal: 0.4 -> ``40 %``; 0.125 -> ``12.5 %``."""
    value = round(weight * 100, 1)
    text = f"{value:.0f}" if value == int(value) else f"{value:.1f}"
    return f"{text} %"


def format_number(value: float) -> str:
    """Plain number with at most one decimal: 3.0 -> ``3``; 1.5 -> ``1.5``."""
    value = round(value, 1)
    return f"{value:.0f}" if value == int(value) else f"{value:.1f}"
