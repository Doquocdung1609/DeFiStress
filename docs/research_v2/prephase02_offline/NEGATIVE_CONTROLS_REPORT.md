# Synthetic negative controls — execution and interpretation

Authorization: [Issue #35](https://github.com/Doquocdung1609/DeFiStress/issues/35). All fixtures in `tests/test_prephase02_offline.py` are **SYNTHETIC contract-validator inputs**, never historical observations or claims about executed liquidations.

**Actual execution evidence:** [offline CI run 39281363424](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39281363424) emits `l2-junit.xml` with one `test_id` parameter per adverse control. Final PASS/FAIL and counts must be read from that CI result, not inferred from these written expectations.

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

**Deliberate limitations:** the tick tests check supplied tick-band entries, not independent exhaustive proof that all bitmap words from historical RPC were observed. Borrower fixture checks missing debt keys, not economic HF consistency with a full reconstructed portfolio. Oracle fixture checks source/timestamp constraints, not Chainlink answered-in-round history or production event processing. These are L2 confidence tests only; no V2 stress model was built or executed.

CI `l2-junit.xml` is the machine-readable input/expected/observed test trace (assertion failures retained). The tests distinguish failure of a negative control (a test FAIL) from intentional rejection of a malformed synthetic fixture (test PASS).

Mandatory governance: `GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED`.
