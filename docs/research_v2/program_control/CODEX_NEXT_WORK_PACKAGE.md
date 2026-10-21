# P02-03 — Oracle & valuation: executable handoff, authorization gated

**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED**

Status: **READY_FOR_CODEX_EXECUTION — P02-03-S ONLY**. Issue #45. Commander authorization **`V2_P02_03_SYNTHETIC_OFFLINE_VALUATION_AUTHORIZED`**, [scope/evidence](https://github.com/Doquocdung1609/DeFiStress/issues/45#issuecomment-6307535866), is effective after PR46 exact-merge CI passed. **AUTHORIZED_FOR_CODEX_EXECUTION; NOT_DISPATCHED**: Work has no callable Codex task launcher; an Issue/prompt is not a launched task. D is prepared; H/N and execution/empirical runtime remain BLOCKED.

## Codex execution order

Fetch repository and pin accepted integration **`38e4b7b2081c9056e98319194898535a3f9cfe8c`** (PR46). Read this entire handoff and Issue45 authorization before coding. Create `research/v2-p02-03-oracle-valuation-contracts` from that base or inspect and record a later accepted integration whose delta preserves these contracts/data. Implement only S against synthetic fixtures/explicit model assumptions; run local-first QA; push one Draft PR into `feat/terra-model-v2` with exact HEAD CI, JUnit/checksum/source evidence and limitations. Do not launch H/N or engine modules. Work owns program-control and parallel-design documents; Codex must not edit them. The latest dated authorization supersedes prior awaiting-grant statements retained in historical comments.

## 1. Exact accepted dependencies and ownership

P02-01 repaired source `59193efc6d4e8ae1ad3233187d8c0e6b8fd9bd43`; P02-02 repaired source `62105de4fd498164c50ce9c7f3df48f068fa9f53`, P02-02 merge `f06d19aa36e1b89d5714064d6262045eaf440062`; approved integration input **`38e4b7b2081c9056e98319194898535a3f9cfe8c`**. Read PR41/44 Work review, final CI/artifacts and program ledger. Fetch actual integration; inspect any movement and record a base without discarding accepted work. Never use superseded Codex 4b931e6… code. Scientific lock `3f6e5302483681209e2408531eb5a15389f9fded` and frozen V1 tag remain immutable.

Authorized planned branch `research/v2-p02-03-oracle-valuation-contracts`. Codex proposed ownership: `defistress_v2/contracts/valuation.py`, pure `defistress_v2/valuation/` modules, `tests/v2/test_valuation.py`, concise `docs/research_v2/p02_03/`, isolated dedicated workflow. Minimal new-symbol export edits to `defistress_v2/contracts/__init__.py` are allowed without changing accepted constructor/guard semantics. These new paths/APIs are PROPOSED, not existing code. Work owns program-control/scientific governance. No shared writer, no P02-01/02 semantic changes to force success. Report any incompatibility rather than silently widening a capability.

Read accepted `phase02_architecture/{DATA_AND_INTERFACE_CONTRACTS,ORACLE_LIQUIDATION_AMM_SPEC,TEST_SPECIFICATIONS}.md` at the merged input. These dated documents are designs; their old PR36 PENDING text is superseded only by the program acceptance ledger, not by rewriting architecture history. Read actual P02-01 units/evidence/guards and P02-02 snapshot/field-availability/provenance types.

V1 policy-control reference: `sim/oracle.py` at scientific lock, Git blob `2ac37f923a4cc35bef95968d353f0724bfdbd3a5`, particularly initial_valuation_price, next_valuation_price and intrawave_reporting_price. This is a counterfactual model control, never actual Aave/Chainlink behavior. Do not import/run the V1 engine or collector. The economic formulas below are the accepted architecture specification, not a universal Aave bytecode formula.

## 2. Scope / GO–NO-GO separation

