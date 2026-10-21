# P03-D01 — Multilayer entities, edges and loss-ledger contract

**DESIGN_ONLY — PROPOSED — NOT_IMPLEMENTED — ALL_TEST_SPECIFICATIONS_NOT_RUN**

Authority: `V2_P02_03_SYNTHETIC_OFFLINE_VALUATION_AUTHORIZED`, parallel research preparation only. Work owns this document; future Codex implementation owns a separately approved runtime namespace. Base: `38e4b7b2081c9056e98319194898535a3f9cfe8c`. No network construction, propagation experiment, historical calculation or new result is performed here.

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED**

## Source → decision → boundary

All paths below are pinned to the base above, except the immutable scientific lock explicitly named.

| Source | Design decision | Scientific boundary |
|---|---|---|
| `docs/research_v2/phase00/V2_RESEARCH_UPGRADE_BLUEPRINT.md`, U06/U08 | Keep layers/units/time and an event-linked loss ledger, with paired intervention controls | V1 structural network is a display baseline, not a validated dynamic contagion model |
| `docs/research_v2/phase02_architecture/DATA_AND_INTERFACE_CONTRACTS.md` | Reuse accepted identity/origin/evidence concepts; all proposed records below need typed interfaces in a future approved package | Saved state supplies limited read capabilities, not execution or propagation capability |
| `docs/research_v2/phase02_architecture/TEST_SPECIFICATIONS.md`, T03–T05 | Require explicit execution stages, conservation, deterministic ordering and idempotence before consuming dynamic flows | Future tests and receipts are absent; 46 architecture specifications are not 46 passing runtime tests |
| `docs/research_v2/gate_b_protocol/PHASE02_DEPENDENCY_AND_RISK_MATRIX.md`, U06 | Separate structural dependence, modeled intervention and historical causal identification | Gate B and temporal co-occurrence do not establish causal Mainnet transmission |
| `docs/research_v2/program_control/PROGRAM_STATE.json` | P02-01/02 are accepted interfaces; P02-03-S permission is narrow and does not open Phase03 runtime | Gate A/backend attestation, source coverage and native execution remain unresolved |

## Proposed records and layer semantics

These are logical contracts, not existing Python API signatures or implemented graph algorithms. Entity identity includes chain/contract/account where applicable, entity type, schema version and evidence domain. A pseudonym mapping must be stable within a declared dataset; it must not imply that different addresses are independent economic owners.

| Record / layer | Required fields and orientation | Unit / meaning |
|---|---|---|
| EntityState | `entity_id`, type BORROWER/RESERVE/POOL/AGENT/PRICE_SOURCE, state/version hash, block/time context, provenance and availability | A versioned entity state; asset identity remains explicit |
| Credit exposure | Borrower → lending reserve; collateral and liabilities kept in separate typed attributes; reserve flags/valuation context and completeness | Raw units by token, plus explicitly priced base valuation; no netting of different assets by default |
| Portfolio overlap | Borrower ↔ asset membership with directed endpoint roles; common collateral is structural overlap | Exposure/membership, not an executed loss transfer; projected borrower–borrower edges require an explicit projection rule |
| Execution flow | Payer → receiver; attempt/event ID, exact token, amount, before/after states and MODEL_TRANSITION or FORK/CHAIN receipt class | Settled raw token transfer; evaluated/skipped/reverted proposals are separate non-flow records |
| DEX/valuation channel | Pool price observation → policy/context → portfolio valuation; parent hashes, observation availability and checkpoint | Price/unit ratio and valuation dependence; not USD transferred along an edge |
| Funding | Funding account → agent reservation/settlement; credit policy and settlement time explicit | Asset budget and committed/reserved amounts; no assumed capital recycling |
| TransitionLink | Source/destination state hashes, event/order, mechanism, origin, policy/profile, evidence locator, active/inactive and reason | A modeled active link requires a valid transition; historical association retains its own evidence tier |

Cross-layer aggregation is opt-in: a reporting view must name its unit conversion, as-of price set, inclusion rule and deduplication key. Normalized edge strengths and centrality scores are not money, probabilities or additive losses. No centrality algorithm or fitted edge weights are selected in this design.

