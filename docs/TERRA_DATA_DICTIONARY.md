# Terra Data Dictionary

All timestamps are timezone-aware UTC. Monetary quantities use asset units or USD as named; ratios are unitless.

| Field | Unit | Meaning |
|---|---:|---|
| `timestamp` | UTC | Hour represented by the observation |
| `block_height` | Terra block | Source block or aligned block |
| `ust_price`, `luna_price` | USD | Asset reference price |
| `ust_supply`, `luna_supply` | token | Circulating/model supply |
| `anchor_total_deposits` | UST | Anchor deposit balance |
| `anchor_deposit_flow`, `anchor_withdrawal_flow` | UST/hour | Gross flows |
| `ust_native_redemption_volume` | UST/hour | Protocol redemption volume |
| `luna_minted_from_redemption`, `luna_burned` | LUNA/hour | Mint/burn flows |
| `ust_dex_sell_volume` | UST/hour | DEX sell pressure |
| `terra_dex_liquidity`, `terra_dex_depth` | USD | Aggregate liquidity/depth |
| `curve_*` | mixed | Secondary Ethereum Curve evidence; nullable |
| `bridge_*` | token/hour | Cross-chain flow; nullable |
| `top10_anchor_share`, `top100_anchor_share` | ratio | Concentration indicators |
| `ust_depeg_bps` | basis points | `(1 - USTPrice) × 10,000`, floored at zero |
| `backing_ratio` | ratio | `LUNA market cap / UST supply value at target peg` |

`backing_ratio < 1` is a risk indicator, not a mathematical guarantee of collapse.
