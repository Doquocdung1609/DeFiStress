# CHƯƠNG 7. THẢO LUẬN, ĐÓNG GÓP, HẠN CHẾ VÀ KẾT LUẬN

Vấn đề đặt ra ở Chương 1 là xác định điều kiện khuếch đại rủi ro thanh lý khi vị thế vay, khả năng giao dịch và quy tắc định giá tương tác với nhau. Các chương phương pháp, dữ liệu và kết quả đã chuyển vấn đề đó thành những so sánh có trạng thái đầu vào, trình tự xử lý và chỉ tiêu xác định. Phát hiện tổng hợp là mức độ bất lợi của một cú sốc chưa đủ để quyết định toàn bộ phản ứng: giá trị danh mục cần vượt ranh giới mất an toàn, nhu cầu xử lý cần đi qua một tuyến khả thi, và tác động giao dịch chỉ tạo phản hồi HF khi chính sách định giá tiếp nhận nó.

Chương này phát triển ý nghĩa của những phân biệt đó đối với nghiên cứu rủi ro DeFi. Sáu RQ được tổng hợp thành một lập luận về cơ chế, sau đó được đối chiếu với literature, đánh giá đóng góp và đặt trong miền hiệu lực của bằng chứng. Hàm ý thực tiễn được trình bày ở tư cách nguyên tắc thiết kế và đọc stress test; các bước cần thiết để chuyển thành khuyến nghị vận hành được giữ riêng. Nguồn khoa học là Scientific Lock `3f6e5302483681209e2408531eb5a15389f9fded`; kết cấu theo Blueprint Lock `8de52bebabef376be700836e6f93a92d7394d2c3`, kế thừa sáu chương tại integration `f5f9c338a3a38ec07b3a21ba5cdc29749daf9833`. Không có kết quả định lượng mới được tạo trong phần tổng hợp.

## 7.1 Sáu câu trả lời trong một khung diễn giải

### 7.1.1 Tóm lược có điều kiện

Sáu câu hỏi cùng xem xét một chuỗi xử lý rủi ro nhưng đặt trọng tâm ở những mắt xích khác nhau. RQ1 xét sự xuất hiện của vòng thanh lý tiếp theo; RQ2 xét sức hấp thụ giao dịch và truyền giá; RQ3 xét khả năng thực hiện xử lý; RQ4 xét phần điều chỉnh sau bán; RQ5 xét phía nghĩa vụ nợ; RQ6 xét các công cụ điều tiết vị thế và động cơ. Cách tổ chức này giúp phân biệt nơi phát sinh áp lực với nơi áp lực bị hấp thụ hoặc bị chặn. Bảng 7.1 giữ nguyên câu hỏi gốc và tóm lược câu trả lời được bằng chứng hỗ trợ, thay vì sao chép lại các bảng số liệu Chương 5.

**Bảng 7.1 (T7.1). Sáu câu trả lời và điều kiện diễn giải.** Nguồn: tác giả tổng hợp từ `six_rq_accepted_claims_matrix.json` và accepted-only support sets tại Scientific Lock, đối chiếu Chương 5 đã khóa. Bảng tổng hợp văn bản, không có đơn vị đo chung hoặc mẫu số thống kê mới. Các giới hạn trong cột cuối đi cùng câu trả lời; bốn records bị loại không thuộc affirmative findings. Những chính sách A/B/C là giả định thí nghiệm, chưa phải feed Aave/Chainlink lịch sử đã kiểm chứng.

| RQ | Nguyên văn câu hỏi nghiên cứu | Câu trả lời được hỗ trợ | Bằng chứng và điều kiện sử dụng |
|---|---|---|---|
| RQ1 | Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)? | Depth 2 xuất hiện ở một số tổ hợp stress đuôi trong mô hình; điều kiện xuất hiện phụ thuộc chính sách định giá và cấu hình. | Hai lưới tất định, batch Severe Policy A và tập diagnostic được chọn; không có ngưỡng phổ quát hoặc xác suất khủng hoảng thị trường. |
| RQ2 | Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt? | Thanh khoản yếu làm tăng biến dạng DEX; biến dạng chuyển thành HF và thanh lý tiếp theo qua cơ chế định giá được đặt. | Một pool, haircut phản thực; tách absorption khỏi transmission; modeled bad debt khác tổn thất thực tế. |
| RQ3 | Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý? | Vốn thấp có thể chặn thực thi; HF danh mục mới dưới ngưỡng chưa bảo đảm tuyến WETH/USDC có thể xử lý. | Phân biệt evaluated, route-eligible, skipped và executed; một liquidator, vốn không recycle, kế hoạch không tự split; tác động gas/capacity/delay giới hạn miền thử. |
| RQ4 | Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi? | Quy tắc arbitrage của mô hình làm giảm độ lệch giá còn lại sau bán, không xóa tác động giá tức thời. | Tái định vị giá của một tác nhân đại diện, chưa là funded on-chain execution; không suy sức xử lý của arbitrageur ngoài thực tế. |
| RQ5 | Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset? | Giá USD của nợ USDC làm đổi HF trong kênh định giá cô lập; lượng token và giá trị quy đổi là hai đại lượng riêng. | Giữ các điều kiện khác theo thiết kế; chưa bao quát redemption, liquidity, confidence hoặc settlement đầy đủ. |
| RQ6 | Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk? | LTV thay giới hạn vay ban đầu, LT thay HF/điều kiện thanh lý, bonus thay động cơ và lượng tài sản chuyển giao; chưa có một biên tối ưu chung. | Danh mục và nợ đóng băng, chưa có phản ứng vay mới; giữ đúng population và đơn vị riêng của từng phép thử. |

**RQ1 — Điều kiện hình thành phản hồi.** So sánh các trường hợp stress cho thấy khả năng xuất hiện Wave 2 là một thuộc tính của cả cấu hình, không chỉ của độ lớn shock. Trong lưới mở rộng dưới A, mức shock nhỏ nhất về độ lớn trong các ô đã quan sát có depth 2 là −40%, đi cùng haircut 90% hoặc 95%; kết quả này không tạo một cutoff đơn điệu áp cho mọi cấu hình. Cú sốc ban đầu tạo nhu cầu thanh lý trực tiếp; sau đó, bán tài sản có thể làm thay giá DEX. Để tạo thêm một vị thế mất an toàn, mức giá dùng cho danh mục phải thay đủ để HF vượt ngưỡng; để thành Wave 2 execution, vị thế ấy còn phải đi qua các cổng của tuyến xử lý. Các trường hợp có depth 2 dưới A không giữ nguyên kết quả khi thay chính sách định giá trong diagnostic. Bởi vậy, một “cú sốc tối thiểu” chỉ có ý nghĩa bên trong miền tham số và quy tắc đã thử.

