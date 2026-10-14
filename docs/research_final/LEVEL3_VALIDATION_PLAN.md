# Kế hoạch tiền đăng ký Level-3

Trạng thái: `PRE-REGISTERED — BEFORE EVENT DISCOVERY`  
Thời điểm khóa kế hoạch: 2026-10-13 (Asia/Bangkok)  
Source commit: `423bcfd4ebf910ef73b94d9deaf7cf746d8ed71c`  
Chain: Ethereum Mainnet, chain ID 1  
Canonical snapshot bất biến: block `26045352`, SHA-256 `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99`

## Phạm vi và nguyên tắc khóa

Nghiên cứu mở rộng này không thay thế canonical, `corrected_run_v1` hoặc `corrected_run_v2`. Mọi đầu ra mới nằm trong `data/processed/research_final/level3_extension/`. Không sửa tham số để tạo thêm wave, không gọi liên hệ thời gian là quan hệ nhân quả và không dùng borrower hiện tại như census lịch sử.

## Thiết kế quan sát lịch sử đã tiền đăng ký

- Khoảng discovery: toàn bộ tuần UTC từ `2026-09-01T00:00:00Z` đến trước `2026-09-08T00:00:00Z`. Lý do chọn trước khi xem kết quả: đây là tuần trọn vẹn gần canonical nhưng đã hoàn tất, và probe Graph lịch sử tại 2026-09-01 từng có coverage trong audit trước.
- Population sự kiện: mọi `LiquidationCall` Aave V3 Ethereum Pool được index trong khoảng trên. Graph/indexer chỉ dùng để discovery; từng sự kiện được đưa vào evidence phải được đối chiếu log/receipt và block hash bằng RPC Mainnet read-only.
- Episode clustering chính: khoảng cách giữa hai liquidation liên tiếp không quá 5 phút. Sensitivity: 1, 15 và 30 phút. Đây là cụm thời gian lịch sử, không phải simulated wave.
- Episode chọn để kiểm tra sâu: tối đa 5 cụm, theo thứ tự xác định trước: cụm có tổng debt-to-cover lớn nhất trong mỗi strata thời gian đầu tuần/giữa tuần/cuối tuần, sau đó bổ sung cụm lớn nhất chưa chọn. Nếu không đủ dữ liệu/đơn vị so sánh, chọn 5 cụm đầu tiên theo `(timestamp, block, tx_index, log_index)` và ghi rõ lý do.
- Inclusion: log đúng Pool, topic ABI `LiquidationCall`, chain ID 1, block hash khớp receipt và không trùng `(tx_hash, log_index)`.
- Exclusion: log không giải mã được, block/receipt không khớp, ngoài cửa sổ, hoặc nguồn không cung cấp provenance đủ để RPC xác minh. Tất cả attempted/included/excluded đều được đếm.
- Uniswap matching: WETH/USDC pools chính thức ở các fee tier có event `Swap` trong cùng transaction/block hoặc cửa sổ ±1/5/15/30 phút. Không có match được giữ như kết quả âm.
- Tier bằng chứng: `DIRECT_TRANSACTION_LINK` chỉ khi receipt/trace hoặc ERC20 movement tạo đường dẫn giao dịch cụ thể; `SAME_BLOCK_ASSOCIATION`; `TIME_WINDOW_ASSOCIATION`; `UNLINKED/UNOBSERVABLE`.
- Control/placebo: cửa sổ cùng độ dài, cùng ngày trong tuần, lệch trước episode 60 phút và không chứa liquidation nếu dữ liệu cho phép. So sánh chỉ mô tả; market-wide ETH move, oracle lag và selection bias là confounders.
- Không tuyên bố full borrower backtest nếu historical candidate census không khả dụng.

## Thiết kế Level-2 fork

