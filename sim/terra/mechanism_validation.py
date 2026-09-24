from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from sim.terra.demo_data import EXTENDED_DATASET, NATIVE_SWAPS, load_extended_frame, sha256_file


def validate_native_mint_mechanism(
    dataset_path: Path = EXTENDED_DATASET,
    native_swaps_path: Path = NATIVE_SWAPS,
) -> dict[str, Any]:
    frame = load_extended_frame(dataset_path)
    swaps = pd.read_parquet(native_swaps_path)
    required = {"timestamp", "offer_amount", "swap_amount", "fee_amount"}
    if not required.issubset(swaps.columns):
        raise ValueError(f"native swap extract is missing {sorted(required.difference(swaps.columns))}")
    swaps["timestamp"] = pd.to_datetime(swaps["timestamp"], utc=True).dt.floor("h")
    hourly = swaps.groupby("timestamp")[["offer_amount", "swap_amount", "fee_amount"]].sum()
    window = frame.loc[frame["timestamp"] >= pd.Timestamp("2022-05-07T00:00:00Z")].copy()
    aligned = (
        window.set_index("timestamp")
        .join(hourly, how="left")
        .fillna({"offer_amount": 0.0, "swap_amount": 0.0, "fee_amount": 0.0})
    )
    actual_delta = aligned["luna_supply"].diff().fillna(0.0).to_numpy(dtype=float)
    direct = (aligned["swap_amount"] + aligned["fee_amount"]).to_numpy(dtype=float)
    old = (aligned["offer_amount"] / aligned["luna_price"].clip(lower=1e-12)).to_numpy(dtype=float)

    def compare(values: np.ndarray) -> dict[str, Any]:
        actual_total = float(actual_delta.sum())
        predicted_total = float(values.sum())
        return {
            "hourly_correlation": float(np.corrcoef(actual_delta, values)[0, 1]),
            "predicted_cumulative_luna": predicted_total,
            "observed_net_supply_change": actual_total,
            "final_cumulative_relative_error": abs(predicted_total - actual_total) / abs(actual_total),
        }

    return {
        "analysis_type": "PROTOCOL_MECHANISM_VALIDATION",
        "raw_swap_rows": len(swaps),
        "source_file": native_swaps_path.as_posix(),
        "source_sha256": sha256_file(native_swaps_path),
        "gross_mint_identity": "swap_amount + fee_amount",
        "old_offchain_approximation": compare(old),
        "direct_event_output_gross_mint": compare(direct),
        "interpretation": (
            "Direct event outputs strongly support the gross-mint accounting identity. Correlation with net supply "
            "change is mechanism validation, not proof that minting alone caused market prices."
        ),
        "limitations": [
            "The extract omits transaction hash, trader, denoms, and action fields.",
            "Gross issuance and observed net supply change are distinct accounting concepts.",
        ],
    }
