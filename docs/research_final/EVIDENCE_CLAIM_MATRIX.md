# MA TRẬN BẰNG CHỨNG–CLAIM

| claim_id | statement | result_ids | status | boundary |
| --- | --- | --- | --- | --- |
| C01 | Terra Historical Fit tái dựng được hướng biến động nhưng chạm các ngưỡng UST sớm hơn lịch sử. | TERRA_HF_UST_CORRELATION, TERRA_TIMING_0_995, TERRA_TIMING_0_9 | PARTIALLY_SUPPORTED | Fit có điều kiện; không phải dự báo ngoài mẫu. |
| C02 | Chỉ báo cutoff-safe không cảnh báo trước depeg ban đầu ở ngưỡng High Risk. | TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH, TERRA_EW_LEAKAGE | SUPPORTED_NEGATIVE_FINDING | Kết luận giới hạn ở định nghĩa chỉ báo và cutoff đã triển khai. |
| C03 | Chỉ báo cutoff-safe High Risk xuất hiện trước severe depeg UST dưới 0,90. | TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_9_HIGH | SUPPORTED | Không đồng nghĩa dự báo khủng hoảng nói chung. |
| C04 | Native-swap event output hỗ trợ nhất quán kế toán gross mint swap_amount + fee_amount. | TERRA_MECH_EVENT_COUNT, TERRA_MECH_DIRECT_CORRELATION, TERRA_MECH_DIRECT_CUMULATIVE_ERROR | SUPPORTED | Không chứng minh gross mint gây ra biến động giá. |
| C05 | Các preset stress Terra cho thấy regime bình thường và runaway khác nhau rõ rệt. | TERRA_STRESS_BASELINE_COLLAPSE_COUNT, TERRA_STRESS_SEVERE_COLLAPSE_COUNT | MODEL_CONDITIONAL | Tần suất đường mô phỏng không phải xác suất ngoài đời. |
| C06 | Snapshot Aave chính là REAL_MAINNET cùng block và không dùng Fixture làm bằng chứng chính. | AAVE_DATA_BLOCK_NUMBER, AAVE_DATA_VERIFIED_BORROWERS, AAVE_DATA_WETH_USDC_COHORT | SUPPORTED | Cohort ứng viên không phải toàn bộ thị trường Aave. |
| C07 | Professor Demo cho thấy mức thanh lý và cascade theo chính giả định kịch bản đã đóng băng. | AAVE_DET_PROFESSOR_DEMO_TOTAL_LIQUIDATED_DEBT, AAVE_DET_PROFESSOR_DEMO_CASCADE_DEPTH, AAVE_DET_PROFESSOR_DEMO_WAVE_2_PLUS_LIQUIDATED_DEBT | MODEL_CONDITIONAL | Không suy rộng thành dự báo Mainnet tương lai. |
| C08 | Độ nhạy Aave được đánh giá bằng sweep một yếu tố và bề mặt shock × liquidity. | AAVE_DET_PROFESSOR_DEMO_MAX_PRICE_IMPACT, AAVE_DET_PROFESSOR_DEMO_BAD_DEBT | MODEL_CONDITIONAL | Association trong mô hình, không phải quan hệ nhân quả. |
| C09 | Tần suất cascade Monte Carlo có khoảng Wilson nhưng vẫn là tần suất lấy mẫu trong mô hình. | AAVE_MC_PROFESSOR_DEMO_CASCADE_FREQUENCY, AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_LOWER, AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_UPPER | MODEL_CONDITIONAL | Không gọi là xác suất thực tế. |
| C10 | Centrality chỉ mô tả vai trò cầu nối trong sub-network Aave–Uniswap nhỏ. |  | SUPPORTED_WITH_BOUNDARY | Không đại diện tầm quan trọng hệ thống trên toàn DeFi. |
| C11 | Terra không định lượng kiểm chứng cơ chế Aave và Aave không chứng minh cơ chế Terra. |  | SUPPORTED_BOUNDARY | Tổng hợp chéo chỉ ở mức phản hồi phi tuyến và khuếch đại nội sinh. |
| C12 | Mô hình dự báo được chính xác vụ sụp đổ Terra. |  | UNSUPPORTED | Strict OOS âm và cảnh báo depeg ban đầu muộn; không được sử dụng claim này. |
