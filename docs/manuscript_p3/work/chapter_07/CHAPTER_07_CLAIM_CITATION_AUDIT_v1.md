# CHAPTER_07_CLAIM_CITATION_AUDIT_v1

**Recommendation: `CHAPTER_07_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`.** Toàn văn tổng hợp học thuật, không tạo một bộ claims hoặc kết quả mới. `WORK_PINNED_SOURCE_SYNTHESIS_AND_SELF_REVIEW`; không external independent peer review hoặc tái chạy kiểm định của Codex.

- Scientific Lock: `3f6e5302483681209e2408531eb5a15389f9fded`; Final Accepted Claims Registry `final-accepted-claims-v1.1-targeted-repair`.
- Blueprint Lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Starting integration / six locked chapters: `f5f9c338a3a38ec07b3a21ba5cdc29749daf9833`.
- Branch: `research/p3-ch07-full-manuscript-work`; exact final commit ở Git/PR handoff, không tự nhúng SHA chính commit.
- Chỉ ba file Work/chapter_07; không sửaCh1–6/scientific sources/Blueprint/Codex paths.

## 1. Claim allocation và usage

1/1 primary claim của Chương7 là P2:C17; không gọi các primary destinations ở chương trước thành primary của chương này. Dùng33accepted components gồm24P2+9Integration: C17primary và32secondary synthesis references. Mọi record giữ nguyên primary/secondary allocation và final gate. Nguồn khái niệm không bị ép có numerical result; source literature không là bằng chứng implementation. Associated source IDs của record có thể rộng hơn các source thực sự được viện dẫn trong Chương7.

| Registry ID | Final gate | Primary chapter | Secondary chapters | Use in Ch07 | Primary evidence tier |
| --- | --- | --- | --- | --- | --- |
| P2:C03 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.1.1/RQ3;7.4.1: HF khác execution | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C04 | ACCEPTED | 2 | 3, 4, 5, 7 | 7.1.1/RQ6;7.4.1: LTV/LT/bonus riêng | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C07 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | 7.1.1/RQ2;7.4.1: thanh khoản theo khoảng | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C09 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | 7.1.1/RQ1;7.1.2: nền fire-sale/tác động giá | MIXED_SCHOLARLY_ONCHAIN_AND_MODEL_CROSSWALK |
| P2:C10 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | 7.1.2;7.3.2: quan hệ thống kê khác nhân quả | MIXED_SCHOLARLY_ONCHAIN_AND_MODEL_CROSSWALK |
| P2:C11 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | 7.1.2: S13 empirical null không bị modelWave2 bác bỏ | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C12 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | 7.1.1/RQ3,RQ6: participationcost/design context | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C13 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | 7.1.1/RQ4: arbitrage access/context, không WETH calibration | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C15 | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | 7.1.1/RQ5: debtvaluation, không full depeg | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C16 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 7.2.3: literature Terra/context, hai version cùng study | SCHOLARLY_SOURCE |
| P2:C17 | ACCEPTED_WITH_LIMITATIONS | 7 | 1, 6 | PRIMARY:7.1.1/RQ5;7.2.3;7.3.2;7.4;7.5: ranh giới chuyển kết quả Terra→Aave | SCHOLARLY_SOURCE |
| P2:C18 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.2.1: ABM là hướng nghiên cứu có trước, S20 abstract | SCHOLARLY_SOURCE |
| P2:C19 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.3.1: representative agents và execution assumptions | CODE_OBSERVATION |
| P2:C20 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.2.1: ODD/traceable description, không chứng nhận implementation | SCHOLARLY_SOURCE |
| P2:C21 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.2.1: Gauntlet practitioner source, không benchmark superiority | SCHOLARLY_SOURCE |
| P2:C22 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.3.2: parameterMC/nestedprefixes, không priceprocess hoặc independent checkpoints | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C23 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.3.2: SevereA280/10000 và lockedWilson conditional | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C24 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.3.1: debt repaid/composite tail không realizedloss | PROJECT_METRIC_DEFINITION |
| P2:C26 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 7.3.2;7.4.2: graphgộp/structural boundary, không riskweighted ranking | CODE_OBSERVATION |
| P2:C30 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 7.2.3;7.3.2: negative cutoff-safe finding | DERIVED_HISTORICAL_VALIDATION_RESULT |
| P2:C31 | ACCEPTED_WITH_LIMITATIONS | 1 | 2, 7 | 7.2;7.4;7.5: scoped integration/tracing contribution | SCHOLARLY_SOURCE |
| P2:C32 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.1;7.3.1: A/B/C hypothetical valuation policies | CODE_OBSERVATION_AND_MODEL_COMPUTED_COUNTERFACTUAL |
| P2:C33 | ACCEPTED_WITH_LIMITATIONS | 4 | 3, 5, 7 | 7.1.1/RQ3;7.2.2: modeledHF transition khác routeexecution | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK |
| P2:C35 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | 7.1.1/RQ5,RQ6;7.3.1: token/USD; scopedUSDCvaluation | CODE_OBSERVATION_WITH_SCOPED_MODEL_LIMITATION |
| INT:CL_INT_RQ1_POLICY_CONDITIONAL | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | 7.1.1/RQ1;7.1.2;T7.1 | MODEL_COMPUTED_COUNTERFACTUAL |
| INT:CL_INT_RQ2_TWO_CHANNELS | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | 7.1.1/RQ2;T7.1 | MODEL_COMPUTED_COUNTERFACTUAL |
| INT:CL_INT_ELIGIBLE_NOT_EXECUTED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | 7.1.1/RQ3;7.2.2;T7.2 | MODEL_COMPUTED_COUNTERFACTUAL |
| INT:CL_INT_RQ3_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | 7.1.1/RQ3;T7.1 | MODEL_COMPUTED_COUNTERFACTUAL |
| INT:CL_INT_RQ4_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | 7.1.1/RQ4;T7.1 | MODEL_COMPUTED_COUNTERFACTUAL |
| INT:CL_INT_RQ5_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | 7.1.1/RQ5;T7.1 | MODEL_COMPUTED_COUNTERFACTUAL |
| INT:CL_INT_RQ6_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | 7.1.1/RQ6;T7.1 | MODEL_COMPUTED_COUNTERFACTUAL |
| INT:CL_INT_HISTORICAL_TIERS_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 7.2.3;7.3.2:28/27,tiers1/2/23/1 | ONCHAIN_HISTORICAL_OBSERVATION |
| INT:CL_INT_TERRA_NEGATIVE_PRESERVED | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | 7.2.3;7.3.2;T7.2 | DERIVED_HISTORICAL_VALIDATION_RESULT |


Nguồn: [docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json); [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json).

