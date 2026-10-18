> G1 follow-up: xem [G1 final evidence](g1/G1_FINAL_EVIDENCE_REPORT.md) và `g1/G1_FINAL_RESULT.json` tại PR26. Các status/coverage bên dưới là snapshot Phase00 trước follow-up, không phải verdict release hiện tại.

# Phase 00 — Commander Handoff

**Task status:** `PHASE00_READY_FOR_COMMANDER_REVIEW`.
**G0:** `COMPLETE_WITH_FINDINGS`. **G1:** `PACKAGE_PREPARED_FREEZE_BLOCKED`.
**Đề nghị:** giữ V1 candidate để đối chiếu; **chưa tạo tag/release**.

## Anchors và phạm vi

- V1 candidate/starting HEAD: `ee9b372823e5c636238efe73a4268a5439cf1f80`.
- Scientific Lock: `3f6e5302483681209e2408531eb5a15389f9fded`.
- Blueprint Lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Work branch: `research/v2-phase00-foundation`; base `feat/terra-model-v2`.
- Exact delivery commit và Draft PR URL được ghi trong GitHub PR handoff, tránh self-embedded commit hash.

Chỉ thêm hồ sơ/tool Phase 00. Không sửa mã V1, engine, Frozen/Oracle/Integration/registry, manuscript, bảy chương hoặc Codex-owned files. Không đọc/quản lý Canva, ảnh slide, PowerPoint hoặc tài khoản thiết kế. Không tạo literature mới, chạy simulation/Monte Carlo/full suite hoặc triển khai Phase 01.

## Deliverables

| File | Nội dung |
|---|---|
| `V1_RELEASE_INVENTORY.md` | Phân loại artifact, manifest, prior evidence và release gates |
| `V1_RELEASE_MANIFEST.json` | Draft release/checksum registry:925 tracked files,446 observed byte SHA256,479 tree-only; environment, declared/observed hashes, limitations và blockers |
| `V1_REPRODUCIBILITY_AUDIT.md` | Kiểm tra thực tế, các mức tái lập, hướng dẫn read-only và điều kiện đóng gates |
| `V2_RESEARCH_UPGRADE_BLUEPRINT.md` | Tám hướng nâng cấp; kiến trúc; reuse/revise/new/proposed; phép thử, kết quả âm và Phase 01–05 |
| File này | Quyết định đề nghị Commander |
| `verify_v1_baseline.py` | Công cụ nhỏ read-only: checksum, AST và5 existing pure tests; không gọi engine/network hoặc ghi artifact |

## Kiểm tra đã thực sự chạy

GitHub xác nhận candidate trùng integration HEAD, PR24 đã merge và chưa có tag. Trong925 tracked blobs, toàn bộ854 file Scientific Lock và878 file Blueprint Lock được bảo toàn, không đổi hoặc mất file nào. Đã xác minh446 file byte-for-byte với Git objects, phân tích cú pháp178 file Python và gọi trực tiếp5 hàm test HF/thanh lý qua `runpy`: tất cả đạt. Đây **không phải pytest run**; audit environment thiếu18 dependencies base/dev được khai báo.

Registry giữ48 records,44 accepted/4 disallowed và6 RQ. Cả29 source-provenance paths tồn tại;28 nguồn có observed SHA256 đều khớp. Source verification labels không thay đổi. Kiểm tra tĩnh manuscript đủ7 chương; DOCX có16 bảng gồm14 approved+2 phụ trợ,11 hình và8 native display equations; ZIP CRC tốt. DOCX SHA256 là `15e1ae5d04429bbcd456886f4002b4977738c38dad58a6856610a5b3209f4285`.

Kết quả rà trực quan126 trang và165 page references thuộc assembly audit **trước đây**. Phase 00 kiểm tra file identity/ZIP/XML, không render hoặc rà126 trang mới. Trong78 legacy checksum declarations:14 khớp exact bytes,61 khớp biểu diễn CRLF riêng,2 chưa byte-check,1 implementation mismatch. Không sửa hash để ép khớp.

Lệnh mới đã chạy:

```bash
python phase00_delivery/docs/research_v2/phase00/verify_v1_baseline.py \
  --repo phase00_cache/repo \
  --manifest phase00_delivery/docs/research_v2/phase00/V1_RELEASE_MANIFEST.json --smoke
```

