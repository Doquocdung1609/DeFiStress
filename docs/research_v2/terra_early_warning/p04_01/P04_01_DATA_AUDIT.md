# P04-01 — Historical Dataset Audit & Point-in-Time Eligibility

Authority `V2_TERRA_EARLY_WARNING_HISTORICAL_VALIDATION_PROGRAM_AUTHORIZED`; parent Issue #49. Source anchor **`9207ead7db3acf1332b34cebcd19981c2f7bd9cc`**, audited 2026-10-21 UTC. This is a new Terra research program, separate from Aave–Uniswap and from the six locked V1 RQs. The mandatory academic objective is investigation and a defensible demonstration, never a guaranteed positive forecast.

## Actual audit scope

The tracked-path inventory uses a declared case-insensitive `terra|early.warning|cutoff|forecast` path filter: **304 paths / 272 distinct Git blobs**. These are not 304 datasets or independent sources. **35 selected files** were fetched in full and verified against pinned Git blob SHA-1, byte size and SHA-256; **269 paths have metadata only**, with bytes explicitly UNVERIFIED. The approximately98MB replication ZIP, large daily-balance, Anchor-wallet and native-swap packs were not fully read by Work. Source-declared counts/validation for those packs remain source evidence, not newly reproduced results.

Selected full-byte inputs cover source manifests/dictionaries/lineage, V1 code/audit reports, three core/legacy CSVs, two daily raw price CSVs and eight Parquets. All eight Parquet schemas were read locally with pyarrow19.0.1; byte/count inspection is not new feature generation or a historical backtest. The primary extended CSV has **1,776 hourly rows**, 2022-03-01 00:00 through 2022-05-13 23:00 UTC. The legacy May CSV has312rows. Both raw May minute-price Parquets have21,600rows from May1 through May15, not just the processed May1–13 window. Native LUNA supply source has337rows and ends May15 00:00. Extra post-window rows must not silently enter future features, normalization or labels.

The registry contains all304path dispositions, the35byte hashes,14core-column profiles, eight schemas and all ten requested data-group assessments. The PIT manifest admits **zero predictive fields at this checkpoint**. This means no field has yet cleared the stricter availability/vintage/interval contract; it does not prove that original chain/trade observations were unavailable in2022. Those observations remain candidates for explicitly anchored availability reconstruction.

## Core coverage measured from the CSV

| Field group | Missing of1,776 | Interpretation |
|---|---:|---|
| UST/LUNA price, UST supply, Anchor deposit stock |0 each| Present retrospective values; timestamp alone is not release-time proof |
| LUNA supply / backing ratio |1,464 each| Valid processed coverage begins May1; backing is a market-cap/supply risk indicator, not literal collateralization |
| Anchor deposit / withdrawal flow |1,584 each| Processed coverage begins May6; absence before coverage is missing, not observed zero |
| Native redemption / gross issuance |1,608 each| Processed coverage begins May7; raw action/direction/availability needs separate evidence |
| Top10 / Top100 Anchor share |168 each| Ends May6; not extrapolated into the collapse |

These are data inventory counts, not early-warning performance statistics. The source lineage distinguishes daily carried values, derived state, event sums and partial observations. BTC/ETH and a multi-stablecoin PIT context panel are not present in the audited forecasting pack; unrelated Ethereum snapshots cannot fill those2022gaps. Volume is not order-book depth. The two inspected Curve files contain trades (405rows for May7/2022;1,733for a May2021window), not complete historical pool reserves or executable depth.

## Findings and exact repair/admission criteria

| ID / priority | Source locator at the anchor | Finding | Condition before forecast/exit use |
|---|---|---|---|
| TERRA-A01 / PIT blocker | Core CSV header; `source_lineage.json`; publisher record | No per-field first-available/publication/vintage proof in the selected records. Repository acquisition and package publication are later than2022 | Retain event, release, available and acquisition times separately; establish original-time evidence or an explicitly reviewed conservative bound for each dependency |
| TERRA-A02 / PIT blocker | `scripts/terra/complete_historical_data.py::aggregate_event_flows` and `sim/terra/early_warning_v2.py::_features` | Events are floored to start-of-hour before whole-hour summation. Using that row at its label time can include later events within the hour; perturbing rows after the label does not detect this | Define interval [h,h+1h), issue only after interval completion plus publication/processing delay; derive max dependency availability from raw events. Synthetic witness: event00:30 cannot affect a00:00decision |
| TERRA-A03 / PIT & exit blocker | `Datasets.md` §§33/35; two minute-price schemas (`time,price`) | May prices are documented cross-exchange volume-weighted aggregates; minute timestamp closure and original availability not retained | Verify start/end/aggregation/venue/vintage semantics, admit only completed aggregates. Do not use them as executable bid/ask quotes |
| TERRA-A04 / design constraint | Extended dictionary and `_composite_price` | March–April daily state is carried into hourly grid; May switches to minute source | Preserve source age/frequency and regime. Do not count carried prices as independent hourly observations or compare methods with unequal information sets |
| TERRA-A05 / model constraint | `early_warning_v2.py::_score_frame` | Missing features are dropped and weights renormalized; a row score/leakage label is not evidence of source availability. Default mode is retrospective | New output needs explicit coverage/validation status and a preregistered minimum-coverage/renormalization policy; abstain when required inputs are unavailable |
| TERRA-A06 / label blocker | `terra_final/final_report.md` §6 versus `validation_audit/phase5_terra_early_warning_audit.json#/modes/CUTOFF_SAFE/lead_times` | Existing sources place first UST<.99 at22:00 versus23:00 on May7 under different datasets/time mappings | Curate a single versioned label source/interval convention independently of model performance; retain old labels in audit trail. Do not select the onset that improves lead time |
| TERRA-A07 / exit blocker | Legacy CSV liquidity/depth fields; extended report; Curve schemas | Legacy liquidity/depth are fixed market-volume proxies. Neither a partial trade list nor price difference proves a feasible exit | Historical pool/order-book state, quote/fee/access/finality/latency and position-size evidence required; otherwise NOT_VERIFIABLE |
| TERRA-A08 / unit reconciliation | Raw V1 provenance `evidence_map` UST supply versus extended `source_lineage.json` | Old metadata describes microUST÷1e6; extended lineage explicitly uses already normalized balances without rescaling | Resolve source/schema/version/unit mapping before rebuilding; keep datasets/version metadata separate. No V1 numeric or manifest edit in this task |
| TERRA-A09 / validation constraint | V1 final report §5 and phase5 warning audit `forecast_claim` | Frozen strict OOS result is negative; CUTOFF_SAFE monitoring weights/scales were developed with knowledge of the event and no pre-event model-selection protocol | Preserve negative finding; label new chronological Terra evaluation as outcome-known retrospective research; no claim of a previously unseen/prospective real-time forecast |
| TERRA-A10 / false-alert constraint | Raw daily CSV coverage; May2021 Curve extract; absence of sealed normal-period labels | May2021 is an adverse-event candidate, not automatically a normal period. Existing hourly model panel does not establish independent crisis controls | Independently label event/non-event/censored windows before evaluation; retain full registered denominators and availability exclusions |

