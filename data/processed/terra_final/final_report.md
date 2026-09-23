# Terra May 2022 final research report

## 1. Research question

Can an auditable agent-based mechanism reproduce the coupled Terra run dynamics without leaking the
May 8--13 evaluation path into calibration?

## 2. Terra mechanism

The tested hypothesis is holder exits → UST selling → arbitrage redemption → LUNA issuance →
dilution/backing deterioration → confidence loss → further exits.

## 3. Dataset and provenance

The 312 hourly rows cover May 1--13, 2022. Native-redemption provenance is `PROVENANCE_SUPPORTED_WITH_EXTRACT_LIMITATION`;
the raw 277,342 swaps aggregate to the processed hourly series with
0 mismatches.

## 4. Data limitations

Dataset status remains `QUALITY_WARNING`. Unavailable archival endpoints were not replaced with
fabricated observations. Curve and bridge fields, plus suspect duplicate mint/burn/sell fields, are
quarantined. DEX liquidity and depth are execution-capacity proxies only.

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

## 7. Baseline models

Four common-window structural variants were evaluated. Conditional ABM UST RMSE is
0.426094, versus static threshold 0.463873,
aggregate hazard 0.461703, and system dynamics
0.426096. The ABM does not materially outperform system dynamics.

## 8. ABM architecture

Depositor and external-holder exits create gross UST selling. Arbitrage throughput absorbs only an
economically executable hourly tranche. UST impact is driven by residual net selling; accepted
redemptions reduce UST supply and issue LUNA according to the protocol identity. A calibration-only
realization ratio accounts for the difference between gross issuance and observed net supply change.
LUNA impact form is selected by rolling-origin error inside calibration only. Confidence feedback is
bounded with `tanh`; prices and supplies have explicit physical bounds.

## 9. Protocol mechanism validation

During conditional calibration, gross identity mint is
533529 LUNA and the
observed positive supply delta is
373909, implying a
calibration-only realization ratio of
0.700822. The evaluation ratio
falls to 0.319061; this instability
is a material limitation, not a parameter retuned on holdout.

## 10. Results

- UST RMSE: 0.426094; correlation: 0.9177519780130398
- LUNA log-RMSE: 6.15994; correlation: 0.9096038897570329
- Final LUNA supply relative error: 0.999887
- Cumulative Anchor withdrawal relative error: 0.646832
- UST < 0.90 F1: 0
- Automated plausibility checks pass: True

The final model remains exploratory: it captures directional co-movement but materially underpredicts
the LUNA supply explosion and does not reproduce the UST < 0.90 collapse state.

## 11. Timing analysis

Timing errors for UST thresholds .995/.99/.95/.90 are respectively
0.0,
-19.0,
54.0, and
None hours. `null` means the model never crossed it.

## 12. Monte Carlo

100 seeded runs were evaluated. 0 crossed the
model collapse condition and 100 did not. Full p05/p25/p50/p75/p95
time-series quantiles are in `monte_carlo.json`; one seed is not presented as the uncertainty result.

## 13. Ablation

Removing external holders changes UST RMSE from 0.426094 to
0.4617. Whale heterogeneity has negligible incremental fit, and no ablation
reproduces collapse. Complexity therefore has limited demonstrated explanatory power here.

## 14. Sensitivity

Across all one-at-a-time proxy/mechanism variations, final UST ranges from
0.899174 to 0.945479. Depth and capacity uncertainty matters, but
no sensitivity value is used to select the primary result.

## 15. Data-quality concerns

The redemption direction is documented by the replication package rather than carried in the
four-column extract. Duplicate synthetic-looking columns are excluded. Rolling-origin 6-hour
forecast checks cover calibration lengths [6, 12, 18, 24].

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
