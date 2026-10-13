# Ma trận luận điểm nguồn và sáu câu hỏi nghiên cứu

Bản P2 ngày 13/10/2026. Tài liệu mục tiêu là bản V2 432 dòng được đọc ngày này và báo cáo/mã tại commit `2b9a29f5e8c0c8dd910b7d65428fb1d57646b06b`. Pxx là đoạn trong `LITERATURE_VERIFIED.md`; Sxx là nguồn trong `APA_REFERENCES_VERIFIED.md`. Địa chỉ đoạn dùng phần–chương–tiêu đề vì bản V2 có cả đề cương và bản mở rộng.

## 1. Sổ nguồn và phạm vi xác minh

Ngày kiểm/truy cập cho tất cả dòng: **13/10/2026**. `DOI_MATCHED` nghĩa chuỗi DOI khớp bản ghi nhà xuất bản/kho tác giả; không có nghĩa mọi resolver đã mở thành công. Những DOI trực tiếp đã thử ở JFE, ACM, Bank of Canada, OECD, OUP và AEA gặp 403/redirect/unavailable được ghi phạm vi thay thế. `VERIFIED_ABSTRACT_INDEXED` là abstract từ kết quả tìm kiếm nguồn gốc; toàn văn vẫn `SOURCE_NOT_VERIFIED_FULLTEXT`. Chỉ dùng các luận điểm ở abstract. Không có bản thân nội dung thì `SOURCE_NOT_VERIFIED` và không viện dẫn thực chất.

Danh tính đầy đủ tác giả, năm, tiêu đề, venue và định danh nằm trong từng mục APA S tương ứng; bảng này giữ tuyến kiểm tra nội dung, tránh trộn biên mục với xác minh kết quả.

