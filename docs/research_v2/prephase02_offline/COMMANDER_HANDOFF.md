# Issue #35 — Commander handoff

**Authorized scope:** L1 offline evidence integrity and L2 pure synthetic data-contract checks. **Branch:** `research/v2-prephase02-offline-contracts`, starting at `2e0ec142c475f8d1362f90c4ca8d2f0718e41f77`. [Draft PR #36](https://github.com/Doquocdung1609/DeFiStress/pull/36). No merge authorized.

## What is tested

- `validate_offline.py` reads pinned Phase01-B sample registration, both preserved gzip evidence manifests, checks each saved file's byte length, SHA-256, uncompressed digest where declared, Ethereum chain/three block-hash identities, two pool fee tiers and USDC/WETH decimals. The script writes a machine-readable `VALIDATION_GATES.json` from actual execution; it never requests RPC data.
- `tests/test_prephase02_offline.py` uses synthetic negative/positive controls to exercise pure guard functions. It is not a model engine, economic simulator, borrower state recreation or new empirical data.
- `OFFLINE_EVIDENCE_MANIFEST.json` pins provenance and declared coverage boundaries. **24 borrower-block pairs, 67 reserves/account, 6 pool-block tick bands and 6 oracle traces** remain source-declared metrics, not generalized coverage claims; validating historic raw value correctness beyond digests requires original collection methods and cannot be extrapolated from counts.

## Non-replayable / residual gaps

Alchemy's saved `VERIFIED_CI_EVIDENCE.json` has run/summary/hash metadata but not all raw returned Alchemy field values: **NOT_REPLAYABLE_FROM_PERSISTED_SUMMARY**. Field agreement 174/174 was established by prior CI and is not independently recomputed here. The originating artifact may expire. dRPC and Alchemy backend identities remain **UNVERIFIED**. L1 may attest local file integrity; it is not scientific archive-independence proof. A correct synthetic test demonstrates guard behavior, not observed Mainnet evidence.

## Machine decision

The [dedicated CI run](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39281363424) creates `VALIDATION_GATES.json` and JUnit data from executed checks. **Do not mark L1/L2 PASS until those artifacts are inspected.** Any check `FAIL` must stop handoff; source missing is `BLOCKED`, never silently green. The gates remain fixed regardless of test results:

- `GATE_A=BLOCKED_BACKEND_INDEPENDENCE`
- `GATE_B=PASS_REGISTERED_CORE_SCOPE` (previously accepted; not revalidated by this task)
- `PHASE02_AUTHORIZATION=NOT_AUTHORIZED`

**Commander decision requested:** accept offline guard implementation if CI passes, then issue a **separate and explicitly scoped** GO/NO-GO for any Phase02 design or code task. Do not treat Issue #35's PASS as engine authorization.

**Status awaiting CI verification:** `V2_PREPHASE02_OFFLINE_VALIDATION_READY_FOR_COMMANDER_REVIEW — GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED`.
