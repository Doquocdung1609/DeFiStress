# Terra May 2022 final research report

## 1. Research question

Can an auditable agent-based mechanism reproduce the coupled Terra run dynamics without leaking the
May 8--13 evaluation path into calibration?

## 2. Terra mechanism

The tested hypothesis is holder exits → UST selling → arbitrage redemption → LUNA issuance →
dilution/backing deterioration → confidence loss → further exits.

## 3. Dataset and provenance

The 312 hourly rows cover May 1--13, 2022. Native-redemption provenance is `DIRECT_EVENT_OUTPUT_PROVENANCE_SUPPORTED_WITH_EXTRACT_LIMITATION`;
the raw 277,342 swaps aggregate to the processed hourly series with
0 mismatches.

## 4. Data limitations

Dataset status remains `QUALITY_WARNING`. Unavailable archival endpoints were not replaced with
fabricated observations. Curve and bridge fields, plus suspect duplicate mint/burn/sell fields, are
quarantined. DEX liquidity and depth are execution-capacity proxies only.

The former external-exit proxy was rejected. With `outside_ust = total_ust_supply - Anchor deposits`,
changes in outside UST combine issuance, redemption burns, and Anchor transfers; holder selling is a
transfer flow and is not identified by that stock difference. The old proxy contributed
8.51223e+07 UST in the 12-hour window. External
exit is now an explicit scenario parameter with hourly rates [0.0, 0.0025, 0.01].

## 5. Strict OOS design

V2 is frozen: 144 calibration rows through May 6 and 168 evaluation rows from May 7. It produced UST
RMSE 0.417488, collapse detected is
False, and its model-implied early-warning score was
0.0228306.
This is valid negative early-warning evidence: the pre-crisis inputs/specification did not forecast
the historical collapse.

## 6. Conditional replay design

The preserved V2 artifact is the **strict out-of-sample replay**. The final V4 model is a
**conditional historical mechanism replay, not a prediction**. Its trigger is the first observed
UST price below 0.99 (2022-05-07T22:00:00Z), its calibration window is exactly
12 hours through 2022-05-08T09:00:00Z, and its sealed
evaluation window starts 2022-05-08T10:00:00Z with 134 rows.
UST price impact remains `UNDERIDENTIFIED`: only
1 independently observable anchor-only rows jointly
have positive residual selling and downside price movement. The old point estimate is not used; the
main value and robustness range were declared as scenarios rather than fitted to holdout.

## 7. Baseline models

Four common-window structural comparator variants sharing the same `ConditionalABM` implementation
were evaluated; they are not four independently implemented models. Conditional ABM UST RMSE is
0.389604, versus static threshold 0.463873,
aggregate hazard 0.452572, and system dynamics
0.389611. The ABM does not materially outperform system dynamics.

## 8. ABM architecture

Depositor and external-holder exits create gross UST selling. Arbitrage throughput absorbs only an
economically executable hourly tranche. UST impact is driven by residual net selling; accepted
redemptions reduce UST supply and issue LUNA according to the protocol identity. A calibration-only
realization ratio accounts for the difference between gross issuance and observed net supply change.
LUNA impact form is selected by rolling-origin error inside calibration only. Confidence feedback is
bounded with `tanh`; prices and supplies have explicit physical bounds.

## 9. Protocol mechanism validation

Terra Core v0.5.20 burns `offerCoin`, then mints `swapCoin + feeCoin`; `swap_amount` is LUNA delivered
to the recipient and `fee_amount` is LUNA minted to the oracle module. Thus gross mint is their sum,
not `offer_amount / off-chain LUNA price`. In calibration, the old approximation has cumulative relative
error 0.556361 and direct event gross mint has error
0.552167. In the
sealed evaluation diagnostics, those errors are respectively
2.1342 and 0.0106516; the
direct event-output hourly correlation is
0.999999892.

## 10. Results

- UST RMSE: 0.389604; correlation: 0.9173549592822899
- LUNA log-RMSE: 5.4181; correlation: 0.9724488680486032
- Final LUNA supply relative error: 0.999879
- Cumulative Anchor withdrawal relative error: 0.662454
- UST < 0.90 F1: 0.661417
- Automated plausibility checks pass: True

The final model remains exploratory: it captures directional co-movement but materially underpredicts
the LUNA supply explosion. It crosses UST < 0.90 only for part of the observed crisis and does so
57.0 hours late; it never satisfies the joint UST/supply
collapse condition.

## 11. Timing analysis

Timing errors for UST thresholds .995/.99/.95/.90 are respectively
0.0,
-23.0,
12.0, and
57.0 hours. `null` means the model never crossed it.

## 12. Monte Carlo

Aleatory uncertainty uses 100 agent-RNG seeds with structural parameters fixed:
0 crossed the collapse condition and 100
did not. Separately, 100 fixed-agent-seed runs sample only predeclared proxy and
underidentified parameter ranges. Their final UST p05/p50/p95 are
0.200174/0.852659/0.977209, with
24 collapse runs. These layers must not be conflated.

## 13. Ablation

Removing external holders changes UST RMSE from 0.389604 to
0.452547. Whale heterogeneity has negligible incremental fit, and no ablation
reproduces collapse. Complexity therefore has limited demonstrated explanatory power here.

## 14. Sensitivity

Across all one-at-a-time proxy/mechanism variations, final UST ranges from
0.223142 to 0.982413. Depth and capacity uncertainty matters, but
no sensitivity value is used to select the primary result.

## 15. Data-quality concerns

The redemption direction and denoms are documented by replication code rather than carried in the
four-column extract. Duplicate synthetic-looking processed columns are excluded. The
expanding-window/moving-origin six-hour short-horizon checks cover calibration lengths [6, 12, 18, 24];
they do not validate the full May 9-13 collapse trajectory.

## 16. Interpretation

The evidence supports a plausible feedback mechanism and shows that external-holder/confidence
channels matter more than cohort heterogeneity in this specification. It does not establish that the
ABM uniquely explains Terra or adds material power over an aggregate system-dynamics baseline.

## 17. Limitations

No archival Terra LCD/RPC, Ethereum archival/Curve source, or indexed bridge source was configured.
The bundled native-swap extract documents direction externally but omits an action column, so its
status is not promoted to independently re-queried canonical ground truth. Wallet-level cohorts are
structural representations rather than identified wallets. Results are research replay evidence,
not investment advice and not a forecast.

## 18. Conclusion

**A. Early-warning evidence:** frozen strict OOS V2 did not forecast the crash. **B. Mechanism-replay
evidence:** conditional V4 gives high price-path correlations but misses collapse severity and supply
scale. **C. Counterfactual capability:** bounded ablations and sensitivities are implemented, but
counterfactual claims remain exploratory. Holdout metrics were not used to select a winning parameter
set. V4 prioritizes protocol identity and auditable failure over the old V3's implausible recursive
over-amplification.
