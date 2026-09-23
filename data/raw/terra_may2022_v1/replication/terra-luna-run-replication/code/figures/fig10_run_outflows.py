"""Figure 10 — Anchor outflows (May 2022 run).

Reproduces ``paper/figures/Run_deposit_outflow3.png``: the outstanding Anchor
deposit balance (black, left axis, billion UST) and the UST price (red, right
axis) during the run, May 6–15, 2022.

The deposit balance is the **exact on-chain contract state**: the live aUST
supply (``aterra_supply``) times the live aUST/UST exchange rate
(``exchange_rate``), read from per-block ``{epoch_state}`` smart-queries of the
Anchor market contract at each ~15-minute snapshot height.  This is the aggregate
total, so it needs no flow reconstruction — and, because total aUST changes only
through mint (deposit) / burn (withdraw) while aUST *transfers between holders*
net to zero in the aggregate, it carries **no aUST-flow caveat** (that caveat
only bites when the total is split by wallet, as in Fig 13).  An earlier port
reconstructed the line from the net deposit/withdraw flow with a fixed rate and
forward-filled flat after the chain halt, which overshot the tail (~2.4B vs the
published ~1.4B); the contract series tracks the published curve through the halt
and down to ~1.4B.

``{epoch_state}`` (not ``{state}``) matters: the contract's stored ``{state}``
caches ``prev_aterra_supply`` / ``prev_exchange_rate`` and only refreshes them at
``execute_epoch_operations`` (~70 times across the run), so a ``prev_*`` series
steps in 6-hour-wide stairs.  ``{epoch_state}`` recomputes supply × rate every
block, giving the smooth line.

Inputs (node Anchor contract state + Kaiko UST price; shippable):
    data/anchor_run/epoch_state_fig10.parquet          time_utc, aterra_supply,
                                                        exchange_rate, deposit_b_ust
    data/prices/ust_price_may2022.parquet              time, ust_price

Output: output/figures/Run_deposit_outflow3.png

Source notebook: code/230109-Run-flows-balances.ipynb / 240401-run-revisit.ipynb.

NOTES
- The ``{epoch_state}`` snapshots run through 2022-05-15, so the deposit line
  extends to the right edge with real data (no forward-fill); it keeps declining
  gently after the May 12-13 chain halt as the exchange rate ticks. The Kaiko UST
  price, which is off-chain, also continues through May 15.
- ``epoch_state_fig10.parquet`` was re-fetched at the snapshot heights of file #2
  (``Anchor_global_stats_fullnode.parquet``); only the shipped parquet is needed
  to reproduce the figure.
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
from figstyle import caption_rc, figsize_cm, integer_yaxis, MYWIDTH_CM  # noqa: E402

START, END = "2022-05-06", "2022-05-15"
DEPEG = "2022-05-09 17:30"   # UST decisively breaks peg (May 9, 17:30 UTC)
PRICE_COLOR = "#d62728"
PAGE_W_CM, PAGE_H_CM = MYWIDTH_CM, 5.6   # true size; mywidth (0.7 textwidth)


def main() -> Path:
    # On-chain Anchor deposit balance = live aUST supply (uaUST) * aUST/UST rate,
    # from per-block {epoch_state} queries (precomputed in deposit_b_ust).
    es = pd.read_parquet(datadir("anchor_run", "epoch_state_fig10.parquet"))
    dep = (
        es.assign(t=pd.to_datetime(es["time_utc"]))
        .set_index("t")["deposit_b_ust"]
        .sort_index()
        .loc[START:END]
    )
    ust = pd.read_parquet(datadir("prices", "ust_price_may2022.parquet"))
    price = ust.set_index("time")["ust_price"].resample("min").last().loc[START:END]

    out = figpath("Run_deposit_outflow3.png")
    with plt.rc_context(caption_rc()):
        fig, axL = plt.subplots(figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM))
        axL.plot(dep.index, dep.to_numpy(), color="black", lw=1.6)
        axL.set_ylabel("Anchor deposits (B UST)", color="black")
        axL.set_ylim(0, 15)
        axL.set_xlim(pd.Timestamp(START), pd.Timestamp(END) + pd.Timedelta(days=1))
        axL.grid(True, alpha=0.3)
        integer_yaxis(axL)
        axL.axvline(pd.to_datetime(DEPEG), color="0.3", ls="--", lw=1.1)
        axL.xaxis.set_major_locator(mdates.DayLocator())
        axL.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

        axR = axL.twinx()
        axR.plot(price.index, price.to_numpy(), color=PRICE_COLOR, lw=1.0)
        axR.set_ylabel("UST/USD price", color=PRICE_COLOR)
        axR.tick_params(axis="y", labelcolor=PRICE_COLOR)
        axR.set_ylim(0, 1.1)

        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
