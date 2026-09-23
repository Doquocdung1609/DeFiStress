"""Figure 8 — UST-3Crv swap transactions on May 7, 2022.

Reproduces ``paper/figures/curve_swap_May7.png``.
Top   — each UST swap on the Curve UST-3Pool against USDT/USDC/DAI on May 7,
        2022. Swaps of UST into the other stablecoins (sells) are red; swaps
        into UST (buys) are green. Swap size is plotted in log10.
Bottom— net signed (buy minus sell) cumulative volume in millions (blue, left)
        and the UST price deviation from $1 in basis points (black, right).

Input (Curve/Ethereum swap txs, originally Flipside; minimal May 7 slice,
redistributed with acknowledgment — content is public Ethereum data):
    data/curve/curve_ust_3pool_may7.parquet
        columns: time, sell_amount, taker_side_sell, trader, price_native, quote_asset

Output:
    output/figures/curve_swap_May7.png

Source notebook: code/Terra-run-analysis-curve.ipynb (`plot_curve_swap_crash`,
In[37/39]); already matplotlib.
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

START, END = "2022-05-07", "2022-05-08"
DEPEG = "2022-05-07 21:44"   # UST de-peg moment marked in the paper (notebook axvline)
PANEL_AR = 8 / 15   # height/width aspect, kept at true on-page size
# four addresses highlighted as blue triangles in the May-2021 panel (IA.2);
# kept here for parity — typically absent in the May-2022 window.
TOP_BUYERS = {
    "0x5dd09afc9ca51b46d6cda2189478b505ace7f37b", "0xe3bdda6413313ed58585e47441815e9662bdd818",
    "0x2747363d886c7fdcc5187217f1ca493922aa4940", "0xaf7bbcfb1c1f987e0ae409c684289b332a425254",
}


def _cumulative_net(sell: pd.DataFrame, buy: pd.DataFrame) -> pd.Series:
    """Net (buy − sell) cumulative volume on a *shared* minute grid.

    Resampling buy and sell independently and cumsum-ing before alignment makes
    the two series end at different minutes; subtracting then zero-fills the
    side that has run out, producing a spurious jump where the last sell/buy
    falls (the artifact the author flagged on Fig IA.2). Reindexing both onto a
    common minute grid *before* cumsum removes it.
    """
    idx = pd.date_range(min(sell["time"].min(), buy["time"].min()).floor("min"),
                        max(sell["time"].max(), buy["time"].max()).ceil("min"),
                        freq="min")
    s = sell.set_index("time")["sell_amount"].resample("min").sum().reindex(idx, fill_value=0).cumsum()
    b = buy.set_index("time")["sell_amount"].resample("min").sum().reindex(idx, fill_value=0).cumsum()
    return (b - s) / 1e6


def plot_curve_swaps(filename: str, start: str, end: str, outname: str,
                     time_fmt: str = "%m-%d %H:%M", min_sell: float = 0.0,
                     depeg: str | None = None, page_w_cm: float = 15, xloc=None,
                     net_legend_loc: str = "lower left") -> Path:
    df = pd.read_parquet(datadir("curve", filename))
    df = df[(df["time"] >= start) & (df["time"] <= end)].copy()
    if min_sell:
        df = df[df["sell_amount"].abs() > min_sell]
    sell = df[df["taker_side_sell"]]
    buy = df[~df["taker_side_sell"]]
    buy_top = buy[buy["trader"].isin(TOP_BUYERS)]
    buy_oth = buy[~buy["trader"].isin(TOP_BUYERS)]

    out = figpath(outname)
    with plt.rc_context(caption_rc()):
        fig, axs = plt.subplots(2, 1, figsize=figsize_cm(page_w_cm, page_w_cm * PANEL_AR), sharex=True)
        # Color-blind-safe (Okabe-Ito) pair, replacing red/green: vermillion (sell) / bluish-green (buy).
        axs[0].scatter(sell["time"], np.log10(sell["sell_amount"]), color="#D55E00", alpha=0.7, s=12, label="UST → stable")
        axs[0].scatter(buy_oth["time"], np.log10(buy_oth["sell_amount"]), color="#009E73", alpha=0.7, s=12, label="stable → UST")
        if len(buy_top):
            axs[0].scatter(buy_top["time"], np.log10(buy_top["sell_amount"]), color="tab:blue",
                           alpha=0.8, marker="^", s=40, label="Top UST buyers (4 addr.)")
        axs[0].set_ylabel("Swaps (in logs)")
        axs[0].grid(alpha=0.4)
        integer_yaxis(axs[0])
        axs[0].legend(loc="upper left")

        net = _cumulative_net(sell, buy)
        ln_net, = axs[1].plot(net.index, net.to_numpy(), color="tab:blue", label="Net swap volume (M)")
        axs[1].set_ylabel("Net swap volume (M)", color="tab:blue")
        axs[1].tick_params(axis="y", labelcolor="tab:blue")
        axs[1].grid(alpha=0.4)
        integer_yaxis(axs[1])

        disc = df[df["quote_asset"] != "3Crv"].set_index("time")
        ax2 = axs[1].twinx()
        ln_disc, = ax2.plot(disc.index, (1 - disc["price_native"]) * 10000, color="black", label="UST discount (bp)")
        ax2.set_ylabel("UST discount (bp)", color="black")
        integer_yaxis(ax2)
        axs[1].legend([ln_net, ln_disc], ["Net swap volume (M)", "UST discount (bp)"],
                      loc=net_legend_loc)
        if xloc is not None:
            axs[1].xaxis.set_major_locator(xloc)
        axs[1].xaxis.set_major_formatter(mdates.DateFormatter(time_fmt))

        if depeg:
            for ax in (axs[0], axs[1]):
                ax.axvline(pd.to_datetime(depeg), color="0.4", ls="--", lw=1.2)

        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


def main() -> Path:
    return plot_curve_swaps("curve_ust_3pool_may7.parquet", START, END,
                            "curve_swap_May7.png", depeg=DEPEG,
                            xloc=mdates.HourLocator(byhour=range(0, 24, 6)))


if __name__ == "__main__":
    main()
