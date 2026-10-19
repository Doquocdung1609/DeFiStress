# Test specifications — PROPOSED, NOT RUN

**DESIGN ONLY · GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED**

Đây là **46 test specifications tương lai**, không phải46 tests đã PASS. Mọi observed outcome hiện tại là `NOT_RUN_DESIGN_ONLY`. Test fixtures ghi `SYNTHETIC`; chỉ historical/fork campaigns được duyệt mới cung cấp empirical evidence. Expected **reject/BLOCKED/skip/revert/no trade** có thể là test PASS khi đúng hợp đồng; không bắt kết quả kinh tế dương. Tests metadata/checks của PR thiết kế được báo riêng trong handoff.

Evidence codes: **F** = versioned synthetic input/expected output/unit tags và comparator; **S** = exact saved source/block/ABI/content hashes; **L** = before/after model states, event/ledger diffs và invariant report; **R** = local-fork environment/block/profile, receipt/events/gas/state deltas. F không được giả thành S/R. Proposed failure codes dưới đây mô tả diagnostic namespace; kết quả protocol revert phải giữ revert selector/data được phép, không chỉ string chung.

## M01 — Historical State Adapter (8)

I01-IDENTITY = chain/block/contract/time phù hợp; I01-SCHEMA = typed precision/schema; I01-PROVENANCE = bytes/lineage; I01-ORIGIN = đúng evidence kind; I01-NO_FILL = missing không thành0.

| Test ID | Requirement | Input | Expected | Invariant | Failure code | Evidence needed |
|---|---|---|---|---|---|---|
| P02-T01-01 | Positive typed load | Complete SYNTHETIC pack, one BlockRef, valid source checksums | OK, origin giữ SYNTHETIC, no network | I01-IDENTITY/ORIGIN | INPUT_IDENTITY_MISMATCH | F; S cho future saved-pack loading |
| P02-T01-02 | Wrong chain/hash/contract | Parametric mutations chain/hash/pool/token ordering | REJECTED affected component; dependent execution blocked | I01-IDENTITY | INPUT_IDENTITY_MISMATCH | F+mutation diff |
| P02-T01-03 | Exact integer/decimals | USDC6/WETH18; mutate decimals, bool/int, float or oversized uint | Valid values preserved; wrong types/scale/overflow rejected | I01-SCHEMA | TYPE_OR_UNIT_MISMATCH | F+boundary vectors |
| P02-T01-04 | Missing vs observed zero | Available0 versus missing/null active liability |0 retained; missing quarantined, not debt-free inference | I01-NO_FILL | MISSING_OBSERVATION | F+dependency report |
| P02-T01-05 | Byte/hash domains | Original gzip/LF/CRLF and one-byte tamper | Correct domain hashes only; tamper rejected, no auto normalization of source | I01-PROVENANCE | DIGEST_MISMATCH | F+raw/decoded hash records |
| P02-T01-06 | Cross-block leakage | Reserve block hash differs; future update timestamp | REJECTED join, no mixed-time snapshot | I01-IDENTITY | TIMESTAMP_OR_BLOCK_LEAKAGE | F; S request refs later |
| P02-T01-07 | Coverage capability | Tick band only, 24 selected portfolios, no native inventory/profile | Registered capabilities only; EXECUTION_INPUT_COMPLETE absent | I01-PROVENANCE | CAPABILITY_INCOMPLETE | F+coverage ledger; S in future |
| P02-T01-08 | Origin/summary safeguards | COUNTERFACTUAL child of observation; Alchemy metadata without values | Child not OBSERVED; summary replay BLOCKED, existing Gate B scoped status unchanged | I01-ORIGIN | NOT_REPLAYABLE_FROM_PERSISTED_SUMMARY | F+S summary schema; no174 comparison rerun |

## M02 — Oracle/Valuation (9)

