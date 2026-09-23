# DeFiStress Lab

DeFiStress Lab is a reproducible DeFi systemic-risk research platform with two deliberately separate case studies:

1. **TerraUSD/LUNA, May 2022** — cutoff-safe historical replay, historical validation, competing-model benchmark, ablation, and counterfactual experiments.
2. **Aave V3 + Uniswap V3** — contemporary Ethereum liquidation and liquidity-feedback stress testing.

Historical validation improves confidence in the research workflow; it does not transfer universal validity from Terra to Aave. A replay is never labelled a prediction.

## Research design

The default Terra experiment freezes calibration at `2022-05-06 23:59:59 UTC` and evaluates `2022-05-07 00:00` through `2022-05-13 23:59 UTC`. Model code receives a `CalibrationDatasetView`, a cutoff state, evaluation timestamps, frozen parameters, and a seed. It cannot receive `GroundTruthState`; the validator loads ground truth only after simulation completes.

Every replay records calibration/evaluation windows, cutoff, dataset/model versions, git commit, seed, scenario parameters, source manifest, and leakage-check status. Modes are `IN_SAMPLE_REPLAY`, `OUT_OF_SAMPLE_REPLAY`, and `COUNTERFACTUAL_STRESS`.

## Data integrity and provenance

Terra Classic is the primary historical chain. Ethereum Curve/bridge data is secondary contagion evidence, and market-provider data is an external cross-check. P2 data never silently replaces missing canonical chain data.

No historical endpoint or credential is bundled. Therefore the repository ships only `terra_fixture_v1`, a deterministic synthetic fixture visibly labelled `FIXTURE`. Historical-source health is now dynamic: a source is `UNAVAILABLE` only when neither a provider nor historical evidence is configured, `CONFIGURED` when an endpoint is present but not yet ingested, and `REAL_HISTORICAL` / `PARTIAL` when a versioned dataset actually carries that evidence. CSV, JSON, and Parquet imports carry source, chain, block/time range, quality flags, dataset hash, transformation version, and git commit.

### Configure historical sources

Copy `.env.example` to `.env` and configure only the providers you actually have:

```env
TERRA_ARCHIVE_LCD_URL=
TERRA_HISTORY_DATA_URL=
ETH_ARCHIVE_RPC_URL=
CURVE_HISTORY_DATA_URL=
BRIDGE_FLOW_DATA_URL=
```

`TERRA_HISTORY_DATA_URL`, `CURVE_HISTORY_DATA_URL`, and `BRIDGE_FLOW_DATA_URL` are normalized historical providers. The source-specific fetch scripts now perform a real HTTP download instead of writing a permanent `UNAVAILABLE` stub. A successful download is labelled `DOWNLOADED_UNVERIFIED`; validate provenance/schema before importing it as `REAL_HISTORICAL`.

Example:

```powershell
.\.venv\Scripts\python.exe scripts\terra\fetch_terra_history.py --output data\raw\terra_history.json
.\.venv\Scripts\python.exe scripts\terra\validate_dataset.py --input data\raw\terra_history.json --dataset-version terra_ground_truth_v1
.\scripts\terra\import_dataset.ps1 --input data\raw\terra_history.json --dataset-version terra_ground_truth_v1 --status REAL_HISTORICAL --source-name "Verified Terra historical provider" --source-type INDEXED_ONCHAIN
```

The Terra CLI now defaults to the same `DATABASE_URL` as the running API, so a dataset imported from the command line is visible in the dashboard without writing to a second SQLite database.

See [Terra provenance](docs/TERRA_DATA_PROVENANCE.md), [data dictionary](docs/TERRA_DATA_DICTIONARY.md), and the [sample schema](docs/data/README.md).

## Model families

- **Threshold** — pre-specified depeg/backing rule.
- **Hazard** — transparent aggregate discrete-time withdrawal hazard fallback. Cox PH is explicitly `UNAVAILABLE` when wallet event durations are absent.
- **System Dynamics** — aggregate UST selling → redemption → LUNA minting → price/backing feedback.
- **ABM** — heterogeneous depositor cohorts, arbitrage, protocol conversion, DEX liquidity, optional reserves, and decomposable decisions.

Validation includes MAE, RMSE, MAPE/sMAPE, correlation, directional accuracy, configurable event-timing errors, supply and withdrawal errors, and crisis classification. Metrics are displayed neutrally; the software does not auto-declare a winner.

## Architecture

