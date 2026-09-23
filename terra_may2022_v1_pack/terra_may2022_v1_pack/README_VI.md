# Terra May 2022 — Data Pack cho DeFiStress

Mục tiêu của gói này là tạo bộ dữ liệu `terra_may2022_v1` cho giai đoạn **01/05/2022 00:00 UTC → 13/05/2022 23:00 UTC** theo schema hiện tại của DeFiStress.

## Nguồn chính

Nguồn ưu tiên là replication package của bài:

- Jiageng Liu, Igor Makarov, Antoinette Schoar (2026), *Anatomy of a Run: The Terra Luna Crash*, Journal of Financial Economics.
- Mendeley Data: DOI `10.17632/j5d8n7hzdy.4`.
- Dataset id: `j5d8n7hzdy`, version 4.
- Replication package được Mendeley mô tả là chứa dữ liệu xử lý từ Terra Classic public blockchain, CoinGecko, cùng một số extract được ghi nhận từ Kaiko/Flipside/Nansen.

Gói builder **không tự bịa dữ liệu**. Nếu một trường không tìm được nguồn đủ rõ, builder sẽ đánh dấu thiếu và **không gắn REAL_HISTORICAL**.

## Hai output khác nhau

1. `terra_may2022_v1_evidence.csv`
   - Chỉ chứa trường đã tìm thấy bằng dữ liệu nguồn / phép tổng hợp trực tiếp.
   - Dùng để audit và provenance.

2. `terra_may2022_v1.csv`
   - Đúng schema mà DeFiStress yêu cầu.
   - Chỉ được xuất với `status=REAL_HISTORICAL` nếu toàn bộ trường bắt buộc qua strict provenance check.
   - Nếu cần proxy để chạy mô hình, dùng `--allow-proxy`; khi đó output bị ép về `QUALITY_WARNING`, tuyệt đối không gọi là REAL_HISTORICAL.

## Cách chạy nhanh trong repo DeFiStress

Copy cả thư mục này vào root repo rồi chạy PowerShell:

```powershell
.\.venv\Scripts\python.exe terra_may2022_v1_pack\build_terra_may2022_v1.py `
  --repo-root . `
  --work-dir data\raw\terra_may2022_v1 `
  --output data\processed\terra_may2022_v1.csv `
  --strict
```

Nếu bạn đã tải thủ công `terra-luna-run-replication.zip` từ Mendeley:

```powershell
.\.venv\Scripts\python.exe terra_may2022_v1_pack\build_terra_may2022_v1.py `
  --repo-root . `
  --replication-zip "C:\path\terra-luna-run-replication.zip" `
  --work-dir data\raw\terra_may2022_v1 `
  --output data\processed\terra_may2022_v1.csv `
  --strict
```

Builder sẽ tạo thêm:

- `source_inventory.csv`
- `mapping_report.json`
- `provenance_manifest.json`
- `missing_fields.json` nếu còn thiếu
- `terra_may2022_v1_evidence.csv`

## Validate trong DeFiStress

Khi strict build thành công:

```powershell
.\.venv\Scripts\python.exe scripts\terra\validate_dataset.py `
  --input data\processed\terra_may2022_v1.csv `
  --dataset-version terra_may2022_v1 `
  --status REAL_HISTORICAL `
  --source-name "Liu-Makarov-Schoar replication + Terra Classic" `
  --source-type "REPLICATION_ONCHAIN" `
  --chain-id columbus-5 `
  --output data\processed\terra_may2022_v1_validation.json
```

## Import vào database

```powershell
.\.venv\Scripts\python.exe scripts\terra\import_dataset.py `
  --input data\processed\terra_may2022_v1.csv `
  --dataset-version terra_may2022_v1 `
  --status REAL_HISTORICAL `
  --source-name "Liu-Makarov-Schoar replication + Terra Classic" `
  --source-type "REPLICATION_ONCHAIN" `
  --chain-id columbus-5 `
  --raw-reference "doi:10.17632/j5d8n7hzdy.4" `
  --manifest-output data\processed\terra_may2022_v1_import_manifest.json
```

Sau đó restart backend và mở:

`http://localhost:3000/terra/overview`

Dashboard nên tự ưu tiên `terra_may2022_v1` nếu status là `REAL_HISTORICAL`.

## Quy tắc học thuật quan trọng

- Không điền số 0 để thay cho dữ liệu bị thiếu.
- Không nội suy một biến dòng giao dịch rồi gọi là giao dịch thực.
- Không dùng dữ liệu sau `2022-05-06T23:59:59Z` để fit/calibrate model trong OUT_OF_SAMPLE replay.
- Có thể dùng toàn bộ 07–13/05 làm `ground truth` chỉ ở lớp validation.
- Các proxy chỉ dùng để debug/mô phỏng và phải mang status `QUALITY_WARNING`.

## Nếu strict builder báo thiếu

Mở `missing_fields.json` và `mapping_report.json`. Những file này cho biết:

- trường nào thiếu;
- candidate source nào đã tìm thấy;
- file/column nào gần nhất;
- lý do không đủ điều kiện REAL_HISTORICAL.

Không sửa CSV bằng số tự ước lượng chỉ để qua importer.
