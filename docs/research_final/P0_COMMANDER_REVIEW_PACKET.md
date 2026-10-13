# P0 Commander Review — Decision Packet

Ngày thực thi: 2026-10-13  
Branch: `feat/terra-model-v2`  
Source base: `c79e090962741c051f6508d27cbf2b3105a60864e`  
Implementation/artifact commit: `672c840a15addd1c461bf502e432c09473467194`

## Quyết định đề xuất

**PASS — VERIFIED cho targeted P0 rework; chờ Commander review độc lập.** Canonical snapshot và
`corrected_run_v1` không thay đổi. Kết quả mới nằm trong `corrected_run_v2`. Không tạo DOCX final.

## Sửa đổi

1. Tách metric forced-sale intrawave impact khỏi residual spread sau arbitrage.
2. Giữ `max_price_impact` làm deprecated compatibility alias của post-arbitrage spread.
3. Sửa recovery time thành first-return semantics; `0` khi tolerance chưa từng bị vượt.
4. Cho `unliquidated_debt` dùng LT override của scenario; giữ metric legacy riêng.
5. Audit full event trace của cả 8 Severe Monte Carlo depth-2 paths.
6. Regenerate Aave/RQ/network outputs vào versioned `corrected_run_v2` và tạo diff v1→v2.

## Kết quả số học chính

- Strong Arbitrage: intrawave impact `0.0010879429953578185`; post-arbitrage spread
  `4.632569078885678e-28`.
- No Arbitrage: intrawave impact và post-arbitrage spread đều `0.0010879429953578185`.
- Severe: intrawave impact `0.005543931893162673`; post-arbitrage spread
  `0.004157948919872006`; recovery vẫn `60` giây.
- Low Liquidity, High Gas, No Arbitrage, Strong Arbitrage, Policy Experiment và Professor:
  recovery v1 `60` giây → v2 `0` vì spread chưa từng vượt tolerance 0.5%.
- RQ6 LT scenario-consistent unliquidated debt:
  `229830.81461902` tại LT 0.81/0.82/0.83; `96839.39478531` tại 0.855;
  `88458.67265557` tại 0.88.
- Severe Monte Carlo: 8/200 depth-2 paths, tần suất model-implied `0.04`, không đổi so với v1.
  Cả 8 pass borrower uniqueness, new eligibility và HF/price-state consistency.
- Structural/Professor/Severe graph numeric edge fingerprints giống v1; chỉ model-version provenance đổi.

## Commands và gate

```powershell
.\.venv\Scripts\python.exe .\scripts\research\run_p0_metric_semantics_audit.py
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy sim
.\.venv\Scripts\python.exe -m pytest
pnpm test
pnpm lint
pnpm build
```

Kết quả: 138 pytest PASS; Ruff PASS; mypy PASS; 21 Vitest PASS; frontend lint/build PASS;
10/10 research quality-gate checks PASS.

## Giới hạn còn lại

- Exogenous shock và arbitrage là price-teleportation abstractions.
- QuoterV2 chỉ xác minh initial canonical state, không xác minh counterfactual repositioned state.
- Foundry/Anvil fork liquidation transaction chưa được thực thi: `UNAVAILABLE`.
- Temporal snapshot panel và Terra genuine out-of-sample forecasting vẫn `LIMITED`.
- Monte Carlo 4% là tần suất có điều kiện trên model/scenario/seed, không phải xác suất thị trường.
