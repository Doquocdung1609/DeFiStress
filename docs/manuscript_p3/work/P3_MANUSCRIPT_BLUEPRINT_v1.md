# P3_MANUSCRIPT_BLUEPRINT_v1

**Decision đề nghị: P3_BLUEPRINT_READY_FOR_COMMANDER_REVIEW.** Trạng thái thực thi: **AWAITING_COMMANDER_BLUEPRINT_APPROVAL**. Đây là đề cương có luận điểm và hợp đồng bằng chứng, chưa phải bản thảo Chương 1 và chưa khóa cấu trúc.

Scientific lock: `3f6e5302483681209e2408531eb5a15389f9fded`; registry `final-accepted-claims-v1.1-targeted-repair`. [Quyết định Commander](https://github.com/Doquocdung1609/DeFiStress/issues/3#issuecomment-6186533199) ưu tiên hơn status lịch sử “awaiting merge/lock” còn trong các báo cáo cũ. Branch HEAD khi audit trùng lock; về sau HEAD thay đổi không tự đổi pin.

## Căn cứ chọn cấu trúc

Bản DOCX hiện có gồm năm chương: Giới thiệu; Cơ sở lý thuyết; Phương pháp; Kết quả; Thảo luận/kết luận. Không tìm thấy một cấu trúc bảy chương đã được phê duyệt trong tree khóa, các attachments hoặc discussions Issue3/4 đã kiểm tra. Work đề xuất phát triển từ năm chương, tách dữ liệu/kiểm chứng thành Ch4 và lịch sử/extensions thành Ch6 để ngăn mô phỏng, quan sát và suy dẫn trộn cấp bằng chứng. Phần còn lại giữ chức năng học thuật của bản cũ, sửa nội dung theo lock.

School template: **TEMPLATE_VERIFICATION_PENDING; REFERENCE_EXAMPLE_AVAILABLE**. Đã đọc trang 1–6 của báo cáo cấp Học viện 01-2024-HV-TĐ như ví dụ tham khảo; chưa có văn bản quy định chính thức để biến ví dụ đó thành yêu cầu bắt buộc. Bìa có tên PTIT không làm DOCX cá nhân trở thành template chính thức. Cấu trúc này là đề xuất Work; citation author–year/APA, số thứ tự theo chương và định dạng exhibit là working convention chờ trường/Commander xác nhận. Chưa ấn định font, margins, số trang hoặc tỷ lệ điểm theo trường.

Đóng góp dự kiến có thể bảo vệ là tích hợp dữ liệu đồng block với thí nghiệm phản thực, định vị vai trò của valuation policy và phân biệt eligible/executed bằng truy vết. Không tuyên bố first-ever, chứng minh causality Mainnet, hoặc công cụ dự báo/production risk tối ưu. Literature synthesis giới hạn theo30records đã duyệt, không gọi là systematic review đầy đủ nếu chưa có search protocol.

## Sáu câu hỏi giữ nguyên văn

- **RQ1:** Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)?
- **RQ2:** Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt?
- **RQ3:** Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý?
- **RQ4:** Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi?
- **RQ5:** Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset?
- **RQ6:** Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk?

## Quy tắc bằng chứng và phân bổ

44/44 affirmative candidates có đúng một primary destination trong `P3_CLAIM_TO_CHAPTER_MATRIX.json`; bốn excluded records có ledger riêng. Primary destination là nơi giải thích đầy đủ, secondary chỉ dẫn chiếu với mục đích khác. Không chuyển toàn bộ44claims vào literature. Mỗi đoạn quan trọng sau approval phải giữ claim/source/result locator theo vai trò, không bắt conceptual claim có numerical result.

## Chương 1 Giới thiệu và thiết kế vấn đề nghiên cứu

**Mục tiêu học thuật:** Xác định bài toán kinh tế và khoảng trống tích hợp có thể kiểm tra trên bộ nguồn hiện có.

**Luận điểm trung tâm cần phát triển:** Giá trị nghiên cứu nằm ở việc kiểm tra điều kiện truyền rủi ro và khả năng truy vết, thay vì mặc định cascade hoặc hứa dự báo khủng hoảng.

**Vai trò:** Mở chuỗi lập luận từ vấn đề tới sáu câu hỏi, không trình bày kết quả chi tiết.

**RQ liên quan:** RQ1, RQ2, RQ3, RQ4, RQ5, RQ6.

**Depth/ưu tiên:** Vừa; ưu tiên problem/gap/RQs, không kéo dài lịch sử DeFi.

**Kế thừa:** 1.1–1.6; Lời mở đầu; proposal §1–5. Xem audit để biết phần cần thay số/diễn đạt.

**Dependencies:** trước không; sau Ch2, Ch3, Ch7. Đây là quan hệ nội dung, không cho phép viết chương sau khi chương trước chưa được Commander duyệt.

**Bằng chứng được phép dùng:**

- Scholarly/P2 IDs: P2:C01, P2:C03, P2:C09, P2:C10, P2:C11, P2:C12, P2:C13, P2:C17, P2:C19, P2:C31, P2:C32, P2:C35.
- Accepted Integration IDs: NOT_APPLICABLE — chương định vị/khái niệm, không cần numerical finding.
- Supporting S IDs: S01, S02, S03, S05, S06, S09, S10, S11, S12, S13, S14, S17, S19, S20, S21, S22, S29.
- Frozen/Integration result IDs: HIST_DIRECT_TRANSFER_PATHS, HIST_GRAPH_MATCHED_EVENTS, HIST_RPC_CENSUS_EVENTS, HIST_SAME_BLOCK_ASSOCIATION, HIST_SAME_TX_COOCCURRENCE, HIST_TIME_WINDOW_ASSOCIATION, INT_A_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES, INT_A_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES, RQ1_MC_SEVERE_DEPTH2_COUNT, RQ4_IMMEDIATE_PRICE_IMPACT, RQ4_SPREAD_ARB0, RQ4_SPREAD_ARB100, RQ5_LIQUIDATED_DEBT_TOKEN_QTY, RQ5_LIQUIDATED_DEBT_USD, RQ6_BONUS103_SEIZED, RQ6_BONUS107_SEIZED.
- Oracle: selection_manifest/comparison_matrix tại lock là bảng sensitivity; không có namespace resultID độc lập được bịa thêm. Integration IDs liên quan giữ mapping nguồn.

**Đề cương cấp2/cấp3 và nhiệm vụ chứng minh:**

### 1.1 Bối cảnh và vấn đề kinh tế

Claim anchors: P2:C01, P2:C03, P2:C32.

- **1.1.1 Sự liên thông của cho vay và thanh khoản:** Giải thích WETH đồng thời là thế chấp và tài sản bán; dẫn C01/S01/S29, không thêm số TVL hiện hành.
- **1.1.2 Câu hỏi về phản hồi nội sinh:** Tách tổn thương do cú sốc ban đầu khỏi thanh lý vòng sau; nêu điều kiện định giá là một biến giả định cần kiểm tra.

### 1.2 Khoảng trống trong phạm vi bộ tài liệu đã kiểm chứng

Claim anchors: P2:C09, P2:C10, P2:C11, P2:C12, P2:C13, P2:C31.

- **1.2.1 Những gì literature giải thích được:** Dẫn các nhánh incentive, DEX impact, stress testing; đối thoại C09–C13 và không xem mọi bài là cùng kết quả.
- **1.2.2 Khoảng trống tích hợp và truy vết:** Định vị C31 là đóng góp tích hợp ở phạm vi đề tài, không kết luận systematic absence/first-ever.

### 1.3 Mục tiêu và câu hỏi nghiên cứu

Claim anchors: P2:C31.

- **1.3.1 Mục tiêu tổng quát và mục tiêu cụ thể:** Kế thừa mục tiêu dữ liệu/mô hình/đối chiếu; chuyển lời hứa sản phẩm/fork thành phạm vi đã đạt và hạn chế.
- **1.3.2 Sáu câu hỏi nguyên văn:** Chép chính xác sáu research_question trong matrix, giữ thứ tự; phần giải thích tiếng Việt không thay câu hỏi.

### 1.4 Đối tượng phạm vi và đóng góp dự kiến

Claim anchors: P2:C17, P2:C19, P2:C31, P2:C35.

- **1.4.1 Biên dữ liệu và thực nghiệm:** Phân biệt 454/109, một block/pool, mô phỏng và cửa sổ lịch sử; chưa triển khai numerical findings.
- **1.4.2 Đóng góp có thể bảo vệ:** Dự kiến đóng góp phương pháp truy vết, độ nhạy oracle và minh bạch kết quả âm; chốt thực chất ở Ch7.

### 1.5 Lộ trình lập luận bảy chương

Claim anchors: P2:C31.

- **1.5.1 Từ lý thuyết tới kiểm chứng và kết quả:** Giải thích vì sao tách phương pháp Ch3, dữ liệu/validation Ch4, lịch sử Ch6; không dùng các bản tóm tắt cũ làm conclusion.

**Exhibit/công thức cần chuẩn bị:** T1.1. Chi tiết units/axes/policy/format và status trong exhibit plan. Không coi các mã P3 T/F/E này là scientific result IDs đã tồn tại.

