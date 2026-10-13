# TÓM TẮT ĐIỀU HÀNH

## Trả lời RQ1–RQ6

- **RQ1 — NOT OBSERVED.** Không quan sát được ngưỡng liquidation cascade trong lưới shock −5% đến −40% và haircut 0/25/50/75%; cascade depth lớn nhất là 1. Không được ngoại suy ra ngoài miền đã thử.
- **RQ2 — SUPPORTED WITH BOUNDARY.** Liquidity haircut làm price impact và bad debt thay đổi, nhưng không tạo wave mới trong lưới; consequence amplification khác cascade creation.
- **RQ3 — PARTIAL.** Gas và capacity sweep không binding; delay 0/1/2/4 chỉ dịch recovery time; capital 25% và 50% của reference 9063 USDC binding, 100% và 200% non-binding.
- **RQ4 — NEGATIVE FINDING.** Arbitrage capacity không làm đổi tested outcomes; price deviation nhỏ và agent không trở thành binding trong range.
- **RQ5 — SUPPORTED FOR ONE CHANNEL.** Tại USDC $1.10 có 3 borrower HF<1, so với 1 ở $1.00. Downward depeg không làm HF xấu hơn trong pure valuation semantics.
- **RQ6 — SUPPORTED AS THREE DISTINCT MECHANISMS.** LTV tăng ex-ante borrowing capacity; LT dịch HF/liquidation boundary; bonus đổi collateral seized và expected profit. LTV không phải direct frozen-snapshot liquidation trigger.


## Historical Validation Extension — Terra 2022

Historical Fit hỗ trợ reconstruction có điều kiện nhưng timing chưa hoàn hảo; cutoff-safe warning muộn cho depeg ban đầu; mechanism accounting được hỗ trợ mà không nâng thành price causality.

## Multilayer Network Analysis Extension

Aave là bridge trong topology nhỏ đã mô hình hóa. Kết quả không đại diện total DeFi importance.

Mọi con số ánh xạ đến `results_registry.json`; claim và boundary nằm trong `claim_ledger.json`.
