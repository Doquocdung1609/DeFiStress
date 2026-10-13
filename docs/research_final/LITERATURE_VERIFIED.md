# Tổng quan tài liệu đã xác minh cho DeFiStress

**Bàn giao P2 của [issue #4](https://github.com/Doquocdung1609/DeFiStress/issues/4), ngày 13/10/2026. Trạng thái: PASS kiểm duyệt độc lập P2, chờ Commander tích hợp.** Đây là tổng quan và hồ sơ chứng cứ, không phải báo cáo Word final, kiểm toán mã đầy đủ hoặc xác nhận kết quả Mainnet. Ba file đi kèm là `REFERENCE_EVIDENCE_MATRIX.md`, `APA_REFERENCES_VERIFIED.md` và `TERMINOLOGY_VI.md`.

## 1. Tài liệu đầu vào và quy trình nghiên cứu

Đã đọc bản hiện hành **DeFiStress_NOI_DUNG_NGHIEN_CUU_V2.md** (tạo/sửa 13/10/2026, 09:40:40 UTC, 432 dòng), báo cáo Word cũ và sáu tài liệu đính kèm còn lại. Đã đọc báo cáo, phương pháp, hạn chế, ma trận RQ, chất lượng dữ liệu, khả năng tái lập và mã cốt lõi tại [commit nghiên cứu 2b9a29f5](https://github.com/Doquocdung1609/DeFiStress/tree/2b9a29f5e8c0c8dd910b7d65428fb1d57646b06b). Bản V2 và báo cáo tại commit này là căn cứ ánh xạ; README/default master cũ không được dùng để phủ định kết quả nghiên cứu mới. P2 không chạy lại thí nghiệm hay chứng nhận số liệu.

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

Sách Glasserman cung cấp nền tảng Monte Carlo trong tài chính; P2 chỉ truy cập phần preview và metadata. Trong engine được đọc, mỗi lần chạy nhiễu hóa shock/haircut/gas rồi gọi lại mô hình tất định. Đây là lấy mẫu kịch bản, không phải mô phỏng đầy đủ đường giá ngẫu nhiên theo thời gian. Tần suất cascade phụ thuộc snapshot, cấu trúc, phân phối và quy tắc gán nhãn. Tăng số seed không khắc phục thiên lệch mẫu, sai cấu trúc hoặc giả định oracle. [S23; mã dự án]

### P14 Không quan sát sự kiện chưa xác lập xác suất bằng không

Tài liệu NIST cho công thức score interval Wilson và phân biệt nó với adjusted Wald. Với 0 sự kiện trong 200 lần độc lập cùng phân phối, khoảng hai phía 95% có cận trên xấp xỉ 1,8845%. Đây là phép tính có điều kiện cho bộ mô phỏng, không phải cận xác suất khủng hoảng Aave thực. Nó chưa chứa bất định về tham số hay cấu trúc và không phải cận một phía 95%. Nguồn Wilson/Agresti gốc chưa đọc toàn văn được giữ riêng ở hàng chờ. [S24]

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

Các biểu thức sau là **mô tả/phân tích của P2 về mã đóng băng**, không gán nguyên văn cho bài nghiên cứu.

Với danh mục đúng nguồn giá:

\[
HF_i=\frac{\sum_j c_{ij}p_j^{oracle}LT_j}{\sum_k d_{ik}p_k^{oracle}}.
\]

Trong `BorrowerPosition.health_factor`, danh mục Aave được thu gọn còn WETH và giá trị gộp tài sản khác. RQ5 dùng mẫu số \(d_{USDC}q_{USDC/USD}+D_{other,USD}\). Với tử số cố định, đạo hàm HF theo \(q\) âm khi dư nợ USDC dương. Điều này xác định riêng dấu của kênh định giá; chưa xác nhận việc mô phỏng thực thi khi USDC mất neo. [S02–S06; `sim/schemas.py`]

Trong một khoảng Uniswap với \(s=\sqrt{P_{raw}}\), token1 vào ròng làm \(s'=s+\Delta y/L\), lượng token0 ra là \(L(1/s-1/s')\). Đổi decimal/chiều token trước khi diễn giải USDC/WETH. Qua tick phải cập nhật L theo đúng hướng. Các công thức này không cho phép đặt lại sqrt price tùy ý mà giữ nguyên thanh khoản hoạt động khi qua nhiều tick. [S08; `sim/dex/uniswap_v3.py`]

| Cơ chế | Mã thực đọc tại 2b9a29f5 | Giới hạn cần giữ trong bản final |
|---|---|---|
| Oracle và phản hồi | `valuation_price=min(reference_price,pool.spot_price)` | Liên kết giá đánh giá lại bảo thủ, đồng bộ do mô hình đặt ra. Không phải dữ liệu feed Aave/Chainlink và không chứng minh bán tại một pool cập nhật oracle ngay. |
| Thanh lý | `plan_liquidation`; HF, close factor, debt/collateral cap | Xấp xỉ hai tài sản/gộp, chưa ngang EVM. S06 mới áp 50% theo tổng nợ vị thế; cần đối chiếu reserve/portfolio cụ thể. Không xác nhận triển khai mainnet chỉ từ GitHub main. |
| USDC trong lượng thu giữ | `seize=repay*bonus/weth_price` | Khi repay là token USDC và WETH price là USD/WETH, chuyển đổi nhất quán cần nhân giá USDC/USD. Code hiện không nhân ở nhánh này; dust nợ cũng dùng nominal USDC. RQ5 không được gọi là mô phỏng toàn diện thực thi mất neo. |
| Lợi nhuận liquidator | Số USDC từ quote trừ nợ trả/gas/funding/buffer | Vốn cộng dồn không tái sử dụng; chọn kế hoạch vượt vốn có thể bị bỏ thay vì thu nhỏ. Giới hạn vốn mô hình không bằng tổng vốn thực có thể huy động. |
| Shock/arbitrage | `arbitrage_toward` đặt sqrt price/tick; `capacity_pct` là tỷ lệ hồi chênh | Không phải swap có kiểm vốn/tồn kho. Việc đặt lại giá ban đầu 100% và hồi giá sau đó không tự cập nhật L qua tick. Cần disclosure, không gọi phép này giao dịch arbitrage chính xác. |
| Đợt và cascade | `completed_waves` ghi chỉ số vòng có thanh lý; hàng chờ bỏ `attempted` | Vị thế đủ điều kiện ngay từ đầu nhưng bị hoãn vì capacity có thể vào vòng sau. `depth>=2` chưa tự chứng minh có người vay mới mất an toàn do phản hồi. Đối chiếu từng borrower/HF/thời điểm với direct-shock cohort. |
| Độ trễ | Thêm bước chờ trước xử lý | Không có đường giá tiếp diễn trong thời gian chờ ở nhánh được đọc. Thời gian tăng chưa chứng minh tổn thất tăng. |
| Nợ xấu | `max(debt_value-collateral_value,0)` | Khoảng thiếu hụt theo giá mô hình; không bằng toàn nợ chưa thanh lý, chưa phải reserve deficit on-chain hoặc giá trị thu hồi sau mọi chi phí. |
| Monte Carlo | Normal shock/haircut, lognormal gas; clipping; các lần gọi engine | Lấy mẫu tham số quanh kịch bản. Cắt biên khác phân phối normal bị truncated đúng nghĩa; phụ thuộc giữa các biến chưa được hiệu chỉnh. |
| ES hiện hành | Mean của `bad_debt+total_liquidated_debt` trên mọi giá trị ≥ quantile 95% | Nợ hoàn trả không phải tổn thất. Trộn USD và nominal USDC nếu depeg. Khi có ties có thể chọn hơn 5% mẫu. Gọi “trung bình đuôi chỉ tiêu phơi nhiễm tổng hợp của mô hình”, chưa gọi ES tổn thất kinh tế. |
| Network | `MultiDiGraph` dị thể; centrality tính trên đồ thị gộp | Gộp max normalized strength theo cặp nút; betweenness bỏ weight; eigenvector không truyền weight. Chưa phải centrality trên supra-adjacency multilayer hoặc DebtRank. |

## 6. P20 Hướng dẫn tích hợp cho Commander

Giữ nguyên sáu RQ và các kết quả có provenance của dự án. Dùng P01–P18 và ma trận để bổ sung luận cứ cho Chương 1–4/7, cùng bối cảnh Chương 6. Không đổi bảng kết quả thành kết quả của literature. Cần sửa diễn giải V2 ở §4.3 để phân biệt đợt xử lý với sự kiện newly eligible; §5.8 để đổi tên/đơn vị chỉ tiêu đuôi; §5.9 để gọi đúng đồ thị gộp; §2.4 để nói đúng số tác nhân đại diện. Các điểm này là giới hạn P2 phát hiện, chưa phải bản vá mã.

Khi viết kết luận về RQ1, chỉ được dùng “không quan sát trong miền thử với định nghĩa chỉ tiêu đã triển khai”. Khi nói về RQ4, tránh dùng tác nhân hồi giá đơn giản để kết luận arbitrage thị trường không quan trọng. Với RQ5, công bố giới hạn kênh định giá và chuyển đổi đơn vị. Bản Terra reconstruction và cutoff-safe warning phải tiếp tục tách riêng; khả năng khớp giá không chứng minh dự báo trước mất neo đầu tiên.

P2 không tự đóng issue, merge hoặc quyết định PASS toàn dự án. Kiểm duyệt độc lập đánh giá tập literature có giới hạn nêu trên; Commander quyết định tích hợp, yêu cầu P0/P1/P3 kiểm chứng mã và phê duyệt báo cáo sau đó.

## 7. Biên bản kiểm duyệt độc lập

**Ngày review:** 13/10/2026. **Reviewer:** tác tử độc lập `p2_independent_review`, tách khỏi tác tử soạn P2. **Kết quả:** `PASS_P2_LITERATURE_PACKAGE`, không có lỗi chặn bàn giao.

Reviewer đã đọc đầy đủ bốn file, kiểm 30 mục S khớp APA, 35 claim, sáu RQ nguyên nghĩa và 92 thuật ngữ. Đối chiếu độc lập chọn mẫu nguồn gốc JFE Terra 2026, Bank of Canada Aave 2026, Springer Glasserman, BIS Lehar–Parlour, bản tác giả Qin và OECD. Các phạm vi abstract/preview, nguồn chưa xác minh và phiên bản tiền nhiệm được phân biệt đúng. Sáu giới hạn phương pháp oracle, cascade/batching, USDC units, arbitrage reset, loss proxy và graph aggregation đã được giữ.

Hai chỉnh sửa nhỏ sau review đã thực hiện: thứ tự tác giả Aave trước Aave DAO trong APA; thuật ngữ “Đủ điều kiện thanh lý”. Review không xác nhận kết quả thực nghiệm, mã đúng giao thức/EVM, hoàn thành P0/P1, hoặc phê duyệt của Commander. Giữ nguyên §5–6 và hàng chờ nguồn khi tích hợp; không suy rộng PASS này sang toàn báo cáo.
