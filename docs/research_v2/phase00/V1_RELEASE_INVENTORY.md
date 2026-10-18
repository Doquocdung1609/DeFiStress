# V1 Release Inventory — Phase 00

**Candidate:** `ee9b372823e5c636238efe73a4268a5439cf1f80`
**G0:** `COMPLETE_WITH_FINDINGS` · **G1:** `PACKAGE_PREPARED_FREEZE_BLOCKED`
Đây là hồ sơ chuẩn bị baseline, không phải quyết định khóa hoặc tuyên bố toàn bộ V1 tái lập được.

## Phạm vi và phiên bản

GitHub xác nhận integration `feat/terra-model-v2` đang ở candidate; PR24 đã merge. Candidate chứa nguyên **854/854 file** của Scientific Lock `3f6e5302483681209e2408531eb5a15389f9fded` và **878/878 file** của Blueprint Lock `8de52bebabef376be700836e6f93a92d7394d2c3`: không đổi blob, không thiếu đường dẫn. Git compare xác nhận cả hai là ancestor, lần lượt cách24 và17 commits. Candidate có **925 tracked blobs**; cây recursive không bị cắt.

`V1_RELEASE_MANIFEST.json` là checksum registry máy đọc được: đủ925 đường dẫn/Git blob IDs, trong đó446 file có SHA256 byte thực tế đã xác minh;479 file còn lại ghi rõ `GIT_TREE_IDENTITY_ONLY`, không gán hash giả. Hash SHA-1 Git object khác SHA256 file bytes. Bản LF và bản biểu diễn CRLF có SHA256 riêng.

