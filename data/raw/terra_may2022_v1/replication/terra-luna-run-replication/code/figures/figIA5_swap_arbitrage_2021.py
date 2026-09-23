"""Figure IA.5 — Swap arbitrage, May 2021 de-pegging event.

Reproduces ``paper/figures/swap_arb_may2021.png``. Same construction and panels
as Figure 11 (see fig11_swap_arbitrage.py), over the May 17–29, 2021 window.

Output: output/figures/swap_arb_may2021.png
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from fig11_swap_arbitrage import swap_arb_window  # noqa: E402


def main() -> Path:
    return swap_arb_window("2021-05-17", "2021-05-29", "swap_arb_may2021.png")


if __name__ == "__main__":
    main()