Kết quả `PASS_SCOPED_CHECKS`:446 checksums,178 AST,5 pure tests;479 tree-only files không được tính byte-verified. Diff/scope và remote blob checks được ghi trong PR sau khi push. Prior reports72 replays/32688 HF traces/2186 events và pytest35/138/217 là các phạm vi lịch sử riêng, không cộng thành test count mới.

## Blockers trước release V1 scientific baseline

| ID | Blocker/ảnh hưởng | Điều kiện giải quyết |
|---|---|---|
| REL-01 | Candidate CI không tạo jobs; không có CI PASS tại anchor | Commander xử lý PR19 chỉ sửa CI, xác minh required jobs tại intended baseline; nếu candidate thay đổi, phát hành anchor mới |
| REL-02 | Python environment gốc chưa đầy đủ/resolved; container tags mutable | Recover environment có nguồn hoặc validate environment pin mới, lưu package/image hashes; không dựng giả lịch sử |
| REL-03 | Integration manifest builder SHA256 không khớp current LF/CRLF hoặc source `c113fc1…`; liên kết generator chưa đủ | Tìm exact generator object hoặc provenance erratum được Commander duyệt; không sửa Frozen/Addendum; chưa suy ra numerical corruption |
| REL-04 | Critical large CSV/checkpoints/archives mới có Git identity hoặc prior reports, chưa observed SHA256 đầy đủ | Đọc authorized complete archive, ghi exact byte hashes/domain và coverage; không cần simulation; vẫn công bố giới hạn row audit/replay |

Chi tiết exact paths/hashes/acceptance criteria nằm trong audit và manifest. Candidate [run38994362948](https://github.com/Doquocdung1609/DeFiStress/actions/runs/38994362948) failure với0 jobs. PR19 đang open, có [run38995096556](https://github.com/Doquocdung1609/DeFiStress/actions/runs/38995096556) success tại SHA khác;9 deselected không tính PASS. Không chuyển verdict nhánh đó sang candidate.

Giữ các giới hạn khoa học: một venue/snapshot/cohort; oracle giả định; eligibility khác execution và36 route-ineligible instances; vốn không recycle/non-split; arbitrage không có funded execution; Monte Carlo có điều kiện/severe tails; historical association khác nhân quả; Terra strict OOS âm; graph chưa full multilayer. LTV dùng255 danh mục khác cohort109; LT là USD danh mục, không USDC token. Template pending là final-submission gate riêng, chưa được giải quyết bởi việc lưu baseline.

## Kiến trúc, lộ trình và quyết định đề nghị

Pipeline đề xuất: **Historical Data → State Reconstruction → Scenario Engine → Lending/DEX/Stablecoin → Agent Execution → Dynamic Contagion → Independent Validation → Research Outputs**. Terra có nhánh dữ liệu/đánh giá riêng, không ép thành kết luận nhân quả chung với Aave. V1 đã có `early_warning_v2.py`, network và fork harness; sự tồn tại của các file đó không đồng nghĩa mục tiêu V2 đã đạt.

Phase 01 ưu tiên dữ liệu lịch sử, nhiều snapshot/pool và oracle; Phase 02 thực thi, tác nhân, vốn và arbitrage; Phase 03 mạng động/đối chứng; Phase 04 Terra early warning; Phase 05 OOS/cross-market/independent validation và công bố. PASS nghĩa là phương pháp và bằng chứng đạt tiêu chuẩn, không yêu cầu kết quả dương.

**Nhiệm vụ đầu tiên đề xuất:** Phase01-A — kiểm tra năng lực nguồn lịch sử và lập pilot catalog đăng ký trước với ít nhất3 blocks/2 pools, cùng source/availability/unit/quarantine controls; chưa chạy stress. Chờ Commander duyệt phạm vi trước triển khai.

Commander có thể nghiệm thu **hồ sơ Phase 00** với các findings trên, đồng thời giữ **V1 freeze chưa được cấp** đến khi các mandatory release gates PASS. Tag đề xuất `v1.0.0-scientific-baseline` chưa được tạo. Work không tự merge hoặc mở Phase 01.
