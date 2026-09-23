"""Figure 13 — Anchor outflows by depositor size.

Reproduces ``paper/figures/Run_outflow_by_size_combined_240518.png``.
Both panels show the remaining Anchor aUST deposit balance (normalised so the
panel's first instant = 1) over time, broken out by the size of each wallet.
Left: the day of May 7, 2022 (15-min resolution).  Right: May 6–14, 2022
(hourly), with a dotted line at the UST de-peg (May 9, 17:30 UTC).

Wallets are grouped by their maximum USD aUST balance over the window
(``full_maxusd``); individual depositors only, > 100 UST pre-run balance, with
intermediaries (DEX/CeX/bridge/contract/high-degree) excluded.  The balance path
is the running cumulative sum of **every aUST transfer touching a depositor**
(not just Anchor deposit/withdraw), seeded with each group's pre-run aUST total.

Inputs (node-derived; see Datasets.md and build_fig13_inputs.py):
    data/anchor_run/run_aust_flow_by_depositor.parquet   time, address, vol
        address-centric aUST flow among depositors (+receive / -send)
    data/loss/depositor_prerun_size.parquet              address, prerun_aust, full_maxusd
    data/labels/interdm_addresses.parquet                address  (intermediaries to drop)

Output: output/figures/Run_outflow_by_size_combined_240518.png

Source notebook: code/Run-3-loss-regression-240404.ipynb
    (``get_depositors`` / ``get_aust_balance_by_group``, "## Size plots").
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
from figstyle import caption_rc, figsize_cm  # noqa: E402

PAGE_W_CM, PAGE_H_CM = 15.5, 5.5   # true on-page size; included at textwidth
PRERUN_AUST_RATE = 1.24616         # 100 UST floor -> aUST, per the source notebook
DEPEG = pd.Timestamp("2022-05-09 17:30:00")

GROUPS = ["100-1K", "1K-10K", "10K-100K", "100K-1M", "1M-10M", ">10M"]
# size bins on the wallet's max USD balance: 10^1.9 .. 10^7 .. inf
BINS = [10 ** n for n in (1.9, 3, 4, 5, 6, 7, np.inf)]
# colours matched to the published "Wallet wealth" legend
COLORS = ["#1f77b4", "#d62728", "#ff7f0e", "#2ca02c", "#8c8c00", "#17becf"]


def get_depositors() -> pd.DataFrame:
    """Individual depositors (>100 UST pre-run, non-intermediary) with a size group."""
    size = pd.read_parquet(datadir("loss", "depositor_prerun_size.parquet"))
    interdm = set(pd.read_parquet(datadir("labels", "interdm_addresses.parquet"))["address"])
    keep = set(size.loc[size.prerun_aust > 100 / PRERUN_AUST_RATE, "address"]) - interdm
    dep = size.loc[size.address.isin(keep)].copy()
    dep["size_group"] = pd.cut(dep["full_maxusd"], bins=BINS, labels=GROUPS)
    return dep.dropna(subset=["size_group"])


def aust_balance_by_group(dep: pd.DataFrame) -> pd.DataFrame:
    """Per-group aUST balance path (cumsum of 15-min net flow on top of pre-run)."""
    flow = pd.read_parquet(datadir("anchor_run", "run_aust_flow_by_depositor.parquet"))
    flow = (
        flow.assign(minute=lambda d: d["time"].dt.ceil("15min"))
        .merge(dep[["address", "size_group"]], on="address")
        .astype({"size_group": "str"})
        .groupby(["minute", "size_group"], as_index=False, observed=True)
        .agg(vol=("vol", lambda x: x.sum() / 1e6))
    )
    init = (
        dep[["size_group", "prerun_aust"]].astype({"size_group": "str"})
        .groupby("size_group", as_index=False, observed=True)
        .agg(vol=("prerun_aust", "sum"))
        .assign(minute=pd.Timestamp("2022-05-06 00:00:00"))
        .astype(flow.dtypes)
    )
    bal = (
        pd.concat([init, flow])
        .set_index(["minute", "size_group"])["vol"]
        .unstack("size_group")
        .fillna(0)
        .cumsum()
    )
    return bal[GROUPS].div(bal[GROUPS].iloc[0], axis=1).loc[:"2022-05-14 00:00:00"]


def _plot_groups(ax, df):
    for g, c in zip(GROUPS, COLORS):
        ax.plot(df.index, df[g], color=c, lw=1.4, label=g)
    ax.grid(alpha=0.3)


def _hour_or_date(x, _pos):
    t = mdates.num2date(x)
    return t.strftime("%-m/%d") if (t.hour == 0 and t.minute == 0) else f"{t.hour}h"


def main() -> Path:
    dep = get_depositors()
    bal = aust_balance_by_group(dep)

    # Left: zoom on May 7, re-normalised to that day's 00:00
    may7 = bal.loc["2022-05-07 00:00:00":"2022-05-08 00:00:00"]
    may7 = may7.div(may7.iloc[0], axis=1)
    # Right: full run window, hourly
    week = bal.resample("h").ffill()

    out = figpath("Run_outflow_by_size_combined_240518.png")
    with plt.rc_context(caption_rc()):
        fig, (axL, axR) = plt.subplots(1, 2, figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM))

        _plot_groups(axL, may7)
        axL.set_ylim(0.85, 1.02)
        axL.set_yticks(np.arange(0.86, 1.021, 0.02))
        axL.set_ylabel("Wallet balance (May 7 12AM = 1)")
        axL.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 4)))
        axL.xaxis.set_major_formatter(plt.FuncFormatter(_hour_or_date))
        axL.legend(title="Wallet wealth", loc="lower left", ncol=1, fontsize="small")

        _plot_groups(axR, week)
        axR.axvline(DEPEG, color="black", lw=1.0, ls=":")
        axR.set_ylim(0, 1.05)
        axR.set_yticks(np.arange(0, 1.01, 0.2))
        axR.set_ylabel("Deposit balance (May 6 12AM = 1)")
        axR.xaxis.set_major_locator(mdates.DayLocator())
        axR.xaxis.set_major_formatter(mdates.DateFormatter("%-m/%d"))
        axR.legend(title="Wallet wealth", loc="lower left", ncol=1, fontsize="small")

        for ax in (axL, axR):
            for lbl in ax.get_xticklabels():
                lbl.set_rotation(0)
            ax.margins(x=0.01)
        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
