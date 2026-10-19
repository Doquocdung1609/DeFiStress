# Data and interface contracts — PROPOSED

**DESIGN ONLY · GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED**

Tất cả signatures/type/fields mới ở đây là **PROPOSED**, không phải Python classes/schema đã chạy. Contract version đề xuất `defistress-v2-contracts/0.1-design`. Thay đổi required fields/units/canonicalization phải có migration/version riêng; không sửa schema hoặc digests của Phase01/V1.

## 1. Primitive và envelope

| Type PROPOSED | Fields / quy tắc validation |
|---|---|
| `BlockRef` | `chain_id:uint`, `number:uint`, `hash:bytes32`, `timestamp_s:uint`, canonicality evidence ref. Historical reads không chỉ dựa number; canonicality là observation có timestamp, không phải cam kết vĩnh viễn |
| `AssetId` | `(chain_id,address)` canonical lower-case hex; symbol chỉ display; `decimals:uint8` có source ref; cùng symbol không đồng nghĩa cùng asset |
| `Amount` | `asset_id`, `raw_amount:integer-string`, explicit signedness/domain; token balances unsigned; deltas/net liquidity signed; không float/bool làm integer |
| `Price` | `base_currency_id`, `base_unit`, `raw_base_per_whole_asset`, `asset_id`, `source_kind`, observation ref; positive value mới được định giá. USD và native base khác nhau nếu không có conversion evidence |
| `EvidenceRef` | source commit/run/provider label, artifact path, locator/JSON pointer, schema/ABI identifier, method/args hash, block ref, retrieved-at, actual-byte SHA256, optional decoded SHA256, Git blob SHA-1, access/verification scope. Không chứa URL có credentials/header/secret |
| `Value<T>` | Tagged union: `AVAILABLE(value,refs)`, `MISSING(reason,refs)`, `UNSUPPORTED(interface,reason)`, `QUARANTINED(reason,refs)`. `AVAILABLE(0)` hợp lệ nếu quan sát đúng; null không tự thành0 |
| `Result<T>` | `OK(payload,warnings)` hoặc `BLOCKED/REJECTED(code,affected_refs)`. BLOCKED = thiếu capability/input/approval; REJECTED = dữ liệu/spec/invariant sai. Không chỉ dựa CLI exit0 |
| `EvidenceEnvelope<T>` | `schema_version`, `payload`, block/scope ref, `origin_kind`, source refs, derivation ref, parent content hashes; immutable sau nhận |

`origin_kind` là `OBSERVED`, `RECONSTRUCTED`, `SYNTHETIC`, `COUNTERFACTUAL`. Fields có thể khác origin trong cùng pack; pack phải công bố lineage từng thành phần. Raw balance có thể OBSERVED, HF tái dựng RECONSTRUCTED, altered price COUNTERFACTUAL; child không được tự đổi thành OBSERVED vì parent có observation. Synthetic fixture có synthetic source ID rõ, không giả request/receipt Mainnet.

Hash domain tách `artifact_bytes_sha256`, `decoded_bytes_sha256`, `deterministic_content_sha256` và Git blob SHA-1. PROPOSED canonical content: schema-versioned sorted compact UTF-8 JSON, integer strings normalized (không leading zeros/-0), decimals có canonical string, no NaN/Infinity, no final LF, maps sorted, ordered vectors có explicit ordering rule. Null/tagged missing được giữ. Tuple→list chỉ là representation conversion, không đổi bool→int, rounding hoặc unit. Source raw bytes giữ nguyên; normalization tạo derived payload/hash riêng, không thay checksum nguồn LF/CRLF/gzip. Volatile retrieval time để ở acquisition envelope, không trộn vào content hash; block/available timestamps vẫn thuộc deterministic payload.

## 2. HistoricalSnapshot và capability

| Record PROPOSED | Required data / rule |
|---|---|
| `HistoricalSnapshot` | snapshot ID/content hash, one BlockRef, selection/registration ref, protocol profiles, assets/reserves/portfolios/pools/oracle observations, coverage & quarantine ledger, field lineage |
| `ResourceLimits` | Registered maximum compressed/decoded input bytes, portfolios/reserves/tick steps, queued events/attempts và replay output size; manifest-declared sizes đối chiếu trước decode. Vượt bound trả resource-limit BLOCKED/CENSORED theo stage, không truncate rồi báo complete; giá trị cụ thể chốt trước future run |
| `ProtocolProfileRef` | chain, provider/proxy/implementation addresses, effective block range, runtime-bytecode hash, ABI/source version/hash, rule/rounding version, verification status. Pool revision number riêng lẻ không chứng minh matching implementation |
| `ReserveState` | reserve ID/asset, aToken/debt token addresses, balances/config flags, LT/LTV/bonus basis points, eMode/bitmap overrides, reserve indexes/rates/timestamps nếu dùng accrual; observed values/source pointers không bị giả định là đầy đủ execution state |
| `Portfolio` | account ID, block/scope, **full** reserve balance vector: supplied amount, collateral-enabled, stable/variable debt, user flags/eMode; explicit participating set và completeness; on-chain account totals/HF với `WAD` scale/sentinel tag. Không thay other-asset USD aggregates bằng token amounts |
| `PoolState` | chain/pool/factory/token0/token1/fee millionths/tickSpacing/slot0/current tick/sqrtPriceX96/active L; initialized ticks net/gross/bitmap words; coverage range inclusive/word set/boundary convention; fee state/inventory as capability-tagged fields |
| `Coverage` | requested vs available ranges/fields, complete registered band vs full legal domain, selection/denominator, omitted regions/reasons; tick count không thay coverage completeness |
| `OracleObservation` | actual oracle/config/source/adapter links; effective answer/base scale; observation time/updatedAt/round semantics. Native round có thể UNSUPPORTED; upstream round có separate source/phase ref |

