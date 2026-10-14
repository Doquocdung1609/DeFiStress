# Đối chiếu phiên bản P2 với P0 v2 và Level-3

**Ngày:** 14/10/2026. **PR:** [Draft #9](https://github.com/Doquocdung1609/DeFiStress/pull/9). **Trạng thái:** cập nhật delta cuối chờ Commander duyệt lại; không phải scientific lock hoặc quyết định merge.

Chỉ đạo áp dụng: [Commander follow-up ngày 14/10/2026](https://github.com/Doquocdung1609/DeFiStress/pull/9#issuecomment-6161682917). Nền học thuật 30 nguồn, 35 luận điểm, sáu RQ, 92 thuật ngữ và tám nguồn hàng chờ đã được chấp nhận có giới hạn; lần này chỉ cập nhật claim mã/thực nghiệm theo HEAD.

## 1. Phiên bản và phạm vi

| Vai trò | Định danh |
|---|---|
| Bộ P2 trước delta cuối | `9367674f84c47c388dceaea124bff2511b0a5c89` |
| Mốc Level-3 P2 đã đọc trước đó | `26cd58489d726a6c98678c725650020edcc1a3f4` |
| HEAD được đối chiếu lần này | `ba62c74950a72751e0030527836082da0c7622ef` |
| P0 corrected artifact | `data/processed/research_final/validation_audit/corrected_run_v2/`; bundle `672c840a15addd1c461bf502e432c09473467194` |
| Level-3 gốc | `data/processed/research_final/level3_extension/` |
| Gói sửa P1 có mục tiêu | `data/processed/research_final/level3_p1_targeted_repair/`; implementation `2dbc7d55`; artifact `6fcda469` |
| Model/canonical input | `0.1.0-aave-v3.10-metric-semantics`; block 26.045.352; snapshot SHA-256 `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99` |

Chỉ sửa năm tài liệu P2. Không sửa mã, dữ liệu, kịch bản, registry, Terra hay Word. P2 đọc artifact và kiểm tra nội dung; không tái thực thi RPC, fork hoặc batch Monte Carlo lớn.

## 2. Đối chiếu thay đổi 9367674 → HEAD ba62c749

| Hạng mục | Trước delta cuối | Nhận định hiện hành | Căn cứ/giới hạn |
|---|---|---|---|
| Census Aave | 27 Graph candidates khớp RPC; census còn pending | Census Pool trong tuần định nghĩa có 28 sự kiện; 27 Graph candidates đều RPC-match; Graph bỏ sót một sự kiện WETH/USDT ở block 25888740 | FIX `historical/census_reconciliation.json`; recall quan sát 27/28, không phải census borrower |
| Receipt route | Ba same-tx đều hạ thành co-occurrence | 1 `DIRECT_TRANSFER_PATH_VERIFIED`, 2 `SAME_TRANSACTION_CO_OCCURRENCE`, 23 cùng block, 1 theo thời gian | Exact WETH amount/order từ receipt; trace `UNAVAILABLE`; không chứng minh price causality |
| Control windows | Completeness/liquidation-free còn pending | 4 pool, 5 episode, half-width 1/5/15/30 phút, 40 tổ hợp, 928 chunks; 5/5 control ±30 phút không liquidation | FIX `historical/control_window_audit.json`; 31.489 swap chỉ thuộc selected windows |
| Checkpoint | 13k unique mới là reported accounting; repair pending | 13.000 định danh batch độc lập, 0 trùng; prefix 200/1k/5k lồng trong 10k; 10k reused, 0 large path chạy lại; 21/21 mẫu khớp | FIX checkpoint/reproduction; legacy duration `UNAVAILABLE_NOT_EMBEDDED_IN_LEGACY_CHECKPOINT`; external attestation được công bố |
| Vòng 2 tất định | Chủ yếu dùng audit 8/200 và một path mẫu | Ca −40%/haircut 90% có HF trực tiếp 1,0211716 và HF sau vòng 1 là 0,9980426 | FIX `wave2_eligibility_audit.json`; simulated eligibility |
| Vòng 2 phân tầng MC | Stratified audit còn pending | 10/10 first-depth2 samples theo 10 stratum có borrower mới mất an toàn | Direct-shock HF 1,00087518–1,00442738; prior-wave HF 0,99581457–0,99940096 |
| Tần suất/độ sâu | Severe 280/10.000 depth≥2; không depth≥3; 4/60 tail cells | Giữ nguyên; cap 100 chỉ là giới hạn cấu hình, max quan sát 2 | Tần suất có điều kiện; haircut 90/95% chưa quan sát |
| Uniswap V3 | Lỗi tick cũ đã được loại khỏi mô tả | Vẫn xác nhận cập nhật ±`liquidityNet`; giới hạn là price reset chưa phải funded swap có vốn/phí/đường thực thi | Không hồi sinh lỗi cũ |
| USDC/Terra/network | Các giới hạn đã công bố | Giữ nguyên kênh định giá nợ USDC; Terra là tái dựng/kiểm cơ chế/cảnh báo hồi cứu; graph là mạng dị thể gộp | Không full-depeg Aave, không OOS success, không formal multilayer contagion |
| NIST/APA | Wilson và adjusted Wald đã phân biệt; S17/S18 dedup | Giữ nguyên toàn bộ 30 nguồn, DOI/URL và access tag | Không thêm nguồn chưa xác minh |

## 3. Bảo toàn hồ sơ học thuật

- Sáu RQ giữ nguyên văn và nguyên phạm vi.
- 30 source records S01–S30, ngày truy cập, DOI/URL và mức truy cập giữ nguyên.
- U01–U08 vẫn mang nhãn `SOURCE_NOT_VERIFIED` tương ứng; không dùng cho claim chi tiết.
- Ma trận giữ 35 claim IDs và 12 alias E; alias E được cập nhật locator sang gói FIX khi cần.
- Danh mục giữ 92 thuật ngữ; chỉ sửa chú giải tier/checkpoint.
- S17 JFE và S18 NBER vẫn được tính là một nghiên cứu; S24 vẫn dùng đúng Wilson score interval theo phần Note của trang NIST.

## 4. Ranh giới khoa học còn phải đưa vào báo cáo

1. Một receipt-level WETH route xác minh dòng token trong giao dịch, chưa chứng minh thanh lý gây biến động giá hay tạo cascade lịch sử.
2. Census chỉ có ý nghĩa cho Pool address/topic và cửa sổ tuần đã định nghĩa; 27/28 là recall quan sát của Graph trong census này.
3. Severe 280/10.000 và 4/60 ô tail là kết quả có điều kiện của mô hình; haircut 90/95% là phản thực chưa quan sát.
4. External attestation được dùng cho checkpoint legacy; thời lượng chạy 10k lịch sử không có trong file cũ.
5. Arbitrage vẫn là thiết lập lại giá theo quy tắc, chưa phải chuỗi giao dịch có vốn, phí và route đầy đủ.
6. Aave depeg chỉ kiểm kênh định giá nợ USDC; unit conversion/redemption/liquidity chưa đầy đủ.
7. Một liquidator và một arbitrageur đại diện không mô tả cạnh tranh nhiều bot; composite exposure tail không phải realized loss hay market ES.
8. Đồ thị dị thể gộp và centrality không tự chứng minh mạng nhiều lớp hình thức hoặc lây lan nhân quả.
9. Terra chỉ hỗ trợ kiểm tra cơ chế, tái dựng lịch sử và đánh giá cảnh báo hồi cứu; không phải dự báo ngoài mẫu thành công.
10. Mainnet fork transaction vẫn `UNAVAILABLE`.

## 5. Phản biện độc lập

**Kết quả:** `PASS_P2_FINAL_VERSION_DELTA`, không còn lỗi chặn bàn giao. Tác tử `p2_independent_review` đã đọc đủ năm file, chỉ đạo Commander và sáu artifact kiểm toán tại HEAD `ba62c749`. Review xác nhận các số census/tier/control/checkpoint/HF; đồng thời kiểm 30 nguồn, U01–U08 và nhãn truy cập, sáu RQ byte-identical, 35 claim IDs và 92 thuật ngữ. Một câu cũ phủ nhận toàn bộ collateral flow đã được sửa: tài liệu nay ghi đúng một tuyến WETH theo biên nhận giao dịch, đồng thời giữ giới hạn chưa xác lập tác động giá nhân quả hoặc lây lan lịch sử. Sign-off chỉ duyệt tính nhất quán tài liệu P2; không thay Commander scientific approval, không xác nhận mã toàn diện và không cho phép merge.

## 6. Bàn giao

Bộ P2 đã hoàn tất phản biện độc lập và sẵn sàng cho Commander re-review ở trạng thái draft. Issue #4 giữ open; không merge, không tuyên bố scientific lock và không tạo Word final.

## 7. Tiếp quản Scientific Claim & Evidence Reconciliation

Starting P2 HEAD `8f5b635a316d72546b8a0eb0c2e8a66503b5d44f`; không có commit oracle reconciliation mới khi preflight. Integration branch được truy hồi trực tiếp tại `9842c4f2c35adb8b4ec906e1bc76afa825d197c7`. PR #11 `3011ba5e8cd23ee697c36d0aec6d047d8d58f653` và #12 `a5d3d73dc037ec4c3a90449b3ccce37331b10597` vẫn Draft/Open chưa merge. Không làm lại tổng quan hoặc sửa bundle của Codex.

Kết quả thanh lý vòng hai được xác nhận trong các kịch bản stress phản thực với chính sách truyền giá bất lợi. Sự xuất hiện và mức độ thanh lý phụ thuộc vào chính sách định giá vị thế, giới hạn mẫu borrower và cấu hình thanh khoản.

Thanh khoản DEX ảnh hưởng đến hấp thụ forced sale và biến động giá; tuy nhiên tác động này chỉ chuyển thành eligibility mới qua cơ chế định giá được mô hình hóa, không phải một mối liên hệ nhân quả Mainnet đã được chứng minh.

Các claim sửa: C03, C07, C11, C13, C22, C23, C32, C33. 35/35 claim IDs và 12/12 aliases có đối chiếu; source/APA/RQ/term invariants được giữ. Delta cũ trong §2 và PASS reviewer §5 chỉ là lịch sử; review phiên này là ba lượt tự rà soát riêng và gates bằng công cụ, không reviewer độc lập mới.

Biên bản [P2_ORACLE_RECONCILIATION.md](P2_ORACLE_RECONCILIATION.md) và JSON crosswalk ghi source commits, result selectors, superseded interpretation, nguồn chưa xác minh và kiểm tra thực tế. Hai raw CSV chưa đọc đủ, nên không tuyên bố full 32688-HF independent review. 72 summaries và 2186 event rows có thể kiểm trực tiếp; state-resolved skip reason nay được Work kiểm độc lập bằng snapshot+event state; raw CSV cell comparisons vẫn chưa thực hiện.

Đề nghị Commander nghiệm thu P2 với giới hạn đọc đã công bố; Issue #4 giữ open, PR #9 Draft; không merge và không tự cấp Scientific Content Lock.

**Tool verification bổ sung:** Work tính tĩnh32.688 cặp HF (65.376 giá trị) từ canonical snapshot+Wave1 events, khớp72/72 summary rows và52/52 event HF, xác nhận36/36 route skips NO_MODELLED_USDC_DEBT; không chạy lại mô phỏng. Hai raw CSV vẫn chưa đọc đủ/cell-by-cell compare. Snapshot hash Git LF76dae833… khác accepted CRLF553e93a3… do serialization; biên bản và JSON ghi cả hai phạm vi, không sửa nguồn.

## Final Cross-PR Reconciliation — 14/10/2026

P2 starting commit `f523f7369011b5ed5b8bd881785bc44f40d1c9bd`; **P2 final commit được ghi đúng SHA trong GitHub handoff PR #9/Issue #4 sau push**, tránh self-reference trong chính commit. PR #11 `3011ba5e8cd23ee697c36d0aec6d047d8d58f653`; PR #12 current `a5d3d73dc037ec4c3a90449b3ccce37331b10597`, cả hai Draft/Open chưa merge. Valid integration source/artifact object: `c113fc1ec6dd98ffcc31241c1dbd1a93b20aa193` — đã kiểm trực tiếp Git object; pointer c113fc190ed9… trước đây không tồn tại và đã loại khỏi active locators.

**35/35 claim và12/12 alias đã đối chiếu phiên bản mới**, đặc biệt C03/C07/C11/C13/C22/C23/C32/C33. [INT_T01_ELIGIBLE_VS_EXECUTED registry](https://github.com/Doquocdung1609/DeFiStress/blob/a5d3d73dc037ec4c3a90449b3ccce37331b10597/data/processed/research_final/scientific_integration_v1/table_figure_registry.json) trỏ đúng summary CSV và detail CSV, với18 selected cases ×4 policies ×454 verified borrowers;109 là cohort WETH/USDC riêng. Units là instances vàUSDC token quantity; portfolio-HF eligibility khác route eligibility/execution. Các số35/14,6/0,11/2 và36 skipped giữ nguyên, route-ineligible là không có modeled USDC debt.

Superseded: nonexistent expanded source pointer c113fc190ed9…→`c113fc1ec6dd98ffcc31241c1dbd1a93b20aa193`; PR12 read HEAD b1786c0…→`a5d3d73dc037ec4c3a90449b3ccce37331b10597`; missing INT_T01 registration→registry mới; integration manifest/result/validation hash metadata cũ→digest tạiHEAD mới. Frozen/Oracle/numerical outcomes không thay.

**Actual verification scope:** `WORK_INDEPENDENT_STATIC_RECONSTRUCTION` là phép tính tĩnh của Work ởP2 `f523f7369011b5ed5b8bd881785bc44f40d1c9bd` (32688 cặpHF,72 summary rows,52 available eventHF,36 route skips); lần sửa này giữ kết quả đó và kiểm immutable blob/summary consistency, không chạy lạiengine. `CODEX_REPLAY_VERIFICATION` là72 replay/hash và32688 HF comparison do Codex báo cáo. `CODEX_PREMERGE_AUDIT` là [báo cáo parser độc lập của Codex](https://github.com/Doquocdung1609/DeFiStress/blob/a5d3d73dc037ec4c3a90449b3ccce37331b10597/docs/research_final/SCIENTIFIC_PREMERGE_AUDIT_v1.md) ởaudit source a393377… (report đọc tạiPR12 currentHEAD), không phải Work đã đọc lạifull rawCSV. Codex19pytest/Ruff/mypy là kết quả Codex báo cáo, không phải test Work.

**Hash provenance:** Windows CRLF checkout hashes và Git LF blob hashes định danh hai file-byte representations khác nhau; normalization chỉ chứng minh nội dung tương ứng, không biến hai digest khác nhau thành cùng mộtSHA. Canonical GitLF76dae833… khác WindowsCRLF553e93a3…; premerge audit ghi cảFrozen/Oracle/Integration domains và exact sourceHEAD.

Remaining limitations: hai largeCSV vẫn `SOURCE_NOT_VERIFIED_IN_THIS_SESSION`, chưa cell-by-cell read/comparison bởi Work; actual oracle/fork/representative agents/extreme haircut/debt valuation/network/Terra negative limits giữ nguyên. Không numerical/scientific conflict mới được phát hiện trong phạm vi đọc. Không sửa mã/bundleCodex, không merge/Word final/Scientific Content Lock. Proposed **P2_FINAL_RECONCILED_READY_FOR_COMMANDER_REVIEW** với các read limitations được giữ.

**Targeted command/result:** `python verify_p2_crosspr.py` → PASS_WITH_PRESERVED_READ_LIMITATIONS, 21 grouped checks; 35 claim/12 alias coverage, 96 locator instances (94 read-content/current-blob matches, 2 preserved unread largeCSV locators). Không cộng vào hoặc chạy lại730 checks của phiên trước; Codex19pytest là reported premerge result.
