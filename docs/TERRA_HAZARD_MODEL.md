# Terra Withdrawal Hazard Model

The preferred research model is Cox proportional hazards when wallet-level event durations and censoring are available. Required outputs are coefficients, hazard ratios, standard errors, survival probabilities, and assumption checks.

The bundled fixture lacks defensible wallet event durations. The implementation therefore reports `AGGREGATE_DISCRETE_HAZARD_FALLBACK`. Its baseline withdrawal intensity is calibrated only from pre-cutoff Anchor flows; transparent pre-specified coefficients cover depeg, backing stress, liquidity stress, and large-holder intensity. Standard errors and proportional-hazards tests are explicitly `UNAVAILABLE`/not applicable.

This fallback must not be presented as a fitted Cox result.