`capabilities` là tập có evidence refs: `READ_CORE`, `REGISTERED_TICK_BAND`, `FULL_PORTFOLIO_ECONOMIC_HF`, `DEEP_ORACLE_TRACE`, `EXECUTION_INPUT_COMPLETE`. Không cấp capability cuối chỉ vì các capability đầu PASS. Missing fee-growth/token inventory/profile data có thể cho phép read-only analysis nhưng chặn native swap accounting/execution. Future scenarios ra ngoài band phải BLOCKED; không coi record có ticks list là full pool.

Mẫu hiện có: 3 registered blocks, 2 USDC/WETH fee tiers; 6 pool-block bands, 6 deep USDC/WETH traces, 24 recent-Borrow borrower-block cases/67 reserves per account. Các metrics giữ provenance riêng; không gộp24 thành population hoặc dùng chúng thay cohort109/portfolio255 của V1.

## 3. Shared transition / execution contracts

| Record PROPOSED | Fields và invariant |
|---|---|
| `Valuation` | parent portfolio hash, price-set hash, policy/clock/profile IDs, per-reserve collateral/debt values, aggregate bases, HF tagged finite WAD hoặc NO_DEBT; rounding/derivation refs |
| `LiquidationRequest` | account + debt/collateral asset, receive-aToken mode, desired raw repay, actor, expected state version, expiry, profile, funding/allowance evidence. Không dựa borrower ID duy nhất để deduplicate mọi lần thanh lý tương lai |
| `SwapRequest` | pool, tokenIn/out, exact gross input raw, minimumOut raw, sqrt limit, quote expiry/version, fill policy. Exact-input hai hướng được thiết kế; exact-output chưa trong first implementation scope |
| `Quote` | input state hash, path/ticks crossed, gross/net input, fees, output, post sqrt/tick/L, remaining amount, coverage/capability status, unit map và numeric profile. Pure: không mutate input |
| `TransitionProposal` | read-set versions/hashes, write-set deltas, agent/nonce, funding reservations, preconditions, transaction boundary, explicit fee/gas transfers, expected outcome; không tự commit |
| `ExecutionEvidence` | `mode=MODEL_TRANSITION|LOCAL_FORK|HISTORICAL_OBSERVATION`, executor/profile/version, before/after hashes/deltas, debt actually repaid, seized/received assets, gas/fees, event/receipt locators. Local-fork tx hash không là Mainnet tx |
| `AuditEvent` | deterministic event/attempt/parent IDs, source state version, simulated clock/phase/order, origin/mode, before/after hashes, outcome/reason, refs; append-only |

Ledger dùng raw token deltas theo asset và actor/accounting bucket, không cộng ETH, USDC, aToken và USD thành một balance. Valuation changes là reporting deltas, không tự tạo token transfers. Debt-token burn/mint, reserve cash, collateral/aToken redemption và gas burn/payee phải có explicit accounts/supply terms. Thiếu complete accounting scope: không báo conservation PASS.

## 4. Interface catalog PROPOSED

| Interface | Inputs → outputs | Side effects / preconditions |
|---|---|---|
| `HistoricalStatePort.load_snapshot` | Selection + EvidenceManifest → Result<HistoricalSnapshot> | Read-only saved root; verify bytes/schema/refs; no RPC fallback, no repair source |
| `HistoricalAcquisitionPort.collect` | RegisteredQueryPlan → AcquisitionEvidence | FUTURE AUTHORIZATION REQUIRED; ngoài default runtime, không được gọi trong task này |
| `ValuationPort.value_portfolio` | Portfolio + PriceSet + RuleProfile → Result<Valuation> | Pure; complete participating inputs, matching clock/base/units |
| `PolicyPort.advance_policy` | PolicyState + completed observations + Clock → Result<PolicyUpdate> | Pure new state; no future/in-progress observation |
| `LiquidationPort.assess_route/plan` | Valuation + request + route/funding/profile → Result<Assessment/Plan> | Pure; separate HF eligibility and executable route; no quote commits |
| `AmmPort.quote_exact_input/propose_swap` | PoolState + SwapRequest + MathProfile → Result<Quote/TransitionProposal> | Pure; required band/inventory/cost capability; no arbitrary boundary extrapolation |
| `AgentPort.propose` | immutable StateView + Clock + AgentConfig → ordered Intent[] | Không mutate market hoặc portfolio; budget check chưa phải execution |
| `ExecutionPort.prepare/execute` | Proposal + snapshot version → ExecutionOutcome | MODEL hoặc LOCAL_FORK rõ mode; historical observations là reconciliation input; no Mainnet broadcast method |
| `Coordinator.commit` | validated read/write sets + ExecutionOutcome → NewState + AuditEvents | Sole writer; atomic transaction boundary, append-only evidence; rollback theo mode |

## 5. Validation và quarantine

Identity/schema/ABI/token-order/decimals/hash mismatch → REJECTED và quarantine affected component; missing active debt/source/config → BLOCKED dependent valuation/execution. Cùng thiếu hai lần không repeatability PASS. Missing bitmap words không suy ra empty liquidity. Round timestamp hợp lệ không tự có freshness; no heartbeat policy thì historical execution BLOCKED hoặc dùng counterfactual mode có nhãn và scope được duyệt riêng. Every accepted join giữ same BlockRef; simulated state sau block chỉ là MODEL-derived state với lineage, không giả historical observation ở future timestamp.

PR36 compatibility là PENDING, xem [gates](SCIENTIFIC_GATES_AND_DEPENDENCIES.md). Không tái định nghĩa active L là “≤ total pool liquidity” khi total chưa có unit/aggregation contract; không bắt adapter không hỗ trợ native round cung cấp round ID giả để qua validator.
