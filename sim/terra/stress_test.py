from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from sim.terra.demo_data import DEMO_OUTPUT, EXTENDED_DATASET, NATIVE_SWAPS, load_extended_frame
from sim.terra.historical_fit import FitParameters, fit_historical

MODEL_VERSION = "terra-stress-test-1.1.0-calibrated-counterfactual"
DEFAULT_SEED = 20220506
DEFAULT_STRESS_START = "2022-05-06T23:00:00Z"
CONVERSION_NAME = "COUNTERFACTUAL_REDEMPTION_TO_LUNA_APPROXIMATION"


@dataclass(frozen=True, slots=True)
class StressScenario:
    withdrawal_pressure: float = 1.0
    liquidity_capacity: float = 0.55
    arbitrage_capacity: float = 0.55
    confidence_sensitivity: float = 1.0
    outside_holder_exit: float = 0.004
    reserve_intervention: float = 0.0
    horizon_hours: int = 168
    initial_shock: float = 0.015
    redemption_friction: float = 0.02

    def validate(self) -> None:
        if self.horizon_hours < 1 or self.horizon_hours > 720:
            raise ValueError("horizon_hours must be between 1 and 720")
        for name, value in asdict(self).items():
            if name != "horizon_hours" and (not math.isfinite(float(value)) or float(value) < 0):
                raise ValueError(f"{name} must be finite and non-negative")


STRESS_PRESETS: dict[str, StressScenario] = {
    "BASELINE": StressScenario(),
    "ADVERSE": StressScenario(
        withdrawal_pressure=1.8,
        liquidity_capacity=0.35,
        arbitrage_capacity=0.35,
        confidence_sensitivity=1.4,
        outside_holder_exit=0.008,
        reserve_intervention=0.05,
        initial_shock=0.03,
    ),
    "SEVERE": StressScenario(
        withdrawal_pressure=3.0,
        liquidity_capacity=0.15,
        arbitrage_capacity=0.15,
        confidence_sensitivity=2.0,
        outside_holder_exit=0.02,
        reserve_intervention=0.0,
        initial_shock=0.06,
    ),
}


def _iso(value: pd.Timestamp) -> str:
    return str(value.isoformat()).replace("+00:00", "Z")


def _load_initial_state(dataset_path: Path, start_timestamp: str) -> dict[str, Any]:
    frame = load_extended_frame(dataset_path)
    selected = pd.Timestamp(start_timestamp)
    selected = selected.tz_localize("UTC") if selected.tzinfo is None else selected.tz_convert("UTC")
    rows = frame.loc[frame["timestamp"] == selected]
    if rows.empty:
        raise ValueError(f"stress start timestamp is not an exact dataset hour: {_iso(selected)}")
    row = rows.iloc[0]
    required = ["ust_price", "luna_price", "ust_supply", "luna_supply", "anchor_total_deposits"]
    missing = [name for name in required if pd.isna(row[name])]
    if missing:
        raise ValueError(f"stress initial state has unavailable required fields: {missing}")
    withdrawal = None if pd.isna(row["anchor_withdrawal_flow"]) else float(row["anchor_withdrawal_flow"])
    deposits = float(row["anchor_total_deposits"])
    return {
        "timestamp": _iso(selected),
        "block_height": int(row["block_height"]),
        "ust_price": float(row["ust_price"]),
        "luna_price": float(row["luna_price"]),
        "ust_supply": float(row["ust_supply"]),
        "luna_supply": float(row["luna_supply"]),
        "anchor_deposits": deposits,
        "outside_ust_stock": max(0.0, float(row["ust_supply"]) - deposits),
        "observed_anchor_withdrawal_flow": withdrawal,
        "base_hourly_withdrawal_rate": max(0.0001, 0.0 if withdrawal is None else withdrawal / max(deposits, 1.0)),
        "source": dataset_path.as_posix(),
        "source_quality": "OBSERVED_HOURLY_HISTORICAL_STATE",
    }


def _load_calibrated_parameters(parameters: FitParameters | None) -> FitParameters:
    if parameters is not None:
        return parameters
    artifact = DEMO_OUTPUT / "historical_fit.json"
    if artifact.exists():
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        return FitParameters(**payload["parameters"])
    payload = fit_historical(candidates=250)
    return FitParameters(**payload["parameters"])


