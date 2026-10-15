# P3_CROSS_AGENT_HANDOFF_CONTRACT

**Trạng thái: PROPOSED — AWAITING_COMMANDER_BLUEPRINT_APPROVAL.** Đây là hợp đồng phối hợp, chưa phải lệnh khởi chạy Codex hoặc chương 1.

Scientific input bất biến: `3f6e5302483681209e2408531eb5a15389f9fded`. Work branch đề xuất `research/p3-manuscript-blueprint-work` tách khỏi integration. Không sửa lock/numerical/source artifacts. Nếu integration HEAD đổi, tiếp tục dùng pin này tới khi Commander phát hành lock mới.

## Quyền ghi và handoff

| Owner | Được ghi | Không ghi |
|---|---|---|
| Work | `docs/manuscript_p3/work/`; blueprint, academic prose, caption/inference và self-review | Numerical registries, simulation code/results hoặc file Codex |
| Codex | `docs/manuscript_p3/codex/`; exhibit registry, extracts, plots, validation/reproducibility và technical review | Work prose/blueprint; không tự đổi luận điểm |
| Commander | Quyết định G0/chapter approval, scope change và lock | Không mặc định approval vì thời gian trôi qua hoặc test PASS |

Mỗi exhibit có handoff ID duy nhất `P3X-<proposed_manuscript_id>` trong plan. ID này là editorial/request ID, không phải scientific result mới. Mọi chỉnh sửa caption số học phải được trao đổi qua finding log, chủ file mới sửa. Nếu cần thay nội dung science, dừng và mở change review riêng sau quyết địnhCommander.

## Ma trận phối hợp theo chương

| Chapter | Work evidence request | Codex deliverable | Review status | Commander approval |
|---|---|---|---|---|
| 1. Giới thiệu và thiết kế vấn đề nghiên cứu | `REQ-CH01-EVIDENCE-v1`; P3X-T1.1 | `docs/manuscript_p3/codex/chapter_1/`: evidence pack + exhibit registry + technical review | NOT_STARTED; chỉ dự kiến sau G0/chapter authorization | PENDING |
| 2. Cơ sở lý thuyết và tổng quan nghiên cứu | `REQ-CH02-EVIDENCE-v1`; P3X-T2.1 | `docs/manuscript_p3/codex/chapter_2/`: evidence pack + exhibit registry + technical review | NOT_STARTED; chỉ dự kiến sau G0/chapter authorization | PENDING |
| 3. Khung mô hình và phương pháp nghiên cứu | `REQ-CH03-EVIDENCE-v1`; P3X-F3.1, P3X-T3.1, P3X-T3.2, P3X-T3.3, P3X-E3.1, P3X-E3.2, P3X-E3.3, P3X-E3.4, P3X-E3.5, P3X-E3.6, P3X-E3.7, P3X-E3.8 | `docs/manuscript_p3/codex/chapter_3/`: evidence pack + exhibit registry + technical review | NOT_STARTED; chỉ dự kiến sau G0/chapter authorization | PENDING |
| 4. Dữ liệu tái dựng trạng thái và kiểm chứng mô hình | `REQ-CH04-EVIDENCE-v1`; P3X-F4.1, P3X-T4.1, P3X-T4.2 | `docs/manuscript_p3/codex/chapter_4/`: evidence pack + exhibit registry + technical review | NOT_STARTED; chỉ dự kiến sau G0/chapter authorization | PENDING |
| 5. Kết quả mô phỏng và phân tích độ nhạy | `REQ-CH05-EVIDENCE-v1`; P3X-F5.1, P3X-T5.1, P3X-T5.2, P3X-F5.2, P3X-F5.3, P3X-F5.4, P3X-F5.5, P3X-T5.3, P3X-F5.6, P3X-F5.7 | `docs/manuscript_p3/codex/chapter_5/`: evidence pack + exhibit registry + technical review | NOT_STARTED; chỉ dự kiến sau G0/chapter authorization | PENDING |
| 6. Đối chiếu lịch sử và các mở rộng nghiên cứu | `REQ-CH06-EVIDENCE-v1`; P3X-T6.1, P3X-F6.1, P3X-F6.2, P3X-T6.2 | `docs/manuscript_p3/codex/chapter_6/`: evidence pack + exhibit registry + technical review | NOT_STARTED; chỉ dự kiến sau G0/chapter authorization | PENDING |
| 7. Thảo luận đóng góp hạn chế và kết luận | `REQ-CH07-EVIDENCE-v1`; P3X-T7.1, P3X-T7.2 | `docs/manuscript_p3/codex/chapter_7/`: evidence pack + exhibit registry + technical review | NOT_STARTED; chỉ dự kiến sau G0/chapter authorization | PENDING |

