"""Figure 5 — LUNA and UST market capitalization.

Reproduces ``paper/figures/mkt_cap2.png``: the circulating market
capitalization of UST (blue) and LUNA (orange) in billions of US dollars from
October 2020 to May 2022.

Inputs (public, CoinGecko daily exports; shippable):
    data/external/lunc-usd-max.csv   LUNA / LUNC
    data/external/ustc-usd-max.csv   UST  / USTC
    columns used: snapped_at, market_cap

Output:
    output/figures/mkt_cap2.png

Source notebook: code/230103-terraluna-supply.ipynb (In[154]-In[156]),
originally drawn with holoviews/hvplot; re-implemented here in matplotlib.
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from figstyle import caption_rc, figsize_cm, integer_yaxis, quarter_date_axis, MYWIDTH_CM  # noqa: E402

# true on-page size; included at \mywidth (0.7 textwidth) in the paper.
PAGE_W_CM, PAGE_H_CM = MYWIDTH_CM, 6.1

LUNA_COLOR = "#E96C1F"  # orange
UST_COLOR = "#25379B"   # blue
START, END = "2020-10-03", "2022-05-31"


def _load_market_cap(filename: str, label: str) -> pd.Series:
    df = pd.read_csv(datadir("external", filename))
    # snapped_at looks like "2019-05-08 00:00:00 UTC"; force tz-naive UTC.
    idx = pd.to_datetime(df["snapped_at"], utc=True).dt.tz_convert(None)
    return pd.Series(df["market_cap"].to_numpy(), index=idx, name=label)


def load_market_cap() -> pd.DataFrame:
    supply = pd.concat(
        [_load_market_cap("lunc-usd-max.csv", "LUNA"),
         _load_market_cap("ustc-usd-max.csv", "UST")],
        axis=1,
    ).sort_index()
    return supply.loc[START:END] / 1e9  # billions of USD


def main() -> Path:
    supply = load_market_cap()
    out = figpath("mkt_cap2.png")
    with plt.rc_context(caption_rc()):
        fig, ax = plt.subplots(figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM))
        ax.plot(supply.index, supply["LUNA"], color=LUNA_COLOR, lw=1.6, label="LUNA")
        ax.plot(supply.index, supply["UST"], color=UST_COLOR, lw=1.6, label="UST")
        ax.set_ylim(0, 45)
        ax.set_ylabel("billion USD")
        ax.margins(x=0)
        ax.grid(True, alpha=0.3)
        integer_yaxis(ax)
        quarter_date_axis(ax)
        ax.legend(title="Market cap", loc="upper left")
        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
