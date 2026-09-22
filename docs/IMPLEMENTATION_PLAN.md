# DeFiStress Lab Implementation Plan

## Objective

Build a reproducible, professor-facing research application that models the Aave V3 liquidation to Uniswap V3 forced-selling feedback loop. Ethereum Mainnet access is read-only. Offline development and CI use an explicitly labelled deterministic fixture.

## Architecture

1. `backend/app/adapters` performs block-pinned JSON-RPC, Aave, and Uniswap reads. All real snapshots carry source versions, a block hash, and quality flags.
2. `backend/app/db` stores immutable snapshots, scenarios, run events, metrics, validation reports, and data-quality flags.
3. `sim` contains the API-independent decimal-safe health-factor, Aave liquidation approximation, Uniswap V3 square-root-price model, agents, cascade scheduler, metrics, threshold search, and Monte Carlo runner.
4. `backend/app/api.py` exposes the versioned REST contract and export endpoint. Deterministic jobs run inline; Monte Carlo jobs can be dispatched to Celery/Redis.
5. `frontend` is a Next.js research dashboard with overview, positions, liquidity, scenario, simulator, results, compare, validation, and provenance routes.
6. `contracts/validation` is a local-only Foundry/Anvil harness. It never contains a Mainnet write path.

## Delivery phases and gates

| Phase | Output | Gate |
|---|---|---|
| A Audit | Spec extraction, environment audit, requirement map | FR-01 to FR-16 traced |
| B Repository | Monorepo, Python/Node config, database, Docker, CI | Local lint/test commands exist |
| C Data spike | Read-only RPC, Aave address-book resolver, Uniswap factory/pool reads | Real smoke test when `ETH_RPC_URL` exists |
| D Snapshot | Fixture and real snapshot orchestration, provenance, coverage | Immutable snapshot schema |
| E Simulation | HF, liquidation agents, V3 price feedback, arbitrage, waves, metrics | Golden Wave 1 to Wave 2 fixture |
| F API | REST endpoints, persistence, export | OpenAPI and API tests pass |
| G Frontend | All required routes and scenario-to-results flow | Production build passes |
| H Monte Carlo | Seeded paths and tail metrics | Same seed reproduces output |
| I Validation | Formula/property tests and local-fork harness | Direct tests pass; fork explicitly NOT RUN if unavailable |
| J Research | Experiments, threshold finder, manifests, documentation | Exported experiment is reproducible |
| K QA | Test, lint, build, Docker, fixture E2E, optional real smoke | Evidence recorded in `docs/STATUS.md` |

## Safety boundary

The application permits only read methods (`eth_call`, block reads, and log reads) against Mainnet. No private-key configuration, signer, transaction submission method, or Mainnet deployment script exists. Foundry transactions are scoped to a localhost fork.

