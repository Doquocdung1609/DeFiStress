# CHAPTER_02_CLAIM_CITATION_AUDIT_v1

**Đề nghị:** `CHAPTER_02_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`. Không tự cấp Chapter Lock.

## 1. Ba source anchors và quyền thực hiện

- Scientific Content Lock: `3f6e5302483681209e2408531eb5a15389f9fded`; `final-accepted-claims-v1.1-targeted-repair`.
- Blueprint Lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Chapter 01 Lock và branch start: `88dbc4234378b5bbcc61b73700a0c5298f66225f`; [quyết định Commander](https://github.com/Doquocdung1609/DeFiStress/issues/3#issuecomment-6208965565) cấp `CHAPTER_02_FULL_DRAFT_AUTHORIZED`.
- Đã truy xuất 33 required/support repository files tại scientific/blueprint pins, toàn văn Ch1 tại Chapter01 Lock và hai implementation helpers Wilson bổ sung: **36 Git-source files**. Đọc phần liên quan của P2, registry, method/code để biên soạn; không tuyên đọc lại toàn văn bài gốc, không mở vòng nghiên cứu/kiểm toán engine.
- File directive tải lên được đọc trực tiếp từ scratch, không sửa. Bản DOCX cũ chỉ tham khảo phần Ch2/đối chiếu legacy, không là scientific source.
- Output commit ghi tại PR/handoff, tránh tự tham chiếu. Không sửa Ch1 hoặc các nguồn khóa.

## 2. Ánh xạ tiểu mục

| Tiểu mục | Accepted IDs | Source IDs | Luận điểm / model crosswalk | Giới hạn |
|---|---|---|---|---|
| 2.1.1 | P2:C01, P2:C02, P2:C03 | S01, S02, S03, S09 | HF, danh mục/tuyến và eligibility/execution; schema và liquidation planner | Nhiều tài sản/nguồn giá; code facts không là scholarly finding; không ghi counts. |
| 2.1.2 | P2:C04, P2:C05, P2:C06, P2:C12 | S04, S06, S09, S12 | LTV/LT/bonus/close factor và hành vi trên dư nợ cố định | Nguồn hiện hành/reference commit không chứng nhận bytecode lịch sử; không mặc định close factor cố định hoặc borrower response. |
| 2.1.3 | P2:C03, P2:C06, P2:C12, P2:C19 | S09, S12 | Động cơ, gas/vốn/capacity/delay; đại diện liquidator | S09/S12 chỉ abstract; không đấu giá Aave hoặc competition calibrated; không auto recycling/splitting. |
| 2.2.1 | P2:C07, P2:C08 | S07, S08 | Range/tick, TVL/active L/depth, token order/decimals | White paper/code khác peer-reviewed empirical evidence; haircut là phản thực; không whole-range xy=k. |
| 2.2.2 | P2:C07, P2:C08, P2:C09, P2:C10, P2:C11, P2:C32 | S05, S10, S11, S13 | Price impact/slippage; horizon/benchmark; oracle-policy transmission | A/B/C không historical feeds; S13 không bị model bác; không causal co-occurrence. |
| 2.2.3 | P2:C13, P2:C19, P2:C34 | S14 | Arbitrage access, immediate/residual và repositioning | Không chuyển hệ số Tether; code không funded swap/cạnh tranh nhiều bots. |
| 2.3.1 | P2:C13, P2:C14 | S14, S15, S16 | Vai trò bảng cân đối, market price/redemption/liquidity | S15 abstract/metadata; S16 issuer disclosure không independent audit. |
| 2.3.2 | P2:C15, P2:C16, P2:C17, P2:C35 | S02, S03, S17, S18 | USDC token/USD; other debt; Terra như case khác | Chỉ valuation; seize/dust/quote chưa repricing toàn diện; S17/S18 cùng study, abstract-only. |
| 2.4.1 | P2:C18, P2:C19, P2:C20, P2:C21 | S19, S20, S21, S22 | ABM/static/scenario, agents và ODD/code | Theory không calibration; forum không peer review; không chứng nhận mọi tiêu chí ODD. |
| 2.4.2 | P2:C22, P2:C23 | S23, S24 | MC sample/conditional uncertainty; Wilson; selected/prefix | S23 preview; S24 phân biệt tên method chứ không xác nhận code; không CI mới/market probability. |
| 2.4.3 | P2:C01, P2:C25, P2:C26, P2:C27, P2:C28 | S01, S25, S26, S27, S28, S29 | Node–layer/coupling, betweenness/DebtRank, aggregation/common shock | Chỉ structural extension; directed/unweighted là code fact; không systemic loss rank hoặc historical contagion. |
| 2.5.1 / T2.1 | P2:C06, P2:C07, P2:C09, P2:C10, P2:C11, P2:C12, P2:C13, P2:C14, P2:C16, P2:C18, P2:C20, P2:C21, P2:C22, P2:C23, P2:C25, P2:C27, P2:C28 | S07, S08, S09, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19, S20, S21, S22, S23, S24, S25, S26, S27, S28 | 12 nhánh đối thoại theo thiết kế/nguồn/horizon/access | Không sample size/coefficient mới; không đếm đôi JFE/NBER; không xếp forum/white paper là scholarly peer review. |
| 2.5.2 | P2:C09, P2:C10, P2:C11, P2:C31, P2:C32 | S10, S11, S13 | Comparability of estimands; modeled Wave2 khác empirical persistent impact | Chỉ nhận diện phạm vi, không báo số models/lịch sử/MC; temporal route không price causation. |
| 2.5.3 | P2:C02, P2:C03, P2:C04, P2:C07, P2:C18, P2:C20, P2:C31, P2:C32, P2:C35 | S21 | Dẫn xuất nhóm biến, giả định và distinction verification/validation/causality | Gap giới hạn bộ P2; không first-ever; không viết trước Ch3. |

## 3. Allocation và accepted gate

Không thay primary/secondary destinations. Có các nguồn được dẫn ở tầng định nghĩa hoặc giới hạn theo narrative Blueprint Ch2 và lệnh hiện tại; chúng không được chuyển thành primary Ch2. Bảng dưới chép nguyên allocation JSON. Nội dung đầy đủ về tham số/thuật toán ở Ch3, số liệu ở Ch5, lịch sử/Terra/network ở Ch6. Commander Ch1 Lock đã ghi nonblocking note về contextual references khác destination; áp dụng cùng nguyên tắc, không sửa source matrix để che khác biệt.

| Registry ID | Final gate | Primary | Secondary gốc | Primary evidence tier | Cách dùng |
|---|---|---:|---|---|---|
| P2:C01 | ACCEPTED | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE | Lý thuyết/literature theo primary Ch2 |
| P2:C02 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE | Lý thuyết/literature theo primary Ch2 |
| P2:C03 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Contextual definition/method/limitation; không empirical result |
| P2:C04 | ACCEPTED | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Lý thuyết/literature theo primary Ch2 |
| P2:C05 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C06 | ACCEPTED | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE | Lý thuyết/literature theo primary Ch2 |
| P2:C07 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Lý thuyết/literature theo primary Ch2 |
| P2:C08 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C09 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | MIXED_SCHOLARLY_ONCHAIN_AND_MODEL_CROSSWALK | Lý thuyết/literature theo primary Ch2 |
| P2:C10 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | MIXED_SCHOLARLY_ONCHAIN_AND_MODEL_CROSSWALK | Lý thuyết/literature theo primary Ch2 |
| P2:C11 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Lý thuyết/literature theo primary Ch2 |
| P2:C12 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Lý thuyết/literature theo primary Ch2 |
| P2:C13 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Lý thuyết/literature theo primary Ch2 |
| P2:C14 | ACCEPTED_WITH_LIMITATIONS | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE | Lý thuyết/literature theo primary Ch2 |
| P2:C15 | ACCEPTED_WITH_LIMITATIONS | 5 | 3, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Contextual definition/method/limitation; không empirical result |
| P2:C16 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C17 | ACCEPTED_WITH_LIMITATIONS | 7 | 1, 6 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C18 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C19 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION | Contextual definition/method/limitation; không empirical result |
| P2:C20 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C21 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C22 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Contextual definition/method/limitation; không empirical result |
| P2:C23 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK | Contextual definition/method/limitation; không empirical result |
| P2:C25 | ACCEPTED | 2 | 3, 4, 5, 7 | SCHOLARLY_SOURCE | Lý thuyết/literature theo primary Ch2 |
| P2:C26 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | CODE_OBSERVATION | Contextual definition/method/limitation; không empirical result |
| P2:C27 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C28 | ACCEPTED_WITH_LIMITATIONS | 6 | 2, 7 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C31 | ACCEPTED_WITH_LIMITATIONS | 1 | 2, 7 | SCHOLARLY_SOURCE | Contextual definition/method/limitation; không empirical result |
| P2:C32 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION_AND_MODEL_COMPUTED_COUNTERFACTUAL | Contextual definition/method/limitation; không empirical result |
| P2:C34 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION | Contextual definition/method/limitation; không empirical result |
| P2:C35 | ACCEPTED_WITH_LIMITATIONS | 3 | 4, 5, 7 | CODE_OBSERVATION_WITH_SCOPED_MODEL_LIMITATION | Contextual definition/method/limitation; không empirical result |

**31 accepted P2 records dùng ở cấp khái niệm/phương pháp/phạm vi**, gồm **12/12 primary Ch2 claims**. Không sử dụng Integration findings làm kết luận số học. 44 affirmative/4excluded,35+13records và sáu RQ giữ nguyên. Conceptual claims không bị buộc có numerical result.

## 4. Citation identities, source access và chức năng

Toàn chương có 29 source records S01–S29; đây không phải29 công trình scholarly độc lập. Bao gồm tài liệu giao thức, mã, white paper, forum, thông cáo, sách preview và hai phiên bản của cùng nghiên cứu Terra. Không dùng S30 vì Ch2 không triển khai kiểm định CV. U01–U08 không xuất hiện trong bibliography.

Nhãn dưới đây giữ nguyên P2; đọc hồ sơ không nâng thành `VERIFIED_FULLTEXT`. Các phát biểu trong T2.1 cũng giữ mức này.

| S ID | Citation identity theo APA | Access nguyên nhãn P2 | Vai trò trong chương |
|---|---|---|---|
| S01 | Schär, F. (2021). Decentralized finance: On blockchain- and smart contract-based financial markets | VERIFIED_CONTENT: trang tác giả/nhà xuất bản đọc được | 2.4.3: tính liên kết; không lặp định nghĩa DeFi ởCh1. |
| S02 | Aave. (n.d.-a) | VERIFIED_CONTENT: nội dung hiện hành; không xác nhận cấu hình lịch sử | 2.1.1: kiến trúc vay/HF; không config lịch sử. |
| S03 | Aave. (n.d.-b) | VERIFIED_CONTENT: HF và nhánh close factor trên trang trợ giúp | 2.1.1: HF/liquidation; không execution đã xảy ra. |
| S04 | Aave. (n.d.-d) | VERIFIED_CONTENT: định nghĩa LTV/LT; tham số thay đổi theo thị trường/thời điểm | 2.1.2: LTV/LT/reserve parameters. |
| S05 | Aave. (n.d.-c) | VERIFIED_CONTENT: API nguồn giá, không xác nhận feed tại block nghiên cứu | 2.2.2: source-price API; chưa historical oracle feed. |
| S06 | Aave DAO. (n.d.) | VERIFIED_CODE: commit đọc được; không phải xác minh bytecode triển khai tại block | 2.1.2: close-factor/dust theo reference code/version; không deployed bytecode. |
| S07 | Adams, H., Zinsmeister, N., Salem, M., Keefer, R., & Robinson, D. (2021) | VERIFIED_CONTENT: PDF gốc; không phân loại peer reviewed | 2.2.1/T2.1: range/ticks/active L; white paper, không empirical causal evidence. |
| S08 | Uniswap. (n.d.) | VERIFIED_CODE: mã chuẩn; bổ trợ https://developers.uniswap.org/docs/protocols/v3/concepts/architecture | 2.2.1/T2.1: SqrtPriceMath/rounding; không xác nhận funded swaps của dự án. |
| S09 | Qin, K., Zhou, L., Gamito, P., Jovanovic, P., & Gervais, A. (2021). An empirical study of DeFi liquidations: Incentives, risks, and instabilities. In *Proceedings of the 21st ACM Internet Measurement Conference* (pp. 336–350). Association for Computing Machinery. https://doi.org/10.1145/3487552.3487811 | VERIFIED_ABSTRACT: bản tác giả arXiv đọc được; DOI/venue khớp UCL; DOI trực tiếp 403 | 2.1.1/2.1.3/T2.1: incentive/risk; chỉ nội dung abstract đã duyệt. |
| S10 | Lehar, A., & Parlour, C. A. (2022) | VERIFIED_ABSTRACT: trang BIS đọc được; chưa kiểm từng bảng/ước lượng; không gán DOI | 2.2.2/2.5: collateral sale/impact; chưa dùng hệ số/bảng chưa đọc. |
| S11 | Sasi-Brodesky, A., & Kaousar Nassr, I. (2023) | VERIFIED_CONTENT: PDF và trang OECD; DOI khớp nhà xuất bản; resolver trực tiếp không truy cập được | 2.2.2/2.5: liquidation/volatility association; hành vi suy gián tiếp. |
| S12 | Tian, P., & Zhu, Y. (2025) | VERIFIED_ABSTRACT: nguồn phát hành; không suy diễn Aave dùng đấu giá | 2.1.2/2.1.3/T2.1: fixed spread/auction phụ thuộc cost; không Aave auction. |
| S13 | Chiu, J., & Danisman, F. (2026) | VERIFIED_CONTENT: PDF gốc và DOI nhà phát hành; resolver trực tiếp không truy cập được | 2.2.2/2.5: persistent-price-impact null theo benchmark; không bị mô hình bác bỏ. |
| S14 | Lyons, R. K., & Viswanath-Natraj, G. (2023). What keeps stablecoins stable? *Journal of International Money and Finance, 131*, Article 102777. https://doi.org/10.1016/j.jimonfin.2022.102777 | VERIFIED_ABSTRACT: bản công bố và kho tác giả khớp; không suy rộng hệ số Tether sang USDC | 2.2.3/2.3.1: arbitrage access/stablecoin; không transfer calibration Tether. |
| S15 | Kosse, A., Glowka, M., Mattei, I., & Rice, T. (2023) | VERIFIED_ABSTRACT/METADATA: tác giả cá nhân, không phải CPMI là tác giả; không gán DOI | 2.3.1: stability/redemption; giữ tác giả Kosse et al., không CPMI. |
| S16 | Circle. (2023, March 13) | VERIFIED_CONTENT: lời công bố của Circle, không phải kiểm toán độc lập | 2.3.1: issuer disclosure về reserve risk; không independent audit. |
| S17 | Liu, J., Makarov, I., & Schoar, A. (2026). Anatomy of a run: The Terra Luna crash | VERIFIED_ABSTRACT: bản ghi nhà xuất bản truy hồi được khi tìm kiếm; lần mở trực tiếp thất bại; không tuyên bố đọc toàn văn JFE | 2.3.2: Terra ở abstract JFE; không results/coefficients toàn văn. |
| S18 | Liu, J., Makarov, I., & Schoar, A. (2023) | VERIFIED_ABSTRACT_INDEXED: bản ghi NBER; cùng nghiên cứu S17, không phải chứng cứ độc lập thứ hai | 2.3.2: NBER predecessor của S17; không evidence độc lập thứ hai. |
| S19 | Bookstaber, R. (2017). Agent-based models for financial crises | VERIFIED_ABSTRACT: trang nhà xuất bản; chưa đọc phần paywall | 2.4.1: ABM methodological context; không project calibration. |
| S20 | Axtell, R. L., & Farmer, J. D. (2025). Agent-based modeling in economics and finance: Past, present, and future | VERIFIED_ABSTRACT: AEA và kho tác giả Oxford; không xác nhận engine DeFiStress | 2.4.1: ABM interactions; không multiple-bot model certification. |
| S21 | Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Milles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism | VERIFIED_CONTENT: toàn văn mở; DOI chuyển đúng tới bài | 2.4.1: ODD/code linkage; không full compliance certification. |
| S22 | Gauntlet. (2021, January 15) | VERIFIED_CONTENT: bài wfu đăng thay mặt Gauntlet; không phải peer review hoặc đặc tả tái lập đầy đủ | 2.4.1: governance practitioner ABM/MC; không peer review hoặc reproducible calibration. |
| S23 | Glasserman, P. (2003) | VERIFIED_PREVIEW/METADATA: chọn edition 1 hardcover 7/8/2003 theo publisher; chưa đọc các chương paywall | 2.4.2: Monte Carlo nền tảng; preview/metadata, không định lý chưa đọc. |
| S24 | National Institute of Standards and Technology. (2014, March 6) | VERIFIED_CONTENT: công thức Wilson được đọc và tính lại; tên trang lịch sử khác tên phương pháp | 2.4.2: Wilson khác adjusted Wald trong Note; không xác nhận project implementation hoặc tính interval mới. |
| S25 | Kivelä, M., Arenas, A., Barthelemy, M., Gleeson, J. P., Moreno, Y., & Porter, M. A. (2014). Multilayer networks | VERIFIED_CONTENT: PDF tác giả đọc được; DOI journal khớp; OUP resolver lỗi | 2.4.3: node–layer/coupling; không full multilayer validation của dự án. |
| S26 | Battiston, S., & Martinez-Jaramillo, S. (2018). Financial networks and stress testing: Challenges and new research avenues for systemic risk analysis and financial stability implications | VERIFIED_ABSTRACT_INDEXED: search đọc được abstract gốc; mở URL thất bại; không tuyên bố đọc toàn văn | 2.4.3: network/stress-testing background, abstract only. |
| S27 | Battiston, S., Puliga, M., Kaushik, R., Tasca, P., & Caldarelli, G. (2012). DebtRank: Too central to fail? Financial networks, the FED and systemic risk | VERIFIED_CONTENT: trang bài gốc; không khẳng định DeFiStress triển khai DebtRank | 2.4.3: DebtRank khác structural centrality; dự án chưa implement. |
| S28 | Freeman, L. C. (1977). A set of measures of centrality based on betweenness | VERIFIED_CONTENT/METADATA: đọc abstract paper gốc qua bản sao https://ucilnica.fri.uni-lj.si/pluginfile.php/1147/course/section/1510/Freeman%20-%20A%20set%20of%20measures%20of%20centrality%20based%20on%20betweenness%2C%201977.pdf; không gán directed variant cho bài gốc | 2.4.3: shortest-path betweenness; directed/unweighted là project-code fact riêng. |
| S29 | Financial Stability Board. (2023, February 16) | VERIFIED_CONTENT: trang phát hành; không gán toàn bộ hệ thống DeFi cho mạng hai giao thức | 2.4.3: interconnections; không systemic-risk measurement từ mạng con. |

Bibliography lấy nguyên mục APA gốc về author/year/title/venue/DOI/URL; không bổ sung số trang. Schär; họ ghép Kaousar Nassr; Aave n.d.-a/b/c/d; Gauntlet tác giả tổ chức; Glasserman2003 theo edition P2 được bảo toàn. Các page ranges vốn nằm trong APA là thông tin biên mục, không claim đã đọc các trang đó. Author–year là working convention; **TEMPLATE_VERIFICATION_PENDING**, chưa là quy định trường được xác minh.

## 5. Model/protocol crosswalk và formula boundaries

| Vị trí | Exact project locator tại Scientific Lock | Nội dung đã đọc / được phép dùng |
|---|---|---|
| 2.1.1/2.3.2 | [sim/schemas.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/schemas.py) | BorrowerPosition.health_factor/debt_value: HF portfolio, USDC component + other debt; token quantity khác USD. |
| 2.1.1/2.1.2/2.3.2 | [sim/lending/liquidation.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/lending/liquidation.py) | close_factor/plan_liquidation: HF+route, repay/seize/dust theo model; seize chưa nhân explicit USDC/USD repricing đầy đủ. |
| 2.1.3 | [sim/agents/liquidator.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/agents/liquidator.py) | Liquidator.evaluate: quote/profit/capital-capacity gates; modeled costs, không ước lượng competition. |
| 2.1.3/2.4.1 | [sim/engine/run.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/engine/run.py) | run_scenario: capital giảm sau execution, remaining capacity, delays; không automatic recycle/split. |
| 2.2.1/2.2.2/2.2.3 | [sim/dex/uniswap_v3.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/dex/uniswap_v3.py) | V3Pool: USDC token0/WETH token1, sqrt/decimals, piecewise liquidityNet, execution average/slippage fee-inclusive, arbitrage_toward repositioning. |
| 2.2.3 | [sim/agents/arbitrageur.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/agents/arbitrageur.py) | Arbitrageur.act gọi repositioning, không funded swap strategy. |
| 2.2.2 | [sim/oracle.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/oracle.py) | OraclePolicy: A min, B ref, C lagged/smoothed completed waves; hypothetical, không Aave/Chainlink feed. |
| 2.2.2/2.5 | [docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md) | Policy purpose/scope, không báo comparison counts. |
| 2.1.1 | [docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md) | Eligibility/evaluation/execution boundary; không tạo historical finding. |
| 2.4.3 | [sim/network/metrics.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/network/metrics.py) | collapse_multigraph/compute_structural_centrality; directed aggregate, betweenness weight=None; chưa DebtRank. |
| 2.4.2 | [sim/research/aave_suite.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/research/aave_suite.py) | _wilson L211: project implementation primary provenance, đọc tĩnh không chạy. |
| 2.4.2 | [scripts/research/run_deep_cascade_study.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/scripts/research/run_deep_cascade_study.py) | _wilson L353: project helper, không tính CI mới. |
| Toàn chương | [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json) | records[registry_id] theo mục3; accepted inference, source tiers, limitations. |

Formula audit: [docs/manuscript_p3/codex/P3_FORMULA_AUDIT_PLAN.md](https://github.com/Doquocdung1609/DeFiStress/blob/8de52bebabef376be700836e6f93a92d7394d2c3/docs/manuscript_p3/codex/P3_FORMULA_AUDIT_PLAN.md). Ch2 **không tạo equation display/number mới**. Inline `HF < 1`, LTV/LT, token quantities và giải thích quy đổi bằng lời là nền khái niệm. Giữ công thức selection E3.x ở Ch3/appendix theo Blueprint.

P3F01/02: HF và route khác nhau; P3F03: baseline USDC-token/USD convention, omitted explicit stablecoin-price factor, C35 limitation; không xuất như identity depeg tổng quát. P3F05/06: token order/decimals và raw amounts, không whole-range constant product. P3F07: hậu bán so reference khác giá bình quân slippage trước lệnh. P3F08/09: phản thực định giá, USDC component khác tổng nợ. P3F15: Wilson dùng implementation/bounds khóa, NIST chỉ phân biệt phương pháp. Không sửa công thức/mã hoặc nhờ Codex kiểm toán lại G0.

## 6. T2.1 provenance

**Request ID:** `P3-CH02-T21-TEXT-v1`; approved display `T2.1`, historical handoff `P3X-T2.1`. Trực tiếp tạo Markdown theo quyền trong chỉ thị, không cần Codex rendering.

Bảng có12 nhánh và7 cột theo yêu cầu: branch/source/question/data-method/supported finding/access-limit/design implication. Nguồn trực tiếp là P2 Literature, Reference Evidence Matrix, APA tại Scientific Lock; Blueprint/crosswalk tại Blueprint Lock. P3 evidence aliases `P3E:050/051/055` chỉ là inventory locators; không scientific result IDs mới. T2.1 không phải kết quả simulation hoặc bảng cỡ mẫu. Không có denominator/unit số học;29S records được dùng trong chương không được gọi29nghiên cứu độc lập, S17/S18 cùng study. Các source metadata/abstract/whitepaper/industry được gắn đúng loại trong bảng.

Nếu chuyển định dạng sau này, cần giữ đủ columns/caption, đối chiếu P2 theo S IDs và giữ qualifiers. Không phát sinh yêu cầu tính toán hoặc data extraction mới. Table source paths/commit pins xuất hiện ngay caption; không có bảng/hình Ch5/6 được dựng trong vòng này.

## 7. Safeguards và giới hạn

| Excluded registry history | Xử lý trong chương |
|---|---|
| CL_FROZEN_RQ1_UNQUALIFIED_WORDING | Không affirmative; cascade gắn policy/scenario, không ngưỡng hệ thống chung. |
| CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING | Không affirmative; absorption/DEX price khác transmission sang HF. |
| CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT | Không affirmative; phân biệt API/source với historical feed. |
| CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION | Không affirmative; temporal linkage/common shock khác causal feedback. |

Những hạn chế được đặt đúng vị trí: eligibility/route và agents ở2.1; price units/policies/repositioning ở2.2; valuation-only/issuer evidence/Terra versions ở2.3; source access, conditional sample, prefixes và network ở2.4; inference/gap ở2.5. Modeled debt/loss không được gọi realized loss. Các claims nguồn chỉ abstract không được dùng cho hệ số, sample size hoặc cơ chế chi tiết chưa xác minh.

Hai raw borrower CSV lớn tiếp tục chưa được Work đọc đầy đủ/cell-by-cell. Không nâng source access hoặc gọi static reading là replay; không chạy RPC/fork/simulation/MC/CI. Git LF blob hash khác Windows CRLF checkout hash, không mô tả hai giá trị khác nhau là cùng SHA. School template pending chỉ chặn final DOCX, không Markdown review.

## 8. Continuity và legacy repair

Ch1 đã đặt vấn đề và sáu RQ; Ch2 không chép lại RQ, quy mô454/109, ba đóng góp hoặc toàn bộ bố cục bảy chương. Các nội dung nhắc lại được phát triển thành nền tảng khác: HF thành portfolio/route/units, liquidity thành range/depth/slippage, literature thành comparability, ABM thành mức agents và uncertainty, network thành measurement semantics. Không có đoạn văn dài sao chép nguyên từ Ch1 (kiểm tra nêu trong self-review).

DOCX Ch2 cũ có định nghĩa/ý tưởng còn dùng được nhưng thiếu phân biệt policies/execution, mô tả ABM dễ suy nhiều bot, viện dẫn CPMI thay tác giả S15 và giản lược graph nhiều lớp. Bản mới viết lại theo P2/registry, dùng Kosse et al.; giữ thông tin source levels và không tái dùng kết luận thực nghiệm lỗi thời. Ch3 nhận đặc tả equations/timing, Ch5 nhận số results, Ch6 nhận census/Terra/network measurements. Không sửa bản Ch1 hoặc DOCX gốc.