| Record | Accepted scope | Required limitations from locked record |
| --- | --- | --- |
| P2:C03 | HF<1 là đủ điều kiện, execution còn điều kiện | Không gọi mọi eligible là đã thanh lý; Independent static reconstruction of 32688 direct/post HF pairs matched all 72 summary counts and 52 available Wave2 event HF values; all 36 raw NOT_ELIGIBLE skips resolved to NO_MODELLED_USDC_DEBT. Oversized raw CSV cells remain unread, so no exact cell-by-cell source-file comparison claimed. |
| P2:C04 | LTV khác LT và liquidation bonus | LTV không viết lại frozen debt |
| P2:C07 | Thanh khoản Uniswap V3 phụ thuộc các khoảng tick. Trong mô phỏng, suy giảm độ sâu làm thay đổi khả năng hấp thụ bán thế chấp và tác động giá; eligibility mới còn phụ thuộc chính sách định giá. | TVL khác depth; 90/95% haircut là giả định tail; Independent static reconstruction of 32688 direct/post HF pairs matched all 72 summary counts and 52 available Wave2 event HF values; all 36 raw NOT_ELIGIBLE skips resolved to NO_MODELLED_USDC_DEBT. Oversized raw CSV cells remain unread, so no exact cell-by-cell source-file comparison claimed. |
| P2:C09 | Literature hỗ trợ bán thế chấp; lịch sử ghi receipt route và association | Một WETH route được kiểm receipt; không chứng minh price causality/cascade |
| P2:C10 | Liquidation/volatility relation khác xác nhận nhân quả | Cùng shock/market movement không là simulated endogenous wave |
| P2:C11 | S13 không tìm thấy tác động giá kéo dài có ý nghĩa thống kê trong thiết kế đã xét; DeFiStress mô phỏng thanh lý vòng hai ở những trường hợp stress được chọn dưới Policy A. Hai kết quả có phạm vi và chuẩn đối chiếu khác nhau. | Khác tần suất/đối chứng; không dùng model wave 2 bác empirical null; Independent static reconstruction of 32688 direct/post HF pairs matched all 72 summary counts and 52 available Wave2 event HF values; all 36 raw NOT_ELIGIBLE skips resolved to NO_MODELLED_USDC_DEBT. Oversized raw CSV cells remain unread, so no exact cell-by-cell source-file comparison claimed. |
| P2:C12 | Fixed spread/auction có đánh đổi theo participation cost | Không nói đấu giá luôn tốt hoặc Aave dùng đấu giá |
| P2:C13 | Arbitrage có điều kiện; v2 tách intrawave và residual | Sweep intrawave giữ nguyên, residual giảm; price teleportation |
| P2:C15 | USDC debt price tăng làm HF giảm ceteris paribus | Là dấu kênh valuation; chưa đầy đủ stress stablecoin |
| P2:C16 | Terra run liên quan khuyến khích/quan sát/tập trung | Không gán chỉ một thủ phạm hoặc thêm tỷ lệ không kiểm |
| P2:C17 | Terra không xác nhận trực tiếp tham số Aave | Kết luận giới hạn của nghiên cứu, không trích như phát hiện định lượng JFE |
| P2:C18 | ABM cho phép tương tác và khác biệt tác nhân | Không chứng minh tham số hay nhiều bot trong implementation |
| P2:C19 | Nhánh Aave của DeFiStress sử dụng một tác nhân thanh lý và một tác nhân kinh doanh chênh lệch giá đại diện. | Không gọi nhiều bot cạnh tranh được ước lượng hành vi; Independent static reconstruction of 32688 direct/post HF pairs matched all 72 summary counts and 52 available Wave2 event HF values; all 36 raw NOT_ELIGIBLE skips resolved to NO_MODELLED_USDC_DEBT. Oversized raw CSV cells remain unread, so no exact cell-by-cell source-file comparison claimed. |
| P2:C20 | ODD nên mô tả scheduling/model con và liên kết code | ODD không tự cấp chứng nhận mô hình đúng |
| P2:C21 | Ngành dùng ABM/MC cho stress tham số DeFi | Forum không peer reviewed, không claim tái tạo Gauntlet |
| P2:C22 | MC lấy mẫu tham số; checkpoint stages có prefix lồng và accounting tách biệt | 13k batch identities, 0 duplicates, 21/21 reproduce; legacy duration unavailable; Independent static reconstruction of 32688 direct/post HF pairs matched all 72 summary counts and 52 available Wave2 event HF values; all 36 raw NOT_ELIGIBLE skips resolved to NO_MODELLED_USDC_DEBT. Oversized raw CSV cells remain unread, so no exact cell-by-cell source-file comparison claimed. |
| P2:C23 | Trong cấu hình baseline Policy A, Severe ghi nhận 8/200 đường mô phỏng ở P0 v2 và 280/10.000 đường ở Level-3 có độ sâu thanh lý từ hai vòng trở lên; Low Liquidity ghi nhận 0/1.000. Khoảng Wilson mô tả bất định lấy mẫu có điều kiện trong từng cấu hình. | Tên lịch sử NIST không đổi tên Wilson; không forecast |
| P2:C24 | Chỉ tiêu đuôi của dự án là thống kê phơi nhiễm tổng hợp theo định nghĩa và đơn vị đã khóa; khoản nợ hoàn trả không được coi là tổn thất đã thực hiện. | Repayment không phải loss; giữ units/ties/provenance |
| P2:C26 | Các chỉ số trung tâm của dự án được tính trên đồ thị dị thể đã gộp. | Gộp max; structural metric chưa risk-weighted |
| P2:C30 | Đánh giá cảnh báo cutoff-safe của Terra ghi nhận kết quả âm trước lần lệch neo ban đầu; kết quả kiểm chứng hồi cứu này không hỗ trợ kết luận dự báo ngoài mẫu thành công. | Source paper không chứng nhận retrospective forecast |
| P2:C31 | Novelty đề xuất là tích hợp truy vết và giới hạn rõ | Không first ever; contribution còn phải audit thực hiện |
| P2:C32 | Policy A của mô hình lấy giá trị nhỏ hơn giữa giá tham chiếu và giá DEX; Policy B chỉ dùng giá tham chiếu; các Policy C là giả định truyền giá có độ trễ và làm trơn. Các chính sách này chưa được xác minh là cơ chế oracle thực tế của Aave hoặc Chainlink. | Synthetic feedback không là Aave oracle thật; Independent static reconstruction of 32688 direct/post HF pairs matched all 72 summary counts and 52 available Wave2 event HF values; all 36 raw NOT_ELIGIBLE skips resolved to NO_MODELLED_USDC_DEBT. Oversized raw CSV cells remain unread, so no exact cell-by-cell source-file comparison claimed. |
| P2:C33 | Kiểm toán HF trong mô hình theo Policy A ghi nhận các vị thế mới mất an toàn sau Wave 1; việc mới đủ điều kiện theo HF được đối chiếu riêng với các lần thanh lý vòng hai có hoàn trả nợ dương. | Chỉ simulated endogenous eligibility; không phải cascade lịch sử; Independent static reconstruction of 32688 direct/post HF pairs matched all 72 summary counts and 52 available Wave2 event HF values; all 36 raw NOT_ELIGIBLE skips resolved to NO_MODELLED_USDC_DEBT. Oversized raw CSV cells remain unread, so no exact cell-by-cell source-file comparison claimed. |
| P2:C35 | RQ5 của dự án giới hạn ở kênh định giá nợ USDC theo đơn vị và phạm vi đã khóa, chưa phải mô hình thực thi đầy đủ khi mất neo. | Đã kiểm version; valuation sensitivity không full-depeg validation |
| INT:CL_INT_RQ1_POLICY_CONDITIONAL | Thanh lý vòng hai xuất hiện trong các trường hợp đuôi đã chọn dưới Policy A và nhạy với chính sách định giá A/B/C. | No oracle-independent threshold, actual Aave probability or historical causal cascade. |
| INT:CL_INT_RQ2_TWO_CHANNELS | Thanh khoản quyết định sức hấp thụ và tác động giá trên DEX; chính sách định giá quyết định việc trạng thái DEX có truyền sang HF hay không. | Liquidity weakness alone does not guarantee new eligibility or execution. |
| INT:CL_INT_ELIGIBLE_NOT_EXECUTED | Vị thế mới đủ điều kiện theo HF danh mục, được engine thẩm định và có thanh lý đã thực thi với khoản nợ hoàn trả dương là ba trạng thái khác nhau. | Execution is modeled by one representative liquidator and does not establish external contagion. |
| INT:CL_INT_RQ3_PRESERVED | Trong miền thử đã khóa, các mức vốn thấp ràng buộc năng lực thanh lý; độ trễ không làm thay đổi mức độ nghiêm trọng trong chính miền thử đó. | Representative agent, no capital recycling, no fork. |
| INT:CL_INT_RQ4_PRESERVED | Tác nhân kinh doanh chênh lệch giá của mô hình làm giảm độ lệch giá còn lại nhưng không xóa tác động giá tức thời của cùng lần bán. | Price teleportation; not funded Mainnet execution. |
| INT:CL_INT_RQ5_PRESERVED | Định giá nợ USDC làm thay đổi HF khi giữ các yếu tố khác cố định; số token USDC và USD-equivalent phải tách biệt. | No liquidity/redemption/settlement channel. |
| INT:CL_INT_RQ6_PRESERVED | LTV, liquidation threshold và liquidation bonus chi phối các cơ chế khác nhau và không thể dùng thay thế nhau. | No borrower behavior/re-underwriting response. |
| INT:CL_INT_HISTORICAL_TIERS_PRESERVED | Cửa sổ lịch sử ghi nhận 28 Pool events, 27 Graph-matched và các tầng liên hệ 1/2/23/1. | Co-occurrence/receipt route does not prove price causality or endogenous cascade. |
| INT:CL_INT_TERRA_NEGATIVE_PRESERVED | Đánh giá cảnh báo cutoff-safe của Terra không hỗ trợ kết luận dự báo ngoài mẫu thành công. | No successful out-of-sample forecasting claim. |


