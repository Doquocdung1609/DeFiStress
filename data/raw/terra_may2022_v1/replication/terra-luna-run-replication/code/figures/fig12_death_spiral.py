"""Figure 12 — LUNA death spiral.

Reproduces ``paper/figures/Run_LUNA_supply_price.png``: the circulating LUNA
supply (black, left axis) and the LUNA price (orange, right axis) during the
run, both on log scales. Convertibility between LUNA and UST was suspended on
May 13, 2022.

Inputs (LUNA supply rebuilt from native-swap mint/burn — on-chain; LUNA price
from Kaiko — both redistributed minimally with acknowledgment):
    data/native_swaps/luna_total_supply_run.parquet   time, luna_supply (hourly)
    data/prices/luna_price_may2022.parquet            time, luna_price (minute)

The supply series is precomputed (shipped as data #30; see Datasets.md): hourly
cumulative net LUNA created on the native swap market since 2021-10-01, added to
the base supply, over May 1–15, 2022.

Output:
    output/figures/Run_LUNA_supply_price.png

Source notebook: code/230103-terraluna-supply.ipynb (In[127-139]).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import LogLocator, FuncFormatter, NullFormatter

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from figstyle import caption_rc, figsize_cm, readable_number, readable_price, MYWIDTH_CM  # noqa: E402

SUPPLY_COLOR = "black"
PRICE_COLOR = "#E96C1F"
PAGE_W_CM, PAGE_H_CM = MYWIDTH_CM, 5.9   # true size; mywidth (0.7 textwidth)


def main() -> Path:
    sup = pd.read_parquet(datadir("native_swaps", "luna_total_supply_run.parquet"))
    prc = pd.read_parquet(datadir("prices", "luna_price_may2022.parquet"))
    prc = prc.set_index("time")["luna_price"].resample("h").last().reindex(sup.index).ffill()

    out = figpath("Run_LUNA_supply_price.png")
    with plt.rc_context(caption_rc()):
        fig, axL = plt.subplots(figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM))
        axL.plot(sup.index, sup["luna_supply"], color=SUPPLY_COLOR, lw=1.6)
        axL.set_yscale("log")
        axL.set_ylim(10 ** 8.3, 10 ** 13.3)
        axL.set_ylabel("LUNA supply", color=SUPPLY_COLOR)
        axL.grid(True, alpha=0.3)
        axL.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        # readable left-axis labels: 300M, 1B, 3B, ... 1T, 3T, 10T (ticks at 1,3)
        axL.yaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 3.0), numticks=20))
        axL.yaxis.set_minor_locator(LogLocator(base=10, subs=(2, 4, 5, 6, 7, 8, 9), numticks=80))
        axL.yaxis.set_minor_formatter(NullFormatter())
        axL.yaxis.set_major_formatter(FuncFormatter(lambda v, _: readable_number(v)))

        axR = axL.twinx()
        axR.plot(prc.index, prc.to_numpy(), color=PRICE_COLOR, lw=1.6)
        axR.set_yscale("log")
        axR.set_ylim(10 ** -6, 10 ** 2)
        axR.set_ylabel("LUNA/USD price", color=PRICE_COLOR)
        axR.tick_params(axis="y", labelcolor=PRICE_COLOR)
        # readable right-axis labels for >= $0.01 (100, 10, 1, 0.1, 0.01),
        # scientific (10^-n) below $0.01, per author review.
        axR.yaxis.set_major_locator(LogLocator(base=10, subs=(1.0,), numticks=20))
        axR.yaxis.set_major_formatter(FuncFormatter(lambda v, _: readable_price(v)))

        axL.axvline(pd.to_datetime("2022-05-13"), color="black", lw=1, ls="dashed")
        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
