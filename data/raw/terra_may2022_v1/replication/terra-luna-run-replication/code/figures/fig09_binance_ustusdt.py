"""Figure 9 — Binance UST/USDT trades on May 7, 2022.

Reproduces ``paper/figures/binance_May7.png``.
Top   — every UST/USDT trade on Binance on May 7, 2022; sell-initiated trades in
        red, buy-initiated in green; trade size on a logarithmic y-axis.
Bottom— net signed (buy minus sell) cumulative volume in millions (blue, left)
        and the deviation of the UST price from $1 in basis points (black, right).

Input (Kaiko exchange tick data, minimal May 7 slice; redistributed with
acknowledgment — see README):
    data/exchange/binance_ustusdt_may7.parquet
        columns: time, price, amount, taker_side_sell

Output:
    output/figures/binance_May7.png

Source notebook: code/Terra-run-analysis-exch-20230212.ipynb
(`plot_tick_bn_crash2`, In[21,25]); already matplotlib.
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from figstyle import caption_rc, figsize_cm, integer_yaxis  # noqa: E402

START, END = "2022-05-07", "2022-05-08"
DEPEG = "2022-05-07 21:44"   # UST de-peg moment marked in the paper
PAGE_W_CM, PAGE_H_CM = 15, 8   # true on-page size; included at 15 cm


def main() -> Path:
    df = pd.read_parquet(datadir("exchange", "binance_ustusdt_may7.parquet"))
    df = df[(df["time"] >= START) & (df["time"] <= END)].copy()
    sell = df[df["taker_side_sell"]]
    buy = df[~df["taker_side_sell"]]

    # net signed cumulative volume on a shared minute grid (avoids the spurious
    # end-jump from subtracting independently-cumsummed buy/sell series).
    idx = pd.date_range(df["time"].min().floor("min"), df["time"].max().ceil("min"), freq="min")
    sell_cum = sell.set_index("time")["amount"].resample("min").sum().reindex(idx, fill_value=0).cumsum()
    buy_cum = buy.set_index("time")["amount"].resample("min").sum().reindex(idx, fill_value=0).cumsum()
    net = (buy_cum - sell_cum) / 1e6
    price_m = df.set_index("time")["price"].resample("min").last()

    out = figpath("binance_May7.png")
    with plt.rc_context(caption_rc()):
        fig, axs = plt.subplots(2, 1, figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM), sharex=True)

        # top: trade scatter, log size
        # Color-blind-safe (Okabe-Ito) pair, replacing red/green: vermillion (sell) / bluish-green (buy).
        axs[0].scatter(sell["time"], sell["amount"], color="#D55E00", s=10, label="Sell-initiated")
        axs[0].scatter(buy["time"], buy["amount"], color="#009E73", s=10, label="Buy-initiated")
        axs[0].set_yscale("log")
        axs[0].set_ylabel("Trade size (UST)")
        axs[0].grid(alpha=0.4)
        axs[0].legend(loc="upper left")

        # bottom: net signed cumulative volume (blue) + UST discount bp (black)
        ln_net, = axs[1].plot(net.index, net.to_numpy(), color="tab:blue", label="Net buy volume (M)")
        axs[1].set_ylabel("Net buy volume (M)", color="tab:blue")
        axs[1].tick_params(axis="y", labelcolor="tab:blue")
        axs[1].grid(alpha=0.4)
        integer_yaxis(axs[1])
        ax2 = axs[1].twinx()
        ln_disc, = ax2.plot(price_m.index, (1 - price_m) * 10000, color="black", label="UST discount (bp)")
        ax2.set_ylabel("UST discount (bp)", color="black")
        integer_yaxis(ax2)
        axs[1].legend([ln_net, ln_disc], ["Net buy volume (M)", "UST discount (bp)"],
                      loc="upper left")
        axs[1].xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
        axs[1].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))

        for ax in axs:
            ax.axvline(pd.to_datetime(DEPEG), color="0.4", ls="--", lw=1.2)

        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
