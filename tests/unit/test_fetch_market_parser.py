"""Offline parsing of the BCRP HTML view used by scripts/fetch_market_data.py (no network)."""

import pytest

from scripts.fetch_market_data import parse_bcrp_table, parse_spanish_month, parse_value

PAGE = """
<html><head><title>Índices Bursátiles - Índice General BVL</title></head><body>
<table><tr><th class="cabecera">Fecha</th>
<th class="cabecera" abbr="series">Bolsa de Valores de Lima - Índices Bursátiles - Índice General BVL</th></tr>
<tr><td class="periodo">
  <b>Dic23</b> </td><td class="dato"> 25960.1 </td></tr>
<tr><td class="periodo"><b>Ene24</b></td><td class="dato">n.d.</td></tr>
<tr><td class="periodo"><b>Feb24</b></td><td class="dato"></td></tr>
<tr><td class="periodo"><b>Set24</b></td><td class="dato">6.7</td></tr>
</table></body></html>
"""


@pytest.mark.parametrize(
    ("label", "expected"),
    [("Ene24", "2024-01"), ("Ago10", "2010-08"), ("Dic99", "1999-12"), ("Set24", "2024-09"), ("sep2024", "2024-09")],
)
def test_spanish_month(label: str, expected: str) -> None:
    assert parse_spanish_month(label) == expected


@pytest.mark.parametrize("label", ["Jan24", "Ene", "Ene2"])
def test_spanish_month_rejects_unknown(label: str) -> None:
    with pytest.raises(ValueError):
        parse_spanish_month(label)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("6.7", 6.7), (" 14440.5 ", 14440.5), ("1,234.5", 1234.5), ("6,7", 6.7), ("n.d.", None), ("", None), ("—", None)],
)
def test_value(text: str, expected) -> None:
    assert parse_value(text) == expected


def test_table_rows_and_title() -> None:
    title, rows = parse_bcrp_table(PAGE)
    assert title == "Bolsa de Valores de Lima - Índices Bursátiles - Índice General BVL"
    assert rows == [("2023-12", 25960.1), ("2024-01", None), ("2024-02", None), ("2024-09", 6.7)]


def test_page_without_table_has_no_rows() -> None:
    assert parse_bcrp_table("<html><title>API</title><body>challenge</body></html>") == ("API", [])
