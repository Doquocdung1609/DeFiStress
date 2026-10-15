# Scientific Content Lock Review Packet

**Commander decision requested:** review delta after `REGISTRY_TARGETED_REPAIR_COMPLETE`.

- Starting integration HEAD: `6560f799f81223cd4a720bd3f6b798aeef1732b9`.
- Registry records: 35 scholarly + 13 integration = 48.
- Six RQs: 6/6; full original wording is parsed from the locked P2 matrix, with short labels stored separately.
- AR-01 primary evidence classifications: 8/8 verified.
- AR-02 slash-RQ mappings: 16/16 verified.
- AR-04 disallowed IDs in affirmative RQ sets: 0.
- Active locator gate: 109/109 resolved.
- Declared locator hashes: 216/216 matched.
- Result IDs: 78/78 resolved.
- Table/figure IDs: 20/20 resolved.
- Validation: PASS; failed gates: [].
- Tests: PASS; Final relevant suite: 35 passed; Ruff passed; mypy passed. The validator is separately implemented but run by the same executor, not an external independent reviewer.
- Proposed lock status: `READY_FOR_COMMANDER_DECISION_WITH_LIMITATIONS`; not a lock grant.
- RQ3 repair: 36 borrower-case-policy instances were skipped because no modeled USDC debt belonged to the WETH/USDC liquidation route; this does not imply debt was repaid in Wave 1 or that gas/capital/profitability caused the skips.

## AR-01 → AR-05 status

| Finding | Status | Evidence |
|---|---|---|
| AR-01 | PASS | 8/8 primary evidence tiers verified; scholarly background separated. |
| AR-02 | PASS | 16/16 slash-RQ mappings and 6/6 full source questions verified. |
| AR-03 | PASS | Six required accepted wordings and route-specific RQ3 conclusion verified. |
| AR-04 | PASS | Zero disallowed/superseded IDs in affirmative RQ sets. |
| AR-05 | PASS | Targeted manuscript-facing terminology polished without numerical changes. |

## Accepted wording delta

- `C07`: Thanh khoản Uniswap V3 phụ thuộc các khoảng tick. Trong mô phỏng, suy giảm độ sâu làm thay đổi khả năng hấp thụ bán thế chấp và tác động giá; eligibility mới còn phụ thuộc chính sách định giá.
- `C11`: S13 không tìm thấy tác động giá kéo dài có ý nghĩa thống kê trong thiết kế đã xét; DeFiStress mô phỏng thanh lý vòng hai ở những trường hợp stress được chọn dưới Policy A. Hai kết quả có phạm vi và chuẩn đối chiếu khác nhau.
- `C19`: Nhánh Aave của DeFiStress sử dụng một tác nhân thanh lý và một tác nhân kinh doanh chênh lệch giá đại diện.
- `C23`: Trong cấu hình baseline Policy A, Severe ghi nhận 8/200 đường mô phỏng ở P0 v2 và 280/10.000 đường ở Level-3 có độ sâu thanh lý từ hai vòng trở lên; Low Liquidity ghi nhận 0/1.000. Khoảng Wilson mô tả bất định lấy mẫu có điều kiện trong từng cấu hình.
- `C32`: Policy A của mô hình lấy giá trị nhỏ hơn giữa giá tham chiếu và giá DEX; Policy B chỉ dùng giá tham chiếu; các Policy C là giả định truyền giá có độ trễ và làm trơn. Các chính sách này chưa được xác minh là cơ chế oracle thực tế của Aave hoặc Chainlink.
- `C33`: Kiểm toán HF trong mô hình theo Policy A ghi nhận các vị thế mới mất an toàn sau Wave 1; việc mới đủ điều kiện theo HF được đối chiếu riêng với các lần thanh lý vòng hai có hoàn trả nợ dương.

## Material unsupported/superseded claims

- `CL_FROZEN_RQ1_UNQUALIFIED_WORDING`: superseded; Policy A qualifier required.
- `CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING`: superseded; DEX absorption and oracle-mediated HF feedback must be separate.
- `CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT`: unsupported external inference.
- `CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION`: unsupported causal inference.

No engine, simulation mathematics, snapshot, cohort, locked evidence, literature bibliography or prior registry was modified. No 10,000-path rerun was performed.
