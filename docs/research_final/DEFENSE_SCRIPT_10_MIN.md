# KỊCH BẢN BẢO VỆ 10 PHÚT

Kính thưa Hội đồng, nghiên cứu này bắt đầu từ câu hỏi: khi các giao thức DeFi nối tín dụng với thanh khoản, một cú sốc có thể tự khuếch đại như thế nào? Em không cố xây dựng một mô hình dự báo giá vạn năng. Em xây dựng một pipeline evidence-first, trong đó mọi con số đều quay lại được artifact và source hash.

Thiết kế có hai ca. Terra tháng 5/2022 là ca lịch sử để kiểm tra cơ chế, Historical Fit và Early Warning. Aave V3 × Uniswap V3 là ca stress hiện đại trên snapshot REAL_MAINNET block 26,045,352. Hai ca không cùng thời điểm và Terra không xác thực định lượng Aave.

Về dữ liệu, Terra có 1,776 giờ và 277,342 native swaps. Aave có 454 borrower xác minh và cohort WETH/USDC 109. Tỷ lệ xác minh ứng viên không phải độ phủ toàn thị trường.

Đối với Terra, identity gross issuance được kiểm tra trực tiếp bằng `swap_amount + fee_amount`. Kết quả hỗ trợ nhất quán kế toán, nhưng em không diễn giải thành bằng chứng minting gây sụp giá. Historical Fit đạt UST RMSE 0.1778, song sai số timing tại ngưỡng 0,995 là -45 giờ, nghĩa là mô phỏng chạm ngưỡng sớm.

Kết quả này không cho thấy mô hình dự báo được cú depeg ban đầu. Cảnh báo cutoff-safe High Risk có lead time -45 giờ tại ngưỡng 0,995, tức là muộn; ở severe depeg 0,90, lead time là 3 giờ. Đây là bằng chứng âm cần giữ lại.

Ở Aave, vòng mô phỏng là shock giá, giảm HF, liquidator trả nợ và thu collateral, bán WETH vào Uniswap, price impact rồi tái định giá. Professor Demo tạo nợ thanh lý 9063 và Wave 2+ 0. Nếu số sau bằng zero, kết luận đúng là không có second wave nội sinh.

Monte Carlo cho tần suất cascade 0 với Wilson [0, 0.01885]. Em nhấn mạnh: đây là tần suất lấy mẫu trong mô hình, không phải xác suất khủng hoảng thực tế.

Mạng đa lớp giúp nhìn đường truyền exposure, liquidation, price impact và stabilization. Aave là bridge trong topology nhỏ này; centrality không đại diện toàn bộ DeFi và điểm 0,8 không phải xác suất 80%.

Đóng góp chính là một quy trình tái lập từ data quality tới claim ledger, figures và defense package. Hạn chế quan trọng là dữ liệu Terra còn unavailable, sample Aave không phải toàn thị trường, một venue Uniswap, topology nhỏ và model dependence.

Kết luận, nghiên cứu cho thấy cách phân tích phản hồi phi tuyến một cách có boundary. Giá trị của nó nằm ở khả năng audit và giữ cả kết quả không thuận lợi, chứ không ở một lời hứa dự báo chắc chắn. Em xin cảm ơn Hội đồng.
