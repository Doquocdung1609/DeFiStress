# CHAPTER_05_RESULT_CLAIM_CITATION_AUDIT_v1

**Overall recommendation: `CHAPTER_05_TARGETED_REPAIR_REQUIRED`.** Toàn văn đã hoàn chỉnh; static content/source checks có thể PASS nhưng hai sai khác metadata nguồn RQ6 chưa có quyết định hòa giải. Không đồng nhất content PASS với scientific acceptance. Không sửa source, không tạo số mới.

- Scientific Lock: `3f6e5302483681209e2408531eb5a15389f9fded`; registry `final-accepted-claims-v1.1-targeted-repair`.
- Blueprint: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Starting integration / Ch01–04 locked: `30c6ce6859603460c8eb5a496e4f8c36f9339cf0`.
- Branch `research/p3-ch05-full-manuscript-work`; exact final SHA ở Git/PR handoff, không tự nhúng SHA chính commit.
- `WORK_STATIC_RESULT_SOURCE_REVIEW_AND_SELF_REVIEW`; không engine/MC/RPC/fullregression/newstatisticaltest/interval. Không là external independent peer review.
- `TEMPLATE_VERIFICATION_PENDING`; chưa DOCX. Chỉ ba file Work/chapter_05.

## 1. Hai findings nguồn cần sửa/xác nhận có mục tiêu

### CH05-P01 — P1: LTV population metadata không khớp artifact tính toán

- Affected: 5.6.1/F5.6; RQ6; `P2:C04`, `INT:CL_INT_RQ6_PRESERVED`.
- Frozen [data/processed/research_final/frozen_v3/results_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/results_registry.json): `results[result_id=RQ6_LTV0755_CAPACITY].population` và `RQ6_LTV0825_CAPACITY.population` đều ghi `109-position frozen cohort`.
- Detailed [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.json): `cohort_size=255`; `method` giữ othercollateral observedLTV proxy và frozen debt.
- Code [sim/research/rq_completion.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/research/rq_completion.py): `run_ltv_capital_efficiency_analysis`, cohort có `collateral_weth>0 and debt_value()>0`, không filter debtUSDC>0.
- Values 50797988.977634266 và53675575.37423773 USD không đổi. Không thể gán chắc cùng hai values cho cohort109 chỉ từ metadata khi detailed source khai báo255.
- Current manuscript wording: “Artifact chi tiết ... ghi cohort_size=255 ... trường population ... ghi109 ... cần Commander/Codex xác nhận cách đồng bộ”.
- Proposed resolved wording, subject to Commander decision: “Kết quả khả năng vay LTV tổng hợp trên255 vị thế có WETH thế chấp và có nợ, theo artifact tính toán đã khóa; không phải riêng cohort109 tuyếnWETH/USDC.”
- Exact repair criterion: Commander/Codex trace nguồn tạo bảng, xác nhận population thực tế của các totals; đồng bộ hoặc ban hành correction/precedence note cho affected registry metadata và exhibit caption bằng quyết định có version. Không chạy/tính lại mô phỏng; không áp số109 bằng cách tự đổi output. Work không sửa numerical registry.

### CH05-P02 — P1: LT unliquidated-debt label không cùng nghĩa metric code

- Affected:5.6.2/F5.6; RQ6; `P2:C35`, `INT:CL_INT_RQ6_PRESERVED`.
- Frozen [data/processed/research_final/frozen_v3/tables/rq6_policy.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq6_policy.csv): `parameter=LT` rows có `outcome_unit=USDC token quantity, scenario-LT`. Frozen results `RQ6_LT083_UNLIQUIDATED`/`RQ6_LT0855_UNLIQUIDATED` có unit `USDC token quantity` và population `109-position frozen cohort`.
- Code [sim/metrics/risk.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/metrics/risk.py): `unliquidated_debt` cộng `position.debt_value(usdc_price_usd)` trên các vị thế HF<1 của danh sách truyền vào; là tổng giá trị nợ danh mục, bao gồm otherdebt, không chỉ tổng debtUSDC token. `run_liquidation_threshold_sensitivity` gọi engine với danh sách positions, còn `_hf_counts` có cohortfilter riêng.
- Detailed [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json): scenario `usdc_price_usd=1` trong mọi row; values229830.81461902/96839.39478531/88458.67265557 giữ nguyên. Bình đẳng số tại q=1 không chứng minh bình đẳng đơn vị token và portfolioUSD.
- Current manuscript wording: đọc values là giá trị nợ danh mục ở baseline q=1; nêu original label và yêu cầu đồng bộ, không khẳng định toàn bộ là USDCtoken.
- Proposed resolved wording: “Giá trị USD của nợ chưa thanh lý theo scenarioLT tại baseline USDC/USD=1; tách khỏi lượngUSDC đã hoàn trả và xác định population metric từ input positions.”
- Exact repair criterion: Commander/Codex trace metric/denominator tới bảng; xác nhận unit và population phù hợp (portfolio aggregate hay filteredroute), cập nhật/bổ sung metadata correction có version và caption. Không đổi numerical values, không tự filter rồi tính output mới. Nếu thật sự cần một output token-only/cohort109 khác, đó là thay đổi khoa học ngoài nhiệm vụ này và cần quyết định riêng.

CH05-P01/P02 là sai khác metadata có tác động đến phạm vi diễn giải, không phải bằng chứng simulation arithmetic sai. Bản thảo công bố cả hai, F5.6 chưa production-ready; không tự phán chúng là nonblocking để tạo overallPASS. Các phần không phụ thuộc hai nhãn đã được viết đầy đủ.

### CH05-N01 — known label caveat, resolved for manuscript by approved crosswalk

Frozen rq2_liquidity.csv dùng OBSERVED_BASELINE cho haircut25/50/75. Crosswalk F5.3 đã ghi chỉ0% là unmodified canonical, mọi positivehaircut là counterfactual,90/95 là extreme tails. Bản thảo giữ rawlabel trong dataset audit và dùng approvedinterpretation trong caption. Không gọi25–75% là observedhistorical withdrawal; không sửa nguồn.

## 2. Claims thật sự dùng và allocation

23 accepted components (16P2+7Integration), đủ8/8 primary destinations. Coverage không đồng nghĩa mọi source-metadata issue đã được giải quyết. Những claims khái niệm có thể được dùng theo component; không ép numerical result vào conceptual claim.

