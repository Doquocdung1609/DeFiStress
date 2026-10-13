# PHƯƠNG PHÁP NGHIÊN CỨU

## 1.4 Sáu câu hỏi nghiên cứu chính

- **RQ1.** Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)?
- **RQ2.** Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt?
- **RQ3.** Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý?
- **RQ4.** Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi?
- **RQ5.** Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset?
- **RQ6.** Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk?


## Thiết kế evidence-first

Canonical Aave REAL_MAINNET tại block 26045352 được dùng cho RQ1–RQ6. Mọi counterfactual giữ snapshot và các trường ngoài one-factor cố định. Terra và multilayer network được tách thành extension.

## RQ3

Reaction delay được suy ra theo `timestep_seconds`, không hard-code đơn vị thời gian. Capital reference là tổng USDC funding được engine tiêu thụ trong finite unconstrained run; capital bị trừ và không recycle, còn per-step capacity reset mỗi wave.

## RQ5

`usdc_price_usd` mặc định 1.0. Debt value = USDC token quantity × USDC/USD + other debt đã được ghi bằng USD. Higher/lower price chỉ kiểm tra debt-valuation channel; settlement, liquidity, redemption và confidence nằm ngoài mô hình.

## RQ6 và lý do tách LTV khỏi LT

LTV là constraint phát sinh khoản vay, nên frozen debt không được viết lại. Phân tích LTV tính ex-ante max capacity/utilization. LT đi trực tiếp vào tử số Health Factor và eligibility. Bonus đi vào collateral seize, DEX quote và liquidator profitability. Các mức policy xuất phát từ WETH reserve canonical (LTV 0.805, LT 0.83, bonus 1.05) và chỉ dùng mức protocol-valid.

## Robustness và tái lập

USDC=$1 phải khớp legacy; delay không mutate input; capital không overspend; LT override không reweight other collateral; LTV không mutate debt. Lệnh chuẩn: `.\.venv\Scripts\python.exe scripts\run_full_research_pipeline.py --research`.