Kết quả này bổ sung cho cách literature đặt vấn đề phản hồi bán tài sản–giá bằng việc chỉ ra mắt xích định giá cần được đặc tả khi chuyển sang stress test. Lehar và Parlour (2022) cung cấp cơ sở nghiên cứu mối liên hệ giữa thanh lý và thị trường, còn tài liệu oracle của Aave xác định một hệ thống nguồn giá riêng (Aave, n.d.-c). DeFiStress không dùng hai nguồn ấy để mặc định rằng DEX spot là giá định danh mục thực tế. Ý nghĩa học thuật là một kết luận cascade cần công bố cả cơ chế nối thị trường giao dịch với bảng cân đối; điều kiện được mô phỏng không tự là một ngưỡng an toàn của Ethereum hay Aave Mainnet.

**RQ2 — Sức hấp thụ và truyền giá.** Kết quả về thanh khoản cho thấy cần tách hai câu hỏi: cùng một nhu cầu bán tạo biến dạng giao dịch đến đâu, và biến dạng đó tác động lên sức khỏe các khoản vay thế nào. Câu hỏi thứ nhất thuộc độ sâu và cấu trúc pool; câu hỏi thứ hai thuộc quy tắc định giá danh mục. Thanh khoản tập trung của Uniswap V3 làm chất lượng thực thi gắn với khoảng giá đang hoạt động và đường đi qua tick, nên tổng tài sản trong pool chưa thay thế được một thước đo sức hấp thụ theo hướng giao dịch (Adams và cộng sự, 2021).

Tách hai kênh giúp giải thích vì sao một DEX có biến dạng sau bán chưa nhất thiết tạo thêm thanh lý. Policy B không tiếp nhận biến dạng DEX vào HF theo thiết kế đối chiếu; các policy C truyền giá khác A theo mức độ và lịch cập nhật. Ngược lại, khi giá định giá tiếp nhận đủ tác động, vị thế gần ranh giới có thể đổi trạng thái. Đóng góp của kết quả là làm rõ điều kiện chuyển tiếp giữa rủi ro thị trường và rủi ro vị thế, thay vì coi một quan hệ thanh khoản–cascade là trực tiếp. Kết luận vẫn thuộc một venue và các haircut phản thực; nó chưa nhận diện tác động nhân quả lịch sử của một đợt rút thanh khoản.

**RQ3 — Nhu cầu xử lý và khả năng xử lý.** Tác động của vốn thấp trong bài thử đi qua một cổng quyết định: khi kế hoạch vượt vốn và không được chia nhỏ tự động, có vốn dương vẫn có thể không tạo hoàn trả dương. Ngược lại, các mức gas, công suất hoặc độ trễ đã thử có thể chưa làm đổi lượng xử lý. Những số không đổi chỉ nói cổng tương ứng chưa đổi quyết định trong miền thử, không loại vai trò của chi phí hoặc tốc độ ở cấu hình khác. Về kinh tế, quy tắc sử dụng nguồn lực quyết định cách chuyển nhu cầu xử lý thành giao dịch, bên cạnh chính mức nguồn lực.

Đối chiếu eligibility/execution còn cho thấy một giới hạn khác với thiếu vốn. Tập audit có 36 borrower–case–policy instances mới dưới ngưỡng HF nhưng bị bỏ qua do `NO_MODELLED_USDC_DEBT`. Đây là giải thích suy dẫn của route boundary, không nói nợ đã được trả hết sau Wave 1 hoặc liquidator hoạt động sai. HF xét danh mục rộng hơn phạm vi hoàn trả USDC bằng WETH của planner. Điều kiện HF được tài liệu Aave mô tả và thiết kế động cơ được literature thảo luận là nền để đặt câu hỏi, còn kết luận về từng cổng dựa vào artifact mô hình (Aave, n.d.-b; Tian và Zhu, 2025). Ý nghĩa học thuật là chất lượng xử lý cần được đo bằng cả trạng thái mất an toàn lẫn hành động đã thực hiện, với đơn vị instances được giữ đúng.

**RQ4 — Thời điểm của ổn định giá.** Quy tắc arbitrage được thử làm phần lệch giá cuối quá trình nhỏ hơn, trong khi tác động tức thời của lần bán bắt buộc vẫn được ghi nhận. Hai thước đo trả lời hai câu hỏi tài chính: điều kiện thực hiện giao dịch mà người bán đã đi qua và trạng thái giá còn lại cho bước tiếp theo. Nếu chỉ xét giá sau hồi phục, áp lực thực thi ban đầu có thể bị che; nếu chỉ xét tác động tức thời, vai trò của điều chỉnh sau bán lại bị bỏ qua. Sự phân biệt về thời điểm vì thế quan trọng hơn việc gọi một cấu hình là “ổn định” theo một chỉ tiêu duy nhất.

Lyons và Viswanath-Natraj (2023) đặt arbitrage trong quan hệ với thiết kế và khả năng tiếp cận ở bối cảnh stablecoin của nghiên cứu. Liên hệ phù hợp là coi điều chỉnh giá có điều kiện, không lấy hệ số của thị trường đó hiệu chỉnh cho WETH/USDC. Trong DeFiStress, cơ chế đã kiểm là price repositioning, chưa là một swap có ngân quỹ, tồn kho, gas và quyết toán trên chuỗi. Vì thế, giảm residual là kết quả của quy tắc được giả định; nó chưa xác nhận một năng lực arbitrage có vốn hoặc thời gian phục hồi ngoài thực tế.

**RQ5 — Stablecoin ở phía nghĩa vụ nợ.** Khi số token nợ được giữ nguyên, thay giá USD của USDC làm đổi giá trị nghĩa vụ trong mẫu số HF. Giá USDC giảm có thể làm HF tăng theo quan hệ kế toán cô lập, trong khi số token mà người vay còn phải trả không tự giảm. Đây là lý do cần báo riêng USDC quantity và USD-equivalent valuation. Một thay đổi thuận lợi của HF trong phép thử này chưa hàm ý mọi mặt của một sự kiện mất neo đều thuận lợi đối với người vay hoặc giao thức.

