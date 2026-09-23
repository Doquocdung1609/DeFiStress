"""Table 1 — Token volume.

Renders ``paper/tables/network_volume_by_token.tex``: the volume (billion USD)
and transaction count of the top 15 tokens on the Terra–Luna network from
2021-09-30 to 2022-05-06.

Provenance / reproducibility note
---------------------------------
The underlying figures come from ``vol_by_token(transfers, action in
{transfer, send}, 2021-10-01 .. 2022-05-06)`` over the **full node token-transfer
log** (≈ 86M transactions; see code/Terra-nansen-data-volume-decomposition-
20230206.ipynb In[12-13]). That raw log is far too large to ship and was built
from the archive node (transaction logs of type ``transfer`` and ``send``); it
is documented in Datasets.md, not redistributed. We therefore
ship the **computed result** as an analysis-data intermediate and render the
LaTeX table from it:

    data/tables/table1_token_volume.csv   cols: token, label, volume_bn_usd, tx_count

Output:
    output/tables/network_volume_by_token.tex
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from config import datadir, tabpath  # noqa: E402


def main() -> Path:
    df = pd.read_csv(datadir("tables", "table1_token_volume.csv"))
    df = df.sort_values("volume_bn_usd", ascending=False)

    lines = [
        r"\begin{center}",
        r"    \begin{tabular}{lrr}",
        r"        \toprule",
        r"        Token                      & Volume (\$ Billion) & Transaction Count \\",
        r"        \midrule",
    ]
    for _, r in df.iterrows():
        lines.append(f"        {r['label']:<26} & {r['volume_bn_usd']:<19.3f} & {int(r['tx_count']):<17d} \\\\")
    lines += [r"        \bottomrule", r"    \end{tabular}", r"\end{center}", ""]

    out = tabpath("network_volume_by_token.tex")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    main()
