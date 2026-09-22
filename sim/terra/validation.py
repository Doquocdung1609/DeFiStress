from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import datetime
from statistics import mean
from typing import Any

from sim.terra.ground_truth import GroundTruthState
from sim.terra.schemas import ModelRun, ValidationResult


def mae(actual: Sequence[float], simulated: Sequence[float]) -> float:
    _same_length(actual, simulated)
    return mean(abs(left - right) for left, right in zip(actual, simulated, strict=True))


def rmse(actual: Sequence[float], simulated: Sequence[float]) -> float:
    _same_length(actual, simulated)
    return math.sqrt(mean((left - right) ** 2 for left, right in zip(actual, simulated, strict=True)))


def mape(actual: Sequence[float], simulated: Sequence[float]) -> float | None:
    _same_length(actual, simulated)
    rows = [abs((left - right) / left) for left, right in zip(actual, simulated, strict=True) if left != 0]
    return mean(rows) if rows else None


def smape(actual: Sequence[float], simulated: Sequence[float]) -> float:
    _same_length(actual, simulated)
    values = []
    for left, right in zip(actual, simulated, strict=True):
        denominator = abs(left) + abs(right)
        values.append(0.0 if denominator == 0 else 2 * abs(left - right) / denominator)
    return mean(values)


def correlation(actual: Sequence[float], simulated: Sequence[float]) -> float | None:
    _same_length(actual, simulated)
    if len(actual) < 2:
        return None
    actual_mean = mean(actual)
    simulated_mean = mean(simulated)
    numerator = sum(
        (left - actual_mean) * (right - simulated_mean) for left, right in zip(actual, simulated, strict=True)
    )
    denominator = math.sqrt(
        sum((item - actual_mean) ** 2 for item in actual) * sum((item - simulated_mean) ** 2 for item in simulated)
    )
    return None if denominator == 0 else numerator / denominator


def directional_accuracy(actual: Sequence[float], simulated: Sequence[float]) -> float | None:
    _same_length(actual, simulated)
    if len(actual) < 2:
        return None
    matches = 0
    for index in range(1, len(actual)):
        actual_direction = actual[index] - actual[index - 1]
        simulated_direction = simulated[index] - simulated[index - 1]
        matches += int(
            (actual_direction == 0 and simulated_direction == 0) or actual_direction * simulated_direction > 0
        )
    return matches / (len(actual) - 1)


def timing_error_hours(
    actual_times: Sequence[datetime],
    actual_values: Sequence[float],
    simulated_times: Sequence[datetime],
    simulated_values: Sequence[float],
    threshold: float,
) -> float | None:
    actual_event = next(
        (time for time, value in zip(actual_times, actual_values, strict=True) if value < threshold), None
    )
    simulated_event = next(
        (time for time, value in zip(simulated_times, simulated_values, strict=True) if value < threshold), None
    )
    if actual_event is None or simulated_event is None:
        return None
    return (simulated_event - actual_event).total_seconds() / 3600


