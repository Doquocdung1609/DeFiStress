"""Master run script for the Terra–Luna crash replication package.

Runs every exhibit-generating script in order and writes outputs to ``output/``.
Each figure script is self-contained and reads only from the shipped ``data/``
directory (paths resolved via ``config.py``), so this is fully relocatable.

Usage:
    python run_all.py            # run everything
    python run_all.py fig01 fig03   # run a subset by id
"""
import importlib
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent
sys.path.append(str(CODE))
sys.path.append(str(CODE / "lib"))

# Prep steps that rebuild shipped intermediates from raw shipped inputs.
PREP = [
    ("prep_fig06", "prep.prep_fig06_concentration"),
]

# (id, module path) in paper order. Extend as exhibits are ported.
FIGURES = [
    ("fig01", "figures.fig01_anchor_net_rates"),
    ("fig02", "figures.fig02_ust_supply_by_entity"),
    ("fig03", "figures.fig03_anchor_cashflow"),
    ("fig04", "figures.fig04_network_volume"),
    ("fig05", "figures.fig05_market_cap"),
    ("fig06", "figures.fig06_anchor_concentration"),
    ("fig07", "figures.fig07_wallet_A_B"),
    ("fig08", "figures.fig08_curve_swaps"),
    ("fig09", "figures.fig09_binance_ustusdt"),
    ("fig10", "figures.fig10_run_outflows"),
    ("fig11", "figures.fig11_swap_arbitrage"),
    ("fig12", "figures.fig12_death_spiral"),
    ("fig13", "figures.fig13_outflow_by_size"),
    ("fig14", "figures.fig14_cox_hazard"),
    ("figIA1", "figures.figIA1_staking_yield"),
    ("figIA2", "figures.figIA2_curve_swaps_2021"),
    ("figIA3", "figures.figIA3_may2021_dynamics"),
    ("figIA4", "figures.figIA4_may2021_by_size"),
    ("figIA5", "figures.figIA5_swap_arbitrage_2021"),
]

# data-driven tables (render LaTeX into output/tables/)
TABLES = [
    ("table1", "tables.fmt_table1_token_volume"),
    ("table2", "tables.fmt_table2_loss_summary"),
    ("table3", "tables.fmt_table3_loss_regression"),
    ("tableIA1", "tables.fmt_tableIA1_native_swap_run"),
    ("tableIA2", "tables.fmt_tableIA2_native_swap_run_2021"),
]


def main(argv):
    wanted = set(argv) or None
    ran, failed = [], []
    for fid, mod in PREP + FIGURES + TABLES:
        if wanted and fid not in wanted:
            continue
        try:
            m = importlib.import_module(mod)
            m.main()
            ran.append(fid)
        except Exception as e:  # keep going; report at the end
            failed.append((fid, repr(e)))
            print(f"  !! {fid} FAILED: {e}")
    print(f"\nDone. ran={ran}")
    if failed:
        print("FAILED:")
        for fid, err in failed:
            print(f"  {fid}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
