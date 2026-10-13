# Scientific Validation Audit

Audit date: 2026-10-13  
Audit-start source commit: `2b9a29f5e8c0c8dd910b7d65428fb1d57646b06b`  
Canonical Mainnet block: `26045352` (`4dffe3bdf7bbaf24fd1e3b6c3f4795687dccfd3189cbfb61f4dbaf926722220a`)  
Canonical evidence policy: preserved; corrected results are versioned under
`data/processed/research_final/validation_audit/corrected_run_v1/`.

## Executive decision

**Overall: LIMITED — REPORT WITH CAVEAT.**

The project can proceed to final-report writing only if all Uniswap-sensitive Aave results are taken
from the versioned corrected run and the limitations in this audit are stated. The original Aave
research package is not suitable as the source for price-impact, arbitrage-effect, bad-debt, or Monte
Carlo cascade-frequency claims because a confirmed Uniswap V3 active-liquidity bug affected those
outputs. The canonical input snapshot remains valid and unchanged.

No result was tuned to create a second wave. The corrected deterministic shock/liquidity grid still
has maximum cascade depth 1. A later wave appears in 8/200 corrected Severe Monte Carlo runs; this is
a model-conditional frequency, not an empirical probability.

## Status summary

| Area | Status | Finding |
|---|---|---|
| Uniswap V3 numerical mechanics | **PASS — VERIFIED** after repair | `arbitrage_toward()` previously moved price/tick without crossing initialized-tick liquidity. The minimal repair and regression tests are in place. |
| Independent protocol validation | **LIMITED — REPORT WITH CAVEAT** | Aave read-only state and QuoterV2 amount outputs were executed at the canonical block. A funded fork liquidation/swap transaction was not executed because Foundry/Anvil are absent. |
| Cohort and metric semantics | **PASS — VERIFIED** | Counts, populations, units, and metric definitions were traced to canonical evidence and engine code. |
| Temporal robustness | **LIMITED — REPORT WITH CAVEAT** | Only 1/3 predeclared historical blocks passed the Graph discovery probe; a 3–5 snapshot same-block panel could not be built. |
| Terra Early Warning | **LIMITED — REPORT WITH CAVEAT** | Calculations are cutoff-safe, but no genuine out-of-sample forecasting claim is supported; HIGH first occurs after the initial depeg. |

## 1. Verified facts

### Canonical Mainnet evidence

- The canonical snapshot is `REAL_MAINNET`, chain ID 1, block `26045352`, and its block hash was
  independently read from the configured archive RPC and matched.
- The Graph candidate population is 500. Ethereum RPC verifies 454 borrowers with positive account
  debt; 46 candidates are excluded and there are no recorded failed reads.
- The WETH-collateral population is 255, the USDC-debt population is 182, and the target research
  cohort contains 109 positions.
- The target cohort rule is: `collateral_weth > 0` after verifying
  `usageAsCollateralEnabled == true`, and `debt_usdc > 0`.
- Direct calls to `Pool.getUserAccountData()` at block `26045352` succeeded for 454/454 borrowers.
  All six stored fields matched exactly: total collateral, total debt, available borrows, current
  liquidation threshold, LTV, and protocol Health Factor. No raw address is emitted in audit evidence.
- The existing model-versus-protocol HF comparison covers all 454 verified borrowers at the canonical
  price state. It reports median absolute error `3.0312e-05`, maximum absolute error `0.603077`,
  maximum relative error ratio `0.00582395`, and six quality flags. These are approximation errors in
  the model representation, not discrepancies in the newly repeated protocol calls.

### Baseline Uniswap quote validation

QuoterV2 `eth_call`s used the canonical block and the selected USDC/WETH 0.30% pool. They have no
transaction hash because they are read-only calls.

| WETH in | QuoterV2 USDC out | Model USDC out | Absolute error (USDC) |
|---:|---:|---:|---:|
| 0.1 | 268.592169 | 268.592169110 | 0.000000110 |
| 1 | 2,685.882673 | 2,685.882673852 | 0.000000852 |
| 5 | 13,428.546387 | 13,428.546387936 | 0.000000936 |
| 10 | 26,854.925637 | 26,854.925637373 | 0.000000373 |
| 50 | 134,187.935531 | 134,187.935532003 | 0.000001003 |