| Test ID | Requirement | Input | Expected | Invariant | Failure code | Evidence needed |
|---|---|---|---|---|---|---|
| P02-T02-01 | Unit-consistent HF | Complete SYNTHETIC multiasset portfolio, eMode off/on and prices with base U | Exact declared economic-profile HF/vector, eMode context retained | I02-UNITS/HF_CONTEXT | VALUATION_MISMATCH | F+manual rational expectation; S/native comparator later |
| P02-T02-02 | Zero-debt boundary | All required debts observed0 | NO_DEBT tag, no division0/Infinity/eligible | I02-NO_DEBT | HF_SENTINEL_MISMATCH | F |
| P02-T02-03 | HF and parameter semantics | HF just below/equal/above WAD1; mutate LT vs LTV vs bonus | Equality not below1; only correct mechanism changes; native rounding uses profile | I02-HF_CONTEXT | HF_RULE_CONTEXT_MISMATCH | F+profile boundary vectors |
| P02-T02-04 | DEX/oracle separation | DEX spot tagged as HISTORICAL_AAVE_ORACLE; wrong source | REJECTED, no price substitution | I02-PRICE_SOURCE | ORACLE_SOURCE_CONFUSION | F+expected source identity |
| P02-T02-05 | Adapter/round semantics | Upstream round present, native adapter round unsupported; wrong phase/answer variant | Valid upstream-only trace allowed; mismatched supported round rejected | I02-PRICE_SOURCE | ORACLE_ROUND_MISMATCH | F; S historical adapter linkage later |
| P02-T02-06 | Time/freshness | Future updatedAt, missing heartbeat, explicit stale rule case | Future rejected; unknown heartbeat blocks native-use freshness; no fill | I02-NO_LOOKAHEAD | TIMESTAMP_LEAKAGE / ORACLE_FRESHNESS_UNSPECIFIED | F+policy config; S when collected |
| P02-T02-07 | A/B/C policy boundary | Deterministic completed price history, g/w/alpha, baseline d0, insufficient lag, invalid params | Equations/spec exact; B independent DEX; C no future; invalid params rejected | I02-POLICY | POLICY_INPUT_INVALID | F+expected rational values; no engine run |
| P02-T02-08 | Context isolation | Intrawave reporting price differs from checkpoint eligibility price | Reporting never mutates frozen eligibility context | I02-HF_CONTEXT | VALUATION_CONTEXT_LEAKAGE | F+checkpoint hashes |
| P02-T02-09 | USDC depeg units | Same raw USDC debt, two COUNTERFACTUAL positive USDC/base prices | Quantity identical, valuation changes; base mismatch/price0 rejects | I02-UNITS | DEBT_QUANTITY_VALUATION_CONFUSION | F+per-asset units |

## M03 — Liquidation (10)

| Test ID | Requirement | Input | Expected | Invariant | Failure code | Evidence needed |
|---|---|---|---|---|---|---|
| P02-T03-01 | Eligible positive execution | Complete SYNTHETIC eligible route, verified modeled profile, funding/quote | Distinct assessed/evaluated/attempted/executed events, repay>0, mode=MODEL_TRANSITION | I03-STAGES/POSITIVE_REPAY | INVALID_EXECUTION_OUTCOME | F+L; R mandatory for fork finding |
| P02-T03-02 | Eligible not executable | HF<1 via other debt, selected route debt observed0 | Evaluated then skipped NO_MODELLED_DEBT_ROUTE; no attempt/repayment; preserve legacy reason mapping | I03-STAGES | NO_MODELLED_DEBT_ROUTE | F+L |
| P02-T03-03 | Debt/collateral zero | NO_DEBT or selected collateral0 | No debt INELIGIBLE; missing collateral route skip; no fabricated balance | I03-BOUNDS | NO_DEBT / NO_COLLATERAL_ROUTE | F+L |
| P02-T03-04 | Versioned close factor/eMode | Two explicit synthetic profiles at HF/dust thresholds; unknown historical implementation | Profile-specific boundaries exact; unknown native profile BLOCKED | I03-PROFILE | PROFILE_UNVERIFIED | F+rule table; S/R historical mapping later |
| P02-T03-05 | Bonus/collateral cap | Nonpar debt price, heterogeneous decimals, collateral cap/fee/dust variants | Reciprocally capped repay/seize with profile rounding; no overrepay/overseize | I03-BOUNDS/LEDGER | LIQUIDATION_AMOUNT_MISMATCH | F+L; R+rounding traces later |
| P02-T03-06 | Capital/gas/allowance | Insufficient debt funding, native gas0, missing allowance, capacity limit | Pre-submit skip with actual reason; no attempted/executed flag | I03-BUDGET | INSUFFICIENT_CAPITAL / INSUFFICIENT_GAS_FUNDS / ALLOWANCE_MISSING / CAPACITY_LIMIT | F+reservation ledger |
| P02-T03-07 | Attempt vs revert/software | Valid submitted protocol failure versus injected application exception | Protocol/model revert has evidence/mode; software exception ABORTED not protocol revert | I03-STAGES | PROTOCOL_REVERT / SOFTWARE_ABORT | F+L; R for actual fork revert |
| P02-T03-08 | Conservation and fee split | Debt burn/repay, collateral/liquidator/treasury/aToken deltas; one corrupted delta | Valid ledger reconciles; any unexplained delta aborts; no plug entry | I03-LEDGER | CONSERVATION_VIOLATION | F+L; R token/storage diffs later |
| P02-T03-09 | Partial/duplicate attempt | Same attempt twice; new version after valid partial repay | Duplicate commits0 extra; new valid attempt allowed after re-evaluation | I03-NO_DUPLICATE | DUPLICATE_ATTEMPT | F+L+nonce/state IDs |
| P02-T03-10 | Liquidation/sale boundary | Liquidation commits; separate sale violates minOut | Repayment remains committed, collateral inventory remains; bundle rollback only if mode justified | I03-LEDGER/STAGES | SLIPPAGE_LIMIT | F+L; R per-transaction evidence |

