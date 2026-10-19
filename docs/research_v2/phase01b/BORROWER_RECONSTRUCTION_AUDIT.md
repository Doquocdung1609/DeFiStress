# Borrower reconstruction audit

Status: **PASS for the registered sample**, 24/24 borrower-block instances, 24 distinct pseudonymous addresses, two identical full decoded passes per block. This is a recent-Borrow-event sample, not an Ethereum/Aave market census.

Integration input: `3c3928a9b71348648980de92fa80b31b6d2a647d`. V1 annotated tag `v1.0.0-scientific-baseline`, object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`. No V1/Phase01-A file is modified.

A/B/C source: `6e5285f04d1d5ab2900b51389cc3c025c9b64f42`; [actual collection run 39212923329](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39212923329). Local paths below are relative to this directory. Evidence is preserved at `evidence/full/`; D has its own source/run and separate `evidence/borrower_repair/`.

D source: `4e0c37ce060d34e6c767ac72c9454ccb48ea4606`; [borrower-only repair run 39213487324](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39213487324). Evidence in `evidence/borrower_repair/`; prior range-query failures stay in `evidence/full/` and in the repair request journals. Phase01-A sentinels are untouched.

## Sample and discovery

Registration commit `c637ab579ff4075b84f2c9c5fed3637759c09632` fixed a complete 1024-block Borrow-event window ending at each target. Distinct `onBehalfOf` addresses are ranked by SHA-256 of `1:` + lowercase address; select first 8, no stress/HF/eMode selection, no replacement of debt-free accounts. `REGISTERED_INPUT.json` in each evidence directory preserves its exact source-version registration; transport amendments did not change the window or ranking.

dRPC rejected range queries with code35 / “ranges over10000 blocks ... free plan” even though the requested window is 1024 blocks. The targeted repair validates all 1024 headers, parent continuity and increasing timestamps, then reads logs at **every exact block hash**, refusing any partial window. Each Borrow log must match its header; duplicates by blockHash/transactionHash/logIndex fail. All three windows are complete on both reads. Saved headers are projected required fields with a digest of full parsed original result; they are not original HTTP wire bytes or a cryptographic independent chain proof.

| Target block | Complete discovery window | Borrow events | Distinct candidates | Selected accounts | Historical reserves/account | HF comparisons PASS | Max absolute HF difference (raw WAD) | Repeat |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 26045352 | 26044329…26045352 | 91 | 59 | 8 | 67 | 8/8 | 0 | PASS |
| 26038152 | 26037129…26038152 | 122 | 86 | 8 | 67 | 8/8 | 0 | PASS |
| 26030952 | 26029929…26030952 | 152 | 93 | 8 | 67 | 8/8 | 0 | PASS |

365 Borrow-event instances across the three nonoverlapping windows; candidate counts are per window, not a market borrower count. Exactly one selected account has zero debt at B0; UINT256_MAX HF sentinel is preserved and the account is not replaced. The sample exercises eMode categories 34, 40, 41 and 43 where present at historical blocks.

## Portfolio reconstruction and units

Read all 67 historical reserve assets/account: supplied aToken balances, stable/variable debts, enabled-collateral flag, reserve IDs/configuration, token decimals, same-block Aave source pointer and price, user configuration bitmap, eMode and per-asset collateral bitmap overrides. All 67 reserve IDs resolve at every target; all saved source/decimals/configuration dependencies and user flags are available. Reserve timestamps are at/before target. Asset amounts retain token base units; portfolio values use Aave base currency 10^8; HF uses 10^18 WAD. Source pointers for all reserves are observed; complete round tracing is only USDC/WETH (see oracle report).

Economic reconstruction: enabled collateral value = floor(balance × Aave price /10^decimals); debt value = ceil((stable+variable debt) × price /10^decimals); weighted per-asset LT incorporates historical user eMode bitmap. HF = floor(sum(collateralBase_i × LT_i) ×10^18 /(totalDebtBase ×10000)). The predeclared HF tolerance is 10^10 raw WAD (10^-8 HF); base-total tolerance max(1, participating reserve count). **Observed differences are all exactly zero**, so no tolerance change or fit was required.

This is a full-portfolio economic reconstruction checked against `getUserAccountData` at the same historical block. It is not a formal source/bytecode replica of each historical Pool implementation, transaction execution validation or a liquidation-route model. A current GenericLogic source was inspected to understand arithmetic; it was not established as historical revision11 bytecode and is not cited as proof of that implementation.

## Quarantine and independent checks

Raw/decoded missing reads remain explicit BLOCKED/null, never filled with zero. Missing account/eMode or active valuation dependencies block reconstruction; flag conflicts fail. `verify_saved.py` additionally refuses saved samples with missing user configuration, reserve source/configuration/ID/decimals, wrong block, incomplete discovery, ranking mismatch, timestamp leakage, changed hashes or any nonzero observed HF/base-total difference. No such missing dependency occurs in this saved sample. Provider failure categories differ from software/data mismatch; the successfully completed sample does not repair the independent-provider BLOCKED gate.

Exact addresses, reserve vectors, source/configuration, account raw values, eMode categories, per-instance comparisons and discovery logs are retained in `components/{block}-pass{1,2}-borrowers.json.gz`. `VALIDATION_SUMMARY.json` indexes per-instance results; no aggregate from this sample is extrapolated to the whole market.