**Artifact locators, tất cả đọc từ scientific lock:**

- `data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json` (nội dung đã đọc G0)
- `data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json` (nội dung đã đọc G0)

**Giới hạn bắt buộc đặt đúng vị trí:**

- L01: Kết quả cascade là mô phỏng phản thực có điều kiện theo policy, cohort và cấu hình thanh khoản; A/B/C chưa được xác minh là feed Aave/Chainlink lịch sử.
- L02: Một block 26045352, 454 verified borrowers; 109 là cohort WETH-collateral-enabled/USDC-debt riêng; một Uniswap venue, không đại diện toàn thị trường.
- L13: Hai raw borrower CSV lớn vẫn chưa được Work đọc đầy đủ/cell-by-cell; giữ source access labels, U01–U08 và mức abstract/metadata/code; S17/S18 cùng nghiên cứu.

**Suy luận cấm:** actual Aave=Uniswap spot; oracle-independent cascade; newly eligible=executed; tần suất mô hình=xác suất khủng hoảng; same-block=causal transmission; modeled debt/loss=realized loss; Terra forecast thành công; graph gộp=full multilayer. Chỉ giữ những giới hạn liên quan trong prose để không lặp phủ định máy móc.

**Acceptance riêng của chương:**

- Luận điểm khoảng trống giới hạn trong bộ nguồn P2
- 6/6 câu hỏi đúng nguyên văn
- Không hứa funded execution, real oracle hoặc dự báo thành công
- Đạt rubric CP1–CP6 và chưa có P0/P1; chapter lock chỉ do Commander cấp.

## Chương 2 Cơ sở lý thuyết và tổng quan nghiên cứu

**Mục tiêu học thuật:** Xây nền tảng khái niệm và tổng hợp phản biện các quan hệ, thiết kế và mức bằng chứng.

**Luận điểm trung tâm cần phát triển:** Cơ chế thanh lý, sức hấp thụ DEX và truyền giá sang định giá khoản vay là các mắt xích riêng; bằng chứng không đồng nhất cần được giữ khác biệt.

**Vai trò:** Tạo lý do chọn biến/giả định ở Ch3 và benchmark đối thoại Ch5–7.

**RQ liên quan:** RQ1, RQ2, RQ3, RQ4, RQ5, RQ6.

**Depth/ưu tiên:** Cao; ưu tiên tổng hợp so sánh thiết kế/horizon và bằng chứng trái chiều.

**Kế thừa:** 2.1–2.8; proposal §2–4. Xem audit để biết phần cần thay số/diễn đạt.

**Dependencies:** trước Ch1; sau Ch3, Ch5, Ch6, Ch7. Đây là quan hệ nội dung, không cho phép viết chương sau khi chương trước chưa được Commander duyệt.

**Bằng chứng được phép dùng:**

- Scholarly/P2 IDs: P2:C01, P2:C02, P2:C03, P2:C04, P2:C05, P2:C06, P2:C07, P2:C08, P2:C09, P2:C10, P2:C11, P2:C12, P2:C13, P2:C14, P2:C15, P2:C16, P2:C17, P2:C18, P2:C20, P2:C21, P2:C22, P2:C23, P2:C25, P2:C27, P2:C28, P2:C31.
- Accepted Integration IDs: NOT_APPLICABLE — chương định vị/khái niệm, không cần numerical finding.
- Supporting S IDs: S01, S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19, S20, S21, S22, S23, S24, S25, S27, S28, S29.
- Frozen/Integration result IDs: HIST_DIRECT_TRANSFER_PATHS, HIST_GRAPH_MATCHED_EVENTS, HIST_RPC_CENSUS_EVENTS, HIST_SAME_BLOCK_ASSOCIATION, HIST_SAME_TX_COOCCURRENCE, HIST_TIME_WINDOW_ASSOCIATION, INT_A_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES, INT_A_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES, MC_INDEPENDENT_PATHS_VALIDATED, RQ1_MC_SEVERE_DEPTH2_COUNT, RQ1_MC_SEVERE_DEPTH2_FREQUENCY, RQ2_CANONICAL_DEPTH_2PCT, RQ2_DEPTH2_HAIRCUT90_COUNT, RQ2_DEPTH2_HAIRCUT95_COUNT, RQ4_IMMEDIATE_PRICE_IMPACT, RQ4_SPREAD_ARB0, RQ4_SPREAD_ARB100, RQ5_HF_LT1_USDC_090, RQ5_HF_LT1_USDC_100, RQ5_HF_LT1_USDC_110, RQ6_BONUS103_SEIZED, RQ6_BONUS107_SEIZED, RQ6_LT083_UNLIQUIDATED, RQ6_LTV0755_CAPACITY, RQ6_LTV0825_CAPACITY.
- Oracle: selection_manifest/comparison_matrix tại lock là bảng sensitivity; không có namespace resultID độc lập được bịa thêm. Integration IDs liên quan giữ mapping nguồn.

**Đề cương cấp2/cấp3 và nhiệm vụ chứng minh:**

### 2.1 Cho vay thế chấp và kinh tế thanh lý

Claim anchors: P2:C02, P2:C03, P2:C04, P2:C05, P2:C06, P2:C12.

- **2.1.1 HF và điều kiện đủ tư cách thanh lý:** Định nghĩa HF theo S02/S03; eligibility khác execution; dẫn phương trình đầy đủ ở Ch3.
- **2.1.2 LTV LT và thưởng thanh lý:** Tách giới hạn vay, ngưỡng an toàn và incentive/transfer theo C04/C05; không xem tham số hiện hành là historical config.
- **2.1.3 Động cơ và chi phí tham gia:** So sánh S09/S12; chỉ abstract-scoped khi nguồn chưa fulltext, không suy Aave dùng đấu giá.

### 2.2 Thanh khoản tập trung và kinh doanh chênh lệch giá

Claim anchors: P2:C07, P2:C08, P2:C09, P2:C10, P2:C11, P2:C13.

- **2.2.1 Từ khoảng tick tới độ sâu thực thi:** Dựa S07/S08, phân biệt liquidity parameter và executable depth, constant product chỉ trực giác cục bộ.
- **2.2.2 Bán tài sản và tác động giá:** Đối thoại S10/S11/S13 theo thiết kế và horizon; association không là causal liquidation feedback.
- **2.2.3 Tác động tức thời và độ lệch còn lại:** Dùng C13/S14; không chuyển hệ số của Tether thành calibration WETH/USDC.

### 2.3 Stablecoin và vị trí trên bảng cân đối

Claim anchors: P2:C14, P2:C15, P2:C16, P2:C17.

- **2.3.1 Rủi ro giá quy đổi và thanh khoản:** S15 là tác giả cá nhân; S16 là issuer disclosure; giữ khác biệt mức độc lập của nguồn.
- **2.3.2 Kênh nợ USDC và trường hợp Terra:** Nêu hai cơ chế khác nhau; S17/S18 là hai phiên bản cùng nghiên cứu, không hai bằng chứng độc lập.

### 2.4 Mô hình tác tử Monte Carlo và mô tả mạng

Claim anchors: P2:C18, P2:C20, P2:C21, P2:C22, P2:C23, P2:C25, P2:C27, P2:C28.

- **2.4.1 ABM và mức không đồng nhất:** S19/S20 hỗ trợ cách tiếp cận; mã DeFiStress mới xác định tác nhân thực sự.
- **2.4.2 Monte Carlo và bất định có điều kiện:** S23 preview không dùng cho định lý chưa đọc; Wilson theo S24 khác adjusted Wald.
- **2.4.3 Mạng nhiều lớp và chỉ số trung tâm:** S25–S28 định nghĩa phương pháp, không chứng nhận graph dự án là full multilayer hoặc đã có DebtRank.

### 2.5 Tổng hợp phản biện và lựa chọn thiết kế

Claim anchors: P2:C09, P2:C10, P2:C11, P2:C12, P2:C13, P2:C31.

- **2.5.1 Ma trận câu hỏi phương pháp và bằng chứng:** Lập literature matrix theo câu hỏi/dataset/horizon/access/đóng góp, không chép danh sách abstracts.
- **2.5.2 Các kết quả khác nhau và quan hệ với mô hình:** C11 tách kết quả S13 khỏi Wave2 Policy A; không dùng mô phỏng để diễn giải lại nghiên cứu nguồn.
- **2.5.3 Khoảng trống còn lại trong đề tài:** Từ đối thoại rút ra nhu cầu snapshot đồng bộ, policy sensitivity và traceability; tránh tuyên bố thiếu vắng toàn ngành.

**Exhibit/công thức cần chuẩn bị:** T2.1. Chi tiết units/axes/policy/format và status trong exhibit plan. Không coi các mã P3 T/F/E này là scientific result IDs đã tồn tại.

**Artifact locators, tất cả đọc từ scientific lock:**

- `data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json` (nội dung đã đọc G0)
- `docs/research_final/LITERATURE_VERIFIED.md` (nội dung đã đọc G0)
- `docs/research_final/REFERENCE_EVIDENCE_MATRIX.md` (nội dung đã đọc G0)
- `docs/research_final/APA_REFERENCES_VERIFIED.md` (nội dung đã đọc G0)

