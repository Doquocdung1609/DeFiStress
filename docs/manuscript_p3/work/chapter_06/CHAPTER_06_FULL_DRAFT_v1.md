# CHƯƠNG 6. ĐỐI CHIẾU LỊCH SỬ VÀ CÁC MỞ RỘNG NGHIÊN CỨU

Kết quả mô phỏng ở Chương 5 xác định những điều kiện để một chuỗi thanh lý–giao dịch–định giá tiếp tục hoặc dừng lại trong thiết kế của DeFiStress. Bước tiếp theo là xem các quan sát bên ngoài mô phỏng hỗ trợ được phần nào của cách giải thích đó. Chương này sử dụng ba hướng bổ sung: đối chiếu sự kiện thanh lý Aave, kiểm tra hồi cứu Terra và biểu diễn mạng liên kết của mô hình. Mỗi hướng trả lời một câu hỏi về bằng chứng: giao dịch nào thực sự liên kết với nhau; tín hiệu nào có trước sự kiện cần cảnh báo; và vị trí cấu trúc nào được các quan hệ đã mô hình hóa tạo ra.

Luận điểm chung là giá trị của đối chiếu phụ thuộc nội dung quan sát và ranh giới thông tin, không phụ thuộc việc hiện vật có mang nhãn “validation” hay không. Một tuyến chuyển tài sản được xác minh, một chỉ báo không cảnh báo kịp và một nút có độ trung gian cao đều là kết quả có ý nghĩa, nhưng ý nghĩa ấy khác nhau. Trình bày riêng từng lớp giúp nghiên cứu khai thác bằng chứng bổ sung mà vẫn giữ đúng phạm vi kết luận của sáu RQ.

Nguồn khoa học của chương được pin tại Scientific Lock `3f6e5302483681209e2408531eb5a15389f9fded`; cấu trúc và exhibit IDs theo Blueprint Lock `8de52bebabef376be700836e6f93a92d7394d2c3`. Các số liệu dưới đây được trích từ kết quả đã khóa, không phải đầu ra của một lượt chạy hoặc kiểm định mới. Những hồ sơ cũ được sử dụng theo thứ tự ưu tiên phiên bản đã xác lập; audit đi kèm lưu exact locators, phạm vi đọc và các điểm đã được thay thế.

## 6.1 Các sự kiện thanh lý Aave trong cửa sổ lịch sử

### 6.1.1 Thiết kế cửa sổ và event census

Đối chiếu lịch sử trước hết cần một tập sự kiện được xác định độc lập với kết luận mong muốn. Trong nghiên cứu này, cửa sổ được khai báo từ `2026-09-01T00:00:00Z` đến trước `2026-09-08T00:00:00Z`. Đối tượng đếm là log `LiquidationCall` của Aave V3 Pool trong cửa sổ đó. Một sự kiện theo log khác một transaction: cùng giao dịch có thể chứa nhiều lần thanh lý, nên số sự kiện không tự là số giao dịch hay số người vay duy nhất. Phạm vi này cũng khác tập 454 danh mục ở snapshot canonical mà các chương trước sử dụng cho mô phỏng.

The Graph cung cấp 27 candidate events; cả 27 được đối chiếu với log, receipt, block number, block hash và thời gian UTC qua RPC trong đợt kiểm đã khóa. Census bổ sung quét trực tiếp Pool theo cửa sổ đầy đủ tìm thấy 28 sự kiện, trong đó 27 khớp Graph và một sự kiện chỉ có ở RPC. Vì vậy, “27/27 candidate được xác minh” nói về độ đúng của tập candidate đã tìm thấy, còn “27 trong 28 Pool events được Graph bao phủ” nói về độ bao phủ của chỉ mục trong cửa sổ. Hai kết quả cùng đúng và trả lời hai yêu cầu dữ liệu khác nhau.

Sự kiện RPC-only ở block 25888740, log index 91, thuộc transaction `0x8f0ab391fcf8c1454f9665460a5d675a0821b4a53e01301c17bc239ac2fcad65`. Sự tồn tại của nó cho thấy cần tách nguồn discovery khỏi nguồn kiểm tra sự kiện. Nó được giữ trong census, nhưng không tự nhận một tier liên kết DEX từ bộ phân loại dành cho 27 Graph-matched events. Tập 28 là mẫu số của đối chiếu Pool; tập 27 là mẫu số của phân tầng ở mục tiếp theo. Nghiên cứu không phân phối lại một event chưa được phân loại để làm các mẫu số trông đồng nhất.

Để chọn trường hợp xem xét sâu, thiết kế sử dụng quy tắc năm cụm 5 phút đầu tiên theo thời gian, sau khi các trường `amountUSD/profitUSD` của Graph bị loại khỏi xếp hạng do bất nhất đơn vị. Năm cụm gồm sáu liquidation events. Đây là fallback đã khai báo, không phải lựa chọn những episode có tác động giá lớn nhất sau khi quan sát kết quả. Các cụm thời gian cũng nhạy với độ rộng: hồ sơ lưu 24, 22, 20 và 19 cụm ứng với khoảng cách tối đa 1, 5, 15 và 30 phút trên tập 27 sự kiện. Chúng mô tả cách nhóm quan sát, chưa đo độ sâu cascade.

Các số hiện hành lấy từ [census reconciliation](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json) và [targeted repair report](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/docs/research_final/LEVEL3_P1_TARGETED_REPAIR_REPORT.md). Báo cáo Level-3 ban đầu chỉ có 27 Graph candidates và một cách phân loại direct rộng hơn; những trường đó không thay thế kết quả census và route audit sau cùng. Attempt có epoch sai được giữ riêng và bị loại khỏi kết luận. Do đó, con số 28 hiện hành phải truy về census đúng cửa sổ, không truy về attempt bị loại chỉ vì chúng tình cờ có cùng số đếm.

### 6.1.2 Bốn tầng liên hệ

Sau khi xác định sự kiện, câu hỏi tiếp theo là bằng chứng nào nối thanh lý với giao dịch DEX. Trong 27 Graph-matched events, phân tầng cuối cùng ghi nhận một `DIRECT_TRANSFER_PATH_VERIFIED`, hai `SAME_TRANSACTION_CO_OCCURRENCE`, 23 `SAME_BLOCK_ASSOCIATION` và một `TIME_WINDOW_ASSOCIATION`. Các nhãn thể hiện mức độ truy vết của liên hệ, không phải bốn mức xác suất nhân quả. Thứ tự tier 1–4 trong Bảng 6.1 được dùng để trình bày các định nghĩa gốc đó.

