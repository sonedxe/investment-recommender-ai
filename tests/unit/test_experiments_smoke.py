"""Smoke test of the experiments runner: one seed, tiny GA, no figures (no matplotlib needed)."""

from __future__ import annotations

import csv

from experiments.ablation import CONFIGURATIONS, main

EXPECTED = [
    f"{name}_{kind}.csv"
    for name in ("ablation", "context", "gene", "calibration")
    for kind in ("runs", "summary")
] + ["ablation_convergence.csv", "README.md"]


def test_ablation_runner_writes_every_output(tmp_path):
    exit_code = main(["--seeds", "1", "--population", "8", "--max-generations", "3", "--no-plots",
                      "--out", str(tmp_path)])

    assert exit_code == 0
    for name in EXPECTED:
        assert (tmp_path / name).stat().st_size > 0, name
    with (tmp_path / "ablation_runs.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3 * len(CONFIGURATIONS)
    for row in rows:
        weights = sum(float(row[f"w_{c}"]) for c in ("stocks", "mixed", "debt", "bonds", "term"))
        assert abs(weights - 1.0) < 1e-6
    assert not list(tmp_path.glob("*.png"))