| Registry ID | Final gate | Primary | Secondary approved | Primary evidence tier | Use |
| --- | --- | --- | --- | --- | --- |
| P2:C03 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.3 — HF/route/evaluation/execution, không thực thi ngoài mô hình |
| P2:C04 | ACCEPTED | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.6 — LTV/LT/bonus ba cơ chế; không governance optimum |
| P2:C05 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE | 5.3; 5.6 — planning gates và cơ chế xử lý; Ch3 giữ đặc tả, không actual deployed-bytecode claim |
| P2:C07 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.2 — thanh khoản tập trung/sức hấp thụ; DEX distortion khác HF transmission |
| P2:C11 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.1.2 — S13 empirical persistent-price null khác model Wave2, không bác bỏ lẫn nhau |
| P2:C12 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.6.3 — participation cost/design context từ S12 abstract; không Aave auction |
| P2:C13 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.4 — immediate vs residual và điều kiện arbitrage; không hiệu chỉnh WETH từ Tether |
| P2:C15 | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.5 — PRIMARY: debt valuation USDC, cohort109 ở direct postshock HF, không full depeg |
| P2:C19 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION | 5.3–5.4 — representative agents, nonsplit/nonrecycled capital, reposition not funded |
| P2:C22 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.1.3; 5.7 — nestedprefix/batch/seed, không price-process hoặc inference ngoài mẫu |
| P2:C23 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.1.3; 5.7.2 — SevereA 280/10000, LowLiq0/1000, lockedWilson |
| P2:C24 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | PROJECT_METRIC_DEFINITION | 5.7.3 — composite tail/repay không loss; p95/ES từ existing batch only |
| P2:C32 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION_AND_MODEL_COMPUTED_COUNTERFACTUAL | 5.1–5.2 — A/B/C hypothetical, không actualoracle |
| P2:C33 | ACCEPTED_WITH_LIMITATIONS | 4 | 3, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | 5.3 — HF transition vs positive event; rawreadlimits giữ nguyên |
| P2:C34 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION | 5.4 — repositioning updatesL chưa funded swap |
| P2:C35 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION_WITH_SCOPED_MODEL_LIMITATION | 5.5; 5.6.2 — units/scopedvaluation, nominal planning/debtmetric distinction |
| INT:CL_INT_RQ1_POLICY_CONDITIONAL | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | MODEL_COMPUTED_COUNTERFACTUAL | 5.1; 5.7 — PRIMARY conditionalcascade, selectedsamples khác batchfrequency |
| INT:CL_INT_RQ2_TWO_CHANNELS | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | MODEL_COMPUTED_COUNTERFACTUAL | 5.2 — PRIMARY absorption và valuation hai kênh |
| INT:CL_INT_ELIGIBLE_NOT_EXECUTED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | MODEL_COMPUTED_COUNTERFACTUAL | 5.3.2–3 — PRIMARY counts35/14/21 etc;36route skips |
| INT:CL_INT_RQ3_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | MODEL_COMPUTED_COUNTERFACTUAL | 5.3.1 — PRIMARY resources/timing và testedrange |
| INT:CL_INT_RQ4_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | MODEL_COMPUTED_COUNTERFACTUAL | 5.4 — PRIMARY residualstabilization, immediateimpact giữ |
| INT:CL_INT_RQ5_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | MODEL_COMPUTED_COUNTERFACTUAL | 5.5 — PRIMARY quantity/USD và debtvaluation only |
| INT:CL_INT_RQ6_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | MODEL_COMPUTED_COUNTERFACTUAL | 5.6 — PRIMARY distinctmechanisms; metadata caveats CH05-P01/P02 pending |

Accepted-wording source: [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json); allocation source [docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json). Mandatory limitations không bị lược khỏi hợp đồng khi main chỉ công bố phần liên quan ở từng mục.

## 3. Citation identity/access và scope

| S ID | Citation | Scope | Access inherited |
| --- | --- | --- | --- |
| S03 | Aave, n.d.-b | HF/debt-side interpretation, không chứng nhận project results | VERIFIED_CONTENT: HF và nhánh close factor trên trang trợ giúp |
| S04 | Aave, n.d.-d | LTV/LT/bonus roles | VERIFIED_CONTENT: định nghĩa LTV/LT; tham số thay đổi theo thị trường/thời điểm |
| S05 | Aave, n.d.-c | Actual source-price architecture khác model policies | VERIFIED_CONTENT: API nguồn giá, không xác nhận feed tại block nghiên cứu |
| S06 | Aave DAO, n.d. | Conditional close factor/dust in reference code; không xác nhận deployed bytecode | VERIFIED_CODE: commit đọc được; không phải xác minh bytecode triển khai tại block |
| S07 | Adams và cộng sự,2021 | Concentrated liquidity mechanism, không verify postshock funded swap | VERIFIED_CONTENT: PDF gốc; không phân loại peer reviewed |
| S09 | Qin và cộng sự,2021 | Abstract về incentives/execution, không số thực nghiệm chưa đọc | VERIFIED_ABSTRACT: bản tác giả arXiv đọc được; DOI/venue khớp UCL; DOI trực tiếp 403 |
| S12 | Tian và Zhu,2025 | Abstract về participationcost/design; không Aave auction hoặc optimalbonus | VERIFIED_ABSTRACT: nguồn phát hành; không suy diễn Aave dùng đấu giá |
| S13 | Chiu và Danisman,2026 | Persistent-price-effect null theo thiết kế bài; không direct refutation bởi modelWave2 | VERIFIED_CONTENT: PDF gốc và DOI nhà phát hành; resolver trực tiếp không truy cập được |
| S14 | Lyons và Viswanath-Natraj,2023 | Abstract arbitrage/access; không hệ sốTether áp WETH | VERIFIED_ABSTRACT: bản công bố và kho tác giả khớp; không suy rộng hệ số Tether sang USDC |
| S15 | Kosse và cộng sự,2023 | Stablecoin convertibility/stability broaderchannels, không DeFiStress full depeg | VERIFIED_ABSTRACT/METADATA: tác giả cá nhân, không phải CPMI là tác giả; không gán DOI |
| S23 | Glasserman,2003 | Preview/metadata MonteCarlo context, không theoremfulltext | VERIFIED_PREVIEW/METADATA: chọn edition 1 hardcover 7/8/2003 theo publisher; chưa đọc các chương paywall |
| S24 | NIST,2014 | Wilson vs adjustedWald terminology; sourceCI là lockedtable, không tính mới | VERIFIED_CONTENT: công thức Wilson được đọc và tính lại; tên trang lịch sử khác tên phương pháp |

12 bibliography entries được sao exact từ APA P2. Không new DOI/URL, không nguồnmới/fulltextupgrade. S17/S18 vẫn hai phiên bản một study; U01–U08 không được dùng mới. Scholarly papers không là bằng chứng implementation hoặc rawproject verification.

## 4. Result registry join và numeric precedence

Các scientific IDs dưới đây tồn tại ở Frozen/Integration tại ScientificLock. Values/units/population là nguyên metadata nguồn, kể cả hai findings đã nêu; không dùng bảng này để che bất nhất.

