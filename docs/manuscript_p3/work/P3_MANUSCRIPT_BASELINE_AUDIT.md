# P3_MANUSCRIPT_BASELINE_AUDIT

**Decision đề nghị: P3_BLUEPRINT_READY_FOR_COMMANDER_REVIEW.** G0 source/baseline audit đã thực hiện; chưa có chapter draft hoặc chapter lock.

## 1. Baseline và nguồn ưu tiên

Scientific lock: `3f6e5302483681209e2408531eb5a15389f9fded`. Registry v1.1 có 48 records: 44 accepted candidates và 4 excluded. Chỉ 44 candidates với mandatory limitations được phân bổ. Quyết định Commander ở Issue #3, comment 6186533199 là authority; các status “unmerged/not locked” trong lịch sử P2 không là trạng thái hiện hành.

Đã truy xuất bằng GitHub connector tại đúng pin 67 file nguồn; tải và kiểm Git blob bytes của từng file. Nguồn quan trọng gồm bảy registry JSON, hai narrative reports, bảy P2 files, Frozen manifest/results/claim ledger/evidence matrix, Oracle selection/comparison/report, Addendum summary/result/RQ/table registry, premerge audit, final consistency review, Terra audit và network evidence. Danh sách chi tiết ở cuối file. Việc đọc file/report không đồng nghĩa tái chạy test hoặc mô phỏng.

Ba DOCX đã được đọc toàn bộ text và bảng bằng OOXML, giữ thứ tự document body. Locator `[n]` dưới đây là zero-based body-block ID trong lần trích xuất, **không phải page number**. Render báo cáo chính tạo 32 trang trong môi trường kiểm tra; đã xem trang 1 và 15 như kiểm tra bố cục đại diện, không tuyên visual QA toàn bộ 32 trang. Không sửa ba file nguồn.

| File đính kèm | SHA256 file bytes | Nội dung kiểm kê | Vai trò |
|---|---|---|---|
| 01-DeFiStress_BAO_CAO_NCKH_HOAN_CHINH.docx | `9c8486027efcd35fe8fbcb8ba4c9fd6cfb714d2785f40ca6a64c247627dceb96` | 349 paragraph blocks; 22 table blocks; 17 embedded media; 0 OOXML math objects | Bản thảo năm chương |
| 06-DeFi_Stress_Lab_Mo_Dau_Tong_Quan_Nghien_Cuu.docx | `582d489189a156f00a563d22b6db36caab8094d7a3581d220b96d8b3f1aebdd5` | 106 paragraph blocks; 8 table blocks; 0 embedded media; 0 OOXML math objects | Proposal/literature sơ bộ |
| 07-DeFiStressLab_Spec_v1_2026.docx | `f1e42ad6a23246f65c3a921e2f7fd70a7c6bf9b9f62ff7ddbdc45b5061fca03a` | 104 paragraph blocks; 25 table blocks; 0 embedded media; 0 OOXML math objects | Product/technical design intention |

Báo cáo chính có 5 Heading 1 nội dung: Giới thiệu; Cơ sở lý thuyết và tổng quan; Phương pháp; Kết quả; Thảo luận/kết luận. Phần mục lục có thể hiện numbering/page cache cũ; không dùng cache làm cấu trúc/đánh số chuẩn. Có 22 table blocks nhưng chỉ 17 bảng nội dung được đánh số; 14 figure captions so với 17 media parts (có tài sản bìa), vì vậy không coi 17 media parts là 17 figures nghiên cứu. Công thức HF hiện là plain text, chưa có OMML equation.

## 2. Kết quả kiểm toán nội dung

- **Dùng lại:** vấn đề liên thông lending/DEX; giải thích LTV/LT/bonus; ý tưởng cùng block; vốn không recycle; RQ5 debt valuation; Terra warning âm; phạm vi mạng con. Giữ sau khi gắn locator và qualifier.
- **Đã lỗi thời:** RQ1 không có Wave 2 là kết luận chung; Severe 0/200 và kết luận tất cả 200 runs không có cascade; RQ4 không phản ứng; mô tả chỉ MC 200 đường và thời gian recovery cũ; commit/command ở Phụ lục 2. Thay bằng nguồn khóa, không chỉnh kết quả cho khớp lý thuyết.
- **Thiếu:** A/B/C như counterfactual policies; eligible/evaluated/executed/skip boundary và 36 route skips; historical 28/27 + tiers 1/2/23/1; provenance hiện hành; source access/two-CSV limits; economic dialogue với S13; một discussion tích hợp giải thích cả kết quả có và không có cascade.
- **Trùng:** Lời mở đầu với 1.1/1.5; gap cuối Chương 2 với đóng góp Chương 5; 4.11 với Phụ lục 1; số liệu mô phỏng nhắc lại trong discussion. Đề xuất giữ một nơi giải thích đầy đủ, nơi khác dẫn chiếu chức năng.
- **Diễn đạt cần sửa:** “mạng nhiều lớp” → đúng khung lý thuyết hoặc graph gộp; ABM không được suy nhiều bot hiệu chỉnh; quy tắc giá cập nhật không là oracle thực tế; local fork là kế hoạch chưa được kiểm chứng; composite exposure không phải realized loss.

