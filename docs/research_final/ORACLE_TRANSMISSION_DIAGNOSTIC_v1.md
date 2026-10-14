# Oracle Transmission Diagnostic v1

Trạng thái: **LIMITED — TARGETED MODEL DIAGNOSTIC; AWAITING COMMANDER REVIEW**. Tài liệu này không tự cấp `SCIENTIFIC_PASS` và không tạo `SCIENTIFIC_CONTENT_LOCK`.

## 1. Câu hỏi và phạm vi

Thí nghiệm cô lập giả định truyền giá dùng để đánh giá Health Factor (HF) giữa các vòng thanh lý. Nó không xác minh oracle Aave/Chainlink thực tế và không phải giao dịch Mainnet. Bộ chạy gồm bốn deterministic depth-2 cases, bốn deterministic controls và đúng mười Monte Carlo paths đã được kiểm toán từ trước; không chạy lại 10.000 paths. Engine đánh giá toàn bộ `454` verified borrowers; `109` chỉ là WETH/USDC target cohort của snapshot và không phải mẫu số của thí nghiệm này.

- Starting HEAD: `9842c4f2c35adb8b4ec906e1bc76afa825d197c7`.
- Selection-lock commit: `a2c37e3d513054131083b791a05f8b50047925fd`.
- Source-code commit của adapter/runner: `619faed07583de36fc29e8b9c3c30788c1819644`.
- Canonical snapshot: block `26045352`, SHA-256 `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99`.
- Frozen v3 manifest SHA-256 trước/sau: `0ee158ad67cd16a009a6d064960619fd03ab93657d12fa25f4b860e351157613`; không thay đổi.

## 2. Thiết kế đã tiền đăng ký

- **Policy A — adverse pass-through:** giá định giá vòng kế tiếp là `min(reference_price, dex_spot)`; đây là hành vi engine gốc.
- **Policy B — reference-only:** HF chỉ dùng `reference_price`; mọi thành phần khác giữ nguyên.
- **Policy C weak:** proxy giả định nhân quả, hệ số `0.25`, lag `1`, cửa sổ `3`.
- **Policy C moderate:** proxy giả định nhân quả, hệ số `0.50`, lag `1`, cửa sổ `2`.

Policy C chỉ đọc DEX observations đã hoàn tất đến cuối vòng trước, không đọc tương lai. Các hệ số được khóa trong `selection_manifest.json` trước khi chạy B/C; không retune sau khi xem kết quả.

## 3. Cổng tái lập Policy A

Policy A **PASS**: `8/8` deterministic rows khớp Frozen/Level-3 trong dung sai tuyệt đối `1e-9`, tương đối `1e-12`; `10/10` Monte Carlo rows khớp exact serialized checkpoint row. B/C chỉ được chạy sau cổng này.

## 4. Kết quả tổng hợp

| Policy | Deterministic depth-2 giữ depth≥2 | Controls depth≥2 | 10 MC audit paths depth≥2 | Mean liquidated debt trên selected cases (USDC) | Mean modeled bad debt trên selected cases (USD) |
|---|---:|---:|---:|---:|---:|
| A_ADVERSE_PASS_THROUGH | 4/4 | 0/4 | 10/10 | 21890.676883 | 30997.488314 |
| B_REFERENCE_ONLY | 0/4 | 0/4 | 0/10 | 18636.514986 | 28722.852843 |
| C_WEAK_LAGGED_SMOOTHED_PROXY | 0/4 | 0/4 | 0/10 | 18636.514986 | 29148.937657 |
| C_MODERATE_LAGGED_SMOOTHED_PROXY | 0/4 | 0/4 | 2/10 | 18911.630536 | 29692.772493 |

Mười MC paths là mẫu mục tiêu đã chọn vì từng có depth≥2 dưới A; tỷ lệ trong bảng **không phải** ước lượng xác suất khủng hoảng hoặc tần suất quần thể.

Trong bốn deterministic cases đã khóa, A cho depth `[2,2,2,2]`; B, C weak và C moderate đều cho `[1,1,1,1]`. Trong mười MC audit paths, A giữ `10/10`, B giữ `0/10`, C weak giữ `0/10`, C moderate giữ `2/10` (`MC_PATH_1060`, `MC_PATH_8005`).

## 5. Bốn deterministic depth-2 cases

