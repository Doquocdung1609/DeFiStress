# P3-G0 Exhibit Reconciliation — Technical Review

Status: `P3_G0_TECHNICAL_REWORK_REQUIRED`

Scientific lock: `3f6e5302483681209e2408531eb5a15389f9fded`

Work PR #15 reviewed HEAD: `e26e2d5a21c6ac78bd4db7be345409b5c7690a80`
Codex PR #14 input HEAD: `17b839528e58a622aa0554067b19823a8f33bda5`

## Verdict

All **25/25** Work manuscript tables/figures and **8/8** selected equations resolve to accepted claims, locked result/evidence IDs when applicable, and source objects at the scientific lock. No display is unsupported by the locked evidence. The evidence gate itself is not blocked.

Blueprint Lock is not yet ready because Work HEAD still lacks the single Commander-requested Work→Codex crosswalk, and E3.7 lists literature/background locators instead of the locked project implementation and numerical table as its primary provenance. These are targeted metadata repairs; they do not authorize or require a new simulation, interval, model change or scientific result.

## Counts and preservation

- Work plan: 14 tables, 11 figures, 8 equations.
- Codex inputs: 11 reusable templates, 15 audited formulas and 67 unchanged evidence-inventory records.
- Claim gate: 44 affirmative and 4 disallowed; no disallowed ID appears as an affirmative exhibit claim.
- Six RQs, Frozen, Oracle, Integration, P2 and Final Registry remain unchanged.
- No rendering, new simulation, retuning, new estimated finding, Chapter 1 prose or DOCX edit occurred.

## Exhibit crosswalk

| Work ID | Placement | Reproducibility class | Codex template(s) | Evidence status |
|---|---|---|---|---|
| T1.1 | Ch1 §1.3 | TEXTUAL_SYNTHESIS | DIRECT/NO TEMPLATE | SUPPORTED_BY_LOCKED_EVIDENCE |
| T2.1 | Ch2 §2.5 | TEXTUAL_SYNTHESIS | DIRECT/NO TEMPLATE | SUPPORTED_BY_LOCKED_EVIDENCE |
| F3.1 | Ch3 §3.1 | SCHEMATIC_FROM_LOCKED_MODEL_SPEC | P3X:SYSTEM_FEEDBACK_SCHEMATIC | SUPPORTED_BY_LOCKED_EVIDENCE |
| T3.1 | Ch3 §3.2 | TEXTUAL_SYNTHESIS | P3X:SYSTEM_FEEDBACK_SCHEMATIC, P3X:METRIC_SEMANTICS_GLOSSARY | SUPPORTED_BY_LOCKED_EVIDENCE |
| T3.2 | Ch3 §3.5 | RENDERABLE_FROM_LOCKED_ARTIFACT | P3X:ORACLE_POLICY_DEPTH2_COMPARISON, P3X:SEVERE_POLICY_A_MONTE_CARLO | SUPPORTED_BY_LOCKED_EVIDENCE |
| T3.3 | Ch3 §3.3 | TEXTUAL_SYNTHESIS | P3X:METRIC_SEMANTICS_GLOSSARY | SUPPORTED_BY_LOCKED_EVIDENCE |
| F4.1 | Ch4 §4.1 | SCHEMATIC_FROM_LOCKED_MODEL_SPEC | P3X:CANONICAL_SCOPE_PROVENANCE | SUPPORTED_BY_LOCKED_EVIDENCE |
| T4.1 | Ch4 §4.2 | RENDERABLE_FROM_LOCKED_ARTIFACT | P3X:CANONICAL_SCOPE_PROVENANCE | SUPPORTED_BY_LOCKED_EVIDENCE |
| T4.2 | Ch4 §4.3 | TEXTUAL_SYNTHESIS | P3X:METRIC_SEMANTICS_GLOSSARY | SUPPORTED_BY_LOCKED_EVIDENCE |
| F5.1 | Ch5 §5.1 | RENDERABLE_FROM_LOCKED_ARTIFACT | P3X:ORACLE_POLICY_DEPTH2_COMPARISON | SUPPORTED_BY_LOCKED_EVIDENCE |
| T5.1 | Ch5 §5.2 | RENDERABLE_FROM_LOCKED_ARTIFACT | P3X:ORACLE_POLICY_DEPTH2_COMPARISON | SUPPORTED_BY_LOCKED_EVIDENCE |
| T5.2 | Ch5 §5.3 | RENDERABLE_FROM_LOCKED_ARTIFACT | P3X:ELIGIBLE_VS_EXECUTED | SUPPORTED_BY_LOCKED_EVIDENCE |
| F5.2 | Ch5 §5.3 | NEEDS_DISPLAY_SPEC | P3X:ELIGIBLE_VS_EXECUTED | SUPPORTED_BY_LOCKED_EVIDENCE |
| F5.3 | Ch5 §5.2 | NEEDS_DISPLAY_SPEC | P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS, P3X:ORACLE_POLICY_DEPTH2_COMPARISON | SUPPORTED_BY_LOCKED_EVIDENCE |
| F5.4 | Ch5 §5.3 | RENDERABLE_FROM_LOCKED_ARTIFACT | DIRECT/NO TEMPLATE | SUPPORTED_BY_LOCKED_EVIDENCE |
| F5.5 | Ch5 §5.4 | RENDERABLE_FROM_LOCKED_ARTIFACT | P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS | SUPPORTED_BY_LOCKED_EVIDENCE |
| T5.3 | Ch5 §5.5 | RENDERABLE_FROM_LOCKED_ARTIFACT | DIRECT/NO TEMPLATE | SUPPORTED_BY_LOCKED_EVIDENCE |
| F5.6 | Ch5 §5.6 | NEEDS_DISPLAY_SPEC | P3X:RISK_PARAMETER_MECHANISMS | SUPPORTED_BY_LOCKED_EVIDENCE |
| F5.7 | Ch5 §5.7 | RENDERABLE_FROM_LOCKED_ARTIFACT | P3X:SEVERE_POLICY_A_MONTE_CARLO | SUPPORTED_BY_LOCKED_EVIDENCE |
| T6.1 | Ch6 §6.1 | RENDERABLE_FROM_LOCKED_ARTIFACT | P3X:HISTORICAL_EVIDENCE_TIERS | SUPPORTED_BY_LOCKED_EVIDENCE |
| F6.1 | Ch6 §6.2 | NEEDS_DISPLAY_SPEC | P3X:TERRA_NEGATIVE_EARLY_WARNING | SUPPORTED_BY_LOCKED_EVIDENCE |
| F6.2 | Ch6 §6.3 | SCHEMATIC_FROM_LOCKED_MODEL_SPEC | P3X:NETWORK_EXTENSION_BOUNDARY | SUPPORTED_BY_LOCKED_EVIDENCE |
| T6.2 | Ch6 §6.4 | TEXTUAL_SYNTHESIS | DIRECT/NO TEMPLATE | SUPPORTED_BY_LOCKED_EVIDENCE |
| T7.1 | Ch7 §7.1 | TEXTUAL_SYNTHESIS | DIRECT/NO TEMPLATE | SUPPORTED_BY_LOCKED_EVIDENCE |
| T7.2 | Ch7 §7.2 | TEXTUAL_SYNTHESIS | DIRECT/NO TEMPLATE | SUPPORTED_BY_LOCKED_EVIDENCE |

