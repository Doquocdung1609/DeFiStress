# PR #9 Mergeability Recovery Report

**Date:** 2026-10-14 (Asia/Bangkok)  
**Scope:** Git integration and scientific-provenance verification only  
**Decision recommendation:** `PR9_READY_FOR_CONTROLLED_MERGE`  
**Scientific Content Lock:** not granted by this report

## 1. Verified GitHub state

- Integration branch: `feat/terra-model-v2` at `df63fee50e39afd545294039b80a79d39379e394`.
- PR #11 is merged as `c72e9733b64ee33bfdf877cc8d6d3fd854fcce44`.
- PR #12 is merged as `df63fee50e39afd545294039b80a79d39379e394`.
- PR #9 original head: `1e25b713d0ecb83e56a9160691d2320f633c95a7`.
- PR #9 base is `feat/terra-model-v2`; it remains Draft/Open and was not merged.
- Before recovery, the GitHub connector reported `mergeable=false`, with no commit statuses and no workflow runs for either the original P2 head or integration head.
- The public unauthenticated REST endpoint could not independently expose the private repository's branch-protection/ruleset configuration. Therefore branch protection is recorded as `NOT_INDEPENDENTLY_QUERYABLE`, not as absent.

The latest Commander merge-hold comment was read before any branch mutation. No later P2 commit or competing recovery was present.

## 2. Independent merge diagnostic

Commands executed from a freshly fetched repository:

```text
git merge-base origin/feat/terra-model-v2 origin/research/p2-verified-literature-20261013
git rev-list --left-right --count origin/feat/terra-model-v2...origin/research/p2-verified-literature-20261013
git merge-tree --write-tree origin/feat/terra-model-v2 origin/research/p2-verified-literature-20261013
git diff --name-status origin/feat/terra-model-v2...origin/research/p2-verified-literature-20261013
```

Results:

- Merge base: `423bcfd4ebf910ef73b94d9deaf7cf746d8ed71c`.
- Divergence before recovery: integration ahead 23 commits; P2 ahead 5 commits.
- `git merge-tree --write-tree` exit code: `0`.
- Synthetic merge tree: `165b0413cc84b23ab2f2e5ad882e7cbff7755df4`.
- Actual conflict paths: none.
- The triple-dot PR diff contained exactly the seven P2 documentation paths.

Classification: **CASE A — merge clean**. The earlier normalized `mergeable=false` was not evidence of a textual or scientific conflict.

## 3. Safe recovery action

Recovery was performed in a separate temporary worktree. The integration branch was merged into the P2 line with a normal two-parent merge commit:

```text
git merge --no-ff origin/feat/terra-model-v2 -m "Merge feat/terra-model-v2 into P2 literature branch"
```

Merge commit: `7f8d77fc40c3c400f4f64a3146844360c252a044`  
Parents: `1e25b713d0ecb83e56a9160691d2320f633c95a7`, `df63fee50e39afd545294039b80a79d39379e394`

The remote P2 head was fetched and compared immediately before push. It still equaled the expected original head, so the merge commit was pushed by ordinary fast-forward update. No rebase, force push, reset, PR merge, draft-state change, or branch-protection bypass was performed.

After this push, GitHub reported:

- PR #9 head: `7f8d77fc40c3c400f4f64a3146844360c252a044`.
- Base head: `df63fee50e39afd545294039b80a79d39379e394`.
- `mergeable=true`.
- Draft/Open, not merged.
- Seven changed paths, all P2 documentation.
- No commit statuses and no workflow runs.

This demonstrates that branch synchronization, not a content-conflict resolution, recovered GitHub mergeability.

## 4. Scientific preservation

The seven P2 blobs were compared before and after the merge. All seven Git blob IDs are byte-identical:

| Path | Git blob ID | Result |
|---|---|---|
| `APA_REFERENCES_VERIFIED.md` | `c76d7cf482565615a92fb17b888a392e4f8fd9cc` | MATCH |
| `LITERATURE_VERIFIED.md` | `6ebe0a11e915e942a422d02a0cc5b1d53b51ff3e` | MATCH |
| `P2_CLAIM_EVIDENCE_CROSSWALK.json` | `932c25f633dee7bdb8cfcf9e6e2473b50f7c4ab3` | MATCH |
| `P2_ORACLE_RECONCILIATION.md` | `2bc140f47ea463a9394858ec8937a808d18eccd7` | MATCH |
| `P2_VERSION_RECONCILIATION.md` | `323958c95e8bb28b3fe66289332ba1f0f3ac69df` | MATCH |
| `REFERENCE_EVIDENCE_MATRIX.md` | `504ea91b046e6612c2840c6a434e740ce917b29f` | MATCH |
| `TERMINOLOGY_VI.md` | `2ca1e29495e6183dfefaf8939e59e6c4eba574fb` | MATCH |

