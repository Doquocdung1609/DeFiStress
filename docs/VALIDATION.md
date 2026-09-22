# Validation

## Data validation

Every real snapshot pins chain ID, block number, block hash, timestamp, address-book commit, contract addresses, pool fee, and selection rule. Direct Aave and Uniswap calls use the same block identifier. Missing or incomplete sources produce named quality flags.

## Health Factor validation

Unit tests cover weighted collateral and zero-debt behavior. Real positions compare the internal portfolio approximation with `Pool.getUserAccountData`; absolute error above 0.02 produces `HF_MISMATCH` with the borrower pseudonym.

## Uniswap validation

Property tests require zero-size zero impact, positive output, decreasing WETH/USDC price for WETH sales, monotone non-improving execution price with size, finite values, safe tick crossing, and correct bitmap decoding across signed word positions. Small/medium/large real quote error against QuoterV2 or a local fork remains environment-dependent.

## Liquidation validation

Tests cover the HF boundary, close-factor branches, collateral and debt caps, nonnegative balances, ordered events, and liquidator profitability/capacity. The Foundry harness is local-only.

## Monte Carlo validation

The same seed produces identical distributions. Summary quantiles and probability remain bounded and use the deterministic engine unchanged.

## Reproducibility validation

The golden fixture is versioned and intentionally creates Wave 1 followed by Wave 2. Exports include snapshot, scenario, seed, model version, Git commit, events, positions, time series, and plots.

## Fork validation status

The local-only harness contains account-state, eligibility, `liquidationCall`, QuoterV2, and SwapRouter02 probes. The current machine must have both `ETH_ARCHIVE_RPC_URL` and Foundry/Anvil plus suitable funded historical sample accounts. The validation endpoint reports missing prerequisites explicitly and cannot return `PASS` without evidence.
