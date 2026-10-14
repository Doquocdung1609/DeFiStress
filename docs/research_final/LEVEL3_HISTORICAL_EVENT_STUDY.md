# Level-3 Historical Evidence Extension — Ethereum

Trạng thái: **LIMITED — REPORT WITH CAVEAT**  
Kế hoạch tiền đăng ký: `LEVEL3_VALIDATION_PLAN.md`  
Source commit khi bắt đầu: `423bcfd4ebf910ef73b94d9deaf7cf746d8ed71c`

## Phạm vi thực chứng

Khoảng quan sát đã khóa trước discovery là `2026-09-01T00:00:00Z` đến trước `2026-09-08T00:00:00Z`. The Graph được dùng để liệt kê candidate event; mỗi event công bố sau đó phải khớp Aave V3 Pool log, transaction receipt, block number, block hash và UTC timestamp qua Ethereum archive RPC. Cửa sổ này có 27 candidate và cả 27 đều được xác minh; không có event bị loại.

Nguồn ABI/deployment:

- Aave address-book release `4.73.5`, commit `6463b76862f4e2ea79764a02e0f1971c3fedb7fe`, Pool `0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2`.
- Aave `LiquidationCall` theo [IPool chính thức](https://github.com/aave/aave-v3-core/blob/master/contracts/interfaces/IPool.sol).
- Uniswap V3 `Swap` theo [IUniswapV3PoolEvents chính thức](https://github.com/Uniswap/v3-core/blob/main/contracts/interfaces/pool/IUniswapV3PoolEvents.sol).
- Bốn WETH/USDC pool fee tier 0.01%, 0.05%, 0.30% và 1.00% lấy từ canonical snapshot và được quét theo block-pinned logs.

Borrower và liquidator được pseudonym hóa. Contract address và public transaction hash được giữ vì cần kiểm toán giao dịch; chúng không được dùng làm nhãn danh tính borrower.

## Lỗi epoch được phát hiện và xử lý

Attempt đầu tiên dùng epoch lệch −10.800 giây so với UTC đã tiền đăng ký. Attempt 28-event đó được giữ riêng dưới `historical_invalid_epoch_attempt`, gắn `FAIL_INVALID_PRE_REGISTRATION_EPOCH` và bị loại khỏi mọi kết luận. Run đúng cửa sổ có 27 events. Swap rows có block/timestamp đã xác minh trong phần giao nhau được tái dùng qua cache; 27 liquidation được RPC xác minh lại. Đây là correction provenance, không phải đổi cửa sổ sau khi xem kết quả.

## Cụm lịch sử và episode selection

“Cụm” ở đây chỉ là nhóm event theo thời gian, không phải simulated wave. Số cụm thay đổi theo định nghĩa:

| Khoảng cách tối đa | Số cụm |
|---:|---:|
| 1 phút | 24 |
| 5 phút (chính) | 22 |
| 15 phút | 20 |
| 30 phút | 19 |

Graph `amountUSD/profitUSD` có dấu hiệu sai đơn vị trong deployment này, nên không dùng để xếp hạng volume. Theo fallback đã tiền đăng ký, 5 cụm đầu tiên theo thời gian được review sâu. Chúng gồm 6 liquidation events.

## Bằng chứng truyền dẫn

Trên toàn bộ 27 events:

| Tier | Số event | Diễn giải |
|---|---:|---|
| `DIRECT_TRANSACTION_LINK` | 3 | Receipt chứa cả Aave liquidation và Uniswap V3 Swap trong cùng transaction. |
| `SAME_BLOCK_ASSOCIATION` | 23 | Có WETH/USDC swap cùng block nhưng transaction khác; không chứng minh execution link. |
| `TIME_WINDOW_ASSOCIATION` | 1 | Swap gần nhất nằm trong ±30 phút; không cùng block/transaction. |
| `UNLINKED/UNOBSERVABLE` | 0 | Không có trong cửa sổ đã quét, nhưng điều này không nâng association thành causal evidence. |

Hai direct episodes đáng chú ý:

1. Transaction [`0xc546…1cfc`](https://etherscan.io/tx/0xc5463ffdc853db390912ccb6f9574a32bc0263af82217ce02e1c11f4dd1d1cfc), block 25,884,280, chứa hai `LiquidationCall` WETH collateral (DAI và USDT debt) và một WETH/USDC 0.01% `Swap` 0.4415196283 WETH trong cùng receipt.
2. Transaction [`0x1b8a…7271`](https://etherscan.io/tx/0x1b8a4a186c944b70e88fbb3572af6e56d992b0577def32da83e65782d6507271), block 25,884,317, trả 8,701.80131 USDC debt, thanh lý 3.8156824521 WETH và chứa WETH/USDC 0.01% swap đúng 3.8156824521 WETH cùng một swap phụ 0.1657785926 WETH. Đây là đường dẫn liquidation-collateral-to-DEX mạnh ở cấp transaction.

Direct transaction link chứng minh collateral liquidation đi qua DEX trong giao dịch đó; nó không tự chứng minh vòng lây lan nội sinh cấp hệ thống.

## Event/control mô tả

Số WETH/USDC `Swap` trong ±5 phút quanh 5 episode chọn so với control lệch trước 60 phút là:

| Episode | Event window | Control |
|---|---:|---:|
| cluster-001 | 154 | 200 |
| cluster-002 | 183 | 196 |
| cluster-003 | 355 | 191 |
| cluster-004 | 337 | 213 |
| cluster-005 | 256 | 203 |

Tổng mô tả là 1.285 so với 1.003 swaps, nhưng sample chỉ gồm 5 episode theo fallback thời gian, activity nền dày và không có inference model đủ để gọi chênh lệch này là causal effect. Hai direct episodes cũng trùng giai đoạn oracle WETH giảm: 2,411.0807 → 2,398.67 USD quanh cluster-003 và 2,398.67 → 2,382.92 USD quanh cluster-004. Market-wide ETH movement và oracle timing là confounders thực chất.

## So sánh với mô phỏng

- Lịch sử: event/cụm theo timestamp và receipt thật.
- Mô phỏng: wave mới chỉ khi forced sale làm borrower trước đó HF≥1 trở thành HF<1 ở valuation mới.
- Vì semantics khác nhau, 2–4 liquidation gần nhau trong lịch sử không được gọi là model cascade depth 2–4.
- Có bằng chứng direct cho kênh “liquidated WETH → Uniswap swap”, nhưng chưa có historical borrower census/same-block state đầy đủ để replay ex ante toàn bộ 454 borrower.

Kết luận bắt buộc: **Quan sát lịch sử có liên hệ theo thời gian, chưa chứng minh vòng lây lan nội sinh**.

## Giới hạn

- Một tuần tiền đăng ký, không phải full-population hay nhiều chế độ thị trường.
- The Graph là discovery index; coverage của index không phải census borrower.
- Control đơn giản chưa điều chỉnh volatility, gas, MEV, route ngoài bốn pool hoặc oracle lag.
- Không enumerate Chainlink `AnswerUpdated`; chỉ lấy Aave oracle state trước/event/sau bằng archive `eth_call`.
- Receipt đủ cho ba direct links; các event còn lại không được suy diễn từ same-block activity thành direct execution.

Machine-readable evidence nằm trong `data/processed/research_final/level3_extension/historical/`.