Các required limitations về historicalstatic reconstruction/replay trong records là inherited evidence. Chương7 không báo lại các con số đó như actualrun của Work; chúng được giữ trong bảng để không cắt mất hợp đồng nguồn.

## 2. Six-RQ synthesis contract và original questions

T7.1 dùng nguyên full_original_research_question, accepted-only supporting sets và qualitative answer được phép. Cột answer diễn đạt tổng hợp, không tự tăng cấp độ bằng chứng hoặc thay accepted conclusion. Toàn bộ sáu câu hỏi được chép đúng một lần trong bảng main; prose thảo luận theoRQ, không đổi thứ tự hoặc thêmRQ7.

| RQ | Full original question | Accepted integration support IDs | Recommended conclusion from registry | Required RQ limitation |
| --- | --- | --- | --- | --- |
| RQ1 | Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)? | CL_INT_RQ1_POLICY_CONDITIONAL | Thanh lý dây chuyền depth 2 tồn tại trong mô hình ở tail stress dưới chính sách định giá cụ thể, nhưng không bền với mọi chính sách oracle đã thử. | 280/10.000 chỉ là tần suất Severe Policy A; 10 paths được chọn có chủ đích; không có depth ≥3 trong bộ khóa. |
| RQ2 | Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt? | CL_INT_RQ2_TWO_CHANNELS | Thanh khoản yếu khuếch đại biến dạng DEX, còn chuyển biến đó sang HF và depth phụ thuộc chính sách định giá. | Một pool, thanh khoản tĩnh/counterfactual, không routing đa venue và không xác minh feed lịch sử. |
| RQ3 | Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý? | CL_INT_ELIGIBLE_NOT_EXECUTED, CL_INT_RQ3_PRESERVED | Trong miền thử, các mức vốn thấp ràng buộc thanh lý. Trong tập đối chiếu mục tiêu, 36 trường hợp mới đủ điều kiện theo HF danh mục bị bỏ qua do không có khoản nợ USDC thuộc tuyến thanh lý WETH/USDC được mô hình hóa. Đây là các borrower-case-policy instances; điều kiện HF danh mục khác điều kiện thực thi theo tuyến. | Một liquidator đại diện, vốn không recycle, không fork execution và route mô hình chỉ WETH/USDC. |
| RQ4 | Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi? | CL_INT_RQ4_PRESERVED | Tác nhân kinh doanh chênh lệch giá của mô hình làm giảm độ lệch giá còn lại sau bán bắt buộc nhưng không xóa tác động giá tức thời của lần thực thi. | Price teleportation, một arbitrageur, không cạnh tranh/latency/gas strategy hoặc SwapRouter fork. |
| RQ5 | Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset? | CL_INT_RQ5_PRESERVED | Giá USD của nợ USDC thay đổi HF trong kênh định giá cô lập, không đại diện toàn bộ cơ chế depeg. | Ceteris paribus debt valuation; không có kênh redemption/liquidity/settlement. |
| RQ6 | Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk? | CL_INT_RQ6_PRESERVED | LTV điều tiết giới hạn vay ban đầu, ngưỡng thanh lý điều tiết HF và điều kiện thanh lý, còn thưởng thanh lý điều tiết khuyến khích và lượng tài sản thế chấp chuyển giao. | Frozen cohort; không borrower behavior hoặc re-underwriting response. |


Nguồn: [data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json). Field disallowed_or_superseded_claim_ids chỉ là audit trail; không được union vào accepted support sets.

## 3. Scholarly citation scope và access labels

15exactAPAentries được kế thừa từ P2, không new DOI/URL hoặc source research. Access labels dưới đây là labels đã khóa, không có lượt tải lại/đọcfulltext paper trong khi viếtCh7. S17/S18 cùngstudy; S22lànguồnthựchành, khôngpeerreview. S19/S23/S24 và những source đi kèm một claim nhưng không được cite trong body không bị mô tả như đã dùng toànvăn; Ch7 chỉ tổng hợp project components và giới hạn có locator riêng khi liên quan.