| Slice | Current disposition | Authorized scope / further gates |
|---|---|---|
| P02-03-D / Work | GO, DESIGN ONLY | Source/interface mapping, tests/reference vectors, authorization proposal and review; no Python implementation/run |
| P02-03-S / Codex | AUTHORIZED_FOR_CODEX_EXECUTION | Pure immutable price/valuation contracts, synthetic economic-profile arithmetic, policy functions on synthetic completed observations, negative tests; no historical portfolio valuation or engine |
| P02-03-H | BLOCKED_AUTHORIZATION_AND_EVIDENCE | Historical price-set/portfolio valuation requires explicit use-class grant, source/availability/participating-set review, profile and comparator. Gate A remains unchanged; saved-byte PASS is not independent historical validation |
| P02-03-N | BLOCKED_AUTHORIZATION_AND_NATIVE_PROFILE | Bit-exact Aave HF/eMode/accrual/rounding requires effective implementation/bytecode/ABI and source/round/freshness profiles, independent vectors and separately authorized native validation |
| P02-04…07 / Phase03–05 runtime | NO-GO | No liquidator, swap, scheduler, propagation, predictor, historical stress or Monte Carlo permission follows |

S is now permitted only by the explicit Commander grant above, not by technical PASS alone. Keep Issue45 open during actual execution/review. No historical acquisition, portfolio valuation, calibration, replay or campaign is authorized. Historical source-class schemas and metadata negative controls use synthetic fixtures; never load saved historical portfolios into a new valuation computation. Economic negative outcomes remain valid test outcomes.

## 3. Proposed contracts and interface decisions

Keep three independent dimensions: transport/evidence SourceKind (e.g. SAVED_ARTIFACT), economic price class (HISTORICAL_AAVE_ORACLE_OBSERVATION / DEX_OBSERVATION / COUNTERFACTUAL_POLICY), and origin (OBSERVED / RECONSTRUCTED / SYNTHETIC / COUNTERFACTUAL). A saved artifact is not automatically an Aave oracle. Never retag a DEX price, upstream round, derived field or model policy as a historical native observation.

Proposed immutable records:

- PriceObservation: asset identity/decimals; explicit base currency identity/unit U; positive exact raw price per whole token; economic source class; source/config/adapter pointers; block/effective/available times and precision; native/upstream round availability separately; evidence/lineage and verification level. No implicit USD base or USDC parity.
- PriceSet: unique participating assets, one explicit base/scale, matching context/version/source requirements, price-set content hash. Missing active liability/configuration blocks the consumer; no substitution from DEX or another time.
- ValuationContext: SYNTHETIC_ECONOMIC_REFERENCE profile/version, checkpoint ID, clock/as-of, purpose ELIGIBILITY_CHECKPOINT or REPORTING_AFTER_TRADE, resolved collateral flags/effective LT and assumptions. Unknown historical profile is BLOCKED, not default Aave rules.
- ValuationResult: immutable per-reserve raw token quantities, collateral/debt base values, weighted LT numerator, debt denominator, finite HF_WAD or tagged NO_DEBT; parents/profile/policy/context hashes, explicit rounding and evidence class. USD-equivalent reporting and settlement quantities are separate fields.
- CounterfactualPolicyState: version, A/B/C policy ID/parameters, seeded baseline, completed observations with availability, frozen eligibility context. Updates return a new state and never mutate the input/history or an existing checkpoint.

Proposed pure ports: validate_price_observation -> Ok/Blocked/Rejected; value_portfolio -> valuation; advance_policy -> new policy state/price; reporting_price -> reporting-only value. All are PROPOSED, not available runtime APIs. Use exact typed constructors and explicit Ok; handle Blocked as distinct from Rejected. No network, filesystem collector, environment/credential discovery or execution side effects. Do not extend FutureStateRef into an engine.

P02-02's data is an assembled RECONSTRUCTED view containing individually marked observations and source-derived fields. Source HF remains read-only source evidence, not a newly validated valuation. artifact_git_ref is caller-declared while content anchors are verified; pair any future usage with actual Git/CI identity. Collection-end upper bounds are retrospective, not per-call or prediction-time availability. Native USDC round is UNSUPPORTED, upstream is separate; heartbeat freshness is unknown. Two deeply traced assets do not establish complete round/freshness data for all 67 reserves.

## 4. Authorized S economic profile and policy semantics

Raw unsigned amounts q, token decimals d, raw price p in common base U per whole token:

```text
C_i = floor(q_collateral_i * p_i / 10**d_i) if enabled, else 0
D_i = ceil((q_stable_debt_i + q_variable_debt_i) * p_i / 10**d_i)
HF_economic_WAD = floor(10**18 * sum(C_i * LT_bps_i) / (10000 * sum(D_i)))
```