**Bảng 6.1 (T6.1). Event census và các tầng liên hệ thanh lý–DEX.** Nguồn: Frozen `historical_evidence.csv`, `HIST_RPC_CENSUS_EVENTS`, `HIST_GRAPH_MATCHED_EVENTS` và bốn result IDs tier; nguồn chi tiết là census reconciliation và linkage route audit tại Scientific Lock. Cửa sổ 01–07/09/2026 UTC, kết thúc loại trừ lúc 00:00 ngày 08/09. Đơn vị đếm là `LiquidationCall events`. Mẫu số tier là 27 Graph matches, khác 28 Pool events; RPC-only chưa được nhập vào phân tầng DEX này. Đây là bảng liên hệ quan sát, chưa xác lập lây lan nhân quả.

| Phạm vi hoặc tier | Nhãn/đối tượng gốc | Số sự kiện | Mẫu số/phạm vi | Nội dung được hỗ trợ |
|---|---|---:|---|---|
| Pool census | RPC log census | 28 | Pool/address/topic/cửa sổ đã khai báo | Tập log thanh lý trong cửa sổ được quét |
| Ghép nguồn | Graph matched | 27 | 28 Pool events | Candidate Graph khớp sự kiện RPC |
| Ngoài Graph | RPC-only | 1 | 28 Pool events | Một event bị chỉ mục Graph bỏ sót; không tự gán tier DEX |
| Tier 1 | DIRECT_TRANSFER_PATH_VERIFIED | 1 | 27 Graph matches | Tuyến WETH đúng lượng và đúng thứ tự log tới pool được đối chiếu |
| Tier 2 | SAME_TRANSACTION_CO_OCCURRENCE | 2 | 27 Graph matches | Thanh lý và swap cùng transaction, chưa đạt tiêu chí transfer path trực tiếp |
| Tier 3 | SAME_BLOCK_ASSOCIATION | 23 | 27 Graph matches | Swap WETH/USDC cùng block, khác transaction; liên hệ theo thời điểm |
| Tier 4 | TIME_WINDOW_ASSOCIATION | 1 | 27 Graph matches | Swap gần sự kiện trong cửa sổ ±30 phút; không cùng block/transaction |

Tier 1 có bằng chứng cụ thể về luồng tài sản. Với event `event-73afad4e8e3d8a92d2a7`, route audit lưu 3.815682452121213010 WETH được nhận tại log 26, `LiquidationCall` tại log 32, cùng lượng WETH đi qua intermediary tại log 33 rồi vào pool tại log 35; swap khớp tại log 36. Chuỗi nằm trong transaction `0x1b8a4a186c944b70e88fbb3572af6e56d992b0577def32da83e65782d6507271`. Tiêu chí đúng lượng và thứ tự tạo cơ sở mạnh hơn việc chỉ thấy hai loại event trong cùng receipt: nó nối tài sản được xử lý với nơi giao dịch theo dấu vết đã lưu.

Ngược lại, hai thanh lý trong transaction `0xc5463ffdc853db390912ccb6f9574a32bc0263af82217ce02e1c11f4dd1d1cfc` chỉ được giữ ở tier 2. Ở event thứ nhất, lượng WETH nhận từ thanh lý không bằng lượng WETH của swap được xét; ở event thứ hai, swap đó xảy ra trước log thanh lý nên chưa thể là đường bán tài sản của event ấy theo tiêu chí kiểm toán. Chúng từng được gộp vào ba “direct transaction links” trong narrative cũ, nhưng audit sau cùng đã phân biệt một tuyến transfer được xác minh và hai đồng xuất hiện. Không đạt tiêu chí bảo thủ này cũng chưa đủ để kết luận chắc rằng tài sản hoàn toàn không liên quan; nó xác định giới hạn của điều đã được xác minh.

Tier 3 và tier 4 giữ ý nghĩa mô tả riêng. Trên một thị trường giao dịch liên tục, việc có swap trong cùng block hoặc gần một liquidation có thể phản ánh hoạt động nền, phản ứng với một cú sốc giá chung, hoặc nhiều chiến lược giao dịch khác nhau. Các nhãn đó chưa nhận diện một tài sản cụ thể đã đi từ thanh lý tới pool. Đặc biệt, 23 sự kiện tier 3 không thể được gọi thành 23 lần “truyền nhiễm” chỉ vì độ gần thời gian cao hơn một cửa sổ nhiều phút.

Ngay cả tier 1 cũng mới xác minh một tuyến giao dịch. Để xác lập vòng phản hồi nội sinh còn cần chứng cứ về tác động giá, giá dùng đánh giá các danh mục khác và sự thay đổi điều kiện thanh lý của những danh mục ấy. Hồ sơ [linkage route audit](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json) ghi `causal_claim=false`; `debug_traceTransaction` cũng có trạng thái `UNAVAILABLE` ở đợt truy xuất được báo cáo. Receipt và Transfer logs hỗ trợ kết luận theo phạm vi của chúng, không được mô tả như một lượt debug trace mới hoặc một xác nhận nhân quả thị trường.

### 6.1.3 Điều gì có thể đối chiếu với mô hình

Đối chiếu hữu ích nhất là đối chiếu từng mắt xích có cùng nội dung kinh tế. Literature về thanh lý và thị trường phi tập trung cung cấp cơ sở xem xét bán tài sản thế chấp cùng khả năng tác động giá (Lehar và Parlour, 2022). Quan hệ giữa thanh lý, biến động và thanh khoản còn đặt ra vấn đề nhận diện hành vi từ dữ liệu giao dịch (Sasi-Brodesky và Kaousar Nassr, 2023). Với DeFiStress, tuyến transfer xác minh hỗ trợ tính khả dĩ của mắt xích tài sản từ thanh lý đi tới DEX. Nó không tự cung cấp độ truyền giá sang oracle hoặc xác suất một danh mục khác trở thành mất an toàn.