## Loss-ledger invariants

1. Keep token accounting separate from valuation accounting. For each asset and atomic transition, reconcile debits, credits and profile-authorized issuance/burn/fee destinations; do not add a balancing “other loss” to hide an unexplained residual. Protocol debt liability/burn and underlying token cash are distinct ledgers.
2. A collateral seizure or repayment transfer moves an asset/claim; it is not automatically a new system loss. Avoid counting the same amount at the borrower, liquidator and pool endpoints. Fees have declared recipients and a defined system boundary.
3. Mark-to-market change needs one fixed reporting boundary and price set. Cash injections, withdrawals, issued claims and external flows must be explicit. An HF reduction, liquidation volume, unliquidated debt and modeled bad debt are different measures; only a versioned valuation/loss definition may connect them.
4. Separate initial shock valuation from subsequent transitions. A proposed paired effect is `loss(full mechanism, same inputs) − loss(declared control, same inputs)`, measured at the same horizon and reporting basis. It is a model contrast, not a realized Mainnet loss or automatically an identified per-edge causal attribution. Nonlinear channel contrasts need not sum to the joint contrast.
5. Replay keys include event/attempt ID, input-state version and profile. Retrying one event commits at most one delta. A new valid partial repayment requires a new state/version and re-evaluation. Concurrent proposals do not merge stale balance deltas.
6. Missing coverage, source or prices yields BLOCKED with the affected entities/metrics. Observed zero remains zero; unknown is never zero. Horizon/event limits produce CENSORED with queued work, not a false equilibrium.

## Proposed control and test specifications

All outcomes currently `NOT_RUN_DESIGN_ONLY`; fixtures would be SYNTHETIC and implementation requires a new grant. No numerical fixture is a research result.

| ID | Input / intervention | Expected / invariant | Failure code / evidence needed |
|---|---|---|---|
| P03-DT01 | One repayment/seizure with two endpoint records | One transfer key, zero unexplained per-asset residual; no doubled system loss | DOUBLE_COUNT / independently specified token ledger |
| P03-DT02 | Add raw USDC to WETH or normalized strength | Reject aggregation without explicit common-base conversion | LAYER_UNIT_MISMATCH / field+unit schema |
| P03-DT03 | Structural overlap and same-block association, no transition | No active modeled propagation flow; preserve association tier | EVIDENCE_PROMOTION / source and origin records |
| P03-DT04 | No shock / no sale / valuation transmission disabled | Report each mechanism's contrast and unchanged channels; zero effect is admissible | CONTROL_CONTAMINATION / paired config and state hashes |
| P03-DT05 | Reference-only and no-arbitrage controls | Price absorption and valuation feedback remain separate; no funded trade inferred | CHANNEL_CONFUSION / profile and event ledger |
| P03-DT06 | Duplicate/reordered stale events | One committed delta; deterministic canonical order or explicit rejection | REPLAY_DIVERGENCE / journal and state versions |
| P03-DT07 | Missing pool band/liability/valuation | Quarantine affected derived metrics; no complete-market label | CAPABILITY_INCOMPLETE / dependency and missingness report |
| P03-DT08 | Pending arrival at terminal horizon | CENSORED; no declared quiescence while pending work exists | TERMINATION_MISLABEL / clock, queue and stop reason |

## Dependencies, unknowns and next delivery

This document can be reviewed in parallel with P02-03-S. Runtime needs accepted P02-03 valuation, P02-04 liquidation, P02-05 swap/accounting, P02-06 scheduling and P02-07 integration evidence plus a specific Phase03 grant. Historical use additionally needs applicable Gate A, coverage, source-clock and execution evidence. Unknowns: precise loss/system boundary, graph projection, future execution profiles, edge completeness, intervention horizon and registered sample. Resolve them in a versioned protocol before coding/runs; no defaults are inferred here.

Next Work delivery is a schema/control review after those interfaces exist. Acceptance of this design means every proposed active edge has state/time/unit/mechanism/evidence and every proposed loss has an accounting boundary; it does not mean contagion exists, amplification is positive or a network has been executed. Rollback is a reviewed document revert; V1 and its claims remain unchanged.
