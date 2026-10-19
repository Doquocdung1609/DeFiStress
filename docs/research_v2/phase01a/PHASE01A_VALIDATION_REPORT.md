# Phase 01-A — Validation report

**Status:** `V2_PHASE01A_READY_FOR_COMMANDER_REVIEW`. Đây là nghiệm thu hồ sơ pilot, không phải scientific lock V2.

## Nguồn thực sự đã chạy

State ingestion commit `85d35785ce759598bff8282e9c3619c49d22d9f9`, [run 39149158699](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39149158699); artifact `phase01a-pilot-39149158699` ID `12144313692`, ZIP SHA-256 `cc3686a6380ee66b0e96d0f1ca8ca43852e5c51ea7e6b5b48c7fabb43e35f1ae`. Work tải toàn ZIP, kiểm tra digest/CRC và từng file theo collection manifest. Header discovery run39148862610 và đăng ký hash có trước state ingestion.

| Block ID | Number | Registered hash |
|---|---:|---|
| B0 | 26045352 | `0x4dffe3bdf7bbaf24fd1e3b6c3f4795687dccfd3189cbfb61f4dbaf926722220a` |
| B1 | 26038152 | `0xbb108203815f257e9f9b023f92a30e67d946799355ceffc4bef0e0e16a1e87bd` |
| B2 | 26030952 | `0xeeb12db7f31e86507bb4be7a1a2953d19c11165c99a75ebc7aa589d65d0b9625` |

Hai pool chain1: P3000 `0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8`, fee3000 millionths = 0,30%; P500 `0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640`, fee500 millionths = 0,05%. Token ordering USDC/WETH; decimals6/18 là expected values được so với historical contract calls, không lấy giá DEX thay oracle.

## Kết quả theo endpoint/block

| Endpoint | Block | Two-pass deterministic content check | Component status |
|---|---:|---|---|
| publicnode | 26045352 | NOT_EVALUABLE_INCOMPLETE | P3000: QUARANTINED, P500: QUARANTINED, aave: QUARANTINED, liquidation_logs: AVAILABLE, swap_logs_P3000: AVAILABLE, swap_logs_P500: AVAILABLE |
| publicnode | 26038152 | NOT_EVALUABLE_INCOMPLETE | P3000: QUARANTINED, P500: QUARANTINED, aave: QUARANTINED, liquidation_logs: AVAILABLE, swap_logs_P3000: AVAILABLE, swap_logs_P500: AVAILABLE |
| publicnode | 26030952 | NOT_EVALUABLE_INCOMPLETE | P3000: QUARANTINED, P500: QUARANTINED, aave: QUARANTINED, liquidation_logs: AVAILABLE, swap_logs_P3000: AVAILABLE, swap_logs_P500: AVAILABLE |
| drpc | 26045352 | PASS | P3000: AVAILABLE, P500: AVAILABLE, aave: AVAILABLE, liquidation_logs: AVAILABLE, swap_logs_P3000: AVAILABLE, swap_logs_P500: AVAILABLE |
| drpc | 26038152 | PASS | P3000: AVAILABLE, P500: AVAILABLE, aave: AVAILABLE, liquidation_logs: AVAILABLE, swap_logs_P3000: AVAILABLE, swap_logs_P500: AVAILABLE |
| drpc | 26030952 | PASS | P3000: AVAILABLE, P500: AVAILABLE, aave: AVAILABLE, liquidation_logs: AVAILABLE, swap_logs_P3000: AVAILABLE, swap_logs_P500: AVAILABLE |

**3/6 provider–block rows** đạt full scoped two-pass repeatability; **1** endpoint có ít nhất một row đầy đủ. **18** component quarantine. Một row chứa cả hai pool, Aave và ba nhóm log; không phải một borrower hay một pool duy nhất. Cross-endpoint comparisons nằm trong JSON provenance; sự đồng thuận hai endpoint không thay kiểm chứng đồng thuận Ethereum.