| Result ID | Value | Unit source | Population / condition source | Locator |
| --- | --- | --- | --- | --- |
| INT_A_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4 | 4 | cases | selected deterministic cases;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_A_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES | 35 | borrower-case instances | 18 selected cases × borrowers;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_A_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES | 14 | borrower-case instances | newly eligible borrower-case instances;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_A_NEWLY_ELIGIBLE_SKIPPED_INSTANCES | 21 | borrower-case instances | newly eligible borrower-case instances;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_A_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10 | 10 | paths | targeted audited MC paths;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_B_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4 | 0 | cases | selected deterministic cases;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_B_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES | 0 | borrower-case instances | 18 selected cases × borrowers;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_B_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES | 0 | borrower-case instances | newly eligible borrower-case instances;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_B_NEWLY_ELIGIBLE_SKIPPED_INSTANCES | 0 | borrower-case instances | newly eligible borrower-case instances;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_B_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10 | 0 | paths | targeted audited MC paths;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_MODERATE_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4 | 0 | cases | selected deterministic cases;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_MODERATE_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES | 11 | borrower-case instances | 18 selected cases × borrowers;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_MODERATE_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES | 2 | borrower-case instances | newly eligible borrower-case instances;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_MODERATE_NEWLY_ELIGIBLE_SKIPPED_INSTANCES | 9 | borrower-case instances | newly eligible borrower-case instances;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_MODERATE_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10 | 2 | paths | targeted audited MC paths;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_WEAK_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4 | 0 | cases | selected deterministic cases;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_WEAK_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES | 6 | borrower-case instances | 18 selected cases × borrowers;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_WEAK_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES | 0 | borrower-case instances | newly eligible borrower-case instances;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_WEAK_NEWLY_ELIGIBLE_SKIPPED_INSTANCES | 6 | borrower-case instances | newly eligible borrower-case instances;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| INT_C_WEAK_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10 | 0 | paths | targeted audited MC paths;  | [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) |
| RQ1_GRID32_MAX_DEPTH | 1 | waves | 32 deterministic cells; shock −5%…−40%; haircut 0/25/50/75% | [data/processed/research_final/validation_audit/corrected_run_v2/aave/shock_liquidity_grid.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/shock_liquidity_grid.csv) |
| RQ1_GRID60_DEPTH0 | 18 | cells | 60 deterministic cells; prespecified extended grid | [data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv) |
| RQ1_GRID60_DEPTH1 | 38 | cells | 60 deterministic cells; prespecified extended grid | [data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv) |
| RQ1_GRID60_DEPTH2 | 4 | cells | 60 deterministic cells; prespecified extended grid | [data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv) |
| RQ1_MC_SEVERE_DEPTH2_COUNT | 280 | paths | 10,000 Severe paths; seed=20260914; max_waves=100; horizon=120 | [data/processed/research_final/level3_p1_targeted_repair/monte_carlo/checkpoint_validation.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/monte_carlo/checkpoint_validation.json) |
| RQ1_MC_SEVERE_DEPTH2_FREQUENCY | 0.028 | ratio | 10,000 Severe paths; same as count | [data/processed/research_final/level3_p1_targeted_repair/monte_carlo/checkpoint_validation.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/monte_carlo/checkpoint_validation.json) |
| RQ1_MC_SEVERE_DEPTH3_COUNT | 0 | paths | 10,000 Severe paths; same as count | [data/processed/research_final/level3_p1_targeted_repair/monte_carlo/checkpoint_validation.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/monte_carlo/checkpoint_validation.json) |
| RQ2_CANONICAL_DEPTH_2PCT | 1667709.859389457 | USDC | canonical WETH/USDC 0.3% pool; executable depth within 2% | [data/processed/research_final/validation_audit/corrected_run_v2/aave/research_summary.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/research_summary.json) |
| RQ2_DEPTH2_HAIRCUT90_COUNT | 2 | cells | 60 deterministic cells; haircut=90% | [data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv) |
| RQ2_DEPTH2_HAIRCUT95_COUNT | 2 | cells | 60 deterministic cells; haircut=95% | [data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv) |
| RQ3_CAPITAL_100_LIQUIDATED | 9063.255437 | USDC token quantity | 109-position WETH/USDC cohort; capital=100% reference demand | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_capital_constraint.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_capital_constraint.csv) |
| RQ3_CAPITAL_25_LIQUIDATED | 0.0 | USDC token quantity | 109-position WETH/USDC cohort; capital=25% reference demand | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_capital_constraint.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_capital_constraint.csv) |
| RQ3_DELAY_SEVERITY_CHANGE | 0.0 | USDC | delay sweep 0/1/2/4 steps; −20% shock; haircut 40% | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_reaction_delay.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_reaction_delay.csv) |
| RQ4_IMMEDIATE_PRICE_IMPACT | 0.0010879429953578185 | ratio | Professor Demo liquidation sale; −20% shock; haircut 40% | [data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.csv) |
| RQ4_SPREAD_ARB0 | 0.0010879429953578185 | ratio | same scenario; arbitrage capacity=0% | [data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.csv) |
| RQ4_SPREAD_ARB100 | 4.632569078885678e-28 | ratio | same scenario; arbitrage capacity=100% | [data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.csv) |
| RQ5_HF_LT1_USDC_090 | 1 | borrowers | 109-position WETH/USDC cohort; USDC price=0.90 USD; debt valuation only | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv) |
| RQ5_HF_LT1_USDC_100 | 1 | borrowers | 109-position WETH/USDC cohort; USDC price=1.00 USD | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv) |
| RQ5_HF_LT1_USDC_110 | 3 | borrowers | 109-position WETH/USDC cohort; USDC price=1.10 USD; debt valuation only | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv) |
| RQ5_LIQUIDATED_DEBT_TOKEN_QTY | 9063.255437 | USDC token quantity | 109-position WETH/USDC cohort; USDC price=1.10 USD | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv) |
| RQ5_LIQUIDATED_DEBT_USD | 9969.5809807 | USD equivalent | 109-position WETH/USDC cohort; USDC price=1.10 USD | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.csv) |
| RQ6_BONUS103_SEIZED | 4.324574159823337 | WETH | executed liquidation in test scenario; bonus=3% | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_bonus.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_bonus.csv) |
| RQ6_BONUS107_SEIZED | 4.492518787389292 | WETH | executed liquidation in test scenario; bonus=7% | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_bonus.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_bonus.csv) |
| RQ6_LT083_UNLIQUIDATED | 229830.81461902 | USDC token quantity | 109-position frozen cohort; WETH LT override=83% | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.csv) |
| RQ6_LT0855_UNLIQUIDATED | 96839.39478531 | USDC token quantity | 109-position frozen cohort; WETH LT override=85.5% | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.csv) |
| RQ6_LTV0755_CAPACITY | 50797988.977634266 | USD | 109-position frozen cohort; counterfactual LTV=75.5% | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.csv) |
| RQ6_LTV0825_CAPACITY | 53675575.37423773 | USD | 109-position frozen cohort; counterfactual LTV=82.5% | [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.csv) |

Oracle comparison row IDs ORACLE_DIAG::… được giữ theo CSV, không bịa một namespace outcome khác. T5.2 table locator INT_T01_ELIGIBLE_VS_EXECUTED có population18×4×454, units instances/USDCtoken và tier MODEL_COMPUTED_COUNTERFACTUAL. Không dùng count instances như uniquewallets hoặc empiricalprobabilities.

## 5. Exhibit display specifications và exact data

Ba bảng T đã hoàn chỉnh trong main. Bảy F gồm một Mermaid schematic và sáu display specs; không gọi bất kỳ hình nào publication-rendered. Trạng thái source mapping G0 không tự thay thành renderer sign-off. Work không ghi Codex paths. Figures dùng SVG/PDF vector và PNG nếu giai đoạn production được giao; numeric source data dưới đây đủ để tạo đúng display, không smoothing/interpolation/newstatistic.


### F5.1 — section 5.1; handoff P3X-F5.1

- Academic purpose: Đối chiếu miền thử cũ/mở rộng và tác động của extreme tails.
- Related accepted claims: INT:CL_INT_RQ1_POLICY_CONDITIONAL, P2:C23.
- Related RQs: RQ1.
- Codex templates: P3X:ORACLE_POLICY_DEPTH2_COMPARISON.
- Display: Two panels groupedbars; x=depth0/1/2; y/fields=count cells; separate32/60.
- Actual production status: `DIRECT_DATA_SPEC_NOT_RENDERED`; G0 source-mapping status remains `DIRECT_LOCKED_SOURCE`.
- Scope/denominator/caption controls: PolicyA; separateP0v2/Level3 domains; not marketprobability.
- Required caption: Số ô depth 0/1/2 lần lượt là 12/20/0 trong lưới32 và 18/38/4 trong lưới60 theo Policy A. Miền thử khác nhau; haircut 90/95% là extreme counterfactual tails. Điều kiện hiển thị: Facet grids separately; 12/20/0 and 18/38/4 use different experiment domains.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/frozen_v3/tables/rq1_deterministic_depth.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq1_deterministic_depth.csv).

| grid | depth | count | source_version |
| --- | --- | --- | --- |
| 32 | 0 | 12 | P0 corrected v2 |
| 32 | 1 | 20 | P0 corrected v2 |
| 32 | 2 | 0 | P0 corrected v2 |
| 60 | 0 | 18 | Level-3 |
| 60 | 1 | 38 | Level-3 |
| 60 | 2 | 4 | Level-3 |

Rawgrid lookup only, không recompute depth/counts:
| shock_pct | liquidity_haircut_pct | cascade_depth |
| --- | --- | --- |
| -40.0 | 90.0 | 2 |
| -40.0 | 95.0 | 2 |
| -50.0 | 90.0 | 2 |
| -50.0 | 95.0 | 2 |

### T5.1 — section 5.2; handoff P3X-T5.1

