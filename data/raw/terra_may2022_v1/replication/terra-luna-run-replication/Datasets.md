# Datasets & column provenance — replication package

_Catalog of every shipped dataset in `data/`, every column in each, and where each column comes from._

## Provenance legend

Each column is tagged with one origin category:

| Tag | Meaning |
|-----|---------|
| **(1) shipped-derived** | Constructed from other columns that are themselves **shipped in this package** (same file or another file under `data/`). |
| **(2) unshipped-derived** | Constructed/aggregated from raw inputs in the authors' research tree that are **not shipped** (full-node transfer/state logs, the per-exchange minute price panel, the sophistication panels, etc.). The originating provider is named. |
| **(3) direct from source** | The value is a raw field taken essentially as-is (at most parsed/relabeled) from a named external source. |

**Source names** used in the tags: **NODE** = Terra Classic archive node (Columbus‑4/5; on-chain); **GENESIS** = Columbus genesis snapshots; **FLIPSIDE** = Flipside extracts (incl. Ethereum/Curve); **NANSEN** = Nansen/Snowflake; **KAIKO** = Kaiko exchange data; **COINGECKO** = CoinGecko public exports; **AUTHOR** = author-created/curated labels; **R** = the shipped `fit_timecox.R` estimation step.

> Note on the (2) vs (3) line: the on-chain "extract" files (raw transfer/swap/trade/state events) are tagged **(3) NODE/FLIPSIDE/KAIKO** because each column is a raw event field. Files that are **balances, cumulative sums, daily aggregates, VWAPs, ranks, or regression transforms** are tagged **(2)** because they are computed from raw logs that the package does not ship. Where a column is a pure transform of another column *in the same shipped file* (e.g. an APY from an APR, a log of a level), it is **(1)**.

---

## Summary — the dataset list

