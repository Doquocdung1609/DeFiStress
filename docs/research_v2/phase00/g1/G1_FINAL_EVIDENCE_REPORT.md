# V1 Release G1 — Final Evidence Report

**Target:** `V1_RELEASE_G1_FINAL_EVIDENCE_READY_FOR_COMMANDER_REVIEW`.
**CI reviewed:** [Run 39125232234](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39125232234), head `aaa010889e857c7042c3a209c88b8e8de1c8d6cc`, conclusion **success**.
Không tạo tag, GitHub Release, merge PR26 hoặc bắt đầu Phase01.

| Gate | Trạng thái | Bằng chứng / thay đổi | Phạm vi còn mở |
|---|---|---|---|
| REL-01 | `PASS_FULL_SUITE_NO_DESELECTION` | Full pytest: **226 PASS / 0 FAIL / 0 ERROR / 0 SKIP; 226 tests**. Không sửa test sources, không -k/deselect/skip mới. Giữ Ruff/mypy/frontend và protected-source guard. | Live RPC job skip do thiếu cấu hình; không gọi là Mainnet validation |
| REL-02 | `PASS_NEW_WINDOWS_TARGET` |105 distributions có wheel hashes; strict install `--require-hashes --only-binary=:all:`; fresh isolated venv + pip check +5 original smoke assertions. Python3.12.10, Windows Server2025 x64. | Đây là môi trường target mới được kiểm tra, không phải phục hồi environment lịch sử; không chứng nhận Linux/Docker deployment |
| REL-03 | `RESOLVED_HISTORICAL_GENERATOR_IDENTIFIED` | Declared SHA256 `5a1bbd87…` khớp source tại `a39337780f0e8d3807138a6048aaa1e1d7d9c8c8`; diff về sau chỉ có3 typing locations. External erratum giữ expected/actual/object IDs. | Không re-execute generator để chứng minh mọi output; manifest gốc giữ nguyên |
| REL-04 | `PASS_COMPLETE_BYTES_SCOPED` |91 complete-byte records,309.463.168 bytes;90 file V1 hiện hữu +1 historical DOCX fixture mới;0 UNVERIFIED trong tập này. SHA256/size/Git blob theo từng file. | Byte identity khác scientific row audit, query lịch sử hoặc full research rerun |

## REL-01: phân loại lỗi và sửa hạ tầng

Run39122762384: **217 passed,9 failed,0 skipped** trong226 tests. Frontend đạt; RPC job skip. Thiếu2 DOCX nguồn là lỗi provision đường dẫn; các hash assertions thất bại do checkout đồng loạt CRLF trong khi declaration gốc dùng hỗn hợp LF/CRLF; các Git-status assertions còn lại chịu hệ quả manifest bị builder thay đổi khi hash của source/test bytes lệch. Không có căn cứ từ các lỗi này để tự sửa numerical results.

Bổ sung đúng2 DOCX có checksum trùng `DOCX_BASELINE`; đây là fixture lịch sử, không thay báo cáo7 ch hoặc template trường. Runtime pin Python và105 package wheels, dùng source pin qua PYTHONPATH, không cần editable install/build backend không được khóa. Nguồn project là Git commit; package build/wheel production chưa được chứng nhận.

Checkout recipe chỉ tạo bản biểu diễn byte đã được ghi nhận từ **exact Git objects**: LF literal, CRLF theo từngpath, binary giữ nguyên. Quy tắc được suy từ frozen manifests và locked G0 inventory; mâu thuẫn phải FAIL. Chỉ cấu hình `.git/info/attributes`, không commit đổi source science. Có byte readback, strict `git diff --exit-code`/cached diff và index-tree guard; không dùng assume-unchanged/skip-worktree hoặc ignore-whitespace. Git index được đọc lại từ chính HEAD và kiểm tra tree trước/sau không đổi để loại cache stat/EOL cũ. Các thử nghiệm hạ tầng và lỗi YAML trung gian giữ trong lịch sử PR; không tính chúng là scientific PASS.

CI cuối và từngjob/step được lưu trong `G1_FINAL_RESULT.json`. Test assertions và collection vẫn nguyên bản. Năm smoke tests môi trường trùng với5 tests trongfullsuite: không cộng chúng thành231 unique tests.

## REL-02: môi trường cài thử thực tế