QuoterV2's `initializedTicksCrossed` is consistently one larger than the model counter in these
samples. Amount-out agreement is excellent, but the counter difference was not traced through a
contract fork and is retained as a limitation rather than declared semantically identical.

## 2. Confirmed numerical bug and repair

### Root cause

Before this audit, `V3Pool.arbitrage_toward()` updated `sqrtPriceX96` and `current tick` directly.
It did not apply each crossed initialized tick's `liquidityNet`, so subsequent depth and forced-sale
quotes could use liquidity belonging to the old price range. `sell_weth()` already handled upward
tick crossings correctly; the defect was the exogenous/arbitrage repositioning path.

The error is economically material. From the canonical pool state, the prior method kept active
liquidity fixed at approximately `3.2060e18`. Correct active liquidity falls to about 19.39% of that
value after a -20% reposition and 8.99% after -40%.

| Reposition from pool spot | New tick | Initialized records crossed | Correct/legacy liquidity | Legacy depth to another -2% (USDC) | Corrected depth (USDC) |
|---:|---:|---:|---:|---:|---:|
| -5% | 197845 | 9 | 0.983494 | 1,631,204 | 1,604,298 |
| -10% | 198385 | 18 | 0.902145 | 1,084,206 | 928,947 |
| -20% | 199563 | 38 | 0.193902 | 1,496,084 | 290,252 |
| -30% | 200899 | 60 | 0.122315 | 1,398,436 | 170,313 |
| -40% | 202440 | 86 | 0.089936 | 1,286,638 | 107,670 |

A 10 WETH sale after a -20% reposition produces about `21,471.42 USDC` and a `0.1487%` marginal
price impact under corrected liquidity, versus `21,484.31 USDC` and `0.0289%` with stale liquidity.

### Minimal repair

- For upward tick movement, add `liquidityNet` in ascending initialized-tick order.
- For downward movement, subtract `liquidityNet` in descending order.
- Reject a reposition that exhausts active liquidity.
- Preserve the original pool data and all scenario parameters.
- Add tests that assert exact active-liquidity accounting and round-trip restoration.
- Version the model as `0.1.0-aave-v3.9-tick-consistent` and update the synthetic golden fixture.

### Before/after canonical research results

The original research outputs were not overwritten. The corrected run uses identical canonical input,
scenarios, seeds, and 200 Monte Carlo runs per scenario.

| Scenario | Liquidated debt before / after | Max price impact before / after | Bad debt before / after | Depth before / after |
|---|---:|---:|---:|---:|
| Severe | 18,126.51 / 18,126.51 | 0.000510 / 0.004158 | 6,985.44 / 7,255.52 | 1 / 1 |
| Low Liquidity | 9,063.26 / 9,063.26 | 0.000255 / 0.001308 | 2,213.49 / 2,234.90 | 1 / 1 |
| High Gas | 9,063.26 / 9,063.26 | 0.000212 / 0.000544 | 2,212.63 / 2,219.37 | 1 / 1 |
| No Arbitrage | 9,063.26 / 9,063.26 | 0.000212 / 0.001088 | 2,212.63 / 2,230.43 | 1 / 1 |
| Strong Arbitrage | 9,063.26 / 9,063.26 | 0.000212 / approximately 0 | 2,212.63 / 2,208.31 | 1 / 1 |

Baseline and Moderate remain unchanged because neither scenario liquidates a position. The corrected
Severe Monte Carlo cascade frequency changes from 0/200 to 8/200 (`0.04`; Wilson 95% interval
`0.0204–0.0769`, conditional on this simulation). Other tested Monte Carlo scenarios remain zero.
Median liquidated debt is unchanged, while price-impact distributions change materially.

## 3. Independent protocol validation

**LIMITED — REPORT WITH CAVEAT.**

The archive RPC is available and provides canonical historical state. Aave state and QuoterV2
amount outputs therefore have executed evidence. The repository also contains a Foundry fork harness,
but neither `forge` nor `anvil` is installed in the audited environment. No funded historical-account
prerequisite was established and no `liquidationCall` or state-changing Uniswap fork transaction was
executed. Accordingly, contract-level liquidation behavior is **not** labeled PASS.

