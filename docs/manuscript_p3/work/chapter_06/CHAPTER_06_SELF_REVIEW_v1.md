# CHAPTER_06_SELF_REVIEW_v1

**Recommendation: `CHAPTER_06_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`.** Toàn văn đã hoàn chỉnh, không phát hiện P0/P1 chưa xử lý trong phạm vi nguồn được sử dụng. Đây là self-review của Work cùng kiểm tra tĩnh nội dung/locator, không phải external independent peer review, một đợt RPC validation hoặc chạy lại các mô hình. Commander giữ quyền nghiệm thu và Chapter Lock.

## 1. Source anchors và phạm vi giao

- Scientific Lock: `3f6e5302483681209e2408531eb5a15389f9fded`.
- Blueprint Lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Starting integration / Chương1–5: `bd93a39f773eacfab182a750c08c0d9fc30914cf`, GitHub xác nhận là merge PR21.
- Branch: `research/p3-ch06-full-manuscript-work`; final SHA báo bằng Git/PR handoff, không nhúng SHA chính commit vào file.
- Đúng ba deliverables trong `docs/manuscript_p3/work/chapter_06/`: full draft, result/claim/citation audit và self-review này. Không sửa các nguồn khoa học, chương trước, Blueprint/allocation hoặc đường dẫn Codex.

## 2. Completeness theo Blueprint

| Tiêu chí | Kết quả | Điều kiện diễn giải |
|---|---|---|
| Cấu trúc | PASS: 4/4 mục, 11/11 tiểu mục, heading/thứ tự nguyên Blueprint | Không thay chapter allocation |
| Primary claims | PASS: 8/8 primary destinations được phát triển | C16,C26,C27,C28,C29,C30 và hai Integration claims historical/Terra |
| Components thực sự dùng | 13 accepted components: tám primary, một secondary và bốn context anchors được Blueprint/exhibit nêu | Không gọi bốn context anchors là primary của Chương6 hoặc tự thêm secondary6 vào nguồn |
| Sáu RQ | PASS: kết nối riêng tại6.4.2; nguyên văn sáu câu hỏi giữ trong audit | Không mở RQ7, không thay câu trả lời định lượng Chương5 |
| Exhibits | PASS: T6.1,F6.1,F6.2,T6.2 đúng IDs và section | Hai bảng Markdown, hai display specs chưa render |
| Registered results | PASS: tám HIST/TERRA result IDs resolve | Không tạo ID cho supplemental metric/code fact |
| Citation coverage | PASS: chín exact APA entries kế thừa P2, có citations trong body | Access labels giữ nguyên; S17/S18 cùng study |
| Bốn disallowed | PASS: chỉ giữ audit trail, không affirmative findings | Registry48/44/4 bảo toàn |
| Ranh giới chương | PASS: không chép nguyên đoạn dài Chương1–5, không viết Chương7 | Chỉ có đoạn chuyển tiếp và dẫn chiếu chức năng |

Tám primary claims là `P2:C16`, `P2:C26`, `P2:C27`, `P2:C28`, `P2:C29`, `P2:C30`, `INT:CL_INT_HISTORICAL_TIERS_PRESERVED`, `INT:CL_INT_TERRA_NEGATIVE_PRESERVED`. `P2:C17` dùng theo secondary6 đã duyệt. `C09/C10/C25` là anchors nền nêu trực tiếp ở Blueprint Chương6; `C33` là context reference của T6.2 trong approved crosswalk. Audit công bố rõ các secondary lists gốc không có6 ở bốn records này, giữ original allocation và phân biệt chapter-use context với primary destination. Không sửa matrix để che khác biệt phạm vi giữa các tài liệu G0.

## 3. Scientific self-review

**6.1 — Historical Aave:** Câu hỏi, cửa sổ, đơn vị event và mục đích census được giải thích trước khi đưa số. Giữ28Pool/27Graph và một RPC-only; tier1/2/23/1 có denominator27. Chỉ exact ordered collateral Transfer path được gọi direct, hai same-tx events được giữ ở mức co-occurrence. Tier3/4 không nâng thành causal contagion. Có phân tích route cụ thể từ report/log selectors, paired event/control counts, lý do không suy unique swaps hoặc causal effect từ activity nền. Temporal clusters khác modeled waves; historical borrower-state census và oracle-transmission validation còn thiếu. Không dùng invalid-epoch attempt làm nguồn của count28.

