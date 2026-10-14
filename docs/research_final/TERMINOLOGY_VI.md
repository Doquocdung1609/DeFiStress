# Thuật ngữ tiếng Việt cho DeFiStress

Quy ước biên tập P2 ngày 13/10/2026, đối chiếu mã/ngữ nghĩa tại `ba62c749` ngày 14/10/2026; giữ nguyên 92 mục thuật ngữ. Lần đầu ghi tiếng Việt kèm thuật ngữ/viết tắt quốc tế; các lần sau dùng thống nhất tiếng Việt hoặc mã đo lường. Tên hợp đồng, hàm, token và trường dữ liệu giữ nguyên. Nguồn S được giải nghĩa trong danh mục APA; “mã/P2” là định nghĩa riêng của dự án, không gán cho literature. Đây là thuật ngữ học thuật và quy ước biên tập, không phải tiêu chuẩn pháp lý.

## 1. Giao thức giá và thanh lý

| Thuật ngữ gốc | Cách dùng tiếng Việt | Định nghĩa hoặc lưu ý | Căn cứ |
|---|---|---|---|
| Decentralized finance — DeFi | Tài chính phi tập trung | Dịch vụ tài chính qua giao thức/hợp đồng thông minh | S01 |
| Composability | Khả năng kết hợp giữa các giao thức | Cơ sở cho liên kết dịch vụ, không tự chứng minh lây lan | S01/S29 |
| Smart contract | Hợp đồng thông minh | Mã thực thi giao thức; tránh nói mọi hợp đồng đều bất biến/không nâng cấp | S02/S06 |
| Lending protocol | Giao thức cho vay | Phân biệt với sàn giao dịch | S02 |
| Borrower | Người vay | Ví/vị thế vay; không tự coi một ví là một người | S09; mã |
| Collateral | Tài sản thế chấp | Chỉ phần được bật dùng bảo đảm tham gia HF | S02; mã |
| Debt asset | Tài sản ghi nợ | Token làm đơn vị dư nợ, ví dụ USDC | S02/S03 |
| Overcollateralization | Thế chấp vượt giá trị khoản vay | Không loại bỏ rủi ro khi giá/thanh khoản biến động | S09 |
| Health factor — HF | Hệ số sức khỏe vị thế | Tài sản bảo đảm điều chỉnh theo LT chia giá trị nợ | S03 |
| Loan-to-value — LTV | Tỷ lệ cho vay tối đa trên giá trị thế chấp | Ràng buộc vay ban đầu; khác LT | S04 |
| Liquidation threshold — LT | Ngưỡng thanh lý | Hệ số điều chỉnh tài sản trong HF | S04 |
| Liquidation eligibility | Đủ điều kiện thanh lý | HF<1 chưa đồng nghĩa đã thực thi thành công | S03; mã |
| Liquidator | Tác nhân thanh lý | Trả nợ để nhận thế chấp theo cơ chế giao thức | S09 |
| Liquidation bonus | Mức thưởng thanh lý | Phân biệt tỷ lệ thưởng 5% và hệ số nhận 1,05 trong code | S06; mã |
| Liquidation penalty | Phần phạt thanh lý của người vay | Chi phí chịu bởi borrower; không bằng cả nợ đã trả | S13 §5.4 |
| Close factor | Tỷ lệ nợ được phép thanh lý trong một lần | Có nhánh/ngoại lệ theo phiên bản và vị thế | S06 |
| Dust | Dư nợ hoặc phần thế chấp quá nhỏ còn lại | Phải nêu ngưỡng, đơn vị và điều kiện giao thức | S06 |
| Bad debt | Nợ xấu hoặc khoản thiếu hụt theo mô hình | Dùng kèm định nghĩa; phân biệt reserve deficit | S06; mã |
| Unliquidated debt | Nợ chưa được thanh lý | Không mặc nhiên mất toàn bộ khả năng thu hồi | mã/P2 |
| Total liquidated debt | Tổng nợ đã được thanh lý | Giá trị nợ hoàn trả, không phải tổng tổn thất | S13; mã |
| Oracle price | Giá oracle dùng trong giao thức | Nguồn định giá account; khác DEX spot | S05 |
| Reference price | Giá tham chiếu | Mốc so sánh engine, không tự gọi là oracle mainnet | mã/P2 |
| Valuation price | Giá dùng để đánh giá lại vị thế | Trong engine hiện là min(reference,DEX) sau vòng | mã/P2 |
| Spot price | Giá giao ngay tức thời | Giá pool tại trạng thái đang xét | S08; mã |
| Execution price | Giá thực thi bình quân | Lượng tài sản nhận/lượng đem bán | mã/P2 |
| Price impact | Tác động giá do giao dịch | Tách intrawave trước arbitrage với residual sau arbitrage; không dùng alias làm cùng nghĩa | S07/S10 |
| Slippage | Độ trượt giá | Chênh giá kỳ vọng với thực thi; code có thể tính kèm phí | mã/P2 |
| Automated market maker — AMM | Cơ chế tạo lập thị trường tự động | Không mặc nhiên là một bot độc lập trong ABM | S07 |
| Concentrated liquidity | Thanh khoản tập trung theo khoảng giá | Không lấy tổng TVL làm độ sâu quanh giá | S07 |
| Active liquidity | Thanh khoản đang hoạt động | L dùng ở khoảng giá hiện hành | S08 |
| Tick | Mốc giá rời rạc | Giữ tên tick khi trình bày dữ liệu V3 | S08 |
| Initialized tick | Tick đã khởi tạo | Có trạng thái cần xét khi đi qua khoảng | S08 |
| liquidityNet | Thay đổi ròng thanh khoản tại tick | Dấu/hướng qua tick cần khớp mã | S08 |
| Q64.96 / sqrtPriceX96 | Biểu diễn căn giá theo Q64.96 | Giữ tên trường; chưa phải giá USD đã chuẩn hóa | S08 |
| Executable liquidity depth | Độ sâu thanh khoản có thể thực thi | Lượng giao dịch trước mức tác động giá định trước | mã/P2 |
| Liquidity haircut | Tỷ lệ suy giảm thanh khoản giả định | Biến stress; không gọi rút LP đã quan sát | mã/P2 |
| Gas cost | Phí gas hoặc phí thực thi giao dịch | Ghi đơn vị ETH, USDC hay USD rõ; tránh dùng “khí phí” | S22; mã |
| Flash loan | Khoản vay chớp nhoáng | Nguồn vốn trả trong giao dịch; không bằng vốn riêng liquidator | S10 |
| Arbitrageur | Tác nhân kinh doanh chênh lệch giá | Nhánh Aave cập nhật L qua tick khi hồi giá, vẫn là price teleportation, không funded swap | S14; mã |
| Liquidator capacity | Năng lực thanh lý mỗi bước | Khác vốn tổng bị tiêu thụ cộng dồn | mã/P2 |
| Reaction delay | Độ trễ phản ứng | Số bước × thời gian bước; không tự có đường giá trong lúc chờ | mã/P2 |

