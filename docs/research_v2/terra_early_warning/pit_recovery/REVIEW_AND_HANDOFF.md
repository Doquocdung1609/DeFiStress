# P04-01 accepted & Terra PIT evidence recovery advanced

**P04_01_ACCEPTED_AND_TERRA_PIT_EVIDENCE_RECOVERY_ADVANCED** trong phạm vi review kỹ thuật, kiểm toán nguồn và thiết kế. Không phải hoàn thành demonstrator dự báo. Quyền `V2_TERRA_P04_01_REVIEW_AND_PIT_EVIDENCE_RESEARCH_AUTHORIZED`; parent [Issue #49](https://github.com/Doquocdung1609/DeFiStress/issues/49). Ngày 21/10/2026.

## Quyết định PR #51 và bằng chứng thực tế

Reviewed HEAD `8ec1eb2c49c1d4c3088b2bb0550b38fb6a05bde5`; starting integration `9207ead7db3acf1332b34cebcd19981c2f7bd9cc`. [PR #51](https://github.com/Doquocdung1609/DeFiStress/pull/51) đã merge thành **`053e94cb722f15eed689814c5a7771fa8f881be8`**, tree `aa35dbe8635e5ed7c218aa2d7e87d946b6c02c5f`, giữ đúng proposed tree. Cả 1.323 blob cũ giữ nguyên, chỉ thêm 10 tệp. V1 tag `v1.0.0-scientific-baseline` giữ tag object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`; tag annotated nhưng unsigned, không tuyên bố signature verification.

Đã fetch lại toàn bộ 10 file PR, đọc implementation/tests/workflow/registry, đối chiếu 35 source blobs với tree, SHA256, Gitblob và size. Đọc lại 8 schema/row counts Parquet bằng pyarrow19.0.1, không dựng feature hay rerun model. Tái chạy local 20 negative/boundary tests và 35 byte/CSV checks đều PASS. Ruff theo actual package-root/repository config và strict mypy một script PASS. Lần Ruff đầu dùng parent scratch làm import context báo I001; đã chạy lại đúng package context, không chỉnh rule hoặc bỏ lỗi. Các lệnh đúng đã được lưu trong conversation PR #51.

Không tìm thấy blocker P0/P1 cho phạm vi auditor này; không cần repair commit. Auditor không phải generic PIT admission engine: output BLOCKED cố định là giới hạn chức năng được công bố. Bytes/CSV audit không xác minh toàn bộ nội dung kinh tế Parquet, historical publication hay mọi hostile/concurrent filesystem scenario. Tests malformed, hash/CRLF, size-type, duplicate, missing, traversal, clock/order/header/width và failure-report được đọc trực tiếp. Không gọi synthetic PASS là historical forecast validation.

| Evidence | Kết quả đã đọc lại |
|---|---|
| Dedicated [39544374841](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39544374841) trên final PR HEAD | SUCCESS; 20 JUnit PASS, 35 nguồn PASS, PIT vẫn BLOCKED/0 trường; 3 checksum entries đúng |
| Repository [39544374812](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39544374812) trên final PR HEAD | SUCCESS; actual artifact/JUnit 552 pytest và 5 environment tests PASS; 21 frontend PASS, RPC tùy chọn SKIPPED |
| Integration [39555351447](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39555351447) trên **053e94cb…** | SUCCESS; actual JUnit 552 pytest, 5 environment tests, không failure/error/skip; 21 frontend, lint/build PASS; RPC smoke SKIPPED |
| Integration artifact 12325227345 | ZIP SHA256 `85f131adbe5a6d8c9967dd3e01840f33d0df0b8a5ce86608c5656730afcf9020`; CRC/member hashes/JUnit và source-preservation đã đọc lại; report gắn đúng integration commit, `changed_paths=[]` |
| Dedicated artifact 12320389585 | ZIP SHA256 `567c6a1e3d9aa0a980d62e3e3c6ccd6f0322836578f0ed049b7936383f567928`; runtime phân biệt workflow HEAD và synthetic merge checkout fd9f385… |
| PR repository artifact 12320912374 | ZIP SHA256 `543f5f8dd644d28a2ad1f3b77bb34592d1194e7ae4b79dfc2bdd422ed5b5ada2`; CRC/JUnit/member hashes và preservation đã đọc lại |

Đây là fresh tool-based reproduction và second-pass review của Work đối với audit do chính Work viết; không giả định có reviewer bên ngoài hay independent empirical replication. CI Windows3.12.10 clean-install evidence chỉ áp dụng target đã thử, không chứng minh mọi platform hoặc live RPC.

## Disposition của 10 findings

| Finding | Kết luận sau review | Việc cần trước dùng làm predictor/exit |
|---|---|---|
| TERRA-A01 availability/vintage | Bảo toàn; tìm được source semantics có phiên bản nhưng chưa có field-level availability | Original release/receipt/vintage proof hoặc bounded reconstruction được duyệt |
| A02 hour aggregation | Mã floor-to-hour và whole-hour sum xác nhận đúng | Interval completion + delay, raw event completeness |
| A03 aggregate prices | Giá vendor không phải bid/ask hay riêng Curve | Asset/venue/quote và minute-closure/vintage contract |
| A04 mixed frequency | Daily carried state khác minute inputs | Source age/frequency và common-support comparison |
| A05 participation | Mã renormalize active features và tự gán latest timestamp đúng như mô tả | Admission mask, minimum participation và abstention có spec |
| A06 22:00/23:00 | **Advanced:** đối chiếu raw rows xác định legacy hourly-last so với extended as-of; chi tiết file onset | Curated source/clock/sustained label; không chọn onset cho lead tốt |
| A07 volume/depth | Proxy và price alias không là executable venue evidence | Reserves/book/fees/access/delay; nếu thiếu NOT_VERIFIABLE |
| A08 supply units | Mã hình bổ sung dùng `/1e9` cho billion display; legacy denom conversion theo label khác normalized source | Schema/version/raw balance reconciliation trước rebuild; chưa đọc toàn bộ large balance pack |
| A09 strict OOS / hindsight | Kết quả âm V1 giữ nguyên; cutoff-safe không tự là prospective model selection | Outcome-known case và confirmatory study phải tách riêng |
| A10 controls | Non-event holdout chưa được khóa; calibration không là độc lập | Curator và đối chứng đủ điều kiện, tránh double-use tháng4 |

## Kết quả nghiên cứu nguồn mới

Đã đọc bốn tài liệu Git nguyên bản có hash: Binance websocket snapshot 09/03/2022, archive README 20/04/2022, README revision hiện tại pin 16/10/2026 và Anchor market schema 30/04/2022. Git commit date là metadata của phiên bản, không phải bằng chứng bất biến rằng từng market-data object đã public vào ngày đó. Tài liệu trước sự kiện giúp đặc tả event/bar/availability, không chứng minh current data tương đương vintage 2022. Ba file repository đọc bổ sung là builder legacy, importer và mã hình supply. Đây là phần bổ sung cho 35 file cũ được tái kiểm, không nâng cả 304 paths thành fully audited.

Đã đọc tài liệu chính thức về Anchor/Tendermint/Kaiko và nguồn chronology Jump; Nansen original URL lỗi404, Etherscan receipts bị403, archive index không truy cập được. Không vượt quyền, không mua nguồn, không giả lập acquisition thành công. Các failed attempts có trong ledger. Không tải archive market-data hay ZIP revision vendor; chưa xác định UST/LUNA có nằm trong danh sách thay thế đó hay không.

Source ledger có 11 hồ sơ; 14 core records vẫn `BLOCKED_INSUFFICIENT_AVAILABILITY_EVIDENCE`, 3 use cases legacy bị `REJECTED`; **không trường dự báo nào mới được admitted**. Clock discrepancy đã giải thích ở hai giờ có bằng chứng trực tiếp, không phải một kết quả warning/backtest mới. Hạn chế lớn về publication, vintage, pre-event intraday coverage và execution depth vẫn mở.

## Giao tiếp với Codex và readiness

[Issue #50](https://github.com/Doquocdung1609/DeFiStress/issues/50) đã nhận accepted integration pin **053e94cb…**, canonical handoff đã nằm trong integration. Nếu Codex đã bắt đầu từ8ec1eb2… thì tree dependency giữ nguyên; không reset/ghi đè công việc. Work chỉ thêm `docs/research_v2/terra_early_warning/pit_recovery/`; không sửa `defistress_v2/terra_pit/` hay tests Codex. Work không có callable Codex launcher, không tự nhận đã dispatch. Trạng thái implementation phải theo PR/CI thực tế Codex bàn giao; chưa có artifact triển khai mới trong lần kiểm tra này.

P04-03 chưa đủ historical readiness. Hợp đồng review P04-02 → P04-03 và comparison design ở amendment; gói acquisition riêng đang **PROPOSED**, không tự mở quyền chạy predictor. P02-03-S Issue #45 tiếp tục synthetic/offline độc lập, không đổi code/gates hoặc quyền H/N.

| Required progress gate | Trạng thái có căn cứ |
|---|---|
| `P04_01_TECHNICALLY_ACCEPTED` | **PASS_SCOPED_AUDIT**, merge + exact integration CI và artifact |
| `P04_02_SYNTHETIC_CONTRACTS_READY` | **HANDOFF_READY; IMPLEMENTATION_NOT_VERIFIED**, không đồng nhất ready order với code hoàn thành |
| `POINT_IN_TIME_DATA_ELIGIBLE` | BLOCKED, 0 core fields admitted |
| `EARLY_WARNING_PROTOCOL_APPROVED` | NOT_APPROVED; proposal + amendment reviewable |
| `HISTORICAL_BACKTEST_AUTHORIZED` | NOT_AUTHORIZED |
| `PRE_EVENT_ALERT_DEMONSTRATED` | NOT_DEMONSTRATED_IN_NEW_PROGRAM |
| `FALSE_ALARM_RISK_EVALUATED` | NOT_EVALUATED |
| `EXIT_FEASIBILITY_EVALUATED` | NOT_EXECUTED / NOT_VERIFIABLE |

Các tài liệu mới chỉ là audit/design, không historical features, onset-search, threshold fitting, warning, portfolio hay exit run. Complete target `TERRA_V2_EARLY_WARNING_RESEARCH_DEMONSTRATOR` vẫn NOT_YET_ACHIEVED. Đề nghị Commander review proposal/clock/curator/acquisition scope để có thể tiến tới một historical protocol hợp lệ, không yêu cầu chấp nhận trước kết quả dương. Rollback của nhánh nghiên cứu mới: reviewed revert riêng các file bổ sung, giữ history và V1.

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED**.
