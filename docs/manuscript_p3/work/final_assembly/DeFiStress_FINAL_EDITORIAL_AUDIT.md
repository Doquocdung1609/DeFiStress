# DeFiStress — Final Editorial Audit

**Trạng thái đề nghị:** `P3_FINAL_MANUSCRIPT_READY_FOR_COMMANDER_REVIEW`  
**Loại kiểm tra:** Work editorial self-review, static/content checks và visual QA; không phải phản biện độc lập bên ngoài.  
**Template gate:** `TEMPLATE_VERIFICATION_PENDING`. Chưa cấp Final Submission Lock.

## 1. Phiên bản và phạm vi

- Scientific Content Lock: `3f6e5302483681209e2408531eb5a15389f9fded`.
- Blueprint Lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Bảy chương kế thừa tại integration: `35560dd884db43fe4f8eb50d52fb0bd1abf47bba`.
- Nhánh bàn giao: `research/p3-final-manuscript-assembly-work`; base `feat/terra-model-v2`.
- Không thay đổi source khoa học, numerical registry, mã, engine hay bảy file chương gốc. Bản hợp nhất, hình và hồ sơ này là các file mới. Không chạy mô phỏng, Monte Carlo, retune hoặc thống kê mới.
- Commit bàn giao chính xác được ghi trong Draft PR; không dùng SHA tự tham chiếu bên trong chính commit đó.

## 2. Nguồn thực sự đọc và xác minh

Đã đọc toàn văn bảy chương, hồ sơ claim/citation và self-review tương ứng tại integration trên; Blueprint, allocation matrix, exhibit/formula crosswalk, rubric và baseline audit tại Blueprint Lock; Final Accepted Claims Registry v1.1, six-RQ matrix, provenance, manifest, hai narrative registry reports, P2 literature/evidence matrix/APA/terminology/crosswalk; các bảng Frozen, Oracle comparison/selection/summary và Integration summaries; nguồn validation, Terra và network thực sự dùng trong chương/hình. Các bản lưu cục bộ chỉ được dùng sau khi hash Git blob khớp cây repository đã truy xuất bằng connector.

Kiểm tra nội dung file: **195/195 Git blobs** khớp integration; **160** đường dẫn chung khớp chính xác Scientific Lock và **174** khớp Blueprint Lock. Không mặc định default branch là nguồn. Bản kiểm tra này xác nhận các file đã có trong inventory, không tuyên bố đã đọc mọi file repository hoặc hai CSV lớn còn giới hạn bên dưới.

| Chương | File nguồn | Git blob SHA-1 tại integration |
|---|---|---|
| 1 | `docs/manuscript_p3/work/chapter_01/CHAPTER_01_FULL_DRAFT_v1.md` | `c3fffec83f427c52c595dd02fd73a9c81db5cfcd` |
| 2 | `docs/manuscript_p3/work/chapter_02/CHAPTER_02_FULL_DRAFT_v1.md` | `b73f337c99cdf6a137fac4d54e9b49b1aebb3a40` |
| 3 | `docs/manuscript_p3/work/chapter_03/CHAPTER_03_FULL_DRAFT_v1.md` | `f8609f120d6f8e1fa9bb3aa9393fe45092888439` |
| 4 | `docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md` | `5fe370a245e11a6ae9a7f2cc6349dc30d97893a2` |
| 5 | `docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md` | `9be3495921243ad5980177071a7a8cd8370e1ce2` |
| 6 | `docs/manuscript_p3/work/chapter_06/CHAPTER_06_FULL_DRAFT_v1.md` | `342accacd1441eb228ac672a5fe7625ee7514a09` |
| 7 | `docs/manuscript_p3/work/chapter_07/CHAPTER_07_FULL_DRAFT_v1.md` | `af707a29ba951d117ada7bbfb9dd692e5079e605` |

Bảy attachments được trích xuất văn bản để tìm quy định trình bày; báo cáo cũ chỉ là nguồn tổ chức tham khảo. Không dùng attachment để nâng mức xác minh nguồn P2. Không tìm thấy template/quy định trường chính thức trong tập nguồn được cung cấp. Báo cáo ví dụ năm 2024 không được coi là quy định hiện hành.

