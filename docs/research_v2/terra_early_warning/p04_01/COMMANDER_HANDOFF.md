# Mandatory Terra Early Warning — P04-01 handoff

**P04_01_DATA_AUDITED_WITH_PIT_BLOCKERS — P04_02_S_READY_FOR_CODEX_EXECUTION.** Authority `V2_TERRA_EARLY_WARNING_HISTORICAL_VALIDATION_PROGRAM_AUTHORIZED`. Parent Issue49; next coding Issue50. Starting integration9207ead7db3acf1332b34cebcd19981c2f7bd9cc; immutable scientific lock3f6e5302483681209e2408531eb5a15389f9fded and V1tag preserved. No P02 ownership or accepted claims changed.

## What was done

-304tracked candidate paths /272unique blobs inventoried;35files fetched in full, pinned Gitblob/size/SHA256 verified;269metadata-only/bytesUNVERIFIED. EightParquet schemas inspected locally. No complete98MBZIP or large event/balance-pack audit is claimed.
-Measured1,776extended hourly rows,312legacy Mayrows and14core-column availability/missingness profiles. All ten requested data groups dispositioned; prices/supplies/Anchor partially present, liquidity/book/context gaps explicit.
-External verification of publisher v4metadata/date/license, vendor time/version docs and candidate public exchange-archive format. No new market data acquired, no liveRPC/node query, no literature re-review or source-access upgrade.
-Read actual existing V1 model/leakage code and saved audit; kept negative early-warning finding. Identified10new-PIT-admission/design constraints in P04_01_DATA_AUDIT.md, including hour-bucket closure, missing historical availability, aggregated price execution limits and label-clock discrepancies.
-Produced proposed RQ-T1…T6/event/split/horizon/baseline/threshold/metric/leakage/holdout/exit protocol. It is **NOT_APPROVED** and has not been executed. May2022 remains an outcome-known retrospective case.
-Small read-only stdlib auditor emits structured FAIL evidence;20negative/boundary tests PASS locally,35input checks PASS. Ruff with repository configuration and strict mypy(1newscript) PASS. An initial lint run inherited scratch policy; reran against actual repository pyproject, fixed formatting/semicolon issues, rechecked without weakening tests. Local Python3.12.14/Linux;pytest8.4.2/Ruff0.17.1/mypy1.20.2; schema-only inspection usedpyarrow19.0.1 in scratch, no dependency changes. CI and actual artifacts are recorded at the PR's exact final HEAD, not inferred from this static report.

## Nine separate gates

| Gate | Current evidence/status |
|---|---|
| DATA_AUDITED | SCOPED_PASS:35bytes/CSVrecords,8schemas,304metadata paths; not all source packs |
| POINT_IN_TIME_ELIGIBLE | BLOCKED;0predictive fields cleared; observation time alone insufficient |
| MODEL_IMPLEMENTED | V2_NOT_IMPLEMENTED; V1 research code exists and is only reviewed, not rerun |
| BACKTEST_PROTOCOL_APPROVED | NOT_APPROVED; concrete proposal available |
| HISTORICAL_BACKTEST_EXECUTED | NOT_EXECUTED in this program |
| PRE_EVENT_ALERT_DEMONSTRATED | NOT_DEMONSTRATED in this program; V1negative/late-initial-warning evidence retained |
| FALSE_ALARM_RISK_EVALUATED | NOT_EVALUATED in this program; no normal-control denominator manufactured |
| EXIT_FEASIBILITY_EVALUATED | NOT_EXECUTED / NOT_VERIFIABLE with current depth/access evidence |
| INDEPENDENTLY_REVIEWED | NOT_REVIEWED; Work self-audit is not external independent validation |

## Package registry / next decisions

| Package | Owner and permitted next step | Gate before empirical use |
|---|---|---|
| P04-01 | Work data/source audit complete within declared scope; preserve registry and resolve clock/unit/source issues incrementally | Historical availability/interval/vintage admission, not mere file presence |
| P04-02-S / Issue50 | Codex saved-data integrity/schema/admission and synthetic temporal primitives; [execution order](P04_02_S_CODEX_EXECUTION_ORDER.md); READY, NOT_DISPATCHED | Inputs35pinnedbytes verified; no historical feature/model run; actual-code/CI review required |
| P04-03 | Work comparison strategy; Codex implementation after specific package definition | Pre-event training support and approved model/threshold/split/feature protocol; positive result not required |
| P04-04 | Approved historical temporal backtest/evaluation later | PIT-admitted inputs, frozen protocol/labels/decisions and explicit applicable run authorization |
| P04-05 | Separate liquidity-aware exit study later | Valid warning, historical execution/depth/access/fee/latency data and approved protocol/run scope; otherwise NOT_VERIFIABLE |
| P04-06 | Named independent comparator/reviewer, robustness and scientific reporting later | Actual result lineage, sealed control/holdout evidence, full negative/unavailable cases; no generalization from one crisis |

Priority source-remediation order: establish source-specific interval/publication/vintage evidence for price-only candidates; resolve event-flow availability and supply-unit metadata; register normal/adverse controls; obtain pre-event intraday support only in a separately scoped source campaign if needed. Never fix data scarcity by fabricating hourly observations, volume-as-depth or zero flows outside coverage. Paid source access requires Commander decision; no purchase or acquisition is initiated here.

P02-03-S Issue45 continues independently at its existing scope; no callable Codex launcher is connected, so Work cannot honestly claim either coding task has started. An actual Codex executor can take Issue50 and the pinned handoff, on separate branch/files. Phase03–05 designPR47 is reference only and is not promoted to an empirical authorization by this program.

## Demonstrator contract (future, not a delivered forecast)

The final professor-facing demonstrator will show source provenance and as-of input mask, observed signals versus derived warning, sealed chronology and baselines, event-level lead/miss and normal-period false alarms, leakage/vintage robustness, conditional exit results or NOT_VERIFIABLE, reproduction steps and failure cases. It must execute at least one genuinely audited historical Terra case after protocol approval, with off-event controls when eligible. This task provides the audited foundation and bounded engineering order; the complete demonstrator target is **NOT_YET_ACHIEVED**, not silently replaced by a mock alert UI.

No new forecasting or financial-performance number is published. V1 remains preserved; audit findings are future-PIT admission constraints, not retroactive edits to accepted scientific results. Review/approval of this audit does not approve backtest/exit execution or guarantee an early warning. Rollback via a reviewed PR reverting only the new Terra program files, retaining audit history.

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED**. AaveGateA does not prevent Terra design/audit; its PASS would not validate Terra vintages or forecast performance either.
