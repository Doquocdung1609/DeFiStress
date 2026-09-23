# Terra May 2022 Pack V4

V4 fixes a Pandas-specific bug in V3.

## Bug fixed

V3 used Python boolean coalescing on Pandas Series:

```python
series_a or series_b
```

A Pandas Series has no single truth value, so Pandas raises:

`ValueError: The truth value of a Series is ambiguous`

V4 uses explicit `is None` fallback logic for both:

- `ust_supply`
- `anchor_total_deposits`

No research assumptions or data mappings were changed in this patch.

## Recommended run

First run strict mode:

```powershell
& ".\terra_may2022_v1_pack\terra_may2022_v1_pack\run_build_and_import.ps1"
```

Then inspect:

```powershell
Get-Content ".\data\raw\terra_may2022_v1\missing_fields.json"
```

If only DEX liquidity/depth remain missing, run the proxy-labelled research mode:

```powershell
& ".\terra_may2022_v1_pack\terra_may2022_v1_pack\run_build_and_import.ps1" -AllowProxy
```

Proxy mode must remain `QUALITY_WARNING`, not `REAL_HISTORICAL`.
