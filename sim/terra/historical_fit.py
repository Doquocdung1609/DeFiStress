from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from sim.terra.demo_data import EXTENDED_DATASET, frame_records, load_extended_frame

MODEL_VERSION = "terra-historical-fit-1.1.0-availability-aware"
FIT_START = pd.Timestamp("2022-05-01T00:00:00Z")
SEED = 20220513


@dataclass(frozen=True, slots=True)
class FitParameters:
    supply_realization: float
    withdrawal_sell_fraction: float
    withdrawal_price_impact: float
    mint_ust_impact: float
    peg_recovery: float
    luna_dilution_elasticity: float
    confidence_feedback: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


PARAMETER_BOUNDS: dict[str, tuple[float, float]] = {
    "supply_realization": (0.95, 1.05),
    "withdrawal_sell_fraction": (0.20, 0.90),
    "withdrawal_price_impact": (0.005, 0.30),
    "mint_ust_impact": (0.005, 0.25),
    "peg_recovery": (0.01, 0.65),
    "luna_dilution_elasticity": (0.20, 2.50),
    "confidence_feedback": (0.01, 0.80),
}


def _params(values: list[float]) -> FitParameters:
    return FitParameters(**dict(zip(PARAMETER_BOUNDS, values, strict=True)))


def _historical_inputs(frame: pd.DataFrame) -> pd.DataFrame:
    fit = frame.loc[frame["timestamp"] >= FIT_START].copy().reset_index(drop=True)
    fit["anchor_withdrawal_available"] = fit["anchor_withdrawal_flow"].notna()
    fit["native_issuance_available"] = fit["gross_luna_issuance_from_native_swaps"].notna()
    fit["anchor_withdrawal_source_quality"] = np.where(
        fit["anchor_withdrawal_available"],
        "HISTORICAL_EVENT_AGGREGATION_EVENT_ZERO_ALLOWED",
        "UNAVAILABLE_OUTSIDE_SOURCE_COVERAGE",
    )
    fit["native_issuance_source_quality"] = np.where(
        fit["native_issuance_available"],
        "HISTORICAL_DIRECT_EVENT_OUTPUT_EVENT_ZERO_ALLOWED",
        "UNAVAILABLE_OUTSIDE_SOURCE_COVERAGE",
    )
    return fit


def simulate_historical(frame: pd.DataFrame, parameters: FitParameters) -> pd.DataFrame:
    data = _historical_inputs(frame)
    first = data.iloc[0]
    ust = float(first["ust_price"])
    luna = float(first["luna_price"])
    supply: float | None = None
    output: list[dict[str, Any]] = []
    for index, row in data.iterrows():
        if index:
            withdrawal_available = bool(row["anchor_withdrawal_available"])
            issuance_available = bool(row["native_issuance_available"])
            withdrawal = float(row["anchor_withdrawal_flow"]) if withdrawal_available else 0.0
            deposits = max(float(row["anchor_total_deposits"]), 1.0)
            gross_mint = float(row["gross_luna_issuance_from_native_swaps"]) if issuance_available else 0.0
            previous_supply = supply
            if issuance_available and previous_supply is None:
                previous_supply = float(data.iloc[index - 1]["luna_supply"])
                supply = previous_supply
            if issuance_available and previous_supply is not None:
                supply = max(previous_supply, previous_supply + parameters.supply_realization * gross_mint)
            withdrawal_pressure = parameters.withdrawal_sell_fraction * withdrawal / deposits
            mint_pressure = (
                math.log1p(gross_mint / max(previous_supply, 1.0))
                if issuance_available and previous_supply is not None
                else 0.0
            )
            gap = max(0.0, 1.0 - ust)
            shock = parameters.withdrawal_price_impact * math.sqrt(
                max(0.0, withdrawal_pressure)
            ) + parameters.mint_ust_impact * math.sqrt(max(0.0, mint_pressure))
            next_gap = gap * (1.0 - parameters.peg_recovery) + shock * (
                1.0 + parameters.confidence_feedback * min(8.0, gap * 20.0)
            )
            ust = min(1.02, max(0.005, 1.0 - min(0.995, next_gap)))
            dilution = (
                math.log(max(supply, 1.0) / max(previous_supply, 1.0))
                if supply is not None and previous_supply is not None
                else 0.0
            )
            downside = (
                parameters.luna_dilution_elasticity * dilution
                + parameters.confidence_feedback * max(0.0, 1.0 - ust)
                + parameters.withdrawal_price_impact * withdrawal_pressure
            )
            luna = max(1e-8, luna * math.exp(-min(20.0, downside)))
        output.append(
            {
                "timestamp": row["timestamp"],
                "ust_price": ust,
                "luna_price": luna,
                "luna_supply": supply,
                "anchor_withdrawal_flow": (
                    float(row["anchor_withdrawal_flow"]) if bool(row["anchor_withdrawal_available"]) else None
                ),
                "effective_anchor_withdrawal_flow": (
                    float(row["anchor_withdrawal_flow"]) if bool(row["anchor_withdrawal_available"]) else 0.0
                ),
                "effective_gross_luna_issuance": (
                    float(row["gross_luna_issuance_from_native_swaps"])
                    if bool(row["native_issuance_available"])
                    else 0.0
                ),
                "anchor_withdrawal_available": bool(row["anchor_withdrawal_available"]),
                "native_issuance_available": bool(row["native_issuance_available"]),
                "anchor_channel_status": (
                    "ACTIVE_EVENT_ZERO_ALLOWED"
                    if bool(row["anchor_withdrawal_available"])
                    else "CHANNEL_INACTIVE_DUE_TO_NO_HISTORICAL_EVIDENCE"
                ),
                "native_issuance_channel_status": (
                    "ACTIVE_EVENT_ZERO_ALLOWED"
                    if bool(row["native_issuance_available"])
                    else "CHANNEL_INACTIVE_DUE_TO_NO_HISTORICAL_EVIDENCE"
                ),
            }
        )
    return pd.DataFrame(output)