Các cửa sổ event/control giúp mô tả môi trường mà tuyến giao dịch đó xuất hiện. Đợt kiểm đã khóa quét bốn WETH/USDC pools cho các half-width 1, 5, 15 và 30 phút, với tâm control cách tâm event đúng 60 phút về trước. Ở năm episode được chọn, số swaps trong ±5 phút tại event/control lần lượt là 154/200, 183/196, 355/191, 337/213 và 256/203. Hoạt động DEX không chỉ xuất hiện quanh thanh lý; hai cặp đầu còn có số swap ở control cao hơn ở event. Số đếm vì vậy cung cấp bối cảnh giao dịch, chưa đo riêng áp lực bán do thanh lý.

Hồ sơ [control-window audit](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/level3_p1_targeted_repair/historical/control_window_audit.json) ghi năm control ±30 phút không có `LiquidationCall` và không có swap thiếu/thừa trong phép đối chiếu cửa sổ đã kiểm. Điều đó làm rõ phạm vi tập so sánh, nhưng chưa khiến các cửa sổ trở thành đối chứng nhân quả: biến động ETH, gas, MEV, giao dịch ngoài bốn pools và thời điểm cập nhật giá vẫn có thể khác nhau. Các cửa sổ cũng có thể chồng lấp, nên không cộng các số swap để tuyên bố một tổng giao dịch duy nhất hoặc một universe Uniswap toàn tuần.

Khái niệm wave trong Chương 5 có điều kiện mạnh hơn khái niệm cụm theo timestamp ở đây. Phản hồi mô hình được diễn giải qua HF dưới chính sách định giá cụ thể, trạng thái trước/sau Wave 1 và giao dịch hoàn trả dương ở vòng sau. Một cụm có nhiều liquidation lịch sử không chứa sẵn những đối chiếu danh mục đó. Việc đổi cửa sổ nhóm từ 5 sang 15 phút có thể thay số cụm mà không thay bất kỳ transaction nào; nó không thể được dùng để đổi một “cascade depth” thực tế theo ý người phân tích.

Khoảng quan sát lịch sử còn đi trước snapshot canonical ở block 26045352. Nghiên cứu chưa có census trạng thái người vay lịch sử đầy đủ để tái hiện ex ante chính các vị thế và đường giá ở những episode đó. Các giá Aave oracle được lấy quanh episode cũng khác việc enumerate chuỗi `AnswerUpdated` và kiểm đường truyền từ DEX sang giá đánh giá HF. Vì vậy, dữ liệu lịch sử bổ sung một tuyến thực thi có thể truy vết và các mức liên hệ quan sát, còn độ nhạy A/B/C tiếp tục là kết quả phản thực của mô hình. Sự phân công bằng chứng này cho phép đối thoại với thực tế mà không biến lịch sử thành một phép xác nhận thay cho giả định oracle.

## 6.2 Terra và giới hạn kiểm chứng hồi cứu

### 6.2.1 Cơ chế và khác biệt thể chế

Phần mở rộng Terra đặt một câu hỏi về cơ chế và kiểm chứng: một mô hình có tương tác tác nhân có thể tái hiện phản hồi rút vốn–bán UST–quy đổi–phát hành LUNA đến đâu khi thông tin đánh giá không được đưa vào hiệu chỉnh? Câu hỏi này bổ sung cho stress testing bằng một trường hợp khủng hoảng đã xảy ra. Nó không thêm RQ thứ bảy hoặc thay việc phân tích khoản nợ USDC trên Aave bằng một bài toán dự báo Terra.

Liu, Makarov và Schoar (2026) phân tích cuộc rút vốn Terra theo tương tác giữa khuyến khích, khả năng quan sát và sự tập trung của người tham gia. Bản NBER năm 2023 là phiên bản tiền nhiệm của cùng nghiên cứu (Liu và cộng sự, 2023, 2026). Nội dung P2 đã xác minh ở mức abstract hỗ trợ việc nhận diện các cơ chế hành vi liên quan; hai phiên bản không được tính thành hai bằng chứng độc lập hoặc dùng để gán thêm các ước lượng chưa được kiểm. Đặc biệt, sự khác biệt hành vi giữa nhóm người tham gia không đủ để quy toàn bộ khủng hoảng cho một thủ phạm duy nhất.

Trong khung Terra của dự án, người gửi tiền rời Anchor và người nắm giữ bên ngoài có thể tạo nhu cầu bán UST; arbitrage redemption hấp thụ phần có thể xử lý, giảm cung UST và phát hành LUNA theo cơ chế quy đổi. Áp lực bán còn lại, sự suy giảm giá LUNA và phản hồi niềm tin có thể tiếp tục tác động quyết định rút vốn. Đây là giả thuyết cơ chế được mô hình hóa; những nhóm tác nhân là biểu diễn cấu trúc, chưa phải từng ví lịch sử được nhận diện và ước lượng hành vi riêng.

Cấu trúc đó khác tuyến WETH thế chấp/USDC nợ. Ở Aave, thay đổi giá trị thế chấp hoặc giá trị nợ làm thay HF, rồi quy tắc và tác nhân quyết định xử lý vị thế. Ở Terra, quy đổi và phát hành gắn trực tiếp với cung của hai tài sản cùng các quyết định rút vốn. Bởi vậy, sự giống nhau về phản hồi bất lợi không tạo sự tương đương về bảng cân đối, cơ chế quyết toán hoặc tham số. Độ khớp giá UST–LUNA không xác nhận LT, bonus hay nguồn giá Aave; chiều tác động của giá USDC trên khoản nợ ở RQ5 cũng chưa giải thích toàn bộ cơ chế mất neo của UST.

Giá trị của ca Terra nằm ở việc buộc mô hình đối diện với một diễn biến bất lợi có quy mô và nhịp thời gian riêng. Một cơ chế nghe hợp lý về kinh tế vẫn có thể thất bại về cảnh báo, thời điểm hoặc biên độ. Do đó, phần mở rộng cần phân biệt khả năng kể lại cơ chế, khả năng tái dựng chuỗi đã xảy ra và năng lực dự báo khi sự kiện còn chưa được quan sát. Các thiết kế khác nhau trong nguồn khóa được đọc theo chính sự phân biệt này.

### 6.2.2 Tái dựng và cutoff safe

