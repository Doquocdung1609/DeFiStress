# Level-3 P1 Targeted Repair Report

Trạng thái: **READY FOR COMMANDER RE-REVIEW — NOT SCIENTIFIC LOCK**

Commander review: Issue #10, comment `6152110805`

Nguồn được kiểm duyệt: `26cd58489d726a6c98678c725650020edcc1a3f4`

Implementation commit: `2dbc7d559b7fcc1890aec9c00d8d0476c93928a9`

Artifact bundle commit: `6fcda4694d2bee3d646af7c3027caac16e9910e4`

Finalization SHA được báo cáo ngoài bundle để tránh manifest tự tham chiếu.

Word final: **không tạo**.

## Phạm vi sửa

Đợt này chỉ xử lý các yêu cầu P1 của Commander. Không chạy lại nghiên cứu Monte Carlo
10.000 path, không thay đổi mô hình, không ghi đè canonical, `corrected_run_v1`,
`corrected_run_v2`, `level3_extension` hoặc invalid-epoch attempt. Bằng chứng mới nằm tại
`data/processed/research_final/level3_p1_targeted_repair/`.

## 1. Independent Aave Pool log census

Đã enumerate read-only sự kiện `LiquidationCall` trực tiếp từ Aave V3 Pool trong cửa sổ
`2026-09-01T00:00:00Z` đến trước `2026-09-08T00:00:00Z`:

- block `25878705`–`25928919`;
- 5.022 chunk, mỗi chunk tối đa 10 block;
- log block hash được đối chiếu với canonical block;
- RPC census tìm thấy **28** sự kiện;
- Graph cung cấp **27** candidate, cả 27 đều khớp RPC;
- Graph bỏ sót **1** sự kiện; recall quan sát được là `27/28 = 96,4286%`.

Sự kiện RPC-only:

| Trường | Giá trị |
|---|---:|
| Block | `25888740` |
| Timestamp | `2026-09-02T09:33:47Z` |
| Transaction | `0x8f0ab391fcf8c1454f9665460a5d675a0821b4a53e01301c17bc239ac2fcad65` |
| Log index | `91` |
| Collateral | WETH, `0.189137810037696670` |
| Debt covered | USDT, `429.098605` |
| Receipt status | `1` |

Do đó câu đúng là: **27/27 Graph candidates được RPC xác minh, nhưng independent Pool
log census có 28 sự kiện và phát hiện một Graph omission**. Census này chứng minh độ đầy
đủ của Pool log theo address/topic/window đã khai báo, không phải census trạng thái borrower.

Quy tắc first-five chronological fallback vẫn giữ nguyên; không chọn lại episode theo kết
quả hấp dẫn hơn.

## 2. Linkage semantics và receipt Transfer routes

`classify_linkage()` không còn nâng mọi swap cùng transaction thành direct. Tier sửa đổi:

- `DIRECT_TRANSFER_PATH_VERIFIED`: 1;
- `SAME_TRANSACTION_CO_OCCURRENCE`: 2;
- `SAME_BLOCK_ASSOCIATION`: 23;
- `TIME_WINDOW_ASSOCIATION`: 1.

Chỉ route sau đạt tiêu chí direct bảo thủ:

1. Liquidator nhận đúng `3.815682452121213010 WETH` tại log 26.
2. `LiquidationCall` xuất hiện tại log 32.
3. Cùng lượng WETH đi từ liquidator qua intermediary tại log 33.
4. Cùng lượng WETH đi vào pool tại log 35.
5. Uniswap V3 `Swap` xác nhận WETH vào pool tại log 36.

Transaction `0xc546...1cfc` không đạt direct:

- event thứ nhất nhận `0.460270661833924435 WETH` nhưng swap chỉ đưa
  `0.441519628321080147 WETH` vào pool, nên không có exact-amount route;
- swap xảy ra trước event thanh lý thứ hai, vì vậy không thể là đường truyền của collateral
  từ event thứ hai.

Hai event này được hạ cấp thành `SAME_TRANSACTION_CO_OCCURRENCE`. `debug_traceTransaction`
không có trên RPC tier hiện tại và được ghi `UNAVAILABLE`; receipt evidence không được nâng
cấp thành causal market evidence.

## 3. Exact event/control-window audit

Đã re-scan cả bốn WETH/USDC pool cho cửa sổ event và control, với control center chính xác
60 phút trước event center và half-width 1/5/15/30 phút:

