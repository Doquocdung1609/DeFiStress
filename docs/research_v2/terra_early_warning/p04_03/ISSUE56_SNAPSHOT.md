# Issue #56 technical contract snapshot

Source: https://github.com/Doquocdung1609/DeFiStress/issues/56

GitHub updated_at: 2026-10-29T07:09:28Z

This is a read-only snapshot of the technical contract, not an independent authorization. The direct user instruction to execute the two supplied masterprompts records the bounded Commander S-only grant; see AUTHORIZATION_AND_DEPENDENCIES.md.

# P04-03-S — Transparent synthetic early-warning models

**EXECUTABLE HANDOFF PROPOSAL — P04-02 ACCEPTED; SCOPED IMPLEMENTATION GRANT TO BE RECORDED; NOT_DISPATCHED.** Prepared under `V2_STEP6_P02_03_INDEPENDENT_REVIEW_AND_TERRA_RESEARCH_AUTHORIZED`. This document does not grant historical model execution. P04-02 is now accepted and integrated; record the bounded P04-03-S implementation grant before starting code. This review/handoff is not historical model permission. No callable Codex launcher was used; an Issue is not execution.

## Start, ownership and prerequisites

Current accepted integration **`c51d4d06d8b560a149e32ade922f8ed62da1a589`**, PR52 merge. Accepted source HEAD **`1b6851feb667ee588ee89fcb51306d2553c3a6b5`**, tree **`5b0579a06c4584c9ce80f6ad803df991a80c1688`**. Exact post-merge [CI40832842756](https://github.com/Doquocdung1609/DeFiStress/actions/runs/40832842756) SUCCESS; actual630pytest+5environment PASS and preservation readback; artifact12880040157 SHA256 `3c695b730b2e98e34ccfb992bfb0772c3646142d5d150a1d0be1f85c8295f1da`. Review [Work acceptance](https://github.com/Doquocdung1609/DeFiStress/pull/52#issuecomment-6490216826). PIT selected-input schema0.2/linear-chain/exact-terminating profiles are accepted within disclosed scope. Before implementation, fetch actual integration, inspect later deltas, pin the accepted source/API/profile; do not reset accepted work. If that dependency changes incompatibly, STOP.

Suggested branch `research/terra-v2-p04-03-synthetic-warning-models`. Codex proposed ownership: new `defistress_v2/terra_warning/` and `tests/v2/terra_warning/`, concise `docs/research_v2/terra_early_warning/p04_03/` evidence, no edits to Work scientific ledger or `terra_pit` unless a separate compatibility repair is approved. Work owns this handoff/protocol/source eligibility. Do not import P02-03 Ethereum AssetId/valuation objects to represent Terra: those interfaces are separate, and PR55 is not accepted. Use the accepted Terra PIT chain/unit/source/vintage contracts.

## Bounded S-only scope

Implement pure, immutable deterministic baseline outputs from **synthetic fixtures only**:

- B0 never-alert; B1 downside peg deviation/persistence; B2 LUNA loss/declared trailing risk summary; B3 transparent multi-signal composite.
- Model configuration, exact feature values, required participation, unit/reference-price assumptions, numeric/selection profiles, source-age policy and risk-level thresholds are explicit and versioned. No learned weights, opaque optimizer, market-data loading or calibrated probability claim.
- Output: decision/issued/information-cutoff UTC; model/config/profile IDs+hashes; selected dependency IDs/vintages/ancestry; exact score numerator/denominator or reasoned abstention; level; contributions; admitted/rejected/stale dependencies; verification/origin=SYNTHETIC. Observed stress input and derived alert have distinct labels.
- Completed/available interval admission must use accepted PIT rules. Missing/stale/unproven required input→ABSTAIN/BLOCKED, not safe/zero. No hidden renormalization from partial features. Compare baseline/composite on common support; expose coverage separately.
- Freeze context per decision. Typed lineage must bind selected causal inputs, reference/model assumptions, policies, window, cutoff and numeric/selection/schema profiles. Unused future perturbation does not alter past selected output; changed selected evidence changes hash even if value is equal. Do not promote current artifact vintage to historical availability.
- Reject non-SYNTHETIC observation origin in scoring. Passing a caller status named ELIGIBLE is not historical admission. Saved P04-01/PR53 data are audit inputs only and must never be loaded into model scoring.

All proposed APIs/paths here are PROPOSED, not existing code. Keep functions network/filesystem-collector free. No UI/dashboard, backtest/evaluator, event-onset search, threshold fit, investor position, order/exit simulation, RPC, MonteCarlo, network propagation or V1 changes.

## Arithmetic and reference fixtures

Use exact rational arithmetic for new synthetic risk computations. Do not silently rely on mutable Decimal context. Accepted PIT candidate's exact-terminating-decimal/1 helper deliberately rejects nonterminating means; never change that helper or choose windows to evade the error. If a new mean is needed, define a separate immutable reduced-fraction result/profile in this package with bounded input/window sizes and exact-bound/plus-one tests. No global contract/profile modification. Float thresholds and implicit USD/USDT equality are prohibited.

Toy reference only: matching unit p0=1, d=max(0,1-pUST/p0), l=max(0,1-pLUNA_t/pLUNA_prev), c=(min(1,d/0.02)+min(1,l/0.20))/2. WATCH c≥1/2, HIGH c≥3/4; B1 WATCH/HIGH d≥0.005/0.01; B2 WATCH/HIGH l≥0.05/0.10. Equality is inclusive. These values are **synthetic test constants**, never historical-fit thresholds or probabilities.

| ID | Synthetic input/control | Independent expected |
|---|---|---|
| P04-M01 | UST1,LUNA100→100 | d0,l0,c0; no alert |
| P04-M02 | UST0.99,LUNA100→100 | d1/100,l0,c1/4; B1HIGH, composite belowWATCH |
| P04-M03 | UST1,LUNA100→90 | d0,l1/10,c1/4; B2HIGH, composite belowWATCH |
| P04-M04 | UST0.99,LUNA100→90 | c1/2, WATCH exactly; notHIGH |
| P04-M05 | UST0.98,LUNA100→80 | c1,HIGH |
| P04-M06 | Missing/quarantined required UST or unproved availability | Reasoned ABSTAIN/BLOCKED/REJECTED, no LUNA-only renormalization |
| P04-M07 | Change unused future value/revision after cutoff; then change selected causal evidence with equal value | First output/hash unchanged; second lineage hash changes; old decision never rewritten |
| P04-M08 | Interval closes/publication occurs after decision; duplicate vintages warmup | Exclude incomplete/unavailable observation; distinct-time warmup only; insufficient→ABSTAIN |
| P04-M09 | Synthetic false-alarm reference:24 eligible labeled non-event hourly decisions, alerts02/03/08 | Future evaluation spec:3alert observations/24,2episodes/one exposure day under explicit episode rule; event recall undefined. Do not implement historical evaluator in S. |
| P04-M10 | No issued alerts on eligible normal exposure | Future metrics spec:precision undefined, not100%; false episodes0 plus exposure. Model outputs quiet; no historical performance claim. |
| P04-M11 | Wrong quote/unit/origin/source; holdout fit attempted; mutable input | Reject/blocked before scoring; no USD relabel or historical admission; no fitting API |
| P04-M12 | Same fixtures under low/high Decimal contexts, threshold equality and one exact step around it | Same exact values/hashes; no rounding threshold flip; nonterminating rational representation explicit |

M09/M10 evaluation formulas remain design/test obligations for P04-04, not permission to build a historical evaluator. Record their disposition instead of falsely claiming all12 are runtime implemented. Add negative tests for bool/int confusion, invalid config, duplicate source/vintage, retracted selected value, future canonicality where applicable, zero previous LUNA price, absent conversion, bounded loading if any fixture reader, hash-domain mismatch and context isolation. Known missingness is not an economic zero.

## Protocol boundary

Research hypotheses RQ-T1…T6 remain separate from technical outputs. No observed pre-event alert exists in this package. First-valid-alert/lead, precision/recall, false episodes per exposure, missed events, robustness and exit success require eligible historical inputs, curator-owned onset/control labels and separately approved protocol/run. Terra case outcome is known; sealing a protocol now does not make it blind prospective evaluation.

## Local-first acceptance and CI

Run scoped synthetic tests/JUnit, accepted PIT regressions and affected typed-contract regressions locally; Ruff/strict mypy, wheel exact source bytes, protected-tree diff, fixture/model/config/source hashes and deterministic replay. Emit PASS/FAIL/BLOCKED with actual counts; retain intentional negative-input outcomes. All tests must be synthetic; no historical values fed into models. Pin original failed cases and fixes; do not deselect to get green.

Provide concise evidence JSON: exact base/head/tree, source-byte hashes, fixture/config/profile versions, implemented/deferred control IDs, JUnit checksums, tool/Python/OS, boundaries and source preservation. One Draft PR into `feat/terra-model-v2`, reviewed revert rollback. Owner confirms budget$0+stop. No budget increase or paid provider. Use the reviewed minimal required CI plan only; don't add another unconditional full-suite workflow. If free tier blocks CI, label `CI_BLOCKED_BY_FREE_TIER_LIMIT`, keep unmerged; skip/pending is never PASS.

## STOP / ready rule

STOP on unaccepted PIT interface, missing explicit S scope grant, need to change scientific gate/source/V1/profile, real historical input, event/threshold tuning, historical backtest, missing publication proof, exit execution, live/network/paid access, unsolved unit/time/hash mismatch or shared-file collision. Return exact path/context/invariant. No empirical capability is inferred from pure code PASS.

**Current: HANDOFF_PREPARED — P04_02_TECHNICALLY_ACCEPTED — P04_03_S_GRANT_TO_BE_RECORDED — NOT_DISPATCHED.** Historical/model-performance/exit gates remain blocked or unexecuted. After prerequisites and scoped grant are recorded, this handoff can be marked READY_FOR_CODEX_EXECUTION; it does not itself launch Codex.


## 29/10/2026 governed checkpoint

P04-02 acceptance is technical/synthetic and saved-metadata scoped; all14historical fields remain BLOCKED. Nohistorical score/backtest/exit authorization follows. PR55 synthetic valuation remains TARGETED_REPAIR_REQUIRED; its types are not dependencies to import into Terra. Existing owner$0budget hard-stop confirmation remains in force. No callable Codex executor was invoked. The earlier23/10dependency-blocked checkpoint is retained in Issue history and superseded only for the now-accepted P04-02 dependency.
