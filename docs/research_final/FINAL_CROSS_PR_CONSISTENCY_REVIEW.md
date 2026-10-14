# Final Cross-PR Consistency & Merge Readiness Review

**Recommendation:** `CROSS_PR_READY_WITH_LIMITATIONS`

This review verifies the final numerical-evidence/literature linkage. It does not merge or retarget any pull request, change Draft state, grant `SCIENTIFIC_CONTENT_LOCK`, or validate scholarly DOI/content work beyond the locators supplied by P2.

## 1. Exact reviewed state

Verified from GitHub and fetched Git objects on 2026-10-14:

| Component | Reviewed HEAD | GitHub state | Role |
|---|---|---|---|
| Integration baseline | `9842c4f2c35adb8b4ec906e1bc76afa825d197c7` | branch | Frozen v3 source |
| Oracle PR #11 | `3011ba5e8cd23ee697c36d0aec6d047d8d58f653` | Draft/Open; mergeable | numerical dependency |
| Integration PR #12 | `a5d3d73dc037ec4c3a90449b3ccce37331b10597` | Draft/Open; mergeable | 13-claim scientific Addendum and pre-merge audit |
| Literature PR #9 | `1e25b713d0ecb83e56a9160691d2320f633c95a7` | Draft/Open; mergeable | 35 scholarly claims and 12 evidence aliases |

The P2 HEAD in the execution request, `f523f7369011b5ed5b8bd881785bc44f40d1c9bd`, was superseded by one targeted documentation commit, `1e25b713d0ecb83e56a9160691d2320f633c95a7`. The delta changes five P2-owned files and aligns them to PR #12 without changing scholarly or numerical findings.

No Commander comment newer than the approved integration/P2 reconciliation instructions was found. Work's latest handoff is PR #9 comment `6172258584`.

## 2. Cross-PR claim and alias coverage

The P2 crosswalk was parsed directly from its final Git blob, then joined against the Frozen v3 result registry and the PR #12 claim/result/table registries.

| Check | Result |
|---|---:|
| Scholarly source records | 30/30 unique (`S01`–`S30`) |
| Scholarly claims | 35/35 unique (`C01`–`C35`) |
| P2 evidence aliases | 12/12 unique (`E01`–`E12`) |
| Integration scientific claims available | 13 |
| Resolvable Frozen + Integration result IDs | 73 |
| Resolvable table/figure IDs | 17 |
| Artifact locator instances | 96 |
| Locator content read/hash checked | 94 |
| Explicitly preserved unread large-CSV locators | 2 |
| Broken commit, path, result, claim, alias or table references | 0 |

The two claim namespaces correctly remain separate: 35 P2 scholarly claims are not expected to map 1:1 onto 13 Integration claims. Every populated P2 `integration_claim_ids`, `model_result_ids`, evidence alias and table/figure locator resolves in its own namespace. Conceptual claims explicitly marked `NOT_APPLICABLE` are not forced to invent numerical result IDs.

Fourteen scholarly claims link to numerical result IDs. Their registry tiers resolve as seven simulation-only, two model-computed counterfactual, two observed, two derived, and one mixed observed/simulated claim. The P2 wording preserves those boundaries: observed snapshot/history facts are not promoted to causal transmission, while simulation and counterfactual results are not presented as empirical frequencies.

The two unread P2 locators are:

- `oracle_transmission_diagnostic_v1/borrower_level_evidence.csv`;
- `scientific_integration_v1/eligible_vs_executed_audit.csv`.

P2 labels both `SOURCE_NOT_VERIFIED_IN_THIS_SESSION`. This is not a numerical blocker because Codex independently read and audited the complete 32,688-row Integration CSV and the underlying Oracle data in the pre-merge audit. P2 does not falsely claim that Work performed that raw-cell audit.

## 3. Scientific content consistency

### RQ1 — conditional cascade

P2 now limits Wave 2 and Severe frequency to the declared valuation policy and simulation scope. It preserves:

- deterministic selected cases A/B/C weak/C moderate: `4/0/0/0` depth-2 cases;
- deliberately selected MC paths: `10/0/0/2`;
- Severe `280/10,000` depth ≥2 only under Policy A;
- zero observed depth ≥3 in the reported paths.

The ten diagnostic paths are explicitly non-random A-depth-2 selections and are not used as a population-frequency estimator. No policy-independent threshold or Ethereum crisis probability is claimed.

### RQ2 — liquidity versus HF feedback

P2 separates DEX forced-sale absorption and price impact from valuation-policy transmission into borrower HF. The 90% and 95% liquidity haircuts remain labeled unobserved counterfactual tail assumptions. Lower liquidity is not described as sufficient by itself to create additional liquidations.

### RQ3 — eligible versus executed

The crosswalk, narrative and terminology consistently distinguish portfolio HF eligibility, planner evaluation, route eligibility and positive-debt execution:

| Policy | Newly eligible | Attempted | Executed Wave 2 | Route-ineligible/skipped |
|---|---:|---:|---:|---:|
| A | 35 | 35 | 14 | 21 |
| B | 0 | 0 | 0 | 0 |
| C weak | 6 | 6 | 0 | 6 |
| C moderate | 11 | 11 | 2 | 9 |

All 36 skipped newly eligible borrower-case instances are described as outside the modeled WETH-collateral/USDC-debt route because they have no modeled USDC debt. P2 does not attribute these skips to gas, profitability, capital or capacity.

### RQ4 — arbitrage

