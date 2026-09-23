"""Table IA.2 — Top native-swap addresses, May 2021 de-pegging event.

Renders ``paper/tables/native_swap_users_run_2021.tex`` (paper \\label
``tab:top-native-swappers-run-2021``): the addresses that swapped the largest
amount of LUNA for UST over the May 2021 de-pegging window, May 19–27, 2021,
with volume in UST (millions), the swap count, and an entity label.

Provenance / reproducibility note
---------------------------------
The numbers come from the ``top_swap_addr`` function in the source notebook
``code/Terra-analysis-native-swaps-prerun-20230205.ipynb`` (In[27]). That
function filters the **per-trader native-swap log** to a direction (here
``offer='uluna', swap='uusd'`` = LUNA -> UST, matching the caption), groups by
``trader``, sums the UST received (``swap_ust``) -> the volume column, counts
swaps -> ``n_trade``, sorts descending, and merges author entity labels. The
committed cell runs it over the full pre-run sample (In[28], 28 rows in $B); this
table is the same function restricted to the May 19–27, 2021 window, top 20, with
volume scaled to UST millions — i.e.

    top_swap_addr(swap, terra_lbl, 'uluna', 'uusd', '2021-05-19', '2021-05-27')[0:20]

(no separate USD column because UST traded ~\\$1 in May 2021, so UST ~= USD).

Why this ships as a computed CSV: see fmt_tableIA1_native_swap_run.py — the
per-trader swap log is not redistributed, and some labels are author-curated.
We ship the computed result and render the LaTeX from it:

    data/tables/tableIA2_native_swap_users_run_2021.csv
        cols: address, vol_ust_m, tx_count, label

Output:
    output/tables/native_swap_users_run_2021.tex
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from config import datadir, tabpath  # noqa: E402

HEADERS = ["Address", "Vol (UST M)", "Transaction Count", "Address Label"]
COLS = ["address", "vol_ust_m", "tx_count", "label"]
COLSPEC = "llrl"


def _row(cells, widths):
    """One tabular line: 12-space indent, each cell left-justified to its
    column width, joined by ' & ', terminated by ' \\\\'."""
    return "            " + " & ".join(c.ljust(w) for c, w in zip(cells, widths)) + r" \\"


def main() -> Path:
    df = pd.read_csv(datadir("tables", "tableIA2_native_swap_users_run_2021.csv"), dtype=str)
    # published rank order is descending UST volume; stable sort preserves ties.
    df = df.sort_values("vol_ust_m", key=lambda s: s.astype(int),
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

    out = tabpath("native_swap_users_run_2021.tex")
    out.write_text("\n".join(lines))
    print(f"wrote {out} ({len(cells)} rows)")
    return out


if __name__ == "__main__":
    main()
