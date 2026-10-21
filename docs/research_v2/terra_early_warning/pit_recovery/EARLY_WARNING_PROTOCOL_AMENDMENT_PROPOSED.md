# Terra — phụ lục protocol đề xuất và hợp đồng P04-03

**PROPOSED_v1.1 — NOT_APPROVED — HISTORICAL_BACKTEST_NOT_AUTHORIZED.** Bổ sung cho [protocol P04-01 đã tích hợp](https://github.com/Doquocdung1609/DeFiStress/blob/053e94cb722f15eed689814c5a7771fa8f881be8/docs/research_v2/terra_early_warning/p04_01/TERRA_TEMPORAL_RESEARCH_PROTOCOL_PROPOSED.md), không thay thế sáu RQ-T1…T6 hay nâng trạng thái protocol khi merge tài liệu. Work giữ quyền ghi `pit_recovery/`; Codex Issue #50 giữ `defistress_v2/terra_pit/` và tests tương ứng.

## Những quyết định cần seal

| Thành phần | Đề xuất có thể nghiệm thu | Điều kiện / trạng thái |
|---|---|---|
| Loại đánh giá | Terra tháng 5/2022 là case hồi cứu đã biết outcome; exploratory và confirmatory có nhãn riêng | Không gọi đó là một sự kiện mù mới. Cross-event holdout thực sự chưa bị xem cần curator độc lập. |
| Information set | Mỗi trường có interval start/end, event time, publication/available time, vintage, acquisition, delay và lineage | Không tự backdate từ archive tải năm 2026; không gán contract Binance cho aggregate Kaiko. |
| Clock và label | Theo tài liệu đối chiếu onset; single và sustained breach báo riêng, không chọn mốc cho lead đẹp | Phải chọn label source độc lập với score. Event curator chưa được chỉ định. |
| Daily track | Train 02/10/2020–trước 01/04/2022; calibration 01/04–trước 01/05; case 01/05–trước 14/05 UTC; horizons 1 và 3 ngày | Chỉ overlap UST/LUNA đủ điều kiện; không chuyển thành mẫu giờ độc lập. |
| Intraday track | Train/calibration trước 01/05; case 01–13/05; hourly decisions, horizons 1/6/24 giờ | Intraday train đủ tính sẵn có hiện thiếu. Không fit trên đoạn May1–13 rồi gọi OOS. |
| Baselines | B0 không cảnh báo; B1 peg/persistence; B2 trailing LUNA returns/volatility; B3 composite minh bạch nếu đủ common support | Không chọn thuật toán phức tạp trước dữ liệu. So sánh trên cùng clock, horizon, availability mask và báo coverage riêng. |
| Ngưỡng | B1 giữ cả bốn peg levels; score watch/high dùng calibration quantiles 95/99 theo proposal gốc | Không chọn quantile/feature từ case holdout. Tie/missing/warm-up phải seal; chưa fit. |
| Tổng hợp đa biến | Feature contributions, participation, required features và abstention hiển thị | Không renormalize ngầm để biến thiếu thành an toàn. Mức điểm không là xác suất nếu chưa calibration. |
| Temporal split | Trailing-only; fit scale/imputer trên train; purge theo forecast horizon và dependence span | Không random split. Cần khóa feature windows để xác định embargo. |
| False alarms | Báo cả alert observations và episodes; episode kết thúc sau một decision hợp lệ dưới ngưỡng; không coi abstention là all-clear | Quy tắc episode đề xuất này phải được duyệt trước run. Alert chỉ được matched với event trong horizon đã đăng ký. |
| Denominators | Observation/event/non-event exposure, abstention, censored và missing theo từng clock | Precision/recall/miss rate để UNDEFINED khi thiếu mẫu số; không suy rộng từ một crisis. |
| Lead time | Signed event time minus issue time của alert hợp lệ, cùng clock; delay bounds được công bố | Không dùng event timestamp làm alert receipt time. Cảnh báo sau initial instability không là dự báo initial instability. |
| Robustness | Frozen source/vintage/threshold/missingness variants, common-mask và full-coverage báo riêng | Không lựa phiên bản cho kết quả thuận lợi. Chưa có vintage panel đủ điều kiện. |
| Exit | Position 1.000/10.000/100.000 UST là illustrative; route/permission/fees/spread/depth/delay riêng | Chưa có execution inputs; NOT_VERIFIABLE. Được viết spec, chưa được mô phỏng. |

Các quy tắc daily/intraday/threshold giữ proposal gốc; bổ sung episode và xử lý clock là đề xuất mới cần review. Nếu thay đổi material trước run, ghi amendment và seal mới, không sửa kết quả để khớp thiết kế.

Tháng 4 đang được dùng để calibration nên thống kê false alarms trên chính giai đoạn này chỉ là diagnostic nội mẫu, không phải đối chứng ngoài mẫu độc lập. Chưa đăng ký một tập non-event holdout đủ điều kiện. Curator cần khóa tập này cùng labels trước run; nếu tách một phần tháng 4 làm holdout thì phải sửa split và chọn threshold trên phần calibration còn lại trước khi chạy. May2021 là adverse-event candidate, không được tự gọi là thời kỳ bình thường. Thiếu đối chứng không được che bằng denominator zero hay precision mặc định 100%.

## Hợp đồng P04-02 → P04-03

Interface sau đây là **PROPOSED**, không phải API đang tồn tại. P04-02-S đã có Draft PR #52, HEAD `fa77aac27a5239c98769663ba85dc6d24977e4a2`, trong lúc chuẩn bị hồ sơ này. Implementation và CI chưa được Work nghiệm thu; references đến API mới vẫn PENDING, không coi là dependency đã accepted.

| Đầu ra cần review từ Codex P04-02-S | Tiêu chí Work kiểm tra | Dùng ở P04-03 |
|---|---|---|
| Observation/vintage/interval identity bất biến | Asset/chain/venue/quote/units và raw-vs-content hash không bị nhập nhằng | Chọn information set có lineage; không ép Terra thành Ethereum numeric chain ID. |
| Admission result có reason codes | `POINT_IN_TIME_ELIGIBLE`, `BLOCKED_INSUFFICIENT_AVAILABILITY_EVIDENCE`, `REJECTED` hoặc ánh xạ rõ từ enum nội bộ; không thiếu → zero | Mask và abstention, không tự promote historical fields. |
| Source event, bar end, publication, received/available, acquisition | Giữ timezone và precision; closure trước prediction; chính sách delay không tự sinh chứng cứ | Gate trước feature/model. Unknown time phải được xử lý rõ. |
| Revision và fit lineage | Latest **eligible** vintage tại cutoff; training-only transform fitting | Ngăn data revision và holdout leakage. |
| Synthetic temporal primitives | 12 vectors của Issue #50 và negative cases, deterministic replay | Chứng minh phần mềm theo toy assumptions, không chứng minh historical PIT. |
| Actual code/JUnit/CI/checksums | Đọc artifacts, đúng final HEAD, có preservation và coverage disposition | Chỉ nghiệm thu kỹ thuật; không thay protocol/run grant. |

Đối với hai giá legacy, yêu cầu admission không cho phép hourly-last của `[22:00,23:00)` được xem là dữ liệu đã có lúc 22:00. Với bảng mở rộng, backward-as-of không tự chứng minh raw minute aggregate đã hoàn chỉnh. Đây là yêu cầu khoa học chuyển cho Codex, không yêu cầu sửa implementation đang có bằng Work.

Surface đang đề xuất trong PR #52 phân biệt `AdmissionStatus.ELIGIBLE/BLOCKED/REJECTED/ABSTAIN` với `ValueStatus.AVAILABLE/MISSING/UNSUPPORTED/QUARANTINED`. Khi review cần ánh xạ enum admission sang nhãn nghiên cứu ở ledger, giữ reason code; `AVAILABLE` của giá trị không tự nghĩa là PIT-eligible. Các record `DatasetVintage`, `TimeInterval`, `SourceProvenance` và `RiskOutputPlaceholder.NOT_IMPLEMENTED` đã được đọc ở cấp contract surface, chưa kiểm tra toàn bộ implementation, tests hoặc artifacts. Không dùng references PENDING này để tuyên bố API được nghiệm thu; partial review không thay full technical review.

## P04-03 readiness

| Slice | Trạng thái | Prerequisites |
|---|---|---|
| P04-03-D: comparison/design | `DESIGN_PREPARED_PROPOSED` | Bản gốc + amendment + eligibility matrix, reviewer/curator còn chưa assigned. |
| P04-03-S: baseline implementation trên synthetic | `NOT_IMPLEMENTED — PACKAGE_NOT_ISSUED` | Issue riêng pin interfaces P04-02 đã nghiệm thu, vectors độc lập và quyền thực thi cụ thể. Không mở rộng Issue #50 thành predictor. |
| P04-03-H/P04-04: historical features/model/backtest | `BLOCKED` | PIT inputs được nghiệm thu; source-specific clock/labels/splits/thresholds sealed; protocol approved và historical run authorization riêng. |
| P04-05: exit simulation | `BLOCKED / NOT_VERIFIABLE` | Valid alert và lịch sử depth/state/access/fees/delay; protocol/permission riêng. |

Không ngăn thiết kế hoặc audit tiếp tục chỉ vì Gate A của Aave đang BLOCKED. P02-03-S vẫn là gói synthetic/offline riêng ở Issue #45. Không có thay đổi file hay quyền runtime của gói đó.

## Seal và evidence tối thiểu cho một run tương lai

Manifest seal cần hash inputs/vintages, source contracts, eligible masks, label/curator version, feature windows, fit scope, split/embargo, model/threshold/horizon, episode/matching rules, metrics và all registered variants. Ghi access log, lịch sử amendment, ai đã xem outcome; không coi một hash mới tạo là xóa hindsight. Chỉ cho historical run khi có quyết định approval và run scope tham chiếu đúng manifest. Phải lưu mọi failed/missing/late/false alert và nguồn không đủ điều kiện, không chỉ hình minh họa thuận lợi.
