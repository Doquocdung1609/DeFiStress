# KẾT QUẢ VÀ THẢO LUẬN

## 5.1 Độ tin cậy dữ liệu — Table_01, Table_02; T01, A01

Terra và Aave được đóng băng bằng hash. Aave có 500 ứng viên và 454 borrower xác minh, tương ứng tỷ lệ ứng viên 0.908; đây không phải độ phủ thị trường. Terra giữ missingness theo availability thay vì điền unavailable thành zero.

## 5.2 Cơ chế Terra — Table_12; T11

277,342 event hỗ trợ identity gross mint trực tiếp. Tương quan theo giờ là 1 và sai số tích lũy tương đối 0.01065. Kết quả là accounting consistency, không phải price causality.

## 5.3 Historical Fit Terra — Table_10; T05–T07

1. Historical Fit Terra đạt UST RMSE 0.1778 và tương quan 0.7601, nhưng sai số thời điểm tại ngưỡng 0,995 là -45 giờ (dấu âm nghĩa là mô phỏng sớm); do đó bằng chứng chỉ hỗ trợ tái dựng có điều kiện, không hỗ trợ claim dự báo chính xác.

## 5.4 Early Warning — Table_11; T08–T09

2. Cảnh báo cutoff-safe High Risk cho ngưỡng 0,995 có lead time -45 giờ: cảnh báo xuất hiện sau depeg ban đầu. Với ngưỡng 0,90, lead time là 3 giờ.

## 5.5 Stress phản thực Terra — Table_13; T10

Baseline có 0 đường chạm điều kiện collapse; Severe có 100. Cách viết đúng là số đường mô phỏng đạt điều kiện, không phải xác suất crash thực tế. Severe chạm floor biểu diễn runaway regime, không phải dự báo tail chính xác.

## 5.6 Vulnerability Aave Mainnet — Table_02–Table_04; A01–A03

Snapshot block 26,045,352 có cohort WETH/USDC 109. Sai khác HF lớn nhất được giữ ở mức 0.6031; cờ mismatch không bị che hoặc loại borrower thủ công.

## 5.7 Cascade lending–DEX — Table_04; A04–A08

Professor Demo có Wave 1 9063 và Wave 2+ 0. Nếu Wave 2+ bằng zero, kết luận là **NO ENDOGENOUS SECOND WAVE**.

## 5.8 Thanh khoản như kênh khuếch đại — Table_05, Table_07; A07–A08

Grid rời rạc đánh giá shock từ −5% đến −40% và haircut 0/25/50/75%. Chỉ báo ngưỡng không được nội suy ngoài các cell thử.

## 5.9 Arbitrage như cơ chế ổn định — Table_05; A11

Sweep arbitrage so sánh capacity trong khi giữ các giả định khác. Đây là phản ứng mô hình, không chứng minh arbitrage quan sát được đã gây ổn định lịch sử.

## 5.10 Monte Carlo tail behavior — Table_06; A09–A10

6. Monte Carlo Professor Demo có tần suất cascade 0, khoảng Wilson 95% [0, 0.01885]. Khoảng này chỉ mô tả lấy mẫu trong mô hình.

## 5.11 Mạng contagion đa lớp — Table_08–Table_09; A12–A16

Aave có vai trò cầu nối cấu trúc giữa exposure và execution venue trong topology đã mô hình hóa. Centrality không phải “tầm quan trọng hệ thống toàn DeFi”; score ma trận không phải xác suất.

## 5.12 Độ bền và độ nhạy — Table_05, Table_14; T12, A11

Strict OOS âm được giữ nguyên. Conditional replay, rolling origin, ablation, parameter uncertainty và seed robustness bổ sung kiểm tra nhưng không biến fit thành forecast.

## 5.13 Tổng hợp hai ca — Table_15; C01

Điểm chung hợp lệ là vòng phản hồi phi tuyến và khuếch đại nội sinh. Terra không định lượng xác thực engine Aave; snapshot Aave 2026 không chứng minh cơ chế Terra 2022.

## 5.14 Mô hình có thể và không thể thiết lập

Mô hình có thể tái lập stress có điều kiện, kiểm tra consistency, so sánh scenario và làm rõ kênh truyền dẫn. Mô hình không thiết lập causal effect lịch sử, xác suất khủng hoảng thực tế, forecast chính xác hoặc systemic importance toàn DeFi.
