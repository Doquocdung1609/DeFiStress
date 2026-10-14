# Đối chiếu phiên bản P2 với P0 v2 và Level-3

**Ngày:** 14/10/2026. **PR:** [Draft #9](https://github.com/Doquocdung1609/DeFiStress/pull/9). **Trạng thái:** cập nhật delta cuối chờ Commander duyệt lại; không phải scientific lock hoặc quyết định merge.

Chỉ đạo áp dụng: [Commander follow-up ngày 14/10/2026](https://github.com/Doquocdung1609/DeFiStress/pull/9#issuecomment-6161682917). Nền học thuật 30 nguồn, 35 luận điểm, sáu RQ, 92 thuật ngữ và tám nguồn hàng chờ đã được chấp nhận có giới hạn; lần này chỉ cập nhật claim mã/thực nghiệm theo HEAD.

## 1. Phiên bản và phạm vi

| Vai trò | Định danh |
|---|---|
| Bộ P2 trước delta cuối | `9367674f84c47c388dceaea124bff2511b0a5c89` |
| Mốc Level-3 P2 đã đọc trước đó | `26cd58489d726a6c98678c725650020edcc1a3f4` |
| HEAD được đối chiếu lần này | `ba62c74950a72751e0030527836082da0c7622ef` |
| P0 corrected artifact | `data/processed/research_final/validation_audit/corrected_run_v2/`; bundle `672c840a15addd1c461bf502e432c09473467194` |
| Level-3 gốc | `data/processed/research_final/level3_extension/` |
| Gói sửa P1 có mục tiêu | `data/processed/research_final/level3_p1_targeted_repair/`; implementation `2dbc7d55`; artifact `6fcda469` |
| Model/canonical input | `0.1.0-aave-v3.10-metric-semantics`; block 26.045.352; snapshot SHA-256 `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99` |

Chỉ sửa năm tài liệu P2. Không sửa mã, dữ liệu, kịch bản, registry, Terra hay Word. P2 đọc artifact và kiểm tra nội dung; không tái thực thi RPC, fork hoặc batch Monte Carlo lớn.

## 2. Đối chiếu thay đổi 9367674 → HEAD ba62c749

| Hạng mục | Trước delta cuối | Nhận định hiện hành | Căn cứ/giới hạn |
|---|---|---|---|
| Census Aave | 27 Graph candidates khớp RPC; census còn pending | Census Pool trong tuần định nghĩa có 28 sự kiện; 27 Graph candidates đều RPC-match; Graph bỏ sót một sự kiện WETH/USDT ở block 25888740 | FIX `historical/census_reconciliation.json`; recall quan sát 27/28, không phải census borrower |
| Receipt route | Ba same-tx đều hạ thành co-occurrence | 1 `DIRECT_TRANSFER_PATH_VERIFIED`, 2 `SAME_TRANSACTION_CO_OCCURRENCE`, 23 cùng block, 1 theo thời gian | Exact WETH amount/order từ receipt; trace `UNAVAILABLE`; không chứng minh price causality |
| Control windows | Completeness/liquidation-free còn pending | 4 pool, 5 episode, half-width 1/5/15/30 phút, 40 tổ hợp, 928 chunks; 5/5 control ±30 phút không liquidation | FIX `historical/control_window_audit.json`; 31.489 swap chỉ thuộc selected windows |
| Checkpoint | 13k unique mới là reported accounting; repair pending | 13.000 định danh batch độc lập, 0 trùng; prefix 200/1k/5k lồng trong 10k; 10k reused, 0 large path chạy lại; 21/21 mẫu khớp | FIX checkpoint/reproduction; legacy duration `UNAVAILABLE_NOT_EMBEDDED_IN_LEGACY_CHECKPOINT`; external attestation được công bố |
| Vòng 2 tất định | Chủ yếu dùng audit 8/200 và một path mẫu | Ca −40%/haircut 90% có HF trực tiếp 1,0211716 và HF sau vòng 1 là 0,9980426 | FIX `wave2_eligibility_audit.json`; simulated eligibility |
| Vòng 2 phân tầng MC | Stratified audit còn pending | 10/10 first-depth2 samples theo 10 stratum có borrower mới mất an toàn | Direct-shock HF 1,00087518–1,00442738; prior-wave HF 0,99581457–0,99940096 |
| Tần suất/độ sâu | Severe 280/10.000 depth≥2; không depth≥3; 4/60 tail cells | Giữ nguyên; cap 100 chỉ là giới hạn cấu hình, max quan sát 2 | Tần suất có điều kiện; haircut 90/95% chưa quan sát |
| Uniswap V3 | Lỗi tick cũ đã được loại khỏi mô tả | Vẫn xác nhận cập nhật ±`liquidityNet`; giới hạn là price reset chưa phải funded swap có vốn/phí/đường thực thi | Không hồi sinh lỗi cũ |
| USDC/Terra/network | Các giới hạn đã công bố | Giữ nguyên kênh định giá nợ USDC; Terra là tái dựng/kiểm cơ chế/cảnh báo hồi cứu; graph là mạng dị thể gộp | Không full-depeg Aave, không OOS success, không formal multilayer contagion |
| NIST/APA | Wilson và adjusted Wald đã phân biệt; S17/S18 dedup | Giữ nguyên toàn bộ 30 nguồn, DOI/URL và access tag | Không thêm nguồn chưa xác minh |

## 3. Bảo toàn hồ sơ học thuật

- Sáu RQ giữ nguyên văn và nguyên phạm vi.
- 30 source records S01–S30, ngày truy cập, DOI/URL và mức truy cập giữ nguyên.
- U01–U08 vẫn mang nhãn `SOURCE_NOT_VERIFIED` tương ứng; không dùng cho claim chi tiết.
- Ma trận giữ 35 claim IDs và 12 alias E; alias E được cập nhật locator sang gói FIX khi cần.
- Danh mục giữ 92 thuật ngữ; chỉ sửa chú giải tier/checkpoint.
- S17 JFE và S18 NBER vẫn được tính là một nghiên cứu; S24 vẫn dùng đúng Wilson score interval theo phần Note của trang NIST.

## 4. Ranh giới khoa học còn phải đưa vào báo cáo

1. Một receipt-level WETH route xác minh dòng token trong giao dịch, chưa chứng minh thanh lý gây biến động giá hay tạo cascade lịch sử.
2. Census chỉ có ý nghĩa cho Pool address/topic và cửa sổ tuần đã định nghĩa; 27/28 là recall quan sát của Graph trong census này.
3. Severe 280/10.000 và 4/60 ô tail là kết quả có điều kiện của mô hình; haircut 90/95% là phản thực chưa quan sát.
4. External attestation được dùng cho checkpoint legacy; thời lượng chạy 10k lịch sử không có trong file cũ.
5. Arbitrage vẫn là thiết lập lại giá theo quy tắc, chưa phải chuỗi giao dịch có vốn, phí và route đầy đủ.
6. Aave depeg chỉ kiểm kênh định giá nợ USDC; unit conversion/redemption/liquidity chưa đầy đủ.
7. Một liquidator và một arbitrageur đại diện không mô tả cạnh tranh nhiều bot; composite exposure tail không phải realized loss hay market ES.
8. Đồ thị dị thể gộp và centrality không tự chứng minh mạng nhiều lớp hình thức hoặc lây lan nhân quả.
9. Terra chỉ hỗ trợ kiểm tra cơ chế, tái dựng lịch sử và đánh giá cảnh báo hồi cứu; không phải dự báo ngoài mẫu thành công.
10. Mainnet fork transaction vẫn `UNAVAILABLE`.

## 5. Phản biện độc lập

**Kết quả:** `PASS_P2_FINAL_VERSION_DELTA`, không còn lỗi chặn bàn giao. Tác tử `p2_independent_review` đã đọc đủ năm file, chỉ đạo Commander và sáu artifact kiểm toán tại HEAD `ba62c749`. Review xác nhận các số census/tier/control/checkpoint/HF; đồng thời kiểm 30 nguồn, U01–U08 và nhãn truy cập, sáu RQ byte-identical, 35 claim IDs và 92 thuật ngữ. Một câu cũ phủ nhận toàn bộ collateral flow đã được sửa: tài liệu nay ghi đúng một tuyến WETH theo biên nhận giao dịch, đồng thời giữ giới hạn chưa xác lập tác động giá nhân quả hoặc lây lan lịch sử. Sign-off chỉ duyệt tính nhất quán tài liệu P2; không thay Commander scientific approval, không xác nhận mã toàn diện và không cho phép merge.

## 6. Bàn giao

Bộ P2 đã hoàn tất phản biện độc lập và sẵn sàng cho Commander re-review ở trạng thái draft. Issue #4 giữ open; không merge, không tuyên bố scientific lock và không tạo Word final.