**Giới hạn bắt buộc đặt đúng vị trí:**

- L01: Kết quả cascade là mô phỏng phản thực có điều kiện theo policy, cohort và cấu hình thanh khoản; A/B/C chưa được xác minh là feed Aave/Chainlink lịch sử.
- L07: RQ5 chỉ kênh định giá nợ USDC; token quantity khác USD-equivalent; chưa redemption/liquidity/confidence/settlement đầy đủ.
- L11: Graph typed/aggregated và centrality cấu trúc chưa là full multilayer contagion, DebtRank đã triển khai hoặc xếp hạng rủi ro toàn DeFi.
- L13: Hai raw borrower CSV lớn vẫn chưa được Work đọc đầy đủ/cell-by-cell; giữ source access labels, U01–U08 và mức abstract/metadata/code; S17/S18 cùng nghiên cứu.

**Suy luận cấm:** actual Aave=Uniswap spot; oracle-independent cascade; newly eligible=executed; tần suất mô hình=xác suất khủng hoảng; same-block=causal transmission; modeled debt/loss=realized loss; Terra forecast thành công; graph gộp=full multilayer. Chỉ giữ những giới hạn liên quan trong prose để không lặp phủ định máy móc.

**Acceptance riêng của chương:**

- Không chỉ liệt kê tài liệu
- Mọi viện dẫn giữ mức đọc và vai trò nguồn
- S13 khác modeled Wave2; S17/S18 không đếm đôi
- Đạt rubric CP1–CP6 và chưa có P0/P1; chapter lock chỉ do Commander cấp.

## Chương 3 Khung mô hình và phương pháp nghiên cứu

**Mục tiêu học thuật:** Đặc tả cơ chế kinh tế, biến, thứ tự cập nhật và thiết kế thí nghiệm đủ để hiểu/tái lập.

**Luận điểm trung tâm cần phát triển:** Cascade là đầu ra của hệ thống giả định được công bố, trong đó cơ chế định giá và các cổng thực thi quyết định phản hồi từ DEX sang vị thế vay.

**Vai trò:** Cung cấp quy tắc trước khi trình bày chất lượng dữ liệu Ch4 và findings Ch5.

**RQ liên quan:** RQ1, RQ2, RQ3, RQ4, RQ5, RQ6.

**Depth/ưu tiên:** Rất cao; ưu tiên timing/oracle/eligibility/units và giải thích kinh tế, không liệt kê Python classes.

**Kế thừa:** 3.1; 3.4–3.9; spec §8–11 chỉ lấy intention khi khớp mã. Xem audit để biết phần cần thay số/diễn đạt.

**Dependencies:** trước Ch2; sau Ch4, Ch5, Ch6. Đây là quan hệ nội dung, không cho phép viết chương sau khi chương trước chưa được Commander duyệt.

**Bằng chứng được phép dùng:**

- Scholarly/P2 IDs: P2:C02, P2:C03, P2:C05, P2:C08, P2:C18, P2:C19, P2:C20, P2:C21, P2:C22, P2:C23, P2:C24, P2:C29, P2:C32, P2:C33, P2:C34, P2:C35.
- Accepted Integration IDs: INT:CL_INT_ELIGIBLE_NOT_EXECUTED, INT:CL_INT_RQ1_POLICY_CONDITIONAL, INT:CL_INT_RQ2_TWO_CHANNELS.
- Supporting S IDs: S02, S03, S05, S06, S07, S08, S09, S13, S19, S20, S21, S22, S23, S24, S30.
- Frozen/Integration result IDs: INT_A_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, INT_A_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES, INT_A_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES, INT_A_NEWLY_ELIGIBLE_SKIPPED_INSTANCES, INT_B_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, INT_C_MODERATE_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, INT_C_WEAK_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, MC_INDEPENDENT_PATHS_VALIDATED, RQ1_GRID60_DEPTH2, RQ1_MC_SEVERE_DEPTH2_COUNT, RQ1_MC_SEVERE_DEPTH2_FREQUENCY, RQ2_CANONICAL_DEPTH_2PCT, RQ2_DEPTH2_HAIRCUT90_COUNT, RQ2_DEPTH2_HAIRCUT95_COUNT, RQ5_LIQUIDATED_DEBT_TOKEN_QTY, RQ5_LIQUIDATED_DEBT_USD.
- Oracle: selection_manifest/comparison_matrix tại lock là bảng sensitivity; không có namespace resultID độc lập được bịa thêm. Integration IDs liên quan giữ mapping nguồn.

**Đề cương cấp2/cấp3 và nhiệm vụ chứng minh:**

### 3.1 Thiết kế nghiên cứu và hệ thống giả định

Claim anchors: P2:C18, P2:C20, P2:C31, P2:C32.

- **3.1.1 Phân tách quan sát mô phỏng và suy dẫn:** Định nghĩa evidence tiers, vai trò snapshot và lịch sử; Terra/network là extensions.
- **3.1.2 Vòng phản hồi và trình tự thời gian:** Sơ đồ shock→HF→plan→forced sale→policy valuation→HF; đánh dấu đường giả định thay vì historical causal link.

### 3.2 Tác nhân và các cổng quyết định

Claim anchors: P2:C03, P2:C05, P2:C19, P2:C33, P2:C34, INT:CL_INT_ELIGIBLE_NOT_EXECUTED.

- **3.2.1 Người vay và HF danh mục:** Passive revaluation, tài sản ngoài WETH/USDC trong HF; không tự thêm deleveraging behavior.
- **3.2.2 Tác nhân thanh lý đại diện:** Eligibility/route/plan/profit/capital/capacity/delay; không tự chia plan hoặc recycle vốn.
- **3.2.3 Tác nhân arbitrage đại diện:** Mô tả repositioning và cập nhật liquidityNet qua tick; không viết như funded trading strategy.

### 3.3 Phương trình và đơn vị đo

Claim anchors: P2:C02, P2:C08, P2:C22, P2:C24, P2:C35.

- **3.3.1 HF và định giá nợ:** Công thức portfolio weighted collateral/debt, collateral enabled flags và debt0; USDC token/USD riêng.
- **3.3.2 Thanh khoản V3 và tác động giá:** sqrtPriceX96, token order/decimals, tick crossing, haircut scaling; tránh dùng x*y=k cho toàn pool.
- **3.3.3 Độ sâu thanh lý và chỉ tiêu đuôi:** Định nghĩa wave, debt repaid, skipped, modeled bad debt/composite exposure theo code/registry; không gọi loss thực hiện.

### 3.4 Các chính sách định giá A B và C

Claim anchors: P2:C32, INT:CL_INT_RQ1_POLICY_CONDITIONAL, INT:CL_INT_RQ2_TWO_CHANNELS.

- **3.4.1 Định nghĩa và cấu hình:** A=min(reference,spot); B=reference; C lag1/window3 α.25 hoặc window2 α.50; minh họa index qua completed waves.
- **3.4.2 Ý nghĩa phản thực và giới hạn:** Nêu đây là sensitivity assumptions; actual oracle chưa verified, B không có nghĩa feed ngoài đời bất biến.

### 3.5 Thiết kế thực nghiệm và bất định

Claim anchors: P2:C21, P2:C22, P2:C23, P2:C24.

- **3.5.1 Deterministic và quét tham số:** 32/60cells khác miền; sáu RQ cùng snapshot, tách LTV/LT/bonus.
- **3.5.2 Monte Carlo và checkpoint:** Phân biệt P0v2, Level3, nested prefixes và10 selected paths; không cộng checkpoints thành sample mới.
- **3.5.3 Tần suất và khoảng Wilson:** Định nghĩa chỉ báo depth≥2 và khoảng Wilson theo n; không ước lượng market probability hoặc gọi composite ES là realized loss.

### 3.6 Tiêu chí kiểm chứng và tái lập

Claim anchors: P2:C20, P2:C29, P2:C33.

- **3.6.1 Thiết kế kiểm chứng nhiều lớp:** Direct reads/HF/DEX initial quote/model sensitivity/historical association; local fork unavailable.
- **3.6.2 Hợp đồng provenance:** Input/code/scenario/seed/event/result/caption; nêu khác biệt Work static, Codex replay, Codex premerge và byte hashes.

**Exhibit/công thức cần chuẩn bị:** F3.1, T3.1, T3.2, T3.3, E3.1, E3.2, E3.3, E3.4, E3.5, E3.6, E3.7, E3.8. Chi tiết units/axes/policy/format và status trong exhibit plan. Không coi các mã P3 T/F/E này là scientific result IDs đã tồn tại.

**Artifact locators, tất cả đọc từ scientific lock:**