`modeled bad debt` là ước lượng nợ không được bảo đảm đủ theo mô hình, không tự động là lỗ tài chính đã thực hiện. Impact/spread là tỷ lệ phần trăm.

| Case | Policy | Depth | Newly eligible sau Wave 1 | Liquidated debt (USDC) | Modeled bad debt (USD) | Max immediate impact (%) | Max residual spread (%) | Post-Wave-1 valuation (USD/WETH) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| DET_D2_M40_H90 | A_ADVERSE_PASS_THROUGH | 2 | 2 | 38434.773 | 38947.963 | 5.3991 | 2.6995 | 1582.303 |
| DET_D2_M40_H90 | B_REFERENCE_ONLY | 1 | 0 | 23078.591 | 36562.410 | 4.5299 | 2.2649 | 1618.972 |
| DET_D2_M40_H90 | C_WEAK_LAGGED_SMOOTHED_PROXY | 1 | 0 | 23078.591 | 37062.789 | 4.5299 | 2.2649 | 1614.388 |
| DET_D2_M40_H90 | C_MODERATE_LAGGED_SMOOTHED_PROXY | 1 | 0 | 23078.591 | 37563.169 | 4.5299 | 2.2649 | 1609.805 |
| DET_D2_M40_H95 | A_ADVERSE_PASS_THROUGH | 2 | 3 | 33482.694 | 41282.424 | 10.6825 | 5.3412 | 1560.182 |
| DET_D2_M40_H95 | B_REFERENCE_ONLY | 1 | 0 | 18126.511 | 36562.410 | 7.2626 | 3.6313 | 1618.972 |
| DET_D2_M40_H95 | C_WEAK_LAGGED_SMOOTHED_PROXY | 1 | 0 | 18126.511 | 37364.650 | 7.2626 | 3.6313 | 1611.623 |
| DET_D2_M40_H95 | C_MODERATE_LAGGED_SMOOTHED_PROXY | 1 | 0 | 18126.511 | 38166.891 | 7.2626 | 3.6313 | 1604.275 |
| DET_D2_M50_H90 | A_ADVERSE_PASS_THROUGH | 2 | 4 | 19677.585 | 88577.495 | 7.3057 | 3.6529 | 1299.861 |
| DET_D2_M50_H90 | B_REFERENCE_ONLY | 1 | 0 | 18126.511 | 81020.861 | 7.3057 | 3.6529 | 1349.143 |
| DET_D2_M50_H90 | C_WEAK_LAGGED_SMOOTHED_PROXY | 1 | 0 | 18126.511 | 82587.907 | 7.3057 | 3.6529 | 1342.983 |
| DET_D2_M50_H90 | C_MODERATE_LAGGED_SMOOTHED_PROXY | 1 | 0 | 18126.511 | 84154.953 | 7.3057 | 3.6529 | 1336.823 |
| DET_D2_M50_H95 | A_ADVERSE_PASS_THROUGH | 2 | 4 | 9014.267 | 88224.065 | 5.9750 | 2.9875 | 1308.838 |
| DET_D2_M50_H95 | B_REFERENCE_ONLY | 1 | 0 | 7463.193 | 80114.536 | 5.9750 | 2.9875 | 1349.143 |
| DET_D2_M50_H95 | C_WEAK_LAGGED_SMOOTHED_PROXY | 1 | 0 | 7463.193 | 81467.224 | 5.9750 | 2.9875 | 1344.105 |
| DET_D2_M50_H95 | C_MODERATE_LAGGED_SMOOTHED_PROXY | 1 | 0 | 7463.193 | 82819.913 | 5.9750 | 2.9875 | 1339.067 |

## 6. Tác động trực tiếp và gián tiếp

Direct shock HF giống nhau giữa bốn policy vì cú sốc reference ban đầu không đổi. DEX state ngay sau Wave 1 cũng giống A cho toàn bộ `72/72` policy-case rows; đây là invariant bắt buộc. Khác biệt HF/eligibility trên DEX state chung đó là **tác động trực tiếp của policy định giá**.

Sau khi eligibility khác nhau, giao dịch Wave 2 khác nhau và từ đó final DEX state, total liquidated debt, immediate impact cực đại và residual spread cực đại có thể khác. Đây là **tác động gián tiếp qua liquidation trades**, không phải thay đổi Uniswap math.

