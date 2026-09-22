# Local Fork Validation

This harness is for localhost fork evidence only. It has no Mainnet broadcast script.

Required variables are `ETH_ARCHIVE_RPC_URL`, `SNAPSHOT_BLOCK`, and `BORROWER_ADDRESS` from a real immutable snapshot. The executable probes additionally require a borrower that was liquidatable at that block, funded public accounts that already held USDC/WETH at that block, and explicit test amounts:

```text
LIQUIDATABLE_BORROWER
FUNDED_LIQUIDATOR
FUNDED_WETH_HOLDER
DEBT_TO_COVER
WETH_QUOTE_AMOUNT
WETH_SWAP_AMOUNT
UNISWAP_FEE
```

Run:

```bash
cd contracts/validation
forge test -vv
```

The harness checks block-pinned Aave account state, liquidation eligibility, a local-fork `liquidationCall`, QuoterV2 output, and a SwapRouter02 WETH→USDC execution. It never broadcasts: prank/impersonation is scoped to the ephemeral fork. Record model/reference repay, seize, quote, and relative error in `validation_report.json`. Do not mark PASS when the archive provider, funded historical samples, or executable case is absent.
