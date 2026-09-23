"""Figure IA.3 — May 2021 de-pegging event.

Reproduces ``paper/figures/May2021-run-dynamics.png``: the outstanding Anchor
deposit balance (black, left axis, MM UST) and the UST price (red, right axis)
during the May 2021 de-pegging, May 17–30, 2021.

Input (node Anchor deposit balance + Kaiko UST price, minute; shippable):
    data/anchor_run/may21_anchor_run_prices.parquet   index minute; cols aust_deposit, price

Output: output/figures/May2021-run-dynamics.png

Source notebook: code/230312-May2021-Run.ipynb (In[4]).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from figstyle import caption_rc, figsize_cm, integer_yaxis, MYWIDTH_CM  # noqa: E402

PRICE_COLOR = "#e54e5f"
PAGE_W_CM, PAGE_H_CM = MYWIDTH_CM, 5.6   # true size; mywidth (0.7 textwidth)


def main() -> Path:
    aust = pd.read_parquet(datadir("anchor_run", "may21_anchor_run_prices.parquet")).loc[:"2021-05-30"]

    out = figpath("May2021-run-dynamics.png")
    with plt.rc_context(caption_rc()):
        fig, axL = plt.subplots(figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM))
        axL.plot(aust.index, aust["aust_deposit"] / 1e6, color="black", lw=1.5)
        axL.set_ylim(250, 320)
        axL.set_ylabel("Anchor deposit (MM UST)", color="black")
        axL.grid(True, alpha=0.3)
        integer_yaxis(axL)
        axL.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

        axR = axL.twinx()
        axR.plot(aust.index, aust["price"], color=PRICE_COLOR, lw=1.0)
        axR.set_ylim(0.85, 1.08)
        axR.set_ylabel("UST/USD price", color=PRICE_COLOR)
        axR.tick_params(axis="y", labelcolor=PRICE_COLOR)
        axR.axhline(1.0, color=PRICE_COLOR, lw=0.4, ls=":")

        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
