from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from sim.terra.demo_data import EXTENDED_DATASET, frame_records, load_extended_frame

MODEL_VERSION = "terra-historical-fit-1.0.0"
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
    fit["anchor_withdrawal_flow"] = fit["anchor_withdrawal_flow"].fillna(0.0).clip(lower=0.0)
    fit["gross_luna_issuance_from_native_swaps"] = (
        fit["gross_luna_issuance_from_native_swaps"].fillna(0.0).clip(lower=0.0)
    )
    return fit


def simulate_historical(frame: pd.DataFrame, parameters: FitParameters) -> pd.DataFrame:
    data = _historical_inputs(frame)
    first = data.iloc[0]
    ust = float(first["ust_price"])
    luna = float(first["luna_price"])
    supply = float(first["luna_supply"])
    output: list[dict[str, Any]] = []
    for index, row in data.iterrows():
        if index:
            withdrawal = float(row["anchor_withdrawal_flow"])
            deposits = max(float(row["anchor_total_deposits"]), 1.0)
            gross_mint = float(row["gross_luna_issuance_from_native_swaps"])
            previous_supply = supply
            supply = max(previous_supply, previous_supply + parameters.supply_realization * gross_mint)
            withdrawal_pressure = parameters.withdrawal_sell_fraction * withdrawal / deposits
            mint_pressure = math.log1p(gross_mint / max(previous_supply, 1.0))
            gap = max(0.0, 1.0 - ust)
            shock = parameters.withdrawal_price_impact * math.sqrt(
                max(0.0, withdrawal_pressure)
            ) + parameters.mint_ust_impact * math.sqrt(max(0.0, mint_pressure))
            next_gap = gap * (1.0 - parameters.peg_recovery) + shock * (
                1.0 + parameters.confidence_feedback * min(8.0, gap * 20.0)
            )
            ust = min(1.02, max(0.005, 1.0 - min(0.995, next_gap)))
            dilution = math.log(max(supply, 1.0) / max(previous_supply, 1.0))
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
                "anchor_withdrawal_flow": float(row["anchor_withdrawal_flow"]),
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
    supply_log_rmse = _rmse(
        np.log(np.maximum(actual["luna_supply"].to_numpy(), 1.0)),
        np.log(np.maximum(simulation["luna_supply"].to_numpy(), 1.0)),
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
    def block(field: str, log: bool = False) -> dict[str, float]:
        left = actual[field].to_numpy(dtype=float)
        right = simulated[field].to_numpy(dtype=float)
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
        }
    return {
        "ust_price": block("ust_price"),
        "luna_price": {**block("luna_price"), "log_rmse": block("luna_price", log=True)["rmse"]},
        "luna_supply": {
            **block("luna_supply", log=True),
            "final_relative_error": abs(
                float(simulated["luna_supply"].iloc[-1]) - float(actual["luna_supply"].iloc[-1])
            )
            / float(actual["luna_supply"].iloc[-1]),
        },
        "event_timing": timing,
    }


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
    columns = ["timestamp", "ust_price", "luna_price", "luna_supply", "anchor_withdrawal_flow"]
    return {
        "analysis_type": "HISTORICAL_FIT",
        "label": "CALIBRATED_HISTORICAL_RECONSTRUCTION_NOT_FORECAST",
        "model_version": MODEL_VERSION,
        "seed": seed,
        "optimizer": {"method": "DETERMINISTIC_BOUNDED_RANDOM_SEARCH", "candidates": candidates},
        "objective": {
            "formula": "4*UST_RMSE + log_LUNA_RMSE + log_supply_RMSE + physical_state_penalty",
            "value": score,
            "component_losses": components,
        },
        "parameters": parameters.to_dict(),
        "bounds": {name: list(bounds) for name, bounds in PARAMETER_BOUNDS.items()},
        "input_policy": {
            "observed_exogenous_inputs": [
                "anchor_withdrawal_flow",
                "gross_luna_issuance_from_native_swaps (swap_amount + fee_amount)",
            ],
            "forbidden_state_input": "No observed future UST price, LUNA price, or LUNA supply is used as next state.",
            "interpretation": "In-sample historical reconstruction; not an ex-ante forecast.",
        },
        "metrics": _metrics(actual, simulation),
        "actual_timeseries": frame_records(actual, columns),
        "simulated_timeseries": frame_records(simulation, columns),
        "checks": {
            "finite_states": bool(np.isfinite(simulation[["ust_price", "luna_price", "luna_supply"]]).all().all()),
            "positive_prices": bool((simulation[["ust_price", "luna_price"]] > 0).all().all()),
            "nondecreasing_supply": bool((simulation["luna_supply"].diff().fillna(0) >= -1e-6).all()),
            "future_prices_not_accepted_by_simulator": True,
            "direct_event_gross_mint_used": True,
        },
    }