Nguồn Terra của dự án gồm các tập dữ liệu và nhiệm vụ khác nhau, nên số hàng không được dùng chung như một mẫu duy nhất. Audit chỉ báo mở rộng đánh giá 1.776 hàng giờ từ tháng 3 đến tháng 5/2022; các thành phần giá tháng 3–4 dựa trên quan sát ngày được mang trong ngày, còn giá tháng 5 dựa trên dữ liệu phút được tổng hợp/as-of theo giờ. Vì vậy, 1.776 hàng biểu diễn lịch chỉ báo, chưa phải 1.776 quan sát thị trường giờ độc lập có cùng chất lượng. Mức khả dụng còn khác giữa tín hiệu rút vốn, backing, native redemption và holder concentration.

Cutoff-safe kiểm một thuộc tính cụ thể của phép tính: thay đổi dữ liệu sau một cutoff không được làm đổi score hoặc cấu trúc thành phần ở cutoff đó và các thời điểm trước. Hồ sơ phase5 ghi năm cutoffs được thử và không có violation theo phép kiểm này. Đây là bằng chứng đã báo cáo về sự tôn trọng ranh giới thông tin trong phép biến đổi; nó khác yêu cầu lựa chọn mô hình hoàn toàn trước sự kiện. Weights, scales, bands và feature set của chỉ báo vẫn được phát triển với hiểu biết về khủng hoảng, và chưa có một giao thức huấn luyện trước sự kiện/đánh giá giữ lại tương ứng để xác nhận năng lực dự báo thực sự.

Ở gói Terra May 2022 riêng, tập 312 hàng giờ bao phủ 01–13/05 và giữ trạng thái `QUALITY_WARNING`. Báo cáo dữ liệu phân biệt nguồn replication có thể truy vết với nguồn archival được truy vấn độc lập. Các trường Curve/bridge và những cột nghi trùng lặp được cách ly khỏi mô hình cuối; liquidity/depth là proxy công suất thực thi. Chẳng hạn, biến đổi của “cung UST ngoài Anchor” chưa nhận diện được bán của người nắm giữ, vì tồn kho đó đồng thời chịu phát hành, đốt qua quy đổi và chuyển vào/ra Anchor. Loại proxy cũ khỏi diễn giải giúp tránh đếm một thay đổi tồn kho như một luồng bán được quan sát.

Hai thiết kế đánh giá trong gói này có thời điểm khởi đầu khác nhau. Strict OOS V2 giữ 144 hàng hiệu chỉnh đến hết ngày 06/05 và 168 hàng đánh giá từ 07/05 theo [final Terra report](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/final_report.md). Conditional V4 bắt đầu sau trigger được ghi nhận trong chính gói đó, hiệu chỉnh 12 giờ từ `2022-05-07T22:00:00Z` đến `2022-05-08T09:00:00Z`, rồi đánh giá 134 hàng từ `2022-05-08T10:00:00Z` đến `2022-05-13T23:00:00Z`. Cửa sổ đánh giá được tách khỏi hiệu chỉnh, nhưng việc đã điều kiện hóa trên trigger khiến V4 là replay cơ chế lịch sử có điều kiện, không phải cảnh báo trước cuộc khủng hoảng. Không ghép các mốc trigger của gói 312 hàng với các ngưỡng trong audit 1.776 hàng như thể chúng dùng cùng một chuỗi đầu vào.

Sự phân biệt này cũng làm rõ phạm vi của kiểm chéo. Bergmeir, Hyndman và Koo (2018) bàn về tính hợp lệ của cross-validation cho tự hồi quy dưới những điều kiện cụ thể, theo abstract đã xác minh. Nguồn ấy không xác nhận mã Terra không rò rỉ dữ liệu và cũng không đưa ra lệnh cấm K-fold phổ quát cho mọi chuỗi thời gian. Bằng chứng của dự án phải đến từ cutoff, lịch hiệu chỉnh/đánh giá và trường dữ liệu thực sự được runner sử dụng. Các kiểm short-horizon moving-origin trong gói cuối chỉ khảo sát chân trời sáu giờ tại các điểm khởi đầu đã khai báo; chúng chưa kiểm chứng thay cho toàn bộ diễn biến sụp đổ nhiều ngày.

Về ý nghĩa phương pháp, tách demo, tính chỉ báo cutoff-safe, strict OOS và conditional replay giúp đặt đúng tiêu chí thành công. Một biểu diễn hồi cứu có thể hữu ích để minh họa cơ chế; một score có thể tôn trọng cutoff; một replay có thể khớp một phần chuỗi sau trigger. Chỉ những kết quả đánh giá phù hợp với thời điểm ra quyết định mới trả lời được câu hỏi cảnh báo. Bởi vậy, kết quả âm phải được đọc từ đúng thiết kế thay vì bị thay bằng một đồ thị khớp giá ở thiết kế khác.

### 6.2.3 Kết quả âm của cảnh báo

Kết quả chính đã đăng ký cho audit cutoff-safe là **0 giờ HIGH trong 1.630 giờ trước mất neo ban đầu**, và lead của cảnh báo HIGH đối với UST dưới 0,995 USD là **−45 giờ**. Theo quy ước nguồn, lead âm nghĩa là cảnh báo xuất hiện sau sự kiện. Mốc UST dưới 0,995 là `2022-05-07T22:00:00Z`, còn HIGH đầu tiên ở `2022-05-09T19:00:00Z`. Kết quả vì thế mô tả một chỉ báo phản ứng muộn so với mất neo ban đầu, không phải 45 giờ cảnh báo sớm.

Hai đại lượng có chức năng đo khác nhau. Số giờ HIGH trước sự kiện cho biết chỉ báo có vượt band trong giai đoạn cần cảnh báo hay không; lead cho biết thời điểm vượt band so với một sự kiện giá đã định nghĩa. Mẫu số 1.630 thuộc bộ đếm giờ trước mất neo, không thuộc phép tính một tỷ lệ thành công của mọi khủng hoảng. Mức HIGH trong audit gắn với threshold score 60; lượt biên soạn giữ nguyên band và không chọn lại cutoff hoặc ngưỡng để làm thay kết luận.

