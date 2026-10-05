"""Loader for data/parameters/bayes.json."""

import json
import shutil
from pathlib import Path

import pytest

from ai.shared.parameters import DEFAULT_PARAMETERS_DIR, ParameterError, load_parameters


def test_bayes_parameters_load() -> None:
    bayes = load_parameters().bayes
    assert tuple(bayes.prior_mean_sd) == pytest.approx((0.03, 0.02, 0.01, 0.01, 0.005))
    assert bayes.min_months == 24
    assert bayes.trend_window_months == 12


def test_bayes_missing_category_raises(tmp_path: Path) -> None:
    target = tmp_path / "parameters"
    shutil.copytree(DEFAULT_PARAMETERS_DIR, target)
    path = target / "bayes.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["prior_mean_sd"]["term"]
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ParameterError):
        load_parameters(target)