- 928 chunk log được quét;
- 40 tổ hợp episode/kind/window được kiểm tra;
- không có swap thiếu hoặc thừa so với locked index;
- cả năm control ±30 phút đều không chứa Aave `LiquidationCall`;
- exclusions: 0.

Control swap counts ở ±30 phút lần lượt là `1.034`, `1.182`, `1.420`, `1.504`, `1.244`.
Các con số này là theo từng cửa sổ và có thể chồng lấp; không được cộng để tuyên bố số swap
unique. Con số 31.489 trước đây là union swap quanh các event/control intervals đã khai báo,
không phải full-week Uniswap universe.

Historical timestamp clusters vẫn chỉ là nhóm sự kiện theo thời gian. Chúng hoàn toàn khác
modeled waves, nơi borrower phải trở thành newly eligible qua biến động HF. Không có kết luận
endogenous historical causation.

## 4. Monte Carlo checkpoint provenance

Không chạy lại batch lớn. Bảy checkpoint đã khóa được kiểm tra bằng file hash, scenario,
seed, target, row count, path index, path seed và prefix equality:

- independent validated paths: **13.000**;
- duplicate cross-batch identity: **0**;
- primary reused checkpoint paths: **10.000**;
- large paths executed trong invocation sửa chữa: **0**;
- independent sample paths executed: **21**;
- exact stored/reproduced row matches: **21/21**.

Các checkpoint legacy không embed canonical SHA/model version. Vì vậy bundle sửa đổi ghi rõ
external attestation: locked file hash, exact metadata/index validation và deterministic sample
reproduction với canonical SHA
`553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99`, model
`0.1.0-aave-v3.10-metric-semantics`. Không hồi tố tuyên bố rằng metadata này đã nằm trong file
cũ.

`_run_mc_stage()` đã được sửa để checkpoint mới:

- validate scenario, seed, target, canonical SHA, model version, unique ordered indices và
  content hashes;
- tách `total_validated_path_count`, `reused_checkpoint_count` và
  `executed_in_current_invocation`;
- chỉ báo historical duration khi duration thực sự được lưu;
- không còn diễn giải restore time khoảng 0,006 giây như thời gian chạy 10.000 path.

Historical execution duration của batch legacy là
`UNAVAILABLE_NOT_EMBEDDED_IN_LEGACY_CHECKPOINT`.

## 5. Wave-2 eligibility

Deterministic case `shock=-40%`, `liquidity haircut=90%` đạt depth 2. Borrower wave 2:

- direct-shock HF: `1.0211715874` — chưa eligible;
- post-wave-1/post-arbitrage valuation HF: `0.9980425717` — newly eligible;
- event HF trước liquidation khớp `0.9980425717`.

Mẫu Monte Carlo dùng quy tắc định trước: first depth-2 path trong mỗi 1.000-index stratum.
Cả 10/10 strata có wave-2 borrower thật sự mới eligible:

- direct-shock HF range: `1.00087518`–`1.00442738`;
- prior-wave-price HF range: `0.99581457`–`0.99940096`.

Đây là kiểm tra eligibility theo direct-shock và prior-wave price, không chỉ đếm số wave.

## 6. Scientific boundaries giữ nguyên

- Haircut 90%/95% là **unobserved counterfactual tails**.
- `uncovered debt + liquidated repayment` là composite modeled tail quantity, không phải
  realized economic loss và không phải market Expected Shortfall.
- Mainnet fork vẫn `UNAVAILABLE`: không có trusted local Foundry/Anvil và không có fork
  transaction nào được thực thi.
- Không gửi bất kỳ real-network transaction nào.
- Kết luận lịch sử hợp lệ vẫn là: quan sát được association và một receipt-level transfer
  route; chưa chứng minh vòng lây lan nội sinh.

## 7. Gate status

| Gate | Status |
|---|---|
| Full-window Pool log census | PASS WITH DISCLOSED GRAPH DISCREPANCY |
| Receipt transfer-route semantics | PASS |
| Exact control-window completeness | PASS |
| Checkpoint validation/accounting | PASS |
| Wave-2 newly eligible validation | PASS |
| Local Mainnet fork transactions | UNAVAILABLE |
| Commander scientific sign-off | PENDING |

Kết quả sẵn sàng để Commander nghiệm thu lại, nhưng không phải final scientific lock.
