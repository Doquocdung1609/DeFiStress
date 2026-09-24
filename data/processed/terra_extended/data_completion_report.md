# Terra historical data-completion report

Dataset: `terra_extended_20220301_20220513_v1`  
Window: `2022-03-01T00:00:00+00:00` through `2022-05-13T23:00:00+00:00`  
Rows: **1776**

## Summary

| Data channel | Status | Coverage | Source | Use |
|---|---|---|---|---|
| UST price | READY WITH LIMITATIONS | 2022-03-01–2022-05-13 | CoinGecko daily + Kaiko minute | Fit + warning |
| LUNA price | READY WITH LIMITATIONS | 2022-03-01–2022-05-13 | CoinGecko daily + Kaiko minute | Fit + warning |
| UST supply | READY WITH LIMITATIONS | 2022-03-01–2022-05-13 | Columbus-5 daily address balances | Fit + warning |
| LUNA total supply | READY WITH LIMITATIONS | 2022-05-01–2022-05-13 | native-swap total-supply reconstruction | Fit + mechanism |
| Anchor deposits | READY WITH LIMITATIONS | 2022-03-01–2022-05-13 | Anchor contract state + live epoch state | Fit + warning |
| Anchor deposit/withdraw events | READY WITH LIMITATIONS | 2022-05-06–2022-05-13 | archive-node event extract | Warning + wallet analysis |
| Native UST→LUNA swaps | READY | 2022-05-07–2022-05-13 | market-module swap events | Mechanism |
| Anchor holder concentration | READY WITH LIMITATIONS | 2022-03-01–2022-05-06 | aUST balance concentration | Warning |
| Anchor wallet events | READY WITH LIMITATIONS | 2022-05-06–2022-05-13 | hashed archive-node events | ABM evidence |
| Terra DEX reserves/depth | MISSING / UNAVAILABLE | none | no pool-state source found | Stress only |
| Legacy DEX proxy | PROXY ONLY | prior May dataset | CoinGecko total_volume / 24 | Explicit opt-in only |
| LFG reserve funding | READY WITH LIMITATIONS | 3 events in Feb 2022 | author-labelled Anchor cash-flow address | Context only |
| LFG peg defense | MISSING / UNAVAILABLE | none | no identified intervention ledger | Defense unavailable |
| Curve | OPTIONAL / PARTIAL | 2022-05-07 | Ethereum Curve trade extract | Secondary channel |
| Bridge flows | QUARANTINED | prior May dataset | invalid identical mapping | Do not use |

## A. READY

- The hourly UTC grid, block heights, May native-swap events, and direct event-output issuance accounting are usable.
- Native swap events are preserved separately; gross issuance is `swap_amount + fee_amount`.

## B. READY WITH LIMITATIONS

- March–April prices are real CoinGecko daily observations carried forward within the day; May uses Kaiko minute observations.
- UST supply is a daily on-chain address-balance sum carried forward, not an hourly observation.
- Direct LUNA total supply starts May 1; earlier core rows remain missing.
- Anchor events start May 6 and native redemptions start May 7; unknown earlier hours are missing, never zero.
- Concentration ends May 6 and is not extrapolated through the collapse.

## C. PROXY ONLY

- Prior `terra_dex_liquidity` and `terra_dex_depth` are `LEGACY_EXECUTION_CAPACITY_PROXY`: median and lower-quartile CoinGecko UST 24h market-wide volume divided by 24, held fixed. They are omitted from the new core table.
- Future model code must explicitly opt in; these values are neither Terraswap/Astroport reserves nor executable depth.

## D. MISSING / UNAVAILABLE

- **Terra DEX liquidity/depth:** package data, scripts, transaction extracts, prior builders, Terraswap/Astroport/pool/reserve keywords were searched. No historical pool reserve/state snapshots exist. This does not block price/Anchor Historical Fit; it limits liquidity Early Warning and parameterized Stress Testing.
- **LFG peg-defense execution:** LFG-labelled Anchor reserve funding exists, but no BTC reserve ledger or identified peg-defense executions exist. This does not block core Historical Fit; reserve-defense Early Warning is unavailable and reserve Stress Tests remain scenario-based.
- **Pre-May direct LUNA total supply:** the daily holder-balance table is not accounting-identical to direct total supply and is not substituted. This makes backing ratio partial from May 1.
- **Bridge flows:** prior directions were both mapped from the same Anchor deposit-state column without action filters. They are quarantined. Bridge is optional for current Historical Fit and Early Warning.