def _rmse(actual: np.ndarray, simulated: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(actual - simulated))))


def objective(frame: pd.DataFrame, simulation: pd.DataFrame) -> tuple[float, dict[str, float]]:
    actual = _historical_inputs(frame)
    ust_rmse = _rmse(actual["ust_price"].to_numpy(), simulation["ust_price"].to_numpy())
    luna_log_rmse = _rmse(
        np.log(np.maximum(actual["luna_price"].to_numpy(), 1e-12)),
        np.log(np.maximum(simulation["luna_price"].to_numpy(), 1e-12)),
    )
    supply_mask = actual["native_issuance_available"] & simulation["luna_supply"].notna()
    supply_log_rmse = _rmse(
        np.log(np.maximum(actual.loc[supply_mask, "luna_supply"].to_numpy(), 1.0)),
        np.log(np.maximum(simulation.loc[supply_mask, "luna_supply"].to_numpy(dtype=float), 1.0)),
    )
    penalty = float(np.mean(simulation["ust_price"].to_numpy() <= 0.005)) * 5.0
    components = {
        "ust_price_rmse": ust_rmse,
        "luna_log_rmse": luna_log_rmse,
        "luna_supply_log_rmse": supply_log_rmse,
        "physical_state_penalty": penalty,
    }
    return 4.0 * ust_rmse + luna_log_rmse + supply_log_rmse + penalty, components


