# Ma trận luận điểm nguồn và sáu câu hỏi nghiên cứu

Bản nguồn ngày 13/10/2026; đối chiếu phiên bản ngày 14/10/2026. V2 và mã 2b9a29f5 là mục tiêu lịch sử; dùng `corrected_run_v2`, Level-3 và gói sửa có mục tiêu tại HEAD **ba62c74950a72751e0030527836082da0c7622ef** cho implementation/kết quả Aave. Giữ 35 claim IDs và sáu RQ; S01–S30, giới hạn truy cập và U01–U08 không đổi. Trạng thái chờ Commander duyệt lại, không phải scientific lock. Pxx là đoạn trong `LITERATURE_VERIFIED.md`; Sxx là nguồn trong `APA_REFERENCES_VERIFIED.md`.

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
| C07 | P04/P19/P21; VIII §2.3; II Chương 4 | Độ sâu V3 theo tick, liquidity stress dùng corrected artifact | S07 §2/§6.2–6.3; S08; E01/E02 | RQ2 | TVL khác depth; 90/95% haircut là giả định tail |
| C08 | P04/P19; II Chương 4 | Giá/L cần đúng token order/decimal/hướng tick | S08; uniswap_v3.py tại ba62c749 | RQ2/5 | Lỗi reposition giữ L cũ đã sửa; USD/USDC/funded-swap caveat giữ |
| C09 | P05/P21; VIII §2.2–2.3 | Literature hỗ trợ bán thế chấp; lịch sử ghi receipt route và association | S10 Findings/Abstract; E09/E11 | RQ1/2/4 | Một WETH route được kiểm receipt; không chứng minh price causality/cascade |
| C10 | P05/P21; VIII §2.3 | Liquidation/volatility relation khác xác nhận nhân quả | S11 abstract/equation (2); E09/E10 | RQ1/2 | Cùng shock/market movement không là simulated endogenous wave |
| C11 | P06/P21; VIII §7.1 | S13 không thấy impact kéo dài significant; model riêng có wave 2 | S13 PDF §5.5; E03/E04/E08 | RQ1/4 | Khác tần suất/đối chứng; không dùng model wave 2 bác empirical null |
| C12 | P07; VIII §7.2 | Fixed spread/auction có đánh đổi theo participation cost | S12 abstract | RQ3/6 | Không nói đấu giá luôn tốt hoặc Aave dùng đấu giá |
| C13 | P08/P19/P20; III §5.5 | Arbitrage có điều kiện; v2 tách intrawave và residual | S14 abstract; E01/E07; mã ba62c749 | RQ4/5 | Sweep intrawave giữ nguyên, residual giảm; price teleportation |
| C14 | P09; III §5.6 | Stablecoin có rủi ro giá và quy đổi khác nhau | S15 abstract; S16 thông cáo | RQ5 | Circle là issuer account, không nghiên cứu độc lập |
| C15 | P09/P19; III §5.6 | USDC debt price tăng làm HF giảm ceteris paribus | S02/S03 cho HF; đại số và `schemas.debt_value` | RQ5 | Là dấu kênh valuation; chưa đầy đủ stress stablecoin |
| C16 | P10; IV §6.1, §6.3 | Terra run liên quan khuyến khích/quan sát/tập trung | S17 abstract JFE | Terra | Không gán chỉ một thủ phạm hoặc thêm tỷ lệ không kiểm |
| C17 | P10; IV §6.8 | Terra không xác nhận trực tiếp tham số Aave | Cơ chế S17 khác S02/S06; thiết kế hai ca của dự án | Terra / RQ1–6 | Kết luận giới hạn của nghiên cứu, không trích như phát hiện định lượng JFE |
| C18 | P11; VIII §2.4 | ABM cho phép tương tác và khác biệt tác nhân | S19/S20 abstracts | RQ1–6 | Không chứng minh tham số hay nhiều bot trong implementation |
| C19 | P11/P19; VIII §2.4 | Aave ba62c749 có một liquidator/arbitrageur đại diện | engine/run.py; agents/* | RQ3/4 | Không gọi nhiều bot cạnh tranh được ước lượng hành vi |
| C20 | P12; VIII §4.5 | ODD nên mô tả scheduling/model con và liên kết code | S21 §§1.6–1.7 và phần code linkage | RQ1–6 / Terra | ODD không tự cấp chứng nhận mô hình đúng |
| C21 | P12; VIII §2.4 | Ngành dùng ABM/MC cho stress tham số DeFi | S22 Agent-Based Simulation/Network Congestion | RQ2/3/6 | Forum không peer reviewed, không claim tái tạo Gauntlet |
| C22 | P13/P19/P21; III §5.8 | MC lấy mẫu tham số; checkpoint stages có prefix lồng và accounting tách biệt | runner.py; targeted repair E04/E12 | RQ1–6 | 13k batch identities, 0 duplicates, 21/21 reproduce; legacy duration unavailable |
| C23 | P14/P21; III §5.8 | Wilson Severe 8/200,280/10k; Low Liquidity 0/1k | S24 Note/formula; E03/E04/E05 | RQ1 | Tên lịch sử NIST không đổi tên Wilson; không forecast |
| C24 | P19/P21; III §5.8 | Chỉ tiêu đuôi là composite exposure, không realized loss | S13 §5.4; runner.py; E04 loss_definition | RQ2/3/5/6 | Repayment không phải loss; giữ units/ties/provenance |
| C25 | P15; VIII §2.5; III §5.9 | Multilayer cần nêu node–layer và kiểu coupling | S25 §2 bản tác giả | Network extension | Nhãn lớp/nhiều cạnh chưa đủ chứng minh supra adjacency |
| C26 | P15/P19; III §5.9 | Centrality hiện tính trên graph gộp typed network | `sim/network/metrics.py`; S25/S26 nền phương pháp | Network extension | Gộp max; structural metric chưa risk-weighted |
| C27 | P16; VIII §2.5 | Betweenness biểu thị vị trí trên shortest paths | S28 paper abstract; implementation NetworkX trong dự án | Network extension | Directed/unweighted variant phải công bố; không universal importance |
| C28 | P16; III §5.9 | DebtRank là chỉ số distress khác centrality cấu trúc | S27 Introduction/abstract | Network extension | Dự án chưa implement DebtRank; không đổi tên điểm normalized |
| C29 | P17; IV §6.5–6.6; VIII §4.5 | Bergmeir nêu CV autoregression với điều kiện cụ thể | S30 abstract kho tác giả | Terra validation | Không dẫn như lệnh cấm K-fold chung hoặc bằng chứng no-leakage |
| C30 | P17/P20; IV §6.5–6.6 | Crisis reconstruction khác cutoff-safe warning | V2 và `FINAL_RESEARCH_REPORT.md`/claim matrix; P2 yêu cầu thiết kế | Terra validation | Source paper không chứng nhận retrospective forecast |
| C31 | P18; VIII §2.6, §7.3 | Novelty đề xuất là tích hợp truy vết và giới hạn rõ | Đối chiếu S09–13/S19–22; evidence pipeline dự án | RQ1–6 | Không first ever; contribution còn phải audit thực hiện |
| C32 | P19/P21; VIII §4.1 | Valuation=min(reference,DEX); history oracle là chứng cứ khác | engine/run.py tại ba62c749; E09/E11 | RQ1/2/4 | Synthetic feedback không là Aave oracle thật |
| C33 | P19/P20/P21; VIII §4.3 | HF audit xác nhận borrower mới HF≥1→HF<1 trước vòng 2 | E03/E08; 8 path P0, ca tất định và 10 mẫu phân tầng MC | RQ1/3 | Chỉ simulated endogenous eligibility; không phải cascade lịch sử |
| C34 | P19; II Chương 4; III §5.5 | Reposition cập nhật ±liquidityNet qua tick | Mã ba62c749; tick/round-trip tests; E01 | RQ2/4 | Không giữ lỗi L cũ; funded swap/fork chưa xác nhận |
| C35 | P19/P20; III §5.6 | USDC seize/dust/quote chưa repricing toàn diện tại ba62c749 | liquidation.py; schemas.py; uniswap_v3.py | RQ5 | Đã kiểm version; valuation sensitivity không full-depeg validation |

## 3. Giữ nguyên sáu câu hỏi nghiên cứu

RQ đối chiếu nguyên văn giữa V2, bản 2b9a29f5 và METHODOLOGY.md tại ba62c749, không thêm RQ Terra/network. Narrative RQ hiện tại chưa là numerical freeze; ưu tiên artifact v2/Level-3 theo locator E. Dưới đây giữ nguyên nghĩa và nội dung gốc của RQ; glossary cung cấp tên tiếng Việt khi biên tập.

1. **RQ1.** Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)?
2. **RQ2.** Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt?
3. **RQ3.** Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý?
4. **RQ4.** Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi?
5. **RQ5.** Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset?
6. **RQ6.** Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk?

| RQ | Nguồn lõi | Biến và phép kiểm đề nghị | Mã/bằng chứng dự án cần đọc | Quy tắc diễn giải |
|---|---|---|---|---|
| RQ1 | S03/S05/S06/S09/S10/S11/S13/S24 | Grid cơ sở; 4/60 tail cells depth2; Severe 8/200 và 280/10k; HF paths | E02/E03/E04/E08; direct-shock cohort/prior-wave valuation | Khác miền/phân phối; Severe 10k không depth≥3; model-conditioned |
| RQ2 | S07/S08/S10/S11 | Tick depth/haircut; intrawave riêng post-arbitrage | E01/E02/E07; code/Quoter initial-state | Haircut là giả định, đặc biệt 90/95%; không observed LP withdrawal |
| RQ3 | S06/S09/S10/S12/S13/S22 | Vốn/capacity/gas; first liquidation timestamp khác recovery | E01/E07; P0 v2 rq3_reaction_delay.* và rq3_capital_constraint.* | Recovery 0 không delay 0; no recycle; delayed batch cần HF audit |
| RQ4 | S07/S10/S14 | Capacity 0–100%; intrawave ~0,108794%, residual giảm về ~0 | E01/E07; arbitrage_toward cập nhật L | Impact tức thời không bị xóa; price teleportation, chưa funded swap |
| RQ5 | S02/S03/S05/S14/S15/S16 | q_USDC/USD, debt/HF; USD/USDC riêng | P0 v2 rq5_usdc_depeg.*; code ba62c749 | Valuation riêng; conversion/redemption/liquidity/confidence chưa đầy đủ |
| RQ6 | S04/S06/S09/S12/S22 | LTV ex ante; LT; bonus; unliquidated theo scenario LT | E01/E07; P0 v2 rq6_*; legacy chỉ comparison | Không forecast governance/re-underwrite; dùng metric v2 |

Terra: S17/S18/S19/S21/S30. Network: S25–S28. Hai extension hỗ trợ đối chiếu cơ chế/phương pháp, không trả lời thay sáu RQ.

## 4. Chứng cứ dự án không được thay bằng nguồn học thuật

| Loại phát biểu trong V2/Word | Nguồn thích hợp | Việc P2 đã làm | Điều chưa xác nhận |
|---|---|---|---|
| 500 ứng viên/454 xác minh/109 cohort | Snapshot manifest, account reads, data quality tại commit | Đọc báo cáo; phân biệt tỷ lệ xác minh với market coverage | Không truy RPC lại, không chứng nhận completeness |
| Grid cơ sở chưa depth≥2; tail grid/MC có depth2 | P0 v2, Level-3 và HF/path audit | Phân biệt grid32/cell60/path200/path10000 | Không giữ old zero-cascade blanket; chưa xác nhận thị trường |
| 1.776 giờ/277.342 Terra swaps | Versioned dataset/provenance và parser audit | Đọc báo cáo và giới hạn V2 | Không gán cỡ mẫu này cho Liu et al. hoặc tự xác minh raw chain |
| Khớp giá/lệch timing/cảnh báo ban đầu muộn | Historical validation/early-warning outputs | Giữ tách reconstruction và prediction | Không học thuật source nào cấp validation thay pipeline |
| Điểm centrality/độ trung gian | Graph schema/build, aggregation policy, metric output | Đọc schema/metrics, ghi scope typed aggregated graph | Không chứng nhận topology đầy đủ toàn DeFi |
| Composite exposure tail / tần suất cascade | Metric units, generator, seed/checkpoint | Đọc code/artifact; tính Wilson; kiểm checkpoint repair | Không realized loss/real probability; legacy runtime unavailable |

## 5. Bằng chứng dự án có phiên bản và đối chiếu lý thuyết

E01–E12 là **alias tra cứu do P2 đặt**, không phải bài học thuật mới hoặc result ID thay registry P1. Các đường dẫn được đối chiếu tại HEAD [ba62c749](https://github.com/Doquocdung1609/DeFiStress/tree/ba62c74950a72751e0030527836082da0c7622ef).

Tiền tố P0 = `data/processed/research_final/validation_audit/corrected_run_v2/`; L3 = `data/processed/research_final/level3_extension/`; FIX = `data/processed/research_final/level3_p1_targeted_repair/`. Phân biệt nguồn giao thức S, facts code, quan sát chuỗi, output mô phỏng và audit sửa. P2 đọc artifact, đối chiếu số học/logic; không tái thực thi chain, fork hoặc batch Monte Carlo lớn. Manifest/hash định danh bundle; checkpoint legacy vẫn cần external attestation và không có duration lịch sử.

| Alias | Loại chứng cứ | Đường dẫn và trường/vị trí tại commit trên | Đối chiếu/kết quả được phép dùng | Trạng thái và giới hạn |
|---|---|---|---|---|
| E01 | Mã/kiểm tra P0 | `sim/dex/uniswap_v3.py::arbitrage_toward`; `sim/tests/test_uniswap_v3.py` tick/round-trip tests; P0 `manifest.json` | Reposition cập nhật L qua tick; model `0.1.0-aave-v3.10-metric-semantics` | Lỗi L cũ đã sửa; còn price teleportation/fork boundary |
| E02 | Mô phỏng deterministic | L3 `deep_stress/deterministic_grid.csv`; `tables/deterministic_grid_depth_counts.csv` | 60 cells: depth 0/1/2 = 18/38/4; bốn cell shock −40/−50 × haircut 90/95; depth≥3 = 0 | P2 đếm lại CSV; 4/60 là tỷ lệ ô được chọn, không xác suất |
| E03 | Mô phỏng/audit P0 | P0 `severe_mc_depth2_path_audit.json`: all_paths_pass, audit_rules, later_wave_checks | Severe 8/200; Wilson 2,0406%–7,6932%; HF direct shock≥1 rồi prior-wave<1 | Wave 2 nội sinh trong các path đã kiểm; không historical causation |
| E04 | Mô phỏng Level-3 trong bundle | L3 `deep_stress/monte_carlo_batches.json`; FIX `monte_carlo/checkpoint_validation.json` | 280/10.000 depth≥2; Wilson 2,4943%–3,1419%; depth≥3=0; 13k batch identities, 0 duplicate | Prefix lồng không cộng; 10k reused trong repair, 0 large path chạy lại; legacy duration unavailable |
| E05 | Negative finding mô phỏng | L3 `deep_stress/monte_carlo_batches.json`: Low Liquidity prespecified, actual_runs 1000 | 0/1.000 depth≥2; Wilson upper 0,3827% | Không rủi ro zero; khác population/scenario Severe |
| E06 | Diagnostics/cap | L3 `deep_stress/numerical_diagnostics.json`; `deep_stress/wave_cap_comparison.csv` | cap 100/horizon 120; max attained 2; cap hits 0; Severe baseline cap sweeps depth 1 | Configured ceiling khác observed depth; không 100 historical rounds |
| E07 | Semantics/outputs P0 | `docs/research_final/P0_COMMANDER_REVIEW_PACKET.md`; P0 `before_after_v1_v2.json`; `rq_completion/rq3_reaction_delay.csv`, `rq6_liquidation_threshold.csv` | Intrawave vs residual; recovery 0/seconds/null; scenario-LT unliquidated debt | `max_price_impact` alias của post spread; không dùng narrative RQ4 cũ |
| E08 | Trace mô phỏng | E03; FIX `monte_carlo/wave2_eligibility_audit.json`, `sample_reproduction.json` | P0 path 5: 1,0041608→0,9990975; deterministic: 1,0211716→0,9980426; 10/10 strata newly eligible; 21/21 rows reproduce | Bằng chứng simulated eligibility; không historical causation |
| E09 | Quan sát chuỗi và census Pool | L3 history; FIX `historical/census_reconciliation.json` | Tuần định nghĩa Sept 1–7 UTC: census 28; 27 Graph candidates đều RPC-match; 1 Graph omission ở block 25888740 | Recall quan sát 27/28 trong census Pool; không census borrower |
| E10 | Clustering và control audit | L3 episode selection; FIX `historical/control_window_audit.json` | Cụm 5 phút=22; 1/15/30 phút=24/20/19; 4 pool, 5 episode, 40 tổ hợp, 928 chunks; 5/5 control ±30 phút không liquidation | Cụm thời gian khác simulated wave; cửa sổ không loại mọi confounder |
| E11 | Receipt route/association tier | `sim/research/historical_events.py::classify_linkage`; FIX `historical/linkage_route_audit.json` | 1 direct WETH route; 2 same-transaction co-occurrence; 23 same-block; 1 time-window; 31.489 swaps trong selected windows | Trace unavailable; direct receipt route không tự chứng minh price causality |
| E12 | Fork/provenance gate | L3 fork; FIX `manifest.json`, `evidence_matrix.json`, `claim_ledger_repair.json` | 0 fork transaction, UNAVAILABLE; artifact bundle 6fcda469; gate audit PASS/LIMITED | External attestation checkpoint; review state chờ Commander, không scientific lock |

**Liên hệ literature.** E01/E02 kiểm tính nhất quán cơ chế thanh khoản S07/S08 trong mã; E03/E04/E08 minh họa phản hồi khả dĩ S10/S11 trong mô hình với oracle abstraction. E09–E11 xác nhận một tuyến WETH theo biên nhận giao dịch và các liên hệ thời gian, nhưng chưa xác lập tác động giá nhân quả hoặc lây lan lịch sử. S13 hỗ trợ giữ đối chứng cú sốc giá chung; S21 hỗ trợ scheduling/provenance rõ ràng, không cấp validity tự động. P1 crosswalk cuối phải nhận đúng evidence tiers và corrected metric semantics, không dùng tên raw tier DIRECT để phát biểu mạnh hơn chứng cứ.

## 6. Kiểm soát suy luận và trạng thái P1

Nguồn thực nghiệm hỗ trợ tính khả dĩ của cơ chế; official docs/code hỗ trợ semantics; mã dự án mô tả implementation; kết quả dự án cần artifacts. Không hoán đổi bốn cấp chứng cứ này. Với phản thực, thay biến và giữ các biến còn lại chỉ định quan hệ **trong mô hình**; empirical causal identification cần thiết kế đối chứng, giả định và dữ liệu riêng.

Gói sửa có mục tiêu đã hoàn thành audit dòng WETH theo receipt, census/control và checkpoint accounting. Xác nhận 13.000 định danh batch độc lập, 0 trùng; 200/1.000/5.000 là prefix lồng trong primary 10.000 nên không cộng thành 16.200 execution. Trong invocation sửa, 10.000 hàng được tái sử dụng và 0 large path chạy lại; 21/21 mẫu độc lập tái hiện. Vẫn giữ external attestation của checkpoint legacy, `UNAVAILABLE` cho fork và `UNAVAILABLE_NOT_EMBEDDED_IN_LEGACY_CHECKPOINT` cho duration. Commander scientific sign-off còn pending; invalid epoch attempt đứng ngoài kết luận.

Reviewer cần kiểm: 35 claim IDs và nguồn; sáu RQ nguyên văn; nguồn/giới hạn không đổi; không còn lỗi L/recovery/LT cũ trong mô tả hiện hành; giữ simulated endogenous wave 2 với HF audit; history chỉ receipt route/association, không causal cascade; tail statistic không economic loss. Review lần cập nhật nằm trong P2_VERSION_RECONCILIATION.md; không thay Commander/P0/P1 sign-off.
