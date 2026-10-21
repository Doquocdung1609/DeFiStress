# P04-D01 — Terra vintages, temporal splits and leakage controls

**DESIGN_ONLY — PROPOSED_PROTOCOL — SPLIT_SEAL_PENDING — ALL_TEST_SPECIFICATIONS_NOT_RUN**

Authority: `V2_P02_03_SYNTHETIC_OFFLINE_VALUATION_AUTHORIZED`, parallel design only. Work owns this file. Base `38e4b7b2081c9056e98319194898535a3f9cfe8c`; immutable V1 scientific lock `3f6e5302483681209e2408531eb5a15389f9fded`. No acquisition, feature computation, threshold selection, prediction, tuning, holdout evaluation or new statistic is performed.

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED**

## Source → decision → boundary

| Pinned source at the base unless stated | Design decision | Limit |
|---|---|---|
| `docs/research_v2/phase00/V2_RESEARCH_UPGRADE_BLUEPRINT.md`, U07/U08 | Separate point-in-time forecasting from conditional replay and retain negative findings | Existing `sim/terra/early_warning_v2.py` is V1 code, not proof that this new protocol has been implemented |
| `docs/research_v2/gate_b_protocol/PHASE02_DEPENDENCY_AND_RISK_MATRIX.md`, U07 | Terra has its own sources, vintages, splits and baselines | Aave/dRPC–Alchemy core agreement cannot validate Terra data or a forecasting claim |
| `docs/research_v2/program_control/PROGRAM_CONTROL.md`, Phase04 | Seal information sets, thresholds and outcome reporting before future evaluation | Current permission is design only; no predictor/run grant |
| V1 accepted registry at scientific lock: `data/processed/research_final/final_accepted_claims_v1/` | Preserve the accepted negative out-of-sample early-warning conclusion | Do not rename conditional replay as successful prediction of the initial depeg |

No new external source has been verified in this task. Candidate feature families below are requirements for a future availability audit, not claims that a complete point-in-time dataset exists. Dates, instruments, frequencies, horizons, thresholds and sample counts remain unsealed until that audit and Commander review; this is an explicit unresolved design dependency, not an executed preregistration.

## Proposed data/vintage contract

Each source row needs dataset/source ID, asset/market/chain identity, variable definition/unit, event/effective time, first-publication time, actual retrieval time, revision/vintage ID, raw-byte locator/hash, transformation lineage, origin/access level and missingness reason. A blockchain event time is not proof of provider publication/operational availability. Finality, ingestion delay, timezone, timestamp precision and candle close semantics must be named.

| Candidate family | Required semantic distinction | Fail-closed rule |
|---|---|---|
| UST/LUNA prices and executable depth | Venue/pair, quote currency, event vs completed candle, observed depth vs proxy | Missing historical depth is unavailable, not current depth or zero |
| Supply and mint/burn/redemption | Supply stock vs directional flow, token decimals and issuance event semantics | Do not derive future flow from final revised supply or label proxy as direct observation |
| Anchor deposits/withdrawals | Gross inflow/outflow vs net change, source coverage and denomination | Net balance decline is not automatically an observed withdrawal transaction total |
| Backing/reserves/liquidity proxies | Actual asset/liability basis, valuation time and proxy assumptions | No complete backing ratio or observed reserve claim without denominator/source evidence |

For a forecast issued at decision time `t`, admit a feature only if every dependency was available by `t`. Use the latest eligible vintage, not the final revision retrieved later. Retrieval today can support a retrospective point-in-time study only when the original publication/vintage is evidenced. Unknown availability is BLOCKED for forecast use; an explicitly conservative upper bound may be declared and evaluated later, never backdated. No automatic forward-fill, zero fill, interpolation across a missing period or future-fitted normalization. Any permitted imputation must be train-only, named, preregistered and carry missingness flags.

## Proposed temporal protocol and seal