| S ID | APA identity | Citation scope | Locked verification/access label |
| --- | --- | --- | --- |
| S03 | Aave. (n.d.-b). *Health factor & liquidations*. Retrieved October 13, 2026, from https://aave.dev/help/borrowing/liquidations | HF/điều kiện thanh lý ởRQ3; không chứng nhận route planner | VERIFIED_CONTENT: HF và nhánh close factor trên trang trợ giúp |
| S04 | Aave. (n.d.-d). *Reserve*. Retrieved October 13, 2026, from https://www.aave.com/docs/aave-v3/concepts/reserve | Vai trò khác nhau LTV/LT/bonus ởRQ6 | VERIFIED_CONTENT: định nghĩa LTV/LT; tham số thay đổi theo thị trường/thời điểm |
| S05 | Aave. (n.d.-c). *Oracles*. Retrieved October 13, 2026, from https://aave.com/docs/aave-v3/smart-contracts/oracles | Oracle architecture/context; không xác nhận historical A/B/C | VERIFIED_CONTENT: API nguồn giá, không xác nhận feed tại block nghiên cứu |
| S07 | Adams, H., Zinsmeister, N., Salem, M., Keefer, R., & Robinson, D. (2021). *Uniswap v3 core* [White paper]. Uniswap. https://blog.uniswap.org/whitepaper-v3.pdf | Concentrated liquidity/sức hấp thụ DEX, không verify engine | VERIFIED_CONTENT: PDF gốc; không phân loại peer reviewed |
| S10 | Lehar, A., & Parlour, C. A. (2022). *Systemic fragility in decentralised markets* (BIS Working Papers No. 1062). Bank for International Settlements. https://www.bis.org/publications/working-paper-1062-systemic-fragility-decentralised-markets | Fire-sale/priceimpact motivation; không lấy hệ số/cỡmẫu chưa kiểm | VERIFIED_ABSTRACT: trang BIS đọc được; chưa kiểm từng bảng/ước lượng; không gán DOI |
| S11 | Sasi-Brodesky, A., & Kaousar Nassr, I. (2023). *DeFi liquidations: Volatility and liquidity* (OECD Working Papers on Finance, Insurance and Private Pensions No. 48). OECD Publishing. https://doi.org/10.1787/0524faaf-en | Liquidation/volatility association; không causalvalidation của DeFiStress | VERIFIED_CONTENT: PDF và trang OECD; DOI khớp nhà xuất bản; resolver trực tiếp không truy cập được |
| S12 | Tian, P., & Zhu, Y. (2025). *Liquidation mechanisms and price impacts in DeFi* (Staff Working Paper 2025-12). Bank of Canada. https://doi.org/10.34989/swp-2025-12 | Design/participationcost context; không Aave auction/bonusoptimum | VERIFIED_ABSTRACT: nguồn phát hành; không suy diễn Aave dùng đấu giá |
| S13 | Chiu, J., & Danisman, F. (2026). *DeFi lending: Returns, leverage, and liquidation risk* (Staff Analytical Paper 2026-13). Bank of Canada. https://doi.org/10.34989/sap-2026-13 | Persistent-price-effect null theo thiết kế riêng, không universal safety hoặc refutedbyWave2 | VERIFIED_CONTENT: PDF gốc và DOI nhà phát hành; resolver trực tiếp không truy cập được |
| S14 | Lyons, R. K., & Viswanath-Natraj, G. (2023). What keeps stablecoins stable? *Journal of International Money and Finance, 131*, Article 102777. https://doi.org/10.1016/j.jimonfin.2022.102777 | Arbitrage/access theo abstract; không Tether coefficients áp WETH | VERIFIED_ABSTRACT: bản công bố và kho tác giả khớp; không suy rộng hệ số Tether sang USDC |
| S15 | Kosse, A., Glowka, M., Mattei, I., & Rice, T. (2023). *Will the real stablecoin please stand up?* (BIS Papers No. 141). Bank for International Settlements. https://www.bis.org/publications/paper-141-will-real-stablecoin-please-stand-up | Stablecoin stability/convertibility widerchannels, không fulltext hoặc full-depeg validation | VERIFIED_ABSTRACT/METADATA: tác giả cá nhân, không phải CPMI là tác giả; không gán DOI |
| S17 | Liu, J., Makarov, I., & Schoar, A. (2026). Anatomy of a run: The Terra Luna crash. *Journal of Financial Economics, 184*, Article 104359. https://doi.org/10.1016/j.jfineco.2026.104359 | Terra run/background, abstract-only; không tham sốAave hoặc forecastcertificate | VERIFIED_ABSTRACT: bản ghi nhà xuất bản truy hồi được khi tìm kiếm; lần mở trực tiếp thất bại; không tuyên bố đọc toàn văn JFE |
| S18 | Liu, J., Makarov, I., & Schoar, A. (2023). *Anatomy of a run: The Terra Luna crash* (NBER Working Paper No. 31160). National Bureau of Economic Research. https://doi.org/10.3386/w31160 | Tiền nhiệm cùngstudyS17; không independent evidence | VERIFIED_ABSTRACT_INDEXED: bản ghi NBER; cùng nghiên cứu S17, không phải chứng cứ độc lập thứ hai |
| S20 | Axtell, R. L., & Farmer, J. D. (2025). Agent-based modeling in economics and finance: Past, present, and future. *Journal of Economic Literature, 63*(1), 197–287. https://doi.org/10.1257/jel.20221319 | ABM conceptual background ởabstract; không xác nhận code DeFiStress | VERIFIED_ABSTRACT: AEA và kho tác giả Oxford; không xác nhận engine DeFiStress |
| S21 | Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Milles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation, 23*(2), Article 7. https://doi.org/10.18564/jasss.4259 | ODD clarity/scheduling/submodels; không chứng nhận compliance đầy đủ | VERIFIED_CONTENT: toàn văn mở; DOI chuyển đúng tới bài |
| S22 | Gauntlet. (2021, January 15). *Gauntlet market risk primer* [Forum post]. Aave Governance. https://governance.aave.com/t/gauntlet-market-risk-primer/2097 | Practitioner simulation context, không peerreview, complete spec hoặc superioritybenchmark | VERIFIED_CONTENT: bài wfu đăng thay mặt Gauntlet; không phải peer review hoặc đặc tả tái lập đầy đủ |


Nguồn: [docs/research_final/APA_REFERENCES_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/APA_REFERENCES_VERIFIED.md); [docs/research_final/REFERENCE_EVIDENCE_MATRIX.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/REFERENCE_EVIDENCE_MATRIX.md); [docs/research_final/LITERATURE_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LITERATURE_VERIFIED.md). U01–U08 không nâng cấp hoặc dùng như verified literature.