Kosse và cộng sự (2023) xem tính ổn định và khả năng quy đổi stablecoin trong một phạm vi rộng hơn phép quy đổi giá trị nợ. Khả năng thanh toán, thanh khoản, redemption và niềm tin có thể chuyển biến cùng lúc trong khủng hoảng, nhưng các kênh ấy chưa được phép thử RQ5 biểu diễn đầy đủ. Terra bổ sung một trường hợp khác về thiết kế rút vốn và cung, không xác nhận tham số hoặc kết quả USDC trên Aave. Đóng góp của RQ5 là xác định rõ phía bảng cân đối và phạm vi một hiệu ứng, qua đó ngăn việc chuyển một phản ứng HF thành kết luận tổng thể về depeg.

**RQ6 — Ba tham số, ba cơ chế điều tiết.** Kết quả không ủng hộ việc gộp LTV, LT và bonus thành một núm điều chỉnh rủi ro chung. LTV nới hoặc siết khả năng vay ban đầu; LT thay ranh giới phân loại sức khỏe và điều kiện xử lý; bonus thay động cơ cùng lượng thế chấp phải chuyển giao để hoàn trả nợ. Các vai trò này phù hợp với cách tài liệu reserve phân biệt tham số (Aave, n.d.-d). Trong thiết kế đóng băng, nới hạn mức chưa tạo hành vi vay thêm; tăng LT có thể làm chỉ tiêu nợ còn mất an toàn giảm mà không có thêm thu hồi nợ; tăng bonus có thể làm tài sản chuyển giao tăng trong khi lượng nợ xử lý giữ nguyên.

Theo ghi chú diễn giải đã áp dụng ở Chương 5, tổng khả năng vay LTV thuộc 255 danh mục có WETH thế chấp và có nợ, khác cohort 109 WETH/USDC. Chỉ tiêu nợ danh mục chưa thanh lý trong phép thử LT là giá trị USD tại USDC/USD = 1, theo tập vị thế truyền vào metric; không tự gán mẫu số 109 hoặc gọi đó là token USDC. Phân biệt phép đo là điều kiện để thảo luận đánh đổi hiệu quả vốn và rủi ro đuôi. Thiết kế hiện tại làm rõ các cơ chế đánh đổi nhưng chưa tạo một frontier tối ưu có phản ứng người vay và hàm mục tiêu phúc lợi chung. Tian và Zhu (2025) hỗ trợ việc đặt cơ chế thanh lý trong điều kiện chi phí tham gia, không cung cấp một mức bonus tối ưu có thể chuyển trực tiếp sang cấu hình này.

### 7.1.2 Tại sao các kết quả khác nhau

Sự khác nhau giữa các kết quả trước hết đến từ câu hỏi đo lường. Một giá DEX sau bán, một HF ở đầu wave, một lượt engine đánh giá và một giao dịch hoàn trả dương là các trạng thái liên quan nhưng khác nhau. Tương tự, liquidity depth là khả năng hấp thụ theo đường giá; số ô có depth 2 là phân loại đầu ra của lưới kịch bản. Đặt chúng dưới một nhãn “mức lây lan” sẽ bỏ mất cơ chế trung gian mà nghiên cứu cần giải thích. Kết quả zero ở một tầng cũng chưa có nghĩa mọi tầng trước nó không chịu tác động.

Khác biệt còn đến từ chính sách và thời điểm. Các policy cùng xuất phát từ một trạng thái nhưng có thể đưa thông tin DEX vào giá định danh mục ở mức và lịch khác nhau. Khi một policy tạo thêm thực thi, lượng bán và trạng thái pool tiếp theo phân kỳ; giá cuối các đường đi không còn là cùng một đầu vào chung. Vì vậy, so sánh giá tại mốc chung và so sánh kết quả toàn đường đi có chức năng khác nhau. Một tham số alpha cũng chưa cho phép nội suy tuyến tính số liquidation qua các ranh giới HF và route rời rạc.

Đối thoại với thực nghiệm cần giữ thêm chuẩn đối chiếu và horizon. Chiu và Danisman (2026) không tìm thấy tác động giá kéo dài có ý nghĩa thống kê trong thiết kế của họ; DeFiStress khảo sát phản hồi theo wave trong các stress phản thực được chọn dưới Policy A. Một kết quả về giá sau điều chỉnh benchmark và một kết quả về cơ chế giả định không phải hai phép kiểm giống nhau. Wave 2 của mô hình không bác bỏ trực tiếp empirical null của công trình nguồn. Đồng thời, nghiên cứu về thanh lý–biến động của Sasi-Brodesky và Kaousar Nassr (2023) cũng chưa khép khoảng trống nhân quả của riêng dữ liệu lịch sử DeFiStress.

Do đó, những kết quả khác nhau có thể bổ sung cho nhau bằng cách xác định điều kiện xuất hiện hoặc sự thiếu vắng của một hiệu ứng. Cơ chế bán tài sản mà Lehar và Parlour (2022) nghiên cứu tạo lý do khảo sát price impact; khác biệt policy trong DeFiStress làm rõ mắt xích định giá phải có nếu muốn diễn giải tiếp thành HF; lớp thực thi chỉ ra vì sao nhu cầu mới chưa tự thành giao dịch. Giá trị tổng hợp nằm ở việc đặt đúng câu hỏi cho từng bằng chứng, thay vì buộc literature và mô phỏng đồng thuận với một quy luật phổ quát.

## 7.2 Đóng góp có thể bảo vệ

### 7.2.1 Đóng góp phương pháp

Đóng góp phương pháp của DeFiStress là tổ chức các quan hệ lending–liquidation–DEX trong một thiết kế stress test có thể lần theo từ trạng thái ban đầu tới kết quả. Trạng thái người vay và pool được tái dựng tại block xác định; quy tắc xử lý chỉ rõ khi nào nhu cầu xuất hiện, kế hoạch nào được xét, giao dịch nào thực thi và giá nào được dùng ở bước tiếp theo. Sự tích hợp này làm cho câu trả lời về thanh lý không chỉ dựa trên một cú sốc ngoại sinh hoặc một bộ đếm cuối lượt chạy.

