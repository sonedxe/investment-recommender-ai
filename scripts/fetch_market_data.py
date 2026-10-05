"""Download the stocks proxy series once and store it as data/market/stocks.csv.

Source (D3): Yahoo Finance via ``yfinance`` -- ``EPU`` (iShares MSCI Peru ETF, USD,
dividend-adjusted close) and ``PEN=X`` (soles per US dollar), monthly bars for
the last 10 years. The ETF is converted to soles: value = EPU_close * PEN=X_close.
The current, still-open month is dropped. This is the only place with network
access; ``yfinance`` lives in requirements-data.txt, not in the app requirements.

Usage: python scripts/fetch_market_data.py [--out data/market]
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TICKERS = ("EPU", "PEN=X")


def _monthly_close(ticker: str) -> dict[str, float]:
    import yfinance as yf  # local import: optional dependency

    frame = yf.Ticker(ticker).history(period="10y", interval="1mo", auto_adjust=True)
    if frame.empty:
        raise RuntimeError(f"no data returned for {ticker}")
    closes = {}
    for stamp, value in frame["Close"].items():
        if np.isfinite(value) and value > 0:
            closes[stamp.strftime("%Y-%m")] = float(value)
    return closes


def fetch(out_dir: Path) -> Path:
    epu, pen = (_monthly_close(t) for t in TICKERS)
    current = dt.date.today().strftime("%Y-%m")
    months = sorted(m for m in set(epu) & set(pen) if m < current)
    if len(months) < 24:
        raise RuntimeError(f"only {len(months)} overlapping complete months")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "stocks.csv"
    with open(target, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "value"])
        for month in months:
            writer.writerow([f"{month}-01", f"{epu[month] * pen[month]:.6f}"])
    print(f"wrote {len(months)} months ({months[0]} .. {months[-1]}) to {target}")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "market")
    fetch(parser.parse_args().out)


if __name__ == "__main__":
    main()
