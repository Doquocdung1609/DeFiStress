# Scientific Evidence Integration Addendum v1

Trạng thái đề nghị: **READY_FOR_COMMANDER_REVIEW**. Addendum này không tự cấp `SCIENTIFIC_CONTENT_LOCK`, không merge PR #11/#9 và không thay Frozen v3 hay Oracle Diagnostic v1.

## 1. Provenance và phạm vi

- Starting HEAD / Oracle Diagnostic HEAD: `3011ba5e8cd23ee697c36d0aec6d047d8d58f653`.
- Frozen v3 baseline: `9842c4f2c35adb8b4ec906e1bc76afa825d197c7`; manifest SHA-256 `0ee158ad67cd16a009a6d064960619fd03ab93657d12fa25f4b860e351157613`.
- Oracle Diagnostic manifest SHA-256 `fb391166fe61805b0690f393f63da844c8449a969a53e692d04b9adae36fc8e6`; selection commit `a2c37e3d513054131083b791a05f8b50047925fd`.
- P2 locator commit: `8f5b635a316d72546b8a0eb0c2e8a66503b5d44f`; PR #9 vẫn DRAFT/OPEN và Commander đã yêu cầu P2 oracle reconciliation riêng.
- Canonical block `26045352`; snapshot SHA-256 `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99`; 454 verified borrowers; cohort riêng 109 WETH collateral-enabled/USDC debt.
- Model/policy version: `0.1.0-aave-v3.10-metric-semantics`; 72 targeted replays, không chạy lại 10.000 Monte Carlo.

Quy tắc ưu tiên: `Original → P0 corrected v2 → Level-3 → targeted repair → Frozen v3 → Oracle Diagnostic v1 → Integration Addendum v1`. Diagnostic chỉ sửa cách diễn giải RQ1/RQ2; không thay số liệu Frozen v3.

## 2. Eligible khác Attempted và Executed

Định nghĩa khóa:

- **Newly eligible:** direct-shock HF ≥ 1, post-Wave-1 HF < 1 và borrower chưa thuộc attempted set Wave 1.
- **Attempted/evaluated:** engine tạo `LIQUIDATION` hoặc `LIQUIDATION_SKIPPED` cho borrower ở wave sau.
- **Executed:** có event `LIQUIDATION` với `debt_repaid > 0`.

| Policy | 4 deterministic depth-2 giữ depth≥2 | 10 targeted MC giữ depth≥2 | Direct eligible instances | Newly eligible | Attempted later | Executed Wave 2 | Skipped | Not attempted | Wave-2 debt repaid (USDC) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A_ADVERSE_PASS_THROUGH | 4/4 | 10/10 | 507 | 35 | 35 | 14 | 21 | 0 | 58574.91415500 |
| B_REFERENCE_ONLY | 0/4 | 0/10 | 507 | 0 | 0 | 0 | 0 | 0 | 0 |
| C_WEAK_LAGGED_SMOOTHED_PROXY | 0/4 | 0/10 | 507 | 6 | 6 | 0 | 6 | 0 | 0 |
| C_MODERATE_LAGGED_SMOOTHED_PROXY | 0/4 | 2/10 | 507 | 11 | 11 | 2 | 9 | 0 | 4952.07991200 |

Các count là **borrower-case instances** trên 18 selected cases, không phải số borrower duy nhất hay tần suất quần thể. Tất cả newly eligible instances đều được engine đánh giá ở wave sau. Trong 36 instances không executed, raw engine reason là `NOT_ELIGIBLE`; state-level reconciliation phân giải thành `NO_MODELLED_USDC_DEBT`, vì HF của full 454-borrower population có thể phản ánh other-debt trong khi liquidation planner chỉ thực thi route WETH-collateral/USDC-debt. Không có skip targeted nào được quy cho capital, capacity, gas hay profitability. Vì vậy không được suy executed từ newly eligible hoặc từ depth aggregate.