ABM là một hướng tiếp cận đã được phát triển trong kinh tế và tài chính, với tương tác và khác biệt tác nhân là những nội dung được tổng quan bởi Axtell và Farmer (2025). Thực hành mô phỏng stress tham số DeFi cũng xuất hiện trong nguồn ngành Gauntlet (2021); bài forum này không phải một công trình peer reviewed hoặc một đặc tả đủ để tái lập mọi phương pháp của tổ chức. Vì thế, đóng góp của đề tài không nằm ở việc phát minh thanh lý, AMM hay mô phỏng tác nhân, mà ở cách thực hiện một khung đối chiếu cụ thể và công khai miền mà nó hỗ trợ.

Việc nối đặc tả, lịch xử lý và output cũng phù hợp với yêu cầu minh bạch mô hình của Grimm và cộng sự (2020). Trong nghiên cứu này, một claim về phản hồi có thể được kiểm lại ở mốc HF, chính sách định giá, tuyến tài sản và event thay vì chỉ nhìn nhãn kịch bản. Literature cung cấp nguyên tắc mô tả, còn bằng chứng dự án xác định việc hiện thực hóa tới đâu. Cách phân vai đó giúp người đọc đánh giá một khác biệt bắt nguồn từ giả định, dữ liệu, cổng thực thi hay định nghĩa chỉ tiêu.

Một ưu điểm nghiên cứu của thiết kế đóng băng là tạo mặt bằng so sánh nhất quán khi thay từng nhóm điều kiện. Đổi policy trên cùng case làm lộ độ nhạy của mắt xích định giá; quét vốn hoặc bonus làm rõ cổng hoặc chuyển giao chịu tác động. Đổi lại, tính kiểm soát đó đi cùng sự giản lược hành vi và trạng thái thị trường. Tính hữu ích của phương pháp vì vậy nằm ở khả năng khảo sát cơ chế có điều kiện, chưa ở một tuyên bố rằng mô hình đã đại diện tốt hơn mọi phương pháp khác.

### 7.2.2 Đóng góp bằng chứng có điều kiện

Đóng góp bằng chứng nổi bật là biến các mắt xích thường bị gộp thành những kết quả có thể đối chiếu riêng. So sánh A/B/C cho thấy giả định về giá đánh giá vị thế có thể làm thay câu trả lời về Wave 2 dù cơ sở dữ liệu và case được giữ. Eligible/executed audit cho thấy ngay cả khi danh mục mới mất an toàn, phạm vi route vẫn có thể chặn việc tạo thêm bán. Hai kết quả bổ sung cho nhau: điều kiện hình thành nhu cầu và điều kiện thực thi cơ chế xử lý cùng quyết định phản hồi quan sát trong mô hình.

Điểm này có ý nghĩa đối với cách xây dựng bằng chứng stress testing. Nếu chỉ báo depth, người đọc có thể không nhận ra một policy tạo thêm HF dưới ngưỡng nhưng không có giao dịch. Nếu chỉ báo HF, họ lại có thể nhầm mọi nhu cầu mới với lượng bán đã xảy ra. Việc duy trì lớp trung gian giúp phân biệt kết quả bị chặn ở định giá, ở route hoặc ở nguồn lực. Một khẳng định về cơ chế vì vậy phải chỉ rõ mình đang nói tới trạng thái nào trong chuỗi.

**Bảng 7.2 (T7.2). Đóng góp tích hợp, đối chiếu và truy vết trong phạm vi đề tài.** Nguồn: tác giả tổng hợp từ accepted registry, literature P2 và bằng chứng ở Chương 3–6; các anchors được duyệt gồm P2:C17, P2:C31, `CL_INT_ELIGIBLE_NOT_EXECUTED` và `CL_INT_TERRA_NEGATIVE_PRESERVED`. Đây là tổng hợp học thuật, không có đơn vị hoặc mẫu số thống kê; 44 accepted candidates là phạm vi nguồn, không phải cỡ mẫu đánh giá đóng góp. Bảng không chấm điểm ưu việt hoặc đưa khuyến nghị tham số vận hành đã hiệu chỉnh.

| Phương diện đóng góp | Nội dung đã thực hiện | Căn cứ trong nghiên cứu | Phạm vi có thể bảo vệ |
|---|---|---|---|
| Tích hợp cơ chế | Nối trạng thái khoản vay, kế hoạch thanh lý, sức hấp thụ DEX và quy tắc định giá theo lịch xác định | Đặc tả Chương 3; dữ liệu/verification Chương 4 | Khung phân tích một tuyến và venue, chưa tái hiện mọi cơ chế DeFi |
| Stress test theo giả định | So sánh cùng case dưới các policy và quét điều kiện thực thi | Oracle Diagnostic; kết quả Chương 5 | Độ nhạy có điều kiện, chưa là mô hình nguồn giá Aave lịch sử |
| Phân tầng xử lý rủi ro | Tách HF eligibility, lượt được xét, route eligibility, skips và positive-repayment execution | Integration audit và T5.2 | Giải thích nhu cầu mới khác hành động; không chuyển instances thành unique wallets |
| Dữ liệu và truy vết | Giữ block, cohort, phiên bản, result/claim locators, đơn vị và nguồn của kết luận | Chuỗi provenance/đối chiếu Chương 4; hồ sơ claims | Tăng khả năng đánh giá và tái sử dụng có điều kiện, không lấy hash thay economic validation |
| Đối chiếu và kết quả âm | Phân tầng lịch sử, giữ Terra negative và giới hạn graph cấu trúc | Chương 6; accepted historical/Terra claims | Công khai nơi suy luận dừng lại; chưa dự báo thành công hoặc xác lập causal Mainnet cascade |

Khả năng truy vết còn làm thay cách đánh giá các tham số. Một thay đổi của chỉ tiêu nợ khi LT được nới có thể đến từ ranh giới phân loại, thay vì nhiều dòng tiền thu hồi hơn. Một residual rất nhỏ có thể đến từ quy tắc tái định vị, thay vì arbitrage được cấp vốn. Việc lần về định nghĩa giúp bảo vệ ý nghĩa tài chính của phép so và nhận diện những câu hỏi chưa được phép thử hiện tại trả lời.

Đóng góp này mang tính tích hợp và đối chiếu trong phạm vi nghiên cứu, không là tuyên bố đầu tiên trên thế giới hoặc một phương pháp đã chứng minh vượt trội. Bằng chứng dương về phản hồi có giá trị vì điều kiện tạo nó được công bố; bằng chứng âm có giá trị vì giúp nhận diện giới hạn. Cả hai đều cần source locators và ranh giới diễn giải tương xứng, thay vì chỉ có một tập kết quả thuận chiều với kỳ vọng ban đầu.

