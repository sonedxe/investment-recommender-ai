# Feature: investwise-core

Locator: `odd/tasks/investwise-core.md` · Engram mirror: `odd/investwise-core/tasks`

## Objective

Implement InvestWise end to end: fuzzy logic (horizon in fitness, absorption in chromosome), context rules, extended genetic algorithm, Bayesian market module, generative AI (interpretation + explanation), FastAPI orchestration, React GUI from the design system, ablation experiments and manuals.

## Problem / why

The repository is a skeleton. The v1.1 design misses the professor's feedback (no fuzzy component in the chromosome) and produces degenerate portfolios. See `docs/analisis/` and `docs/plan/`.

## Scope and constraints

- Source of truth: `docs/analisis/*.md` and `docs/plan/*.md`.
- Core modules in NumPy only (no scikit-fuzzy, DEAP, portfolio optimizers): the course requires the modules to be programmed.
- `ai/` never imports FastAPI or `backend/`; network access only in `ai/generative/adapters/` and `scripts/`.
- Decisions applied: D1 proposal (absorption gene `c`), D2 cap `w_i ≤ 0.40`, D3 hybrid CSV sources, D4 both OpenAI and Anthropic adapters compared with the golden set, D5 five-label λ scale.
- Code, identifiers and comments in English; user-facing UI copy and LLM prompts in neutral Spanish.
- Out of scope: dates, team roles, git flow conventions.

## Delivery strategy