## 3. Ma trận sáu RQ

## RQ1 — Điều kiện và ngưỡng xuất hiện thanh lý dây chuyền.

**Question.** Điều kiện và ngưỡng xuất hiện thanh lý dây chuyền.

**Method.** Đối chiếu Frozen grid/checkpoint Policy A với A/B/C targeted diagnostic và event-level eligibility/execution audit.

**Evidence.** `RQ1_GRID32_MAX_DEPTH`, `RQ1_GRID60_DEPTH2`, `RQ1_MC_SEVERE_DEPTH2_COUNT`, `INT_A_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4`, `INT_B_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4`, `INT_C_WEAK_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4`, `INT_C_MODERATE_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4`.

**Result.** Policy A: grid 60 có 4 depth-2 cells và Severe 280/10.000 depth≥2; trong bốn selected deterministic cases A/B/Cweak/Cmoderate = 4/0/0/0. Trong mười targeted A-depth2 MC paths = 10/0/0/2.

**Interpretation.** Wave 2 là simulated endogenous feedback dưới policy định giá cụ thể; không có ngưỡng cascade độc lập oracle được xác lập.

**Limitation.** 280/10.000 chỉ thuộc locked Severe Policy A; 10 paths là sample có chủ đích; không phải xác suất Ethereum hay Aave oracle thực tế.

**Accepted Claim.** Trong môi trường frozen và Policy A adverse pass-through, tail stress có thể tạo Wave 2; sự xuất hiện Wave 2 nhạy với policy truyền giá.

**Status:** `ACCEPTED_WITH_LIMITATIONS`.

## RQ2 — Vai trò thanh khoản DEX.

**Question.** Vai trò thanh khoản DEX.

**Method.** Tách executable depth/haircut, immediate DEX impact, post-arbitrage spread và HF feedback qua policy.

**Evidence.** `RQ2_CANONICAL_DEPTH_2PCT`, `RQ2_DEPTH2_HAIRCUT90_COUNT`, `RQ2_DEPTH2_HAIRCUT95_COUNT`, `RQ4_IMMEDIATE_PRICE_IMPACT`, `RQ4_SPREAD_ARB100`.

**Result.** Haircut làm giảm sức hấp thụ forced selling và tăng biến dạng DEX; nhưng eligibility mới và depth phụ thuộc valuation policy A/B/C.

**Interpretation.** DEX liquidity là kênh hấp thụ giao dịch; oracle policy là kênh truyền DEX state sang HF. Hai kênh không được nhập làm một.

**Limitation.** Một pool/snapshot; haircut 90/95% chưa quan sát; không routing đa venue; không xác minh Aave dùng Uniswap spot.

**Accepted Claim.** Thanh khoản thấp có thể khuếch đại price impact trong mô hình, nhưng không tự nó bảo đảm có borrower mới đủ điều kiện thanh lý.

**Status:** `ACCEPTED_WITH_LIMITATIONS`.

## RQ3 — Gas, vốn, công suất và độ trễ thanh lý.

**Question.** Gas, vốn, công suất và độ trễ thanh lý.

**Method.** Giữ Frozen v3 sweeps vốn/capacity/gas/delay; dùng event audit để tách eligible, evaluated, skipped và executed.

**Evidence.** `RQ3_CAPITAL_25_LIQUIDATED`, `RQ3_CAPITAL_100_LIQUIDATED`, `RQ3_DELAY_SEVERITY_CHANGE`.

**Result.** Vốn 25/50% binding; 100/200% không binding trong miền thử. Trong targeted audit, newly eligible không đồng nghĩa executed: các skip sau Wave 1 được truy về gate tài sản của route WETH-collateral/USDC-debt, không phải profitability.

**Interpretation.** Funding stock, throughput, gas/profitability và latency là các gate execution khác nhau.

**Limitation.** Một liquidator đại diện, vốn không tái sử dụng; không fork execution.

