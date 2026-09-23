"""Shared figure-styling helpers for the replication package.

The published paper (JFE final revision) is a 12pt ``article`` with a 155 mm text
width (``\\textwidth 155mm``) and captions set with the ``caption`` package
``small`` option, i.e. roughly 11 pt.  Each figure is therefore rendered at its
**true on-page size** (``figsize_cm``) with text set directly at caption size
(``caption_rc``): the saved PNG is what-you-see-is-what-you-get — placed at the
matching ``\\includegraphics`` width it is not scaled, so fonts land at caption
size and line/marker weights print at their natural matplotlib values.  These
helpers:

  * ``caption_rc`` — rcParams with text at ~caption size, for a figure drawn at
    its true on-page size (the convention every exhibit uses).
  * ``figsize_cm`` — matplotlib ``figsize`` (inches) from an on-page width/height
    given in centimetres.
  * ``integer_yaxis`` — whole-number y-axis ticks, capped to avoid crowding short panels.
  * ``quarter_date_axis`` — quarter-spaced, month-labelled ticks (``Jan 2021``,
    ``Apr 2021``, …), rotated, for the long 2020–2022 time-series panels.
  * ``readable_number`` / ``readable_price`` — human-readable axis tick labels
    (ports of ``code/header.py:readable``), used by the log-scale exhibits.
"""
from __future__ import annotations

import numpy as np
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

TEXTWIDTH_CM = 15.5      # \textwidth = 155 mm
CAPTION_PT = 11.0        # caption package `small` option in a 12pt document (~10.95pt)
MYWIDTH_CM = 0.7 * TEXTWIDTH_CM   # \mywidth = 0.7\textwidth

# Render every figure at SCALE x its on-page size.  Placed at the matching
# \includegraphics width it scales down by 1/SCALE, so the in-figure text prints
# at ~CAPTION_PT/SCALE and multi-panel exhibits get room for legends and ticks,
# while line and font weights stay in proportion.
SCALE = 1.6


def caption_rc(caption_pt: float = CAPTION_PT) -> dict:
    """rcParams for a figure rendered at its TRUE on-page size: text is set
    directly at ``caption_pt`` with no shrink-compensation.  Pair with
    ``figsize=figsize_cm(page_w_cm, page_h_cm)`` so the saved PNG is WYSIWYG and
    line/marker weights print at their natural matplotlib values."""
    return {
        "font.size": caption_pt,
        "axes.titlesize": caption_pt,
        "axes.labelsize": caption_pt,
        "xtick.labelsize": caption_pt * 0.9,
        "ytick.labelsize": caption_pt * 0.9,
        "legend.fontsize": caption_pt * 0.9,
        "legend.title_fontsize": caption_pt * 0.9,
        "legend.frameon": True,        # bordered, slightly shaded box (figIA4 style)
        "legend.facecolor": "0.93",
        "legend.edgecolor": "0.5",
        "legend.framealpha": 0.9,
    }


def figsize_cm(w_cm: float, h_cm: float) -> tuple:
    """matplotlib ``figsize`` (inches) for a figure that is ``w_cm`` x ``h_cm`` on
    the page, enlarged by ``SCALE`` so ``\\includegraphics[width=w_cm]`` scales it
    back down by 1/SCALE (shrinking the in-figure text to ~CAPTION_PT/SCALE)."""
    return (w_cm * SCALE / 2.54, h_cm * SCALE / 2.54)


def integer_yaxis(ax, nbins=6, **kwargs) -> None:
    """Whole-number y-axis ticks, few enough to avoid crowding short panels."""
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=nbins, **kwargs))


def quarter_date_axis(ax, fmt: str = "%b %Y") -> None:
    """Quarter-spaced major ticks (Jan/Apr/Jul/Oct) labelled like ``Jan 2021``."""
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))


# --- human-readable axis labels (port of code/header.py:readable) ------------
def readable_number(num: float) -> str:
    """Human-readable large number: 3e8 -> '300M', 1e9 -> '1B', 1e12 -> '1T'.

    Mirrors ``header.readable`` for num >= 1, extended to trillions and without a
    trailing '.0' on whole values (so log-axis ticks read '1B'/'3B' not '1.0B')."""
    num = float(num)
    if num < 0:
        return "-" + readable_number(-num)
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if num >= div:
            v = num / div
            return (f"{v:.0f}" if abs(v - round(v)) < 1e-9 else f"{v:.1f}") + suf
    if num == 0:
        return "0"
    return f"{num:.0f}"


def readable_price(num: float) -> str:
    """Readable dollar tick for >= $0.01 (e.g. '100', '1', '0.1', '0.01');
    scientific (``10^-n``) below $0.01, per author review of Fig 12."""
    num = float(num)
    if num >= 0.01:
        if num >= 1:
            return f"{num:.0f}"
        return f"{num:g}"
    exp = int(round(np.log10(num)))
    return r"$10^{%d}$" % exp