Prerequisites for upgrading this phase to PASS are: Foundry/Anvil, an archive RPC, deterministic
historical account funding/impersonation, and recorded fork test transaction traces at block
`26045352`.

## 4. Cohort and metric semantics

**PASS — VERIFIED.** Every analysis must name its population rather than use “borrowers” without a
denominator:

- Snapshot protocol/model HF validation: all 454 RPC-verified debt borrowers, canonical state.
- RQ5 stablecoin repricing: the 109-position WETH-collateral/USDC-debt cohort.
- Stress engine: all 454 positions are retained; collateral eligibility, debt composition, and
  scenario state determine liquidation behavior.
- Snapshot HF uses the canonical oracle state. Scenario HF uses shocked/evolving WETH and USDC prices.

Metric definitions:

- `bad_debt`: final model-based uncovered debt,
  `sum(max(0, debt USD - collateral market value))`. It is not automatically a realized protocol,
  treasury, liquidator, or investor loss.
- `unliquidated_debt`: final debt value of positions whose model HF remains below 1.
- `liquidation_at_risk`: debt value initially associated with positions below HF 1 immediately after
  the direct shock.
- `cascade_depth`: count of completed positive-liquidation waves. Depth 1 is direct-only; depth 2+
  contains an endogenous later wave.
- `cascade_amplification`: total liquidated debt divided by direct-shock liquidated debt; undefined
  when direct-shock liquidated debt is zero.
- `time_to_recovery_seconds`: model-clock time until the final DEX/reference spread is within 0.5%,
  or null if not recovered. It is not an empirical market-time prediction.
- RQ5 `debt_usdc` and `total_liquidated_debt_usdc` are token quantities. Their USD equivalent equals
  USDC quantity multiplied by the scenario USDC/USD price; other debt is separately USD-denominated.

Original tables and figures used engine-consistent definitions, but any Uniswap-sensitive number in
the original package is numerically superseded by `corrected_run_v1`.

## 5. Temporal robustness feasibility

**LIMITED — REPORT WITH CAVEAT.** Dates were selected before looking at stress outcomes: the first
Ethereum block at or after 00:00 UTC on the first day of each of the three months preceding the
canonical snapshot month.

| UTC anchor | Block | Archive RPC | Graph borrower discovery |
|---|---:|---|---|
| 2026-07-01 | 25433939 | Available, hash verified | Unavailable: all returned indexers report missing block |
| 2026-08-01 | 25656293 | Available, hash verified | Unavailable: all returned indexers report missing block |
| 2026-09-01 | 25878705 | Available, hash verified | One-candidate discovery probe succeeds; full snapshot not executed |

Only one of three predeclared blocks passes even the borrower-discovery probe. This is insufficient
for the requested 3–5 snapshot panel, and running only the surviving September date would introduce
availability selection. No cross-snapshot cascade comparison is claimed. Required missing evidence is
an archival Aave borrower index (or another reproducible historical candidate set) for July and August,
plus full same-block Aave and Uniswap extraction at every selected block. Canonical block `26045352`
remains unchanged.

## 6. Terra Early Warning audit

**LIMITED — REPORT WITH CAVEAT.** Both retrospective and cutoff-safe calculations pass the implemented
future-perturbation test: changing observations after five cutoffs produces no earlier score or feature
change. This establishes causal calculation, not out-of-sample model validation.

Before the first `UST < 0.995` observation at `2022-05-07T22:00:00Z`, both modes have 1,630 NORMAL
hours, zero WATCH/HIGH/CRISIS hours, and therefore zero pre-event HIGH/CRISIS false-alert hours. This
zero false-alert count is not a positive forecasting result: it accompanies zero useful pre-depeg
alerts. HIGH first occurs at `2022-05-09T19:00:00Z`, 45 hours after the initial depeg and exactly when
`UST < 0.95`; it precedes `UST < 0.90` by only three hours. CRISIS first occurs 72 hours after the
initial depeg.

Feature availability is highly nonuniform:

- Price-derived features: 1,776/1,776 hours.
- Anchor deposit stress: 1,752 hours.
- Holder concentration: 1,608 hours, ending 2022-05-06 23:00 UTC.
- Backing stress: 312 hours; supply growth: 288; Anchor outflow: 192; native redemption: 168.
- Observed DEX liquidity and observed LFG peg-defense intervention are unavailable and excluded.

