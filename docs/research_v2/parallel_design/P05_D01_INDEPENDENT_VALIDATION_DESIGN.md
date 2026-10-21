# P05-D01 — Independent comparator and reproducibility protocol

**DESIGN_ONLY — PROPOSED — NO_VALIDATION_CAMPAIGN_RUN**

Authority: `V2_P02_03_SYNTHETIC_OFFLINE_VALUATION_AUTHORIZED`, parallel design only. Work owns this protocol; an independently assigned comparator author/reviewer is not presumed to exist. Base `38e4b7b2081c9056e98319194898535a3f9cfe8c`. No new numerical result, external replication or scientific release is claimed.

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED**

## Sources and decisions

| Source at base | Decision | Limitation |
|---|---|---|
| `docs/research_v2/phase00/V2_RESEARCH_UPGRADE_BLUEPRINT.md`, U08/Phase05 | Seal comparator/input/tolerance and holdout contracts; publish failed/unavailable outcomes | Independent validation is a future delivery, not ingestion CI |
| `docs/research_v2/gate_b_protocol/GATE_A_VS_B_PROTOCOL.md` | Keep infrastructure independence distinct from deterministic state agreement | Repeated reads or different brand URLs cannot close Gate A |
| `docs/research_v2/phase02_architecture/TEST_SPECIFICATIONS.md` | Track specification clauses separately from actual test instances and empirical evidence | A green aggregate test count does not prove every specification or native profile |
| `docs/research_v2/program_control/PROGRAM_STATE.json` | Retain exact branch/merge-ref/tree/run/artifact identity and scoped limitations | P02-01/02 technical acceptance is not HF/execution/historical scientific acceptance |

V1 scientific lock `3f6e5302483681209e2408531eb5a15389f9fded`, V1 tag and accepted claims/access levels remain immutable. A future V2 claim registry needs its own namespace and review; no V1 result ID is repurposed for a different result.

## Five independent questions

| Dimension | Minimum proposed evidence | What it cannot establish alone |
|---|---|---|
| Byte identity | Complete input/output bytes, sizes, source commit, raw/decoded hashes, retained requests where authorized | Historical correctness, source independence or economic validity |
| Software correctness | Negative/boundary controls, independent expectations, types/units/state invariants | Native protocol equivalence or full specification coverage |
| Comparator independence | Separately authored algorithm using a declared specification; no import/call of builder routine for expected results | Infrastructure independence or external reviewer independence |
| Historical/native agreement | Effective chain/block/contract/profile, source/round/time, complete use-specific data and authorized native/receipt comparator | Broad market representativeness or causal Mainnet identification |
| Research validity | Sealed sample/controls/information set, failed cases and denominators, justified identification/OOS protocol | Scientific-final approval or universal predictive performance |

An author reviewing their own repair is self-review. Work reviewing independent Codex authorship is a separate technical review but not automatically external peer review. Record actual reviewer identity/role and shared code/dependencies; do not infer independence from a different file or CI job.

## Proposed comparator contract

Each comparison case has a predeclared ID, use class SYNTHETIC_ECONOMIC / HISTORICAL_OBSERVATION / NATIVE_EXECUTION / FORECAST_EVALUATION, exact source/profile version, required fields/capabilities, model mode, expectation provenance, units/scales/rounding, registered tolerance and mismatch taxonomy. P02-03-S may implement only its own synthetic controls under its current narrow grant; this protocol grants no additional code or campaign.

For exact integer/rational reference profiles require exact equality at the declared quantization stages. A native comparison needs a separately verified operation order/rounding/profile; a native tolerance is not derived from a synthetic match. Any numerical tolerance must be specified in explicit absolute unit and/or relative rule, zero handling and aggregation before observing residuals. Unknown tolerance/profile is BLOCKED, not a tuned threshold. Do not count tests that compute expected output using the implementation being tested as an independent comparator.

For each field record input/expected/observed hashes, signed residual if defined, unit, tolerance version, diagnostic and PASS/FAIL/BLOCKED. Exact identity/hash/chain/time mismatches cannot be averaged away. Distinguish software error, invalid source, access/availability gap and economically valid negative outcome. Quarantine affected descendants while retaining the original record. If mismatches reveal a scientific contradiction, stop the affected claim and present the evidence to Commander; do not edit locked sources.

## Reproducibility package and hash domains