## 2. Rủi ro stablecoin và phương pháp nghiên cứu

| Thuật ngữ gốc | Cách dùng tiếng Việt | Định nghĩa hoặc lưu ý | Căn cứ |
|---|---|---|---|
| Stablecoin | Tài sản số hướng tới giá trị neo ổn định | Không gọi giá trị bảo đảm luôn bằng 1 USD | S15 |
| Peg / depeg | Neo giá / mất neo giá | Có thể lệch lên hoặc xuống; nêu mức giá và vai trò tài sản | S14/S15 |
| Redemption | Quy đổi với tổ chức/cơ chế phát hành | Khác mua bán token trên DEX | S14/S16 |
| Settlement | Hoàn tất nghĩa vụ thanh toán | Không đồng nhất với định giá khoản nợ | quy ước P2 |
| Debt-valuation channel | Kênh định giá tài sản nợ | Chỉ thay giá token nợ, các điều kiện khác cố định | mã/P2 |
| TerraUSD — UST / LUNA | UST / LUNA trong hệ Terra năm 2022 | Phân biệt tài sản lịch sử với token/chain về sau | S17 |
| Mint / burn | Phát hành / hủy token | Khi quy đổi phải chỉ rõ token tăng/giảm nguồn cung | S17; dữ liệu dự án |
| Run | Hiện tượng rút vốn dồn dập | Có thể do nhiều cơ chế tương tác; không nhất thiết bank run truyền thống | S17 |
| Contagion | Lây lan rủi ro | Phản hồi nội sinh khác cùng chịu shock chung | S10/S11; P2 |
| Liquidation wave | Đợt xử lý thanh lý | Phân biệt batch theo capacity với wave có HF trace mới mất an toàn | mã/P2 |
| Liquidation cascade | Chuỗi thanh lý do phản hồi nội sinh | P0 có path HF trace mới mất an toàn do feedback; lịch sử co-occurrence chưa là cascade | mã/P2 |
| Cascade depth | Độ sâu chuỗi hoặc chỉ số vòng xử lý | Index engine cần kiểm eligibility; bundle đã ghi depth 2, cap 100 không là 100 wave | mã/P2 |
| Cascade amplification | Hệ số khuếch đại nợ thanh lý | Tỷ số có mẫu số rõ; chỉ định nghĩa khi mẫu số dương | mã/P2 |
| Fire sale | Bán tháo tài sản dưới áp lực | Cơ chế tác động giá, chưa phải mọi lần thanh lý | S10/S12 |
| Agent-based model — ABM | Mô hình dựa trên tác tử | “Tác nhân” dùng cho vai trò kinh tế, “tác tử” dùng khi nói phương pháp | S19/S20 |
| Representative agent | Tác nhân đại diện | Code Aave chưa có quần thể liquidator cạnh tranh | mã/P2 |
| Heterogeneity | Sự không đồng nhất giữa tác nhân | Phân biệt khác số dư với khác quy tắc hành vi | S19; mã |
| ODD protocol | Quy trình mô tả ODD | Overview, Design concepts, Details; mô tả phải khớp code | S21 |
| Monte Carlo simulation | Mô phỏng Monte Carlo | Lấy mẫu kịch bản/biến; chưa mặc nhiên mô phỏng path thời gian | S23; mã |
| Random seed | Hạt giống số ngẫu nhiên | Ghi seed cùng phiên bản sinh số và dữ liệu | mã/P2 |
| Tail risk | Rủi ro ở đuôi phân phối | Phải đặt tên biến rủi ro và phân phối có điều kiện | quy ước P2 |
| Expected shortfall — ES | Tổn thất kỳ vọng ở đuôi | Chỉ dùng nếu biến đầu vào là loss có đơn vị nhất quán; code hiện exposure composite | S13; mã/P2 |
| Wilson score interval | Khoảng tin cậy Wilson cho tỷ lệ | Khác adjusted Wald và khác cận một phía | S24 |
| Model-implied probability | Xác suất có điều kiện do mô hình suy ra | Không đổi thành xác suất thị trường thực | mã/P2 |
| Counterfactual stress | Kiểm định sức chịu đựng phản thực | Thay điều kiện trong mô hình đóng băng, chưa empirical causality | quy ước P2 |
| Calibration | Hiệu chỉnh mô hình | Dữ liệu/tham số dùng trước đánh giá; không lẫn ground truth tương lai | mã/P2 |
| Verification | Kiểm tra thực thi đúng đặc tả | Tests đúng implementation không chứng minh thị trường được mô tả đúng | quy ước P2 |
| Validation | Đánh giá mức phù hợp với mục đích/dữ liệu kiểm chứng | Phạm vi dữ liệu và cơ chế phải nêu rõ | S21; quy ước P2 |
| Historical replay / reconstruction | Tái dựng diễn biến lịch sử | Retrospective; ghi có dùng dữ liệu khủng hoảng hay không | mã/P2 |
| Out-of-sample evaluation | Đánh giá ngoài mẫu | Không đồng nghĩa dự báo triển khai trong tương lai | quy ước P2 |
| Look-ahead leakage | Rò rỉ thông tin tương lai | Input/feature/parameter vượt cutoff đều cần xét | mã/P2 |
| Cutoff | Mốc chốt thông tin | Ghi timestamp/timezone, tập thông tin được phép biết | mã/P2 |
| Negative finding | Kết quả không quan sát được hiệu ứng trong miền thử | Có giá trị; không phải chứng minh hiệu ứng không tồn tại | S13; quy ước P2 |

