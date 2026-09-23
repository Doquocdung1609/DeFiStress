"""Figure IA.2 — UST-3Crv swap transactions, May 2021 de-pegging event.

Reproduces ``paper/figures/curve_swap_may2021.png``. Same construction as
Figure 8 (see fig08_curve_swaps.py) over May 17–29, 2021; swaps below 300 UST
are dropped, and the four addresses that bought UST in size appear as blue
triangles (now also labelled in the upper-panel legend, per author review).

The spurious upward jump at the right end of the net-swap-volume line in the
published figure was an artifact of mis-aligned buy/sell cumulative sums; it is
fixed in ``fig08_curve_swaps._cumulative_net`` (shared minute grid).

Output: output/figures/curve_swap_may2021.png
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from fig08_curve_swaps import plot_curve_swaps  # noqa: E402


def main() -> Path:
    return plot_curve_swaps("curve_ust_may2021.parquet", "2021-05-17", "2021-05-29",
                            "curve_swap_may2021.png", time_fmt="%m-%d",
                            min_sell=300, page_w_cm=15.5, net_legend_loc="upper left")


if __name__ == "__main__":
    main()