- `data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json` (nội dung đã đọc G0)
- `sim/engine/run.py` (nội dung đã đọc G0)
- `sim/oracle.py` (nội dung đã đọc G0)
- `sim/lending/liquidation.py` (nội dung đã đọc G0)
- `sim/dex/uniswap_v3.py` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq1_deterministic_depth.csv` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv` (nội dung đã đọc G0)
- `data/processed/research_final/oracle_transmission_diagnostic_v1/selection_manifest.json` (nội dung đã đọc G0)
- `docs/research_final/TERMINOLOGY_VI.md` (nội dung đã đọc G0)
- `sim/lending/health_factor.py` (nội dung đã đọc G0)
- `docs/research_final/APA_REFERENCES_VERIFIED.md` (nội dung đã đọc G0)
- `docs/research_final/LITERATURE_VERIFIED.md` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq5_usdc_valuation.csv` (nội dung đã đọc G0)

**Giới hạn bắt buộc đặt đúng vị trí:**

- L01: Kết quả cascade là mô phỏng phản thực có điều kiện theo policy, cohort và cấu hình thanh khoản; A/B/C chưa được xác minh là feed Aave/Chainlink lịch sử.
- L03: Phân biệt HF danh mục mới dưới 1, engine evaluation, route eligibility và execution có debt repaid dương; đếm borrower-case-policy instances, không unique wallets.
- L04: 280/10.000 chỉ Severe Policy A; mười targeted MC paths chọn theo A-depth2; không ước lượng xác suất thị trường, không suy không thể có depth≥3 ngoài tập thử.
- L05: Liquidator/arbitrageur đại diện; vốn không recycle, kế hoạch vượt vốn không tự chia nhỏ; kết quả gas/capacity/delay chỉ trong miền thử.
- L06: Arbitrage là price repositioning, chưa funded executable swap; tác động giá tức thời khác spread sau arbitrage.
- L07: RQ5 chỉ kênh định giá nợ USDC; token quantity khác USD-equivalent; chưa redemption/liquidity/confidence/settlement đầy đủ.
- L08: Haircut 90/95% là extreme counterfactual tails, chưa có bằng chứng lịch sử tương ứng; không có independent local-fork execution được kiểm chứng.
- L12: Modeled bad debt/composite tail exposure khác realized financial loss hoặc market expected shortfall; debt repaid không phải loss.
- L14: Git LF blob bytes khác Windows CRLF checkout bytes; kết quả kiểm thử do Codex báo cáo khác lượt Work tự chạy; không đồng nhất hash domains.

**Suy luận cấm:** actual Aave=Uniswap spot; oracle-independent cascade; newly eligible=executed; tần suất mô hình=xác suất khủng hoảng; same-block=causal transmission; modeled debt/loss=realized loss; Terra forecast thành công; graph gộp=full multilayer. Chỉ giữ những giới hạn liên quan trong prose để không lặp phủ định máy móc.

**Acceptance riêng của chương:**

- Mỗi phương trình có biến/đơn vị và locator code/source
- Thứ tự cập nhật khớp mô hình khóa
- Không chuyển intended spec thành implementation fact
- Đạt rubric CP1–CP6 và chưa có P0/P1; chapter lock chỉ do Commander cấp.

## Chương 4 Dữ liệu tái dựng trạng thái và kiểm chứng mô hình

**Mục tiêu học thuật:** Trình bày dữ liệu quan sát, lọc mẫu và độ trung thực của trạng thái đầu vào.

**Luận điểm trung tâm cần phát triển:** Trạng thái cùng block và kiểm tra vùng HF gần thanh lý hỗ trợ tính nhất quán nội bộ, nhưng không xác lập độ phủ thị trường hoặc giao dịch fork độc lập.

**Vai trò:** Làm cầu nối giữa giả định Ch3 và tính hợp lệ có giới hạn của kết quả Ch5.

**RQ liên quan:** RQ1, RQ2, RQ3, RQ4, RQ5, RQ6.

**Depth/ưu tiên:** Cao; tập trung sampling/HF/unit/provenance và external fidelity.

**Kế thừa:** 3.2–3.3;3.9;4.1;Phụ lục2. Xem audit để biết phần cần thay số/diễn đạt.

**Dependencies:** trước Ch3; sau Ch5, Ch6. Đây là quan hệ nội dung, không cho phép viết chương sau khi chương trước chưa được Commander duyệt.

**Bằng chứng được phép dùng:**

- Scholarly/P2 IDs: P2:C02, P2:C03, P2:C07, P2:C08, P2:C19, P2:C20, P2:C22, P2:C32, P2:C33, P2:C34.
- Accepted Integration IDs: INT:CL_INT_ELIGIBLE_NOT_EXECUTED.
- Supporting S IDs: S02, S03, S05, S06, S07, S08, S09, S21, S23.
- Frozen/Integration result IDs: INT_A_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES, INT_A_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES, INT_A_NEWLY_ELIGIBLE_SKIPPED_INSTANCES, MC_INDEPENDENT_PATHS_VALIDATED, RQ2_CANONICAL_DEPTH_2PCT, RQ2_DEPTH2_HAIRCUT90_COUNT, RQ2_DEPTH2_HAIRCUT95_COUNT.
- Oracle: selection_manifest/comparison_matrix tại lock là bảng sensitivity; không có namespace resultID độc lập được bịa thêm. Integration IDs liên quan giữ mapping nguồn.

**Đề cương cấp2/cấp3 và nhiệm vụ chứng minh:**

### 4.1 Nguồn và tái dựng snapshot

Claim anchors: P2:C02, P2:C08, P2:C19.

- **4.1.1 Khám phá và xác minh:** Phân biệt bước khám phá ứng viên qua nguồn lập chỉ mục với xác minh RPC. Không dùng tỷ lệ ứng viên được xác minh để suy độ phủ toàn thị trường Aave.
- **4.1.2 Định nghĩa cohort:** Định nghĩa riêng 454 người vay được xác minh và 109 vị thế có WETH được bật làm thế chấp, có nợ USDC. Dùng borrower hashes khi minh họa.
- **4.1.3 Đồng bộ pool và trạng thái:** Trình bày block, thứ tự token, fee tier, tick, thanh khoản hoạt động và cửa sổ tick; không tuyên bố pool được chọn đại diện thanh khoản toàn Ethereum.

### 4.2 Đối chiếu Health Factor

Claim anchors: P2:C03, P2:C33, INT:CL_INT_ELIGIBLE_NOT_EXECUTED.

- **4.2.1 Sai số và vùng gần ngưỡng:** Tách sai số tuyệt đối, sai số tương đối và khả năng phân loại gần HF bằng 1. Đặt cực trị sai số trong bối cảnh quy mô nợ và mức HF.
- **4.2.2 Tái kiểm sau Wave1:** Giải thích phép tái kiểm HF sau Wave 1 và phạm vi đối chiếu tĩnh; vị thế mới đủ điều kiện chưa đồng nghĩa có thanh lý được thực thi.
- **4.2.3 Đối chiếu tuyến thanh lý:** Phân biệt nợ trong toàn danh mục với khoản nợ USDC của tuyến thanh lý được mô hình hóa; dẫn phân tích 36 skips ở Chương 5.

### 4.3 Kiểm tra thanh khoản và mức fidelity

Claim anchors: P2:C07, P2:C08, P2:C32, P2:C34.

- **4.3.1 Độ sâu giá thực thi:** Trình bày độ sâu suy ra từ tick và đối chiếu báo giá ở trạng thái đầu; tách phép kiểm kỹ thuật này khỏi giao dịch có nguồn vốn sau cú sốc.
- **4.3.2 Những lớp chưa kiểm chứng:** Nêu phạm vi chưa xác minh của nguồn giá Aave lịch sử và thực thi local fork độc lập; tránh một nhãn kiểm chứng chung cho toàn giao thức.

### 4.4 Chất lượng dữ liệu và provenance

Claim anchors: P2:C20, P2:C22, P2:C33.

- **4.4.1 Phiên bản và thứ tự ưu tiên:** Registry v1.1 và quyết định lock chi phối diễn giải. Frozen giữ nguồn số học nền, Oracle/Addendum bổ sung đối chiếu; DOCX cũ chỉ là nguồn tổ chức bài viết.
- **4.4.2 Hashes và phạm vi đọc:** Phân biệt Git LF và Windows CRLF; giữ trạng thái chưa đọc đầy đủ hai raw CSV. Gắn người thực hiện và phạm vi thực tế cho từng kiểm tra.
- **4.4.3 Khả năng tái lập có giới hạn:** Nêu đầu vào cần để tái lập và những lớp chưa độc lập lặp lại; không dùng lệnh cũ hoặc con số 130 tests như bằng chứng hiện hành.

**Exhibit/công thức cần chuẩn bị:** F4.1, T4.1, T4.2. Chi tiết units/axes/policy/format và status trong exhibit plan. Không coi các mã P3 T/F/E này là scientific result IDs đã tồn tại.

**Artifact locators, tất cả đọc từ scientific lock:**

- `data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/results_registry.json` (nội dung đã đọc G0)
- `data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/core_facts.csv` (nội dung đã đọc G0)
- `docs/research_final/LEVEL2_FORK_VALIDATION.md` (nội dung đã đọc G0)
- `docs/research_final/FINAL_CROSS_PR_CONSISTENCY_REVIEW.md` (nội dung đã đọc G0)
- `docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md` (nội dung đã đọc G0)

**Giới hạn bắt buộc đặt đúng vị trí:**

- L02: Một block 26045352, 454 verified borrowers; 109 là cohort WETH-collateral-enabled/USDC-debt riêng; một Uniswap venue, không đại diện toàn thị trường.
- L03: Phân biệt HF danh mục mới dưới 1, engine evaluation, route eligibility và execution có debt repaid dương; đếm borrower-case-policy instances, không unique wallets.
- L08: Haircut 90/95% là extreme counterfactual tails, chưa có bằng chứng lịch sử tương ứng; không có independent local-fork execution được kiểm chứng.
- L13: Hai raw borrower CSV lớn vẫn chưa được Work đọc đầy đủ/cell-by-cell; giữ source access labels, U01–U08 và mức abstract/metadata/code; S17/S18 cùng nghiên cứu.
- L14: Git LF blob bytes khác Windows CRLF checkout bytes; kết quả kiểm thử do Codex báo cáo khác lượt Work tự chạy; không đồng nhất hash domains.

**Suy luận cấm:** actual Aave=Uniswap spot; oracle-independent cascade; newly eligible=executed; tần suất mô hình=xác suất khủng hoảng; same-block=causal transmission; modeled debt/loss=realized loss; Terra forecast thành công; graph gộp=full multilayer. Chỉ giữ những giới hạn liên quan trong prose để không lặp phủ định máy móc.

**Acceptance riêng của chương:**

- 454/109 đúng từng denominator
- Hash/source paths pin đúngLOCK
- Không dùng source-read/hash gate như external validation
- Đạt rubric CP1–CP6 và chưa có P0/P1; chapter lock chỉ do Commander cấp.

## Chương 5 Kết quả mô phỏng và phân tích độ nhạy

**Mục tiêu học thuật:** Trả lời sáu RQ bằng đối chiếu kết quả khóa và giải thích cơ chế kinh tế.

**Luận điểm trung tâm cần phát triển:** Thanh lý vòng hai có điều kiện theo valuation policy; kết quả zero/positive và các cổng route execution cần được giải thích trong cùng thiết kế.

**Vai trò:** Trung tâm bằng chứng định lượng; tách khỏi đối chiếu lịch sử ở Ch6 và đóng góp tổng hợp Ch7.

**RQ liên quan:** RQ1, RQ2, RQ3, RQ4, RQ5, RQ6.

**Depth/ưu tiên:** Cao nhất; giải thích cơ chế và contrasts, ưu tiênChương 5 trongtoàn báo cáo.

**Kế thừa:** 4.2–4.8;4.11 chỉ để đối chiếu;5.1.1–5.1.4. Xem audit để biết phần cần thay số/diễn đạt.

**Dependencies:** trước Ch3, Ch4; sau Ch6, Ch7. Đây là quan hệ nội dung, không cho phép viết chương sau khi chương trước chưa được Commander duyệt.

**Bằng chứng được phép dùng:**

- Scholarly/P2 IDs: P2:C03, P2:C04, P2:C05, P2:C07, P2:C11, P2:C12, P2:C13, P2:C15, P2:C19, P2:C22, P2:C23, P2:C24, P2:C32, P2:C33, P2:C34, P2:C35.
- Accepted Integration IDs: INT:CL_INT_RQ1_POLICY_CONDITIONAL, INT:CL_INT_RQ2_TWO_CHANNELS, INT:CL_INT_ELIGIBLE_NOT_EXECUTED, INT:CL_INT_RQ3_PRESERVED, INT:CL_INT_RQ4_PRESERVED, INT:CL_INT_RQ5_PRESERVED, INT:CL_INT_RQ6_PRESERVED.
- Supporting S IDs: S02, S03, S04, S05, S06, S07, S08, S09, S12, S13, S14, S15, S16, S23, S24.
- Frozen/Integration result IDs: INT_A_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, INT_A_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES, INT_A_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES, INT_A_NEWLY_ELIGIBLE_SKIPPED_INSTANCES, INT_B_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, INT_C_MODERATE_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, INT_C_WEAK_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, MC_INDEPENDENT_PATHS_VALIDATED, RQ1_GRID60_DEPTH2, RQ1_MC_SEVERE_DEPTH2_COUNT, RQ1_MC_SEVERE_DEPTH2_FREQUENCY, RQ2_CANONICAL_DEPTH_2PCT, RQ2_DEPTH2_HAIRCUT90_COUNT, RQ2_DEPTH2_HAIRCUT95_COUNT, RQ3_CAPITAL_100_LIQUIDATED, RQ3_CAPITAL_25_LIQUIDATED, RQ3_DELAY_SEVERITY_CHANGE, RQ4_IMMEDIATE_PRICE_IMPACT, RQ4_SPREAD_ARB0, RQ4_SPREAD_ARB100, RQ5_HF_LT1_USDC_090, RQ5_HF_LT1_USDC_100, RQ5_HF_LT1_USDC_110, RQ5_LIQUIDATED_DEBT_TOKEN_QTY, RQ5_LIQUIDATED_DEBT_USD, RQ6_BONUS103_SEIZED, RQ6_BONUS107_SEIZED, RQ6_LT083_UNLIQUIDATED, RQ6_LTV0755_CAPACITY, RQ6_LTV0825_CAPACITY.
- Oracle: selection_manifest/comparison_matrix tại lock là bảng sensitivity; không có namespace resultID độc lập được bịa thêm. Integration IDs liên quan giữ mapping nguồn.

**Đề cương cấp2/cấp3 và nhiệm vụ chứng minh:**

### 5.1 RQ1 điều kiện xuất hiện thanh lý vòng hai

Claim anchors: P2:C11, P2:C22, P2:C23, P2:C32, INT:CL_INT_RQ1_POLICY_CONDITIONAL.

- **5.1.1 Hai lưới 32 và 60 ô:** Đối chiếu số ô depth 0/1/2 lần lượt 12/20/0 và 18/38/4. Thảo luận ngưỡng trong các kịch bản Policy A đã thử, không gọi đó là ngưỡng hệ thống phổ quát.
- **5.1.2 Độ nhạy chính sách:** So bốn trường hợp tất định đã chọn: A/B/C weak/C moderate bằng 4/0/0/0. Giải thích các kết quả không có vòng hai như bằng chứng về độ nhạy giả định.
- **5.1.3 Tần suất Severe có điều kiện:** Báo 280/10.000 đường Severe có depth từ hai trở lên và không thấy depth từ ba trong tập kiểm tra. Giữ Policy A, mẫu số và giới hạn ngoại suy.

### 5.2 RQ2 sức hấp thụ DEX và kênh định giá

Claim anchors: P2:C07, P2:C32, INT:CL_INT_RQ2_TWO_CHANNELS.

- **5.2.1 Độ sâu và forced sale:** Đọc tác động của độ sâu và haircut theo đúng đơn vị. Đặt haircut 90% và 95% trong phần đuôi phản thực chưa có đối chiếu lịch sử tương ứng.
- **5.2.2 Từ DEX distortion sang HF:** So chính sách định giá từ trạng thái DEX chung sau Wave 1. Không quy khác biệt cực trị của các giao dịch muộn hơn cho hiệu ứng arbitrage đơn lẻ.
- **5.2.3 Hai cơ chế trong kết luận:** Giải thích riêng sức hấp thụ giao dịch và việc truyền biến động sang HF; không gán chính sách định giá của mô hình cho oracle Aave thực tế.

### 5.3 RQ3 hạn chế thực thi và vị thế đủ điều kiện

Claim anchors: P2:C03, P2:C19, P2:C33, INT:CL_INT_ELIGIBLE_NOT_EXECUTED, INT:CL_INT_RQ3_PRESERVED.

- **5.3.1 Vốn gas công suất và độ trễ:** Đọc các mức vốn 25%/50% cùng quy tắc không chia nhỏ kế hoạch. Phân biệt ảnh hưởng lên thời điểm xử lý với mức độ thanh lý và chỉ tiêu phục hồi.
- **5.3.2 Eligible evaluated executed skipped:** Báo eligible/executed/skipped lần lượt A 35/14/21, B 0/0/0, C weak 6/0/6, C moderate 11/2/9. Nêu denominator 18 cases × 4 policies × 454 borrowers và đơn vị instances.
- **5.3.3 Các tuyến không có nợ USDC:** Giải thích 36 trường hợp bỏ qua do không có nợ USDC thuộc tuyến mô hình. Codex cung cấp event locator đã khóa cho ví dụ, không suy nguyên nhân là lỗi bot, gas hoặc thiếu vốn.

### 5.4 RQ4 arbitrage và quá trình phục hồi giá

Claim anchors: P2:C13, P2:C34, INT:CL_INT_RQ4_PRESERVED.

- **5.4.1 Impact ngay sau bán và spread còn lại:** So cùng lượng bán bắt buộc ở các mức năng lực arbitrage 0%/50%/100%. Trình bày tác động giá tức thời và độ lệch giá còn lại như hai đại lượng khác nhau.
- **5.4.2 Ý nghĩa ổn định giá trong mô hình:** Giải thích cách quy tắc tái định vị làm giảm spread trong mô hình; giữ giới hạn về nguồn vốn, độ trễ và cạnh tranh chưa được kiểm chứng.

### 5.5 RQ5 kênh định giá khoản nợ USDC

Claim anchors: P2:C15, P2:C35, INT:CL_INT_RQ5_PRESERVED.

- **5.5.1 Phản ứng HF khi giá nợ thay đổi:** So các mức định giá USDC 0,90/1,00/1,10 và số vị thế HF dưới 1, khi các yếu tố khác cố định và vị thế có nợ USDC.
- **5.5.2 Token quantity và USD equivalent:** Phân biệt 9.063,255437 USDC với 9.969,5809807 USD tương đương ở giá 1,10 USD/USDC. Không biến chiều tác động riêng của khoản nợ thành kết luận mất neo là có lợi.

### 5.6 RQ6 ba tham số và đánh đổi

Claim anchors: P2:C04, P2:C05, P2:C12, INT:CL_INT_RQ6_PRESERVED.

- **5.6.1 LTV và khả năng vay ban đầu:** Giải thích khả năng vay ban đầu theo LTV trên danh mục đóng băng; khoản nợ hiện hữu không tự thay đổi do tái cấp tín dụng.
- **5.6.2 LT và ranh giới HF:** Dùng LT của kịch bản thay vì trường LT ghi nhận cũ. Phân biệt nợ còn chưa được thanh lý với khoản nợ đã hoàn trả.
- **5.6.3 Thưởng thanh lý và chuyển giao tài sản:** Tách tài sản thế chấp chuyển giao và động cơ lợi nhuận khỏi số sự kiện, khoản nợ hoàn trả. Không suy một cấu hình là tối ưu quản trị ngoài mẫu.

### 5.7 Độ bền và cách đọc rủi ro đuôi

Claim anchors: P2:C22, P2:C23, P2:C24, INT:CL_INT_RQ1_POLICY_CONDITIONAL.

- **5.7.1 Checkpoint và cỡ mẫu:** Phân biệt các prefix Severe 200/1.000/5.000/10.000; không cộng chúng thành các mẫu độc lập. Đối chiếu Low Liquidity 0/1.000 với giai đoạn 200 đường cũ.
- **5.7.2 Wilson và tần suất:** Báo số lần thành công, mẫu số và khoảng Wilson có điều kiện. Giữ khác biệt giữa sai số lấy mẫu trong mô hình và bất định về cấu trúc mô hình.
- **5.7.3 Kết quả không xuất hiện và giới hạn metric:** Giải thích kết quả không có vòng hai ở B/C weak và các miền lưới qua valuation/route. Chỉ tiêu phơi nhiễm tổng hợp không được gọi là lỗ đã thực hiện.

**Exhibit/công thức cần chuẩn bị:** F5.1, T5.1, T5.2, F5.2, F5.3, F5.4, F5.5, T5.3, F5.6, F5.7. Chi tiết units/axes/policy/format và status trong exhibit plan. Không coi các mã P3 T/F/E này là scientific result IDs đã tồn tại.

**Artifact locators, tất cả đọc từ scientific lock:**

- `data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq1_deterministic_depth.csv` (nội dung đã đọc G0)
- `data/processed/research_final/oracle_transmission_diagnostic_v1/selection_manifest.json` (nội dung đã đọc G0)
- `data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv` (nội dung đã đọc G0)
- `data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv` (nội dung đã đọc G0)
- `data/processed/research_final/scientific_integration_v1/table_figure_registry.json` (nội dung đã đọc G0)
- `docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq2_liquidity.csv` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq3_constraints.csv` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq4_arbitrage.csv` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq5_usdc_valuation.csv` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq6_policy.csv` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv` (nội dung đã đọc G0)

