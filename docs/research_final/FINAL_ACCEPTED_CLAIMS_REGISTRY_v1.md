# Final Accepted Scientific Claims Registry v1

Trạng thái đề nghị: **REGISTRY_TARGETED_REPAIR_COMPLETE**. Tài liệu này không tự cấp `SCIENTIFIC_CONTENT_LOCK`.

Nguồn được pin tại integration HEAD `6560f799f81223cd4a720bd3f6b798aeef1732b9`. Output commit của registry được ghi trong Git handoff để tránh self-reference.

## Phạm vi registry

Registry có 35 scholarly claims (`P2:C01`–`P2:C35`) và 13 Integration scientific claims, tổng 48 bản ghi. 44 bản ghi được đề nghị dùng với trạng thái ACCEPTED hoặc ACCEPTED_WITH_LIMITATIONS; bốn Integration records còn lại là wording đã superseded hoặc stronger inference không được hỗ trợ.

`NOT_APPLICABLE` nghĩa là claim khái niệm không cần result định lượng; không phải PASS giả. `SOURCE_NOT_VERIFIED` giữ nguyên giới hạn đọc nguồn. `NOT_ESTABLISHED` không được chuyển thành khẳng định dương.

## Numerical claim lock

- Deterministic depth-2 A/B/Cweak/Cmoderate: `[4, 0, 0, 0]`.
- Targeted MC A/B/Cweak/Cmoderate: `[10, 0, 0, 2]`; 10 paths không phải population estimator.
- Severe Policy A: `280/10.000` depth ≥2; không phải xác suất khủng hoảng Ethereum.
- Mới đủ điều kiện theo HF/thanh lý vòng hai đã thực thi/bị bỏ qua: A `35/14/21`; B `0/0/0`; C weak `6/0/6`; C moderate `11/2/9`. Đây là borrower-case-policy instances cộng qua nhiều kịch bản, không phải người vay duy nhất.
- Lịch sử: 28 Pool events, 27 Graph-matched; tiers `1/2/23/1`; không xác lập causal contagion.
- Terra: giữ kết quả âm cutoff-safe và không có claim successful out-of-sample forecasting.

## Sáu RQ được chấp nhận có giới hạn

### RQ1 — Điều kiện và ngưỡng xuất hiện thanh lý dây chuyền.

**Nguyên văn câu hỏi nghiên cứu:** Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)?

**Kết luận đề nghị:** Thanh lý dây chuyền depth 2 tồn tại trong mô hình ở tail stress dưới chính sách định giá cụ thể, nhưng không bền với mọi chính sách oracle đã thử.

**Được báo cáo:** Có thể báo cáo Wave 2 phản thực dưới Policy A và sensitivity A/B/C; newly eligible phải tách khỏi executed Wave 2.

**Không được suy rộng:** Không có ngưỡng cascade độc lập oracle, xác suất khủng hoảng Ethereum hay xác nhận Aave dùng Uniswap spot.

**Giới hạn bắt buộc:** 280/10.000 chỉ là tần suất Severe Policy A; 10 paths được chọn có chủ đích; không có depth ≥3 trong bộ khóa.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ2 — Vai trò thanh khoản DEX.

**Nguyên văn câu hỏi nghiên cứu:** Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt?

**Kết luận đề nghị:** Thanh khoản yếu khuếch đại biến dạng DEX, còn chuyển biến đó sang HF và depth phụ thuộc chính sách định giá.

**Được báo cáo:** Có thể tách sức hấp thụ thanh khoản, immediate price impact, residual spread và HF feedback qua policy.

**Không được suy rộng:** Không suy ra mọi tác động DEX tạo eligibility hoặc cascade; haircut 90/95% không phải quan sát lịch sử tương ứng.

**Giới hạn bắt buộc:** Một pool, thanh khoản tĩnh/counterfactual, không routing đa venue và không xác minh feed lịch sử.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ3 — Gas, vốn, công suất và độ trễ thanh lý.

**Nguyên văn câu hỏi nghiên cứu:** Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý?

**Kết luận đề nghị:** Trong miền thử, các mức vốn thấp ràng buộc thanh lý. Trong tập đối chiếu mục tiêu, 36 trường hợp mới đủ điều kiện theo HF danh mục bị bỏ qua do không có khoản nợ USDC thuộc tuyến thanh lý WETH/USDC được mô hình hóa. Đây là các borrower-case-policy instances; điều kiện HF danh mục khác điều kiện thực thi theo tuyến.

**Được báo cáo:** Có thể báo cáo riêng vốn, công suất, gas/profitability, delay và route-level execution; eligibility không đồng nghĩa execution.

**Không được suy rộng:** Không gán 36 skip cho gas, vốn hoặc profitability; không suy rộng một liquidator đại diện thành thị trường bot cạnh tranh.

**Giới hạn bắt buộc:** Một liquidator đại diện, vốn không recycle, không fork execution và route mô hình chỉ WETH/USDC.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ4 — Arbitrage và phục hồi giá.

**Nguyên văn câu hỏi nghiên cứu:** Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi?

**Kết luận đề nghị:** Tác nhân kinh doanh chênh lệch giá của mô hình làm giảm độ lệch giá còn lại sau bán bắt buộc nhưng không xóa tác động giá tức thời của lần thực thi.

