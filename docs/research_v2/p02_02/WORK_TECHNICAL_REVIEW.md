# Work independent code review and targeted repair — P02-02

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED**

Original Codex HEAD `4b931e6425fd491f45af3d62532e7847ae5d05ee`, integration base `817b0f85547963939841e8bc7181e55b2b84d86f`. Work reviewed actual implementation, tests, handoff, architecture, pinned controls and all original CI evidence. Review is separate from Codex authorship; repair and recheck are Work self-review, not external peer review. No observed P0/frozen-data corruption. Six P1 and two P2 finding groups below required correction before technical acceptance.

| Finding | Reproduction / risk at original HEAD | Repair and acceptance criterion |
|---|---|---|
| WR02-01 / P1 | Provenance root can re-anchor its own modified catalog; actual saved identity is ignored, caller Git ref is presented without verification, read-pass boolean is accepted | Pin accepted LF registration/provenance SHA256 and Git blob identities, then verify their declared manifest/catalog/input bytes. Recheck supplied manifest against pinned on-disk controls, exact component filename/block/pass, actual identity and registration. Persist canonicality observation pointer and call accepted block/time/canonicality guards. Artifact Git ref remains explicitly CALLER_DECLARED, not an offline proof of a Git tree |
| WR02-02 / P1 | Pool spacing/price/numeric bounds, missing bitmap/ticks and duplicate initialized ticks can still return COMPLETE | Schema-check exact integer/decimal identities, uint160/uint128/int128 domains, band, bitmap word continuity and tick-bit membership. Missing/duplicate/inconsistent records reject. These are structural saved-data checks, not active-L reconstruction, native math or a swap |
| WR02-03 / P1 | Empty/duplicate borrower sample or reserves, wrong decimals, missing flags and future discovery headers pass | Compare selected identities and reserve sets/counts/IDs; validate ABI field types/config units, account observation-to-source trace, discovery window/headers and source configurations. Retain source-derived HF without recalculating it; missing dependencies reject complete views |
| WR02-04 / P1 | Duplicate oracle assets, wrong configuration, unsupported native-round promotion and future/contradictory round metadata pass; whole trace marked observed | Validate source/asset/configuration/scale and raw-to-normalized round linkage, timestamps and unsupported status. Composite view is RECONSTRUCTED, specific raw observations OBSERVED; normalized traces/age/cap checks remain RECONSTRUCTED/source-declared. Explicit field availability keeps unsupported native round and unknown heartbeat freshness visible |
| WR02-05 / P1 | Mutable containers/untyped enums and boolean timestamps survive DTO constructors; negative resource limits accepted; huge JSON integer or malformed gzip may leak decoder errors | Exact typed immutable DTOs and read-only capability allowlist, fixed positive resource ceilings, pre-parse depth/digit bounds, structured decoder errors and regular-file/path checks. Zero observed liquidity/debt-sentinel controls remain valid. Freeze is not protection against deliberate Python object mutation or a concurrently hostile filesystem |
| WR02-06 / P1 | CLI reverses distinct artifact/adapter commit arguments; first failure aborts without a report; eight specifications labeled implemented without remaining clauses | Correct argument order, retain per-view FAIL/BLOCKED reasons and nonzero exits, expose code-byte hashes and measured component coverage. Eight T01 specifications are PARTIAL_SAVED_ADAPTER_SCOPE; 38 T02–T05 remain NOT_IMPLEMENTED. No full native/source-independent validation implied |
| WR02-07 / P2 | Preservation test only checks existence; AST test misses import-from module names; wheel check only greps a filename; dedicated evidence lacks checksum list | Preserve all original 28 cases and strengthen weak assertions, add runtime/schema negative controls; compare all V2 wheel source bytes and emit/verify SHA256SUMS. Actual source trees and artifacts are also checked externally |
| WR02-08 / P2 | Committed smoke names an older adapter source and omits exact verification limits/availability | Committed smoke is explicitly STATIC_WORKTREE_EVIDENCE with code hashes and no self-referential final commit claim. Exact-head CI smoke + checkout/tree metadata is acceptance evidence. Partial-view loading is not implemented; missing required input blocks, never falls back to the old blocked borrower source |

## Reproduction and local verification

Original 28 adapter cases passed. Initial 24 independent reviewer controls exposed **22 failures / 2 passes** on original code; subsequent controls cover trust-root tampering, DTOs, changed economic payload, canonicality, unsupported native round, symlink escape, CLI identities/failure report and zero/opaque values. Final adapter suite is **70 cases = original 28 + 42 Work controls**. No original case removed; two weak assertions were strengthened. Synthetic fixtures test schema behavior only, never claim Mainnet evidence.