Proposed run manifest: input manifests and complete bytes, code/tree/commit, environment/package locks with installed verification, platform and numeric profile, deterministic seeds/PRNG/order/clock, parameters/controls, source selection/missingness, output/journal hashes, commands, actual results and scope/limitations. A virtual environment lock is not installed-environment validation. No claim of all-platform reproducibility follows from one Windows or Linux run.

Track separately raw compressed bytes, decoded bytes, canonical typed content, Git blob SHA-1, Git LF bytes SHA-256 and any Windows CRLF checkout representation. A semantic content hash is not an artifact hash. Preserve the exact conversion rule and provenance instead of claiming different byte hashes are the same SHA. Any native receipt record includes execution mode, effective fork block/profile, funding injection assumptions, actual transaction/event/state locators and gas/nonce outcomes; no such receipt is created here.

CI evidence must pair workflow head SHA with actual checkout SHA and tree; a PR merge-ref can differ from the branch commit. A parent CI run does not validate a later merge commit. Read JUnit, check failures/errors/skips, digest/size/CRC and embedded checksum lists when present; absence of an embedded list is disclosed. Retain complete permitted request/response bytes, manifests, reports and sanitizer policy before Actions retention expires. Metadata-only historical summaries remain non-replayable; do not manufacture the missing values.

## Holdouts, reporting and failure disposition

Future sample/market/regime selection, exclusion/missing rules, controls, horizons and denominators are sealed before tuning/comparison. Overlapping snapshots or nested prefixes are not independent samples; targeted Wave2 paths are selected audits, not market-probability estimators. Cross-market comparisons require compatible mechanism/unit/information-set mapping or separate strata. Terra forecast evaluation uses P04-D01 and its own sealed dataset; Aave agreement is not transferred to Terra.

Proposed report maps `requirement/version → implemented clauses → test IDs → fixture origin/hash → run/checkout → result/artifact → limitation → claim allowed`. A case expected to reject can PASS its software test while the historical capability remains BLOCKED. Report coverage/exclusions over all registered candidates and performance over the explicitly eligible subset. No silently dropped failures, skipped native cases promoted to PASS, post-hoc tolerance change or “zero” for missing values. Test counts from overlapping suites are never added as independent replications.

## Future test specifications — NOT_RUN_DESIGN_ONLY

| ID | Deliberate input / fault | Expected outcome | Evidence needed |
|---|---|---|---|
| P05-DT01 | One-byte input tamper or wrong hash domain | FAIL identity; quarantine downstream claim | Complete raw/decoded bytes and expected-domain registry |
| P05-DT02 | Comparator imports/calls builder for expected values | Not independent; reject independence claim | Dependency/code review and separately authored reference |
| P05-DT03 | Different native rounding/profile or wrong decimals | Field-level FAIL/BLOCKED; no tolerance widening | Predeclared profile, unit and boundary vectors |
| P05-DT04 | Workflow SHA differs from checkout/merge tree | Preserve both IDs; no exact-merge PASS without actual evidence | Git objects, workflow/JUnit/artifact linkage |
| P05-DT05 | Missing native receipt, raw provider values or heartbeat | BLOCKED affected use; technical integrity may remain PASS | Capability/availability matrix and scope-specific report |
| P05-DT06 | Holdout/tolerance changed after result inspection | Seal violation; new exploratory version, prior record retained | Versioned registrations and access/history log |
| P05-DT07 | No cascade/no trade/forecast miss in valid case | Report negative outcome; no retuning/deselection for green result | Registered candidate denominator and all-case ledger |
| P05-DT08 | Same inputs/seed with worker/time/serialization variation | Same contract gives same canonical state/journal, or locate first divergence | Numeric/environment/ordering profile and deterministic trace |

## Acceptance, ownership and STOP

P05-D01 design review can proceed now. Actual comparator implementation, historical/OOS campaigns and scientific reporting need their own grants, accepted upstream outputs and source/profile prerequisites. Proposed ownership: Work protocol/claim boundaries; separately assigned comparator code; Codex source implementation; named independent reviewer if appointed. Do not share writers or represent roles as staffed before assignment.

Design acceptance requires explicit units, comparison profiles, independence dimensions, retention plan, failure dispositions and no ungranted runtime. Unknowns remain: future native profile/receipt availability, independent comparator/reviewer staffing, data/vintage rights/retention and sealed sample/tolerances. Gate A attestation and Alchemy replay gaps stay open. No provider reprobe, simulation, empirical test, tag/release or Scientific Final V2 approval follows. Commander alone resolves conflicting scientific evidence and grants final publication/release. Rollback uses reviewed reverts with evidence retained.
