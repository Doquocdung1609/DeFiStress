# CHAPTER_04_SELF_REVIEW_v1

**Trạng thái đề nghị:** `CHAPTER_04_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`.

Đây là tự rà soát học thuật của Work kết hợp kiểm tra nội dung và đối chiếu nguồn tĩnh bằng công cụ (`WORK_STATIC_SOURCE_AND_CONTENT_REVIEW`). Không phải external peer review, RPC validation mới hoặc một đợt lặp lại mô phỏng. Work chưa cấp `CHAPTER_04_LOCKED`; quyết định nghiệm thu thuộc Commander.

## 1. Nguồn và ranh giới thực thi

| Vai trò | Exact commit |
|---|---|
| Scientific Content Lock | `3f6e5302483681209e2408531eb5a15389f9fded` |
| Approved Blueprint | `8de52bebabef376be700836e6f93a92d7394d2c3` |
| Starting integration / Ch01–03 locked | `1ebd54b428c568ede7dda02bc04fd486e68a2e13` |
| Branch | `research/p3-ch04-full-manuscript-work` |
| Final Work HEAD | Exact SHA trong PR/Git handoff; không tự nhúng SHA chính file |

Đã kiểm GitHub: PR #18 merged tại starting integration và Commander comment `6209955661` cấp `CHAPTER_03_LOCKED — CHAPTER_04_FULL_DRAFT_AUTHORIZED`. Ba chương khóa được truy xuất toàn văn đúng ref và đối chiếu blob với bản đã đọc/biên soạn. Các source scientific và Blueprint giữ anchor riêng, không dùng default branch để thay thế.

57 file nguồn được truy xuất qua GitHub connector đúng ref và kiểm identity theo Git blob, gồm canonical snapshot, schema/loaders, pool/tick readers, registry/manifest, HF tables và audit records. Tác giả kiểm các selector dùng trong chương; không tính lại HF từng borrower, không đọc mọi raw cell, không chạy engine, full regression, RPC hoặc Monte Carlo. Danh sách file/hash nằm trong provenance audit.

## 2. Coverage và chức năng học thuật

| Mục Blueprint | Nội dung hoàn chỉnh | Self-review |
|---|---|---|
| 4.1 — 3 tiểu mục | Candidate discovery, RPC filter, 454/109, normalization, collateral flag, nominal/baseUSD, aggregate other assets, canonical pool và bounded tick window; F4.1 | Giải thích đường hình thành trạng thái, không chỉ liệt kê dữ liệu |
| 4.2 — 3 tiểu mục | Sáu-field RPC comparison, HF abs/relative/median/flags và nhóm đã khóa; T4.1; phép tái kiểm theo mốc; route/event units | Phân biệt observed HF, reconstructed HF và simulation-state audit; dành outcome policy cho Ch5 |
| 4.3 — 2 tiểu mục | Initial depth/Quoter, amount-out vs tick-counter semantics, version repair; oracle/fork/historical boundaries; T4.2 | Fidelity theo từng miền, không nhãn validated toàn hệ thống |
| 4.4 — 3 tiểu mục | Version precedence, input/engine version roles, hash domains, author-read scope và reproducibility/validity | Giữ các limitations có tác động; chuyển sang Ch5 mà chưa viết kết quả |

Đủ **4 mục cấp 2 và 11 tiểu mục cấp 3**, đúng nguyên văn và thứ tự Blueprint. Không tạo công thức hiển thị mới hay chép lại tám công thức Ch3. Các phép tính HF/DEX chỉ được nhắc để giải thích quy trình tạo/đối chiếu dữ liệu.

## 3. Claims, citations và exhibits

| Nhóm kiểm | Kết quả |
|---|---|
| Primary Ch4 | 1/1: `P2:C33`, phát triển về nguồn và phạm vi kiểm toán HF/event |
| Các accepted components dùng | 13: 11 P2 + 2 Integration; giữ nguyên primary/secondary allocation |
| Sáu RQ | Giữ nguyên phạm vi; nguyên văn ở sidecar từ registry, không viết lại hay lặp cả sáu câu trong main |
| Bốn disallowed | Có bảng safeguard; không làm affirmative premise trong manuscript |
| Literature | Sáu APA entries đúng P2; scope protocol/theory/transparency; không DOI/URL hoặc access upgrade mới |
| T4.1 | Bảng hoàn chỉnh 19 hàng, 6 cột; unit, denominator, locked value, selector và caveat |
| T4.2 | Bảng hoàn chỉnh 12 hàng, 5 cột; nguồn, người thực hiện/status, điều hỗ trợ và boundary |
| F4.1 | Mermaid provenance schematic có nhánh discovery/borrower/pool và checks, `SCHEMATIC_FROM_LOCKED_MODEL_SPEC`; chưa publication-rendered |