## 4. Cross-chapter reconciliation

| Locked chapter | Read version | Function retained in Ch07 | Boundary |
| --- | --- | --- | --- |
| Ch01 | [docs/manuscript_p3/work/chapter_01/CHAPTER_01_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_01/CHAPTER_01_FULL_DRAFT_v1.md) | Mục tiêu đánh giá cơ chế, thiết kế6RQ, đóng góp tích hợp/truyvết | 7.5 không thêm mục tiêu dự báo/productproduction |
| Ch02 | [docs/manuscript_p3/work/chapter_02/CHAPTER_02_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_02/CHAPTER_02_FULL_DRAFT_v1.md) | Lý thuyết/citation và đối thoại khácdesign/horizon | S10/S11/S13 không bị gộp thành một causal law |
| Ch03 | [docs/manuscript_p3/work/chapter_03/CHAPTER_03_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_03/CHAPTER_03_FULL_DRAFT_v1.md) | Policy/timing/gates và định nghĩa chỉ tiêu | Không viết lại equations hoặc thêm agents/code mechanisms |
| Ch04 | [docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md) | 454/109,source lineage,verification≠economicvalidation | Không nâng Quoter/hash thành fundedexecution/fullmarketvalidation |
| Ch05 | [docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md) | SixRQ results,policydependence,eligible/executed,token/USD,LTV/LT/bonus | RQ6LTV255;LTUSD atq1,noinvented109denominator |
| Ch06 | [docs/manuscript_p3/work/chapter_06/CHAPTER_06_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_06/CHAPTER_06_FULL_DRAFT_v1.md) | 28/27,tiers1/2/23/1,Terra negative,graphaggregation | Khônghistcausal,forecastsupported hoặcfullmultilayer/DebtRank |


Sáu file được truy xuất toàn văn đúng integration, với blobidentities trong ledger. Bảnthảo1–6 đã được viết/đối chiếu ở các lượt trước; lượt này kiểm lại nội dung và cách các kết luận đi vào synthesis, không gọi đó là một đợt external validation mới. Không dùng attachments DOCX/PDF/PPTX làm nguồn ưu tiên và không mở lại chúng trong lượtCh7.

## 5. Numeric references và version precedence

Ch7 chủ yếu dùng synthesis định tính. Những số được nhắc trong văn xuôi dưới đây có cùng nghĩa/đơnvị/mẫusố với chương đã khóa; không tính lại thống kê hoặc gán scientific resultID mới. Các bảng T7.1/T7.2 không chứa bảng dữ liệu mô phỏng mới.

| Location | Existing value | Unit/cohort/policy | Result/source selector | Read locator |
| --- | --- | --- | --- | --- |
| 7.1.1/RQ1 | −40%;haircut90%/95% | Observed minimum shock magnitude among depth2cells of extended grid underA; không cutoff đơn điệu | Ch05§5.1.1/F5.1; RQ1_GRID60_DEPTH2; rawgrid source được Ch05 trích | [docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md) |
| 7.1.1/RQ3 | 36 | borrower-case-policy instances skipped for NO_MODELLED_USDC_DEBT,khônguniquewallets | CL_INT_ELIGIBLE_NOT_EXECUTED;Ch05T5.2;rawreasonNOT_ELIGIBLE làengineoutput | [docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md) |
| 7.1.1/RQ6 | 255vs109;USDC/USD=1 | LTVscope255WETH-positiveindebtedportfolios;109route riêng;LTportfolioUSD,nofixed109denominator | Chapter-specific versioned interpretation note;NOT reissuedScientificLock | [docs/manuscript_p3/work/chapter_05/CHAPTER_05_RESULT_CLAIM_CITATION_AUDIT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_05/CHAPTER_05_RESULT_CLAIM_CITATION_AUDIT_v1.md) |
| 7.2.3;7.3.2 | 0HIGHhours;lead−45hours | Derivedcutoff-safe earlywarning,notforecastsuccess; preinitialdenominator1630hours retained inCh06 | TERRA_PRE_DEPEG_HIGH_ALERT_HOURS;TERRA_INITIAL_DEPEG_HIGH_LEAD | [data/processed/research_final/frozen_v3/tables/terra_limitations.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/terra_limitations.csv) |
| 7.3.1 | block26045352;454;109 | Onecanonicalblock;verifiedportfolios454,routecohort109;notallAave | Ch04§4.1;Ch03§3.1.1 | [docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md) |
| 7.3.1 | 90%/95% | Extreme counterfactual haircuts; notobservedwithdrawalhistory | Ch05§5.1.1/5.2.1 | [docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md) |
| 7.3.2 | 280/10000 | SeverePolicyA paths,notmarketcrisisprobability; noobserveddepth>=3 inlockedtestedset | RQ1_MC_SEVERE_DEPTH2_COUNT;RQ1_MC_SEVERE_DEPTH3_COUNT;FrozenMCrowactual_runs10000/seed20260914 | [data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv) |
| 7.3.2 | 10targetedpaths | SelectedforAdepth2,notnewprobabilitysample;nestedprefixesnotindependent | Oraclepolicy_summary selected_mc_depth2_count_of_10;selectionreportedCh05 | [data/processed/research_final/oracle_transmission_diagnostic_v1/policy_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/oracle_transmission_diagnostic_v1/policy_summary.csv) |
| 7.3.2 | 28/27;tiers1/2/23/1 | LiquidationCallevents;tiersdenominator27;RPC-onlynotautoassignedtier | HIST_RPC_CENSUS_EVENTS,HIST_GRAPH_MATCHED_EVENTS,HIST_DIRECT_TRANSFER_PATHS,HIST_SAME_TX_COOCCURRENCE,HIST_SAME_BLOCK_ASSOCIATION,HIST_TIME_WINDOW_ASSOCIATION | [data/processed/research_final/frozen_v3/tables/historical_evidence.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/historical_evidence.csv) |


**RQ6 precedence inherited unchanged:** [docs/manuscript_p3/work/chapter_05/CHAPTER_05_RESULT_CLAIM_CITATION_AUDIT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_05/CHAPTER_05_RESULT_CLAIM_CITATION_AUDIT_v1.md) retains [Commander16/10/2026decision](https://github.com/Doquocdung1609/DeFiStress/pull/21#issuecomment-6214848952). Frozen LTVresults still carry legacypopulation109; detailedartifact declarescohort255. Frozen LTlabels `USDC token quantity` are legacy; actualmetric isportfolioUSD atUSDC/USD=1 and population follows passedposition set. Ch7 uses effective manuscript interpretation and does not alter/certify Frozen metadata or declare a newlock. No numerical endpoint values are repeated tocreate a secondRQ6table.

| Source | Selector | Scoped check |
| --- | --- | --- |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.json) | cohort_size;method;rows.aggregate_max_borrowing_capacity_usd | cohort255;WETHpositive+debt,notUSDC-only route |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json) | rows.usdc_price_usd;unliquidated_debt | allq1;notnewUSDC-tokenquantityclaim |