**Giới hạn bắt buộc đặt đúng vị trí:**

- L01: Kết quả cascade là mô phỏng phản thực có điều kiện theo policy, cohort và cấu hình thanh khoản; A/B/C chưa được xác minh là feed Aave/Chainlink lịch sử.
- L02: Một block 26045352, 454 verified borrowers; 109 là cohort WETH-collateral-enabled/USDC-debt riêng; một Uniswap venue, không đại diện toàn thị trường.
- L03: Phân biệt HF danh mục mới dưới 1, engine evaluation, route eligibility và execution có debt repaid dương; đếm borrower-case-policy instances, không unique wallets.
- L04: 280/10.000 chỉ Severe Policy A; mười targeted MC paths chọn theo A-depth2; không ước lượng xác suất thị trường, không suy không thể có depth≥3 ngoài tập thử.
- L05: Liquidator/arbitrageur đại diện; vốn không recycle, kế hoạch vượt vốn không tự chia nhỏ; kết quả gas/capacity/delay chỉ trong miền thử.
- L06: Arbitrage là price repositioning, chưa funded executable swap; tác động giá tức thời khác spread sau arbitrage.
- L07: RQ5 chỉ kênh định giá nợ USDC; token quantity khác USD-equivalent; chưa redemption/liquidity/confidence/settlement đầy đủ.
- L08: Haircut 90/95% là extreme counterfactual tails, chưa có bằng chứng lịch sử tương ứng; không có independent local-fork execution được kiểm chứng.
- L12: Modeled bad debt/composite tail exposure khác realized financial loss hoặc market expected shortfall; debt repaid không phải loss.

