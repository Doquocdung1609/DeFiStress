# Integration Commander Review Packet

**Đề nghị:** `READY_FOR_COMMANDER_REVIEW`. Không đề nghị merge tự động hoặc scientific lock.

## Provenance

- Starting HEAD: `3011ba5e8cd23ee697c36d0aec6d047d8d58f653`.
- Source/artifact commit: `c113fc190ed9eb1c9244bbf8e84e68176738ea95`.
- Artifact bundle commit: `c113fc190ed9eb1c9244bbf8e84e68176738ea95`.
- Dependency PR #11: DRAFT/OPEN, accepted `SCIENTIFIC_PASS_WITH_LIMITATIONS` for targeted diagnostic.
- P2 PR #9: DRAFT/OPEN @ `8f5b635a316d72546b8a0eb0c2e8a66503b5d44f`; oracle reconciliation delta do Work quản lý còn mở.

## Deliverables

- `data/processed/research_final/scientific_integration_v1/`: manifest, six-RQ matrix, claim registry, result registry, eligible/executed borrower audit, event trace, summary, accepted claims, validation and precedence.
- `docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md`.
- `docs/research_final/INTEGRATION_COMMANDER_REVIEW_PACKET.md`.

## Kết quả gate trọng yếu

- 72/72 targeted replays hash-match; không 10k rerun.
- 32,688 audit rows; 2186 event locators.
- Policy A/B/C deterministic 4/0/0/0; targeted MC 10/0/0/2.
- Claim registry: {'ACCEPTED_WITH_LIMITATIONS': 9, 'REQUIRES_CORRECTION': 2, 'UNSUPPORTED': 2}.
- RQ1/RQ2 được giới hạn policy-dependent; RQ3–RQ6 bảo toàn.
- Frozen/Oracle/canonical hashes giữ nguyên.

## Tiêu chí Commander

**PASS/ready:** chấp nhận wording policy-conditional, eligible-vs-executed reconciliation, evidence tiers và provenance.

**REWORK:** locator thiếu, policy attribution sai, nhầm 454/109, USDC/USD, newly/executed, hoặc claim dùng artifact superseded.

**BLOCK:** hash input thay đổi, event trace không tái lập, hoặc P2 delta tạo xung đột claim chưa hòa giải.

## Blocker và caveat

Không có blocker số học nội bộ được phát hiện. Dependency không chặn review addendum nhưng chặn global lock: P2 oracle reconciliation trên PR #9 chưa có HEAD mới sau Commander comment `6166173420`. Các giới hạn actual oracle, fork, extreme haircut, historical causality, representative agents, Terra OOS và network aggregation phải được công bố.

## Test evidence

- Trạng thái: `PASS`.
- `.\.venv\Scripts\python.exe scripts/research/build_scientific_integration_v1.py` → **PASS** (72/72 targeted replay hashes; 32,688/32,688 independently recomputed HF traces; 2,186 event rows; all integration gates passed).
- `.\.venv\Scripts\python.exe -m pytest tests/test_scientific_integration_v1.py tests/test_oracle_diagnostic_artifacts.py tests/test_frozen_v3.py -q` → **PASS** (15 tests passed).
- `.\.venv\Scripts\python.exe -m pytest -q` → **PASS** (180 tests passed; 3 dependency deprecation warnings).
- `.\.venv\Scripts\python.exe -m ruff check .` → **PASS** (All checks passed).
- `.\.venv\Scripts\python.exe -m mypy sim` → **PASS** (Success: no issues found in 49 source files; matches pyproject and CI scope).
- `.\.venv\Scripts\python.exe -m mypy .` → **OUT_OF_SCOPE_CONFIGURATION_FAILURE** (Duplicate legacy Terra pack module names outside configured mypy package scope; no integration source error evaluated by this invocation).