### 7.2.3 Minh bạch kết quả âm

Một nghiên cứu stress test không nên lấy việc tạo ra cascade làm tiêu chí thành công duy nhất. Những trường hợp không có Wave 2 giúp nhận diện nơi chuỗi phản hồi dừng lại: biến dạng chưa truyền đủ vào HF, nhu cầu không thuộc route, hoặc các cổng thực thi không cho phép xử lý. Chúng chỉ trở thành thông tin cơ chế khi được nối với trạng thái trung gian tương ứng. Một số zero tổng hợp chưa tự xác nhận an toàn, cũng chưa đủ chỉ ra tác nhân hoặc thanh khoản nào đã hấp thụ áp lực.

Terra làm rõ giá trị của việc giữ những kết quả không đạt kỳ vọng. Chương 6 ghi nhận không có giờ HIGH trước mất neo ban đầu và lead HIGH −45 giờ trong thiết kế cutoff-safe; kết quả này không hỗ trợ câu chuyện dự báo ngoài mẫu thành công. Việc conditional replay nắm một phần đồng biến giá ở thiết kế khác chưa thay thế mục tiêu cảnh báo. Literature về Terra của Liu, Makarov và Schoar (2023, 2026) cung cấp bối cảnh cơ chế, với hai phiên bản thuộc cùng một nghiên cứu; nó không chứng nhận pipeline dự báo của đề tài hoặc tham số Aave.

Tương tự, một receipt route được xác minh nhưng phần lớn liên hệ lịch sử còn ở cấp đồng xuất hiện là một kết quả đáng công bố. Nó hỗ trợ một mắt xích tài sản cụ thể và đồng thời chỉ rõ nơi bằng chứng chưa nối tới chuỗi giá–HF–thanh lý. Graph cấu trúc cũng có giá trị khi giúp đọc các quan hệ được mô hình hóa, dù chưa trở thành full multilayer contagion. Sự trung thực ở những điểm này làm cho đóng góp của mô hình có phạm vi rõ và có thể tiếp tục kiểm tra.

Minh bạch kết quả âm vì thế là một đóng góp về chất lượng suy luận, không phải cách bù cho mọi sai số hoặc thiếu dữ liệu. Công bố hạn chế chỉ có tác dụng khi nó làm thay cách sử dụng kết luận: không chọn lại một ngưỡng thuận lợi để gọi là cảnh báo ban đầu, không dùng absence trong tập thử như một quy luật an toàn, và không đổi tên chỉ số cấu trúc thành một thước đo tổn thất. Những điều kiện đó xác định giá trị của kết quả hiện tại và tiêu chí cho bước nghiên cứu tiếp theo.

## 7.3 Hạn chế và phạm vi hiệu lực

### 7.3.1 Nội bộ mô hình và dữ liệu

Phạm vi dữ liệu quyết định miền áp dụng của kết quả. Một snapshot tại block 26045352 hỗ trợ so sánh nhất quán trên cùng trạng thái, nhưng chưa cho biết kết quả ổn định tới đâu qua các giai đoạn thị trường. Tập 454 danh mục đã xác minh và cohort 109 WETH-collateral-enabled/USDC-debt có chức năng khác nhau; không phải mọi danh mục đều có cùng route. Một pool Uniswap V3 cũng chưa thể đại diện khả năng routing qua nhiều venue, rút thanh khoản LP hoặc dịch chuyển dòng giao dịch. Bởi vậy, kết quả về hấp thụ bán phản ánh một cấu trúc thanh khoản được chọn và những phép biến đổi đã khai báo.

Giá định danh mục là hạn chế cấu trúc quan trọng nhất đối với kết luận về cascade. A là adverse pass-through, B giữ tham chiếu, còn C là các proxy có mức truyền, độ trễ và làm mượt. Những lựa chọn này tạo thiết kế sensitivity, chưa được hiệu chỉnh thành mô tả feed Aave/Chainlink trong lịch sử. Cùng với đó, haircut dương là điều kiện phản thực; các mức 90% và 95% trong lưới stress là extreme tails chưa có quan sát lịch sử tương ứng. Chúng hữu ích để khảo sát cơ chế khi sức hấp thụ suy giảm rất mạnh, không tự xác định tần suất một trạng thái như vậy ngoài thị trường.

Mức đại diện tác nhân tiếp tục giới hạn khả năng ngoại suy thực thi. Một liquidator và một arbitrageur chưa tái hiện cạnh tranh, chiến lược gas, khả năng huy động vốn hoặc các tuyến thay thế của nhiều bot. Vốn liquidator không recycle, kế hoạch quá vốn không được tự chia nhỏ; chờ theo đồng hồ trong thiết kế hiện tại chưa sinh một thị trường biến động liên tục trong lúc chờ. Arbitrage price repositioning có cập nhật trạng thái pool nhưng chưa là funded executable swap. Lớp giao dịch local fork độc lập cũng chưa có thực thi được kiểm chứng; mức khớp của báo giá ban đầu không thay bằng chứng cho mọi giao dịch sau shock.

Danh mục người vay được đóng băng về hành vi. Người vay không chủ động bổ sung thế chấp, trả nợ hoặc sử dụng hạn mức mới để phản ứng với tham số. Ngoài tuyến WETH/USDC, thế chấp và nợ khác được giữ ở dạng tổng hợp USD thay vì tái định giá động từng reserve. Điều đó giới hạn cả RQ5 và RQ6: sensitivity giá nợ chưa là full depeg, khả năng vay LTV chưa tạo phân bố đòn bẩy mới, và LT/bonus chưa được đánh giá trong một cân bằng hành vi hoàn chỉnh. Các điều kiện này cần đi cùng bất kỳ hàm ý governance nào.

Cuối cùng, thước đo rủi ro phải giữ nội hàm đã định. Modeled bad debt là thiếu hụt bao phủ theo trạng thái mô hình, chưa phải tổn thất tài chính đã thực hiện. Chỉ tiêu đuôi tổng hợp còn chứa phần nợ được hoàn trả; repayment phản ánh hoạt động xử lý nợ, không phải loss của cùng một chủ thể. Vì vậy, biến động của composite tail exposure không thể được đọc tự động như biến động market Expected Shortfall đã hiệu chỉnh. Đây là giới hạn của đối tượng đo, bên cạnh giới hạn của tham số hoặc dữ liệu.