## Chapter evidence pack tối thiểu

- Work tạo `CHAPTER_N_EVIDENCE_PACK` trong work/ sau approval. Header ghi approved blueprint commit, scientific lock commit, chapter version và request IDs. Chỉ accepted claims nằm trong affirmative list; bốn excluded IDs lưu audit riêng.
- Codex trả pack tương ứng ở codex/chapter_N/, không ghi chung file: mỗi result/table/figure có path+commit+selector, original generator/source version, Git blob SHA và SHA256 với byte-domain; fields/axes/units/cohort/policy/sample denominator, plot-data extract và rendering source.
- Bảng: CSV+Markdown+sidecar. Hình: vector SVG/PDF, PNG300dpi, plot-data CSV, code và sidecar; schema/diagram không dựng data giả. Công thức: LaTeX/MathML và bảng ký hiệu/đơn vị, đối chiếu code timing và phạm vi, không thay toán mô phỏng.
- Mỗi caption trả lời: đo gì, loại bằng chứng, sample/unit, policy/cohort, được kết luận gì và giới hạn gì. Work chịu academic prose; Codex kiểm numeric semantics.
- Nếu không có result ID vì claim concept/code, dùng NOT_APPLICABLE với artifact/code locator. Nếu một ID được kỳ vọng nhưng chưa xác minh, dùng EVIDENCE_ID_PENDING và EVIDENCE_REQUEST; không tạo ID giống nguồn thật.
- Event sample chỉ từ trace/audit đã khóa, có event ID và trường dữ liệu thực tế; pseudonym hóa. Không tuyên Work đã đọc hai CSV lớn vì nhận summary/extract từ Codex.

## State transitions và checkpoint

`G0_REVIEW → COMMANDER_BLUEPRINT_APPROVED → CHAPTER_N_CP1 → CP2_DRAFT → CP3_TECHNICAL_REVIEW → CP4_WORK_SELF_REVIEW → CP5_REPAIR → COMMANDER_CHAPTER_N_APPROVED → CHAPTER_N_LOCKED`. Sau lock N, dừng chờ lệnh riêng cho N+1. Không có auto-advance, không cấp lock bằng một test flag.

CP1–CP6 và severity theo `P3_CHAPTER_ACCEPTANCE_RUBRIC.md`. Mỗi chapter lock packet phải có version, exact commit, accepted IDs, RQ coverage, citations, exhibit IDs, technical review, Work self-review, limitations và remaining nonblocking items. Commander là quality gate, không gọi Work self-review là external review.

## Xử lý thiếu bằng chứng

| Request | Tình trạng | Quyết định/điều kiện giải quyết |
|---|---|---|
| ER-G0-TEMPLATE | TEMPLATE_VERIFICATION_PENDING | Commander cung cấp/xác nhận nguồn mẫu trường; không chặn blueprint nội dung, chặn format final |
| ER-G0-LEGACY-TERRA | Optional, chưa cấp quyền thêm finding | Muốn tái dùng numerical fit/mechanism/stress cũ cần xác định vai trò trong 44 claims và artifact/caption; không chạy mô phỏng mới để lấp chỗ trống |
| ER-G0-RAW-READ | Preserved read limitation | Codex cung cấp extract có locator từ dữ liệu khóa nếu cần minh họa; thay scope phải Commander quyết định |

Mọi yêu cầu bổ sung ghi Request ID, affected chapter/exhibit/claim, missing path/selector, tác động khoa học, proposed static resolution, owner và trạng thái. Đang pending không được thay bằng một kết quả dựng. Thiếu dữ liệu cho figure không dẫn tới việc Work tự vẽ số hoặc mở simulation mới.

## Hợp đồng bảo toàn

- Chỉ 44 affirmative candidates làm nền kết luận; accepted Integration sets tách typed audit references. Giữ 35+13 IDs, sáu RQ nguyên văn, 30 S records/access và U01–U08.
- Không thay canonical/frozen/oracle/integration/numerical registry. Không nâng source verification, không claim xác suất thị trường, actual feed, nhân quả lịch sử, full multilayer hoặc realized loss.
- Phân biệt Work static reconstruction, Codex replay, Codex premerge và G0 content checks. Không cộng số tests của các lượt khác nhau, không tái chạy 10.000 paths.
- PR/branch Work chỉ chứa sáu G0 files. Không merge; không tạo chapter draft; chờ approval. GitHub handoff ghi output commit ngoài file để tránh self-reference.

**Điểm dừng: AWAITING_COMMANDER_BLUEPRINT_APPROVAL.** Commander cần phê duyệt cấu trúc bảy chương, claim allocation và exhibit/ownership plan trước khi cho phép Chương 1 CP1.