## M04 — AMM (10)

| Test ID | Requirement | Input | Expected | Invariant | Failure code | Evidence needed |
|---|---|---|---|---|---|---|
| P02-T04-01 | Positive within interval | SYNTHETIC L>0, exact-input each direction, complete band | Analytic reference and integer-profile outputs reconcile by declared rounding; quote no mutation | I04-EXACT_UNITS/QUOTE_PURE | SWAP_MATH_MISMATCH | F+rational expectation; R comparison later |
| P02-T04-02 | Zero/dust/negative input | Gross input0, smallest raw amounts/fee rounding, negative input |0 no-op; dust skip according spec; negative rejected, no fake execution | I04-EXACT_UNITS | ZERO_REPAY_OR_DUST / INPUT_AMOUNT_INVALID | F |
| P02-T04-03 | Both-direction crossing | Known initialized boundaries, signed net, exact-boundary endpoints | Upward+net, downward−net; tick boundary convention correct, no duplicate crossing | I04-TICK_CROSS | TICK_TRANSITION_MISMATCH | F+crossing trace |
| P02-T04-04 | Zero active liquidity | Known empty interval then initialized liquidity; fully empty band | No divide0; only traverse verified empty interval; no reachable liquidity→no executable output | I04-ACTIVE_L/COVERAGE | NO_REACHABLE_LIQUIDITY | F+coverage/progress trace |
| P02-T04-05 | Coverage exceeded | Input needs price beyond band; missing bitmap word inside band | BLOCKED ALL_OR_NOTHING, no extrapolated L or partial commit | I04-COVERAGE | COVERAGE_EXCEEDED | F+requested/available ranges |
| P02-T04-06 | Tick/bitmap invalidity | Duplicate ticks, wrong spacing/bitmap, gross<abs(net), negative resultant L | REJECTED; partial band not required to have sumNet0 | I04-TICK_CROSS/ACTIVE_L | TICK_DATA_INVALID | F+validator diagnostics |
| P02-T04-07 | Orientation and decimals | Token-order reversal, USDC6/WETH18 vs wrong metadata, fee500/3000 | Correct reciprocal human quote/fee units; wrong identity rejected | I04-ORIENTATION/EXACT_UNITS | TYPE_OR_UNIT_MISMATCH | F+formula/unit labels |
| P02-T04-08 | Execution bounds | Quote expiry, minimumOut/sqrtLimit/deadline violation | Skip before submit or evidenced revert after attempt; outcome stage explicit | I04-NATIVE_PROFILE | STALE_STATE_OR_QUOTE / SLIPPAGE_LIMIT / DEADLINE_EXCEEDED | F+L; R later |
| P02-T04-09 | Swap accounting | Pool/user balances, input fee split and output; missing inventory/fee-growth; corrupted fee double count | Conservation only with complete accounting; incomplete native capability blocked; corrupt ledger abort | I04-FEE_CONSERVATION | CAPABILITY_INCOMPLETE / CONSERVATION_VIOLATION | F+L; R ERC20/fee-state deltas |
| P02-T04-10 | Native profile/token bounds | Negative tick/Q96 boundaries/large uint/mulDiv vectors; unsupported transfer behavior | Profile-specific exact ints; no float/log fallback; unknown profile/token blocked | I04-NATIVE_PROFILE | PROFILE_UNVERIFIED / TOKEN_BEHAVIOR_UNSUPPORTED | F+profile source hashes; S/R later |

