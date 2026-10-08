from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.app.db import Repository

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MAINNET_ARTIFACT = (
    REPOSITORY_ROOT / "data" / "processed" / "mainnet" / "aave_uniswap_snapshot_26045352.json"
)

REQUIRED_ARTIFACT_FIELDS = {
    "id",
    "mode",
    "chain_id",
    "block_number",
    "block_hash",
    "block_timestamp",
    "retrieved_at",
    "borrowers",
    "coverage",
    "dex_pool",
    "oracle_prices",
    "source_manifest",
    "data_quality_flags",
}


def validate_mainnet_artifact(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Mainnet snapshot artifact must be a JSON object")
    missing = sorted(REQUIRED_ARTIFACT_FIELDS.difference(payload))
    if missing:
        raise ValueError(f"Mainnet snapshot artifact is missing required fields: {missing}")
    if payload["mode"] not in {"REAL_MAINNET", "CACHED_MAINNET"}:
        raise ValueError("Mainnet artifact mode must be REAL_MAINNET or CACHED_MAINNET")
    if payload["chain_id"] != 1:
        raise ValueError("Mainnet artifact chain_id must be 1")
    if isinstance(payload["block_number"], bool) or not isinstance(payload["block_number"], int):
        raise ValueError("Mainnet artifact block_number must be an integer")
    if payload["block_number"] <= 0:
        raise ValueError("Mainnet artifact block_number must be positive")
    if not isinstance(payload["block_hash"], str) or len(payload["block_hash"].removeprefix("0x")) != 64:
        raise ValueError("Mainnet artifact block_hash must be a 32-byte hexadecimal value")
    try:
        int(payload["block_hash"].removeprefix("0x"), 16)
    except ValueError as exc:
        raise ValueError("Mainnet artifact block_hash must be hexadecimal") from exc
    for field in ("borrowers", "data_quality_flags"):
        if not isinstance(payload[field], list):
            raise ValueError(f"Mainnet artifact {field} must be a list")
    for field in ("coverage", "dex_pool", "oracle_prices", "source_manifest"):
        if not isinstance(payload[field], dict):
            raise ValueError(f"Mainnet artifact {field} must be an object")
    if not payload["borrowers"]:
        raise ValueError("Mainnet artifact must contain at least one verified borrower")
    return payload


def load_mainnet_artifact(path: Path = DEFAULT_MAINNET_ARTIFACT) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError("The approved Mainnet snapshot artifact is unavailable")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("The approved Mainnet snapshot artifact is malformed") from exc
    return validate_mainnet_artifact(payload)


def snapshot_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = snapshot.get("coverage", {})
    pool = snapshot.get("dex_pool", {})
    return {
        "id": snapshot["id"],
        "mode": snapshot["mode"],
        "label": snapshot.get("label", snapshot["mode"]),
        "chain_id": snapshot["chain_id"],
        "block_number": snapshot["block_number"],
        "block_hash": snapshot["block_hash"],
        "block_timestamp": snapshot["block_timestamp"],
        "retrieved_at": snapshot.get("retrieved_at"),
        "coverage": {
            key: coverage.get(key)
            for key in (
                "candidates_discovered",
                "positions_loaded",
                "active_borrowers",
                "weth_collateral_borrowers",
                "usdc_borrowers",
                "weth_usdc_cohort",
                "failed_reads",
                "coverage_pct",
            )
            if key in coverage
        },
        "selected_uniswap_pool": {
            key: pool.get(key) for key in ("pool_address", "fee") if key in pool
        },
        "quality_flag_count": len(snapshot.get("data_quality_flags", [])),
    }


def import_approved_mainnet_artifact(repository: Repository) -> tuple[dict[str, Any], bool]:
    payload = load_mainnet_artifact()
    already_loaded = repository.get_snapshot(str(payload["id"])) is not None
    stored = repository.save_snapshot(payload)
    return stored, not already_loaded


def mainnet_artifact_status(repository: Repository) -> dict[str, Any]:
    if not DEFAULT_MAINNET_ARTIFACT.is_file():
        return {"available": False, "loaded": False, "snapshot_id": None}
    try:
        payload = load_mainnet_artifact()
    except ValueError:
        return {"available": False, "loaded": False, "snapshot_id": None}
    snapshot_id = str(payload["id"])
    return {
        "available": True,
        "loaded": repository.get_snapshot(snapshot_id) is not None,
        "snapshot_id": snapshot_id,
        "block_number": int(payload["block_number"]),
    }