## Kiểm thử và cấp bằng chứng

| Kiểm tra | Kết quả / phạm vi |
|---|---|
| Pure integrity unit tests | **21 PASS / 0 FAIL / 0 ERROR / 0 SKIP** trên runner; local stdlib run cũng21 PASS. Fixtures chỉ kiểm tra guard/logic, không giả làm dữ liệu Mainnet |
| Chain / number / hash | Header discovery có3/3 hashes trùng giữa hai endpoint; header đầu/cuối và chain được kiểm tra lại trong từng sweep |
| Factory / token / fee / decimals / spacing | Khi component pool AVAILABLE, historical factory identity và contract metadata đều qua validator; xem từng snapshot và raw request |
| Historical oracle link | Pool → AddressesProvider → PriceOracle/DataProvider tại block; source address, BASE_CURRENCY_UNIT và effective price. Không chứng nhận underlying aggregator round history |
| Repeated snapshot | Chỉ PASS nếu hai content hashes trùng và mọi component AVAILABLE; hai lần cùng thiếu luôn NOT_EVALUABLE |
| Timestamp/block leakage | State calls dùng EIP-1898 hash; logs dùng blockHash; không latest fallback; reserve update timestamp không vượt timestamp block |
| Missing data | Component lỗi là QUARANTINED/null và giữ reason. Empty logs chỉ khi RPC thực trả [] |

Không gọi một job xanh là toàn bộ dữ liệu PASS: catalog/quarantine mới là kết quả data availability. **PublicNode: header/log khả dụng, historical state DATA_ACCESS_BLOCKED** do RPC code4444 `pruned history unavailable`;18 quarantine records là3 state components ×3 blocks ×2 passes. dRPC:3/3 blocks với cả hai pool, Aave và logs AVAILABLE; six block–pool combinations được quan sát đủ hai pass. Không ghép state dRPC vào các snapshot PublicNode bị thiếu. Underlying borrower/reserve calls của PublicNode không được thực hiện tiếp sau lỗi upstream; không gọi đó là quan sát giá trị0.

Các lỗi workflow YAML ban đầu và một Ruff SIM117 ở test mới được sửa tại nhánh V2, giữ trong lịch sử. SIM117 chỉ đổi cách ghép context manager, không đổi assertion. CI trên collection commit có247 pytest PASS nhưng workflow tổng failure vì Ruff; CI final delivery được kiểm tra riêng trong PR handoff, không chuyển failure đó thành SUCCESS bằng diễn giải. Không thay CI/scientific sources V1 để che lỗi.

## Giới hạn và Phase 01-B

Mẫu tối thiểu3 block ×2 pool đã có dữ liệu đầy đủ và two-pass hashes qua dRPC. Đề nghị Commander nghiệm thu nền tảng pilot, quyết định riêng Phase 01-B; trước khi dùng như bộ dữ liệu nghiên cứu mở rộng cần archival coverage ổn định và đối chứng state từ nguồn độc lập. PublicNode state vẫn DATA_ACCESS_BLOCKED, không phải PASS. Dù pilot đạt, trước khi mở rộng cần khóa thêm thời điểm/thị trường và borrower discovery không chịu survivor bias; quy định full tick range, trace proxy/adapter và underlying oracle rounds; có archival access được xác nhận cho toàn kỳ nghiên cứu; xác định kiểm chứng độc lập và ngân sách dữ liệu. Không bắt đầu các việc đó trong Phase 01-A.

Tick evidence chỉ là slot0/active liquidity + một bitmap word và tối đa8 initialized ticks gần current tick; không suy executable depth hoặc full pool reconstruction. Ba địa chỉ V1 chỉ là availability sentinels. Log window chỉ ba exact blocks. Không có transaction execution, stress, Monte Carlo hoặc kết luận contagion. V1 tag và toàn bộ scientific artifacts được bảo toàn.
