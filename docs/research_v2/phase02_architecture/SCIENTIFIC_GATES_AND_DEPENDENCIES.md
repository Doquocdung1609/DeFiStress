# Scientific gates, source decisions và unresolved dependencies

**DESIGN ONLY · GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED**

Architecture authorization của người dùng chỉ mở thiết kế tài liệu. Issue35 chỉ mở offline L1/L2 guards. Không scope nào tự cho phép engine, historical calibration, stress/Monte Carlo, liquidation/swap execution, funded arbitrage, network propagation hoặc release/merge.

## 1. Gates không được gộp

| Gate / use class | Evidence hiện tại | Điều kiện còn cần / quyết định |
|---|---|---|
| Gate A — strict independent archival validation | Request-serving backend identities/separation chưa được xác minh | Giữ nguyên tiêu chí request-linked verifiable actual serving paths. Brand/URL/CI/hash match không đủ; không tự đổi thành PASS |
| Gate B — scoped core agreement | Alchemy2 passes ×3blocks×29labels,174 field-pass agreements/87 block-field pairs vs saved dRPC; không paired contemporaneous collection | PASS_REGISTERED_CORE_SCOPE hiện hữu, không mở rộng sang whole tick/HF/round vectors hoặc mọi market |
| L1 saved evidence integrity | Có original byte/provenance/coverage dossiers; PR36 đề xuất executable harness | Xem PR36 là PENDING đến khi exact CI/artifacts và Commander acceptance có. Byte equality không archive independence |
| L2 synthetic contract/primitive checks | Có V1 tests, PR36 guard fixtures tham khảo | Implementation của architecture tests cần lệnh riêng. Synthetic input≠observed Mainnet; không mock Gate A/receipts thành PASS |
| L3 engine / execution components | Có thiết kế trong PR này, không implementation được phép | Commander grant + prerequisites từng package. Historical engine entry vẫn NO-GO theo accepted Gate B protocol; ngoại lệ scope nếu có phải do Commander quyết định riêng và giữ Gate A BLOCKED |
| L4 historical stress/execution findings | Chưa có use-specific verified execution inputs/receipts hoặc V2 results | Gate A cho input campaign + coverage/profile/oracle/native execution tests + run authorization; A PASS một mình không đủ |
| L5 causal/predictive publication | Không có identification hoặc sealed OOS validation mới | Model interventions không xác lập Mainnet causality; Terra cần bộ evaluation riêng; publication approval riêng |

## 2. Source → design decision → scientific limitation

Locators dưới đây relative repository tại **integration anchor `2e0ec142c475f8d1362f90c4ca8d2f0718e41f77`**, trừ scientific registry tại `3f6e5302483681209e2408531eb5a15389f9fded` và PR36 tại `c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb` (PENDING). Exact source link/blob index ở [handoff](COMMANDER_HANDOFF.md). Không coi paths PROPOSED là existing evidence.

