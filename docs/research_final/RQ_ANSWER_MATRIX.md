# Ma trận trả lời sáu câu hỏi nghiên cứu — Frozen v3

Trạng thái: **P1_NUMERICAL_READY — AWAITING_P2_CITATION_RECONCILIATION**

Nguồn định lượng ưu tiên: Original → P0 corrected v2 → Level-3 → Level-3 targeted repair → Frozen v3.

## RQ1 — Ngưỡng và điều kiện xuất hiện thanh lý dây chuyền là gì?

**Phương pháp.** Đối chiếu lưới P0 32 ô với lưới mở rộng 60 ô và checkpoint Severe 10.000 đường.

**Dữ liệu.** Snapshot block 26.045.352; 454 borrower xác minh; cohort 109; state Aave/Uniswap cùng block.

**Thí nghiệm.** Shock −5%…−50%, haircut tới 95%, cap tới 100 wave và horizon tới 120 step; không ép Wave 2.

**Kết quả.** Lưới 32 ô: 12 depth 0, 20 depth 1, không depth 2. Lưới 60 ô: 18/38/4 ở depth 0/1/2. Severe: 280/10.000 depth ≥2; 0 depth ≥3.

**Giải thích.** Wave 2 chỉ xuất hiện trong tail liquidity assumptions; kiểm toán trực tiếp xác nhận borrower Wave 2 mới đủ điều kiện sau wave trước.

**Giới hạn.** Haircut 90/95% chưa có độ sâu Mainnet lịch sử; frequency mô hình không phải xác suất thực.

**Kết luận.** Có bằng chứng model-conditional cho depth 2, chưa có bằng chứng cho depth ≥3 hoặc ngưỡng phổ quát.

**Trạng thái:** `LIMITED — REPORT WITH CAVEAT`; claim ID: `CL_RQ1`.

## RQ2 — Thanh khoản thị trường ảnh hưởng cascade như thế nào?

**Phương pháp.** So sánh executable depth và shock×haircut, đọc lượng WETH bán, price impact, residual spread và wave depth.

**Dữ liệu.** Uniswap V3 WETH/USDC 0,3% tại cùng snapshot block; depth 2% khoảng 1,668 triệu USDC.

**Thí nghiệm.** Haircut 0–95%; shock −5%…−50%; các cell khác giữ theo grid đã khai báo.

**Kết quả.** Bốn cell depth 2 đều ở haircut 90/95%; haircut làm giảm sức hấp thụ giao dịch và tăng biến dạng giá trong tail.

**Giải thích.** Thanh khoản là bộ đệm hấp thụ forced sale; suy giảm depth có thể tạo eligibility mới ở wave sau.

**Giới hạn.** Một pool, liquidity tĩnh/counterfactual; không có routing đa venue.

**Kết luận.** Thanh khoản quyết định mức khuếch đại trong mô hình nhưng tail thresholds chưa được xác nhận lịch sử.

**Trạng thái:** `LIMITED — REPORT WITH CAVEAT`; claim ID: `CL_RQ2`.

## RQ3 — Chi phí và giới hạn năng lực người thanh lý đóng vai trò gì?

**Phương pháp.** Tách sweeps vốn, capacity/gas và reaction delay.

**Dữ liệu.** Cohort 109 vị thế trên snapshot cố định; nhu cầu vốn tham chiếu 9.063,255437 USDC.

**Thí nghiệm.** Vốn 25/50/100/200%; delay 0/1/2/4 step; các sweep capacity/gas hiện có.

**Kết quả.** 25/50% vốn chặn execution; 100/200% cho cùng 9.063,255437 USDC thanh lý. Delay không đổi severity trong range.

**Giải thích.** Funding stock, throughput và latency là ba ràng buộc khác nhau; time-to-position-processing không phải time-to-recovery.

**Giới hạn.** Capital cộng dồn không tái sử dụng; execution agent đơn giản.

