# Kịch bản trình diễn DeFiStress Lab (6–10 phút)

## Chuẩn bị

Máy cần Python 3.12, Node.js 24 và pnpm; chạy từ thư mục gốc:

```powershell
.\scripts\start_demo.ps1
.venv\Scripts\python.exe scripts\demo_smoke.py
```

Lệnh đầu tiên cài thư viện còn thiếu, khởi động API/giao diện ở cổng 8100/3100
và chờ cả hai sẵn sàng. Nếu cổng đã bận, dừng ứng dụng khác rồi chạy lại.
Mở <http://localhost:3100/overview>. Không cần khóa API hay dịch vụ trả phí.

## 9 cảnh trình diễn

| Cảnh | Thao tác trên giao diện | Lời dẫn, API và kết quả đã kiểm chứng |
|---|---|---|
| 01 Aave cơ sở | Chọn **Aave V3**, giữ Fixture, mở Overview và Positions, chọn preset **Baseline** rồi Run deterministic. | `/api/v1/snapshots`, `/scenarios`, `/runs`. Quan sát giá oracle, giá DEX, nợ, tài sản thế chấp và HF. Fixture là dữ liệu tổng hợp. |
| 02 Thanh lý | Vào Scenarios, chọn **Severe**, chạy. | `/api/v1/runs`. Chỉ ra số vị thế *đủ điều kiện* và số thanh lý *được thực thi* theo vốn, độ trễ, lợi nhuận. Không đồng nhất hai số này. |
| 03 Phản hồi Uniswap | Chọn **Low Liquidity**, chạy và mở Results/contagion graph. | `/api/v1/runs/{id}`. So sánh reference/oracle price với DEX spot, tác động giá, các bước phản hồi có điều kiện. Run fixture mặc định thực tế ngày 18/11: total liquidated debt 172,944.16 USDC, depth 2, max price impact 1.17%; đây là mô hình, không phải quan sát Mainnet. |
| 04 Terra lịch sử | Chọn **Terra 2022 → Historical Data**; chuyển All, May, Crisis week, rồi Custom dates. | `/api/v1/terra/demo/historical-data`: 1.776 giờ từ 01/03 đến 13/05/2022. Xem chú thích nguồn; giờ thiếu là khoảng trống, không được điền 0. Giá được carry từ tần suất thấp trước tháng 5. |
| 05 B0–B3 | Mở **Synthetic B0–B3**. Chạy giá UST 0.99, LUNA 100→90; chọn HIGH, MISSING, LATE và chạy lại. Mở từng phần chi tiết. | `POST /api/v1/terra/demo/warnings`. Bộ 0.99/100/90 cho B0 NORMAL, B1 HIGH, B2 HIGH, B3 WATCH; 0.96/100/50 cho B3 HIGH; thiếu UST cho ABSTAIN. Xem ngưỡng, đóng góp, cutoff và lineage. Đây là dữ liệu tạo cho demo năm 2030, không phải cảnh báo Terra 2022. |
| 06 Cảnh báo hồi cứu | Mở **Early Warning**, đổi Retrospective/Cutoff-Safe. | `GET /api/v1/terra/early-warning?mode=...`. Dòng thời gian 1.776 giờ và event marker là thăm dò hồi cứu; không chứng minh một dự báo V2 đã sẵn có trước khủng hoảng. |
| 07 Terra stress | Mở **Stress Test**, chọn Baseline rồi Adverse, chạy 1 scenario mỗi lần; thử 100 runs nếu còn thời gian. | `POST /api/v1/terra/stress-test`. Fan chart, LUNA supply và collapse count phụ thuộc giả định. Smoke thực tế dùng 2 seeded runs/4 giờ. Collapse count không phải xác suất. |
| 08 Thoát minh họa | Mở **Exit Calculator**. Để trống capacity, bấm tính; nhập capacity 600 với 1.000 UST, giá lúc cảnh báo 1 USD, giá ra 0,8 USD, phí 1%, trượt giá 2%, trễ 15 phút, tính lại. | `POST /api/v1/terra/demo/exits`. Khi không biết capacity: `NOT_VERIFIABLE`. Với capacity 600: khớp 600, còn 400, gross 480, phí 4,8, trượt 9,6, ròng 465,6 USD; mất 134,4 USD so với 600 USD ở giá cảnh báo. Không có đảm bảo giao dịch thật. |
| 09 Lưu và xuất | Chọn **Mở kết quả đã lưu** ở cảnh 08, kiểm tra tham số và nhãn nguồn, bấm **Tải kết quả ZIP**, tải lại trang. | `GET /api/v1/terra/demo/runs`, `GET /runs/{id}`, `GET /runs/{id}/export`. Bản lưu và ZIP `result.json` trùng với kết quả trả về; SQLite giữ nguyên sau khi dừng. |

## Khi gặp lỗi

- Trang báo API unavailable: chạy lại `scripts/start_demo.ps1`; xem `data/runs/demo-api-error.log` và `demo-web-error.log`.
- Cổng bận hoặc ghi nhận tiến trình cũ: chạy `.\scripts\stop_demo.ps1`, kiểm tra dịch vụ đang dùng cổng 8100/3100 rồi khởi động lại. Script không tự dùng ứng dụng ở cổng khác.
- Thiếu dữ liệu UST/LUNA: xem `ABSTAIN`; không diễn giải thành rủi ro thấp.
- Không có dung lượng thị trường: xem `NOT_VERIFIABLE`; không nhập volume làm depth.
- Docker: chỉ là đường chạy tùy chọn. Cần Docker Engine trước `docker compose up --build`.

Kết thúc: `.\scripts\stop_demo.ps1`. Bản ghi demo nằm ở
`data/runs/demo.sqlite`; sao lưu trước nếu muốn đặt lại môi trường. Không xóa
`data/processed`, `docs/research_v2` hay bằng chứng V1.
