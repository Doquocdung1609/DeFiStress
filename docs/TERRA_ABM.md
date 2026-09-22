# Terra Agent-Based Model

The Terra ABM is separate from Aave Health Factor semantics. It uses vectorized cohorts (`WHALE`, `LARGE`, `MEDIUM`, `SMALL`) for practical 1k–100k-agent configurations while retaining representative agent events.

Depositor exit probability combines depeg, backing deterioration, observed large-holder activity, liquidity stress, a cohort baseline, confidence sensitivity, and reaction delay. Events record each contribution.

The arbitrageur acts only when redemption value minus purchase, trading, slippage, settlement/risk, and minimum-profit costs is positive. The protocol agent burns redeemed UST and mints LUNA under an explicit friction simplification. DEX impact depends on modeled order flow and remaining liquidity. Reserve intervention is optional, capacity-bound, delayed through configuration, and never assumed effective.

Invariants include nonnegative supplies, withdrawals capped by balances, reserve spending capped by capital, arbitrage capital limits, monotonic event time, and deterministic same-seed output.
