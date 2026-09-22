# DeFiStress Lab

DeFiStress Lab is a reproducible research dashboard for the Aave V3 to Uniswap V3 liquidation feedback loop on Ethereum. It combines immutable block-pinned snapshots, an agent-based liquidation model, Uniswap V3 square-root-price liquidity math, deterministic and Monte Carlo experiments, traceable metrics, and local-fork validation hooks.

The Mainnet integration is strictly read-only. The project has no signer, private-key setting, `eth_sendTransaction`, or `eth_sendRawTransaction` path.

## 1 Project overview

The system asks what happens after an ETH shock: which Aave positions cross Health Factor 1, how liquidators respond to profit and capacity limits, how seized WETH execution moves a Uniswap V3 pool, whether the endogenous price move creates further liquidation waves, and how bad debt and cascade probability change under liquidity, gas, and arbitrage assumptions.

## 2 Architecture

- `sim`: API-independent quantitative engine using `Decimal` for monetary/accounting values.
- `backend`: FastAPI, SQLAlchemy storage, block-pinned adapters, Celery worker, export and validation status.
- `frontend`: Next.js and Recharts research dashboard.
- `contracts/validation`: local-only Foundry/Anvil harness.
- `data`: explicitly labelled fixture and generated experiment artifacts.
- `docs`: assumptions, validation, status, demo procedure, and requirement traceability.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 3 Research question

For an ETH price shock, estimate direct liquidations, forced WETH selling, DEX price impact, endogenous liquidation waves, unliquidated debt, bad debt, recovery, and Monte Carlo tail risk under alternative market and agent capacities.

## 4 Safety

`REAL_MAINNET` calls only block reads, `eth_call`, and `eth_getLogs`. Never add a private key or seed phrase. Fork transactions belong on `127.0.0.1` Anvil only. The UI always displays `Research Simulation — Mainnet Read-Only` and a `FIXTURE` snapshot is never called Mainnet data.

## 5 Requirements

- Python 3.12+
- Node.js 20+ and pnpm
- PostgreSQL and Redis for the full Docker topology; SQLite and local background jobs work for development
- Optional Mainnet RPC for real snapshots
- Optional archive RPC plus Foundry/Anvil for local-fork validation

## 6 Quick start fixture mode

PowerShell:

```powershell
.\scripts\bootstrap.ps1
.\scripts\dev.ps1
```

Bash:

```bash
./scripts/bootstrap.sh
./scripts/dev.sh
```

Open `http://localhost:3000/overview`; the API and Swagger run at `http://localhost:8000` and `http://localhost:8000/docs`. Run a non-browser smoke demo with:

```powershell
.\.venv\Scripts\python.exe scripts\run_demo.py
```

## 7 Real Mainnet mode

Set `APP_MODE=REAL_MAINNET` and `ETH_RPC_URL`, start the API, then request:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/snapshots -ContentType application/json -Body '{"mode":"REAL_MAINNET"}'
```

The service selects one finalized block first. Every Aave and Uniswap contract read uses that block number. Borrower discovery scans a configurable recent log range with adaptive chunks; use `candidate_users` for a controlled research cohort. The Uniswap adapter scans initialized `tickBitmap` words directly at that same block and selects the fee tier with the largest modeled ±2% executable depth.

## 8 RPC configuration

Copy `.env.example` to `.env`. `ETH_RPC_URL` is sufficient for a current finalized snapshot. `ETH_ARCHIVE_RPC_URL` is required for historical blocks and Anvil validation. `GRAPH_API_KEY` enables indexed history/tick work; its absence must not be hidden.

## 9 Database

SQLite is the default:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

Set a PostgreSQL SQLAlchemy URL for the full stack. Snapshots, locked scenarios, and completed runs are immutable; re-running creates a new run.

## 10 Docker

```bash
docker compose up --build
```

Services are `postgres`, `redis`, `backend`, `worker`, and `frontend`, each with a health check where supported. Docker Desktop must be running.

## 11 Create snapshot

Fixture:

```bash
curl -X POST http://localhost:8000/api/v1/snapshots -H "Content-Type: application/json" -d '{"mode":"FIXTURE"}'
```

Real snapshot:

```bash
python scripts/create_real_snapshot.py
```

## 12 Run stress simulation

Create a scenario using `POST /api/v1/scenarios`, then call `POST /api/v1/runs`. The professor preset is ETH −20%, liquidity haircut 40%, gas 2×, arbitrage capacity 50%, seed `20260914`. A scientific no-cascade result is returned as-is; the threshold endpoint can search for the first shock producing depth at least two.

## 13 Monte Carlo

Use run mode `MONTE_CARLO`. With `ASYNC_BACKEND=local`, FastAPI schedules a local background task for development. With `ASYNC_BACKEND=CELERY`, the Redis-backed worker executes it and `/runs/{id}` reports status and progress. The same snapshot, scenario, model version, and seed reproduce the same paths.

## 14 Fork validation

Set `ETH_ARCHIVE_RPC_URL`, install Foundry, and follow [contracts/validation/README.md](contracts/validation/README.md). The API reports `NOT_RUN_MISSING_ARCHIVE_RPC`, `NOT_RUN_MISSING_FOUNDRY`, `UNAVAILABLE`, or `READY_LOCAL_ONLY`; it never fabricates `PASS`.

## 15 Export results

`GET /api/v1/runs/{id}/export` returns a ZIP with manifest, snapshot summary, scenario, metrics, event/position/timeseries CSVs, validation status, README, and four generated charts.

## 16 Testing

```powershell
.\scripts\test.ps1
```

The suite covers decimals, HF, Aave close-factor approximation, V3 swap behavior, cascade waves, invariants, seeded Monte Carlo, API lifecycle, export, and the read-only RPC allowlist. Real RPC and fork checks skip when credentials/tooling are absent.

Run the deterministic 1,000/5,000-position benchmark with:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_simulation.py
```

## 17 Known limitations

- A real snapshot whose direct initialized-tick reads fail is valid for direct state analysis but receives `TICK_DATA_INCOMPLETE`; trades beyond the configured bitmap window require a Quoter/fork cross-check.
- The ABM models WETH-to-USDC liquidation while retaining other portfolio value in aggregate. `HF_MISMATCH` records approximation error against `getUserAccountData`.
- Aave V3.7 dust, protocol-fee, e-mode, isolation, and rounding behavior is approximated off-chain and must be measured against a local fork for publication claims.
- No RPC credentials, archive RPC, Foundry, or running Docker daemon are bundled.

## 18 Research methodology

Separate exogenous shock from endogenous price feedback. Direct liquidation is eligibility immediately after the shock; cascade liquidation is eligibility created only after forced-sale DEX feedback. Events preserve each liquidation decision and execution. Monte Carlo changes price, liquidity, and gas inputs but uses the identical deterministic core.

## 19 Data sources

P0 sources are Ethereum JSON-RPC, the Aave DAO Address Book/Aave V3 contracts, and Uniswap V3 contracts. Official subgraphs/SDKs are P1 acceleration and cross-check sources. DefiLlama/CoinGecko are P2 external references only and never substitute for the Aave oracle.

## 20 Demo script

The exact 5–7 minute flow is in [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md). Before presenting real data, capture and cache the snapshot so the live run does not depend entirely on internet connectivity.