## 3. Ma trận chuyển năm chương sang bảy chương

RETAIN là giữ phần luận giải phù hợp, không xác nhận mọi số/citation cũ; RELOCATE giữ vai trò nhưng đổi vị trí; REVISE sửa nội dung có mục tiêu; REPLACE_WITH_LOCKED_EVIDENCE thay nguồn số/diễn giải; REMOVE_AS_UNSUPPORTED chỉ loại suy luận không được hỗ trợ khỏi prose mới, **không xóa file nguồn**.

| Existing section / locator | Scientific status | Proposed new section | Rewrite scope | Evidence anchors |
|---|---|---|---|---|
| Bìa/tóm tắt/mục lục [0–106] | REVISE | Front matter sau bảy chapter locks | Giữ tên đề tài, không suy quy chuẩn PTIT; thay abstract theo accepted findings; TOC/LOF/LOT dựng lại ở assembly | C31; Registry 44 accepted |
| Lời mở đầu [108–111] và 1.1 [113–116] | RELOCATE | 1.1–1.2; đối thoại ở 2.5 | Gộp phần lý do trùng lặp; sửa phản hồi giá thành policy-conditional, không gán literature xác nhận mã | C01/C09/C10/C11/C32 |
| 1.2 mục tiêu [117–124] | REVISE | 1.3 | Giữ mục tiêu thực nghiệm; Terra/network là extension, không mở thêm RQ; bỏ lời hứa forecast/fork thành công nếu có | C17/C31 |
| 1.3 sáu RQ [125–131] | REPLACE_WITH_LOCKED_EVIDENCE | 1.3.2 | Bản cũ dịch/paraphrase và có lỗi “Chi phí phí”; dùng nguyên văn sáu research_question của registry | six_rq_accepted_claims_matrix.json |
| 1.4 phạm vi [132–134] | RETAIN | 1.4; dữ liệu ở 4.1 | Giữ block và phân biệt 454/109 sau kiểm nguồn; không dùng sample này làm toàn thị trường | AAVE_SNAPSHOT_BLOCK/AAVE_VERIFIED_BORROWERS/AAVE_WETH_USDC_COHORT |
| 1.5–1.6 [135–138] | REVISE | 1.4–1.5 | Giữ ý nghĩa nghiên cứu có giới hạn; đổi mô tả năm chương thành phương án bảy chương chờ approval | C31 |
| 2.1–2.2 [140–145] | RETAIN | 2.1; phương trình đầy đủ ở 3.3 | Kế thừa định nghĩa; bổ sung HF danh mục và eligibility khác execution, LTV/LT/bonus khác nhau | C01–C06 |
| 2.3 AMM [146–148] | REVISE | 2.2;3.3 | Giữ concentrated liquidity; tách impact, residual và oracle transmission; không suy trực tiếp Mainnet cascade | C07–C13/C32/C34 |
| 2.4 stablecoin [149–150] | REVISE | 2.3;5.5 | Giữ debt valuation và giới hạn; sửa tác giả BIS Papers 141 từ CPMI sang nhóm tác giả theo S15 | C14/C15/S15/S16 |
| 2.5 network [151–155] | RELOCATE | Lý thuyết 2.4; mô hình 3.1; extension 6.3 | Khung multilayer là lý thuyết; graph hiện tại aggregated typed graph; hình feedback phải thêm policy gate | C25–C28/C32 |
| 2.6 ABM/MC [156–158] | REVISE | 2.4;3.2;3.5 | Sửa hàm ý nhiều tác nhân không đồng nhất được hiệu chỉnh; một liquidator/arbitrageur đại diện theo mã | C18–C24 |
| 2.7–2.8 literature/gap [159–164] | REVISE | 2.5;1.2 | Bổ sung đối thoại S13 và khác biệt benchmark/access; khoảng trống tích hợp trong bộ nguồn, không thiếu vắng toàn ngành | C09/C10/C11/C31 |
| 3.1 thiết kế [166–170] | RETAIN | 3.1;6.2 | Giữ hai ca phân tích riêng; Terra không xác nhận định lượng Aave | C17/C20 |
| 3.2–3.3 dữ liệu [171–177] | RELOCATE | 4.1–4.3 | Tách khỏi phương pháp quy tắc; thêm nguồn/chất lượng/provenance và đúng cohort | AAVE_SNAPSHOT_BLOCK/AAVE_VERIFIED_BORROWERS/AAVE_WETH_USDC_COHORT |
| 3.4–3.6 mô hình/biến/thiết kế [178–189] | REVISE | 3.2–3.5 | Thêm A/B/C, route gate, timing và định nghĩa metric; không coi bad debt là realized loss | C03/C19/C24/C32/C34/C35 |
| 3.7 MC [190–191] | REPLACE_WITH_LOCKED_EVIDENCE | 3.5;5.7 | Không mô tả chỉ 200 runs; phân biệt P0 v2/Level-3/prefix/targeted; Wilson khác adjusted Wald | C22/C23/RQ1_MC_SEVERE_DEPTH2_COUNT |
| 3.8 Terra [192–193] | RELOCATE | 6.2 | Phân biệt cutoff-safe, thiết kế event-informed và OOS; Bergmeir không chứng minh leakage-free pipeline | C29/C30 |
| 3.9 tái lập [194–195] | REVISE | 4.4; phụ lục tái lập | Bỏ tuyên “130 tests” như gate hiện hành; dùng provenance với executor/commit, không tái chạy/khẳng định tất cả checks độc lập | C20; validation_report.json |
| 4.1 HF [197–205] | RELOCATE | 4.2 | Có thể giữ cách giải thích cực trị HF sau đối chiếu; bảng/ảnh phải rebuild từ nguồn pin, không ảnh cũ không có sidecar | AAVE_HF_MAX_ABS_ERROR/AAVE_HF_MAX_REL_ERROR |
| 4.2 RQ1 [206–208] | REPLACE_WITH_LOCKED_EVIDENCE | 5.1 | Kết quả zero ở lưới 32 ô chỉ đúng miền cũ; bổ sung lưới 60 ô và Severe Policy A/Oracle sensitivity; bỏ kết luận chung chưa có Wave 2 | CL_INT_RQ1_POLICY_CONDITIONAL; RQ1_GRID60_DEPTH2 |
| 4.3 RQ2 [209–216] | REPLACE_WITH_LOCKED_EVIDENCE | 5.2 | Sức hấp thụ DEX khác đường truyền sang HF; sửa tổng quát hóa liquidity chỉ khuếch đại hậu quả | CL_INT_RQ2_TWO_CHANNELS |
| 4.4 RQ3 [217–225] | REVISE | 5.3 | Giữ ràng buộc vốn; tách processing delay/recovery và thêm eligible/evaluated/executed/skipped; 36 route skips | CL_INT_RQ3_PRESERVED/CL_INT_ELIGIBLE_NOT_EXECUTED |
| 4.5 RQ4 [226–227] | REPLACE_WITH_LOCKED_EVIDENCE | 5.4 | Thay kết luận arbitrage không phản ứng bằng immediate impact khác residual; không gọi repositioning là funded swap | CL_INT_RQ4_PRESERVED/RQ4_SPREAD_ARB100 |
| 4.6 RQ5 [228–235] | RETAIN | 5.5 | Giữ chiều debt-valuation khi các yếu tố khác cố định; số liệu và bảng/hình phải có locator pin, tách token/USD | CL_INT_RQ5_PRESERVED/C35 |
| 4.7 RQ6 [236–254] | REVISE | 5.6 | Giữ ba cơ chế; kiểm scenario LT/outcome units; không dùng legacy HF hoặc suy cấu hình tối ưu quản trị | CL_INT_RQ6_PRESERVED |
| 4.8 MC [255–262] | REPLACE_WITH_LOCKED_EVIDENCE | 5.7 | Bảng Severe 0/200 và tất cả kết quả đều zero đã lỗi thời; dùng 8/200 → 280/10.000 và 0/1.000 Low Liquidity; composite đuôi không phải ES của tổn thất đã thực hiện | C22/C23/C24 |
| 4.9.1 fit;4.9.3 mechanism;4.9.4 stress [264–268,277–292] | REVISE | 6.2 hoặc phụ lục nếu được duyệt | Không tự tái dùng các số fit/mechanism/100%collapse như affirmative finding mới; ưu tiên negative findings đã khóa. ER-G0-LEGACY-TERRA nếu cần giữ | C17/C30; artifact Terra chỉ supporting context |
| 4.9.2 warning [269–276] | RETAIN | 6.2.3 | Giữ âm initial-depeg; không cherry-pick+3h ởngưỡng0.90;  xác định derivedvalidation khác rawobservation | TERRA_PRE_DEPEG_HIGH_ALERT_HOURS/TERRA_INITIAL_DEPEG_HIGH_LEAD |
| 4.10 network [293–301] | REVISE | 6.3 | Giữ cấu trúc támnode nếu nguồn pin khớp; bỏ cách gọi toàn bộ analysis là full multilayer; centrality không là lossimpact | C25/C26/C27/C28 |
| 4.11 RQsummary [302–305] vàPhụ lục1 [363–364] | REPLACE_WITH_LOCKED_EVIDENCE | 7.1; phụ lục claim map | Một summary nguồn, không hai bảng trùng; thay RQ1/RQ4 kết luận cũ bằng accepted-only sets | six_rq_accepted_claims_matrix.json |
| 5.1–5.6 thảo luận/kết luận [307–345] | REVISE | 7.1–7.5 | Giữ economic interpretation có giá trị; cập nhật Policy A/negativecases/eligibleexecuted; không lặp nguyênCh5 | C17/C31;9 accepted Integration claims |
| Bibliography [346–362] | REVISE | Tài liệu tham khảo sau bảy chương | Đối chiếu từng mục với S01–S30; giữ DOI/URL đã duyệt, không thêm nguồn từ proposalUqueue | APA_REFERENCES_VERIFIED.md;source access labels |
| Phụ lục2 [365–370] | REPLACE_WITH_LOCKED_EVIDENCE | Phụ lục provenance/tái lập | Commit2b9a29f5 và lệnh có chuỗi “quy trình” không dùng như lệnh đã kiểm; pinLOCK vàCodex xác nhận command phù hợp, không chạy 10.000 paths | source_provenance_registry.json;C20 |
| Proposal §1–4,§8–10 | REVISE | 1.1–1.2;2.5;7.2 | Giữ câu hỏi kinh tế/tích hợp; FSB thuộcS29, các nguồn chưa duyệt giữUstatus; đổi “xác suất/tổn thất” thành đúng conditional metric | C01/C09–C13/C31;U01–U08 |
| Proposal §5–7 vàSpec §8–11 | REVISE | 3.1–3.6 | Đối chiếu ý định với code thực tế; không tự kế thừa heterogeneousbots/fundedarb/localforksuccess | C19/C20/C32/C34/C35 |
| Spec §3–7,§12–24 product/API/sprint/demo | RELOCATE | Phụ lục hệ thống nếu thật sự cần; phần lớn ngoài prose học thuật | Chỉ giữ điều giải thích scope/data/provenance; không biến API contract/roadmap thành phương pháp hoặc kết quả đã đạt | C20/C31 |
| Các lời hứa Spec về demo tất yếuWave2, fork, P(Cascade) ngoài đời | REMOVE_AS_UNSUPPORTED | Không đưa vào affirmative prose; ghi ý định lịch sử nếu cần | Không xóa file nguồn; loại đúng lời hứa khỏi bản thảo mới vì chưa được dữ liệu/registry hỗ trợ | EXCLUDED_CLAIMS_LEDGER;C19/C32/C34 |

