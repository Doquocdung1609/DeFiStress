"""Prep — Anchor deposit concentration series (input to Figure 6, left panel).

Builds ``data/anchor/anchor_deposit_concentration.parquet`` (daily share of
Anchor aUST deposits held by the top 10 / 100 / 1000 depositors, excluding
intermediaries) by stitching the Columbus-4 and Columbus-5 periods.

Shipped inputs (small; both derived from on-chain aUST balances, intermediaries
already excluded):
    data/anchor/aust_topk_col4.parquet   Columbus-4 daily {total, t10, t100, t1000} aUST sums
    data/anchor/aust_rnk_col5.parquet    Columbus-5 ranked aUST balances (date, address, balance, rnk)
    data/anchor/aust_supply_col5.parquet Columbus-5 daily aUST supply (date, supply)

Provenance: the Columbus-4 sums are aggregated from the full node aUST balance
panel (`daily_aust_col4_balances`, ~134 MB, not shipped — available from the
archive node); the Columbus-5 rank/supply tables were originally pulled from the
daily_balance_by_token table (Nansen) but their content is on-chain aUST
balances and is rebuildable from the node. See Datasets.md.

Run:  python prep/prep_fig06_concentration.py
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from config import datadir  # noqa: E402

END = "2022-05-06"


def main() -> Path:
    # Columbus-4: shares from pre-aggregated top-k sums
    c4 = pd.read_parquet(datadir("anchor", "aust_topk_col4.parquet"))
    c4sh = c4[["t10", "t100", "t1000"]].div(c4["total"], axis=0)

    # Columbus-5: shares from ranked balances + daily supply
    rnk = pd.read_parquet(datadir("anchor", "aust_rnk_col5.parquet"))
    sup = pd.read_parquet(datadir("anchor", "aust_supply_col5.parquet")).set_index("date")
    c5 = (sup.join(rnk.loc[rnk.rnk <= 10].groupby("date").agg(t10=("balance", "sum")))
             .join(rnk.loc[rnk.rnk <= 100].groupby("date").agg(t100=("balance", "sum")))
             .join(rnk.loc[rnk.rnk <= 1000].groupby("date").agg(t1000=("balance", "sum"))))
    c5sh = c5[["t10", "t100", "t1000"]].div(c5["supply"], axis=0)

    adconc = pd.concat([c4sh, c5sh]) * 100
    adconc.index = pd.to_datetime(adconc.index)
    adconc = adconc.sort_index().loc[:END]
    adconc.columns = ["Top 10", "Top 100", "Top 1000"]

    out = datadir("anchor", "anchor_deposit_concentration.parquet")
    adconc.to_parquet(out)
    print(f"wrote {out}  {adconc.shape}")
    return out


if __name__ == "__main__":
    main()
