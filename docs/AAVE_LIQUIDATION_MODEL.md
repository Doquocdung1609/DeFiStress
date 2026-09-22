# Aave V3 Liquidation Model

## Official semantics used

The model follows the maintained `aave-dao/aave-v3-origin` liquidation logic and Aave's official liquidation guidance as checked on 14 September 2026. A borrower is eligible below HF 1. V3 uses a default 50% close factor near the boundary and permits 100% at or below HF 0.95 or for small debt/collateral conditions. V3.3+ also enforces dust rules for residual debt and collateral.

Official sources:

- https://github.com/aave-dao/aave-v3-origin/blob/main/src/contracts/protocol/libraries/logic/LiquidationLogic.sol
- https://github.com/aave-dao/aave-v3-origin/blob/main/docs/3.3/Aave-v3.3-features.md
- https://aave.com/help/borrowing/liquidations
- https://github.com/aave-dao/aave-address-book

## Off-chain implementation

`sim/lending/liquidation.py` selects the close factor, caps debt repayment by available WETH collateral, applies the reserve liquidation bonus, and avoids residual values below the documented thresholds. The simulation records repay, seize, gas, expected profit, DEX execution, price change, and HF before/after.

## Differences from exact EVM execution

The model does not claim wei-exact parity for scaled aToken/vToken indexes, ray rounding, reserve deficit accounting, protocol fee transfer, e-mode price sources, isolation ceilings, or all reserve-specific flags. A fork report must quantify those differences. Without an archive RPC and Foundry, the correct status is `NOT RUN`, never `PASS`.

