"""Build-time extractor for the swap-arbitrage price input (NOT part of ``run_all``).

Rebuilds the minute price series consumed by the swap-arbitrage figures::

    data/prices/ust_luna_minute_price_run.parquet   time, UST, LUNA   (USD)

used by ``fig11_swap_arbitrage`` (May 2022 run) and ``figIA5_swap_arbitrage_2021``
(May 2021 de-peg).  Both call ``swap_arb_window`` and read this one file.

Why two price definitions in one file
-------------------------------------
The discount adjustment plotted by both figures,

    ust_discount_adj = 100*(1-UST) * (fee_amount + swap_amount) * LUNA / offer_amount,

is *linear in the LUNA price*, so the choice of price series sets the y-scale.
The two published panels were generated from **different** price series, and this
script reproduces each panel's source faithfully:

* **May 2022 (Fig 11)** — single-venue **FTX** USD spot (`price_native`, USD quote).
  This is the original code path inside ``ust_luna_swap_arb`` (the commented-out
  ``df_price`` block / cell ``ftx_tmp`` of the source notebook).  The notebook was
  later edited to pass the *cross-exchange* volume-weighted aggregate instead, but
  the published ``swap_arb.png`` predates that edit.  During the crash the
  cross-exchange LUNA price ran ~1.5-2x the FTX price (DEX/other-venue prints
  stayed elevated while FTX's LUNA fell faster), which roughly DOUBLED the
  discount/spread y-scale.  Using FTX reproduces the published figure
  (discount peaks ~84%, spread ~66%); the aggregate gives ~165%/~156%.

* **May 2021 (Fig IA.5)** — the cross-exchange volume-weighted aggregate
  (`price_usd` summed across all venues, the notebook's ``price21_agg`` recipe).
  FTX carried no UST/LUNA USD pair in May 2021, so the published IA.5 panel used
  the aggregate; it reproduces that panel (discount ~15%, spread ~8.6%).

Source notebook: ``code/Terra-analysis-native-swaps-run-20230324.ipynb``
    (``ust_luna_swap_arb`` + price cells ``price21_agg`` [In 58-62] / ``ftx_tmp`` [In 33]).

Raw input (authors' research tree; market data, not on the Terra node — see
Datasets.md):
    data/terra_minute_price_volume_exchgusd.parquet
        exchange, base_asset, quote_asset, minute, sell_amount, price_usd, price_native
    (per-exchange per-minute Kaiko/DEX price & volume, ~25M rows; not shipped.)

Run (authors' environment only):  python prep/build_swap_arb_price.py
"""
import sys
from pathlib import Path

import pandas as pd

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(CODE_DIR))
from config import datadir, PKG_ROOT  # noqa: E402

# Raw research-data tree (repo ``data/``): replication_package -> publish -> code -> Terra.
RAW = PKG_ROOT.parents[2] / "data" / "terra_minute_price_volume_exchgusd.parquet"

# Plot windows (match the figure calls + the prior shipped coverage).
WIN_2021 = ("2021-05-17 00:00:00", "2021-05-30 23:59:59")   # Fig IA.5
WIN_2022 = ("2022-05-07 00:00:00", "2022-05-14 23:59:59")   # Fig 11


def _ftx_native(price: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Single-venue FTX USD spot (UST, LUNA) — the published Fig 11 price."""
    f = price[(price.exchange == "FTX")
              & price.base_asset.isin(["UST", "LUNA"])
              & (price.quote_asset == "USD")
              & (price.minute >= start) & (price.minute <= end)]
    p = f.pivot_table(index="minute", columns="base_asset",
                      values="price_native", aggfunc="mean")
    return p.ffill().bfill()


def _xexch_aggregate(price: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Cross-exchange volume-weighted USD price (the notebook's ``price21_agg``).

    Computed over the full series so the ffill/bfill matches the notebook, then
    sliced to the window.  This is the published Fig IA.5 price.
    """
    p = price[price.base_asset.isin(["UST", "WUST", "LUNA"])].copy()
    p["base_asset"] = p["base_asset"].str.replace("WUST", "UST")
    p["sell_amount_usd"] = p["sell_amount"] * p["price_usd"]
    p = p[p["price_usd"].notnull()]
    agg = (p.groupby(["base_asset", "minute"])
             .agg(sell_amount_usd=("sell_amount_usd", "sum"),
                  sell_amount=("sell_amount", "sum"))
             .eval("price_usd = sell_amount_usd / sell_amount"))
    agg = agg.loc[agg.sell_amount_usd >= 1000, "price_usd"].unstack("base_asset")
    agg = agg.ffill().bfill()
    return agg[(agg.index >= start) & (agg.index <= end)]


def main() -> None:
    price = pd.read_parquet(
        RAW, columns=["exchange", "base_asset", "quote_asset",
                      "minute", "sell_amount", "price_usd", "price_native"])

    p21 = _xexch_aggregate(price, *WIN_2021)   # Fig IA.5 (May 2021)
    p22 = _ftx_native(price, *WIN_2022)         # Fig 11   (May 2022)

    out = (pd.concat([p21, p22])
             .rename_axis("time").reset_index()[["time", "UST", "LUNA"]]
             .sort_values("time", ignore_index=True))
    dest = datadir("prices", "ust_luna_minute_price_run.parquet")
    out.to_parquet(dest, index=False)
    print(f"  ust_luna_minute_price_run.parquet: {len(out):,} rows "
          f"({(out.time < '2022-01-01').sum():,} May-2021 aggregate + "
          f"{(out.time >= '2022-01-01').sum():,} May-2022 FTX) -> {dest}")


if __name__ == "__main__":
    main()
