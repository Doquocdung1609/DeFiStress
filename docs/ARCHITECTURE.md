# DeFiStress Lab Architecture

## Runtime flow

`Ethereum RPC and official registries -> immutable snapshot -> scenario -> simulation core -> event and metric store -> API -> dashboard and export`

The snapshot is the consistency boundary. A real snapshot chooses one finalized or explicit block before contract calls begin and passes that same block identifier to every state read. The simulation never calls an external service, which makes runs deterministic and repeatable.

## Trust boundaries

- P0: Ethereum JSON-RPC, Aave V3 contracts and address book, Uniswap V3 contracts.
- P1: official subgraphs or SDKs for discovery, ticks, history, and cross-checking.
- P2: DefiLlama and CoinGecko only for external reference/calibration.
- A secondary source never replaces an Aave liquidation oracle value.

## Runtime modes

- `FIXTURE`: deterministic synthetic positions and V3 liquidity state, clearly labelled, used by CI and offline demos.
- `REAL_MAINNET`: requires `ETH_RPC_URL`; block and direct contract reads are Mainnet data and are cached immutably.
- `CACHED_MAINNET`: reloads an immutable real snapshot with its original block, capture time, and provenance.

## Persistence and jobs

SQLite is the local fallback; PostgreSQL is selected by `DATABASE_URL`. Celery and Redis execute larger Monte Carlo batches. The HTTP API can run a small deterministic simulation synchronously for a reliable classroom demo.