**Suy luận cấm:** actual Aave=Uniswap spot; oracle-independent cascade; newly eligible=executed; tần suất mô hình=xác suất khủng hoảng; same-block=causal transmission; modeled debt/loss=realized loss; Terra forecast thành công; graph gộp=full multilayer. Chỉ giữ những giới hạn liên quan trong prose để không lặp phủ định máy móc.

**Acceptance riêng của chương:**

- Sáu RQ có findings, đơn vị, denominator và giới hạn rõ.
- Policy A hiện cùng tần suất 280/10.000; các tập chọn 4/10 không là xác suất quần thể.
- Eligibility khác execution; 36 skips được giải thích đúng theo tuyến.
- Bảng/hình trỏ đúng lock và caption không tăng mức suy luận.
- Đạt rubric CP1–CP6 và chưa có P0/P1; chapter lock chỉ do Commander cấp.

## Chương 6 Đối chiếu lịch sử và các mở rộng nghiên cứu

**Mục tiêu học thuật:** Phân tích bằng chứng ngoài mô phỏng cốt lõi và làm rõ những suy luận chưa được xác lập.

**Luận điểm trung tâm cần phát triển:** Giá trị kiểm chứng phụ thuộc loại quan sát và ranh giới thông tin; lịch sử, hồi cứu Terra và graph cấu trúc có chức năng khác nhau.

**Vai trò:** Đặt kiểm nghiệm bên ngoài có giới hạn trước thảo luận đóng góp Ch7, không thay thế sáu RQ.

**RQ liên quan:** RQ1, RQ2, RQ3, RQ4, RQ5, RQ6.

**Depth/ưu tiên:** Cao về inference/negative evidence; không mở thêm thực nghiệmTerra/network.

**Kế thừa:** 3.8;4.9–4.10;5.1.5;proposal stablecoin literature. Xem audit để biết phần cần thay số/diễn đạt.

**Dependencies:** trước Ch2, Ch3, Ch4, Ch5; sau Ch7. Đây là quan hệ nội dung, không cho phép viết chương sau khi chương trước chưa được Commander duyệt.

**Bằng chứng được phép dùng:**

- Scholarly/P2 IDs: P2:C09, P2:C10, P2:C16, P2:C17, P2:C25, P2:C26, P2:C27, P2:C28, P2:C29, P2:C30.
- Accepted Integration IDs: INT:CL_INT_HISTORICAL_TIERS_PRESERVED, INT:CL_INT_TERRA_NEGATIVE_PRESERVED.
- Supporting S IDs: S02, S06, S10, S11, S13, S17, S18, S25, S26, S27, S28, S30.
- Frozen/Integration result IDs: HIST_DIRECT_TRANSFER_PATHS, HIST_GRAPH_MATCHED_EVENTS, HIST_RPC_CENSUS_EVENTS, HIST_SAME_BLOCK_ASSOCIATION, HIST_SAME_TX_COOCCURRENCE, HIST_TIME_WINDOW_ASSOCIATION, TERRA_INITIAL_DEPEG_HIGH_LEAD, TERRA_PRE_DEPEG_HIGH_ALERT_HOURS.
- Oracle: selection_manifest/comparison_matrix tại lock là bảng sensitivity; không có namespace resultID độc lập được bịa thêm. Integration IDs liên quan giữ mapping nguồn.

**Đề cương cấp2/cấp3 và nhiệm vụ chứng minh:**

### 6.1 Các sự kiện thanh lý Aave trong cửa sổ lịch sử

Claim anchors: P2:C09, P2:C10, INT:CL_INT_HISTORICAL_TIERS_PRESERVED.

- **6.1.1 Thiết kế cửa sổ và event census:** Trình bày census 28 Pool events, 27 Graph matches và một RPC-only event trong cửa sổ đã khai báo; không suy độ phủ toàn bộ lịch sử.
- **6.1.2 Bốn tầng liên hệ:** Phân biệt 1 tuyến chuyển tài sản xác minh, 2 cùng giao dịch, 23 cùng block, 1 gần thời gian trong 27 matches. Nêu mức bằng chứng khác nhau của từng loại.
- **6.1.3 Điều gì có thể đối chiếu với mô hình:** Dùng quan sát tuyến và thời điểm để đối chiếu tính khả dĩ của các kênh; giữ ranh giới chưa xác lập nhân quả hoặc truyền giá oracle lịch sử.