- Academic purpose: Đặt 4/0/0/0 và10/0/0/2 đúng tập chọn.
- Related accepted claims: INT:CL_INT_RQ1_POLICY_CONDITIONAL, INT:CL_INT_RQ2_TWO_CHANNELS, P2:C32.
- Related RQs: RQ1, RQ2, RQ4.
- Codex templates: P3X:ORACLE_POLICY_DEPTH2_COMPARISON.
- Display: Markdowntable; x=Policy; y/fields=selecteddet /4;controls /4;targetedMC /10.
- Actual production status: `WORK_MARKDOWN_COMPLETE`; G0 source-mapping status remains `MATCHED`.
- Scope/denominator/caption controls: Targeted paths chosen onAdepth2; not probabilitysample.
- Required caption: Bốn selected deterministic cases cho 4/0/0/0 và mười targeted MC paths cho 10/0/0/2 ở A/B/C weak/C moderate. Paths được chọn theo depth2 dưới A, không ước lượng xác suất quần thể. Điều kiện hiển thị: Show /4 and /10 denominators; controls remain separate; ten paths are not a frequency estimator.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/oracle_transmission_diagnostic_v1/selection_manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/oracle_transmission_diagnostic_v1/selection_manifest.json); [data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv); [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv).

| policy_id | deterministic_depth2_count_of_4 | control_depth2_count_of_4 | selected_mc_depth2_count_of_10 |
| --- | --- | --- | --- |
| A_ADVERSE_PASS_THROUGH | 4 | 0 | 10 |
| B_REFERENCE_ONLY | 0 | 0 | 0 |
| C_WEAK_LAGGED_SMOOTHED_PROXY | 0 | 0 | 0 |
| C_MODERATE_LAGGED_SMOOTHED_PROXY | 0 | 0 | 2 |

### T5.2 — section 5.3; handoff P3X-T5.2

- Academic purpose: Bảng chính cho kết quả eligible/executed/skipped.
- Related accepted claims: INT:CL_INT_ELIGIBLE_NOT_EXECUTED, P2:C33.
- Related RQs: RQ1, RQ3.
- Codex templates: P3X:ELIGIBLE_VS_EXECUTED.
- Display: Markdowntable; x=Policy; y/fields=borrower-case-policy instances; new/evaluated/executed/skipped.
- Actual production status: `WORK_MARKDOWN_COMPLETE`; G0 source-mapping status remains `MATCHED`.
- Scope/denominator/caption controls: 18casesperpolicy; totaldesign18×4×454; no new ratios.
- Required caption: Eligible/executed/skipped: A 35/14/21; B 0/0/0; C weak 6/0/6; C moderate 11/2/9. Đơn vị borrower-case-policy instances, không unique wallets; 36 skips không có modeled USDC debt trên tuyến WETH/USDC. Điều kiện hiển thị: Units are borrower-case-policy instances; 36 skips are route-ineligible due to zero modeled USDC route debt.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv); [data/processed/research_final/scientific_integration_v1/table_figure_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/table_figure_registry.json).

| policy | new | evaluatedlater | executedwave2 | skipped |
| --- | --- | --- | --- | --- |
| A | 35 | 35 | 14 | 21 |
| B | 0 | 0 | 0 | 0 |
| C_WEAK | 6 | 6 | 0 | 6 |
| C_MODERATE | 11 | 11 | 2 | 9 |

### F5.2 — section 5.3; handoff P3X-F5.2

- Academic purpose: Sơ đồ phân nhánh giải thích vì sao newly eligible không bằng executed.
- Related accepted claims: P2:C03, P2:C33, INT:CL_INT_ELIGIBLE_NOT_EXECUTED.
- Related RQs: RQ1, RQ3.
- Codex templates: P3X:ELIGIBLE_VS_EXECUTED, P3X:SYSTEM_FEEDBACK_SCHEMATIC.
- Display: Mermaid category branching; x=decision gates; y/fields=no numericaxis; counts inT5.2.
- Actual production status: `SCHEMATIC_FROM_LOCKED_MODEL_SPEC`; G0 source-mapping status remains `CODEX_SPEC_REQUIRED`.
- Scope/denominator/caption controls: NO_NEW_BORROWER_EXAMPLE_SELECTED; no rawtraceevent selector independently read; genericgates do not attribute36skips to costs.
- Required caption: Phân biệt HF danh mục mới dưới 1, engine evaluation, route eligibility và execution có khoản nợ hoàn trả dương. 36 route skips không được gán cho gas, vốn hoặc profitability; ví dụ chỉ dùng event ID đã khóa. Điều kiện hiển thị: Use the smallest stable case/borrower key within the predeclared executed/skipped category; preserve pseudonymization; do not sample after viewing outcomes. Predeclare category (executed or skipped); sort case key then stable pseudonymized borrower key lexicographically; select the smallest key per category; pin exact trace/event locator in CP1 before rendering. No outcome-dependent manual choice; omit the example if locator/selector cannot be verified.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv); [docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md).

### F5.3 — section 5.2; handoff P3X-F5.3

- Academic purpose: Hai panel tránh đánh đồng impact với eligibility.
- Related accepted claims: P2:C07, P2:C32, INT:CL_INT_RQ2_TWO_CHANNELS.
- Related RQs: RQ1, RQ2, RQ4.
- Codex templates: P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS, P3X:ORACLE_POLICY_DEPTH2_COMPARISON.
- Display: Two independent panels; x=haircut%; policy atsinglecase; y/fields=countdepth2cells; separateUSD/WETH axis atq1.
- Actual production status: `DISPLAY_SPEC_READY_NOT_RENDERED`; G0 source-mapping status remains `CODEX_SPEC_REQUIRED`.
- Scope/denominator/caption controls: Only0unmodified;25–95counterfactual; compare commonpostWave1, not latermaxima.
- Required caption: Panel haircut dùng phần trăm và số ô, không phải đường độ sâu. Panel giá so cùng trạng thái sau Wave 1 theo USD/WETH trong comparison CSV. Policy A/B/C là giả định; later-trade maxima không là hiệu ứng arbitrage thuần. Điều kiện hiển thị: Only 0% is the unmodified canonical pool; 25–95% haircuts are modeled counterfactual transformations; 90/95% are extreme unobserved tails. Use separate axes for cells and USD/WETH.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/frozen_v3/tables/rq2_liquidity.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq2_liquidity.csv); [data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv).

PanelA: original assumption_status retained as source metadata; approved interpretation correctspositivehaircut labels.
| liquidity_haircut_pct | depth2_cells | assumption_status |
| --- | --- | --- |
| 0 | 0 | OBSERVED_BASELINE |
| 25 | 0 | OBSERVED_BASELINE |
| 50 | 0 | OBSERVED_BASELINE |
| 75 | 0 | OBSERVED_BASELINE |
| 90 | 2 | UNOBSERVED_COUNTERFACTUAL_TAIL |
| 95 | 2 | UNOBSERVED_COUNTERFACTUAL_TAIL |

PanelB: selector case_id=DET_D2_M40_H90, allfourpolicies.
| result_id | policy_id | direct_shock_valuation_price_usd_per_weth | post_wave1_dex_trade_price_usd_per_weth | post_wave1_borrower_valuation_price_usd_per_weth | post_wave1_dex_state_matches_a |
| --- | --- | --- | --- | --- | --- |
| ORACLE_DIAG::DET_D2_M40_H90::A_ADVERSE_PASS_THROUGH | A_ADVERSE_PASS_THROUGH | 1618.972080564 | 1582.303188529721999790257020 | 1582.303188529721999790257020 | True |
| ORACLE_DIAG::DET_D2_M40_H90::B_REFERENCE_ONLY | B_REFERENCE_ONLY | 1618.972080564 | 1582.303188529721999790257020 | 1618.972080564 | True |
| ORACLE_DIAG::DET_D2_M40_H90::C_WEAK_LAGGED_SMOOTHED_PROXY | C_WEAK_LAGGED_SMOOTHED_PROXY | 1618.972080564 | 1582.303188529721999790257020 | 1614.388469059715249973782128 | True |
| ORACLE_DIAG::DET_D2_M40_H90::C_MODERATE_LAGGED_SMOOTHED_PROXY | C_MODERATE_LAGGED_SMOOTHED_PROXY | 1618.972080564 | 1582.303188529721999790257020 | 1609.804857555430499947564255 | True |

### F5.4 — section 5.3; handoff P3X-F5.4

