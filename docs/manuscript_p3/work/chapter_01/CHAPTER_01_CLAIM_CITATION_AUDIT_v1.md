# CHAPTER_01_CLAIM_CITATION_AUDIT_v1

**Manuscript status:** `CHAPTER_01_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW` — đề nghị review, chưa chapter lock.

## 1. Authority và source precedence

- Scientific Content Lock: `3f6e5302483681209e2408531eb5a15389f9fded`; registry `final-accepted-claims-v1.1-targeted-repair`.
- Approved Blueprint integration/lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- [Commander Blueprint Lock](https://github.com/Doquocdung1609/DeFiStress/issues/3#issuecomment-6208624665) xác nhận cấu trúc/claim allocation/exhibit plan. Comment này lúc phát hành chỉ cấp evidence preparation. **Lệnh trực tiếp mới nhất của người dùng trong phiên hiện tại** cấp `CHAPTER_01_FULL_DRAFT_AUTHORIZED`, cho phép viết toàn văn và tạo T1.1 Markdown, thay checkpoint Evidence Pack riêng. Không sửa lịch sử hoặc diễn giải comment cũ như đã cho phép full draft.
- Truy xuất 18 required repository files tại hai pin và thêm bốn support files Frozen/Oracle/Addendum qua GitHub connector, đọc các phần liên quan đến Chương1; không dùng default branch làm scientific source. Đọc lại phần mở đầu/chương giới thiệu của hai DOCX cung cấp để đối chiếu; không dùng chúng làm khoa học ưu tiên.
- Output commit được ghi tại PR/handoff sau push, không tự chèn SHA của chính file.

## 2. Ánh xạ tiểu mục và chức năng bằng chứng

| Vị trí | Accepted IDs thực sự dùng | Source IDs | Vai trò bằng chứng | Giới hạn tại vị trí |
|---|---|---|---|---|
| 1.1.1 | P2:C01, P2:C03, P2:C07 | S01, S02, S03, S07, S09, S29 | Composability; HF và động cơ; thanh khoản theo khoảng; chưa triển khai một kết luận cascade. | C01 chỉ khái niệm; HF khác execution; S07 là white paper; tài liệu Aave hiện hành chưa xác nhận cấu hình lịch sử. |
| 1.1.2 | P2:C03, P2:C09, P2:C10, P2:C32 | S10, S11 | Oracle Diagnostic và Addendum: hai kênh DEX/HF, portfolio/route/positive-debt event. | A/B/C phản thực; chưa historical Aave/Chainlink; không causal Mainnet; không báo số Wave2. |
| 1.2.1 | P2:C03, P2:C09, P2:C10, P2:C11, P2:C12, P2:C13, P2:C19, P2:C31 | S09, S10, S11, S12, S13, S14, S19, S20, S21, S22 | Đối thoại empirical impact, incentives, ABM/ODD, thực hành ngành; không lấy nguồn nền chứng nhận mã. | S13 khác frequency/benchmark với modeled Wave2; S14 không hiệu chỉnh WETH/USDC; S22 không peer review; abstract không fulltext. |
| 1.2.2 | P2:C03, P2:C11, P2:C31, P2:C32 | S09, S10, S11, S12, S13, S19, S20, S21, S22 | Khoảng trống tích hợp/truy vết; Frozen results/manifest và registry là chứng cứ thực hiện. | Không first-ever/systematic search claim; traceability không chứng nhận external validity. |
| 1.3.1 | P2:C31, P2:C32, P2:C35 | — | Sáu mục tiêu theo RQ; mô tả thiết kế, chưa trả lời định lượng. | USDC định giá nợ; modeled bad debt khác realized loss; không dự báo thị trường. |
| 1.3.2 / T1.1 | P2:C31 | — | Sáu câu hỏi và required limitations từ six_rq matrix; Blueprint và exhibit plan chỉ định T1.1. | Nguyên văn RQ; evidence types là thiết kế nghiên cứu; không kết luận số học hoặc quan sát mới. |
| 1.4.1 | P2:C03, P2:C17, P2:C19, P2:C26, P2:C32, P2:C35, INT:CL_INT_TERRA_NEGATIVE_PRESERVED | — | Frozen scope results; registry implementation/limitations; Terra derived validation chỉ ở mức giới hạn. | 454 khác109; một block/pool; representative agents; không fork/funded execution; không successful Terra OOS; network chỉ cấu trúc. |
| 1.4.2 | P2:C31, P2:C17, INT:CL_INT_TERRA_NEGATIVE_PRESERVED | S21 | Đóng góp về phương pháp/phân tích/bằng chứng, dựa trên nguồn dự án; ODD chỉ là nền. | Không superiority/first-ever/production-ready hoặc đã kiểm định quản trị rủi ro thực tế. |
| 1.5.1 | P2:C31 | — | Thứ tự bảy chương và chức năng lập luận theo Blueprint. | Không viết kết quả/chương sau; không tự đổi chapter allocation. |

S05 được dùng riêng trong 1.1.1 để phân biệt source-price API với spot DEX (C32). Không có phương trình hiển thị; T1.1 là exhibit duy nhất. Các chi tiết kết quả của Ch5/6 chỉ được dùng để xác định ranh giới, chưa báo cáo các counts/bounds trong Ch1.

## 3. Accepted records và allocation được bảo toàn

Các references ở Ch1 là định vị/khái niệm/phạm vi, không chuyển primary destination. Blueprint phần Ch1 và lệnh mới nhất chỉ định các chapter-use references; JSON allocation gốc vẫn bất biến. Một số candidate đã được Blueprint cho dùng ở Ch1 nhưng JSON không liệt kê Ch1 trong secondary destinations. Bảng dưới ghi nguyên văn destinations đã duyệt, không âm thầm thêm Ch1. C07/S07 chỉ giải thích nền thanh khoản theo yêu cầu §1.1.1; C26 và Terra chỉ công bố scope/limits theo §1.4.1 và chỉ thị mục X. Không đưa kết luận định lượng của chúng vào Ch1; các phát triển đầy đủ vẫn ở primary chapter đã khóa. Commander có thể rà soát cách ghi cross-reference này khi review, không cần sửa scientific registry.

| Registry ID | Final gate | Primary | Secondary theo JSON gốc | Evidence tier | Công dụng tại Ch1 |
|---|---|---:|---|---|---|
| INT:CL_INT_TERRA_NEGATIVE_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | DERIVED_HISTORICAL_VALIDATION_RESULT | Giới hạn derived historical validation; không forecast-success finding |
| P2:C01 | ACCEPTED | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C03 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C07 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C09 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | MIXED_SCHOLARLY_ONCHAIN_AND_MODEL_CROSSWALK | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C10 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | MIXED_SCHOLARLY_ONCHAIN_AND_MODEL_CROSSWALK | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C11 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C12 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C13 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C17 | ACCEPTED_WITH_LIMITATIONS | 7 | 1, 6 | SCHOLARLY_SOURCE | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C19 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C26 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | CODE_OBSERVATION | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C31 | ACCEPTED_WITH_LIMITATIONS | 1 | 2, 7 | SCHOLARLY_SOURCE | Luận điểm tích hợp/truy vết; primary Ch1 |
| P2:C32 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION_AND_MODEL_COMPUTED_COUNTERFACTUAL | Bối cảnh/phạm vi/phương pháp, không numerical finding |
| P2:C35 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION_WITH_SCOPED_MODEL_LIMITATION | Bối cảnh/phạm vi/phương pháp, không numerical finding |

Tổng: **15 accepted records** (14 P2 + 1 Integration limitation record); không tạo claim ID mới. Claim khái niệm không bị yêu cầu có numerical result.

## 4. Citation identity, access và phạm vi

Không truy hồi lại bài gốc hoặc resolver trong vòng này; mức access kế thừa nguyên nhãn P2 ngày 13/10/2026. Đọc P2/registry không nâng mức đọc bài gốc. `VERIFIED_CONTENT` giữ đúng nhãn nguồn, không tự đổi thành `VERIFIED_FULLTEXT`.

| S ID | Author–year dùng trong chương | Source access nguyên nhãn | Citation scope |
|---|---|---|---|
| S01 | Schär (2021) | VERIFIED_CONTENT: trang tác giả/nhà xuất bản đọc được | 1.1.1: tính kết hợp dịch vụ; không đo cascade. |
| S02 | Aave (n.d.-a) | VERIFIED_CONTENT: nội dung hiện hành; không xác nhận cấu hình lịch sử | 1.1.1: cho vay/thanh lý nói chung; không lịch sử bytecode. |
| S03 | Aave (n.d.-b) | VERIFIED_CONTENT: HF và nhánh close factor trên trang trợ giúp | 1.1.1: HF<1 và quá trình thanh lý; không mọi eligible đã thực thi. |
| S05 | Aave (n.d.-c) | VERIFIED_CONTENT: API nguồn giá, không xác nhận feed tại block nghiên cứu | 1.1.1: nguồn giá là mắt xích riêng; không xác minh feed tại snapshot. |
| S07 | Adams et al. (2021) | VERIFIED_CONTENT: PDF gốc; không phân loại peer reviewed | 1.1.1: thanh khoản V3 theo khoảng, TVL khác khả năng thực thi; không công thức hoặc số liệu mới. |
| S09 | Qin et al. (2021) | VERIFIED_ABSTRACT: bản tác giả arXiv đọc được; DOI/venue khớp UCL; DOI trực tiếp 403 | 1.1.1/1.2.1: incentive/risk và bốn giao thức được khảo sát; không ước lượng/bảng chưa đọc. |
| S10 | Lehar & Parlour (2022) | VERIFIED_ABSTRACT: trang BIS đọc được; chưa kiểm từng bảng/ước lượng; không gán DOI | 1.1.2/1.2.1: collateral sale/price impact như cơ sở câu hỏi; không causal Mainnet của DeFiStress. |
| S11 | Sasi-Brodesky & Kaousar Nassr (2023) | VERIFIED_CONTENT: PDF và trang OECD; DOI khớp nhà xuất bản; resolver trực tiếp không truy cập được | 1.1.2/1.2.1: liquidation/volatility/liquidity và giới hạn nhận diện hành vi. |
| S12 | Tian & Zhu (2025) | VERIFIED_ABSTRACT: nguồn phát hành; không suy diễn Aave dùng đấu giá | 1.2.1: trade-off fixed-spread/auction phụ thuộc participation; không ưu việt phổ quát hoặc Aave đấu giá. |
| S13 | Chiu & Danisman (2026) | VERIFIED_CONTENT: PDF gốc và DOI nhà phát hành; resolver trực tiếp không truy cập được | 1.2.1: không tìm tác động giá kéo dài có ý nghĩa theo thiết kế benchmark; không bị model Wave2 bác bỏ. |
| S14 | Lyons & Viswanath-Natraj (2023) | VERIFIED_ABSTRACT: bản công bố và kho tác giả khớp; không suy rộng hệ số Tether sang USDC | 1.2.1: arbitrage/tiếp cận trong stablecoin, chủ yếu Tether; không chuyển hệ số sang WETH/USDC. |
| S19 | Bookstaber (2017) | VERIFIED_ABSTRACT: trang nhà xuất bản; chưa đọc phần paywall | 1.2.1: nền phương pháp ABM tài chính ở mức abstract; không calibration/validation engine. |
| S20 | Axtell & Farmer (2025) | VERIFIED_ABSTRACT: AEA và kho tác giả Oxford; không xác nhận engine DeFiStress | 1.2.1: nền phương pháp ABM ở mức abstract; không kiểm định các agents DeFiStress. |
| S21 | Grimm et al. (2020) | VERIFIED_CONTENT: toàn văn mở; DOI chuyển đúng tới bài | 1.2.1/1.4.2: mục đích, trạng thái, trình tự, mô hình con và liên hệ code; không chứng nhận dự án tuân thủ đầy đủ ODD. |
| S22 | Gauntlet (2021) | VERIFIED_CONTENT: bài wfu đăng thay mặt Gauntlet; không phải peer review hoặc đặc tả tái lập đầy đủ | 1.2.1: bài forum thực hành ngành ABM/MC; không peer review, không tái tạo phương pháp Gauntlet. |
| S29 | Financial Stability Board (2023) | VERIFIED_CONTENT: trang phát hành; không gán toàn bộ hệ thống DeFi cho mạng hai giao thức | 1.1.1: liên kết/đòn bẩy/thanh khoản ở mức bối cảnh, không full-market đo từ hai giao thức. |

16 references cuối chương lấy nguyên mục APA tương ứng về tác giả, năm, tiêu đề, DOI/URL. Họ ghép **Kaousar Nassr** được giữ; Aave dùng n.d.-a/b/c; S07 là white paper; S22 là forum thực hành ngành. Không thêm page number để giả đọc nguồn abstract. Không thêm DOI hoặc URL mới. S17/S18 không được dùng làm hai bằng chứng độc lập; U01–U08 không được đưa vào references. Chương không viện dẫn Wilson hoặc trình bày CI.

Author–year là working convention, **TEMPLATE_VERIFICATION_PENDING**. Chưa tuyên bố APA là quy định chính thức của PTIT. References trong chương là subset để review citation coverage, chưa là bibliography final của bảy chương.

## 5. Project evidence và locators

Tất cả đường dẫn khoa học dưới đây được đọc tại Scientific Lock; phiên bản lịch sử embedded trong manifest vẫn được giữ. Literature là nền cho cơ chế; các artifact dưới đây mới hỗ trợ mô tả phần triển khai và phạm vi của dự án.

| Vị trí trong chương | Exact locator/selector | Evidence/result IDs | Chức năng |
|---|---|---|---|
| Toàn chương | [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json); `records[registry_id] theo bảng mục3` | NOT_APPLICABLE cho khái niệm hoặc scope; registry IDs nêu riêng | 44 affirmative/4excluded và allowed inference, tiers, limitations. |
| 1.3.2/T1.1 | [data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json); `research_questions[0:6].full_original_research_question; rq; required_limitations` | NOT_APPLICABLE cho khái niệm hoặc scope; registry IDs nêu riêng | Sáu RQ nguyên văn và biên câu trả lời; không lấy recommended conclusion làm nội dung cột số. |
| 1.4.1 | [data/processed/research_final/frozen_v3/results_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/results_registry.json); `AAVE_SNAPSHOT_BLOCK=26045352; AAVE_VERIFIED_BORROWERS=454; AAVE_WETH_USDC_COHORT=109` | Các result IDs ghi ở selector | Chỉ số quy mô dữ liệu, đơn vị block/borrowers/positions; cohort109 có WETH enabled + USDC debt>0 trong tập454. |
| 1.2.2/1.4.2 | [data/processed/research_final/frozen_v3/manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/manifest.json); `provenance/source hashes and scope` | NOT_APPLICABLE cho khái niệm hoặc scope; registry IDs nêu riêng | Hỗ trợ provenance; không đồng nghĩa Work rerun. |
| 1.1.2 | [docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md); `Policy definitions/selection/scope` | NOT_APPLICABLE cho khái niệm hoặc scope; registry IDs nêu riêng | A/B/C phản thực; chưa actual historical Aave feed. |
| 1.1.2 | [docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md); `Eligible vs Executed; skip reason/scope` | NOT_APPLICABLE cho khái niệm hoặc scope; registry IDs nêu riêng | Phân biệt portfolio HF và route execution; không báo 35/14 trong intro. |
| 1.2.1/1.4.1 | [docs/research_final/FINAL_ACCEPTED_CLAIMS_REGISTRY_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/FINAL_ACCEPTED_CLAIMS_REGISTRY_v1.md); `C19/C32/C35; scientific limitations; Terra/network` | NOT_APPLICABLE cho khái niệm hoặc scope; registry IDs nêu riêng | Mô tả project facts và giới hạn, không dùng scholarly paper chứng nhận code. |
| Audit nguồn | [data/processed/research_final/final_accepted_claims_v1/claim_evidence_crosswalk.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/claim_evidence_crosswalk.json); `rows[registry_id]` | NOT_APPLICABLE cho khái niệm hoặc scope; registry IDs nêu riêng | Đối chiếu allowed inference/result/source/limitations. |
| Audit provenance | [data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json); `sources; locked_p2_blob_ids; hash_semantics` | NOT_APPLICABLE cho khái niệm hoặc scope; registry IDs nêu riêng | Pin source objects và phân biệt hash domains. |

Terra chỉ dẫn **CL_INT_TERRA_NEGATIVE_PRESERVED**, tier `DERIVED_HISTORICAL_VALIDATION_RESULT`; không gọi kết luận cutoff-safe là raw observation. Hai result IDs `TERRA_PRE_DEPEG_HIGH_ALERT_HOURS` và `TERRA_INITIAL_DEPEG_HIGH_LEAD` xác định nền cho giới hạn; không đưa giá trị số vào Ch1. Network C26 là `CODE_OBSERVATION`; không mượn C29 time-series CV làm topology evidence.

## 6. T1.1 provenance và technical acceptance

**Request ID:** `P3-CH01-T11-TEXT-v1`; liên kết approved exhibit `T1.1` / historical handoff `P3X-T1.1`, không đổi scientific registry IDs.

Work được lệnh trực tiếp cho phép tạo bảng Markdown, không mở một vòng Codex chỉ để dựng bảng văn bản. Bảng có đúng sáu hàng RQ1–RQ6 và năm cột: RQ, nguyên văn câu hỏi, cơ chế/biến, loại bằng chứng/thiết kế, giới hạn. Cột2 lấy chuỗi exact `full_original_research_question`; các cột còn lại là synthesis từ required limitations/research design trong ma trận và Blueprint. Đây là **textual synthesis**, không có quan sát, statistics hay kết quả simulation mới.

Không có đơn vị số chung cho bảng. HF là tỷ số, depth theo vòng, giá/giá trị nợ phải theo đúng đơn vị khi các chương sau báo cáo; T1.1 chỉ định vai trò đo lường, không in giá trị. Caption chứa hai permalink tại đúng scientific/blueprint pins và statement về bảng thiết kế, không là bảng Mainnet findings. RQ5 giữ `debt/settlement asset` nguyên văn nhưng cột giới hạn nêu rõ phần thực hiện chỉ debt valuation.

Nếu Codex review hoặc chuyển định dạng ở bước sau: kiểm exact 6 chuỗi, thứ tự hàng/cột, units/denominator semantics, full limitation/caption links và không tự bổ sung câu trả lời số học. Output tiếp theo chỉ khi được giao: Markdown/CSV UTF-8 + provenance sidecar trong Codex-owned chapter_01, không chỉnh prose Work và không cần mô phỏng. Trong lượt này không có numerical rendering request hoặc audit lại toàn P2/G0.

## 7. Disallowed safeguard và giới hạn

| Audit record | Disposition trong Ch1 |
|---|---|
| CL_FROZEN_RQ1_UNQUALIFIED_WORDING | Không dùng affirmative; cascade luôn được đặt theo cấu hình/policy. |
| CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING | Không dùng affirmative; DEX price impact khác transmission sang HF. |
| CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT | Không dùng affirmative; source API khác xác minh feed lịch sử. |
| CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION | Không dùng affirmative; historical linkage khác nhận diện nhân quả. |

Giới hạn được đặt tại nơi cần: policy và route ở1.1.2; S13/causal identification ở1.2.1; conditional MC tại1.2.1 vàT1.1; valuation-only tại1.3/1.4; scope454/109, one pool, agents/no recycle/no split, repositioning, Terra/network ở1.4.1; external/practical use ở1.4.2. Modeled debt không là realized loss. Không báo severe frequency hoặc eligible/executed counts trong Ch1.

Hai raw CSV lớn của audit borrower tiếp tục chưa được Work đọc đầy đủ/cell-by-cell; đọc registry/summary/report không xóa hạn chế này. Không đổi nhãn source access, S17/S18 hoặc U01–U08. Hash file DOCX là SHA256 của binary thực; hash Git blob dùng bytes Git/LF theo nguồn; không gọi hash Windows CRLF và Git LF khác nhau là cùng SHA.

## 8. Kế thừa và thay thế legacy

| Existing material | Dùng ở bản mới | Quyết định |
|---|---|---|
| Main DOCX Lời mở đầu/Ch1: composability, collateral–liquidity link | 1.1, viết lại có citations và định giá là cổng riêng | REVISE/RELOCATE; không chép overclaim feedback tự động. |
| Main DOCX mục tiêu/phạm vi; proposal §1–3 và§7–8 | 1.2–1.4: thiết kế có thể truy vết, phân biệt evidence tiers | RETAIN ý phù hợp; thay product/fork/calibration claims chưa được hỗ trợ. |
| Main DOCX câu hỏi đã dịch diễn đạt lại | T1.1 | REPLACE bằng sáu chuỗi nguyên văn từ locked matrix. |
| Main DOCX bố cục năm chương | 1.5 | REPLACE theo Blueprint bảy chương đã khóa. |
| Zero Wave2 chung, Severe0/200; arbitrage không phản ứng | Không tái dùng trong Ch1 | SUPERSEDED: kết quả chi tiết chỉ ở chương sau theo lock. |
| Proposal: full price paths, competition calibrated, fork validation, Monte Carlo như market probability | Không đưa vào manuscript mới | REMOVE_AS_UNSUPPORTED; dùng scope thực tế, không đổi dữ liệu. |
| Proposal U04–U07 và lời hứa stablecoin full settlement | Không cite hoặc dùng làm kết luận | SOURCE_NOT_VERIFIED/ngoài scope; không bổ sung nguồn mới. |

Hai DOCX chỉ được đọc để kiểm nội dung kế thừa; không chỉnh file đính kèm, không render/visual QA hoặc xuất Word ở vòng này.