### 6.2 Terra và giới hạn kiểm chứng hồi cứu

Claim anchors: P2:C16, P2:C17, P2:C29, P2:C30, INT:CL_INT_TERRA_NEGATIVE_PRESERVED.

- **6.2.1 Cơ chế và khác biệt thể chế:** Đặt S17/S18 như hai phiên bản của cùng nghiên cứu. So sánh cơ chế run và phản hồi Terra với cho vay Aave mà không chuyển tham số giữa hai ca.
- **6.2.2 Tái dựng và cutoff safe:** Phân biệt demo, audit, conditional replay và strict OOS. Tính đúng của cutoff thông tin không loại bỏ việc lựa chọn mô hình đã tham khảo sự kiện.
- **6.2.3 Kết quả âm của cảnh báo:** Giữ 0 giờ HIGH trước mất neo ban đầu và lead −45 giờ. Không chọn riêng tín hiệu trước ngưỡng UST 0,90 USD để tuyên bố dự báo ngoài mẫu thành công.

### 6.3 Mạng cấu trúc và ý nghĩa chỉ số trung tâm

Claim anchors: P2:C25, P2:C26, P2:C27, P2:C28.

- **6.3.1 Các node và kênh đã mô hình hóa:** Mô tả các node và kênh của mạng dự án; đánh dấu cạnh truyền giá là giả định mô hình. Không coi mạng con là bản đồ đầy đủ của DeFi.
- **6.3.2 Từ typed graph tới graph gộp:** Tách khái niệm node–layer của mạng nhiều lớp khỏi graph gộp dùng để tính centrality; giải thích quy tắc gộp độ mạnh cạnh theo mã.
- **6.3.3 Centrality và rủi ro kinh tế:** Giải thích betweenness theo đường đi ngắn nhất, không đồng nhất với đóng góp vào tổn thất. DebtRank chỉ là đối chứng phương pháp, chưa được triển khai.

### 6.4 Tổng hợp các cấp bằng chứng

Claim anchors: P2:C17, P2:C30, INT:CL_INT_HISTORICAL_TIERS_PRESERVED.

- **6.4.1 Bảng vai trò của từng lớp kiểm chứng:** So sánh quan sát, suy dẫn, mô phỏng và kiểm tra mã theo câu hỏi mà từng lớp trả lời; hash integrity không tự tạo bằng chứng nhân quả.
- **6.4.2 Kết nối với sáu câu hỏi chính:** Chỉ ra vai trò bổ trợ về phương pháp và giới hạn của Terra/network. Không thêm RQ hoặc để các mở rộng thay câu trả lời sáu câu hỏi chính.

**Exhibit/công thức cần chuẩn bị:** T6.1, F6.1, F6.2, T6.2. Chi tiết units/axes/policy/format và status trong exhibit plan. Không coi các mã P3 T/F/E này là scientific result IDs đã tồn tại.

**Artifact locators, tất cả đọc từ scientific lock:**

- `data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/historical_evidence.csv` (nội dung đã đọc G0)
- `docs/research_final/LEVEL3_HISTORICAL_EVENT_STUDY.md` (nội dung đã đọc G0)
- `data/processed/research_final/frozen_v3/tables/terra_limitations.csv` (nội dung đã đọc G0)
- `data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json` (nội dung đã đọc G0)
- `data/processed/research_final/network/structural_centrality.json` (nội dung đã đọc G0)
- `data/processed/research_final/network/structural_graph.json` (Git object đã xác định; content cần Codex evidence pack)
- `sim/network/metrics.py` (nội dung đã đọc G0)
- `docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md` (nội dung đã đọc G0)

**Giới hạn bắt buộc đặt đúng vị trí:**

- L09: 28 Pool events/27 Graph matches và tiers 1/2/23/1 chỉ theo cửa sổ đã khai báo; receipt route và đồng xuất hiện không xác lập lây lan nhân quả.
- L10: Terra tái dựng hồi cứu khác dự báo; giữ HIGH trước initial depeg bằng 0, lead −45 giờ và kết luận âm ngoài mẫu; không dùng Terra xác nhận tham số Aave.
- L11: Graph typed/aggregated và centrality cấu trúc chưa là full multilayer contagion, DebtRank đã triển khai hoặc xếp hạng rủi ro toàn DeFi.
- L13: Hai raw borrower CSV lớn vẫn chưa được Work đọc đầy đủ/cell-by-cell; giữ source access labels, U01–U08 và mức abstract/metadata/code; S17/S18 cùng nghiên cứu.

**Suy luận cấm:** actual Aave=Uniswap spot; oracle-independent cascade; newly eligible=executed; tần suất mô hình=xác suất khủng hoảng; same-block=causal transmission; modeled debt/loss=realized loss; Terra forecast thành công; graph gộp=full multilayer. Chỉ giữ những giới hạn liên quan trong prose để không lặp phủ định máy móc.

**Acceptance riêng của chương:**

- 28/27 và các tầng liên hệ có đúng mẫu số.
- Kết quả âm Terra được trình bày rõ, không bị che bởi fit hoặc ngưỡng chọn thuận lợi.
- Graph gộp không được gọi là full multilayer; extensions không thay sáu RQ.
- Đạt rubric CP1–CP6 và chưa có P0/P1; chapter lock chỉ do Commander cấp.

## Chương 7 Thảo luận đóng góp hạn chế và kết luận

**Mục tiêu học thuật:** Tổng hợp trả lời sáu RQ và xác định đóng góp, ứng dụng, ranh giới ngoại suy có thể bảo vệ.

**Luận điểm trung tâm cần phát triển:** DeFiStress bổ sung quy trình đối chiếu có truy vết và chỉ ra độ nhạy giả định; tính hữu ích dựa vào điều kiện công bố, không phải tuyên bố đại diện toàn thị trường.

**Vai trò:** Khép chuỗi problem→theory→design→validation→results→inference; không thêm kết quả mới.

**RQ liên quan:** RQ1, RQ2, RQ3, RQ4, RQ5, RQ6.

**Depth/ưu tiên:** Cao về synthesis; ngắn hơn Ch5, không sinh metric/bảngsốlần2.

**Kế thừa:** 5.1–5.6;4.11;Phụ lục1. Xem audit để biết phần cần thay số/diễn đạt.

**Dependencies:** trước Ch1, Ch2, Ch3, Ch4, Ch5, Ch6; sau final assembly sau7chapter locks. Đây là quan hệ nội dung, không cho phép viết chương sau khi chương trước chưa được Commander duyệt.

**Bằng chứng được phép dùng:**

- Scholarly/P2 IDs: P2:C11, P2:C17, P2:C19, P2:C22, P2:C24, P2:C30, P2:C31, P2:C35.
- Accepted Integration IDs: INT:CL_INT_RQ1_POLICY_CONDITIONAL, INT:CL_INT_RQ2_TWO_CHANNELS, INT:CL_INT_ELIGIBLE_NOT_EXECUTED, INT:CL_INT_RQ3_PRESERVED, INT:CL_INT_RQ4_PRESERVED, INT:CL_INT_RQ5_PRESERVED, INT:CL_INT_RQ6_PRESERVED, INT:CL_INT_HISTORICAL_TIERS_PRESERVED, INT:CL_INT_TERRA_NEGATIVE_PRESERVED.
- Supporting S IDs: S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19, S20, S21, S22, S23, S30.
- Frozen/Integration result IDs: HIST_DIRECT_TRANSFER_PATHS, HIST_GRAPH_MATCHED_EVENTS, HIST_RPC_CENSUS_EVENTS, HIST_SAME_BLOCK_ASSOCIATION, HIST_SAME_TX_COOCCURRENCE, HIST_TIME_WINDOW_ASSOCIATION, INT_A_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, INT_A_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES, INT_A_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES, INT_A_NEWLY_ELIGIBLE_SKIPPED_INSTANCES, INT_B_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, INT_C_MODERATE_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, INT_C_WEAK_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4, MC_INDEPENDENT_PATHS_VALIDATED, RQ1_GRID60_DEPTH2, RQ1_MC_SEVERE_DEPTH2_COUNT, RQ2_CANONICAL_DEPTH_2PCT, RQ2_DEPTH2_HAIRCUT90_COUNT, RQ2_DEPTH2_HAIRCUT95_COUNT, RQ3_CAPITAL_100_LIQUIDATED, RQ3_CAPITAL_25_LIQUIDATED, RQ3_DELAY_SEVERITY_CHANGE, RQ4_IMMEDIATE_PRICE_IMPACT, RQ4_SPREAD_ARB0, RQ4_SPREAD_ARB100, RQ5_HF_LT1_USDC_090, RQ5_HF_LT1_USDC_100, RQ5_HF_LT1_USDC_110, RQ5_LIQUIDATED_DEBT_TOKEN_QTY, RQ5_LIQUIDATED_DEBT_USD, RQ6_BONUS103_SEIZED, RQ6_BONUS107_SEIZED, RQ6_LT083_UNLIQUIDATED, RQ6_LTV0755_CAPACITY, RQ6_LTV0825_CAPACITY, TERRA_INITIAL_DEPEG_HIGH_LEAD, TERRA_PRE_DEPEG_HIGH_ALERT_HOURS.
- Oracle: selection_manifest/comparison_matrix tại lock là bảng sensitivity; không có namespace resultID độc lập được bịa thêm. Integration IDs liên quan giữ mapping nguồn.

