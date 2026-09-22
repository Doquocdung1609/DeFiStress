from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path
from typing import Any

from sim.terra.datasets import DatasetManifest, ResearchDataset, dataset_hash, quality_report
from sim.terra.schemas import DataStatus, TerraObservation

REQUIRED_COLUMNS = {
    "timestamp",
    "block_height",
    "ust_price",
    "luna_price",
    "ust_supply",
    "luna_supply",
    "anchor_total_deposits",
    "anchor_deposit_flow",
    "anchor_withdrawal_flow",
    "ust_native_redemption_volume",
    "luna_minted_from_redemption",
    "luna_burned",
    "ust_dex_sell_volume",
    "terra_dex_liquidity",
    "terra_dex_depth",
    "top10_anchor_share",
    "top100_anchor_share",
}


def import_research_dataset(
    path: Path,
    dataset_version: str,
    status: DataStatus,
    source_name: str,
    source_type: str,
    chain_id: str = "columbus-5",
    raw_reference: str | None = None,
) -> ResearchDataset:
    rows = _load_rows(path)
    return dataset_from_rows(
        rows,
        dataset_version,
        status,
        source_name,
        source_type,
        chain_id,
        raw_reference or str(path.resolve()),
    )


def dataset_from_rows(
    rows: list[dict[str, Any]],
    dataset_version: str,
    status: DataStatus,
    source_name: str,
    source_type: str,
    chain_id: str,
    raw_reference: str,
) -> ResearchDataset:
    if not rows:
        raise ValueError("dataset contains no observations")
    missing = REQUIRED_COLUMNS - set(rows[0])
    if missing:
        raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
    observations = []
    for raw in rows:
        enriched = {
            **raw,
            "source_name": raw.get("source_name") or source_name,
            "source_type": raw.get("source_type") or source_type,
            "chain_id": raw.get("chain_id") or chain_id,
            "raw_reference": raw.get("raw_reference") or raw_reference,
            "quality_flag": raw.get("quality_flag") or status.value,
        }
        observations.append(TerraObservation.from_mapping(enriched))
    ordered = tuple(sorted(observations, key=lambda row: row.timestamp))
    report = quality_report(ordered)
    if report["duplicate_timestamps"]:
        raise ValueError("duplicate timestamps are not allowed")
    if report["negative_supply_rows"]:
        raise ValueError("negative supply is impossible")
    manifest = DatasetManifest(
        dataset_version=dataset_version,
        status=status,
        row_count=len(ordered),
        start_timestamp=ordered[0].timestamp,
        end_timestamp=ordered[-1].timestamp,
        dataset_hash=dataset_hash(ordered),
        source_manifest={
            "primary": {
                "source": source_name,
                "source_type": source_type,
                "chain": chain_id,
                "raw_reference": raw_reference,
                "historical_evidence": status == DataStatus.REAL_HISTORICAL,
            }
        },
        quality_report=report,
        transformation_version="terra-importer-1",
        git_commit=_git_commit(),
    )
    return ResearchDataset(manifest, ordered)


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise ValueError(f"dataset file does not exist: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        rows = payload.get("observations", []) if isinstance(payload, dict) else payload
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("JSON must be an array of observation objects or contain an observations array")
        return rows
    if suffix in {".parquet", ".pq"}:
        try:
            import pandas as pd
        except ImportError as exc:
            raise ValueError("Parquet import requires pandas and a parquet engine such as pyarrow") from exc
        return list(pd.read_parquet(path).to_dict(orient="records"))
    raise ValueError("supported dataset formats are CSV, JSON, and Parquet")


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        return "UNCOMMITTED"