### 7.3.2 Ngoại suy và chất lượng nguồn

Monte Carlo trong nghiên cứu lấy mẫu tham số theo cấu hình đã đặt, không tái tạo một phân bố đầy đủ của thị trường tương lai. Kết quả 280/10.000 paths có depth từ hai trở lên thuộc batch Severe Policy A. Mười targeted Monte Carlo paths của diagnostic được chọn vì có depth từ hai dưới A, không phải một mẫu ước lượng tần suất mới. Các checkpoints prefix lồng nhau cũng không được cộng như các samples độc lập. Khoảng Wilson đã báo cáo chỉ diễn tả bất định lấy mẫu có điều kiện, chưa chứa đầy đủ bất định về cấu trúc hoặc hành vi. Không quan sát depth từ ba trở lên trong tập đã khóa chưa xác lập một trần cascade cho các trạng thái khác.

Ngoại suy lịch sử cần một thiết kế nhận diện riêng. Cửa sổ Aave có 28 Pool events, 27 Graph matches và các tier 1/2/23/1 trong 27 matches. Một ordered transfer path xác minh mạnh hơn same-transaction hoặc same-block association nhưng vẫn chưa xác định trọn chuỗi tác động giá và HF của người vay khác. Dữ liệu này còn khác thời điểm snapshot và chưa cung cấp borrower-state census lịch sử đầy đủ. Vì thế, liên hệ receipt hoặc timestamp chưa thể dùng để xác nhận causal contagion hoặc nguồn giá A/B/C thực tế.

Terra có những giới hạn về thông tin và thiết kế riêng: cutoff-safe của một phép tính khác lựa chọn mô hình ex ante; strict OOS khác conditional replay sau trigger; proxy và dữ liệu chưa khả dụng còn ảnh hưởng miền nhận diện. Kết quả âm được giữ nguyên như bằng chứng về năng lực hiện tại. Mạng cũng cần giới hạn tương tự: nhiều loại node/cạnh và centrality trên graph gộp chưa là một hệ lan truyền tổn thất đa tầng hoặc DebtRank đã triển khai. Kết quả của hai mở rộng hỗ trợ đánh giá phương pháp, không xác nhận tham số Aave hoặc thứ hạng rủi ro toàn DeFi.

Chất lượng citation và provenance còn đặt ranh giới cho việc đối thoại học thuật. Nguồn abstract, preview, metadata, tài liệu giao thức hiện hành và mã tham chiếu có phạm vi hỗ trợ khác nhau; chúng không được tự nâng thành fulltext hoặc xác nhận cấu hình triển khai lịch sử. S17/S18 là hai phiên bản cùng nghiên cứu; U01–U08 giữ trạng thái chưa xác minh. Hai raw borrower CSV lớn của Oracle và Integration vẫn chưa được Work rà đầy đủ từng cell. Các kết quả kiểm toán đã báo cáo được viện dẫn đúng người thực hiện/phạm vi, không gọi thành một lượt kiểm độc lập mới trong quá trình viết.

Tính toàn vẹn file giúp nhận đúng hiện vật nhưng không thay economic validation. Git LF blob bytes khác Windows CRLF checkout bytes; hash khác thuật toán hoặc miền bytes không được gọi là cùng một SHA. Tương tự, replay hoặc test do Codex báo cáo khác với kiểm tra tĩnh mà Work thực hiện khi biên soạn. Giữ các phân biệt này làm rõ mức tin cậy thực tế của từng kết luận, thay vì biến một chuỗi provenance đầy đủ thành bảo đảm đúng cho mọi cách sử dụng kết quả.

### 7.3.3 Audit các kết luận bị loại

Bốn records bị loại hoặc thay thế có vai trò như một lịch sử kiểm soát suy luận. Hai wording về RQ1 không kèm điều kiện và RQ2 chuyển trực tiếp biến dạng DEX thành eligibility đã được thay bằng kết luận có policy và hai kênh riêng. Sửa đổi này làm thay nội dung kinh tế của phát biểu: phản hồi không còn là hệ quả tất yếu của một lệnh bán, mà cần cơ chế định giá và trạng thái vị thế phù hợp. Giữ lịch sử sửa giúp người đọc thấy điều kiện đã được bổ sung ở đâu, thay vì chỉ thấy một bộ kết luận cuối cùng không có nguồn gốc.

Hai records còn lại liên quan đến nhận định Aave dùng Uniswap spot và nhận định lây lan nhân quả trong lịch sử không được bằng chứng hiện có hỗ trợ. Sự xuất hiện của chúng trong audit trail không phải tư cách accepted findings. Quan sát một giá DEX cùng thay đổi hoặc thấy nhiều liquidation trong một block chưa xác định giá oracle thực tế, hướng nhân quả hoặc một danh mục mới mất an toàn do chính hoạt động bán trước đó. Những kết luận hiện hành được trình bày ở Bảng 7.1 giữ đúng khoảng trống đó.

Nội dung audit này cũng cho thấy một nguyên tắc đánh giá mô hình: cần kiểm cả dạng câu được kết quả cho phép và các dạng mạnh hơn mà kết quả chưa cho phép. Một qualifier mất đi có thể biến sensitivity thành quy luật hoặc association thành causality, dù con số được chép đúng. Vì vậy, độ chính xác học thuật không chỉ nằm ở việc khớp numerical values mà còn ở policy, denominator, thời điểm, đơn vị và loại bằng chứng đi cùng chúng. Đây là cơ sở để bảo toàn kết luận khi tái sử dụng trong báo cáo hoặc nghiên cứu tiếp theo.

## 7.4 Hàm ý nghiên cứu và thực tiễn

### 7.4.1 Hàm ý theo dõi rủi ro

Hàm ý thứ nhất là stress testing cần báo cáo những giả định nối các cơ chế, bên cạnh mức độ cú sốc. Một kết quả có hoặc không có cascade chỉ có thể được đánh giá khi người đọc biết giá nào đi vào HF, lịch cập nhật ra sao và các cổng xử lý nào được đặt. Từ đó, so sánh policy có thể được sử dụng như một cách phát hiện kết luận nhạy với giả định, thay vì chọn một policy rồi coi output là dự báo trung tâm. Hàm ý này thuộc thiết kế kiểm tra và minh bạch mô hình; nghiên cứu chưa chỉ định một oracle vận hành tối ưu.