**6.2 — Terra:** Luận điểm phân biệt cơ chế rút vốn/quy đổi/phát hành với tuyến Aave; literature abstract không dùng để xác nhận tham số dự án. Giữ riêng ba thiết kế: score cutoff-safe1776h, strict OOS V2 và conditional replay V4 trên gói312h. Dữ liệu tháng3–4 daily-carried không được gọi independent hourly market observations. Tính bất biến trước cutoff dưới perturbation sau cutoff khác lựa chọn mô hình ex ante. Kết quả0HIGH/1630h và lead−45h được đặt trung tâm; positive lead3h đối với ngưỡng muộn0.90 không chuyển thành initial-depeg forecast success. V2 collapse False và V4 fit/supply-error chỉ báo theo đúng nguồn/mẫu, không gộp các thiết kế. Không chọn lại cutoff, threshold, proxy hoặc tham số.

**6.3 — Network:** Có giải thích tám node, chín typed edges, hướng quan hệ, evidence status và vai trò tác nhân. Snapshot-derived input khác observed transaction graph; kênh đánh giá lại không xác nhận DEX spot là Aave oracle. Phân biệt typed graph với graph gộp max, node–layer/coupling với nhãn layer, structural centrality với active weighted influence. Betweenness dùng directed/unweighted topology, có thể chứa route inactive; weighted influence lọc active. Aave có bridge centrality nhưng weighted influence0 được giải thích bằng hai câu hỏi đo khác nhau. DebtRank chỉ làm đối chứng phương pháp, chưa được triển khai; không risk ranking toàn DeFi hoặc mô hình contagion đa tầng hoàn chỉnh.

**6.4 — Tổng hợp:** T6.2 phân vai onchain state/event, modeled counterfactual, derived historical validation, code/structural metric và integrity control. Không cộng ba hướng đối chiếu thành ba independent validations của cùng một hypothesis. Mỗi RQ được nối với điều extensions hỗ trợ và mắt xích chưa được xác lập. Không lặp bảng số Chương5 hoặc đưa kết luận toàn đề tài thay Chương7.

## 4. Targeted repairs đã thực hiện trong lượt viết

| Finding | Vị trí/nguyên nhân | Repair | Nguồn và recheck |
|---|---|---|---|
| CH06-R01 | Narrative cũ có27events/3direct links | Dùng census28/27 và targeted tiers1/2/23/1; giữ lịch sử sửa trong audit | Census/linkage audit + Frozen8IDs; PASS |
| CH06-R02 | Dễ gộp cutoff-safe, V2 OOS, V4 conditional thành một sample | Tách1776h score khỏi312h May dataset; giữ144/168 và12h/134 đúng report | phase5/dataquality/finalreport/benchmark; PASS |
| CH06-R03 | Có thể chọn positive lead ngưỡng0.90 để kể thành cảnh báo thành công | Đặt0/1630,−45h trước; giải thích later-threshold3h khác target | Exact phase5 selectors; PASS |
| CH06-R04 | Graph labels/normalized scores dễ bị gọi fullmultilayer/risk | Công bố max aggregation, inactive topology và active weighted metric; không DebtRank | network code + structural artifacts; PASS |
| CH06-R05 | Context anchors và primary allocation có chức năng khác | Giữ matrix gốc, chỉ rõ approved Blueprint/exhibit context authority | Blueprint/crosswalk/allocation; PASS, không mutation |
| CH06-R06 | Window counts dễ bị đọc thành total unique swaps/causal effect | Giữ năm cặp event/control, công bố overlap/four-pool scope | CSV/control audit; PASS |
| CH06-R07 | Bibliography có LF dư đầu mục đầu tiên và thứ tự chưa thống nhất | Chuẩn khoảng cách và xếp alphabetically, giữ exact APA entry text | Đối chiếu9P2entries; PASS |

CH06-R02 là phòng ngừa trộn mẫu, không sửa một con số trong scientific source. Tập score là1776 hàng và preinitial window là1630 giờ. Các sửa đổi chỉ là authoring/interpretation; không repair engine hoặc retune để cải thiện fit. Phần audit giữ nguyên trạng thái lịch sử của report, nhưng không dùng chữ “PENDING” trong report cũ như trạng thái khóa hiện tại.

## 5. Actual tool checks

Lệnh thực tế: `python verify_chapter06.py` — **exit0/PASS**. Đây là checker tạm tại phiên làm việc, không commit thành file thứ tư và không là một test mô phỏng. Các kiểm đã chạy:

