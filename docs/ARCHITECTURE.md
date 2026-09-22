# DeFiStress Lab V2 Architecture

The product keeps the original Aave V3 + Uniswap V3 stress laboratory and adds
an isolated Terra/UST historical-research path. The two cases share persistence,
API conventions, experiment exports, and the dashboard shell, but not their
domain models.

## Runtime flow

`Ethereum RPC and official registries -> immutable snapshot -> scenario -> simulation core -> event and metric store -> API -> dashboard and export`

`Terra source files -> validated immutable research dataset -> pre-cutoff calibration view -> model run -> sealed ground-truth view -> metrics/export`

The snapshot is the consistency boundary. A real snapshot chooses one finalized or explicit block before contract calls begin and passes that same block identifier to every state read. The simulation never calls an external service, which makes runs deterministic and repeatable.

For Terra, `2022-05-06T00:00:00Z` is the anti-leakage boundary. The model receives
only a `CalibrationDatasetView`; `GroundTruthState` is loaded only after model
execution. Dataset manifests carry status (`REAL`, `FIXTURE`, `UNAVAILABLE`),
source URLs, retrieval times, hashes, license notes, and quality reports.

## Trust boundaries

- P0: Ethereum JSON-RPC, Aave V3 contracts and address book, Uniswap V3 contracts.
- P1: official subgraphs or SDKs for discovery, ticks, history, and cross-checking.
- P2: DefiLlama and CoinGecko only for external reference/calibration.
- A secondary source never replaces an Aave liquidation oracle value.

## Runtime modes

- `FIXTURE`: deterministic synthetic positions and V3 liquidity state, clearly labelled, used by CI and offline demos.
- `REAL_MAINNET`: requires `ETH_RPC_URL`; block and direct contract reads are Mainnet data and are cached immutably.
- `CACHED_MAINNET`: reloads an immutable real snapshot with its original block, capture time, and provenance.
- `TERRA FIXTURE`: deterministic synthetic observations used for offline tests;
  never represented as historical evidence.
- `TERRA REAL`: imported historical CSV/JSON/Parquet that passes schema, timestamp,
  hash, provenance, and cutoff validation.
- `UNAVAILABLE`: an honest source state when no authenticated/reproducible provider
  has been configured; it cannot silently fall back to generated historical data.

## Persistence and jobs

SQLite is the local fallback; PostgreSQL is selected by `DATABASE_URL`. Celery and Redis execute larger Monte Carlo batches. The HTTP API can run a small deterministic simulation synchronously for a reliable classroom demo.