## 4. Kiểm kê bảng và hình cũ

Tất cả captions bên dưới đã được thấy trong DOCX. Các dòng “Nguồn: nhóm nghiên cứu” hoặc tên CSV chưa kèm commit/hash/selector nên **chưa đủ provenance để đưa trực tiếp vào P3**. Chỉ kế thừa thiết kế giải thích; dữ liệu/exhibit phải đối chiếu nguồn khóa. Không nói tất cả bảng đều không có nguồn; chúng có nguồn mô tả, nhưng thiếu phiên bản có thể kiểm toán.

| Block | Existing caption | Disposition / destination | Provenance action |
|---|---|---|---|
| 154 | Hình 2.1: Vòng phản hồi rủi ro Aave V3 - Uniswap V3 | REVISE → F3.1 | Thêm policy/route gates; không feed Aave thực tế |
| 160 | Bảng 2.1: Tóm tắt các nhóm tài liệu liên quan | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 169 | Hình 3.1: Quy trình nghiên cứu và tái lập kết quả | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 172 | Bảng 3.1: Nguồn dữ liệu và độ phủ | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 182 | Bảng 3.2: Các biến và chỉ số chính | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 186 | Bảng 3.3: Kịch bản demo hội đồng | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 199 | Bảng 4.1: Đối chiếu hệ số sức khỏe | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 204 | Hình 4.1: Số vị thế nằm dưới các ngưỡng hệ số sức khỏe | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 211 | Bảng 4.2: Kết quả một số kịch bản Aave | REPLACE_WITH_LOCKED_EVIDENCE → Ch5 | Thay số/metric semantics cũ; policy/denominator/caption mới |
| 215 | Hình 4.2: Kết quả một số kịch bản Aave | REPLACE_WITH_LOCKED_EVIDENCE → Ch5 | Thay số/metric semantics cũ; policy/denominator/caption mới |
| 220 | Bảng 4.3: Kết quả RQ3 về độ trễ và vốn thanh lý | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 224 | Hình 4.3: Ràng buộc vốn của tác nhân thanh lý | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 230 | Bảng 4.4: Kết quả RQ5 về định giá USDC | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 234 | Hình 4.4: Định giá USDC và mức độ dễ tổn thương của vị thế vay | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 240 | Hình 4.5: LTV và hiệu quả sử dụng vốn trước khi vay | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 245 | Hình 4.6: Ngưỡng thanh lý và điều kiện kích hoạt thanh lý | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 250 | Hình 4.7: Thưởng thanh lý và kinh tế của quá trình thực thi | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 252 | Bảng 4.5: Tổng hợp RQ6 về LTV, ngưỡng và thưởng thanh lý | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |
| 256 | Bảng 4.6: Kết quả Monte Carlo | REPLACE_WITH_LOCKED_EVIDENCE → Ch5 | Thay số/metric semantics cũ; policy/denominator/caption mới |
| 261 | Hình 4.12: Rủi ro đuôi trong mô phỏng Monte Carlo | REPLACE_WITH_LOCKED_EVIDENCE → Ch5 | Thay số/metric semantics cũ; policy/denominator/caption mới |
| 265 | Bảng 4.7: Kết quả tái dựng lịch sử Terra | REVISE/DEFER → Ch6 hoặc phụ lục | ER-G0-LEGACY-TERRA: chưa duyệt numerical finding ngoài44claims |
| 270 | Bảng 4.8: Thời điểm cảnh báo sớm Terra | RETAIN_WITH_RECONCILIATION → F6.1 | Giữ negative initial-depeg, dẫn2TerraresultIDs, không cherry-pick+3h |
| 275 | Hình 4.8: Thời điểm cảnh báo so với các ngưỡng mất neo UST | RETAIN_WITH_RECONCILIATION → F6.1 | Giữ negative initial-depeg, dẫn2TerraresultIDs, không cherry-pick+3h |
| 278 | Bảng 4.9: Kiểm tra cơ chế phát hành LUNA | REVISE/DEFER → Ch6 hoặc phụ lục | ER-G0-LEGACY-TERRA: chưa duyệt numerical finding ngoài44claims |
| 283 | Hình 4.9: Kiểm tra cơ chế phát hành LUNA | REVISE/DEFER → Ch6 hoặc phụ lục | ER-G0-LEGACY-TERRA: chưa duyệt numerical finding ngoài44claims |
| 286 | Bảng 4.10: Kết quả kiểm định sức chịu đựng Terra | REVISE/DEFER → Ch6 hoặc phụ lục | ER-G0-LEGACY-TERRA: chưa duyệt numerical finding ngoài44claims |
| 291 | Hình 4.10: Kịch bản kiểm định sức chịu đựng Terra | REVISE/DEFER → Ch6 hoặc phụ lục | ER-G0-LEGACY-TERRA: chưa duyệt numerical finding ngoài44claims |
| 295 | Bảng 4.11: Chỉ số trung tâm mạng | REVISE → F6.2 | Typed/aggregated graph; verify node set/normalization, khôngcausalloss |
| 300 | Hình 4.11: Vai trò cầu nối trong mạng con Aave - Uniswap | REVISE → F6.2 | Typed/aggregated graph; verify node set/normalization, khôngcausalloss |
| 303 | Bảng 4.12: Ma trận trả lời sáu câu hỏi nghiên cứu | REPLACE_WITH_LOCKED_EVIDENCE → T7.1 | Accepted-only RQ sets, bỏ summarycũ về zero cascade và arbitrage không phản ứng |
| 319 | Bảng 5.1: Đóng góp và hạn chế chính | REVISE; map theo baseline matrix | Rebuild từ source pin + result/claim IDs; không tái dùng ảnh như data authority |

