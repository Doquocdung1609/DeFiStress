# CHAPTER_06_RESULT_CLAIM_CITATION_AUDIT_v1

**Status: `CHAPTER_06_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`.** Đây là hồ sơ truy vết của toàn văn, không phải một bộ claims mới hoặc lượt tái chạy nghiên cứu. `WORK_PINNED_SOURCE_REVIEW_AND_STATIC_CONTENT_CHECK`; self-review không phải external independent peer review.

- Scientific Lock: `3f6e5302483681209e2408531eb5a15389f9fded`; registry `final-accepted-claims-v1.1-targeted-repair`.
- Blueprint Lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Starting integration / Ch01–05: `bd93a39f773eacfab182a750c08c0d9fc30914cf`.
- Branch: `research/p3-ch06-full-manuscript-work`; final SHA được báo ngoài commit tại PR handoff.
- Chỉ ba file Work/chapter_06; không thay scientific source, allocation hoặc Codex paths.

## 1. Coverage và chức năng của claims

Bảo toàn 48 records/44 affirmative/4 disallowed. Chương dùng 13 accepted components: tám primary destinations, một secondary destination và bốn context anchors được chính Blueprint/exhibit crosswalk nêu. Các labels primary/secondary dưới đây là nguyên allocation, không thêm secondary_chapter=6 vào nguồn. C09/C10/C25 là anchors nền được phần Chương6 của Blueprint chỉ rõ; C33 là reference phân loại của T6.2 được crosswalk duyệt. Chúng có chức năng dẫn chiếu khái niệm/kết quả chương trước, không tái phân bổ primary claim sang Chương6. C17 đã có secondary6.

| Registry ID | Final gate | Primary chapter | Secondary chapters theo matrix | Use in Ch06 | Primary evidence tier |
| --- | --- | --- | --- | --- | --- |
| P2:C09 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | 6.1.2–3;T6.1 | MIXED_SCHOLARLY_ONCHAIN_AND_MODEL_CROSSWALK |
| P2:C10 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | 6.1.3;T6.1 | MIXED_SCHOLARLY_ONCHAIN_AND_MODEL_CROSSWALK |
| P2:C16 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 6.2.1 | SCHOLARLY_SOURCE |
| P2:C17 | ACCEPTED_WITH_LIMITATIONS | 7 | 1, 6 | 6.2.1;6.4;T6.2 | SCHOLARLY_SOURCE |
| P2:C25 | ACCEPTED | 2 | 3, 4, 5, 7 | 6.3.2;F6.2 | SCHOLARLY_SOURCE |
| P2:C26 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 6.3.2;F6.2 | CODE_OBSERVATION |
| P2:C27 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 6.3.3;F6.2 | SCHOLARLY_SOURCE |
| P2:C28 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 6.3.3;F6.2 | SCHOLARLY_SOURCE |
| P2:C29 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 6.2.2 | SCHOLARLY_SOURCE |
| P2:C30 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 6.2.3;6.4;F6.1;T6.2 | DERIVED_HISTORICAL_VALIDATION_RESULT |
| P2:C33 | ACCEPTED_WITH_LIMITATIONS | 4 | 3, 5, 7 | 6.4.1;T6.2 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| INT:CL_INT_HISTORICAL_TIERS_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 6.1;6.4;T6.1 | ONCHAIN_HISTORICAL_OBSERVATION |
| INT:CL_INT_TERRA_NEGATIVE_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 6.2;F6.1 | DERIVED_HISTORICAL_VALIDATION_RESULT |


8/8 primary: `P2:C16`, `P2:C26`, `P2:C27`, `P2:C28`, `P2:C29`, `P2:C30`, `INT:CL_INT_HISTORICAL_TIERS_PRESERVED`, `INT:CL_INT_TERRA_NEGATIVE_PRESERVED`. Không tạo RQ mới hoặc đổi original RQ. Nguồn: [docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json); [docs/manuscript_p3/work/P3_MANUSCRIPT_BLUEPRINT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_MANUSCRIPT_BLUEPRINT_v1.md).

| Claim | Accepted scope used | Required limitations from registry |
| --- | --- | --- |
| P2:C09 | Literature hỗ trợ bán thế chấp; lịch sử ghi receipt route và association | Một WETH route được kiểm receipt; không chứng minh price causality/cascade |
| P2:C10 | Liquidation/volatility relation khác xác nhận nhân quả | Cùng shock/market movement không là simulated endogenous wave |
| P2:C16 | Terra run liên quan khuyến khích/quan sát/tập trung | Không gán chỉ một thủ phạm hoặc thêm tỷ lệ không kiểm |
| P2:C17 | Terra không xác nhận trực tiếp tham số Aave | Kết luận giới hạn của nghiên cứu, không trích như phát hiện định lượng JFE |
| P2:C25 | Multilayer cần nêu node–layer và kiểu coupling | Nhãn lớp/nhiều cạnh chưa đủ chứng minh supra adjacency |
| P2:C26 | Các chỉ số trung tâm của dự án được tính trên đồ thị dị thể đã gộp. | Gộp max; structural metric chưa risk-weighted |
| P2:C27 | Betweenness biểu thị vị trí trên shortest paths | Directed/unweighted variant phải công bố; không universal importance |
| P2:C28 | DebtRank là chỉ số distress khác centrality cấu trúc | Dự án chưa implement DebtRank; không đổi tên điểm normalized |
| P2:C29 | Bergmeir nêu CV autoregression với điều kiện cụ thể | Không dẫn như lệnh cấm K-fold chung hoặc bằng chứng no-leakage |
| P2:C30 | Đánh giá cảnh báo cutoff-safe của Terra ghi nhận kết quả âm trước lần lệch neo ban đầu; kết quả kiểm chứng hồi cứu này không hỗ trợ kết luận dự báo ngoài mẫu thành công. | Source paper không chứng nhận retrospective forecast |
| P2:C33 | Kiểm toán HF trong mô hình theo Policy A ghi nhận các vị thế mới mất an toàn sau Wave 1; việc mới đủ điều kiện theo HF được đối chiếu riêng với các lần thanh lý vòng hai có hoàn trả nợ dương. | Chỉ simulated endogenous eligibility; không phải cascade lịch sử; Independent static reconstruction of 32688 direct/post HF pairs matched all 72 summary counts and 52 available Wave2 event HF values; all 36 raw NOT_ELIGIBLE skips resolved to NO_MODELLED_USDC_DEBT. Oversized raw CSV cells remain unread, so no exact cell-by-cell source-file comparison claimed. |
| INT:CL_INT_HISTORICAL_TIERS_PRESERVED | Cửa sổ lịch sử ghi nhận 28 Pool events, 27 Graph-matched và các tầng liên hệ 1/2/23/1. | Co-occurrence/receipt route does not prove price causality or endogenous cascade. |
| INT:CL_INT_TERRA_NEGATIVE_PRESERVED | Đánh giá cảnh báo cutoff-safe của Terra không hỗ trợ kết luận dự báo ngoài mẫu thành công. | No successful out-of-sample forecasting claim. |