## 3. Dữ liệu và mạng

| Thuật ngữ gốc | Cách dùng tiếng Việt | Định nghĩa hoặc lưu ý | Căn cứ |
|---|---|---|---|
| Snapshot | Ảnh chụp trạng thái tại một khối | Pin chain/block/hash, không chỉ ngày lịch | mã/P2 |
| Provenance | Nguồn gốc và quá trình hình thành dữ liệu | Nêu cả nguồn, biến đổi, phiên bản | quy ước P2 |
| Observed / derived / simulated | Quan sát / suy dẫn / mô phỏng | Ba mức chứng cứ phải tách nhãn | quy ước P2 |
| Fixture | Bộ dữ liệu kiểm thử tổng hợp | Kiểm phần mềm; không chuyển thành dữ liệu lịch sử thật | mã/P2 |
| Cohort | Nhóm vị thế được chọn để nghiên cứu | Khác toàn bộ thị trường | mã/P2 |
| Coverage | Mức bao phủ | Tỷ lệ xác minh ứng viên chưa phải market coverage | mã/P2 |
| Multilayer network | Mạng nhiều lớp | Cần xác định node–layer/kiểu coupling | S25 |
| Multiplex network | Mạng đa lớp quan hệ trên cùng thực thể | Không dùng thay mọi mạng nhiều loại nút | S25 |
| Heterogeneous network | Mạng dị thể | Nhiều loại nút/cạnh; tên phù hợp cho graph đọc hiện tại | mã/P2 |
| Directed multigraph | Đa đồ thị có hướng | Có nhiều cạnh song song; chưa tự là multilayer formalism | mã/P2 |
| Supra-adjacency matrix | Ma trận kề tổng hợp các lớp | Cần block quan hệ trong/giữa lớp; code hiện chưa dùng | S25; mã |
| Centrality | Mức độ trung tâm trong cấu trúc mạng | Chỉ có nghĩa với topology/aggregation cụ thể | S25/S26 |
| Betweenness centrality | Độ trung gian | Dựa trên shortest paths; code tính không trọng số | S28; mã |
| Structural bridge | Nút cầu nối về cấu trúc | Không tự là nguồn truyền tổn thất lớn nhất | mã/P2 |
| Eigenvector centrality | Độ trung tâm theo vector riêng | Phải ghi directed/weighted và hội tụ | mã/P2 |
| Normalized strength | Cường độ cạnh chuẩn hóa | Chuẩn hóa riêng mỗi cơ chế, không đọc là xác suất | mã/P2 |
| DebtRank | Chỉ số DebtRank về tác động distress | Khác betweenness; chưa triển khai trong DeFiStress đã đọc | S27; mã |
| Transmission channel | Kênh truyền dẫn | Cạnh tiềm năng khác dòng rủi ro đã hoạt động | mã/P2 |

