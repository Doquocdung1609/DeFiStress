# Uniswap V3 registered tick-range coverage

Status: **PASS_REGISTERED_RANGE_COMPLETE**, 6/6 pool-block cases, each repeated twice. Full legal pool domain is explicitly **not reconstructed**.

Integration input: `3c3928a9b71348648980de92fa80b31b6d2a647d`. V1 annotated tag `v1.0.0-scientific-baseline`, object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`. No V1/Phase01-A file is modified.

A/B/C source: `6e5285f04d1d5ab2900b51389cc3c025c9b64f42`; [actual collection run 39212923329](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39212923329). Local paths below are relative to this directory. Evidence is preserved at `evidence/full/`; D has its own source/run and separate `evidence/borrower_repair/`.

## Scope fixed before collection

`SAMPLE_REGISTRATION.json`: historical current tick ±6932, approximately half-to-twice price in tick space, rounded inward to usable tick spacing and clamped to legal ticks. Fetch every intersecting bitmap word and every initialized tick inside the required band. There is no eight-tick count truncation. All words outside the band remain `OUT_OF_SCOPE_NOT_RECONSTRUCTED`; bitmap words intersecting the band may also contain outside-band bits that are deliberately excluded from the required tick list.

P3000 = `0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8`, fee 3000 millionths (0.30%), spacing 60. P500 = `0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640`, fee 500 millionths (0.05%), spacing 10. Token0 USDC (6 decimals), token1 WETH (18); factory/pool identity and historical decimals checked. See registration for exact token/factory addresses.

| Block | Pool | Current tick | Required inclusive ticks | Bitmap words | Initialized tick instances | Active liquidity, raw protocol L | Two-pass content match |
|---|---|---:|---|---:|---:|---:|---|
| 26045352 | P3000 | 197332 | 190440…204240 | 2 | 231 | 3206024567373452858 | PASS |
| 26045352 | P500 | 197349 | 190420…204280 | 6 | 1164 | 2897773765975215625 | PASS |
| 26038152 | P3000 | 197042 | 190140…203940 | 2 | 231 | 3148756851099163801 | PASS |
| 26038152 | P500 | 197064 | 190140…203990 | 6 | 1153 | 2984212788208198405 | PASS |
| 26030952 | P3000 | 197216 | 190320…204120 | 2 | 231 | 3151563998189505951 | PASS |
| 26030952 | P500 | 197233 | 190310…204160 | 6 | 1159 | 2982914187753690775 | PASS |

Total **4169 initialized tick instances across six pool-block cases** (not globally unique ticks); 24 bitmap-word instances per pass. Missing required words/ticks = 0. Exact sqrtPriceX96, bitmap integers, initialized tick raw tuples and gross/net liquidity are in `evidence/full/components/{block}-pass{1,2}-{P3000,P500}.json.gz`.

## Validation semantics

Contiguous required words; initialized-bit/list consistency; no duplicate tick indices; gross liquidity ≥ absolute net liquidity; current sqrt-price/tick consistency; historical token ordering/fees/decimals; no mixed-block calls. Active liquidity is the observed `liquidity()` at current tick, not sum of all position liquidity. All integers use exact arbitrary precision; raw L and sqrtPriceX96 are protocol units, not USD or token inventory.

Interval liquidity is reconstructed by applying signed net changes, anchored at observed active liquidity, and must stay nonnegative. The derived lower-bound liquidity is **not an independent boundary observation**. Sum(net)=0 is inapplicable to a partial band. This audit does not validate executable swap execution, whole-pool depth, gas costs, or causal market transmission. A later scenario exceeding the band must be quarantined or collect a newly registered wider range before use.