## 2. Scholarly citations và mức truy cập

Danh mục chín mục APA trong main sao đúng P2. Không tải lại hoặc tuyên đọc toàn văn các paper ở lượt viết này; mức access là mức P2 đã khóa, không nâng cấp. Source papers chỉ hỗ trợ khái niệm/thiết kế và đối thoại học thuật, không chứng nhận code, cutoff hoặc kết quả dự án. S17/S18 là một study/hai phiên bản; U01–U08 không được sử dụng mới.

| Source ID | APA identity | Citation scope | Locked access label |
| --- | --- | --- | --- |
| S10 | Lehar, A., & Parlour, C. A. (2022). *Systemic fragility in decentralised markets* (BIS Working Papers No. 1062). Bank for International Settlements. https://www.bis.org/publications/working-paper-1062-systemic-fragility-decentralised-markets | 6.1.3: cơ sở nghiên cứu bán tài sản/tác động giá; không thêm hệ số hoặc cỡ mẫu chưa đọc | VERIFIED_ABSTRACT: trang BIS đọc được; chưa kiểm từng bảng/ước lượng; không gán DOI |
| S11 | Sasi-Brodesky, A., & Kaousar Nassr, I. (2023). *DeFi liquidations: Volatility and liquidity* (OECD Working Papers on Finance, Insurance and Private Pensions No. 48). OECD Publishing. https://doi.org/10.1787/0524faaf-en | 6.1.3: quan hệ thanh lý/biến động và giới hạn hành vi suy gián tiếp | VERIFIED_CONTENT: PDF và trang OECD; DOI khớp nhà xuất bản; resolver trực tiếp không truy cập được |
| S17 | Liu, J., Makarov, I., & Schoar, A. (2026). Anatomy of a run: The Terra Luna crash. *Journal of Financial Economics, 184*, Article 104359. https://doi.org/10.1016/j.jfineco.2026.104359 | 6.2.1: khuyến khích/quan sát/tập trung; không một thủ phạm; không numerical calibration Aave | VERIFIED_ABSTRACT: bản ghi nhà xuất bản truy hồi được khi tìm kiếm; lần mở trực tiếp thất bại; không tuyên bố đọc toàn văn JFE |
| S18 | Liu, J., Makarov, I., & Schoar, A. (2023). *Anatomy of a run: The Terra Luna crash* (NBER Working Paper No. 31160). National Bureau of Economic Research. https://doi.org/10.3386/w31160 | 6.2.1: bản tiền nhiệm cùng study S17, không independent replication | VERIFIED_ABSTRACT_INDEXED: bản ghi NBER; cùng nghiên cứu S17, không phải chứng cứ độc lập thứ hai |
| S25 | Kivelä, M., Arenas, A., Barthelemy, M., Gleeson, J. P., Moreno, Y., & Porter, M. A. (2014). Multilayer networks. *Journal of Complex Networks, 2*(3), 203–271. https://doi.org/10.1093/comnet/cnu016 | 6.3.2: node–layer/coupling, phân biệt typed graph với full multilayer | VERIFIED_CONTENT: PDF tác giả đọc được; DOI journal khớp; OUP resolver lỗi |
| S26 | Battiston, S., & Martinez-Jaramillo, S. (2018). Financial networks and stress testing: Challenges and new research avenues for systemic risk analysis and financial stability implications. *Journal of Financial Stability, 35*, 6–16. https://doi.org/10.1016/j.jfs.2018.03.010 | 6.3.3: network/stress-testing motivation ở mức abstract, không chứng nhận risk ranking | VERIFIED_ABSTRACT_INDEXED: search đọc được abstract gốc; mở URL thất bại; không tuyên bố đọc toàn văn |
| S27 | Battiston, S., Puliga, M., Kaushik, R., Tasca, P., & Caldarelli, G. (2012). DebtRank: Too central to fail? Financial networks, the FED and systemic risk. *Scientific Reports, 2*, Article 541. https://doi.org/10.1038/srep00541 | 6.3.3: DebtRank khác structural centrality; dự án chưa triển khai | VERIFIED_CONTENT: trang bài gốc; không khẳng định DeFiStress triển khai DebtRank |
| S28 | Freeman, L. C. (1977). A set of measures of centrality based on betweenness. *Sociometry, 40*(1), 35–41. https://doi.org/10.2307/3033543 | 6.3.3: shortest-path betweenness concept; directed/unweighted variant do project code | VERIFIED_CONTENT/METADATA: đọc abstract paper gốc qua bản sao https://ucilnica.fri.uni-lj.si/pluginfile.php/1147/course/section/1510/Freeman%20-%20A%20set%20of%20measures%20of%20centrality%20based%20on%20betweenness%2C%201977.pdf; không gán directed variant cho bài gốc |
| S30 | Bergmeir, C., Hyndman, R. J., & Koo, B. (2018). A note on the validity of cross-validation for evaluating autoregressive time series prediction. *Computational Statistics & Data Analysis, 120*, 70–83. https://doi.org/10.1016/j.csda.2017.11.003 | 6.2.2: CV autoregression điều kiện riêng, không cấm K-fold chung hoặc chứng minh no-leakage | VERIFIED_ABSTRACT: kho tác giả; chỉ dùng để giới hạn viện dẫn CV, không chứng minh cutoff Terra |


[docs/research_final/LITERATURE_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LITERATURE_VERIFIED.md); [docs/research_final/APA_REFERENCES_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/APA_REFERENCES_VERIFIED.md).

## 3. Result registry join — tám registered results

Đơn vị, sample và locator theo registry; tác giả không gán thêm result ID cho supplemental metric của report/code. Historical totals và tiers có mẫu số khác nhau. Terra là DERIVED_HISTORICAL_VALIDATION_RESULT, không raw observation về năng lực dự báo.

