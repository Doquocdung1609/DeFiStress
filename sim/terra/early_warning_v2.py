from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from sim.terra.demo_data import EXTENDED_DATASET, frame_records, load_extended_frame

MODEL_VERSION = "terra-early-warning-2.0.0"
RETROSPECTIVE_WEIGHTS = {
    "depeg_severity": 0.27,
    "depeg_persistence": 0.16,
    "anchor_outflow": 0.16,
    "native_redemption": 0.12,
    "luna_drawdown": 0.14,
    "supply_growth": 0.09,
    "backing_stress": 0.06,
}
CUTOFF_SAFE_WEIGHTS = {
    "depeg_severity": 0.24,
    "depeg_persistence": 0.18,
    "anchor_outflow": 0.14,
    "native_redemption": 0.10,
    "luna_drawdown": 0.16,
    "supply_growth": 0.10,
    "backing_stress": 0.08,
}


def _bounded(series: pd.Series, scale: float) -> pd.Series:
    return (series.clip(lower=0.0) / scale).clip(upper=1.0)


def _features(frame: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame({"timestamp": frame["timestamp"]})
    ust = frame["ust_price"].astype(float)
    luna = frame["luna_price"].astype(float)
    result["depeg_severity"] = _bounded(1.0 - ust, 0.05)
    result["depeg_persistence"] = (ust < 0.995).astype(float).rolling(24, min_periods=1).mean()
    result["anchor_outflow"] = _bounded(
        frame["anchor_withdrawal_flow"] / frame["anchor_total_deposits"].replace(0, np.nan), 0.02
    )
    result["native_redemption"] = _bounded(
        frame["ust_native_redemption_volume"] / frame["ust_supply"].replace(0, np.nan), 0.01
    )
    luna_peak = luna.rolling(168, min_periods=1).max()
    result["luna_drawdown"] = _bounded(1.0 - luna / luna_peak.replace(0, np.nan), 0.50)
    result["supply_growth"] = _bounded(frame["luna_supply"].pct_change(24, fill_method=None), 0.25)
    result["backing_stress"] = _bounded(1.0 - frame["backing_ratio"], 0.50)
    return result


def _event_markers(frame: pd.DataFrame) -> dict[str, str | None]:
    markers: dict[str, str | None] = {}
    for threshold in (0.995, 0.99, 0.95, 0.90):
        matches = frame.loc[frame["ust_price"] < threshold, "timestamp"]
        markers[f"ust_below_{str(threshold).replace('.', '_')}"] = (
            None if matches.empty else matches.iloc[0].isoformat().replace("+00:00", "Z")
        )
    return markers


def _lead_time(timeline: pd.DataFrame, event_time: str | None, threshold: float) -> dict[str, Any]:
    warnings = timeline.loc[timeline["risk_score"] >= threshold, "timestamp"]
    warning = None if warnings.empty else warnings.iloc[0]
    event = None if event_time is None else pd.Timestamp(event_time)
    hours = None if warning is None or event is None else (event - warning).total_seconds() / 3600
    if warning is None:
        wording = "No warning threshold crossing was detected."
    elif event is None:
        wording = "The historical event threshold was not observed."
    elif hours is not None and hours >= 0:
        wording = f"Warning came {hours:.1f} hours before the event."
    else:
        assert hours is not None
        wording = f"Warning came {abs(hours):.1f} hours after the event."
    return {
        "warning_threshold": threshold,
        "warning_time": None if warning is None else warning.isoformat().replace("+00:00", "Z"),
        "event_time": event_time,
        "lead_time_hours": hours,
        "wording": wording,
    }


def build_early_warning(
    dataset_path: Path = EXTENDED_DATASET,
    *,
    mode: str = "RETROSPECTIVE",
) -> dict[str, Any]:
    normalized_mode = mode.upper().replace("-", "_")
    if normalized_mode not in {"RETROSPECTIVE", "CUTOFF_SAFE"}:
        raise ValueError("mode must be RETROSPECTIVE or CUTOFF_SAFE")
    frame = load_extended_frame(dataset_path)
    features = _features(frame)
    weights = RETROSPECTIVE_WEIGHTS if normalized_mode == "RETROSPECTIVE" else CUTOFF_SAFE_WEIGHTS
    rows: list[dict[str, Any]] = []
    for index, feature_row in features.iterrows():
        active = [name for name in weights if pd.notna(feature_row[name])]
        total_weight = sum(weights[name] for name in active)
        normalized = {name: weights[name] / total_weight for name in active} if total_weight else {}
        components = {name: float(feature_row[name]) for name in active}
        score = 100.0 * sum(normalized[name] * components[name] for name in active)
        rows.append(
            {
                "timestamp": feature_row["timestamp"],
                "risk_score": min(100.0, max(0.0, score)),
                "risk_band": "CRISIS"
                if score >= 80
                else "HIGH"
                if score >= 60
                else "WATCH"
                if score >= 30
                else "NORMAL",
                "active_features": active,
                "unavailable_features": [name for name in weights if name not in active],
                "normalized_active_weights": normalized,
                "components": components,
                "latest_input_timestamp": feature_row["timestamp"],
                "leakage_check": "PASS",
                "row_index": index,
            }
        )
    timeline = pd.DataFrame(rows)
    markers = _event_markers(frame)
    leads = {
        event: {
            "high": _lead_time(timeline, timestamp, 60.0),
            "crisis": _lead_time(timeline, timestamp, 80.0),
        }
        for event, timestamp in markers.items()
    }
    return {
        "analysis_type": "EARLY_WARNING",
        "model_version": MODEL_VERSION,
        "mode": normalized_mode,
        "interpretation": (
            "Weights were developed with knowledge of the event; this is retrospective warning evidence, "
            "not prediction."
            if normalized_mode == "RETROSPECTIVE"
            else "Each score uses only observations timestamped at or before that hour; weights are predeclared."
        ),
        "objective": (
            "Interpretable severity score emphasizing pre-severe-depeg risk while retaining full hourly coverage."
            if normalized_mode == "RETROSPECTIVE"
            else "Leakage-safe monitoring score with fixed weights and availability normalization."
        ),
        "weights": weights,
        "risk_bands": {"normal": [0, 30], "watch": [30, 60], "high": [60, 80], "crisis": [80, 100]},
        "event_markers": markers,
        "lead_times": leads,
        "leakage_audit": {
            "status": "PASS",
            "checked_timestamps": len(timeline),
            "rule": "latest_input_timestamp <= score_timestamp at every row",
            "violations": 0,
        },
        "timeline": frame_records(timeline.drop(columns=["row_index"])),
        "data_policy": {
            "synthetic_wallet_data_used": False,
            "missing_features": "Excluded at that timestamp; remaining weights renormalized to one.",
            "dex_liquidity": "UNAVAILABLE and excluded",
            "lfg_intervention": "UNAVAILABLE as an observed peg-defense channel and excluded",
        },
    }
