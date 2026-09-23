"""Table IA.1 — Top native-swap addresses, May 2022 Terra run.

Renders ``paper/tables/native_swap_users_run.tex`` (paper \\label
``tab:top-native-swappers-run``): the addresses that swapped the largest dollar
amount on the Terra native swap market over the run window, May 7–13, 2022, with
volume in UST (millions), volume in USD (millions), the swap count, and an
entity label.

Provenance / reproducibility note
---------------------------------
The numbers come from ``get_top_lbl_swappers(swap_ftx, 'uusd', 'uluna', 'UST',
terra_lbl, ...)[0:21]`` in the source notebook
``code/Terra-analysis-native-swaps-run-20230324.ipynb`` (In[43] defines the
function, In[46] calls it, In[47] is the ``to_latex`` whose output is this
table). That function groups the **per-trader native-swap log** by ``trader``
over the window, summing ``offer_amount`` -> ``vol`` (UST, millions) and
``offer_amount * UST_price`` -> ``volusd`` ($, millions), counting swaps ->
``n_trade``, and merging author entity labels.

Direction note: despite the paper caption ("LUNA for UST"), the underlying call
is ``offer='uusd', swap='uluna'`` (UST -> LUNA), i.e. the swaps that *minted*
LUNA during the run. The dollar column confirms the direction (e.g. 687 UST M x
~0.65 ~= 449 $M at the run-period UST price).

Why this ships as a computed CSV (cf. Table 1): the per-trader swap log carries
trader addresses and is not redistributed — the shipped
``data/native_swaps/ust_luna_swaps_run.parquet`` is a minimal 4-column extract
(time, offer/swap/fee amount, no trader) used only by Fig 11 / Fig IA.5.
Additionally, several labels here ("UST/LUNA arbitrageur", ...) were curated by
the authors for the paper and are not in the on-chain label file. We therefore
ship the **computed result** and render the LaTeX from it:

    data/tables/tableIA1_native_swap_users_run.csv
        cols: address, vol_ust_m, vol_usd_m, tx_count, label

Output:
    output/tables/native_swap_users_run.tex
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from config import datadir, tabpath  # noqa: E402

HEADERS = ["Address", "Vol (UST M)", r"Vol (\$M)", "Transaction Count", "Address Label"]
COLS = ["address", "vol_ust_m", "vol_usd_m", "tx_count", "label"]
COLSPEC = "lllrl"


def _row(cells, widths):
    """One tabular line: 12-space indent, each cell left-justified to its
    column width, joined by ' & ', terminated by ' \\\\'."""
    return "            " + " & ".join(c.ljust(w) for c, w in zip(cells, widths)) + r" \\"


def main() -> Path:
    df = pd.read_csv(datadir("tables", "tableIA1_native_swap_users_run.csv"), dtype=str)
    # published rank order is descending USD volume; stable sort preserves ties.
    df = df.sort_values("vol_usd_m", key=lambda s: s.astype(int),
                        ascending=False, kind="stable").reset_index(drop=True)

    cells = [[r[c] for c in COLS] for _, r in df.iterrows()]
    widths = [max(len(HEADERS[j]), max(len(row[j]) for row in cells)) for j in range(len(COLS))]

    lines = [
        "",
        r"\begin{center}",
        r"    % \vspace{-8pt}",
        r"    % This table reports...",
        r"    % \vspace{10pt}",
        r"    {\scriptsize",
        rf"        \begin{{tabular}}{{{COLSPEC}}}",
        r"            \toprule",
        _row(HEADERS, widths),
        r"            \midrule",
        *[_row(row, widths) for row in cells],
        r"            \bottomrule",
        r"        \end{tabular}",
        r"    }",
        r"\end{center}",
        "",
    ]

    out = tabpath("native_swap_users_run.tex")
    out.write_text("\n".join(lines))
    print(f"wrote {out} ({len(cells)} rows)")
    return out


if __name__ == "__main__":
    main()
