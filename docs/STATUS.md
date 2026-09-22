# Project Status

Last verified locally: 2026-09-15. A checked item means its offline/fixture implementation and automated checks pass. Environment-dependent Mainnet and fork evidence is tracked separately and is never inferred from fixture results.

- [x] FR-01 Data Source Health — API/UI and read-only RPC health implemented; live RPC check skipped.
- [x] FR-02 Create Snapshot — fixture, real, and explicit cached-Mainnet modes implemented; fixture/cached tests pass.
- [x] FR-03 Aave Market Snapshot — address-book resolution, pinned reserve/account calls, normalization, caps/rates/totals implemented; live read skipped.
- [x] FR-04 Borrower Universe — adaptive event discovery, Top-N coverage, failed-read accounting, and pseudonyms implemented; live discovery skipped.
- [x] FR-05 DEX Liquidity Snapshot — all fee tiers, direct pinned bitmap ticks, transparent ±2% depth selection, and V3 tests implemented; Quoter comparison skipped.
- [x] FR-06 Stablecoin Monitor — separate Aave/DEX/reference price channels and USDC depeg basis points implemented.
- [x] FR-07 Scenario Builder — immutable scenarios, eight presets, policy overrides, capacities, delays, and horizon controls implemented.
- [x] FR-08 Deterministic Stress Run — reproducible fixture run and golden Wave 1 → Wave 2 regression pass.
- [x] FR-09 ABM Liquidation Engine — profitability, priority, gas, funding, risk, delay, per-step capacity, and total capital implemented.
- [x] FR-10 Arbitrage Stabilizer — OFF/0/25/50/100 behavior and unit test implemented.
- [x] FR-11 Monte Carlo — seeded engine, progress updates, P(cascade), ES95, histogram, and CDF implemented.
- [x] FR-12 Scenario Compare — same-snapshot 2–4 run comparison and delta API/UI implemented.
- [x] FR-13 Historical Replay — explicit block-pinned archive-RPC path and cached immutable snapshot implemented; archive read skipped.
- [ ] FR-14 Fork Validation — local-only account/eligibility/liquidation/Quoter/swap harness implemented, but not run.
- [x] FR-15 Export Experiment — reproducible ZIP with manifests, CSVs, validation status, and four charts passes integration test.
- [x] FR-16 Data Provenance View — block/source/formula/quality evidence API and UI implemented.

## Verification evidence

| Check | Status | Evidence |
|---|---|---|
| Python backend/simulation tests | PASS | 36 tests |
| Ruff | PASS | backend, simulation, tests, scripts |
| mypy | PASS | 19 simulation source files |
| Vitest | PASS | 2 tests |
| ESLint | PASS | frontend source |
| Next.js production build | PASS | Next.js 16.3.5, TypeScript strict build |
| Alembic migration | PASS | SQLite upgraded to head |
| Fixture API/UI E2E | PASS | Scenario → Run → Results, two waves, browser console clean |
| Docker Compose configuration | PASS | five-service topology resolves |
| Deterministic performance | PASS | 1,000 positions 0.0616s; 5,000 positions 0.2297s on this machine |

## Environment-dependent checks

| Check | Current status | Reason |
|---|---|---|
| Real Mainnet snapshot smoke | SKIPPED | `ETH_RPC_URL` not configured |
| Historical/archive read | SKIPPED | `ETH_ARCHIVE_RPC_URL` not configured |
| QuoterV2 / executable local-fork comparison | NOT RUN | Archive RPC and Foundry/Anvil unavailable |
| Foundry harness compile/run | NOT RUN | `forge` and `anvil` unavailable |
| Docker image build / `compose up` | NOT RUN | Docker Desktop engine unavailable; Compose config itself passes |

## Definition-of-Done assessment

The offline fixture product, simulation, API, frontend, experiments, export, and documentation are complete and demonstrable. The project must not yet be called **real-Mainnet demo-ready** under the specification’s strict definition: items 1–4 (captured Mainnet snapshot/cohort/HF/pool evidence) and item 15 (Docker image build) remain unverified in this environment.