- Academic purpose: Phân biệt capital gate và timing, không đồng nhất recovery với processing delay.
- Related accepted claims: P2:C19, INT:CL_INT_RQ3_PRESERVED.
- Related RQs: RQ3, RQ4.
- Codex templates: .
- Display: Two independent panels; x=capitalratio; delaysteps; y/fields=USDCrepaid; processingdelayseconds.
- Actual production status: `DISPLAY_SPEC_READY_NOT_RENDERED`; G0 source-mapping status remains `DIRECT_LOCKED_SOURCE`.
- Scope/denominator/caption controls: ProfessorDemo; no split/recycle; recovery0 not reaction0.
- Required caption: Vốn tính theo phần trăm nhu cầu tham chiếu, debt repaid bằng USDC token; độ trễ tính bằng bước/giây. Không recycle vốn hoặc tự chia plan. Processing delay khác time to recovery. Điều kiện hiển thị: Debt repaid is USDC token quantity; processing delay is seconds; zero recovery is not zero reaction delay.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/frozen_v3/tables/rq3_constraints.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq3_constraints.csv).

| experiment | level | status | total_liquidated_debt_usdc | processing_delay_seconds |
| --- | --- | --- | --- | --- |
| capital | 0.25 | BINDING | 0.0 | 0 |
| capital | 0.5 | BINDING | 0.0 | 0 |
| capital | 1.0 | NON_BINDING | 9063.255437 | 0 |
| capital | 2.0 | NON_BINDING | 9063.255437 | 0 |
| delay | 0 | NOT_BINDING_IN_TESTED_RANGE | 9063.255437 | 0 |
| delay | 1 | NOT_BINDING_IN_TESTED_RANGE | 9063.255437 | 60 |
| delay | 2 | NOT_BINDING_IN_TESTED_RANGE | 9063.255437 | 120 |
| delay | 4 | NOT_BINDING_IN_TESTED_RANGE | 9063.255437 | 240 |

### F5.5 — section 5.4; handoff P3X-F5.5

- Academic purpose: Sửa kết luận cũ arbitrage không phản ứng.
- Related accepted claims: P2:C13, P2:C34, INT:CL_INT_RQ4_PRESERVED.
- Related RQs: RQ2, RQ4, RQ5.
- Codex templates: P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS.
- Display: Two series at3configpoints; x=arbcapacity0/50/100%; y/fields=impact/residual ratios; percentformat×100 iflabelled.
- Actual production status: `DISPLAY_SPEC_READY_NOT_RENDERED`; G0 source-mapping status remains `MATCHED`.
- Scope/denominator/caption controls: Sameforcedsale4.4085464736063145WETH; no timeseries/fundedexecution.
- Required caption: Với cùng forced sale, immediate impact và post-arbitrage residual là các tỷ lệ riêng, hiển thị phần trăm bằng nhân 100. Repositioning giảm residual chưa là funded executable swap. Điều kiện hiển thị: Immediate price impact and post-arbitrage residual are separate ratios; price repositioning is not a funded swap.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/frozen_v3/tables/rq4_arbitrage.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq4_arbitrage.csv).

| arbitrage_capacity_pct | immediate_price_impact_ratio | post_arbitrage_spread_ratio |
| --- | --- | --- |
| 0.0 | 0.0010879429953578185 | 0.0010879429953578185 |
| 50.0 | 0.0010879429953578185 | 0.0005439714976789092 |
| 100.0 | 0.0010879429953578185 | 4.632569078885678e-28 |

### T5.3 — section 5.5; handoff P3X-T5.3

- Academic purpose: Tách hướng tác động ceteris paribus và đơn vị tiền.
- Related accepted claims: P2:C15, P2:C35, INT:CL_INT_RQ5_PRESERVED.
- Related RQs: RQ5.
- Codex templates: .
- Display: Markdowntable; x=USD/USDC; y/fields=directpostshockHF<1in109; USDCtoken; USDequivalent.
- Actual production status: `WORK_MARKDOWN_COMPLETE`; G0 source-mapping status remains `DIRECT_LOCKED_SOURCE`.
- Scope/denominator/caption controls: HFcountbeforeliquidation; repaycolumnafterrun; debtvaluationonly.
- Required caption: RQ5 cô lập định giá nợ USDC trong cohort109. Báo riêng USD/USDC, số borrower HF<1, USDC token và USD-equivalent; chưa bao gồm redemption, liquidity hoặc settlement đầy đủ. Điều kiện hiển thị: Keep USDC token debt and USD-equivalent debt in separate columns with explicit price.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/frozen_v3/tables/rq5_usdc_valuation.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq5_usdc_valuation.csv).

| usdc_price_usd | borrowers_hf_below_1 | liquidated_debt_usdc_token | liquidated_debt_usd_equivalent |
| --- | --- | --- | --- |
| 0.9 | 1 | 9063.255437 | 8156.9298933 |
| 0.95 | 1 | 9063.255437 | 8610.09266515 |
| 0.99 | 1 | 9063.255437 | 8972.62288263 |
| 1.0 | 1 | 9063.255437 | 9063.255437 |
| 1.01 | 1 | 9063.255437 | 9153.88799137 |
| 1.05 | 2 | 9063.255437 | 9516.41820885 |
| 1.1 | 3 | 9063.255437 | 9969.5809807 |

### F5.6 — section 5.6; handoff P3X-F5.6

- Academic purpose: Ba panels không tạo một trục risk score chưa định nghĩa.
- Related accepted claims: P2:C04, P2:C05, P2:C12, INT:CL_INT_RQ6_PRESERVED.
- Related RQs: RQ3, RQ6.
- Codex templates: P3X:RISK_PARAMETER_MECHANISMS.
- Display: Three facets, no sharedyaxis; x=LTV; LT; bonusrate; y/fields=USDcapacity; portfolioUSD atq1 pendingunitlabel; WETHseized.
- Actual production status: `DISPLAY_SPEC_WITH_PROVENANCE_REPAIR_PENDING`; G0 source-mapping status remains `CODEX_SPEC_REQUIRED`.
- Scope/denominator/caption controls: P01LTV255vs109;P02LTunit/population; no governanceoptimum.
- Required caption: Ba panels biểu diễn ba cơ chế: LTV và ex-ante capacity USD; scenario LT và unliquidated USDC; bonus và WETH seized. Frozen cohort không có borrower response hoặc tối ưu governance. Điều kiện hiển thị: LTV→USD capacity, LT→USDC-token unliquidated debt, bonus→WETH seized; retain scenario LT semantics. Use separate facets with independent labelled axes; never combine USD, USDC token and WETH on one y-axis.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/frozen_v3/tables/rq6_policy.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq6_policy.csv).

Exactpoints; renderer không chọn unit/population cuối trước khiP01/P02 đượcCommander giải quyết. Bonusrawrate có floatingrepresentation; display3–7% là formatting, multiplier lấy detailedJSON.
| parameter | value | outcome | outcome_unit |
| --- | --- | --- | --- |
| LTV | 0.755 | 50797988.977634266 | USD max borrowing capacity |
| LTV | 0.78 | 51825698.40499265 | USD max borrowing capacity |
| LTV | 0.805 | 52853407.83235103 | USD max borrowing capacity |
| LTV | 0.815 | 53264491.60329438 | USD max borrowing capacity |
| LTV | 0.825 | 53675575.37423773 | USD max borrowing capacity |
| LT | 0.81 | 229830.81461902 | USDC token quantity, scenario-LT |
| LT | 0.82 | 229830.81461902 | USDC token quantity, scenario-LT |
| LT | 0.83 | 229830.81461902 | USDC token quantity, scenario-LT |
| LT | 0.855 | 96839.39478531 | USDC token quantity, scenario-LT |
| LT | 0.88 | 88458.67265557 | USDC token quantity, scenario-LT |
| bonus | 0.030000000000000027 | 4.324574159823337 | WETH seized |
| bonus | 0.040000000000000036 | 4.366560316714826 | WETH seized |
| bonus | 0.050000000000000044 | 4.4085464736063145 | WETH seized |
| bonus | 0.06000000000000005 | 4.450532630497803 | WETH seized |
| bonus | 0.07000000000000006 | 4.492518787389292 | WETH seized |