**Đề cương cấp2/cấp3 và nhiệm vụ chứng minh:**

### 7.1 Sáu câu trả lời trong một khung diễn giải

Claim anchors: P2:C11, P2:C17, INT:CL_INT_RQ1_POLICY_CONDITIONAL, INT:CL_INT_RQ2_TWO_CHANNELS, INT:CL_INT_RQ3_PRESERVED, INT:CL_INT_RQ4_PRESERVED, INT:CL_INT_RQ5_PRESERVED, INT:CL_INT_RQ6_PRESERVED.

- **7.1.1 Tóm lược có điều kiện:** Dùng các accepted sets của RQ matrix để tóm lược mỗi câu trả lời và dẫn bảng Chương 5; không sao chép lại toàn bộ phần kết quả.
- **7.1.2 Tại sao các kết quả khác nhau:** Giải thích khác biệt do policy, tuyến thực thi, denominator và horizon; đặt kết quả S13 và Wave 2 của mô hình vào đúng thiết kế riêng.

### 7.2 Đóng góp có thể bảo vệ

Claim anchors: P2:C31, P2:C30, INT:CL_INT_ELIGIBLE_NOT_EXECUTED, INT:CL_INT_TERRA_NEGATIVE_PRESERVED.

- **7.2.1 Đóng góp phương pháp:** Đánh giá đóng góp tích hợp snapshot, thực nghiệm phản thực và chuỗi truy vết. Không tự nhận first-ever hoặc phương pháp đã chứng minh ưu việt.
- **7.2.2 Đóng góp bằng chứng có điều kiện:** Tổng hợp bằng chứng về độ nhạy A/B/C và eligible/executed trong thiết kế khóa; không chuyển thành kết luận nhân quả bên ngoài mô hình.
- **7.2.3 Minh bạch kết quả âm:** Giải thích giá trị của các kết quả zero và Terra negative cùng các source limitations; trình bày chúng như điều kiện diễn giải, không né tránh.

### 7.3 Hạn chế và phạm vi hiệu lực

Claim anchors: P2:C17, P2:C19, P2:C22, P2:C24, P2:C35.

- **7.3.1 Nội bộ mô hình và dữ liệu:** Tổng hợp các biên cohort, pool, tác nhân đại diện, oracle, USDC và thực thi có nguồn vốn. Liên kết mỗi giới hạn với kết luận chịu ảnh hưởng.
- **7.3.2 Ngoại suy và chất lượng nguồn:** Giữ ranh giới lịch sử không nhân quả, tần suất mô hình, source access và hai raw CSV chưa đọc đầy đủ; công bố đúng hash domains.
- **7.3.3 Audit các kết luận bị loại:** Nếu thảo luận bốn records bị loại, dùng chúng để giải thích ranh giới suy luận và lịch sử chỉnh sửa; không đưa vào accepted findings.

### 7.4 Hàm ý nghiên cứu và thực tiễn

Claim anchors: P2:C17, P2:C31.

- **7.4.1 Hàm ý theo dõi rủi ro:** Rút ra hàm ý xem xét đồng thời HF, thanh khoản, tuyến thực thi và vốn. Nêu tư cách hàm ý nghiên cứu, không là khuyến nghị tham số quản trị đã hiệu chỉnh.
- **7.4.2 Hướng phát triển có kiểm soát:** Đặt oracle history, nhiều snapshot và arbitrage có nguồn vốn vào future work; không mở rộng phạm vi thực nghiệm của bản thảo hiện tại.

### 7.5 Kết luận và điều kiện sử dụng kết quả

Claim anchors: P2:C31, P2:C17.

- **7.5.1 Kết luận cuối theo scientific lock:** Kết nối vấn đề, kết quả và đóng góp trong một kết luận có điều kiện, dùng các kết quả đã trình bày và tránh chuỗi câu phủ định lặp lại.
- **7.5.2 Điểm kết thúc nghiên cứu hiện tại:** Xác định điểm kết thúc của nghiên cứu hiện tại; dữ liệu, mô hình hoặc claim mạnh hơn cần change review riêng trước khi đưa vào báo cáo.

**Exhibit/công thức cần chuẩn bị:** T7.1, T7.2. Chi tiết units/axes/policy/format và status trong exhibit plan. Không coi các mã P3 T/F/E này là scientific result IDs đã tồn tại.

**Artifact locators, tất cả đọc từ scientific lock:**

- `data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json` (nội dung đã đọc G0)
- `data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json` (nội dung đã đọc G0)
- `docs/research_final/LITERATURE_VERIFIED.md` (nội dung đã đọc G0)

**Giới hạn bắt buộc đặt đúng vị trí:**

- L01: Kết quả cascade là mô phỏng phản thực có điều kiện theo policy, cohort và cấu hình thanh khoản; A/B/C chưa được xác minh là feed Aave/Chainlink lịch sử.
- L02: Một block 26045352, 454 verified borrowers; 109 là cohort WETH-collateral-enabled/USDC-debt riêng; một Uniswap venue, không đại diện toàn thị trường.
- L03: Phân biệt HF danh mục mới dưới 1, engine evaluation, route eligibility và execution có debt repaid dương; đếm borrower-case-policy instances, không unique wallets.
- L04: 280/10.000 chỉ Severe Policy A; mười targeted MC paths chọn theo A-depth2; không ước lượng xác suất thị trường, không suy không thể có depth≥3 ngoài tập thử.
- L05: Liquidator/arbitrageur đại diện; vốn không recycle, kế hoạch vượt vốn không tự chia nhỏ; kết quả gas/capacity/delay chỉ trong miền thử.
- L06: Arbitrage là price repositioning, chưa funded executable swap; tác động giá tức thời khác spread sau arbitrage.
- L07: RQ5 chỉ kênh định giá nợ USDC; token quantity khác USD-equivalent; chưa redemption/liquidity/confidence/settlement đầy đủ.
- L08: Haircut 90/95% là extreme counterfactual tails, chưa có bằng chứng lịch sử tương ứng; không có independent local-fork execution được kiểm chứng.
- L09: 28 Pool events/27 Graph matches và tiers 1/2/23/1 chỉ theo cửa sổ đã khai báo; receipt route và đồng xuất hiện không xác lập lây lan nhân quả.
- L10: Terra tái dựng hồi cứu khác dự báo; giữ HIGH trước initial depeg bằng 0, lead −45 giờ và kết luận âm ngoài mẫu; không dùng Terra xác nhận tham số Aave.
- L11: Graph typed/aggregated và centrality cấu trúc chưa là full multilayer contagion, DebtRank đã triển khai hoặc xếp hạng rủi ro toàn DeFi.
- L12: Modeled bad debt/composite tail exposure khác realized financial loss hoặc market expected shortfall; debt repaid không phải loss.
- L13: Hai raw borrower CSV lớn vẫn chưa được Work đọc đầy đủ/cell-by-cell; giữ source access labels, U01–U08 và mức abstract/metadata/code; S17/S18 cùng nghiên cứu.
- L14: Git LF blob bytes khác Windows CRLF checkout bytes; kết quả kiểm thử do Codex báo cáo khác lượt Work tự chạy; không đồng nhất hash domains.

**Suy luận cấm:** actual Aave=Uniswap spot; oracle-independent cascade; newly eligible=executed; tần suất mô hình=xác suất khủng hoảng; same-block=causal transmission; modeled debt/loss=realized loss; Terra forecast thành công; graph gộp=full multilayer. Chỉ giữ những giới hạn liên quan trong prose để không lặp phủ định máy móc.

**Acceptance riêng của chương:**

- Sáu RQ được trả lời bằng accepted IDs.
- Đóng góp tích hợp và truy vết được giới hạn đúng bằng chứng.
- Đủ các mandatory limitations, giữ kết quả âm.
- Không có claim first-ever, realized loss, xác suất thị trường hoặc nhân quả Mainnet.
- Đạt rubric CP1–CP6 và chưa có P0/P1; chapter lock chỉ do Commander cấp.

## Các quyết định xin Commander phê duyệt tại G0

1. Phê duyệt hoặc sửa đúng cấu trúc bảy chương và primary destinations; không đổi sáu RQ/scientific lock.
2. Duyệt exhibit requests và quyền sở hữu Work/Codex trước khi giao evidence packs; mọi figure chỉ từ dữ liệu khóa.
3. Xác nhận template/citation conventions khi có nguồn chính thức; thiếu template không chặn nội dung blueprint.
4. Sau approval riêng, cho phép Chương 1 bắt đầu CP1. Không tự chuyển sang Chương 1 hoặc Chương N+1 theo thời gian hay do một file xuất hiện.

**Điểm dừng hiện tại: AWAITING_COMMANDER_BLUEPRINT_APPROVAL.** Không có chapter draft, không DOCX final, không sửa numeric/source artifacts, không tự chapter lock hoặc scientificlock.