## 6. Exhibit contract — textual synthesis only

### T7.1 — section7.1;handoffP3X-T7.1

- Academic purpose: Tổng hợp kết luận, không nhân bản toàn bộ bảng kết quả.
- Related accepted IDs: INT:CL_INT_RQ1_POLICY_CONDITIONAL, INT:CL_INT_RQ2_TWO_CHANNELS, INT:CL_INT_RQ3_PRESERVED, INT:CL_INT_RQ4_PRESERVED, INT:CL_INT_RQ5_PRESERVED, INT:CL_INT_RQ6_PRESERVED.
- Units: không đơn vị.
- Denominator: Six original RQs; accepted-only support sets.
- Approved mapping status: `DIRECT_LOCKED_SOURCE`;actual production: `WORK_MARKDOWN_COMPLETE`.
- No numerical Codex template required; no newfigure/equationID.
- Required caption controls: Tóm lược sáu accepted RQ answers cùng policy, cohort và giới hạn. Bốn excluded records không thuộc affirmative findings. Điều kiện hiển thị: Exclude all four disallowed records and preserve each RQ limitation.

| Path | Source commit | Selector | Gitblob |
| --- | --- | --- | --- |
| [data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json) | 3f6e5302483681209e2408531eb5a15389f9fded | research_questions[]; preserve full original questions and accepted-only claim sets | fffe69d45f2c70e8f4cb781c8b521ef4cf6f1a45 |


Fields: RQ,fulloriginalquestion,accepted qualitativeanswer,evidence/conditions. Sixrows in sourceRQorder, no new numerical table. Each answer retains valuationpolicy/route/cohort/measurement qualifier; fourdisallowed cannot enter affirmativesets. Exact typed supportingreferences remain separate from accepted-only IDs.

### T7.2 — section7.2;handoffP3X-T7.2

- Academic purpose: Thể hiện đóng góp tích hợp/truy vết thay claims ưu việt phổ quát.
- Related accepted IDs: P2:C17, P2:C31, INT:CL_INT_ELIGIBLE_NOT_EXECUTED, INT:CL_INT_TERRA_NEGATIVE_PRESERVED.
- Units: không đơn vị.
- Denominator: NOT_APPLICABLE_ACADEMIC_SYNTHESIS;44acceptedcandidates are source scope,not statisticalsample.
- Approved mapping status: `DIRECT_LOCKED_SOURCE`;actual production: `WORK_MARKDOWN_COMPLETE`.
- No numerical Codex template required; no newfigure/equationID.
- Required caption controls: Đóng góp tích hợp, đối chiếu và truy vết trong phạm vi đề tài; không first-ever, calibrated live-risk prescription hoặc phát hiện định lượng mới. Điều kiện hiển thị: No first-ever, calibrated live-risk advice or stronger external validity claim.