**Hình 6.1 (F6.1). Kết quả âm của cảnh báo Terra theo ranh giới thông tin đã khai báo.** Display specification gồm hai panel độc lập: panel A, x=“trước initial depeg”, y=số giờ HIGH, giá trị 0 trên 1.630 giờ; panel B, x=“HIGH so với UST<0,995”, y=lead tính bằng giờ, giá trị −45, có mốc 0 và chú thích “cảnh báo sau sự kiện”. Nguồn: `TERRA_PRE_DEPEG_HIGH_ALERT_HOURS`, `TERRA_INITIAL_DEPEG_HIGH_LEAD`, Frozen `terra_limitations.csv` và `phase5_terra_early_warning_audit.json` tại Scientific Lock. Đây là derived historical validation, không là raw observation về khả năng dự báo. Không dùng chung trục cho count và lead, không dựng đường score/timeline khi chỉ dùng hai summary values. Trạng thái `DISPLAY_SPEC_READY_NOT_RENDERED`; dữ liệu/selector chính xác nằm trong audit F6.1.

Một điểm dễ tạo cách kể thuận lợi hơn là HIGH có lead dương 3 giờ đối với mốc UST dưới 0,90 USD trong cùng audit. Khi ấy, mất neo ban đầu đã xảy ra từ trước; đổi sự kiện đích từ 0,995 sang 0,90 làm đổi câu hỏi đang đánh giá. Con số 3 giờ có thể được công bố như một quan hệ thời điểm đối với ngưỡng muộn hơn, nhưng không xóa kết quả 0 giờ HIGH trước mất neo và không chứng minh quy trình đã dự báo ngoài mẫu cuộc khủng hoảng. Cách đọc nhất quán giữ cả sự kiện đích lẫn band cảnh báo bên cạnh lead.

Strict OOS V2 trong gói May 2022 cũng được báo cáo là không phát hiện collapse, với RMSE giá UST 0.417488 USD/UST trong thiết kế 168 hàng đánh giá. Đây là bằng chứng âm của mô hình giữ lại cho đánh giá, khác phép kiểm cutoff của score hồi cứu; không chuyển RMSE đó sang F6.1 hoặc nhập hai thiết kế thành một mẫu. Đối với một mục tiêu cảnh báo, không tái hiện được biến cố là kết quả thực chất cần giải thích, dù một số phép kiểm dữ liệu và tính hợp lý của trạng thái vẫn đạt yêu cầu riêng.

Conditional replay V4 cung cấp một đối chiếu khác về giới hạn giải thích. Trên 134 hàng, [final metrics](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/terra/audit/final_metrics.json) lưu tương quan giá UST 0.9173549592822899 nhưng sai số tương đối cung LUNA cuối kỳ 0.9998790562492551. Việc cùng nắm được một phần chiều biến động chưa bảo đảm đúng biên độ hoặc quy mô; mô hình không tái hiện đầy đủ sự bùng nổ cung lịch sử. Các comparator dùng chung implementation với các component overrides, không phải bốn mô hình độc lập; kết quả cũng chưa xác lập lợi thế thực chất của ABM so với system dynamics trong gói đó.

Những kết quả âm phù hợp với chất lượng thông tin và mức nhận diện tham số đã công bố. Một số kênh thiếu quan sát độc lập, proxy có thể trộn lẫn luồng với tồn kho, và một hệ số phản ứng chưa được nhận diện đủ không thể được coi là tham số thị trường chỉ nhờ fit sau trigger. Tuy nhiên, bằng chứng hiện tại chưa phân rã nhân quả phần sai số của từng nguyên nhân; không quy thất bại cho riêng một biến. Đóng góp của mở rộng là chỉ rõ những bước đã được kiểm tra, những kết quả không đạt mục tiêu và vì sao tính đúng về cutoff chưa đủ cho thành công dự báo. Việc retune trên chính sự kiện thất bại sẽ trả lời một bài toán mới và không được thực hiện trong chương này.

## 6.3 Mạng cấu trúc và ý nghĩa chỉ số trung tâm

### 6.3.1 Các node và kênh đã mô hình hóa

Mạng giúp tổ chức những quan hệ tài chính mà mô phỏng đã xác định, qua đó làm rõ điểm nối giữa tài sản, giao thức và tác nhân. Graph cấu trúc của DeFiStress có tám node: Aave V3, Uniswap V3, WETH, USDC, nhóm người vay gộp, liquidator đại diện, arbitrageur đại diện và thị trường tham chiếu. Bốn nhãn loại node là giao thức, tài sản, vai trò tác nhân và thị trường tham chiếu. Một node nhóm người vay không tái hiện mạng liên kết giữa từng ví; hai node giao thức cũng không đại diện mọi venue hoặc mọi giao thức DeFi.

Nguồn [structural graph](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/network/structural_graph.json) gắn trạng thái canonical tại block 26045352 cho phần dữ liệu nền. Nhóm người vay chứa 454 danh mục xác minh và thông tin cohort 109 WETH/USDC như hai phạm vi riêng. Vai trò liquidator, arbitrageur và giá tham chiếu mang nhãn giả định kịch bản. Nhãn `REAL_MAINNET` của đầu vào vì vậy không làm cả đồ thị thành mạng giao dịch thực tế đã quan sát: nguồn của mỗi node, cạnh và metric vẫn cần được xét riêng.

Chín typed edges của graph cấu trúc biểu diễn các quan hệ cụ thể. WETH và USDC nối tới Aave qua phơi nhiễm thế chấp và nợ; nhóm người vay nối tới Aave qua vị thế gộp. Hai cạnh WETH→Aave giữ riêng phơi nhiễm thế chấp và kênh đánh giá lại. Tuyến Aave→Uniswap mô tả khả năng đưa tài sản thanh lý tới DEX; Uniswap→WETH biểu diễn kênh giá thực hiện. Liquidator→Aave, arbitrageur→Uniswap và reference market→WETH biểu diễn vai trò thực thi, ổn định và giá đối chiếu. Hướng mũi tên là quy ước quan hệ của mô hình, không mặc nhiên là dòng tiền theo lịch sử hoặc một hợp đồng nợ giữa hai node.