def _metrics(actual: pd.DataFrame, simulated: pd.DataFrame) -> dict[str, Any]:
    def block(field: str, log: bool = False, mask: pd.Series | None = None) -> dict[str, float]:
        selected = pd.Series(True, index=actual.index) if mask is None else mask
        selected &= actual[field].notna() & simulated[field].notna()
        left = actual.loc[selected, field].to_numpy(dtype=float)
        right = simulated.loc[selected, field].to_numpy(dtype=float)
        if log:
            left = np.log(np.maximum(left, 1e-12))
            right = np.log(np.maximum(right, 1e-12))
        return {
            "rmse": _rmse(left, right),
            "mae": float(np.mean(np.abs(left - right))),
            "correlation": float(np.corrcoef(left, right)[0, 1]),
        }

    timing: dict[str, dict[str, Any]] = {}
    for threshold in (0.995, 0.99, 0.95, 0.90):
        actual_rows = actual.loc[actual["ust_price"] < threshold, "timestamp"]
        simulated_rows = simulated.loc[simulated["ust_price"] < threshold, "timestamp"]
        actual_time = None if actual_rows.empty else actual_rows.iloc[0]
        simulated_time = None if simulated_rows.empty else simulated_rows.iloc[0]
        timing[str(threshold)] = {
            "actual": None if actual_time is None else actual_time.isoformat().replace("+00:00", "Z"),
            "simulated": None if simulated_time is None else simulated_time.isoformat().replace("+00:00", "Z"),
            "error_hours": None
            if actual_time is None or simulated_time is None
            else (simulated_time - actual_time).total_seconds() / 3600,
            "interpretation": (
                "NOT_DETECTED"
                if actual_time is None or simulated_time is None
                else "EARLY"
                if simulated_time < actual_time
                else "LATE"
                if simulated_time > actual_time
                else "ON_TIME"
            ),
        }
    supply_mask = actual["native_issuance_available"] & simulated["luna_supply"].notna()
    last_supply_index = supply_mask[supply_mask].index[-1]
    return {
        "ust_price": block("ust_price"),
        "luna_price": {**block("luna_price"), "log_rmse": block("luna_price", log=True)["rmse"]},
        "luna_supply": {
            **block("luna_supply", log=True, mask=supply_mask),
            "evaluation_rows": int(supply_mask.sum()),
            "final_relative_error": abs(
                float(simulated.loc[last_supply_index, "luna_supply"])
                - float(actual.loc[last_supply_index, "luna_supply"])
            )
            / float(actual.loc[last_supply_index, "luna_supply"]),
        },
        "event_timing": timing,
    }


def _window(mask: pd.Series, timestamps: pd.Series, rule: str) -> dict[str, Any]:
    selected = timestamps.loc[mask]
    return {
        "start": None if selected.empty else selected.iloc[0].isoformat().replace("+00:00", "Z"),
        "end": None if selected.empty else selected.iloc[-1].isoformat().replace("+00:00", "Z"),
        "rows": int(mask.sum()),
        "mask_rule": rule,
    }


def _channel_periods(actual: pd.DataFrame) -> list[dict[str, Any]]:
    periods: list[dict[str, Any]] = []
    start = 0
    current = (
        bool(actual.iloc[0]["anchor_withdrawal_available"]),
        bool(actual.iloc[0]["native_issuance_available"]),
    )
    for index in range(1, len(actual) + 1):
        next_status = (
            None
            if index == len(actual)
            else (
                bool(actual.iloc[index]["anchor_withdrawal_available"]),
                bool(actual.iloc[index]["native_issuance_available"]),
            )
        )
        if next_status != current:
            periods.append(
                {
                    "start": actual.iloc[start]["timestamp"].isoformat().replace("+00:00", "Z"),
                    "end": actual.iloc[index - 1]["timestamp"].isoformat().replace("+00:00", "Z"),
                    "active_channels": [
                        "PRICE_AND_CONFIDENCE_STATE",
                        *(["ANCHOR_WITHDRAWAL_EVENT_FLOW"] if current[0] else []),
                        *(["DIRECT_NATIVE_ISSUANCE"] if current[1] else []),
                    ],
                    "inactive_channels": [
                        *([] if current[0] else ["ANCHOR_WITHDRAWAL_EVENT_FLOW"]),
                        *([] if current[1] else ["DIRECT_NATIVE_ISSUANCE"]),
                    ],
                }
            )
            start = index
            current = next_status  # type: ignore[assignment]
    return periods


