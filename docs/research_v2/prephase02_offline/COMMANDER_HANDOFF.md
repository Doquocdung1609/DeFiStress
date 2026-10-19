# Issue #35 — Commander handoff

**Authorized scope:** L1 offline evidence integrity and L2 pure synthetic data-contract checks. **Branch:** `research/v2-prephase02-offline-contracts`, starting at `2e0ec142c475f8d1362f90c4ca8d2f0718e41f77`. [Draft PR #36](https://github.com/Doquocdung1609/DeFiStress/pull/36). No merge authorized.

## What is tested

- `validate_offline.py` reads pinned Phase01-B sample registration, both preserved gzip evidence manifests, checks each saved file's byte length, SHA-256, uncompressed digest where declared, Ethereum chain/three block-hash identities, two pool fee tiers and USDC/WETH decimals. The script writes a machine-readable `VALIDATION_GATES.json` from actual execution; it never requests RPC data.
- `tests/test_prephase02_offline.py` uses synthetic negative/positive controls to exercise pure guard functions. It is not a model engine, economic simulator, borrower state recreation or new empirical data.
- `OFFLINE_EVIDENCE_MANIFEST.json` pins provenance and declared coverage boundaries. **24 borrower-block pairs, 67 reserves/account, 6 pool-block tick bands and 6 oracle traces** remain source-declared metrics, not generalized coverage claims; validating historic raw value correctness beyond digests requires original collection methods and cannot be extrapolated from counts.

## Non-replayable / residual gaps

Alchemy's saved `VERIFIED_CI_EVIDENCE.json` has run/summary/hash metadata but not all raw returned Alchemy field values: **NOT_REPLAYABLE_FROM_PERSISTED_SUMMARY**. Field agreement 174/174 was established by prior CI and is not independently recomputed here. The originating artifact may expire. dRPC and Alchemy backend identities remain **UNVERIFIED**. L1 may attest local file integrity; it is not scientific archive-independence proof. A correct synthetic test demonstrates guard behavior, not observed Mainnet evidence.

## Targeted validator/CI repair

Starting PR36 HEAD verified: `c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb`. [Run39281653358](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39281653358) failed before report creation: file records had `path/status/reason` but aggregation expected every check to contain `id`. Full repository CI also found one Ruff I001 in the test imports, although320 pytest tests passed before the added regressions.

Repair: a shared validated check record contract and explicit scope; missing/malformed IDs/records and duplicates become diagnostic FAIL, not fallback normalization. File/JSON/schema/I/O errors produce reasoned FAIL/BLOCKED, report writes are serialized before atomic replacement, software/serialization failure emits a diagnostic report where writable, and missing L1 evidence returns nonzero BLOCKED rather than success. Only registered Alchemy replay/backend limitations are excluded from L1, with exact IDs/status/reasons checked; Gate A/B semantics are unchanged.

Running L1 then exposed an independent typo in the P500 constant: `0x88e6a0c2dd26feeb64f039a2c41296fcb3f5640` (41characters) versus the locked registration `0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640` (42characters). The code literal was corrected to the existing source; registration, manifest, blocks/pools and numerical evidence are unchanged. Both fee-tier identities have positive/negative regression coverage.

Local actual checks after repair: **L1 PASS —196 checks PASS /0 FAIL /0 L1 BLOCKED**, including189 source-manifest file entries (110 full+79 borrower repair) with saved bytes/size and decoded gzip hashes when declared; seven registration/provenance summary checks. Global counts retain **two BLOCKED LIMITATION records**, not unresolved L1 failures: Alchemy full-value replay and backend independence. These are byte-integrity/declared metadata checks, not fresh blockchain verification or a reconstruction rerun.

L2/regression tests: **80 PASS /0 FAIL /0 ERROR /0 SKIP**, pytest8.4.2 on Python3.12; Ruff0.17.1 PASS on changed validator/tests. Generated JSON and JUnit were read back, counters and JUnit SHA256 matched. Local command:

```bash
python -m pytest tests/test_prephase02_offline.py --junitxml=l2-junit.xml
python docs/research_v2/prephase02_offline/validate_offline.py \
  --output VALIDATION_GATES.json --l2-junit l2-junit.xml --l2-exit-code 0
```

In CI, `--l2-exit-code` is taken from the actual pytest step outcome (not hardcoded0); L2/finalize/upload steps retain failure evidence with `if: always()`. Missing/empty/invalid JUnit cannot issue L2 PASS. No continue-on-error or tests removed. Final-head CI run/commit/artifact digests will be provided in the PR handoff; these local results do not substitute for that gate. PR37, integration, tag/V1 and prior research outputs are not modified.

## Machine decision

The dedicated offline workflow creates `VALIDATION_GATES.json` and `l2-junit.xml` from executed checks and writes the exact validator commit/runtime-byte hash. Schema is `defistress-prephase02-offline-v1.1` for the repaired report, not a change to historical source schemas. **Do not propose final technical acceptance until final-head CI succeeds and both artifacts are inspected.** Any L1/L2 FAIL or unexplained BLOCKED stops acceptance; source missing is BLOCKED, never silently green. The two declared scientific limitations stay explicit. The gates remain fixed regardless of test results:

- `GATE_A=BLOCKED_BACKEND_INDEPENDENCE`
- `GATE_B=PASS_REGISTERED_CORE_SCOPE` (previously accepted; not revalidated by this task)
- `PHASE02_AUTHORIZATION=NOT_AUTHORIZED`

**Commander decision requested:** accept offline guard implementation if CI passes, then issue a **separate and explicitly scoped** GO/NO-GO for any Phase02 design or code task. Do not treat Issue #35's PASS as engine authorization.

**Repair delivery target, subject to final CI/artifact readback:** `V2_PR36_REPAIR_READY_FOR_COMMANDER_REVIEW — GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED`.
