"""Figure 1 — Anchor net rates and recursive loans.

Reproduces ``paper/figures/Anchor_net_rates_recursive_loans.png``: the daily net
APR of lending (deposit) and borrowing on Anchor after accounting for the
opportunity cost of collateral and the ANC subsidy, plus the share of Anchor
loans that are recursively re-deposited (dashed). All series are 7-day rolling.

Net borrow APR = (borrow APR) - (ANC subsidy APR) + (LUNA opportunity cost)
% recursive loans = Exploit UST / loan balance * 100

Input (node-derived Anchor daily state; shippable):
    data/anchor/Anchor_daily_stats.parquet
    columns used: deposit APR, borrow APR, ANC APR, LUNA_opp_cost,
                  loan balance, Exploit UST

Output:
    output/figures/Anchor_net_rates_recursive_loans.png

Source notebook: code/230325-Anchor-plot-final.ipynb (In[93], In[98]-In[101]);
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
from figstyle import caption_rc, figsize_cm, integer_yaxis, quarter_date_axis  # noqa: E402

# rendered at its true on-page size (included at 10 cm in the paper) so fonts are
# set at caption size directly and line/marker weights print at natural values.
PAGE_W_CM, PAGE_H_CM = 10, 5.75

DEPOSIT_COLOR = "#1f77b4"   # blue (lending)
BORROW_COLOR = "#d62728"    # red (borrowing)
XLIM = ("2021-03-24", "2022-05-06")


def build_rates() -> pd.DataFrame:
    ads = pd.read_parquet(datadir("anchor", "Anchor_daily_stats.parquet"))
    out = pd.DataFrame(index=ads.index)
    out["Deposit APR (%)"] = ads["deposit APR"] * 100
    out["Net borrow APR (%)"] = (
        ads["borrow APR"] - ads["ANC APR"] + ads["LUNA_opp_cost"]
    ) * 100
    out["% of recursive loans"] = ads["Exploit UST"] / ads["loan balance"] * 100
    return out.rolling(7).mean().dropna().loc[XLIM[0]:XLIM[1]]


def main() -> Path:
    r = build_rates()
    out = figpath("Anchor_net_rates_recursive_loans.png")
    with plt.rc_context(caption_rc()):
        fig, ax = plt.subplots(figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM))
        ax.axhline(0, color="black", lw=0.5)
        ax.plot(r.index, r["Deposit APR (%)"], color=DEPOSIT_COLOR, lw=1.6,
                label="Deposit APR (%)")
        ax.plot(r.index, r["Net borrow APR (%)"], color=BORROW_COLOR, lw=1.6,
                label="Net borrow APR (%)")
        ax.plot(r.index, r["% of recursive loans"], color="black", lw=1.4,
                linestyle="--", label="% of recursive loans")
        ax.set_ylim(-100, 100)
        ax.set_ylabel("Percent")
        ax.margins(x=0)
        ax.grid(True, alpha=0.3)
        integer_yaxis(ax)
        quarter_date_axis(ax)
        ax.legend(loc="lower right")
        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
