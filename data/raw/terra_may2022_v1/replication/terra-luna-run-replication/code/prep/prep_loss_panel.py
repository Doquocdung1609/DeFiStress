"""Prep — depositor loss/sophistication panel (input to Tables 2 and 3).

Rebuilds ``data/loss/anchor_loss_panel.parquet``: one row per Anchor depositor
(pre-run aUST > 100 UST, intermediaries removed) with the realized percentage
loss over the May 2022 run plus pre-run sophistication measures.  This is the
analysis panel consumed by ``tables/fmt_table2_loss_summary.py`` and
``tables/fmt_table3_loss_regression.py``.

This script reproduces the source notebook's ``loss_reg`` *exactly* (verified to
the digit against the notebook's Table-2 summary): full sample 159,669 wallets,
size groups 31,668 / 62,334 / 48,969 / 14,481 / 2,005 / 212.  It supersedes the
earlier shipped panel, which was assembled from two narrower precomputed files
(``anchor_depositor_losses`` + ``prerun-sophistication-measures``) and so dropped
~11.6 k depositors and binned on the wrong size variable.

Output: data/loss/anchor_loss_panel.parquet
    address, prerun_usd, full_maxusd, perc_loss, log_wealth, log_volume_adj,
    age, log_age_months, cex_degree, used_bridge
    (perc_loss is stored RAW — the table scripts winsorize at read time, as the
    notebook does in ``prepare_regression_table``.)

    NOTE on the "Exited" count (Table 2, col 8): that figure is an EXTERNAL
    number and is not reconstructable from the on-chain panel, so it is NOT a
    column here — it is hard-coded in fmt_table2_loss_summary.py.

Shipped inputs (small, derived; intermediaries/DEX label sets):
    data/labels/interdm_addresses.parquet   intermediary wallets to exclude
    data/labels/dex_swap_addresses.parquet  DEX contracts (with a known creator),
        used to flag two-leg DEX swaps in the flow log (``label_dex_swaps``)
    data/loss/depositor_prerun_size.parquet authoritative prerun_usd per wallet

Raw inputs (authors' research tree; node-rebuildable — see Datasets.md):
    data/terra_run/anchor_depositor_size.parquet            full_maxusd, prerun_aust (index: address)
    data/terra_run/terra_run_depositor_6token_transfers.parquet  time, src, tgt, token, amount
    data/terra_run/prerun_balances_fullnode.parquet         token, address, found (May 6)
    data/terra_run/postrun_balances_fullnode.parquet        token, address, found (May 13)
    data/terra_run/terra_may2022_run_usd_prices.parquet     minute, base_asset, vwap_usd
    data/loss_regression/address_balance_volume_cex.parquet address, cex_degree, volusd, balusd, age
    data/loss_regression/address_using_bridges.parquet      address

Source notebook: ``code/Run-3-loss-regression-240404.ipynb``
    (cells: get_depositors / get_depositor_centric_transfer / get_sophistication /
     get_pre_post_balance / get_flow_loss / prepare_regression_table).

Run (authors' environment only — reads the raw research tree):
    python prep/prep_loss_panel.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CODE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(CODE_DIR))
from config import datadir, PKG_ROOT  # noqa: E402

# Raw research-data tree (repo ``data/``): replication_package -> publish -> code -> Terra.
RAW_TR = PKG_ROOT.parents[2] / "data" / "terra_run"
RAW_LR = PKG_ROOT.parents[2] / "data" / "loss_regression"

PRERUN_AUST_RATE = 1.24616          # 100 UST floor -> aUST, per the source notebook
WINDOW = ("2022-05-06 00:00:00", "2022-05-13 23:59:59")
FEE_ADDRESS = "terra17xpfvakm2amg962yls6f84z3kell8c5lkaeqfa"
ANCHOR_MARKET = "terra1sepfj7s0aeg5967uxnfk4thzlerrsktkpelm5s"   # aUST mint/redeem
BLUNA_HUB = "terra1mtwph2juhj0rvjz7dy92gvl6xvukaxu8rfv8ts"       # bLUNA
SIZE_LABELS = ["100-1K", "1K-10K", "10K-100K", "100K-1M", "1M-10M", ">10M"]
BALANCE_TOKENS = ["aUST", "UST", "LUNA", "bLUNA", "ANC", "bETH"]


def get_balance_group(x: pd.Series) -> pd.Series:
    return pd.cut(x, bins=[10 ** n for n in [1.9, 3, 4, 5, 6, 7, np.inf]], labels=SIZE_LABELS)


def get_depositors(interdm: set) -> pd.DataFrame:
    """Notebook ``get_depositors``: pre-run aUST > 100 UST, minus intermediaries.

    The size group bins on ``full_maxusd`` (the wallet's peak USD balance over
    the window) — the same size variable the source notebook uses.
    """
    depbal = pd.read_parquet(RAW_TR / "anchor_depositor_size.parquet").reset_index()
    keep = set(depbal.loc[depbal.prerun_aust > 100 / PRERUN_AUST_RATE, "address"]) - interdm
    depbal = depbal.loc[depbal.address.isin(keep)].reset_index(drop=True)
    depbal["size_group"] = get_balance_group(depbal["full_maxusd"])
    return depbal


def _address_centric(fl: pd.DataFrame, addrs: set) -> pd.DataFrame:
    """Notebook ``get_address_centric_vol(..., keep_duplicates=True)``."""
    infl = fl.loc[fl.tgt.isin(addrs)].rename(columns={"tgt": "address", "src": "tgt"})
    outfl = fl.loc[fl.src.isin(addrs)].rename(columns={"src": "address"}).copy()
    outfl["vol"] *= -1
    return pd.concat([infl, outfl], ignore_index=True)


def _label_dex_swaps(deptrr: pd.DataFrame, dexaddrs: set) -> pd.DataFrame:
    """Notebook ``label_dex_swaps``: a single-tx pair (one src, one tgt that is a
    DEX, two tokens, opposite signs) is a two-leg DEX swap."""
    deptrr = deptrr.copy()
    deptrr["txind"] = pd.Categorical(
        deptrr["address"].astype(str) + "_" + deptrr["time"].astype(str)
    ).codes
    dextxids = []
    for txind, df in deptrr.groupby("txind"):
        if len(df) != 2:
            continue
        if len(set(df.tgt)) != 1 or len(set(df.address)) != 1:
            continue
        if next(iter(set(df.tgt))) not in dexaddrs:
            continue
        if len(set(df.token)) != 2:
            continue
        if len({np.sign(v) for v in df.vol}) != 2:
            continue
        dextxids.append(txind)
    deptrr["is_dex_swap"] = deptrr["txind"].isin(dextxids)
    return deptrr.drop(columns=["txind"])


def get_depositor_centric_transfer(depositors, dexaddrs: set) -> pd.DataFrame:
    """Notebook ``get_depositor_centric_transfer``: address-centric 6-token flow
    over the run window, with DEX swaps flagged and aUST/bLUNA mints attributed."""
    deptr = (
        _address_centric(
            pd.read_parquet(
                RAW_TR / "terra_run_depositor_6token_transfers.parquet"
            ).rename(columns={"amount": "vol"}),
            set(depositors),
        )
        .query("time >= @WINDOW[0] and time <= @WINDOW[1]")
        .sort_values("time", ignore_index=True)
    )
    # fee transfers carry no second leg, so they can never be a swap
    deptr = pd.concat(
        [deptr.loc[deptr.tgt == FEE_ADDRESS],
         _label_dex_swaps(deptr.loc[deptr.tgt != FEE_ADDRESS], dexaddrs)]
    ).reset_index(drop=True)
    deptr.loc[(deptr.token == "aUST") & (deptr.tgt.isnull()), "tgt"] = ANCHOR_MARKET
    deptr.loc[(deptr.token == "bLUNA") & (deptr.tgt.isnull()), "tgt"] = BLUNA_HUB
    deptr = (
        deptr.query("time >= @WINDOW[0] and time <= @WINDOW[1]")
        .sort_values("time")
        .reset_index(drop=True)
    )
    deptr["is_dex_swap"] = deptr["is_dex_swap"].fillna(False)
    return deptr


def get_sophistication() -> pd.DataFrame:
    """Notebook ``get_sophistication``: CEX degree, age, and the log
    volume/balance ratio (across all tokens), plus the bridge-user flag."""
    bridge_addrs = pd.read_parquet(RAW_LR / "address_using_bridges.parquet")
    tasp = pd.read_parquet(
        RAW_LR / "address_balance_volume_cex.parquet",
        columns=["address", "cex_degree", "volusd", "balusd", "age"],
    )
    tasp["log_volume_adj"] = np.log(tasp["volusd"] + 1) - np.log(tasp["balusd"] + 1)
    tasp["used_bridge"] = tasp.address.isin(bridge_addrs.address).astype(float)
    tasp["log_age_months"] = np.log(tasp["age"] / 30 + 1)
    return tasp[["address", "cex_degree", "age", "log_volume_adj", "used_bridge", "log_age_months"]]


def get_pre_post_balance(depbal: pd.DataFrame) -> pd.DataFrame:
    """Notebook ``get_pre_post_balance``: per-token May-6 and May-13 USD balances
    fetched from the full node, valued at the run-window VWAP."""
    prebal = pd.read_parquet(RAW_TR / "prerun_balances_fullnode.parquet")
    postbal = pd.read_parquet(RAW_TR / "postrun_balances_fullnode.parquet")
    addrs = set(depbal.address)
    prebal = prebal.loc[prebal.address.isin(addrs) & prebal.token.isin(BALANCE_TOKENS)].rename(columns={"found": "may6_balance"})
    postbal = postbal.loc[postbal.address.isin(addrs) & postbal.token.isin(BALANCE_TOKENS)].rename(columns={"found": "may13_balance"})
    usdbal = prebal.merge(postbal, on=["token", "address"], how="outer")
    usdbal["may6_balance"] = usdbal["may6_balance"].fillna(0.0) / 1e6
    usdbal["may13_balance"] = usdbal["may13_balance"].fillna(0.0) / 1e6

    prices = pd.read_parquet(RAW_TR / "terra_may2022_run_usd_prices.parquet")
    prepostprice = (
        pd.concat(
            [prices.xs(WINDOW[0], level="minute").rename(columns={"vwap_usd": "prerun"}),
             prices.xs("2022-05-13 23:59:00", level="minute").rename(columns={"vwap_usd": "postrun"})],
            axis=1,
        ).reset_index().rename(columns={"base_asset": "token"})
    )
    usdbal = usdbal.merge(prepostprice, on="token", how="left")
    usdbal["may6_usdbalance"] = usdbal["prerun"] * usdbal["may6_balance"]
    usdbal["may13_usdbalance"] = usdbal["postrun"] * usdbal["may13_balance"]
    return usdbal.drop(columns=["prerun", "postrun"])


def get_flow_loss(usdbal: pd.DataFrame, cvfl: pd.DataFrame) -> pd.DataFrame:
    """Notebook ``get_flow_loss(..., count_usd=None)`` — the "mark every flow"
    branch used for the headline loss.  Realized loss combines the pre/post USD
    balances with net flows; ``add_to_balance`` credits inflows received before a
    wallet's first outflow so that pass-through deposits are not counted as gains.

    (The ``count_usd`` / counterparty-label branch of the notebook function feeds
    a *different* statistic and is not needed for the panel, so it is omitted;
    ``is_dex_swap`` is retained as a flow-grain key to keep the first-outflow
    timing bit-identical to the notebook.)
    """
    prices = pd.read_parquet(RAW_TR / "terra_may2022_run_usd_prices.parquet")
    prices = prices.reset_index().rename(columns={"base_asset": "token"})
    cvflc = cvfl.merge(prices, on=["minute", "token"]).eval("volusd = vol * vwap_usd")

    cvflca = (
        cvflc.groupby(["address", "minute"], as_index=False).agg({"volusd": "sum"})
    )
    cvflca["is_outflow"] = np.where(cvflca["volusd"] < 0, "outflow", "inflow")
    cvflca = cvflca.groupby(["address", "is_outflow"]).agg({"volusd": "sum"})["volusd"].unstack("is_outflow")
    cvflca["outflow"] = cvflca["outflow"].abs()

    first_out_time = cvflc.loc[cvflc.volusd < 0].groupby("address").agg(first_out_time=("minute", "min"))
    cvflc = cvflc.merge(first_out_time.reset_index(), how="left")
    add_to_balance = (
        cvflc.loc[(cvflc["minute"] < cvflc["first_out_time"]) & (cvflc["volusd"] > 0)]
        .groupby("address").agg(add_to_balance=("volusd", "sum"))
    )

    usdbalagg = usdbal.groupby("address").agg({"may6_usdbalance": "sum", "may13_usdbalance": "sum"})
    fbcb = usdbalagg.join(cvflca).join(add_to_balance).fillna(0)
    if "inflow" not in fbcb.columns:
        fbcb["inflow"] = 0
    fbcb.eval(
        "perc_loss = (1 - (may13_usdbalance + outflow - inflow + add_to_balance)"
        " / (may6_usdbalance + add_to_balance)) * 100",
        inplace=True,
    )
    return fbcb


def main() -> Path:
    interdm = set(pd.read_parquet(datadir("labels", "interdm_addresses.parquet"))["address"])
    dexaddrs = set(pd.read_parquet(datadir("labels", "dex_swap_addresses.parquet"))["address"])

    depbal = get_depositors(interdm)
    print(f"  depositors: {len(depbal):,}")
    tasp = get_sophistication()
    deptr = get_depositor_centric_transfer(depbal.address, dexaddrs)
    print(f"  depositor flow rows: {len(deptr):,}")

    cvfl = (
        deptr.eval("vol = vol / 1e6")
        .assign(minute=lambda df: df.time.dt.floor("1min"))
        .groupby(["minute", "token", "address", "tgt", "is_dex_swap"], as_index=False)
        .agg({"vol": "sum"})
    )
    usdbal = get_pre_post_balance(depbal)
    fbcb = get_flow_loss(usdbal, cvfl)

    # assemble the panel (notebook ``prepare_regression_table``, pre-winsorize)
    panel = (
        depbal[["address", "full_maxusd"]]
        .merge(fbcb[["perc_loss"]].reset_index())
        .merge(tasp)
    )
    panel["log_wealth"] = np.log(panel["full_maxusd"] + 1)

    # authoritative prerun_usd (shipped; also used by Fig 10 and the size table)
    prerun = pd.read_parquet(datadir("loss", "depositor_prerun_size.parquet"))[["address", "prerun_usd"]]
    panel = panel.merge(prerun, on="address", how="left")

    panel = panel[[
        "address", "prerun_usd", "full_maxusd", "perc_loss", "log_wealth",
        "log_volume_adj", "age", "log_age_months", "cex_degree", "used_bridge",
    ]]

    out = datadir("loss", "anchor_loss_panel.parquet")
    panel.to_parquet(out, index=False)
    print(f"wrote {out}  ({len(panel):,} rows, {panel.shape[1]} cols)")
    grp = get_balance_group(panel["full_maxusd"]).value_counts().reindex(SIZE_LABELS)
    print("  size groups:", " / ".join(f"{g:,}" for g in grp))
    return out


if __name__ == "__main__":
    main()
