# P04-01A — đề xuất thu hồi và verification bằng chứng lịch sử

**PROPOSED_ACQUISITION_PACKAGE — NOT_DISPATCHED — NO_BACKTEST_OR_EXIT_PERMISSION.** Không có dữ liệu thị trường mới được thu thập trong hồ sơ này; đã đọc tài liệu nguồn và dữ liệu repository hiện có. Đây là gói tiếp theo để Commander quyết định scope/quyền truy cập. Không dùng thiết kế như chứng nhận có archive.

Base nghiên cứu `053e94cb722f15eed689814c5a7771fa8f881be8`; ledger và quyết định nguồn nằm cùng thư mục. Không ghi vào dữ liệu V1, Phase01 hoặc Codex `terra_pit/`. Đề xuất owner acquisition riêng; Work sở hữu source adjudication. Output sau khi được duyệt nên ở namespace mới có manifest/version, không ghi đè pack cũ.

## A. CEX price / vintage recovery — ưu tiên đầu

Candidate symbols: **USTUSDT, LUNAUSDT, BTCUSDT, ETHUSDT, USDCUSDT** trên Binance spot. Đây là nhãn tìm kiếm được đăng ký, **chưa xác minh coverage**. Phải xác minh UST/LUNA lịch sử và chuỗi đổi tên Classic trước dùng; symbol hiện tại không tự thay tài sản tháng 5/2022.

Cửa sổ intraday đề xuất `[2022-03-01,2022-05-14)` UTC, 1-minute hoàn chỉnh; đồng thời đánh giá khả năng truy xuất daily `[2020-10-02,2022-05-14)` cho daily track. Không chọn lại cửa sổ vì có warning. Khả năng dữ liệu trước May1 là mục tiêu đo lường, không giả định có đủ. Bắt đầu bằng catalog/terms/HEAD/checksum/revision metadata và vài tệp pilot theo ngày đăng ký, rồi mới quyết định mở rộng sau audit.

Yêu cầu: URL/file ID, symbol/base/quote, trade/kline method, schema ms-versus-us đúng phiên bản, khoảng open/close, first publication evidence, available time hoặc bound được review, revision history và old/new checksum. Chứng minh từng archive hiện tại có thể hoặc không thể khớp vintage lịch sử. Đọc danh sách thay thế kline năm 2022 trước khi công bố file nào không bị sửa. Nếu chỉ còn current vintage, giữ `RETROSPECTIVE_REVISED_DATA`, không gọi PIT-confirmed.

Tài liệu 20/04/2022 cho biết daily archive tải vào ngày kế tiếp, nhưng không có giờ upload cụ thể. Không tự gán 00:00 ngày kế tiếp. Nếu dùng live-feed reconstruction, phải có bằng chứng capture/emission/receipt hoặc một chính sách bound được duyệt; tài liệu websocket có `E` không tái tạo `E` đã mất trong CSV. UST/USDT cần đường đổi USDT/USD đúng thời điểm; không mặc định bằng một USD.

## B. Curve historical state — kiểm tra khả năng, chưa execution

Hai candidate anchors được báo cáo ngoài mô hình: block14732235 và14732287 ngày 07/05/2022; tx hashes trong file onset. Trước request: xác minh chain, header/hash/timestamp/receipt, đúng contract/ABI/token identity/decimals/code version. Không điền pool address bằng trí nhớ. Báo cáo hiện tại chỉ đọc các liên kết bị403; các anchor chưa được independently readback.

Đăng ký pre-event control grid và nguồn archive sau feasibility, trước phân tích stress. Thu thập balances, amplification/fee/virtual-price semantics và trạng thái cần cho quote nếu được duyệt. Phân biệt reserves/state observations với giả thuyết thực thi; không chạy swap, liquidation, portfolio hay exit. Thiếu archive quyền truy cập → `DATA_ACCESS_BLOCKED`; thiếu ABI/header → quarantine. Hai URL khác nhau không tự tạo nguồn độc lập.

## C. Terra/Anchor — đúng state height và deployed query semantics

Candidate chain `columbus-5`, không phải mạng Terra mới. Cần full header/commit/chain identity, query response height, deployed code ID/hash và historical address mapping. Read-only state query tại height phải thật sự được provider thực thi ở height đó; tham số `block_height` bên trong message còn có thể chỉ là đầu vào tính accrued interest. Kiểm tra hai chiều này riêng.

Tách stored `prev_aterra_supply`/`prev_exchange_rate`, epoch response, native denom `uusd` và normalized token-unit dataset. Gắn unit contract theo từng source version. Với deposit/withdraw/native swap events: transaction/action, direction, coverage completeness và interval end; không suy zero từ trang events vắng dữ liệu. Không dùng tổng daily holders như một nguồn supply đã được kiểm chứng nếu chưa kiểm tra scope/normalization.

## Acceptance và stop conditions

| Gate | PASS cần có | Nếu thiếu |
|---|---|---|
| AQC-01 identity | Tài sản/venue/symbol/chain/contract và nguồn gốc đúng, lịch sử đổi tên rõ | REJECTED hoặc BLOCKED theo lý do; không fallback tài sản mới |
| AQC-02 bytes/vintage | Raw bytes, size, SHA256, publisher checksum, revision mapping và retrieval provenance | Không tuyên bố nguyên bản lịch sử; chỉ current-vintage audit |
| AQC-03 timing | Interval/clock/publication/availability theo nguồn và latency semantics có bằng chứng | BLOCKED_INSUFFICIENT_AVAILABILITY_EVIDENCE |
| AQC-04 coverage | Gaps/duplicate/order/range, training support, zero-vs-missing và quarantine đo được | Giữ mẫu số và exclusions; không forward-fill ngầm |
| AQC-05 chain state | Request height, response height, header/hash, ABI/deployed code và precision khớp | DATA_ACCESS_BLOCKED hoặc provenance mismatch |
| AQC-06 repeatability | Re-read cùng request/version tạo deterministic semantic hash; raw byte hash giữ riêng | Điều tra timestamp/request metadata khác biệt; không ép hash bằng nhau |
| AQC-07 preservation | V1/Phase01/P02/frozen registry/tag giữ nguyên, không feature/model/exit run | STOP; sửa scope trước tiếp tục |

Paid API, account permission, terms/license bất định, forbidden access, revision không truy vết, unsupported deployed version hoặc thiếu record time phải dừng/escalate đúng vấn đề. Không vượt kiểm soát truy cập. Kết quả hợp lệ có thể là không thể khôi phục PIT hoặc không đủ intraday training. Gói không yêu cầu tìm được tín hiệu dương và không cấp quyền historical backtest.