## Validation

- Native issuance hourly correlation: **0.999999892** over 168 hours.
- Native cumulative issuance: **6872102967292.583008 LUNA**; supply increase: **6799674843979.965820 LUNA**; relative error: **1.065170%**.
- Anchor cached-state validation: 419 overlap days; mean/median/max relative error **2.284526% / 1.289190% / 58.271323%**; correlation **0.999865132**.
- Pre-run Anchor validation through May 5: mean/median/max **0.230053% / 0.098863% / 4.607449%**; correlation **0.998866965**. Live epoch state is used during the run.
- UST node supply vs CoinGecko-implied supply: median relative error **0.630774%** over 74 days.
- LUNA holder-balance sum vs direct total supply: median relative error **3.110139%**; it is not used as total supply.
- Duplicate audit found 6 near-identical numeric pairs in the legacy May dataset; suspect mappings are quarantined rather than copied.

## Core-field availability

| Field | First valid | Last valid | Missing | Positive |
|---|---|---|---:|---:|
| block_height | 2022-03-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 0 | 1776 |
| ust_price | 2022-03-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 0 | 1776 |
| luna_price | 2022-03-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 0 | 1776 |
| ust_supply | 2022-03-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 0 | 1776 |
| luna_supply | 2022-05-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 1464 | 312 |
| anchor_total_deposits | 2022-03-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 0 | 1776 |
| anchor_deposit_flow | 2022-05-06T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 1584 | 183 |
| anchor_withdrawal_flow | 2022-05-06T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 1584 | 183 |
| ust_native_redemption_volume | 2022-05-07T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 1608 | 146 |
| gross_luna_issuance_from_native_swaps | 2022-05-07T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 1608 | 146 |
| backing_ratio | 2022-05-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | 1464 | 312 |
| top10_anchor_share | 2022-03-01T00:00:00+00:00 | 2022-05-06T23:00:00+00:00 | 168 | 1608 |
| top100_anchor_share | 2022-03-01T00:00:00+00:00 | 2022-05-06T23:00:00+00:00 | 168 | 1608 |

## Early-warning readiness

| Feature | Status | First calculable without look-ahead | Basis |
|---|---|---|---|
| UST depeg | AVAILABLE | 2022-03-01T00:00:00+00:00 | 1 - ust_price |
| depeg persistence | AVAILABLE | 2022-03-01T01:00:00+00:00 | lagged UST price |
| Anchor outflow stress | PARTIAL | 2022-05-06T00:00:00+00:00 | explicit withdrawal events only from May 6 |
| Anchor outflow acceleration | PARTIAL | 2022-05-06T01:00:00+00:00 | lagged explicit withdrawals |
| native redemption stress | PARTIAL | 2022-05-07T00:00:00+00:00 | native UST→LUNA events from May 7 |
| LUNA return 1h | AVAILABLE | 2022-03-01T01:00:00+00:00 | lagged market price |
| LUNA return 6h | AVAILABLE | 2022-03-01T06:00:00+00:00 | lagged market price |
| LUNA return 24h | AVAILABLE | 2022-03-02T00:00:00+00:00 | lagged market price |
| LUNA volatility | AVAILABLE | 2022-03-02T00:00:00+00:00 | trailing returns only |
| backing ratio | PARTIAL | 2022-05-01T00:00:00+00:00 | direct LUNA supply starts May 1 |
| backing deterioration | PARTIAL | 2022-05-01T01:00:00+00:00 | lagged backing ratio |
| DEX liquidity stress | UNAVAILABLE |  | no Terra pool reserve/depth history |
| large-holder concentration | PARTIAL | 2022-03-01T00:00:00+00:00 | daily series ends May 6 |
| reserve-defense activity | UNAVAILABLE |  | LFG Anchor funding is not peg-defense execution |

## Scientific interpretation

The `backing_ratio` is only a risk indicator: LUNA market capitalization divided by UST supply value. It must not be described as literal one-for-one collateralization.

The data layer is defensible for core price, supply (with explicit LUNA coverage limits), Anchor state, partial flow, and mechanism analyses. It is not complete for Terra-native DEX liquidity, bridge flows, or LFG peg-defense behavior; later model work must keep those channels optional or explicitly proxy/scenario based.
