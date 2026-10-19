# Phase01-B validation report

Delivery status: **V2_PHASE01B_READY_FOR_COMMANDER_REVIEW**. Scientific acceptance gate: **BLOCKED_INDEPENDENT_ARCHIVE_VALIDATION**. `phase02_ready=false`; ingestion success is not validation of stress results.

Integration input: `3c3928a9b71348648980de92fa80b31b6d2a647d`. V1 annotated tag `v1.0.0-scientific-baseline`, object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`. No V1/Phase01-A file is modified.

A/B/C source: `6e5285f04d1d5ab2900b51389cc3c025c9b64f42`; [actual collection run 39212923329](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39212923329). Local paths below are relative to this directory. Evidence is preserved at `evidence/full/`; D has its own source/run and separate `evidence/borrower_repair/`.

## Test → input → expected → observed → disposition

| Test | Input | Expected | Observed | PASS/FAIL/BLOCKED |
|---|---|---|---|---|
| Block/hash identity | 3 registered headers, chain1 | Exact chain/number/hash/time | All primary reads match; BlockPI/PublicNode header identity agrees | PASS |
| Cross-provider historical state | Same address/method/hash across4 endpoints | Independent complete second archive + distinct backend | Only dRPC complete; Llama403; other state missing; backend unattested | BLOCKED |
| Deterministic readback | 12 decoded components:6 pools+3 oracle+3 borrower | Same canonical content in two reads | 12/12 identical | PASS |
| Tick coverage | 6 registered pool-block bands | Every required word/tick, no duplicate, gross/net valid | 24 word instances;4169 ticks; no missing required range | PASS |
| Oracle source fidelity | USDC/WETH ×3 blocks | Historical config/source/effective price/round linked | 6/6 traces; adapter upstream rounds; cap checked | PASS |
| Borrower/reserve consistency | 8accounts/block ×67reserves | Complete event window; configured balances and HF agree | 24/24 HF/base totals exact;67/67reserveIDs | PASS |
| Units/decimals | Pool and all67reserve tokens | Token decimals match config; raw/base/HF domains separate | USDC6,WETH18; reserve decimals available and matched | PASS |
| Quarantine | Provider failures and negative fixtures | Missing not zero/agreement; incomplete sample not accepted | Unavailable comparison fields retained; missing-data fixtures reject | PASS |
| Timestamp/block leakage | Pinned calls, discovery headers/logs, rounds and reserves | No latest-state calls or future values | 15100 pinned state request records; all selected evidence in declared bounds | PASS |
| SHA-256 integrity | Full+repair manifests | All file bytes and gzip decoded bytes match | 189 manifest entries verified; registry digests match; ZIP digests/CRC match | PASS |
| Pool outer boundary | Outside registered tick bands | Full-pool reconstruction only if independently observed | Explicitly uncollected, not required for registered-band PASS | BLOCKED |
| Oracle heartbeat freshness | Observed rounds | Preregistered source-specific heartbeat | Not preregistered; age reported, no freshness conclusion | BLOCKED |

“Outer boundary” and heartbeat are disclosed out-of-scope limitations, not silently claimed required-gate passes. The mandatory independent archive gate blocks overall acceptance. No current saved numerical discrepancy was observed. Initial false proxy phase mismatch was a software error corrected and re-read, with exact history in oracle report. Discovery range failure was a provider capability limit; complete exact-hash fallback resolved sample collection without changing selection.

## Executed checks and CI

- `python -m unittest discover -s tests -p test_phase01b_validation.py -v`: **25 PASS,0FAIL,0SKIP**, locally (PYTHONPATH includes unchanged Phase01-A) and in saved Windows job. Negative fixtures are synthetic, never labeled Mainnet.
- `python -m pytest tests/test_phase01b_validation.py --junitxml=...`: **25 PASS** in actual borrower run [39213487324](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39213487324), Python3.12.10, Windows Server2025. Original tested hashed Windows dependency lock installed successfully.
- `python docs/research_v2/phase01b/verify_saved.py`: offline full-byte and decoded-evidence validation **PASS**;189 manifest entries,15100 pinned state request records,12 deterministic components,24 borrower-block comparisons. No network or simulation.
- Existing automatic repository CI on code HEAD `4e0c37ce060d34e6c767ac72c9454ccb48ea4606`: [39213486969](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39213486969), **272pytest PASS/0FAIL/0ERROR/0SKIP**, environment smoke5PASS; ruff/mypy and frontend test/lint/build green. Fresh environment smoke overlaps existing tests; do not add5 to272. Existing optional `real-rpc-smoke` job was **SKIPPED**, not a live RPC PASS. This automatic repository workflow was not weakened; no manual full research/MonteCarlo replay was requested or launched.
- Saved JUnit: `evidence/ci/` for code HEAD above and each collection's `targeted-tests.xml`. CI on final documentation/evidence HEAD and Draft PR is reported in the final PR handoff separately, not misattributed to this earlier commit.

## Reproduce within scope

Use the Phase00 hashed Windows lock on its tested platform. A fresh network collection depends on historical provider availability and will legitimately return BLOCKED if access changes.

```powershell
python -m pip install --require-hashes --only-binary=:all: -r docs/research_v2/phase00/g1/requirements-windows-py312.lock.txt
$env:PYTHONPATH = (Get-Location).Path
python docs/research_v2/phase01b/collector.py --registry docs/research_v2/phase01b/SAMPLE_REGISTRATION.json --output phase01b-new-read --full
python -m pytest tests/test_phase01b_validation.py
python docs/research_v2/phase01b/verify_saved.py
```

Without `--full`, the registered execution mode collects only the targeted borrower repair; A/B/C evidence is not overwritten. Always use a **new empty output directory**. `verify_saved.py` checks the committed saved evidence and never reads external RPC. The separate offline workflow runs byte/boundary checks on final push/PR without another data collection. Unix/Windows checkout line endings are not interchangeable file-byte hashes: saved JSON manifests refer to LF artifact bytes; gzip binary hashes refer to exact compressed bytes, separately from uncompressed canonical JSON. Do not describe CRLF checkout SHA-256 as the same hash as LF blob bytes.

## Remaining gates

1. Obtain authorized second archive with verifiable distinct serving-backend provenance; reproduce same-method state comparisons.
2. Preregister heartbeat policy if a later study needs a freshness assertion; no current assertion is made.
3. Expand tick scope before scenarios exceed the registered band; do not substitute whole-pool liquidity for active L.
4. Expand borrower sample/market coverage only with a new auditable sampling plan. This sample contains24 unique accounts and does not estimate whole-market distributions.
5. Before engine work, Commander should resolve independent validation; no Phase02 engine/execution, stress, arbitrage, network or Terra work is included here.
