# TÓM TẮT ĐIỀU HÀNH

## Các phát hiện mạnh nhất

1. Historical Fit Terra đạt UST RMSE 0.1778 và tương quan 0.7601, nhưng sai số thời điểm tại ngưỡng 0,995 là -45 giờ (dấu âm nghĩa là mô phỏng sớm); do đó bằng chứng chỉ hỗ trợ tái dựng có điều kiện, không hỗ trợ claim dự báo chính xác.
2. Cảnh báo cutoff-safe High Risk cho ngưỡng 0,995 có lead time -45 giờ: cảnh báo xuất hiện sau depeg ban đầu. Với ngưỡng 0,90, lead time là 3 giờ.
3. Kiểm tra 277,342 native swaps hỗ trợ identity `swap_amount + fee_amount`; đây là nhất quán kế toán, không phải bằng chứng nhân quả giá.
4. Snapshot Aave REAL_MAINNET tại block 26,045,352 xác minh 454 borrower; cohort WETH/USDC là 109. Tỷ lệ xác minh ứng viên không được gọi là độ phủ thị trường.
5. Professor Demo tạo tổng nợ thanh lý 9063, nợ xấu 2213, cascade depth 1; Wave 2+ là 0. Đây là kết quả model-implied.
6. Monte Carlo Professor Demo có tần suất cascade 0, khoảng Wilson 95% [0, 0.01885]. Khoảng này chỉ mô tả lấy mẫu trong mô hình.

## Các hạn chế mạnh nhất

- Terra không có độ sâu DEX lịch sử canonical và không có kênh can thiệp LFG quan sát được.
- Dữ liệu bridge bị quarantine; giá tháng 3–4 có giai đoạn carry-forward tần suất thấp.
- Historical Fit sai thời điểm và cảnh báo cutoff-safe muộn đối với depeg ban đầu.
- Chuyển đổi phản thực Terra có sai số; preset Severe chạm numerical floors nên chỉ biểu diễn runaway regime.
- Aave dùng sample ứng viên, trọng tâm WETH/USDC và một venue Uniswap V3 được chọn; không phải toàn thị trường.
- Centrality được tính trên topology nhỏ; protocol tương lai chưa được ingest.
- Monte Carlo và mọi kết quả stress phụ thuộc cấu trúc mô hình, phân phối nhiễu và giả định kịch bản.

Mọi số liệu trên ánh xạ tới `results_registry.json`; các claim ánh xạ tới `claim_ledger.json` và `document_claim_index.json`.
