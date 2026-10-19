# Phase 02 — dependencies, risks và điều kiện nghiệm thu đề xuất

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED**

Đây là readiness plan, không triển khai Phase02. Baseline `cbcf8c451c9f2c83a2f07ae483ba6c3a25ecd815`; kế thừa [V2 blueprint Phase00](https://github.com/Doquocdung1609/DeFiStress/blob/cbcf8c451c9f2c83a2f07ae483ba6c3a25ecd815/docs/research_v2/phase00/V2_RESEARCH_UPGRADE_BLUEPRINT.md). U01–U08 là upgrade workstreams hiện có, không phải tám RQ mới. Six-RQ wording lấy từ Final Accepted Claims Registry v1.1 trong source catalog; không đổi V1 claims/results.

## Dependencies và rủi ro theo workstream

| Workstream / phạm vi | Đã có và gap thực sự | Prerequisite / risk | Minimal future test design và acceptance | Disposition hiện tại |
|---|---|---|---|---|
| U01 Multi-snapshot/pool | 3 blocks, 2 fee tiers cùng cặp, registered bands; 24 recent-Borrow accounts. Không phải thị trường/khủng hoảng mẫu rộng | Đăng ký selection/coverage mới; mọi historical dependency phải cùng block; Gate A cho inputs dùng ở historical engine scope | Wrong hash/chain/decimals/missing fixture phải bị reject; đủ required band, deterministic content; 0 silent fill/leakage; retained incomplete cases. Không đòi stress dương | Design ready; expanded empirical use chưa ready |
| U02 Historical oracle | USDC/WETH6 deep traces, all-reserve source pointers; chưa heartbeat protocol/full price timeline hoặc backend attestation | Source/version/adapter/available-time fidelity; freshness theo nguồn đăng ký trước. DEX spot và V1 A/B/C tách actual oracle | Negative wrong source/round/future timestamp; adapter unsupported round giữ unavailable; 0 price substitution. No freshness PASS khi chưa threshold | B core không đủ execution use |
| U03 Liquidation execution | Portfolio HF comparison có, transaction receipts chưa có | Gate A, historical protocol implementation/version, collateral/debt route, allowance, rounding/close-factor/bonus/fees; local-fork funding assumptions và no-broadcast boundary | Local-fork positive/revert/zero-route-debt/insufficient funds/allowance/rounding; phân biệt newly eligible→evaluated→attempted→executed với positive debt repaid, skipped/reverted reason; 0 unexplained receipt/model mismatch, conservation và locators đầy đủ | Phase02 chưa được phép; execution gate OPEN |
| U04 Multiple liquidators/capital | V1 agents đại diện, capital không recycle và không tự split oversized plan; chưa multiagent executable budget ledger | U03 + registered scheduling, budgets, gas/latency, splitting/recycling là cơ chế riêng; không tự coi V1 hạn chế là bug | Synthetic controls no overspend/no double execute, delay/capacity0, competing bids; future receipts/ledger trước/sau;0 unexplained balance/gas discrepancy | Pure fixture design có thể đề nghị L2; integrated execution NO-GO |
| U05 Executable arbitrage | V1 price repositioning chưa funded swap | U01/U02/U03; token funding, route liquidity bands, fees/gas/slippage, quote/receipt semantics | No-arb/no-profitable-route/insufficient funding/price-band breach; reconciliation inputs/outputs/net profit cùng đơn vị,0 unexplained conservation failure. Không yêu cầu lợi nhuận dương | Funding/execution validation OPEN |
| U06 Dynamic network | Structural network evidence không phải validated multilayer propagation | U03–U05 ledgers, typed directed edges, units/time, transition rules; source completeness | No-edge/no-shock/no-sale/reference-only controls; mỗi propagation edge có locator,0 double-counted losses; model intervention effect tách historical causal claim | Phase03 future; không triển khai trong Phase02 readiness task |
| U07 Terra EW V2 | V1 cutoff-safe early-warning negative evidence được giữ | Dataset/vintage/availability riêng, sealed OOS splits và thresholds trước evaluation; không phụ thuộc Aave outcome dương | Leakage/purge checks, naive baselines, equal horizon/information set, misses/false alarms/lead time có denominators;0 cutoff violation; không chọn lại threshold theo holdout | Phase04 riêng; Gate B Aave không validate Terra |
| U08 OOS / independent validation | Ingestion CI và core agreement chưa là independent scientific replication | Sealed holdouts/cross-market sources, independent reference implementation và reviewer role nếu có; Gate A theo historical inputs liên quan | Wrong-units/schema/negative controls; holdout integrity, failed/unavailable disposition,0 unsupported generalization; no test-set tuning. Software independence khác backend independence | Phase05/publication chưa ready |

Các tiêu chí trên là điều kiện thiết kế cho công việc được phép sau này; chưa được chạy trong Issue33 và không phải test results mới. PASS nghĩa là thiết kế/quan sát hợp lệ, không buộc cascade, profit hoặc forecasting success xuất hiện.

## Sáu RQ và dependencies

Giữ nguyên văn câu hỏi V1 dưới đây để theo dõi dependency; Phase02 không tự cấp câu trả lời V2 hoặc thay kết luận V1.

### RQ1

> Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)?

