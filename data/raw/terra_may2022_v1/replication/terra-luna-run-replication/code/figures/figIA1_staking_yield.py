"""Figure IA.1 — Anchor borrowing costs and incentives.

Reproduces ``paper/figures/LUNA_staking_decomposition.png`` (left) and
``paper/figures/Anchor_ANC_subsidy_rate.png`` (right).

Left  — opportunity cost of LUNA collateral (annualized %), decomposed by the
        source of the LUNA yield: block-reward (commission) staking plus the
        ANC / MIR / MINE airdrops (valued in LUNA). 7-day rolling, stacked.
Right — the annualized ANC subsidy rate paid to Anchor borrowers. 7-day rolling.

Inputs (node staking rewards + airdrops, orig. Flipside; on-chain content,
shipped with acknowledgment):
    data/anchor/luna_staking_stats.parquet   apr_percent_comm, anc_luna, mir_luna,
                                             mine_luna, luna_stake_balance (index date_reward)
    data/anchor/Anchor_daily_stats.parquet   ANC APR

Output (two separate panels, matching the paper's two subfigures):
    output/figures/LUNA_staking_decomposition.png  (left panel)
    output/figures/Anchor_ANC_subsidy_rate.png     (right panel)

Source notebook: code/230325-Anchor-plot-final.ipynb (In[56-59], In[88]).
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

PANEL_W_CM, PAGE_H_CM = 7.75, 5.25   # each panel drawn separately at ~half-textwidth (0.45-0.5\textwidth)

COMPONENTS = {
    "LUNA staking": "#1f77b4",  # blue
    "ANC airdrop": "#fc4f30",   # red
    "MIR airdrop": "#e8b818",   # gold
    "MINE airdrop": "#2ca02c",  # green
}


def build_decomposition() -> pd.DataFrame:
    b = pd.read_parquet(datadir("anchor", "luna_staking_stats.parquet"))
    out = pd.DataFrame(index=b.index)
    out["LUNA staking"] = b["apr_percent_comm"]
    for tok, col in [("ANC", "anc_luna"), ("MIR", "mir_luna"), ("MINE", "mine_luna")]:
        out[f"{tok} airdrop"] = b[col] / b["luna_stake_balance"] * 365 * 100
    out = out.iloc[3:].fillna(0).rolling(7).mean().dropna()
    out.index = pd.to_datetime(out.index)
    return out


def main() -> list:
    dec = build_decomposition()
    anc = pd.read_parquet(datadir("anchor", "Anchor_daily_stats.parquet"), columns=["ANC APR"])
    anc = (anc["ANC APR"].rolling(7).mean().dropna() * 100)

    outL = figpath("LUNA_staking_decomposition.png")
    outR = figpath("Anchor_ANC_subsidy_rate.png")
    with plt.rc_context(caption_rc()):
        # --- left panel: LUNA staking-yield decomposition ---
        figL, axL = plt.subplots(figsize=figsize_cm(PANEL_W_CM, PAGE_H_CM))
        axL.stackplot(dec.index, [dec[c].to_numpy() for c in COMPONENTS],
                      labels=list(COMPONENTS), colors=list(COMPONENTS.values()), alpha=0.85)
        axL.set_ylim(0, 20)
        axL.set_ylabel("APR (%)")
        axL.margins(x=0)
        axL.grid(alpha=0.3)
        integer_yaxis(axL)
        quarter_date_axis(axL)
        axL.legend(loc="upper right")
        figL.tight_layout()
        figL.savefig(outL, dpi=300, bbox_inches="tight")
        plt.close(figL)

        # --- right panel: ANC subsidy rate ---
        figR, axR = plt.subplots(figsize=figsize_cm(PANEL_W_CM, PAGE_H_CM))
        axR.plot(anc.index, anc.to_numpy(), color="black", lw=1.5)
        axR.set_ylim(0, 320)
        axR.set_ylabel("ANC subsidy APR (%)")
        axR.margins(x=0)
        axR.grid(alpha=0.3)
        integer_yaxis(axR)
        quarter_date_axis(axR)
        figR.tight_layout()
        figR.savefig(outR, dpi=300, bbox_inches="tight")
        plt.close(figR)
    print(f"wrote {outL}")
    print(f"wrote {outR}")
    return [outL, outR]


if __name__ == "__main__":
    main()