Chỉ chạy fork local ephemeral khi có `ETH_ARCHIVE_RPC_URL`, `forge` và `anvil`, cùng sample/funds lịch sử hợp lệ. Không broadcast. Baseline QuoterV2 `eth_call` không được gắn nhãn là counterfactual fork PASS. Thiếu điều kiện nào sẽ ghi `UNAVAILABLE` với prerequisite cụ thể.

## Stress surface đã tiền đăng ký

- Canonical cohort/state giữ nguyên.
- Wave caps: `12, 24, 48, 100`; horizon tương ứng tối thiểu `cap + max(delay, 20)` và mặc định `cap + 20`.
- Grid chính: shock ETH `[-5,-10,-15,-20,-25,-30,-35,-40,-45,-50]%` × haircut `[0,25,50,75,90,95]%`.
- Mechanism cases khóa trước: Professor/baseline, Moderate, Severe, Low Liquidity, No Arbitrage, Strong Arbitrage, capital binding 25%, capital nonbinding 200%, delay 5 steps. Haircut 90/95% là counterfactual tail.
- Báo cáo observed positive-liquidation waves; configured cap không được gọi là observed depth.
- Invariants: không borrower trùng qua wave, wave sau phải mới trở nên eligible ở prior-wave valuation, không double count, giá trị hữu hạn, không vượt schema.

## Monte Carlo đã tiền đăng ký

- Scenario chính: `Severe`, `max_waves=100`, horizon `120`, seed chính `20260914`.
- Stages: `200 → 1,000 → 5,000 → 10,000`, chỉ tiến cấp nếu checkpoint trước hợp lệ và runtime/disk ước tính nằm trong budget.
- Seed robustness: 1,000 path cho `20260914`, `20261014`, `20261114`.
- Scenario phụ nếu còn budget: `Low Liquidity` 1,000 path; không dùng kết quả để thay đổi scenario chính.
- Tần suất cascade báo Wilson 95% conditional on model/scenario. Loss cho ES95 giữ định nghĩa engine hiện tại: modeled uncovered debt + executed liquidated debt; không gọi realized loss.
- Checkpoint mỗi 200 path; resume không lặp path và lưu actual completed count.

## Budget và điều kiện dừng

- Offline simulation: tối đa 6 giờ wall-clock, 4 logical workers, peak RAM mục tiêu < 8 GiB, artifact mới mục tiêu < 500 MiB.
- RPC: read-only; tối đa 25.000 request, không mua quota; exponential backoff, cache theo request; không log URL/key.
- Mỗi command dài có timeout/checkpoint; không spin vô hạn. Dừng stage tăng cấp nếu ETA vượt budget, lỗi số học, thiếu disk/RAM hoặc nguồn mất tính xác minh; giữ checkpoint và ghi `INCOMPLETE`.
- Không cài binary không tin cậy hoặc công cụ trả phí. Foundry vắng mặt không chặn historical/offline stages.

## Population và claim boundary

- Snapshot: 500 Graph candidates, 454 RPC-verified borrowers có debt; WETH-collateral/USDC-debt cohort 109. Đây không phải market coverage.
- Historical events là giao dịch thật khi RPC xác minh; simulation là counterfactual model output.
- `DIRECT_TRANSACTION_LINK` có thể chứng minh đường giao dịch, không tự động chứng minh vòng lây lan thị trường.
- Mọi association thấp hơn direct tier dùng câu bắt buộc: “Quan sát lịch sử có liên hệ theo thời gian, chưa chứng minh vòng lây lan nội sinh”.

## Cổng quyết định

- Gate A: kế hoạch/cửa sổ/population khóa trước discovery; provenance đầy đủ.
- Gate B: episode được kiểm tra độc lập qua block/log/receipt và tiering nhất quán.
- Gate C: stress/MC hoàn tất trong budget, invariants và numerical diagnostics PASS.
- Gate D: claim ledger, bảng/hình và RQ1–RQ6 được reconcile mà không ghi đè evidence cũ.
- Gate E: chỉ Commander có quyền khóa khoa học; executor không tự tuyên bố evidence freeze.
