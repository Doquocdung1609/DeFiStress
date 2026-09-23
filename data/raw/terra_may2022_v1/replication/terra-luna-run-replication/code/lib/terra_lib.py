"""Shared helpers for the Terra–Luna crash replication package.

Small, dependency-light utilities used by several figure scripts:
  * label loading / address-name mapping
  * address-centric flow aggregation (signed in/out flows around an address)
  * signed stacked-area plotting in matplotlib (positive bands above 0,
    negative bands below 0) — the matplotlib analogue of the original
    holoviews ``plot_stacked`` helper.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import datadir  # noqa: E402


def load_labels() -> pd.DataFrame:
    """Anchor cash-flow counterparty labels (address, address_name)."""
    return pd.read_csv(datadir("labels", "anchor_contracts.csv"))


def address_name_map() -> dict:
    """address -> human-readable address_name (falls back to the address itself)."""
    labs = load_labels()
    return labs.dropna(subset=["address_name"]).set_index("address")["address_name"].to_dict()


def get_address_centric_vol(fl: pd.DataFrame, addrs, volcol: str = "vol") -> pd.DataFrame:
    """Re-orient a (src, tgt, vol) flow table around a set of addresses.

    Inflows (tgt in addrs) keep positive volume; outflows (src in addrs) are
    negated. The focal address becomes ``address`` and the counterparty ``tgt``.
    Mirrors header.get_address_centric_vol(..., keep_duplicates=True).
    """
    infl = fl.loc[fl.tgt.isin(addrs)].rename(columns={"tgt": "address", "src": "tgt"})
    outfl = fl.loc[fl.src.isin(addrs)].rename(columns={"src": "address"}).copy()
    outfl[volcol] = outfl[volcol] * -1
    return pd.concat([infl, outfl], ignore_index=True)


def plot_stacked_area(ax, df: pd.DataFrame, colors=None, alpha: float = 0.9):
    """Signed stacked area: columns that are (mostly) >=0 stack upward from 0,
    columns that are (mostly) <=0 stack downward from 0.

    Returns the matplotlib handles/labels for building a legend.
    """
    x = df.index
    pos_base = np.zeros(len(df))
    neg_base = np.zeros(len(df))
    handles, labels = [], []
    for i, col in enumerate(df.columns):
        y = df[col].to_numpy()
        color = None if colors is None else colors[i % len(colors)]
        if np.nansum(y) >= 0:
            top = pos_base + y
            h = ax.fill_between(x, pos_base, top, color=color, alpha=alpha, linewidth=0)
            pos_base = top
        else:
            bot = neg_base + y
            h = ax.fill_between(x, neg_base, bot, color=color, alpha=alpha, linewidth=0)
            neg_base = bot
        handles.append(h)
        labels.append(col)
    return handles, labels
