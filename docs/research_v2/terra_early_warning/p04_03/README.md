# Synthetic Terra warning models

P04-03-S implements B0 never-alert, B1 UST peg stress/persistence, B2 LUNA loss/trailing risk summary and B3 transparent composite. All computations are synthetic demonstrations. No pre-collapse alert, lead time, historical predictive accuracy or feasible historical exit has been demonstrated here.

The authoritative toy arithmetic is [Issue56](https://github.com/Doquocdung1609/DeFiStress/issues/56), captured in [ISSUE56_SNAPSHOT.md](ISSUE56_SNAPSHOT.md). With explicitly declared matching quote units, reference `p0=1`, peg downside `d=max(0,1-pUST/p0)`, and LUNA downside `l=max(0,1-pCurrent/pPrevious)`, composite `c=(min(1,d/(1/50))+min(1,l/(1/5)))/2`.

| Model | Score | WATCH inclusive | HIGH inclusive | Required default support |
|---|---|---|---|---|
| B0 | 0 on complete common support | Never | Never | 1 UST bar, 2 LUNA bars |
| B1 | d | 1/200 | 1/100 | 1 UST bar |
| B2 | l | 1/20 | 1/10 | 2 LUNA bars |
| B3 | c | 1/2 | 3/4 | 1 UST bar, 2 LUNA bars |

These are fixed toy thresholds, not historically calibrated rules, probabilities or investor protection levels. A different positive reference price must use the same declared quote/unit and enters the configuration hash. No implicit USDT=USD conversion exists. Nonpositive prices fail closed, including a zero previous LUNA price.

`peg_persistence` (default1, maximum16) requires consecutive completed hourly slots and uses their minimum downside: every bar must meet the peg threshold. `luna_return_window` (default1, maximum16) needs n+1 consecutive bars. It exposes the exact mean signed simple return and population variance of those n returns; B2's thresholded score remains the most recent downside loss. No square-root approximation or fitted volatility threshold is introduced. B3 uses the peg persistence score and most recent LUNA loss with fixed half-weights. There is no partial-feature weight renormalization.

All streams are bounded immutable tuples (maximum512 observations each). Ratios use reduced integer numerator/positive denominator, a12000-bit size bound, and integer comparisons. Arithmetic and hashes do not depend on ambient Decimal precision. The accepted PIT terminating-decimal helper is unchanged; its rejection of a nonterminating mean is tested separately.

`evaluate(model_id, inputs, context, config)` freezes decision, information-cutoff and issued UTC clocks, model/config/profile identity and hashes, required/available observations, raw source/vintage references, selected revision ancestry and missing/stale/rejected reasons. Admission uses the information cutoff, even if decision/issue occurs later. Missing required support yields `ABSTAIN`, no numeric score and no partial signals. Malformed identity, units, ordering, revision chain or non-synthetic origin raises a typed error before scoring. A caller's historical `ELIGIBLE` label is not an accepted input.

Observed input records and derived warning records have separate types. Output carries `SYNTHETIC_MODEL_WARNING_NOT_NATIVE_OBSERVATION`, `SYNTHETIC_CONTROLS_ONLY`, model version, configuration/profile hashes, selected-input hash, exact features and score contributions. Its canonical output hash is separate from the PIT input hash domain. Hashes are integrity/identity evidence, not cryptographic proof that a caller's synthetic source is historically real.

Only selected causal evidence and its ancestry enter the output. Unused future values/revisions do not change a past decision/hash. Changed selected source bytes or ancestry change lineage even if price/score stays equal. Published retractions do not restore an older value. Per-stream age and delay policies are explicit. Actual source staleness is measured by accepted PIT rules; no model code rewrites those semantics.

B1/B2 can operate independently on their declared participation. A future comparison must intersect all required masks (including B0/B3), report common support plus each method's separate coverage, and retain abstentions. There is no performance-comparison evaluator in this package.

## Reproduction

From the implementation worktree, with the project's Python3.12 environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/v2/terra_warning
.\.venv\Scripts\python.exe -m ruff check defistress_v2/terra_warning tests/v2/terra_warning
.\.venv\Scripts\python.exe -m mypy --strict defistress_v2
```

See [CONTROL_MATRIX.json](CONTROL_MATRIX.json), [EVIDENCE.json](EVIDENCE.json), [HISTORICAL_READINESS.md](HISTORICAL_READINESS.md), [P04_04_PROTOCOL_PROPOSED.md](P04_04_PROTOCOL_PROPOSED.md), [P04_05_EXIT_BLUEPRINT_PROPOSED.md](P04_05_EXIT_BLUEPRINT_PROPOSED.md) and [CONTINUATION_REVIEW.md](CONTINUATION_REVIEW.md). Example fixture/output JSON is labeled synthetic, includes source/config/profile hashes and cannot be used as historical evidence. M09/M10 evaluator semantics remain deferred.

Rollback is a reviewed revert of these new warning/test/document files only. No migration or data rewrite is needed. Keep the PR Draft for independent Work acceptance; local QA does not authorize a governed merge.