- 4/4 section headings và11/11subheadings so nguyên Blueprint; mỗi tiểu mục có nội dung phát triển, không heading rỗng.
- 8/8 primary,13acceptedcomponents và nguyên primary/secondary lists đối chiếu matrix/registry. Bốn disallowed records không xuất hiện trong affirmative prose.
- Sáu original RQ ở audit đúng source; không thay câu hỏi hoặc thêm RQ.
- T6.1/F6.1/F6.2/T6.2 đúng placement, status và locked-source blob locators. Hai bảng main có7 và6rows; không thêm manuscript exhibit ID.
- Tám result IDs tồn tại và values/unit/population giữ source. Census28/27/1,27linkage rows và tier counts1/2/23/1 được đối chiếu với audit; tất cả causal_claim=false.
- Kiểm route event/log selectors, năm cặp event/control ±5m, offset−3600seconds, four-pool/control boundary; không re-query RPC.
- Kiểm cutoff-safe count/denominator/lead từ JSON, future/forecast boundary; V2 summary từ report, V4 windows/selected metrics từ JSON nhỏ. Không tính lại lead/RMSE/correlation.
- Kiểm8nodes/9typededges, đầy đủ edge/node IDs trong audit, centrality values, max/active/unweighted semantics bằng đọc mã; không chạy NetworkX hoặc graph simulation.
- 47file identities khớp Git blob SHA. Các bản cache text có một LF thêm khi lưu; chỉ bỏ đúng LF dư khỏi hash comparison khi exact source Git blob khớp. Không coi hai bytestring khác nhau là cùng SHA; Git LF domain khác Windows CRLF checkout bytes/SHA256.
- Chín mục APA đúng nguyên văn P2 và URL/DOI không mới; giữ source access labels. Không có đoạn văn dài sao nguyên Chương1–5, placeholder hoặc trailing whitespace.

Kết quả định lượng các phép kiểm hoặc replay trước đây của Codex/P2 là inherited verification, không phải độc lập được Work chạy lại trong lượt này. Self-review nội dung còn đánh giá mạch lập luận, độ rõ tiếng Việt, giới hạn novelty và vị trí dẫn nguồn; không gọi nhận định đó là automated proof hoặc external academic review.

## 6. Source-read và production limitations còn lại

47 nguồn truy xuất qua GitHub đúng ref được ghi toàn bộ trong audit ledger, gồm toàn văn Chương1–5, Blueprint/allocation, registry/P2 và các nguồn lịch sử/Terra/network liên quan. Lượt này không nghiên cứu literature mới hoặc nâng abstract lên fulltext. S17JFE/S18NBER cùng nghiên cứu; S10/S17/S18/S26/S30 chỉ được dùng ở phạm vi access đã khóa. Nguồn scholarly không chứng nhận output của code DeFiStress.

Work đọc reports/summary/targeted selectors, không chạy lại archived RPC/receipt/debug trace, không đọc đầy đủ census_cache/raw_swap gzip. Raw Terra parquet/native-redemption rows, score timeline và toàn bộ strict-OOS/conditional trajectories cũng chưa được rà từng hàng. Những hạn chế data quality/proxy/quarantine/archival availability giữ nguyên. Hai borrower CSVs lớn8.775.089 và18.489.195bytes vẫn chưa được đọc đủ; không nhận công một rawHF/event re-audit mới. Các attachments DOCX/PDF/PPTX không được mở lại ở lượt này và không được dùng để thêm số liệu vào chương.

T6.1/T6.2 đã là bảng Markdown đầy đủ. F6.1/F6.2 có display specification, exact selectors, đơn vị, mẫu số/phạm vi, caption controls và toàn bộ dữ liệu hiển thị cần thiết trong audit; trạng thái `DISPLAY_SPEC_READY_NOT_RENDERED`. Chưa có publication render hoặc technical-renderer sign-off. Việc sản xuất hình khi được giao có thể dùng nguồn khóa, không tạo dữ liệu hoặc bố cục có hàm ý causal mới.

`TEMPLATE_VERIFICATION_PENDING` tiếp tục là hạn chế của final formatting, không tự nhận ví dụ2024 là quy định trường hiện hành. Không tạo DOCX. Không simulation, Monte Carlo, retune, kiểm định thống kê mới hoặc full regression. Không Chương7, merge hoặc tự cấp `CHAPTER_06_LOCKED`.

## 7. Commander recommendation

Đề nghị review toàn văn Chương6 cùng hai hồ sơ đi kèm. Mục tiêu chương và tám primary claims đã được phát triển; các kết quả âm và ranh giới nhân quả được giữ rõ, không có evidence blocker mới cần mở một nhiệm vụ Codex hoặc vòng literature khác. Commander có thể đánh giá chất lượng prose và tính nhất quán khoa học trên bản hoàn chỉnh, sau đó quyết định targeted repair/merge/Chapter Lock riêng. Trạng thái bàn giao là `CHAPTER_06_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`.
