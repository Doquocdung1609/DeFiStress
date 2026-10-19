# Aave historical oracle trace

Status: **PASS for six registered USDC/WETH asset-block observations**, two identical decoded passes per block; independent archive corroboration remains BLOCKED. This is oracle observation, not DEX observation or a counterfactual valuation policy.

Integration input: `3c3928a9b71348648980de92fa80b31b6d2a647d`. V1 annotated tag `v1.0.0-scientific-baseline`, object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`. No V1/Phase01-A file is modified.

A/B/C source: `6e5285f04d1d5ab2900b51389cc3c025c9b64f42`; [actual collection run 39212923329](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39212923329). Local paths below are relative to this directory. Evidence is preserved at `evidence/full/`; D has its own source/run and separate `evidence/borrower_repair/`.

## Historical configuration

At all three pinned blocks, provider `0x2f39d218133afab8f2b819b1066c7e434ad94e9e` resolves Pool `0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2`, revision 11, Oracle `0x54586be62e3c3580375ae3723c145253060ca0c2`, DataProvider `0x0a16f2fcc0d44fae41cc54e079281d84a363becd`. Oracle base currency address zero, base unit 100000000; reported prices below are **raw base units**, divide by 10^8 for base-currency valuation. Prices are never substituted with Uniswap spot.

USDC source `0x3f73f03aa83b2a48ed27e964ed0fdb590332095b` is a cap adapter: `latestAnswer/decimals/getPriceCap/ASSET_TO_USD_AGGREGATOR` work; `latestRoundData` on the adapter does not. Trace the upstream proxy `0xea674bbc33ae708bc9eb4ba348b04e4eb55b496b`, its observed round and historical aggregator. Cap 104000000; effective adapter answer = min(upstream answer, cap), and scaling agrees with Aave `getAssetPrice`. This does not invent an adapter-native round ID.

WETH source `0x5424384b256154046e9667ddfaaa5e550145215e` exposes proxy rounds. `getRoundData(observedRoundId)` at the same block, phase-to-aggregator mapping, aggregator answer/start/update and normalized round IDs agree.

| Block | Asset | Aave price raw (10^8 base/unit asset) | Observed upstream/proxy round ID | Updated at (Unix s) | Age at block (s) | Trace |
|---|---|---:|---:|---:|---:|---|
| 26045352 | USDC | 99982053 | 55340232221128654858 | 1790173907 | 55128 | PASS |
| 26045352 | WETH | 269828680094 | 36893488147419127492 | 1790226383 | 2652 | PASS |
| 26038152 | USDC | 99986496 | 55340232221128654857 | 1790087483 | 54504 | PASS |
| 26038152 | WETH | 277070022545 | 36893488147419127458 | 1790139827 | 2160 | PASS |
| 26030952 | USDC | 99995000 | 36893488147419103788 | 1790005799 | 49212 | PASS |
| 26030952 | WETH | 272565870374 | 36893488147419127427 | 1790052647 | 2364 | PASS |

`evidence/full/components/{block}-pass{1,2}-oracle.json.gz` retains source addresses, source decimals (8), answers, startedAt, updatedAt, answeredInRound, exact round lookup, historical phase ID and current aggregator address. USDC aggregator changes across the sampled historical states are retained; no current configuration is substituted retrospectively.

## Time and verification boundary

Require positive answer and `0 < startedAt <= updatedAt <= block timestamp`, valid round completion and same-round values. **Heartbeat freshness is NOT evaluated**: no source-specific heartbeat threshold was preregistered. The 49–55k-second USDC ages remain visible rather than silently called fresh. This is point-in-time round tracing, not complete round-history recovery, cryptographic state proof or independent archive validation. For borrowers, all-reserve Aave prices/source pointers are collected at the same block; deep round tracing is limited to these two registered assets.

## Software erratum

Initial run 39212645247 at `5a73c96d521c56d93b914e334b61cc5fcaad368d` compared proxy phase-wrapped IDs with raw aggregator IDs as if identical and reported a false round mismatch. Correction at `6e5285f04d1d5ab2900b51389cc3c025c9b64f42` normalizes both roundId and answeredInRound low 64 bits while checking answer/timestamps and phase aggregator. Unit test rejects changed answers. Initial mismatch is **SOFTWARE_ERROR**, not observed oracle disagreement. The corrected run supplies current oracle evidence; V1 artifacts are unchanged.

[Aave oracle interface](https://www.aave.com/docs/aave-v3/smart-contracts/oracles), [USDC adapter verified interface](https://etherscan.io/address/0x3f73f03aa83b2a48ed27e964ed0fdb590332095b), [WETH proxy verified interface](https://etherscan.io/address/0x5424384B256154046E9667dDFaaa5e550145215e) inform ABI interpretation; saved historical RPC calls are the actual observations.
