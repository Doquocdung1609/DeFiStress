# Replication package — "Anatomy of a Run: The Terra Luna Crash"

Liu, Makarov, and Schoar — *Journal of Financial Economics* (final revision).

This README follows the [Social Science Data Editors README
template](https://social-science-data-editors.github.io/template_README/) and
the [JFE data & code sharing policy](https://www.jfinec.com/data-and-code-sharing-policy).

---

## Overview

The code in this replication package reproduces the figures and tables in the
paper from the data in `data/`. All analysis is in Python. Each exhibit is
produced by a self-contained script under `code/figures/` (or `code/tables/`);
`code/run_all.py` runs them all. Replicators can expect the ported figures to
run in a few minutes on a laptop.

## Data availability and provenance

### Rights statement
The authors certify that they have the legal right to distribute all data
included in this package. The package is **self-contained**: it ships every
dataset needed to reproduce the figures and tables, and only those datasets
(no unused files).

### Summary of availability
- **All data needed to plot are included.** `data/` contains the minimal
  processed inputs each exhibit reads. Most are derived from the **public Terra
  Classic blockchain**; others are public **CoinGecko** price series or
  **author-created address labels**.
- **Minimal third-party-derived extracts are included with acknowledgment.**
  Some figures use small processed slices that originated from commercial
  providers — exchange prices/order-book aggregates from **Kaiko**, preprocessed
  swap/Curve tables from **Flipside**, and balance/transfer slices from
  **Nansen**. We redistribute only the minimal slice each figure plots and
  gratefully acknowledge these providers (see Acknowledgments). The underlying
  raw feeds are not redistributed.
- **Provenance / rebuild-from-node.** For on-chain-content files (including those
  originally pulled via Flipside/Nansen), the underlying content is public Terra
  Classic on-chain data and can be rebuilt from a Columbus-5 archive node; the
  Sources table above gives the node, genesis, and query pointers.

### Acknowledgments
Address labels and processed tables were obtained with the help of **Nansen**
and **Flipside**; exchange trading data are from **Kaiko**. We thank these
providers. Redistributed extracts here are limited to what is necessary to
reproduce the paper's exhibits.

### Sources
| Source | Role in paper | In this package? | How to obtain / rebuild |
|--------|---------------|------------------|--------------------------|
| **Terra Classic blockchain (archive node)** | token transfers, balances, Anchor on-chain state, native swaps, supply | **derived files included** | Run a Columbus-5 full node from [ChainLayer Quicksync](https://quicksync.io/networks/terra.html); query via LCD/RPC. See `Datasets.md` for per-file provenance. Public. |
| **Genesis files** (Columbus-1…5) | initial balances for reconstruction | reconstructed series included | [github.com/terra-money/classic-mainnet](https://github.com/terra-money/classic-mainnet). Public. |
| **CoinGecko** | LUNA/UST market-cap & price series | **included** (`data/external/*.csv`) | CoinGecko public exports. |
| **Author-created address labels** | entity classification | **included** (`data/labels/`) | Created by the authors from public sources + manual inspection; only the rows each exhibit uses are shipped. |
| **Flipside** | preprocessed swaps, governance, airdrops, Ethereum/Curve | **minimal extracts included** (acknowledged) | Was [flipsidecrypto.xyz](https://flipsidecrypto.xyz/). On-chain content also rebuildable from the node. |
| **Snowflake / Nansen** | daily balance / transfer slices | **minimal extracts included** (acknowledged) | On-chain content rebuildable from the node. |
| **Kaiko** | exchange price / volume series used in run figures | **minimal extracts included** (acknowledged) | Commercial provider ([kaiko.com](https://www.kaiko.com/)); only the plotted series are shipped. |

## Dataset list
The package ships **38 datasets in 13 subfolders** under `data/`. See **`Datasets.md`**
for the complete catalog: every file, its primary source, the exhibits that use it, and
full per-column provenance. The **Sources** table above summarizes where each provider's
data comes from.

## Computational requirements
- **Software:** Python 3.13 (tested). Packages in `requirements.txt`
  (pandas, numpy, matplotlib, pyarrow; statsmodels for the regression tables;
  scipy for the Fig 14 kernel recovery). Install: `pip install -r requirements.txt`.
- **R (optional, Figure 14 only):** the time-varying Cox hazard model is estimated
  in R with `timereg::timecox` (a compiled-C estimator with no Python equivalent).
  The estimation code is `code/figures/fit_timecox.R`; its output (the cumulative
  coefficients `data/hazard/timecox_cum_may6_12.parquet`) is **shipped**, so
  Figure 14 — and the whole package — is redrawn in Python without R. Re-run the R
  script only to regenerate that parquet; not required for any other exhibit.
  Tested with R 4.5. Install the three required packages once, then run:
  ```bash
  Rscript -e 'install.packages(c("timereg","survival","arrow"), repos="https://cloud.r-project.org")'
  Rscript code/figures/fit_timecox.R
  ```
  The fit is single-threaded and takes ≈3 h on the full 90,768-event panel; it
  runs in < 1 GB because the script sets `robust = 0` (this leaves the estimated
  coefficients unchanged — only the unused robust-variance step is skipped, which
  would otherwise allocate ~100 GB on a panel this size).
- **Memory/runtime:** the ported Python exhibits run in a few minutes and < 2 GB;
  the optional R re-estimation above is the sole exception (≈3 h, < 1 GB).

## Description of code
```
code/
  config.py                 relocatable path configuration
  run_all.py                runs all ported exhibit scripts
  lib/terra_lib.py          shared helpers (labels, flow aggregation, stacked area)
  lib/figstyle.py           shared figure-styling helpers (on-page sizing, axes, tick labels)
  figures/figNN_*.py        one script per figure
  tables/fmt_*.py           one script per data-driven table (Tables 1–3, IA.1–IA.2)
  prep/                     build scripts for derived inputs. prep_fig06_concentration.py
                            runs in run_all (rebuilds a shipped file from shipped data);
                            the other prep scripts are authors-only provenance and need
                            un-shipped raw inputs (not required to reproduce any exhibit)
data/                       shipped inputs (public / on-chain-derived only)
output/figures, output/tables   regenerated exhibits
```

## Instructions to replicators
```bash
pip install -r requirements.txt
cd code
python run_all.py            # writes figures to ../output/figures/
```
Run a single exhibit, e.g. `python run_all.py fig03`, or
`python figures/fig03_anchor_cashflow.py` directly.

## List of exhibits and code
The 19 figures, Tables 1–3, and Tables IA.1–IA.2 are generated by `run_all.py`; Table A.1
ships as a static `.tex`.

Each script writes its output under the **exact filename the paper expects** — figures
under the paper's `\includegraphics` name and tables under its `\input{tables/...}` name —
so the contents of `output/figures/` and `output/tables/` can be copied straight into the
paper's `figures/` and `tables/` folders and the manuscript compiles unchanged. Four
figures that appear as two side-by-side panels in the paper (Figs 3, 4, 6, IA.1) are each
written as **two separate files**, one per panel.

The last column gives **one line number per output file**: the line that writes that file —
`fig.savefig(...)` for figures, `out.write_text(...)` for tables. Line numbers refer to the
script in the "Script" column, except for Figs IA.2 and IA.5, which are thin wrappers that
call the shared plotting function of Fig 8 / Fig 11 (the file holding the line is named).

| Exhibit | Script | Output file(s) (= paper `\includegraphics` / `\input` name) | Line that writes the output |
|---------|--------|--------------------------------------------------------------|------------------------------|
| Fig 1 — Anchor net rates & recursive loans | `figures/fig01_anchor_net_rates.py` | `Anchor_net_rates_recursive_loans.png` | L74 |
| Fig 2 — UST supply by entity | `figures/fig02_ust_supply_by_entity.py` | `ust_supply_by_entity.png` | L84 |
| Fig 3 — Cash-flow decomposition on Anchor | `figures/fig03_anchor_cashflow.py` | `anchor_cash_flow.png` (left) · `anchor_reserve_injection.png` (right) | L127 (left) · L147 (right) |
| Fig 4 — Network volume of UST/LUNA | `figures/fig04_network_volume.py` | `UST_new.png` (left) · `Luna_new.png` (right) | L243 (both panels) |
| Fig 5 — LUNA & UST market cap | `figures/fig05_market_cap.py` | `mkt_cap2.png` | L69 |
| Fig 6 — Concentration of Anchor deposits | `figures/fig06_anchor_concentration.py` | `Anchor_deposit_conc.png` (left) · `Anchor_amount_histogram.png` (right) | L78 (left) · L95 (right) |
| Fig 7 — Anchor flows on May 7 (wallet A/B) | `figures/fig07_wallet_A_B.py` | `wallet_A_B.png` | L92 |
| Fig 8 — UST-3Crv swaps (May 7) | `figures/fig08_curve_swaps.py` | `curve_swap_May7.png` | L113 |
| Fig 9 — Binance UST/USDT trades | `figures/fig09_binance_ustusdt.py` | `binance_May7.png` | L84 |
| Fig 10 — Anchor run outflows | `figures/fig10_run_outflows.py` | `Run_deposit_outflow3.png` | L96 |
| Fig 11 — Swap arbitrage | `figures/fig11_swap_arbitrage.py` | `swap_arb.png` | L92 |
| Fig 12 — LUNA death spiral | `figures/fig12_death_spiral.py` | `Run_LUNA_supply_price.png` | L75 |
| Fig 13 — Anchor outflows by size | `figures/fig13_outflow_by_size.py` | `Run_outflow_by_size_combined_240518.png` | L135 |
| Fig 14 — Cox time-varying hazard (R `timecox`) | `figures/fig14_cox_hazard.py` | `Run22-Cox-hazard.png` | L153 |
| Fig IA.1 — LUNA staking-yield decomposition | `figures/figIA1_staking_yield.py` | `LUNA_staking_decomposition.png` (left) · `Anchor_ANC_subsidy_rate.png` (right) | L76 (left) · L89 (right) |
| Fig IA.2 — UST-3Crv swaps (May 2021) | `figures/figIA2_curve_swaps_2021.py` | `curve_swap_may2021.png` | `fig08_curve_swaps.py` L113 |
| Fig IA.3 — May 2021 de-pegging dynamics | `figures/figIA3_may2021_dynamics.py` | `May2021-run-dynamics.png` | L53 |
| Fig IA.4 — May 2021 outflows by size | `figures/figIA4_may2021_by_size.py` | `May2021_run_by_size.png` | L70 |
| Fig IA.5 — Swap arbitrage (May 2021) | `figures/figIA5_swap_arbitrage_2021.py` | `swap_arb_may2021.png` | `fig11_swap_arbitrage.py` L92 |
| Table 1 — Token volume | `tables/fmt_table1_token_volume.py` | `network_volume_by_token.tex` | L49 |
| Table 2 — Summary statistics | `tables/fmt_table2_loss_summary.py` | `anchor_loss_summary.tex` | L88 |
| Table 3 — Loss regression | `tables/fmt_table3_loss_regression.py` | `anchor_loss_regression.tex` | L93 |
| Table IA.1 — Top native-swap addresses (May 2022 run) | `tables/fmt_tableIA1_native_swap_run.py` | `native_swap_users_run.tex` | L88 |
| Table IA.2 — Top native-swap addresses (May 2021 de-peg) | `tables/fmt_tableIA2_native_swap_run_2021.py` | `native_swap_users_run_2021.tex` | L83 |
| Table A.1 — Address categories (static) | shipped `.tex` | `network_entity_classification.tex` | — (no code; static file) |

## License
This package is dual-licensed (full text in [`LICENSE`](LICENSE)):

- **Code** — everything under `code/` — is released under the **MIT License**.
- **Data and generated exhibits** — everything under `data/` and `output/` — are
  released under the **Creative Commons Attribution 4.0 International (CC-BY-4.0)**
  License (https://creativecommons.org/licenses/by/4.0/).

When reusing the data, please cite the paper and credit the third-party providers
named in the Acknowledgments. CC-BY-4.0 covers the authors' compilation and
processing; reuse of the provider-derived extracts (Kaiko, Flipside, Nansen) may
additionally be subject to those providers' own terms.
