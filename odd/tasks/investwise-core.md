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
| W0 | Commit analysis, plan and this feature document | inline (docs only) | pending | |
| W1 | Foundation: dependencies, folder layout, shared types, parameter JSON + loader, docstring cleanup (T0.3–T0.5) | delegated (2+ non-trivial files) | pending | |
| W2 | Fuzzy module: membership, Sugeno, Mamdani, horizon, absorption (F1) | delegated | pending | |
| W3 | Context rules engine and adjustment (F2) | delegated | pending | |
| W4 | Genetic algorithm: chromosome `[w|c]`, fitness with breakdown, operators, convergence, cap (F3) | delegated | pending | |
| W5 | Bayesian module + market data script and CSVs (F4, T0.6) | delegated | pending | |
| W6 | Generative AI core: port, offline adapter, interpreter, explainer with number validation (F6a/b) | delegated | pending | |
| W7 | Orchestration service + API endpoints + integration tests (F5) | delegated | pending | |
| W8 | OpenAI and Anthropic adapters + golden set runner (D4) | delegated | pending | |
| W9 | Frontend: tokens, base styles, components ported from the design system (T7.0–T7.3) | delegated | pending | |
| W10 | Frontend: API client, mappers, containers, flow state machine, states (T7.4–T7.7) | delegated | pending | |
| W11 | Ablation and calibration experiments (F8) | delegated | pending | |
| W12 | Installation and user manuals, README update (F9) | delegated | pending | |

## Acceptance criteria

- Reference tests pass: tip exercise P* ≈ 15.9 %, H = 2.5 → m_H ≈ 1.30, context table 4.6.4, base fitness −0.14.
- GA invariants hold (Σw = 1, w ≥ 0, w ≤ 0.40, c ∈ [0, 1], elitism monotonic, seed reproducible).
- Full flow text → recommendation works offline (no API key).
- GUI covers the 4 screens + technical detail + states.

## Progress log

_(updated after each task with commit id, checks and review outcome)_

## Next step

W0.