## 3. Hợp nhất và kiểm tra khoa học xuyên chương

Giữ đủ bảy chương theo thứ tự, cùng toàn bộ heading chính/tiểu mục đã khóa. Bổ sung tóm tắt tiếng Việt, từ khóa, danh mục viết tắt, ba danh mục tự động, một bibliography và bốn phụ lục. Chỉ hợp nhất ghi chú provenance/bibliography trùng lặp, đưa công thức kỹ thuật vào vị trí phụ lục đã duyệt và cập nhật caption sau khi hình thực sự được render. Không viết lại nghiên cứu hoặc rút bỏ chiều sâu lập luận.

| Nội dung | Kết quả và ranh giới bảo toàn |
|---|---|
| Registry | 48 records = 35 P2 + 13 Integration; 44 accepted affirmative và 4 disallowed giữ nguyên cấp bằng chứng |
| Sáu RQ | RQ1–RQ6 chép nguyên văn từ six-RQ matrix; mỗi câu xuất hiện đúng hai lần trong nội dung hợp nhất (T1.1 và T7.1) |
| Snapshot/cohort | Block 26045352; 454 danh mục RPC-verified, 109 tuyến/cohort WETH/USDC, không đồng nhất hai phạm vi |
| Hai lưới | 32 ô: 12/20/0; 60 ô: 18/38/4 theo depth0/1/2; hai miền tham số riêng |
| Oracle | A/B/C weak/C moderate là giả định mô hình, không phải feed Aave/Chainlink đã được đối chiếu lịch sử |
| Tập lựa chọn | Bốn selected deterministic:4/0/0/0; mười targeted MC:10/0/0/2; không dùng làm ước lượng xác suất ngoài tập chọn |
| Severe | 280/10.000 dưới Policy A; nested prefixes và stored Wilson bounds; không gọi là xác suất khủng hoảng thị trường |
| Eligibility/execution | A35/14, B0/0, C weak6/0, C moderate11/2; đơn vị borrower–case–policy instances, không phải unique wallets |
| Skips | 36 instances có đối chiếu `NO_MODELLED_USDC_DEBT`; giữ raw engine reason `NOT_ELIGIBLE` riêng với giải thích derived; không suy ra nợ đã trả hết sau Wave1 |
| RQ6 LTV | Hai tổng 50.797.988,977634266 và 53.675.575,37423773 USD thuộc 255 danh mục có WETH thế chấp và có nợ; tách109 |
| RQ6 LT | 229830.81461902 và 96839.39478531 là USD nợ danh mục chưa thanh lý tại USDC/USD=1; không gọi tokenUSDC, không tự gán109 |
| RQ4/RQ5 | Arbitrage price repositioning khác funded swap; lượng USDC khác USD-equivalent; debt valuation không phải toàn cơ chế depeg |
| Lịch sử | 28 Pool events/27 Graph-matched/1 RPC-only; tiers1/2/23/1 trên27; temporal/same-block association khác causal transmission |
| Terra | 0 HIGH/1.630 giờ trước initial depeg, lead−45giờ; cutoff-safe derived validation khác raw observation và dự báo out-of-sample thành công |
| Network | Cấu trúc8nút/9cạnh, metric lưu sẵn; không mô tả như full multilayer contagion/DebtRank đã kiểm chứng |

Bốn record audit-only: `CL_FROZEN_RQ1_UNQUALIFIED_WORDING`, `CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING`, `CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT`, `CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION`. Không dùng làm affirmative findings. Giới hạn representative agents, vốn không recycle, không tự chia kế hoạch vượt vốn, một venue/cohort/snapshot, severe tails và không có independent local-fork transaction execution vẫn được công bố.