Hàm ý thứ hai là theo dõi sức khỏe vị thế và khả năng xử lý bằng những nhóm thông tin riêng. HF nhận diện nhu cầu theo danh mục; route và khả năng chuyển đổi tài sản quyết định phạm vi xử lý; vốn, công suất, chi phí và lợi nhuận quyết định kế hoạch có được thực thi. Một đánh giá chỉ dựa trên lượng thanh lý đã xảy ra có thể bỏ qua nhu cầu chưa xử lý, trong khi chỉ dựa trên số HF thấp có thể phóng đại lượng bán thực thi. Bài học của audit là đặt các tầng chỉ tiêu cạnh nhau và giữ nguyên đơn vị/phạm vi của chúng.

Hàm ý thứ ba là đánh giá thanh khoản và điều chỉnh giá theo thời điểm. Executable depth quanh trạng thái đang xét cung cấp nội dung khác tổng thanh khoản; immediate impact cung cấp nội dung khác residual sau arbitrage. Đối với stablecoin, vị trí ở phía tài sản hay phía nghĩa vụ nợ cũng làm thay cách diễn giải một biến động giá. Các phân biệt này gợi ý một cấu trúc phân tích kịch bản có ích cho nghiên cứu và đào tạo, chưa là bằng chứng rằng một dashboard hoặc bộ ngưỡng cảnh báo cụ thể đã giảm được tổn thất trên thị trường.

Đối với tham số rủi ro, kết quả khuyến khích đánh giá tách biệt hiệu quả vốn, phân loại an toàn và chi phí/chuyển giao khi xử lý. Một metric được cải thiện bởi thay định nghĩa ngưỡng cần được nhận diện khác với cải thiện do thu hồi nợ hoặc tăng sức hấp thụ giao dịch. Trước khi chuyển thành khuyến nghị LTV/LT/bonus, còn cần xác định hàm mục tiêu, phản ứng người vay, năng lực thực thi và dữ liệu đại diện cho điều kiện áp dụng. Đề tài cung cấp khung câu hỏi và bằng chứng có điều kiện để bắt đầu quá trình ấy, không phát hành một bộ tham số quản trị đã hiệu chỉnh cho vận hành.

### 7.4.2 Hướng phát triển có kiểm soát

Ưu tiên tiếp theo nên gắn với mắt xích có thể làm thay cách diễn giải kết quả nhiều nhất. Đối với oracle, cần thu thập và đối chiếu lịch sử nguồn giá dùng đánh giá vị thế với trạng thái DEX và thời điểm cập nhật, để đánh giá miền thực tế mà các proxy A/B/C có thể hoặc không thể đại diện. Đây là yêu cầu bằng chứng mới, không phải đổi tên một policy hiện tại thành feed đã kiểm chứng. Khi có thiết kế phù hợp, so sánh nhiều snapshot và các chế độ thị trường sẽ giúp kiểm tra kết luận nào bền hơn phạm vi một block.

Đối với thực thi, hướng phát triển có thể bổ sung ngân quỹ và tồn kho cho arbitrage, nhiều liquidators, recycle vốn, kế hoạch chia nhỏ và route/venue thay thế. Từng mở rộng cần đặc tả riêng và được đối chiếu ở đúng mức, kể cả giao dịch local fork nếu khả thi. Việc nhiều cơ chế hơn tạo ra một kết quả khác chỉ có ý nghĩa khi biết quy tắc nào thay đổi; tăng độ phức tạp không tự bảo đảm tăng độ đúng. Phản ứng của người vay đối với hạn mức, thế chấp và điều kiện thị trường cũng cần được nghiên cứu trước khi suy một frontier governance có hành vi nội sinh.

Đối với lịch sử và stablecoin, hướng đi phù hợp là nâng độ đầy đủ trạng thái và chất lượng nhận diện. Cần dữ liệu người vay tại các episode, luồng tài sản và giá theo thời điểm để kiểm chuỗi trung gian; một event study muốn phát biểu nhân quả còn cần đối chứng và xử lý các yếu tố chung tương ứng. Các kênh quy đổi, thanh khoản, settlement và niềm tin của stablecoin cần biến trạng thái và nguồn quan sát riêng. Terra nên được đánh giá bằng thiết kế ex ante/held-out phù hợp với mục tiêu cảnh báo; dùng lại sự kiện để chọn ngưỡng thuận lợi không giải quyết giới hạn đã quan sát.

Với network extension, việc phát triển tiếp cần xác định rõ node–layer, coupling, đại lượng phơi nhiễm và quy tắc truyền distress trước khi tuyên bố một mô hình contagion nhiều lớp. Chỉ số trung tâm hiện có có thể giúp đặt câu hỏi cấu trúc, nhưng một chỉ tiêu tổn thất hoặc một thuật toán mới cần được triển khai và kiểm chứng thực sự. Những hướng này là chương trình nghiên cứu tương lai, được lựa chọn theo nguồn dữ liệu và khả năng kiểm định; chúng chưa được tính vào đóng góp đã hoàn thành của DeFiStress.

## 7.5 Kết luận và điều kiện sử dụng kết quả

### 7.5.1 Kết luận cuối theo scientific lock

DeFiStress trả lời bài toán đặt ra bằng một thiết kế mô phỏng nối trạng thái khoản vay, thanh khoản giao dịch và điều kiện định giá với những cổng thực thi xác định. Kết quả cho thấy thanh lý vòng sau có thể hình thành trong một số cấu hình stress, nhưng việc xuất hiện và mức độ phản hồi phụ thuộc cách định giá vị thế, sức hấp thụ DEX và khả năng xử lý trên tuyến tài sản. Giá giao dịch, HF danh mục và giao dịch hoàn trả dương vì thế cần được xem như các tầng riêng của cùng một chuỗi rủi ro.

Sáu RQ làm rõ những vai trò bổ sung: điều kiện cascade; hai kênh absorption và transmission; ràng buộc thanh lý; điều chỉnh residual khác tác động tức thời; định giá nợ USDC khác toàn bộ depeg; và ba cơ chế LTV, LT, bonus. Nghiên cứu không cần mọi cấu hình tạo cascade để có giá trị. Những trường hợp không có vòng tiếp theo và những vị thế mới mất an toàn nhưng chưa được thực thi giúp xác định nơi chuỗi phản hồi bị giới hạn trong thiết kế được kiểm tra.

