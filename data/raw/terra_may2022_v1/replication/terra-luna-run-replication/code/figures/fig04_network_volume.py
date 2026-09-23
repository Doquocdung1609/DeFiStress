"""Figure 4 — Network volume of UST (left) and LUNA (right).

Node-link diagram of inter-entity-type transaction flows, one panel per token.
Reproduces ``paper/figures/UST_new.png`` and ``Luna_new.png`` (originally laid
out by hand in an external GraphML viewer) deterministically in matplotlib:

  * node size   ~ total volume flowing through the entity type,
  * node colour = sequential blue, darker = larger volume,
  * node label  = entity type + its total volume ($B),
  * directed curved edges, width ~ flow; the top-N flows highlighted in red,
  * edge label  = the flow volume ($B).

Node volume is the total volume of every edge incident to the node, with a
self-loop counted once (this matches the published node totals exactly, e.g.
UST: Other=282.4, Anchor=175.7, CEX=61.6; LUNA: Other=115.4, Admin=75.2,
CEX=59.9). Self-loops are counted in node size but are not drawn as edges.

Per the paper caption we show entity types with >= $10B total volume in the UST
network and >= $5B in the LUNA network, and edges with >= $1B of volume; the
displayed node sets (``LAYOUT``) follow the published figures (the LUNA panel
omits Anchor/Bridge).

Input (on-chain Columbus-5 volume, shippable):
    data/network/volume_by_group_token.csv   cols: volusd, srctype, tgttype, token

Output (one file per token, matching the paper's two subfigures):
    output/figures/UST_new.png    (left panel, UST network)
    output/figures/Luna_new.png   (right panel, LUNA network)

Source notebook: Snowflake/Terra-nansen-data-volume-decomposition-20230206.ipynb
    (``build_nw_lbl_typen``, which builds the networkx graph and exports it to
    GraphML); the published positions were then hand-tuned in the GraphML viewer.
"""

import sys
from math import cos, sin, pi, sqrt
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "lib"))
from config import datadir, figpath  # noqa: E402
from figstyle import caption_rc, figsize_cm  # noqa: E402

PANEL_W_CM, PAGE_H_CM = (
    7.75,
    8.0,
)  # each token panel drawn separately at ~half-textwidth (0.45\textwidth)

EDGE_MIN = 1.0  # $B: smallest cross-type flow drawn (paper: >= $1B)
N_HIGHLIGHT = 5  # number of largest non-self edges drawn in red
RAD = 0.16  # edge curvature

# Displayed nodes + clockwise order around the circle (matches the published
# layout). UST shows all eight types; LUNA omits the negligible Anchor/Bridge.
LAYOUT = {
    "UST": dict(
        order=["CEX", "Anchor", "Other", "TFL", "Bridge", "DEX", "DeFi", "Admin"],
        start_deg=90,
    ),
    "LUNA": dict(order=["CEX", "Admin", "Other", "DeFi", "DEX", "TFL"], start_deg=120),
}
# Edges whose arc should bend the other way, to move a label off a node it would
# otherwise overlap. Keyed by token, as (src, tgt).
FLIP_EDGES = {
    "UST": {("TFL", "Anchor")},  # otherwise its 1.17 label lands on the Other node
    "LUNA": set(),
}

# drawing sizes, tuned for the two-panel (half-textwidth) layout
NODE_SIZE_MAX = 2800.0
NAME_FS, VAL_FS, EDGE_FS = 7.5, 6.5, 5.5
EDGE_LW_MAX, ARROW_SCALE = 6.0, 9.0


def load_edges(token: str) -> dict:
    """{(src, tgt): volume_$B} aggregated by entity-type pair for one token."""
    df = pd.read_csv(datadir("network", "volume_by_group_token.csv"))
    sub = df[df["token"] == token]
    agg = sub.groupby(["srctype", "tgttype"])["volusd"].sum() / 1e9
    return {(s, t): v for (s, t), v in agg.items()}


def node_volume(edges_all: dict, nodes) -> dict:
    """Total incident volume per displayed node, self-loops counted once.

    Computed over the FULL edge set (incl. flows to/from nodes that are not
    drawn, e.g. Anchor/Bridge for LUNA) so node totals match the paper."""
    vol = {n: 0.0 for n in nodes}
    for (s, t), v in edges_all.items():
        if s == t:
            if s in vol:
                vol[s] += v  # self-loop counted once
        else:
            if s in vol:
                vol[s] += v
            if t in vol:
                vol[t] += v
    return vol


