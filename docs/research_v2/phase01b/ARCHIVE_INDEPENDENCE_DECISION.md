# Archive independence decision

**V2_ARCHIVE_INDEPENDENCE_READY_FOR_COMMANDER_REVIEW**  
**Final scientific gate: BLOCKED — INDEPENDENT_ARCHIVE_VALIDATION_BLOCKED.**  
**Phase02 remains NOT AUTHORIZED.**

Input integration: `2f850411613ddb6607ea3232f5637fd798156f6f` (PR #28 merged). Commander scoped acceptance: [6262030996](https://github.com/Doquocdung1609/DeFiStress/pull/28#issuecomment-6262030996). Frozen V1 annotated tag object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`. Scientific sources, Phase01-A and accepted tick/oracle/borrower reconstructions are unchanged.

Collection source: `dd32f7c19b2c899d95c77d83f6fa19a4769ab535`; [bounded run 39217670638](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39217670638); initial request-plan source `84ab944e35cfef521290732b79d6cf27118340d3`. The initial workflow was rejected before any job/RPC due to an unquoted YAML scalar containing a colon; corrected before collection. JSON-list/ABI-tuple comparison normalization was also corrected before collection. No actual result or numerical threshold was adjusted.

## What was and was not compared

`INDEPENDENT_ARCHIVE_COMPARISON.json` is an exact byte copy of the collection result under `archive_independence/evidence/`. Expected/observed values, missing statuses, two passes, source/block identity, same-run pairwise comparisons and raw error reasons remain available. Each block has **29 registered labeled values**:4chain/block identity values and25contract-state/configuration values. `slot0()` is one labeled tuple compared in full, not7separately counted scalar values.

| Comparison scope | Expected distinct block-value points | Pass-indexed rows (2reads) | Actual value agreements | Actual mismatches | Missing rows |
|---|---:|---:|---:|---:|---:|
| Fresh dRPC against saved dRPC,3blocks | 87 | 174 | 174 | 0 | 0 |
| SubQuery against saved dRPC,3blocks | 87 | 174 | 0 | 0 | 174 |
| BlockReq against saved dRPC,3blocks | 87 | 174 | 0 | 0 | 174 |
| Two new candidates against same-run dRPC,3blocks each | 174 | 348 | 0 | 0 | 348 |

The saved-baseline and contemporaneous tables address the same attempted comparison points; **do not add them together**. No independent historical-state comparison completed. BlockReq's6raw chain-ID successes are visible in the HTTP entities; they do not complete the identity gate or count as historical-state agreement. There are **0 observed independent state mismatches**, because no independent state was returned; this is BLOCKED, not a zero-mismatch PASS.

The earlier Phase01-B union-key comparison reported30rows for incomplete providers because it also included an aggregate `aave_configuration` unavailability marker. The current expected-value table lists the29actual saved core values; no contract call/ABI/value or scientific result has been removed. The denominator difference is bookkeeping of an error marker, not new data coverage.

## Gate reasoning

- **Access:** SubQuery DNS transport failure; BlockReq public endpoint denies target headers and requests registered archive access. Neither candidate is eligible for historical state calls in this run.
- **Backend independence:** no request-level distinct-serving-backend attestation was established. dRPC selected headers include `drpc-core-free`; new candidate responses provide no verifiable independent node identity. Absence of evidence is not a finding that all providers are the same backend.
- **Numerical data:** reference observations are complete, repeatable and unchanged; no independent numeric comparison exists. Missing fields remain null/explicit BLOCKED.
- **Software:**7synthetic gate tests PASS, including tuple/list equality, null versus0, mismatch precedence, empty comparisons and two-read/independence prerequisites. They validate decision logic, **not backend independence**. The collector conservatively leaves independence UNVERIFIED; the human/tool review of selected headers and official source material does not supply evidence to promote it.

## Provenance and checks actually executed

Collection [run39217670638](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39217670638) **SUCCESS as an evidence-producing process**,7pytestPASS/0FAIL/0SKIP; Python3.12.10 and the existing hashed Windows dependency lock installed successfully. Initial invalid-workflow run39217501837 had0jobs and0RPC; its corrected successor is the data source above. Code-head repository CI39217670618 exposed an import-order lint issue in the new7-test file; the import order was corrected without changing test assertions, source observations or existing tests. Do not interpret green CI as gatePASS.

Artifact12169754856 ZIP SHA-256 `f63e7cc2ca0a64aa5feafc28d814db31c2eecef44cfe03ad326f345612e8138e` and ZIPCRC verified. All55original manifest entries were checked in full, including actual gzip bytes and uncompressed canonical JSON. All102captured HTTP response entities were decoded and their exact body SHA-256/size checked. SubQuery produced0HTTP entities; its bounded transport errors remain in the request journals. Response capture records request-body bytes, UTC start/end, status and selected routing headers. Captured bytes are HTTP response entity bytes after client decoding, **not TLS/chunk wire bytes** and not automatically proof of signed JSON-result verification.

`archive_independence/EVIDENCE_PROVENANCE.json` covers every preserved evidence file including post-collection JUnit and this result's byte-identical main copy. Generator/request-plan source is pinned to the collection commit; old Phase01-B source and evidence are untouched. LF JSON artifact bytes, CRLF checkouts, gzip bytes and decoded JSON have distinct hash domains. Final-head CI and exact final commit are reported in the PR handoff after commit, avoiding self-referential hashes.

Offline reproduction (no network):

```bash
python docs/research_v2/phase01b/archive_independence/verify_saved.py
python -m unittest discover -s tests -p test_archive_independence.py -v
```

A new authorized collection, using a new empty output directory, can reuse the preserved plan and pinned core methods; do not repeatedly run it against these blocked public endpoints. No simulation, stress, MonteCarlo, tick-range rebuild, oracle-round trace, borrower reconstruction, V1 modification, release/tag operation or Phase02 implementation was performed.

## Commander recommendation

Accept the targeted investigation and exact access requirements as a **BLOCKED return**, retain the mandatory gate, and obtain authorized archive access plus request-linked backend provenance before another comparison. A self-operated archive with independently authenticated chain data or an independently verified state-proof strategy could be proposed as a **separate** validation design; it has not been implemented, tested or approved here and does not satisfy this existing gate by renaming it. No Phase02 authorization is issued by Work.