| # | File | Primary source | Cols | Used by |
|---|------|----------------|------|---------|
| 1 | `anchor/Anchor_daily_stats.parquet` | NODE (Anchor contract state + epoch ops) | 21 (+date idx) | Figs 1, 3, 6, IA.1 |
| 2 | `anchor/Anchor_global_stats_fullnode.parquet` | NODE (`{state}` per-block) | 13 (+minute idx) | Fig 3 |
| 3 | `anchor/anchor_deposit_concentration.parquet` | shipped-derived (from #5,#6,#7) | 3 (+date idx) | Fig 6 |
| 4 | `anchor/aust_rnk_col5.parquet` | NANSEN→NODE (aUST balances) | 4 | Fig 6 (via prep) |
| 5 | `anchor/aust_supply_col5.parquet` | NANSEN→NODE (aUST supply) | 2 | Fig 6 (via prep) |
| 6 | `anchor/aust_topk_col4.parquet` | NODE (col‑4 aUST balance panel) | 4 (+date idx) | Fig 6 (via prep) |
| 7 | `anchor/luna_staking_stats.parquet` | NODE + FLIPSIDE (staking + airdrops) | 15 (+date_reward idx), 10 plot-unused | Fig IA.1 |
| 8 | `anchor/anchor_cashflow_transfers.parquet` | FLIPSIDE→NODE (Anchor cash-flow events) | 5 | Fig 3 |
| 9 | `anchor/prerun_deposits.parquet` | NODE (aUST snapshot 2022‑05‑05) | 2 (1 plot-unused) | Fig 6 |
| 10 | `anchor_run/anchor_run_tx_cleaned.parquet` | NODE (Anchor deposit/withdraw events) | 5 (1 plot-unused) | Fig 7 |
| 11 | `anchor_run/may2021_aust_run_balances.parquet` | NODE (hourly aUST balances) | 3 | Fig IA.4 |
| 12 | `anchor_run/may21_anchor_run_prices.parquet` | NODE + KAIKO | 3 (+minute idx), 1 plot-unused | Fig IA.3 |
| 13 | `anchor_run/run_aust_flow_by_depositor.parquet` | unshipped-derived NODE (built by prep) | 3 | Fig 13 |
| 13a | `anchor_run/epoch_state_fig10.parquet` | NODE (`{epoch_state}` per-block) | 5 | Fig 10 |
| 14 | `curve/curve_ust_3pool_may7.parquet` | FLIPSIDE (Ethereum Curve) | 6 | Fig 8 |
| 15 | `curve/curve_ust_may2021.parquet` | FLIPSIDE (Ethereum Curve) | 6 | Fig IA.2 |
| 16 | `daily_balances/columbus-4-lunaust-supply-breakdown-fullnode.parquet` | NODE (transfer cumsum + genesis) | 4 | Fig 2 |
| 17 | `daily_balances/columbus-5-lunaust-supply-breakdown-fullnode.parquet` | NODE (transfer cumsum) | 4 | Fig 2 |
| 18 | `exchange/binance_ustusdt_may7.parquet` | KAIKO (tick trades) | 4 | Fig 9 |
| 19 | `external/lunc-usd-max.csv` | COINGECKO | 4 | Fig 5 |
| 20 | `external/ustc-usd-max.csv` | COINGECKO | 4 | Fig 5 |
| 21 | `hazard/survival_may6_12.parquet` | unshipped-derived NODE + AUTHOR (survival panel) | 8 | Fig 14 (via R) |
| 22 | `hazard/timecox_cum_may6_12.parquet` | shipped-derived via R (from #21) | 3 | Fig 14 |
| 23 | `hazard/ust_discount_may6_12.parquet` | unshipped-derived KAIKO (UST price) | 2 | Fig 14 |
| 25 | `labels/interdm_addresses.parquet` | AUTHOR (derived label set) | 1 | Figs 6,10,13; Tabs 2,3; Fig IA.4 |
| 26 | `labels/anchor_contracts.csv` | AUTHOR | 2 | Fig 3 |
| 27 | `labels/terra_labels_4vol.parquet` | AUTHOR | 2 | Figs 2, 4 |
| 28 | `loss/anchor_loss_panel.parquet` | mixed (built by prep) | 10 | Tabs 2, 3 |
| 29 | `loss/depositor_prerun_size.parquet` | NODE (+ prep adds full_maxusd) | 4 | Figs 10,13; Tabs 2,3 |
| 30 | `native_swaps/luna_total_supply_run.parquet` | unshipped-derived NODE (swap mint/burn) | 1 (+time idx) | Fig 12 |
| 31 | `native_swaps/ust_luna_swaps_run.parquet` | FLIPSIDE→NODE (swap events) | 4 | Figs 11, IA.5 |
| 32 | `network/volume_by_group_token.csv` | NODE (transfers) + AUTHOR (types) | 4 | Fig 4 |
| 33 | `prices/luna_price_may2022.parquet` | KAIKO (minute VWAP) | 2 | Fig 12 |
| 34 | `prices/ust_luna_minute_price_run.parquet` | unshipped-derived KAIKO/DEX (built by prep) | 3 | Figs 11, IA.5 |
| 35 | `prices/ust_price_may2022.parquet` | KAIKO (minute VWAP) | 2 | Fig 10 |
| 36 | `tables/table1_token_volume.csv` | unshipped-derived NODE + AUTHOR | 4 | Table 1 |
| 37 | `tables/tableIA1_native_swap_users_run.csv` | unshipped-derived NODE + AUTHOR | 5 | Table IA.1 |
| 38 | `tables/tableIA2_native_swap_users_run_2021.csv` | unshipped-derived NODE + AUTHOR | 4 | Table IA.2 |

> Dataset #24 (the former `labels/dex_swap_addresses.parquet`) has been removed; the remaining IDs are unchanged. The shipped label sets carry only the rows the runnable exhibits consume (see `data/labels/` below).

Files **rebuilt by a shipped `prep/` script** (so their construction is fully documented in-package): #3, #13, #28, #29 (full_maxusd col), #34. File #22 is rebuilt by `fit_timecox.R`.

---

## `data/anchor/`

### 1. `Anchor_daily_stats.parquet` — daily Anchor money-market state (419 rows; index `date`)
Built from daily `wasm` smart-queries of the Anchor market contract (`MKT`) `{epoch_state}`/`{state}` plus epoch-operation txs. Raw per-block queries are not shipped.

| Column | Origin | Notes |
|--------|--------|-------|
| `date` (index) | (3) NODE | block-day key |
| `market balance` | (2) NODE | contract UST reserve/market balance |
| `loan balance` | (2) NODE | total outstanding loans (used Figs 1, 3) |
| `borrow APR` | (2) NODE | from epoch interest state (used Figs 1, 3) |
| `borrow APY` | (1) | compounding transform of `borrow APR` |
| `aUST/UST` | (2) NODE | aUST exchange rate from `{epoch_state}` (used Fig 6; Fig 10 uses the per-block `{epoch_state}` series in file #13a) |
| `deposit APR` | (2) NODE | deposit rate (used Figs 1, 3) |
| `deposit APY` | (1) | compounding transform of `deposit APR` |
| `ANC distribution` | (2) NODE | ANC emitted to depositors/borrowers |
| `ANC repurchase` | (2) NODE | ANC buyback amount (not plotted; Fig 3 derives the ANC-repurchase leg from the `Collector` address in `anchor_cashflow_transfers`, not this column) |
| `bLuna collateral` | (2) NODE | bLUNA collateral value |
| `bLuna APR` | (2) NODE | bLUNA staking yield |
| `bLuna APY` | (1) | transform of `bLuna APR` |
| `bLuna LTV` | (3) PROTOCOL CONSTANT | max LTV = 0.5 (protocol parameter) |
| `deposit balance` | (2) NODE | total aUST deposits in UST (used Fig 3 deposit-interest leg) |
| `net_collateral_usd` | (2) NODE | collateral net of loans |
| `LUNA_staking_airdrop` | (2) NODE + FLIPSIDE | total LUNA staking+airdrop yield rate (`ardb.sum(axis=1)/100`); not plotted directly — Fig 1 reads the precomputed `LUNA_opp_cost` (its 2× transform) |
| `LUNA_opp_cost` | (1) shipped-derived | `= LUNA_staking_airdrop / bLuna LTV` — both columns in this same file; `bLuna LTV`=0.5 ⇒ exactly 2× the airdrop yield (`230207-Anchor-new-accounting.ipynb` cell 57). Used Fig 1 |
| `ANC/UST` | (2) NODE/oracle | ANC price in UST |
| `ANC APR` | (2) NODE | ANC subsidy APR (used Figs 1, IA.1) |
| `ANC APY` | (1) | transform of `ANC APR` |
| `Exploit UST` | (2) NODE | UST attributable to the Anchor exploit (used Fig 1) |

### 2. `Anchor_global_stats_fullnode.parquet` — per-block Anchor `{state}` (41,714 rows; index `minute`)
Raw `{state}` contract reads of `MKT`. One column is used: `prev_interest_buffer` (Fig 3 reserve injection); the rest are shipped as the raw state record. (Fig 10's deposit balance previously came from `prev_aterra_supply` × `prev_exchange_rate` here, but those `prev_*` fields are epoch-cached and only refresh ~70 times across the run, producing a staircase; Fig 10 now reads the per-block `{epoch_state}` series in file #13a instead.)

| Column | Origin | Notes |
|--------|--------|-------|
| `minute` (index) | (3) NODE | block-minute key |
| `height` | (3) NODE | block height |
| `total_liabilities` | (3) NODE | contract state field |
| `total_reserves` | (3) NODE | contract state field |
| `last_interest_updated` | (3) NODE | contract state field (block height) |
| `last_reward_updated` | (3) NODE | contract state field (block height) |
| `global_interest_index` | (3) NODE | contract state field |
| `global_reward_index` | (3) NODE | contract state field |
| `anc_emission_rate` | (3) NODE | contract state field |
| `deposit_rate` | (3) NODE | contract state field |
| `prev_aterra_supply` | (3) NODE | contract state field |
| `prev_exchange_rate` | (3) NODE | contract state field |
| `prev_interest_buffer` | (3) NODE | yield-reserve buffer |
| `last_executed_height` | (3) NODE | contract state field |

### 3. `anchor_deposit_concentration.parquet` — top-k deposit shares (416 rows; index `date`)
**Built in-package** by `prep/prep_fig06_concentration.py` from the three shipped aUST tables below.

| Column | Origin | Notes |
|--------|--------|-------|
| `date` (index) | (1) | stitched col‑4/col‑5 day index |
| `Top 10` | (1) shipped-derived | top‑10 aUST share %; from `aust_topk_col4` (col‑4) + `aust_rnk_col5`/`aust_supply_col5` (col‑5) |
| `Top 100` | (1) shipped-derived | top‑100 share %, same inputs |
| `Top 1000` | (1) shipped-derived | top‑1000 share %, same inputs |

### 4. `aust_rnk_col5.parquet` — ranked Columbus‑5 aUST balances (227,000 rows)
| Column | Origin | Notes |
|--------|--------|-------|
| `date` | (3) NODE | snapshot day |
| `address` | (3) NODE | holder address |
| `balance` | (2) NANSEN→NODE | daily aUST balance (transfer cumsum; orig. Nansen `daily_balance_by_token`, content on-chain) |
| `rnk` | (1) | rank of `balance` within `date` |

### 5. `aust_supply_col5.parquet` — daily Columbus‑5 aUST supply (227 rows)
| Column | Origin | Notes |
|--------|--------|-------|
| `date` | (3) NODE | day |
| `supply` | (2) NANSEN→NODE | total aUST supply that day (sum of balances) |

### 6. `aust_topk_col4.parquet` — Columbus‑4 daily top-k aUST sums (197 rows; index `date`)
| Column | Origin | Notes |
|--------|--------|-------|
| `date` (index) | (3) NODE | day |
| `total` | (2) NODE | total aUST that day (sum over col‑4 balance panel, ~134 MB, not shipped) |
| `t10` | (2) NODE | sum of top‑10 balances |
| `t100` | (2) NODE | sum of top‑100 balances |
| `t1000` | (2) NODE | sum of top‑1000 balances |

### 7. `luna_staking_stats.parquet` — LUNA staking-yield decomposition (416 rows; index `date_reward`)
Daily LUNA staking rewards + ANC/MIR/MINE airdrops (node staking module + Flipside airdrop data). Used by Fig IA.1.

| Column | Origin | Notes |
|--------|--------|-------|
| `date_reward` (index) | (3) NODE | reward day |
| `luna_stake_balance` | (2) NODE | LUNA staked by the reserve (used IA.1) |
| `total_reward_luna` | (2) NODE | gross staking reward (LUNA) |
| `total_comm_luna` | (2) NODE | validator commission (LUNA) |
| `reward_adjusted` | (1) | `total_reward_luna − total_comm_luna` |
| `anc_luna` | (2) FLIPSIDE | ANC airdrop valued in LUNA (used IA.1) |
| `mir_luna` | (2) FLIPSIDE | MIR airdrop in LUNA (used IA.1) |
| `mine_luna` | (2) FLIPSIDE | MINE airdrop in LUNA (used IA.1) |
| `airdrop_luna` | (1) | sum of the three airdrop columns |
| `apr_percent_airdrop` | (1)/(2) | airdrop-only APR |
| `apy_percent_airdrop` | (1) | transform of the above |
| `apr_percent` | (1)/(2) | total staking+airdrop APR |
| `apy_percent` | (1) | transform |
| `apr_percent_comm` | (1)/(2) | commission/block-reward APR (used IA.1) |
| `apy_percent_comm` | (1) | transform |
| `percent_cut` | (1) | commission share % |

### 8. `anchor_cashflow_transfers.parquet` — Anchor cash-flow transfer events (221,721 rows)
UST `transfer` events with the Anchor market contract (`MKT`) as sender/recipient. Originally a Flipside "anchor cashflow" extract; content is on-chain. Used by Fig 3.

| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (3) FLIPSIDE→NODE | event timestamp (figure derives day bucket = `time.ceil('D')`) |
| `sender` | (3) FLIPSIDE→NODE | transfer sender |
| `recipient` | (3) FLIPSIDE→NODE | transfer recipient |
| `denom` | (3) FLIPSIDE→NODE | token denom (figure keeps `uusd`) |
| `amount` | (3) FLIPSIDE→NODE | transfer amount |

### 9. `prerun_deposits.parquet` — pre-run aUST snapshot (303,730 rows)
| Column | Origin | Notes |
|--------|--------|-------|
| `address` | (3) NODE | depositor address |
| `balance` | (2) NODE | aUST balance on 2022‑05‑05 (transfer cumsum; used Fig 6 histogram) |

---

## `data/anchor_run/`

### 10. `anchor_run_tx_cleaned.parquet` — run-window Anchor txs (293,276 rows)
Anchor `deposit`/`withdraw` (and borrow/repay) events at `MKT`, May 6–13 2022 (RPC `tx_search`). 

| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (3) NODE | event time |
| `sender` | (3) NODE | acting wallet |
| `action` | (3) NODE | `deposit` / `withdraw` / … |
| `aust_vol` | (3) NODE | aUST amount (was Fig 10's input before the contract-state rework above; no current consumer) |
| `ust_vol` | (3) NODE | UST amount of the action (used Fig 7) |

### 11. `may2021_aust_run_balances.parquet` — hourly aUST balances, May 2021 (1,858,680 rows)
| Column | Origin | Notes |
|--------|--------|-------|
| `address` | (3) NODE | depositor address |
| `hour` | (3) NODE | hour bucket |
| `balance` | (2) NODE | hourly aUST balance (transfer cumsum); used Fig IA.4 |

### 12. `may21_anchor_run_prices.parquet` — May 2021 deposit balance + UST price (4,320 rows; index `minute`)
| Column | Origin | Notes |
|--------|--------|-------|
| `minute` (index) | (3) | minute key |
| `aust_deposit` | (2) NODE | outstanding Anchor deposit balance (used IA.3) |
| `price` | (3) KAIKO | UST/USD price (volume-weighted; weight = `sell_amount`) (used IA.3) |
| `sell_amount` | (3) KAIKO | the trading-volume weight that accompanies `price` (used as the VWAP weight: `pricevol = sell_amount × price`, `230312-May2021-Run.ipynb` cells 67–68); present in the file but not plotted by Fig IA.3 |

### 13. `run_aust_flow_by_depositor.parquet` — address-centric aUST flow (310,240 rows)
**Built in-package** by `prep/build_fig13_inputs.py` from the un-shipped run-window 6-token depositor transfer log. Used by Fig 13.

| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (2) NODE | aUST transfer time |
| `address` | (2) NODE | a depositor on one side of the transfer |
| `vol` | (2) NODE | signed aUST amount (+received / −sent) per depositor side |

### 13a. `epoch_state_fig10.parquet` — per-block Anchor `{epoch_state}` (917 rows)
Live Anchor deposit balance for Fig 10. Re-fetched from `{epoch_state}` smart-queries of `MKT` at the 917 snapshot heights of file #2 (the stored `{state}` `prev_*` fields are epoch-cached and step in stairs; `{epoch_state}` recomputes supply × rate every block). May 6–15 2022. Shipped; no rebuild step in-package.

| Column | Origin | Notes |
|--------|--------|-------|
| `time_utc` | (3) NODE | block time (UTC), aligned to file #2's snapshot heights |
| `height` | (3) NODE | block height |
| `aterra_supply` | (3) NODE | live total aUST supply (µaUST) from `{epoch_state}` |
| `exchange_rate` | (3) NODE | live aUST/UST exchange rate from `{epoch_state}` |
| `deposit_b_ust` | (1) | `aterra_supply` × `exchange_rate` / 1e6 / 1e9 (B UST); plotted |

---

## `data/curve/` (Ethereum — rebuild via an Ethereum node/Dune, not the Terra node)

### 14. `curve_ust_3pool_may7.parquet` — Curve UST swaps, May 7 2022 (405 rows)
### 15. `curve_ust_may2021.parquet` — Curve UST swaps, May 2021 (1,733 rows)
Both have identical schemas (Flipside Ethereum Curve-pool trade extracts). Used by Figs 8 and IA.2.

| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (3) FLIPSIDE | trade timestamp |
| `sell_amount` | (3) FLIPSIDE | UST sold |
| `taker_side_sell` | (3) FLIPSIDE | True = UST sold into pool |
| `trader` | (3) FLIPSIDE | Ethereum address |
| `price_native` | (3) FLIPSIDE | UST price in the quote asset |
| `quote_asset` | (3) FLIPSIDE | counter-token of the swap: `USDC`/`DAI`/`3Crv`/`USDT` (#14, May-2022); `USDT`/`USDC`/`DAI` (#15, May-2021). Fig 8/IA.2 drop the `3Crv` rows from the discount subplot (`quote_asset != "3Crv"`) |

---

## `data/daily_balances/` (UST/LUNA supply breakdown)

### 16. `columbus-4-lunaust-supply-breakdown-fullnode.parquet` (1,468,900 rows)
### 17. `columbus-5-lunaust-supply-breakdown-fullnode.parquet` (159,939 rows)
Per-address daily UST/LUNA balances, reconstructed by parsing `transfer`/`send`/`mint`/`burn` logs and cumulative-summing from the genesis snapshot. Used by Fig 2.

| Column | Origin | Notes |
|--------|--------|-------|
| `denom` | (3) NODE | token (`uusd`/`UST`, `uluna`/`LUNA`) |
| `balance` | (2) NODE + GENESIS | per-address daily balance (transfer cumsum from genesis) |
| `address` | (3) NODE | holder address |
| `date` | (3) NODE | day |

---

## `data/exchange/`

### 18. `binance_ustusdt_may7.parquet` — Binance UST/USDT ticks, May 7 2022 (41,985 rows)
Kaiko tick trades. Used by Fig 9.

| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (3) KAIKO | trade time |
| `price` | (3) KAIKO | UST/USDT price |
| `amount` | (3) KAIKO | trade size |
| `taker_side_sell` | (3) KAIKO | taker side flag |

---

## `data/external/` (CoinGecko public exports)

### 19. `lunc-usd-max.csv` (1,252 rows) · ### 20. `ustc-usd-max.csv` (739 rows)
Standard CoinGecko "max" daily exports. Used by Fig 5 (`market_cap` only).

| Column | Origin | Notes |
|--------|--------|-------|
| `snapped_at` | (3) COINGECKO | UTC day |
| `price` | (3) COINGECKO | USD price |
| `market_cap` | (3) COINGECKO | USD market cap |
| `total_volume` | (3) COINGECKO | 24h USD volume |

---

## `data/hazard/` (Figure 14 — Cox time-varying hazard)

### 21. `survival_may6_12.parquet` — survival panel (157,741 rows)
The regression-ready survival panel fed to `fit_timecox.R`. Columns are the run-exit timing + depositor covariates, derived from the un-shipped run-window withdrawal log and the sophistication panels (same covariates as the loss panel, #28).

| Column | Origin | Notes |
|--------|--------|-------|
| `log10_size` | (2) NODE | `= log10(full_maxusd + 1)`, the wallet's peak USD aUST balance (size panel, un-shipped) |
| `status` | (2) NODE | event indicator = 1 if the wallet withdrew >50% of pre-run aUST during the window (`get_withdraw_time`) |
| `log_volume_adj` | (2) NANSEN/NODE | log volume/balance ratio (from un-shipped `sophistication_prerun_may5.parquet`) |
| `cex_degree` | (2) NANSEN/NODE | # distinct CEX counterparties (same un-shipped panel) |
| `used_bridge` | (2) NODE | bridge-user flag (same un-shipped panel) |
| `log_age_months` | (2) NODE | log wallet age in months (same un-shipped panel) |
| `sophistication` | (1) shipped-derived | composite = sum of the four covariates above after z-scoring (`StandardScaler` each, then sum) |
| `time` | (2) NODE | survival time (hours from May 6) until withdrawal/censoring |

### 22. `timecox_cum_may6_12.parquet` — R `timecox` cumulative coefficients (90,769 rows)
**Built by `fit_timecox.R`** from the shipped survival panel (#21). Used by Fig 14.

| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (1) via R | time (days from May 6) |
| `intercept` | (1) via R | cumulative baseline-hazard coefficient B₀(t) |
| `size` | (1) via R | cumulative `log10_size` coefficient B₁(t) |

### 23. `ust_discount_may6_12.parquet` — UST discount series (192 rows)
| Column | Origin | Notes |
|--------|--------|-------|
| `hours_from_may6` | (1) | hour index |
| `ust_discount_bp` | (2) KAIKO | (1 − UST price) in basis points, from the run-window UST price |

---

## `data/labels/` (author-created)

Each label set ships only the rows the runnable exhibits consume; the full master
label list is not redistributed. (The former `dex_swap_addresses.parquet`, dataset
#24, is removed — it was read only by `prep/prep_loss_panel.py`, which `run_all.py`
does not run and which needs un-shipped inputs.)

### 25. `interdm_addresses.parquet` (396 rows)
| Column | Origin | Notes |
|--------|--------|-------|
| `address` | (3) AUTHOR | intermediary wallets to exclude; reduced to the depositors Figs 13 & IA.4 actually test |

### 26. `anchor_contracts.csv` (11 rows)
Anchor cash-flow counterparties (address → readable name); consumed only as the Fig 3 legend map.
| Column | Origin | Notes |
|--------|--------|-------|
| `address` | (3) AUTHOR | Anchor market counterparty address |
| `address_name` | (3) AUTHOR | human-readable name (used Fig 3) |

### 27. `terra_labels_4vol.parquet` (233 rows)
| Column | Origin | Notes |
|--------|--------|-------|
| `address` | (3) AUTHOR | labeled address |
| `label_type` | (3) AUTHOR | coarse entity type for the volume/supply decomposition (`CEX`, `Anchor`, …) — used Fig 2; reduced to UST-holding addresses |

---

## `data/loss/` (Tables 2 & 3 inputs)

### 28. `anchor_loss_panel.parquet` — per-depositor loss + sophistication (159,669 rows)
**Built in-package** by `prep/prep_loss_panel.py`, reproducing the source notebook's `loss_reg`. Mixed provenance per column.

| Column | Origin | Notes |
|--------|--------|-------|
| `address` | (3) NODE | depositor address |
| `prerun_usd` | (1) shipped-derived | copied from shipped `depositor_prerun_size.parquet` (#29) |
| `full_maxusd` | (2) NODE | peak USD aUST balance over the window (un-shipped size panel); size-bin variable for Tabs 2/3 |
| `perc_loss` | (2) NODE | realized % loss; `get_flow_loss` over un-shipped transfers + pre/post node balances + run-window VWAP |
| `log_wealth` | (1) | `log(full_maxusd + 1)` |
| `log_volume_adj` | (2) NANSEN/NODE | log volume/balance ratio (from un-shipped `address_balance_volume_cex`) |
| `age` | (2) NODE | wallet age in days (un-shipped sophistication panel) |
| `log_age_months` | (1) | `log(age/30 + 1)` |
| `cex_degree` | (2) NANSEN/NODE | # CEX counterparties (un-shipped panel) |
| `used_bridge` | (2) NODE | bridge-user flag (un-shipped `address_using_bridges`) |

### 29. `depositor_prerun_size.parquet` — depositor size table (242,536 rows)
`full_maxusd` is added by `prep/build_fig13_inputs.py`; the other columns are the original shipped node-derived sizes. Used by Figs 10, 13; Tabs 2, 3.

| Column | Origin | Notes |
|--------|--------|-------|
| `address` | (3) NODE | depositor address |
| `prerun_aust` | (2) NODE | aUST balance on 2022‑05‑05 (transfer cumsum); used Fig 10 base level |
| `prerun_usd` | (2) NODE | `prerun_aust` valued in USD (× pre-run rate/price) |
| `full_maxusd` | (2) NODE | peak USD aUST balance over the window (added by prep from un-shipped size panel) |

---

## `data/native_swaps/`

### 30. `luna_total_supply_run.parquet` — hourly LUNA supply (337 rows; index `time`)
| Column | Origin | Notes |
|--------|--------|-------|
| `time` (index) | (2) NODE | hour |
| `luna_supply` | (2) NODE | base supply + cumulative net LUNA minted−burned on native swaps since 2021‑10‑01 (from the swap parse); used Fig 12 |

### 31. `ust_luna_swaps_run.parquet` — native swap events (277,342 rows)
Parsed `swap` events from the market module. Trader-less 4-column extract (the per-trader log behind Tables IA.1/IA.2 is not shipped). Originally Flipside; content on-chain. Used by Figs 11, IA.5.

| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (3) FLIPSIDE→NODE | swap time |
| `offer_amount` | (3) FLIPSIDE→NODE | coin offered |
| `swap_amount` | (3) FLIPSIDE→NODE | coin received |
| `fee_amount` | (3) FLIPSIDE→NODE | swap fee |

---

## `data/network/`

### 32. `volume_by_group_token.csv` — inter-entity volume (747 rows)
Pairwise transfer volume by entity-type pair and token. Used by Fig 4 (and underlies Table A.1 grouping).

| Column | Origin | Notes |
|--------|--------|-------|
| `volusd` | (2) NODE | summed USD transfer volume for the (srctype, tgttype, token) cell |
| `srctype` | (3) AUTHOR | sender entity type (author label applied to the address) |
| `tgttype` | (3) AUTHOR | recipient entity type (author label) |
| `token` | (3) NODE | token transferred |

---

## `data/prices/`

### 33. `luna_price_may2022.parquet` (21,600 rows)
| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (3) KAIKO | minute |
| `luna_price` | (2) KAIKO/DEX | `vwap_usd` = cross-exchange **volume-weighted** USD price. Used Fig 12 |

### 34. `ust_luna_minute_price_run.parquet` (31,661 rows)
**Built in-package** by `prep/build_swap_arb_price.py` from the un-shipped per-exchange minute panel. May‑2022 rows = single-venue FTX USD spot; May‑2021 rows = cross-exchange volume-weighted aggregate. Used by Figs 11, IA.5.

| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (2) | minute |
| `UST` | (2) KAIKO/DEX | UST USD price (FTX 2022 / aggregate 2021) |
| `LUNA` | (2) KAIKO/DEX | LUNA USD price (FTX 2022 / aggregate 2021) |

### 35. `ust_price_may2022.parquet` (21,600 rows)
| Column | Origin | Notes |
|--------|--------|-------|
| `time` | (3) KAIKO | minute |
| `ust_price` | (2) KAIKO/DEX | `price_usd` = cross-exchange **volume-weighted** USD price. Used Fig 10 |

---

## `data/tables/` (shipped computed results — raw per-tx logs too large/identifying to ship)

### 36. `table1_token_volume.csv` — Table 1 (15 rows)
From `vol_by_token` over the ~86M-tx node transfer log (`action ∈ {transfer, send}`, 2021‑10‑01..2022‑05‑06).

| Column | Origin | Notes |
|--------|--------|-------|
| `token` | (3) NODE | token denom |
| `label` | (3) AUTHOR | display label for the token |
| `volume_bn_usd` | (2) NODE | Σ USD volume over the transfer log |
| `tx_count` | (2) NODE | # transfers |

### 37. `tableIA1_native_swap_users_run.csv` — Table IA.1 (21 rows)
Top UST→LUNA swappers, May 7–13 2022, from the un-shipped per-trader native-swap log + author labels.

| Column | Origin | Notes |
|--------|--------|-------|
| `address` | (3) NODE | trader address (from the un-shipped per-trader swap log) |
| `vol_ust_m` | (2) NODE | Σ `offer_amount` in UST millions |
| `vol_usd_m` | (2) NODE + KAIKO | `vol_ust_m` × run-period UST price |
| `tx_count` | (2) NODE | # swaps |
| `label` | (3) AUTHOR | author-curated entity label |

### 38. `tableIA2_native_swap_users_run_2021.csv` — Table IA.2 (20 rows)
Top LUNA→UST swappers, May 19–27 2021 (no USD column; UST ≈ $1 then).

| Column | Origin | Notes |
|--------|--------|-------|
| `address` | (3) NODE | trader address (from the un-shipped per-trader swap log) |
| `vol_ust_m` | (2) NODE | Σ `swap_ust` (UST received) in millions |
| `tx_count` | (2) NODE | # swaps |
| `label` | (3) AUTHOR | author-curated entity label |
