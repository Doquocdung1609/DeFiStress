"""Table 2 — Summary statistics: individual addresses.

Renders ``paper/tables/anchor_loss_summary.tex``: summary statistics for
individual Anchor depositors prior to the run, for the full sample and broken
out by pre-run deposit balance, plus a count of addresses that fully exited.

Input (analysis panel rebuilt by prep/prep_loss_panel.py; see prep note below):
    data/loss/anchor_loss_panel.parquet
      cols: address, prerun_usd, full_maxusd, perc_loss, log_wealth,
            log_volume_adj, age, log_age_months, cex_degree, used_bridge
    (the "Exited" count is external, not a panel column — see EXITED_COUNT)

Provenance: the panel is built by prep/prep_loss_panel.py, which reproduces the
source notebook's loss_reg exactly (full sample 159,669; size groups 31,668 /
62,334 / 48,969 / 14,481 / 2,005 / 212).  Size groups bin on `full_maxusd` (the
wallet's peak USD balance), the same size variable the notebook uses.

Output: output/tables/anchor_loss_summary.tex

NOTE: the six summary rows now reproduce the notebook's Table 2 to the digit.
The "Exited" count (col 8) is an EXTERNAL figure that is not reconstructable from
the on-chain panel, so it is hard-coded here (EXITED_COUNT).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from config import datadir, tabpath  # noqa: E402

BINS = [10 ** 1.9, 1e3, 1e4, 1e5, 1e6, 1e7, np.inf]
COLHEADS = ["$<$1K", "10K", "100K", "1M", "10M", "$>$10M"]

# Wallets that fully exited the ecosystem (Table 2, col 8).  This is an external
# figure — it is not reconstructable from the on-chain loss panel — so it is
# fixed here rather than derived.
EXITED_COUNT = 63015


def _summary(g: pd.DataFrame) -> dict:
    return {
        "Address count": int(g["address"].count()),
        "Percent loss": g["perc_loss"].mean(),
        "log(volume/balance)": np.mean(np.exp(g["log_volume_adj"])),
        "Age in months": g["age"].mean() / 30,
        "No. of CEXs": g["cex_degree"].mean(),
        "Used bridges?": g["used_bridge"].mean(),
    }


def main() -> Path:
    lr = pd.read_parquet(datadir("loss", "anchor_loss_panel.parquet"))
    lr["size_group"] = pd.cut(lr["full_maxusd"], bins=BINS)
    lr = lr.dropna(subset=["size_group"])
    lo, hi = np.percentile(lr["perc_loss"], [0.5, 99.5])
    lr["perc_loss"] = lr["perc_loss"].clip(lo, hi)

    full = _summary(lr)
    groups = [_summary(lr[lr["size_group"] == cat]) for cat in lr["size_group"].cat.categories]
    exited = EXITED_COUNT

    rows = ["Address count", "Percent loss", "log(volume/balance)",
            "Age in months", "No. of CEXs", "Used bridges?"]

    def fmt(v, row):
        return f"{int(v)}" if row == "Address count" else f"{v:.2f}"

    lines = [
        r"\begin{center}",
        r"    \begin{tabular}{rcccccccc}",
        r"        \toprule",
        r"         & Full Sample & \multicolumn{6}{c}{Pre-Run Balance} & Exited \\",
        r"        \cline{3-8}",
        r"         &  & " + " & ".join(COLHEADS) + r" &  \\",
        r"         & (1) & (2) & (3) & (4) & (5) & (6) & (7) & (8) \\",
        r"        \hline",
    ]
    for row in rows:
        cells = [fmt(full[row], row)] + [fmt(g[row], row) for g in groups]
        tail = f" & {exited}" if row == "Address count" else " & "
        lines.append(f"        {row:<20} & " + " & ".join(cells) + tail + r" \\")
    lines += [r"        \bottomrule", r"    \end{tabular}", r"\end{center}", ""]

    out = tabpath("anchor_loss_summary.tex")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