| Result ID | Value | Unit | Population/condition | Source path | Interpretation limit |
| --- | --- | --- | --- | --- | --- |
| HIST_RPC_CENSUS_EVENTS | 28 | LiquidationCall events | Aave V3 Pool, 2026-09-01…07 UTC; independent RPC log census | [data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json) | Một tuần tiền đăng ký; không phải toàn bộ lịch sử Aave. |
| HIST_GRAPH_MATCHED_EVENTS | 27 | events | same week; Graph candidates reverified by RPC | [data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json) | Graph bỏ sót một event trong RPC census. |
| HIST_DIRECT_TRANSFER_PATHS | 1 | events | 27 Graph-matched events; ordered exact-amount WETH transfer path | [data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json) | Bằng chứng tuyến tài sản không tự chứng minh nhân quả thị trường. |
| HIST_SAME_TX_COOCCURRENCE | 2 | events | 27 Graph-matched events; same transaction without verified direct transfer path | [data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json) | Không gọi là direct transfer hoặc causal transmission. |
| HIST_SAME_BLOCK_ASSOCIATION | 23 | events | 27 Graph-matched events; same block | [data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json) | Temporal association only. |
| HIST_TIME_WINDOW_ASSOCIATION | 1 | events | 27 Graph-matched events; nearby in time | [data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json) | Weakest evidence tier; no direct linkage. |
| TERRA_PRE_DEPEG_HIGH_ALERT_HOURS | 0 | hours | 1,630 pre-initial-depeg hours; cutoff-safe indicator | [data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json) | Negative finding; no genuine out-of-sample forecast claim. |
| TERRA_INITIAL_DEPEG_HIGH_LEAD | -45.0 | hours | UST < 0.995 event; cutoff-safe HIGH threshold | [data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json) | Negative means warning after event; design choices were event-informed. |


## 4. Numeric/semantic locator ledger bổ sung

Các hàng này chỉ định vị số đã lưu hoặc thông tin thiết kế; `NO_NEW_RESULT_ID` nghĩa là không tạo một scientific registry ID mới. Không tính lại RMSE/correlation/lead/centrality. V2 RMSE0.417488 là số được làm tròn trong final_report, không tự nhận là exact full-precision JSON. Các dữ liệu 1776/312/168/134 không gộp thành một sample.

| Section | Pinned artifact | Exact selector | Stored value/design | Unit/sample/limit |
| --- | --- | --- | --- | --- |
| 6.1.1 | [data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json) | start_block/end_block; rpc_only[0] | 25878705…25928919; block25888740/log91 | block/log IDs, không denominator ví |
| 6.1.1 | [data/processed/research_final/level3_extension/historical/episode_selection.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/historical/episode_selection.json) | pre_registered_window; sensitivity_cluster_counts; selected_episodes | 01–07/09/2026UTC;24/22/20/19clusters;first5clusters/6events | 27 Graph events, 60/300/900/1800seconds grouping |
| 6.1.2 | [data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json) | route_audits[event_id=event-73afad4e8e3d8a92d2a7] | 3.815682452121213010WETH; logs26/32/33/35/36 | ordered exact-amount receipt path, causal_claim=false |
| 6.1.2 | [data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json) | route_audits[event_id in event-354a52d7f60e59f1d358,event-986a88b46e6bfb565dff] | 2 same-tx events; no ordered exact transfer route | Không dùng legacy DIRECT_TRANSACTION_LINK |
| 6.1.3 | [data/processed/research_final/level3_extension/historical/historical_event_study.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/historical/historical_event_study.csv) | selected_for_deep_review=True; uniswap_swaps_within_5m/control_swaps_within_5m | 154/200;183/196;355/191;337/213;256/203 | window counts, không unique swaps hoặc causal effect |
| 6.1.3 | [data/processed/research_final/level3_p1_targeted_repair/historical/control_window_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/control_window_audit.json) | declared_control_offset_seconds;all_30m_controls_liquidation_free;rows | -3600seconds;True; half_width1/5/15/30min | four declared pools, exact event/control windows |
| 6.2.2 | [data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json) | rows;price_frequency;modes.CUTOFF_SAFE.future_perturbation_audit | 1776rows;5cutoffs;violations0 | March–April daily-carried prices khác independent hourly observations |
| 6.2.2 | [data/processed/research_final/terra/audit/data_quality.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/data_quality.json) | dataset.row_count;dataset.status;quarantined_variables | 312;QUALITY_WARNING; quarantine list | May1–13 dataset, không initial-depeg score sample |
| 6.2.2 | [data/processed/research_final/terra/audit/final_report.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/final_report.md) | sections5–6 | 144calibration/168evaluation V2;12hcalibration/134evaluation V4 | NO_NEW_RESULT_ID; report design summaries |
| 6.2.2 | [data/processed/research_final/terra/audit/conditional_benchmark.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/conditional_benchmark.json) | common_calibration.calibration_start/calibration_end_inclusive/evaluation_start/evaluation_end/evaluation_rows | 2022-05-07T22:00:00Z…2022-05-08T09:00:00Z; evaluation2022-05-08T10:00:00Z…2022-05-13T23:00:00Z;134 | post-trigger replay, not strict OOS |
| 6.2.2 | [data/processed/research_final/terra/audit/rolling_origin.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/rolling_origin.json) | forecast_horizon_hours;method;warning | 6hours;EXPANDING_WINDOW_MOVING_ORIGIN_SIX_HOUR_SHORT_HORIZON_ROBUSTNESS | Không validate whole-collapse trajectory |
| 6.2.3 | [data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json) | modes.CUTOFF_SAFE.lead_times.ust_below_0_995.high | event2022-05-07T22:00:00Z;HIGH2022-05-09T19:00:00Z;threshold60;lead-45 | hours; initialdepeg target |
| 6.2.3 | [data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json) | modes.CUTOFF_SAFE.lead_times.ust_below_0_9.high | lead3.0 | hours before later UST<0.90 event; không initial-depeg forecast success |
| 6.2.3 | [data/processed/research_final/terra/audit/final_report.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/final_report.md) | section5 | UST RMSE0.417488;collapse detected False | V2strictOOS/168eval rows; price RMSE đơn vị USD/UST; số đã làm tròn của report |
| 6.2.3 | [data/processed/research_final/terra/audit/final_metrics.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/final_metrics.json) | aligned_observations;ust_price.correlation;luna_supply.final_relative_error | 134;0.9173549592822899;0.9998790562492551 | conditionalV4; ratio/correlation không demonstratedforecast |
| 6.2.3 | [data/processed/research_final/terra/audit/conditional_benchmark.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/conditional_benchmark.json) | implementation;independently_implemented_models;comparators | All variants share ConditionalABM;False | Không bốn independentmodel families; no new performance test |
| 6.3.1 | [data/processed/research_final/network/structural_graph.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/network/structural_graph.json) | nodes;edges;graph_metadata;mode | 8nodes/9typededges;STRUCTURAL | snapshot topology, không empirical transaction network |
| 6.3.2 | [sim/network/metrics.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/network/metrics.py) | collapse_multigraph;compute_structural_centrality | max normalized strength per directed pair;active_only for weighted influence | directed/unweighted betweenness; no new centrality run |
| 6.3.3 | [data/processed/research_final/network/structural_centrality.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/network/structural_centrality.json) | nodes[protocol:aave-v3,protocol:uniswap-v3,asset:weth].betweenness_centrality;structural_bridge_node | 0.19047619047619047;0.14285714285714285;0.09523809523809523;protocol:aave-v3 | dimensionless within eight-node topology |
| 6.3.3 | [data/processed/research_final/network/structural_centrality.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/network/structural_centrality.json) | nodes.protocol:aave-v3.weighted_influence_strength | 0.0 | structural inactive outgoing route, không no-risk finding |


