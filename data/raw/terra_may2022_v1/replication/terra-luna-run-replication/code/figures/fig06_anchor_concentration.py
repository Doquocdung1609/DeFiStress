"""Figure 6 — Concentration of Anchor deposits.

Reproduces ``paper/figures/Anchor_deposit_conc.png`` (left) and
``paper/figures/Anchor_amount_histogram.png`` (right).

Left  — share of Anchor deposits held by the top 10 / 100 / 1000 depositors on
        each day (May 2021 – May 2022), excluding intermediaries.
Right — histogram of the number of individual wallets by pre-run (May 6, 2022)
        Anchor deposit size (UST, log scale), excluding exchanges, smart
        contracts and other intermediaries.

Inputs (node-derived aUST balances + author labels; shippable):
    data/anchor/anchor_deposit_concentration.parquet
        pre-computed top-k deposit shares (Top 10/100/1000), see
        code/prep/prep_fig06_concentration.py for the derivation from the raw
        Columbus-4/5 aUST balances + interdm exclusion list.
    data/anchor/prerun_deposits.parquet      cols: address, balance (aUST, 2022-05-05)
    data/anchor/Anchor_daily_stats.parquet   col: aUST/UST (to convert aUST -> UST)

Output (two separate panels, matching the paper's two subfigures):
    output/figures/Anchor_deposit_conc.png       (left panel)
    output/figures/Anchor_amount_histogram.png   (right panel)

Source notebook: code/230305-summary-stats.ipynb (In[87-93], In[97]); originally
holoviews; re-implemented in matplotlib.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from figstyle import caption_rc, figsize_cm, integer_yaxis, quarter_date_axis  # noqa: E402

PANEL_W_CM, PAGE_H_CM = 7.75, 5.25   # each panel drawn separately at ~half-textwidth (0.49\linewidth)

# histogram bin edges: 10, 30, 100, 300, ... 1e7, 3e7 UST
BINS = np.outer(10.0 ** np.arange(1, 8), [1, 3]).reshape(-1)


def _readable(num: float) -> str:
    if num < 1e3:
        return str(int(round(num)))
    if num < 1e6:
        return f"{round(num/1e3)}K"
    if num < 1e9:
        return f"{round(num/1e6)}M"
    return f"{round(num/1e9)}B"


def main() -> list:
    adconc = pd.read_parquet(datadir("anchor", "anchor_deposit_concentration.parquet"))
    pre = pd.read_parquet(datadir("anchor", "prerun_deposits.parquet"))
    aust_ust = pd.read_parquet(datadir("anchor", "Anchor_daily_stats.parquet"),
                               columns=["aUST/UST"]).loc["2022-05-06", "aUST/UST"]

    outL = figpath("Anchor_deposit_conc.png")
    outR = figpath("Anchor_amount_histogram.png")
    with plt.rc_context(caption_rc()):
        # --- left panel: concentration ---
        figL, axL = plt.subplots(figsize=figsize_cm(PANEL_W_CM, PAGE_H_CM))
        for col, color in zip(["Top 10", "Top 100", "Top 1000"],
                              ["#30a2da", "#fc4f30", "#e8b818"]):
            axL.plot(adconc.index, adconc[col], lw=1.6, label=col, color=color)
        axL.set_ylim(0, 100)
        axL.set_ylabel("Share of deposits (%)")
        axL.margins(x=0)
        axL.grid(True, alpha=0.3)
        integer_yaxis(axL)
        quarter_date_axis(axL)
        axL.legend(title="Depositor size", loc="upper right")
        figL.tight_layout()
        figL.savefig(outL, dpi=300, bbox_inches="tight")
        plt.close(figL)

        # --- right panel: pre-run deposit-size histogram ---
        figR, axR = plt.subplots(figsize=figsize_cm(PANEL_W_CM, PAGE_H_CM))
        ust = (pre["balance"].astype(float) * float(aust_ust))
        ust = ust[ust > 0]
        axR.hist(np.log10(ust), bins=np.log10(BINS), color="#1f77b4",
                 edgecolor="white", linewidth=0.4)
        ticks = 10.0 ** np.arange(1, 8)   # label powers of 10 only (drop 30, 300, 3K, ...)
        axR.set_xticks(np.log10(ticks))
        axR.set_xticklabels([_readable(b) for b in ticks])
        axR.set_xlabel("pre-run Anchor deposit (UST)")
        axR.set_ylabel("Number of addresses")
        axR.grid(True, alpha=0.3)
        integer_yaxis(axR)
        figR.tight_layout()
        figR.savefig(outR, dpi=300, bbox_inches="tight")
        plt.close(figR)
    print(f"wrote {outL}")
    print(f"wrote {outR}")
    return [outL, outR]


if __name__ == "__main__":
    main()