CH05-P01/P02 đã được Commander giải quyết tại [quyết định PR21](https://github.com/Doquocdung1609/DeFiStress/pull/21#issuecomment-6214848952). Metadata Frozen cũ về cohort/đơn vị không thống nhất được giữ như lịch sử nguồn, không tiếp tục trình bày là vấn đề chờ Commander. Bản hợp nhất dùng artifact chi tiết và diễn giải đã được duyệt; không sửa registry để che khác biệt.

## 4. APA và mức tiếp cận nguồn

**102 mục bibliography lặp giữa các chương → 30 bản ghi chuẩn P2 S01–S30**, mỗi bản ghi xuất hiện một lần. Nội dung từng mục khớp nguyên văn danh mục APA đã xác minh; không tạo DOI/URL, tác giả, năm hoặc số trang mới. Các danh tính citation trong bài đã đối chiếu với 30 bản ghi và citation audit từng chương. Quy ước author–year được giữ; cách gọi “và cộng sự” trong văn xuôi Việt và “et al.” trong một số ngoặc dẫn đều trỏ cùng danh tính nguồn.

S17 JFE2026 và S18 NBER2023 được giữ như hai phiên bản của một nghiên cứu, không gộp sai năm hoặc đếm thành hai bằng chứng độc lập. Phụ lục C giữ đủ30 access records: abstract/metadata/preview/code/practitioner khác fulltext; U01–U08 vẫn chưa được nâng cấp và không đưa thành bibliography đã kiểm chứng. Phạm vi citation không dùng literature để chứng thực engine. Wilson score interval được phân biệt adjusted Wald.

**76 permalinks** nội bộ trong manuscript đã kiểm tra commit/path tồn tại ở Scientific/Blueprint Lock. Tài liệu project, code evidence và scholarly citation được phân biệt. Lần assembly không mở lại vòng xác minh publisher/link ngoài repo; không tuyên bố mọi URL publisher còn truy cập được tại ngày bàn giao.

## 5. Bảng, hình và công thức

**14 bảng approved + 2 bảng phụ trợ** (viết tắt, danh mục9cạnh) đều là Word tables có thể chỉnh sửa. **11/11 hình** đã render từ nguồn khóa, có PNG và SVG; không còn Mermaid/display-spec chưa render đóng vai hình hoàn chỉnh. **8/8 công thức** E3.1–E3.8 là Word OMML có thể chỉnh sửa (59 native math objects nếu tính cả ký hiệu inline). E3.2/E3.3/E3.7 đặt ở Phụ lục A theo Blueprint; chỉ tách dòng E3.4/E3.5 để vừa lề, không thay đại số.

| Approved ID | Tên | Trạng thái |
|---|---|---|
| T1.1 | Sáu câu hỏi nghiên cứu và phạm vi bằng chứng | EDITABLE_WORD_TABLE |
| T2.1 | Đối thoại giữa các nhánh nghiên cứu | EDITABLE_WORD_TABLE |
| F3.1 | Trình tự xử lý và kênh phản hồi trong mô hình | RENDERED_FROM_LOCKED_SOURCES |
| T3.1 | Tác nhân, trạng thái thông tin và các cổng quyết định | EDITABLE_WORD_TABLE |
| T3.2 | Các tập thực nghiệm, miền tham số và mẫu số | EDITABLE_WORD_TABLE |
| T3.3 | Từ điển trạng thái, biến và chỉ tiêu | EDITABLE_WORD_TABLE |
| F4.1 | Chuỗi nguồn gốc và đối chiếu trạng thái canonical | RENDERED_FROM_LOCKED_SOURCES |
| T4.1 | Chất lượng dữ liệu người vay và đối chiếu HF tại trạng thái canonical | EDITABLE_WORD_TABLE |
| T4.2 | Các lớp kiểm tra, người thực hiện và ranh giới xác nhận | EDITABLE_WORD_TABLE |
| F5.1 | Phân bố depth trong hai miền thử tất định | RENDERED_FROM_LOCKED_SOURCES |
| T5.1 | Độ sâu giữ lại trong các tập diagnostic theo chính sách định giá | EDITABLE_WORD_TABLE |
| T5.2 | Từ newly eligible đến thực thi Wave 2 trong tập kiểm toán được chọn | EDITABLE_WORD_TABLE |
| F5.2 | Phân nhánh giữa sức khỏe danh mục và thực thi trên tuyến tài sản | RENDERED_FROM_LOCKED_SOURCES |
| F5.3 | Sức hấp thụ giao dịch và giá đưa vào HF là hai lớp khác nhau | RENDERED_FROM_LOCKED_SOURCES |
| F5.4 | Ràng buộc vốn và độ trễ xử lý trong miền thử Professor Demo | RENDERED_FROM_LOCKED_SOURCES |
| F5.5 | Tác động tức thời và độ lệch còn lại theo capacity arbitrage | RENDERED_FROM_LOCKED_SOURCES |
| T5.3 | Giá khoản nợ USDC, HF trực tiếp và đơn vị nợ đã hoàn trả | EDITABLE_WORD_TABLE |
| F5.6 | Ba tham số, ba cơ chế và ba đại lượng kết quả | RENDERED_FROM_LOCKED_SOURCES |
| F5.7 | Tần suất có điều kiện và khoảng Wilson theo checkpoint và batch | RENDERED_FROM_LOCKED_SOURCES |
| T6.1 | Event census và các tầng liên hệ thanh lý–DEX | EDITABLE_WORD_TABLE |
| F6.1 | Kết quả âm của cảnh báo Terra theo ranh giới thông tin đã khai báo | RENDERED_FROM_LOCKED_SOURCES |
| F6.2 | Graph dị thể, phép gộp cạnh và phạm vi centrality | RENDERED_FROM_LOCKED_SOURCES |
| T6.2 | Vai trò và ranh giới của các lớp bằng chứng | EDITABLE_WORD_TABLE |
| T7.1 | Sáu câu trả lời và điều kiện diễn giải | EDITABLE_WORD_TABLE |
| T7.2 | Đóng góp tích hợp, đối chiếu và truy vết trong phạm vi đề tài | EDITABLE_WORD_TABLE |

Giữ approved IDs kể cả vị trí T3.3 trướcT3.2 hoặc F5.3 trướcF5.2: đây là định danh crosswalk, không tự đánh lại làm gãy provenance. Caption có số theo chương, ID, nguồn, đơn vị/mẫu số và giới hạn. `figures/RENDER_PROVENANCE.json` chứa các locator, selector, result IDs, scope, source blobs và SHA256 từng PNG/SVG; nó phân biệt source spec G0 với trạng thái đã render của lần assembly này.

F3.1 là sơ đồ scheduler/feedback, không causal graph Mainnet. F4.1 là lineage kiểm chứng. F5.3 có hai panel độc lập (count/price), không ghép trục thành executable depth. F5.6 tách255/LTUSD/bonusWETH. F5.7 chép stored intervals, không tính lại; lower bound gần0 của LowLiquidity chỉ được hiển thị theo độ phân giải, không sửa số nguồn. F6.1 phân biệt hai estimands, F6.2 sao chép centralities và typed edges, không recompute. Không sinh dữ liệu để lấp hình.

## 6. Nhật ký biên tập có mục tiêu

| Vị trí | Thao tác | Nội dung/quyết định |
|---|---|---|
| Chương 3 / văn bản | RELOCATE | E3.2/E3.3/E3.7 chuyển đến Phụ lục A theo Blueprint; giữ nguyên công thức và giải thích. |
| Chương 3 / văn bản | CONSOLIDATE_VERSION_NOTE | Hợp nhất ghi chú phiên bản vào phụ lục; bảo toàn nguồn. |
| Chương 3 / văn bản | ASSEMBLY_VERSION_NOTE | Hợp đồng provenance của nghiên cứu giữ riêng nguồn khoa học và implementation, phiên bản Blueprint cho bố cục và vị trí trình bày, cùng mốc hợp nhất bảy chương được ghi tại Phụ lục B. Mỗi phát biểu phương pháp quan trọng được nối với registry ID được chấp nhận, hàm hoặc selector artifact, loại bằng chứng và giới hạn. Mỗi exhibit giữ ID Work và các template Codex liên quan nhưng không đổi template mapping thành chứng nhận hình đã render. |
| Chương 3 / F3.1 | RENDER_EXHIBIT | Sơ đồ luồng trạng thái từ đặc tả mô hình; giá định giá được giữ trong wave và cập nhật sau arbitrage. Nhánh lặp trong wave khác nhánh mở wave mới. Nguồn: run_simulation, OraclePolicy và quy tắc tác nhân tại Scientific Lock. Mũi tên không biểu diễn bằng chứng truyền nhiễm Mainnet. |
| Chương 4 / F4.1 | RENDER_EXHIBIT | Nguồn: snapshot block 26045352, bộ đọc Aave/Uniswap, Frozen manifest và result registry. Đơn vị: ứng viên hoặc danh mục; cohort 109 là tập con WETH/USDC của 454 danh mục có nợ được giữ sau RPC. Sơ đồ biểu diễn lineage dữ liệu và kiểm chứng, không phải mạng truyền nhiễm. |
| Chương 5 / văn bản | CONSOLIDATE_VERSION_NOTE | Hợp nhất ghi chú phiên bản vào phụ lục; bảo toàn nguồn. |
| Chương 5 / F5.1 | RENDER_EXHIBIT | Nguồn: Frozen rq1_deterministic_depth.csv; các result IDs RQ1_GRID32_MAX_DEPTH, RQ1_GRID60_DEPTH0/1/2. Số ô depth 0/1/2 lần lượt 12/20/0 trên 32 và 18/38/4 trên 60 ô. Policy A; hai miền tham số khác nhau. Lưới mở rộng chứa haircut 90%/95% là đuôi phản thực; số ô không phải xác suất thị trường. |
| Chương 5 / F5.3 | RENDER_EXHIBIT | Nguồn: Frozen rq2_liquidity.csv và Oracle comparison_matrix.csv, case DET_D2_M40_H90. Panel (a): số ô depth 2 trên lưới 60 ô theo haircut, Policy A; chỉ haircut 0% là pool canonical chưa biến đổi. Panel (b): giá định giá sau Wave 1 theo bốn policy giả định, đơn vị USD/WETH tại USDC/USD = 1; các đường DEX và tham chiếu là mốc chung đã lưu. Các trục và mẫu số độc lập; panel (a) không phải đường executable depth. |
| Chương 5 / F5.4 | RENDER_EXHIBIT | Nguồn: Frozen rq3_constraints.csv. Panel (a): vốn/nhu cầu tham chiếu và USDC token hoàn trả; panel (b): delay steps và processing delay tính bằng giây. Mỗi điểm là một case quét, Policy A, snapshot cố định. Vốn không recycle, kế hoạch không split; recovery = 0 không đồng nghĩa processing delay = 0. |
| Chương 5 / F5.2 | RENDER_EXHIBIT | Nguồn: T5.2, Integration Addendum và Scientific Pre-Merge Audit tại Scientific Lock. Đây là sơ đồ cổng của mô hình, không phải chuỗi giao dịch Mainnet. 36 skips đã đối chiếu là borrower–case–policy instances, có raw reason NOT_ELIGIBLE và lời giải thích suy dẫn NO_MODELLED_USDC_DEBT. Các cổng nguồn lực/lợi nhuận được thể hiện để giải thích thiết kế, không dùng thay nguyên nhân của 36 skips này. |
| Chương 5 / F5.5 | RENDER_EXHIBIT | Nguồn: Frozen rq4_arbitrage.csv; RQ4_IMMEDIATE_PRICE_IMPACT và RQ4_SPREAD_ARB0/100. Các tỷ lệ nguồn được hiển thị theo phần trăm (nhân 100), capacity 0/50/100% là ba cấu hình, không phải chuỗi thời gian. Cùng forced sale 4.4085464736063145 WETH, Professor Demo, Policy A. Arbitrage là price repositioning, chưa phải funded swap; residual gần 0 ở capacity 100% là kết quả số học của mô hình. |
| Chương 5 / F5.6 | RENDER_EXHIBIT | Nguồn: Frozen rq6_policy.csv và ba artifact RQ6 chi tiết corrected v2. Panel (a): LTV và khả năng vay tối đa (USD) trên 255 danh mục có WETH thế chấp và có nợ, khác cohort 109 WETH/USDC. Panel (b): LT WETH và giá trị nợ danh mục chưa thanh lý (USD), tại USDC/USD = 1; phạm vi theo tập vị thế truyền vào metric, chưa gán mẫu số 109. Panel (c): bonus và lượng WETH thu giữ. Nhãn hiệu lực theo quyết định CH05-P01/P02; metadata Frozen cũ được bảo lưu trong audit. Ba trục độc lập, không tạo một risk score hoặc lựa chọn governance tối ưu. |
| Chương 5 / F5.7 | RENDER_EXHIBIT | Nguồn: Frozen rq1_monte_carlo.csv. Các cận Wilson 95% được lấy nguyên từ nguồn, không tính lại. Panel (a): bốn nested prefixes cùng seed 20260914, Policy A; 280/10.000 paths Severe có depth ≥2, không quan sát depth ≥3. Panel (b): hai robustness seeds, mỗi seed 1.000 paths; panel (c): Low Liquidity định trước, 1.000 paths. Prefix không phải các mẫu độc lập cộng dồn; mười targeted diagnostic paths không nằm trên hình. Tần suất có điều kiện theo phân phối stress, không phải xác suất khủng hoảng thị trường. |
| Chương 5 / văn bản | EDITORIAL_RQ6 | Hai tổng 50797988.977634266 USD và 53675575.37423773 USD được tính trên 255 danh mục có WETH thế chấp và có nợ, theo `cohort_size=255` của artifact `rq6_ltv_capital_efficiency.json`. Tiêu chí này không bắt buộc nợ USDC dương, nên khác cohort 109 WETH/USDC dùng cho tuyến thanh lý. Phạm vi tính toán chi tiết là căn cứ diễn giải hai tổng; nhãn cohort chưa thống nhất trong metadata tổng hợp được ghi lại ở hồ sơ biên tập, cùng nguồn quyết định. |
| Chương 6 / văn bản | CONSOLIDATE_VERSION_NOTE | Hợp nhất ghi chú phiên bản vào phụ lục; bảo toàn nguồn. |
| Chương 6 / F6.1 | RENDER_EXHIBIT | Nguồn: TERRA_PRE_DEPEG_HIGH_ALERT_HOURS, TERRA_INITIAL_DEPEG_HIGH_LEAD, Frozen terra_limitations.csv và phase5_terra_early_warning_audit.json. Panel (a): 0 giờ HIGH trên 1.630 giờ trước initial depeg; panel (b): lead −45 giờ so với UST < 0,995, tức cảnh báo sau sự kiện. Hai đơn vị được tách trục. Đây là derived historical validation của thiết kế cutoff-safe, không phải raw observation về năng lực dự báo; không nhập với mẫu strict OOS V2. |
| Chương 6 / F6.2 | RENDER_EXHIBIT | Nguồn: corrected_run_v2/network/structural_graph.json và structural_centrality.json tại Scientific Lock. Panel (a) giữ đúng tám nút, chín typed edges; số cạnh liên kết với danh mục ở Phụ lục B, cạnh nét đứt có active = false và chỉ là tuyến tiềm năng. Panel (b/c) chép các chỉ số không thứ nguyên đã lưu, không tính lại. Cạnh song song được gộp max theo cặp có hướng khi tính metric; betweenness có hướng/không trọng số khác weighted influence chỉ lọc cạnh active. Đây là mạng con cấu trúc của dự án, chưa phải full multilayer contagion hoặc DebtRank. |

Sửa định dạng bổ sung: tái tạo paragraph properties trong cell để khắc phục renderer đẩy chữ ra ngoài bảng; đặt độ rộng cột, repeat header, bỏ fixed row height; dùng landscape cho T2.1 và T4.1; giữ caption/source trong cùng section; bỏ caption lặp từ image alt text; chuẩn hóa Times New Roman, heading đen, header/footer; thụt treo APA và giữ mục thư mục liền khối; sửa dấu `###` từng hiện như chữ thường ở phụ lục. Các sửa này không đổi giá trị trong bảng/công thức.

## 7. Kiểm tra DOCX thực tế

- **126 trang** trong bản render cuối; đã rà toàn bộ trang bằng contact sheets và mở riêng các trang cần kiểm tra; 42 trang có thay đổi cuối đã được rà lại. Render từ bản sao có byte-identical DOCX cho kết quả pixel-identical126/126 trang với bản v12 đã rà. Không coi chỉ thành công xuất file là visual QA.
- 3 trường Word TOC (mục lục, danh mục bảng, danh mục hình), 33 SEQ, 7 REF và165 PAGEREF; không có target bookmark thiếu. Cached page numbers **165/165** đã khớp render; các trường vẫn cập nhật được trong Word.
- 16 bảng,11 embedded images; ảnh giải mã đủ, ZIP CRC không lỗi; 8 native display equations. Kiểm tra numeric-token parity **14/14 bảng** so với các bảng chương gốc.
- Kiểm tra hình học PDF: không có text vượt vùng an toàn, không có raw TeX, broken REF hoặc dấu heading Markdown sót lại. Kiểm tra trực quan không thấy hình vỡ, cột tràn hoặc ký hiệu mất. Có hai section landscape; số trang liên tục, trang bìa không hiện số.
- Word fonts/fields/render có thể phân trang lại trên máy khác; cần cập nhật fields và rà lại trước nộp. Đây là đặc tính file có thể chỉnh sửa, không phải tuyên bố layout bất biến trên mọi môi trường.
- File cuối ghi atomically; kiểm tra ZIP và SHA sau render. **DOCX SHA256:** `15e1ae5d04429bbcd456886f4002b4977738c38dad58a6856610a5b3209f4285`; **bytes:** 2158504. Git SHA-1 blob và SHA256 bytes là hai định danh khác nhau; Git LF và checkout Windows CRLF cũng không mô tả là cùng hash.

Các lệnh kiểm tra thực tế: `python verify_final_assembly.py`; `python map_assembly_pages.py assembly_render_verified/assembly_docx_qa.pdf`; skill `render_docx.py` xuất126 trang; `python build_final_audit.py` kiểm tra path/hash/geometry/ZIP; kiểm tra XML Word và image decode bằng python-docx/lxml/Pillow. Không chạy full regression suite, mô phỏng hoặc independent Codex replay.

## 8. Vấn đề còn mở và đề nghị nghiệm thu

1. **TEMPLATE_VERIFICATION_PENDING:** chưa có quy định chính thức của trường. File dùng định dạng học thuật chuyên nghiệp; chưa chứng nhận tuân thủ font/margin/page size riêng của trường. Gate này cần giải quyết trước Final Submission Lock; không ngăn Commander review nội dung hợp nhất.
2. Hai CSV lớn Oracle `borrower_level_evidence.csv` và Integration `eligible_vs_executed_audit.csv` chưa được Work đọc đầy đủ. Các kết luận dựa trên registry/summary/báo cáo khóa và selectors; không tuyên bố đọc cell-by-cell hoặc rerun. `WORK_INDEPENDENT_STATIC_RECONSTRUCTION`, `CODEX_REPLAY_VERIFICATION`, `CODEX_PREMERGE_AUDIT` là các phạm vi khác nhau.
3. Access level P2, nguồn chưa kiểm chứng, hạn chế lịch sử/Terra/network, khác biệt metadata Frozen đã công bố vẫn tồn tại đúng phạm vi; không che chúng bằng nhãn PASS chung.
4. Bìa chưa có danh tính tác giả/hướng dẫn/đơn vị do nguồn cung cấp không xác minh metadata hành chính; dùng bìa đề tài hoàn chỉnh, không bịa hoặc đặt ô trống giả nội dung.

**Không phát hiện blocking scientific conflict mới sau biên tập.** Đề nghị Commander review DOCX/MD và hồ sơ này; chỉ Commander quyết định nghiệm thu, merge và Final Submission Lock sau khi xử lý gate hình thức. Không tự cấp khóa.