| Artifact | Path tại candidate | Commit/hash | Status | Reproducibility | Limitation |
|---|---|---|---|---|---|
| Mã mô hình Aave/DEX/oracle/agents | `sim/engine/`, `sim/lending/`, `sim/dex/`, `sim/oracle.py`, `sim/agents/` | Candidate; blob/SHA256 từng file trong manifest | Byte verified; không đổi từ Scientific Lock | AST và5 pure tests đạt | Không chạy engine hoặc replay |
| Terra models/data/cutoff tools | `sim/terra/`, `scripts/terra/` | Candidate; checksum registry | Source verified | Tái sử dụng có điều kiện | Tên `early_warning_v2.py` đã tồn tại ở V1; không phải bằng chứng dự báo thành công |
| Backend/adapters/state import | `backend/` | Candidate; checksum registry | Source/config verified | Chưa khởi động API/DB | Audit runtime thiếu dependency/service |
| Dependency/runtime | `pyproject.toml`, `backend/Dockerfile`, `docker-compose.yml` | Candidate | Đã đọc, có SHA256 | Chưa có Python resolver lock; image tags mutable | Không biết đầy đủ environment gốc |
| Frontend | `frontend/package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `.npmrc`, `Dockerfile` | Candidate; checksum registry | Lock/config verified | pnpm lock có; build không chạy lại | Frontend test/build thành công ở PR19 branch, không tại candidate |
| Canonical state | `data/processed/mainnet/aave_uniswap_snapshot_26045352.json` | LF SHA256 `76dae833c5b1a6e620cf116e332f1f47c53454a1f3530a02fefacd800cb3b329` | Byte/schema/count verified | Có thể kiểm tra offline |454 borrowers;109 WETH/USDC subset; một block26045352 |
| Canonical legacy checksum | Cùng snapshot | CRLF declaration `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99` | Khớp biểu diễn CRLF | Không phải hash byte LF thực tế | Không sửa source để làm test legacy PASS |
| Frozen v3 | `data/processed/research_final/frozen_v3/` | Scientific Lock; manifest + artifact checks | JSON/CSV/4PNG byte verified | Kiểm tra bảng/registry, không tái mô phỏng | Metadata cũ cần đọc theo accepted registry và CH05-P01/P02 |
| Severe checkpoints | `data/processed/research_final/level3_extension/deep_stress/checkpoints/` | Git blob IDs trong release manifest | Tree identity; báo cáo checkpoint validation đã đọc | Lần này không tái chạy/check toàn byte checkpoint lớn | Nested prefixes không độc lập;280/10.000 chỉ Severe Policy A |
| Historical route/census | `data/processed/research_final/level3_p1_targeted_repair/historical/` | Candidate | Census cache nhỏ, reconciliation/audit verified | Đối chiếu artifact đã lưu | Raw swap archive lớn chưa byte-check; không truy vấn archive RPC |
| Oracle Diagnostic | `data/processed/research_final/oracle_transmission_diagnostic_v1/` | Scientific Lock; manifest/checksum | Small matrices/reports verified | Không replay72cases | `borrower_level_evidence.csv` chưa đọc đầy đủ/quan sát SHA256 mới |
| Integration Addendum | `data/processed/research_final/scientific_integration_v1/` | Scientific Lock; manifest/checksum | Summaries/result registry verified | Builder source hash declaration có discrepancy REL-03 | CSV audit lớn chưa được Work đọc đầy đủ |
| Accepted Claims v1.1 | `data/processed/research_final/final_accepted_claims_v1/` | Scientific Lock |48records,44accepted/4disallowed;6RQ;29 provenance paths tồn tại |28/29 nguồn có SHA256 observed khớp | Một nguồn lớn chỉ tree identity; prior28gates không phải run mới |
| Literature/citation | `docs/research_final/LITERATURE_VERIFIED.md`, `APA_REFERENCES_VERIFIED.md`, ma trận/crosswalk/terms | Scientific Lock; blobs giữ nguyên |30S/35C/12aliases/92terms giữ nguyên | Không mở lại research/P2 verification | Access levels và U01–U08 không nâng cấp |
| Blueprint | `docs/manuscript_p3/work/P3_*` | Blueprint Lock; blobs giữ nguyên |7 ch/44 claim allocation/25 exhibits/8 equations | Cấu trúc đã được khóa | Source spec G0 khác chứng nhận render |
| Bảy chương chính thức | `docs/manuscript_p3/work/chapter_01/` … `chapter_07/` | Candidate; toàn văn/audits/self-review có SHA256 | Đủ7 ch, không thay đổi | Phân biệt chapter sources với bản hợp nhất | Báo cáo5ch cũ chỉ lịch sử, không làm baseline |
| Final manuscript | `docs/manuscript_p3/work/final_assembly/DeFiStress_FINAL_MANUSCRIPT.docx` | SHA256 `15e1ae5d04429bbcd456886f4002b4977738c38dad58a6856610a5b3209f4285` | ZIP CRC/XML đạt, byte khớp Git | Editable16tables/11images/8displayequations |126 trang visual QA là bằng chứng assembly trước; Phase00 không render lại |
| Final MD/audit/figures | Cùng `final_assembly/`; `figures/RENDER_PROVENANCE.json` | Candidate;26file assembly có byte hashes | Đủ14approved tables,11PNG+11SVG,8 equations | RQ giữ nguyên; nguồn caption đã lưu | Chưa có renderer script/environment hoàn chỉnh trong repository |
| Tests/CI | `tests/`, `sim/tests/`, `.github/workflows/ci.yml` | Candidate; test sources verified |178 Python AST PASS,5 pure tests PASS | Candidate CI failure/0 jobs | PR19 open có portable-suite PASS ở SHA khác |
| Fork validation | `contracts/validation/README.md`, `data/validation/validation_report.json` | Candidate | Status gốc đọc trực tiếp | `NOT_RUN_MISSING_ARCHIVE_RPC_AND_FOUNDRY` | Harness tồn tại không đồng nghĩa executed transaction validated |

## Release gates

| Gate | Hiện tại | Điều kiện đóng |
|---|---|---|
| Identity, preservation, không ghi V1 | PASS | Đã đối chiếu Git cây nguồn, byte checksums và diff Phase00 |
| Scientific inventory/limitations | PASS_SCOPED | Không đồng nghĩa full scientific rerun |
| CI tại baseline | FAIL — REL-01 | Required jobs chạy và có verdict đúng commit Commander chọn |
| Environment tái lập | INCOMPLETE — REL-02 | Resolver environment được pin/kiểm tra, không dựng giả lịch sử |
| Builder provenance | UNRESOLVED — REL-03 | Đối soát declaration với exact generator object hoặc erratum được duyệt |
| Checksum critical large artifacts | PARTIAL — REL-04 | Đọc byte từ clone/archive có quyền và bổ sung hash đúng domain |
| Commander freeze approval | PENDING | Chỉ xét tag sau khi mandatory gates PASS |

`TEMPLATE_VERIFICATION_PENDING` là giới hạn final-submission formatting còn giữ từ V1, không được đổi thành một phát hiện khoa học. Phase00 loại trừ Canva, slide images, PowerPoint và tài khoản thiết kế; không đọc các attachment ấy cho nhiệm vụ này. Chưa tạo tag/release.
