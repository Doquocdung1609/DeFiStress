# DỰ THẢO TÓM TẮT

Nghiên cứu xây dựng một quy trình kiểm định sức chịu đựng DeFi có thể tái lập bằng hai ca bổ sung nhưng không đồng nhất: Terra Classic tháng 5/2022 để kiểm tra tái dựng lịch sử, cảnh báo sớm và cơ chế phát hành; Aave V3 × Uniswap V3 để mô phỏng thanh lý dây chuyền trên snapshot Ethereum Mainnet. Dữ liệu Terra gồm 1,776 giờ và 277,342 native swaps; ca Aave dùng 454 borrower xác minh tại block 26,045,352.

Historical Fit Terra đạt UST RMSE 0.1778, nhưng sai số timing tại ngưỡng 0,995 là -45 giờ (mô phỏng sớm). Chỉ báo cutoff-safe High Risk có lead time -45 giờ, tức xuất hiện sau depeg ban đầu, nên không hỗ trợ claim dự báo sớm sự kiện này; ngược lại, nó đi trước severe depeg 0,90 khoảng 3 giờ. Bằng chứng transaction hỗ trợ nhất quán kế toán gross issuance nhưng không xác lập nhân quả giá.

Trong ca Aave, Professor Demo tạo nợ thanh lý 9063 và cascade depth 1. Monte Carlo cho tần suất cascade model-implied 0 với khoảng Wilson [0, 0.01885]. Các kết quả này phụ thuộc snapshot, giả định và engine; chúng không phải xác suất thị trường.

Đóng góp chính là kiến trúc evidence-first liên kết dữ liệu, mô hình, bảng, hình và claim ledger. Hạn chế gồm availability Terra, single-venue Aave/Uniswap, sample borrower, topology nhỏ và model dependence. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]