### F5.7 — section 5.7; handoff P3X-F5.7

- Academic purpose: Trình bày hội tụ có điều kiện không đếm prefix như samples độc lập.
- Related accepted claims: P2:C22, P2:C23, P2:C24.
- Related RQs: RQ1, RQ2, RQ3, RQ4, RQ5, RQ6.
- Codex templates: P3X:SEVERE_POLICY_A_MONTE_CARLO.
- Display: Prefix panel plusseparatebatchpanels; x=n forprefix; batchidotherwise; y/fields=frequencyratio +existingWilsonlower/upper.
- Actual production status: `DISPLAY_SPEC_READY_NOT_RENDERED`; G0 source-mapping status remains `MATCHED`.
- Scope/denominator/caption controls: PolicyA; nestedprefixes; no diagnostic10paths onfrequencychart.
- Required caption: Severe Policy A có 280/10.000 đường depth≥2, không thấy depth≥3 trong tập kiểm tra. Prefix 200/1.000/5.000/10.000 lồng nhau; dùng Wilson bounds đã khóa, không CI mới hoặc xác suất khủng hoảng. Điều kiện hiển thị: Prefixes are nested, Policy A only; no new interval; selected ten diagnostic paths stay off this frequency chart.
- Main caption có bổ sung findings nơi cần; không sửa numeric source hoặc originalmetadata.
- Exact locked sources: [data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv).

Exactbounds copied, no Wilsoncalculation. LowLiq lower~0 không silentlychange source.
| actual_runs | depth_ge_2_successes | depth_ge_2_frequency | depth_ge_2_wilson_lower | depth_ge_2_wilson_upper | depth_ge_3_successes | label | max_observed_cascade_depth | seed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 200 | 8 | 0.04 | 0.020405632066152313 | 0.07693206820093293 | 0 | Severe | 2 | 20260914 |
| 1000 | 31 | 0.031 | 0.02192400344715857 | 0.04366549601229214 | 0 | Severe | 2 | 20260914 |
| 5000 | 139 | 0.0278 | 0.023593021362704494 | 0.032731996354207454 | 0 | Severe | 2 | 20260914 |
| 10000 | 280 | 0.028 | 0.02494338524886922 | 0.03141910921304949 | 0 | Severe | 2 | 20260914 |
| 1000 | 23 | 0.023 | 0.015374276932992922 | 0.03427645066222666 | 0 | Severe seed robustness | 2 | 20261014 |
| 1000 | 37 | 0.037 | 0.026961180875554738 | 0.0505823974820693 | 0 | Severe seed robustness | 2 | 20261114 |
| 1000 | 0 | 0.0 | 2.168404344971009e-19 | 0.0038267584855551217 | 0 | Low Liquidity prespecified | 1 | 20260914 |

## 6. Supplemental numerical selectors được dùng trong prose

Các bảng sau chỉ lọc/chép existingfields, không tính thêm totals/statistics. Số scenario/debt/value của mỗi bảng giữ scope source; no new ratio, pvalue, CI or simulation.


[data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_capital_constraint.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_capital_constraint.json); selector `rows`:

| capital_ratio | capital_usdc | total_liquidated_debt_usdc | unliquidated_debt | usdc_price_usd |
| --- | --- | --- | --- | --- |
| 0.25 | 2265.81385925 | 0.0 | 230266.68368061 | 1.0 |
| 0.5 | 4531.6277185 | 0.0 | 230266.68368061 | 1.0 |
| 1.0 | 9063.255437 | 9063.255437 | 221203.42824361 | 1.0 |
| 2.0 | 18126.510874 | 9063.255437 | 221203.42824361 | 1.0 |

[data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_reaction_delay.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_reaction_delay.json); selector `rows`:

| delay_steps | delay_seconds | total_liquidated_debt_usdc | time_to_recovery_seconds | unliquidated_debt |
| --- | --- | --- | --- | --- |
| 0 | 0 | 9063.255437 | 0 | 221203.42824361 |
| 1 | 60 | 9063.255437 | 0 | 221203.42824361 |
| 2 | 120 | 9063.255437 | 0 | 221203.42824361 |
| 4 | 240 | 9063.255437 | 0 | 221203.42824361 |

[data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json); selector `rows`:

| liquidation_threshold | number_of_liquidation_events | total_liquidated_debt_usdc | unliquidated_debt | unliquidated_debt_legacy_recorded_lt | usdc_price_usd |
| --- | --- | --- | --- | --- | --- |
| 0.81 | 1 | 9063.255437 | 229830.81461902 | 221203.42824361 | 1.0 |
| 0.82 | 1 | 9063.255437 | 229830.81461902 | 221203.42824361 | 1.0 |
| 0.83 | 1 | 9063.255437 | 229830.81461902 | 221203.42824361 | 1.0 |
| 0.855 | 0 | 0.0 | 96839.39478531 | 230266.68368061 | 1.0 |
| 0.88 | 0 | 0.0 | 88458.67265557 | 230266.68368061 | 1.0 |

[data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_bonus.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_bonus.json); selector `rows`:

| liquidation_bonus | number_of_liquidation_events | total_liquidated_debt_usdc | collateral_seized_weth | liquidator_expected_profit_usdc |
| --- | --- | --- | --- | --- |
| 1.03 | 1 | 9063.255437 | 4.324574159823337 | 213.86115704675 |
| 1.04 | 1 | 9063.255437 | 4.366560316714826 | 304.12490977015113 |
| 1.05 | 1 | 9063.255437 | 4.4085464736063145 | 394.3877269836328 |
| 1.06 | 1 | 9063.255437 | 4.450532630497803 | 484.64960870173854 |
| 1.07 | 1 | 9063.255437 | 4.492518787389292 | 574.9105549390118 |

[data/processed/research_final/validation_audit/corrected_run_v2/aave/sensitivity.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/sensitivity.csv); familyselection:

| sensitivity_family | parameter_value | total_liquidated_debt_usdc | liquidation_events | unliquidated_debt |
| --- | --- | --- | --- | --- |
| GAS_MULTIPLIER | 1.0 | 9063.255437 | 1 | 221203.42824361 |
| GAS_MULTIPLIER | 2.0 | 9063.255437 | 1 | 221203.42824361 |
| GAS_MULTIPLIER | 4.0 | 9063.255437 | 1 | 221203.42824361 |
| GAS_MULTIPLIER | 8.0 | 9063.255437 | 1 | 221203.42824361 |
| LIQUIDATOR_CAPACITY | 500000.0 | 9063.255437 | 1 | 221203.42824361 |
| LIQUIDATOR_CAPACITY | 2500000.0 | 9063.255437 | 1 | 221203.42824361 |
| LIQUIDATOR_CAPACITY | 10000000.0 | 9063.255437 | 1 | 221203.42824361 |

[data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.json); scenario selector:

| scenario_name | forced_weth_sold | cascade_depth | total_liquidated_debt_usdc | max_intrawave_liquidation_price_impact | max_post_arbitrage_spread | time_to_recovery_seconds |
| --- | --- | --- | --- | --- | --- | --- |
| Severe | 10.07667765395729 | 1 | 18126.510874 | 0.005543931893162673 | 0.004157948919872006 | 60 |
| No Arbitrage | 4.4085464736063145 | 1 | 9063.255437 | 0.0010879429953578185 | 0.0010879429953578185 | 0 |
| Strong Arbitrage | 4.4085464736063145 | 1 | 9063.255437 | 0.0010879429953578185 | 4.632569078885678e-28 | 0 |
| PROFESSOR_DEMO | 4.4085464736063145 | 1 | 9063.255437 | 0.0010879429953578185 | 0.0005439714976789092 | 0 |

[data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json); batches[label=Severe,actual_runs=10000,seed=20260914].loss_quantiles:

| field | value | unitcondition |
| --- | --- | --- |
| p95 | 36256.10583716855 | composite exposure; baselineUSDC/USD1; not realizedloss |
| expected_shortfall_95 | 38959.72038374711 | composite exposure; baselineUSDC/USD1; not realizedloss |

[data/processed/research_final/validation_audit/corrected_run_v2/aave/monte_carlo.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/monte_carlo.json); scenarios[Low Liquidity]: runs=200, seed=20260914, summary.model_implied_cascade_frequency=0.0. Old200-scenario provenance separate fromLevel3prespecified1000; no source replacement.

## 7. RQ coverage và source-role separation

| RQ | Exact original question | Coverage |
| --- | --- | --- |
| RQ1 | Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)? | 5.1/5.7; grids/PolicyAfrequency/targeteddiagnostic; conditionalcascade |
| RQ2 | Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt? | 5.2; DEXabsorption khác valuation; postWave1 commonstate |
| RQ3 | Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý? | 5.3; resourcegates và eligibility/route/positiveevents |
| RQ4 | Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi? | 5.4; sameforcedsale immediate/residual; nofundedexecution |
| RQ5 | Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset? | 5.5;109route directHFcount vs executedtoken/USD; debtvaluationonly |
| RQ6 | Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk? | 5.6; separatecapacity/HF/assettransfer;P01/P02metadata awaitingrepair |

## 8. Source-read limits, integrity và boundaries

62 files fetched đúng ref và kiểm Gitblob. Bốn lockedchapters lấy toàn văn đúng integration, identitymatches bản đã đọc/biên soạn; không sửa. Mã đọc bổ sung chỉ nhằm xác minh metric/cohort/decision gates, không fullrepoaudit.

Hai oversized borrowerCSVs vẫn chưa Work directfullrow/fullcellread: Oracle borrower_level_evidence.csv (8.775.089bytes) và Integration eligible_vs_executed_audit.csv (18.489.195bytes). Không có targeted_event_trace.jsonl read trong lượt này, nên F5.2 không thêm borrowerexample hoặc claim raw event verification. Addendum/premerge reports được dùng như reports có executor/scope đã nêu.

WORK_INDEPENDENT_STATIC_RECONSTRUCTION là hoạt độngP2 thừa kế; CODEX_REPLAY_VERIFICATION và CODEX_PREMERGE_AUDIT không là newWorkrun. Lượt hiện tại kiểm nguồn/tables/claims/captions và selfreview; không rerunHF, replay, MC, RPC, regressions hoặc CI.

Hash table dùng SHA1 Gitblob/LF domain, khác SHA256 filebytes. WindowsCRLF checkout bytes có thể khác GitLF; không khẳng định byte-identical crossOS hay dùng hashmatch làm economicvalidation. source access labels abstract/preview giữ nguyên.

Một snapshot26045352,454verifiedportfolios,109routecohort; thêm LTVdetail255 là provenancefindingP01, không cohorttự tạo. Một venue/representativeagents/nonrecycle/nonsplit, A/B/Chypothetical, extremehaircuts, no validatedfundedfork, stablecoinvaluationonly, metricexposurekhácrealizedloss đều đặt giới hạn kết luận. Historical/Terra/network phân tích ởCh6, không newcausal/forecast claim.

## 9. Four disallowed records

| Registry ID | Original disposition | Safeguard |
| --- | --- | --- |
| INT:CL_FROZEN_RQ1_UNQUALIFIED_WORDING | REJECTED_AS_WORDED_SUPERSEDED | Audittrail only; noaffirmative premise or ID inmain |
| INT:CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING | REJECTED_AS_WORDED_SUPERSEDED | Audittrail only; noaffirmative premise or ID inmain |
| INT:CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT | UNSUPPORTED | Audittrail only; noaffirmative premise or ID inmain |
| INT:CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION | UNSUPPORTED | Audittrail only; noaffirmative premise or ID inmain |

## 10. Exact read-source identity ledger