Actual local results: 247 scoped tests PASS (70 adapter + 97 P02-01 + 80 pre-Phase02), 0 fail/error/skip; affected 70-case suite rerun after report changes. L1 196 PASS / 0 FAIL / 0 L1 BLOCKED, L2 80 PASS. Two separate scientific LIMITATION BLOCKED records remain unchanged. Ruff PASS; strict mypy PASS on 13 V2 source files; wheel contains 14 exact V2 entries including py.typed. Local Python 3.12.14/Linux, pytest 8.4.2, Ruff 0.17.1, mypy 1.20.2, hatchling 1.27.0. No dependency lock changed.

Commands executed from the assembled pinned source root, with scratch-installed tools on PYTHONPATH:

```text
python -m pytest -q tests/v2/test_saved_adapter.py tests/v2/test_saved_adapter_review.py tests/v2/test_contracts.py tests/test_prephase02_offline.py --junitxml=FINAL_SCOPED.xml
python -m pytest -q tests/v2/test_saved_adapter.py tests/v2/test_saved_adapter_review.py --junitxml=FINAL_ADAPTER.xml
python -m pytest -q tests/test_prephase02_offline.py --junitxml=FINAL_LEGACY.xml
python docs/research_v2/prephase02_offline/validate_offline.py --validator-commit 4b931e6425fd491f45af3d62532e7847ae5d05ee --output FINAL_VALIDATION_GATES.json --l2-junit FINAL_LEGACY.xml --l2-exit-code 0
python -m ruff check defistress_v2 tests/v2 scripts/research/validate_p02_02_saved_adapter.py
python -m mypy --strict defistress_v2
python scripts/research/validate_p02_02_saved_adapter.py --source-commit 817b0f85547963939841e8bc7181e55b2b84d86f --adapter-source-commit 4b931e6425fd491f45af3d62532e7847ae5d05ee --output WORKTREE_SMOKE.json
```

Output filenames above abbreviate absolute scratch destinations; base SHA in the local validator is a validator-source anchor, not a claim that uncommitted adapter changes belong to that commit. An initial combined run failed because the assembled local checkout omitted P02-01 coverage JSON; it was restored from the pinned Git blob, then all 247 passed unchanged. Wheel built via hatchling.build.build_wheel and every V2 .py/py.typed compared byte-for-byte. Neither a model nor the historical collector was invoked.

## Original CI evidence actually read

All original runs completed SUCCESS on 4b931e6… . These are pre-repair evidence, not acceptance of a repaired HEAD.

| Run / artifact | ZIP SHA256 | Actual XML |
|---|---|---|
| Repository 39389630327 / 12248634305 | `5db073410445da62e75b8493c08cc5f7058ec83dc18954fe9bbf5b0919a41ac8` | 490 pytest + 5 environment smoke PASS |
| P02-02 39389630267 / 12248992039 | `e1b15ca4a4d9d7b9dc5c43ee31d0532edd4e83550b432dcb27c76a8121c5d98a` | 28 adapter / 97 contracts / 80 legacy PASS |
| P02-01 39389630132 / 12249265562 | `b4293b57f3c6b3e23c1bca7add77685e599cd6c290b4f6782feec9442260082c` | 97 contracts / 80 legacy PASS |

Full ZIP bytes/digests/CRC, JSON, JUnit and execution metadata read. Original PR checkout `9f24da1004cc7037eaae187a94f35984d104bd97` differs from branch SHA; actual Git objects resolve both to tree `4798d010a3851e3feb54b05a3d67b6914ccbdc07`. Optional live RPC job is SKIPPED. No source-independent historical or native execution inference follows.

## Hashes, scope and unresolved limitations

Accepted LF registration/provenance blobs are pinned in code and compared before loading. Actual CRLF checkout bytes, LF Git blob bytes, gzip artifact bytes, decoded JSON and snapshot content hashes are separate domains; normalization does not make their SHA256 equal. The component Git blob is computed from verified exact bytes; declared artifact/adapter commits are metadata until paired with externally checked CI checkout/tree. Legacy producer content hashes remain SOURCE_DECLARED, not V2 canonical hashes. Retrospective collection-end upper bounds are explicit, not invented per-request capture times or real-time forecast availability.

Canonicality is saved identity linkage with a collection-end bound, not a fresh chain assertion. Native USDC round remains unsupported, upstream trace separate, heartbeat freshness unknown. Composite observed/derived artifacts are not wholly labeled observed. Partial loading, general new-pack acquisition and native execution completeness remain unsupported. Borrower-repair is selected explicitly; original blocked full-borrower and metadata-only Alchemy limitations stay in audit. Snapshot/read-pass provenance hashes need not match across different passes or byte domains; repeatability means the same pinned input under the same selection.

Final repaired HEAD, exact-head runs, actual JUnit/checksums, protected-tree comparison and merge decision must be recorded in the PR verdict/program ledger after CI. Do not insert a circular self-commit here. Merge only with all applicable final-head CI passing; integration CI at the actual merge commit is a separate required gate. Rollback is a reviewed revert, never reset/tag movement. Gate A and historical execution authorization remain unchanged.
