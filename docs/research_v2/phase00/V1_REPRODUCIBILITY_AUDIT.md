# V1 Reproducibility Audit — Phase 00

**Verdict:** `PARTIAL_STATIC_REPRODUCIBILITY_VERIFIED — RELEASE_FREEZE_BLOCKED`.
**Candidate:** `ee9b372823e5c636238efe73a4268a5439cf1f80`. Đây là Work static/smoke audit; không phải independent research replay.

## 1. Việc đã thực sự chạy

| Kiểm tra | Kết quả | Phạm vi |
|---|---|---|
| GitHub commit/ref/recursive trees/compare | PASS |925 tracked blobs; Scientific854/854 và Blueprint878/878 không đổi; integration đúng candidate |
| Exact Git blob + observed SHA256 |446/446 PASS | File cache chỉ dùng khi byte hash khớp Git tree đã truy xuất;479 file chỉ object identity |
| AST Python |178/178 PASS | Toàn bộ `.py` dưới backend/sim/tests/scripts đã lấy; syntax, không chứng nhận semantics |
| Existing pure HF/liquidation tests |5/5 PASS | Gọi trực tiếp5 hàm test qua `runpy`; không chạy pytest, engine hoặc Monte Carlo |
| Registry/provenance |48records,44affirmative/4disallowed;6RQ;29/29paths |28source byte hashes khớp; một nguồn lớn chưa byte-check |
| Bảy chương/final manuscript | PASS_STATIC |7 ch đúng thứ tự;6RQ nguyên văn mỗi câu2lần; DOCX CRC tốt;16tables/11figures/8native display equations |
| Legacy checksum sample |78 declarations |14 exact;61khớp biểu diễn CRLF;2 chưa byte-check;1 builder declaration mismatch |
| Candidate CI | FAIL |[run38994362948](https://github.com/Doquocdung1609/DeFiStress/actions/runs/38994362948),0 jobs; không suy ra tests đã chạy và fail |
| Fresh install/API/frontend/fork/replay | NOT_RUN | Không được nhận là PASS |

Công cụ nhỏ `verify_v1_baseline.py` đi cùng hồ sơ chạy read-only, không có đường gọi engine. Lệnh thực tế:

```bash
python phase00_delivery/docs/research_v2/phase00/verify_v1_baseline.py \
  --repo phase00_cache/repo \
  --manifest phase00_delivery/docs/research_v2/phase00/V1_RELEASE_MANIFEST.json --smoke
```

Audit environment: CPython3.12.14 trên Linux x86_64, Node24.19.0. Quan sát18package base/dev khai báo chưa cài (gồm pytest, Web3, FastAPI, NetworkX…). Không cài thêm rồi gọi đó là môi trường khoa học gốc. Năm pure tests không cần các dependency đó; không phải con số pytest PASS. Phần environment trong manifest lưu từng version quan sát được, bản khai báo V1 và các package do Terra manifest báo cáo trước đây như ba tập bằng chứng riêng.

## 2. Các mức tái lập

| Mức | Trạng thái | Có thể kết luận |
|---|---|---|
| R0: xác định nguồn/code/data/results | PASS cho tree; byte coverage446/925 | Khôi phục đúng snapshot Git và đối chiếu các file đã đọc |
| R1: parse/schema/link/checksum | PASS_SCOPED; REL-03/04 còn mở | Small artifacts/registry kiểm tra được; không nhận full archive integrity |
| R2: primitives/smoke |5 pure assertions PASS | Một số bất biến HF/close factor/collateral cap đúng trong test có sẵn |
| R3: dependency/application/CI | Chưa đạt ở candidate | Python môi trường chưa khóa; CI không tạo jobs; frontend/API không test mới |
| R4: selected deterministic/replay | PRIOR_EVIDENCE_ONLY | Báo cáo Codex72replays/32688HF/2186events là kiểm tra trước đây, không phải Work đã tái thực hiện |
| R5: full frozen research rerun | NOT_RUN | Không xác nhận tái sinh toàn bộ grids/10kpaths/Terra outputs |
| R6: lịch sử và fork execution | LIMITED/NOT_RUN | Snapshot/events có provenance; không có validated independent local-fork liquidation/swap |

## 3. Blockers và điều kiện giải quyết

**REL-01 — CI baseline.** `.github/workflows/ci.yml`, job `real-rpc-smoke.if`, dùng trực tiếp `secrets.ETH_RPC_URL`. Candidate workflow kết thúc failure trước khi tạo job. [PR19](https://github.com/Doquocdung1609/DeFiStress/pull/19) đang open, chỉ đổiCI. Audit đã đọc [run38995096556](https://github.com/Doquocdung1609/DeFiStress/actions/runs/38995096556) tại `b3b34f4a837a2854f5348a75d07fc66b55a1b232`: backend/frontend/config steps success, RPC skipped. Con số217passed/9deselected là báo cáo [handoff](https://github.com/Doquocdung1609/DeFiStress/pull/19#issuecomment-6228553623), không phải đếm lại logs hay PASS của candidate. Cần Commander xử lý PR19 và xác định lại release candidate nếu merge; Phase00 không sửaCI hoặc chuyển anchor âm thầm.

**REL-02 — environment chưa khóa.** `pyproject.toml` dùng ranges, không có Python resolver lock hoặc đầy đủ resolved environment cho workload khoa học gốc; Docker dùng tags không digest. pnpm có lockfile nên mức khóa frontend tốt hơn, nhưng Phase00 chưa install/build. `docs/research_final/REPRODUCIBILITY.md` mô tả run cũ/commits cũ, PythonWindows3.12.14/Node22.13.1, không phải đủ đặc tả release hiện hành. Terra manifest lưu vài package versions, không phải toàn bộ pip lock. Cần recover environment có nguồn hoặc tạo môi trường pin mới có kiểm tra riêng, lưu OS, dependency/package hashes và image digests; không tự gán toàn bộ V1 reproducible.

**REL-03 — builder hash chưa đối soát.** Tại `data/processed/research_final/scientific_integration_v1/manifest.json`, field `implementation_hashes["scripts/research/build_scientific_integration_v1.py"]` khai `5a1bbd87ccf065763c3f82d921b977dadb21c520d073e5a2f69498f42ed094a2`. File candidate có LF SHA256 `9e88de4f4d17dc43f9c09183e9c93bce639ebdde4ea059eaa7bbed81788d5159`; biểu diễn CRLF là `81e5d1dadaac1533b818409a0e0f0e13dc6c8b7ad9a3469033cf43243fa7e686`. File tại source commit `c113fc1ec6dd98ffcc31241c1dbd1a93b20aa193` có Git blob `ee06689a114c4e07eead7a320cb71dd8cdbb6157`, LF `3b5feaeb4d85ea2d493a4d3c7b06df139a79d7f52eae9ee23db1883e1d471a7f`, CRLF `1b4be15bfa5c135811ecdeb9390255264cc27f6003c4ea9377d069e0317f0930`, cũng không khớp declaration. Đây là thiếu liên kết generator–manifest, không tự chứng minh numerical corruption. Cần exact historical generator matching declaration hoặc một provenance erratum Commander duyệt, đặt ngoài frozen sources; không sửa/ghi đè Addendum để làm khớp.

**REL-04 — chưa đủ byte coverage critical archives.** HaiCSV lớn Oracle `borrower_level_evidence.csv` và Integration `eligible_vs_executed_audit.csv` cùng các checkpoint Severe10000/5000 và raw swap archive có đường dẫn, kích thước, Git object identity; Phase00 chưa đọc đủ byte/rows hoặc tái tạo. Cần đối chiếu exact SHA256 qua full authorized clone/archive trước khi tuyên bố checksum gate hoàn chỉnh. Việc này không cần chạy lại mô phỏng. Kể cả khi checksum khớp vẫn phải ghi riêng row-level scientific audit và replay scope.

Các manifest cũ còn `scientific_content_lock_declared:false`/trạng thái pending là lịch sử tạo artifact, không phải bằng chứng Scientific Lock đã bị hủy. Quyết định khóa sau đó và registry v1.1 có precedence. Không sửa metadata gốc.

## 4. Hash domains và checkout

Canonical LF SHA256 là `76dae833c5b1a6e620cf116e332f1f47c53454a1f3530a02fefacd800cb3b329`; declaration Windows CRLF là `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99`. Cả hai được lưu riêng. Đối với61 declarations, phép chuyển LF→CRLF tạo byte hash khớp declaration; đây là phép kiểm tra representation, không phải quan sát lại file Windows ban đầu. Không gọi hai hash khác nhau là cùngSHA. Mismatch REL-03 vẫn mismatch sau kiểm tra cả hai representations, không được che bằng giải thích line endings.

Test sources có raw-byte assertions, lịch sử Git/remote refs và builder path Windows; một số kiểm thử sẽ không portable trên shallowLinux checkout. Không chạy nguyên suite rồi đánh tráo deselected thành PASS. Giữ đủ lịch sửGit cho những tests dùng `git show`/`cat-file` và ghi rõ kết quả từng platform.

## 5. Hướng dẫn khôi phục an toàn từ frozen inputs

Các lệnh dưới là hướng dẫn cho máy có quyền repository, không phải lệnh đã thực thi ở Phase00:

```bash
git -c core.autocrlf=false clone --no-checkout https://github.com/Doquocdung1609/DeFiStress.git DeFiStress-v1
cd DeFiStress-v1
git -c core.autocrlf=false checkout --detach ee9b372823e5c636238efe73a4268a5439cf1f80
git rev-parse HEAD
git status --short
```

Lấy sáu file Phase00 tại commit PR bàn giao vào thư mục audit riêng (candidate tự nó chưa chứa hồ sơ mới). Chạy verifier bằng Python3.12; chế độ Git-object tránh nhầm CRLF checkout:

```bash
python /path/to/phase00/verify_v1_baseline.py --repo . \
  --manifest /path/to/phase00/V1_RELEASE_MANIFEST.json --git-object
```

Chỉ trên cleanLF checkout, dùng `--smoke` thay `--git-object` để chạy5 pure assertions và đối chiếu byte filesystem. Verifier chỉ check những file có SHA256 observed, in rõ479 file chưa byte-check; không cấp tag/gate PASS toàn hệ. Cập nhật checksum coverage còn thiếu là công việc read-only riêng trước phát hành.

Environment cài mới, nếu sau này được thực hiện, phải ở venv/container riêng; `pip install -e '.[dev]'` hiện chỉ là resolver theo ranges, **không đủ tái lập environment gốc**. Ghi lại output lock/resolution và xác minh trước khi chọn làm baseline environment. RPC/Graph/archive credentials, DB import, Foundry và frontend services thuộc các cấp kiểm tra riêng; không thay cached snapshot khi live RPC không sẵn.

Không chạy `scripts/run_full_research_pipeline.py --research`, các bundle builders, `--overwrite-final` hoặc demo/simulation để kiểm tra release này: có thể chạy workload lớn hoặc ghi lại artifact khóa. Nếu Commander mở một reproduction study sau này, dùng checkout và output directory cách ly, pin inputs/seeds/versions, đối chiếu generated outputs với frozen archive; kết quả âm hoặc mismatch phải báo cáo, không retune để ép khớp.

## 6. Giới hạn nghiên cứu và phát hành

Giữ Scientific Lock với một snapshot/venue/cohort, hypothetical policies, eligibility≠execution, vốn không recycle/non-split plans, unfunded arbitrage repositioning, Severe counterfactual tails, MC có điều kiện, historical associations không nhân quả, negative Terra strictOOS và graph chưa fullmultilayer. RQ6 LTV255 khác109; LTUSDportfolio tại USDC/USD1 khác tokenUSDC. Nguồn P2 không nâng access level. `TEMPLATE_VERIFICATION_PENDING` và administrative cover metadata thuộc final submission, không được xem là đã xử lý bởi việc đóng băng code.

**Kết luận:** có cơ sở bảo toàn một archival candidate có định danh chính xác và kiểm tra tĩnh hữu ích; chưa đủ điều kiện tag `v1.0.0-scientific-baseline`. G1 chỉ hoàn thành hồ sơ chuẩn bị. Cần đóng REL-01…04 và nhận quyết định Commander trước tag/release; không phải sửa số liệu để tạo PASS.