Các cạnh không cùng cấp quan sát. Phơi nhiễm được xây từ snapshot, kênh đánh giá lại là đại lượng cấu trúc suy dẫn, còn vai trò thực thi/hồi giá được đặt bởi thiết kế tác nhân. Ở graph `STRUCTURAL`, các tuyến liquidation và arbitrage chưa có thực thi nên có strength bằng 0 và `active=false`. Riêng đường từ giá DEX đến giá định danh mục vẫn phải được đọc cùng A/B/C của mô hình; hình vẽ nối DEX–WETH–Aave chưa là bằng chứng oracle Aave nhận spot Uniswap trong lịch sử.

Mã có thể tạo graph `RUN_WEIGHTED` và frames từ các event mô phỏng đã lưu, cũng như trả summary cho Monte Carlo thay vì bịa một đường giao dịch đại diện. Chức năng này hỗ trợ giải thích diễn biến của một run; nó không phải một engine thứ hai độc lập tìm ra cascade từ topology. Wave trong graph được kế thừa từ event của mô hình gốc. Vì thế, một animation phản hồi có thể làm cơ chế dễ hiểu hơn nhưng chưa tạo thêm bằng chứng kiểm định ngoài mô hình hoặc xác nhận một đợt lan truyền tổn thất thực tế.

### 6.3.2 Từ typed graph tới graph gộp

Biểu diễn nhiều loại node và nhiều kiểu quan hệ giúp bảo toàn ý nghĩa từng kênh, nhưng chưa đủ để xác định một mô hình nhiều lớp hoàn chỉnh. Kivelä và cộng sự (2014) phân biệt các thành phần node–layer và quan hệ coupling khi mô tả multilayer networks. Trong DeFiStress, các nhãn layer và multiedges cho phép đọc graph dị thể nhiều quan hệ. Phép tính centrality hiện hành lại sử dụng graph có hướng đã gộp, không vận hành trên một hệ node–layer/supra-adjacency được mô tả như một động lực contagion đa tầng đầy đủ.

Quy tắc gộp trong [metrics.py](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/sim/network/metrics.py) lấy maximum normalized strength giữa các cạnh song song cùng cặp node có hướng. Nó không cộng các giá trị thô khác đơn vị và không cộng cơ học các strength để gọi thành tổng phơi nhiễm. Chẳng hạn, hai cạnh WETH→Aave giữ hai mô tả khác nhau trong typed graph, nhưng graph gộp chỉ giữ một cặp quan hệ cho tính topology. Lấy max là một quy ước so sánh có thể truy vết, không phải luật bảo toàn giá trị tài chính.

Các strength được chuẩn hóa còn phản ánh những mẫu số khác nhau: tỷ trọng thế chấp, tỷ trọng nợ, độ bao phủ candidate, áp lực thanh lý so với độ sâu, hoặc phần độ lệch giá được hồi phục. Do đó, cùng một giá trị chuẩn hóa không có nghĩa hai cạnh chuyển cùng một số USD hay cùng một xác suất gây mất an toàn. Các raw fields và đơn vị gốc phải đi cùng legend nếu hình dùng độ dày cạnh. Một mức chuẩn hóa cao của quan hệ borrower coverage chẳng hạn có thể phản ánh mức bao phủ dữ liệu, không tự đo cường độ lây lan từ người vay.

Phép tính topology cũng khác phép tính weighted influence. Centrality cấu trúc gọi graph gộp không lọc `active`, nên có thể giữ cả tuyến tiềm năng strength bằng 0; betweenness dùng hướng cạnh và không dùng trọng số. Weighted influence lại chỉ xét cạnh active, cộng outgoing normalized strength của các cặp đã gộp rồi chia cho số node khác. Với tám node, mẫu chuẩn hóa theo mã là số node trừ một; đây là quy ước chỉ số trong mạng dự án, không là mẫu số số người vay hay số giao dịch. Nhận diện khác biệt này giúp giải thích vì sao một node có thể trung gian về topology nhưng chưa có outgoing activity trong graph cấu trúc.

**Hình 6.2 (F6.2). Graph dị thể, phép gộp cạnh và phạm vi centrality.** Display specification: panel A trình bày đúng tám node và chín typed edges từ `network/structural_graph.json`; ký hiệu theo loại node và evidence status, cạnh có `active=false` nét đứt và ghi “tuyến tiềm năng”. Giữ hai cạnh WETH→Aave riêng, không tự thêm node hoặc cạnh. Panel B dùng các giá trị centrality đã lưu của cùng tám node, đơn vị không thứ nguyên; thể hiện graph dùng phép gộp max, betweenness directed/unweighted và weighted influence lọc active như hai metric riêng. Nguồn: `structural_centrality.json`, graph cùng snapshot và `sim/network/metrics.py` tại Scientific Lock. Đây là chỉ số cấu trúc trong mạng con của dự án, chưa là full multilayer contagion, DebtRank hoặc xếp hạng rủi ro toàn DeFi. Trạng thái `DISPLAY_SPEC_READY_NOT_RENDERED`; audit F6.2 lưu toàn bộ node/edge selectors và dữ liệu panel B.

### 6.3.3 Centrality và rủi ro kinh tế

Betweenness trả lời một câu hỏi về vị trí trên các đường đi ngắn nhất của graph đã chọn. Đó là nội dung khái niệm của Freeman (1977); biến thể có hướng và không trọng số trong dự án được xác định bởi mã, không được gán như một kết quả thực nghiệm của bài nguồn. Trong graph cấu trúc đã khóa, betweenness của Aave V3 là 0.19047619047619047, Uniswap V3 là 0.14285714285714285 và WETH là 0.09523809523809523. Artifact chọn Aave là `structural_bridge_node` theo quy tắc dựa trên chỉ số này.

Kết quả phù hợp với cách mạng được xây: Aave nối các phơi nhiễm người vay/tài sản với tuyến thanh lý; Uniswap nối thực thi với giá WETH; WETH nối các quan hệ giá và thế chấp. Tuy nhiên, “phù hợp” ở đây là giải thích một topology đã đặc tả, chưa phải kiểm định rằng các node đó gây ra cùng thứ hạng tổn thất. Việc bổ sung hoặc loại một vai trò, đổi hướng cạnh hay bỏ tuyến tiềm năng có thể làm thay các đường đi mà chỉ số đếm. Chương sử dụng cấu trúc đã khóa và không tính lại centrality cho một graph thuận lợi hơn.