def validate_model_run(
    run: ModelRun,
    ground_truth: GroundTruthState,
    event_thresholds: dict[str, float] | None = None,
) -> ValidationResult:
    thresholds = event_thresholds or {"minor": 0.99, "major": 0.95, "severe": 0.90}
    actual_by_time = {row.timestamp: row for row in ground_truth.observations}
    pairs = [(state, actual_by_time[state.timestamp]) for state in run.states if state.timestamp in actual_by_time]
    if not pairs:
        raise ValueError("simulation and ground truth have no aligned timestamps")
    simulated_times = [state.timestamp for state, _ in pairs]
    actual_times = [row.timestamp for _, row in pairs]

    fields = {
        "ust": ([float(row.ust_price) for _, row in pairs], [float(state.ust_price) for state, _ in pairs]),
        "luna": ([float(row.luna_price) for _, row in pairs], [float(state.luna_price) for state, _ in pairs]),
        "luna_supply": ([float(row.luna_supply) for _, row in pairs], [float(state.luna_supply) for state, _ in pairs]),
        "ust_supply": ([float(row.ust_supply) for _, row in pairs], [float(state.ust_supply) for state, _ in pairs]),
        "withdrawal": (
            [float(row.anchor_withdrawal_flow) for _, row in pairs],
            [float(state.anchor_withdrawal_flow) for state, _ in pairs],
        ),
        "dex_liquidity": (
            [float(row.terra_dex_liquidity) for _, row in pairs],
            [float(state.terra_dex_liquidity) for state, _ in pairs],
        ),
        "backing_ratio": (
            [float(row.backing_ratio) for _, row in pairs],
            [float(state.backing_ratio) for state, _ in pairs],
        ),
    }
    metrics: dict[str, float | int | bool | None] = {}
    for name, (actual, simulated) in fields.items():
        metrics[f"MAE_{name.upper()}"] = mae(actual, simulated)
        metrics[f"RMSE_{name.upper()}"] = rmse(actual, simulated)
        metrics[f"MAPE_{name.upper()}"] = mape(actual, simulated)
        metrics[f"SMAPE_{name.upper()}"] = smape(actual, simulated)
        metrics[f"CORRELATION_{name.upper()}"] = correlation(actual, simulated)
    actual_ust, simulated_ust = fields["ust"]
    metrics["directional_accuracy_UST"] = directional_accuracy(actual_ust, simulated_ust)
    metrics["depeg_start_timing_error_hours"] = timing_error_hours(
        actual_times, actual_ust, simulated_times, simulated_ust, thresholds["minor"]
    )
    metrics["major_depeg_timing_error_hours"] = timing_error_hours(
        actual_times, actual_ust, simulated_times, simulated_ust, thresholds["major"]
    )
    metrics["death_spiral_timing_error_hours"] = timing_error_hours(
        actual_times, actual_ust, simulated_times, simulated_ust, thresholds["severe"]
    )
    actual_min_time = actual_times[min(range(len(actual_ust)), key=actual_ust.__getitem__)]
    simulated_min_time = simulated_times[min(range(len(simulated_ust)), key=simulated_ust.__getitem__)]
    metrics["max_drawdown_timing_error_hours"] = (simulated_min_time - actual_min_time).total_seconds() / 3600
    actual_supply = fields["luna_supply"][0][-1]
    simulated_supply = fields["luna_supply"][1][-1]
    metrics["LUNA_supply_relative_error"] = (
        None if actual_supply == 0 else abs(simulated_supply - actual_supply) / actual_supply
    )
    actual_events = [value < thresholds["severe"] for value in actual_ust]
    simulated_events = [value < thresholds["severe"] for value in simulated_ust]
    tp = sum(a and s for a, s in zip(actual_events, simulated_events, strict=True))
    fp = sum((not a) and s for a, s in zip(actual_events, simulated_events, strict=True))
    fn = sum(a and (not s) for a, s in zip(actual_events, simulated_events, strict=True))
    tn = len(actual_events) - tp - fp - fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    metrics.update(
        {
            "precision": precision,
            "recall": recall,
            "F1": 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall),
            "false_positive_rate": fp / (fp + tn) if fp + tn else 0.0,
            "false_negative_rate": fn / (fn + tp) if fn + tp else 0.0,
            "collapse_detected": any(simulated_events),
            "false_alarms": fp,
            "aligned_observations": len(pairs),
        }
    )
    warnings = (
        ("FIXTURE metrics are software-validation evidence only, not historical empirical results.",)
        if any(row.quality_flag == "FIXTURE" for _, row in pairs)
        else ()
    )
    return ValidationResult(run.model_name, metrics, warnings)


def benchmark_row(validation: ValidationResult, runtime_seconds: float) -> dict[str, Any]:
    metrics = validation.metrics
    return {
        "model": validation.model_name,
        "MAE_UST": metrics["MAE_UST"],
        "RMSE_UST": metrics["RMSE_UST"],
        "MAE_LUNA": metrics["MAE_LUNA"],
        "RMSE_LUNA": metrics["RMSE_LUNA"],
        "supply_error": metrics["LUNA_supply_relative_error"],
        "withdrawal_error": metrics["RMSE_WITHDRAWAL"],
        "depeg_timing_error": metrics["major_depeg_timing_error_hours"],
        "death_spiral_timing_error": metrics["death_spiral_timing_error_hours"],
        "collapse_detected": metrics["collapse_detected"],
        "false_alarms": metrics["false_alarms"],
        "runtime_seconds": runtime_seconds,
    }


def _same_length(left: Sequence[float], right: Sequence[float]) -> None:
    if not left or len(left) != len(right):
        raise ValueError("metric inputs must be non-empty and have equal length")
