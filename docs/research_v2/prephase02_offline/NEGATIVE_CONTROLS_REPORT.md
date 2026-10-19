# Synthetic negative controls — execution and interpretation

Authorization: [Issue #35](https://github.com/Doquocdung1609/DeFiStress/issues/35). All fixtures in `tests/test_prephase02_offline.py` are **SYNTHETIC contract-validator inputs**, never historical observations or claims about executed liquidations.

**Targeted repair:** source HEAD before repair `c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb`; [failed offline run39281653358](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39281653358) crashed in L1 with `KeyError: 'id'` and did not run L2. Earlier run39281363424 is historical, not final acceptance evidence. Final-head CI/artifact URLs are recorded in the PR #36 repair handoff comment.

**Local execution after repair:** pytest8.4.2, Ruff0.17.1, Python3.12: **80 PASS /0 FAIL /0 ERROR /0 SKIP**, including35 original tests and45 added regressions. Actual `l2-junit.xml` was read back, counters reconciled with test cases, and its SHA256 attached to generated `VALIDATION_GATES.json`; final CI counts must be read separately, not inferred from this local run.

| Control families | Expected outcome |
|---|---|
| Wrong chain, block/hash, pool address, token order | Validator rejects (False) |
| USDC 6 / WETH 18 decimals, negative/fractional integers | Validator rejects |
| ABI tuple vs JSON list with identical values | Validator accepts |
| Tuple changed value, missing/extra/null-vs-zero/swapped fields | Validator detects |
| Duplicate or out-of-band ticks, wrong bitmap initialization, gross/net invalid | Validator rejects |
| Active liquidity greater than total, negative liquidity | Validator rejects |
| Oracle source/round/future timestamp/DEX spot substitution | Validator rejects |
| Borrower reserve identity, missing liabilities, duplicate reserve, invalid HF shape | Validator rejects |
| Mutated artifact bytes, changed JSON state | SHA-256 differs |
| Known correct controls | Validator accepts |
| Missing/empty/non-string check ID, malformed status/scope/reason, invalid container and duplicate IDs | Explicit failed diagnostic; original malformed record not silently assigned fallback ID or passed |
| File producer's typed ID; malformed manifest row/gzip/bytes/missing input | Valid report record with FAIL/BLOCKED and reason; no unhandled aggregation KeyError |
| P500 registered42-character address versus old41-character truncated literal | Exact registration identity accepts; truncated address rejects |
| Internal producer exception, malformed source/report serialization, denied report write | FAIL report where output is writable; otherwise nonzero exit plus REPORT_WRITE_ERROR, never silent success |
| Missing/invalid/empty/inconsistent JUnit, skipped tests, nonzero pytest exit | L2 BLOCKED/FAIL as appropriate; cannot overwrite L1 FAIL or change scientific gates |

The original failure joined registration checks carrying `id` with `file_record()` records carrying only `path`. The repair uses one explicit record contract (`id/scope/status/reason`, optional path), validates records before aggregation and rejects malformed records. Only the two registered scientific limitations may use LIMITATION scope; arbitrary missing files or digest errors cannot be excluded from L1 by relabeling.

**Deliberate limitations:** the tick tests check supplied tick-band entries, not independent exhaustive proof that all bitmap words from historical RPC were observed. Borrower fixture checks missing debt keys, not economic HF consistency with a full reconstructed portfolio. Oracle fixture checks source/timestamp constraints, not Chainlink answered-in-round history or production event processing. These are L2 confidence tests only; no V2 stress model was built or executed.

CI `l2-junit.xml` records case names/outcomes and assertion failures. Input fixtures and expected dispositions are in the exact-commit test source/table above; the XML does not contain every complete fixture payload. The tests distinguish failure of a negative control (a test FAIL) from intentional rejection of a malformed synthetic fixture (test PASS). Workflow finalization reads actual JUnit/counters/pytest outcome to populate `L2_CONTRACTS` and `L2_TEST_RESULTS`; `if: always()` retains L2 and report diagnostics when L1 fails. No continue-on-error, deselection or weakened assertions are used.

Mandatory governance: `GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED`.
