# BRIEF THUYẾT TRÌNH 10–12 PHÚT

## 1. Vấn đề

- Mục đích: DeFi có vòng phản hồi; mục tiêu là đo stress có provenance.
- Màn hình/hình: C01
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Từ vấn đề, chuyển sang thiết kế hai ca.

## 2. Thiết kế

- Mục đích: Terra là historical validation; Aave là Mainnet stress.
- Màn hình/hình: C01
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Hai ca bổ sung nhưng không xác thực lẫn nhau.

## 3. Dữ liệu

- Mục đích: 1,776 giờ Terra; 454 borrower Aave.
- Màn hình/hình: T01 + A01
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Tiếp theo là cơ chế Aave.

## 4. Vòng Aave

- Mục đích: shock → HF → liquidation → DEX → repricing.
- Màn hình/hình: A12
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Cơ chế này được chạy trên snapshot cùng block.

## 5. Terra lịch sử

- Mục đích: Quan sát collapse nhưng không gọi fit là forecast.
- Màn hình/hình: T01
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Đầu tiên kiểm tra mechanism.

## 6. Mechanism

- Mục đích: 277,342 swaps; accounting consistency.
- Màn hình/hình: T11
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Sau đó đánh giá Historical Fit.

## 7. Historical Fit

- Mục đích: UST RMSE 0.1778; timing sớm.
- Màn hình/hình: T05
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Fit tốt về hướng chưa đủ cho cảnh báo.

## 8. Early Warning

- Mục đích: Initial depeg lead -45 giờ.
- Màn hình/hình: T09
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Chuyển sang stress Aave.

## 9. Aave stress

- Mục đích: Professor liquidated 9063.
- Màn hình/hình: A04
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Thanh khoản quyết định vòng khuếch đại.

## 10. Contagion graph

- Mục đích: Aave là bridge trong sub-network nhỏ.
- Màn hình/hình: A12–A16
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Độ bền cần MC và sensitivity.

## 11. MC/sensitivity

- Mục đích: Cascade frequency 0 model-implied.
- Màn hình/hình: A09 + A11
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Tổng hợp phát hiện.

## 12. Phát hiện

- Mục đích: Phản hồi nội sinh là điểm chung hợp lệ.
- Màn hình/hình: C01
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Nhưng boundary là bắt buộc.

## 13. Hạn chế

- Mục đích: Availability, sample, venue, topology, model dependence.
- Màn hình/hình: Table_14
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Kết luận ở mức phòng thủ được.

## 14. Kết luận

- Mục đích: Evidence-first, reproducible, giữ kết quả âm.
- Màn hình/hình: C01
- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.
- Chuyển ý: Mời hội đồng đặt câu hỏi.