Các cụm cần tránh trong bản final: “xác suất khủng hoảng Aave 1,8845%”, “thanh lý là tổng tổn thất”, “mọi vòng 2 đều là contagion”, “giá DEX chính là oracle Aave”, “nhiều cạnh chứng minh mạng nhiều lớp hoàn chỉnh”, “Terra xác nhận mô hình Aave”, “stablecoin giảm giá luôn có lợi”. Dùng giới hạn cụ thể trong file literature và ma trận thay cho những phát biểu này.

## Chú giải đo lường và evidence tier tại phiên bản ba62c749

- `max_intrawave_liquidation_price_impact`: mức lệch giá tối đa ngay sau forced sale, trước arbitrage.
- `max_post_arbitrage_spread`: mức lệch giá tối đa sau stabilization mỗi wave. `max_price_impact` là deprecated compatibility alias của chỉ tiêu này, không phải intrawave.
- `time_to_recovery_seconds`: 0 khi chưa từng vượt tolerance 0,5%; giá trị giây là first return sau khi vượt; null nếu chưa trở lại trong horizon. Báo riêng first liquidation timestamp khi xét reaction delay.
- `unliquidated_debt`: dùng LT override của scenario; `unliquidated_debt_legacy_recorded_lt` là đối chiếu cách tính cũ.
- `DIRECT_TRANSFER_PATH_VERIFIED`: receipt cho thấy tuyến WETH đúng lượng và đúng thứ tự từ liquidator qua trung gian vào pool trước `Swap`. `SAME_TRANSACTION_CO_OCCURRENCE` dùng cho hai ca cùng giao dịch không đạt tuyến trực tiếp; trace vẫn `UNAVAILABLE`.
- `SAME_BLOCK_ASSOCIATION` / `TIME_WINDOW_ASSOCIATION`: liên hệ cùng khối / cửa sổ thời gian; không là causal contagion hoặc simulated wave.
- Composite exposure tail statistic: trung bình đuôi của chỉ tiêu thiếu hụt nợ cộng nợ hoàn trả theo mô hình; field `expected_shortfall_95` không đổi thành realized loss hoặc market ES.
- Tổng hàng đã kiểm, checkpoint tái sử dụng và path chạy trong invocation là ba đại lượng khác nhau. Gói sửa xác nhận 13.000 định danh batch độc lập, 0 trùng; 10.000 hàng tái sử dụng và 0 large path chạy lại trong invocation; duration lịch sử không có trong checkpoint legacy.

Đây là chú giải các trường/tier, không thêm nguồn học thuật hay đổi tập 92 mục. Mọi nhận định mã hiện hành trong file này được gắn HEAD `ba62c749`; phiên bản tương lai cần đối chiếu lại.
