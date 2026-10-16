# P3_G0_RECONCILIATION_REPORT

**Recommendation: P3_BLUEPRINT_RECONCILED_READY_FOR_COMMANDER_REVIEW.** Work đã hoàn thành source/display mapping và tự rà soát nội dung. **Codex đã review starting HEAD; independent verdict cho final Work delta còn PENDING**; Commander cần verdict đó trước khi phê duyệt cuối. Không có chapter draft, rendering hoặc blueprint lock.

## 1. Phiên bản đã đọc

- Scientific lock: `3f6e5302483681209e2408531eb5a15389f9fded`.
- Work starting HEAD: `e26e2d5a21c6ac78bd4db7be345409b5c7690a80`.
- Codex reviewed HEAD: `f3ca9dcd3a8bc1c17ca336f880d5b0adf3b4866a`.
- Commander comments: [PR14/6197267439](https://github.com/Doquocdung1609/DeFiStress/pull/14#issuecomment-6197267439), [PR15/6197268184](https://github.com/Doquocdung1609/DeFiStress/pull/15#issuecomment-6197268184).
- Cả hai PR Draft/Open. Work HEAD giữ checkpoint; Codex có commit mới f3ca9dc sau preflight và đã được đọc trước push. Delta Codex thêm hai artifacts reconciliation, builder và tests; sáu G0 inputs và scientific lock không đổi. Final Work SHA được ghi ở GitHub handoff sau push.

Đã đọc sáu Codex G0 artifacts và năm Work baseline files trực tiếp qua GitHub tại đúng HEAD; 11 downloaded files khớp Git blob IDs. Đọc thêm hai Codex delta artifacts, `sim/research/aave_suite.py`, `scripts/research/run_deep_cascade_study.py`, `frozen_v3/tables/rq1_monte_carlo.csv`, `sim/schemas.py` và `sim/metrics/risk.py` tại đúng lock/ref để kiểm đơn vị và thành phần nợ. Không nghiên cứu literature mới, không chạy simulation, không sửa file Codex hoặc numerical registry.

## 2. Crosswalk bảng và hình

**25/25 displays**: 14 bảng, 11 hình/sơ đồ/composite; **11/11 Codex templates có ít nhất một đề xuất sử dụng**. Đây là quan hệ nhiều–nhiều. Status nói về mapping nguồn/spec, không phải rendering hay technical sign-off.

| Work ID | Chương/section | Codex reusable template | Mapping status | Cách tái dùng |
|---|---|---|---|---|
| T1.1 | 1/1.3 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Bảng văn bản lấy nguyên văn sáu RQ, không cần template số riêng. |
| T2.1 | 2/2.5 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Tổng hợp học thuật từ nguồn P2; Work sở hữu nội dung/citation, không tạo numerical estimate. |
| F3.1 | 3/3.1 | P3X:SYSTEM_FEEDBACK_SCHEMATIC | MATCHED | Tái dùng đúng template sơ đồ feedback và ký hiệu đường giả định. |
| T3.1 | 3/3.2 | P3X:SYSTEM_FEEDBACK_SCHEMATIC, P3X:METRIC_SEMANTICS_GLOSSARY | CODEX_SPEC_REQUIRED | Tái dùng nguồn về agent/metric; cần spec bảng agent-state/gate, không xem schematic template là bảng đã có. |
| T3.2 | 3/3.5 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Bảng thiết kế lấy từ selection manifest, bảng grid/prefix; không chạy lại thí nghiệm. |
| T3.3 | 3/3.3 | P3X:METRIC_SEMANTICS_GLOSSARY | MATCHED | Template glossary khớp chức năng định nghĩa và ranh giới metric. |
| F4.1 | 4/4.1 | P3X:CANONICAL_SCOPE_PROVENANCE | CODEX_SPEC_REQUIRED | Dùng nguồn canonical provenance để dựng lineage schematic; nguồn là bảng, rendition mới cần spec. |
| T4.1 | 4/4.2 | P3X:CANONICAL_SCOPE_PROVENANCE | CODEX_SPEC_REQUIRED | Canonical scope template chỉ hỗ trợ block/cohort; bổ sung HF errors từ source đã khóa, không giả template đã bao gồm validation. |
| T4.2 | 4/4.3 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Tổng hợp các kiểm tra/report đã có; tách executor và phạm vi, không numerical test mới. |
| F5.1 | 5/5.1 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Không có template Codex riêng cho grid; nguồn trực tiếp là bảng phân bố32/60 và Frozen F01. Chỉ dựng lại display từ counts đã khóa. |
| T5.1 | 5/5.2 | P3X:ORACLE_POLICY_DEPTH2_COMPARISON | MATCHED | Template policy counts khớp; giữ hai denominators4 và10 riêng, controls riêng. |
| T5.2 | 5/5.3 | P3X:ELIGIBLE_VS_EXECUTED | MATCHED | Tái dùng INT_T01/summary với eligible/executed/skipped; không đếm unique wallets. |
| F5.2 | 5/5.3 | P3X:ELIGIBLE_VS_EXECUTED, P3X:SYSTEM_FEEDBACK_SCHEMATIC | CODEX_SPEC_REQUIRED | Cùng evidence có thể tạo sơ đồ gate khác bảngT5.2; cần spec luồng và event-example locator, không tạo event mới. |
| F5.3 | 5/5.2 | P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS, P3X:ORACLE_POLICY_DEPTH2_COMPARISON | CODEX_SPEC_REQUIRED | Composite mới: haircut/depth2 cells và common postWave1 DEX/valuation; không đồng nhất với bảng arbitrage hoặc depth curve chưa có. |
| F5.4 | 5/5.3 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Capital/delay chưa có một template riêng trong11; dùng trực tiếp T06/F03 và fields đã khóa. |
| F5.5 | 5/5.4 | P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS | MATCHED | Chọn phần immediate/residual của template, nguồn T07/F04; không kéo thêm các kết luận về valuation. |
| T5.3 | 5/5.5 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Bảng RQ5 dùng trực tiếp T08; glossary chỉ là diễn giải, không ép gán thành template dữ liệu. |
| F5.6 | 5/5.6 | P3X:RISK_PARAMETER_MECHANISMS | CODEX_SPEC_REQUIRED | Template gốc là mechanism table; ba panels LTV/LT/bonus cần spec riêng, lấy các hàng T09 đã khóa. |
| F5.7 | 5/5.7 | P3X:SEVERE_POLICY_A_MONTE_CARLO | MATCHED | Tái dùng nguồn/figure prefix; cập nhật captionPolicyA, không tính CI mới hoặc cộng nested samples. |
| T6.1 | 6/6.1 | P3X:HISTORICAL_EVIDENCE_TIERS | MATCHED | Evidence ladder và census khớp template; không causal arrows. |
| F6.1 | 6/6.2 | P3X:TERRA_NEGATIVE_EARLY_WARNING | CODEX_SPEC_REQUIRED | Negative-finding table có thể thành hai panels count/lead; mỗi panel có đơn vị riêng, không vẽ timeline giả. |
| F6.2 | 6/6.3 | P3X:NETWORK_EXTENSION_BOUNDARY | CODEX_SPEC_REQUIRED | Boundary template và graph dùng cùng Git blob ở hai path. Chỉ dùng claim network đúng vai trò; C29 của template không được kế thừa làm chứng cứ cấu trúc. |
| T6.2 | 6/6.4 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Bảng phân tầng evidence là synthesis từ registry/report, không một phép kiểm mới. |
| T7.1 | 7/7.1 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Accepted-only RQ matrix là nguồn trực tiếp; không có nhu cầu numerical template mới. |
| T7.2 | 7/7.2 | Nguồn khóa trực tiếp | DIRECT_LOCKED_SOURCE | Bảng tổng hợp contribution/limits dùng claims và literature đã duyệt; không chấm điểm đóng góp mới. |

Status counts: **7 MATCHED, 10 DIRECT_LOCKED_SOURCE, 8 CODEX_SPEC_REQUIRED**. Không có EVIDENCE_PENDING hoặc DROP_RECOMMENDED cho displays đã chọn. **Unmapped Codex template IDs: []**. JSON crosswalk chứa caption, units, denominators, accepted claim/RQ IDs và exact commit/path/blob/selector cho từng display.

Hai đường dẫn structural_graph của Work/Codex cùng trỏ blob `8c980da9a10d1ef52f3b13cf8a14398b0e0cd75d`; crosswalk ghi rõ alias thay vì đánh đồng hai đường dẫn. P3E là evidence locator của rendering inventory, không phải scientific result hoặc scholarly source mới.

## 3. Đối chiếu công thức

**8/8 biểu thức Work được ánh xạ; 15/15 candidates Codex có disposition.** Giữ nguyên LaTeX Work từ starting plan: năm biểu thức thân bài và ba biểu thức phụ lục là đề xuất placement, không phải công thức hay kết quả mới.

| Work ID | Codex ID | Category | Placement | Source locator |
|---|---|---|---|---|
| E3.1 | P3F01, P3F02 | Protocol-shaped project implementation | 3.3.1 | `sim/lending/health_factor.py:5`; portfolio implementation `sim/schemas.py:29` |
| E3.2 | P3F05 | Protocol identity / inverse display transformation | Phụ lục A.1; dẫn từ3.3.2 | `sim/dex/uniswap_v3.py:26`, `:35` |
| E3.3 | P3F06 | Piecewise implementation identity | Phụ lục A.2; dẫn từ3.3.2 | `sim/dex/uniswap_v3.py:77` |
| E3.4 | P3F08 | Hypothetical project valuation policy | 3.4.1 | `sim/oracle.py:43` |
| E3.5 | P3F02, P3F13 | Project route/status definition | 3.2.2 | `sim/lending/liquidation.py:38`; `sim/engine/run.py:246`–`:287` |
| E3.6 | P3F15 | Statistical display definition | 3.5.3 | P2:C23; `data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json` |
| E3.7 | P3F15 | Locked Wilson implementation; display only | Phụ lục A.3; dẫn từ3.5.3 | `sim/research/aave_suite.py:211`; `scripts/research/run_deep_cascade_study.py:353`; `data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv` |
| E3.8 | P3F09 | Scoped analytical component identity | 3.3.1; áp dụng ở5.5.2 | `sim/schemas.py:25` |

| Codex candidate | Disposition | Placement | Scope/giải thích |
|---|---|---|---|
| P3F01 | MAIN_TEXT | 3.3.1 | Giữ HF; mã dự án là nguồn implementation. |
| P3F02 | MAIN_TEXT | 3.2.2 | Giải thích riêng HF eligibility và route eligibility. |
| P3F03 | PROSE_ONLY_UNIT_REVIEW_REQUIRED | 3.2.2;5.6.3 | Không thêm equation display. Repay là USDC token trong khi P_WETH được gắn USD/WETH; cần giữ quy ước baseline và giới hạn C35, không suy full USDC-depeg execution identity. |
| P3F04 | PROSE_ONLY | 3.2.2;5.3.1 | Giải thích lợi nhuận và các cổng bằng văn bản/bảng tác nhân; không thêm công thức hay mô hình cạnh tranh liquidator. |
| P3F05 | APPENDIX | A.1;3.3.2 dẫn chiếu | Chọn phần chuyển đổi giá ở phụ lục; giải thích tick rounding bằng văn bản theo mã. |
| P3F06 | APPENDIX | A.2;3.3.2 dẫn chiếu | Đặt chi tiết swap ở phụ lục để thân bài tập trung cơ chế tài chính. |
| P3F07 | PROSE_ONLY | 3.3.3;5.4;T3.3 | Định nghĩa immediate impact và residual bằng văn bản với denominator reference; không đồng nhất trường legacy max_price_impact. |
| P3F08 | MAIN_TEXT | 3.4.1 | Giả định valuation là một mắt xích quyết định, cần equation thân bài. |
| P3F09 | MAIN_TEXT_SCOPED_COMPONENT | 3.3.1;5.5.2 | Chọn thành phần USDC và giải thích nợ khác trong HF danh mục; không sửa công thức Codex. |
| P3F10 | PROSE_ONLY | 3.3.3;T3.3 | Uncovered debt là metric mô hình; không thêm phương trình hoặc realized-loss claim. |
| P3F11 | PROSE_ONLY | 3.3.3;5.6.2;T3.3 | Scenario LT và USD-equivalent trong định nghĩa metric khác cột USDC token của một số bảng xuất; caption theo đúng artifact. |
| P3F12 | NOT_NEEDED_AS_STANDALONE_EQUATION | T3.3 nếu chỉ tiêu được dùng | Không cần display độc lập. Nếu dùng amplification thì giải thích denominator bằng 0 là undefined và hai vế cùng đơn vị. |
| P3F13 | PROSE_WITH_STATUS_COMPONENT | 3.2.2;3.3.3;5.3 | Chỉ điều kiện positive-debt event hỗ trợ E3.5; depth và recovery được giải thích bằng văn bản. |
| P3F14 | PROSE_ONLY | 2.1.2;5.6;F5.6 | Giải thích ba cơ chế cùng các panels đã có; không thêm equation chỉ để tăng số lượng. |
| P3F15 | MAIN_TEXT_AND_APPENDIX | 3.5.3 vàA.3 | Tần suất k/n trong thân bài, Wilson ở phụ lục; chỉ dùng locked intervals. |

Các điểm cần giữ trong caption và technical review:

- **E3.2/P3F05:** nghịch đảo giá phải giữ token order và decimals; USDC/WETH không tự là USD/WETH khi USDC khác 1.
- **E3.5/P3F02/P3F13:** HF danh mục, tuyến khả dụng và positive-debt execution khác nhau; attempted không phải giao dịch broadcast.
- **E3.7/P3F15:** audit cho phép Wilson trên locked pairs nhưng không in toàn bộ biểu thức. Giữ nguyên biểu thức Work; primary provenance là hai implementations và bảng locked k/n/bounds. S24/NIST chỉ là background, không kiểm chứng code Wilson; không tính CI mới.
- **E3.8/P3F09:** biểu thức Work là phần nợ USDC; tổng nợ trong `BorrowerPosition.debt_value()` còn `other_debt_usd`. Bổ sung qualifier, giữ nguyên phương trình.
- **P3F03:** không chọn làm equation display. Repay USDC token và giá gắn USD/WETH cần quy ước baseline/C35; không dùng biểu thức như một mô hình thực thi depeg đầy đủ.

## 4. Rà soát chất lượng Blueprint

| Chương | Kiểm tra có mục tiêu | Verdict |
|---|---|---|
| 1 | Đặt vấn đề, mục tiêu và RQ; T1.1 chỉ định hướng, không đưa kết quả chi tiết | PASS_WORK_SCOPE |
| 2 | Đối thoại thiết kế/horizon/access của literature, tách scholarly/code/project evidence | PASS_WORK_SCOPE |
| 3 | Giải thích cơ chế, timing, policy và gates; chi tiết raw-price/tick/CI đưa phụ lục | PASS_WORK_SCOPE |
| 4 | Dữ liệu/cohort/HF khác kiểm chứng fidelity; không đồng nhất data quality với external validation | PASS_WORK_SCOPE |
| 5 | Giải thích cơ chế của sáu RQ bằng contrasts và các điều kiện mô hình | PASS_WORK_SCOPE |
| 6 | Lịch sử, negative Terra và structural network giữ ba vai trò bằng chứng khác nhau | PASS_WORK_SCOPE |
| 7 | Tổng hợp accepted claims và limits; không thêm numerical hoặc causal finding | PASS_WORK_SCOPE |

Giữ bảy chương, 44/44 primary destinations, bốn excluded records và sáu RQ nguyên văn. Phần outline gốc được giữ nguyên; chỉ thêm section reconciliation về ID, placement và references. Baseline audit vẫn đánh dấu thay các kết luận cũ về zero Wave2, Severe0/200, arbitrage không phản ứng và legacy reproduction pointers.

Cùng DOCX hash có 32 trang trong bản render LibreOffice của Work và 33 trang trong bản Word của Codex. Đây là khác biệt môi trường rendering, không là scientific conflict hoặc nguồn quy định trình bày.

## 5. Requests còn mở và gate tiếp theo

- **G0-REC-01 — PENDING_DISPLAY_SPEC; owner Codex:** Source/template reuse is grounded but these renditions/compositions exceed the 11 đặc tả template hiện có. Acceptance: Acknowledge each Work ID/section, exact filters/units/denominators and feasibility without new simulation/statistics; produce specification only, not rendered exhibits. Gate: Production/CP1 technical completeness; not content blueprint mapping.
- **G0-REC-02 — PRE_PRODUCTION_SEMANTICS_CHECK; owner Codex:** Inverse token-price convention, raw versus normalized swap amounts, route/status predicates, fullWilson typography and USDCcomponent versus portfolio debt require explicit review. Acceptance: Cross-verdict confirms declared domains and unchanged formulas; no additional CI or formula/model rewrite. Gate: Equation production/technical sign-off.
- **G0-REC-03 — P2_CATALOG_CLAIM_ASSOCIATION; owner Codex:** Template currently lists P2:C29 (time-series CV/validation). It does not support network topology. Work uses network C25/C26/C27/C28 and does not inherit C29 for F6.2. Acceptance: Correct or explain the catalog association on Codex branch; no change to locked C29 or Work files. Gate: Catalog reconciliation acknowledgement before final Commander gate.
- **G0-REC-04 — SCOPED_UNIT_NOTE_NOT_SELECTED_EQUATION; owner Codex:** repay USDC token × bonus / price labelledUSD/WETH needs baseline/peg convention; source implementation does not provide universal USDC-depeg seize repricing. Acceptance: Keep formula verbatim as implementation approximation, state unit/convention limitation C35; do not render a general depeg execution identity. Gate: Use of this candidate formula beyond prose; it is not selected for formal display.
- **G0-REC-05 — TEMPLATE_VERIFICATION_PENDING; owner Commander:** 2024report is a reference example; no authoritative current school-formatting regulation verified. Acceptance: Verify applicable template/rules before final DOCX; can approve content blueprint independently. Gate: Final DOCX formatting only.
- **G0-REC-06 — PRESERVED_LIMITATION; owner Codex/Commander:** Work has not fully read two large borrower CSVs; optional legacy Terra fit/mechanism/stress are not automatically affirmative additions. Acceptance: Use pinned summary/audit extracts with declared scope; request separate review for added findings, no invented data. Gate: Any new dependent extract/inference; does not block existing mapping.

**Scientific/numerical conflicts phát hiện: không có.** Hai lưu ý cần Codex xác nhận là association C29 trong network template và unit convention P3F03. Work không kế thừa C29 làm chứng cứ topology và không dùng P3F03 như equation tổng quát. Không sửa locked claims để làm khớp catalog.

**TEMPLATE_VERIFICATION_PENDING.** Ví dụ báo cáo năm2024 chỉ là tài liệu tham khảo, chưa xác minh quy định hiện hành. Thiếu template không chặn nội dung Blueprint, nhưng chặn final DOCX formatting. Hai raw CSV read limitations và toàn bộ scientific limitations giữ nguyên.

## 6. Kiểm tra và phạm vi thực thi

Lệnh `python verify_p3_reconciliation.py` **PASS**; `python verify_p3_codex_delta_adoption.py` **PASS**, kiểm thêm adoption 25/8, toàn bộ display controls, primary provenance E3.7 và năm freshly fetched Git blobs. Kiểm tra đầu tiên kiểm coverage25/8/15/11, source/claim/result IDs, template reverse assignments, formula text preservation, baseline outline preservation và bốn file output. Kết quả cuối ghi trong GitHub handoff. Đây là Work static checks và self-review, không phải lượt chạy lại Codex 217 pytest/17 targeted tests ở commit mới; đó chỉ là kết quả Codex tự báo cáo, Work không nhận là independent run.

Inventory Codex có67 entries:65 Git source paths và hai external DOCX. Work so 65 Git blob IDs với tree khóa, hai DOCX binary hashes với file đã cung cấp; không gọi đó là đọc toàn bộ raw source trong vòng này. Source verification levels không được nâng.

Files của vòng này:

1. `P3_G0_WORK_CODEX_EXHIBIT_CROSSWALK.json` — mới.
2. `P3_MANUSCRIPT_BLUEPRINT_v1.md` — chỉ thêm mapping/placement/references.
3. `P3_TABLE_FIGURE_EQUATION_PLAN.json` — thêm đồng bộ crosswalk/caption/placement, giữ nguồn và công thức cũ.
4. `P3_G0_RECONCILIATION_REPORT.md` — mới.

Đề nghị Commander nhận Work reconciliation và yêu cầu Codex chỉ kiểm delta tại final Work HEAD trước final approval. Không merge PR14/15, không render exhibits và không viết Chương1.

**AWAITING_COMMANDER_BLUEPRINT_APPROVAL.**

## 7. Final delta sau Codex review mới nhất

Codex review [PR15/6197557479](https://github.com/Doquocdung1609/DeFiStress/pull/15#issuecomment-6197557479), artifacts tại `f3ca9dcd3a8bc1c17ca336f880d5b0adf3b4866a`, đã đối chiếu **Work starting HEAD**, không phải commit Work cuối sắp push. Nhãn trước đó `P3_G0_TECHNICAL_REWORK_REQUIRED` là hold provenance/metadata; Codex xác định 0 unsupported displays. Work không tự đổi verdict của Codex.

| Finding | Work delta | Recheck còn lại |
|---|---|---|
| G0-X01 | Adopt/mirror 25/25 primary template links và 8/8 primary formula links; Work additional context được typed riêng; source/result/owner/chapter đủ | Codex verify final delta |
| G0-X02 | E3.7 primary locators là `_wilson` tại aave_suite:211, run_deep_cascade_study:353 và locked rq1_monte_carlo.csv. Literature chuyển background; không đổi LaTeX/bounds | Codex verify pointers/scope |
| G0-X03 | Embed nguyên văn display controls cho toàn bộ 25 hàng; T4.1 bỏ subgroup gần ngưỡng; bốn hình có production constraints dưới đây | Codex verify specification, không render |

- F5.2: predeclare executed/skipped category; sort stable case then pseudonymized borrower keys, chọn nhỏ nhất mỗi category; pin event/trace ở CP1 trước rendering; không manual cherry-pick. Không có locator thì chỉ giữ schematic tổng hợp.
- F5.3: canonical chỉ tại 0%; haircut dương là phản thực, 90/95% extreme tails; tách cell counts và USD/WETH.
- F5.6: USD capacity, USDC-token unliquidated debt và WETH seized ở các facets/trục riêng, giữ scenario LT semantics.
- F6.1: zero HIGH-alert hours và −45-hour lead là hai đại lượng; panels riêng, giữ kết luận cutoff-safe/OOS âm.
- T4.1: maxima không là typical error; bỏ optional near-threshold detail khi chưa có locked locator.

Codex technical classes **10 renderable/3 schematic/8 synthesis/4 needs-display-spec** khác Work mapping status **7 matched/10 direct/8 Codex-spec**. Không có mâu thuẫn số lượng: synthesis/schematic có thể vẫn cần xác nhận rendition. Các contextual links mới cho T3.2, F5.1 và T4.2 được thêm trong JSON; bảng ở mục 2 giữ vai trò nguồn chính trực tiếp, không ngụ ý template oracle tạo dữ liệu grid. E3.1 thêm P3F02 cho cổng HF; E3.5 primary P3F02, P3F13 chỉ semantic context positive-debt event.

**Recommendation giữ `P3_BLUEPRINT_RECONCILED_READY_FOR_COMMANDER_REVIEW`; final Work delta technical verdict còn PENDING. TEMPLATE_VERIFICATION_PENDING. AWAITING_COMMANDER_BLUEPRINT_APPROVAL.**