**Accepted Claim.** Kết luận Frozen v3 về vốn/delay giữ nguyên; addendum bổ sung rằng eligibility phải được đối chiếu quyết định execution.

**Status:** `ACCEPTED_WITH_LIMITATIONS`.

## RQ4 — Arbitrage và phục hồi giá.

**Question.** Arbitrage và phục hồi giá.

**Method.** Giữ Frozen v3 comparison immediate impact và residual spread; kiểm tra policy chỉ ảnh hưởng trades sau khi eligibility phân kỳ.

**Evidence.** `RQ4_IMMEDIATE_PRICE_IMPACT`, `RQ4_SPREAD_ARB0`, `RQ4_SPREAD_ARB100`.

**Result.** Immediate impact 0,108794% trong sweep gốc; residual spread giảm theo arbitrage capacity. Oracle diagnostic không thay đổi Uniswap math.

**Interpretation.** Arbitrage tái neo sau giao dịch trong mô hình; không xóa impact tại execution và không xác minh hiệu quả ngoài đời.

**Limitation.** Price repositioning/teleportation, một arbitrageur, không funded fork swap.

**Accepted Claim.** Kết luận Frozen v3 giữ nguyên; chỉ downstream liquidation trades có thể khác khi oracle policy làm eligibility khác.

**Status:** `ACCEPTED_WITH_LIMITATIONS`.

## RQ5 — Mất neo stablecoin và định giá nợ USDC.

**Question.** Mất neo stablecoin và định giá nợ USDC.

**Method.** Giữ token debt quantity và thay USDC/USD valuation 0,90–1,10 như Frozen v3.

**Evidence.** `RQ5_HF_LT1_USDC_090`, `RQ5_HF_LT1_USDC_100`, `RQ5_HF_LT1_USDC_110`, `RQ5_LIQUIDATED_DEBT_TOKEN_QTY`, `RQ5_LIQUIDATED_DEBT_USD`.

**Result.** HF<1 là 1/1/3; 9.063,255437 USDC = 9.969,580981 USD tại 1,10 USD/USDC.

**Interpretation.** Đây là kênh định giá nợ USDC, không phải full stablecoin-depeg market model.

**Limitation.** Không liquidity/redemption/settlement/confidence channel; oracle diagnostic WETH không mở rộng kết luận này.

**Accepted Claim.** Kết luận RQ5 Frozen v3 giữ nguyên với đơn vị USDC token và USD-equivalent tách biệt.

**Status:** `ACCEPTED_WITH_LIMITATIONS`.

## RQ6 — Đánh đổi LTV, liquidation threshold, liquidation bonus.

**Question.** Đánh đổi LTV, liquidation threshold, liquidation bonus.

**Method.** Giữ ba counterfactual tách biệt LTV, LT và bonus của Frozen v3.

**Evidence.** `RQ6_LTV0755_CAPACITY`, `RQ6_LTV0825_CAPACITY`, `RQ6_LT083_UNLIQUIDATED`, `RQ6_BONUS103_SEIZED`, `RQ6_BONUS107_SEIZED`.

**Result.** LTV đổi capacity ex ante; LT đổi HF/eligibility và scenario-LT unliquidated debt; bonus đổi collateral seized/incentive.

**Interpretation.** Ba tham số không thay thế nhau.

**Limitation.** Frozen cohort, không borrower re-underwriting/behavior response; oracle addendum không retune policy sweep.

**Accepted Claim.** Kết luận RQ6 Frozen v3 giữ nguyên.

**Status:** `ACCEPTED_WITH_LIMITATIONS`.


## 4. Claim traceability và tầng bằng chứng