## 5. Citation audit và nguồn chưa duyệt

- Bibliography chính có16entries tạiblocks347–362; không dùng số lượng để đánh giá chất lượng. Chuẩn P3 là30 records S01–S30 đã duyệt, chỉ cite những nguồn thực sự dùng.
- **S15:** DOCX gán CPMI cho BIS Papers 141; P2 xác định Kosse, Glowka, Mattei và Rice. Sửa author–year và bibliography theo APA_REFERENCES_VERIFIED, không tự tra hoặc thêm DOI.
- **S24:** Wilson (1927)/Agresti–Coull (1998) trong DOCX không phải hai entries thuộc S24 hiện hành. Dùng record NIST đã khóa cho công thức Wilson; không nhầm Wilson với adjusted Wald hoặc tự mở kiểm chứng nguồn mới.
- **S10/S11/S13:** đối thoại theo horizon/thiết kế và access; tài liệu nền không xác nhận feedback hoặc mã của DeFiStress. Bổ sung S13vì market impact của nghiên cứu nguồn khác Wave 2 dưới Policy A.
- **S17/S18:** giữ hai phiên bản cùng study; không gọi đọc toàn văn JFE hoặc coi là hai nghiên cứu độc lập. S30 chỉ giới hạn việc viện dẫn cross-validation, không xác nhận pipeline cutoff-safe.
- Proposal viện dẫn FSB thuộc S29; các bài Lee/Perez/Gadzinski/Castillo nếu chỉ thuộc U01–U08 vẫn giữ unverified; không đưa vào findings như nguồn mới đã kiểm chứng. Spec S1–S11 là nhãn tài liệu kỹ thuật cục bộ, **không đồng nhất** với global S01–S30.
- Toàn bộ source access labels, DOI, URL và U queue giữ từ P2; author–year/APA là working convention, chưa được xác minh là quy định riêng của trường.

