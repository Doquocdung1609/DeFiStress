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

## Independent final-review repair profile

The repair is based on PR HEAD `c74c307e155af2baa96168e76224c46641f83c04`; commit and CI provenance belong in the delivery evidence rather than this semantic contract. The selected-input hash domain is now `defistress-terra-pit-contracts/0.2`, binding admission policy, explicit zero interval delay, selected revision ancestry, units/window and selection/arithmetic profiles. Old content hashes must not be reused for this profile. Unused future descendants do not enter the selected lineage.

Revision inputs represent one stable logical observation ID/source/chain/unit/interval/frequency and a linear, parent-before-child chain. Multiple roots, forks, cycles/unknown parents, and decreasing availability fail closed. Proven descendant order resolves equal availability without lexical names. A published missing/quarantined revision does not resurrect an older value. Unknown publication/availability still provides no new admission proof.

Arithmetic retains the Codex exact-terminating-decimal profile: rational computation is exact; a nonterminating result raises NON_TERMINATING_MEAN_UNSUPPORTED. It is not rounded using Work decimal34, and no general rolling-feature model is claimed. Unsupported averages require a separately reviewed representation extension.

A domain-separated semantic identity digest binds the exact35 registered source paths, sizes, raw Git SHA256, Git blob SHA1 and verification labels from the pinned P04-01 registry. It is independent of JSON whitespace/checkout line endings; caller-supplied raw-byte pins remain checked separately. This verifies saved metadata identities, not a fresh read of all35 source files. The14field and9gate guards retain their existing source-boundary behavior.

The loader caps reads before allocation and compares the opened descriptor with the pre-read path identity, descriptor after read, and path after read. These controls detect tested swap/growth cases in a trusted offline checkout. They do not claim comprehensive protection against every hostile filesystem race, FIFO replacement or adversarial concurrent directory writer; such environments remain unsupported. Deep parser failures become typed integrity errors and the CLI retains failure-report behavior. Historical fields/backtests/exit permissions remain blocked.