- `CODE_OBSERVATION`: hành vi mã, không phải quan sát thị trường.
- `MODEL_COMPUTED_COUNTERFACTUAL`: kết quả mô phỏng A/B/C, không phải giao dịch lịch sử.
- `ONCHAIN_HISTORICAL_OBSERVATION`: log/receipt/association đã kiểm, không tự chứng minh nhân quả.
- `EXTERNAL_EMPIRICAL_INFERENCE`: chỉ được dùng khi thiết kế/dữ liệu bên ngoài thực sự hỗ trợ; hiện claim Aave dùng Uniswap spot và historical causal cascade là `UNSUPPORTED`.

Registry có 13 claims: {'ACCEPTED_WITH_LIMITATIONS': 9, 'REQUIRES_CORRECTION': 2, 'UNSUPPORTED': 2}. Hai diễn giải Frozen RQ1/RQ2 không có qualifier Policy A được gắn `REQUIRES_CORRECTION`; số liệu gốc không bị phủ định. Terra negative findings và network-extension limits giữ nguyên.

## 5. Self-audit

- 72/72 targeted replay hashes khớp Oracle Diagnostic.
- 32,688 borrower-case-policy rows đối chiếu; 32,688 HF traces khớp source rows.
- 2186 raw modeled event rows có event locator duy nhất.
- Result IDs/claim locators, sáu RQ, units, policy attribution, hashes và evidence tiers được gate tự động.
- Không raw wallet/API key, NaN/Infinity hoặc claim 2,8% là xác suất khủng hoảng.
- P2 locator được pin tại `8f5b635a316d72546b8a0eb0c2e8a66503b5d44f` nhưng delta oracle của Work theo comment `6166173420` vẫn là dependency mở.

- Trạng thái: `PASS`.
- `.\.venv\Scripts\python.exe scripts/research/build_scientific_integration_v1.py` → **PASS** (72/72 targeted replay hashes; 32,688/32,688 independently recomputed HF traces; 2,186 event rows; all integration gates passed).
- `.\.venv\Scripts\python.exe -m pytest tests/test_scientific_integration_v1.py tests/test_oracle_diagnostic_artifacts.py tests/test_frozen_v3.py -q` → **PASS** (15 tests passed).
- `.\.venv\Scripts\python.exe -m pytest -q` → **PASS** (180 tests passed; 3 dependency deprecation warnings).
- `.\.venv\Scripts\python.exe -m ruff check .` → **PASS** (All checks passed).
- `.\.venv\Scripts\python.exe -m mypy sim` → **PASS** (Success: no issues found in 49 source files; matches pyproject and CI scope).
- `.\.venv\Scripts\python.exe -m mypy .` → **OUT_OF_SCOPE_CONFIGURATION_FAILURE** (Duplicate legacy Terra pack module names outside configured mypy package scope; no integration source error evaluated by this invocation).

## 6. Giới hạn phải công bố

1. Policy A/B/C là counterfactual; không policy nào được xác minh là Aave/Chainlink lịch sử.
2. 280/10.000 là tần suất locked Severe Policy A, không dùng cho B/C hoặc Ethereum thực.
3. Mười MC paths được chọn vì depth≥2 dưới A; 10/0/0/2 không phải estimator quần thể.
4. Eligible, attempted và executed là ba gate khác nhau; execution vẫn do một liquidator đại diện.
5. Historical tiers 1/2/23/1 là route/co-occurrence/association, không causal contagion.
6. Fork validation vẫn `UNAVAILABLE`; haircut 90/95% chưa quan sát; một DEX/snapshot/cohort.
7. Terra không hỗ trợ claim dự báo ngoài mẫu thành công; network graph là heterogeneous aggregate extension.

## 7. Kết luận tích hợp

RQ3–RQ6 giữ nguyên kết luận Frozen v3 có giới hạn. RQ1–RQ2 phải dùng wording policy-conditional: thanh khoản quyết định DEX absorption/impact, còn việc biến distortion thành HF eligibility và Wave 2 phụ thuộc valuation policy. Addendum đủ điều kiện để Commander kiểm duyệt claim gate, nhưng P2 oracle reconciliation và quyết định scientific lock vẫn thuộc Commander.