This named economic profile is distinct from Solidity operation order and eMode/native rounding. Full required participation must be explicit; no route-only HF or dropping another asset's debt. All-zero observed debt yields NO_DEBT, not finite HF or Infinity. Preserve UINT256_MAX only as an observed/tagged sentinel. HF equality at WAD is not below one; eligibility is an informational context-specific comparison, never an execution request. LTV and liquidation bonus do not enter the HF formula. Resolved effective LT for a toy eMode fixture is an explicit synthetic input, not inferred historical behavior.

For A/B/C controls preserve V1 initialization: valuation starts at reference; history seeds baseline d0. At the next checkpoint use completed, already available observations only. A=min(reference,last completed DEX); B=reference. C uses end=len(history)-(lag-1), window ending at end; if insufficient lag, reference is a MODEL_DEFINED_INITIALIZATION, not fabricated history. Otherwise average the permitted window, blend reference+alpha*(mean-reference), cap at reference. C weak=(alpha 1/4,lag1,window3); C moderate=(1/2,lag1,window2). Positive prices, exact alpha in [0,1], exact integer lag/window>=1. A without its required seeded/completed history blocks instead of leaking an IndexError or inventing a reference observation.

Exact rational reference vectors may guide S; declare representation and rounding/version before implementation. Do not silently quantize a fractional result into a historical integer price or claim bit-exact equivalence with all V1 Decimal contexts. Any additional integer/native profile requires a separate approved specification. A reporting price can use current completed trade price only in the separate reporting context; it cannot mutate frozen eligibility inside the batch. There is no batch/agent engine in S.

## 5. Synthetic reference vectors / required tests — NOT EXECUTED

All entries below are hand-specified synthetic fixtures, not Mainnet results, calibration or performance claims. Independently encode expected values; do not calculate expectations by calling the implementation under test.

| Vector | Input / declared profile | Expected |
|---|---|---|
| V03-01 units | Synthetic USD U=10^8; 2 WETH raw=2*10^18 at p=2000*U; LT=8000; 1000 USDC raw=1000*10^6 at p=U | C=4000*U, D=1000*U, HF=3.2*10^18; explicit quantities/units |
| V03-02 debt price | Same quantities, COUNTERFACTUAL USDC p=0.8*U | D=800*U, HF=4*10^18; 1000 USDC unchanged; this is debt valuation, not a successful depeg model |
| V03-03 threshold | Synthetic collateral value100*U, LT8000; debt80*U; vary debt quantity by one raw unit | HF=WAD exactly is not below1; neighboring cases use declared integer floor, not float epsilon |
| V03-04 no debt | Every participating debt observed0 | Tagged NO_DEBT, no division0/Infinity or eligibility; a missing debt observation is BLOCKED instead |
| V03-05 rounding | Toy asset decimals2, price raw33, collateral raw1, debt raw1 | C=floor(33/100)=0, D=ceil(33/100)=1; deliberately synthetic profile |
| V03-06 distinct mechanisms | Hold portfolio/prices/LT fixed, vary only LTV/bonus | HF unchanged; capacity/bonus are different mechanisms and outside liquidation execution |
| V03-07 policy | Synthetic completed DEX [100,80,60], reference100, seeded baseline included | A60; B100; C weak95; C moderate85 |
| V03-08 lag | Same history, C lag3 versus lag4 | lag3 permitted mean100; lag4 insufficient history→reference with MODEL_DEFINED_INITIALIZATION label |
| V03-09 context | Eligibility frozen95; reference100/current reporting DEX70 | A reporting70, B100, C frozen95; eligibility context/hash unchanged |
| V03-10 source/time | DEX masquerades as Aave; unsupported native round0; future updatedAt/availability; wrong base/decimals | REJECTED or reasoned BLOCKED as specified; no substitution, fill or origin promotion |

Map all nine P02-T02-01…09 requirements to actual tests and remaining clauses. Include wrong chain/hash/asset, duplicate assets, boolean-as-integer, float/nonfinite/overflow, zero/negative price, absent conversion evidence, all participating liabilities, effective-LT context, exact NO_DEBT semantics, stale/unknown heartbeat, native/upstream phase/round mismatch, no-lookahead, invalid alpha/lag/window, immutable history/input, reporting/eligibility isolation, content/evidence hash domains and deterministic replay of pure functions. Supported synthetic profiles may pass with valid negative/no-eligibility outcomes. Keep all 46 design specifications dispositioned; T03–T05 are not implemented by S.


