# NỀN TẢNG BÁO CÁO NGHIÊN CỨU CUỐI CÙNG

## TÓM TẮT

Nghiên cứu xây dựng một quy trình kiểm định sức chịu đựng DeFi có thể tái lập bằng hai ca bổ sung nhưng không đồng nhất: Terra Classic tháng 5/2022 để kiểm tra tái dựng lịch sử, cảnh báo sớm và cơ chế phát hành; Aave V3 × Uniswap V3 để mô phỏng thanh lý dây chuyền trên snapshot Ethereum Mainnet. Dữ liệu Terra gồm 1,776 giờ và 277,342 native swaps; ca Aave dùng 454 borrower xác minh tại block 26,045,352.

Historical Fit Terra đạt UST RMSE 0.1778, nhưng sai số timing tại ngưỡng 0,995 là -45 giờ (mô phỏng sớm). Chỉ báo cutoff-safe High Risk có lead time -45 giờ, tức xuất hiện sau depeg ban đầu, nên không hỗ trợ claim dự báo sớm sự kiện này; ngược lại, nó đi trước severe depeg 0,90 khoảng 3 giờ. Bằng chứng transaction hỗ trợ nhất quán kế toán gross issuance nhưng không xác lập nhân quả giá.

Trong ca Aave, Professor Demo tạo nợ thanh lý 9063 và cascade depth 1. Monte Carlo cho tần suất cascade model-implied 0 với khoảng Wilson [0, 0.01885]. Các kết quả này phụ thuộc snapshot, giả định và engine; chúng không phải xác suất thị trường.

Đóng góp chính là kiến trúc evidence-first liên kết dữ liệu, mô hình, bảng, hình và claim ledger. Hạn chế gồm availability Terra, single-venue Aave/Uniswap, sample borrower, topology nhỏ và model dependence. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

# 1. GIỚI THIỆU

## 1.1 Bối cảnh

DeFi kết nối tín dụng, thanh khoản và định giá bằng hợp đồng thông minh; vì vậy cú sốc có thể lan qua vòng phản hồi. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

## 1.2 Vấn đề, mục tiêu và đóng góp

Mục tiêu là tách dữ liệu quan sát khỏi metric suy dẫn và kết quả mô phỏng, đồng thời giữ bằng chứng âm. Đóng góp là pipeline evidence-first, không phải một tuyên bố dự báo phổ quát.

## Đề xuất chuẩn hóa câu hỏi nghiên cứu từ mô hình hiện tại

- RQ1: Cú sốc giá tài sản thế chấp tạo vòng thanh lý giữa Aave V3 và Uniswap V3 như thế nào?
- RQ2: Thanh khoản DEX, năng lực liquidator và arbitrage ảnh hưởng đến khuếch đại rủi ro ra sao?
- RQ3: Mô hình phản hồi tái dựng được và chưa tái dựng tốt đặc điểm nào của Terra 2022?
- RQ4: Chỉ báo cutoff-safe có cảnh báo trước severe depeg hay không?
- RQ5: Mạng đa lớp cho thấy kênh truyền dẫn và node cầu nối nào trong sub-network Aave–Uniswap?

# 2. CƠ SỞ LÝ THUYẾT VÀ KHUNG RỦI RO

Các chủ đề DeFi, lending, DEX, stablecoin, liquidation, liquidity, contagion, agent-based modeling và multilayer graph cần được neo bằng tài liệu học thuật. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

# 3. DỮ LIỆU VÀ PHƯƠNG PHÁP

Xem `METHODOLOGY.md`. Thiết kế phân biệt quan sát, suy dẫn, mô phỏng và phản thực; snapshot Aave cùng block; Early Warning cutoff-safe; kiểm tra fixed-seed reproducibility.

# 4. MÔ HÌNH

Vòng Aave–Uniswap đi từ shock giá tới HF, thanh lý, bán WETH, price impact và tái định giá; arbitrage/liquidator bị giới hạn bởi capacity. Vòng Terra đi từ peg stress tới redemption, issuance, dilution và confidence. Agent là vai trò mô phỏng, không phải danh tính thực.

# 5. KẾT QUẢ

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

# 6. THẢO LUẬN

Hai ca hỗ trợ cách nghiên cứu feedback-driven stress bằng provenance và claim boundary. Chúng không tạo một phép kiểm định chéo định lượng. Kết quả âm về timing và early warning là phần cốt lõi của tính phòng thủ khoa học.

# 7. HẠN CHẾ

- Terra không có độ sâu DEX lịch sử canonical và không có kênh can thiệp LFG quan sát được.
- Dữ liệu bridge bị quarantine; giá tháng 3–4 có giai đoạn carry-forward tần suất thấp.
- Historical Fit sai thời điểm và cảnh báo cutoff-safe muộn đối với depeg ban đầu.
- Chuyển đổi phản thực Terra có sai số; preset Severe chạm numerical floors nên chỉ biểu diễn runaway regime.
- Aave dùng sample ứng viên, trọng tâm WETH/USDC và một venue Uniswap V3 được chọn; không phải toàn thị trường.
- Centrality được tính trên topology nhỏ; protocol tương lai chưa được ingest.
- Monte Carlo và mọi kết quả stress phụ thuộc cấu trúc mô hình, phân phối nhiễu và giả định kịch bản.

# 8. HƯỚNG NGHIÊN CỨU TIẾP THEO

Mở rộng borrower/protocol, thêm venue execution, ingest bridge/LFG khi có nguồn canonical, kiểm định calibration ngoài mẫu và so sánh topology theo thời gian.

# 9. KẾT LUẬN

Package này cung cấp một chuỗi tái lập từ input hash đến claim. Kết luận mạnh nhất là về cơ chế mô hình và tính minh bạch bằng chứng, không phải khả năng tiên tri khủng hoảng.

# PHỤ LỤC

Xem `TABLE_FIGURE_INDEX.md`, `EVIDENCE_CLAIM_MATRIX.md`, `REPRODUCIBILITY.md` và các registry máy đọc được.
