# Model Benchmark

| Model | Purpose | Strength | Limitation |
|---|---|---|---|
| Threshold | Pre-specified alert baseline | Interpretable | No endogenous heterogeneity |
| Hazard | Withdrawal-risk baseline | Direct behavioral interpretation | Aggregate fallback without wallet durations |
| System Dynamics | Aggregate feedback loop | Transparent nonlinear mechanism | No individual cohorts |
| ABM | Heterogeneous behavioral mechanism | Timing/decision explanations | More assumptions and computation |

Every model is evaluated on the same dataset, cutoff, window, and event definitions. Rows report UST/LUNA MAE/RMSE, supply and withdrawal error, event timing, collapse detection, false alarms, and runtime. No winner is automatically declared.

The contribution is integration, reproducibility, historical ground-truth validation, cross-model comparison, and counterfactual experimentation—not novelty from merely including a model family.