Đóng góp có thể bảo vệ nằm ở việc tích hợp các cơ chế đó với dữ liệu và chuỗi bằng chứng có thể truy vết, đồng thời duy trì cách diễn giải phản thực phù hợp. Đối chiếu lịch sử bổ sung event và một tuyến tài sản được xác minh; Terra giữ kết quả âm về cảnh báo; network làm rõ cấu trúc mà các chỉ số dựa vào. Mỗi phần giúp đánh giá mức hỗ trợ của bằng chứng thay vì được gộp thành một lời bảo đảm nhân quả hoặc dự báo. Tính hữu ích của đề tài vì vậy gắn với khả năng giải thích kết quả và điều kiện sử dụng chúng.

Theo mục tiêu Chương 1, nghiên cứu đã cung cấp một khung phân tích cơ chế và kiểm định có điều kiện trong miền dữ liệu đã khai báo. Giá trị thực tiễn trước hết là cải thiện cách đặt và đọc một stress test: công khai nguồn giá, theo dõi cả nhu cầu lẫn khả năng thực thi, giữ đúng đơn vị chỉ tiêu và phân biệt mô phỏng với lịch sử. Những điều kiện cần cho sử dụng vận hành rộng hơn vẫn là các câu hỏi phải kiểm chứng tiếp, không phải thành tích được suy ra từ bản thảo hiện tại.

### 7.5.2 Điểm kết thúc nghiên cứu hiện tại

Điểm kết thúc của nghiên cứu là tập kết luận có điều kiện được hỗ trợ bởi trạng thái, mô hình và bằng chứng đã trình bày. Không có phát hiện mới được thêm chỉ để làm phần kết luận mạnh hơn. Người sử dụng kết quả cần giữ cùng policy, scenario, cohort, định nghĩa chỉ tiêu và loại bằng chứng hoặc chỉ rõ điều kiện nào đã được thay đổi. Một output giữ nguyên con số nhưng mất qualifier về nguồn giá, tuyến tài sản hoặc mẫu số có thể đã trở thành một phát biểu khác với kết quả nghiên cứu.

Việc mở rộng dữ liệu, hành vi hoặc cơ chế vì vậy phải đi cùng một thiết kế kiểm tra và đối chiếu phiên bản riêng trước khi ghép vào kết luận. Quy tắc này không làm mất giá trị của mô hình hiện tại; nó xác định cách kế thừa giá trị ấy mà vẫn giữ khả năng đánh giá. Trên cơ sở đó, DeFiStress khép lại ở đóng góp về mô hình hóa, so sánh giả định, phân tầng kết quả và minh bạch bằng chứng cho bài toán rủi ro thanh lý DeFi. Các giới hạn đã công bố là ranh giới của kết luận hiện hành và cũng là căn cứ lựa chọn hướng phát triển tiếp theo.

## Tài liệu tham khảo sử dụng trong chương

Các mục dưới đây kế thừa nguyên danh tính và thông tin xuất bản P2. Phạm vi citation, mức truy cập và project locators được lưu riêng trong audit; hai phiên bản Liu–Makarov–Schoar không được xem là hai bằng chứng độc lập.

Aave. (n.d.-b). *Health factor & liquidations*. Retrieved October 13, 2026, from https://aave.dev/help/borrowing/liquidations

Aave. (n.d.-c). *Oracles*. Retrieved October 13, 2026, from https://aave.com/docs/aave-v3/smart-contracts/oracles

Aave. (n.d.-d). *Reserve*. Retrieved October 13, 2026, from https://www.aave.com/docs/aave-v3/concepts/reserve

Adams, H., Zinsmeister, N., Salem, M., Keefer, R., & Robinson, D. (2021). *Uniswap v3 core* [White paper]. Uniswap. https://blog.uniswap.org/whitepaper-v3.pdf

Axtell, R. L., & Farmer, J. D. (2025). Agent-based modeling in economics and finance: Past, present, and future. *Journal of Economic Literature, 63*(1), 197–287. https://doi.org/10.1257/jel.20221319

Chiu, J., & Danisman, F. (2026). *DeFi lending: Returns, leverage, and liquidation risk* (Staff Analytical Paper 2026-13). Bank of Canada. https://doi.org/10.34989/sap-2026-13

Gauntlet. (2021, January 15). *Gauntlet market risk primer* [Forum post]. Aave Governance. https://governance.aave.com/t/gauntlet-market-risk-primer/2097

Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., Edmonds, B., Ge, J., Giske, J., Groeneveld, J., Johnston, A. S. A., Milles, A., Nabe-Nielsen, J., Polhill, J. G., Radchuk, V., Rohwäder, M.-S., Stillman, R. A., Thiele, J. C., & Ayllón, D. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation, 23*(2), Article 7. https://doi.org/10.18564/jasss.4259

Kosse, A., Glowka, M., Mattei, I., & Rice, T. (2023). *Will the real stablecoin please stand up?* (BIS Papers No. 141). Bank for International Settlements. https://www.bis.org/publications/paper-141-will-real-stablecoin-please-stand-up

Lehar, A., & Parlour, C. A. (2022). *Systemic fragility in decentralised markets* (BIS Working Papers No. 1062). Bank for International Settlements. https://www.bis.org/publications/working-paper-1062-systemic-fragility-decentralised-markets

Liu, J., Makarov, I., & Schoar, A. (2023). *Anatomy of a run: The Terra Luna crash* (NBER Working Paper No. 31160). National Bureau of Economic Research. https://doi.org/10.3386/w31160

Liu, J., Makarov, I., & Schoar, A. (2026). Anatomy of a run: The Terra Luna crash. *Journal of Financial Economics, 184*, Article 104359. https://doi.org/10.1016/j.jfineco.2026.104359

Lyons, R. K., & Viswanath-Natraj, G. (2023). What keeps stablecoins stable? *Journal of International Money and Finance, 131*, Article 102777. https://doi.org/10.1016/j.jimonfin.2022.102777

Sasi-Brodesky, A., & Kaousar Nassr, I. (2023). *DeFi liquidations: Volatility and liquidity* (OECD Working Papers on Finance, Insurance and Private Pensions No. 48). OECD Publishing. https://doi.org/10.1787/0524faaf-en

Tian, P., & Zhu, Y. (2025). *Liquidation mechanisms and price impacts in DeFi* (Staff Working Paper 2025-12). Bank of Canada. https://doi.org/10.34989/swp-2025-12