## 5. Exhibits — bốn approved IDs, không tự tạo exhibit mới

T6.1/T6.2 là Markdown tables hoàn chỉnh trong main; F6.1/F6.2 là `DISPLAY_SPEC_READY_NOT_RENDERED`, chưa là PNG/SVG đã được render/kiểm duyệt kỹ thuật. Quyền sở hữu output vẫn Work prose/Codex numerical rendering khi được giao; lượt này không mở Codex task, không ghi codex/. Output production dự kiến SVG/PDF vector +PNG preview và source-data export, không cần DOCX. Source-mapping status G0 khác production status hiện tại.

### T6.1 — section 6.1; handoff P3X-T6.1

- Academic purpose: Tách coverage/event selection và sức mạnh từng liên hệ.
- Related accepted claims: P2:C09, P2:C10, INT:CL_INT_HISTORICAL_TIERS_PRESERVED.
- Related RQs: RQ1, RQ2, RQ4.
- Codex template(s): P3X:HISTORICAL_EVIDENCE_TIERS.
- Scientific result IDs: HIST_RPC_CENSUS_EVENTS, HIST_GRAPH_MATCHED_EVENTS, HIST_DIRECT_TRANSFER_PATHS, HIST_SAME_TX_COOCCURRENCE, HIST_SAME_BLOCK_ASSOCIATION, HIST_TIME_WINDOW_ASSOCIATION.
- Approved G0 source mapping: `MATCHED`; actual display status: `WORK_MARKDOWN_COMPLETE`.
- Units: LiquidationCall events.
- Denominator: 28Pool events;27Graphmatches; tiercounts1/2/23/1 use27denominator.
- Approved caption controls: Cửa sổ 01–07/09/2026 UTC có 28 Pool events và 27 Graph matches. Trong 27 matches: 1 transfer path, 2 same-transaction, 23 same-block và 1 time-window association; chưa xác lập causal contagion. Điều kiện hiển thị: 28 Pool/27 Graph; tier denominator 27; association does not prove causal contagion.

