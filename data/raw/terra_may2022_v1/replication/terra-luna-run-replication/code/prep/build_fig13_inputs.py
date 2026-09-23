"""Build-time extractor for the Figure 13 inputs (NOT part of ``run_all``).

Figure 13 (Anchor outflows by size) tracks each depositor's *full aUST balance
trajectory* during the run, broken out by wallet size.  The balance path is the
running cumulative sum of **every aUST transfer that touches a depositor** — not
just Anchor deposit/withdraw — so the raw input is the run-window aUST transfer
log restricted to depositor wallets.  That log (the aUST slice of a 6-token
depositor transfer panel, ~0.56 M rows) lives only in the authors' research data
tree, so — exactly like the 86 M-tx transfer log behind Table 1 — it is not
shipped; this script extracts the small derived inputs that ARE shipped:

    data/anchor_run/run_aust_flow_by_depositor.parquet   time, address, vol
        Address-centric aUST flow among depositors over May 6–13, 2022.
        For every aUST transfer with a depositor on either side, one row per
        depositor side: ``vol`` = +amount when the depositor received, -amount
        when it sent (a depositor->depositor transfer yields both rows).  This is
        ``get_address_centric_vol(..., keep_duplicates=True)`` from the source
        notebook, restricted to ``token == 'aUST'``.

    data/loss/depositor_prerun_size.parquet  (+ full_maxusd column)
        The shipped depositor-size table gains ``full_maxusd`` — the wallet's
        maximum USD balance over the window, which is the size measure the
        figure bins on (``get_balance_group``).  Existing columns (address,
        prerun_aust, prerun_usd; used by Fig 10 and Table 2/3) are preserved.

Source notebook: ``code/Run-3-loss-regression-240404.ipynb``
    (``get_depositors`` / ``get_address_centric_vol`` / ``get_aust_balance_by_group``).

Raw inputs (authors' research tree; node-rebuildable — see Datasets.md):
    data/terra_run/anchor_depositor_size.parquet          full_maxusd, prerun_aust (index: address)
    data/terra_run/terra_run_depositor_6token_transfers.parquet   time, src, tgt, token, amount

Rebuild from the archive node: parse aUST (`terra1hzh9...8z07zu`) transfer/send
logs per block over May 6–13 2022, keep those whose sender or recipient is an
Anchor depositor, and orient them address-centric as above.  ``full_maxusd`` is
the per-address max of the daily USD aUST balance from the same balance panel.

Run (authors' environment only):  python prep/build_fig13_inputs.py
  NOTE: this OVERWRITES the shipped data/loss/depositor_prerun_size.parquet in
  place (adding the full_maxusd column) and writes
  data/anchor_run/run_aust_flow_by_depositor.parquet.  It requires the un-shipped
  raw inputs above, so it is not runnable against the published package and is not
  part of run_all; the shipped files it would produce are already included.
"""
import sys
from pathlib import Path

import pandas as pd

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(CODE_DIR))
from config import datadir, PKG_ROOT  # noqa: E402

# Raw research-data tree (repo ``data/``): replication_package -> publish -> code -> Terra.
RAW = PKG_ROOT.parents[2] / "data" / "terra_run"

PRERUN_AUST_RATE = 1.24616          # 100 UST floor -> aUST, per the source notebook
WINDOW = ("2022-05-06 00:00:00", "2022-05-13 23:59:59")


def main() -> None:
    interdm = set(pd.read_parquet(datadir("labels", "interdm_addresses.parquet"))["address"])

    # --- depositor universe (notebook get_depositors) -----------------------
    size_raw = pd.read_parquet(RAW / "anchor_depositor_size.parquet").reset_index()
    depositors = set(
        size_raw.loc[size_raw.prerun_aust > 100 / PRERUN_AUST_RATE, "address"]
    ) - interdm

    # --- (1) add full_maxusd to the shipped depositor-size table ------------
    shipped = pd.read_parquet(datadir("loss", "depositor_prerun_size.parquet"))
    shipped = shipped.drop(columns=[c for c in ("full_maxusd",) if c in shipped])
    shipped = shipped.merge(
        size_raw[["address", "full_maxusd"]], on="address", how="left"
    )
    shipped.to_parquet(datadir("loss", "depositor_prerun_size.parquet"), index=False)
    print(f"  depositor_prerun_size.parquet: {len(shipped):,} rows (+full_maxusd)")

    # --- (2) address-centric aUST flow among depositors ---------------------
    fl = (
        pd.read_parquet(
            RAW / "terra_run_depositor_6token_transfers.parquet",
            columns=["time", "src", "tgt", "token", "amount"],
        )
        .query("token == 'aUST'")
    )
    infl = fl.loc[fl.tgt.isin(depositors), ["time", "tgt", "amount"]].rename(
        columns={"tgt": "address", "amount": "vol"}
    )
    outfl = fl.loc[fl.src.isin(depositors), ["time", "src", "amount"]].rename(
        columns={"src": "address", "amount": "vol"}
    )
    outfl["vol"] = -outfl["vol"]
    flow = (
        pd.concat([infl, outfl], ignore_index=True)
        .query("time >= @WINDOW[0] and time <= @WINDOW[1]")
        .sort_values("time", ignore_index=True)
    )
    out = datadir("anchor_run", "run_aust_flow_by_depositor.parquet")
    flow.to_parquet(out, index=False)
    print(f"  run_aust_flow_by_depositor.parquet: {len(flow):,} rows -> {out}")


if __name__ == "__main__":
    main()