March-April contain 1,464 hourly rows but only 61 unique UST and 61 unique LUNA prices; 1,403
hour-to-hour transitions are unchanged because daily CoinGecko states are carried within each day.
May has 312 unique hourly price states from the higher-frequency Kaiko source. March-April price-derived
components are therefore stepwise and must not be interpreted as 1,464 independent hourly market
observations.

The cutoff-safe weights are fixed during scoring, but the weights, scales, bands, and feature choices
were developed with knowledge of the historical event. There is no pre-event training registration or
held-out event evaluation. The historical data support retrospective monitoring/mechanism analysis,
not a genuine out-of-sample forecasting claim. No synthetic Anchor flow, DEX liquidity, or LFG
intervention was introduced.

## 7. Conclusions that remain valid

- The canonical same-block snapshot provenance and the 454/109 population counts are verified.
- WETH is counted as collateral only when the user collateral flag is enabled.
- Baseline QuoterV2 amount outputs support the numerical token1-in swap implementation at the canonical
  state for the tested sizes.
- The corrected deterministic -5% to -40% shock/liquidity grid does not produce an endogenous Wave 2;
  its maximum cascade depth remains 1.
- RQ5 USDC depeg direction and the distinction between token quantity and USD value remain valid.
- Aave liquidation-threshold mechanics and direct protocol HF source remain valid.
- Terra results remain retrospective and mechanism-oriented; they do not establish forecasting skill.
- Network/contagion topology findings that do not consume post-reposition Uniswap depth are not changed
  by this numerical repair, subject to their existing one-venue and modeled-topology caveats.

## 8. Conclusions that must be revised

- All old post-reposition Uniswap price-impact and executable-depth values.
- Downstream `bad_debt` values in scenarios with liquidations.
- The prior apparent insensitivity to arbitrage capacity. Corrected No Arbitrage, High Gas, and Strong
  Arbitrage outputs now separate clearly.
- The old Severe Monte Carlo claim of zero modeled cascades; corrected evidence contains 8/200 runs
  with depth at least 2. This remains a model-conditional result.
- Any figure, table, abstract sentence, executive-summary sentence, or presentation claim that cites
  those superseded original outputs.
- Any suggestion that Terra HIGH/CRISIS alerts forecast the initial depeg, or that zero pre-event false
  alerts alone demonstrates predictive value.
- Any broad temporal-robustness claim based only on the canonical snapshot.

## 9. Readiness for final report writing

**LIMITED — REPORT WITH CAVEAT.** Final writing may begin after the author treats the corrected run as
the sole numerical source for Uniswap-sensitive Aave claims and explicitly retains the protocol-fork,
temporal-panel, and Terra forecasting limitations. The original generated figures/tables are not to be
silently overwritten; corrected figures and tables should be regenerated into a new versioned report
package with a differences appendix referencing this audit.

The project is not ready for claims of contract-fork liquidation validation, multi-snapshot temporal
robustness, or out-of-sample Terra forecasting.

## 10. Evidence map and reproduction

- `data/processed/research_final/validation_audit/phase1_uniswap_numerical_audit.json`
- `data/processed/research_final/validation_audit/phase2_protocol_validation.json`
- `data/processed/research_final/validation_audit/phase3_metric_cohort_audit.json`
- `data/processed/research_final/validation_audit/phase4_temporal_robustness.json`
- `data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json`
- `data/processed/research_final/validation_audit/before_after_corrected_run.json`
- `data/processed/research_final/validation_audit/verification_results.json`
- `data/processed/research_final/validation_audit/audit_manifest.json`

Reproduce the audit evidence (configured archive RPC and Graph credentials are used without being
written to artifacts):

```powershell
.\.venv\Scripts\python.exe .\scripts\research\run_scientific_validation_audit.py
```

The structured protocol evidence records exact block identifiers, call counts, numerical errors, and
unavailable prerequisites. API keys and raw borrower addresses are excluded.

Final verification: 132 pytest tests passed (three dependency deprecation warnings), Ruff passed,
mypy strict validation of the `sim` package passed, and all ten research quality-gate checks passed.
