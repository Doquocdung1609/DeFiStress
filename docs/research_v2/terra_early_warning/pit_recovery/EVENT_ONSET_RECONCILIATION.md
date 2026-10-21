# Terra — đối chiếu mốc sự kiện và nhãn thời gian

**RECONCILIATION_OF_SOURCE_SEMANTICS — NOT_A_NEW_ONSET_OR_FORECAST_RUN.** Anchor repository `053e94cb722f15eed689814c5a7771fa8f881be8`. Chỉ đọc các dòng đã liên quan trực tiếp đến tranh chấp; không dò lại onset toàn chuỗi, tính lead time hay chạy cảnh báo.

## 1. Vì sao hai artifact dùng 22:00 và 23:00?

`data/processed/terra_final/final_report.md` mục 6 ghi trigger UST dưới 0,99 tại 07/05/2022 22:00 UTC. `data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json#/modes/CUTOFF_SAFE/lead_times/ust_below_0_99` ghi 23:00 UTC trên bảng mở rộng. Hai bảng không lấy cùng một điểm trong giờ.

Đã đọc lại các dòng dưới đây từ bytes đã xác minh. Các chữ số được giữ nguyên, đơn vị theo nguồn là USD/UST và USD/LUNA; danh nghĩa USD của giá vendor vẫn chịu điều kiện nguồn/quote/vintage trong ledger.

| Nhãn giờ 07/05 UTC | Bảng legacy: UST / LUNA | Bảng mở rộng: UST / LUNA |
|---|---|---|
| 22:00 | 0.989186461186343 / 65.04399843524503 | 0.9946504295722324 / 66.58563664815836 |
| 23:00 | 0.993538818615646 / 68.04390029107051 | 0.9889272685779045 / 65.25051734908128 |

| Nhãn minute trong Parquet nguồn | UST | LUNA | Đối chiếu trực tiếp |
|---|---:|---:|---|
| 22:00 | 0.9946504295722324 | 66.58563664815836 | Bảng mở rộng nhãn 22:00 |
| 22:59 | 0.989186461186343 | 65.04399843524503 | Bảng legacy nhãn 22:00 |
| 23:00 | 0.9889272685779045 | 65.25051734908128 | Bảng mở rộng nhãn 23:00 |
| 23:59 | 0.993538818615646 | 68.04390029107051 | Bảng legacy nhãn 23:00 |

Locators: `data/processed/terra_may2022_v1.csv`; `data/processed/terra_extended/terra_state_hourly_20220301_20220513.csv`; `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/prices/{ust,luna}_price_may2022.parquet`.

Manifest legacy `data/raw/terra_may2022_v1/provenance_manifest.json#/evidence_map` khai báo `hourly last` cho hai giá. Mã `terra_may2022_v1_pack/terra_may2022_v1_pack/build_terra_may2022_v1.py`, `hourly_series` dòng 354–372, dùng `resample("1h").last()`; các dòng 909–910 yêu cầu `last` cho giá. Trong khi đó `scripts/terra/complete_historical_data.py::_composite_price`/`_minute_price` dùng backward-as-of tại giờ đích. Các giá trị cụ thể xác nhận ánh xạ khác nhau ở hai giờ này, phù hợp với mã và manifest. Không có bằng chứng đây đơn thuần là chênh múi giờ.

**Kết luận về TERRA-A06:** đã giải thích được sự khác nhau về điểm lấy mẫu, nhưng chưa chọn onset chuẩn cho nghiên cứu V2. Không dịch mọi dòng một giờ một cách cơ học: minute nguồn có thể là bar chưa rõ closure, dữ liệu có khoảng thiếu, và các trường khác có phép tổng hợp riêng. Cần contract về interval label/end/availability trước khi quyết định thông tin nào hợp lệ tại một giờ phát cảnh báo. Không sửa bảng V1 và không tính lại các lead time đã lưu.

## 2. Mốc cấu trúc thị trường khác mốc vượt ngưỡng giá

[Jump Crypto, báo cáo ngày 02/06/2022](https://jumpcrypto.com/resources/the-depegging-of-ust) dùng GMT. Nguồn mô tả các thay đổi Curve ở 21:44 và 21:57 ngày 07/05, và một giai đoạn suy giảm rõ hơn khoảng 18:30 ngày 09/05. Đây là các mốc hồi cứu từ một bên tham gia thị trường, độc lập với mô hình DeFiStress nhưng không phải một replication vô tư hay bằng chứng dự báo.

Hai candidate để verification: withdrawal tại block **14732235**, transaction `0x18bd477f9beeff22b2ad0c6d48a9c0f02b542049789f0638f5ec50365f1d1de7`; swap tại block **14732287**, transaction `0xaa23df48c53f221d0e8ac60ffc9e69340f3e8948fcdc936f3aee9c887d802abb`. Chúng được lấy từ bảng/liên kết của báo cáo; explorer trả 403 nên trạng thái vẫn **SOURCE_REPORTED — RECEIPT_AND_HEADER_NOT_VERIFIED**. Không suy ra số dư pool hoặc khả năng thoát vị thế từ các mốc này.

Mốc giao dịch, lần giá dưới 0,99, vi phạm kéo dài và mức nghiêm trọng dưới 0,90 trả lời các câu hỏi khác nhau. Mốc khoảng 18:30 trong mô tả và mốc 22:00 ở threshold 0,90 của artifact cũ không mặc nhiên mâu thuẫn; không lựa chọn mốc thuận lợi hơn cho cảnh báo. Nansen URL gốc hiện không truy cập được; bản trích lại không được nâng thành nguồn nguyên thủy đã đọc.

## 3. Onset policy đề xuất trước khi chạy

Curator phải pin source/venue/base currency/vintage, chất lượng thời gian và phạm vi đầy đủ; đăng ký nhãn single-breach và sustained-breach riêng, bốn mức 0,995/0,99/0,95/0,90, quy tắc phục hồi/tách episode và censoring. Nến giá hoàn chỉnh mới được dùng để xác định nhãn; chỉ số dự báo tuân thủ thông tin khả dụng ở thời điểm phát. Timestamps của nhãn và alert phải cùng convention.

Nguồn label có thể thu thập sau sự kiện để xác định outcome, nhưng không được đưa tri thức hậu nghiệm đó vào feature, chọn ngưỡng hoặc chọn onset có lead tốt nhất. Phân biệt quyền truy cập thông tin dùng xác định outcome với quyền sử dụng predictor tại từng cutoff. Curator chưa được chỉ định; onset V2 chưa được khóa. Các lựa chọn đang đề xuất, không được coi là protocol đã duyệt.
