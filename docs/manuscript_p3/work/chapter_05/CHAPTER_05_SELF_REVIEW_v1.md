# CHAPTER_05_SELF_REVIEW_v1

**Recommendation: `CHAPTER_05_TARGETED_REPAIR_REQUIRED`.** Toàn văn Chương 5 đã hoàn chỉnh để Commander review; hai sai khác metadata nguồn RQ6 cần được hòa giải trước khi đề nghị khóa. Đây là self-review của Work kết hợp kiểm tra tĩnh bằng công cụ, không phải phản biện độc lập bên ngoài hoặc chạy lại kiểm định của Codex.

## 1. Phiên bản và phạm vi giao

- Scientific Lock: `3f6e5302483681209e2408531eb5a15389f9fded`.
- Blueprint Lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Starting integration / Chương 4 đã merge: `30c6ce6859603460c8eb5a496e4f8c36f9339cf0`.
- Branch: `research/p3-ch05-full-manuscript-work`; final commit được xác định bởi Git và handoff trên PR.
- Chỉ ba file trong `docs/manuscript_p3/work/chapter_05/`: toàn văn, result/claim/citation audit và self-review này. Không thay scientific sources, Codex paths hoặc chương đã khóa.

## 2. Kết quả kiểm tra nội dung

| Tiêu chí | Kết quả thực tế | Giới hạn đánh giá |
| --- | --- | --- |
| Cấu trúc Blueprint | PASS: 7/7 mục và 19/19 tiểu mục, đúng heading và thứ tự | Không tự đổi đề cương |
| Sáu RQ | 6/6 có phân tích riêng, kết nối tại 5.7 | RQ6 có hai metadata findings chưa đóng |
| Primary allocation | 8/8: P2:C15 và bảy Integration claims của Chương 5 | Coverage không thay thế scientific acceptance |
| Accepted components sử dụng | 23 components: 16 P2 và 7 Integration; primary/secondary giữ allocation | Không dùng cả 44 claims chỉ để tăng coverage |
| Registry boundary | Giữ 48 records, 44 affirmative và bốn disallowed; không dùng disallowed trong bản văn như finding | Kiểm tra phía consumer; không chỉnh registry |
| Numeric locators | 47 result IDs resolve trong Frozen/Integration registry; 95 supplemental source-field entries đối chiếu trực tiếp | Không tính output mới |
| Exhibits | 10/10 đúng placement: F5.1, T5.1, F5.3, T5.2, F5.2, F5.4, F5.5, T5.3, F5.6, F5.7 | Không gọi đặc tả hình là hình đã render |
| Citations | 12 mục APA kế thừa nguyên văn từ P2; source/access/scope trong audit | Abstract/preview vẫn giữ đúng giới hạn |
| Chapter boundary | Không chép đoạn dài Chương 1–4; không viết Chương 6 | Có câu chuyển cuối chương, không mở nội dung mới |

F5.2 là Mermaid schematic từ đặc tả mô hình, không phải một borrower-event reconstruction mới. Ba bảng Markdown đã hiển thị. Năm hình có trạng thái `DISPLAY_SPEC_READY_NOT_RENDERED`; F5.6 có `DISPLAY_SPEC_WITH_PROVENANCE_REPAIR_PENDING`. Audit cung cấp dữ liệu điểm, trường, trục, đơn vị, selector, policy, caption và handoff cho cả mười exhibits. Rendering còn lại là công việc sản xuất hình; riêng F5.6 còn phụ thuộc hòa giải nguồn.

## 3. Self-review lập luận khoa học

**RQ1, mục 5.1:** Phân biệt hai lưới 32/60 ô, bốn selected deterministic cases, mười targeted paths và Severe Policy A 10.000 paths. Phân tích cả khả năng hình thành Wave 2 và những điều kiện chặn phản hồi. Không biến bốn ô quan sát thành một ngưỡng hệ thống hoặc ép kết quả đơn điệu theo shock; trường hợp −45% được công bố đúng raw grid và không gán nguyên nhân borrower chưa truy nguyên.

**RQ2, mục 5.2:** Tách DEX absorption khỏi valuation transmission. Case chung sau Wave 1 có giá DEX/định giá được trích đúng comparison matrix; không so cực đại của những đường đi đã phân kỳ như thể cùng lượng bán. Haircut dương được gọi phản thực, kể cả các hàng có nhãn nguồn `OBSERVED_BASELINE`. Không dùng A/B/C như oracle Aave/Chainlink thực tế.

