# Terra May 2022 Pack V6

## Why V5 `-AllowProxy` still stopped

V5 only allowed a DEX proxy when pre-cutoff native UST redemption turnover was
positive. In the current replication mapping, the 01–06 May pre-cutoff
redemption-flow series exists but has no positive turnover, so V5 correctly
refused to invent a nonzero liquidity/depth value.

## V6 proxy hierarchy

V6 keeps strict mode unchanged.

When `-AllowProxy` is enabled:

### Tier 1
Use positive native UST redemption turnover before the cutoff if available.

### Tier 2 fallback
If Tier 1 has no positive pre-cutoff activity, use the replication package's
`external/ustc-usd-max.csv` CoinGecko UST `total_volume`, using only 01–06 May.

Because CoinGecko `total_volume` is a rolling 24h market-wide volume snapshot:

- `terra_dex_liquidity` proxy =
  median pre-cutoff daily `total_volume` / 24
- `terra_dex_depth` proxy =
  25th percentile pre-cutoff daily `total_volume` / 24

These are **market execution-capacity proxies**, not observed Terraswap/Astroport
pool reserves and not true order-book depth.

Therefore:
- dataset status = `QUALITY_WARNING`
- source type = `REPLICATION_ONCHAIN_WITH_PRECRISIS_PROXIES`
- provenance explicitly records that these two fields are proxies
- no observations after 2022-05-06 are used to calibrate them

This is intended to unblock the current simulation pipeline while preserving
the anti-lookahead rule. For the final thesis, exact historical Terra DEX state
should still be sourced separately if available.

## Run

```powershell
& ".\terra_may2022_v1_pack\terra_may2022_v1_pack\run_build_and_import.ps1" -AllowProxy
```

Then inspect:

```powershell
Get-Content ".\data\raw\terra_may2022_v1\missing_fields.json"
Get-Content ".\data\raw\terra_may2022_v1\mapping_report.json"
(Import-Csv ".\data\processed\terra_may2022_v1.csv").Count
```