| Source path | Commit | Selector | Git blob SHA |
| --- | --- | --- | --- |
| [data/processed/research_final/frozen_v3/tables/historical_evidence.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/historical_evidence.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | Locked rows/columns for T6.1; fields/axes: 28Pool/27Graph/1RPC-only; Tier1/2/23/1among27; Selection/window; Allowed evidence strength | ea2d04143baee6a2d561b588bd8174b6dbfbc64b |
| [docs/research_final/LEVEL3_HISTORICAL_EVENT_STUDY.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LEVEL3_HISTORICAL_EVENT_STUDY.md) | 3f6e5302483681209e2408531eb5a15389f9fded | Declared locked artifact for T6.1; Codex must pin extraction selector before rendering; no new statistic. | e56da602592dd53fe52c830a3ca05537179a9b7a |


Fields: phạm vi/tier, original label, event count, denominator, permitted inference. Main table rows Pool28/Graph27/RPConly1 và tier1/2/23/1. Không cộng census rows với tier rows; không gán tier cho RPC-only. Receipt route không là causal arrow.

### F6.1 — section 6.2; handoff P3X-F6.1

- Academic purpose: Đặt negative finding ở vị trí trung tâm thay chọn ngưỡng thuận lợi.
- Related accepted claims: P2:C29, P2:C30, INT:CL_INT_TERRA_NEGATIVE_PRESERVED.
- Related RQs: Extension/context; no new RQ.
- Codex template(s): P3X:TERRA_NEGATIVE_EARLY_WARNING.
- Scientific result IDs: TERRA_PRE_DEPEG_HIGH_ALERT_HOURS, TERRA_INITIAL_DEPEG_HIGH_LEAD.
- Approved G0 source mapping: `CODEX_SPEC_REQUIRED`; actual display status: `DISPLAY_SPEC_READY_NOT_RENDERED`.
- Units: hours, HIGH alert hours; không gộp hai đại lượng.
- Denominator: 1630pre-initial-depeg hours for HIGHcount; Lead−45hours relative toUST<0.995 event; not forecast-success rate.
- Approved caption controls: Terra cutoff-safe là kết quả kiểm chứng suy dẫn: 0 giờ HIGH trong 1.630 giờ trước mất neo ban đầu và lead −45 giờ đối với UST<0,995. Hai đại lượng ở hai panels riêng; không kết luận dự báo ngoài mẫu thành công. Điều kiện hiển thị: Preserve the negative cutoff-safe/OOS conclusion; do not turn later-threshold behavior into forecast success. Use two panels: zero HIGH-alert hours and minus 45 hours lead; distinct labels and denominators, no shared interpretation as forecast success.

| Source path | Commit | Selector | Git blob SHA |
| --- | --- | --- | --- |
| [data/processed/research_final/frozen_v3/tables/terra_limitations.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/terra_limitations.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | Locked rows/columns for F6.1; fields/axes: Panel1 zero HIGH pre-initial-depeg; Panel2 lead−45h relative toUST<0.995event; Cutoff/info boundary annotation | 264d5294bd8da978f8718c15b9ca7bcb221c704b |
| [data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json) | 3f6e5302483681209e2408531eb5a15389f9fded | Declared locked artifact for F6.1; Codex must pin extraction selector before rendering; no new statistic. | c57615dbfe686863b366db648234cf0af1d6b8ca |


Display: two separate panels. PanelA x=preinitialdepeg, y=HIGH alert hours, fixedpoint0, annotation denominator1630hours. PanelB x=HIGH relative to UST<0.995, y=leadhours, fixedpoint-45, zero line và annotation warning after event. Count và lead không dùng chung trục; không lineplot giả từ hai summaries; no interpolated score timeline.

| Panel | Value | Unit | Selector |
| --- | --- | --- | --- |
| A | 0 | HIGH alert hours /1630preinitial hours | modes.CUTOFF_SAFE.pre_initial_depeg_high_alert_hours; pre_initial_depeg_hours |
| B | -45 | lead hours relative to UST<0.995 | modes.CUTOFF_SAFE.lead_times.ust_below_0_995.high.lead_time_hours |


### F6.2 — section 6.3; handoff P3X-F6.2

- Academic purpose: Giải thích topology/centrality chưa phải fullmultilayer contagion.
- Related accepted claims: P2:C25, P2:C26, P2:C27, P2:C28.
- Related RQs: Extension/context; no new RQ.
- Codex template(s): P3X:NETWORK_EXTENSION_BOUNDARY.
- Scientific result IDs: NOT_APPLICABLE: code/structural/classification exhibit; no invented ID.
- Approved G0 source mapping: `CODEX_SPEC_REQUIRED`; actual display status: `DISPLAY_SPEC_READY_NOT_RENDERED`.
- Units: nodes, dimensionless centrality.
- Denominator: 8nodes in project structural graph; not an empirical market-wide denominator.
- Approved caption controls: Mạng con typed/aggregated và chỉ số cấu trúc của DeFiStress chưa là full multilayer contagion hoặc DebtRank đã triển khai. Cạnh định giá là giả định mô hình, không phải quan sát nhân quả lịch sử. Điều kiện hiển thị: No invented edge, DebtRank label, empirical causal styling or all-DeFi ranking; centrality is within-model and dimensionless.

| Source path | Commit | Selector | Git blob SHA |
| --- | --- | --- | --- |
| [data/processed/research_final/network/structural_centrality.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/network/structural_centrality.json) | 3f6e5302483681209e2408531eb5a15389f9fded | Declared locked artifact for F6.2; Codex must pin extraction selector before rendering; no new statistic. | b3608bd848b0594ec86a70fbe28d5b94d2358fa7 |
| [data/processed/research_final/network/structural_graph.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/network/structural_graph.json) | 3f6e5302483681209e2408531eb5a15389f9fded | Declared locked artifact for F6.2; Codex must pin extraction selector before rendering; no new statistic. | 8c980da9a10d1ef52f3b13cf8a14398b0e0cd75d |
| [sim/network/metrics.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/network/metrics.py) | 3f6e5302483681209e2408531eb5a15389f9fded | Implementation definition only; inspect named gates/metrics used by F6.2; not an external protocol-validation claim. | db7aca57029e973637e4969d3a20d5c61e2e330d |


PanelA: 8 nodes/9 typededges, directed. Không dùng force-layout như một metric mới; arrangement theo nhóm loại node không thêm cạnh. Shape/legend theo node.layer; status legend theo evidence_status; inactive edges dashed và ghi potential route. Hai parallel WETH→Aave giữ riêng; line weight chỉ dùng normalized_strength đã lưu với raw-unit legend, không probability/correlation/causal styling. PanelB: tám node trên x/category; y=dimensionless centrality, betweenness và weighted outgoing influence tách series/panel, dùng giá trị gốc dưới đây. Không lấy tọa độ hoặc kích thước node như một output thực nghiệm.

| Node ID | Label | Layer | Evidence status |
| --- | --- | --- | --- |
| protocol:aave-v3 | Aave V3 | PROTOCOL | OBSERVED_ONCHAIN |
| protocol:uniswap-v3 | Uniswap V3 | PROTOCOL | OBSERVED_ONCHAIN |
| asset:weth | WETH | ASSET | OBSERVED_ONCHAIN |
| asset:usdc | USDC | ASSET | OBSERVED_ONCHAIN |
| agent:borrower-cohort | Borrower Cohort | AGENT_ROLE | OBSERVED_ONCHAIN |
| agent:liquidator | Liquidator | AGENT_ROLE | SCENARIO_ASSUMPTION |
| agent:arbitrageur | Arbitrageur | AGENT_ROLE | SCENARIO_ASSUMPTION |
| market:reference | Reference Market | REFERENCE_MARKET | SCENARIO_ASSUMPTION |


| Edge ID | From | To | Relation | Evidence status | Active | Stored normalized strength | Raw unit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| structural:collateral-exposure | asset:weth | protocol:aave-v3 | COLLATERAL_EXPOSURE | OBSERVED_ONCHAIN | True | 0.28461582627300297 | USD |
| structural:revaluation-channel | asset:weth | protocol:aave-v3 | REVALUATION_CHANNEL | DERIVED_METRIC | True | 0.28461582627300297 | USD |
| structural:debt-exposure | asset:usdc | protocol:aave-v3 | DEBT_EXPOSURE | OBSERVED_ONCHAIN | True | 0.2881574593064089 | USD |
| structural:borrower-position-exposure | agent:borrower-cohort | protocol:aave-v3 | BORROWER_POSITION_EXPOSURE | OBSERVED_ONCHAIN | True | 0.908 | borrowers_and_USD |
| structural:liquidation-route | protocol:aave-v3 | protocol:uniswap-v3 | LIQUIDATION_ROUTE | DERIVED_METRIC | False | 0.0 | USD |
| structural:execution-price-channel | protocol:uniswap-v3 | asset:weth | EXECUTION_PRICE_CHANNEL | OBSERVED_ONCHAIN | True | 1.0 | USD |
| structural:liquidator-route | agent:liquidator | protocol:aave-v3 | LIQUIDATION_EXECUTION | SCENARIO_ASSUMPTION | False | 0.0 | USD |
| structural:arbitrage-route | agent:arbitrageur | protocol:uniswap-v3 | ARBITRAGE_STABILIZATION | SCENARIO_ASSUMPTION | False | 0.0 | ratio |
| structural:reference-price-link | market:reference | asset:weth | REFERENCE_PRICE_LINK | SCENARIO_ASSUMPTION | True | 1.0 | USD |


| Node | In degree | Out degree | Betweenness | Eigenvector | Weighted influence |
| --- | --- | --- | --- | --- | --- |
| agent:arbitrageur | 0.0 | 0.14285714285714285 | 0.0 | 7.876455163444983e-13 | 0.0 |
| agent:borrower-cohort | 0.0 | 0.14285714285714285 | 0.0 | 7.876455163444983e-13 | 0.12971428571428573 |
| agent:liquidator | 0.0 | 0.14285714285714285 | 0.0 | 7.876455163444983e-13 | 0.0 |
| asset:usdc | 0.0 | 0.14285714285714285 | 0.0 | 7.876455163444983e-13 | 0.04116535132948699 |
| asset:weth | 0.2857142857142857 | 0.14285714285714285 | 0.09523809523809523 | 0.5773502691880505 | 0.04065940375328614 |
| market:reference | 0.0 | 0.14285714285714285 | 0.0 | 7.876455163444983e-13 | 0.14285714285714285 |
| protocol:aave-v3 | 0.5714285714285714 | 0.14285714285714285 | 0.19047619047619047 | 0.577350269191201 | 0.0 |
| protocol:uniswap-v3 | 0.2857142857142857 | 0.14285714285714285 | 0.14285714285714285 | 0.5773502691896258 | 0.14285714285714285 |


Graph/corrected_v2 graph alias ở ScientificLock có cùng Git blob `8c980da9a10d1ef52f3b13cf8a14398b0e0cd75d`; hai đường dẫn vẫn giữ riêng. Centrality alias cùng blob `b3608bd848b0594ec86a70fbe28d5b94d2358fa7`. Không dùng output ProfessorDemo/Severe cũ thay structural graph. `graph_type=MULTILAYER_DIRECTED_MULTIGRAPH` và version string là nhãn implementation, không chứng minh full multilayer contagion. `frames[0].active_edge_ids` liệt kê structural routes; đọc `edges[].active` khi phân biệt activity, không gọi mọi route ở initial frame là realized flow.

### T6.2 — section 6.4; handoff P3X-T6.2

- Academic purpose: Giúp độc giả hiểu simulated/observed/derived/code khác nhau.
- Related accepted claims: P2:C17, P2:C30, P2:C33, INT:CL_INT_HISTORICAL_TIERS_PRESERVED.
- Related RQs: RQ1, RQ2, RQ3, RQ4, RQ5, RQ6.
- Codex template(s): .
- Scientific result IDs: NOT_APPLICABLE: code/structural/classification exhibit; no invented ID.
- Approved G0 source mapping: `DIRECT_LOCKED_SOURCE`; actual display status: `WORK_MARKDOWN_COMPLETE`.
- Units: không đơn vị.
- Denominator: NOT_APPLICABLE_EVIDENCE_CLASSIFICATION.
- Approved caption controls: Phân biệt code observation, modeled counterfactual, historical observation và derived validation. Một tầng bằng chứng không tự xác minh kết luận ở tầng khác. Điều kiện hiển thị: Hash integrity and code observation must not be elevated to empirical validation.

| Source path | Commit | Selector | Git blob SHA |
| --- | --- | --- | --- |
| [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | records filtered by registry_id in P2:C17,P2:C30,P2:C33,INT:CL_INT_HISTORICAL_TIERS_PRESERVED | bac44e61633b5efdde3665731ea69fbf4ca345e6 |
| [docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md) | 3f6e5302483681209e2408531eb5a15389f9fded | Declared locked artifact for T6.2; Codex must pin extraction selector before rendering; no new statistic. | f3fd437b41d0feabacf01f6708ca65d3a738ef05 |


Fields: evidence/control layer, object, allowed support, inference boundary. Sáu rows của bảng là tổng hợp học thuật từ source contract: onchain state; historical events/receipts; modeled counterfactual; derived historical validation; code/structural metric; integrity control. Không common numeric denominator. C33 chỉ làm context về modeled eligibility/execution theo crosswalk T6.2, không thêm rawrow claims.

## 6. Version precedence và targeted repairs trong lúc viết

| Finding | Location/cause | Repair | Evidence | Recheck |
| --- | --- | --- | --- | --- |
| CH06-R01 | 6.1.1–2: old Level3 narrative says27events and3direct transaction links | Current census28/27; tiers1/2/23/1, preserve old classification as superseded history | Frozen HIST IDs; census/linkage targetedrepair | PASS; no old count used as current |
| CH06-R02 | 6.2.2–3: risk of merging cutoff-safe and strictOOS/conditional datasets | Keep1776hour-score sample separate from312May rows;144/168V2 and12h/134V4 separate | phase5audit;dataquality;finalreport;benchmark | PASS; no pooledsample |
| CH06-R03 | 6.2.3: favourable late UST0.90 lead could hide initial-depeg failure | Keep0/1630 andlead-45 central; laterlead3 stated as later event only | phase5 CUTOFF_SAFE exactselectors | PASS; no forecastsupportedclaim |
| CH06-R04 | 6.3.2–3: graphtypedlabels/centrality may look empirical or riskweighted | Explainmaxaggregation, directed/unweighted betweenness, potentialinactivepaths, weightedactive-only | metrics.py/build.py;structuralgraph/centrality | PASS; no fullmultilayer/DebtRank claim |
| CH06-R05 | Chapter allocation: some Blueprint/exhibit context anchors absent from matrix secondary6 | Retain original primary/secondary matrix and label context authority explicitly; all8primary developed | Blueprint Ch6;crosswalk T6.1/F6.2/T6.2;allocation | PASS for approved chapter-use context; no allocation mutation |
| CH06-R06 | 6.1 event/control counts may be read as unique universe | Keep5episode pairedwindowcounts; no pooleduniquecount or causal effect | eventstudyCSV;controlaudit | PASS |


Historical source precedence: `LEVEL3_HISTORICAL_EVENT_STUDY.md`/original summary retain legacy `DIRECT_TRANSACTION_LINK=3`; targeted repair revises those three into1verified path+2cooccurrences. Census adds1RPConly to28, but tiers remain over27matches. Invalid epoch attempt excluded; correct census28 must not be attributed to that invalid attempt. Do not promote original table wording that calls all same-tx links direct.

Terra source precedence: F6.1 uses Frozen/phase5 cutoff-safe indicators. May2022 V2/V4 report/metrics are separate supplemental design/failure evidence. V4 own trigger convention and timestamps are not forced to equal phase5 threshold times because the datasets differ. Exact field semantics, not filename “final” alone, determine allowed inference. No threshold/cutoff retuning. The historical status strings in old reports are not the current Commander lock state.

Network source precedence: F6.2 uses exact structural graph/centrality at ScientificLock, with corrected-v2 aliases verified equal by blob. Source function definitions establish implementation only. No recalculation, new algorithm name or causal empirical interpretation.

Ch05 RQ6 manuscript interpretation note merged at starting integration is inherited unchanged: LTV255 distinct from109route; LTportfolioUSD atq1. Ch06 refers back without restating/altering numerical results or reissuing lock.

## 7. Boundaries và source-read limitations

L09/L10/L11/L13 của Blueprint được đặt trong main tại6.1/6.2/6.3 và giữ trong hồ sơ: một tuần Pool logs khác borrower census; receipt route khác pricecausality; Terra cutoff-safe/strictOOS negative; graphgộp khác fullmultilayer/DebtRank; S17/S18 cùngstudy; accesslabels không nâng cấp. Snapshot26045352,454verifiedborrowers và109WETH/USDCroute là các phạm vi khác nhau. Không historicalcascade, actualoracleA/B/C, modeleddebt=realizedloss hoặc forecastsupported claim.

Nguồn được đọc qua GitHub connector đúng refs trong ledger bên dưới. Ch01–05 được truy xuất toàn văn đúng integration; phần liên quan phương pháp/validation và boundary được đối chiếu để tránh lặp. Scholar access là P2 kế thừa, không là vòng literature mới. Chương không kế thừa số từ các attachments DOCX/PDF/PPTX; lượt này không mở lại/đọc các attachments đó.

Raw Ethereum receipts/debugtraces không được re-query trong lượt viết. Routeaudit là báo cáo quan sát của đợt kiểm đã khóa, Work đọc route/log selectors và tier rows; không tự nhận một RPC validation độc lập mới. Census cache gzip và raw_swap_index.json.gz chưa được đọc đầy đủ. Control audit và episodeCSV được dùng ở phạm vi window đã ghi, không phải rawswap-universe re-audit.

Raw Terra parquet,277342redemption rows, strict_oos_v2/conditional_abm_final full trajectories và early_warning_timeline rawseries chưa được đọc/đối chiếu toàn bộ ở lượt này. V2 summary dựa trên final_report đã đọc; V4 windows/selected metrics đọc JSON nhỏ. Trạng thái QUALITY_WARNING, quarantined/proxy/unavailable archival fields theo dataquality giữ nguyên; không khẳng định independently re-queried canonical Terra truth. Không chạy report reproduce_command.

Hai oversized borrower CSVs của Oracle/Integration (8.775.089 và18.489.195bytes) vẫn chưa được Work đọc đầy đủ; giới hạn P2/Ch04 không biến thành PASS mới. Không rawHF hoặc event-cell comparison mới trong Ch06. CODEX_REPLAY_VERIFICATION, CODEX_PREMERGE_AUDIT và WORK_INDEPENDENT_STATIC_RECONSTRUCTION trước đây là inherited evidence, không phải actualrun của lượt viết.

Source identity check dùng Git blob SHA1/LF domain. Một LF dư do local text caching chỉ được bỏ khỏi hash comparison khi exactsourceblob khớp; không sửa nội dung source hoặc coi hai bytestring khác nhau cùng SHA. Windows CRLF checkout hash và Git LF blob hash là những miền bytes khác, cần giữ rõ; hash integrity không là economic/causal validation.

TEMPLATE_VERIFICATION_PENDING còn nguyên; APA author–year là working convention. Rendering F6.1/F6.2 chưa làm; không gọi source-mapping match thành technical renderer approval. Không simulation/MC/retune/newstatistics/fullregression/DOCX/Ch07 hoặc tựChapterLock.

## 8. Source ledger — exact read versions

| Path | Read commit | Git blob SHA |
| --- | --- | --- |
| [docs/research_final/LITERATURE_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LITERATURE_VERIFIED.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 6ebe0a11e915e942a422d02a0cc5b1d53b51ff3e |
| [docs/manuscript_p3/work/P3_CHAPTER_ACCEPTANCE_RUBRIC.md](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_CHAPTER_ACCEPTANCE_RUBRIC.md) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 753b40a123677ddda25a178957ed6cc8a55b2c16 |
| [data/processed/research_final/frozen_v3/manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/manifest.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 5fa6f68d25dd4df88b042a7b31be014f8b46dd38 |
| [data/processed/research_final/frozen_v3/results_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/results_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 6dde91fc11d189de8899c742b44fea9cf0f386ae |
| [data/processed/research_final/frozen_v3/evidence_source_matrix.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/evidence_source_matrix.json) | 3f6e5302483681209e2408531eb5a15389f9fded | ece34ff3c883ca17af3b2b55fc046ff0328e790f |
| [docs/research_final/APA_REFERENCES_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/APA_REFERENCES_VERIFIED.md) | 3f6e5302483681209e2408531eb5a15389f9fded | c76d7cf482565615a92fb17b888a392e4f8fd9cc |
| [data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | a6784fd7f1b7288c4f2177ff8ba102be5e01c81e |
| [data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json) | 3f6e5302483681209e2408531eb5a15389f9fded | fffe69d45f2c70e8f4cb781c8b521ef4cf6f1a45 |
| [docs/manuscript_p3/work/chapter_02/CHAPTER_02_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/bd93a39f773eacfab182a750c08c0d9fc30914cf/docs/manuscript_p3/work/chapter_02/CHAPTER_02_FULL_DRAFT_v1.md) | bd93a39f773eacfab182a750c08c0d9fc30914cf | b73f337c99cdf6a137fac4d54e9b49b1aebb3a40 |
| [docs/manuscript_p3/work/chapter_01/CHAPTER_01_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/bd93a39f773eacfab182a750c08c0d9fc30914cf/docs/manuscript_p3/work/chapter_01/CHAPTER_01_FULL_DRAFT_v1.md) | bd93a39f773eacfab182a750c08c0d9fc30914cf | c3fffec83f427c52c595dd02fd73a9c81db5cfcd |
| [docs/manuscript_p3/work/chapter_03/CHAPTER_03_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/bd93a39f773eacfab182a750c08c0d9fc30914cf/docs/manuscript_p3/work/chapter_03/CHAPTER_03_FULL_DRAFT_v1.md) | bd93a39f773eacfab182a750c08c0d9fc30914cf | f8609f120d6f8e1fa9bb3aa9393fe45092888439 |
| [docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json) | 8de52bebabef376be700836e6f93a92d7394d2c3 | e10159ba8659c4dc6b528a7da645d4a20f39a9aa |
| [docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/bd93a39f773eacfab182a750c08c0d9fc30914cf/docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md) | bd93a39f773eacfab182a750c08c0d9fc30914cf | 9be3495921243ad5980177071a7a8cd8370e1ce2 |
| [data/processed/research_final/final_accepted_claims_v1/claim_evidence_crosswalk.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/claim_evidence_crosswalk.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 312b72f23b0115d1de69eec2dc1a87b0f490070a |
| [docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/bd93a39f773eacfab182a750c08c0d9fc30914cf/docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md) | bd93a39f773eacfab182a750c08c0d9fc30914cf | 5fe370a245e11a6ae9a7f2cc6349dc30d97893a2 |
| [docs/manuscript_p3/work/P3_G0_WORK_CODEX_EXHIBIT_CROSSWALK.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_G0_WORK_CODEX_EXHIBIT_CROSSWALK.json) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 27475694e8e94ae4f6dd16bfdb76a956ba080877 |
| [docs/manuscript_p3/work/P3_MANUSCRIPT_BLUEPRINT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_MANUSCRIPT_BLUEPRINT_v1.md) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 10194e95b67a360cadd7ab2eb9550deac206e672 |
| [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | bac44e61633b5efdde3665731ea69fbf4ca345e6 |
| [docs/research_final/P2_CLAIM_EVIDENCE_CROSSWALK.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/P2_CLAIM_EVIDENCE_CROSSWALK.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 932c25f633dee7bdb8cfcf9e6e2473b50f7c4ab3 |
| [docs/research_final/LEVEL3_HISTORICAL_EVENT_STUDY.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LEVEL3_HISTORICAL_EVENT_STUDY.md) | 3f6e5302483681209e2408531eb5a15389f9fded | e56da602592dd53fe52c830a3ca05537179a9b7a |
| [data/processed/research_final/terra/audit/final_report.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/final_report.md) | 3f6e5302483681209e2408531eb5a15389f9fded | c51c4c2dc620dbc140efd6360577fbf62d34fe74 |
| [data/processed/research_final/terra/audit/final_metrics.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/final_metrics.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 662fcad4c302ee95d1b2e9e46a9f4d85fb9a1934 |
| [data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json) | 3f6e5302483681209e2408531eb5a15389f9fded | c57615dbfe686863b366db648234cf0af1d6b8ca |
| [docs/research_final/LEVEL3_P1_TARGETED_REPAIR_REPORT.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LEVEL3_P1_TARGETED_REPAIR_REPORT.md) | 3f6e5302483681209e2408531eb5a15389f9fded | bf3ab3bf6cbd68792dc7b99b33da1be619ea71b9 |
| [data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json) | 3f6e5302483681209e2408531eb5a15389f9fded | b56ac7ecf46026efccd85b2bab2e5da5c836b442 |
| [data/processed/research_final/terra/audit/data_quality.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/data_quality.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 70f157d9eaa957ac80acd1b3e00aa54bb71d2540 |
| [data/processed/research_final/terra/audit/ablation.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/ablation.json) | 3f6e5302483681209e2408531eb5a15389f9fded | ab571fe316d358d818ab0f64209fbb2628308bfb |
| [data/processed/research_final/level3_extension/historical/summary.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/historical/summary.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 0acc57b3bbc7e623aed026703555daefdf8542a5 |
| [data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 008ee07e710933bf4ee10cc049f889b695406654 |
| [sim/network/metrics.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/network/metrics.py) | 3f6e5302483681209e2408531eb5a15389f9fded | db7aca57029e973637e4969d3a20d5c61e2e330d |
| [data/processed/research_final/terra/audit/model_diagnostics.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/model_diagnostics.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 79a973b6f4c81cf9c8f0d09e43cdb4ae7828e094 |
| [data/processed/research_final/terra/audit/rolling_origin.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/rolling_origin.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 49d745eee4ed15c9b4ca1e1e2eae9d4c19dc80a3 |
| [data/processed/research_final/frozen_v3/tables/terra_limitations.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/terra_limitations.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 264d5294bd8da978f8718c15b9ca7bcb221c704b |
| [data/processed/research_final/level3_extension/historical/episode_selection.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/historical/episode_selection.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 226d06b2ab33e3fd56ae5418b88b2df8228f4b3b |
| [data/processed/research_final/level3_extension/historical/historical_event_study.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/historical/historical_event_study.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 73207b7f11773d34f856eb3ed053e3cfa51caf1c |
| [data/processed/research_final/terra/audit/conditional_benchmark.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/conditional_benchmark.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 0779e47571d5a2fc7d671c9f264526f85dc3786d |
| [data/processed/research_final/validation_audit/corrected_run_v2/network/structural_matrix.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/network/structural_matrix.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | e1b4bfd749c7f881d2b23fba3067a3ed9a6b42b9 |
| [sim/network/schemas.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/network/schemas.py) | 3f6e5302483681209e2408531eb5a15389f9fded | 391a13ea47c99f0771746fb844a65a381daefa91 |
| [data/processed/research_final/frozen_v3/tables/historical_evidence.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/historical_evidence.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | ea2d04143baee6a2d561b588bd8174b6dbfbc64b |
| [data/processed/research_final/validation_audit/corrected_run_v2/network/structural_centrality.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/network/structural_centrality.json) | 3f6e5302483681209e2408531eb5a15389f9fded | b3608bd848b0594ec86a70fbe28d5b94d2358fa7 |
| [sim/network/build.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/network/build.py) | 3f6e5302483681209e2408531eb5a15389f9fded | 5ba1e7ccf90f631d29882012e40362658b9960cf |
| [data/processed/research_final/level3_p1_targeted_repair/historical/control_window_audit.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/control_window_audit.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 88093cf756301cb7157f13f1301cf98287dd3044 |
| [data/processed/research_final/terra/audit/reproducibility_manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/reproducibility_manifest.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 531598eb588afbe3abbd4b6163877ce6191d6aa9 |
| [data/processed/research_final/validation_audit/corrected_run_v2/network/structural_graph.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/network/structural_graph.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 8c980da9a10d1ef52f3b13cf8a14398b0e0cd75d |
| [data/processed/research_final/network/structural_centrality.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/network/structural_centrality.json) | 3f6e5302483681209e2408531eb5a15389f9fded | b3608bd848b0594ec86a70fbe28d5b94d2358fa7 |
| [data/processed/research_final/network/structural_graph.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/network/structural_graph.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 8c980da9a10d1ef52f3b13cf8a14398b0e0cd75d |
| [docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md) | 3f6e5302483681209e2408531eb5a15389f9fded | f3fd437b41d0feabacf01f6708ca65d3a738ef05 |


## 9. Four disallowed records safeguard

| Registry ID | Disposition from lock | Manuscript safeguard |
| --- | --- | --- |
| INT:CL_FROZEN_RQ1_UNQUALIFIED_WORDING | REJECTED_AS_WORDED_SUPERSEDED | Audit trail only; không affirmative finding trong main |
| INT:CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING | REJECTED_AS_WORDED_SUPERSEDED | Audit trail only; không affirmative finding trong main |
| INT:CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT | UNSUPPORTED | Audit trail only; không affirmative finding trong main |
| INT:CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION | UNSUPPORTED | Audit trail only; không affirmative finding trong main |


## 10. Six RQ coverage không thay câu hỏi gốc

| RQ | Original question unchanged | Role of Chapter06 |
| --- | --- | --- |
| RQ1 | Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)? | 6.1/6.4.2:historicalclusters khác modeledwaves |
| RQ2 | Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt? | 6.1/6.3/6.4.2:route khác DEX→oraclecausality |
| RQ3 | Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý? | 6.1/6.4.2:observedexecution khác liquidatorresourcecapacity |
| RQ4 | Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi? | 6.1/6.3/6.4.2:swaps/networkroles khác fundedarbitragevalidation |
| RQ5 | Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset? | 6.2/6.4.2:Terra khác USDCdebtvaluation |
| RQ6 | Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk? | 6.4.2:no historical governance optimum/parametertransfer |


## 11. Handoff và actual checks

`python verify_chapter06.py` — PASS/exit0 sau targeted repair, static content/locator/source identity checks; script tạm không phải engine test và không commit thành file thứ tư. Kiểm 4/4 headings,11/11subsections,8/8primary,13acceptedcomponents,8resultIDs,4exhibits,9APAentries, sixoriginalRQ ở audit; đối chiếu main tables, exact selectors của count/lead và structuralgraph/centrality. Không tính lại output nghiên cứu. Các lệnh và giới hạn chi tiết ở self-review.

**Recommendation: `CHAPTER_06_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`.** Không phát hiện scientific blocker trong nguồn được dùng sau áp dụng locked precedence. Remaining production/source limits giữ rõ; Commander quyết định review/merge/ChapterLock. Không tự mở Chương7.