### Required T02 coverage mapping

| Accepted specification | Synthetic controls / remaining boundary |
|---|---|
| P02-T02-01 | V03-01/05; complete multiasset/effective-LT toy eMode contexts; native operation order is not implemented by S |
| P02-T02-02 | V03-04; observed-zero NO_DEBT vs missing BLOCKED |
| P02-T02-03 | V03-03/06; equality/neighbor raw unit; LT vs LTV/bonus |
| P02-T02-04 | V03-10; source identity and DEX/Aave distinction |
| P02-T02-05 | V03-10; synthetic upstream/native round variants, no historical round-validation claim |
| P02-T02-06 | V03-10; future time/stale declared rule/unknown heartbeat; native-use freshness stays blocked |
| P02-T02-07 | V03-07/08; exact initialization/lag/smoothing/parameters and immutable replay |
| P02-T02-08 | V03-09; reporting never changes eligibility checkpoint/hash |
| P02-T02-09 | V03-02; fixed token quantity/two counterfactual prices; base and zero-price negatives |

The ten vectors and nine requirement rows are test obligations, NOT_RUN until Codex records actual outputs. S may discharge synthetic clauses only; retain native/historical clauses as NOT_IMPLEMENTED/BLOCKED with reasons. The pre-existing46 architecture IDs are not renumbered or blanket promoted to PASS.

## 6. Required local/CI acceptance and evidence

Record the explicit authorization token and S-only scope from this handoff/Issue45 in the implementation PR before coding. The grant is now effective; H/N remains excluded. Run new scoped pytest/JUnit, all accepted 70 adapter + 97 contracts + 80 legacy regressions, L1, Ruff, strict mypy, wheel/source-byte and protected-tree checks locally first. Tests must not load historical portfolios into a new valuation calculation under a synthetic-only grant; saved-loader regression tests are byte/schema tests only. No full research workflow or Monte Carlo.

Provide dedicated and repository CI on the exact final HEAD; read actual reports/JUnit/checksum lists, verify code hashes and PR merge-ref tree versus branch tree. Emit failure reports with reasons, do not hide invalid evidence with a green exit. Pin fixture input/expected output/origin/profile hashes. P02-02 saved integrity does not validate a new valuation formula. Native profile comparisons require independent implementation/reference evidence and separate authorization, not copying the formula into a test.

One Draft PR into feat/terra-model-v2, exact base/head/changed paths, implemented/remaining clauses, actual counts/environment/commands, CI/artifact URLs/hashes, limitations and reviewed-revert rollback. No expected-result weakening, tolerance relaxation or deselection to manufacture success. Work reviews actual code, then governed merge only if applicable gates pass; post-merge CI is separate. This is not V2 scientific-final or release-candidate approval.

## 7. STOP conditions and parallel work

Verify the explicit S grant above before coding; STOP if the proposed task exceeds it. STOP on required historical/native execution, live RPC/paid access, source/gate edits, unresolved heartbeat/profile/participation required for a proposed native/historical use, unexplained units/time/hash mismatch, need for liquidation/AMM/scheduler or an unapproved formula/control change. Intentional missing/stale/malformed synthetic controls must produce the specified reasoned BLOCKED/REJECTED result; they are test cases, not permission to fill missing data or abort report creation. Return a precise field/claim/path impact rather than a fabricated value. No upward source verification relabeling.

Work may continue independent L0 designs: P03-D01 layer/edge/unit/loss-ledger and controls; P04-D01 separate Terra vintages/availability/sealed holdout/baselines; P05-D01 independent comparator/retention/reproduction/reviewer protocol. These have separate files/owners and no propagation/predictor/empirical run. Positive Aave results are not a prerequisite for Terra protocol design. Source/clock/ownership contracts can be reviewed in parallel; P02-03-S contract implementation is granted above; other shared-contract or runtime packages still await their own scoped grants and prerequisites.

Handoff target: `P02_03_S_AUTHORIZED_AND_READY_FOR_CODEX`. Actual S implementation target: `P02_03_SYNTHETIC_VALUATION_READY_FOR_TECHNICAL_REVIEW`. Neither target grants historical execution, native equivalence or scientific-final status.
