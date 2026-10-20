# Work technical review and targeted repair — P02-01

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED**

Reviewed original Codex HEAD `c67129877f97be204e5623954dd3057166fb7531`, base `0ea1c878a6e0f0d62fe01bedc37f619602b9d35f`. Work reviewed actual code independently of Codex authorship; targeted repairs and their recheck are Work self-review, not external independent peer review. No engine, empirical result, scientific source or gate has changed.

## Findings and acceptance criteria

| ID / severity | Actual reproduction at original HEAD | Targeted repair / acceptance criterion |
|---|---|---|
| WR-01 / P1 | A mutable CanonicalSerializable retained inside EvidenceEnvelope changes stored content hash after caller mutation; a frozen shell can also contain mutable fields | deep_freeze only retains deeply immutable slotted frozen serializers; nested fields are checked. Caller-owned mutable serializers/frozen mutable children reject; native immutable contracts preserve nominal types. Ordinary freeze API is not a sandbox against deliberate object.__setattr__ or impure user code. |
| WR-02 / P1 | Observation at block100 wrapping evidence for block101 returns OK; OBSERVED envelope accepts the wrong source; same-hash timestamp mismatch and effective-time after block pass | Context↔source↔as-of identities and timestamps agree. Missing source block returns BLOCKED/MISSING_BLOCK_REFERENCE. Historical effective time≤block timestamp; effective≤available≤as-of. OBSERVED envelope requires block-bound matching sources. Derived/counterfactual parents may refer to historical inputs with explicit lineage; this repair does not force all parent history into one block. |
| WR-03 / P1 | Changing only retrieved_at_s changes deterministic content hash | Full serialization preserves acquisition fields; explicit typed content projection excludes only EvidenceRef.retrieved_at_s, also in nested payload references. Economic/block/availability/canonicality assertion timestamps and ordinary user payload keys remain. Raw/source/full-provenance hashes and stable content hashes have different domains and may differ. |
| WR-04 / P1 | sources iterator is consumed by validation and then materializes empty; OBSERVED envelope gets zero sources | Snapshot explicit tuple/list containers before checking entries/nonempty/alignment; single-use iterators reject. Same discipline for parent vectors, availability refs and warning vectors. No fallback fills absent references. |
| WR-05 / P2 | A5000-digit amount raises Python ValueError; raw-string constructors coerce integers despite nominal signature | Compare canonical magnitude length/value to uint256/int256 bounds before conversion; from_int range-checks before formatting; raw constructors require exact strings. Wrong types/overflow have typed contract rejection. |
| WR-06 / P2 | NET_LIQUIDITY could be represented as an asset-denominated SignedDelta with USDC decimals | Asset deltas accept DELTA only; NET_LIQUIDITY enumerator remains reserved/unsupported until a pool-liquidity unit contract is implemented. Do not use token decimals to label active L/gross/net liquidity. |

Original70 tests PASS locally. First25 reviewer controls exposed22 failures/3 passes at the original implementation (70 original cases deselected only for that focused reproduction). Further controls cover pool units and canonicality header-time binding. Final suite retains all70 original cases and adds27 controls:97 total. One original assertion equated content hash with full acquisition-provenance hash; replaced by the stronger separation contract and retrieval-invariance/economic-change/nested-reference controls. The normative source is accepted architecture DATA_AND_INTERFACE_CONTRACTS §1 and the P02-01 handoff, not a relaxed expectation for CI.

## Scope and compatibility

pyproject changes only extend wheel packages from backend/sim to include defistress_v2; dependency constraints, pytest paths, lint/type rules and existing CI workflow are unchanged. The new workflow is isolated to P02 files/pyproject, records workflow head separately from checkout/merge-ref, runs actual97/80 JUnit and strict mypy on the new package. It does not launch RPC or a model. WORK repair does not alter that workflow or V1 sources. Import review found only stdlib/internal contract dependencies; no engine/network/secret invocation.

guard_same_block_and_time now includes a structured Blocked outcome for missing evidence identity. Consumers must distinguish OK/BLOCKED/REJECTED; do not assume every non-Rejected result is OK. EvidenceEnvelope.to_content_canonical is the stable projection; to_canonical is the full provenance serialization. Decoder schema remains defistress-v2-contracts/0.1 because this is a pre-acceptance correction, not a rewrite of a released scientific dataset. canonical JSON is serialization, not proof of external source authenticity or historical validation.

All46 design IDs were reconciled:6 partially implemented contract specifications,40 not implemented. Remaining clauses for each partial ID are explicit in P02_01_SPEC_COVERAGE.json. P02-T01-01/07 adapter/capability work and all T02–T05 math/execution/orchestration remain unimplemented. No native/market-wide inference follows from tests.

## Actual evidence and verification limits

Original artifacts were downloaded in full, ZIP digest/CRC checked and XML parsed. Dedicated push artifact12234378770 has4/4 SHA256SUMS matches,70 P02 tests,80 legacy tests and L1=196PASS/0FAIL/0 L1 BLOCKED. Dedicated PR artifact12234523927 has the same counts; checkout1122d861271b4003e630f606a640893c243abe06 is distinct from workflow head c671298…, with the same source tree. Normal push artifact12233889801 contains435 passing pytest cases and5 environment-smoke cases. These are pre-repair evidence, not acceptance of the repaired HEAD.

Final local/remote results, exact repaired SHA, run URLs and artifact checksums are recorded in the PR technical verdict and program-control ledger after CI, rather than inserting a circular self-commit reference here. Local scoped tools: Python3.12.14/Linux, pytest8.4.2, Ruff0.17.1, mypy1.20.2; target CI is Python3.12.10. mypy/hatchling installed in a scratch tool directory; no V1 lock/dependency changed. Native protocol/execution and independent archive validation are outside these tests.

Only propose merge when final-head dedicated and repository CI pass, actual reports/JUnit/checksums are read, allowed diff/preservation is verified, and all six findings meet the acceptance criteria above. Rollback via reviewed revert; no reset or V1 tag movement. Integration CI at the actual merge commit is a separate required gate.
