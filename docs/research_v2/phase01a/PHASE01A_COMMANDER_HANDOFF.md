# Phase 01-A — Commander handoff

`DEFISTRESS_V1_SCIENTIFIC_BASELINE_RELEASED` · `V2_PHASE01A_READY_FOR_COMMANDER_REVIEW`

## V1

- [Annotated tag](https://github.com/Doquocdung1609/DeFiStress/tree/v1.0.0-scientific-baseline), tag object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`.
- [Published GitHub Release](https://github.com/Doquocdung1609/DeFiStress/releases/tag/v1.0.0-scientific-baseline), ID416585898. No slide/Canva/PPT assets. No tag move, engine/data/manuscript change.
- Exact [post-merge CI39147469533](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39147469533): backend226 PASS/0FAIL/0ERROR/0SKIP; frontend21 PASS; fresh Windows/Python3.12.10 environment105 locked packages and5 subset smoke tests. V1 live-RPC job skipped, historical replay and every deployment environment not certified.
- Dedicated release branch workflow [39148422358](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39148422358) created tag/release after checking gates. It changed no V1 source; tag targets the original release candidate. Initial read-PR permission issue was repaired by adding read-only PR metadata permission.

## Phase 01-A

Branch `research/v2-phase01a-historical-data` starts at the V1 release target. Number/pool registration commit `79ca47ee5459bc602f24553d3eb519216bec10dd`; historical hashes bound at `85d35785ce759598bff8282e9c3619c49d22d9f9` before state collection. Final delivery commit/one Draft PR are reported in the PR handoff to avoid a self-referential commit field.

- Three blocks:26045352,26038152,26030952; fixed offsets, baseline retained.
- Two factory-verified pool candidates: USDC/WETH3000 and500 millionths; concrete addresses/hashes in registry.
- Live collection: [run 39149158699](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39149158699) at `85d35785ce759598bff8282e9c3619c49d22d9f9`. **3/6** complete two-pass provider/block rows; **1** full-data endpoints; **18** quarantined components. Unit suite21 PASS, separate from live data findings.
- Exact raw request/result and snapshot files, catalog and quarantine are archived under `evidence/`; their actual SHA-256/size are in `PILOT_DATA_PROVENANCE.json`. Canonical registry hash is distinct from raw Git file hash. Parsed JSON transcripts do not claim original HTTP wire-byte capture.

## Gate recommendation

Mẫu tối thiểu3 block ×2 pool đã có dữ liệu đầy đủ và two-pass hashes qua dRPC. Đề nghị Commander nghiệm thu nền tảng pilot, quyết định riêng Phase 01-B; trước khi dùng như bộ dữ liệu nghiên cứu mở rộng cần archival coverage ổn định và đối chứng state từ nguồn độc lập. PublicNode state vẫn DATA_ACCESS_BLOCKED, không phải PASS. Commander review should accept the data/provenance foundation at its declared scope, then issue a separate next-phase order. Three nearby blocks, one pair/two fee tiers, three borrower sentinels, local tick sampling and source-address-level oracle tracing remain explicit limits. Two public endpoints do not certify archive coverage/SLA for future sampling. No stress model result, causal validation, forecasting claim, new scientific claim or Phase 01-B execution is asserted.

No merge or V2 scientific lock performed. Scientific/Blueprint/manuscript anchors and annotated V1 tag remain immutable.