HF của borrower đã hết nợ là vô hạn về toán học; artifact lưu `null` cùng status `DEBT_FREE_UNDEFINED`, không ghi giá trị không hữu hạn. Borrower identifiers tiếp tục là `borrower_hash` đã redacted, không có địa chỉ ví thô.

## 7. Diễn giải RQ1–RQ2

- **RQ1 — cần giới hạn:** bốn depth-2 deterministic outcomes là kết quả phụ thuộc mạnh vào policy truyền giá. Không được gọi chúng là ngưỡng cascade độc lập với oracle. Policy B loại Wave 2 trong bốn cases; hai proxy C đã tiền đăng ký cũng loại Wave 2 trong bốn cases, nhưng đây chỉ là sensitivity model.
- **RQ2 — cần giới hạn:** liquidity haircut vẫn điều khiển sức hấp thụ DEX và tác động giá, nhưng đường truyền từ DEX state sang borrower eligibility phụ thuộc policy định giá. Thí nghiệm không xác minh rằng Aave oracle thực tế truyền DEX spot theo A, B hay C.

Kết quả không phủ định toàn bộ cơ chế cascade mô phỏng; nó xác định rằng kết luận về depth 2 không bền với thay đổi oracle-policy hợp lý trong phạm vi test này.

## 8. Kiểm toán và invariant

- `72` policy-case results, mỗi result chạy lặp lại và khớp hash determinism.
- `32,688` borrower-policy-case rows (`18 × 4 × 454`); không nhầm với target cohort `109`.
- Không borrower bị liquidate lặp; later-wave liquidations đều không trực tiếp đủ điều kiện ở shock ban đầu và có HF trước liquidation `<1`.
- Không NaN/Infinity trong artifacts; không raw address/API key.
- Frozen v3, canonical snapshot, sáu RQ và historical artifacts không bị sửa.
- Không chạy lại 10.000 Monte Carlo, không retune, không sửa Uniswap swap math hay Aave liquidation semantics.

- Trạng thái: `PASS`.
- `.\.venv\Scripts\python.exe scripts/research/run_oracle_transmission_diagnostic.py --phase a` → **PASS** (8/8 deterministic and 10/10 audited Monte Carlo rows reproduced).
- `.\.venv\Scripts\python.exe scripts/research/run_oracle_transmission_diagnostic.py --phase bc` → **PASS** (72 policy-case results; 144 identical primary/repeat simulation executions).
- `.\.venv\Scripts\python.exe -m pytest sim/tests/test_oracle_policy.py tests/test_oracle_diagnostic_artifacts.py -q` → **PASS** (9 passed).
- `.\.venv\Scripts\python.exe -m pytest` → **PASS** (175 passed, 3 dependency deprecation warnings).
- `.\.venv\Scripts\python.exe -m ruff check .` → **PASS** (all checks passed).
- `.\.venv\Scripts\python.exe -m mypy sim` → **PASS** (no issues in 49 source files).

## 9. Giới hạn chưa thể xác minh

1. Không có contract-level hoặc historical oracle observation trong thí nghiệm này; không policy nào được chứng minh là oracle Aave/Chainlink thực tế.
2. Policy C là proxy giả định với hai cấu hình đã tiền đăng ký, không phải calibration thực nghiệm.
3. Mười MC paths là targeted audit sample, không hỗ trợ suy luận xác suất.
4. Kết quả phụ thuộc canonical block `26045352`, toàn bộ 454 verified borrowers (trong đó target cohort WETH/USDC là 109) và các giả định stress đã khóa.
5. Mean across selected cases chỉ là mô tả tập mục tiêu không đồng nhất, không phải estimator quần thể.

## 10. Tái lập

```powershell
.\.venv\Scripts\python.exe .\scripts\research\run_oracle_transmission_diagnostic.py --phase a
.\.venv\Scripts\python.exe .\scripts\research\run_oracle_transmission_diagnostic.py --phase bc
.\.venv\Scripts\python.exe .\scripts\research\build_oracle_diagnostic_bundle.py
```

Artifacts chuẩn nằm tại `data/processed/research_final/oracle_transmission_diagnostic_v1/`. Quyết định khoa học cuối cùng thuộc Commander; branch này không merge tự động.