Classification totals: `RENDERABLE_FROM_LOCKED_ARTIFACT=10`, `SCHEMATIC_FROM_LOCKED_MODEL_SPEC=3`, `TEXTUAL_SYNTHESIS=8`, `NEEDS_DISPLAY_SPEC=4`, `UNSUPPORTED_BY_LOCKED_EVIDENCE=0`.

Four displays are classified `NEEDS_DISPLAY_SPEC`; T4.1 is directly renderable only if its optional near-threshold extension is omitted. These controls require no new evidence:

- **F5.2:** predeclare a deterministic, pseudonymized event selector and exact trace locator.
- **F5.3:** only 0% is the unmodified canonical pool; every positive haircut is a model counterfactual, with 90/95% extreme tails. Separate cell counts from USD/WETH.
- **F5.6:** facet USD capacity, USDC-token unliquidated debt and WETH seized; never share one y-axis.
- **F6.1:** keep zero HIGH-alert hours and −45-hour lead as distinct quantities/two panels.
- **T4.1:** omit optional near-threshold detail until a locked locator is named.

## Formula reconciliation

| Work formula | Codex audit mapping | Category | Compatibility |
|---|---|---|---|
| E3.1 | P3F01, P3F02 | PROTOCOL_SHAPED_PROJECT_IMPLEMENTATION | PASS_WITH_REQUIRED_LIMITATIONS |
| E3.2 | P3F05 | PROTOCOL_IDENTITY_IMPLEMENTED_BY_PROJECT | PASS_WITH_REQUIRED_LIMITATIONS |
| E3.3 | P3F06 | PROTOCOL_IDENTITY_IMPLEMENTED_PIECEWISE | PASS_WITH_REQUIRED_LIMITATIONS |
| E3.4 | P3F08 | PROJECT_SPECIFIC_HYPOTHETICAL_POLICY | PASS_WITH_REQUIRED_LIMITATIONS |
| E3.5 | P3F02 | PROJECT_STATE_CLASSIFICATION_DISPLAY_IDENTITY | PASS_WITH_REQUIRED_LIMITATIONS |
| E3.6 | P3F15 | DISPLAY_TRANSFORMATION_OF_LOCKED_RUNS | PASS_WITH_REQUIRED_LIMITATIONS |
| E3.7 | P3F15 | DISPLAY_TRANSFORMATION_LOCKED_VALUES_ONLY | PASS_WITH_REQUIRED_LIMITATIONS |
| E3.8 | P3F09 | ANALYTICAL_IDENTITY_INSIDE_MODEL | PASS_WITH_REQUIRED_LIMITATIONS |

