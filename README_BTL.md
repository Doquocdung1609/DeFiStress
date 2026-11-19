# DeFiStress — bản demo bài tập lớn Nhóm 1

**Đề tài:** Mô hình hóa và kiểm định sức chịu đựng rủi ro lây lan trong tài chính phi tập trung (DeFi).

**Nhóm thực hiện theo báo cáo gốc:** Đỗ Quốc Dũng, Nguyễn Duy Anh, Đỗ Trung Hải, Nguyễn Quang Minh. Học phần, giảng viên và phân công cá nhân phải được nhóm xác nhận trước khi nộp.

## Phương pháp và phạm vi

Agent-Based Modeling (ABM) là phương pháp mô phỏng chính. Các vị thế người vay tương tác với một tác nhân thanh lý và một tác nhân kinh doanh chênh lệch giá đại diện trong môi trường Aave V3 và Uniswap V3. Stress tất định, Monte Carlo, phân tích mạng và tái dựng Terra là các kỹ thuật bổ trợ. Các kết quả mô phỏng là phản thực có điều kiện, không là giao dịch blockchain lịch sử.

Ứng dụng đọc trạng thái blockchain để tạo dữ liệu đầu vào có provenance; engine, API, lưu kết quả và dashboard chạy ngoài chuỗi. Không có smart contract được triển khai hay giao dịch Mainnet trong bản demo.

## Chạy bản demo local

Trên Windows, cần Python 3.12, Node.js, pnpm và PowerShell. Không cần RPC/API key trả phí cho fixture demo.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
cd frontend
pnpm install --frozen-lockfile
cd ..
.\scripts\start_demo.ps1
```

- Frontend: <http://localhost:3100>
- FastAPI: <http://localhost:8100/docs>
- Kiểm tra API: `.\.venv\Scripts\python.exe scripts\demo_smoke.py`
- Dừng: `.\scripts\stop_demo.ps1`

Nếu chưa có snapshot Mainnet đã xác minh, chọn **Fixture Dataset** trong Aave. Nhãn fixture không được hiểu là dữ liệu Mainnet. Terra Historical Data/Historical Fit/Early Warning hồi cứu và Synthetic Warning B0–B3 là các chế độ tách biệt. B0–B3 và Exit Calculator chỉ minh họa giả định, không phải dự báo Terra 2022 hay giao dịch thoát vốn thật.

## Các luồng cần xem

1. Aave Overview → Positions → Scenarios → chạy Baseline/Severe → Results → xem/liên kết dữ liệu nguồn.
2. Terra Historical Data → Historical Fit → Early Warning: xem sự kiện và kết quả hồi cứu, kể cả cảnh báo muộn.
3. Terra Synthetic B0–B3 → lưu cảnh báo → mở Exit Calculator với giá/thời điểm được điền từ cùng lượt chạy.
4. Terra Stress Test → Saved Demo Runs → mở lại run ID và xuất ZIP.

## Hồ sơ nộp bài

Thư mục `NHOM_01_DEFISTRESS_BAO_CAO_BTL` chứa báo cáo Word/PDF, 49 slide PPTX/PDF, kịch bản thuyết trình, video MP4, phương pháp mô phỏng, giải trình blockchain, hướng dẫn cài đặt, bằng chứng kiểm thử và manifest SHA-256. Video quay từ ứng dụng local, không phải mockup.

Repo này có hai nhánh liên quan: `submission/group01-btl-final` dùng cho bản demo bài tập lớn; `feat/terra-model-v2` lưu bản tích hợp nghiên cứu. Bản demo không tự thay thế các kết quả nghiên cứu đã khóa.

## Giới hạn quan trọng

- Snapshot Aave đã khóa ở block 26045352 có 454 người vay xác minh và cohort WETH/USDC 109 vị thế; bản demo local có thể chạy trên fixture synthetic riêng.
- Các vòng thanh lý thứ hai trong lưới mở rộng phụ thuộc giả định truyền giá oracle. Policy A không được mô tả là oracle thực tế của Aave.
- Monte Carlo Severe 280/10.000 là tần suất có điều kiện của mô hình Policy A, không là xác suất khủng hoảng thực tế.
- Terra không có bằng chứng đủ mạnh để tuyên bố hệ thống dự báo ngoài mẫu trước sụp đổ.
- Công cụ thoát vị thế báo riêng phần khớp và phần chưa thoát; giá, thanh khoản và phí do người dùng giả định.
