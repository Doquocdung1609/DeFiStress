# NỀN TẢNG BÁO CÁO NGHIÊN CỨU CUỐI CÙNG

## TÓM TẮT

Nghiên cứu trả lời sáu câu hỏi về cascade threshold, liquidity, liquidator frictions, arbitrage, USDC debt valuation và policy parameters trên snapshot Aave V3 × Uniswap V3 REAL_MAINNET block 26,045,352. Không quan sát cascade depth ≥2 trong lưới đã thử; liquidity khuếch đại hậu quả nhưng chưa tạo wave mới; capital thấp là friction binding; USDC depeg có hướng phụ thuộc vai trò debt; LTV, LT và bonus có cơ chế khác nhau. Terra 2022 được giữ như Historical Validation Extension và graph như Multilayer Network Analysis Extension. Kết quả có provenance, claim boundary và regression comparison; không phải forecast hay xác suất thị trường. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

# 1. GIỚI THIỆU

## 1.1 Bối cảnh

DeFi nối tín dụng, thanh khoản và định giá, tạo khả năng phản hồi nội sinh. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

## 1.2 Vấn đề nghiên cứu

Vấn đề là xác định channel nào tạo hoặc khuếch đại stress mà không biến output mô hình thành observed fact.

## 1.3 Mục tiêu nghiên cứu

Đo threshold, liquidity, frictions, arbitrage, stablecoin valuation và policy trade-offs trên evidence frozen.

## 1.4 Sáu câu hỏi nghiên cứu chính

- **RQ1.** Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)?
- **RQ2.** Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt?
- **RQ3.** Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý?
- **RQ4.** Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi?
- **RQ5.** Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset?
- **RQ6.** Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk?


## 1.5 Đóng góp

Pipeline nối input hash → simulation → registry → claim → table/figure/document, giữ cả negative findings.

## 1.6 Kiểm chứng và mở rộng nghiên cứu

### A. Historical Validation Extension — Terra 2022

Terra cung cấp historical mechanism validation, conditional reconstruction, cutoff-safe early warning và historical stress evidence. Extension này không thay thế hoặc trả lời hộ sáu RQ Aave.

### B. Multilayer Network Analysis Extension — Aave × Uniswap

Đồ thị biểu diễn transmission channel, contagion topology, centrality, structural bridge và wave visualization. Centrality chỉ có nghĩa trong sub-network đã mô hình hóa, không phải total DeFi importance.


# 2. CƠ SỞ LÝ THUYẾT

Khung gồm lending risk, HF, liquidation, AMM liquidity, stablecoin balance-sheet role và contagion. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

# 3. DỮ LIỆU VÀ PHƯƠNG PHÁP

Xem `METHODOLOGY.md`; dữ liệu observed, derived và simulated được phân lớp, với snapshot/hash/seed cố định.

# 4. MÔ HÌNH

Engine mô phỏng shock → HF → liquidation → forced WETH sale → DEX impact → revaluation; parameter semantics được kiểm thử từ implementation thực tế.

# 5. KẾT QUẢ

## 5.1 Data validation

Snapshot Aave block 26,045,352 có 454 borrower xác minh và cohort WETH/USDC 109; đây không phải market coverage.

## 5.2 RQ1 — Shock threshold / cascade

**Question.** Shock tối thiểu nào tạo cascade depth ≥2?

**Method.** Lưới shock −5%…−40% × haircut 0/25/50/75%.

**Evidence/Finding.** `RQ1_GRID_MAX_CASCADE_DEPTH` = 1. Không quan sát được ngưỡng liquidation cascade trong miền stress đã thử.

**Interpretation/Limitation/Answer.** Đây là negative finding trên lưới rời rạc, không phải bằng chứng threshold nằm ngoài −40%.

## 5.3 RQ2 — Liquidity

**Question/Method.** Sweep haircut và shock × liquidity grid kiểm tra price impact, bad debt, liquidated debt và depth.

**Evidence/Finding.** Range response của max price impact và bad debt lần lượt được ghi ở `AAVE_SENS_LIQUIDITY_HAIRCUT_MAX_PRICE_IMPACT_RANGE` và `AAVE_SENS_LIQUIDITY_HAIRCUT_BAD_DEBT_RANGE`; depth vẫn dưới 2.

**Interpretation/Limitation/Answer.** Liquidity làm khuếch đại hậu quả nhưng chưa tạo liquidation wave mới trong range/snapshot/venue này.

## 5.4 RQ3 — Liquidator frictions