The eight formulas are compatible with locked code/outputs when their recorded limitations are retained. E3.7 requires a provenance correction: the primary project locators are `sim/research/aave_suite.py:211`, `scripts/research/run_deep_cascade_study.py:353` and `frozen_v3/tables/rq1_monte_carlo.csv`. The NIST Agresti–Coull-titled page cannot be presented as direct verification of the Wilson implementation. No new confidence interval is permitted.

## Codex template disposition

| Codex template | Disposition | Work manuscript IDs |
|---|---|---|
| P3X:SYSTEM_FEEDBACK_SCHEMATIC | USED | F3.1, T3.1 |
| P3X:ORACLE_POLICY_DEPTH2_COMPARISON | USED | F5.1, F5.3, T3.2, T5.1 |
| P3X:ELIGIBLE_VS_EXECUTED | USED | F5.2, T5.2 |
| P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS | USED | F5.3, F5.5 |
| P3X:SEVERE_POLICY_A_MONTE_CARLO | USED | F5.7, T3.2 |
| P3X:HISTORICAL_EVIDENCE_TIERS | USED | T6.1 |
| P3X:TERRA_NEGATIVE_EARLY_WARNING | USED | F6.1 |
| P3X:NETWORK_EXTENSION_BOUNDARY | USED | F6.2 |
| P3X:RISK_PARAMETER_MECHANISMS | USED | F5.6 |
| P3X:CANONICAL_SCOPE_PROVENANCE | USED | F4.1, T4.1 |
| P3X:METRIC_SEMANTICS_GLOSSARY | USED | T3.1, T3.3, T4.2 |

All 11 Codex templates have a declared use. Work displays without a dedicated template are direct locked tables or textual syntheses, which is valid and does not create an orphan evidence requirement.

## Findings requiring Work delta

| Finding | Severity | Exact IDs | Minimum correction |
|---|---|---|---|
| G0-X01 | P1_METADATA | T1.1, T2.1, F3.1, T3.1, T3.2, T3.3, F4.1, T4.1, T4.2, F5.1, T5.1, T5.2, F5.2, F5.3, F5.4, F5.5, T5.3, F5.6, F5.7, T6.1, F6.1, F6.2, T6.2, T7.1, T7.2, E3.1, E3.2, E3.3, E3.4, E3.5, E3.6, E3.7, E3.8 | Work should mirror or explicitly adopt this validated crosswalk in its next delta; no scientific number or claim changes are required. |
| G0-X02 | P1_METADATA | E3.7 | Use sim/research/aave_suite.py:211, scripts/research/run_deep_cascade_study.py:353 and frozen_v3/tables/rq1_monte_carlo.csv as primary project locators; retain scholarship as background only. |
| G0-X03 | P2_DISPLAY_SPEC | F5.2, F5.3, F5.6, F6.1, T4.1 | Apply each row's required_display_controls during chapter evidence-pack specification. |

Ten Work source paths are outside the original 67-record Codex inventory, but all ten exist at `3f6e5302483681209e2408531eb5a15389f9fded` and their declared Git object IDs match. This is not an evidence failure: the 67-record inventory was the initial accepted-claim/rendering inventory, not an assertion that every later direct manuscript source already had a P3 evidence ID. This review leaves those 67 records unchanged and records the extra paths with independent Git-object and blob-SHA-256 verification.

## Required next gate

Work should publish a delta that either embeds or explicitly adopts the 25/25 and 8/8 mappings and corrects E3.7 provenance. Codex must then verify only that delta. Until then the recommendation is `P3_G0_TECHNICAL_REWORK_REQUIRED`; this is a provenance/metadata hold, not `P3_G0_BLOCKED_BY_EVIDENCE`.

Stop state: `AWAITING_WORK_FINAL_CROSSWALK_DELTA_AND_COMMANDER_BLUEPRINT_DECISION`. No Chapter 1 work is authorized.

Content SHA-256 (UTF-8, excluding this checksum line): `93aa56055f7d91d2663f31b74eab1aa8356cc5b0c0f208c2bac66eb8876a601c`
