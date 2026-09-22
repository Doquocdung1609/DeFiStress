# Requirements Traceability

`PASS` means the available automated or browser evidence passed. `PASS (FIXTURE)` is not evidence about Mainnet. `IMPLEMENTED / SKIPPED` means the code path exists but its external prerequisite was absent.

| Requirement | Implementation | Test | Status |
|---|---|---|---|
| FR-01 Data Source Health | `backend/app/api.py`, `backend/app/adapters/rpc.py`, Overview source panel | `tests/test_api.py`, `tests/test_rpc_safety.py` | PASS (offline); live RPC SKIPPED |
| FR-02 Create Snapshot | `backend/app/services/real_snapshot.py`, `backend/app/db/repository.py` | fixture/cached lifecycle in `tests/test_api.py` | PASS (FIXTURE/CACHED); real smoke SKIPPED |
| FR-03 Aave Market Snapshot | `backend/app/adapters/aave/*` | `tests/test_aave_values.py`, `tests/test_aave_adapter.py` | PASS unit; live integration SKIPPED |
| FR-04 Borrower Universe | `backend/app/adapters/aave/events.py`, `positions.py`, coverage UI | event/coverage assertions and fixture API integration | IMPLEMENTED; live discovery SKIPPED |
| FR-05 DEX Liquidity Snapshot | `backend/app/adapters/uniswap/*`, `sim/dex/uniswap_v3.py` | `tests/test_uniswap_adapter.py`, `sim/tests/test_uniswap_v3.py`, property tests | PASS model/adapter unit; real Quoter SKIPPED |
| FR-06 Stablecoin Monitor | snapshot schema, market endpoint, Overview card | fixture API lifecycle | PASS (FIXTURE) |
| FR-07 Scenario Builder | `sim/presets.py`, scenario API, frontend builder | preset/API and validation tests | PASS |
| FR-08 Deterministic Stress Run | `sim/engine/run.py` | golden/cascade/reproducibility tests | PASS |
| FR-09 ABM Liquidation Engine | `sim/agents/liquidator.py`, `sim/lending/liquidation.py` | agent, liquidation, capacity, invariant tests | PASS |
| FR-10 Arbitrage Stabilizer | `sim/agents/arbitrageur.py` | `sim/tests/test_agents.py`, cascade golden test | PASS |
| FR-11 Monte Carlo | `sim/monte_carlo/runner.py`, Celery worker, MC results UI | seed and API lifecycle tests | PASS |
| FR-12 Scenario Compare | compare API and frontend route | same-snapshot comparison integration | PASS |
| FR-13 Historical Replay | explicit pinned block/archive path, `CACHED_MAINNET` | cached-mode integration; block-tag safety test | IMPLEMENTED; archive RPC SKIPPED |
| FR-14 Fork Validation | `contracts/validation`, validation API/UI | environment prerequisite check | HARNESS IMPLEMENTED; NOT RUN |
| FR-15 Export Experiment | `backend/app/services/export.py` | ZIP content integration test | PASS |
| FR-16 Data Provenance View | provenance API and frontend route | API integration and browser walkthrough | PASS (FIXTURE) |

The broader NFR, model, UI, data-source, testing, and Definition-of-Done mappings are documented in `docs/IMPLEMENTATION_PLAN.md`, `docs/ARCHITECTURE.md`, `docs/MODEL_ASSUMPTIONS.md`, and `docs/VALIDATION.md`.