def calibrate_counterfactual_conversion(
    dataset_path: Path = EXTENDED_DATASET,
    native_swaps_path: Path = NATIVE_SWAPS,
) -> dict[str, Any]:
    swaps = pd.read_parquet(
        native_swaps_path,
        columns=["timestamp", "offer_amount", "swap_amount", "fee_amount"],
    )
    swaps["timestamp"] = pd.to_datetime(swaps["timestamp"], utc=True).dt.floor("h")
    swaps["gross_luna_event_output"] = swaps["swap_amount"] + swaps["fee_amount"]
    hourly = swaps.groupby("timestamp", as_index=False).agg(
        offer_amount_ust=("offer_amount", "sum"),
        gross_luna_event_output=("gross_luna_event_output", "sum"),
    )
    prices = load_extended_frame(dataset_path)[["timestamp", "luna_price"]]
    aligned = hourly.merge(prices, on="timestamp", how="inner")
    aligned = aligned.loc[
        (aligned["timestamp"] >= pd.Timestamp("2022-05-07T00:00:00Z"))
        & (aligned["offer_amount_ust"] > 0)
        & (aligned["luna_price"] > 0)
    ].copy()
    aligned["price_implied_luna"] = aligned["offer_amount_ust"] / aligned["luna_price"]
    aligned["event_to_price_implied_ratio"] = (
        aligned["gross_luna_event_output"] / aligned["price_implied_luna"]
    )
    validation_start = pd.Timestamp("2022-05-11T00:00:00Z")
    training = aligned.loc[aligned["timestamp"] < validation_start]
    validation = aligned.loc[aligned["timestamp"] >= validation_start].copy()
    if training.empty or validation.empty:
        raise ValueError("native swap conversion calibration requires non-empty train and validation windows")
    multiplier = float(training["event_to_price_implied_ratio"].median())
    validation["predicted_gross_luna"] = validation["price_implied_luna"] * multiplier
    error = validation["predicted_gross_luna"] - validation["gross_luna_event_output"]
    actual = validation["gross_luna_event_output"].to_numpy(dtype=float)
    predicted = validation["predicted_gross_luna"].to_numpy(dtype=float)
    relative = np.abs(predicted - actual) / np.maximum(actual, 1e-12)
    return {
        "name": CONVERSION_NAME,
        "claim_boundary": (
            "Calibrated counterfactual conversion from simulated UST redemption demand to gross LUNA mint. "
            "It is an approximation fitted to historical native swap outputs, not a protocol accounting identity."
        ),
        "formula": "gross_luna_mint = redemption_ust / simulated_luna_price * calibration_multiplier",
        "calibration_multiplier": multiplier,
        "training_window": {
            "start": _iso(training["timestamp"].iloc[0]),
            "end": _iso(training["timestamp"].iloc[-1]),
            "aligned_hours": int(len(training)),
        },
        "validation_window": {
            "start": _iso(validation["timestamp"].iloc[0]),
            "end": _iso(validation["timestamp"].iloc[-1]),
            "aligned_hours": int(len(validation)),
        },
        "validation_metrics": {
            "mae_luna": float(np.mean(np.abs(error))),
            "bias_luna": float(np.mean(error)),
            "cumulative_relative_error": float(abs(predicted.sum() - actual.sum()) / max(actual.sum(), 1e-12)),
            "median_absolute_relative_error": float(np.median(relative)),
        },
        "limitations": [
            "Hourly market price is used as a conversion reference and does not reproduce every on-chain curve state.",
            "The multiplier is fixed before the validation window and is not re-estimated inside a stress path.",
            "No future observed issuance, price, withdrawal, liquidity, or reserve flow enters a simulated path.",
        ],
    }


def _parameter_mapping(parameters: FitParameters) -> dict[str, Any]:
    return {
        "frozen_historical_fit_parameters": parameters.to_dict(),
        "reused": {
            "withdrawal_sell_fraction": "Maps simulated Anchor withdrawals into UST sell pressure.",
            "withdrawal_price_impact": "Scales market impact from net UST sell pressure.",
            "mint_ust_impact": "Feeds simulated LUNA dilution pressure back into the UST gap.",
            "peg_recovery": "Scales recovery supplied by executable arbitrage.",
            "luna_dilution_elasticity": "Maps endogenous supply dilution into LUNA price pressure.",
            "confidence_feedback": "Amplifies endogenous confidence stress.",
        },
        "not_reused": {
            "supply_realization": (
                "Historical net-supply calibration is not treated as a future gross-mint identity; "
                "stress mint uses the separately calibrated counterfactual conversion."
            )
        },
    }


