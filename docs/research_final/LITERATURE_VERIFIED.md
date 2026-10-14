# Tổng quan tài liệu đã xác minh cho DeFiStress

**Bản đối chiếu P2 ngày 14/10/2026 cho [issue #4](https://github.com/Doquocdung1609/DeFiStress/issues/4) và [Draft PR #9](https://github.com/Doquocdung1609/DeFiStress/pull/9). Nền literature đã được Commander chấp nhận có giới hạn; bản cập nhật phiên bản chờ Commander duyệt lại.** Đây là tổng quan và hồ sơ chứng cứ, không phải báo cáo Word final, kiểm toán mã đầy đủ hoặc xác nhận kết quả Mainnet. Ba file nền đi kèm là `REFERENCE_EVIDENCE_MATRIX.md`, `APA_REFERENCES_VERIFIED.md` và `TERMINOLOGY_VI.md`; bản đối chiếu thay đổi nằm trong `P2_VERSION_RECONCILIATION.md`.

## 1. Tài liệu đầu vào và quy trình nghiên cứu

Đã đọc bản hiện hành **DeFiStress_NOI_DUNG_NGHIEN_CUU_V2.md** (tạo/sửa 13/10/2026, 09:40:40 UTC, 432 dòng), báo cáo Word cũ và sáu tài liệu đính kèm còn lại. Đã đọc báo cáo, phương pháp, hạn chế, ma trận RQ, chất lượng dữ liệu, khả năng tái lập và mã cốt lõi tại [commit nghiên cứu 2b9a29f5](https://github.com/Doquocdung1609/DeFiStress/tree/2b9a29f5e8c0c8dd910b7d65428fb1d57646b06b). Đây là căn cứ lịch sử của lần bàn giao 13/10, không còn là phiên bản để mô tả mã hay kết quả nhạy với Uniswap.

Lần cập nhật cuối đã đọc [chỉ đạo Commander trên PR #9](https://github.com/Doquocdung1609/DeFiStress/pull/9#issuecomment-6161682917), mã, báo cáo và artifact tại HEAD [ba62c749](https://github.com/Doquocdung1609/DeFiStress/tree/ba62c74950a72751e0030527836082da0c7622ef). Căn cứ số liệu Aave trước mở rộng vẫn là `validation_audit/corrected_run_v2/`; nghiên cứu mở rộng gốc là `level3_extension/`; sửa có mục tiêu nằm tại `level3_p1_targeted_repair/`, implementation `2dbc7d55`, artifact bundle `6fcda469`. Mã mô hình giữ `0.1.0-aave-v3.10-metric-semantics`. P2 đọc artifact và đối chiếu phép tính/mã; không chạy lại RPC, fork hay batch Monte Carlo lớn.

Theo gói sửa có mục tiêu và [chỉ đạo Commander mới nhất](https://github.com/Doquocdung1609/DeFiStress/pull/9#issuecomment-6161682917), các kiểm tra census Pool, receipt route, cửa sổ đối chứng, checkpoint và điều kiện đủ vòng 2 đã hoàn thành ở mức artifact. Trạng thái vẫn là **chờ Commander duyệt lại, không phải scientific lock**. Một số bảng narrative cũ không còn là căn cứ cho các claim đã sửa; dùng artifact `corrected_run_v2`, `level3_extension` và `level3_p1_targeted_repair` theo locator E. Terra giữ ca riêng; nguồn S01–S30 và hàng chờ U01–U08 giữ nguyên phạm vi truy cập ngày 13/10.

Tìm kiếm có mục tiêu, không tự gọi là systematic review: Aave liquidation/close factor/oracle; Uniswap V3 tick/liquidity/price impact; DeFi contagion/fire sale; ABM/ODD; Monte Carlo/rare event interval; stablecoin/redemption; Terra/Anchor run; multilayer/centrality. Ưu tiên nhà xuất bản, kho bản tác giả, ngân hàng trung ương và mã giao thức. Phạm vi tìm đến ngày 13/10/2026. Chọn nguồn có danh tính và luận điểm truy hồi được; loại nội dung quảng bá không có cơ sở, thống kê không kiểm được mẫu số, hoặc diễn giải vượt phần đã đọc.

Phân loại riêng công trình có phản biện, working paper, sách, báo cáo chính sách, tài liệu giao thức và mã triển khai. Bản tiền nhiệm và bản công bố cùng nghiên cứu không được tính thành hai bằng chứng độc lập. Mỗi S có DOI/URL, ngày kiểm, vị trí chứng cứ và mức truy cập trong ma trận. `VERIFIED_ABSTRACT` chỉ duyệt luận điểm nằm trong abstract; `SOURCE_NOT_VERIFIED` giữ cho nội dung không truy cập được. DOI khớp metadata và DOI resolver mở thành công là hai việc khác nhau. Không sao chép các tỷ lệ trong bản nháp để biến thành phát hiện của literature.

Tài liệu giảng dạy giải thích nền tảng toán/mô phỏng, nhưng không thay cho bằng chứng học thuật: `UniswapCurveLatex.pdf` có CPAMM/StableSwap và mục giới thiệu V3; hai PPTX có đồ thị và kiểm chứng mô phỏng; slide trò chơi giải thích tương tác chiến lược. P2 không áp SIR, song đề tù nhân, giả định cân bằng Nash hoặc công thức CPAMM vào engine nếu mã và dữ liệu không triển khai cơ chế đó.

## 2. Tổng hợp cơ sở lý thuyết và bằng chứng

### P01 Tính liên thông tạo kênh truyền rủi ro

Schär (2021) mô tả khả năng kết hợp dịch vụ tài chính trên hợp đồng thông minh. FSB (2023) lưu ý liên kết giữa DeFi, nền tảng tập trung và stablecoin. Từ đó, nghiên cứu có cơ sở phân tích đường truyền từ khoản vay sang nơi thực thi giao dịch. Tuy nhiên, đồ thị hai giao thức chỉ biểu diễn mạng con được chọn; nó chưa đo rủi ro toàn hệ sinh thái hoặc chứng minh tác động lên tài chính truyền thống. [S01, S29]

### P02 Điều kiện thanh lý và tham số rủi ro Aave

Tài liệu Aave phân biệt giới hạn vay ban đầu LTV với LT dùng trong hệ số sức khỏe. HF dưới 1 tạo điều kiện thanh lý; việc thực hiện còn phụ thuộc giao dịch hợp lệ và tác nhân có động cơ. Close factor, ngoại lệ vị thế nhỏ, xử lý dư nợ nhỏ, E-Mode và phí cần gắn với phiên bản triển khai. Tài liệu hiện hành và mã chuẩn S06 là căn cứ giải thích, nhưng chưa xác nhận mọi quy tắc áp dụng tại block 26.045.352. Không ghi “Aave V3 luôn thanh lý 50%”. [S02–S06]

### P03 Thanh lý có động cơ kinh tế nhưng không xảy ra tự động về thời gian

Qin và cộng sự (2021) nghiên cứu Aave, Compound, MakerDAO và dYdX, hệ thống hóa cơ chế và rủi ro của người vay/tác nhân thanh lý. Kết quả hỗ trợ đưa chi phí thực thi và ưu đãi thanh lý vào mô hình, đồng thời xét tổn thất của người vay. Phạm vi giao thức/thời kỳ của bài không trùng mặc nhiên với Aave V3 năm 2026. Trong DeFiStress, lợi nhuận ròng và khả năng huy động vốn phải là điều kiện thực thi, thay vì cho mọi vị thế HF<1 được xử lý tức thì. [S09]

### P04 Thanh khoản Uniswap V3 phụ thuộc khoảng giá

White paper gốc mô tả thanh khoản tập trung, giao dịch trong một khoảng và cập nhật thanh khoản khi qua tick. Vì thế TVL không thay thế được độ sâu có thể thực thi quanh giá đang xét. DeFiStress cần dữ liệu tick, thanh khoản hoạt động, phí và đúng chiều token. Mã `SqrtPriceMath` là căn cứ kỹ thuật cho phép tính lượng giao dịch; đối chiếu vài phương trình chưa chứng minh toàn bộ đường trạng thái pool hoặc phép làm tròn tương đương EVM. [S07, S08]

### P05 Áp lực bán tài sản thế chấp và giới hạn suy luận lây lan

Lehar và Parlour (2022) dùng giao dịch thanh lý trên Aave/Compound, phân biệt nguồn vốn tồn kho và flash loan, ghi nhận tác động giá tại nhiều DEX và trao đổi khác. Bài cung cấp cơ sở cho khả năng phản hồi bán tài sản–giá–rủi ro khoản vay. OECD (2023) ghi nhận quan hệ dương giữa thanh lý và biến động giá sau đó; tác giả nói rõ hành vi liquidator được suy ra gián tiếp. Tương quan, đồng thời chịu cú sốc giá chung và phản hồi nội sinh phải được phân biệt. [S10, S11]

### P06 Những kết quả khác nhau không thể gộp thành quy luật phổ quát

Chiu và Danisman (2026), trên dữ liệu Aave V3, không tìm thấy bằng chứng có ý nghĩa thống kê về tác động giá kéo dài sau điều chỉnh benchmark trong thiết kế của họ. Điều này không phủ định tác động rất ngắn hạn trên DEX mà S10 xem xét. Khác giao thức/thời kỳ, nơi giao dịch, tần suất và đối chứng có thể cho kết quả khác nhau. Do đó, “có tác động giá nhưng chưa có vòng thanh lý nội sinh thứ hai” là kết quả có thể diễn giải; nó không xác nhận Aave an toàn tuyệt đối. [S10, S13]

### P07 Thiết kế thanh lý có đánh đổi

Tian và Zhu (2025) kết hợp mô hình lý thuyết với dữ liệu Ethereum để so sánh fixed spread và đấu giá. Ưu thế của đấu giá phụ thuộc chi phí tham gia và cạnh tranh. Bài hỗ trợ kiểm tra mức thưởng/chi phí trong RQ3 và RQ6, không cho phép kết luận một thiết kế luôn tốt hơn hoặc rằng Aave hiện dùng đấu giá. Thay đổi LTV trên dư nợ đóng băng cũng không tự tạo lại hành vi vay mới. [S12, S04]

### P08 Kinh doanh chênh lệch giá có điều kiện thực thi

Lyons và Viswanath-Natraj (2023) nghiên cứu cơ chế duy trì neo, chủ yếu qua Tether, và vai trò tiếp cận giao dịch với tổ chức phát hành. Đây là bằng chứng cho tầm quan trọng của thiết kế arbitrage, không phải hiệu chỉnh tốc độ hồi giá WETH trên Uniswap. DeFiStress đang dùng một quy tắc hồi giá đơn giản; tỷ lệ capacity 50% là tham số phản thực của engine, không phải lượng vốn thị trường đo được. [S14; mã dự án]

### P09 Stablecoin cần được đặt đúng bên bảng cân đối

Kosse và cộng sự (2023) phân tích tính ổn định và khả năng quy đổi của stablecoin. Thông cáo Circle tháng 3/2023 cho thấy ngân hàng giữ dự trữ là một kênh riêng cần xét; đây là lời công bố của tổ chức phát hành. Với WETH thế chấp cố định theo USD và USDC là nợ, giảm giá USDC làm giá trị nợ giảm về mặt đại số, trong khi quy đổi/thanh khoản có thể xấu đi. Kết quả RQ5 chỉ về kênh định giá nợ, không mô phỏng đầy đủ một sự kiện mất neo. [S15, S16, S02–S05]

### P10 Terra là ca về rút vốn và phản hồi tiền tệ

Liu, Makarov và Schoar (2026) dùng dữ liệu blockchain để phân tích tương tác giữa tiền tạo ra với khuyến khích, khả năng quan sát giao dịch và sự tập trung nhà đầu tư. Nhà đầu tư lớn phản ứng sớm hơn là một cơ chế được bài nêu, không đủ để quy toàn bộ sự kiện cho một tác nhân tấn công. Bản NBER 2023 là tiền nhiệm của cùng nghiên cứu. Terra/Anchor và UST–LUNA có cơ chế khác Aave, nên không chuyển sai số khớp lịch sử Terra thành độ chính xác của engine Aave. [S17, S18]

### P11 ABM phù hợp với tương tác nhưng mức không đồng nhất phải đúng mã

Bookstaber (2017) và Axtell–Farmer (2025) trình bày ABM trong tài chính, nhấn mạnh tương tác và phản hồi của tác nhân. Cơ sở này hỗ trợ lựa chọn phương pháp, không xác nhận tham số DeFiStress. Nhánh Aave được đọc có danh mục người vay khác nhau nhưng một liquidator và một arbitrageur đại diện. Vì vậy không mô tả nó như thị trường nhiều bot cạnh tranh có hành vi được ước lượng thực nghiệm; nhánh Terra với các nhóm tác nhân phải được thuyết minh riêng. [S19, S20; mã dự án]

### P12 Minh bạch mô hình và nguồn thực hành ngành

Grimm và cộng sự (2020) đề xuất ODD để nối mục đích, trạng thái, trình tự xử lý và mô hình con với mã. Gauntlet (2021) công bố dùng mô phỏng tác tử/Monte Carlo cho tham số Aave V2, nhưng bài forum không cung cấp toàn bộ định nghĩa để tái lập. DeFiStress có thể kế thừa cách đặt vấn đề stress về thanh khoản, gas và động cơ, không tuyên bố đã tái tạo hay vượt phương pháp Gauntlet. [S21, S22]

### P13 Monte Carlo đo bất định trong mô hình

Sách Glasserman cung cấp nền tảng Monte Carlo trong tài chính; P2 chỉ truy cập phần preview và metadata. Trong engine được đọc, mỗi lần chạy nhiễu hóa shock/haircut/gas rồi gọi lại mô hình tất định; đây không phải mô phỏng đầy đủ đường giá ngẫu nhiên theo thời gian. Gói sửa xác nhận 13.000 định danh batch độc lập, không trùng lặp; các stage 200/1.000/5.000 là tiền tố lồng trong batch chính 10.000 nên không cộng thành số đường chạy mới. Trong lần sửa, 10.000 hàng được tái sử dụng, không có batch lớn nào chạy lại; 21/21 mẫu tái hiện khớp. Thời lượng chạy lịch sử 10.000 path không được lưu trong checkpoint cũ và giữ `UNAVAILABLE_NOT_EMBEDDED_IN_LEGACY_CHECKPOINT`. Tần suất cascade vẫn phụ thuộc snapshot, cấu trúc, phân phối và quy tắc gán nhãn. [S23; E04/E08/E12]

### P14 Wilson và tần suất có điều kiện cần đúng phiên bản

S24 có tiêu đề lịch sử **Agresti Coull Confidence Limits**, nhưng phần Note phân biệt Wilson với adjusted Wald/Agresti–Coull và ghi default Wilson. Tên phép tính ở đây là **Wilson score interval**, không đổi theo tên trang. Từ artifact mới: Severe 8/200 có khoảng hai phía 95% 2,0406%–7,6932%; Level-3 Severe 280/10.000 có 2,4943%–3,1419%; Low Liquidity 0/1.000 có cận trên 0,3827%. P2 tính lại các khoảng này từ k/n, không suy ra xác suất khủng hoảng ngoài đời. Khoảng chỉ phản ánh lấy mẫu có điều kiện, chưa chứa bất định cấu trúc/tham số. Ví dụ 0/200 trước đây không còn được dùng làm kết quả Severe hiện hành. [S24; artifact v2/Level-3, E03–E05]

### P15 Mạng nhiều lớp và centrality là hai tầng mô hình khác nhau

Kivelä và cộng sự (2014) phân biệt các cách biểu diễn multilayer, multiplex và mạng phụ thuộc. Battiston–Martinez-Jaramillo (2018) đặt mạng trong stress testing tài chính. Đồ thị có nhiều loại nút/cạnh có thể là mạng dị thể nhiều quan hệ; chỉ gắn nhãn lớp chưa chứng minh đã dùng đầy đủ biểu diễn node–layer. DeFiStress tính centrality trên đồ thị gộp, nên cần công bố phép gộp và gọi đúng cấp độ phân tích. [S25, S26; mã dự án]

### P16 Vị trí cầu nối không tương đương tác động tổn thất

Freeman (1977) định nghĩa độ trung gian theo đường đi ngắn nhất. DebtRank của Battiston và cộng sự (2012) xây dựng thước đo tác động distress gắn với phơi nhiễm tài chính. DeFiStress không triển khai DebtRank trong mã được đọc. Betweenness cao trong đồ thị gộp hoặc điểm cạnh chuẩn hóa không phải xác suất lây lan hay xếp hạng rủi ro toàn DeFi. Đó là chỉ báo cấu trúc cần kiểm bằng thí nghiệm cơ chế nếu muốn phát biểu về nhân quả. [S27, S28]

### P17 Kiểm chứng lịch sử cần bảo vệ ranh giới thông tin

Bergmeir và cộng sự (2018) bàn về CV cho mô hình tự hồi quy, với điều kiện sai số không tương quan. Bài không đưa ra quy tắc phổ quát rằng mọi chuỗi thời gian phải cấm K-fold, cũng không chứng minh quy trình Terra không rò rỉ dữ liệu. P2 đề nghị kiểm cutoff, dữ liệu đầu vào, tham số đóng băng và phân biệt reconstruction dùng thông tin khủng hoảng với cảnh báo tại thời điểm. Đó là yêu cầu thiết kế nghiên cứu và kiểm mã của dự án. [S30, S21; báo cáo dự án]

## 3. Ma trận đối thoại với nghiên cứu thực nghiệm

| Nghiên cứu | Câu hỏi và dữ liệu | Phương pháp đã xác minh | Kết quả sử dụng | Giới hạn và liên hệ DeFiStress |
|---|---|---|---|---|
| S09 Qin et al. | Cơ chế thanh lý trong bốn giao thức Ethereum | Đo giao dịch, so sánh thiết kế | Động cơ và chi phí người vay | Bản 2021, không đặc tả V3 2026; RQ3/6 |
| S10 Lehar–Parlour | Bán thế chấp Aave/Compound tại nhiều DEX | Đo tác động giá tần suất cao | Kênh bán tài sản và phản hồi khả dĩ | Không cung cấp ngưỡng shock của snapshot mới; RQ1/2/4 |
| S11 OECD | Thanh lý và biến động giá sau sự kiện | Giao dịch, hồi quy volatility | Quan hệ thống kê dương | Hành vi liquidator suy gián tiếp; RQ1/2 |
| S12 Tian–Zhu | Cách thiết kế ảnh hưởng tác động giá | Lý thuyết và dữ liệu Ethereum | Vai trò chi phí tham gia | Không tối ưu bonus hiện hành; RQ3/6 |
| S13 Chiu–Danisman | Đòn bẩy và thanh lý Aave V3 | Dữ liệu giao dịch, benchmark giá | Không tìm tác động kéo dài có ý nghĩa trong thiết kế | Khác hiệu ứng DEX tức thời; RQ1/3/5 |
| S14 Lyons–Viswanath-Natraj | Thiết kế arbitrage giữ neo | Giao dịch treasury/nhà đầu tư | Khả năng tiếp cận arbitrage quan trọng | Tether không thay cho WETH/USDC hoặc tham số engine; RQ4/5 |
| S17 Liu et al. | Rút vốn Terra tháng 5/2022 | Dữ liệu blockchain chi tiết | Quan sát hành vi, tập trung, khuyến khích | Giải thích ca lịch sử, không validation Aave; extension Terra |

Các tóm tắt trên chỉ dùng phần đã đọc/abstract. Không bổ sung cỡ mẫu, tỷ lệ tác động hay mức giảm rủi ro chưa kiểm bảng gốc.

## 4. P18 Khoảng trống và đóng góp có thể bảo vệ

Literature đã nghiên cứu thanh lý, tác động giá, ABM và mạng tài chính. P2 không xác lập rằng “chưa có ai nối lending với DEX” hoặc DeFiStress là công trình đầu tiên. Đóng góp phù hợp là **tích hợp có thể truy vết**: trạng thái cùng block; quy tắc thực thi cụ thể; kiểm định có điều kiện sáu RQ; bảng kết quả gắn input/hash/seed; công bố kết quả âm và sai khác so với giao thức. Terra bổ sung ca lịch sử riêng và mạng hỗ trợ giải thích cấu trúc. Mức đóng góp này phải được kiểm bằng sản phẩm/mã/bằng chứng dự án, không mượn uy tín bài học thuật để chứng minh thực hiện thành công. [S09–S13, S19–S22, S25–S27; báo cáo dự án]

Các khoảng trống còn mở là đường truyền DEX tới oracle, nguồn vốn có thể tái sử dụng/flash loan, nhiều liquidator cạnh tranh, tác động rút LP và nhiều venue, cấu trúc phụ thuộc giữa shock/thanh khoản/gas, kênh quy đổi/settlement stablecoin và độ bền qua nhiều snapshot. Đây là hướng cần kiểm chứng, chưa phải các cơ chế đã triển khai.

## 5. P19 Ánh xạ toán học với mã thực tế và giới hạn

Các biểu thức sau mô tả **mã tại HEAD `ba62c749`**; bản `2b9a29f5` chỉ được giữ trong bảng đối chiếu lịch sử. Chúng không phải trích nguyên văn bài nghiên cứu.

Với danh mục đúng nguồn giá:

\[
HF_i=\frac{\sum_j c_{ij}p_j^{oracle}LT_j}{\sum_k d_{ik}p_k^{oracle}}.
\]

Trong `BorrowerPosition.health_factor`, danh mục Aave được thu gọn còn WETH và giá trị gộp tài sản khác. RQ5 dùng mẫu số \(d_{USDC}q_{USDC/USD}+D_{other,USD}\). Với tử số cố định, đạo hàm HF theo \(q\) âm khi dư nợ USDC dương. Điều này xác định riêng dấu của kênh định giá; chưa xác nhận việc mô phỏng thực thi khi USDC mất neo. [S02–S06; `sim/schemas.py`]

Trong một khoảng Uniswap với \(s=\sqrt{P_{raw}}\), token1 vào ròng làm \(s'=s+\Delta y/L\), lượng token0 ra là \(L(1/s-1/s')\). Đổi decimal/chiều token trước khi diễn giải USDC/WETH. Qua tick phải cập nhật L theo đúng hướng. Mã tại HEAD `ba62c749` đã duyệt tick theo hướng đi và cộng/trừ `liquidityNet` trong `arbitrage_toward`; P0 có regression đi qua tick và round trip. Giới hạn còn lại là đặt lại giá theo tỷ lệ spread mà không thực thi funded swap, không phải lỗi giữ L cố định của phiên bản cũ. [S08; `sim/dex/uniswap_v3.py`]

| Cơ chế | Mã/bằng chứng tại HEAD ba62c749 | Diễn giải hiện hành và giới hạn |
|---|---|---|
| Oracle và phản hồi | `valuation_price=min(reference_price,pool.spot_price)` | Liên kết giá đánh giá lại bảo thủ, đồng bộ do mô hình đặt ra. Không phải feed Aave/Chainlink quan sát được; event history không tự xác nhận phép liên kết này. |
| Thanh lý | `plan_liquidation`; HF, close factor, debt/collateral cap | Xấp xỉ danh mục; chưa ngang EVM. Pin bytecode/reserve/portfolio tại block vẫn cần thiết; tài liệu chuẩn S06 không thay fork. |
| USDC trong lượng thu giữ | `seize=repay*bonus/weth_price` vẫn không nhân q_USDC/USD | Với repay nominal USDC, WETH giá USD/WETH, đơn vị chưa nhất quán khi q≠1; dust nợ dùng nominal USDC. Đã kiểm lại ở HEAD ba62c749, giữ RQ5 như kênh định giá nợ riêng. |
| Liquidator đại diện | Một liquidator, vốn tổng không recycle, capacity reset mỗi bước | Kế hoạch vượt vốn có thể bị bỏ nguyên khối. Không tương đương tổng vốn thực có thể huy động/flash loan hoặc nhiều bot cạnh tranh. |
| Shock/arbitrage và tick | `arbitrage_toward` duyệt initialized ticks, cập nhật L bằng ±liquidityNet | Lỗi không cập nhật L đã sửa. Vẫn là price teleportation, chưa funded swap/fork sau shock; Quoter initial state không chứng nhận repositioned states. |
| Đợt và cascade | `cascade_depth` còn từ vòng có execution; audit HF kiểm điều kiện đủ riêng | Không suy causal cascade chỉ từ index. P0 xác nhận tám path Severe; gói sửa xác nhận ca tất định HF 1,0211716→0,9980426 và 10/10 mẫu phân tầng Monte Carlo có borrower mới mất an toàn trước vòng 2. Đây là **vòng 2 nội sinh trong mô hình**, không phải cascade quan sát trên Ethereum. |
| Impact trước/sau arbitrage | `max_intrawave_liquidation_price_impact` / `max_post_arbitrage_spread` | Điểm đo khác nhau. `max_price_impact` deprecated alias của post-arbitrage spread; không dùng nó để nói forced-sale impact tức thời biến mất. |
| Recovery và độ trễ | tolerance 0,5%; first-return semantics; delay trước execution | `0` = chưa từng vượt tolerance, số giây = first return sau vượt, `null` = chưa hồi trong horizon. Recovery 0 không bằng liquidation delay 0. Không có path giá mới trong lúc chờ. |
| Nợ xấu và nợ chưa thanh lý | `max(debt_value-collateral_value,0)`; unliquidated debt dùng scenario LT override | Shortfall theo giá mô hình, không realized loss. Lỗi dùng LT cũ đã sửa; `unliquidated_debt_legacy_recorded_lt` chỉ để so sánh có nhãn. |
| Monte Carlo | Nhiễu normal shock/haircut, lognormal gas; clipping; checkpoint stages Level-3 | Lấy mẫu tham số, không path giá đầy đủ. 90/95% haircut là đuôi phản thực chưa quan sát. Gói sửa tách đúng số hàng kiểm tra, checkpoint tái sử dụng và path chạy trong lần hiện tại; giới hạn external attestation của checkpoint cũ vẫn phải công bố. |
| Chỉ tiêu đuôi | `bad_debt+total_liquidated_debt`, mean các giá trị ≥ q95 | **Composite exposure tail statistic**, không realized loss/market ES. Repayment không phải tổn thất; USD/USDC khác nhau khi depeg, ties có thể chọn hơn 5% mẫu. |
| Network | `MultiDiGraph` dị thể; centrality trên graph gộp | Gộp max strength/cặp nút; betweenness/eigenvector hiện bỏ weight. Không phải supra-adjacency multilayer, DebtRank hoặc xác suất lây lan. |
| Lịch sử Aave–Uniswap | `classify_linkage` đã dùng receipt Transfer route bảo thủ | Trong 27 sự kiện Graph: 1 `DIRECT_TRANSFER_PATH_VERIFIED`, 2 `SAME_TRANSACTION_CO_OCCURRENCE`, 23 cùng block, 1 theo thời gian. Một tuyến WETH đúng lượng và thứ tự được xác minh bằng receipt; trace `UNAVAILABLE`. Tuyến này vẫn không chứng minh tác động giá nhân quả hoặc cascade lịch sử. |

## 6. P20 Hướng dẫn tích hợp cho Commander

Giữ nguyên sáu RQ và nguồn S01–S30. Kết quả nhạy với Uniswap của bản `2b9a29f5` phải được thay bằng `corrected_run_v2`; Level-3 là mở rộng có phiên bản. Bảng RQ1 cần ghi riêng: deterministic 8×4 grid cơ sở chưa có depth≥2; Severe stochastic v2 có 8/200 path; tail grid Level-3 có 4/60 cell depth 2; Severe Level-3 ghi 280/10.000 path depth≥2 và không depth≥3. Các miền/phân phối khác nhau nên không mâu thuẫn. Không nội suy ngưỡng chính xác hoặc đếm số cell như xác suất.

RQ3 phải tách thời điểm thanh lý đầu với recovery tolerance. RQ4 phải tách intrawave impact với residual sau arbitrage: trong Professor sweep, intrawave khoảng 0,108794% giữ nguyên còn residual giảm theo capacity về xấp xỉ 0. RQ6 dùng nợ chưa thanh lý theo scenario LT; LT legacy chỉ để đối chiếu. RQ5 tiếp tục giới hạn valuation/conversion units. P1 sửa bảng/claim/result crosswalk trước freeze cuối; P2 không thay artifact hay registry.

Sửa các đoạn V2 §4.3/§5.8/§5.9/§2.4 theo semantics hiện hành: cascade cần HF trace nhưng đã có bằng chứng mô phỏng path kiểm được; tail metric là composite exposure; graph là typed aggregated network; Aave có tác nhân đại diện. Terra reconstruction/cutoff-safe warning giữ riêng, không xác nhận Aave. Lịch sử Ethereum tại §7 chỉ là event evidence extension, không thêm RQ thứ bảy.

## 7. P21 Đối chiếu literature với kiểm chứng P0 và Level-3

**Bằng chứng mô phỏng.** S10/S11 hỗ trợ khả năng tồn tại phản hồi qua thanh khoản; chúng không bảo đảm mọi snapshot sinh cascade. P0 v2 ghi 8/200 Severe path và Level-3 có 4/60 ô tail depth 2. Gói sửa kiểm tra trực tiếp điều kiện đủ: ca tất định −40%/haircut 90% có HF tại cú sốc trực tiếp 1,0211716 rồi giảm còn 0,9980426 tại giá sau vòng 1; 10/10 mẫu phân tầng Monte Carlo cũng có HF trực tiếp ≥1 và HF tại giá vòng trước <1. Path index 5 cũ vẫn khớp 1,0041608020→0,9990974835. Đây là bằng chứng borrower mới mất an toàn **trong engine**, mạnh hơn đếm wave nhưng không chứng minh oracle ngoài đời phản ứng như mô hình. [S03/S05/S10/S11; E03/E08]

Grid Level-3 gồm shock −5%…−50% và haircut 0/25/50/75/90/95%; bốn ô depth 2 là (−40%,90%), (−40%,95%), (−50%,90%), (−50%,95%). Haircut 90/95% chưa được quan sát trong dữ liệu hiệu chỉnh. Severe seed 20260914 có 280/10.000 path depth≥2 = 2,8%, depth≥3 = 0 và độ sâu tối đa 2; giới hạn cấu hình 100 chỉ là năng lực thí nghiệm. Checkpoint audit xác nhận 13.000 định danh batch độc lập, 0 trùng lặp và 21/21 mẫu tái hiện, nhưng không phục hồi thời lượng thực thi lịch sử bị thiếu. Đây là tần suất có điều kiện của mô hình, không phải dự báo hay xác suất thị trường. [E02/E04/E06/E12]

**Bằng chứng quan sát chuỗi.** Trong tuần đã định nghĩa từ `2026-09-01T00:00:00Z` đến trước `2026-09-08T00:00:00Z`, census log trực tiếp từ Aave V3 Pool tìm 28 `LiquidationCall`. Graph phát hiện 27 và cả 27 đều khớp RPC; recall quan sát trong census này là 27/28. Sự kiện Graph bỏ sót ở block 25.888.740 có WETH thế chấp và USDT là tài sản nợ. Kết quả này chỉ chứng minh độ đầy đủ theo địa chỉ/topic/cửa sổ đã khai báo, không phải census trạng thái người vay. Có 22 cụm theo cửa sổ chính 5 phút; thay 1/15/30 phút cho 24/20/19 cụm, nên số cụm phụ thuộc định nghĩa. [E09/E10]

Trong 27 sự kiện Graph, receipt audit phân loại 1 `DIRECT_TRANSFER_PATH_VERIFIED`, 2 `SAME_TRANSACTION_CO_OCCURRENCE`, 23 `SAME_BLOCK_ASSOCIATION` và 1 `TIME_WINDOW_ASSOCIATION`. Ca direct có chuỗi WETH đúng lượng theo thứ tự: liquidator nhận thế chấp, chuyển qua trung gian, vào pool rồi phát sinh `Swap`. Hai ca còn lại trong cùng giao dịch không đạt exact-amount/ordering và không được gọi direct. `debug_traceTransaction` vẫn `UNAVAILABLE`; receipt route không tự chứng minh tác động giá nhân quả. 31.489 swap là union quanh các cửa sổ event/control đã chọn, không phải tổng tuần. [E09/E11]

**Đối thoại học thuật.** Một receipt route trực tiếp và các liên hệ thời gian phù hợp để khảo sát kênh giao dịch mà S10 đặt ra, nhưng chưa nhận diện quan hệ nhân quả. S11 vốn suy hành vi liquidator gián tiếp; DeFiStress không dùng association để tuyên bố cascade lịch sử. Đối chứng được đặt đúng 60 phút trước tâm sự kiện và quét bốn pool ở half-width 1/5/15/30 phút: 40 tổ hợp episode/kind/window, 928 log chunks; cả năm cửa sổ control ±30 phút không có `LiquidationCall`. Năm episode đầu vẫn theo fallback định trước. Các kiểm tra này tăng độ tin cậy về bao phủ cửa sổ, không loại mọi nhiễu thị trường chung mà S13 cảnh báo. [S10/S11/S13/S21; E09–E11]

**Mức xác nhận.** Fork contract execution vẫn `UNAVAILABLE`, 0 transaction; initial-state Quoter validation không chuyển thành post-shock execution. Các gate census, receipt route, control-window, checkpoint và wave-2 eligibility đã PASS trong bundle sửa, với discrepancy Graph 27/28 và external attestation của checkpoint cũ được công bố. Trạng thái toàn gói vẫn `READY FOR COMMANDER RE-REVIEW — NOT SCIENTIFIC LOCK`. Không có bằng chứng cascade nội sinh lịch sử, realized loss hoặc dự báo ngoài mẫu. [E12; quyết định Commander]

## 8. Biên bản kiểm duyệt độc lập

### Bản bàn giao gốc ngày 13/10/2026

Review `PASS_P2_LITERATURE_PACKAGE` của tác tử `p2_independent_review` áp dụng cho bốn file tại commit P2 `f753629c`, ánh xạ mã nghiên cứu `2b9a29f5`. Kết quả này là hồ sơ lịch sử; không tự phê duyệt lần cập nhật 14/10 hoặc khoa học Level-3.

### Bản đối chiếu ngày 14/10/2026

Reviewer độc lập `p2_independent_review` đã cho `PASS_P2_FINAL_VERSION_DELTA` sau khi đọc đủ năm file và đối chiếu trực tiếp chỉ đạo Commander, báo cáo sửa P1 cùng sáu artifact kiểm toán tại HEAD `ba62c749`. Reviewer xác nhận 30 nguồn, U queue/nhãn truy cập, sáu RQ, 35 claim IDs và 92 thuật ngữ được bảo toàn; các số census, tier, control, checkpoint và HF audit khớp artifact. Sign-off chỉ duyệt tính nhất quán của tài liệu P2, không thay Commander scientific approval và không cho phép merge. Issue #4 giữ open, PR giữ draft.