| Source locator / symbol | Design decision | Scientific limitation retained |
|---|---|---|
| `docs/research_v2/phase00/V2_RESEARCH_UPGRADE_BLUEPRINT.md` U01–U08/Phase02 | Separate state, valuation, execution/agents and validation; Terra/network outside first engine packages | Upgrade proposals chưa là implemented features; positive outcome không là PASS condition |
| `docs/research_v2/phase01a/PILOT_SAMPLE_REGISTRY.json` và `PHASE01A_VALIDATION_REPORT.md` qua accepted gate matrix | Snapshot/selection/quarantine capability model; no collector fallback | Eight-tick/sentinel pilot không là full tick/census; Phase01B band không sửa artifact cũ |
| `docs/research_v2/phase01b/SAMPLE_REGISTRATION.json:/tick_scope,/borrower_sample,/gates` | Explicit bands, complete window selection, units/tolerances |3 close blocks/2 fee tiers one pair; sample24 not market; old tolerances không tự relax |
| `docs/research_v2/phase01b/collector.py:core_observation,oracle_config` | Historical read port phải pin chain/hash/contract/method; record round/config origin | Core29 labels không full data independence; native contract implementation chưa chứng minh từ revision number |
| `docs/research_v2/phase01b/{AAVE_HISTORICAL_ORACLE_TRACE,UNISWAP_TICK_COVERAGE_REPORT,BORROWER_RECONSTRUCTION_AUDIT}.md` | Capability-specific execution blocks; separate upstream/native rounds, HF profile và band |6 deep traces không freshness attestation; partial band not whole pool; HF exact sample not bytecode proof |
| `docs/research_v2/phase01b/verify_saved.py` | Reuse guard concepts after isolation/version review; record historical economic reconstruction versus native profile | Static verifier không thay fork execution; unknown reserve dependencies phải BLOCKED |
| `docs/research_v2/backend_provenance/BACKEND_INDEPENDENCE_DECISION.md` và `docs/research_v2/gate_b_protocol/GATE_A_VS_B_PROTOCOL.md` | Immutable independent gates; read-only/synthetic/protocol/execution scopes separate | Common-backend risk unresolved; no new authorization from architecture |
| `docs/research_v2/gate_b_protocol/EVIDENCE_SCOPE_MATRIX.json:GBE-01…12` | Field-level evidence lineage, coverage, replay labels |174 comparisons≠174 independent samples; Alchemy full values absent; saved-reference time asymmetry |
| `sim/schemas.py:BorrowerPosition,SimulationEvent,json_safe` | New full-portfolio vectors, typed outcome stages và integer-string serialization | V1 route+other-value aggregates/float serialization not silently native-exact inputs |
| `backend/app/adapters/aave/{contracts,positions,oracle}.py` | ABI/base concepts reused as candidates; historical code/profile and WAD tags explicit | Block-number calls and legacy HF-ray field không chứng minh complete native historical fidelity |
| `sim/oracle.py:OraclePolicy` và `sim/tests/test_oracle_policy.py` | Preserve A/B/C formulas/history/initialization as counterfactual controls | Code test mô hình không xác minh oracle thực tế Aave/Chainlink |
| `sim/lending/{health_factor,liquidation}.py` | Economic math reference; new versioned close-factor/bonus/fee/eMode/native rounding profile | V1 constants/route constraints không universal Aave V3 rule; USDC price quantity/valuation tách |
| `sim/dex/uniswap_v3.py:V3Pool` và adapter `ticks.py:bitmap_ticks` | Reuse tick decoding/algebra concept; new native integer profile and coverage guard | Decimal/log-derived tick and last-band extrapolation không bit-exact executable V3 validation |
| `sim/agents/{liquidator,arbitrageur}.py`, `sim/engine/run.py` | New budgets/reservations, deterministic ordering/replay và named reposition control | V1 no-recycle/representative agents; arbitrage reset not funded; don't copy permanent attempted-borrower lock |
| `contracts/validation/{README.md,test/ForkValidation.t.sol}` | Future local-fork execution port with receipts/deltas/profile/mode | Harness exists but independent funded execution chưa nghiệm thu; positive amount alone không complete conservation |
| Locked `accepted_claims_registry.json:P2:C32,P2:C33,INT:CL_INT_RQ1_POLICY_CONDITIONAL,INT:CL_INT_RQ2_TWO_CHANNELS,INT:CL_INT_ELIGIBLE_NOT_EXECUTED` | Explicit policy source, two channels DEX absorption/valuation transmission và lifecycle counts | Không oracle-independent cascade, newly eligible≠executed; policy instances not unique wallets |
| Locked integration RQ3/RQ4/RQ5/RQ6, historical tiers/Terra negative records | Mechanism-specific funding/arbitrage/unit/config contracts; separate future Terra/network namespaces | No Mainnet causal claim, successful Terra forecast, realized loss hoặc full multilayer contagion inference |
| PR36 `prephase02_offline/{validate_offline.py,OFFLINE_EVIDENCE_MANIFEST.json}`, `tests/test_prephase02_offline.py` | Candidate offline helpers only; no compile/import dependency from unmerged head | CI/acceptance PENDING; don't propagate simplified guard semantics into protocol/native contracts |

## 3. PR36 compatibility review — PENDING, không sửa parallel task

Preflight: Issue35 OPEN; PR36 OPEN/Draft, head `c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb`; offline run39281653358 và repository CI39281653451/39281659860 QUEUED khi kiểm tra. Handoff PR36 còn liên kết run cũ39281363424; run đó không được dùng để tuyên bố current head đã PASS. CI/Commander acceptance mới có thể thay trạng thái sau này, nhưng architecture không tự phụ thuộc vào kết quả đó.