## 6. School requirements và blockers

**TEMPLATE_VERIFICATION_PENDING — REFERENCE_EXAMPLE_AVAILABLE.** Ngoài cây Git khóa và bảy attachments, Work đã tìm thấy và đọc trang 1–6/85 của `Báo cáo đề tài NCKH 01-2024-HV-TĐ.docx` (Library ID `libfile_3edd27becd388191a2a9ec94dcc6e6a5`). Đây là báo cáo cấp Học viện năm 2024, mã số 01-2024-HV-TĐ, về đánh giá ứng dụng công nghệ số, có phần mở đầu và bốn chương. Nó cung cấp ví dụ về front matter, mục lục và cấp heading; các trang đã đọc không phải văn bản ban hành quy định trình bày. Work không gọi đây là template bắt buộc của trường, không áp bốn chương cho P3, không khai đã đọc toàn bộ 85 trang hoặc xác minh font/margins/numbering từ văn bản trích xuất. Chưa truy xuất được tài liệu quy định chính thức có thẩm quyền để chốt format. Các PDF/PPT bài giảng đính kèm chưa được dùng làm nguồn quy định/citation ở G0.

Không thiếu nguồn quan trọng cho nội dung G0. Việc chưa xác minh template chặn chốt định dạng và Word final, không chặn Blueprint. Hai CSV lớn của Oracle/Addendum giữ trạng thái SOURCE_NOT_VERIFIED_IN_THIS_SESSION đối với phần Work chưa đọc đầy đủ; đọc summary/audit không đồng nghĩa đọc raw source. Các hình Terra fit/mechanism/stress cũ cần request có phạm vi trước khi tái dùng; không mở mô phỏng mới để lấp chỗ trống.

