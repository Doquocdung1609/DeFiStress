# Final Accepted Scientific Claims Registry v1

Trạng thái đề nghị: **FINAL_REGISTRY_READY_FOR_COMMANDER_REVIEW**. Tài liệu này không tự cấp `SCIENTIFIC_CONTENT_LOCK`.

Nguồn được pin tại integration HEAD `6560f799f81223cd4a720bd3f6b798aeef1732b9`. Output commit của registry được ghi trong Git handoff để tránh self-reference.

## Phạm vi registry

Registry có 35 scholarly claims (`P2:C01`–`P2:C35`) và 13 Integration scientific claims, tổng 48 bản ghi. 44 bản ghi được đề nghị dùng với trạng thái ACCEPTED hoặc ACCEPTED_WITH_LIMITATIONS; bốn Integration records còn lại là wording đã superseded hoặc stronger inference không được hỗ trợ.

`NOT_APPLICABLE` nghĩa là claim khái niệm không cần result định lượng; không phải PASS giả. `SOURCE_NOT_VERIFIED` giữ nguyên giới hạn đọc nguồn. `NOT_ESTABLISHED` không được chuyển thành khẳng định dương.

## Numerical claim lock

- Deterministic depth-2 A/B/Cweak/Cmoderate: `[4, 0, 0, 0]`.
- Targeted MC A/B/Cweak/Cmoderate: `[10, 0, 0, 2]`; 10 paths không phải population estimator.
- Severe Policy A: `280/10.000` depth ≥2; không phải xác suất khủng hoảng Ethereum.
- Eligible/executed/skipped: A `35/14/21`; B `0/0/0`; C weak `6/0/6`; C moderate `11/2/9`. Đây là borrower-case instances cộng qua nhiều kịch bản, không phải unique borrowers.
- Lịch sử: 28 Pool events, 27 Graph-matched; tiers `1/2/23/1`; không xác lập causal contagion.
- Terra: giữ kết quả âm cutoff-safe và không có claim successful out-of-sample forecasting.

## Sáu RQ được chấp nhận có giới hạn

### RQ1 — Điều kiện và ngưỡng xuất hiện thanh lý dây chuyền.

**Kết luận đề nghị:** Thanh lý dây chuyền depth 2 tồn tại trong mô hình ở tail stress dưới chính sách định giá cụ thể, nhưng không bền với mọi chính sách oracle đã thử.

**Được báo cáo:** Có thể báo cáo Wave 2 phản thực dưới Policy A và sensitivity A/B/C; newly eligible phải tách khỏi executed Wave 2.

**Không được suy rộng:** Không có ngưỡng cascade độc lập oracle, xác suất khủng hoảng Ethereum hay xác nhận Aave dùng Uniswap spot.

**Giới hạn bắt buộc:** 280/10.000 chỉ là tần suất Severe Policy A; 10 paths được chọn có chủ đích; không có depth ≥3 trong bộ khóa.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ2 — Vai trò thanh khoản DEX.

**Kết luận đề nghị:** Thanh khoản yếu khuếch đại biến dạng DEX, còn chuyển biến đó sang HF và depth phụ thuộc chính sách định giá.

**Được báo cáo:** Có thể tách sức hấp thụ thanh khoản, immediate price impact, residual spread và HF feedback qua policy.

**Không được suy rộng:** Không suy ra mọi tác động DEX tạo eligibility hoặc cascade; haircut 90/95% không phải quan sát lịch sử tương ứng.

**Giới hạn bắt buộc:** Một pool, thanh khoản tĩnh/counterfactual, không routing đa venue và không xác minh feed lịch sử.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ3 — Gas, vốn, công suất và độ trễ thanh lý.

**Kết luận đề nghị:** Vốn thấp có tính ràng buộc trong miền thử; execution phụ thuộc các cổng riêng và các skip targeted là route-ineligible do không còn modeled USDC debt.

**Được báo cáo:** Có thể báo cáo riêng vốn, công suất, gas/profitability, delay và route-level execution; eligibility không đồng nghĩa execution.

**Không được suy rộng:** Không gán 36 skip cho gas, vốn hoặc profitability; không suy rộng một liquidator đại diện thành thị trường bot cạnh tranh.

**Giới hạn bắt buộc:** Một liquidator đại diện, vốn không recycle, không fork execution và route mô hình chỉ WETH/USDC.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ4 — Arbitrage và phục hồi giá.

**Kết luận đề nghị:** Arbitrage mô hình làm giảm residual spread sau forced sale nhưng không xóa tác động tức thời của execution.

**Được báo cáo:** Có thể báo cáo immediate impact và post-arbitrage residual riêng biệt trong mô hình.

**Không được suy rộng:** Không gọi price repositioning là funded executable swap hoặc bằng chứng hiệu quả arbitrage Mainnet.

**Giới hạn bắt buộc:** Price teleportation, một arbitrageur, không cạnh tranh/latency/gas strategy hoặc SwapRouter fork.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ5 — Mất neo stablecoin và định giá nợ USDC.

**Kết luận đề nghị:** Giá USD của nợ USDC thay đổi HF trong kênh định giá cô lập, không đại diện toàn bộ cơ chế depeg.

**Được báo cáo:** Có thể báo cáo kênh định giá nợ USDC và tách USDC token quantity khỏi USD-equivalent.

**Không được suy rộng:** Không suy rộng thành mô hình settlement, redemption, confidence hoặc thanh khoản stablecoin đầy đủ.

**Giới hạn bắt buộc:** Ceteris paribus debt valuation; không có kênh redemption/liquidity/settlement.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

### RQ6 — Đánh đổi LTV, liquidation threshold, liquidation bonus.

**Kết luận đề nghị:** LTV điều tiết capacity ex ante, LT điều tiết HF/eligibility và bonus điều tiết incentive/collateral transfer.

**Được báo cáo:** Có thể báo cáo riêng tác động của LTV, liquidation threshold và liquidation bonus trong các counterfactual khóa.

**Không được suy rộng:** Không hoán đổi ba tham số hoặc suy ra hành vi tái underwrite/borrower response ngoài mô hình.

**Giới hạn bắt buộc:** Frozen cohort; không borrower behavior hoặc re-underwriting response.

**Trạng thái:** `ACCEPTED_WITH_LIMITATIONS`.

## Gate và giới hạn

Builder validation: **PASS**, 22/22 gates. Test evidence: **PASS**.

Các giới hạn bắt buộc tiếp tục gồm: actual Aave/Chainlink oracle chưa được xác minh; fork validation unavailable; representative agents; extreme 90/95% haircuts là counterfactual; stablecoin chỉ có debt-valuation channel; graph extension không phải full multilayer contagion; modeled bad debt không phải realized loss; hai large CSV giữ read limitation của P2; Terra không có successful OOS forecast.
