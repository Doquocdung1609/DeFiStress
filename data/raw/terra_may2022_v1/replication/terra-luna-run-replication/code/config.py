"""Shared path configuration for the Terra–Luna crash replication package.

All scripts import paths from here so the package is fully relocatable: paths
are resolved relative to this file, never to a user's home directory or an
absolute machine path.

Layout (relative to the package root):
    data/      shipped input data (public / on-chain-derived only)
    output/    regenerated figures and tables
    code/      this folder
"""
from pathlib import Path

# code/config.py  ->  package root is the parent of code/
PKG_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PKG_ROOT / "data"
OUTPUT_DIR = PKG_ROOT / "output"
FIG_DIR = OUTPUT_DIR / "figures"
TAB_DIR = OUTPUT_DIR / "tables"


def datadir(*parts) -> Path:
    """Path to a file under the package data/ directory."""
    return DATA_DIR.joinpath(*parts)


def figpath(name: str) -> Path:
    """Path to an output figure; ensures the output dir exists."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    return FIG_DIR / name


def tabpath(name: str) -> Path:
    """Path to an output table; ensures the output dir exists."""
    TAB_DIR.mkdir(parents=True, exist_ok=True)
    return TAB_DIR / name