**Kết luận.** Vốn binding trong miền thấp; bằng chứng cho delay/gas/capacity còn âm hoặc không binding trong miền thử.

**Trạng thái:** `LIMITED — REPORT WITH CAVEAT`; claim ID: `CL_RQ3`.

## RQ4 — Arbitrage có ổn định giá sau forced sale không?

**Phương pháp.** So sánh immediate liquidation price impact với post-arbitrage residual spread ở capacity 0/50/100%.

**Dữ liệu.** Kịch bản −20%, haircut 40%, cùng lượng forced sale 4,408546 WETH.

**Thí nghiệm.** Thay đổi duy nhất năng lực arbitrage.

**Kết quả.** Immediate impact giữ ở 0,108794%; residual spread giảm từ 0,108794% (0%) xuống 0,054397% (50%) và xấp xỉ 0 (100%).

**Giải thích.** Agent arbitrage tái neo giá sau bán, không xóa impact phát sinh tại thời điểm execution.

**Giới hạn.** Không có competition, latency thực, gas strategy hoặc fork SwapRouter execution.

**Kết luận.** Ổn định hậu arbitrage được hỗ trợ trong mô hình; không phải bằng chứng hiệu quả arbitrage ngoài đời.

**Trạng thái:** `LIMITED — REPORT WITH CAVEAT`; claim ID: `CL_RQ4`.

## RQ5 — Mất neo USDC tác động thế nào khi USDC là debt asset?

**Phương pháp.** Giữ token debt quantity, định giá USDC từ 0,90 đến 1,10 USD và tính lại HF/liquidation metrics.

**Dữ liệu.** 109 vị thế WETH collateral + USDC debt.

**Thí nghiệm.** Debt-valuation channel only; không thêm liquidity/redemption/settlement.

**Kết quả.** Số HF<1 là 1/1/3 tại USDC 0,90/1,00/1,10. 9.063,255437 USDC token tương đương 9.969,580981 USD tại giá 1,10.

**Giải thích.** USDC tăng giá làm nghĩa vụ nợ USD lớn hơn; giảm giá làm nghĩa vụ USD nhỏ hơn trong kênh cô lập này.

**Giới hạn.** Không mô hình hóa khả năng thanh toán, thanh khoản hay confidence của stablecoin.

**Kết luận.** Chỉ kết luận về kênh định giá nợ, không về toàn bộ cơ chế depeg.

**Trạng thái:** `LIMITED — REPORT WITH CAVEAT`; claim ID: `CL_RQ5`.

## RQ6 — Đánh đổi giữa LTV, liquidation threshold và liquidation bonus là gì?

**Phương pháp.** Ba counterfactual tách biệt: LTV capacity, LT HF boundary, bonus execution economics.

**Dữ liệu.** Frozen cohort 109 vị thế; other-collateral parameters được giữ riêng.

**Thí nghiệm.** LTV 75,5–82,5%; LT 81–88%; bonus 3–7%.

**Kết quả.** Tăng LTV làm capacity tổng tăng 50,798 lên 53,676 triệu USD; LT đổi eligibility/unliquidated debt theo scenario; bonus 3→7% làm WETH seized tăng 4,324574→4,492519.

**Giải thích.** LTV là ràng buộc cấp tín dụng ex ante; LT là trigger solvency; bonus là incentive/transfer khi execution.

**Giới hạn.** Không có phản ứng tái underwrite hay hành vi borrower sau policy change.

**Kết luận.** Ba tham số không thể dùng thay thế nhau; mỗi tham số tạo một trade-off khác.

**Trạng thái:** `LIMITED — REPORT WITH CAVEAT`; claim ID: `CL_RQ6`.

## Phần mở rộng không thay thế sáu RQ

Terra 2022 là kiểm chứng lịch sử mở rộng và giữ kết quả âm về early warning. Mạng lưới nhiều lớp là phân tích truyền dẫn mở rộng; centrality trong sub-network không đại diện tầm quan trọng toàn DeFi.