**RQ3, mục 5.3:** Tách HF eligibility, newly eligible, evaluated/attempted, skipped và executed với debt repaid dương. Giữ số instances theo case-policy; không gọi là unique wallets. T5.2 trình bày A 35/35/14/21, B 0/0/0/0, C weak 6/6/0/6, C moderate 11/11/2/9. Tổng 36 skips có derived reason `NO_MODELLED_USDC_DEBT`; raw reason `NOT_ELIGIBLE` được giữ trong audit. Không suy khoản nợ đã được trả hết sau Wave 1 hoặc lỗi liquidator. Phân tích nguồn lực riêng theo thiết kế sensitivity, không áp nguyên nhân đó lên 36 skips.

**RQ4, mục 5.4:** Giữ immediate impact khác residual spread. Số ratio gốc có trong audit; phần trăm trong văn bản chỉ chuyển cách hiển thị đơn vị. Arbitrage là price repositioning cùng cập nhật trạng thái mô hình; không gọi funded swap hay profit on-chain. Repaid volume không đổi trong so sánh được công bố cùng với residual giảm.

**RQ5, mục 5.5:** Bộ đếm HF là trạng thái direct post-shock của cohort109, không phải bộ đếm sau tất cả liquidation. Lượng USDC đã hoàn trả và USD-equivalent được giữ thành hai cột riêng. Kết quả chỉ khảo sát debt valuation, không xác nhận full depeg dynamics. Planning/seize/profit còn quy ước nominal được nêu ở đúng giới hạn.

**RQ6, mục 5.6:** LTV điều chỉnh khả năng vay tính toán; LT điều chỉnh phân loại HF; bonus thay lượng tài sản chuyển giao và động cơ. Không suy governance optimum hoặc phản ứng vay thêm từ frozen debt. Những giảm trong unliquidated-debt metric tại LT cao được tách khỏi dòng tiền hoàn trả. Hai sai khác cohort/unit bên dưới được công bố; không được đóng acceptance bằng cách bỏ caveat.

**Độ bền, mục 5.7:** Nested prefixes không được gộp thành mẫu độc lập; robustness batches giữ seed riêng; Low Liquidity zero không biến thành xác suất thị trường bằng zero. Wilson bounds sao từ bảng đã khóa, không gọi adjusted Wald và không tính khoảng mới. Modeled bad debt và composite exposure không được gọi realized loss; p95/ES đã lưu không được đặt nhãn market VaR/ES đã hiệu chỉnh.

Đối thoại literature giữ đúng cấp bằng chứng: kết quả thực nghiệm S13 và stress phản thực Wave 2 có thiết kế khác nhau; nghiên cứu này không bác bỏ trực tiếp S13. S12 không là bằng chứng Aave dùng đấu giá; S14 không cung cấp hệ số hiệu chỉnh Tether cho WETH/USDC. Những source abstract/metadata/preview không được nâng lên fulltext. Văn bản ưu tiên cơ chế và kết quả trước điều kiện diễn giải, không mở mọi đoạn bằng lời phủ định.

## 4. Targeted repairs đã thực hiện

| Finding trong quá trình soạn | Sửa trong bản giao | Recheck |
| --- | --- | --- |
| Dễ nhầm ô −45% thuộc vùng depth2 | Dùng đúng bốn cặp shock/haircut; nêu tính không đơn điệu của phân loại, giới hạn giải thích nguyên nhân | Raw 60-cell grid đối chiếu trực tiếp |
| Dễ gộp control vào mẫu selected hoặc targeted MC vào frequency | T5.1 giữ ba mẫu số /4, /4 và /10; 5.1.3/5.7 tách batch10.000 | Policy summary và MC table khớp |
| Dễ gọi token repay là USD value khi q khác1 | T5.3 giữ bốn cột và giải thích bộ đếm HF | Bảy hàng đối chiếu từng ô với Frozen CSV |
| Dễ gọi haircut25–75% là quan sát lịch sử do raw label | Dùng approved crosswalk interpretation, giữ raw label trong audit | F5.3 và 5.2.1 thống nhất |
| Dễ mô tả sáu hình chưa render như hình đã có | Trạng thái/caption/đặc tả và dữ liệu điểm ghi rõ; không tạo ảnh giả | 5 ready specs + 1 pending spec; Mermaid riêng |
| Literal finding ID ở caption F5.6 bị viết tắt CH05-P01/P02 | Viết đầy đủ `CH05-P01` và `CH05-P02` | Kiểm tra ID trong cả main và audit PASS |

## 5. Hai findings chưa giải quyết, cần Commander quyết định

**CH05-P01 — P1, RQ6/LTV:** Frozen `results_registry.json`, results `RQ6_LTV0755_CAPACITY`/`RQ6_LTV0825_CAPACITY`, ghi population109. Artifact `validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.json` ghi `cohort_size=255`; code `run_ltv_capital_efficiency_analysis` chọn WETH collateral dương và tổng nợ dương. Values giữ nguyên. Cần trace và correction/precedence note có version cho population; bản thảo chưa khẳng định totals này thuộc riêng cohort109.