**Question/Method.** Kết hợp gas/capacity sweep, delay 0/1/2/4 và capital bằng 25/50/100/200% funding reference.

**Evidence/Finding.** Delay status `REACTION_DELAY_TIME_SHIFT_ONLY_NOT_SEVERITY_BINDING`; recovery time tăng từ 60 lên 300 giây trong khi severity không đổi. Required capital reference = 9063 USDC. Capital 25/50% làm total liquidated debt bằng 0/0; 100% khôi phục 9063.

**Interpretation/Limitation/Answer.** Binding: capital 25/50%. Non-binding: gas/capacity ranges cũ; delay không binding cho severity nhưng binding cho simulated processing time. Engine dùng funding cộng dồn, không tái sử dụng.

## 5.5 RQ4 — Arbitrage

**Question/Method.** Arbitrage-capacity one-factor sweep.

**Evidence/Finding.** Range response max price impact = 0; cascade depth range = 0.

**Interpretation/Limitation/Answer.** Arbitrage capacity không binding trong tested range; không suy ra arbitrage thị trường thực không quan trọng.

## 5.6 RQ5 — Stablecoin debt valuation

**Question/Method.** USDC/USD $0.90, $0.95, $0.99, $1.00, $1.01, $1.05, $1.10; chỉ revalue USDC debt tokens, không reprice `other_debt_usd`.

**Evidence/Finding.** Explicit $1 baseline tương thích legacy = True. HF<1 là 3 tại $1.10 và 1 tại $1.00; HF<1.20 tại $0.90 là 4.

**Interpretation/Limitation/Answer.** Upward depeg làm USDC debt đắt hơn theo USD và làm HF yếu đi; downward depeg làm debt value giảm và HF mạnh lên hoặc không xấu đi. **This experiment isolates the USDC debt-valuation channel.** It does not represent the full market-liquidity, redemption, settlement or confidence consequences of a real stablecoin depeg.

## 5.7 RQ6 — Policy parameters

### LTV — ex-ante capital efficiency

Capacity aggregate tăng từ 50,797,988.98 USD ở LTV 0.755 lên 53,675,575.37 USD ở 0.825. Higher LTV tăng capacity nhưng giảm origination buffer. Borrower above counterfactual capacity không được gọi là liquidatable.

### Liquidation Threshold — Health Factor boundary

Total liquidated debt là 9063 tại LT 0.83 và 0 tại LT 0.855. LT trực tiếp thay đổi WETH collateral term trong HF; other collateral giữ threshold quan sát.

### Liquidation Bonus — execution economics

Status `LIQUIDATION_BONUS_BINDING_IN_TESTED_RANGE`. Collateral seized tăng từ 4.325 WETH tại 1.03 lên 4.493 WETH tại 1.07; bonus đi qua quote/profitability path.

**Answer.** Ba parameter không thể gộp: LTV điều khiển ex-ante capital efficiency; LT điều khiển liquidation boundary; bonus điều khiển execution incentive/collateral economics.


## 5.8 Terra Historical Validation Extension

Terra giữ vai trò historical mechanism validation, reconstruction, cutoff-safe warning và counterfactual stress. Initial-depeg warning muộn và timing fit chưa hoàn hảo được giữ như negative evidence; Terra không trả lời thay RQ5 Aave.

## 5.9 Multilayer Network Analysis Extension

`NETWORK_AAVE_BETWEENNESS` = 0.1905; kết luận chỉ là structural bridge trong modeled sub-network.

## 5.10 Robustness / Monte Carlo

Fixed-seed Monte Carlo là model-implied sampling, không phải real-world probability.

## 5.11 Cross-case discussion

Điểm chung hợp lệ là phản hồi phi tuyến. `CROSS_CASE_SYNTHESIS_BOUNDARY` ngăn suy luận Terra kiểm chứng Aave hoặc ngược lại.

# 6. THẢO LUẬN

Negative result không phải lỗi mô hình: nó xác định những mechanism không binding trong snapshot/range, còn capital và một số policy channels có response rõ.

# 7. HẠN CHẾ

Một snapshot, cohort không phải toàn market, một execution venue, capital không recycle, stablecoin chỉ có valuation channel, topology nhỏ và model dependence.

# 8. HƯỚNG NGHIÊN CỨU

Mở rộng multi-collateral/debt, multi-venue, time-varying liquidity, capital recycling, stablecoin settlement/liquidity và out-of-sample validation.

# 9. KẾT LUẬN

Sáu RQ gốc đã có evidence và boundary. Terra/network là extension, không thay thế RQ chính.
