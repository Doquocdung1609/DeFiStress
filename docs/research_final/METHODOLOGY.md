# PHƯƠNG PHÁP NGHIÊN CỨU

## Đề xuất chuẩn hóa câu hỏi nghiên cứu từ mô hình hiện tại

- RQ1: Cú sốc giá tài sản thế chấp tạo vòng thanh lý giữa Aave V3 và Uniswap V3 như thế nào?
- RQ2: Thanh khoản DEX, năng lực liquidator và arbitrage ảnh hưởng đến khuếch đại rủi ro ra sao?
- RQ3: Mô hình phản hồi tái dựng được và chưa tái dựng tốt đặc điểm nào của Terra 2022?
- RQ4: Chỉ báo cutoff-safe có cảnh báo trước severe depeg hay không?
- RQ5: Mạng đa lớp cho thấy kênh truyền dẫn và node cầu nối nào trong sub-network Aave–Uniswap?

## Thiết kế hai ca

Terra là ca lịch sử dùng dữ liệu giờ từ 2022-03-01T00:00:00Z đến 2022-05-13T23:00:00Z, gồm 1776 timestamp và 277342 native swaps. Aave–Uniswap là ca stress hiện đại dùng snapshot REAL_MAINNET cùng block 26045352. Hai ca không được xem là cùng thời điểm và không kiểm chứng cơ chế lẫn nhau.

## Phân lớp bằng chứng

- **Quan sát:** giá, state protocol, event extract và trạng thái pool có provenance.
- **Suy dẫn:** Health Factor kiểm tra lại, độ sâu, điểm cảnh báo, centrality và ma trận chuẩn hóa.
- **Mô phỏng:** liquidation waves, bad debt, price impact và stress paths.
- **Phản thực:** các preset và sweep thay đổi shock, thanh khoản, gas, arbitrage, liquidator.

## Terra

Historical Fit được hiệu chỉnh trên luồng lịch sử quan sát và được gọi là tái dựng có điều kiện, không phải forecast. Early Warning gồm retrospective và cutoff-safe; kiểm tra future perturbation yêu cầu dữ liệu sau cutoff không làm thay đổi điểm trước cutoff. Mechanism Check dùng gross mint trực tiếp `swap_amount + fee_amount`. Stress Test giữ mapping tham số đã đóng băng rồi thay đổi giả định preset.

## Aave–Uniswap

The Graph chỉ phục vụ discovery trong snapshot gốc; state cuối cùng được xác minh bằng Ethereum RPC cùng block. `Pool.getUserAccountData` là chuẩn đối chiếu Health Factor. WETH chỉ được tính collateral khi `usageAsCollateralEnabled=true`. Engine hiện hữu mô phỏng shock → HF → liquidator → forced WETH sale → Uniswap price impact → tái định giá; arbitrage là agent ổn định theo capacity giả định.

## Monte Carlo và độ bền

Mỗi kịch bản research dùng 200 lần chạy do benchmark thời gian đã ghi; seed chính 20260914 và kiểm tra seed 20260915–20260916. Tần suất cascade và Wilson interval là thống kê lấy mẫu có điều kiện trên mô hình, không phải xác suất ngoài đời. Sweep một yếu tố và grid 8×4 không tạo suy luận nhân quả.

## Mạng đa lớp

Đồ thị chỉ chứa node và cạnh có nguồn từ snapshot, engine hoặc giả định kịch bản. Điểm cạnh chuẩn hóa, ma trận contagion và centrality chỉ có nghĩa trong sub-network này. Compound, Maker và Curve không được đưa vào metric khi chưa ingest dữ liệu.

## Tái lập

Lệnh chuẩn: `.\.venv\Scripts\python.exe scripts\run_full_research_pipeline.py --research`. Hash input/output, phiên bản, seed, scenario và kết quả kiểm tra được ghi trong manifest và preflight.