Các statistical details trong T4.1 có locked source: hai max từ Frozen và corrected-v2 summary; hai median từ snapshot-quality/research-summary và bảng HF đã có; subgroup38 và thresholdcounts từ canonical snapshot/Phase-3 audit. Không tạo MAE, CI hoặc subgroup analysis mới. T4.2 không đồng nhất static PASS với external/economic validity; local-fork giữ `UNAVAILABLE`.

Mapping G0 và owner được bảo toàn. Directive hiện hành cho phép Work tạo trực tiếp bảng Markdown/schematic từ nguồn khóa; việc đó chưa chuyển trạng thái rendering của Codex hoặc tự cấp acceptance kỹ thuật. `TEMPLATE_VERIFICATION_PENDING` tiếp tục áp dụng cho DOCX assembly.

## 4. Sửa chữa và phân biệt nguồn có mục tiêu

| Finding | Vị trí | Vấn đề phát hiện | Cách xử lý bản cuối | Bằng chứng kiểm lại |
|---|---|---|---|---|
| CH04-R01 | 4.1.1 | Nhãn “Top500” có thể bị đọc thành debt-size ranking; 454/500 thành market coverage | Đối chiếu orderBy ID/dedup/cap; chỉ gọi tập ứng viên giới hạn; 90.8% có mẫu số500 | `subgraph.py`, snapshot coverage, quality boundary |
| CH04-R02 | 4.1.1–2 | Dễ coi46 bị loại là failed reads hoặc tất cả454 thuộc route | Tách excluded46/failed0; portfolio454, WETH255, USDC182 và cohort109 | Snapshot coverage; `load_position` và cohort condition |
| CH04-R03 | 4.1.2 / 4.2.1 | File có USDC oracle price có thể khiến văn bản ngầm giả full USD normalization | Nêu other-debt residual trừ USDC danh nghĩa; other collateral là aggregate, account-weighted LT | `positions.py`, `real_snapshot.py`, schema; C35 |
| CH04-R04 | 4.1.3 | Biểu diễn L lớn đã được ghi theo khoa học, không nên đổi thành một raw integer có vẻ bit-exact | Sửa draft sang đúng `3.206024567373453e+18`; nói rõ serialized representation | Raw JSON/Decimal(str(...)); kiểm giá trị source trong lệnh content check |
| CH04-R05 | 4.2.1 / T4.1 | Max dễ thành typical error; “gần ngưỡng” dễ trở thành phân nhóm mới | Đưa median có nguồn riêng, group38 có exact locked selector; không suy identity precision/recall | Corrected-v2 quality, HF CSV, canonical validation, Phase-3 |
| CH04-R06 | T4.1 | Một số selector nháp dùng dấu rút gọn hoặc thiếu prefix | Sửa đủ `health_factor_validation.quality_flag_count` và `canonical_health_factor_comparison…` | Selector resolution trong audit/field map |
| CH04-R07 | 4.3.1 | Báo cáo lịch sử nói “sub-micro” chung, nhưng sai lệch ở50WETH là1.0029681713273774e-06; tick counts vẫn khác | Dùng đúng số của cặp50WETH; giữ amount-out PASS/limited counter, không all-below-one-micro | Phase-2 quotes và status |
| CH04-R08 | 4.2.2–3 / 4.4.2 | Dễ biến32.688 hàng thành số ví, hoặc inherited audit thành new Work run | Ghi18×4×454 repeated observations; phân vai WorkP2/Codex/current author read | Integration manifest, summary, accepted C33/pre-merge |
| CH04-R09 | 4.4.1 | Báo cáo cũ cònPENDING/source input version cũ có thể bị đọc như trạng thái hiện hành | Giữ generation metadata và ưu tiên Scientific Lock/registry, tách snapshot creator khỏi engine version | Manifest/source registry và corrected-v2 summary |
| CH04-R10 | Audit / 4.3.1 | Registry depth giữ nhãnOBSERVED, trong khi độ sâu là giá trị tính từ observed state | Giữ nguyên nhãn nguồn; tách class của thành phần dữ liệu và phép suy dẫn trong câu viết | Frozen result row, source code depth, field provenance; không sửa registry |

Đã sửa các lỗi bản thảo/selector trong cùng nhiệm vụ. Những khác biệt đã khóa về aggregation, oracle và local fork được công bố đúng phạm vi; không sửa implementation để khiến nội dung “đẹp hơn”. Không phát hiện conflict mới cần thay scientific source hoặc mở lại Codex audit toàn bộ.

