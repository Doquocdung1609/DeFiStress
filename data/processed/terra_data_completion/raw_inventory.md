# Terra raw/source inventory

Inventory entries: **342** (including ZIP members as `zip://` virtual paths).

Raw files and the original ZIP were read only. Generated completion outputs are deliberately excluded so reruns remain stable.

## Formats

| Format | Files |
|---|---:|
| NO_EXTENSION | 5 |
| csv | 22 |
| json | 27 |
| md | 24 |
| parquet | 62 |
| png | 46 |
| ps1 | 11 |
| py | 120 |
| r | 2 |
| sh | 2 |
| tex | 12 |
| ts | 2 |
| tsx | 3 |
| txt | 2 |
| zip | 2 |

## Inventory

| Path | Format | Rows | Time field | Start | End | Candidate use |
|---|---|---:|---|---|---|---|
| `audit_terra_may2022_v1.py` | py | 235 |  |  |  | metadata/code/audit context |
| `backend/alembic/versions/0002_terra_research.py` | py | 28 |  |  |  | metadata/code/audit context |
| `backend/app/adapters/terra/__init__.py` | py | 5 |  |  |  | metadata/code/audit context |
| `backend/app/adapters/terra/history.py` | py | 53 |  |  |  | metadata/code/audit context |
| `backend/app/services/terra_datasets.py` | py | 135 |  |  |  | metadata/code/audit context |
| `backend/app/services/terra_export.py` | py | 98 |  |  |  | metadata/code/audit context |
| `backend/app/terra_api.py` | py | 412 |  |  |  | metadata/code/audit context |
| `data/processed/model_v2/terra_abm_v2_strict_oos.json` | json | 1 |  |  |  | existing model artifact; audit only |
| `data/processed/terra_final/ablation.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/conditional_abm_final.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/conditional_benchmark.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/data_quality.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/final_metrics.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/final_report.md` | md | 164 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/model_diagnostics.json` | json | 1 |  |  |  | existing model artifact; audit only |
| `data/processed/terra_final/monte_carlo.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/parameter_uncertainty_ensemble.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/protocol_mechanism_validation.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/reproducibility_manifest.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/rolling_origin.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/sensitivity.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/strict_oos_v2.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_final/test_evidence.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_may2022_v1.csv` | csv | 312 | timestamp | 2022-05-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | metadata/code/audit context |
| `data/processed/terra_may2022_v1_audit.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_may2022_v1_import_manifest.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_may2022_v1_validation.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/processed/terra_model_benchmark_v1.json` | json | 1 |  |  |  | existing model artifact; audit only |
| `data/raw/terra_may2022_v1/evidence_map.json` | json | 20 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/mapping_report.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/missing_fields.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/missing_source_detail.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/provenance_manifest.json` | json | 1 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/.extracted` | NO_EXTENSION |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/.gitignore` | NO_EXTENSION |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/config.py` | py | 36 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig01_anchor_net_rates.py` | py | 81 |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig02_ust_supply_by_entity.py` | py | 91 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig03_anchor_cashflow.py` | py | 155 |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig04_network_volume.py` | py | 251 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig05_market_cap.py` | py | 76 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig06_anchor_concentration.py` | py | 103 |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig07_wallet_A_B.py` | py | 99 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig08_curve_swaps.py` | py | 126 |  |  |  | secondary Ethereum Curve trade channel |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig09_binance_ustusdt.py` | py | 91 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig10_run_outflows.py` | py | 103 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig11_swap_arbitrage.py` | py | 103 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig12_death_spiral.py` | py | 82 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig13_outflow_by_size.py` | py | 142 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fig14_cox_hazard.py` | py | 161 |  |  |  | published hazard-analysis derivative |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/figIA1_staking_yield.py` | py | 97 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/figIA2_curve_swaps_2021.py` | py | 28 |  |  |  | secondary Ethereum Curve trade channel |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/figIA3_may2021_dynamics.py` | py | 60 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/figIA4_may2021_by_size.py` | py | 77 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/figIA5_swap_arbitrage_2021.py` | py | 20 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/figures/fit_timecox.R` | r | 59 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/lib/figstyle.py` | py | 104 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/lib/terra_lib.py` | py | 68 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/prep/build_fig13_inputs.py` | py | 105 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/prep/build_swap_arb_price.py` | py | 112 |  |  |  | historical market price |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/prep/prep_fig06_concentration.py` | py | 58 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/prep/prep_loss_panel.py` | py | 275 |  |  |  | wallet loss/depositor derivative |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/run_all.py` | py | 80 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/tables/fmt_table1_token_volume.py` | py | 55 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/tables/fmt_table2_loss_summary.py` | py | 94 |  |  |  | wallet loss/depositor derivative |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/tables/fmt_table3_loss_regression.py` | py | 99 |  |  |  | wallet loss/depositor derivative |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/tables/fmt_tableIA1_native_swap_run.py` | py | 94 |  |  |  | native-swap event and issuance evidence |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/code/tables/fmt_tableIA2_native_swap_run_2021.py` | py | 89 |  |  |  | native-swap event and issuance evidence |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor/anchor_cashflow_transfers.parquet` | parquet | 221721 | time | 2021-03-17T09:26:35+00:00 | 2022-05-26T18:38:00+00:00 | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor/Anchor_daily_stats.parquet` | parquet | 419 | __index__ | 2021-03-18T00:00:00+00:00 | 2022-05-10T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor/anchor_deposit_concentration.parquet` | parquet | 416 | __index__ | 2021-03-17T00:00:00+00:00 | 2022-05-06T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor/Anchor_global_stats_fullnode.parquet` | parquet | 41714 | __index__ | 2021-03-17T04:59:00+00:00 | 2022-05-26T19:12:00+00:00 | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor/aust_rnk_col5.parquet` | parquet | 227000 | date | 2021-09-30T00:00:00+00:00 | 2022-05-14T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor/aust_supply_col5.parquet` | parquet | 227 | date | 2021-09-30T00:00:00+00:00 | 2022-05-14T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor/aust_topk_col4.parquet` | parquet | 197 | __index__ | 2021-03-17T00:00:00+00:00 | 2021-09-29T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor/luna_staking_stats.parquet` | parquet | 416 | __index__ | 2021-03-17T00:00:00+00:00 | 2022-05-06T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor/prerun_deposits.parquet` | parquet | 303730 |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor_run/anchor_run_tx_cleaned.parquet` | parquet | 293276 | time | 2022-05-06T00:00:01+00:00 | 2022-05-13T23:59:39+00:00 | Anchor run events/state or depositor analysis |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor_run/epoch_state_fig10.parquet` | parquet | 917 | time_utc | 2022-05-06T00:14:00+00:00 | 2022-05-15T23:59:00+00:00 | Anchor run events/state or depositor analysis |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor_run/may2021_aust_run_balances.parquet` | parquet | 1858680 | hour | 2021-05-17T00:00:00+00:00 | 2021-05-31T23:00:00+00:00 | Anchor run events/state or depositor analysis |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor_run/may21_anchor_run_prices.parquet` | parquet | 4320 | __index__ | 2021-05-17T00:00:00+00:00 | 2021-05-31T23:55:00+00:00 | Anchor run events/state or depositor analysis |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/anchor_run/run_aust_flow_by_depositor.parquet` | parquet | 310240 | time | 2022-05-06T00:00:01+00:00 | 2022-05-13T23:59:39+00:00 | Anchor run events/state or depositor analysis |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/curve/curve_ust_3pool_may7.parquet` | parquet | 405 | time | 2022-05-07T00:11:28+00:00 | 2022-05-07T23:59:04+00:00 | secondary Ethereum Curve trade channel |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/curve/curve_ust_may2021.parquet` | parquet | 1733 | time | 2021-05-17T00:46:58+00:00 | 2021-05-28T23:05:08+00:00 | secondary Ethereum Curve trade channel |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/daily_balances/columbus-4-lunaust-supply-breakdown-fullnode.parquet` | parquet | 1468900 | date | 2020-10-03T00:00:00+00:00 | 2021-09-29T00:00:00+00:00 | daily UST/LUNA holder-balance reconstruction |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/daily_balances/columbus-5-lunaust-supply-breakdown-fullnode.parquet` | parquet | 159939 | date | 2021-09-30T00:00:00+00:00 | 2022-05-26T00:00:00+00:00 | daily UST/LUNA holder-balance reconstruction |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/exchange/binance_ustusdt_may7.parquet` | parquet | 41985 | time | 2022-05-07T00:00:14.059000+00:00 | 2022-05-07T23:59:59.253000+00:00 | centralized-exchange trade evidence |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/external/lunc-usd-max.csv` | csv | 1252 | snapped_at | 2019-05-08T00:00:00+00:00 | 2022-10-10T00:00:00+00:00 | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/external/ustc-usd-max.csv` | csv | 739 | snapped_at | 2020-10-02T00:00:00+00:00 | 2022-10-10T00:00:00+00:00 | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/hazard/survival_may6_12.parquet` | parquet | 157741 | time | 1970-01-01T00:00:00+00:00 | 1970-01-01T00:00:00.000000168+00:00 | published hazard-analysis derivative |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/hazard/timecox_cum_may6_12.parquet` | parquet | 90769 | time | 1970-01-01T00:00:00+00:00 | 1970-01-01T00:00:00.000000006+00:00 | published hazard-analysis derivative |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/hazard/ust_discount_may6_12.parquet` | parquet | 192 |  |  |  | published hazard-analysis derivative |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/labels/anchor_contracts.csv` | csv | 11 |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/labels/interdm_addresses.parquet` | parquet | 396 |  |  |  | author-curated address/entity labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/labels/terra_labels_4vol.parquet` | parquet | 233 |  |  |  | author-curated address/entity labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/loss/anchor_loss_panel.parquet` | parquet | 159669 |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/loss/depositor_prerun_size.parquet` | parquet | 242536 |  |  |  | wallet loss/depositor derivative |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/native_swaps/luna_total_supply_run.parquet` | parquet | 337 | __index__ | 2022-05-01T00:00:00+00:00 | 2022-05-15T00:00:00+00:00 | native-swap event and issuance evidence |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/native_swaps/ust_luna_swaps_run.parquet` | parquet | 277342 | time | 2021-05-17T03:30:30+00:00 | 2022-05-13T01:58:49+00:00 | native-swap event and issuance evidence |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/network/volume_by_group_token.csv` | csv | 747 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/prices/luna_price_may2022.parquet` | parquet | 21600 | time | 2022-05-01T00:00:00+00:00 | 2022-05-15T23:59:00+00:00 | historical market price |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/prices/ust_luna_minute_price_run.parquet` | parquet | 31661 | time | 2021-05-17T00:00:00+00:00 | 2022-05-14T23:59:00+00:00 | historical market price |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/prices/ust_price_may2022.parquet` | parquet | 21600 | time | 2022-05-01T00:00:00+00:00 | 2022-05-15T23:59:00+00:00 | historical market price |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/tables/table1_token_volume.csv` | csv | 15 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/tables/tableIA1_native_swap_users_run.csv` | csv | 21 |  |  |  | native-swap event and issuance evidence |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/tables/tableIA2_native_swap_users_run_2021.csv` | csv | 20 |  |  |  | native-swap event and issuance evidence |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/Datasets.md` | md | 484 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/LICENSE` | NO_EXTENSION |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/Anchor_amount_histogram.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/Anchor_ANC_subsidy_rate.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/anchor_cash_flow.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/Anchor_deposit_conc.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/Anchor_net_rates_recursive_loans.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/anchor_reserve_injection.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/binance_May7.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/curve_swap_may2021.png` | png |  |  |  |  | secondary Ethereum Curve trade channel |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/curve_swap_May7.png` | png |  |  |  |  | secondary Ethereum Curve trade channel |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/Luna_new.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/LUNA_staking_decomposition.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/May2021-run-dynamics.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/May2021_run_by_size.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/mkt_cap2.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/Run22-Cox-hazard.png` | png |  |  |  |  | published hazard-analysis derivative |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/Run_deposit_outflow3.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/Run_LUNA_supply_price.png` | png |  |  |  |  | historical market price |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/Run_outflow_by_size_combined_240518.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/swap_arb.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/swap_arb_may2021.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/UST_new.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/ust_supply_by_entity.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/figures/wallet_A_B.png` | png |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/tables/anchor_loss_regression.tex` | tex | 38 |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/tables/anchor_loss_summary.tex` | tex | 17 |  |  |  | Anchor state, flow, concentration, or labels |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/tables/native_swap_users_run.tex` | tex | 35 |  |  |  | native-swap event and issuance evidence |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/tables/native_swap_users_run_2021.tex` | tex | 34 |  |  |  | native-swap event and issuance evidence |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/tables/network_entity_classification.tex` | tex | 14 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/output/tables/network_volume_by_token.tex` | tex | 23 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/README.md` | md | 170 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/replication/terra-luna-run-replication/requirements.txt` | txt | 14 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/source_inventory.csv` | csv | 38 |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/terra-luna-run-replication.zip` | zip |  |  |  |  | metadata/code/audit context |
| `data/raw/terra_may2022_v1/terra_may2022_v1_evidence.csv` | csv | 312 | timestamp | 2022-05-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | metadata/code/audit context |
| `data/raw/terra_may2022_v1/v4_remaining_diagnostics.json` | json | 1 |  |  |  | metadata/code/audit context |
| `diagnose_terra_v4_remaining.py` | py | 236 |  |  |  | metadata/code/audit context |
| `diagnose_terra_v4_remaining_v2.py` | py | 251 |  |  |  | metadata/code/audit context |
| `docs/data/terra_hourly_state.csv` | csv | 2 | timestamp | 2022-05-06T22:00:00+00:00 | 2022-05-06T23:00:00+00:00 | metadata/code/audit context |
| `docs/TERRA_ABM.md` | md | 9 |  |  |  | metadata/code/audit context |
| `docs/TERRA_CASE_STUDY.md` | md | 17 |  |  |  | metadata/code/audit context |
| `docs/TERRA_DATA_DICTIONARY.md` | md | 23 |  |  |  | metadata/code/audit context |
| `docs/TERRA_DATA_PROVENANCE.md` | md | 15 |  |  |  | metadata/code/audit context |
| `docs/TERRA_HAZARD_MODEL.md` | md | 7 |  |  |  | published hazard-analysis derivative |
| `docs/TERRA_RESEARCH_BACKGROUND.md` | md | 11 |  |  |  | metadata/code/audit context |
| `docs/TERRA_SYSTEM_DYNAMICS.md` | md | 12 |  |  |  | metadata/code/audit context |
| `frontend/app/components/terra/TerraCharts.tsx` | tsx |  |  |  |  | metadata/code/audit context |
| `frontend/app/components/terra/TerraDashboard.tsx` | tsx |  |  |  |  | metadata/code/audit context |
| `frontend/app/terra/[section]/page.tsx` | tsx |  |  |  |  | metadata/code/audit context |
| `frontend/lib/terra.test.ts` | ts |  |  |  |  | metadata/code/audit context |
| `frontend/lib/terra.ts` | ts |  |  |  |  | metadata/code/audit context |
| `inspect_terra_missing.py` | py | 162 |  |  |  | metadata/code/audit context |
| `scripts/terra/_cli.py` | py | 84 |  |  |  | metadata/code/audit context |
| `scripts/terra/_fetch_normalized.py` | py | 111 |  |  |  | metadata/code/audit context |
| `scripts/terra/_fetch_unavailable.py` | py | 37 |  |  |  | metadata/code/audit context |
| `scripts/terra/benchmark_abm.py` | py | 48 |  |  |  | metadata/code/audit context |
| `scripts/terra/build_hourly_dataset.py` | py | 41 |  |  |  | metadata/code/audit context |
| `scripts/terra/complete_historical_data.py` | py | 1420 |  |  |  | metadata/code/audit context |
| `scripts/terra/fetch_anchor_history.py` | py | 4 |  |  |  | Anchor state, flow, concentration, or labels |
| `scripts/terra/fetch_bridge_flows.py` | py | 8 |  |  |  | metadata/code/audit context |
| `scripts/terra/fetch_curve_ethereum.py` | py | 8 |  |  |  | secondary Ethereum Curve trade channel |
| `scripts/terra/fetch_terra_dex.py` | py | 4 |  |  |  | metadata/code/audit context |
| `scripts/terra/fetch_terra_history.py` | py | 8 |  |  |  | metadata/code/audit context |
| `scripts/terra/import_dataset.ps1` | ps1 | 3 |  |  |  | metadata/code/audit context |
| `scripts/terra/import_dataset.py` | py | 29 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_ablation.ps1` | ps1 | 3 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_ablation.py` | py | 15 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_audit_checks.py` | py | 94 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_benchmark.ps1` | ps1 | 3 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_benchmark.sh` | sh |  |  |  |  | metadata/code/audit context |
| `scripts/terra/run_counterfactual.ps1` | ps1 | 3 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_counterfactual.py` | py | 23 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_final_pipeline.py` | py | 42 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_historical_replay.py` | py | 17 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_model_benchmark.py` | py | 15 |  |  |  | existing model artifact; audit only |
| `scripts/terra/run_replay.ps1` | ps1 | 3 |  |  |  | metadata/code/audit context |
| `scripts/terra/run_replay.sh` | sh |  |  |  |  | metadata/code/audit context |
| `scripts/terra/validate_dataset.py` | py | 38 |  |  |  | metadata/code/audit context |
| `sim/terra/__init__.py` | py | 23 |  |  |  | metadata/code/audit context |
| `sim/terra/agents.py` | py | 82 |  |  |  | metadata/code/audit context |
| `sim/terra/calibration_v2.py` | py | 118 |  |  |  | metadata/code/audit context |
| `sim/terra/conditional.py` | py | 669 |  |  |  | metadata/code/audit context |
| `sim/terra/datasets.py` | py | 125 |  |  |  | metadata/code/audit context |
| `sim/terra/early_warning.py` | py | 50 |  |  |  | metadata/code/audit context |
| `sim/terra/experiments.py` | py | 94 |  |  |  | metadata/code/audit context |
| `sim/terra/fixtures.py` | py | 96 |  |  |  | metadata/code/audit context |
| `sim/terra/ground_truth.py` | py | 17 |  |  |  | metadata/code/audit context |
| `sim/terra/leakage.py` | py | 33 |  |  |  | metadata/code/audit context |
| `sim/terra/models.py` | py | 567 |  |  |  | existing model artifact; audit only |
| `sim/terra/monte_carlo.py` | py | 71 |  |  |  | metadata/code/audit context |
| `sim/terra/replay.py` | py | 116 |  |  |  | metadata/code/audit context |
| `sim/terra/research_pipeline.py` | py | 1067 |  |  |  | metadata/code/audit context |
| `sim/terra/schemas.py` | py | 283 |  |  |  | metadata/code/audit context |
| `sim/terra/validation.py` | py | 190 |  |  |  | metadata/code/audit context |
| `terra_mapping_diagnostics.zip` | zip |  |  |  |  | metadata/code/audit context |
| `terra_may2022_v1_pack/terra_may2022_v1_pack/build_terra_may2022_v1.py` | py | 1074 |  |  |  | metadata/code/audit context |
| `terra_may2022_v1_pack/terra_may2022_v1_pack/expected_hourly_index.csv` | csv | 312 | timestamp | 2022-05-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | metadata/code/audit context |
| `terra_may2022_v1_pack/terra_may2022_v1_pack/field_mapping.csv` | csv | 16 |  |  |  | metadata/code/audit context |
| `terra_may2022_v1_pack/terra_may2022_v1_pack/README_VI.md` | md | 110 |  |  |  | metadata/code/audit context |
| `terra_may2022_v1_pack/terra_may2022_v1_pack/run_build_and_import.ps1` | ps1 | 54 |  |  |  | metadata/code/audit context |
| `terra_may2022_v1_pack/terra_may2022_v1_pack/source_contract.json` | json | 1 |  |  |  | metadata/code/audit context |
| `terra_pack_v2/terra_may2022_v1_pack/build_terra_may2022_v1.py` | py | 611 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v2/terra_may2022_v1_pack/expected_hourly_index.csv` | csv | 312 | timestamp | 2022-05-01T00:00:00+00:00 | 2022-05-13T23:00:00+00:00 | prior ingestion/build implementation or documentation |
| `terra_pack_v2/terra_may2022_v1_pack/field_mapping.csv` | csv | 16 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v2/terra_may2022_v1_pack/README_VI.md` | md | 110 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v2/terra_may2022_v1_pack/run_build_and_import.ps1` | ps1 | 53 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v2/terra_may2022_v1_pack/source_contract.json` | json | 1 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v3/terra_may2022_v1_pack_v3/terra_may2022_v1_pack/build_terra_may2022_v1.py` | py | 885 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v3/terra_may2022_v1_pack_v3/terra_may2022_v1_pack/README_V3.md` | md | 81 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v3/terra_may2022_v1_pack_v3/terra_may2022_v1_pack/run_build_and_import.ps1` | ps1 | 54 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v4/terra_may2022_v1_pack_v4/terra_may2022_v1_pack/build_terra_may2022_v1.py` | py | 900 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v4/terra_may2022_v1_pack_v4/terra_may2022_v1_pack/README_V3.md` | md | 81 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v4/terra_may2022_v1_pack_v4/terra_may2022_v1_pack/README_V4.md` | md | 44 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v4/terra_may2022_v1_pack_v4/terra_may2022_v1_pack/run_build_and_import.ps1` | ps1 | 54 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v5/terra_may2022_v1_pack_v5/terra_may2022_v1_pack/build_terra_may2022_v1.py` | py | 941 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v5/terra_may2022_v1_pack_v5/terra_may2022_v1_pack/README_V3.md` | md | 81 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v5/terra_may2022_v1_pack_v5/terra_may2022_v1_pack/README_V4.md` | md | 44 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v5/terra_may2022_v1_pack_v5/terra_may2022_v1_pack/README_V5.md` | md | 65 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v5/terra_may2022_v1_pack_v5/terra_may2022_v1_pack/run_build_and_import.ps1` | ps1 | 54 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v6/terra_may2022_v1_pack_v6/terra_may2022_v1_pack/build_terra_may2022_v1.py` | py | 1074 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v6/terra_may2022_v1_pack_v6/terra_may2022_v1_pack/README_V3.md` | md | 81 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v6/terra_may2022_v1_pack_v6/terra_may2022_v1_pack/README_V4.md` | md | 44 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v6/terra_may2022_v1_pack_v6/terra_may2022_v1_pack/README_V5.md` | md | 65 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v6/terra_may2022_v1_pack_v6/terra_may2022_v1_pack/README_V6.md` | md | 55 |  |  |  | prior ingestion/build implementation or documentation |
| `terra_pack_v6/terra_may2022_v1_pack_v6/terra_may2022_v1_pack/run_build_and_import.ps1` | ps1 | 54 |  |  |  | prior ingestion/build implementation or documentation |
| `tests/test_terra_api.py` | py | 86 |  |  |  | metadata/code/audit context |
| `tests/test_terra_data_and_leakage.py` | py | 98 |  |  |  | metadata/code/audit context |
| `tests/test_terra_data_completion.py` | py | 141 |  |  |  | metadata/code/audit context |
| `tests/test_terra_final_pipeline.py` | py | 234 |  |  |  | metadata/code/audit context |
| `tests/test_terra_models.py` | py | 100 |  |  |  | existing model artifact; audit only |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/.gitignore` | NO_EXTENSION |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/config.py` | py | 36 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig01_anchor_net_rates.py` | py | 81 |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig02_ust_supply_by_entity.py` | py | 91 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig03_anchor_cashflow.py` | py | 155 |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig04_network_volume.py` | py | 251 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig05_market_cap.py` | py | 76 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig06_anchor_concentration.py` | py | 103 |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig07_wallet_A_B.py` | py | 99 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig08_curve_swaps.py` | py | 126 |  |  |  | secondary Ethereum Curve trade channel |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig09_binance_ustusdt.py` | py | 91 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig10_run_outflows.py` | py | 103 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig11_swap_arbitrage.py` | py | 103 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig12_death_spiral.py` | py | 82 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig13_outflow_by_size.py` | py | 142 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fig14_cox_hazard.py` | py | 161 |  |  |  | published hazard-analysis derivative |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/figIA1_staking_yield.py` | py | 97 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/figIA2_curve_swaps_2021.py` | py | 28 |  |  |  | secondary Ethereum Curve trade channel |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/figIA3_may2021_dynamics.py` | py | 60 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/figIA4_may2021_by_size.py` | py | 77 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/figIA5_swap_arbitrage_2021.py` | py | 20 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/figures/fit_timecox.R` | r | 59 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/lib/figstyle.py` | py | 104 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/lib/terra_lib.py` | py | 68 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/prep/build_fig13_inputs.py` | py | 105 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/prep/build_swap_arb_price.py` | py | 112 |  |  |  | historical market price |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/prep/prep_fig06_concentration.py` | py | 58 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/prep/prep_loss_panel.py` | py | 275 |  |  |  | wallet loss/depositor derivative |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/run_all.py` | py | 80 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/tables/fmt_table1_token_volume.py` | py | 55 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/tables/fmt_table2_loss_summary.py` | py | 94 |  |  |  | wallet loss/depositor derivative |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/tables/fmt_table3_loss_regression.py` | py | 99 |  |  |  | wallet loss/depositor derivative |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/tables/fmt_tableIA1_native_swap_run.py` | py | 94 |  |  |  | native-swap event and issuance evidence |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/code/tables/fmt_tableIA2_native_swap_run_2021.py` | py | 89 |  |  |  | native-swap event and issuance evidence |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor/anchor_cashflow_transfers.parquet` | parquet | 221721 | time | 2021-03-17T09:26:35+00:00 | 2022-05-26T18:38:00+00:00 | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor/Anchor_daily_stats.parquet` | parquet | 419 | __index__ | 2021-03-18T00:00:00+00:00 | 2022-05-10T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor/anchor_deposit_concentration.parquet` | parquet | 416 | __index__ | 2021-03-17T00:00:00+00:00 | 2022-05-06T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor/Anchor_global_stats_fullnode.parquet` | parquet | 41714 | __index__ | 2021-03-17T04:59:00+00:00 | 2022-05-26T19:12:00+00:00 | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor/aust_rnk_col5.parquet` | parquet | 227000 | date | 2021-09-30T00:00:00+00:00 | 2022-05-14T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor/aust_supply_col5.parquet` | parquet | 227 | date | 2021-09-30T00:00:00+00:00 | 2022-05-14T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor/aust_topk_col4.parquet` | parquet | 197 | __index__ | 2021-03-17T00:00:00+00:00 | 2021-09-29T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor/luna_staking_stats.parquet` | parquet | 416 | __index__ | 2021-03-17T00:00:00+00:00 | 2022-05-06T00:00:00+00:00 | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor/prerun_deposits.parquet` | parquet | 303730 |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor_run/anchor_run_tx_cleaned.parquet` | parquet | 293276 | time | 2022-05-06T00:00:01+00:00 | 2022-05-13T23:59:39+00:00 | Anchor run events/state or depositor analysis |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor_run/epoch_state_fig10.parquet` | parquet | 917 | time_utc | 2022-05-06T00:14:00+00:00 | 2022-05-15T23:59:00+00:00 | Anchor run events/state or depositor analysis |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor_run/may2021_aust_run_balances.parquet` | parquet | 1858680 | hour | 2021-05-17T00:00:00+00:00 | 2021-05-31T23:00:00+00:00 | Anchor run events/state or depositor analysis |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor_run/may21_anchor_run_prices.parquet` | parquet | 4320 | __index__ | 2021-05-17T00:00:00+00:00 | 2021-05-31T23:55:00+00:00 | Anchor run events/state or depositor analysis |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/anchor_run/run_aust_flow_by_depositor.parquet` | parquet | 310240 | time | 2022-05-06T00:00:01+00:00 | 2022-05-13T23:59:39+00:00 | Anchor run events/state or depositor analysis |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/curve/curve_ust_3pool_may7.parquet` | parquet | 405 | time | 2022-05-07T00:11:28+00:00 | 2022-05-07T23:59:04+00:00 | secondary Ethereum Curve trade channel |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/curve/curve_ust_may2021.parquet` | parquet | 1733 | time | 2021-05-17T00:46:58+00:00 | 2021-05-28T23:05:08+00:00 | secondary Ethereum Curve trade channel |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/daily_balances/columbus-4-lunaust-supply-breakdown-fullnode.parquet` | parquet | 1468900 | date | 2020-10-03T00:00:00+00:00 | 2021-09-29T00:00:00+00:00 | daily UST/LUNA holder-balance reconstruction |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/daily_balances/columbus-5-lunaust-supply-breakdown-fullnode.parquet` | parquet | 159939 | date | 2021-09-30T00:00:00+00:00 | 2022-05-26T00:00:00+00:00 | daily UST/LUNA holder-balance reconstruction |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/exchange/binance_ustusdt_may7.parquet` | parquet | 41985 | time | 2022-05-07T00:00:14.059000+00:00 | 2022-05-07T23:59:59.253000+00:00 | centralized-exchange trade evidence |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/external/lunc-usd-max.csv` | csv | 1252 | snapped_at | 2019-05-08T00:00:00+00:00 | 2022-10-10T00:00:00+00:00 | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/external/ustc-usd-max.csv` | csv | 739 | snapped_at | 2020-10-02T00:00:00+00:00 | 2022-10-10T00:00:00+00:00 | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/hazard/survival_may6_12.parquet` | parquet | 157741 | time | 1970-01-01T00:00:00+00:00 | 1970-01-01T00:00:00.000000168+00:00 | published hazard-analysis derivative |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/hazard/timecox_cum_may6_12.parquet` | parquet | 90769 | time | 1970-01-01T00:00:00+00:00 | 1970-01-01T00:00:00.000000006+00:00 | published hazard-analysis derivative |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/hazard/ust_discount_may6_12.parquet` | parquet | 192 |  |  |  | published hazard-analysis derivative |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/labels/anchor_contracts.csv` | csv | 11 |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/labels/interdm_addresses.parquet` | parquet | 396 |  |  |  | author-curated address/entity labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/labels/terra_labels_4vol.parquet` | parquet | 233 |  |  |  | author-curated address/entity labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/loss/anchor_loss_panel.parquet` | parquet | 159669 |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/loss/depositor_prerun_size.parquet` | parquet | 242536 |  |  |  | wallet loss/depositor derivative |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/native_swaps/luna_total_supply_run.parquet` | parquet | 337 | __index__ | 2022-05-01T00:00:00+00:00 | 2022-05-15T00:00:00+00:00 | native-swap event and issuance evidence |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/native_swaps/ust_luna_swaps_run.parquet` | parquet | 277342 | time | 2021-05-17T03:30:30+00:00 | 2022-05-13T01:58:49+00:00 | native-swap event and issuance evidence |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/network/volume_by_group_token.csv` | csv | 747 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/prices/luna_price_may2022.parquet` | parquet | 21600 | time | 2022-05-01T00:00:00+00:00 | 2022-05-15T23:59:00+00:00 | historical market price |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/prices/ust_luna_minute_price_run.parquet` | parquet | 31661 | time | 2021-05-17T00:00:00+00:00 | 2022-05-14T23:59:00+00:00 | historical market price |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/prices/ust_price_may2022.parquet` | parquet | 21600 | time | 2022-05-01T00:00:00+00:00 | 2022-05-15T23:59:00+00:00 | historical market price |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/tables/table1_token_volume.csv` | csv | 15 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/tables/tableIA1_native_swap_users_run.csv` | csv | 21 |  |  |  | native-swap event and issuance evidence |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/data/tables/tableIA2_native_swap_users_run_2021.csv` | csv | 20 |  |  |  | native-swap event and issuance evidence |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/Datasets.md` | md | 484 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/LICENSE` | NO_EXTENSION |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/Anchor_amount_histogram.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/Anchor_ANC_subsidy_rate.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/anchor_cash_flow.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/Anchor_deposit_conc.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/Anchor_net_rates_recursive_loans.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/anchor_reserve_injection.png` | png |  |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/binance_May7.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/curve_swap_may2021.png` | png |  |  |  |  | secondary Ethereum Curve trade channel |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/curve_swap_May7.png` | png |  |  |  |  | secondary Ethereum Curve trade channel |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/Luna_new.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/LUNA_staking_decomposition.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/May2021-run-dynamics.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/May2021_run_by_size.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/mkt_cap2.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/Run22-Cox-hazard.png` | png |  |  |  |  | published hazard-analysis derivative |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/Run_deposit_outflow3.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/Run_LUNA_supply_price.png` | png |  |  |  |  | historical market price |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/Run_outflow_by_size_combined_240518.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/swap_arb.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/swap_arb_may2021.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/UST_new.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/ust_supply_by_entity.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/figures/wallet_A_B.png` | png |  |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/tables/anchor_loss_regression.tex` | tex | 38 |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/tables/anchor_loss_summary.tex` | tex | 17 |  |  |  | Anchor state, flow, concentration, or labels |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/tables/native_swap_users_run.tex` | tex | 35 |  |  |  | native-swap event and issuance evidence |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/tables/native_swap_users_run_2021.tex` | tex | 34 |  |  |  | native-swap event and issuance evidence |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/tables/network_entity_classification.tex` | tex | 14 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/output/tables/network_volume_by_token.tex` | tex | 23 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/README.md` | md | 170 |  |  |  | metadata/code/audit context |
| `zip://data/raw/terra_may2022_v1/terra-luna-run-replication.zip!/terra-luna-run-replication/requirements.txt` | txt | 14 |  |  |  | metadata/code/audit context |
