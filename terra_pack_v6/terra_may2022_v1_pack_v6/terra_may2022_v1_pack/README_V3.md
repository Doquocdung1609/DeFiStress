# Terra May 2022 Pack V3

## What V3 fixes

V3 uses explicit historical mappings discovered from the replication package:

1. `block_height`
   - `Anchor_global_stats_fullnode.parquet`
   - DatetimeIndex `minute`
   - column `height`
   - last known block at or before each UTC hour

2. `luna_supply`
   - `native_swaps/luna_total_supply_run.parquet`
   - DatetimeIndex `time`
   - column `luna_supply`

3. `ust_supply`
   - `daily_balances/columbus-5-lunaust-supply-breakdown-fullnode.parquet`
   - filter native denom `uusd`
   - sum balances per daily snapshot
   - convert microUST to UST by `/ 1e6`
   - forward-fill the state within the day

4. `anchor_total_deposits`
   - `Anchor_global_stats_fullnode.parquet`
   - derived protocol state: `prev_aterra_supply * prev_exchange_rate`
   - unit scaling is validated using ONLY pre-cutoff observations from
     `Anchor_daily_stats.parquet` / `deposit balance`
   - strict mode rejects the mapping if pre-cutoff median relative error > 5%

## Important: DEX liquidity and depth

The replication package does not expose full Terra DEX pool reserve/depth state for
01–13 May 2022. V3 therefore DOES NOT call those exact historical observations.

### Strict mode
Run without `-AllowProxy`.

Expected behavior:
- V3 should recover the four exact fields above.
- If no real Terra DEX pool state exists, strict build still stops rather than fabricating it.

### Research-running mode
Run with `-AllowProxy`.

V3 creates two clearly labelled model-input proxies:
- `terra_dex_liquidity`: median trailing-24h PRE-CUTOFF native UST redemption turnover
- `terra_dex_depth`: 95th percentile hourly PRE-CUTOFF native UST redemption flow

Both are calibrated only with `t <= 2022-05-06 23:00 UTC`, held fixed through
evaluation, and marked `exact=false`. The resulting dataset is
`QUALITY_WARNING`, never `REAL_HISTORICAL`.

This mode is suitable for running the current four-model software pipeline while
the team separately sources exact Terraswap/Astroport historical pool state.

## Commands

Replace the old two files with the V3 versions and unblock them.

First audit strict mapping:

```powershell
& ".\terra_may2022_v1_pack\terra_may2022_v1_pack\run_build_and_import.ps1"
```

If it stops only on:
- `terra_dex_liquidity`
- `terra_dex_depth`

then the four newly recovered historical mappings are working.

To run the research pipeline now with explicit pre-cutoff execution-capacity
proxies:

```powershell
& ".\terra_may2022_v1_pack\terra_may2022_v1_pack\run_build_and_import.ps1" -AllowProxy
```

The final status MUST be `QUALITY_WARNING`, not `REAL_HISTORICAL`.
