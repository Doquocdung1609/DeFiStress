# Gate A và Gate B — giao thức khoa học đề xuất

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED**

Issue [#33](https://github.com/Doquocdung1609/DeFiStress/issues/33) chỉ cấp quyền thiết kế/đánh giá. Nguồn đầu vào cố định: `cbcf8c451c9f2c83a2f07ae483ba6c3a25ecd815`. Tài liệu này đề xuất tiêu chí cho quyết định tương lai; không sửa điều kiện Gate A, không cấp quyền Phase 02. [Ma trận bằng chứng](EVIDENCE_SCOPE_MATRIX.json) chứa 12 record quản trị `GBE-*`, source catalog với commit, Git blob SHA-1, SHA-256 và permalink. Các ID này không phải scientific result IDs mới.

## Hai câu hỏi khác nhau

| Cổng | Câu hỏi và điều kiện PASS | Trạng thái hiện tại | Không suy ra từ PASS |
|---|---|---|---|
| Gate A — independent archival validation | Historical reads cùng chain/block/contract/method có bằng chứng định danh backend phục vụ actual requests của cả hai bên và bằng chứng tách biệt có thể kiểm tra; mismatch có disposition theo tiêu chí đã đăng ký | `INDEPENDENT_ARCHIVE_VALIDATION_BLOCKED`: request-serving identities chưa được attest, separation chưa xác minh | Independence của mọi provider/thời kỳ; execution accuracy hoặc causal validity |
| Gate B — registered core agreement | Phép so sánh chính xác trên core scope đã đăng ký, identity/units/method phù hợp, hai lượt đọc ổn định, đầy đủ trường và provenance | `PASS_REGISTERED_CORE_SCOPE`: Alchemy so với saved dRPC, 3 blocks × 29 labels × 2 passes = 174 field-pass agreements; 87 block-field pairs; 0 mismatch/missing/additional | Hai failure domains độc lập; full tick/borrower/round cross-validation; quyền Phase 02 |

Quyết định [Commander PR30](https://github.com/Doquocdung1609/DeFiStress/pull/30#issuecomment-6263482238) có ưu tiên hơn câu “Draft” trong review lịch sử. PR29/30/32 đã merge. Gate B không đổi tên hoặc thay thế Gate A. `CASE2 PLAUSIBLE_BUT_UNPROVEN` là phân loại thiếu bằng chứng, không phải ước lượng xác suất hai backend độc lập.

## Phạm vi được nghiệm thu và phần còn thiếu

| Thành phần | Bằng chứng hiện hữu | Giới hạn / yêu cầu bổ sung |
|---|---|---|
| Registered core, GBE-01–04 | Chain1, 26045352/26038152/26030952, hai pool USDC/WETH, fee3000/500 millionths; 4 identity labels + 25 state/config labels; `slot0()` tuple là một label | Không bao gồm toàn bộ bitmap/ticks, borrower vectors hoặc aggregator rounds trong Alchemy comparison |
| Tick bands, GBE-05 | 6 pool-block cases, 24 bitmap-word instances/pass, 4169 initialized-tick instances; không missing required band | Mỗi band current tick ±6932, làm tròn vào trong theo spacing; outside-band chưa thu thập. Lower boundary L là suy dẫn từ observed active L; không phải independent boundary proof |
| Oracle, GBE-06–07 | 6 USDC/WETH asset-block traces tại dRPC; actual Aave configuration và effective price; adapter upstream rounds khi interface hỗ trợ | Không có freshness threshold đã đăng ký; tuổi round USDC 55128/54504/49212 giây được giữ nguyên. Core agreement không cross-check toàn bộ round trace |
| Borrower, GBE-08 | 24 borrower-block cases, 24 distinct addresses, 67 reserves/account; HF/base differences được báo cáo bằng 0, hai decoded passes khớp | First8 theo SHA256 ranking từ complete1024-block Borrow window/block; một zero-debt account được giữ. Đây không phải census hoặc execution validation; chưa cross-provider full portfolio |
| Provenance, GBE-09–10 | dRPC raw/decoded artifacts giữ trong Git; Alchemy original summary artifact tải lại và kiểm digest/CRC trong phiên này | Alchemy không lưu full field values/raw transport: summary không đủ tự tái tính offline174 comparisons. Actions artifact có thể hết retention; durable index vẫn giữ scope/hashes |
| Independence, GBE-11 | Dossier ghi rõ gateway/routing và absence of request attribution | Khác brand, URL, TLS, clientVersion hoặc digest không đóng Gate A. Chưa chứng minh cùng backend, cũng chưa chứng minh tách backend |
| Execution/inference, GBE-12 | Chỉ ingestion/reconstruction và integrity đã nghiệm thu | Chưa có receipts, funded execution, V2 stress, dynamic causal validation hoặc sealed OOS prediction |

## Ngưỡng chấp nhận và xử lý dữ liệu cho lần mở rộng tương lai

Các quy tắc dưới đây là **protocol proposal**, không tuyên bố đã chạy kiểm thử mới. Những controls đã có được ghi riêng; không thêm điều kiện hồi tố để đổi trạng thái Gate B đã nghiệm thu.

| Control | Expected / ngưỡng và disposition | Bằng chứng / gap hiện tại |
|---|---|---|
| Identity và ABI | 0 sai chain ID, block number/hash/time, contract, token ordering, selector, ABI output type hoặc decimals. Bất kỳ sai identity nào: `FAIL_IDENTITY`, quarantine case và dừng publication của pack | Registration + collector + saved requests có; không chạy lại RPC |
| Exact historical reads | `eth_call` dùng registered blockHash và `requireCanonical`; logs dùng exact registered block hoặc cửa sổ đã đăng ký đầy đủ. Không `latest` fallback. Reorg/hash change: block lại toàn case đến khi có registration revision được duyệt | Source guards và journals hiện hữu; checksum không thay canonical-chain attestation độc lập |
| Core equality | 29/29 labels/pass đúng với reference; 0 mismatch, 0 missing, 0 extra. So sánh integer/address/tuple theo spec, không tolerance số thực. Tuple→JSON list là lossless representation normalization; không rounding để tăng agreement | Origin CI báo174/174; phiên này chỉ đọc kết quả, không tính lại |
| Repeatability | Hai decoded core content hashes của từng block phải bằng nhau và cả hai complete. Hai lần cùng thiếu là `BLOCKED_MISSING`, không PASS | 3/3 blocks có hai hashes khớp trong origin artifact |
| Hash domain | Công bố serialization/version, input projection và bytes. Alchemy `run.py:canonical_hash`: sorted compact JSON, `default=str`, mặc định ensure_ascii, UTF-8, **không LF cuối**; tuple normalized trước hashing. SHA actual JSON bytes khác canonical field hash | Phase01-A/B `pilot.py:canonical` dùng ensure_ascii=False, compact sorted JSON **cộng LF**. Gzip, decoded JSON, ZIP, Git blob, Windows CRLF checkout và Git LF có digest riêng; không gọi chúng là cùng SHA |
| Reference provenance | Pin reference commit/blob/SHA256, provider label, contract/method/ABI, recorded collection run/time; hash trước khi dùng. Reference checksum mismatch: `FAIL_INTEGRITY`, dừng pack. Thiếu provenance cần thiết: `BLOCKED_REFERENCE` | `evidence/full/core/drpc-{block}-pass1.json.gz`, source6e5285f…/run39212923329; origin Alchemy sourcef63cee…/run39223539524. Per-request backend vẫn thiếu |
| Provider-time asymmetry | Ghi rõ saved-reference vs new-read; tách block timestamp khỏi retrieval timestamp. Cùng immutable block hash cho phép historical state comparison; không tuyên bố đọc hai provider đồng thời | dRPC trước, Alchemy sau. Không suy routing của lần đọc cũ từ bounded collection mới hoặc từ routing label khác |
| No leakage | Mọi state dependency cùng block; oracle/reserve timestamps không vượt block time. Đối với forward test: available-at không vượt decision time và holdout không tham gia tuning. 1 vi phạm chưa giải thích: `FAIL_LEAKAGE`, quarantine ảnh hưởng | Historical guards có; không có OOS forecasting experiment V2 trong pack |
| Tick/portfolio completeness | 0 missing required word/tick, 0 duplicate, gross≥abs(net), anchored L≥0; không vượt band. Portfolio thiếu active dependency hoặc incomplete discovery window: `BLOCKED_DEPENDENCY`, không zero-fill | Registered-band và sample component PASS theo reports. Core Gate B không tự mở rộng sang các vectors này |
| Borrower numeric semantics | Giữ tolerance Phase01B đã đăng ký: HF≤10^10 raw WAD, base totals≤max(1, participating reserves) raw base units; saved verifier hiện hành đòi quan sát exact0. Không nới saved verifier; future change phải đăng ký trước và trình Commander | Observed differences0. UINT256_MAX khi debt0 không phải finite HF. Aave base10^8, token quantities theo decimals, HF10^18 tách riêng |
| Oracle fidelity/freshness | Actual source/config/round/effective value tách khỏi DEX observation và counterfactual policies. Timestamp hợp lệ chưa đủ freshness; future threshold theo source/adapter phải được preregister trước use | USDC adapter không có native round interface; upstream round không tự đổi tên thành adapter round. Chưa có freshness PASS |
| Missing/provider failures | Null/unavailable + reason + affected dependency; không thay zero, spot, forward-fill hoặc snapshot khác. Distinguish `BLOCKED_ACCESS`, `BLOCKED_CAPABILITY`, `FAIL_DATA`, `FAIL_SOFTWARE`; thành phần khác chỉ dùng khi không phụ thuộc dữ liệu lỗi | Prior unavailable providers và initial software errata được giữ, không gọi là agreeing observations |
| Recheck | 1 unexplained value mismatch hoặc nonrepeatability: case không PASS; giữ cả expected/observed và request scope, freeze affected output. Root-cause triage trước; chỉ retest phần bị ảnh hưởng sau quyền truy xuất phù hợp. Systemic parser/hash/ABI defect ảnh hưởng toàn pack phải dừng pack | Không tự đổi sample/threshold, xoá negative hoặc lấy majority vote từ cùng gateway để sửa lỗi. Issue33 không cấp quyền requery |
| Retention / common-mode risk | Future pack lưu sanitized decoded field values + request method/parameters không secret, comparator/version và checksums; nếu policy cấm full transport thì nêu rõ phạm vi replay. Giữ common-backend risk label dù mọi value khớp; chỉ request-linked evidence đóng Gate A | Existing Alchemy summary accepted ở mức CI result; full offline comparator replay còn gap. CI xanh/checksum không giải quyết common upstream/cache/software risk |

## Gate A: bằng chứng tối thiểu còn cần

Chỉ đề xuất hai câu hỏi cho provider; **không gửi liên hệ hoặc mua dịch vụ trong nhiệm vụ này**:

1. Với đúng request IDs/time windows của saved dRPC run39212923329 và Alchemy run39223539524, có thể cung cấp bằng chứng kiểm tra được gắn từng tập request với operator/upstream/serving node hoặc attested infrastructure path hay không? Nếu không còn retention, nêu giới hạn và khả năng lập một prospective attested campaign riêng.
2. Bằng chứng nào cho phép đánh giá hai actual serving paths có tách operator/upstream/shared-cache hoặc failure domain liên quan? Disclosure có giới hạn gì, yêu cầu access/chi phí gì? Tuyên bố kiến trúc chung hoặc tên sản phẩm không thay request binding.

Prospective attestation chỉ nghiệm thu campaign mới khi đủ dữ liệu; không hồi tố xác nhận backend của run cũ. Nếu chứng cứ không đủ, giữ Gate A BLOCKED. Nếu phát hiện shared backend, đánh dấu không đủ độc lập cho cặp đó, không biến absence of evidence thành PASS. Mọi quyết định thay entry gate cho công việc tương lai phải do Commander ban hành và giữ audit trail Gate A nguyên vẹn.