| Path | Source commit | Selector | Gitblob |
| --- | --- | --- | --- |
| [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | records filtered by registry_id in P2:C17,P2:C31,INT:CL_INT_ELIGIBLE_NOT_EXECUTED,INT:CL_INT_TERRA_NEGATIVE_PRESERVED | bac44e61633b5efdde3665731ea69fbf4ca345e6 |
| [docs/research_final/LITERATURE_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LITERATURE_VERIFIED.md) | 3f6e5302483681209e2408531eb5a15389f9fded | Declared locked artifact for T7.2; Codex must pin extraction selector before rendering; no new statistic. | 6ebe0a11e915e942a422d02a0cc5b1d53b51ff3e |


Fields: contributionaspect,implementedcontent,projectbasis,defensiblescope. Fiverows:integration;policy stresscomparison;executionlayers;provenance;negative/historical evidence. No contribution score,first-everclaim,liveoperatingthreshold or common statistical denominator. Renderingowner is Work textual Markdown inthisstage;noCodexownedfilesedited or numericalrenderingtaskopened.

## 7. Mandatory limitations L01–L14 coverage

| Limit ID | Original locked limitation | Main location |
| --- | --- | --- |
| L01 | Kết quả cascade là mô phỏng phản thực có điều kiện theo policy, cohort và cấu hình thanh khoản; A/B/C chưa được xác minh là feed Aave/Chainlink lịch sử. | 7.1.1/RQ1–2;7.3.1 |
| L02 | Một block 26045352, 454 verified borrowers; 109 là cohort WETH-collateral-enabled/USDC-debt riêng; một Uniswap venue, không đại diện toàn thị trường. | 7.1.1/RQ6;7.3.1 |
| L03 | Phân biệt HF danh mục mới dưới 1, engine evaluation, route eligibility và execution có debt repaid dương; đếm borrower-case-policy instances, không unique wallets. | 7.1.1/RQ3;7.2.2;7.4.1 |
| L04 | 280/10.000 chỉ Severe Policy A; mười targeted MC paths chọn theo A-depth2; không ước lượng xác suất thị trường, không suy không thể có depth≥3 ngoài tập thử. | 7.3.2 |
| L05 | Liquidator/arbitrageur đại diện; vốn không recycle, kế hoạch vượt vốn không tự chia nhỏ; kết quả gas/capacity/delay chỉ trong miền thử. | 7.1.1/RQ3;7.3.1 |
| L06 | Arbitrage là price repositioning, chưa funded executable swap; tác động giá tức thời khác spread sau arbitrage. | 7.1.1/RQ4;7.3.1 |
| L07 | RQ5 chỉ kênh định giá nợ USDC; token quantity khác USD-equivalent; chưa redemption/liquidity/confidence/settlement đầy đủ. | 7.1.1/RQ5;7.3.1 |
| L08 | Haircut 90/95% là extreme counterfactual tails, chưa có bằng chứng lịch sử tương ứng; không có independent local-fork execution được kiểm chứng. | 7.3.1 |
| L09 | 28 Pool events/27 Graph matches và tiers 1/2/23/1 chỉ theo cửa sổ đã khai báo; receipt route và đồng xuất hiện không xác lập lây lan nhân quả. | 7.2.3;7.3.2 |
| L10 | Terra tái dựng hồi cứu khác dự báo; giữ HIGH trước initial depeg bằng 0, lead −45 giờ và kết luận âm ngoài mẫu; không dùng Terra xác nhận tham số Aave. | 7.1.1/RQ5;7.2.3;7.3.2 |
| L11 | Graph typed/aggregated và centrality cấu trúc chưa là full multilayer contagion, DebtRank đã triển khai hoặc xếp hạng rủi ro toàn DeFi. | 7.3.2;7.4.2 |
| L12 | Modeled bad debt/composite tail exposure khác realized financial loss hoặc market expected shortfall; debt repaid không phải loss. | 7.3.1 |
| L13 | Hai raw borrower CSV lớn vẫn chưa được Work đọc đầy đủ/cell-by-cell; giữ source access labels, U01–U08 và mức abstract/metadata/code; S17/S18 cùng nghiên cứu. | 7.2.3;7.3.2 |
| L14 | Git LF blob bytes khác Windows CRLF checkout bytes; kết quả kiểm thử do Codex báo cáo khác lượt Work tự chạy; không đồng nhất hash domains. | 7.3.2 |


Sourceaccesslimitations đặt đúng chỗ: main không gắn sourceID thay author–year, không yêu cầu conceptualclaim phải numerical; contributionyêu cầu bằngchứngprojectthực hiện chứkhôngmượn uy tín literature. Lời đềxuấtở7.4 làfuturework/researchimplication,không thao tác đã làm hoặc riskparameters đượccalibratelive.

## 8. Excluded-claim safeguard

| Registry ID | Locked disposition | Main discussion / allowed use |
| --- | --- | --- |
| INT:CL_FROZEN_RQ1_UNQUALIFIED_WORDING | REJECTED_AS_WORDED_SUPERSEDED | 7.3.3: discussion of rejected reasoning only; notacceptedaffirmativefinding |
| INT:CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING | REJECTED_AS_WORDED_SUPERSEDED | 7.3.3: discussion of rejected reasoning only; notacceptedaffirmativefinding |
| INT:CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT | UNSUPPORTED | 7.3.3: discussion of rejected reasoning only; notacceptedaffirmativefinding |
| INT:CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION | UNSUPPORTED | 7.3.3: discussion of rejected reasoning only; notacceptedaffirmativefinding |


Bốn records vẫn có trong registry/audit trail. 7.3.3 giải thích điều kiện bị lược hoặc nhận định chưa được hỗ trợ; không đưa ID của chúng vào T7.1 accepted sets. Giữ lịch sử chỉnh sửa khác việc tái khẳng định claim. Các kết luận hiện hành không tái tạo overclaim tương đương bằng wording khác.

## 9. Targeted authoring review and repair log

| Finding | Risk/location | Repair | Recheck |
| --- | --- | --- | --- |
| CH07-R01 | RQ1minimum question could become vague policy caveat only | Add observed−40%/90–95% condition fromCh05,retainnonuniversal/nonmonotonic reading | PASS; no newthresholdestimate |
| CH07-R02 | RQ6legacyFrozenunit/cohort could resurface in conclusion | InheritChapter5Commanderinterpretation:LTV255≠109route;LTportfolioUSD atq1,nofixed109denominator | PASS; noFrozenmutation |
| CH07-R03 | T7.1could paraphrase originalRQ whileclaimingverbatim | Copy sixfullquestions and preserveorderedacceptedsets | PASS; exactstringcheck |
| CH07-R04 | Contributioncould be first-ever/superiority/productclaim | CompareABM/ODD/Gauntlet context;projectimplementationevidence separatefrompapers | PASS; scopedintegration/tracing only |
| CH07-R05 | Ch7could repeat numericalchapter or dilute primaryallocation | Only selectedanchors;no numericplots;primary1C17and32secondaryreferences | PASS; noallocationorpriorchapteredits |
| CH07-R06 | Literaturedesign difference could be framed as empiricalcontradiction | 7.1.2distinguishespricehorizon/benchmark/stresspolicy;S13notrefutedbyWave2 | PASS |
| CH07-R07 | Negativefindings/sourcegaps could be hiddenbyfinalconclusion | RetainTerra0HIGH/−45h,historicaltiers,graphlimits andrawCSVaccess | PASS; noforecastsupported/causalclaim |


## 10. Actual verification and remaining scope

Lệnh thực tế: `python verify_chapter07.py` — exit0/PASS sau targeted repairs. Static source/contentchecker ở phiên làm việc,khôngcommitthànhfilethứtư. Kiểm5sections/12subsections,6RQverbatim,1/1primaryC17+32secondary,33acceptedcomponents,2MarkdownTables,15APAentries,14limitationsand4disallowedguards. Đối chiếu sourceidentities và số nhắc lại qua locators;không tính lại modeloutput hoặc newstatisticaltest.

Không simulation/MonteCarlo/retuning/HFrecalculation/fullregression/RPC hoặc NetworkXrun. Ch7 đọc cácfile nguồn nhỏ,registry,report và sáu chương;khôngrawcellre-audit. Hai borrowerCSVs Oracle8.775.089bytes vàIntegration18.489.195bytes vẫn chưa được Workđọcđầyđủ. Rawhistoricalcensus/swapgzip,Terra parquet/fulltrajectories không được rà lại toàn bộ. CODEX_REPLAY_VERIFICATION/CODEX_PREMERGE_AUDIT và P2WORK_INDEPENDENT_STATIC_RECONSTRUCTION là inherited verification,khôngactualnewWorkrun. FinalCrossPRreview/manifestoldstatuslàhistory,khôngthayquyếtđịnhScientificLock.

Hashledger dùngSHA1Gitblob/LFdomain;localcachetext có thêmterminalLF chỉ được bỏ khỏicomparison khi exactblobkhớp. GitLFbytes khácWindowsCRLFcheckoutbytes/SHA256;khônggọi haihashkhácnhau cùngSHA. Blobmatchingxácnhậnidentity,khôngeconomicvalidation.

Không thêmscholarlysources hoặc nângaccesslabels. U01–U08 và92thuậtngữ giữ nguồnnguyêntrạng;citation15sources nằm trongS01–S30. Cácattachments không được đọc lạitronglượtCh7/khônglàmnguồnsố. TEMPLATE_VERIFICATION_PENDING giữ choformattingcuối;APAtạmthờikhôngđượctựgánlàquyđịnhriêngcủatrường. T7.1/T7.2 làMarkdownhoànchỉnh,khôngcófigurependingcủaCh7;figurespecscácchươngtrướckhôngđượcgọiđãrender.

NoP0/P1sourceconflict found trongphạmvinguồnđượcsửdụng sau kếthừanoteCh5. Đây là self-reviewcủaWork,khôngindependentexternalreview hoặc tựchứngnhậnscientificlock. Chưa assembly/DOCX/merge hoặc ChapterLock.

## 11. Source-read ledger

| Path | Exact read commit | Gitblob SHA |
| --- | --- | --- |
| [docs/research_final/APA_REFERENCES_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/APA_REFERENCES_VERIFIED.md) | 3f6e5302483681209e2408531eb5a15389f9fded | c76d7cf482565615a92fb17b888a392e4f8fd9cc |
| [docs/manuscript_p3/work/P3_CHAPTER_ACCEPTANCE_RUBRIC.md](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_CHAPTER_ACCEPTANCE_RUBRIC.md) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 753b40a123677ddda25a178957ed6cc8a55b2c16 |
| [docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_05/CHAPTER_05_FULL_DRAFT_v1.md) | f5f9c338a3a38ec07b3a21ba5cdc29749daf9833 | 9be3495921243ad5980177071a7a8cd8370e1ce2 |
| [data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json) | 3f6e5302483681209e2408531eb5a15389f9fded | fffe69d45f2c70e8f4cb781c8b521ef4cf6f1a45 |
| [data/processed/research_final/final_accepted_claims_v1/manifest.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/manifest.json) | 3f6e5302483681209e2408531eb5a15389f9fded | bad223e0859a4fe135dd4f7b48b78513ade88123 |
| [data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/source_provenance_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | a6784fd7f1b7288c4f2177ff8ba102be5e01c81e |
| [docs/research_final/LITERATURE_VERIFIED.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LITERATURE_VERIFIED.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 6ebe0a11e915e942a422d02a0cc5b1d53b51ff3e |
| [docs/manuscript_p3/work/chapter_03/CHAPTER_03_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_03/CHAPTER_03_FULL_DRAFT_v1.md) | f5f9c338a3a38ec07b3a21ba5cdc29749daf9833 | f8609f120d6f8e1fa9bb3aa9393fe45092888439 |
| [docs/manuscript_p3/work/P3_MANUSCRIPT_BLUEPRINT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_MANUSCRIPT_BLUEPRINT_v1.md) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 10194e95b67a360cadd7ab2eb9550deac206e672 |
| [docs/manuscript_p3/work/chapter_02/CHAPTER_02_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_02/CHAPTER_02_FULL_DRAFT_v1.md) | f5f9c338a3a38ec07b3a21ba5cdc29749daf9833 | b73f337c99cdf6a137fac4d54e9b49b1aebb3a40 |
| [docs/manuscript_p3/work/chapter_01/CHAPTER_01_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_01/CHAPTER_01_FULL_DRAFT_v1.md) | f5f9c338a3a38ec07b3a21ba5cdc29749daf9833 | c3fffec83f427c52c595dd02fd73a9c81db5cfcd |
| [docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_04/CHAPTER_04_FULL_DRAFT_v1.md) | f5f9c338a3a38ec07b3a21ba5cdc29749daf9833 | 5fe370a245e11a6ae9a7f2cc6349dc30d97893a2 |
| [docs/research_final/TERMINOLOGY_VI.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/TERMINOLOGY_VI.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 2ca1e29495e6183dfefaf8939e59e6c4eba574fb |
| [docs/manuscript_p3/work/chapter_06/CHAPTER_06_FULL_DRAFT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_06/CHAPTER_06_FULL_DRAFT_v1.md) | f5f9c338a3a38ec07b3a21ba5cdc29749daf9833 | 342accacd1441eb228ac672a5fe7625ee7514a09 |
| [data/processed/research_final/frozen_v3/results_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/results_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 6dde91fc11d189de8899c742b44fea9cf0f386ae |
| [data/processed/research_final/final_accepted_claims_v1/claim_evidence_crosswalk.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/claim_evidence_crosswalk.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 312b72f23b0115d1de69eec2dc1a87b0f490070a |
| [docs/manuscript_p3/work/P3_G0_WORK_CODEX_EXHIBIT_CROSSWALK.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_G0_WORK_CODEX_EXHIBIT_CROSSWALK.json) | 8de52bebabef376be700836e6f93a92d7394d2c3 | 27475694e8e94ae4f6dd16bfdb76a956ba080877 |
| [docs/research_final/REFERENCE_EVIDENCE_MATRIX.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/REFERENCE_EVIDENCE_MATRIX.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 504ea91b046e6612c2840c6a434e740ce917b29f |
| [docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json) | 8de52bebabef376be700836e6f93a92d7394d2c3 | e10159ba8659c4dc6b528a7da645d4a20f39a9aa |
| [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | bac44e61633b5efdde3665731ea69fbf4ca345e6 |
| [docs/research_final/FINAL_CROSS_PR_CONSISTENCY_REVIEW.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/FINAL_CROSS_PR_CONSISTENCY_REVIEW.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 7e54828a39e05f9e41e9d2b206bcfa0402a6fb7a |
| [data/processed/research_final/scientific_integration_v1/integration_result_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/integration_result_registry.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 64b78e13f87adcc9bcc70188ca692d4a4196bff1 |
| [docs/research_final/P2_ORACLE_RECONCILIATION.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/P2_ORACLE_RECONCILIATION.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 2bc140f47ea463a9394858ec8937a808d18eccd7 |
| [docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md) | 3f6e5302483681209e2408531eb5a15389f9fded | 856768b29fd0cefa5caba5d5721dc759f025cdba |
| [docs/manuscript_p3/work/chapter_05/CHAPTER_05_RESULT_CLAIM_CITATION_AUDIT_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/f5f9c338a3a38ec07b3a21ba5cdc29749daf9833/docs/manuscript_p3/work/chapter_05/CHAPTER_05_RESULT_CLAIM_CITATION_AUDIT_v1.md) | f5f9c338a3a38ec07b3a21ba5cdc29749daf9833 | 84b4f162510a17534b23d8ea224494fe32173b4c |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_ltv_capital_efficiency.json) | 3f6e5302483681209e2408531eb5a15389f9fded | a58c672cb123eccc0e64a040c37c636d1541698f |
| [data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/validation_audit/corrected_run_v2/rq_completion/rq6_liquidation_threshold.json) | 3f6e5302483681209e2408531eb5a15389f9fded | 603ca694a923bbe7872782d64779e96497fee3b9 |
| [data/processed/research_final/frozen_v3/tables/historical_evidence.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/historical_evidence.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | ea2d04143baee6a2d561b588bd8174b6dbfbc64b |
| [data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | ea71db6f633b7e5df1f12cd3d9f2533e5d5f9438 |
| [data/processed/research_final/oracle_transmission_diagnostic_v1/policy_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/oracle_transmission_diagnostic_v1/policy_summary.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | bc8a138a0d6c4b7ddce98379aec14a1f811c4d5b |
| [data/processed/research_final/frozen_v3/claim_ledger.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/claim_ledger.json) | 3f6e5302483681209e2408531eb5a15389f9fded | f8d095676f1a0e10b37206c851b4e229a5e563a1 |
| [data/processed/research_final/frozen_v3/tables/terra_limitations.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/frozen_v3/tables/terra_limitations.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 264d5294bd8da978f8718c15b9ca7bcb221c704b |
| [data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv) | 3f6e5302483681209e2408531eb5a15389f9fded | 664eeac6d3d80a38dc4c2ca6c942070f09d8d9f8 |


**Handoff: `CHAPTER_07_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`.** Commander quyếtđịnhreview/targetedrepair/merge/ChapterLock riêng;Ch7 không tự khóa bảy chương hoặc bắt đầu final assembly.
