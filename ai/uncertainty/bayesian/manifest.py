"""Read ``data/market/manifest.json`` and turn each category's series into monthly returns.

The manifest (written by ``scripts/fetch_market_data.py``) maps a category to a
local CSV and the kind of values it holds (``index``, ``yield``, ``rate``) or to
a ``composite`` of other categories. Only local files are read here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ai.shared.types import CATEGORY_ORDER, CategoryId
from ai.uncertainty.bayesian.estimation import (
    MonthlySeries,
    composite_returns,
    monthly_returns,
    rate_returns,
    read_series,
    yield_returns,
)

MANIFEST_NAME = "manifest.json"
KINDS = ("index", "yield", "rate", "composite")


@dataclass(frozen=True)
class SeriesSpec:
    """One manifest entry; ``components``/``weights`` only for composites, ``duration_years`` for yields."""

    category: CategoryId
    kind: str
    source: str
    file: str | None = None
    series_code: str | None = None
    title: str | None = None
    duration_years: float | None = None
    components: tuple[CategoryId, ...] = ()
    weights: tuple[float, ...] = ()


def _spec(category: CategoryId, raw: Mapping) -> SeriesSpec:
    kind = raw.get("kind")
    if kind not in KINDS:
        raise ValueError(f"manifest: {category.value} has unknown kind {kind!r}")
    spec = SeriesSpec(
        category=category,
        kind=kind,
        source=str(raw.get("source") or "unknown"),
        file=raw.get("file"),
        series_code=raw.get("series_code"),
        title=raw.get("title"),
        duration_years=None if raw.get("duration_years") is None else float(raw["duration_years"]),
        components=tuple(CategoryId(c) for c in raw.get("components") or ()),
        weights=tuple(float(w) for w in raw.get("weights") or ()),
    )
    if kind == "yield" and (spec.duration_years is None or spec.duration_years < 0):
        raise ValueError(f"manifest: {category.value} (yield) needs a non-negative duration_years")
    if kind == "composite":
        if not spec.components or len(spec.components) != len(spec.weights):
            raise ValueError(f"manifest: {category.value} composite needs matching components and weights")
        if category in spec.components or any(
            w < 0 for w in spec.weights
        ) or abs(sum(spec.weights) - 1.0) > 1e-9:
            raise ValueError(f"manifest: {category.value} composite weights must be >= 0, sum to 1, no self-reference")
    elif not spec.file:
        raise ValueError(f"manifest: {category.value} needs a file")
    return spec


def load_manifest(data_dir: Path | str) -> dict[CategoryId, SeriesSpec]:
    """Specs by category; an absent manifest means no data (every category keeps its prior)."""
    path = Path(data_dir) / MANIFEST_NAME
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8")).get("categories", {})
    return {c: _spec(c, raw[c.value]) for c in CATEGORY_ORDER if c.value in raw}


def category_returns(specs: Mapping[CategoryId, SeriesSpec], data_dir: Path | str) -> dict[CategoryId, MonthlySeries | None]:
    """Monthly returns per category; ``None`` when the file (or a composite component) is missing."""
    directory = Path(data_dir)
    returns: dict[CategoryId, MonthlySeries | None] = {c: None for c in CATEGORY_ORDER}
    for category, spec in specs.items():
        if spec.kind == "composite":
            continue
        path = directory / spec.file
        if not path.is_file():
            continue
        series = read_series(path)
        if spec.kind == "index":
            returns[category] = monthly_returns(series)
        elif spec.kind == "yield":
            returns[category] = yield_returns(series, spec.duration_years)
        else:
            returns[category] = rate_returns(series)
    for category, spec in specs.items():
        if spec.kind != "composite":
            continue
        parts = [(returns.get(c), w) for c, w in zip(spec.components, spec.weights)]
        if all(r is not None for r, _ in parts):
            returns[category] = composite_returns(parts)
    return returns
