"""Figure IA.4 — Anchor May 2021 outflows by size.

Reproduces ``paper/figures/May2021_run_by_size.png``: the remaining Anchor
deposit balance (normalized so May 17, 2021 = 1, log scale) over the May 2021
de-pegging (May 17–28), broken out by the size of each address's deposit
balance as of May 17. Individual addresses only; intermediaries and addresses
below 100 UST excluded.

Inputs (full-node hourly aUST balances + intermediary list; shippable):
    data/anchor_run/may2021_aust_run_balances.parquet   address, hour, balance
    data/labels/interdm_addresses.parquet               address (excluded)

Output: output/figures/May2021_run_by_size.png

Source notebook: code/230312-May2021-Run.ipynb (In[22-26]).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator, NullLocator, ScalarFormatter

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from figstyle import caption_rc, figsize_cm, MYWIDTH_CM  # noqa: E402

PAGE_W_CM, PAGE_H_CM = MYWIDTH_CM, 5.6   # true size; mywidth (0.7 textwidth)
YTICKS = [0.5, 1, 1.5, 2, 2.5, 3]   # readable labels on the log axis
BINS = [100, 1e3, 1e4, 1e5, 1e6, np.inf]
GROUPS = ["<1K", "1K-10K", "10K-100K", "100K-1M", ">1M"]
# colours matched to the published legend
COLORS = ["#1f77b4", "#d62728", "#e8b818", "#6b8e23", "#7f7f7f"]


def main() -> Path:
    aub = pd.read_parquet(datadir("anchor_run", "may2021_aust_run_balances.parquet"))
    interdm = set(pd.read_parquet(datadir("labels", "interdm_addresses.parquet"))["address"])

    pre = aub[aub["hour"] == aub["hour"].min()].copy()
    pre["balance_group"] = pd.cut(pre["balance"], bins=BINS, labels=GROUPS)

    aub = aub[~aub["address"].isin(interdm)].merge(pre[["address", "balance_group"]])
    wide = (aub.groupby(["balance_group", "hour"], observed=True)["balance"].sum()
              .unstack("balance_group"))[GROUPS]
    norm = wide.div(wide.iloc[0]).loc[:"2021-05-28"]

    out = figpath("May2021_run_by_size.png")
    with plt.rc_context(caption_rc()):
        fig, ax = plt.subplots(figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM))
        for g, c in zip(GROUPS, COLORS):
            ax.plot(norm.index, norm[g], color=c, lw=1.5, label=g)
        ax.set_yscale("log")
        ax.set_ylim(0.5, 3)
        # readable, evenly-labelled log ticks (0.5, 1, 1.5, ... 3) instead of the
        # cluttered default log decades/minors (author review).
        ax.yaxis.set_major_locator(FixedLocator(YTICKS))
        ax.yaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_major_formatter(ScalarFormatter())
        ax.set_ylabel("Balance (May 17 = 1)")
        ax.grid(True, alpha=0.3, which="major")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        ax.legend(title="Deposit size")

        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
