# Terra May 2022 Pack V5

V5 resolves the two remaining historical-state mappings found by V4 diagnostics.

## 1) block_height

Source:
`data/anchor/Anchor_global_stats_fullnode.parquet`

The diagnostic found:
- 1,393 observations in the expanded May window
- monotonically non-decreasing block height
- a maximum source gap of 571 minutes
- exactly nine missing hourly observations on 13 May

That interval aligns with the historical Terra chain halt. V5 therefore treats
block height as a state variable and carries the last committed height through
ONLY the bounded halt interval (02:00–10:00 UTC on 13 May). It does not linearly
interpolate block production.

## 2) anchor_total_deposits

V5 keeps the protocol-state derivation:

`prev_aterra_supply * prev_exchange_rate * 1e-6`

The `1e-6` unit conversion is validated using only 1–6 May (pre-cutoff) against
`Anchor_daily_stats.parquet / deposit balance`.

Diagnostic pre-cutoff median relative error:
~0.595%

The same nine hourly holes occur during the chain halt. Because no new on-chain
state is committed while the chain is halted, V5 carries the last committed
Anchor state through ONLY that bounded interval.

## 3) DEX liquidity/depth

Strict mode still refuses to fabricate:
- `terra_dex_liquidity`
- `terra_dex_depth`

Expected strict result after V5:
only those two fields remain missing.

Research-running mode (`-AllowProxy`) may then use the already documented
pre-cutoff execution-capacity proxies and MUST remain `QUALITY_WARNING`.

## Run

```powershell
& ".\terra_may2022_v1_pack\terra_may2022_v1_pack\run_build_and_import.ps1"
```

Inspect:

```powershell
Get-Content ".\data\raw\terra_may2022_v1\missing_fields.json"
```

If only the two DEX fields remain:

```powershell
& ".\terra_may2022_v1_pack\terra_may2022_v1_pack\run_build_and_import.ps1" -AllowProxy
```