def _run(
    scenario: StressScenario,
    seed: int,
    initial: dict[str, Any],
    parameters: FitParameters,
    conversion_multiplier: float,
) -> dict[str, Any]:
    scenario.validate()
    rng = Random(seed)
    ust = max(0.005, float(initial["ust_price"]) - min(0.30, scenario.initial_shock))
    luna = float(initial["luna_price"])
    ust_supply = float(initial["ust_supply"])
    luna_supply = float(initial["luna_supply"])
    initial_luna_supply = luna_supply
    deposits = float(initial["anchor_deposits"])
    outside_stock = float(initial["outside_ust_stock"])
    base_withdrawal_rate = float(initial["base_hourly_withdrawal_rate"])
    rows: list[dict[str, float | int]] = []
    collapse_time: int | None = None
    max_withdrawal = 0.0
    for hour in range(scenario.horizon_hours):
        peg_gap = max(0.0, 1.0 - ust)
        confidence = peg_gap * scenario.confidence_sensitivity * (1.0 + parameters.confidence_feedback)
        withdrawal_rate = min(
            0.25,
            base_withdrawal_rate * scenario.withdrawal_pressure * (1.0 + 8.0 * confidence),
        )
        withdrawal = min(deposits, deposits * withdrawal_rate * rng.uniform(0.85, 1.15))
        outside_sell_rate = min(0.20, scenario.outside_holder_exit * (1.0 + 10.0 * confidence))
        outside_sell = min(outside_stock, outside_stock * outside_sell_rate * rng.uniform(0.90, 1.10))
        gross_sell = withdrawal * parameters.withdrawal_sell_fraction + outside_sell
        reserve_support = min(gross_sell, gross_sell * min(1.0, scenario.reserve_intervention))
        arbitrage_limit = scenario.arbitrage_capacity * float(initial["ust_supply"]) * 0.01
        executable_arb = min(
            max(0.0, gross_sell - reserve_support),
            arbitrage_limit * max(0.0, 1.0 - 0.2 * confidence),
        )
        net_sell = max(0.0, gross_sell - reserve_support - executable_arb)
        depth = max(1_000_000.0, scenario.liquidity_capacity * float(initial["ust_supply"]) * 0.05)
        market_impact = min(0.65, parameters.withdrawal_price_impact * math.sqrt(net_sell / depth))
        redemption = executable_arb if peg_gap > scenario.redemption_friction else 0.0
        minted_luna = redemption / max(luna, 1e-8) * conversion_multiplier
        previous_luna_supply = luna_supply
        luna_supply += minted_luna
        ust_supply = max(0.0, ust_supply - redemption)
        dilution = math.log(max(luna_supply, 1.0) / max(previous_luna_supply, 1.0))
        mint_pressure = math.log1p(minted_luna / max(previous_luna_supply, 1.0))
        recovery = parameters.peg_recovery * peg_gap * (
            executable_arb / max(gross_sell, 1.0)
        )
        next_gap = peg_gap + market_impact + parameters.mint_ust_impact * math.sqrt(mint_pressure) - recovery
        ust = min(1.01, max(0.005, 1.0 - min(0.995, next_gap)))
        luna_downside = (
            parameters.luna_dilution_elasticity * dilution
            + parameters.confidence_feedback * confidence
            + parameters.withdrawal_price_impact * market_impact
        )
        luna = max(1e-8, luna * math.exp(-min(20.0, luna_downside)))
        deposits = max(0.0, deposits - withdrawal)
        outside_stock = max(0.0, outside_stock - outside_sell - redemption)
        max_withdrawal = max(max_withdrawal, withdrawal)
        collapsed = ust < 0.90 and luna_supply > initial_luna_supply * 2.0
        if collapsed and collapse_time is None:
            collapse_time = hour
        rows.append(
            {
                "hour": hour,
                "ust_price": ust,
                "luna_price": luna,
                "ust_supply": ust_supply,
                "luna_supply": luna_supply,
                "anchor_deposits": deposits,
                "outside_ust_stock": outside_stock,
                "withdrawal": withdrawal,
                "outside_sell": outside_sell,
                "gross_ust_sell": gross_sell,
                "reserve_support": reserve_support,
                "executable_arbitrage": executable_arb,
                "net_ust_sell": net_sell,
                "redemption_ust": redemption,
                "gross_luna_mint": minted_luna,
            }
        )
    return {
        "seed": seed,
        "scenario": asdict(scenario),
        "collapse_flag": collapse_time is not None,
        "collapse_time_hours": collapse_time,
        "minimum_ust": min(float(row["ust_price"]) for row in rows),
        "minimum_luna": min(float(row["luna_price"]) for row in rows),
        "final_luna_supply": float(rows[-1]["luna_supply"]),
        "max_withdrawal_stress": max_withdrawal,
        "timeseries": rows,
    }


