# TÁI LẬP

## Lệnh chuẩn

```powershell
.\.venv\Scripts\python.exe scripts\run_full_research_pipeline.py --research
```

## Provenance

- Source code commit: `620746513dec3a7afad00eb8ce10b0d0add538cc`
- Artifact bundle commit: `c4c9a363adfc55addd6da1fd1bf5c15f500eff97`.
- Metadata finalization commit: là commit chứa cập nhật provenance này; không tự ghi SHA của chính nó để tránh vòng lặp tự tham chiếu.
- Canonical Aave: `data/processed/mainnet/aave_uniswap_snapshot_26045352.json`; SHA-256 `553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99`.
- Canonical Terra: `data/processed/terra_extended/terra_state_hourly_20220301_20220513.parquet`; SHA-256 `0e338c3d096600d93bf29884370e46cb5e260820e910b483a7f19048521dcac1`.
- Native swaps: `data/processed/terra_extended/terra_native_swaps.parquet`; SHA-256 `e1e01ed390eb82356141e924c99d7af8bd0549534defb40dd172d797a0a485a1`.
- Python: `3.12.14 (main, Aug 25 2026, 14:01:42) [MSC v.1944 64 bit (AMD64)]`; Node: `v22.13.1`.
- Seeds: 20260914, 20260915, 20260916; Terra fixed seeds nằm trong manifest con.
- Pipeline mode: research; Aave MC runs/scenario: 200.

`manifest.json` chứa hash output. Deterministic Professor Demo và Monte Carlo fixed-seed được chạy hai lần và phải identical.