## 7. Nguồn GitHub thực tế đã truy xuất tại lock

Mỗi dòng dưới là file content truy xuất pin qua connector và Git blob SHA đã được kiểm tra; toàn bộ summary CSV được parse, các JSON được đọc/parse. Một số báo cáo chứa status lịch sử được giữ như hồ sơ lịch sử, không thay quyết định Commander hiện hành. Đây không là tuyên đọc lại toàn văn nguồn học thuật gốc, RPC, raw CSV hoặc simulation.

| Path tại lock | Git blob SHA | Scope |
|---|---|---|
| `data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json` | `bac44e61633b5efdde3665731ea69fbf4ca345e6` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/final_accepted_claims_v1/claim_evidence_crosswalk.json` | `312b72f23b0115d1de69eec2dc1a87b0f490070a` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/final_accepted_claims_v1/manifest.json` | `bad223e0859a4fe135dd4f7b48b78513ade88123` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/final_accepted_claims_v1/scientific_lock_readiness.json` | `a381359eeeff8cc9cd393d79f0f84138a17b6056` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json` | `fffe69d45f2c70e8f4cb781c8b521ef4cf6f1a45` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json` | `a6784fd7f1b7288c4f2177ff8ba102be5e01c81e` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/final_accepted_claims_v1/validation_report.json` | `3e467a7894589062791c3546050d59316b4bf2b2` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/claim_ledger.json` | `f8d095676f1a0e10b37206c851b4e229a5e563a1` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/evidence_source_matrix.json` | `ece34ff3c883ca17af3b2b55fc046ff0328e790f` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/manifest.json` | `5fa6f68d25dd4df88b042a7b31be014f8b46dd38` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/results_registry.json` | `6dde91fc11d189de8899c742b44fea9cf0f386ae` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/rq_answer_matrix.json` | `e7a3349f8ce70624973d6604b770ff853b8f63ee` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/network/severe_centrality.json` | `3551d5074181c45cb422e5de45db93e8147d1f39` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/network/structural_centrality.json` | `b3608bd848b0594ec86a70fbe28d5b94d2358fa7` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv` | `dee128ff278efe94895220aca5eccec4150c1cc4` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/oracle_transmission_diagnostic_v1/manifest.json` | `f9fe56ca2325dca85a8cfe580571cfc0964ce7f5` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/oracle_transmission_diagnostic_v1/result_summary.json` | `9d18021d15f2e85ebaa68d4b5b716fde7b32a86b` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/oracle_transmission_diagnostic_v1/scientific_interpretation.json` | `91075b9beef037c046abd3fdcfa3df469a70382d` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/oracle_transmission_diagnostic_v1/selection_manifest.json` | `1bb5bdea8be74c1e62dc89badbcb8cbae67b7bd3` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv` | `664eeac6d3d80a38dc4c2ca6c942070f09d8d9f8` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/scientific_integration_v1/integration_result_registry.json` | `64b78e13f87adcc9bcc70188ca692d4a4196bff1` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/scientific_integration_v1/integration_validation_report.json` | `c92c43e6a3cd68869e35736148ba2b53c7deb6ae` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/scientific_integration_v1/manifest.json` | `2c80327f45bcb1bc3173c0017718dc933410a0fd` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/scientific_integration_v1/six_rq_evidence_matrix.json` | `0f9707700e508a100bbe0ff845f54579d3d28733` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/scientific_integration_v1/table_figure_registry.json` | `c74345f75c02a4550151a0cf7802fa96fecdd202` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/scientific_premerge_audit_v1/audit_results.json` | `8bd88bd5a96388af2e20e83ad12d6a52665c48a0` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/terra/audit/final_metrics.json` | `662fcad4c302ee95d1b2e9e46a9f4d85fb9a1934` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/terra/audit/final_report.md` | `c51c4c2dc620dbc140efd6360577fbf62d34fe74` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/terra/audit/strict_oos_v2.json` | `51e518c4df02c935def0affbd8eb422ad0d3847e` | Connector content read; exact Git bytes verified |
| `docs/TERRA_ABM.md` | `02b3e0661b8da61e3c387ba8c032a0805f623f15` | Connector content read; exact Git bytes verified |
| `docs/TERRA_HAZARD_MODEL.md` | `00709f35608109d3c14000d9f4d86da115b10688` | Connector content read; exact Git bytes verified |
| `docs/research_final/APA_REFERENCES_VERIFIED.md` | `c76d7cf482565615a92fb17b888a392e4f8fd9cc` | Connector content read; exact Git bytes verified |
| `docs/research_final/FINAL_ACCEPTED_CLAIMS_REGISTRY_v1.md` | `0c3298c2cb8a7d2ed317bd04278811f054c3753d` | Connector content read; exact Git bytes verified |
| `docs/research_final/FINAL_CROSS_PR_CONSISTENCY_REVIEW.md` | `7e54828a39e05f9e41e9d2b206bcfa0402a6fb7a` | Connector content read; exact Git bytes verified |
| `docs/research_final/LEVEL2_FORK_VALIDATION.md` | `4baa8b825743cacd20b1586cff5fb05d1aad96c2` | Connector content read; exact Git bytes verified |
| `docs/research_final/LEVEL3_HISTORICAL_EVENT_STUDY.md` | `e56da602592dd53fe52c830a3ca05537179a9b7a` | Connector content read; exact Git bytes verified |
| `docs/research_final/LITERATURE_VERIFIED.md` | `6ebe0a11e915e942a422d02a0cc5b1d53b51ff3e` | Connector content read; exact Git bytes verified |
| `docs/research_final/METHODOLOGY.md` | `21e0f85f681f7cc826c757614adf71a61db83e0a` | Connector content read; exact Git bytes verified |
| `docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md` | `144c14e9d7fe1a567a5c694abb8a93c1a483ec13` | Connector content read; exact Git bytes verified |
| `docs/research_final/P2_CLAIM_EVIDENCE_CROSSWALK.json` | `932c25f633dee7bdb8cfcf9e6e2473b50f7c4ab3` | Connector content read; exact Git bytes verified |
| `docs/research_final/P2_ORACLE_RECONCILIATION.md` | `2bc140f47ea463a9394858ec8937a808d18eccd7` | Connector content read; exact Git bytes verified |
| `docs/research_final/P2_VERSION_RECONCILIATION.md` | `323958c95e8bb28b3fe66289332ba1f0f3ac69df` | Connector content read; exact Git bytes verified |
| `docs/research_final/REFERENCE_EVIDENCE_MATRIX.md` | `504ea91b046e6612c2840c6a434e740ce917b29f` | Connector content read; exact Git bytes verified |
| `docs/research_final/SCIENTIFIC_CONTENT_LOCK_REVIEW_PACKET.md` | `c2a25f45ddff2eed89c1394c0591674e3ee8d8e3` | Connector content read; exact Git bytes verified |
| `docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md` | `856768b29fd0cefa5caba5d5721dc759f025cdba` | Connector content read; exact Git bytes verified |
| `docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md` | `f3fd437b41d0feabacf01f6708ca65d3a738ef05` | Connector content read; exact Git bytes verified |
| `docs/research_final/TABLE_FIGURE_INDEX.md` | `9f278f62facf19f495f39c80c08c41037220d868` | Connector content read; exact Git bytes verified |
| `docs/research_final/TERMINOLOGY_VI.md` | `2ca1e29495e6183dfefaf8939e59e6c4eba574fb` | Connector content read; exact Git bytes verified |
| `sim/oracle.py` | `2ac37f923a4cc35bef95968d353f0724bfdbd3a5` | Connector content read; exact Git bytes verified |
| `sim/lending/health_factor.py` | `8d8cae6754e718856867ce3696498bd68134a294` | Connector content read; exact Git bytes verified |
| `sim/lending/liquidation.py` | `9f95f18e8aa52f48facbebe1b3bdc8f88c0f162a` | Connector content read; exact Git bytes verified |
| `sim/dex/uniswap_v3.py` | `4172eae06907ae8bf95a10e7e50463111d0eec3d` | Connector content read; exact Git bytes verified |
| `sim/engine/run.py` | `2b23c9ee88ee4976755e5f4795026e381d5fe497` | Connector content read; exact Git bytes verified |
| `sim/network/metrics.py` | `db7aca57029e973637e4969d3a20d5c61e2e330d` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json` | `c57615dbfe686863b366db648234cf0af1d6b8ca` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/core_facts.csv` | `52a074b9b8284221c5996d14d903504ee8abe414` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/historical_evidence.csv` | `ea2d04143baee6a2d561b588bd8174b6dbfbc64b` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/old_to_new.csv` | `81f00299500af9b96bc2ebed25cc31b796015431` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/rq1_deterministic_depth.csv` | `f0e80bc73735de7684feadd2cd3c82519331c033` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv` | `ea71db6f633b7e5df1f12cd3d9f2533e5d5f9438` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/rq2_liquidity.csv` | `d753e24d06d35cc6d31ab2ef07ea6740ce862edb` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/rq3_constraints.csv` | `0a51fb795e562c0276ac36903662be92d52ce86f` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/rq4_arbitrage.csv` | `1fdeb6b31a7537d79e9e8c9e97544dbf78bb4f2e` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/rq5_usdc_valuation.csv` | `3f36a867c750f90d5a88ae5b1b00eae6be151b6e` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/rq6_policy.csv` | `deab1f45c56d8c836fead08190faffb1a5000fd2` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/terra_limitations.csv` | `264d5294bd8da978f8718c15b9ca7bcb221c704b` | Connector content read; exact Git bytes verified |
| `data/processed/research_final/frozen_v3/tables/version_precedence.csv` | `c518d2fdf31f2e437c0662a7f64213b987d8e267` | Connector content read; exact Git bytes verified |