- `sim`: API-independent Aave and Terra quantitative engines.
- `sim/terra`: dataset views, leakage guard, four model families, replay, metrics, benchmark, ablation, sensitivity, and counterfactuals.
- `backend`: FastAPI, SQLAlchemy, migrations, persistence, import services, export, and read-only chain adapters.
- `frontend`: Next.js research dashboard with a top-level Terra/Aave selector.
- `data`: immutable raw, interim, processed, fixture, export, and run layers.
- `docs`: methodology, assumptions, provenance, validation, limitations, and professor demo.

SQLite remains the default local database. PostgreSQL/Redis remain optional for the full topology.

## Bootstrap and start

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

Open:

- Terra demo: `http://localhost:3000/terra/overview`
- Aave demo: `http://localhost:3000/overview`
- API docs: `http://localhost:8000/docs`

## Terra fixture workflow

```powershell
.\scripts\terra\run_replay.ps1 --model ABM --output data\exports\terra-abm.json
.\scripts\terra\run_benchmark.ps1 --output data\exports\terra-benchmark.json
.\scripts\terra\run_ablation.ps1 --output data\exports\terra-ablation.json
.\scripts\terra\run_counterfactual.ps1 --reaction-delay-hours 6 --output data\exports\terra-counterfactual.json
```

These results are software demonstrations, not historical empirical evidence, because the bundled dataset status is `FIXTURE`.

## Import historical Terra data

Validate first, then import with an honest status:

```powershell
.\.venv\Scripts\python.exe scripts\terra\validate_dataset.py --input path\terra.csv --dataset-version terra_ground_truth_v1
.\scripts\terra\import_dataset.ps1 --input path\terra.csv --dataset-version terra_ground_truth_v1 --status PARTIAL --source-name "Research export" --source-type INDEXED_ONCHAIN
```

Use `REAL_HISTORICAL` only when provenance actually supports that label. Import refuses duplicate timestamps, naive timestamps, impossible negative supplies, and a reused dataset version with a different hash.

## Terra May 2022 final research bundle

The final pipeline preserves the strict-OOS V2 artifact and builds a separate, explicitly post-trigger
conditional mechanism replay. It validates native-redemption provenance, excludes quarantined duplicate
and unavailable fields, and emits structural comparator, aleatory Monte Carlo, epistemic parameter
ensemble, ablation, sensitivity, six-hour moving-origin robustness, diagnostic, metrics, report, and
reproducibility artifacts under `data/processed/terra_final`.

```powershell
.\.venv\Scripts\python.exe scripts\terra\run_final_pipeline.py --overwrite-final
```

`--overwrite-final` is restricted to that generated final directory; it cannot overwrite the V1
benchmark or frozen V2 output.

Run and save exact local verification evidence separately after generation:

```powershell
.\.venv\Scripts\python.exe scripts\terra\run_audit_checks.py
```

## Terra API

Core endpoints include `/api/v1/case-studies`, `/api/v1/terra/status`, dataset import/list/timeseries/provenance, replay lifecycle/timeseries/metrics/events/export, benchmark, ablation, sensitivity, and counterfactual execution.

The export ZIP contains `manifest.json`, source/cutoff/parameter/model files, simulation and ground-truth CSVs, validation metrics, agent events, quality report, and charts.

## Aave contemporary stress test

The original case remains intact. Create an immutable `FIXTURE`, `REAL_MAINNET`, or `CACHED_MAINNET` snapshot, lock a scenario, then run deterministic or seeded Monte Carlo stress. Ethereum integration is strictly read-only: no signer, private-key setting, `eth_sendTransaction`, or `eth_sendRawTransaction` path exists.

The professor preset remains ETH −20%, liquidity haircut 40%, gas 2×, arbitrage capacity 50%, seed `20260914`. No-cascade results are reported as-is.

## Database migrations

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

Migration `0002_terra_research` adds case studies, dataset manifests/sources, hourly Terra states, wallet cohorts, historical replays, model benchmarks, and generic Terra experiment records.

## Tests

```powershell
.\scripts\test.ps1
```

The suite includes timestamp/timezone validation, cutoff enforcement, the mandatory ground-truth isolation test, manifests/hashes, Terra accounting and behavior, deterministic replay, metrics/timing, benchmark/ablation/counterfactuals, API/export lifecycle, the full original Aave suite, frontend tests, lint, and production build.

## Scientific limitations

Archival Terra endpoints may be incomplete; wallet behavior and confidence are only partially observable; CEX order books may be absent; protocol conversion and aggregate DEX execution are simplified; missing intervals may remain; out-of-sample historical replay is not prospective prediction; and Terra validation does not validate Aave liquidation mechanics. See [research limitations](docs/RESEARCH_LIMITATIONS.md).