Sự khác nhau giữa topology và activity thể hiện ngay ở Aave. Node này có betweenness dương nhưng weighted influence strength bằng 0 trong structural artifact, vì tuyến outgoing thanh lý còn inactive ở trạng thái cấu trúc. Kết quả không mâu thuẫn: một metric xét vị trí trên đường đi có thể có, metric kia tổng hợp cường độ outgoing active được gán. Nó cũng chưa nói Aave không có rủi ro hoặc không thể truyền rủi ro. Tương tự, một node betweenness bằng 0 vẫn có thể mang phơi nhiễm kinh tế; chỉ số không gắn trực tiếp với vốn hấp thụ lỗ của node đó.

Battiston và Martinez-Jaramillo (2018), trong phạm vi abstract đã được xác minh, đặt cấu trúc mạng vào bài toán stress testing và phân tích rủi ro hệ thống. Sự liên hệ đó tạo động lực phát triển chỉ tiêu tài chính, không chứng nhận một centrality bất kỳ là thước đo tác động distress. DebtRank của Battiston và cộng sự (2012) là một cách tiếp cận khác với centrality thuần cấu trúc. DeFiStress chưa triển khai DebtRank; không thể đổi tên normalized strength hoặc betweenness thành DebtRank chỉ vì các giá trị đều được chuẩn hóa.

Giá trị hiện tại của network extension là công khai các quan hệ mà mô hình dựa vào, phân biệt kênh tiềm năng với hoạt động đã có event và cho phép lần theo cách một chỉ số được tính. Để chuyển từ đó sang một mô hình lan truyền tổn thất nhiều lớp còn cần xác định phơi nhiễm có nội dung tài chính tương thích, trạng thái vốn/khả năng hấp thụ, quy tắc truyền và nguồn kiểm chứng phù hợp. Đó là điều kiện của hướng nghiên cứu tiếp theo, chưa là chức năng được kết quả hiện tại xác nhận. Bởi vậy, network bổ sung khả năng giải thích cơ chế nhưng không thay kết quả RQ bằng một thứ hạng trung tâm.

## 6.4 Tổng hợp các cấp bằng chứng

### 6.4.1 Bảng vai trò của từng lớp kiểm chứng

Ba phần trên không tạo thành ba lần kiểm định độc lập của cùng một giả thuyết. Lịch sử Aave cung cấp quan sát event và liên hệ theo mức truy vết; Terra đặt mô hình trước yêu cầu thông tin, thời điểm và biên độ của một sự kiện khác; network tổ chức các quan hệ và chỉ số trong thiết kế của dự án. Tích hợp có giá trị khi mỗi phần làm rõ điều kiện sử dụng kết quả của phần kia, thay vì cộng chúng thành một số lần “validation PASS”.

**Bảng 6.2 (T6.2). Vai trò và ranh giới của các lớp bằng chứng.** Tác giả tổng hợp từ accepted registry, các locators đã khóa và Scientific Pre-Merge Audit; claim anchors P2:C17, P2:C30, P2:C33 và `CL_INT_HISTORICAL_TIERS_PRESERVED`. Bảng phân loại học thuật, không có đơn vị hoặc mẫu số thực nghiệm chung, không tạo kết quả mới. Quan sát mã/hash không tự nâng thành empirical validation; một lớp bằng chứng không chứng minh thay lớp khác.

| Lớp bằng chứng/kiểm soát | Đối tượng được kiểm tra | Điều hỗ trợ được | Giới hạn khi dùng kết luận |
|---|---|---|---|
| Quan sát trạng thái on-chain | Snapshot, block và vị thế/pool đã thu thập | Nhận diện trạng thái khởi đầu, phạm vi danh mục và venue | Không tự xác nhận mọi trạng thái sau stress |
| Quan sát event và receipt lịch sử | Pool census, transfer route, co-occurrence theo tier | Sự kiện đã xảy ra và mức liên hệ truy vết được | Không suy trực tiếp chuỗi DEX–oracle–HF–liquidation nhân quả |
| Kết quả mô phỏng phản thực | HF chuyển trạng thái, policy và event hoàn trả dương | Kết quả có điều kiện theo quy tắc, kịch bản và tuyến tài sản | Newly eligible khác executed; không là quan sát Mainnet |
| Kiểm chứng lịch sử suy dẫn | Score Terra, lead theo ngưỡng, đối chiếu theo thiết kế | Kết quả âm của cảnh báo và giới hạn của replay | Cutoff-safe khác lựa chọn mô hình ex ante; fit khác forecast |
| Quan sát mã và chỉ số cấu trúc | Gộp cạnh, centrality, đơn vị và các cổng thực thi | Giải thích implementation và graph được dùng | Không xác nhận causal contagion, DebtRank hoặc tổn thất thực tế |
| Kiểm soát provenance/integrity | Commit, path, selector, hash và phiên bản | Nhận đúng artifact, biết diễn giải nào đang hiệu lực | Hash khớp không xác nhận mô hình đúng về kinh tế |

Một ví dụ cho quan hệ bổ trợ là giữa receipt và HF audit. Receipt có thể chỉ ra tài sản đã vào pool trong một giao dịch lịch sử, nhưng không chứa sẵn trạng thái phản thực của người vay khác. HF audit của mô hình lại kiểm được chuyển trạng thái theo giá và policy đã đặt, nhưng không biến đường giá mô hình thành nguồn giá Aave thực tế. Cả hai cùng hữu ích nếu kết luận giữ đúng phần giao nhau về cơ chế và phần chưa được kết nối về thực chứng.

Tương tự, đối chiếu cutoff kiểm một thuộc tính của pipeline thông tin, còn giá trị dự báo cần thêm thiết kế đánh giá tương ứng. Network centrality kiểm một định nghĩa toán trên topology, còn mức rủi ro kinh tế cần các đại lượng và quy tắc truyền thích hợp. Khả năng phân biệt các yêu cầu này giúp tránh việc một kiểm tra kỹ thuật thành công che một kết quả nghiên cứu không đạt kỳ vọng, như không phát hiện collapse hoặc không tái hiện đúng cung LUNA.

