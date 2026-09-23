"""Figure 7 — Anchor flows on May 7, 2022 (the start of the run).

Reproduces ``paper/figures/wallet_A_B.png``.
Top two panels — cumulative withdrawals of the two largest net-withdrawing
   addresses on May 7 ("Wallet A" and "Wallet B"), which begin the run.
Bottom panel  — the timing and size (millions of UST) of all *other* Anchor
   deposits (green) and withdrawals (red) on May 7.

Input (cleaned Anchor run transactions from the archive node; shippable):
    data/anchor_run/anchor_run_tx_cleaned.parquet
        columns: time, sender, action ('deposit'/'withdraw'), ust_vol

Output:
    output/figures/wallet_A_B.png

Source notebook: Snowflake/Terra-run-analysis-anchor-may-7.ipynb
(`plot_ts_anc_cleaned`, In[19]); already matplotlib.
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
N_WALLETS = 2
WALLET_LABELS = ["Wallet A", "Wallet B"]
# Rendered at true on-page size for \includegraphics[width=15cm]; fonts are set
# at caption size directly, so line/marker weights print at their natural values.
PAGE_W_CM, PAGE_H_CM = 15, 11


def main() -> Path:
    data = pd.read_parquet(datadir("anchor_run", "anchor_run_tx_cleaned.parquet"))
    win = data[(data["time"] >= START) & (data["time"] <= END)].copy()

    # signed flow: withdrawals positive, deposits negative
    win["svol"] = np.where(win["action"] == "withdraw", win["ust_vol"], -win["ust_vol"])
    per_min = (win.set_index("time").groupby("sender")["svol"].resample("min")
                  .sum().reset_index())

    rank = per_min.groupby("sender", as_index=False)["svol"].sum().sort_values("svol", ascending=False)
    top = rank["sender"].head(N_WALLETS).tolist()

    cum = per_min[per_min["sender"].isin(top)].copy()
    cum["svol_cum"] = cum.groupby("sender")["svol"].cumsum()
    # Extend each cumulative line across the whole window: forward-fill the last
    # level to the right edge and back-fill the leading 0 to the left edge so the
    # wallet curves span the full plot (author review).
    full_idx = pd.date_range(START, END, freq="min")
    wide = (cum.pivot(index="time", columns="sender", values="svol_cum")
               .reindex(full_idx).ffill().fillna(0))

    out = figpath("wallet_A_B.png")
    with plt.rc_context(caption_rc()):
        fig, axs = plt.subplots(N_WALLETS + 1, 1,
                                figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM), sharex=True)
        for i, addr in enumerate(top):
            axs[i].plot(wide.index, wide[addr] / 1e6, color="tab:blue", label=WALLET_LABELS[i])
            axs[i].set_ylabel("Withdrawal (M)", color="tab:blue")
            axs[i].tick_params(axis="y", labelcolor="tab:blue")
            axs[i].legend(loc="upper left")
            axs[i].grid(alpha=0.4)
            integer_yaxis(axs[i], nbins=5)

        others = win[~win["sender"].isin(set(top))]
        wd = others[others["action"] == "withdraw"]
        dp = others[others["action"] == "deposit"]
        # Color-blind-safe (Okabe-Ito) pair, replacing red/green: vermillion (out) / bluish-green (in).
        axs[N_WALLETS].scatter(wd["time"], wd["ust_vol"] / 1e6, color="#D55E00", s=10, label="Withdrawals")
        axs[N_WALLETS].scatter(dp["time"], dp["ust_vol"] / 1e6, color="#009E73", s=10, label="Deposits")
        axs[N_WALLETS].set_ylabel("Amount (M)")  # short: legend gives dep./withdr.
        axs[N_WALLETS].legend(loc="upper left")
        axs[N_WALLETS].grid(alpha=0.4)
        axs[N_WALLETS].set_xlim(full_idx[0], full_idx[-1])
        integer_yaxis(axs[N_WALLETS], nbins=5)
        # 6-hourly ticks so the labels don't collide at caption size; date + time
        # so the two midnight ticks (05-07 00:00 / 05-08 00:00) are
        # distinguishable (author review).
        axs[N_WALLETS].xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
        axs[N_WALLETS].xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))

        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
