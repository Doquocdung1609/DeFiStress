# Phase 01-B — Alchemy–dRPC cross-check: final evidence

**Decision: STATE AGREEMENT PASS IN REGISTERED CORE SCOPE; BACKEND INDEPENDENCE UNVERIFIED.**

This is a durable, sanitized index to the original artifact from [GitHub Actions run 39223539524](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39223539524), source commit `f63cee66dce12ea432188b1bd65d934443afbdac`. The exact origin artifact is `ALCHEMY_CROSSCHECK_RESULT.json` (artifact ID `12173300304`), 4,002 bytes, SHA-256 `8aa33a26b4d950ff92661f1fd794ee84211cb4a8668ad0514b050e1fa7267e43`. The GitHub artifact ZIP as downloaded has SHA-256 `82a006751255af18b377312cb20a046a88e4b9adb11cd33fded086b41bab5c32`. The stable index is [VERIFIED_CI_EVIDENCE.json](VERIFIED_CI_EVIDENCE.json); values and hashes can be independently cross-checked with the original ZIP while retained.

The script read the **same preregistered Ethereum Mainnet blocks** from Alchemy, twice each, and compared each read against the previously saved dRPC Phase 01-B core reference—not a newly collected contemporaneous dRPC read. Results:

| Block | Alchemy pass 1 | Alchemy pass 2 | Repeatability |
|---|---|---|---|
| 26045352 | 29/29 agreeing | 29/29 agreeing | PASS |
| 26038152 | 29/29 agreeing | 29/29 agreeing | PASS |
| 26030952 | 29/29 agreeing | 29/29 agreeing | PASS |

**Aggregate:** 174/174 per-pass field comparisons agree; 0 mismatches, 0 missing fields, 0 additional fields; 87 unique block-field pairs each read twice. These are *not* 174 statistically independent observations.

## Exact scope and correction history

- Alchemy RPC: HTTPS endpoint supplied solely by GitHub Actions secret `ALCHEMY_ETH_RPC_URL`; secret, URL, raw HTTP records and error bodies are not included in committed evidence.
- Core `eth_call` requests use the registered EIP-1898 block-hash selector, the same contract addresses and ABIs as Phase 01-B.
- Earlier run `39221909247` retrieved complete, repeatable state but flagged six `slot0()` values due to a Python Web3 tuple vs persisted JSON list representation difference. The fix canonicalizes decoded ABI values to JSON and retains strict comparison; the successful run `39223539524` shows agreement across all core fields.
- The cross-check covers **core state fields** only. It does not redo full tick reconstruction, historic oracle-round proofs, borrower analysis or stress simulations.

## Acceptance gates

| Gate | Status |
|---|---|
| Historical Alchemy archive data access | PASS (three registered blocks) |
| Field-level agreement with saved dRPC core reference | PASS (174/174 comparisons) |
| Two-pass Alchemy repeatability | PASS (three blocks) |
| Distinct serving-backend provenance | **UNVERIFIED** |
| Independent archive scientific gate | **BLOCKED** |
| Phase 02 authorized | **NO** |

Alchemy and dRPC are different access services, but field agreement, endpoint names and client versions are **not sufficient evidence** that they rely on independent archival backends. Obtaining independently verifiable request-level serving-backend provenance (or an alternative explicitly approved scientific acceptance criterion) remains outstanding.

This documentation is an append-only evidence supplement. V1, the release tag, Phase 01-A/01-B research results, original data and frozen scientific claims have not been altered. PR #30 remains Draft pending Commander review; no Phase 02 work is included.