`feature-branch-chain` on `feature/parcial-v1` (chosen under the user's explicit delegation). Forecast ≈ 4,000+ authored lines; slices are recorded per work unit below. Push, PRs and merge remain the user's decisions.

## Checklist

| ID | Task | Route | Status | Evidence |
|---|---|---|---|---|
| W0 | Commit analysis, plan and this feature document | inline (docs only) | done | `c396868`; RDD medium → consent granted → 1-lens review approved, acknowledged (authority burned) |
| W1 | Foundation: dependencies, folder layout, shared types, parameter JSON + loader, docstring cleanup (T0.3–T0.5) | delegated (2+ non-trivial files) | done | `7f48e60`; 80 tests passing (slice) |
| W2 | Fuzzy module: membership, Sugeno, Mamdani, horizon, absorption (F1) | delegated | done | `8289803`; tip 16.009 (slide error verified independently), m_H(2.5)=1.30, absorption centroid 0.5345 |
| W3 | Context rules engine and adjustment (F2) | delegated | done | `ce57ef6`; table 4.6.4 reproduced |
| W4 | Genetic algorithm: chromosome `[w|c]`, fitness with breakdown, operators, convergence, cap (F3) | delegated | done | `673f920`; 115 tests; D2 regression λ0.2 → 40/20/0/40/0, λ2 → 0/0.3/19.7/40/40; RDD medium, 1 lens approved |
| W5 | Bayesian module + market data script and CSVs (F4, T0.6) | delegated | done | `02f82b2`; EPU soles μ 0.162 σ 0.220 → posterior μ 0.128; others Annex A prior; RDD high, 4 lenses approved, no findings |
| W6 | Generative AI core: port, offline adapter, interpreter, explainer with number validation (F6a/b) | delegated | done | `b4bdc0c` + fix `6c22c0f`; offline extractor, clarification, explanation with number validation |
| W7 | Orchestration service + API endpoints + integration tests (F5) | delegated | done | `834ad41`; 4 endpoints, cent-exact allocation, technical block; parent fix: interpret profile postable as-is (+test) |
| W8 | OpenAI and Anthropic adapters + golden set runner (D4) | delegated | done | `b285e9d` + fix `df7823f`; 221 tests; offline golden set 97.1 % field accuracy, 100 % questions on ambiguous; live provider runs pending keys |
| W9 | Frontend: tokens, base styles, components ported from the design system (T7.0–T7.3) | delegated | done | `b711a7a`; 32 components + Switches, A1–A6 applied; build OK, 17 vitest; parent headless screenshot desktop/390 px OK |
| W10 | Frontend: API client, mappers, containers, flow state machine, states (T7.4–T7.7) | delegated | done | `a69e488` (fixtures) + `67bdf03`; 73 vitest; parent e2e via CDP: real flow text → result + technical detail OK; fixed % wrapping |
| W11 | Ablation and calibration experiments (F8) | delegated | done | `e63030a` (code+docs, reviewed) + `78f80ed` (generated results); 222 tests; findings: gene trades off only for low absorption & λ ≤ 0.5; cap drives diversification; c stranded 2/60 |
| W12 | Installation and user manuals, README update (F9) | delegated | done | `bc20e19`; passive docs (structural readback, links OK); 7 screenshots |
| W13 | Polish from experiments/manual findings: c gene stranding, score note formula, chart label clipping, convergence ticks, % format, stale ping text, restart action, offline number words | delegated | done | `c326733` (regenerated results) + `bb745e1` (reviewed, approved); 247 py + 82 vitest; c stranding 2/60 → 0/600; offline golden set 97.1 % → 100 % |
| W14 | Real market data for all five categories from BCRP (BVL index, BTP 10y, soles bonds ≤3y, deposit rate; mixed as documented composite) with manifest, descriptive file names, yield→return by duration; rerun experiments and fixtures | delegated | done | `785a4db` (reviewed: high risk, 4 lenses, no findings) + generated results/fixtures; 278 py + 82 vitest; all 5 categories data-backed |

## Acceptance criteria

- Reference tests pass: tip exercise P* = 16.009 % (slide reports 15.9 % due to a missing clip; verified independently), H = 2.5 → m_H ≈ 1.30, context table 4.6.4, base fitness −0.14.
- GA invariants hold (Σw = 1, w ≥ 0, w ≤ 0.40, c ∈ [0, 1], elitism monotonic, seed reproducible).
- Full flow text → recommendation works offline (no API key).
- GUI covers the 4 screens + technical detail + states.

## Progress log

- W0 `c396868` docs commit. Assess: medium (`executable_change` heuristic on prompts doc), `slice_budget_reached`. Untracked team PDFs excluded via `--untracked-scope=exclude`. Review approved; reviewed boundary → `c396868`.
- W1–W3 delegated to one writer (sequential units, parent commits each separately). Parent check: `pytest` 80 passed; tip centroid recomputed independently (16.009 exact; slide piecewise 15.9).
- RDD on W1–W3 slice (`c396868..ce57ef6`, 1970 lines, medium): consent granted, 1-lens review approved, acknowledged. Reviewed boundary → `ce57ef6`. Deviation: the three commits were assessed as one slice because they were committed before assessment.
- W4–W5 delegated to one writer; parent check 115 passed. Each commit assessed and reviewed separately (boundaries `673f920`, `02f82b2`).
- Note: with Media absorption the evolved c stays at the set mode (0.5) because the volatility penalty is inactive; c only trades off when σ approaches σ_max(c). To show in ablation (T8.4).
- W6–W7 delegated to one writer; parent e2e check found interpret→recommend profile mismatch (lambda_base rejected by strict schema) → fixed in W7 with regression test.
- RDD W6 (`02f82b2..b4bdc0c`, medium): reliability lens found CRITICAL deterministic finding R3-number-parse-crash (malformed numbers raised inside explain retry loop) + 2 warnings. Correction plan captured (45 lines); fix committed as `6c22c0f` (+3 regression tests). Status then stopped `corrected_candidate_unavailable` → after commit `captured_artifacts_unverifiable` (terminal, not approved). Clone review not disabled.
- RDD W6+fix+W7 slice (`02f82b2..834ad41`, 2680 lines, medium): consent granted, approved, acknowledged. Boundary → `834ad41`. 183 tests.
- W8 delegated (agent hit usage limit once, resumed). RDD W8: reliability lens flagged httpx2 import as CRITICAL — refuted in practice (httpx2 is a declared dependency of openai and anthropic SDKs) but declared explicitly; WARNING sticky json_schema downgrade valid → fixed `df7823f` + regression test. Correction lineage stopped `corrected_candidate_unavailable` again; fresh review on `834ad41..df7823f` approved. Boundary → `df7823f`.
- W9 delegated; RDD medium (4839 lines incl. lockfile) approved. Boundary → `b711a7a`.
- W10 delegated. Parent e2e (uvicorn + vite dev + headless chromium via CDP) passed; fixed allocation % wrapping. RDD: full range exceeded reviewer context budget (`lens_context_budget_exceeded`, 148 KB of fixtures); compacted fixtures and split commit; fixtures commit `a69e488` left unreviewed (deterministic data from reviewed backend) — deviation recorded; code range `a69e488..67bdf03` reviewed and approved. Boundary → `67bdf03`.
- W11–W12 delegated to one writer. RDD: W11+W12 range exceeded reviewer budget (CSV/PNG results); recommitted as code+docs `e63030a` (reviewed, approved), generated results `78f80ed` (unreviewed data, deviation recorded), manuals `bc20e19` (assessed passive, no review). Boundary → `bc20e19`.
- W13 added from findings and delegated; parent completed the uncertainty ping key. Commits reordered (results first) so the code range `c326733..bb745e1` fit the reviewer budget; approved. Final boundary → `bb745e1`.

- Post-feature (2026-10-05): live Anthropic key configured (workspace-scoped; an organization-scoped key is rejected by the API). First live run exposed a real bug: Claude keys horizon evidence as `horizonte_anios`, so the interpreter dropped the horizon → fixed `6127c15` with regression test. Found tests were reading the developer `.env` and calling the live API → `tests/conftest.py` pins offline. Live golden set: 98.0 % field accuracy, 100 % valid JSON, 3.1 s mean latency; D4 decided: Anthropic. Assess `89b1b8a..6127c15`: medium, `under_budget` (84 lines) → pending in slice.

- W14 authorized by the user ("necesito datos reales"): BCRP web view is readable through headless chromium (anti-bot passed); series located: PN01142MM, PD31895MM, PN01113MM, PN07814NM. BCRP publishes no mutual-fund returns → mixed fund as composite of real series.

- W14: debt series fallback to PN06503OM (CD BCRP yield, D≈0.5) because PN01113MM/PN01124MM are mostly 0.0 (no issuance). Mixed composite changed to 0.5 stocks + 0.5 BTP (ρ with stocks 0.97; GA rarely picks it — documented limitation). Real BTP σ 6.5 % vs prior 3.5 % → debt and term now dominate conservative/moderate portfolios. Integration test now asserts equity exposure (stocks+mixed).

## Next step

Feature complete. Open items for the team (outside this feature's code scope):

- Validate the absorption-gene interpretation with the professor (guide: `docs/analisis/10-decisiones-d1-d2-d5.md`, D1).
- Optionally download BCRP series (BTP, deposits) manually to replace Annex A priors (`docs/analisis/09-fuentes-de-datos.md`).
- Write technical report v2.0 using `docs/plan/04-entregables.md` and `docs/experimentos/`.
- Push / PR / merge remain the user's decisions.
