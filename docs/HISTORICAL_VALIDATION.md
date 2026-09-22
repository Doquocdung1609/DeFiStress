# Historical Validation

Continuous metrics include MAE, RMSE, MAPE where denominators are nonzero, sMAPE, correlation, and UST directional accuracy. Variables cover UST/LUNA price, UST/LUNA supply, Anchor withdrawal, DEX liquidity, and backing ratio.

Default event thresholds are minor depeg `<0.99`, major `<0.95`, and severe/death-spiral price condition `<0.90`; they are explicit and configurable. Timing error is simulated event time minus actual event time in hours. Classification metrics include precision, recall, F1, false-positive rate, and false-negative rate.

Plots are supporting evidence only. Model comparison does not assign an arbitrary composite score or automatic winner.
