# Deep Cascade Stress Study

Trạng thái: **PASS — model execution; LIMITED — external validity**  
Model: `0.1.0-aave-v3.10-metric-semantics`  
Canonical snapshot: block 26,045,352; 454 verified borrowers; WETH/USDC cohort 109.

## Thiết kế

Runner dùng chính corrected engine, không tạo simulator thứ hai. Wave caps được so sánh ở 12, 24, 48 và 100; horizon tương ứng 32, 44, 68 và 120 steps. Một step là đơn vị mô phỏng 60 giây theo scenario hiện tại, không phải giờ lịch sử.

Grid tiền đăng ký gồm 10 shock mức −5%…−50% × 6 liquidity haircut mức 0%, 25%, 50%, 75%, 90%, 95% = 60 cells. Hai mức 90/95% là tail counterfactual, không phải depth quan sát trên Mainnet.

## Deterministic findings

Trong 60 cells:

- depth 0: 18 cells;
- depth 1: 38 cells;
- depth 2: 4 cells;
- depth ≥3: 0 cells.

Bốn depth-2 cells là `(−40%,90%)`, `(−40%,95%)`, `(−50%,90%)`, `(−50%,95%)`. Max intrawave impact lớn nhất là 10.6825% tại `(−40%,95%)`, post-arbitrage spread 5.3412%, 26 initialized ticks crossed và recovery là null vì spread vượt tolerance nhưng chưa phục hồi trong horizon. Đây là vùng giả định thanh khoản bị rút cực đoan.

Preset Severe ở cả caps 12/24/48/100 đều dừng tại depth 1 và total liquidated debt 18,126.510874 USDC. Tăng ceiling không tạo wave mới khi borrower đủ điều kiện đã cạn. Không path deterministic nào chạm cap.

Case capital được định nghĩa lại đúng cơ chế:

- 25% của unconstrained Severe required capital = 4,531.6277185 USDC: binding, không execution vì liquidation plan đầu vượt capital; unliquidated debt 238,894.08358703.
- 200% = 36,253.021748 USDC: nonbinding, khôi phục Severe result 18,126.510874 USDC.

Bảng trước sửa definition được giữ trong `deterministic_mechanisms_pre_capital_fix.csv`; thay đổi này sửa design case, không đổi engine logic.

## Monte Carlo staged results

Chuỗi Severe chính seed `20260914`, cap 100, horizon 120, dùng prefix reuse có checkpoint:

| Stage | Depth≥2 | Tần suất | Wilson 95% | Max depth |
|---:|---:|---:|---:|---:|
| 200 | 8 | 4.00% | 2.041%–7.693% | 2 |
| 1,000 | 31 | 3.10% | 2.192%–4.367% | 2 |
| 5,000 | 139 | 2.78% | 2.359%–3.273% | 2 |
| 10,000 | 280 | 2.80% | 2.494%–3.142% | 2 |

Prefix 8/200 của `corrected_run_v2` được tái lập; không tune để giữ 4%. Tại 10.000 paths, depth≥3/5/10 đều 0. Loss được định nghĩa là modeled uncovered debt + executed liquidated debt, không phải realized loss; p95 = 36,256.10584 và ES95 = 38,959.72038 theo đơn vị USD/USDC model.

Seed robustness 1.000 paths:

- `20260914`: 31/1,000 = 3.1%;
- `20261014`: 23/1,000 = 2.3%;
- `20261114`: 37/1,000 = 3.7%.

Low Liquidity prespecified: 0/1,000 depth≥2; Wilson upper 95% = 0.3827%. Không được diễn giải 0/1,000 là rủi ro bằng zero.

Tổng unique Severe primary paths là 10.000, không phải 16.200: các stage 1k/5k/10k tái dùng prefix đã xác minh. Hai seed bổ sung và Low Liquidity mỗi batch chạy 1.000 path riêng.

## Invariants và negative findings

- max observed depth = 2, không phải 100;
- 0 cap hits;
- toàn bộ metrics finite;
- không borrower bị liquidate lặp qua wave;
- mọi wave-2 borrower có initial HF≥1 tại direct-shock reference và HF<1 tại prior-wave valuation;
- không depth≥3 trong 13.000 unique paths được thực thi qua các prespecified batches;
- haircut 90/95% cho depth 2 không được gọi là observed market liquidity.

## Giới hạn mô hình

- Exogenous shock và arbitrage repositioning vẫn là price-teleport abstractions.
- Frozen borrower cohort không có borrow/repay/collateral updates xuyên thời gian.
- Liquidator capital không recycle và plan bị bỏ qua nguyên khối nếu vượt capital; không mô hình partial aggregation/flash liquidity.
- Một Uniswap venue family WETH/USDC không đại diện toàn route/MEV/CEX liquidity.
- Monte Carlo chỉ perturb shock/haircut/gas quanh scenario; tần suất là conditional sampling frequency, không phải xác suất thực tế.
- `bad_debt` là model-implied uncovered-debt estimate, không phải realized financial loss.

Evidence: `data/processed/research_final/level3_extension/deep_stress/`, gồm checkpoint, paths, diagnostics, tables và figures.
