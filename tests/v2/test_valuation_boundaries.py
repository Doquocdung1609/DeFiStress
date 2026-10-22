"""Static P02-03-S scope boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_PATHS = (
    ROOT / "defistress_v2/contracts/valuation.py",
    ROOT / "defistress_v2/valuation",
)
BANNED_IMPORT_ROOTS = {"httpx", "requests", "socket", "urllib", "web3"}
BANNED_PROJECT_ROOTS = {"sim", "backend"}


def _sources() -> tuple[Path, ...]:
    result: list[Path] = []
    for path in PACKAGE_PATHS:
        result.extend(path.rglob("*.py") if path.is_dir() else (path,))
    return tuple(result)


def test_p02_03_s_has_no_network_historical_or_engine_imports() -> None:
    violations: list[str] = []
    for path in _sources():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots = {node.module.split(".")[0]}
            else:
                continue
            if roots & (BANNED_IMPORT_ROOTS | BANNED_PROJECT_ROOTS):
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert violations == []


def test_p02_03_s_exposes_no_liquidation_swap_backtest_or_monte_carlo_api() -> None:
    exported = (ROOT / "defistress_v2/valuation/__init__.py").read_text(encoding="utf-8").lower()
    for forbidden in ("liquidation", "swap", "backtest", "monte_carlo", "collector", "rpc"):
        assert forbidden not in exported