| Observed candidate API | Compatibility boundary / future acceptance criterion |
|---|---|
| `canonical_equal` normalize tuple/list rồi dùng Python equality | V2 contracts phải type-check trước so sánh: bool/int không tương đương vì Python `True==1`; equality helper không thay typed schema |
| `liquidity_consistent(active,total)` | `total` chưa có aggregation/unit contract trong proposed pool model; active≤total không độc lập xác nhận tick/fee/inventory consistency. Không dùng sum gross như total executable liquidity |
| `oracle_valid(... round_id>0 ...)` | Chỉ hợp với supported round-bearing source; USDC cap adapter cần upstream/native union, không fabricated round0 để qua guard |
| `borrower_complete(... hf_wad:int ...)` | Integer HF không đủ xác minh WAD scale/eMode/profile/complete liabilities. New typed scale/complete participation checks bắt buộc |
| `run_offline`/CLI | Structured L1/L2/gate/check statuses là authority; CLI exit0 có thể vẫn có BLOCKED checks, không infer whole pack PASS từ process success |

Đây là integration compatibility constraints từ source review, không tuyên bố PR36 tests đã FAIL hoặc thay Commander review của parallel task. Sau merge+acceptance mới quyết định reuse/wrapper; nếu API khác contract, adapter mới phải giữ semantics, không thay accepted Phase01 data.

## 4. Unresolved constraints và STOP conditions

| ID | Unknown / impact | Điều kiện giải quyết trước use |
|---|---|---|
| UQ-01 | Aave historical implementation/bytecode→close-factor/eMode/dust/fee/rounding chưa mapping đầy đủ | Pin effective implementation/ABI/source/rule profile và native boundary/fork cases; unknown native use BLOCKED |
| UQ-02 | Native Uniswap integer/profile/fee-growth and inventory completeness | Source-hashed native math/version plus tick boundary tests, balance/fee data; analytic quote riêng, native execution chưa PASS |
| UQ-03 | Request-serving backend independence chưa attest | Gate A strict original protocol; no URL/brand inference hoặc RPC re-probe trong task này |
| UQ-04 | Freshness/available-time/elapsed accrual policy và price timeline | Preregister source-specific heartbeat/adapter and clock/accounting policies; không dùng future feed hoặc stale silent fallback |
| UQ-05 | Historical funded route/allowance/gas/archive/receipt capability | Future authorized local-fork evidence; injected funding labeled; no Mainnet broadcast |
| UQ-06 | Account reserves/source-round coverage vs route-specific execution | Full required liabilities/config/flags cho use case, no observed debt0 từ missing; deep round trace2assets không bao phủ67reserve feeds |
| UQ-07 | Agent behavior, competition, ordering, capital recycle/splitting | Scenario/version assumptions đăng ký trước; không coi calibration/benefit đã có |
| UQ-08 | PR36 API/CI/acceptance pending | Exact head/artifacts/Commander disposition rồi optional adapter review; no cherry-pick or API coupling now |
| UQ-09 | Alchemy values absent/Actions retention | Preserve summary/index and explicit non-replayability; prospective sanitized per-field policy nếu được phép; không sửa origin data |

Unknown không chặn việc review **design** khi đã fail-closed thành explicit contracts; chúng chặn historical/native implementation acceptance và scientific claims tương ứng. Nếu muốn scope exception/prototype, Commander phải ban hành grant mới; không đổi Gate A thành PASS hoặc tự làm Phase02.

## 5. Six-RQ và locked-claim safeguards

Sáu RQ nguyên văn và dependencies được đưa ở handoff để tránh ID/wording drift. RQ1–RQ2 cần riêng absorption và valuation controls; RQ3 cần execution states/budgets; RQ4 cần funded route evidence nếu claim execution; RQ5 cần quantity/base/settlement separation; RQ6 cần LTV/LT/bonus profiles riêng. V1 LTV255 portfolios không cohort109 WETH/USDC; V1 LT reported debt valuation theo USD tại USDC/USD=1, không USDC token quantity. Không tạo numerical result V2 từ architecture.

Registry48 records vẫn44 affirmative/4 disallowed. Bốn original claim IDs `CL_FROZEN_RQ1_UNQUALIFIED_WORDING`, `CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING`, `CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT`, `CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION` chỉ audit trail, không dùng làm affirmative findings. Source access verification labels không thay đổi. Severe frequency/selected-path denominators, historical association tiers, Terra negative result và network limits V1 được giữ, không suy xác suất thị trường, tổn thất thực tế hoặc causal Mainnet transmission.
