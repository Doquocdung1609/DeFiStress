"""Table 3 — Percentage loss of Anchor depositors (regression).

Renders ``paper/tables/anchor_loss_regression.tex``: OLS of the percentage loss
over the run on pre-run balance and trader-sophistication measures.
  Col 1: log balance + sophistication (full sample)
  Col 2: balance-size dummies + sophistication (full sample)
  Cols 3-8: sophistication only, within each pre-run balance subgroup.

Input (analysis panel rebuilt by prep/prep_loss_panel.py — see
fmt_table2_loss_summary.py / prep note):
    data/loss/anchor_loss_panel.parquet

Output: output/tables/anchor_loss_regression.tex

NOTE: with the rebuilt panel (which reproduces the notebook's loss_reg exactly),
the coefficients, R^2 and N reproduce the notebook regression to the digit. Size
subgroups bin on `full_maxusd` (the notebook's size variable), matching Table 2.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from config import datadir, tabpath  # noqa: E402

BINS = [10 ** 1.9, 1e3, 1e4, 1e5, 1e6, 1e7, np.inf]
SIZE_LABELS = ["<1K", "1K-10K", "10K-100K", "100K-1M", "1M-10M", ">10M"]
SOPH = "log_volume_adj + log_age_months + cex_degree + used_bridge"


def _load() -> pd.DataFrame:
    lr = pd.read_parquet(datadir("loss", "anchor_loss_panel.parquet"))
    lr["size_group"] = pd.cut(lr["full_maxusd"], bins=BINS, labels=SIZE_LABELS)
    lr = lr.dropna(subset=["size_group"]).copy()
    lo, hi = np.percentile(lr["perc_loss"], [0.5, 99.5])
    lr["perc_loss"] = lr["perc_loss"].clip(lo, hi)
    return lr


def main() -> Path:
    lr = _load()
    col1 = smf.ols(f"perc_loss ~ log_wealth + {SOPH}", data=lr).fit()
    col2 = smf.ols(f"perc_loss ~ C(size_group) + {SOPH}", data=lr).fit()
    subs = [smf.ols(f"perc_loss ~ {SOPH}", data=lr[lr.size_group == s]).fit() for s in SIZE_LABELS]
    models = [col1, col2] + subs

    # rows: (display label, statsmodels param name)
    rows = [
        ("log balance", "log_wealth"),
        ("Size[1K-10K]", "C(size_group)[T.1K-10K]"),
        ("Size[10K-100K]", "C(size_group)[T.10K-100K]"),
        ("Size[100K-1M]", "C(size_group)[T.100K-1M]"),
        ("Size[1M-10M]", "C(size_group)[T.1M-10M]"),
        ("Size[>10M]", "C(size_group)[T.>10M]"),
        ("log(volume/balance)", "log_volume_adj"),
        ("log age", "log_age_months"),
        ("No. of CEXs", "cex_degree"),
        ("Used bridges?", "used_bridge"),
        ("Constant", "Intercept"),
    ]

    def cell(m, param):
        if param in m.params.index:
            return f"{m.params[param]:.2f}", f"({m.bse[param]:.2f})"
        return "", ""

    lines = [
        r"\begin{center}",
        r"    \begin{tabular}{lcccccccc}",
        r"        \hline",
        r"         & \multicolumn{8}{c}{Percent Loss} \\",
        r"        \cline{2-9}",
        r"         & \multicolumn{2}{c}{Full Sample} & \multicolumn{6}{c}{Balance Subgroup} \\",
        r"        \cline{4-9}",
        r"         &  &  & $<$1K & 10K & 100K & 1M & 10M & $>$10M \\",
        r"         & (1) & (2) & (3) & (4) & (5) & (6) & (7) & (8) \\",
        r"        \hline",
    ]
    for label, param in rows:
        coefs, ses = zip(*(cell(m, param) for m in models))
        lines.append(f"        {label:<20} & " + " & ".join(coefs) + r" \\")
        lines.append(f"        {'':<20} & " + " & ".join(ses) + r" \\")
    lines.append(r"        \hline")
    lines.append(f"        $R^2$ & " + " & ".join(f"{m.rsquared:.2f}" for m in models) + r" \\")
    lines.append(f"        $N$ & " + " & ".join(f"{int(m.nobs)}" for m in models) + r" \\")
    lines += [r"        \hline", r"    \end{tabular}", r"\end{center}", ""]

    out = tabpath("anchor_loss_regression.tex")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
