# Báo cáo khóa bằng chứng định lượng Frozen v3

Trạng thái: **P1_NUMERICAL_READY — AWAITING_P2_CITATION_RECONCILIATION**

Starting HEAD: `ba62c74950a72751e0030527836082da0c7622ef`  
Implementation commit: `54e6779c1f1fd8974c059ab6750bad0be0d88940`  
Artifact bundle commit: xem `manifest.json` (được điền trong bước đóng gói provenance).

## Quy tắc nguồn chuẩn

`Original → P0 corrected v2 → Level-3 → Level-3 targeted repair → Frozen v3`.

Frozen v3 là lớp registry/synthesis; không retune mô hình và không ghi đè artifact cũ. Canonical snapshot block 26.045.352 giữ SHA-256 `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99`.

## Sự thật đã khóa

- 454 borrower được RPC xác minh; cohort WETH collateral-enabled + USDC debt có 109 vị thế. Tỷ lệ xác minh ứng viên không phải market coverage.
- Lưới cũ 32 ô: depth 0/1/2 = 12/20/0. Lưới mở rộng 60 ô: 18/38/4.
- Severe Monte Carlo: 280/10.000 đường depth ≥2 (2,8%); 0 depth ≥3. 100 wave là cap, không phải độ sâu đạt được.
- Cửa sổ 01–07/09/2026: 28 `LiquidationCall` trong RPC census; 27 Graph-matched; một RPC-only event.
- Trong 27 Graph-matched: 1 direct transfer path, 2 same-transaction co-occurrences, 23 same-block, 1 time-window. Không suy diễn causal chain.
- P0 tách immediate price impact khỏi post-arbitrage spread, processing delay khỏi recovery, và scenario-LT unliquidated debt khỏi legacy recorded-LT comparison.

## Ngữ nghĩa metric bắt buộc

`bad_debt` là model-based uncovered debt estimate, không mặc định là realized financial loss. `unliquidated_debt` là nợ đủ điều kiện nhưng chưa được thực thi trong điều kiện kịch bản. `liquidation_at_risk` là exposure đủ điều kiện trước giới hạn execution. `cascade_depth` đếm positive liquidation waves. `cascade_amplification` so tổng nợ thanh lý với direct-shock liquidation. `time_to_recovery_seconds` chỉ có nghĩa khi residual spread thực sự vượt tolerance. Monte Carlo tail quantity là composite modeled quantity, không gọi là realized loss hay market expected shortfall.

## Terra và phần mở rộng mạng

Terra cutoff-safe có 0 HIGH alert trong 1.630 giờ trước initial depeg; HIGH threshold đến muộn 45 giờ so với UST<0,995. Không có claim out-of-sample forecasting. Không có dữ liệu DEX liquidity hoặc LFG intervention quan sát đầy đủ. Network analysis chỉ là sub-network Aave–Uniswap/structural extension.

## Citation P2

Năm file literature của PR #9 không được sửa trong P1 này. Citation cuối chỉ được hòa giải sau khi Commander duyệt minimal delta của P2. Vì vậy không tuyên bố `SCIENTIFIC_CONTENT_LOCK`.