Locked tree objects in the recovered branch exactly match the integration head:

| Locked area | Tree ID | Result |
|---|---|---|
| Frozen v3 | `0e48dfdc408d04d484e5432e7f4e6137b940ce78` | MATCH |
| Oracle Diagnostic v1 | `455d9a6a67b525e921bda249eb57e17bc6d8a4c5` | MATCH |
| Scientific Integration v1 | `25cba400a383a9576864acd2ed23967d05316443` | MATCH |
| Scientific Pre-Merge Audit v1 | `cc0537c534eba307fd5bbb9b697974adc3968b35` | MATCH |

The canonical block-26045352 snapshot blob remains `18234390e54f353ab7fd7c85ad0a86b46c34937b`; its standard Windows-checkout SHA-256 remains `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99`.

## 5. P2 integrity and numerical consistency

Independent parsing of the crosswalk and linked artifacts produced:

- 30/30 scholarly source records.
- 35/35 unique scholarly claims.
- 12/12 unique evidence aliases.
- Six research questions.
- 92 glossary terms.
- U01–U08 all present.
- 96/96 locator instances resolve to an existing commit/path and match the declared Git blob.
- `INT_T01_ELIGIBLE_VS_EXECUTED` resolves in the integration table registry.

The 72-row eligible/executed summary remains:

| Policy | Newly eligible | Executed Wave 2 | Skipped newly eligible |
|---|---:|---:|---:|
| A — adverse pass-through | 35 | 14 | 21 |
| B — reference-only | 0 | 0 | 0 |
| C weak | 6 | 0 | 6 |
| C moderate | 11 | 2 | 9 |

Across 32,688 borrower-policy-case rows, all 36 newly eligible but non-executed instances resolve to `NO_MODELLED_USDC_DEBT`, have zero modeled post-Wave-1 USDC debt, and are unavailable on the modeled WETH/USDC liquidation route. No scientific values or claims were changed.

The Policy-A-only interpretation of Severe 280/10,000, the selected-path denominator limitation, modeled-bad-debt wording, historical 28/27 event evidence tiers, non-causal historical wording, and Terra negative findings remain inherited unchanged from the locked evidence chain.

## 6. Tests and hash semantics

Actual checks:

- Crosswalk/count/locator validator: PASS; 30 sources, 35 claims, 12 aliases, 96/96 locators and blob IDs.
- Standard project checkout targeted pytest: **19 passed**:
  `tests/test_frozen_v3.py`, `tests/test_oracle_diagnostic_artifacts.py`, `tests/test_scientific_integration_v1.py`, `tests/test_scientific_premerge_audit_v1.py`.
- Merge-tree before recovery: exit `0`; after recovery, integration is an ancestor of P2 and the branch is six commits ahead / zero behind (five P2 commits plus the merge commit).
- PR triple-dot diff check: no recovery-induced conflict or content change in the seven P2 files.

A fresh worktree run produced 17 passes and two hash-test failures because four text artifacts were checked out with LF bytes while their manifests declare Windows CRLF byte hashes. The standard project checkout passed all 19 tests. Git blob/tree comparisons independently proved content preservation. This is reported as an existing checkout-portability limitation; no locked artifact was rewritten merely to normalize line endings.

No GitHub CI pass is claimed: GitHub exposed no status contexts or workflow runs for the reviewed heads.

## 7. Remaining conditions and recommendation

No content conflict, provenance mismatch, invalid locator, or material scientific blocker was found. The remaining controls are procedural:

1. PR #9 is still Draft and must only be moved forward by Commander.
2. Branch-protection/ruleset details were not independently queryable through the available authenticated connector; repository policy must still be respected by the GitHub merge operation.
3. Existing disclosed model, historical-causality, large-CSV-read and line-ending/hash-domain limitations remain in force.

Recommendation: **`PR9_READY_FOR_CONTROLLED_MERGE`**. This report does not merge PR #9 and does not grant `SCIENTIFIC_CONTENT_LOCK`.
