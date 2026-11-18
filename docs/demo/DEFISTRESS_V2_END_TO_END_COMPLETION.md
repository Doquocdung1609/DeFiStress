# DeFiStress V2: functional demo completion report

**Date:** 2026-11-18 (Asia/Bangkok)

**Scope:** Local, fixture-first academic product demo on `demo/e2e-preview`
**Scientific acceptance:** **No.** This preview neither merges the Draft PRs nor
admits the 14 historical Terra fields to V2. No P04-04 historical backtest was run.

**GitHub:** [Draft demo PR #59](https://github.com/Doquocdung1609/DeFiStress/pull/59)
compares `demo/e2e-preview` with the pinned candidate base
`demo/e2e-candidates` (`e4dc052127e83e26de088ab7c029037b422137c6`).
The tested application implementation commit is
`875d5feb295ded52eacec0d08eb1d53d9fe73642`.

## Functionality: existing → gap → delivered

| Area | Existing/reused | Gap handled in this preview | Observed result |
|---|---|---|---|
| Aave/Uniswap | Snapshot, presets, scenario engine, result graph, compare, export | Isolated startup and end-to-end QA | Browser executed Baseline, Severe and Low Liquidity; three saved result routes and screenshots. Fixture run via live API was `COMPLETE`, debt liquidated 172,944.16 USDC, 2 cascade waves. |
| Terra historical | Preserved 1,776 hourly observations, fit, V1 retrospective warning, stress | Date range/zoom and chart null gaps | Browser showed crisis-week plots; live API returned 1,776 rows and 1,776 warning timeline points. |
| V2 synthetic B0–B3 | PR #58 P04-03-S engine and source lineage | Bounded synthetic API, editor, persistence and export | Browser produced B0 NORMAL, B1 HIGH, B2 HIGH, B3 WATCH for 0.99/100/90; missing UST produced ABSTAIN. A HIGH B3 scenario was also computed. |
| Exit | Proposed P04-05 blueprint only | Separate illustrative calculator and stored results | Capacity unknown gave NOT_VERIFIABLE; capacity 600/1,000 UST gave 600 filled, 400 unfilled, 465.6 USD net and 134.4 USD modeled loss. |
| Startup | General bootstrap/dev scripts, Compose | Fixture-safe 8100/3100 start/stop with health checks and logs; image includes V2 and Terra data | Windows local script started API and Next; `scripts/demo_smoke.py` passed all nine checks. Compose config parsed. |

## Source composition and governance

Base accepted integration commit:
`c51d4d06d8b560a149e32ade922f8ed62da1a589`.

| PR | Source HEAD | Exact copied paths | State on Nov 18 |
|---|---|---:|---|
| #57 CI compatibility | `724eaa106c83947996636dd89a68caebcb0702b8` | 3 | Draft, unmerged; GitHub workflow billing/runner issue persists. |
| #55 valuation | `3b70eee46055e64149b164af9fa8da759756acd1` | 8 | Draft, unmerged; two old CI failures, local targeted tests pass. |
| #58 synthetic warning | `ecddfc5c09da841c9929fde712ead3a4053150b4` | 44 | Draft, unmerged; no formal check run at observation time. |
| #53 historical clock/evidence | `96de4c8f4d3fd7bd3974eba3a50bde49fcd8dc5b` | 6 | Draft, unmerged; six successful and two skipped checks. |

Exact path and SHA inventory is in [CANDIDATE_SOURCES.json](CANDIDATE_SOURCES.json).
The 61 copied Git blobs were matched to their source HEADs. The preview adds
application adapters; no file under frozen `sim/terra`, existing research
evidence, or the four candidate file sets was edited by the demo layer.
The PRs remain subject to their own review and branch protection.

## Runtime evidence

Local HTTP smoke on 2026-11-18, after a stop/start cycle:

```text
1 health: healthy
2 Aave fixture snapshot: fixture-main-v1
3 Aave scenario and run: 751608b9-4cd1-4ad2-adbc-c1dfea86276b
4 Terra historical rows: 1776
5 Terra retrospective warning: timeline 1776
6 synthetic B0-B3: WATCH and ABSTAIN verified
7 Terra stress: 2 seeded runs
8 illustrative exit: 465.6 USD
9 persistence, history, ZIP export: verified
```

The browser walkthrough ran against the same local stack with Chrome headless
and saved 11 ordered screenshots in [evidence/browser](evidence/browser). Its
script is [browser_demo.mjs](../../frontend/scripts/browser_demo.mjs). It
clicked real buttons, changed parameters, waited for computed outputs, reopened
the saved exit result and verified a browser ZIP download. No video was
recorded; the screenshots and repeatable walkthrough are the available evidence.
The [example exit JSON](evidence/example-exit-result.json) and
[ZIP](evidence/example-exit.zip) came from the live API.

## Quality gates

| Gate | Result |
|---|---|
| Focused warning, exit, valuation, warning regressions and existing Aave/Terra APIs | 205/205 passed on Windows; [JUnit evidence](evidence/demo-tests.xml). |
| Frontend Vitest | 22/22 passed. |
| Frontend ESLint and Next.js production build | Passed; Next.js 16.3.5. |
| Ruff on changed Python | Passed. |
| Strict mypy on new warning/exit services with imported modules silent | Passed. The configured whole-project run exposed 21 existing errors in DB model typing, Terra adapters and pandas stubs; an explicit backend check exposed 28 including existing Terra API/schema typing. These remain an outstanding quality gate. |
| Docker Compose syntax | `docker compose config --quiet` passed. Container runtime not tested: Docker Desktop daemon was stopped. |
| Windows browser | 11 actual screenshots and ZIP download; repeatable script passed. |
| Fresh Python 3.12 virtual environment | `pip install -e .` succeeded; an independent TestClient returned health 200, warning 201/WATCH and exit 201/CAPACITY_ASSUMED_PARTIAL. |

The existing Windows PIT symlink regression depends on Windows Developer Mode
or elevated symlink privileges; this is a host limitation. The PR #58 Linux
evidence remains the relevant scientific regression artifact. The preview did
not reinterpret that evidence as an approved historical validation.

## Feature and blocked-item matrix

| Requirement | Status | Boundary or follow-up |
|---|---|---|
| Local fixture startup, API, frontend, SQLite persistence | Working and exercised | Windows script uses Python 3.12/pnpm; a fresh install was independently exercised. |
| Aave/Uniswap fixture simulation and comparison/export | Working; simulation exercised in browser and API | Comparison and export are existing services. No live Mainnet transaction. |
| Terra historical timeline and V1 retrospective warning | Working; browser and API exercised | Coverage and carried prices displayed; historical V2 admission remains blocked. |
| Terra synthetic B0–B3 | Working; browser and API exercised | Synthetic origin only. No historical forecast claim. |
| Terra counterfactual stress | Working; browser and API exercised | User assumptions, collapse count not probability. |
| Exit planner, saved run, ZIP | Working; browser and API exercised | Assumed capacity only; unknown depth remains NOT_VERIFIABLE. |
| Celery/PostgreSQL Compose mode | Configuration validated, runtime unverified | Docker daemon unavailable on the test host. Local deterministic path uses no worker. |
| POSIX start/stop script | Supplied, not runtime-tested | The test host was Windows; validate on Linux/macOS before relying on this path. |
| Whole-project strict mypy | Existing failures remain | 21 errors in old typing/stubs; explicit backend check reported 28. New services pass focused check. |
| Formal PR integration/CI | Blocked by Draft review/checks/billing | Keep #53/#55/#57/#58 separate. Preview is not the governed merge. |
| Historical V2/P04-04/P04-05 empirical proof | Not authorized | No promotion of 14 fields, no investor-exit effectiveness claim. |

## Reproduction

Follow [the Vietnamese runbook](DEFISTRESS_V2_DEMO_RUNBOOK_VI.md), then run:

```powershell
.\scripts\start_demo.ps1
.venv\Scripts\python.exe scripts\demo_smoke.py
cd frontend
node scripts\browser_demo.mjs
```

Stop with `.\scripts\stop_demo.ps1`. Database/logs are in ignored
`data/runs/`; the source dataset and research artifacts are not reset or
deleted. The local fixture product path is functional. Scientific and formal
integration gates remain pending as stated above.