1. First audit source/vintage coverage without inspecting future model performance. Define event labels independently from predictor outputs: onset/persistence/recovery, venue, deviation threshold, minimum duration and label revision policy. Threshold values are not chosen in this document.
2. Propose chronological train, calibration and terminal holdout intervals, with named eligible event and non-crisis windows. Hash and retain all proposed IDs, exclusion rules, maximum lookback/horizon, feature availability rules, baseline definitions and metric denominators. Commander scope approval and a recorded seal must precede fitting/evaluation. A random row split is not acceptable for overlapping temporal windows.
3. Fit transforms and model parameters on train only. Select any threshold on calibration only. Purge overlapping target horizons at boundaries and embargo according to the full feature/label dependence span; the exact interval requires the future feature/horizon specification. Keep validation and terminal holdout roles distinct.
4. Generate forecasts only from information available at each issue time. Freeze the forecast record before joining future labels. Conditional mechanism replay is a separate record namespace with explicit ex-post inputs and never enters forecast accuracy denominators.
5. Evaluate the sealed holdout once per registered model/version. Publish misses, late warnings, false alarms and unavailable cases. A changed threshold/feature after holdout inspection is a new exploratory version, not the original confirmatory score. One crisis cannot establish cross-event predictive generalization.

The seal record must contain dataset/vintage hashes, time cutoffs and timezone, event IDs, eligibility masks and reasons, model/config/transform hashes, threshold rule, horizons, control models, metrics and intended statistical procedure if any. No significance test, confidence interval or tuning campaign is authorized by this design.

## Baselines, denominators and admissible negative outcomes

Proposed baselines include a no-warning control and a simple price/deviation rule using the same eligible information and horizon. These are not yet fitted or run. A complex model must not receive later vintages, a longer history or a different eligible subset than its comparator without reporting a separate analysis. Variants sharing one implementation/data are not independent models or independent crises.

Store a forecast ledger with issue time, target horizon, availability mask, model version, score, threshold status and immutable input hash; store labels in a separate versioned ledger. Report event-level detection over all eligible events and coverage over the entire registered universe, observation-level classification over eligible labeled decisions, and false alarms over declared non-event time or alarm episodes. Define episode merging/cooldown and censored horizon rules before evaluation. Undefined precision/recall in zero-denominator cases is tagged UNDEFINED, not silently zero or perfect.

Proposed signed lead time is `event onset − first qualifying alarm issue time`, positive for earlier warning and negative for late warning. An alarm is evaluated against its declared horizon; an arbitrarily early alarm does not become a correct forecast merely because a crisis occurs eventually. A miss has no lead time and remains in the event denominator. All decisions excluded for missing inputs are counted in coverage; report performance conditional on availability alongside exclusions to prevent favorable-case selection.

## Test specifications — not run

| ID | Input / mutation | Expected | Failure / evidence |
|---|---|---|---|
| P04-DT01 | Event before `t`, release after `t` | Feature unavailable at forecast `t` | AVAILABILITY_LEAK / source clocks |
| P04-DT02 | Final revised vintage substituted | Reject; retain originally eligible vintage | VINTAGE_LEAK / immutable revision history |
| P04-DT03 | Incomplete candle, wrong timezone or precision | No future close; explicit aligned clock/uncertainty | CLOCK_LEAK / candle and publication contract |
| P04-DT04 | Train transform fitted on calibration/holdout | Reject fitted artifact lineage | FIT_LEAK / split and transform hashes |
| P04-DT05 | Overlapping label horizon across split | Purge/embargo per sealed dependence span | SPLIT_OVERLAP / interval registry |
| P04-DT06 | Missing flow/depth or proxy substituted | Quarantine or labeled approved proxy; no observed-zero promotion | SOURCE_PROMOTION / availability matrix |
| P04-DT07 | No alarms, all misses, late alarm, zero denominator | Complete counts, tagged undefined metric, signed lead semantics | OUTCOME_CENSORING / forecast-label ledger |
| P04-DT08 | Comparator sees earlier vintage or different mask | Same registered information set or separately labeled comparison | COMPARATOR_ASYMMETRY / eligibility hashes |
| P04-DT09 | Threshold changed after seal; replay mixed with forecast | Seal violation; new exploratory version; replay excluded from forecast scores | HOLDOUT_CONTAMINATION / audit history |

## Dependencies and next action

P04-D01 can proceed independently of Aave outcomes and P02-03-S coding. Before data acquisition/model implementation/evaluation, obtain a separate Terra-specific grant and verify source availability, event definition, complete split/horizon specification, costs/rights and storage policy. No source purchase or acquisition is initiated here. Proposed Codex namespace is separate from `defistress_v2/valuation/`; Work owns protocol and scientific decisions, future Codex owns an explicitly approved data/evaluation implementation. A methodologically valid miss or failure to outperform baselines is an acceptable economic result, not a reason to tune the holdout. Design acceptance is not forecast validation or Scientific Final V2.
