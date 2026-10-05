# Market data sources (decision D3)

Each `<category>.csv` holds a monthly level series (`date,value`, first day of the month).
`ai/uncertainty/bayesian/market.py` uses a file only when it yields at least 24 monthly
returns (`data/parameters/bayes.json`); otherwise the category keeps its Annex A prior.

| Category | File | Source | Fetched | Transformation |
|---|---|---|---|---|
| Stocks (`stocks`) | `stocks.csv` | Yahoo Finance via `yfinance`: `EPU` (iShares MSCI Peru ETF, dividend-adjusted monthly close, USD) and `PEN=X` (soles per USD, monthly close) | 2026-10-04, `scripts/fetch_market_data.py` | `value = EPU × PEN=X`; months present in both series; current open month dropped. 119 months, 2016-11 .. 2026-09 |
| Mixed funds (`mixed`) | — | Annex A prior (no data) | — | — |
| Debt funds (`debt`) | — | Annex A prior (no data) | — | — |
| Sovereign bonds (`bonds`) | — | Annex A prior (no data) | — | — |
| Term deposit (`term`) | — | Annex A prior (no data) | — | — |

Correlations: only pairs of data-backed categories are estimated; with stocks as the
only series, the whole matrix is the documented `default_correlation` of Annex A.

## Caveats

1. **EPU is a proxy.** It tracks the Peruvian equity market (MSCI Peru), not a Peruvian
   equity mutual fund; fund fees and composition differ.
2. **EPU is quoted in USD.** It is converted to soles with `PEN=X`, so the series mixes the
   equity return with the USD/PEN exchange-rate return, as a local investor would see it.
3. **BCRP is not automated.** The BCRP statistics API is blocked by an anti-bot challenge for
   scripted requests; BTP yields (`PD31895MM`) and deposit rates must be downloaded manually
   from the web view if they are added later.
4. **BTP yield ≠ return.** A bond yield series is not the holding-period return (which also
   depends on price changes); using it as μ would be a declared simplification.
5. **Yahoo terms.** `yfinance` reads public Yahoo data without an official API; it may break
   or be rate-limited, and is for personal/academic use. The CSV is versioned so the app never
   needs network access.