## M05 — Agents/Orchestration (9)

| Test ID | Requirement | Input | Expected | Invariant | Failure code | Evidence needed |
|---|---|---|---|---|---|---|
| P02-T05-01 | Phase causality | Synthetic shock/completed observations and decision phases | Valuation→eligibility→decision→attempt→commit/impact→next checkpoint; no in-progress feedback | I05-TIME/ORDER | PHASE_ORDER_VIOLATION | F+L chronological events |
| P02-T05-02 | Sequential/concurrent conflict | Two proposals same pool/account version; worker completion order permuted | Canonical commit order; second stale proposal re-evaluated, not additive merge | I05-SOLE_WRITER/ORDER | STALE_STATE_OR_QUOTE | F+L read/write-set trace |
| P02-T05-03 | Shared budgets/recycling | Competing reservations, proceeds not yet settled, split policy off/on | No overspend, no premature reuse; split only if declared with separate costs | I05-RESERVATION | INSUFFICIENT_CAPITAL | F+L per-asset budget ledger |
| P02-T05-04 | Latency/state changes | Delayed intent, changed HF/debt/pool, expiry | Revalidate at arrival; no falsely paid debt; skip/replan according rule | I05-TIME | LATENCY_EXPIRED / STALE_STATE_OR_QUOTE | F+L clock versions |
| P02-T05-05 | Transaction rollback | Model invariant failure; fork protocol revert; already-committed prior tx | Model abort isolates invalid proposal; fork gas/nonce retained; previous tx not rolled back | I05-ATOMICITY | SOFTWARE_ABORT / PROTOCOL_REVERT | F+L; R actual receipt |
| P02-T05-06 | Idempotent replay/duplicates | Same event/attempt retried twice across restart | One committed delta; retained attempt lineage, no double gas/token charge | I05-IDEMPOTENCY | DUPLICATE_ATTEMPT | F+L persisted replay journal |
| P02-T05-07 | Arbitrage/control labels | Price residual but no funds/venue; reposition control toggled | No funded trade; reposition not PnL/swap evidence; funded route future requires own ledger | I05-RESERVATION/TIME | EXECUTION_CAPABILITY_UNAVAILABLE | F+L+mode tags |
| P02-T05-08 | Termination/censoring | Volume0 with pending arrival; horizon/max-events; true quiescence | No premature stop; pending-limit case CENSORED, quiescence scoped to policy | I05-TERMINATION | CENSORED_HORIZON / CENSORED_EVENT_LIMIT | F+L queue/stop reason |
| P02-T05-09 | Replay failure | Same manifest/seed/order vs mutated config/hash/PRNG/rounding or worker order | Same contract→same deterministic ledger/state; mutation identifies first divergent event; no wall-clock/UUID leakage | I05-REPLAY/ORDER | REPLAY_DIVERGENCE | F+L+run/env manifests |

## Acceptance procedure tương lai

Mỗi implemented case xuất test ID, requirement/version, fixture origin/hash, expected, observed, diagnostic, evidence refs và PASS/FAIL/BLOCKED. F-only test PASS là implementation confidence, không historical validation. Historical suite chỉ nhận accepted source/profile/capabilities; Gate A/backend independence và receipts không thể được mock thành PASS. Preserve failed/unavailable cases, không deselect hoặc nới tolerance để làm xanh. Spec changes cần version và Commander disposition; các pure fixtures này chưa được cấp quyền implementation bởi PR kiến trúc.

P02-07 phải reconcile direct component and integration outcomes: event counts không unique-wallet counts; observed/reconstructed/synthetic/counterfactual lineage; conservation/rounding có declared tolerances **trước** đối chiếu; control no shock/no sale/reference-only/no arb có thể cho no cascade/no profit. Không chạy Monte Carlo hoặc historical stress trong việc nghiệm thu tài liệu thiết kế.