Lock: `requirements-windows-py312.lock.txt`, SHA256 `edc53ad79a7b9924bd8a9c889e053547dc620a9b1482a3551b150fcd1e08f4ff`. Mỗi version đi kèm SHA256 wheel đã tải, không tạo hash giả. Collector cài vào venv sạch từ wheelhouse bằng require-hashes, pip check và smoke; phiên sau cài từ lock đã commit, rồi đối chiếu lock tái tạo với Git bytes. Báo cáo environment lưu Python build, OS, runner image nếu có,105 package names/versions/wheels/hashes và source/run locator.

Container không được sử dụng: Docker digest là `NOT_APPLICABLE_NO_CONTAINER_USED`; không bịa image digest. Dockerfile/compose cũ chưa được kiểm định triển khai bằng dossier này. Wheelhouse không được vendor vào repository; đây không phải cam kết tái lập offline khi package server không còn khả dụng. Mức xác nhận là **native Windows target source-execution environment**, không phải toàn bộ V1 reproducible trên mọi máy.

## REL-03: provenance erratum

Xem `GENERATOR_PROVENANCE_ERRATUM.md` và `GENERATOR_HISTORY.json`. Declared checksum trỏ generator ở `a3933778…`, blob `ba55014f33a435b91fdd797eb08616e561b6cd02`,72.333 bytes LF. Pointer `c113fc1…` là nguồn gốc integration sớm hơn; không phải object matching checksum. Current generator tại `cebd23a4…` có LF `9e88de4f…` và CRLF `81e5d1da…` sau typing patch; không equate hai representation. Không sửa Frozen/Oracle/Integration manifest để che lịch sử.

## REL-04: complete-byte scope

`LARGE_ARTIFACT_CHECKSUMS.json` giữ từngpath, exact byte size, Git blob SHA1, actual SHA256 Git bytes, text CRLF representation riêng nếu áp dụng và status. CI collector dùng full `git cat-file` và kiểm tra lại header/blob identity, không suy SHA256 từ Git object ID. Work tải ZIP evidence qua connector, đối chiếu ZIP digest với GitHub metadata và đối chiếu57 file overlap với local verified bytes. Hai CSV trước đây chưa được Work đọc đầy đủ nay đã được **collector do Work viết đọc toàn byte trong CI**; không tự nâng thành row-by-row scientific audit độc lập.

Các file bắt buộc đều được bao phủ (hash đầy đủ trong JSON): Oracle borrower CSV8.775.089bytes; Integration eligible/executed CSV18.489.195bytes; Severe10000 checkpoint8.992.978bytes,5000 checkpoint4.494.875bytes; raw swap archive4.172.573bytes. Không chạy lại Monte Carlo hoặc tạo metric nghiên cứu mới.

## Preservation / quyết định

Scientific Lock `3f6e5302483681209e2408531eb5a15389f9fded`, Blueprint Lock `8de52bebabef376be700836e6f93a92d7394d2c3` và V1 candidate `ee9b372823e5c636238efe73a4268a5439cf1f80` vẫn là source anchors lịch sử. Chỉ workflow, release tools/fixtures và hồ sơ release thay đổi. Source-preservation và PR diff phải giữ0 thay đổi engine/data/claims/bảy chương/Scientific Lock/test sources.

Không còn blocker bằng chứng REL-01–04 trong phạm vi đã kiểm tra; quyết định release vẫn thuộc Commander.

Scientific limitations V1 vẫn giữ nguyên, gồm oracle giả định, một snapshot/venue/cohort, eligibility khác execution, capital/arbitrage simplifications, conditional MC, historical association không nhân quả, Terra negative OOS và mạng chưa full multilayer. `TEMPLATE_VERIFICATION_PENDING` vẫn là gate hình thức riêng. Không tự cấp V1 freeze, tag/release hoặc merge; Commander quyết định trên evidence cụ thể.

Frontend tại run đã đọc: **21 PASS / 0 FAIL / 0 SKIP**, Node `v24.21.0`, pnpm `11.19.0`; Ruff, mypy và fixture demo đều đạt. RPC smoke là **job SKIP**, không phải pytest SKIP. CI không có deselection.

Các JSON evidence được archive từ run39125232234 tại head `aaa010889e857c7042c3a209c88b8e8de1c8d6cc`. Commit bàn giao sau đó chỉ cập nhật hồ sơ và loại fixture Spec không thuộc DOCX_BASELINE; CI của exact delivery HEAD được kiểm tra và ghi trong PR26 handoff để tránh self-referential commit hashes.
