# P04-02-S — saved audit and synthetic PIT contracts

Source baseline: `8ec1eb2c49c1d4c3088b2bb0550b38fb6a05bde5` (the pinned PR #51 head). Its functional P04-01 source anchor is `9207ead7db3acf1332b34cebcd19981c2f7bd9cc`.

This package implements immutable Terra-specific identities, observation/vintage/source clocks, four-way value availability, point-in-time admission, completed-interval and derived-availability guards, synthetic trailing windows, split/fit leakage checks, bounded saved-metadata loading, deterministic canonical hashes and quality summaries.

The package does **not** produce a warning score. It does not read historical rows into temporal feature functions, fit thresholds, classify an onset, run a Terra backtest, simulate exits, call a network or alter V1/scientific evidence.

## Historical boundary

The saved P04-01 registry contains 35 byte-verified inputs and 14 candidate historical fields. All 14 fields retain `approved_forecast_use=false`; zero historical fields are point-in-time cleared. The nine gate statuses from the P04-01 manifest are preserved as distinct values. A synthetic fixture becoming `ELIGIBLE` never changes those historical statuses.

The Terra chain identity is `terra:columbus-5` and is not represented as an EVM numeric chain ID. Quote pairs and units are exact: `UST/USDT` cannot become `UST/USD` without a separately evidenced conversion contract.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/v2/terra_pit --junitxml=p04-02-junit.xml
.\.venv\Scripts\python.exe -m ruff check defistress_v2/terra_pit tests/v2/terra_pit
.\.venv\Scripts\python.exe -m mypy --strict defistress_v2/terra_pit
```

The saved-metadata smoke must run from Git-LF checkout bytes because its pins intentionally reject CRLF rewriting:

```powershell
.\.venv\Scripts\python.exe -m defistress_v2.terra_pit.validate `
  --implementation-commit <HEAD> `
  --output P04_02_VALIDATION_REPORT.json
```

Required status remains:

`TERRA_POINT_IN_TIME_ELIGIBILITY_BLOCKED — HISTORICAL_BACKTEST_NOT_AUTHORIZED`

`GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED`
