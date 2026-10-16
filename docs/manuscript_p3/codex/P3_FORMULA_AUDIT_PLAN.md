# P3 Formula Audit Plan

Status: `P3-G0 — FORMULA INVENTORY, NOT MANUSCRIPT PROSE`

Scientific source lock: `3f6e5302483681209e2408531eb5a15389f9fded`
Transformation version: `p3-g0-builder-v1`

The classifications below prevent a project approximation from being presented as a protocol formula. Variables and units must be repeated in the eventual equation caption or adjacent text.

| Formula ID | Classification | LaTeX display | Variables / units | Conditions and source locator | RQ | Simplification / required limitation |
|---|---|---|---|---|---|---|
| P3F01 | Protocol-shaped project implementation | `$HF_i(t)=\frac{\sum_j q^C_{ij}P^C_j(t)LT_j}{\sum_k q^D_{ik}P^D_k(t)}$` | `q`: token quantity; `P`: USD/token; `LT`: ratio; HF dimensionless | `sim/lending/health_factor.py:5`; portfolio implementation `sim/schemas.py:29` | RQ1, RQ3, RQ5, RQ6 | Aave-style aggregate; project cohort has WETH/USDC route plus aggregate other collateral/debt. Oracle policy is separate. |
| P3F02 | Project route eligibility rule | `$Eligible_i = [HF_i<1]\land[D^{USDC}_i>0]\land[C^{WETH}_i>0]$` | Boolean; modeled USDC debt and WETH collateral quantities | `sim/lending/liquidation.py:38` | RQ1, RQ3 | Portfolio HF eligibility is not route eligibility, attempted processing or positive-debt execution. |
| P3F03 | Protocol-shaped project liquidation mapping | `$q_{repay}=CF(HF,D,C)D^{USDC};\quad q_{seize}=q_{repay}\,b/P_{WETH}$` | `q_repay`: USDC token; `q_seize`: WETH; `P_WETH`: USD/WETH; `b`: liquidation-bonus multiplier. Dimensional equality uses the baseline convention `1 USDC token = 1 USD`. | `sim/lending/liquidation.py:26`, `:38`; scoped limitation `P2:C35` | RQ3, RQ6 | Verbatim project approximation: close-factor and dust rules are implemented, but the seize mapping omits an explicit `P_USDC/USD` factor. It is not a general USDC-depeg execution identity or contract-fork evidence and is not selected among the eight Work manuscript equations. |
| P3F04 | Project-specific liquidator decision | `$\Pi=Q_{USDC}^{out}-q_{repay}-Gas-Funding-Risk$`; execute if eligible, within capital/capacity and `$\Pi>\Pi_{min}$` | USDC-equivalent modeled quantities | `sim/agents/liquidator.py:33` | RQ3 | One representative liquidator, fixed cost/risk rules, no capital recycling or competitive bot market. |
| P3F05 | Uniswap V3 identity used by the project | `$\sqrt{P}_{X96}=2^{96}\sqrt{10^{d_1-d_0}/P_{WETH}}$`; `$tick=\lfloor\log_{1.0001}((\sqrt{P}_{X96}/2^{96})^2)\rfloor$` | `P`: USDC/WETH; token decimals; tick integer | `sim/dex/uniswap_v3.py:26`, `:35` | RQ2, RQ4 | Token ordering is USDC token0/WETH token1. Tick rounding is the project implementation. |
| P3F06 | Project swap calculation across initialized ticks | `$\Delta y=L(\sqrt{P_b}-\sqrt{P_a});\quad \Delta x=L(1/\sqrt{P_a}-1/\sqrt{P_b})$` | raw token1 in and token0 out; active liquidity `L` | `sim/dex/uniswap_v3.py:77` | RQ2, RQ4 | Applied piecewise with fee and liquidityNet tick crossing; quotes are model outputs, not funded Mainnet swaps. |
| P3F07 | Display transformation | `$Impact_{sale}=|P_{DEX,post-sale}-P_{ref}|/P_{ref}$`; `$Residual_{arb}=|P_{DEX,post-arb}-P_{ref}|/P_{ref}$` | dimensionless ratio, normally displayed as percent | `sim/engine/run.py:143`, `:248`, metrics `:278`–`:282` | RQ2, RQ4 | Immediate impact and residual spread are distinct; deprecated `max_price_impact` aliases residual spread. |
| P3F08 | Hypothetical model policy | `$P_A=\min(P_{ref},P_{DEX});\ P_B=P_{ref};\ P_C=P_{ref}+\alpha(\overline{P}_{DEX,lag}-P_{ref})$`, capped adverse | USD/WETH; alpha ratio; lag/window steps | `sim/oracle.py:43` | RQ1, RQ2, RQ4 | A/B/C are sensitivity policies, not verified Aave or Chainlink feeds. C is causal in time and uses completed waves only. |
| P3F09 | Analytical identity inside the model | `$D_{USD}=q_{USDC}P_{USDC/USD}+D_{other,USD}$` | USDC token quantity, USD/USDC, USD | `sim/schemas.py:25` | RQ5 | Isolates debt valuation only; no redemption, settlement, confidence or stablecoin-liquidity channel. |
| P3F10 | Project metric definition | `$BadDebt=\sum_i\max(0,D_{i,USD}-C_{i,USD})$` | USD-equivalent modeled uncovered debt | `sim/metrics/risk.py:9` | RQ2, RQ5 | Not realized financial loss. It excludes execution and recovery economics not represented in the formula. |
| P3F11 | Project metric definition | `$UnliquidatedDebt=\sum_{i:HF_i(LT^*)<1}D_{i,USD}$` | USD-equivalent debt | `sim/metrics/risk.py:20`; call with scenario LT `sim/engine/run.py:262` | RQ3, RQ6 | Use scenario LT when overridden; the legacy recorded-LT value is comparison-only. |
| P3F12 | Analytical identity inside the model | `$Amplification=L_{total}/L_{direct}$` when `$L_{direct}>0$` | ratio; liquidated debt numerator/denominator use the same unit | `sim/metrics/risk.py:36` | RQ1, RQ2 | Undefined when direct liquidation is zero; not a multiplier of realized loss. |
| P3F13 | Project event/time definition | `$Depth=\max(wave\ with\ positive\ repaid\ debt)$`; recovery is the first post-exceedance wave-end time with residual `≤0.5%` | waves; seconds | `sim/engine/run.py:246`–`:287` | RQ1, RQ3, RQ4 | Max-waves=100 is a cap, not observed depth. Delay and time-to-recovery are different measures. |
| P3F14 | Policy mechanism identity | `$BorrowCapacity=\sum_j C_j LTV_j$`; LT enters HF; bonus enters seized collateral and expected profit | USD, ratios, WETH/USDC | `sim/schemas.py:17`; `sim/lending/liquidation.py:38`; locked RQ6 results | RQ6 | LTV, liquidation threshold and bonus must never be substituted for one another. Frozen cohort omits behavioral response. |
| P3F15 | Display-only statistical formula, approval required | `$\hat p=k/n$`; Wilson score interval only for locked `k/n` pairs | count/paths and dimensionless interval | P2:C23; `data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json` | RQ1 | G0 will not calculate a new CI. Any manuscript interval must reproduce an already locked pair and remain model-conditional. |

## Formula gate

Every produced equation must carry: formula class, source locator, variable dictionary, units, cohort/scenario/policy and the simplification text above. A missing field blocks chapter technical sign-off.

Content SHA-256 (UTF-8, excluding this checksum line): `d43fd796e055260ee656b7150bae8b778a982cf6c33e13264288d1fe56ed3877`
