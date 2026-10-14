# Đối chiếu phiên bản P2 với P0 v2 và Level-3

**Ngày:** 14/10/2026. **PR:** [Draft #9](https://github.com/Doquocdung1609/DeFiStress/pull/9). **Trạng thái:** cập nhật nội dung chờ Commander duyệt lại; không phải scientific lock hoặc P1 evidence freeze.

Chỉ đạo chính: [Commander comment trên PR #9](https://github.com/Doquocdung1609/DeFiStress/pull/9#issuecomment-6152088844). Giới hạn còn mở theo [review #10](https://github.com/Doquocdung1609/DeFiStress/issues/10#issuecomment-6152110805) và [roadmap #3](https://github.com/Doquocdung1609/DeFiStress/issues/3#issuecomment-6152119839).

## 1. Phiên bản và phạm vi

| Vai trò | Định danh |
|---|---|
| Bộ P2 trước cập nhật | `f753629c10b1237a4f9f4250d75aa6ded4af4ee3` trên `research/p2-verified-literature-20261013` |
| Mã/báo cáo được P2 cũ đọc | `2b9a29f5e8c0c8dd910b7d65428fb1d57646b06b` |
| Mốc đối chiếu hiện tại | `26cd58489d726a6c98678c725650020edcc1a3f4` |
| P0 corrected artifact | `data/processed/research_final/validation_audit/corrected_run_v2/`; bundle commit `672c840a15addd1c461bf502e432c09473467194` |
| Level-3 implementation / artifact | `92ca73c2bdd4cdcdd34c693483d17a4dbef33513` / `28cf16c52c219ba2794dde7fdb22c77e147de7a0` |
| Model tại mốc mới | `0.1.0-aave-v3.10-metric-semantics` |
| Canonical input giữ nguyên | Ethereum block 26.045.352; snapshot SHA-256 `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99`; 454 borrowers xác minh, cohort WETH/USDC 109 |

Cập nhật bốn file P2 và thêm file đối chiếu này. Không sửa mã, artifact, scenario, registry, Terra hoặc Word. Mọi facts code dưới đây pin `26cd5848`, không tự áp dụng cho commit tương lai. P2 đọc artifact, đếm lại grid, tính lại Wilson và đối chiếu trace mẫu; không tuyên bố đã chạy lại RPC/fork/10k paths.

## 2. Bảng nhận định cũ sang phiên bản mới

| Hạng mục | P2 cũ hoặc diễn giải cần loại | Nhận định tại 26cd5848 | Vị trí sửa và căn cứ |
|---|---|---|---|
| Arbitrage/tick | Reposition đặt giá mà không cập nhật L | Đã duyệt tick theo hai hướng và ±liquidityNet; có regression. Vẫn price teleportation, chưa funded swap/fork | P19/C34; E01 và tests tick/round trip |
| Cascade | Blanket caution từ wave index; phần cũ giữ zero-cascade story | P0 tám Severe paths có borrower mới HF≥1→HF<1 trước wave 2. Giữ simulated endogenous wave 2, không áp cho mọi batch/index | P19/C33/P21; E03/E08 |
| RQ1 grid | Chỉ grid cơ sở −5…−40% × haircut 0/25/50/75 | Grid cơ sở chưa depth≥2; grid Level-3 60 cells có depth 0/1/2 = 18/38/4 | RQ1/P20/P21; E02 |
| Tail cells | Không có mở rộng stress tail | Bốn depth-2 cells: −40/−50% × 90/95% haircut. Haircut tail không quan sát Mainnet | E02; CSV đã đếm lại |
| Monte Carlo | Dùng ví dụ 0/200 như kết quả Severe | P0 Severe 8/200; Level-3 Severe 280/10.000, 2,8%; Wilson hai phía 2,4943–3,1419%; depth≥3=0 trong batch này | P14/P21/C23; E03/E04 |
| Wave ceiling | Dễ nhầm max_waves với realized depth | Configured 100, horizon 120; attained tối đa 2, không cap hits. Severe deterministic baseline cap sweeps dừng depth 1 | P21/E06; không “100 vòng lịch sử” |
| RQ4 impact | Narrative cũ không response / max_price_impact không phân điểm đo | Intrawave khoảng 0,108794% giữ nguyên trong Professor sweep; post-arbitrage residual giảm về xấp xỉ 0 | P19/P20/C13/RQ4; E07; alias deprecated được giải thích |
| Recovery/delay | 60→300 giây recovery dưới giả định cũ | Recovery 0 nếu chưa vượt tolerance; không bằng liquidation delay 0. First-liquidation timestamp đo riêng | P19/P20/RQ3; E07 |
| LT output | Metric nợ chưa thanh lý dùng recorded LT | Đã dùng scenario LT override; legacy field chỉ so sánh có nhãn | P19/RQ6/E07 |
| Lịch sử Ethereum | Chưa tích hợp Level-3 | Tuần Sept 1–7: 27 Graph candidates khớp RPC, 0 excluded; primary 5-minute 22 clusters | P21/E09/E10; candidate verification, không census |
| Transaction tier | Raw artifact gọi 3 ca DIRECT_TRANSACTION_LINK | P2 diễn giải 3 same-tx co-occurrences, 23 same-block, 1 time-window; cần Transfer/trace trước direct collateral flow | P19/P21/C09/E11; raw tier không bị sửa |
| Swap/control scope | Dễ hiểu 31.489 swaps là toàn tuần | Swaps được index quanh event/control windows; control 60 phút và completeness còn pending review | P21/E10/E11; không inference nhân quả |
| Checkpoint counts | actual_runs hoặc runtime được đọc như execution mới | 10k rows khác path mới chạy trong invocation; `_run_mc_stage` nhánh restore chưa ghi reused đúng. Unique 13k được báo cáo nhưng còn audit dedup/metadata | P13/P19/E04–E06; pending targeted #10 |
| RQ5 | Có nguy cơ gán caveat cũ không kiểm version | Kiểm lại code26: seize/dust/quote unit caveat vẫn còn, chỉ debt valuation sensitivity | P19/C35/glossary; không full depeg |
| Tác nhân/network/tail | Có nguy cơ đổi tên abstraction thành mô hình đầy đủ | Một liquidator/arbitrageur; typed graph gộp; composite exposure tail statistic, không realized loss/market ES | P11/P19/C19/C24; glossary giữ scope |
| NIST/APA | Tên trang Agresti Coull có thể gây lẫn phương pháp | Note của S24 phân biệt Wilson và adjusted Wald; giữ tên Wilson. S17/S18 là một nghiên cứu hai phiên bản | P14/APA note/S24 ledger; không thêm nguồn |

## 3. Bảo toàn và mức xác nhận

Sáu RQ giữ nguyên văn; 30 source records S01–S30, ngày truy cập 13/10, DOI/URL, phạm vi abstract/fulltext/preview và hàng chờ U01–U08 giữ nguyên. Không thêm nguồn học thuật. Ma trận giữ 35 claim IDs; bổ sung 12 alias E cho **bằng chứng dự án có provenance**, không thay result IDs P1. Glossary giữ 92 mục, thêm chú giải trường metric/evidence tier.

P0 scoped PASS không bị phủ định. Level-3 được Commander chấp nhận có điều kiện: discovery census/control, direct token linkage và checkpoint provenance còn cần sửa #10. Không gọi artifact `quality_gate=PASS` là Commander scientific lock. Fork execution vẫn UNAVAILABLE, 0 transaction; Quoter initial state không xác nhận toàn counterfactual path.

Giữ nguyên các kết quả Terra riêng và ranh giới historical reconstruction/forecast. Lịch sử Aave–Uniswap chỉ event association hiện tại; mô phỏng mới đủ cơ sở gọi wave 2 nội sinh trong các path có HF audit. Tần suất 2,8% là conditional model frequency, không xác suất thị trường hay 280 cascade Ethereum thật.

## 4. Kiểm tra và review

**Review ngày 14/10/2026:** tác tử độc lập `p2_independent_review` cho `PASS_P2_VERSION_RECONCILIATION`, không lỗi trọng yếu chặn bàn giao. Đã đọc đủ năm file, so với baseline và mã/artifact tại 26cd5848: 30 S records, giới hạn truy cập/U queue, 35 claim IDs và sáu RQ giữ nguyên; cập nhật tick/impact/recovery/LT đúng; giữ simulated wave 2 qua HF audit; không nâng lịch sử co-occurrence thành dòng thế chấp hay causal contagion; checkpoint/P1 pending vẫn công bố.

Reviewer đếm lại 60-cell grid, kiểm eight-path HF audit P0 và tính lại Wilson; không chạy RPC/fork/Monte Carlo, không bổ sung literature và không sửa mã. Sign-off chỉ xác nhận tính nhất quán của bộ tài liệu P2 phiên bản mới, không phê duyệt kết quả khoa học, P0/P1 hoặc quyết định Commander.

Kiểm tra soạn thảo cũng xác nhận bất biến nguyên văn RQ, source records/DOI/URL/ledger/U queue, 35 claims, 12 evidence aliases và 92 mục glossary. Căn cứ số liệu/code pin 26cd5848; bản cũ chỉ tồn tại trong cột lịch sử. Không sử dụng lỗi L/recovery/LT đã sửa như lỗi hiện hành.

**Yêu cầu bàn giao:** Commander duyệt lại PR #9 theo sáu repair items đã chỉ đạo. Issue #4 giữ open, PR giữ draft; P1 numerical freeze và targeted #10 còn gate riêng. Không merge hoặc tạo Word final.
