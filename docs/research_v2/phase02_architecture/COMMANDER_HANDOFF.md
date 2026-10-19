# Commander handoff — Phase 02 architecture design

**V2_PHASE02_ARCHITECTURE_READY_FOR_COMMANDER_REVIEW**  
**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED**

## 1. Preflight và phạm vi

Reference và actual integration HEAD đều `2e0ec142c475f8d1362f90c4ca8d2f0718e41f77`; PR34 đã merge tại commit này. Branch đề xuất `research/v2-phase02-architecture-design` xuất phát đúng anchor, target `feat/terra-model-v2`. Chỉ tám Markdown design files; không tạo proposed packages, engine, schema implementation, executable state machine, fixtures hoặc Codex tasks. Exact submission SHA, Draft PR và CI URL/status được ghi trong GitHub handoff để tránh self-embedded commit hash.

V1 annotated tag object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7` → `2b505813d35d3cf6f4414585f9dd50f3b4281ac2` đã được kiểm tra qua GitHub. Scientific lock `3f6e5302483681209e2408531eb5a15389f9fded` và Blueprint lock `8de52bebabef376be700836e6f93a92d7394d2c3` giữ nguyên. Không có dữ liệu, source registry, V1 report hoặc Phase01A/B artifact được sửa.

[Issue35](https://github.com/Doquocdung1609/DeFiStress/issues/35) OPEN, chỉ cấp offline L1/L2 validation. [PR36](https://github.com/Doquocdung1609/DeFiStress/pull/36) OPEN/Draft, chưa merge/Commander accepted; reviewed head `c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb`. Các runs [39281653358](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39281653358) (offline), [39281653451](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39281653451) và [39281659860](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39281659860) (repository CI) còn QUEUED tại lần kiểm tra trong nhiệm vụ này. Không gọi PR36 PASS; API chỉ PENDING reference, không import/cherry-pick. Nếu parallel HEAD/acceptance thay đổi sau đó phải review delta trước optional reuse; không tự đổi base thiết kế vì chưa có merge.

## 2. Deliverables và quyết định chính

| Document | Coverage |
|---|---|
| [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) |5 module owners, acyclic dependency graph, V1 reuse/revise/new disposition; proposed paths không bị gọi là existing code |
| [DATA_AND_INTERFACE_CONTRACTS.md](DATA_AND_INTERFACE_CONTRACTS.md) | Typed amounts/prices/HF/evidence, field lineage, historical snapshot/capabilities, ports/DTOs, quarantine/hash/version contracts |
| [ORACLE_LIQUIDATION_AMM_SPEC.md](ORACLE_LIQUIDATION_AMM_SPEC.md) | A/B/C counterfactual control math, historical oracle distinctions, versioned Aave rules, lifecycle/reasons, AMM integer/band/accounting boundaries |
| [AGENT_ORCHESTRATION_SPEC.md](AGENT_ORCHESTRATION_SPEC.md) | Sole writer, deterministic sequencing/conflict handling, funding/gas/latency/rollback/termination/replay |
| [TEST_SPECIFICATIONS.md](TEST_SPECIFICATIONS.md) |46 future test specifications, expected negative/blocked outcomes, F/S/L/R evidence requirements; **NOT_RUN_DESIGN_ONLY** |
| [CODEX_IMPLEMENTATION_PLAN.md](CODEX_IMPLEMENTATION_PLAN.md) |7 packages, prerequisites/expected files/interfaces/acceptance/risks/STOP; no tasks launched |
| [SCIENTIFIC_GATES_AND_DEPENDENCIES.md](SCIENTIFIC_GATES_AND_DEPENDENCIES.md) | Source→decision→limitation matrix, Gate A/B/use classes, PR36 compatibility boundaries, UQ-01…09 |
| This handoff | Source index, self-review/check scope, six unchanged RQs và decision proposal |

Kiến trúc dùng immutable historical envelopes, pure assess/quote, coordinator sole writer và typed execution evidence modes. Economic model formulas không được gọi native integer fidelity khi chưa có profile/receipt verification. Liquidation và collateral sale mặc định tách transaction boundaries; failed sale không tự rollback successful repayment. Concurrency chỉ parallel pure proposals, commit deterministic/revalidated. Price repositioning control không có funded trade/PnL claim. Model clock/accrual/source freshness và hash domains là explicit contracts.

## 3. Acceptance recommendation theo package

GO cho **review thiết kế** P02-01…07. Mọi implementation hiện tại **NOT_AUTHORIZED**. Có thể xin lệnh riêng cho bounded core contracts/saved-input adapter/pure valuation fixtures sau architecture acceptance; đây không phải quyền có sẵn từ PR36. P02-04 liquidation, P02-05 swap execution, P02-06 engine/agents và P02-07 historical integration/run hiện **NO-GO**: chưa có authorization, Gate A/use-specific native profile/coverage/execution evidence còn thiếu. Native/publication acceptance phải có receipt/accounting/OOS/identification gates tương ứng, không chỉ CI xanh.

Suggested order **P02-01 → P02-02 → P02-03 → P02-04 và P02-05 → P02-06 → P02-07**. PR36 reuse là optional sau merge+acceptance; architecture không bị compile/API dependency vào unmerged branch. Không yêu cầu Commander cho phép thực thi bất kỳ package nào chỉ để nghiệm thu docs.

## 4. Self-review và actual verification scope

Work đã đọc/inspect44 source artifacts qua GitHub tại exact refs bên dưới: source code V1 liên quan, tests/harness, Phase00/01 protocols/provenance, backend/Gate B dossiers, PR36 candidate sources và locked registry. Code inspection tập trung interfaces/arithmetic/order/coverage; không gọi đây là independent protocol verification, đọc hết mọi artifact lớn hoặc fresh RPC validation. JSON registry48 records được parse:44 accepted affirmative,4 disallowed giữ disposition; source access levels không đổi.

Tự phát hiện và sửa trước push: header test count nhầm48 được đối chiếu actual46 IDs; loại typo/working-note; làm rõ schema proposals không existing APIs, zero-liquidity empty interval không whole-pool zero, adapter native-round unsupported khác missing, frozen HF eligibility khác intrawave reporting, và split transaction rollback semantics. Không sửa source evidence để làm design PASS.

Static checker tạm `python arch_inputs/validate_architecture.py` kiểm tra tám files/local links/source paths+Git blobs, signature labels PROPOSED,46 unique test IDs và7 columns/evidence fields, invariant references, acyclic module/work-package DAGs, đủ7 packages/5 modules,6 verbatim RQs/44+4 registry boundary, mandatory statuses và no implementation paths trong output. **7 nhóm kiểm tra PASS**, gồm44 sources và67 Markdown links. Đây là **self-review/static document checks**, không phải46 executable tests hoặc independent peer review. Không chạy engine, simulation/Monte Carlo, fork/RPC, calibration hoặc full research suite; normal repository CI nếu tự trigger sẽ báo riêng, đúng head/status, không dùng PR36 CI để gán PASS thiết kế.

Sau push phải so recursive remote tree với1281 existing blobs: chỉ8 Markdown additions,0 existing blobs changed/deleted; đọc lại exact content và kiểm tag. Actual preservation/readback/CI results ghi ở GitHub handoff. Tài liệu đính kèm cũ không cần cho architecture và không được dùng thay locked scientific evidence.

## 5. Sáu RQ nguyên văn — traceability, không findings V2

**RQ1:** Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)?

**RQ2:** Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt?

**RQ3:** Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý?

**RQ4:** Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi?

**RQ5:** Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset?

**RQ6:** Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk?

## 6. Exact source index

`I` = integration anchor nêu trên; `S` = scientific lock `3f6e5302483681209e2408531eb5a15389f9fded`; `P` = PR36 pending head `c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb`. Links pin full commit. Git blob SHA-1 được xác minh trên exact fetched content; byte SHA256 được tính local trong source audit, không đồng nhất hai hash domains. JSON large registries/provenance được parse và relevant fields reviewed; không rerun scientific comparisons.

| Source at exact ref | Anchor | Git blob SHA-1 |
|---|---|---|
| [sim/schemas.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/schemas.py) | I | `0f9a93180ada5912c55d0d36d5c142d0e4a356a6` |
| [sim/oracle.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/oracle.py) | I | `2ac37f923a4cc35bef95968d353f0724bfdbd3a5` |
| [sim/engine/run.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/engine/run.py) | I | `2b23c9ee88ee4976755e5f4795026e381d5fe497` |
| [sim/dex/uniswap_v3.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/dex/uniswap_v3.py) | I | `4172eae06907ae8bf95a10e7e50463111d0eec3d` |
| [sim/lending/health_factor.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/lending/health_factor.py) | I | `8d8cae6754e718856867ce3696498bd68134a294` |
| [sim/lending/liquidation.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/lending/liquidation.py) | I | `9f95f18e8aa52f48facbebe1b3bdc8f88c0f162a` |
| [sim/agents/liquidator.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/agents/liquidator.py) | I | `9f44ba9a8037f239b2b5ef8881ad2d49c25ecf6d` |
| [sim/agents/arbitrageur.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/agents/arbitrageur.py) | I | `2160d0fed0797e665d6aaaec65b7f6bb21f471b7` |
| [contracts/validation/README.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/contracts/validation/README.md) | I | `c27a56543ec72e705e99e7943c5578e9a557a7d7` |
| [contracts/validation/src/ValidationProbe.sol](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/contracts/validation/src/ValidationProbe.sol) | I | `25d4036e35db490e36b05093c6b2942dc500077d` |
| [contracts/validation/test/ForkValidation.t.sol](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/contracts/validation/test/ForkValidation.t.sol) | I | `76453bb159cc35784d3659e435da4dfe59472221` |
| [docs/research_v2/phase00/V2_RESEARCH_UPGRADE_BLUEPRINT.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase00/V2_RESEARCH_UPGRADE_BLUEPRINT.md) | I | `0763b85937f11ab13e36983bd825e968061c9562` |
| [docs/research_v2/phase01a/PHASE01A_VALIDATION_REPORT.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01a/PHASE01A_VALIDATION_REPORT.md) | I | `4deb602b1786b330f25be58539aadf40150ca248` |
| [docs/research_v2/phase01a/pilot.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01a/pilot.py) | I | `62e2732fd4e8ac1928ee67f70816bc78a5e6b479` |
| [docs/research_v2/phase01b/collector.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01b/collector.py) | I | `eca5ad25848e009cbe14a4df3d9af148a6055549` |
| [docs/research_v2/phase01b/verify_saved.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01b/verify_saved.py) | I | `1a4d05e856f28dae19ea958b7052fcc72bca9b25` |
| [docs/research_v2/phase01b/SAMPLE_REGISTRATION.json](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01b/SAMPLE_REGISTRATION.json) | I | `804b3561419e7d20adc8d401eea29a9cb5647a6c` |
| [docs/research_v2/phase01b/AAVE_HISTORICAL_ORACLE_TRACE.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01b/AAVE_HISTORICAL_ORACLE_TRACE.md) | I | `180e0e4859a7de0dbec86edf46a0d316054449f0` |
| [docs/research_v2/phase01b/UNISWAP_TICK_COVERAGE_REPORT.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01b/UNISWAP_TICK_COVERAGE_REPORT.md) | I | `41859f20f46f093e45788479ea1eda32021c8b90` |
| [docs/research_v2/phase01b/BORROWER_RECONSTRUCTION_AUDIT.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01b/BORROWER_RECONSTRUCTION_AUDIT.md) | I | `809cf726feb2ffb636524b0409fb198baa9891cd` |
| [docs/research_v2/backend_provenance/BACKEND_INDEPENDENCE_DECISION.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/backend_provenance/BACKEND_INDEPENDENCE_DECISION.md) | I | `90c8f5a71780ee6b9456246ba2faa83fa63bc0f3` |
| [docs/research_v2/gate_b_protocol/GATE_A_VS_B_PROTOCOL.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/gate_b_protocol/GATE_A_VS_B_PROTOCOL.md) | I | `bcdec513a1feda924a22d432f81372399e78e814` |
| [docs/research_v2/gate_b_protocol/SCIENTIFIC_GO_NO_GO_DECISION.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/gate_b_protocol/SCIENTIFIC_GO_NO_GO_DECISION.md) | I | `a86a21f1fbbc0329dfb33e7cdef12debe50c4454` |
| [docs/research_v2/gate_b_protocol/PHASE02_DEPENDENCY_AND_RISK_MATRIX.md](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/gate_b_protocol/PHASE02_DEPENDENCY_AND_RISK_MATRIX.md) | I | `55f6b74e21c7730a51256828a3b27e3267643f38` |
| [docs/research_v2/gate_b_protocol/EVIDENCE_SCOPE_MATRIX.json](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/gate_b_protocol/EVIDENCE_SCOPE_MATRIX.json) | I | `6e346077ddcf62a1751fbc6624da067adc9443c0` |
| [docs/research_v2/prephase02_offline/validate_offline.py](https://github.com/Doquocdung1609/DeFiStress/blob/c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb/docs/research_v2/prephase02_offline/validate_offline.py) | P | `c44f8e00cc5cb03c51da69fa6c40fa1f771cc965` |
| [docs/research_v2/prephase02_offline/OFFLINE_EVIDENCE_MANIFEST.json](https://github.com/Doquocdung1609/DeFiStress/blob/c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb/docs/research_v2/prephase02_offline/OFFLINE_EVIDENCE_MANIFEST.json) | P | `6cf535bd2dde3849e04c853e229022d4913926b9` |
| [tests/test_prephase02_offline.py](https://github.com/Doquocdung1609/DeFiStress/blob/c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb/tests/test_prephase02_offline.py) | P | `a7ae883f55da089386b3fd28249a77b9c2290a7d` |
| [docs/research_v2/prephase02_offline/COMMANDER_HANDOFF.md](https://github.com/Doquocdung1609/DeFiStress/blob/c2f85d93b78bc4d4c3b90d169ca65811c7ed9deb/docs/research_v2/prephase02_offline/COMMANDER_HANDOFF.md) | P | `43c38d4eee7a2d6b2f0bac02d1be2530cd9ee535` |
| [data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json) | S | `bac44e61633b5efdde3665731ea69fbf4ca345e6` |
| [data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json](https://github.com/Doquocdung1609/DeFiStress/blob/3f6e5302483681209e2408531eb5a15389f9fded/data/processed/research_final/final_accepted_claims_v1/six_rq_accepted_claims_matrix.json) | S | `fffe69d45f2c70e8f4cb781c8b521ef4cf6f1a45` |
| [backend/app/adapters/aave/contracts.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/backend/app/adapters/aave/contracts.py) | I | `d3dd2e3c49757c46da37497683241773e541b81d` |
| [backend/app/adapters/aave/positions.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/backend/app/adapters/aave/positions.py) | I | `f4d832d8e29e2b0cdf5476e64ef6496e2643b8c9` |
| [backend/app/adapters/aave/oracle.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/backend/app/adapters/aave/oracle.py) | I | `2ffb791e36cec02823d7eba0764b4bb0f011fdf0` |
| [backend/app/adapters/uniswap/math.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/backend/app/adapters/uniswap/math.py) | I | `e99dffd6fc81ced0d5d4acb69f0f949ad740ebe4` |
| [backend/app/adapters/uniswap/ticks.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/backend/app/adapters/uniswap/ticks.py) | I | `37d2068d4cc3de77239d5bcb73957e98111c3c23` |
| [backend/app/adapters/uniswap/pool.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/backend/app/adapters/uniswap/pool.py) | I | `d48c6b3a1876145c819250fef2b90caed9a338e0` |
| [sim/tests/test_uniswap_v3.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/tests/test_uniswap_v3.py) | I | `7a1c851573fa703fac4ee53d77338a7e8274ef34` |
| [sim/tests/test_oracle_policy.py](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/sim/tests/test_oracle_policy.py) | I | `146cafd0f272176456f1cc9c9d44234078546948` |
| [docs/research_v2/phase01a/PILOT_SAMPLE_REGISTRY.json](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01a/PILOT_SAMPLE_REGISTRY.json) | I | `a41372353fe379d013209d325b91b2241260639a` |
| [docs/research_v2/phase01a/PILOT_DATA_PROVENANCE.json](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01a/PILOT_DATA_PROVENANCE.json) | I | `3f35cdf4da46b1b0683db1892e12566a6363f0b8` |
| [docs/research_v2/phase01b/VALIDATION_SUMMARY.json](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01b/VALIDATION_SUMMARY.json) | I | `3effd85f1930c38fcbc5df569a2317f830a56a1a` |
| [docs/research_v2/phase01b/EVIDENCE_PROVENANCE.json](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/phase01b/EVIDENCE_PROVENANCE.json) | I | `376b9e4672745fddbfdd3445dc313df44950c7f7` |
| [docs/research_v2/backend_provenance/REQUEST_PROVENANCE_EVIDENCE.json](https://github.com/Doquocdung1609/DeFiStress/blob/2e0ec142c475f8d1362f90c4ca8d2f0718e41f77/docs/research_v2/backend_provenance/REQUEST_PROVENANCE_EVIDENCE.json) | I | `43e274b7937d7c7cdfc1c066ea10d55c7ea11a63` |

## 7. Remaining risks và Commander decision

UQ-01…09 chưa đóng: historical Aave implementation/rules; native AMM integer/fee/inventory profiles; independent backend attestation; freshness/accrual/timelines; funded execution/receipts; complete route/reserve dependencies; agent/order assumptions; PR36 pending compatibility; Alchemy value-level replay/retention gap. Chúng được fail-closed theo capability, không cản review design nhưng chặn native historical findings tương ứng. Không claim mọi quy tắc Aave/Uniswap đã kiểm chứng chỉ từ equations hoặc code V1.

Đề nghị Commander nghiệm thu hoặc targeted-repair architecture. Nếu chấp thuận, cấp lệnh riêng có scope/gates/test artifacts cho package được chọn; giữ Gate A/B riêng và `PHASE02_NOT_AUTHORIZED` đến khi có quyết định mới. Không merge, di chuyển tag, thay Scientific Content Lock hoặc tạo Codex implementation tasks trong nhiệm vụ này.
