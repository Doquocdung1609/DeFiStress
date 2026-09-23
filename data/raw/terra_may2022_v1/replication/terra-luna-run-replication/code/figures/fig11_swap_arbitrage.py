"""Figure 11 — Swap arbitrage on the Terra native swap market (May 2022 run).

Reproduces ``paper/figures/swap_arb.png`` (and, via ``swap_arb_window``, the
May-2021 panel ``swap_arb_may2021.png`` = Figure IA.5).

Top    — the UST discount (black) and the native swap fee (blue), in percent.
Middle — the arbitrage spread = max(UST discount − swap fee, 0): the gain from
         swapping UST for LUNA at the protocol rate rather than selling UST.
Bottom — dollar value of UST swapped for LUNA per minute ($M).

Inputs (minimal extracts; native swaps orig. Flipside, prices from Kaiko — both
on-chain/market content, redistributed with acknowledgment — see README):
    data/native_swaps/ust_luna_swaps_run.parquet   time, offer_amount, swap_amount, fee_amount
    data/prices/ust_luna_minute_price_run.parquet  time, UST, LUNA  (minute USD price)

Output:
    output/figures/swap_arb.png

Source notebook: code/Terra-analysis-native-swaps-run-20230324.ipynb
(`ust_luna_swap_arb`, In[24/27]); already matplotlib. The discount adjustment
``ust_discount_adj = ust_discount * (fee+swap) * LUNA / offer`` is reproduced
verbatim from that cell (confirmed against the original notebook).

Price series (important — sets the y-scale): ``ust_discount_adj`` is linear in
the LUNA price, and the two published panels used DIFFERENT price series.  Fig 11
(May 2022) used single-venue **FTX** USD spot; Fig IA.5 (May 2021) used the
cross-exchange volume-weighted aggregate.  Both are baked into the shipped
``ust_luna_minute_price_run.parquet`` per window by ``prep/build_swap_arb_price.py``
(read its header).  NB: the *final* state of the source notebook fed the
cross-exchange aggregate to both panels, which doubles the May-2022 discount/spread
(peaks ~165%/~156% vs the published ~84%/~66%) because the aggregate LUNA price ran
up to ~3x the FTX price during the crash; the published ``swap_arb.png`` predates
that notebook edit, so we ship the FTX price to match it.
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
from figstyle import caption_rc, figsize_cm, integer_yaxis  # noqa: E402

PANEL_AR = 11 / 15   # height/width aspect, kept at true on-page size


def swap_arb_window(start: str, end: str, outname: str, time_fmt: str = "%m-%d",
                    page_w_cm: float = 15) -> Path:
    swap = pd.read_parquet(datadir("native_swaps", "ust_luna_swaps_run.parquet"))
    price = pd.read_parquet(datadir("prices", "ust_luna_minute_price_run.parquet"))

    df = swap[(swap["time"] >= start) & (swap["time"] <= end)].set_index("time")
    per = df.resample("min").agg(fee_amount=("fee_amount", "sum"),
                                 swap_amount=("swap_amount", "sum"),
                                 offer_amount=("offer_amount", "sum")).reset_index()
    per["fee_perc"] = 100 * per["fee_amount"] / (per["fee_amount"] + per["swap_amount"])

    m = per.merge(price, on="time", how="inner")
    m["ust_discount"] = 100 * (1 - m["UST"])
    m["ust_discount_adj"] = (m["ust_discount"] * (m["fee_amount"] + m["swap_amount"])
                             * m["LUNA"] / m["offer_amount"]).clip(lower=0)

    out = figpath(outname)
    with plt.rc_context(caption_rc()):
        fig, axs = plt.subplots(3, 1, figsize=figsize_cm(page_w_cm, page_w_cm * PANEL_AR), sharex=True)
        axs[0].plot(m["time"], m["fee_perc"], color="tab:blue", label="swap fee")
        axs[0].plot(m["time"], m["ust_discount_adj"], color="black", label="UST discount")
        axs[0].set_ylabel("(%)")
        axs[0].legend()
        axs[0].grid(alpha=0.4)

        axs[1].plot(m["time"], np.maximum(m["ust_discount_adj"] - m["fee_perc"], 0), color="tab:red")
        axs[1].set_ylabel("arbitrage spread (%)")
        axs[1].grid(alpha=0.4)

        axs[2].plot(m["time"], m["swap_amount"] * m["LUNA"] / 1e6, color="tab:blue")
        axs[2].set_ylabel("swap volume ($M)")
        axs[2].grid(alpha=0.4)
        axs[2].xaxis.set_major_formatter(mdates.DateFormatter(time_fmt))

        for ax in axs:
            integer_yaxis(ax)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


def main() -> Path:
    return swap_arb_window("2022-05-07", "2022-05-13", "swap_arb.png")


if __name__ == "__main__":
    main()
