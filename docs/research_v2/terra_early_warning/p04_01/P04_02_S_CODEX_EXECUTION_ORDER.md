# P04-02-S — executable Codex order

**READY_FOR_CODEX_EXECUTION — NOT_DISPATCHED.** Parent Issue49, bounded coding Issue50. Authority `V2_TERRA_EARLY_WARNING_HISTORICAL_VALIDATION_PROGRAM_AUTHORIZED` permits pure offline data audit and synthetic engineering. No callable Codex launcher is exposed; an Issue is not a running task.

## Exact inputs and ownership

Functional source anchor **9207ead7db3acf1332b34cebcd19981c2f7bd9cc**, P02-01/02 accepted; P02-03-S Issue45 is independent. Read the exact P04-01 commit and final integration/CI pin in Issue50's latest execution comment before coding. Its `P04_01_DATASET_REGISTRY.json` supplies35verified files, sizes and raw Git-byte SHA256/GitblobSHA1. The registry/report/PIT manifest have explicit scoped statuses; zero fields are cleared as historical predictive inputs. Read the actual byte auditor and20tests, no model imports.

Branch `research/terra-v2-p04-02-pit-contracts`; one Draft PR to `feat/terra-model-v2`. Codex owns proposed `defistress_v2/terra_pit/`, `tests/v2/terra_pit/`, `docs/research_v2/terra_early_warning/p04_02/` and isolated `v2-terra-pit-contracts.yml`. Work owns p04_01 docs/auditor/tests and Phase03–05 design. No shared writer; no edits to `defistress_v2/valuation/`, P02 constructors/guards or frozen artifacts. Reuse compatible pure identity/hash/unit concepts after reading them; Terra `columbus-5` must not be coerced into an EVM numeric chain ID. Proposed new paths/records below are not existing API signatures.

## Scope

Implement immutable observation, time interval, availability/vintage, asset/base/unit, source/verification, missingness and transformation-lineage records; explicit reasoned admission result. Bound bytes/rows/depth and aggregate pack sizes before parsing. Saved source inputs may be read only for byte/schema/count/clock/metadata audit. Missing publication/vintage proof in those historical records stays BLOCKED. No data acquisition/RPC/secrets or fallback source.

Implement pure temporal primitives with **synthetic fixtures only**: admissible-at(t), completed interval, latest eligible vintage, derived availability bound, trailing-window/warm-up checks, split-overlap/purge checks and deterministic hashes. A valid synthetic control may PASS admission without promoting any historical field. No warning/risk model, threshold fitting, label/onset computation, historical feature generation, historical portfolio calculation, temporal backtest, exit simulation or new metric. Schema placeholders for risk output must be explicitly NOT_IMPLEMENTED, never fabricated risk_score0.

## Synthetic reference controls — independently specified, NOT_RUN here

| ID | Fixture | Required result |
|---|---|---|
| P04-S01 | Observation10:00, available10:05, decision10:02/10:05UTC | First blocked, second eligible under explicit0additional-delay toy policy |
| P04-S02 | Entire hourly aggregate[00:00,01:00), event00:30 | Not available at00:00; earliest01:00 plus declared processing/release delay |
| P04-S03 | Vintage1available10:00/value1; revisionavailable12:00/value9; as-of11:00 | Use vintage1; later revision cannot rewrite past feature |
| P04-S04 | Unknown publication/availability, observation in2022, acquisition2026 | Historical PIT admission BLOCKED; acquisition is not backdated availability |
| P04-S05 | Observed flow0 vs missing/null before coverage |0 retained only with completeness evidence; missing blocked, never0/NORMAL |
| P04-S06 | Derived dependency times10:01and10:03, processing2minutes | Earliest derived availability10:05; no latest-input timestamp self-assignment shortcut |
| P04-S07 | Synthetic values1,2,4 at successive completed times; trailing2at secondtime | Exact mean1.5; change future4→999 leaves prior result/hash unchanged |
| P04-S08 | Duplicate/out-of-order timestamps, naive timezone, bool as integer timestamp | Reject/quarantine with precise reason; no ambiguous silent sort/last-row overwrite |
| P04-S09 | Source quoteUST/USDT claimedUST/USD without conversion | Reject unit/source promotion; no assumed peg or executable quote |
| P04-S10 | Daily source carried hourly and unknown staleness; exhausted warm-up | Preserve source age/frequency; abstain when policy unresolved, no independent hourly sample claim |
| P04-S11 | Split labels overlap boundary by forecast horizon; transform fitted on heldout | Detect purge requirement/fit-lineage leak; do not fit/evaluate a real model |
| P04-S12 | Tamper/duplicateJSON/CSVwidth/oversize/traversal/symlink/unsupported schema | FAIL/quarantine with nonzero failure report; source-byte hash distinct from content hash |

Add immutable input/lineage, process/replay stability and no-network/import-side-effect controls. Synthetic source classes can represent source semantics; origin and expected results remain SYNTHETIC. Test expected outputs must not call the implementation under test. Missing-data/native errors as expected negatives can PASS a software test while capability remains BLOCKED.

## Local-first and CI

Retain the Work20audit cases and run the35record source audit against pinned Git LF bytes; do not auto-normalize CRLF tampering into a PASS. Run new synthetic tests/JUnit, accepted97contracts/70adapter/80offline regressions, Ruff, strict mypy over new modules, exact source-byte wheel inclusion and protected-tree diff before push. Use accepted installed tool/environment provenance; no ad hoc dependency relaxation or test deselection. Full repository CI runs automatically and is distinct from a research campaign.

Dedicated+repository CI must succeed on the actual final HEAD. Record workflow vs checkout SHA/tree, Python/OS/package versions, fixture/expected/profile/source hashes, requirements implemented/remaining, counts PASS/FAIL/SKIP, JUnit/report/checksum artifacts and protected-source preservation. Upload failure evidence with reasons; code must not crash before its failure report is issued. Read back actual artifacts and SHA256 lists. Source-declared old outcomes, new audit evidence and independently rerun validation are separate.

Keep all nine Terra acceptance statuses separate. P04-03 model package, P04-04 historical backtest and P04-05 exit study require an approved protocol and applicable permission. Historical fields do not become eligible because synthetic tests or ingestion succeed. No GateA/B change, false pre-event alert, investor-protection guarantee, V1 edit, predictor or new empirical claim.

## Delivery / STOP

Provide one reviewable Draft PR with exact base/head/allowed paths, actual commands/results/CI/artifacts, measured coverage/quarantines, untouched V1/Phase01/02, remaining source-clock issues and reviewed-revert rollback. Work reviews actual code independently of Codex authorship; Codex does not self-merge or open a further runtime package through this order.

STOP on historical feature/model/backtest/exit needs, invalid source/clock/unit/hash mapping, unreviewed protocol choice, source acquisition/cost, scientific contradiction or ownership conflict. Do not alter frozen evidence to resolve a failure. Target `P04_02_S_PIT_CONTRACTS_READY_FOR_TECHNICAL_REVIEW`, not `TERRA_V2_EARLY_WARNING_RESEARCH_DEMONSTRATOR` or historical warning validation.
