from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd  # type: ignore[import-untyped]

EXTENDED_DATASET = Path("data/processed/terra_extended/terra_state_hourly_20220301_20220513.parquet")
NATIVE_SWAPS = Path("data/processed/terra_extended/terra_native_swaps.parquet")
PROVENANCE_MANIFEST = Path("data/processed/terra_extended/provenance_manifest.json")
DEMO_OUTPUT = Path("data/processed/terra_demo")
DEMO_VERSION = "terra-demo-1.0.0"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_extended_frame(path: Path = EXTENDED_DATASET) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"extended Terra dataset is missing: {path}")
    frame = pd.read_parquet(path).copy()
    required = {
        "timestamp",
        "block_height",
        "ust_price",
        "luna_price",
        "ust_supply",
        "luna_supply",
        "anchor_total_deposits",
        "anchor_withdrawal_flow",
        "ust_native_redemption_volume",
        "gross_luna_issuance_from_native_swaps",
        "backing_ratio",
    }
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"extended Terra dataset is missing columns: {missing}")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    if frame["timestamp"].duplicated().any():
        raise ValueError("extended Terra dataset contains duplicate timestamps")
    expected = pd.date_range(frame["timestamp"].iloc[0], frame["timestamp"].iloc[-1], freq="h")
    if len(expected) != len(frame) or not frame["timestamp"].equals(pd.Series(expected)):
        raise ValueError("extended Terra dataset is not a complete hourly index")
    return frame


def json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat().replace("+00:00", "Z")
    if hasattr(value, "item"):
        return value.item()
    return value


def frame_records(frame: pd.DataFrame, columns: list[str] | None = None) -> list[dict[str, Any]]:
    selected = frame if columns is None else frame[columns]
    return [{name: json_value(value) for name, value in row.items()} for row in selected.to_dict("records")]


def dataset_summary(path: Path = EXTENDED_DATASET) -> dict[str, Any]:
    frame = load_extended_frame(path)
    return {
        "dataset_version": "terra_extended_20220301_20220513_v1",
        "status": "READY_WITH_LIMITATIONS",
        "row_count": len(frame),
        "start_timestamp": json_value(frame["timestamp"].iloc[0]),
        "end_timestamp": json_value(frame["timestamp"].iloc[-1]),
        "sha256": sha256_file(path),
        "quality_classes": {
            "prices_march_april": "LOWER_FREQUENCY_STATE_CARRIED_FORWARD",
            "prices_may": "OBSERVED_MINUTE_OR_DAILY_COMPOSITE",
            "anchor_state": "OBSERVED_STATE",
            "anchor_event_flows": "OBSERVED_MAY_6_ONWARD_OTHERWISE_MISSING",
            "native_redemptions_and_issuance": "OBSERVED_MAY_7_ONWARD_OTHERWISE_MISSING",
            "luna_supply_and_backing": "OBSERVED_MAY_1_ONWARD_OTHERWISE_MISSING",
            "dex_liquidity": "UNAVAILABLE",
            "lfg_peg_defense": "UNAVAILABLE_AS_OBSERVED_CHANNEL",
        },
        "quarantined_variables": [
            "ust_dex_sell_volume",
            "luna_minted_from_redemption",
            "luna_burned",
            "bridge_outflow_terra_to_ethereum",
            "bridge_inflow_ethereum_to_terra",
            "curve_ust_price",
        ],
    }
