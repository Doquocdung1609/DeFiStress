# Level-3 Commander Review Packet

Trạng thái executor: **READY FOR COMMANDER REVIEW — NOT SCIENTIFIC LOCK**  
Starting HEAD: `423bcfd4ebf910ef73b94d9deaf7cf746d8ed71c`  
Implementation commit: `92ca73c2bdd4cdcdd34c693483d17a4dbef33513`  
Artifact bundle commit: `28cf16c52c219ba2794dde7fdb22c77e147de7a0`
Provenance-finalization commit: được báo cáo ngoài bundle để tránh manifest tự tham chiếu  
Word final: **không tạo**.

## Gate summary

| Gate | Trạng thái | Bằng chứng |
|---|---|---|
| A — Pre-registration/data | PASS | Cửa sổ UTC, population, episode/control rules, budgets khóa trước discovery. |
| B — On-chain episodes | LIMITED | 27/27 events RPC verified; 3 direct tx links; một tuần không phải market coverage. |
| C — Deep simulation | PASS | 60-cell grid, caps 12/24/48/100, 10k primary MC, invariants/cap semantics. |
| D — Research integration | LIMITED | Claim ledger/tables/figures cập nhật; chưa evidence freeze P1. |
| E — Commander sign-off | PENDING | Executor không tự tuyên bố khóa khoa học. |

## Kết quả cần Commander kiểm tra

### Historical Ethereum

- Window đúng: 01–07/09/2026 UTC.
- 27 Graph-discovered Aave V3 `LiquidationCall`; 27 RPC log/receipt/block verified; 0 excluded.
- 22 clusters theo định nghĩa 5 phút; sensitivity 24/22/20/19 clusters tại 1/5/15/30 phút.
- Evidence tiers: 3 `DIRECT_TRANSACTION_LINK`, 23 `SAME_BLOCK_ASSOCIATION`, 1 `TIME_WINDOW_ASSOCIATION`.
- Direct WETH/USDC case: 8,701.80131 USDC debt, 3.8156824521 WETH collateral, cùng transaction có Uniswap V3 swap đúng 3.8156824521 WETH.
- Kết luận: **Quan sát lịch sử có liên hệ theo thời gian, chưa chứng minh vòng lây lan nội sinh**.

### Fork

- `ETH_ARCHIVE_RPC_URL`: configured.
- `forge`/`anvil`: unavailable.
- Executed fork transactions: 0.
- Status: `UNAVAILABLE`, không PASS giả.

### Deep deterministic/Monte Carlo

- Largest configured cap: 100; largest horizon: 120.
- Max observed depth: 2 deterministic và 2 Monte Carlo; cap hits: 0.
- Grid 60 cells: depth 0/1/2 = 18/38/4; bốn depth-2 cells chỉ ở shock −40/−50% với haircut 90/95%.
- Severe 10k: 280/10,000 depth≥2 = 2.8%; Wilson 95% 2.494%–3.142%; depth≥3 = 0.
- Seed robustness 1k: 3.1%, 2.3%, 3.7%.
- Low Liquidity 1k: 0 depth≥2; Wilson upper 0.3827%.
- Không borrower trùng, wave-2 eligibility hợp lệ, metrics finite, không numerical cap saturation.

## Corrections trong execution

1. Epoch constant attempt đầu lệch −3 giờ. Attempt được giữ và gắn FAIL; run đúng cửa sổ có 27 thay vì 28 events.
2. Case “Capital 25%” ban đầu lấy 25% total portfolio debt nên không binding. Sửa design runner thành 25% unconstrained Severe required capital; case mới binding. Core engine, canonical và corrected runs không đổi.

## Claims còn hợp lệ

- corrected_run_v2 metric semantics và canonical 454/109 vẫn nguyên vẹn.
- Engine có thể sinh endogenous Wave 2 trong một phần tail paths/cells; mọi path được audit eligibility.
- Kênh liquidation WETH → Uniswap có ít nhất ba transaction-level historical links trong tuần đã chọn.
- Tăng wave cap không tự tạo thêm waves; observed depth phải báo riêng.

## Claims không được phép

- “Đã quan sát cascade 100 vòng”.
- “2.8% là xác suất cascade ngoài đời”.
- “Same-block swap chứng minh causal liquidation flow”.
- “Local Mainnet fork validation PASS”.
- “27 events là full market coverage hoặc full borrower backtest”.
- “Modeled bad debt là realized loss”.

## Quyết định còn cần Commander

1. Chấp nhận Gate B ở mức LIMITED hay yêu cầu thêm nhiều tuần/chế độ thị trường.
2. Có cung cấp môi trường Foundry/Anvil để mở Gate Level-2 hay giữ UNAVAILABLE.
3. Có chấp nhận 90/95% haircut chỉ như tail mechanism experiment, không dùng làm empirical calibration.
4. Reconcile extension này vào P1 issue #3 trước evidence freeze.
5. Chỉ sau sign-off mới tiếp tục manuscript/Word final.

## Reproduce

```powershell
.\.venv\Scripts\python.exe scripts/research/run_level3_historical_study.py
.\.venv\Scripts\python.exe scripts/research/run_level2_fork_validation.py
.\.venv\Scripts\python.exe scripts/research/run_deep_cascade_study.py --research --max-waves 100 --horizon-steps 120 --workers 4
.\.venv\Scripts\python.exe scripts/research/build_level3_evidence_bundle.py
```

Các runner từ chối overwrite artifact hoàn chỉnh. Để reproduce ở đường dẫn mới, truyền `--output-dir` cho historical/deep runners; fork evidence hiện dùng path chuẩn của extension.
