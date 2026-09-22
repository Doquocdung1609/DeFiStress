# Model Assumptions

## Scope and price channels

The V1 liquidation pair is WETH collateral and USDC debt. The snapshot can retain other exposures as aggregate collateral and debt value so Health Factor is portfolio-aware. Aave oracle, DEX execution, and external/reference prices remain separate. USDC is valued by its Aave oracle for protocol accounting and monitored independently for depeg.

## Health Factor

`HF = sum(collateral amount × oracle price × liquidation threshold) / sum(debt amount × oracle price)`. Eligibility begins below 1. A real position stores Aave `Pool.getUserAccountData` HF and an internal cross-check. An absolute mismatch above 0.02 is a visible `HF_MISMATCH`, commonly caused by aggregate-only non-WETH exposures.

## Aave liquidation approximation

The model uses a 50% close factor for HF above 0.95 when debt and collateral values are both at least 2,000 base currency units; otherwise it permits 100%. Partial actions must not leave 1,000 units or less of both debt and collateral. Seized WETH is `repaid USDC × liquidation bonus / WETH oracle price`, capped by available collateral. Exact EVM rounding, protocol liquidation fee, e-mode, isolation, deficit bookkeeping, and reserve-specific configuration remain fork-validation concerns.

## Liquidator behavior

Eligible does not mean executed. The single representative liquidator prioritizes lowest HF and then largest debt. Execution requires positive profit after DEX output, debt repayment, gas, funding, and risk buffer, and it respects per-step and total capital capacity. Reaction delay shifts availability by scenario steps.

## Uniswap execution model

The price-impact engine is not constant product. It uses the V3 Q64.96 square-root price, active liquidity, swap fee, initialized tick boundaries, and `liquidityNet` changes while moving upward in token1/token0 for WETH sales into a USDC-token0/WETH-token1 pool. Real snapshots scan a configurable symmetric `tickBitmap` word window at the pinned block. If those reads fail, direct `slot0` and active liquidity are retained and `TICK_DATA_INCOMPLETE` is raised; trades beyond the captured window still require Quoter or fork validation.

## Arbitrage behavior

When the DEX/reference spread exceeds 0.05%, the representative arbitrageur closes the configured fraction of the spread after its delay. Capacity 0 disables the balancing loop; capacity 100 restores the reference level in that step.

## Gas and funding

The fixture uses an 8 USDC base execution cost times the gas multiplier, a 5 bp funding cost, and a 5 bp execution-risk buffer. Real research should calibrate these values at the snapshot block.

## Bad debt and cascade

Bad debt is `sum(max(remaining debt value − recoverable collateral value, 0))` after executable actions. Unliquidated debt is reported separately for positions still below HF 1. A cascade exists when at least one position becomes liquidatable only after endogenous DEX feedback, represented by cascade depth at least 2. Amplification is total liquidated debt divided by wave-1 liquidated debt; a zero denominator returns null, never NaN.

## Monte Carlo

V1 supports a one-time deterministic shock and seeded stochastic perturbations around shock, liquidity haircut, and gas. Expected Shortfall 95% is the mean of the worst 5% of `bad debt + total liquidated debt`, an internal stress-loss proxy rather than accounting loss.

## Borrower sampling and coverage

Event discovery scans a stated lookback interval and can stop at a configured Top-N. The snapshot reports candidates, successful reads, failures, exclusions, pair cohort size, and coverage percentage. It must not represent a Top-N cohort as the entire Aave market.
