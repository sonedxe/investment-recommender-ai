"""Offline SBS valor cuota handling in scripts/fetch_market_data.py (no network)."""

import datetime as dt
from pathlib import Path

import pytest

from scripts.fetch_market_data import (
    SBS_ALL_AFPS,
    build_sbs_series,
    equal_weight_index,
    month_end_levels,
    parse_sbs_workbook,
    reject_daily_spikes,
    sbs_candidate_urls,
)

D = dt.date


def test_candidate_urls_step_back_with_sbs_month_names() -> None:
    urls = sbs_candidate_urls(D(2026, 10, 5))
    assert len(urls) == 4
    assert urls[0].endswith("/2026/Octubre/B-220932-oc2026.XLS")
    assert urls[1].endswith("/2026/Setiembre/B-220932-se2026.XLS")
    assert sbs_candidate_urls(D(2026, 1, 2))[1].endswith("/2025/Diciembre/B-220932-di2025.XLS")


def test_month_end_takes_last_business_day_and_drops_open_month() -> None:
    points = [(D(2024, 1, 30), 10.0), (D(2024, 1, 31), 11.0), (D(2024, 2, 28), 12.0), (D(2024, 2, 29), 13.0),
              (D(2024, 3, 4), 14.0)]
    assert month_end_levels(points, current="2024-03", start="2024-01") == {"2024-01": 11.0, "2024-02": 13.0}
    assert month_end_levels(points, current="2024-03", start="2024-02") == {"2024-02": 13.0}


def test_month_end_drops_final_month_cut_before_its_last_weekday() -> None:
    points = [(D(2026, 8, 31), 10.0), (D(2026, 9, 25), 11.0)]  # 2026-09-30 is a Wednesday
    assert month_end_levels(points, current="2026-10", start="2026-01") == {"2026-08": 10.0}
    # A month ending on a weekend closes on its last Friday.
    assert month_end_levels([(D(2024, 8, 30), 9.0)], current="2024-10", start="2024-01") == {"2024-08": 9.0}


def test_spike_filter_drops_single_day_jumps_only() -> None:
    points = [(D(2024, 1, 1), 10.0), (D(2024, 1, 2), 100.0), (D(2024, 1, 3), 10.1), (D(2024, 1, 4), 0.1)]
    kept, rejected = reject_daily_spikes(points)
    assert kept == [(D(2024, 1, 1), 10.0), (D(2024, 1, 3), 10.1)] and rejected == 2
    assert reject_daily_spikes([(D(2024, 1, 1), 10.0), (D(2024, 1, 2), 14.9)]) == (
        [(D(2024, 1, 1), 10.0), (D(2024, 1, 2), 14.9)], 0)


def test_spike_filter_raises_on_persistent_level_break() -> None:
    points = [(D(2024, 1, 1), 10.0), (D(2024, 1, 2), 100.0), (D(2024, 1, 3), 101.0)]
    with pytest.raises(ValueError):
        reject_daily_spikes(points)


def test_equal_weight_chained_index() -> None:
    levels = {"A": {"2024-01": 10.0, "2024-02": 11.0, "2024-03": 11.0},
              "B": {"2024-01": 50.0, "2024-02": 50.0, "2024-03": 45.0, "2024-04": 46.0}}
    index = equal_weight_index(levels, ("A", "B"))
    assert [m for m, _ in index] == ["2024-01", "2024-02", "2024-03"]
    assert [v for _, v in index] == pytest.approx([100.0, 105.0, 105.0 * 0.95])


def test_equal_weight_index_rejects_gaps() -> None:
    levels = {"A": {"2024-01": 1.0, "2024-03": 1.1}, "B": {"2024-01": 1.0, "2024-03": 1.0}}
    with pytest.raises(ValueError):
        equal_weight_index(levels, ("A", "B"))


def _workbook(path: Path) -> Path:
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Valor Cuota diario por Tipo de Fondo de Pensiones y AFP"])
    ws.append(["(En Soles)"])
    groups = [None]
    for fund in range(4):
        groups += [f"Fondo Tipo {fund}", None, None, None]
    ws.append(groups)
    ws.append(["Mes", *(["Habitat", "Integra", "Prima", "Profuturo"] * 4)])
    rows = [
        (dt.datetime(2024, 1, 30), (None, 10.0, 20.0, 30.0)),
        (dt.datetime(2024, 1, 31), (5.0, 11.0, 22.0, 33.0)),
        (dt.datetime(2024, 2, 29), (5.5, 11.0, 22.0, 33.0)),
        (dt.datetime(2024, 3, 28), (5.5, 12.1, 22.0, 33.0)),
        (dt.datetime(2024, 3, 29), (5.5, 12.1, 22.0, 99.0)),  # one-day spike in Profuturo
        (dt.datetime(2024, 4, 1), (5.5, 12.1, 22.0, 33.0)),
        (dt.datetime(2024, 4, 30), (5.5, 12.1, 24.2, 36.3)),
    ]
    for stamp, fund2 in rows:
        ws.append([stamp, *([1.0] * 8), *fund2, *([2.0] * 4)])
    ws.append(["Fuente: SBS"])
    target = path / "b220932.xlsx"
    wb.save(target)
    return target


def test_parse_workbook_reads_fund_type_2_columns(tmp_path: Path) -> None:
    series = parse_sbs_workbook(_workbook(tmp_path))
    assert set(series) == set(SBS_ALL_AFPS)
    assert series["Habitat"][0] == (D(2024, 1, 31), 5.0)
    assert series["Integra"][:2] == [(D(2024, 1, 30), 10.0), (D(2024, 1, 31), 11.0)]
    assert len(series["Prima"]) == 7


def test_parse_workbook_without_fund_header_raises(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    wb.active.append(["otra cosa"])
    wb.save(tmp_path / "x.xlsx")
    with pytest.raises(ValueError):
        parse_sbs_workbook(tmp_path / "x.xlsx")


def test_build_series_end_to_end_from_workbook(tmp_path: Path) -> None:
    daily = parse_sbs_workbook(_workbook(tmp_path))
    levels, index, rejected = build_sbs_series(daily, current="2024-05", start="2024-01")
    assert rejected["Profuturo"] == 1 and rejected["Integra"] == 0
    assert levels["Profuturo"] == {"2024-01": 33.0, "2024-02": 33.0, "2024-03": 33.0, "2024-04": 36.3}
    assert levels["Habitat"]["2024-01"] == 5.0
    # Feb: (0 + 0 + 0)/3; Mar: (+10 % + 0 + 0)/3; Apr: (0 + 10 % + 10 %)/3.
    assert [v for _, v in index] == pytest.approx([100.0, 100.0, 100.0 * (1 + 0.1 / 3), 100.0 * (1 + 0.1 / 3) * (1 + 0.2 / 3)])
