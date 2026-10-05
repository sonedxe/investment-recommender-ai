"""Download the monthly market series and write data/market/*.csv plus manifest.json.

Sources (decision D3, revised in W14):

- BCRP (Banco Central de Reserva del Perú) statistics, monthly series in soles. The
  BCRP JSON API is protected by an anti-bot challenge, but the public HTML view runs
  that challenge in a real browser, so each series is loaded once with headless
  Chromium (``--dump-dom``) and its table is parsed here.
- Yahoo Finance (optional fallback for stocks, ``--stocks-source yahoo``): the
  ``EPU`` ETF converted to soles with ``PEN=X`` via ``yfinance`` (requirements-data.txt).
- Mixed funds: BCRP publishes no mutual-fund return series, so the category is a
  documented composite of the stocks and bonds series (weights in the manifest).

CSV values are written exactly as published (index level or % annual rate);
months marked "n.d." or empty are skipped. The current, still-open month is dropped.
This is the only place with network access; the app reads the local files only.

Usage: python scripts/fetch_market_data.py [--out data/market] [--start 2010-1]
                                           [--stocks-source bcrp|yahoo]
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import shutil
import subprocess
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BCRP_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/{code}/html/{start}/{end}"
CHROMIUM_CANDIDATES = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome")
MAX_ATTEMPTS = 2  # be gentle with BCRP: one request per series, at most one retry
SPANISH_MONTHS = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12,
}
MISSING_MARKERS = {"", "n.d.", "nd", "n.d", "-", "—"}
MIN_MONTHS = 24


@dataclass(frozen=True)
class BcrpSeries:
    category: str
    code: str
    file: str
    kind: str  # index | yield | rate
    duration_years: float | None = None
    duration_note: str | None = None


BCRP_SERIES = (
    BcrpSeries("stocks", "PN01142MM", "acciones__bcrp_indice_general_bvl.csv", "index"),
    # Debt: PN01113MM (private bonds in S/ up to 3 years) and PN01124MM (Treasury bonds up to
    # 5 years) are issuance yields with 0.0 in every month without issues (146/200 and 118/188
    # months in 2010-2026), too sparse for monthly returns. The yield of the outstanding stock
    # of BCRP certificates of deposit is published every month and is used instead.
    BcrpSeries(
        "debt", "PN06503OM", "deuda__bcrp_tasa_saldo_cd_bcrp.csv", "yield", 0.5,
        "Aproximación: duración supuesta de ~0,5 años para el saldo de CD BCRP (plazos mayormente "
        "menores a un año); el fondo de deuda real puede tener mayor duración.",
    ),
    BcrpSeries(
        "bonds", "PD31895MM", "btp__bcrp_rendimiento_10a.csv", "yield", 7.0,
        "Aproximación: duración modificada supuesta de ~7 años para un bono soberano a 10 años.",
    ),
    BcrpSeries("term", "PN07814NM", "deposito__bcrp_tasa_pasiva_181_360d.csv", "rate"),
)
YAHOO_STOCKS_FILE = "acciones__yahoo_epu_en_soles.csv"
# Mixed funds hold equities plus bonds: 0.5 x BVL index + 0.5 x BTP 10y (duration 7).
MIXED_COMPOSITE = {"components": ["stocks", "bonds"], "weights": [0.5, 0.5]}


# --------------------------------------------------------------------------- parsing


def parse_spanish_month(label: str) -> str:
    """``'Ene24'`` -> ``'2024-01'``; two-digit years above next year are read as 19xx."""
    text = label.strip()
    month = SPANISH_MONTHS.get(text[:3].lower())
    year_text = text[3:].strip()
    if month is None or not year_text.isdigit() or len(year_text) not in (2, 4):
        raise ValueError(f"unrecognized BCRP period {label!r}")
    year = int(year_text)
    if len(year_text) == 2:
        pivot = (dt.date.today().year + 1) % 100
        year += 2000 if year <= pivot else 1900
    return f"{year:04d}-{month:02d}"


def parse_value(text: str) -> float | None:
    """Published number or ``None`` for "n.d."/empty; accepts ``1,234.5`` and ``6,7``."""
    cleaned = text.strip().replace("\xa0", "").replace(" ", "")
    if cleaned.lower() in MISSING_MARKERS:
        return None
    if "," in cleaned:
        cleaned = cleaned.replace(",", "") if "." in cleaned else cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


class _BcrpTableParser(HTMLParser):
    """Collect the text of ``<td class="periodo">`` / ``<td class="dato">`` cells in order."""

    def __init__(self) -> None:
        super().__init__()
        self.cells: list[tuple[str, str]] = []
        self.title: str | None = None
        self._cell: str | None = None
        self._text: list[str] = []
        self._in_title = False
        self._in_header = False

    def handle_starttag(self, tag, attrs):
        if tag == "th" and dict(attrs).get("abbr") == "series":
            self._in_header, self._text = True, []
        elif tag == "td":
            classes = (dict(attrs).get("class") or "").split()
            self._cell = "periodo" if "periodo" in classes else "dato" if "dato" in classes else None
            self._text = []
        elif tag == "title":
            self._in_title, self._text = True, []

    def handle_endtag(self, tag):
        if tag == "td" and self._cell is not None:
            self.cells.append((self._cell, "".join(self._text).strip()))
            self._cell = None
        elif tag == "title" and self._in_title:
            self.title = self.title or " ".join("".join(self._text).split())
            self._in_title = False
        elif tag == "th" and self._in_header:
            # The column header carries the full published name (group - series); prefer it.
            self.title, self._in_header = " ".join("".join(self._text).split()), False

    def handle_data(self, data):
        if self._cell is not None or self._in_title or self._in_header:
            self._text.append(data)


def parse_bcrp_table(html: str) -> tuple[str | None, list[tuple[str, float | None]]]:
    """Return the page title and ``[(YYYY-MM, value or None), ...]`` from a BCRP HTML view."""
    parser = _BcrpTableParser()
    parser.feed(html)
    rows: list[tuple[str, float | None]] = []
    period: str | None = None
    for kind, text in parser.cells:
        if kind == "periodo":
            period = text
        elif kind == "dato" and period is not None:
            rows.append((parse_spanish_month(period), parse_value(text)))
            period = None
    return parser.title, rows


# --------------------------------------------------------------------------- network


def find_chromium() -> str:
    for name in CHROMIUM_CANDIDATES:
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit(
        "Chromium (or Google Chrome) is required to download BCRP series: the BCRP site only "
        "serves data after a browser challenge. Install it (e.g. 'sudo pacman -S chromium' or "
        "'sudo apt install chromium') or use --stocks-source yahoo for the stocks fallback."
    )


def dump_dom(chromium: str, url: str) -> str:
    command = [
        chromium, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--virtual-time-budget=15000", "--dump-dom", url,
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"chromium exited with {result.returncode} for {url}")
    return result.stdout


def fetch_bcrp(chromium: str, code: str, start: str, end: str) -> tuple[str, str, list[tuple[str, float]]]:
    url = BCRP_URL.format(code=code, start=start, end=end)
    last_error: Exception | None = None
    for _ in range(MAX_ATTEMPTS):
        try:
            title, rows = parse_bcrp_table(dump_dom(chromium, url))
        except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
            last_error = exc
            continue
        if rows:
            return url, title or code, [(m, v) for m, v in rows if v is not None]
        last_error = RuntimeError(f"no data table in the page for {code} (anti-bot challenge not passed?)")
    raise RuntimeError(f"could not download {code}: {last_error}")


def _yahoo_monthly_close(ticker: str) -> dict[str, float]:
    import numpy as np
    import yfinance as yf  # local import: optional dependency

    frame = yf.Ticker(ticker).history(period="max", interval="1mo", auto_adjust=True)
    if frame.empty:
        raise RuntimeError(f"no data returned for {ticker}")
    return {
        stamp.strftime("%Y-%m"): float(value)
        for stamp, value in frame["Close"].items()
        if np.isfinite(value) and value > 0
    }


def fetch_yahoo_stocks() -> list[tuple[str, float]]:
    epu, pen = _yahoo_monthly_close("EPU"), _yahoo_monthly_close("PEN=X")
    return [(m, epu[m] * pen[m]) for m in sorted(set(epu) & set(pen))]


# --------------------------------------------------------------------------- output


def write_csv(path: Path, rows: list[tuple[str, float]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "value"])
        for month, value in rows:
            writer.writerow([f"{month}-01", repr(value) if isinstance(value, float) else value])


def _span(rows: list[tuple[str, float]]) -> dict:
    return {"first": rows[0][0], "last": rows[-1][0], "months": len(rows)}


def _complete(rows: list[tuple[str, float]], current: str) -> list[tuple[str, float]]:
    return sorted((m, v) for m, v in rows if m < current)


def fetch(out_dir: Path, start: str, stocks_source: str) -> Path:
    today = dt.date.today()
    current, end = today.strftime("%Y-%m"), f"{today.year}-{today.month}"
    fetched_at = today.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    entries: dict[str, dict] = {}
    months_by_category: dict[str, set[str]] = {}

    chromium = find_chromium()
    for spec in BCRP_SERIES:
        if spec.category == "stocks" and stocks_source == "yahoo":
            continue
        url, title, rows = fetch_bcrp(chromium, spec.code, start, end)
        rows = _complete(rows, current)
        if spec.kind != "index":
            # BCRP writes 0.0 for months without operations in rate series: treat as missing.
            rows = [(m, v) for m, v in rows if v != 0.0]
        if len(rows) < MIN_MONTHS:
            raise RuntimeError(f"{spec.code}: only {len(rows)} months with data")
        write_csv(out_dir / spec.file, rows)
        entry = {"file": spec.file, "source": "BCRP", "series_code": spec.code, "title": title, "kind": spec.kind}
        if spec.duration_years is not None:
            entry["duration_years"] = spec.duration_years
            entry["duration_note"] = spec.duration_note
        entries[spec.category] = {**entry, "url": url, "fetched_at": fetched_at, **_span(rows)}
        months_by_category[spec.category] = {m for m, _ in rows}
        print(f"{spec.category:7s} {spec.code}: {len(rows)} months ({rows[0][0]} .. {rows[-1][0]}) -> {spec.file}")

    if stocks_source == "yahoo":
        rows = _complete(fetch_yahoo_stocks(), current)
        write_csv(out_dir / YAHOO_STOCKS_FILE, rows)
        entries["stocks"] = {
            "file": YAHOO_STOCKS_FILE, "source": "Yahoo", "series_code": "EPU*PEN=X",
            "title": "iShares MSCI Peru ETF (EPU) convertido a soles con PEN=X", "kind": "index",
            "url": "https://finance.yahoo.com/quote/EPU", "fetched_at": fetched_at, **_span(rows),
        }
        months_by_category["stocks"] = {m for m, _ in rows}
        print(f"stocks  Yahoo EPU*PEN=X: {len(rows)} months -> {YAHOO_STOCKS_FILE}")

    common = sorted(set.intersection(*(months_by_category[c] for c in MIXED_COMPOSITE["components"])))
    entries["mixed"] = {
        "file": None, "source": "composite", "series_code": None,
        "title": "Compuesto a partir de series reales: 50 % acciones (Índice General BVL) + 50 % bonos (BTP 10 años) (retornos mensuales)",
        "kind": "composite", **MIXED_COMPOSITE,
        "url": None, "fetched_at": fetched_at,
        "first": common[0], "last": common[-1], "months": len(common),
    }

    manifest = {
        "description": "Monthly market series per category (W14). Values in each CSV are exactly as "
        "published: index level (kind=index) or % annual rate (kind=yield|rate). "
        "ai/uncertainty/bayesian/market.py converts them to monthly returns by kind.",
        "generated_by": "scripts/fetch_market_data.py",
        "categories": {c: entries[c] for c in ("stocks", "mixed", "debt", "bonds", "term")},
    }
    target = out_dir / "manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {target}")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "market")
    parser.add_argument("--start", default="2010-1", help="first month, BCRP format YYYY-M")
    parser.add_argument("--stocks-source", choices=("bcrp", "yahoo"), default="bcrp")
    args = parser.parse_args()
    fetch(args.out, args.start, args.stocks_source)


if __name__ == "__main__":
    main()