## 8. G0 kiểm tra và tự rà soát

Lệnh `python verify_p3_g0.py` đã PASS: sáu deliverables, bảy chương, 44/44 primary destinations, bốn excluded IDs riêng, 6/6 câu hỏi nguyên văn, 30 source records/access labels bảo toàn, 67 Git blobs và ba DOCX file hashes khớp. Có 14 bảng, 11 hình, tám công thức dự kiến; 5 mục READY về nguồn/cấu trúc và 28 mục CODEX_REQUIRED, chưa có render triển khai. Các result IDs, existing table/figure IDs và artifact paths trong plan đều resolve trong các registry/tree đã đọc. Academic review trongG0 là **self-review của Work**, không tuyên một reviewer độc lập mới. Codex review chưa thực hiện; Commander chưa duyệt Blueprint. Nguồn trong repository không bị sửa; chưa có chapter draft.

**Điểm dừng: AWAITING_COMMANDER_BLUEPRINT_APPROVAL.**

## 9. Findings tự rà soát G0 và targeted repair

| Finding | Vị trí | Nguyên nhân và sửa | Recheck |
|---|---|---|---|
| G0-SR01 | Exhibit plan | Loại FIGURE cần khác TABLE để yêu cầu vector output; đã sửa 11 figures và output contract | PASS — 14 TABLE / 11 FIGURE / 8 EQUATION |
| G0-SR02 | T4.1 existing evidence ID | Core facts thuộc T02, không phải T01 version precedence; đã sửa locator | PASS — existing ID đúng artifact |
| G0-SR03 | Blueprint/baseline | Bản nháp có ghi chú rút gọn khó đọc; đã biên tập nhiệm vụ tiểu mục và chuẩn hóa khoảng cách | Work self-review hoàn tất; Commander quality review pending |
| G0-SR04 | School source status | Tìm được báo cáo ví dụ trong Library; đã đọc trang 1–6/85 và phân biệt với quy định chính thức | REFERENCE_EXAMPLE_AVAILABLE; TEMPLATE_VERIFICATION_PENDING |

Đây là các sửa G0-owned files; không sửa nguồn scientific lock. Không có review Codex, chapter approval, simulation hoặc tái chạy bộ tests khoa học trong lượt này.