def circle_pos(order, start_deg) -> dict:
    n = len(order)
    return {
        name: np.array(
            [
                cos(np.deg2rad(start_deg) - i * (2 * pi / n)),
                sin(np.deg2rad(start_deg) - i * (2 * pi / n)),
            ]
        )
        for i, name in enumerate(order)
    }


def _text_color(rgba) -> str:
    r, g, b = rgba[:3]
    return "white" if (0.299 * r + 0.587 * g + 0.114 * b) < 0.55 else "#222222"


def draw_panel(ax, token: str) -> dict:
    """Draw one token's network into ``ax``; return the node volumes."""
    edges_all = load_edges(token)
    cfg = LAYOUT[token]
    nodes = cfg["order"]
    pos = circle_pos(nodes, cfg["start_deg"])
    flip = FLIP_EDGES.get(token, set())

    nvol = node_volume(edges_all, nodes)
    vmax = max(nvol.values())

    edges = {
        (s, t): v
        for (s, t), v in edges_all.items()
        if s != t and s in nodes and t in nodes and v >= EDGE_MIN
    }
    emax = max(edges.values())
    highlight = {k for k, _ in sorted(edges.items(), key=lambda x: -x[1])[:N_HIGHLIGHT]}

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.55, 1.55)

    node_size = {n: max(v / vmax * NODE_SIZE_MAX, 120) for n, v in nvol.items()}
    node_r_pts = {n: sqrt(node_size[n] / pi) for n in nodes}
    cmap = plt.colormaps["Blues"]
    node_rgba = {n: cmap(0.18 + 0.80 * (nvol[n] / vmax)) for n in nodes}

    # edges: faint (gray) first, highlighted (red) on top
    for (s, t), v in sorted(edges.items(), key=lambda kv: (kv[0] in highlight, kv[1])):
        hot = (s, t) in highlight
        rad = -RAD if (s, t) in flip else RAD
        col = "#b22222" if hot else "#9a9a9a"
        lw = 0.4 + (v / emax) * EDGE_LW_MAX
        p0, p1 = pos[s], pos[t]
        ax.add_patch(
            FancyArrowPatch(
                posA=p0,
                posB=p1,
                connectionstyle=f"arc3,rad={rad}",
                arrowstyle="-|>",
                mutation_scale=ARROW_SCALE,
                lw=lw,
                color=col,
                alpha=0.85 if hot else 0.40,
                shrinkA=node_r_pts[s] + 1,
                shrinkB=node_r_pts[t] + 2,
                zorder=2 if hot else 1,
            )
        )
        # label sits ON the arc midpoint: mid + 0.5*rad*(dy, -dx)
        d = p1 - p0
        L = np.hypot(*d)
        perp = np.array([d[1], -d[0]]) / L
        lp = (p0 + p1) / 2 + 0.5 * rad * L * perp
        ax.text(
            lp[0],
            lp[1],
            f"{v:.2f}",
            fontsize=EDGE_FS,
            color=col,
            fontweight="bold" if hot else "normal",
            ha="center",
            va="center",
            zorder=6 if hot else 5,
            bbox=dict(
                boxstyle="round,pad=0.12",
                fc="white",
                ec=col,
                lw=0.7 if hot else 0.4,
                alpha=0.92,
            ),
        )

    # nodes + labels on top
    for n in nodes:
        ax.scatter(
            *pos[n],
            s=node_size[n],
            color=node_rgba[n],
            edgecolors="white",
            linewidths=0.8,
            zorder=3,
        )
        tcol = _text_color(node_rgba[n])
        ax.text(
            pos[n][0],
            pos[n][1] + 0.07,
            n,
            fontsize=NAME_FS,
            fontweight="bold",
            ha="center",
            va="center",
            color=tcol,
            zorder=5,
        )
        ax.text(
            pos[n][0],
            pos[n][1] - 0.09,
            f"{nvol[n]:.1f}",
            fontsize=VAL_FS,
            ha="center",
            va="center",
            color=tcol,
            zorder=5,
        )
    return nvol


def main() -> list:
    outs = []
    with plt.rc_context(caption_rc()):
        for token, name in [("UST", "UST_new.png"), ("LUNA", "Luna_new.png")]:
            out = figpath(name)
            fig, ax = plt.subplots(figsize=figsize_cm(PANEL_W_CM, PAGE_H_CM))
            draw_panel(ax, token)
            fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
            fig.savefig(out, dpi=300, bbox_inches="tight")
            plt.close(fig)
            print(f"wrote {out}")
            outs.append(out)
    return outs


if __name__ == "__main__":
    main()
