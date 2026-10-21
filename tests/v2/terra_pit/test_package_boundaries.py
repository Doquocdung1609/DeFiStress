"""Static controls for offline-only package boundaries and immutable source ownership."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "defistress_v2/terra_pit"
BANNED_IMPORT_ROOTS = {"httpx", "requests", "socket", "urllib", "web3"}
BANNED_TERMS = {"risk_score", "threshold_fit", "historical_backtest", "monte_carlo"}


def test_package_has_no_network_imports() -> None:
    violations: list[str] = []
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots = {node.module.split(".")[0]}
            else:
                continue
            if roots & BANNED_IMPORT_ROOTS:
                violations.append(f"{path.name}:{node.lineno}")
    assert violations == []


def test_package_does_not_import_v1_terra_models() -> None:
    for path in PACKAGE.glob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        assert "sim.terra" not in text


def test_no_implemented_model_or_backtest_api_is_exposed() -> None:
    exported = (PACKAGE / "__init__.py").read_text(encoding="utf-8").lower()
    for term in BANNED_TERMS:
        assert term not in exported
