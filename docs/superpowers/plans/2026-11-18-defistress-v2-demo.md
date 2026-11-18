# DeFiStress V2 Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The user requested one agent and autonomous execution.

**Goal:** Run a complete academic product demo using real Aave and Terra computations, persistence, exports and a browser walkthrough.

**Architecture:** Compose the four reviewed candidate PR trees on a dedicated preview branch. Extend FastAPI with narrow synthetic-warning and illustrative-exit adapters backed by existing SQLAlchemy persistence; extend existing Next.js navigation and Terra UI. Use the existing Aave and Terra V1 engines for their current functions.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, SQLAlchemy, Next.js 16, React 19, TypeScript, pnpm, SQLite for default demo, optional Docker Compose PostgreSQL/Redis/Celery.

**Spec:** `docs/superpowers/specs/2026-11-18-defistress-v2-demo-design.md`

## Global Constraints

- Single agent, zero paid infrastructure; formal PRs remain Draft until separate governance checks.
- V2 synthetic warning accepts synthetic origin only; existing 14 historical fields remain blocked.
- No frozen V1 scientific source or artifact modifications.
- Frontend code follows installed Next.js 16 docs under `node_modules/next/dist/docs/`.
- Every new run records origin, mode, assumptions, source, status and reproducible result.

## Review Focus

- Missing UST/LUNA input must yield ABSTAIN and not a safe score.
- Future synthetic publication beyond the cutoff cannot enter a past warning.
- Nonfinite or negative exit inputs must produce validation errors; unknown capacity must not be treated as infinite executable liquidity.
- Missing historical chart cells must be visible gaps, not zero or removed time.
- Failed/pending runs must not appear as completed or export as successful results.

## Files and tasks

### Task 1: Compose candidate source and verify isolation

**Files:** Existing PR paths only; new `docs/demo/CANDIDATE_SOURCES.json`.

- [ ] Record current integration and PR SHAs, CI/review status.
- [ ] Copy exact PR #57, #55, #58, #53 changed paths into `demo/e2e-preview` in dependency order; commit each source set separately.
- [ ] Verify SHA of every copied file and preservation of all other accepted integration blobs.
- [ ] Run targeted valuation, warning, PIT and existing API tests. Record Windows symlink limitation separately from Linux outcome.

### Task 2: Make the local stack reproducible

**Files:** `scripts/start_demo.ps1`, `scripts/stop_demo.ps1`, `scripts/start_demo.sh`, `backend/Dockerfile`, `docker-compose.yml`, `docs/demo/README.md`.

- [ ] Write a smoke that checks local startup with fixture-only settings and detects wrong port owners.
- [ ] Implement one-command startup: check Python/pnpm, initialize SQLite schema/fixture, start API/Next, poll health/routes, print URL and recovery instructions. Keep generated state outside research evidence.
- [ ] Repair Docker image so packaged V2 and preserved Terra data are available; verify Compose config and local runtime when Docker is available.
- [ ] Verify shutdown preserves data and research artifacts.

### Task 3: Synthetic B0–B3 API and persisted results

**Files:** `backend/app/services/demo_warning.py`, `backend/app/schemas.py`, `backend/app/terra_api.py`, `backend/app/db/repository.py`, `tests/test_demo_warning_api.py`.

- [ ] Write failing API tests for NORMAL/WATCH/HIGH/ABSTAIN, cutoff guard, persistence/readback/export and invalid inputs.
- [ ] Build exact typed synthetic observations from bounded decimal strings at an explicit UTC cutoff; call the unchanged P04-03-S `evaluate` for all four models.
- [ ] Persist and retrieve a complete run through `terra_experiments`; expose history/export.
- [ ] Run focused tests and strict type/lint checks.

### Task 4: Illustrative exit calculator API and persisted results

**Files:** `backend/app/services/demo_exit.py`, `backend/app/schemas.py`, `backend/app/terra_api.py`, `backend/app/db/repository.py`, `tests/test_demo_exit_api.py`.

- [ ] Write failing tests for finite arithmetic, capacity-limited fills, unknown capacity, latency, fee/slippage and validation errors.
- [ ] Implement exact decimal proceeds calculations labeled ILLUSTRATIVE, with explicit NOT_VERIFIABLE when execution capacity is unknown.
- [ ] Persist/retrieve/export with the same demo history mechanism and verify readback.

### Task 5: Connect Next.js UI and preserve historical gaps

**Files:** `frontend/app/page.tsx`, `frontend/app/components/terra/TerraDashboard.tsx`, `frontend/app/components/terra/TerraCharts.tsx`, new focused warning/exit components, `frontend/lib/api.ts`, `frontend/app/terra/[section]/page.tsx`, `frontend/app/globals.css`, frontend tests.

- [ ] Write failing pure UI-data tests for missing historical cells and response mapping.
- [ ] Add landing links and Terra warning/exit sections with real API calls, loading/success/error/empty states and source labels.
- [ ] Add date/zoom controls and preserve nulls as chart gaps. Keep retrospective V1 warning separate from synthetic B0–B3.
- [ ] Link saved result history/export; maintain responsive layout and keyboard labels.
- [ ] Run frontend tests/lint/build.

### Task 6: Real application and browser acceptance

**Files:** `tests/test_demo_e2e.py`, `docs/demo/DEFISTRESS_V2_END_TO_END_COMPLETION.md`, `docs/demo/DEFISTRESS_V2_DEMO_RUNBOOK_VI.md`, evidence files under `docs/demo/evidence/` if portable.

- [ ] Start the actual stack from the documented command and run API smoke for all nine scenarios.
- [ ] Use browser automation to navigate, change inputs, execute and reload results; save actual screenshots or video if supported.
- [ ] Run Python regressions, Ruff, strict mypy, frontend tests/lint/build, export/readback and source-preservation checks.
- [ ] Record actual outputs, exact source SHAs, failures and blockers. Claim PRODUCT_DEMO_COMPLETE only if all user-defined requirements are observed.
- [ ] Open a focused demo PR when local QA is complete; keep formal integration governance separate.