| Nguồn | Loại | DOI đối chiếu | URL chứng cứ | Vị trí đã kiểm | Phạm vi xác minh |
|---|---|---|---|---|---|
| [S01](APA_REFERENCES_VERIFIED.md#s01) | Bài tổng quan học thuật | 10.20955/r.103.153-74 | [Nguồn gốc](https://www.stlouisfed.org/publications/review/2021/02/05/decentralized-finance-on-blockchain-and-smart-contract-based-financial-markets) | Abstract; phần về composability và các lớp hạ tầng | VERIFIED_CONTENT: trang tác giả/nhà xuất bản đọc được |
| [S02](APA_REFERENCES_VERIFIED.md#s02) | Tài liệu giao thức | — | [Nguồn gốc](https://www.aave.com/docs/aave-v3/overview) | Borrow; Liquidations | VERIFIED_CONTENT: nội dung hiện hành; không xác nhận cấu hình lịch sử |
| [S03](APA_REFERENCES_VERIFIED.md#s03) | Tài liệu giao thức | — | [Nguồn gốc](https://aave.dev/help/borrowing/liquidations) | Health Factor; Liquidation Process | VERIFIED_CONTENT: HF và nhánh close factor trên trang trợ giúp |
| [S04](APA_REFERENCES_VERIFIED.md#s04) | Tài liệu giao thức | — | [Nguồn gốc](https://www.aave.com/docs/aave-v3/concepts/reserve) | Key Reserve Parameters; Dynamic Parameters and Governance | VERIFIED_CONTENT: định nghĩa LTV/LT; tham số thay đổi theo thị trường/thời điểm |
| [S05](APA_REFERENCES_VERIFIED.md#s05) | Tài liệu giao thức | — | [Nguồn gốc](https://aave.com/docs/aave-v3/smart-contracts/oracles) | AaveOracle; getAssetPrice; getSourceOfAsset | VERIFIED_CONTENT: API nguồn giá, không xác nhận feed tại block nghiên cứu |
| [S06](APA_REFERENCES_VERIFIED.md#s06) | Mã triển khai chuẩn | — | [Nguồn gốc](https://github.com/aave-dao/aave-v3-origin/blob/8305565ae342f1773c42cd2e4593f175fe5968a0/src/contracts/protocol/libraries/logic/LiquidationLogic.sol) | Các hằng close factor; executeLiquidationCall; tính debt/collateral theo base currency | VERIFIED_CODE: commit đọc được; không phải xác minh bytecode triển khai tại block |
| [S07](APA_REFERENCES_VERIFIED.md#s07) | White paper giao thức | — | [Nguồn gốc](https://blog.uniswap.org/whitepaper-v3.pdf) | §2; §6.2.3–6.3.1; phương trình 6.14–6.16 | VERIFIED_CONTENT: PDF gốc; không phân loại peer reviewed |
| [S08](APA_REFERENCES_VERIFIED.md#s08) | Mã triển khai chuẩn | — | [Nguồn gốc](https://github.com/Uniswap/v3-core/blob/d0831dc6b8a318df3872b6d68f6de135c9f3ec29/contracts/libraries/SqrtPriceMath.sol) | getAmount0Delta; getAmount1Delta; quy tắc làm tròn | VERIFIED_CODE: mã chuẩn; bổ trợ https://developers.uniswap.org/docs/protocols/v3/concepts/architecture |
| [S09](APA_REFERENCES_VERIFIED.md#s09) | Hội nghị có phản biện | 10.1145/3487552.3487811 | [Nguồn gốc](https://arxiv.org/abs/2106.06389) | Abstract; phân loại cơ chế và rủi ro thanh lý | VERIFIED_ABSTRACT: bản tác giả arXiv đọc được; DOI/venue khớp UCL; DOI trực tiếp 403 |
| [S10](APA_REFERENCES_VERIFIED.md#s10) | Working paper | — | [Nguồn gốc](https://www.bis.org/publications/working-paper-1062-systemic-fragility-decentralised-markets) | Focus; Contribution; Findings; Abstract | VERIFIED_ABSTRACT: trang BIS đọc được; chưa kiểm từng bảng/ước lượng; không gán DOI |
| [S11](APA_REFERENCES_VERIFIED.md#s11) | Working paper | 10.1787/0524faaf-en | [Nguồn gốc](https://www.oecd.org/en/publications/defi-liquidations_0524faaf-en.html) | Abstract; PDF §2, phương trình (2) | VERIFIED_CONTENT: PDF và trang OECD; DOI khớp nhà xuất bản; resolver trực tiếp không truy cập được |
| [S12](APA_REFERENCES_VERIFIED.md#s12) | Working paper | 10.34989/swp-2025-12 | [Nguồn gốc](https://www.bankofcanada.ca/2025/03/staff-working-paper-2025-12/) | Abstract; đối chiếu bản ghi Publications Canada 9.951207 | VERIFIED_ABSTRACT: nguồn phát hành; không suy diễn Aave dùng đấu giá |
| [S13](APA_REFERENCES_VERIFIED.md#s13) | Staff analytical paper | 10.34989/sap-2026-13 | [Nguồn gốc](https://www.bankofcanada.ca/2026/04/staff-analytical-paper-2026-13/) | PDF §5.4–5.5, trang in 24–27; Abstract | VERIFIED_CONTENT: PDF gốc và DOI nhà phát hành; resolver trực tiếp không truy cập được |
| [S14](APA_REFERENCES_VERIFIED.md#s14) | Tạp chí có phản biện | 10.1016/j.jimonfin.2022.102777 | [Nguồn gốc](https://www.sciencedirect.com/science/article/pii/S0261560622001802) | Abstract; Highlights; bản tác giả tại https://wrap.warwick.ac.uk/id/eprint/173269/ | VERIFIED_ABSTRACT: bản công bố và kho tác giả khớp; không suy rộng hệ số Tether sang USDC |
| [S15](APA_REFERENCES_VERIFIED.md#s15) | BIS Paper | — | [Nguồn gốc](https://www.bis.org/publications/paper-141-will-real-stablecoin-please-stand-up) | Danh sách Authors; phần tóm tắt | VERIFIED_ABSTRACT/METADATA: tác giả cá nhân, không phải CPMI là tác giả; không gán DOI |
| [S16](APA_REFERENCES_VERIFIED.md#s16) | Thông cáo tổ chức phát hành | — | [Nguồn gốc](https://www.circle.com/pressroom/3-3-billion-of-usdc-reserve-risk-removed-dollar-de-peg-closes) | Ngày hiển thị trang 13/3; dateline trong nội dung 12/3/2023 | VERIFIED_CONTENT: lời công bố của Circle, không phải kiểm toán độc lập |
| [S17](APA_REFERENCES_VERIFIED.md#s17) | Tạp chí có phản biện | 10.1016/j.jfineco.2026.104359 | [Nguồn gốc](https://www.sciencedirect.com/science/article/pii/S0304405X26001303) | Metadata; Abstract bản JFE; NBER Published Versions | VERIFIED_ABSTRACT: bản ghi nhà xuất bản truy hồi được khi tìm kiếm; lần mở trực tiếp thất bại; không tuyên bố đọc toàn văn JFE |
| [S18](APA_REFERENCES_VERIFIED.md#s18) | Working paper bản tiền nhiệm | 10.3386/w31160 | [Nguồn gốc](https://www.nber.org/papers/w31160) | Abstract; Issue Date; Published Versions | VERIFIED_ABSTRACT_INDEXED: bản ghi NBER; cùng nghiên cứu S17, không phải chứng cứ độc lập thứ hai |
| [S19](APA_REFERENCES_VERIFIED.md#s19) | Tạp chí có phản biện | 10.1146/annurev-financial-110716-032556 | [Nguồn gốc](https://www.annualreviews.org/content/journals/10.1146/annurev-financial-110716-032556) | Abstract; article metadata | VERIFIED_ABSTRACT: trang nhà xuất bản; chưa đọc phần paywall |
| [S20](APA_REFERENCES_VERIFIED.md#s20) | Tạp chí có phản biện | 10.1257/jel.20221319 | [Nguồn gốc](https://swlb1.aeaweb.org/articles?id=10.1257%2Fjel.20221319) | Abstract; Citation; Additional Materials (corrigendum 24/3/2025) | VERIFIED_ABSTRACT: AEA và kho tác giả Oxford; không xác nhận engine DeFiStress |
| [S21](APA_REFERENCES_VERIFIED.md#s21) | Tạp chí có phản biện | 10.18564/jasss.4259 | [Nguồn gốc](https://jasss.soc.surrey.ac.uk/23/2/7.html) | Abstract; §§1.6–1.7; Issues and Challenges; liên kết ODD với code | VERIFIED_CONTENT: toàn văn mở; DOI chuyển đúng tới bài |
| [S22](APA_REFERENCES_VERIFIED.md#s22) | Thực hành ngành | — | [Nguồn gốc](https://governance.aave.com/t/gauntlet-market-risk-primer/2097) | Background; Agent-Based Simulation; Network Congestion | VERIFIED_CONTENT: bài wfu đăng thay mặt Gauntlet; không phải peer review hoặc đặc tả tái lập đầy đủ |
| [S23](APA_REFERENCES_VERIFIED.md#s23) | Sách phương pháp | 10.1007/978-0-387-21617-1 | [Nguồn gốc](https://link.springer.com/book/10.1007/978-0-387-21617-1) | About this book; Bibliographic information; Table of contents | VERIFIED_PREVIEW/METADATA: chọn edition 1 hardcover 7/8/2003 theo publisher; chưa đọc các chương paywall |
| [S24](APA_REFERENCES_VERIFIED.md#s24) | Tài liệu thống kê chuẩn | — | [Nguồn gốc](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/agcoulci.htm) | Description; công thức score interval; Note phân biệt Wilson và adjusted Wald | VERIFIED_CONTENT: công thức Wilson được đọc và tính lại; tên trang lịch sử khác tên phương pháp |
| [S25](APA_REFERENCES_VERIFIED.md#s25) | Tạp chí có phản biện | 10.1093/comnet/cnu016 | [Nguồn gốc](https://arxiv.org/abs/1309.7233) | Bản tác giả v4, §§2 và 4; journal reference; DOI liên quan | VERIFIED_CONTENT: PDF tác giả đọc được; DOI journal khớp; OUP resolver lỗi |
| [S26](APA_REFERENCES_VERIFIED.md#s26) | Tạp chí có phản biện | 10.1016/j.jfs.2018.03.010 | [Nguồn gốc](https://www.sciencedirect.com/science/article/pii/S157230891830192X) | Abstract và metadata nhà xuất bản | VERIFIED_ABSTRACT_INDEXED: search đọc được abstract gốc; mở URL thất bại; không tuyên bố đọc toàn văn |
| [S27](APA_REFERENCES_VERIFIED.md#s27) | Tạp chí có phản biện | 10.1038/srep00541 | [Nguồn gốc](https://www.nature.com/articles/srep00541) | Abstract; Introduction; chỉ số truyền distress | VERIFIED_CONTENT: trang bài gốc; không khẳng định DeFiStress triển khai DebtRank |
| [S28](APA_REFERENCES_VERIFIED.md#s28) | Tạp chí có phản biện | 10.2307/3033543 | [Nguồn gốc](https://www.jstor.org/stable/i352126) | JSTOR mục lục xác nhận DOI; bản paper trong tài liệu giảng dạy University of Ljubljana | VERIFIED_CONTENT/METADATA: đọc abstract paper gốc qua bản sao https://ucilnica.fri.uni-lj.si/pluginfile.php/1147/course/section/1510/Freeman%20-%20A%20set%20of%20measures%20of%20centrality%20based%20on%20betweenness%2C%201977.pdf; không gán directed variant cho bài gốc |
| [S29](APA_REFERENCES_VERIFIED.md#s29) | Báo cáo cơ quan ổn định tài chính | — | [Nguồn gốc](https://www.fsb.org/2023/02/the-financial-stability-risks-of-decentralised-finance/) | Tóm tắt về liên thông DeFi, CeFi, stablecoin | VERIFIED_CONTENT: trang phát hành; không gán toàn bộ hệ thống DeFi cho mạng hai giao thức |
| [S30](APA_REFERENCES_VERIFIED.md#s30) | Tạp chí có phản biện | 10.1016/j.csda.2017.11.003 | [Nguồn gốc](https://research.monash.edu/en/publications/a-note-on-the-validity-of-cross-validation-for-evaluating-autoreg/) | Abstract tác giả: pure autoregression và uncorrelated errors | VERIFIED_ABSTRACT: kho tác giả; chỉ dùng để giới hạn viện dẫn CV, không chứng minh cutoff Terra |

Các nguồn U01–U08 trong file APA là hàng chờ, không tính vào tập 30 mục S. S17 được duyệt đúng abstract nhà xuất bản truy hồi ngày kiểm, chưa duyệt toàn văn JFE. S18 là cùng công trình bản 2023. S23 chỉ duyệt preview/biên mục, không duyệt định lý chương sách. S26 chỉ duyệt abstract. Việc ghi nguồn này không xóa các giới hạn truy cập.

## 2. Luận điểm đoạn nguồn RQ

| Claim | Đoạn P2 và vị trí V2 cần tích hợp | Luận điểm được phép dùng | Nguồn và vị trí chứng cứ | RQ/ca | Giới hạn hoặc sửa cần thiết |
|---|---|---|---|---|---|
| C01 | P01; VIII §1.1, §2.1 | DeFi có các kênh kết hợp dịch vụ và phơi nhiễm | S01 abstract/composability; S29 tóm tắt phát hành | RQ1–6 | Tính liên thông chưa chứng minh cascade xảy ra |
| C02 | P02/P19; VIII §2.2, §4.1 | HF so sánh thế chấp điều chỉnh với giá trị nợ | S02 Borrow; S03 Health Factor; S05 oracle | RQ1/5/6 | Portfolio approximation cần đối chiếu Aave |
| C03 | P02; VIII §4.2 | HF<1 là đủ điều kiện, execution còn điều kiện | S03 Liquidation Process; S09 abstract | RQ1/3 | Không gọi mọi eligible là đã thanh lý |
| C04 | P02/P07; VIII §7.2 | LTV khác LT và liquidation bonus | S04 Key Reserve Parameters; S06 logic | RQ6 | LTV không viết lại frozen debt |
| C05 | P02/P19; VIII §4.2 | Close factor và dust phụ thuộc phiên bản/vị thế | S06 executeLiquidationCall và các hằng | RQ3/6 | Pin implementation/bytecode tại block; không dùng 50% phổ quát |
| C06 | P03; VIII §2.2, §4.2 | Incentive thiết kế có thể chuyển chi phí sang borrower | S09 abstract bản tác giả | RQ3/6 | Không đưa tỷ lệ/cỡ mẫu chưa đọc |
| C07 | P04; VIII §2.3; II Chương 4 | Độ sâu V3 thay đổi theo khoảng giá/tick | S07 §2/§6.2–6.3; S08 amount delta | RQ2 | TVL không tương đương executable depth |
| C08 | P04/P19; II Chương 4 | Đổi Q64.96, token order và decimals trước định giá | S08 mã; `sim/dex/uniswap_v3.py` | RQ2/5 | Giá USDC/WETH chưa phải USD/WETH nếu q khác 1 |
| C09 | P05; VIII §2.2–2.3 | Bán collateral có thể tạo price impact | S10 Findings/Abstract | RQ1/2/4 | Không gán critical shock từ bài cho snapshot |
| C10 | P05; VIII §2.3 | Thanh lý và post-volatility có quan hệ thống kê | S11 abstract; PDF equation (2) | RQ1/2 | Không suy ra nhân quả từ OLS/cùng shock |
| C11 | P06; VIII §7.1 | Một thiết kế Aave V3 không thấy tác động kéo dài significant | S13 PDF §5.5, trang in 25–27 | RQ1/4 | Không phủ định tác động DEX tức thời |
| C12 | P07; VIII §7.2 | Fixed spread/auction có đánh đổi theo participation cost | S12 abstract | RQ3/6 | Không nói đấu giá luôn tốt hoặc Aave dùng đấu giá |
| C13 | P08; VIII §2.3; III §5.5 | Arbitrage phụ thuộc thiết kế và khả năng thực thi | S14 abstract/Highlights | RQ4/5 | Không dùng hệ số Tether hiệu chỉnh WETH agent |
| C14 | P09; III §5.6 | Stablecoin có rủi ro giá và quy đổi khác nhau | S15 abstract; S16 thông cáo | RQ5 | Circle là issuer account, không nghiên cứu độc lập |
| C15 | P09/P19; III §5.6 | USDC debt price tăng làm HF giảm ceteris paribus | S02/S03 cho HF; đại số và `schemas.debt_value` | RQ5 | Là dấu kênh valuation; chưa đầy đủ stress stablecoin |
| C16 | P10; IV §6.1, §6.3 | Terra run liên quan khuyến khích/quan sát/tập trung | S17 abstract JFE | Terra | Không gán chỉ một thủ phạm hoặc thêm tỷ lệ không kiểm |
| C17 | P10; IV §6.8 | Terra không xác nhận trực tiếp tham số Aave | Cơ chế S17 khác S02/S06; thiết kế hai ca của dự án | Terra / RQ1–6 | Kết luận giới hạn của nghiên cứu, không trích như phát hiện định lượng JFE |
| C18 | P11; VIII §2.4 | ABM cho phép tương tác và khác biệt tác nhân | S19/S20 abstracts | RQ1–6 | Không chứng minh tham số hay nhiều bot trong implementation |
| C19 | P11/P19; VIII §2.4 | Aave code đọc có một liquidator/arbitrageur đại diện | `sim/engine/run.py`; `sim/agents/*` | RQ3/4 | Sửa mô tả nhiều bot có hành vi dị thể |
| C20 | P12; VIII §4.5 | ODD nên mô tả scheduling/model con và liên kết code | S21 §§1.6–1.7 và phần code linkage | RQ1–6 / Terra | ODD không tự cấp chứng nhận mô hình đúng |
| C21 | P12; VIII §2.4 | Ngành dùng ABM/MC cho stress tham số DeFi | S22 Agent-Based Simulation/Network Congestion | RQ2/3/6 | Forum không peer reviewed, không claim tái tạo Gauntlet |
| C22 | P13; III §5.8 | MC engine lấy mẫu shock/haircut/gas, không path giá đầy đủ | `sim/monte_carlo/runner.py`; S23 preview cho nền MC | RQ1–6 | Độc lập/clipping là giả định; chưa hiệu chỉnh joint distribution |
| C23 | P14; III §5.8 | 0/200 có Wilson upper hai phía ≈1,8845% | S24 Description/formula; phép tính P2 | RQ1 | Có điều kiện; không crisis probability ngoài đời |
| C24 | P19/P20; III §5.8 | Tổng repayment cộng shortfall không phải economic loss | S13 §5.4; `runner.py` loss/tail | RQ2/3/5/6 | USD+USDC khi q≠1; ties làm tail khác fixed 5% |
| C25 | P15; VIII §2.5; III §5.9 | Multilayer cần nêu node–layer và kiểu coupling | S25 §2 bản tác giả | Network extension | Nhãn lớp/nhiều cạnh chưa đủ chứng minh supra adjacency |
| C26 | P15/P19; III §5.9 | Centrality hiện tính trên graph gộp typed network | `sim/network/metrics.py`; S25/S26 nền phương pháp | Network extension | Gộp max; structural metric chưa risk-weighted |
| C27 | P16; VIII §2.5 | Betweenness biểu thị vị trí trên shortest paths | S28 paper abstract; implementation NetworkX trong dự án | Network extension | Directed/unweighted variant phải công bố; không universal importance |
| C28 | P16; III §5.9 | DebtRank là chỉ số distress khác centrality cấu trúc | S27 Introduction/abstract | Network extension | Dự án chưa implement DebtRank; không đổi tên điểm normalized |
| C29 | P17; IV §6.5–6.6; VIII §4.5 | Bergmeir nêu CV autoregression với điều kiện cụ thể | S30 abstract kho tác giả | Terra validation | Không dẫn như lệnh cấm K-fold chung hoặc bằng chứng no-leakage |
| C30 | P17/P20; IV §6.5–6.6 | Crisis reconstruction khác cutoff-safe warning | V2 và `FINAL_RESEARCH_REPORT.md`/claim matrix; P2 yêu cầu thiết kế | Terra validation | Source paper không chứng nhận retrospective forecast |
| C31 | P18; VIII §2.6, §7.3 | Novelty đề xuất là tích hợp truy vết và giới hạn rõ | Đối chiếu S09–13/S19–22; evidence pipeline dự án | RQ1–6 | Không first ever; contribution còn phải audit thực hiện |
| C32 | P19; VIII §4.1 | Liên kết giá đánh giá lại là min(reference,DEX) | `sim/engine/run.py` | RQ1/2/4 | Không Aave oracle đã quan sát; không đồng nhất DEX với feed |
| C33 | P19/P20; VIII §4.3 | Vòng xử lý thứ hai có thể chỉ vì capacity | `run.py` eligible/attempted/completed_waves | RQ1/3 | Tag newly eligible do feedback trước dùng causal cascade |
| C34 | P19; II Chương 4; III §5.5 | Arbitrage đặt lại sqrt price chưa cập nhật L qua tick | `V3Pool.arbitrage_toward` so với S07/S08 | RQ2/4 | Không gọi exact V3 state path; P2 chỉ disclosure |
| C35 | P19/P20; III §5.6 | Seize/dust/quote chưa repricing toàn diện theo USDC/USD | `liquidation.py`, `schemas.py`, `uniswap_v3.py` | RQ5 | Counterfactual valuation limited; P0/P1 cần audit units trước final |

## 3. Giữ nguyên sáu câu hỏi nghiên cứu

Bản gốc đối chiếu từ V2 và `METHODOLOGY.md`/`FINAL_RESEARCH_REPORT.md` tại 2b9a29f5, không thêm RQ Terra/network. Dưới đây giữ nguyên nghĩa và nội dung gốc của RQ; glossary cung cấp tên tiếng Việt khi biên tập.

1. **RQ1.** Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)?
2. **RQ2.** Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt?
3. **RQ3.** Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý?
4. **RQ4.** Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi?
5. **RQ5.** Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset?
6. **RQ6.** Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk?

| RQ | Nguồn lõi | Biến và phép kiểm đề nghị | Mã/bằng chứng dự án cần đọc | Quy tắc diễn giải |
|---|---|---|---|---|
| RQ1 | S03/S05/S06/S09/S10/S11/S13/S24 | Shock grid; newly eligible after feedback; cùng cohort | `run.py`, `threshold.py`, direct-shock eligibility và borrower event log | Không suy ngưỡng liên tục/ngoài miền; depth index chưa đủ causal cascade |
| RQ2 | S07/S08/S10/S11 | Tick depth, haircut; price impact trước/sau; liquidation vs shortfall | `uniswap_v3.py`, tick provenance, quote/fork | Kết luận trên venue/mẫu hữu hạn; haircut là stress giả định, chưa observed LP withdrawal |
| RQ3 | S06/S09/S10/S12/S13/S22 | Vốn tổng, capacity/bước, gas, delay; isolate channel | `liquidator.py`, `run.py`; funding reference và rejection reasons | Không recycle/flash loan đầy đủ; delayed batches không tự là contagion |
| RQ4 | S07/S10/S14 | OFF/on/capacity/delay; so sánh spread và newly eligible | `arbitrageur.py`, `arbitrage_toward` | Năng lực tỷ lệ hồi spread là giả định; reset price khác executable swap |
| RQ5 | S02/S03/S05/S14/S15/S16 | q_USDC/USD, debt quantity, HF; USD và USDC tách riêng | `schemas.py`, `liquidation.py`, DEX quote unit | Ceteris paribus valuation; không gán full depeg/crisis effect |
| RQ6 | S04/S06/S09/S12/S22 | LTV capacity ex ante, LT eligibility, bonus seizure/profit | Chính sách frozen cohort; kiểm semantic invariants | Chính sách phản thực không forecast governance hoặc borrower re-underwriting |

Terra: S17/S18/S19/S21/S30. Network: S25–S28. Hai extension hỗ trợ đối chiếu cơ chế/phương pháp, không trả lời thay sáu RQ.

## 4. Chứng cứ dự án không được thay bằng nguồn học thuật

| Loại phát biểu trong V2/Word | Nguồn thích hợp | Việc P2 đã làm | Điều chưa xác nhận |
|---|---|---|---|
| 500 ứng viên/454 xác minh/109 cohort | Snapshot manifest, account reads, data quality tại commit | Đọc báo cáo; phân biệt tỷ lệ xác minh với market coverage | Không truy RPC lại, không chứng nhận completeness |
| Lưới shock chưa thấy depth≥2 | Grid output và event log | Đọc RQ answer matrix, giữ negative finding | Chưa chứng nhận cascade classifier phân biệt batching |
| 1.776 giờ/277.342 Terra swaps | Versioned dataset/provenance và parser audit | Đọc báo cáo và giới hạn V2 | Không gán cỡ mẫu này cho Liu et al. hoặc tự xác minh raw chain |
| Khớp giá/lệch timing/cảnh báo ban đầu muộn | Historical validation/early-warning outputs | Giữ tách reconstruction và prediction | Không học thuật source nào cấp validation thay pipeline |
| Điểm centrality/độ trung gian | Graph schema/build, aggregation policy, metric output | Đọc schema/metrics, ghi scope typed aggregated graph | Không chứng nhận topology đầy đủ toàn DeFi |
| ES hoặc tỷ lệ cascade | Metric definition, units, stochastic generator, seeds | Đọc công thức/code; tính Wilson có điều kiện | Không xác nhận economic loss distribution hay real crisis probability |

## 5. Kiểm soát suy luận và bàn giao reviewer

Nguồn thực nghiệm hỗ trợ tính khả dĩ của cơ chế; official docs/code hỗ trợ semantics; mã dự án mô tả implementation; kết quả dự án cần artifacts. Không hoán đổi bốn cấp chứng cứ này. Với phản thực, thay biến và giữ các biến còn lại chỉ định quan hệ **trong mô hình**; empirical causal identification cần thiết kế đối chứng, giả định và dữ liệu riêng.

Reviewer cần kiểm: (a) mọi claim C có nguồn/vị trí hoặc mã dự án cụ thể; (b) bản JFE/NBER không đếm đôi; (c) nguồn không truy cập được có nhãn; (d) 6 RQ giữ nguyên; (e) các caveat oracle/cascade/unit/arbitrage/ES/graph chưa bị loại khi biên tập. P2 không triển khai bản vá hoặc đẩy trạng thái PASS của P0/P1.