Provenance giữ vai trò nối các lớp nhưng không xóa ranh giới của chúng. Khi cùng một đường dẫn narrative còn mô tả ba direct links, registry và targeted route audit xác định phân tầng hiện hành. Khi một report mang nhãn strict OOS còn report khác là conditional replay, tên phiên bản và cửa sổ quyết định câu hỏi nào được trả lời. Đây là nội dung của minh bạch nghiên cứu: cho phép người đọc phục dựng lý do của cách diễn giải, kể cả khi kết quả không thuận lợi cho mô hình.

### 6.4.2 Kết nối với sáu câu hỏi chính

Đối với RQ1, lịch sử Aave cung cấp tập sự kiện và một tuyến xử lý có thể truy vết, còn điều kiện xuất hiện Wave 2 vẫn được trả lời bằng stress phản thực và đối chiếu policy ở Chương 5. Số liquidation trong một cụm lịch sử không thay cho cascade depth, vì chưa có chuỗi HF của danh mục tại các mốc để xác lập một vòng phản hồi mới. Giá trị bổ sung là làm rõ mắt xích nào có quan sát ngoài mô hình và mắt xích nào còn phụ thuộc giả định.

Với RQ2, receipt route hỗ trợ sự tồn tại của kênh tài sản thanh lý tới DEX trong giao dịch đã kiểm, nhưng không lượng hóa riêng tác động giá hoặc truyền giá vào HF. Các quan hệ cấu trúc trong network giúp phân biệt sức hấp thụ giao dịch và kênh đánh giá lại; chúng không khép khoảng trống oracle lịch sử. Do đó, kết luận về hai kênh trong Chương 5 tiếp tục có điều kiện, và không được nâng lên causal Mainnet transmission bằng cách thêm một mũi tên vào graph.

Với RQ3, sự hiện diện của một tuyến thực thi lịch sử cho thấy một quá trình xử lý cụ thể đã xảy ra, chưa cho biết ngân quỹ, khả năng recycle vốn, công suất hoặc phản ứng thời gian của toàn bộ liquidators. Network dùng vai trò đại diện, còn việc newly eligible khác executed được xác định từ audit mô hình. RQ4 cũng giữ ranh giới tương tự: các swap quan sát không tự nhận diện arbitrageur hay xác nhận quy tắc price repositioning là giao dịch có nguồn vốn. Các giới hạn thực thi và hồi giá vì thế vẫn được đọc từ đúng thiết kế của chúng.

Với RQ5, Terra mở rộng nhận thức về phản hồi giữa rút vốn, quy đổi, cung và niềm tin, đồng thời cho thấy những khó khăn khi kiểm dự báo và nhận diện proxy. Phần đó bổ sung bối cảnh cho việc giới hạn bài thử USDC ở kênh định giá nợ, không biến kết quả Terra thành một phép mô phỏng full depeg của USDC. Với RQ6, hình thức biểu diễn mạng hoặc sự khủng hoảng của một cơ chế khác cũng chưa chọn được LTV, LT hay bonus tối ưu. Ba tham số và các đơn vị/phạm vi đã làm rõ ở Chương 5 tiếp tục phải được đánh giá riêng; chương này không hiệu chỉnh lại chúng bằng ca Terra hoặc centrality.

Kết quả tích hợp của chương là một đánh giá rõ hơn về sức hỗ trợ của bằng chứng. Lịch sử xác nhận sự kiện và một tuyến tài sản ở cấp receipt; Terra giữ kết quả âm về cảnh báo cùng giới hạn của replay; mạng làm minh bạch cấu trúc đã mô hình hóa và phép tính chỉ số. Ba đóng góp đó giúp xác định nơi cần thêm quan sát hoặc một thiết kế kiểm định khác, đồng thời giữ các câu trả lời mô phỏng trong miền được hỗ trợ. Chương 7 sẽ tổng hợp đóng góp và giới hạn của toàn nghiên cứu trên nền phân công bằng chứng này; Chương 6 chưa phát hành thêm kết luận chung hoặc một bộ câu hỏi nghiên cứu mới.

## Tài liệu tham khảo sử dụng trong chương

Danh mục kế thừa các mục APA P2 đã khóa. S17/S18 là hai phiên bản của cùng nghiên cứu; phạm vi abstract/content và source locators của kết quả dự án được lưu riêng trong audit.

Battiston, S., & Martinez-Jaramillo, S. (2018). Financial networks and stress testing: Challenges and new research avenues for systemic risk analysis and financial stability implications. *Journal of Financial Stability, 35*, 6–16. https://doi.org/10.1016/j.jfs.2018.03.010

Battiston, S., Puliga, M., Kaushik, R., Tasca, P., & Caldarelli, G. (2012). DebtRank: Too central to fail? Financial networks, the FED and systemic risk. *Scientific Reports, 2*, Article 541. https://doi.org/10.1038/srep00541

Bergmeir, C., Hyndman, R. J., & Koo, B. (2018). A note on the validity of cross-validation for evaluating autoregressive time series prediction. *Computational Statistics & Data Analysis, 120*, 70–83. https://doi.org/10.1016/j.csda.2017.11.003

Freeman, L. C. (1977). A set of measures of centrality based on betweenness. *Sociometry, 40*(1), 35–41. https://doi.org/10.2307/3033543

Kivelä, M., Arenas, A., Barthelemy, M., Gleeson, J. P., Moreno, Y., & Porter, M. A. (2014). Multilayer networks. *Journal of Complex Networks, 2*(3), 203–271. https://doi.org/10.1093/comnet/cnu016

Lehar, A., & Parlour, C. A. (2022). *Systemic fragility in decentralised markets* (BIS Working Papers No. 1062). Bank for International Settlements. https://www.bis.org/publications/working-paper-1062-systemic-fragility-decentralised-markets

Liu, J., Makarov, I., & Schoar, A. (2023). *Anatomy of a run: The Terra Luna crash* (NBER Working Paper No. 31160). National Bureau of Economic Research. https://doi.org/10.3386/w31160

Liu, J., Makarov, I., & Schoar, A. (2026). Anatomy of a run: The Terra Luna crash. *Journal of Financial Economics, 184*, Article 104359. https://doi.org/10.1016/j.jfineco.2026.104359

Sasi-Brodesky, A., & Kaousar Nassr, I. (2023). *DeFi liquidations: Volatility and liquidity* (OECD Working Papers on Finance, Insurance and Private Pensions No. 48). OECD Publishing. https://doi.org/10.1787/0524faaf-en
