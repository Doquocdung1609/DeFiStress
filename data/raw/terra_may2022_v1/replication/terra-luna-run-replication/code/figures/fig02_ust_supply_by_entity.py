"""Figure 2 — UST supply by entity.

Reproduces ``paper/figures/ust_supply_by_entity.png``: the aggregate circulating
supply of UST (billion UST) stacked by the type of entity holding it. Entity
groups are defined in Table A.1.

Inputs (node-derived daily balance breakdown + our manual entity labels; shippable):
    data/daily_balances/columbus-4-lunaust-supply-breakdown-fullnode.parquet
    data/daily_balances/columbus-5-lunaust-supply-breakdown-fullnode.parquet
        columns used: address, date, denom, balance
    data/labels/terra_labels_4vol.parquet   columns: address, label_type

Output:
    output/figures/ust_supply_by_entity.png

Source notebook: code/230311-LUNA-UST-supply.ipynb (In[2,3,40,41]); originally
holoviews; re-implemented in matplotlib.
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from figstyle import caption_rc, figsize_cm, integer_yaxis, quarter_date_axis  # noqa: E402

# true on-page size; included at 11 cm in the paper.
PAGE_W_CM, PAGE_H_CM = 11, 5.7

END = "2022-05-10"
# entity types that get their own band; everything else -> "Other"
VALID = ["Anchor", "Admin", "TFL", "Bridge", "CEX", "DEX", "DeFi"]
# stacking order (bottom -> top)
ORDER = ["Anchor", "TFL", "Bridge", "CEX", "DEX", "DeFi", "Other", "Admin"]

# colours: holoviews Category20 sampled at i/9 over this entity order (In[2])
_PALETTE_ORDER = ["Anchor", "Admin", "TFL", "Staked", "Bridge", "CEX", "DEX", "DeFi", "Other"]
_tab20 = mpl.colormaps["tab20"]
COLORMAP = {k: _tab20(i / 9) for i, k in enumerate(_PALETTE_ORDER)}


def build_ust_supply() -> pd.DataFrame:
    supp = pd.concat(
        [pd.read_parquet(datadir("daily_balances", f"columbus-{c}-lunaust-supply-breakdown-fullnode.parquet"))
         for c in (4, 5)],
        ignore_index=True,
    )
    supp["denom"] = supp["denom"].map({"uusd": "UST", "uluna": "LUNA", "UST": "UST", "LUNA": "LUNA"})
    ust = supp.loc[supp.denom == "UST"].copy()

    labs = pd.read_parquet(datadir("labels", "terra_labels_4vol.parquet"))
    eld = labs.loc[labs.label_type.isin(VALID)].set_index("address")["label_type"].to_dict()

    ust["Entity"] = ust["address"].map(lambda a: eld.get(a, "Other"))
    grp = (ust.groupby(["date", "Entity"]).agg({"balance": "sum"})["balance"]
              .unstack("Entity").loc[:END].fillna(0)) / 1e9   # billion UST
    grp.index = pd.to_datetime(grp.index)
    cols = [c for c in ORDER if c in grp.columns]
    return grp[cols]


def main() -> Path:
    g = build_ust_supply()
    out = figpath("ust_supply_by_entity.png")
    with plt.rc_context(caption_rc()):
        fig, ax = plt.subplots(figsize=figsize_cm(PAGE_W_CM, PAGE_H_CM))
        ax.stackplot(g.index, [g[c].to_numpy() for c in g.columns],
                     labels=list(g.columns),
                     colors=[COLORMAP[c] for c in g.columns], linewidth=0)
        ax.set_ylim(0, 20)
        ax.set_ylabel("billion UST")
        ax.margins(x=0)
        ax.grid(True, alpha=0.3)
        integer_yaxis(ax)
        quarter_date_axis(ax)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], title="Entity", loc="upper left")
        fig.tight_layout()
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