**Được báo cáo:** Có thể báo cáo immediate impact và post-arbitrage residual riêng biệt trong mô hình.

**Không được suy rộng:** Không gọi price repositioning là funded executable swap hoặc bằng chứng hiệu quả arbitrage Mainnet.

**Giới hạn bắt buộc:** Price teleportation, một arbitrageur, không cạnh tranh/latency/gas strategy hoặc SwapRouter fork.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ5 — Mất neo stablecoin và định giá nợ USDC.

**Nguyên văn câu hỏi nghiên cứu:** Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset?

**Kết luận đề nghị:** Giá USD của nợ USDC thay đổi HF trong kênh định giá cô lập, không đại diện toàn bộ cơ chế depeg.

**Được báo cáo:** Có thể báo cáo kênh định giá nợ USDC và tách USDC token quantity khỏi USD-equivalent.

**Không được suy rộng:** Không suy rộng thành mô hình settlement, redemption, confidence hoặc thanh khoản stablecoin đầy đủ.

**Giới hạn bắt buộc:** Ceteris paribus debt valuation; không có kênh redemption/liquidity/settlement.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ6 — Đánh đổi LTV, liquidation threshold, liquidation bonus.

**Nguyên văn câu hỏi nghiên cứu:** Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk?

**Kết luận đề nghị:** LTV điều tiết giới hạn vay ban đầu, ngưỡng thanh lý điều tiết HF và điều kiện thanh lý, còn thưởng thanh lý điều tiết khuyến khích và lượng tài sản thế chấp chuyển giao.

**Được báo cáo:** Có thể báo cáo riêng tác động của LTV, liquidation threshold và liquidation bonus trong các counterfactual khóa.

**Không được suy rộng:** Không hoán đổi ba tham số hoặc suy ra hành vi tái underwrite/borrower response ngoài mô hình.

**Giới hạn bắt buộc:** Frozen cohort; không borrower behavior hoặc re-underwriting response.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

## Sửa chữa học thuật AR-01 đến AR-05

- AR-01: tám primary evidence tiers được phân loại lại; scholarly background được lưu tách biệt và không được dùng để xác nhận implementation của dự án.
- AR-02: 16 slash-separated RQ mappings được khôi phục theo nguồn P2; sáu câu hỏi đầy đủ được lấy nguyên văn từ source đã khóa.
- AR-03: accepted Vietnamese wording đã được hòa giải cho C07/C11/C19/C23/C32/C33; kết luận RQ3 nêu rõ 36 borrower-case-policy instances không có khoản nợ USDC thuộc tuyến WETH/USDC được mô hình hóa.
- AR-04: bốn claim superseded/unsupported vẫn tồn tại làm audit trail nhưng bị loại khỏi mọi accepted RQ finding set.
- AR-05: thuật ngữ manuscript-facing được chuẩn hóa có mục tiêu; số liệu và mức xác minh nguồn không đổi.

### Accepted wording đã hòa giải

- `C07`: Thanh khoản Uniswap V3 phụ thuộc các khoảng tick. Trong mô phỏng, suy giảm độ sâu làm thay đổi khả năng hấp thụ bán thế chấp và tác động giá; eligibility mới còn phụ thuộc chính sách định giá.
- `C11`: S13 không tìm thấy tác động giá kéo dài có ý nghĩa thống kê trong thiết kế đã xét; DeFiStress mô phỏng thanh lý vòng hai ở những trường hợp stress được chọn dưới Policy A. Hai kết quả có phạm vi và chuẩn đối chiếu khác nhau.
- `C19`: Nhánh Aave của DeFiStress sử dụng một tác nhân thanh lý và một tác nhân kinh doanh chênh lệch giá đại diện.
- `C23`: Trong cấu hình baseline Policy A, Severe ghi nhận 8/200 đường mô phỏng ở P0 v2 và 280/10.000 đường ở Level-3 có độ sâu thanh lý từ hai vòng trở lên; Low Liquidity ghi nhận 0/1.000. Khoảng Wilson mô tả bất định lấy mẫu có điều kiện trong từng cấu hình.
- `C32`: Policy A của mô hình lấy giá trị nhỏ hơn giữa giá tham chiếu và giá DEX; Policy B chỉ dùng giá tham chiếu; các Policy C là giả định truyền giá có độ trễ và làm trơn. Các chính sách này chưa được xác minh là cơ chế oracle thực tế của Aave hoặc Chainlink.
- `C33`: Kiểm toán HF trong mô hình theo Policy A ghi nhận các vị thế mới mất an toàn sau Wave 1; việc mới đủ điều kiện theo HF được đối chiếu riêng với các lần thanh lý vòng hai có hoàn trả nợ dương.

## Gate và giới hạn

Builder validation: **PASS**, 28/28 gates. Test evidence: **PASS**.

Các giới hạn bắt buộc tiếp tục gồm: actual Aave/Chainlink oracle chưa được xác minh; fork validation unavailable; representative agents; extreme 90/95% haircuts là counterfactual; stablecoin chỉ có debt-valuation channel; graph extension không phải full multilayer contagion; modeled bad debt không phải realized loss; hai large CSV giữ read limitation của P2; Terra không có successful OOS forecast.