def run_stress_test(
    scenario: StressScenario | None = None,
    *,
    runs: int = 100,
    seed: int = DEFAULT_SEED,
    dataset_path: Path = EXTENDED_DATASET,
    start_timestamp: str = DEFAULT_STRESS_START,
    parameters: FitParameters | None = None,
    conversion_calibration: dict[str, Any] | None = None,
    initial_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected = scenario or StressScenario()
    if runs < 1 or runs > 1000:
        raise ValueError("runs must be between 1 and 1000")
    initial = initial_state or _load_initial_state(dataset_path, start_timestamp)
    fitted = _load_calibrated_parameters(parameters)
    conversion = conversion_calibration or calibrate_counterfactual_conversion(dataset_path)
    simulations = [
        _run(selected, seed + index, initial, fitted, float(conversion["calibration_multiplier"]))
        for index in range(runs)
    ]
    fan: list[dict[str, Any]] = []
    for hour in range(selected.horizon_hours):
        row: dict[str, Any] = {"hour": hour}
        for field in ("ust_price", "luna_price", "luna_supply"):
            sample = np.asarray([run["timeseries"][hour][field] for run in simulations], dtype=float)
            row[field] = {
                "p05": float(np.quantile(sample, 0.05)),
                "median": float(np.quantile(sample, 0.50)),
                "p95": float(np.quantile(sample, 0.95)),
            }
        fan.append(row)
    collapsed = sum(bool(run["collapse_flag"]) for run in simulations)

    def quantiles(field: str) -> dict[str, float]:
        values = [run[field] for run in simulations]
        return {
            "p05": float(np.quantile(values, 0.05)),
            "median": float(np.quantile(values, 0.50)),
            "p95": float(np.quantile(values, 0.95)),
        }

    return {
        "analysis_type": "CALIBRATED_COUNTERFACTUAL_STRESS_TEST",
        "label": "ENDOGENOUS_SCENARIO_SIMULATION_NOT_HISTORICAL_REPLAY",
        "model_version": MODEL_VERSION,
        "initial_state": initial,
        "frozen_parameter_mapping": _parameter_mapping(fitted),
        "counterfactual_conversion": conversion,
        "preset_definitions": {name: asdict(value) for name, value in STRESS_PRESETS.items()},
        "scenario": asdict(selected),
        "scenario_assumptions": {
            name: {"value": value, "status": "SCENARIO_ASSUMPTION"}
            for name, value in asdict(selected).items()
            if name not in {"horizon_hours"}
        },
        "runs": runs,
        "seed_start": seed,
        "seed_end": seed + runs - 1,
        "random_variation": "Seeded per-run behavioral multiplier; structural assumptions fixed.",
        "model_assumption_uncertainty": (
            "Use the BASELINE, ADVERSE, and SEVERE presets to vary structural assumptions; "
            "the run count is not a claim about real-world probability."
        ),
        "summary": {
            "collapse_count": collapsed,
            "noncollapse_count": runs - collapsed,
            "probability_estimate": False,
            "wording": f"{collapsed} of {runs} simulated runs reached the collapse condition.",
            "minimum_ust": quantiles("minimum_ust"),
            "minimum_luna": quantiles("minimum_luna"),
            "final_luna_supply": quantiles("final_luna_supply"),
            "max_withdrawal_stress": quantiles("max_withdrawal_stress"),
        },
        "fan_chart": fan,
        "run_summaries": [{key: value for key, value in run.items() if key != "timeseries"} for run in simulations],
        "representative_timeseries": simulations[0]["timeseries"],
        "data_policy": {
            "future_observations": (
                "No future observed price, supply, withdrawal, liquidity, reserve, or issuance value is used."
            ),
            "dex_liquidity": "Scenario assumption, not observed historical Terra DEX depth.",
            "reserve_intervention": "Scenario assumption; audited LFG peg-defense flow is unavailable.",
            "conversion": (
                "Calibrated historical approximation used only to parameterize an endogenous counterfactual mapping; "
                "not a protocol identity."
            ),
        },
    }


def run_stress_presets(
    *,
    runs: int = 100,
    seed: int = DEFAULT_SEED,
    dataset_path: Path = EXTENDED_DATASET,
    start_timestamp: str = DEFAULT_STRESS_START,
) -> dict[str, dict[str, Any]]:
    initial = _load_initial_state(dataset_path, start_timestamp)
    fitted = _load_calibrated_parameters(None)
    conversion = calibrate_counterfactual_conversion(dataset_path)
    return {
        name.lower(): run_stress_test(
            scenario,
            runs=runs,
            seed=seed,
            dataset_path=dataset_path,
            start_timestamp=start_timestamp,
            parameters=fitted,
            conversion_calibration=conversion,
            initial_state=initial,
        )
        for name, scenario in STRESS_PRESETS.items()
    }
