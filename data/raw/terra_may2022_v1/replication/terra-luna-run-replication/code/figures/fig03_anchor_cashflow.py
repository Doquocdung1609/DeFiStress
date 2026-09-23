"""Figure 3 — Cash-flow decomposition on Anchor.

Reproduces ``paper/figures/anchor_cash_flow.png`` (left) and
``paper/figures/anchor_reserve_injection.png`` (right).

Left panel — daily inflows (+) and outflows (-) of Anchor's market/reserve in
million UST, 7-day rolling, decomposed by source:
    Loan interest (+)      interest on outstanding loans          (blue)
    bLUNA staking (+)      staking rewards on bLUNA collateral    (red)
    bETH staking (+)       staking rewards on bETH collateral     (yellow)
    Liquidation fees (+)   fees on liquidated loans               (green)
    Deposit interest (-)   interest paid to depositors            (gray)
    ANC repurchase (-)     ANC buyback from the DEX               (teal)
    Daily net cash flow                                           (black line)

Right panel — Anchor's yield-reserve balance (million UST) with the two large
UST injections (TFL ~71M on 2021-07-15, LFG ~510M on 2022-02-19).

Inputs (node-derived; shippable. ``anchor_cashflow_transfers`` is on-chain Anchor
cash-flow transfer events, originally pulled via Flipside, rebuildable from the
archive node — see Datasets.md):
    data/anchor/anchor_cashflow_transfers.parquet  cols: time, sender, recipient, denom, amount
        (daily bucket = time.ceil('D'), the end-of-day label the source carried)
    data/anchor/Anchor_daily_stats.parquet        cols: loan balance, borrow APR, deposit balance, deposit APR
    data/anchor/Anchor_global_stats_fullnode.parquet  col: prev_interest_buffer
    data/labels/anchor_contracts.csv              cols: address, address_name

Output (two separate panels, matching the paper's two subfigures):
    output/figures/anchor_cash_flow.png          (left panel)
    output/figures/anchor_reserve_injection.png  (right panel)

Source notebook: code/230208-Anchor-cashflow-updated.ipynb (In[8]-In[18]);
originally holoviews; re-implemented in matplotlib.
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from terra_lib import address_name_map, get_address_centric_vol, plot_stacked_area  # noqa: E402
from figstyle import caption_rc, figsize_cm, integer_yaxis, quarter_date_axis  # noqa: E402

ANCHOR_MARKET = "terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8"
END = "2022-05-06"
PANEL_W_CM, PAGE_H_CM = 7.75, 5.5   # each panel drawn separately at ~half-textwidth (0.49\linewidth)

# component -> colour (matches the published caption)
COMPONENTS = {
    "Loan interest (+)": "#1f77b4",     # blue
    "bLUNA staking (+)": "#d62728",     # red
    "bETH staking (+)": "#e8c441",      # yellow
    "Liquidation fees (+)": "#2ca02c",  # green
    "Deposit interest (-)": "#7f7f7f",  # gray
    "ANC repurchase (-)": "#17becf",    # teal
}


def build_cashflow_components() -> pd.DataFrame:
    cf = pd.read_parquet(datadir("anchor", "anchor_cashflow_transfers.parquet"))
    # day bucket = the transfer's end-of-day (next-midnight) label, reproducing
    # the `date` column the source extract carried (verified == time.ceil('D')).
    cf["date"] = cf["time"].dt.ceil("D")
    acf = (cf.groupby(["date", "recipient", "sender", "denom"])
                .agg({"amount": "sum"})
                .xs("uusd", level="denom").reset_index())
    acf.columns = ["date", "tgt", "src", "vol"]

    namemap = address_name_map()
    acbf = get_address_centric_vol(acf, [ANCHOR_MARKET], volcol="vol")
    acbf["tgtnm"] = acbf["tgt"].map(lambda a: namemap.get(a, a))
    acbf = acbf.loc[acbf["date"] <= END]
    acbf = (acbf.groupby(["tgtnm", "date"]).agg({"vol": "sum"})["vol"]
                .unstack("tgtnm").fillna(0))
    acbf.index = pd.to_datetime(acbf.index)
    acbf["Liquidation"] = acbf.get("Liquidation Contract", 0) + acbf.get("Liquidation Queue", 0)

    # Computed interest legs from Anchor daily state (override on-chain market leg)
    ads = pd.read_parquet(datadir("anchor", "Anchor_daily_stats.parquet"))
    acbf["Loan interest"] = ads["loan balance"] * ads["borrow APR"] / 365
    acbf["Deposit interest"] = -ads["deposit balance"] * ads["deposit APR"] / 365

    out = pd.DataFrame(index=acbf.index)
    out["Loan interest (+)"] = acbf["Loan interest"]
    out["bLUNA staking (+)"] = acbf.get("bLuna Custody", 0)
    out["bETH staking (+)"] = acbf.get("bETH mmCustody", 0)
    out["Liquidation fees (+)"] = acbf["Liquidation"]
    out["Deposit interest (-)"] = acbf["Deposit interest"]
    out["ANC repurchase (-)"] = -acbf.get("Collector", 0).abs() if "Collector" in acbf else 0
    return (out.rolling(7).mean() / 1e6).dropna(how="all")


def build_reserve_balance() -> pd.Series:
    g = pd.read_parquet(datadir("anchor", "Anchor_global_stats_fullnode.parquet"))
    bal = pd.to_numeric(g["prev_interest_buffer"], errors="coerce").resample("D").last()
    return (bal / 1e12).loc[:"2022-05-26"]   # micro-UST -> million UST


def main() -> list:
    comp = build_cashflow_components()
    bal = build_reserve_balance()

    outL = figpath("anchor_cash_flow.png")
    outR = figpath("anchor_reserve_injection.png")
    with plt.rc_context(caption_rc()):
        # --- left panel: cash flow decomposition ---
        figL, axL = plt.subplots(figsize=figsize_cm(PANEL_W_CM, PAGE_H_CM))
        handles, labels = plot_stacked_area(axL, comp[list(COMPONENTS)],
                                            colors=list(COMPONENTS.values()))
        net = comp[list(COMPONENTS)].sum(axis=1)
        nl, = axL.plot(net.index, net.to_numpy(), color="black", lw=1.3, label="Daily net cash flow")
        axL.axhline(0, color="black", lw=0.5)
        axL.set_ylabel("million UST")
        axL.set_ylim(-8, 3)
        axL.margins(x=0)
        axL.grid(True, alpha=0.3)
        axL.set_title("Anchor's daily cash flow")
        integer_yaxis(axL)
        quarter_date_axis(axL)
        axL.legend(handles + [nl], labels + ["Daily net cash flow"],
                   loc="lower left")
        figL.tight_layout()
        figL.savefig(outL, dpi=300, bbox_inches="tight")
        plt.close(figL)

        # --- right panel: reserve balance with injections ---
        figR, axR = plt.subplots(figsize=figsize_cm(PANEL_W_CM, PAGE_H_CM))
        axR.plot(bal.index, bal.to_numpy(), color="#1f77b4", lw=1.5)
        axR.set_ylabel("million UST")
        axR.set_ylim(0, 580)
        axR.margins(x=0)
        axR.grid(True, alpha=0.3)
        axR.set_title("Anchor's daily cash balance")
        integer_yaxis(axR)
        quarter_date_axis(axR)
        # injection labels centred over their dotted event lines (author review)
        for date, txt, y in [("2021-07-15", "TFL injects 71M UST", 110),
                             ("2022-02-19", "LFG injects 510M UST", 545)]:
            d = pd.to_datetime(date)
            axR.axvline(d, color="black", lw=0.8, ls="dotted")
            axR.annotate(txt, xy=(d, y), ha="center", va="top")
        figR.tight_layout()
        figR.savefig(outR, dpi=300, bbox_inches="tight")
        plt.close(figR)
    print(f"wrote {outL}")
    print(f"wrote {outR}")
    return [outL, outR]


if __name__ == "__main__":
    main()