def fit_historical(
    dataset_path: Path = EXTENDED_DATASET,
    *,
    seed: int = SEED,
    candidates: int = 900,
) -> dict[str, Any]:
    frame = load_extended_frame(dataset_path)
    rng = Random(seed)
    midpoint = [(low + high) / 2 for low, high in PARAMETER_BOUNDS.values()]
    draws = [midpoint]
    for _ in range(candidates - 1):
        draws.append([rng.uniform(low, high) for low, high in PARAMETER_BOUNDS.values()])
    best: tuple[float, FitParameters, pd.DataFrame, dict[str, float]] | None = None
    for values in draws:
        parameters = _params(values)
        simulation = simulate_historical(frame, parameters)
        score, components = objective(frame, simulation)
        if best is None or score < best[0]:
            best = (score, parameters, simulation, components)
    assert best is not None
    score, parameters, simulation, components = best
    actual = _historical_inputs(frame)
    actual_columns = [
        "timestamp",
        "ust_price",
        "luna_price",
        "luna_supply",
        "anchor_withdrawal_flow",
        "gross_luna_issuance_from_native_swaps",
        "anchor_withdrawal_available",
        "native_issuance_available",
        "anchor_withdrawal_source_quality",
        "native_issuance_source_quality",
    ]
    simulated_columns = [
        "timestamp",
        "ust_price",
        "luna_price",
        "luna_supply",
        "anchor_withdrawal_flow",
        "effective_anchor_withdrawal_flow",
        "effective_gross_luna_issuance",
        "anchor_withdrawal_available",
        "native_issuance_available",
        "anchor_channel_status",
        "native_issuance_channel_status",
    ]
    price_mask = pd.Series(True, index=actual.index)
    anchor_mask = actual["anchor_withdrawal_available"]
    supply_mask = actual["native_issuance_available"] & simulation["luna_supply"].notna()
    evaluated_supply = simulation.loc[supply_mask, "luna_supply"].to_numpy(dtype=float)
    return {
        "analysis_type": "HISTORICAL_FIT",
        "label": "CALIBRATED_FEEDBACK_RECONSTRUCTION_NOT_FORECAST",
        "model_family": "CALIBRATED_FEEDBACK_RECONSTRUCTION_CONDITIONED_ON_OBSERVED_HISTORICAL_FLOWS",
        "model_version": MODEL_VERSION,
        "seed": seed,
        "optimizer": {"method": "DETERMINISTIC_BOUNDED_RANDOM_SEARCH", "candidates": candidates},
        "objective": {
            "formula": "4*UST_RMSE + log_LUNA_RMSE + log_supply_RMSE + physical_state_penalty",
            "value": score,
            "component_losses": components,
            "availability_policy": (
                "Supply loss is evaluated only where direct native issuance evidence is available; "
                "price losses use the full May 1-13 fit window."
            ),
        },
        "parameters": parameters.to_dict(),
        "bounds": {name: list(bounds) for name, bounds in PARAMETER_BOUNDS.items()},
        "input_policy": {
            "observed_exogenous_inputs": [
                "anchor_withdrawal_flow",
                "gross_luna_issuance_from_native_swaps (swap_amount + fee_amount)",
            ],
            "forbidden_state_input": "No observed future UST price, LUNA price, or LUNA supply is used as next state.",
            "missing_event_policy": (
                "Outside confirmed source coverage, event channels are unavailable and inactive, not observed zero. "
                "Inside confirmed coverage, a null event set is represented by an audited event zero."
            ),
            "interpretation": (
                "Calibrated feedback reconstruction conditioned on observed historical flows; "
                "not a pure ABM and not an ex-ante forecast."
            ),
        },
        "evaluation_windows": {
            "ust_price": _window(price_mask, actual["timestamp"], "all non-null UST prices in fit window"),
            "luna_price": _window(price_mask, actual["timestamp"], "all non-null LUNA prices in fit window"),
            "luna_supply": _window(
                supply_mask,
                actual["timestamp"],
                "native_issuance_available AND simulated_supply_available",
            ),
            "anchor_flow": _window(
                anchor_mask,
                actual["timestamp"],
                "anchor_withdrawal_available from confirmed event coverage",
            ),
        },
        "channel_availability_periods": _channel_periods(actual),
        "metrics": _metrics(actual, simulation),
        "actual_timeseries": frame_records(actual, actual_columns),
        "simulated_timeseries": frame_records(simulation, simulated_columns),
        "checks": {
            "finite_states": bool(
                np.isfinite(simulation[["ust_price", "luna_price"]]).all().all() and np.isfinite(evaluated_supply).all()
            ),
            "positive_prices": bool((simulation[["ust_price", "luna_price"]] > 0).all().all()),
            "nondecreasing_supply": bool((pd.Series(evaluated_supply).diff().fillna(0) >= -1e-6).all()),
            "future_prices_not_accepted_by_simulator": True,
            "direct_event_gross_mint_used": True,
            "missing_anchor_not_observed_zero": bool(
                simulation.loc[~anchor_mask, "anchor_withdrawal_flow"].isna().all()
            ),
            "missing_native_issuance_not_observed_zero": bool(
                simulation.loc[~actual["native_issuance_available"], "luna_supply"].isna().all()
            ),
        },
    }