These findings restrict admission into a new PIT/exit study; they do not rewrite V1's already qualified claims or its numerical outputs. Work read source and bytes, and performed static/self-review. No external independent reviewer has reviewed this new audit.

## What existing results actually support

Reading the saved phase5 audit, not rerunning it: HIGH first appears2022-05-09 19:00UTC,44hours after that artifact's UST<.99 marker and3hours before its UST<.90 marker. This is late relative to initial instability and earlier relative to a later severity threshold. The artifact explicitly has `forecast_claim.supported=false`; future-perturbation PASS only tests causal row-index calculations, not publication-time safety, ex-ante model selection, false-alarm risk or feasible exits. Frozen strict OOS model failure remains negative evidence. No new alert or metric was computed here.

## External source verification and limits

- [Publisher v4](https://data.mendeley.com/datasets/j5d8n7hzdy/4), accessed2026-10-21: version4 / DOI10.17632/j5d8n7hzdy.4, published2026-08-03; named contributors Liu/Makarov/Schoar; data/exhibits CC-BY4.0, code MIT. Metadata/license verified; current full publisher ZIP was not downloaded or equated with every local file. Release date is not historical observation availability.
- [Kaiko versioning](https://docs.kaiko.com/rest-api/general/getting-started/data-versioning): pin dataset version separately from API version; current docs do not establish the shipped aggregates'2022latency/vintage.
- [CoinGecko range documentation](https://docs.coingecko.com/reference/coins-id-market-chart-range): explicit timestamps, resolution and24hvolume semantics. Current API documentation is not a2022release certificate. No historical API data newly acquired.
- [Binance public-data documentation](https://github.com/binance/binance-public-data): trade and kline time fields and archive publication schedule are useful candidate requirements. No symbol/window/file coverage or market access has been verified or acquired; next-day archive availability must not be confused with live trade availability.

No new literature/source verification label is inserted into frozen P2. All source IDs here are audit metadata, not accepted scientific findings. Git LF bytes, CRLF checkout representations, compressed/decoded bytes and typed content remain separate hash domains. Extended CSV/parquet declared output hashes match actual Git bytes for the two files inspected; no invented erratum or Frozen Manifest change is needed.

## Reproduction and scope

From the exact source checkout with normal Git LF input bytes:

```bash
python scripts/research/terra_v2/audit_p04_01.py --repo-root . --registry docs/research_v2/terra_early_warning/p04_01/P04_01_DATASET_REGISTRY.json --output /tmp/p04-01-audit.json
python -m pytest -q tests/research_v2/test_terra_p04_01_audit.py
ruff check scripts/research/terra_v2 tests/research_v2
mypy --strict scripts/research/terra_v2/audit_p04_01.py
```

The auditor is stdlib-only and checks35byte records plus declared CSV structure/counts. It emits FAIL/nonzero on invalid evidence and cannot promote PIT eligibility or run a model. An explicitly CRLF checkout can fail an LF hash check; preserve/report byte domains, do not silently normalize evidence. Local schema inspection used pyarrow19.0.1 separately; the automated35-record replay is byte/CSV audit, not an independent reconstruction of all Parquet economic content. Larger inputs/unknown schemas need a separately reviewed bounded reader; no hostile-concurrent-filesystem sandbox is claimed.

Current status: **P04_01_DATA_AUDITED_WITH_PIT_BLOCKERS — READY_FOR_REVIEW**. The complete `TERRA_V2_EARLY_WARNING_RESEARCH_DEMONSTRATOR` has **NOT_YET_BEEN_ACHIEVED**. Next permitted implementation is Issue #50's saved-audit/synthetic scope. Historical backtest and exit simulations wait for approved protocol and eligible sources, not for a positive outcome or closure of Aave Gate A.