**Dependencies:** U01/U02/U03; U04 khi xét competition. State coverage + actual-oracle timeline/policy specification + eligibility/execution ledger. So sánh reference-only/no-sale/zero-shock và noncascade controls; chưa suy universal threshold.

**Gate:** A và coverage trước historical engine; execution validation trước executed-wave finding; causal Mainnet claim cần identification riêng.

### RQ2

> Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt?

**Dependencies:** U01/U02/U05. Tách DEX absorption khỏi valuation transmission; complete required tick band, active L, fee/decimals và no-sale/reference-only controls. Haircut là scenario assumption.

**Gate:** A + band/use-specific coverage; swap validation trước executable price-impact claim. Không lấy toàn pool L làm active L.

### RQ3

> Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý?

**Dependencies:** U03/U04. HF tính portfolio, route có debt/collateral, planning/evaluation, attempted/executed/skipped/reverted được log riêng; budgets/latency/gas/scheduling định trước.

**Gate:** A + receipt validation + budgets; debt quantity và valuation tách đơn vị. HF-match không chứng minh liquidation khả thi.

### RQ4

> Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi?

**Dependencies:** U01/U02/U05. Funded route, fees/gas, residual price và recovery time theo clock đã định; no-arb/insufficient-funding controls.

**Gate:** A + executable-swap receipts và conservation. Price reset không thay funded on-chain arbitrage.

### RQ5

> Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset?

**Dependencies:** U01/U02/U03/U05; không phải U07. Debt token quantity, USD-equivalent valuation, oracle price, settlement/funding/collateral semantics tách riêng; paired no-depeg control.

**Gate:** A + actual source/units và settlement execution nếu kết luận về execution. Aave stablecoin scenario không phải Terra forecast.

### RQ6

> Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk?

**Dependencies:** U01/U02/U03/U04. LTV quyết định borrowing capacity; LT tác động HF/eligibility; bonus tác động incentive/repayment/collateral transfer. Giữ cohort/units của từng thí nghiệm; V1 LTV255 portfolios khác109 WETH/USDC; V1 LT là USD portfolio-debt valuation tại USDC/USD=1.

**Gate:** A + configuration fidelity; execution validation khi nói incentive/execution. Không gán109 vào LT nếu chưa chứng minh, không gọi USD valuation là số USDC tokens.

## Trình tự tối thiểu được đề xuất, chưa cấp quyền

| Bước | Deliverable / kiểm soát | GO để thiết kế | Điều kiện để chạy / báo cáo |
|---|---|---|---|
| Scope decision | Commander chọn L1/L2 hoặc tiếp tục attestation, ghi rõ inputs/output claim class | Hồ sơ Issue33 có thể review ngay | Một lệnh riêng; hiện tại `PHASE02_NOT_AUTHORIZED` |
| Input readiness | Registration/versioned manifest, field/band/cohort completeness, quarantine, timestamp/units, backend evidence | Dùng saved evidence để thiết kế | Không mở historical engine với gaps hiện tại; A và use-specific requirements phải có disposition |
| Execution protocol | Historical version mapping, local-fork receipt plan, synthetic fixtures và budget/route invariants | Chỉ specs hiện tại; pure code fixtures cần lệnh L2 riêng | U03–U05 receipt/balance tests đủ disposition; không broadcast Mainnet |
| Engine experimental run | Registered policies/seeds/controls và V1 controls immutable | Sau input/execution specs | Lệnh Phase02 + cổng tương ứng; không Monte Carlo trong Issue33 |
| Scientific interpretation | Result namespaceV2, denominators/units/cohorts, negative findings, validation report | Có thể thiết kế reporting contract | Technical PASS không tự cấp scientific/publication lock; review riêng |

## Rủi ro và stop rules chung

**Common backend / correlated software:** mức độ chưa định lượng; không giảm rủi ro bằng cách đếm các repeated fields thành independent samples. Residual risk được giữ ngay cả khi values bằng nhau. **Reference-time asymmetry:** historical immutable block hash cho phép comparison nhưng không chứng minh cùng thời điểm phục vụ hoặc routing độc lập. **Coverage leakage:** core-only crosscheck không truyền nhãn cross-provider PASS sang ticks, HF vectors hoặc round chains. **Retention:** summary/index không đủ full offline Alchemy replay; future sanitized per-field capture cần policy riêng, không đụng secret.

Sai chain/hash/ABI hoặc integrity/leakage: dừng affected pack, không công bố outputs phụ thuộc. Missing/access: BLOCKED, giữ quarantine và reasons. Model negative/null result với inputs hợp lệ: báo kết quả, không tự retune để đạt PASS. Không đủ spec để đo invariant: NO-GO cho claim tương ứng, không thêm số liệu giả. Mọi revised gate phải do Commander ban hành; strict Gate A giữ nguyên lịch sử.
