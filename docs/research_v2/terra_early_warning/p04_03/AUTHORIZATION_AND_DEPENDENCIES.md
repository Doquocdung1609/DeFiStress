# P04-03-S authorization and reuse map

The human user explicitly requested execution of both supplied masterprompts in this chat on 29 October 2026 (Asia/Bangkok). Commander grant `V2_P04_03_S_SYNTHETIC_WARNING_IMPLEMENTATION_AUTHORIZED` activates the bounded implementation. Collaborator grant `V2_COLLABORATOR_CONTINUATION_AND_SCOPED_ENGINEERING_AUTHORIZED` authorizes the separate technical reviews. The Commander grant supersedes the older grant-pending wording retained in Issue56; this does not assert that Work has accepted the implementation. The exact input-document SHA256 values are recorded in EVIDENCE.json. No permissions are inferred from an Issue title.

Repository: Doquocdung1609/DeFiStress. Refreshed integration base is `c51d4d06d8b560a149e32ade922f8ed62da1a589`, not the local legacy `master` checkout. Branch: `research/terra-v2-p04-03-synthetic-warning-models`. Authenticated GitHub connector login: `Trunghai05`, matching configured Git author; no previous developer's worktree was accessed. A managed worktree reuses the existing authorized clone. A clean worktree was materialized with Git-LF bytes before edits so pinned historical checksums are not rewritten by CRLF conversion.

| Accepted dependency | Reuse / adapter | Scientific boundary |
|---|---|---|
| P02-01 canonical serializer and typed errors | Reuse `canonical_json_bytes`, explicit numeric strings and `TypeContractError`; new warning hash domains | No Ethereum `AssetId` imported to represent Terra |
| P02-02 saved state adapter | Regression dependency only | No saved Aave portfolio enters warning computation |
| P04-01 registry, PIT manifest, audit | Read-only source-readiness metadata and byte checks | All 14 historical records remain blocked; 0 approved fields |
| P04-02 contracts | Reuse `TemporalObservation`, `TerraChainId`, `AssetUnit`, `DatasetVintage`, `AdmissionPolicy`, UTC and missingness types unchanged | Synthetic eligibility does not grant historical admission |
| P04-02 temporal primitives | Reuse `latest_eligible_vintage`, `admissible_at`, `completed_interval_time`, `derived_availability`, ordering checks | Accepted linear ancestry, no published-retraction fallback and unknown-clock rejection preserved |
| New grid adapter | Explicit consecutive completed hourly slots, per-model required participation; pass each vintage group through accepted selector | No dropping a missing current slot in favor of an older value; no daily sample inflation |
| Accepted terminating-decimal mean | Preserve unchanged; negative regression retained | New package uses its separately versioned reduced-rational arithmetic, including nonterminating results |
| Terra V1 signals/results and `sim/terra/early_warning_v2.py` | Methodological audit references only, no runtime imports | Frozen V1 negative OOS conclusion and historical results preserved; old feature renormalization is not reused |
| Network / Aave stress indicators, PR55 valuation types | Unavailable as Terra dependencies | Distinct chain, sources and use classes; no propagation, Monte Carlo or historical scoring |
| PR53 source evidence and Issue54 acquisition proposal | Review/read-only specification inputs | No new source acquisition; no assumed publication time, USD parity or executable depth |

Only new files beneath `defistress_v2/terra_warning/`, `tests/v2/terra_warning/`, and this `p04_03/` folder belong to this PR. PR55 valuation, PR57 runner pinning and PR53 evidence retain separate review dispositions. Work-owned program control, PIT, V1, datasets, existing workflows and accepted contracts are untouched. There is no shared writer.

The package contains pure functions and immutable records only. No historical reader, fitting API, evaluation pipeline, RPC, live alert, order, withdrawal, UI or investor position exists. Reference fixtures use an artificial 2030 clock and explicitly synthetic provenance. Hour-start observations must declare `[start,start+1h)` bars; the grid closes at the latest whole hour at/before the information cutoff. Publication and availability plus any declared additional delay must independently permit admission.

`GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED`

`TERRA_POINT_IN_TIME_ELIGIBILITY_BLOCKED — HISTORICAL_BACKTEST_NOT_AUTHORIZED`