## 5. Các kiểm tra thực tế đã chạy

Lệnh authoring cục bộ `python build_chapter04_audit.py` tạo audit từ dữ liệu đã đọc, và `python verify_chapter04.py` kiểm nội dung/source identity. Scripts này là công cụ biên soạn cục bộ, không được thêm thành file repository; không phải test suite của engine. Bộ kiểm ban đầu phát hiện cách hiển thị active liquidity không giữ đúng biểu diễn JSON; đã sửa manuscript và chạy lại PASS.

| Nội dung kiểm bằng công cụ | Kết quả |
|---|---|
| Headings exact to Blueprint | PASS — 4/4 main +11/11 subsections, không heading rỗng |
| Data-field locators | PASS — 51 selector/value/unit/scope entries resolve trong source khóa |
| Canonical counts và HF values | PASS — block/454/109/46/0, Frozen maxima, median đã có và subgroup38 |
| Table structure | PASS — T4.1:19 rows×6 columns; T4.2:12 rows×5 columns |
| Quoter/pool fields | PASS — 5 locked quote sizes, exact50-WETH pair/error, limited tick-counter status; pool/token/spacing/window |
| Claim allocation | PASS —13 accepted components, primaryC33 1/1; các đích chapter khác giữ nguyên |
| RQ và disallowed guard | PASS —6 original questions trong audit;4 records không được dùng affirmative |
| P2 reference identity/access | PASS —6 exact APA entries, không URL mới, labels giữ nguyên |
| Source identity | PASS —57 Git blob checks; canonical Git LF content SHA256 khớp literal được pre-merge lưu |
| Long verbatim overlap | Không có đoạn văn dài main trùng nguyên văn Ch01–03 theo kiểm tra chuỗi |
| Scientific boundary | Không số tổng Wave2/MC outcomes hoặc census lịch sử ở main; không công thức hiển thị mới |
| Execution scope | Không new simulation/MC/RPC/full regressions/HF population recalculation |

Kiểm tra nguồn/hash chỉ xác nhận đối tượng được dùng đúng phiên bản. Độ sâu lập luận, tiếng Việt và cách đặt giới hạn được Work tự đọc/rà soát; không tự động suy từ PASS cấu trúc hoặc độ dài văn bản. Không tuyên kiểm GitHub CI hay một external review mới.

## 6. Phạm vi chưa xác minh và đề nghị Commander

Hai CSV borrower lớn vẫn chưa được Work đọc trực tiếp toàn bộ: Oracle `borrower_level_evidence.csv` và Integration `eligible_vs_executed_audit.csv`. Bản thảo dùng summary/registry/manifests và kết quả kiểm dự án đã khóa, phân biệt rõ tác giả hiện tại với người thực hiện pipeline. Canonical snapshot được truy xuất toàn bytes và kiểm metadata/fields cần dùng; không tuyên đã tái tính HF/kiểm từng reserve của mọi borrower trong lượt này.

Chưa có ma trận missingness toàn reserve, identity-level cutoff classification, phân rã nguyên nhân sai số từng ví hoặc cam kết phục hồi bit-exact mọi raw integer từ JSON. Những thiếu hụt đó được công bố mà không tự tạo số thay thế. Nhóm gần ngưỡng38 được dùng vì đã có source khóa, không là thí nghiệm bổ sung.

F4.1 còn là schematic; các bảng cần bước dàn trang và school-template verification khi hợp nhất DOCX. Nguồn giá oracle lịch sử, funded arbitrage và independent local-fork execution còn giới hạn như Scientific Lock. Một block/mẫu thu thập/một route/một pool và aggregate other assets không cho phép suy rộng toàn DeFi. Số census và kết quả Terra/network vẫn dành Chương6; không tạo kết luận dương mới về dự báo hay nhân quả lịch sử.

Commander có thể kiểm có mục tiêu: T4.1 selector/mẫu số và subgroup38; nominalUSDC residual trong borrower reconstruction; cửa sổtick600 và Quoter limited counter; phân biệt code-input version/hash domains; provenance của các hoạt động kiểm thừa kế. Không có critical field thiếu ngăn hoàn thiện chương; không phát hiện scientific blocker mới trong lượt static review.

Đề nghị nghiệm thu bản đầy đủ tại Draft PR, sau đó Commander quyết định merge và Chapter Lock. **STOP — AWAIT COMMANDER CHAPTER 04 REVIEW.** Chưa viết Chương5, chưa tạo DOCX, chưa tự cấp khóa.