P2 preserves the distinction between immediate sale impact and post-arbitrage residual spread. Tick traversal updates active liquidity, but `arbitrage_toward` remains a price-repositioning abstraction rather than a funded executable swap or Mainnet-fork validation.

### RQ5 — stablecoin valuation

USDC token quantity and USD-equivalent value are kept separate. The evidence supports a modeled USDC debt-valuation channel, not a complete stablecoin liquidity, redemption or settlement model.

### RQ6 — risk parameters

LTV, liquidation threshold and liquidation bonus remain distinct mechanisms. Scenario-LT unliquidated debt is not reverted to the superseded recorded-LT semantics.

### Historical and extension claims

- Historical evidence remains 28 Pool events, 27 Graph-matched events and Graph-event tiers `1/2/23/1` for verified direct route / same-transaction co-occurrence / same-block / time-window association.
- The direct receipt route and co-occurrences are not promoted to a causal historical liquidation-price-liquidation chain.
- `modeled bad debt` and the composite tail statistic are not described as realized financial loss or market expected shortfall.
- Terra's negative cutoff-safe/out-of-sample warning is retained.

## 4. Provenance gate

The current full integration source object is:

`c113fc1ec6dd98ffcc31241c1dbd1a93b20aa193`

The formerly expanded `c113fc190ed9...` object does not exist. It appears in P2 only as an explicitly superseded historical pointer and is absent from active source, claim, alias and registry locator fields.

`INT_T01_ELIGIBLE_VS_EXECUTED` resolves through PR #12's `table_figure_registry.json` to the summary and detail CSV, with population `18 × 4 × 454`, units `instances` and `USDC token quantity`, and tier `MODEL_COMPUTED_COUNTERFACTUAL`.

Independent Git-object checks found all 96 locator commit/path pairs present. For all 94 locators marked `READ_CONTENT`, both the declared Git blob object and SHA-256 of LF Git-blob bytes match.

Key Git-blob SHA-256 values:

| Artifact | LF Git-blob SHA-256 |
|---|---|
| Canonical snapshot | `76dae833c5b1a6e620cf116e332f1f47c53454a1f3530a02fefacd800cb3b329` |
| Frozen v3 manifest | `d31660ba134656c2882d95cc26545bd6aba9bf79ad59bd7d88e9d7a8ae0d1168` |
| Oracle Diagnostic manifest | `213a58b5856a52b7d200b1a537475bb3f5ba10d6b4a28c9b7235738950e334c9` |
| Scientific Integration manifest | `a36f761a1bd4135a50ab95de2f1fba2f7c2a867b3378bb878ea15aef289f2f60` |
| Final P2 crosswalk | `818c606235335a268da7cf27d0ab77391cd0e7ed57bf25a301d28bd5c9b1895d` |

P2 correctly labels these as Git LF-byte hashes and does not equate them with legacy Windows CRLF checkout hashes. The canonical, Frozen and Oracle artifacts were not modified by either the P2 final delta or this review.

## 5. Merge readiness — no merge performed

`git merge-tree --write-tree` completed without conflicts at the reviewed heads:

| Proposed dependency step | Exit | Synthetic tree |
|---|---:|---|
| Integration baseline + PR #11 | 0 | `0becd31d854f3a74a09f9ab1a567273ab54b27a8` |
| PR #11 + PR #12 | 0 | `43fc47655ff29f0b6a69ed57a0abab87fd988b8e` |
| PR #12 + final P2 PR #9 | 0 | `0656cb10cec727a15fa4a330abe6b5c1450a4d48` |

PR #12 contributes 20 paths relative to PR #11. PR #9 contributes seven P2 documentation paths relative to its branch point. Their changed-path intersection is empty. There are no duplicate documentation paths or content conflicts between PR #12 and PR #9.

The dependency order remains:

1. merge PR #11 into `feat/terra-model-v2`;
2. retarget/review and merge PR #12 after PR #11;
3. merge PR #9 after numerical evidence integration.

This is a readiness assessment, not authorization. All three PRs remain Draft/Open. GitHub reports no commit statuses and no pull-request workflow runs for the three reviewed heads; therefore no CI PASS is claimed.

## 6. Remaining limitations and blockers

### Material blockers

None found within the reviewed numerical/literature integration scope.

### Disclosed limitations

- A/B/C are counterfactual valuation policies; none is validated as the historical Aave/Chainlink oracle.
- Mainnet-fork liquidation and funded post-shock arbitrage validation remain unavailable.
- The ten selected MC paths are not a probability sample; Severe `280/10,000` is model- and Policy-A-conditional.
- The route model is WETH collateral/USDC debt while portfolio HF can include other assets.
- Extreme liquidity haircuts are counterfactual; one snapshot/pool and representative agents limit external generalization.
- Historical association tiers do not identify price causality or endogenous historical contagion.
- Terra forecasting and multilayer-network conclusions retain their published negative/aggregation limitations.
- Scholarly source/DOI verification remains Work's responsibility; this review verifies the data/evidence linkage only.
- GitHub CI is absent at the reviewed heads.

## 7. Commander recommendation

`CROSS_PR_READY_WITH_LIMITATIONS`

The final P2 delta is present, all active cross-PR locators resolve, and the scientific wording matches the locked numerical evidence. The former `AWAITING_WORK_FINAL_DELTA` condition is therefore cleared. Commander may now evaluate the documented merge order and any later `SCIENTIFIC_CONTENT_LOCK_WITH_LIMITATIONS`; this review does not grant that lock.