**CH05-P02 — P1, RQ6/LT:** Frozen `rq6_policy.csv`/results `RQ6_LT083_UNLIQUIDATED`, `RQ6_LT0855_UNLIQUIDATED` gắn đơn vị USDC token và population109. `sim/metrics/risk.py:unliquidated_debt` cộng portfolio `debt_value`, còn `run_liquidation_threshold_sensitivity` truyền positions rộng hơn bộ đếm `_hf_counts`. Các rows có USDC/USD=1; bằng nhau về trị số ở baseline không xác nhận cùng đơn vị hoặc cùng population. Cần xác nhận nguồn tạo metric và đồng bộ metadata/caption bằng quyết định có version.

Exact pinned permalinks, current/proposed wording và acceptance criteria từng finding nằm ở mục1 của result/claim/citation audit. Đây là yêu cầu sửa provenance có mục tiêu, không đề nghị mở mô phỏng mới hoặc kiểm toán toàn repo. Work không tự sửa scientific lock để làm chương đạt. Sau quyết định hòa giải, chỉ cần cập nhật các đoạn 5.6.1–5.6.2/F5.6 và audit tương ứng nếu được ủy quyền.

## 6. Công cụ đã chạy và giới hạn truy cập

Lệnh tự kiểm tra thực tế: `python verify_chapter05.py` — exit0. Script tạm kiểm tra nội dung/evidence tại phiên làm việc; không là một test trong engine và không được commit thành file thứ tư. Kết quả:

- 7/7 +19/19 headings khớp Blueprint; sáu RQ và tám primary destinations được kiểm theo registry/allocation.
- 23 accepted components; 12 exact P2 reference entries/access labels; bốn disallowed không đi vào affirmative prose.
- 47 result IDs resolve; 95 supplemental source-field entries khớp artifact; ba bảng main đối chiếu trực tiếp từng ô với nguồn khóa.
- 62 source identities khớp Git blob SHA. 21 cache text copies có thêm một LF do cơ chế lưu; so sánh bỏ đúng LF dư chỉ khi Git blob khớp. Đây không phải tuyên bố hai file byte khác nhau có cùng SHA; byte identity được kiểm ở dạng nguồn đã đối chiếu. Không gọi Windows checkout hash là Git LF blob hash.
- Python AST parse ba source files cần đọc, chỉ kiểm cú pháp để rà phạm vi code; không import/chạy engine, tính lại HF, CI hoặc output.
- Không có đoạn văn dài được chép nguyên từ Chương1–4; không placeholder/TODO/control characters hoặc trailing whitespace trong ba file giao.
- Script xác nhận chính hai metadata contradictions; output overall vẫn `CHAPTER_05_TARGETED_REPAIR_REQUIRED`, không phải PASS chung.

Hai borrower-level CSV 8.775.089 và 18.489.195 bytes chưa được Work đọc đầy đủ. Event trace JSONL 1.983.471 bytes cũng chưa được đọc trong lượt này. Các đối chiếu sử dụng summary/registry/CSV nhỏ, manifest, diagnostic comparison và targeted code locators; không nhận công kiểm chứng lại mọi raw row. Các kết quả replay/hash/tests được Codex/P2 báo trước chỉ là inherited verification, không là lượt test độc lập mới của Work. Không gọi truy cập source citation trong P2 là đã tải lại/read fulltext ở lượt viết chương này.

Không chạy simulation, Monte Carlo, retune, full regression, local-fork transaction, RPC, hoặc kiểm định thống kê mới. Không tính lại các số liệu, Wilson bounds, p95/ES; chỉ so các giá trị đã lưu và chuyển cách hiển thị ratio khi ghi phần trăm. School template vẫn `TEMPLATE_VERIFICATION_PENDING`; không tạo DOCX.

## 7. Commander handoff

Toàn văn đủ chiều sâu để review lập luận và số liệu: bảy mục, mười chín tiểu mục, sáu RQ, tám primary claims và cả mười exhibits. Đề nghị Commander review Draft PR và chuyển đúng hai findings nguồn RQ6 cho người sở hữu numerical provenance để xác nhận/sửa có version. Chưa đề nghị `CHAPTER_05_LOCKED` hoặc một overall PASS khi hai vấn đề còn mở. Việc render những hình đã có đủ đặc tả có thể tách khỏi sửa metadata; F5.6 phải chờ kết luận nguồn. Không bắt đầu Chương6.