| File/permalink | Read ref | GitblobSHA1 |
| --- | --- | --- |
| [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | bac44e61633b5efdde3665731ea69fbf4ca345e6 |
| [data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json) | 3f6e5302483681209e2408531eb5a15389f9fded | fffe69d45f2c70e8f4cb781c8b521ef4cf6f1a45 |
| [data/processed/research_final/final_accepted_claims_v1/claim_evidence_crosswalk.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/claim_evidence_crosswalk.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 312b72f23b0115d1de69eec2dc1a87b0f490070a |
| [data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | a6784fd7f1b7288c4f2177ff8ba102be5e01c81e |
| [data/processed/research_final/final_accepted_claims_v1/manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/manifest.json) | 3f6e5302483681209e2408531eb5a15389f9fded | bad223e0859a4fe135dd4f7b48b78513ade88123 |
| [data/processed/research_final/final_accepted_claims_v1/validation_report.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/validation_report.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 3e467a7894589062791c3546050d59316b4bf2b2 |
| [docs/research_final/FINAL_ACCEPTED_CLAIMS_REGISTRY_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/FINAL_ACCEPTED_CLAIMS_REGISTRY_v1.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 0c3298c2cb8a7d2ed317bd04278811f054c3753d |
| [docs/research_final/SCIENTIFIC_CONTENT_LOCK_REVIEW_PACKET.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_CONTENT_LOCK_REVIEW_PACKET.md) | 3f6e5302483681209e2408531eb5a15389f9fded | c2a25f45ddff2eed89c1394c0591674e3ee8d8e3 |
| [docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 856768b29fd0cefa5caba5d5721dc759f025cdba |
| [docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 144c14e9d7fe1a567a5c694abb8a93c1a483ec13 |
| [docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md) | 3f6e5302483681209e2408531eb5a15389f9fded | f3fd437b41d0feabacf01f6708ca65d3a738ef05 |
| [docs/research_final/LITERATURE_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LITERATURE_VERIFIED.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 6ebe0a11e915e942a422d02a0cc5b1d53b51ff3e |
| [docs/research_final/REFERENCE_EVIDENCE_MATRIX.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/REFERENCE_EVIDENCE_MATRIX.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 504ea91b046e6612c2840c6a434e740ce917b29f |
| [docs/research_final/APA_REFERENCES_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/APA_REFERENCES_VERIFIED.md) | 3f6e5302483681209e2408531eb5a15389f9fded | c76d7cf482565615a92fb17b888a392e4f8fd9cc |
| [docs/research_final/TERMINOLOGY_VI.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/TERMINOLOGY_VI.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 2ca1e29495e6183dfefaf8939e59e6c4eba574fb |
| [docs/research_final/P2_CLAIM_EVIDENCE_CROSSWALK.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/P2_CLAIM_EVIDENCE_CROSSWALK.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 932c25f633dee7bdb8cfcf9e6e2473b50f7c4ab3 |
| [data/processed/research_final/frozen_v3/manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/manifest.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 5fa6f68d25dd4df88b042a7b31be014f8b46dd38 |
| [data/processed/research_final/frozen_v3/results_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/results_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 6dde91fc11d189de8899c742b44fea9cf0f386ae |
| [data/processed/research_final/frozen_v3/claim_ledger.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/claim_ledger.json) | 3f6e5302483681209e2408531eb5a15389f9fded | f8d095676f1a0e10b37206c851b4e229a5e563a1 |
| [data/processed/research_final/frozen_v3/tables/rq1_deterministic_depth.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq1_deterministic_depth.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | f0e80bc73735de7684feadd2cd3c82519331c033 |
| [data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | ea71db6f633b7e5df1f12cd3d9f2533e5d5f9438 |
| [data/processed/research_final/frozen_v3/tables/rq2_liquidity.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq2_liquidity.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | d753e24d06d35cc6d31ab2ef07ea6740ce862edb |
| [data/processed/research_final/frozen_v3/tables/rq3_constraints.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq3_constraints.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 0a51fb795e562c0276ac36903662be92d52ce86f |
| [data/processed/research_final/frozen_v3/tables/rq4_arbitrage.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq4_arbitrage.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 1fdeb6b31a7537d79e9e8c9e97544dbf78bb4f2e |
| [data/processed/research_final/frozen_v3/tables/rq5_usdc_valuation.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq5_usdc_valuation.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 3f36a867c750f90d5a88ae5b1b00eae6be151b6e |
| [data/processed/research_final/frozen_v3/tables/rq6_policy.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq6_policy.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | deab1f45c56d8c836fead08190faffb1a5000fd2 |
| [data/processed/research_final/oracle_transmission_diagnostic_v1/manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/oracle_transmission_diagnostic_v1/manifest.json) | 3f6e5302483681209e2408531eb5a15389f9fded | f9fe56ca2325dca85a8cfe580571cfc0964ce7f5 |
| [data/processed/research_final/oracle_transmission_diagnostic_v1/selection_manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/oracle_transmission_diagnostic_v1/selection_manifest.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 1bb5bdea8be74c1e62dc89badbcb8cbae67b7bd3 |
| [data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | dee128ff278efe94895220aca5eccec4150c1cc4 |
| [data/processed/research_final/scientific_integration_v1/manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/manifest.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 2c80327f45bcb1bc3173c0017718dc933410a0fd |
| [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 664eeac6d3d80a38dc4c2ca6c942070f09d8d9f8 |
| [data/processed/research_final/scientific_integration_v1/table_figure_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/table_figure_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | c74345f75c02a4550151a0cf7802fa96fecdd202 |
| [data/processed/research_final/scientific_integration_v1/claim_to_result_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/claim_to_result_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | f893411d13a5ee83dc64fe8d3530bd59355ac503 |
| [data/processed/research_final/scientific_integration_v1/six_rq_evidence_matrix.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/six_rq_evidence_matrix.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 0f9707700e508a100bbe0ff845f54579d3d28733 |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_capital_constraint.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_capital_constraint.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 8944562ec11fb550f3eede06fbb2044634de31e9 |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_reaction_delay.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq3_reaction_delay.json) | 3f6e5302483681209e2408531eb5a15389f9fded | e73525a5bbd6910d441e4b1bd9ad9cc8b2848c0a |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq5_usdc_depeg.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 39f0cb744adc8e24578960f2a3352c196393f824 |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_bonus.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_bonus.json) | 3f6e5302483681209e2408531eb5a15389f9fded | c8d8f83ac40bf38275e58f07f2020c21243c0012 |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 603ca694a923bbe7872782d64779e96497fee3b9 |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.json) | 3f6e5302483681209e2408531eb5a15389f9fded | a58c672cb123eccc0e64a040c37c636d1541698f |
| [data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 1fa9f467a663f5a7fc971068571311ce55e71c9c |
| [data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 3a38cce65c91dcc9eb4ca957aa6946d34bb2e7e3 |
| [data/processed/research_final/level3_p1_targeted_repair/monte_carlo/checkpoint_validation.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/monte_carlo/checkpoint_validation.json) | 3f6e5302483681209e2408531eb5a15389f9fded | bc8c06873698ec01620e3dd5e260ed29c8c1e55f |
| [docs/manuscript_p3/work/P3_MANUSCRIPT_BLUEPRINT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_MANUSCRIPT_BLUEPRINT_v1.md) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 10194e95b67a360cadd7ab2eb9550deac206e672 |
| [docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json) | 8de52bebabef376be700836e6f93a92d7394d2c3 | e10159ba8659c4dc6b528a7da645d4a20f39a9aa |
| [docs/manuscript_p3/work/P3_TABLE_FIGURE_EQUATION_PLAN.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_TABLE_FIGURE_EQUATION_PLAN.json) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 5d4897797915b9359d6e4e3defeedff770e6b875 |
| [docs/manuscript_p3/work/P3_G0_WORK_CODEX_EXHIBIT_CROSSWALK.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_G0_WORK_CODEX_EXHIBIT_CROSSWALK.json) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 27475694e8e94ae4f6dd16bfdb76a956ba080877 |
| [docs/manuscript_p3/work/P3_CHAPTER_ACCEPTANCE_RUBRIC.md](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_CHAPTER_ACCEPTANCE_RUBRIC.md) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 753b40a123677ddda25a178957ed6cc8a55b2c16 |
| [docs/manuscript_p3/work/chapter_01/CHAPTER_01_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/30c6ce6859603460c8eb5a496e4f8c36f9339cf0/docs/manuscript_p3/work/chapter_01/CHAPTER_01_FULL_DRAFT_v1.md) | 30c6ce6859603460c8eb5a496e4f8c36f9339cf0 | c3fffec83f427c52c595dd02fd73a9c81db5cfcd |
| [docs/manuscript_p3/work/chapter_02/CHAPTER_02_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/30c6ce6859603460c8eb5a496e4f8c36f9339cf0/docs/manuscript_p3/work/chapter_02/CHAPTER_02_FULL_DRAFT_v1.md) | 30c6ce6859603460c8eb5a496e4f8c36f9339cf0 | b73f337c99cdf6a137fac4d54e9b49b1aebb3a40 |
| [docs/manuscript_p3/work/chapter_03/CHAPTER_03_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/30c6ce6859603460c8eb5a496e4f8c36f9339cf0/docs/manuscript_p3/work/chapter_03/CHAPTER_03_FULL_DRAFT_v1.md) | 30c6ce6859603460c8eb5a496e4f8c36f9339cf0 | f8609f120d6f8e1fa9bb3aa9393fe45092888439 |
| [docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/30c6ce6859603460c8eb5a496e4f8c36f9339cf0/docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md) | 30c6ce6859603460c8eb5a496e4f8c36f9339cf0 | 5fe370a245e11a6ae9a7f2cc6349dc30d97893a2 |
| [data/processed/research_final/scientific_integration_v1/integration_result_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/integration_result_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 64b78e13f87adcc9bcc70188ca692d4a4196bff1 |
| [data/processed/research_final/validation_audit/corrected_run_v2/aave/sensitivity.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/sensitivity.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 45f9b94fe2fe8559cf52eb496fcf4eca918bff01 |
| [sim/metrics/risk.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/metrics/risk.py) | 3f6e5302483681209e2408531eb5a15389f9fded | 794593593b2afc0d2a23eb375744c0a9e4eae7aa |
| [sim/research/rq_completion.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/research/rq_completion.py) | 3f6e5302483681209e2408531eb5a15389f9fded | c4d824bbdbf6fcdd846b23306b6e3fc83301d8e3 |
| [sim/agents/liquidator.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/agents/liquidator.py) | 3f6e5302483681209e2408531eb5a15389f9fded | 9f44ba9a8037f239b2b5ef8881ad2d49c25ecf6d |
| [data/processed/research_final/oracle_transmission_diagnostic_v1/policy_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/oracle_transmission_diagnostic_v1/policy_summary.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | bc8a138a0d6c4b7ddce98379aec14a1f811c4d5b |
| [data/processed/research_final/validation_audit/corrected_run_v2/aave/monte_carlo.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/monte_carlo.json) | 3f6e5302483681209e2408531eb5a15389f9fded | b76df66141d4382736d52e8eb6ef3bea9353ed8f |
| [data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 4f1b5682445306a48751a231eadf87c6d03dbc8c |
| [data/processed/research_final/validation_audit/corrected_run_v2/aave/shock_liquidity_grid.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/aave/shock_liquidity_grid.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 6fcdd0ef1cb674ea467a577d2eea6cc8ba5a63b4 |
| [scripts/run_full_research_pipeline.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/scripts/run_full_research_pipeline.py) | 3f6e5302483681209e2408531eb5a15389f9fded | 460e7d79f3ca9835df56181f65e9d2c83a3d2748 |

**Handoff decision:** `CHAPTER_05_TARGETED_REPAIR_REQUIRED` vì CH05-P01/P02. Fullmanuscript và exhibitspecs hoàn chỉnh; cần source metadata decision/repair có mục tiêu trước scientificacceptance, không viết lại toàn chương và không tự merge/lock.
