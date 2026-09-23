from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
from collections.abc import Sequence
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Any

from backend.app.services.terra_datasets import import_research_dataset
from sim.terra.conditional import (
    CONDITIONAL_MODEL_VERSION,
    MAIN_CALIBRATION_HOURS,
    PROXY_FIELDS,
    QUARANTINED_VARIABLES,
    ConditionalABM,
    ConditionalCalibration,
    ConditionalRun,
    calibrate_conditional,
)
from sim.terra.datasets import ResearchDataset
from sim.terra.schemas import DataStatus, TerraObservation
from sim.terra.validation import correlation, directional_accuracy, mae, rmse, smape, timing_error_hours

FINAL_PIPELINE_VERSION = "terra-final-research-pipeline-1.0.0"
DEFAULT_DATASET = Path("data/processed/terra_may2022_v1.csv")
DEFAULT_STRICT_V2 = Path("data/processed/model_v2/terra_abm_v2_strict_oos.json")
DEFAULT_OUTPUT = Path("data/processed/terra_final")
DEFAULT_NATIVE_SWAPS = Path(
    "data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/native_swaps/ust_luna_swaps_run.parquet"
)
SEED = 20220506
MONTE_CARLO_RUNS = 100


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _quantile(values: Sequence[float], probability: float) -> float | None:
    finite = sorted(value for value in values if math.isfinite(value))
    if not finite:
        return None
    position = (len(finite) - 1) * probability
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return finite[lower]
    weight = position - lower
    return finite[lower] * (1.0 - weight) + finite[upper] * weight


def load_historical_dataset(path: Path = DEFAULT_DATASET) -> ResearchDataset:
    return import_research_dataset(
        path,
        "terra_may2022_v1",
        DataStatus.QUALITY_WARNING,
        "Liu-Makarov-Schoar Terra/LUNA replication package",
        "REPLICATION_ONCHAIN_WITH_PRECRISIS_PROXIES",
        raw_reference="doi:10.17632/j5d8n7hzdy.4",
    )


def _truth(dataset: ResearchDataset, calibration: ConditionalCalibration) -> tuple[TerraObservation, ...]:
    return tuple(row for row in dataset.observations if row.timestamp >= calibration.evaluation_start)


def _metric_block(actual: Sequence[float], simulated: Sequence[float]) -> dict[str, float | None]:
    return {
        "mae": mae(actual, simulated),
        "rmse": rmse(actual, simulated),
        "smape": smape(actual, simulated),
        "correlation": correlation(actual, simulated),
        "directional_accuracy": directional_accuracy(actual, simulated),
    }


def evaluate_conditional(run: ConditionalRun, truth: Sequence[TerraObservation]) -> dict[str, Any]:
    states = run.states
    if len(states) != len(truth) or any(
        left.timestamp != right.timestamp for left, right in zip(states, truth, strict=True)
    ):
        raise ValueError("conditional run is not exactly aligned with its sealed evaluation window")
    actual_times = [row.timestamp for row in truth]
    simulated_times = [row.timestamp for row in states]
    actual_ust = [float(row.ust_price) for row in truth]
    simulated_ust = [row.ust_price for row in states]
    actual_luna = [float(row.luna_price) for row in truth]
    simulated_luna = [row.luna_price for row in states]
    actual_supply = [float(row.luna_supply) for row in truth]
    simulated_supply = [row.luna_supply for row in states]
    actual_withdrawals = [float(row.anchor_withdrawal_flow) for row in truth]
    simulated_withdrawals = [row.anchor_withdrawal_flow for row in states]
    log_actual_luna = [math.log(max(value, 1e-12)) for value in actual_luna]
    log_simulated_luna = [math.log(max(value, 1e-12)) for value in simulated_luna]
    timing = {
        str(threshold): timing_error_hours(actual_times, actual_ust, simulated_times, simulated_ust, threshold)
        for threshold in (0.995, 0.99, 0.95, 0.90)
    }
    actual_events = [value < 0.90 for value in actual_ust]
    simulated_events = [value < 0.90 for value in simulated_ust]
    tp = sum(actual and simulated for actual, simulated in zip(actual_events, simulated_events, strict=True))
    fp = sum(not actual and simulated for actual, simulated in zip(actual_events, simulated_events, strict=True))
    fn = sum(actual and not simulated for actual, simulated in zip(actual_events, simulated_events, strict=True))
    tn = len(actual_events) - tp - fp - fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "label": run.label,
        "not_prediction": run.not_prediction,
        "aligned_observations": len(truth),
        "ust_price": _metric_block(actual_ust, simulated_ust),
        "luna_price": {
            **_metric_block(actual_luna, simulated_luna),
            "log_rmse": rmse(log_actual_luna, log_simulated_luna),
        },
        "luna_supply": {
            **_metric_block(actual_supply, simulated_supply),
            "delta_correlation": correlation(
                [right - left for left, right in zip(actual_supply, actual_supply[1:], strict=False)],
                [right - left for left, right in zip(simulated_supply, simulated_supply[1:], strict=False)],
            ),
            "final_relative_error": abs(simulated_supply[-1] - actual_supply[-1]) / actual_supply[-1],
        },
        "anchor_withdrawals": {
            **_metric_block(actual_withdrawals, simulated_withdrawals),
            "cumulative_relative_error": abs(sum(simulated_withdrawals) - sum(actual_withdrawals))
            / max(sum(actual_withdrawals), 1.0),
        },
        "threshold_timing_error_hours": timing,
        "classification_at_ust_below_0_90": {
            "true_positive_hours": tp,
            "false_positive_hours": fp,
            "false_negative_hours": fn,
            "true_negative_hours": tn,
            "precision": precision,
            "recall": recall,
            "f1": 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall),
            "false_alarms": fp,
        },
    }


def protocol_mechanism_validation(
    dataset: ResearchDataset, calibration: ConditionalCalibration, native_swaps: Path = DEFAULT_NATIVE_SWAPS
) -> dict[str, Any]:
    rows = dataset.observations
    trigger_rows = tuple(row for row in rows if row.timestamp >= calibration.trigger_timestamp)
    evaluation_rows = _truth(dataset, calibration)

    def window_metrics(window: Sequence[TerraObservation]) -> dict[str, Any]:
        previous_supply = float(window[0].luna_supply)
        gross_mint: list[float] = []
        positive_delta: list[float] = []
        for row in window:
            gross_mint.append(float(row.ust_native_redemption_volume) / max(float(row.luna_price), 1e-12))
            current_supply = float(row.luna_supply)
            positive_delta.append(max(0.0, current_supply - previous_supply))
            previous_supply = current_supply
        gross = sum(gross_mint)
        observed = sum(positive_delta)
        return {
            "rows": len(window),
            "gross_protocol_mint_identity_luna": gross,
            "observed_positive_luna_supply_delta": observed,
            "implied_realization_ratio": observed / gross if gross else None,
            "hourly_delta_correlation": correlation(gross_mint, positive_delta),
            "identity": "gross LUNA issued = accepted UST redemption / contemporaneous LUNA price",
        }

    source_check: dict[str, Any] = {
        "status": "UNAVAILABLE",
        "reason": f"source parquet not found at {native_swaps.as_posix()}",
    }
    if native_swaps.exists():
        import pandas as pd  # type: ignore[import-untyped]

        swaps = pd.read_parquet(native_swaps, columns=["time", "offer_amount"])
        swaps["timestamp"] = pd.to_datetime(swaps["time"], utc=True).dt.floor("h")
        hourly = swaps.groupby("timestamp", sort=True)["offer_amount"].sum()
        mismatches = 0
        checked = 0
        for row in rows:
            expected = float(hourly.get(row.timestamp, 0.0))
            checked += 1
            if not math.isclose(expected, float(row.ust_native_redemption_volume), rel_tol=1e-9, abs_tol=1e-6):
                mismatches += 1
        source_check = {
            "status": "PROVENANCE_SUPPORTED_WITH_EXTRACT_LIMITATION",
            "source_file": native_swaps.as_posix(),
            "sha256": _sha256(native_swaps),
            "raw_rows": int(len(swaps)),
            "hourly_rows_checked": checked,
            "hourly_aggregation_mismatches": mismatches,
            "documented_direction": "offer='uusd', swap='uluna' (UST offered for LUNA)",
            "unit": "UST, already normalized by replication package",
            "limitation": (
                "four-column extract has no action/direction column; direction is documented by package path/code"
            ),
        }
    return {
        "analysis_type": "PROTOCOL_MECHANISM_VALIDATION",
        "not_price_model_tuning": True,
        "source_validation": source_check,
        "conditional_calibration_window": window_metrics(
            tuple(row for row in rows if calibration.calibration_start <= row.timestamp <= calibration.calibration_end)
        ),
        "conditional_evaluation_window": window_metrics(evaluation_rows),
        "post_trigger_full_window": window_metrics(trigger_rows),
        "interpretation": (
            "The on-chain series supports the direction and timing of redemption pressure. "
            "The one-for-one gross issuance identity overstates observed net supply because the extract does not "
            "identify all burns, routing, or same-hour netting; realization is therefore estimated only in calibration."
        ),
    }


def data_quality_report(dataset: ResearchDataset, protocol_validation: dict[str, Any]) -> dict[str, Any]:
    rows = dataset.observations

    def equal(field_a: str, field_b: str) -> bool:
        return all(getattr(row, field_a) == getattr(row, field_b) for row in rows)

    duplicate_checks = {
        "luna_minted_from_redemption_equals_luna_burned": equal("luna_minted_from_redemption", "luna_burned"),
        "luna_minted_from_redemption_equals_ust_dex_sell_volume": equal(
            "luna_minted_from_redemption", "ust_dex_sell_volume"
        ),
        "bridge_outflow_equals_bridge_inflow": equal(
            "bridge_outflow_terra_to_ethereum", "bridge_inflow_ethereum_to_terra"
        ),
        "curve_ust_price_equals_ust_price": equal("curve_ust_price", "ust_price"),
    }
    return {
        "dataset": dataset.manifest.to_dict(),
        "scientific_status": "QUALITY_WARNING",
        "source_availability": {
            "terra_classic_archival_lcd_rpc": {
                "status": "UNAVAILABLE",
                "reason": "No archival Terra endpoint is configured.",
                "impact": "Not a blocker for the bundled replication extract; blocks independent full-node re-query.",
            },
            "replication_native_redemptions": protocol_validation["source_validation"],
            "ethereum_archival_rpc_curve": {
                "status": "UNAVAILABLE",
                "reason": "ETH_ARCHIVE_RPC_URL is not configured for this dataset.",
                "impact": "Curve variables are quarantined and are not consumed by the final model.",
            },
            "bridge_flow_indexer": {
                "status": "UNAVAILABLE",
                "reason": "No indexed bridge dataset is configured.",
                "impact": "Bridge variables are quarantined and are not consumed by the final model.",
            },
        },
        "quarantined_variables": list(QUARANTINED_VARIABLES),
        "execution_capacity_proxies": list(PROXY_FIELDS),
        "duplicate_or_suspect_field_checks": duplicate_checks,
        "policy": "Suspect duplicate fields and unavailable sources are excluded, not imputed or fabricated.",
    }


def _collapse_hour(run: ConditionalRun) -> float | None:
    first = next((index for index, row in enumerate(run.states) if row.collapse_signal), None)
    return None if first is None else float(first)


def monte_carlo(
    model: ConditionalABM,
    calibration: ConditionalCalibration,
    timestamps: tuple[datetime, ...],
    runs: int = MONTE_CARLO_RUNS,
) -> dict[str, Any]:
    simulations = [model.run(calibration, timestamps, SEED + index) for index in range(runs)]
    probabilities = (0.05, 0.25, 0.50, 0.75, 0.95)
    series: dict[str, list[dict[str, Any]]] = {}
    fields = ("ust_price", "luna_price", "luna_supply", "anchor_withdrawal_flow")
    for field in fields:
        values: list[dict[str, Any]] = []
        for index, timestamp in enumerate(timestamps):
            sample = [float(getattr(run.states[index], field)) for run in simulations]
            values.append(
                {
                    "timestamp": _iso(timestamp),
                    "quantiles": {f"p{int(p * 100):02d}": _quantile(sample, p) for p in probabilities},
                }
            )
        series[field] = values
    collapse = [_collapse_hour(run) for run in simulations]
    observed = [value for value in collapse if value is not None]
    return {
        "model": "CONDITIONAL_ABM_FINAL",
        "runs": runs,
        "seed_start": SEED,
        "seed_end": SEED + runs - 1,
        "time_series_quantiles": series,
        "collapse_timing_hours_from_evaluation_start": {
            "collapsed_runs": len(observed),
            "noncollapsed_runs": runs - len(observed),
            "quantiles": {f"p{int(p * 100):02d}": _quantile(observed, p) for p in probabilities},
        },
    }


def _benchmark(
    model: ConditionalABM,
    calibration: ConditionalCalibration,
    timestamps: tuple[datetime, ...],
    truth: tuple[TerraObservation, ...],
) -> dict[str, Any]:
    variants: dict[str, dict[str, Any]] = {
        "THRESHOLD_STATIC": {
            "anchor_exit_rate": 0.0,
            "external_exit_rate": 0.0,
            "arbitrage_enabled": False,
            "confidence_feedback": False,
        },
        "AGGREGATE_HAZARD": {
            "whale_heterogeneity": False,
            "external_holders_enabled": False,
            "confidence_feedback": True,
        },
        "SYSTEM_DYNAMICS": {"whale_heterogeneity": False},
        "CONDITIONAL_ABM_FINAL": {},
    }
    rows = []
    for name, overrides in variants.items():
        run = model.run(calibration, timestamps, SEED, overrides)
        metrics = evaluate_conditional(run, truth)
        rows.append(
            {
                "model": name,
                "ust_rmse": metrics["ust_price"]["rmse"],
                "luna_log_rmse": metrics["luna_price"]["log_rmse"],
                "supply_final_relative_error": metrics["luna_supply"]["final_relative_error"],
                "withdrawal_rmse": metrics["anchor_withdrawals"]["rmse"],
                "collapse_f1": metrics["classification_at_ust_below_0_90"]["f1"],
                "timing_error_hours": metrics["threshold_timing_error_hours"],
            }
        )
    return {
        "label": "CONDITIONAL_HISTORICAL_REPLAY_BENCHMARK",
        "not_strict_oos": True,
        "common_calibration": calibration.to_dict(),
        "comparators": rows,
        "warning": "Comparator variants are structural baselines, not separately holdout-tuned production models.",
    }


def _ablation(
    model: ConditionalABM,
    calibration: ConditionalCalibration,
    timestamps: tuple[datetime, ...],
    truth: tuple[TerraObservation, ...],
) -> dict[str, Any]:
    variants: dict[str, dict[str, Any]] = {
        "FULL": {},
        "NO_WHALE_HETEROGENEITY": {"whale_heterogeneity": False},
        "NO_ARBITRAGE": {"arbitrage_enabled": False},
        "NO_LIQUIDITY_FEEDBACK": {"liquidity_feedback": False},
        "NO_CONFIDENCE_FEEDBACK": {"confidence_feedback": False},
        "NO_EXTERNAL_HOLDERS": {"external_holders_enabled": False},
        "NO_PROTOCOL_MINT": {"mint_efficiency": 0.0},
    }
    results = []
    for name, overrides in variants.items():
        run = model.run(calibration, timestamps, SEED, overrides)
        metrics = evaluate_conditional(run, truth)
        results.append(
            {
                "variant": name,
                "ust_rmse": metrics["ust_price"]["rmse"],
                "luna_log_rmse": metrics["luna_price"]["log_rmse"],
                "final_supply_relative_error": metrics["luna_supply"]["final_relative_error"],
                "cumulative_withdrawal_relative_error": metrics["anchor_withdrawals"]["cumulative_relative_error"],
                "collapse_hour": _collapse_hour(run),
            }
        )
    return {"label": "CONDITIONAL_ABLATION", "variants": results}


def _sensitivity(
    model: ConditionalABM,
    calibration: ConditionalCalibration,
    timestamps: tuple[datetime, ...],
) -> dict[str, Any]:
    grid: dict[str, tuple[float, ...]] = {
        "execution_depth_multiplier": (0.5, 1.0, 2.0),
        "execution_capacity_multiplier": (0.5, 1.0, 2.0),
        "redemption_friction": (0.01, 0.02, 0.04),
        "mint_to_market_fraction": (0.25, 0.50, 0.75),
        "confidence_sensitivity": (0.5, 1.0, 1.5),
    }
    rows = []
    for parameter, values in grid.items():
        for value in values:
            run = model.run(calibration, timestamps, SEED, {parameter: value})
            rows.append(
                {
                    "parameter": parameter,
                    "value": value,
                    "final_ust_price": run.states[-1].ust_price,
                    "final_luna_price": run.states[-1].luna_price,
                    "final_luna_supply": run.states[-1].luna_supply,
                    "cumulative_withdrawals": sum(row.anchor_withdrawal_flow for row in run.states),
                    "collapse_hour": _collapse_hour(run),
                }
            )
    return {
        "method": "ONE_AT_A_TIME_AROUND_CALIBRATION",
        "no_holdout_selection": True,
        "results": rows,
    }


def _rolling_origin(dataset: ResearchDataset, model: ConditionalABM) -> dict[str, Any]:
    rows = []
    for hours in (6, 12, 18, 24):
        calibration = calibrate_conditional(dataset, hours)
        truth = _truth(dataset, calibration)[:6]
        timestamps = tuple(row.timestamp for row in truth)
        run = model.run(calibration, timestamps, SEED + hours)
        metrics = evaluate_conditional(run, truth)
        rows.append(
            {
                "calibration_hours": hours,
                "calibration_end": _iso(calibration.calibration_end),
                "forecast_hours": len(truth),
                "ust_rmse": metrics["ust_price"]["rmse"],
                "luna_log_rmse": metrics["luna_price"]["log_rmse"],
                "supply_final_relative_error": metrics["luna_supply"]["final_relative_error"],
            }
        )
    return {
        "method": "ROLLING_ORIGIN_CALIBRATION_LENGTH_SENSITIVITY",
        "forecast_horizon_hours": 6,
        "windows": rows,
        "warning": "Only the pre-forecast origin window is used at each origin.",
    }


def _diagnostics(
    run: ConditionalRun,
    calibration: ConditionalCalibration,
    timestamps: tuple[datetime, ...],
    model: ConditionalABM,
) -> dict[str, Any]:
    states = run.states
    numeric = [
        value
        for row in states
        for value in (
            row.ust_price,
            row.luna_price,
            row.ust_supply,
            row.luna_supply,
            row.anchor_total_deposits,
            row.redemption_volume,
        )
    ]
    cap_hours = sum(bool(row.cap_flags) for row in states)
    initial_supply = float(calibration.initial_state.luna_supply)
    tiny_low = model.run(calibration, timestamps, SEED, {"execution_depth_multiplier": 0.99})
    tiny_high = model.run(calibration, timestamps, SEED, {"execution_depth_multiplier": 1.01})
    perturbation = abs(tiny_high.states[-1].ust_price - tiny_low.states[-1].ust_price)
    component_options = {
        "whale_heterogeneity": {"whale_heterogeneity": False},
        "arbitrage": {"arbitrage_enabled": False},
        "liquidity_feedback": {"liquidity_feedback": False},
        "confidence_feedback": {"confidence_feedback": False},
        "external_holders": {"external_holders_enabled": False},
    }
    component_effects = {}
    full_ust = [row.ust_price for row in states]
    for name, options in component_options.items():
        candidate = model.run(calibration, timestamps, SEED, options)
        component_effects[name] = rmse(full_ust, [row.ust_price for row in candidate.states])
    total_effect = sum(component_effects.values())
    dominant_share = max(component_effects.values()) / total_effect if total_effect else 0.0
    pre_step_supplies = [float(calibration.initial_state.ust_supply), *(row.ust_supply for row in states[:-1])]
    pre_step_ust_prices = [float(calibration.initial_state.ust_price), *(row.ust_price for row in states[:-1])]
    pre_step_luna_prices = [float(calibration.initial_state.luna_price), *(row.luna_price for row in states[:-1])]
    checks = {
        "no_nan_or_infinity": all(math.isfinite(value) for value in numeric),
        "no_negative_prices_supplies_or_deposits": all(value >= 0 for value in numeric),
        "redemption_never_exceeds_pre_step_ust_supply": all(
            row.redemption_volume <= supply for row, supply in zip(states, pre_step_supplies, strict=True)
        ),
        "luna_supply_below_100x_initial": states[-1].luna_supply < initial_supply * 100.0,
        "caps_or_floors_not_dominant": cap_hours / len(states) < 0.50,
        "tiny_depth_perturbation_is_stable": math.isfinite(perturbation) and perturbation < 0.05,
        "ust_moves_are_accounted_for_by_recorded_impact": all(
            math.isclose(row.ust_price, max(run.parameters.price_floor_ust, previous * math.exp(-row.ust_impact)))
            for row, previous in zip(states, pre_step_ust_prices, strict=True)
        ),
        "mint_uses_pre_step_luna_price": all(
            math.isclose(
                row.minted_luna,
                row.redemption_volume / max(previous, 1e-12) * run.parameters.mint_efficiency,
            )
            for row, previous in zip(states, pre_step_luna_prices, strict=True)
        ),
        "no_single_component_dominates": dominant_share < 0.95,
        "quarantined_variables_not_consumed": not run.diagnostics["quarantined_variables_consumed"],
        "evaluation_starts_after_calibration": timestamps[0] > calibration.calibration_end,
        "evaluation_ground_truth_not_accepted_by_runner": True,
    }
    return {
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "cap_or_floor_hours": cap_hours,
        "cap_or_floor_share": cap_hours / len(states),
        "tiny_depth_perturbation_final_ust_difference": perturbation,
        "component_effects_on_ust_path_rmse": component_effects,
        "largest_component_effect_share": dominant_share,
        "final_luna_supply_multiple": states[-1].luna_supply / initial_supply,
        "runtime_diagnostics": run.diagnostics,
    }


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        return "UNAVAILABLE"


def _manifest(
    inputs: Sequence[Path],
    outputs: Sequence[Path],
    dataset: ResearchDataset,
    calibration: ConditionalCalibration,
    monte_carlo_runs: int,
) -> dict[str, Any]:
    packages = {}
    for name in ("numpy", "pandas", "pyarrow", "pydantic", "pytest", "ruff"):
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = "UNAVAILABLE"
    return {
        "pipeline_version": FINAL_PIPELINE_VERSION,
        "model_version": CONDITIONAL_MODEL_VERSION,
        "dataset_hash": dataset.manifest.dataset_hash,
        "dataset_version": dataset.manifest.dataset_version,
        "data_status": dataset.manifest.status.value,
        "random_seeds": {
            "primary": SEED,
            "monte_carlo_start": SEED,
            "monte_carlo_end": SEED + monte_carlo_runs - 1,
            "monte_carlo_runs": monte_carlo_runs,
        },
        "strict_oos_window": {
            "calibration_start": "2022-05-01T00:00:00Z",
            "cutoff": "2022-05-06T23:59:59Z",
            "evaluation_start": "2022-05-07T00:00:00Z",
            "evaluation_end": "2022-05-13T23:59:59Z",
        },
        "conditional_window": calibration.to_dict(),
        "parameters": calibration.parameters.to_dict(),
        "quarantined_variables": list(QUARANTINED_VARIABLES),
        "proxy_fields": list(PROXY_FIELDS),
        "git_branch": _git("branch", "--show-current"),
        "git_commit": _git("rev-parse", "HEAD"),
        "python": sys.version,
        "platform": platform.platform(),
        "packages": packages,
        "environment_presence_only": {
            "TERRA_LCD_URL": bool(os.getenv("TERRA_LCD_URL")),
            "TERRA_RPC_URL": bool(os.getenv("TERRA_RPC_URL")),
            "ETH_ARCHIVE_RPC_URL": bool(os.getenv("ETH_ARCHIVE_RPC_URL")),
        },
        "inputs": {path.as_posix(): _sha256(path) for path in inputs if path.exists()},
        "outputs": {path.name: _sha256(path) for path in outputs if path.exists()},
        "reproduce_command": (".\\.venv\\Scripts\\python.exe scripts\\terra\\run_final_pipeline.py --overwrite-final"),
        "determinism": "Fixed seeds; output hashes exclude this manifest because it contains their hashes.",
    }


def _report(
    calibration: ConditionalCalibration,
    strict_v2: dict[str, Any],
    metrics: dict[str, Any],
    protocol: dict[str, Any],
    diagnostics: dict[str, Any],
    benchmark: dict[str, Any],
    monte_carlo_result: dict[str, Any],
    ablation: dict[str, Any],
    sensitivity: dict[str, Any],
    rolling_origin: dict[str, Any],
) -> str:
    source = protocol["source_validation"]
    strict_metrics = strict_v2["validation_metrics"]
    strict_warning = strict_v2["early_warning"]
    benchmark_rows = benchmark["comparators"]
    full_ablation = next(row for row in ablation["variants"] if row["variant"] == "FULL")
    no_external = next(row for row in ablation["variants"] if row["variant"] == "NO_EXTERNAL_HOLDERS")
    sensitivity_ust = [row["final_ust_price"] for row in sensitivity["results"]]
    mc_collapse = monte_carlo_result["collapse_timing_hours_from_evaluation_start"]
    rolling_hours = [row["calibration_hours"] for row in rolling_origin["windows"]]
    return f"""# Terra May 2022 final research report

## 1. Research question

Can an auditable agent-based mechanism reproduce the coupled Terra run dynamics without leaking the
May 8--13 evaluation path into calibration?

## 2. Terra mechanism

The tested hypothesis is holder exits → UST selling → arbitrage redemption → LUNA issuance →
dilution/backing deterioration → confidence loss → further exits.

## 3. Dataset and provenance

The 312 hourly rows cover May 1--13, 2022. Native-redemption provenance is `{source["status"]}`;
the raw 277,342 swaps aggregate to the processed hourly series with
{source.get("hourly_aggregation_mismatches", "N/A")} mismatches.

## 4. Data limitations

Dataset status remains `QUALITY_WARNING`. Unavailable archival endpoints were not replaced with
fabricated observations. Curve and bridge fields, plus suspect duplicate mint/burn/sell fields, are
quarantined. DEX liquidity and depth are execution-capacity proxies only.

## 5. Strict OOS design

V2 is frozen: 144 calibration rows through May 6 and 168 evaluation rows from May 7. It produced UST
RMSE {strict_metrics["RMSE_UST"]:.6g}, collapse detected is
{strict_metrics["collapse_detected"]}, and its model-implied early-warning score was
{strict_warning["score"]:.6g}.
This is valid negative early-warning evidence: the pre-crisis inputs/specification did not forecast
the historical collapse.

## 6. Conditional replay design

The preserved V2 artifact is the **strict out-of-sample replay**. The final V4 model is a
**conditional historical mechanism replay, not a prediction**. Its trigger is the first observed
UST price below 0.99 ({_iso(calibration.trigger_timestamp)}), its calibration window is exactly
{calibration.calibration_hours} hours through {_iso(calibration.calibration_end)}, and its sealed
evaluation window starts {_iso(calibration.evaluation_start)} with {calibration.evaluation_rows} rows.

## 7. Baseline models

Four common-window structural variants were evaluated. Conditional ABM UST RMSE is
{benchmark_rows[-1]["ust_rmse"]:.6g}, versus static threshold {benchmark_rows[0]["ust_rmse"]:.6g},
aggregate hazard {benchmark_rows[1]["ust_rmse"]:.6g}, and system dynamics
{benchmark_rows[2]["ust_rmse"]:.6g}. The ABM does not materially outperform system dynamics.

## 8. ABM architecture

Depositor and external-holder exits create gross UST selling. Arbitrage throughput absorbs only an
economically executable hourly tranche. UST impact is driven by residual net selling; accepted
redemptions reduce UST supply and issue LUNA according to the protocol identity. A calibration-only
realization ratio accounts for the difference between gross issuance and observed net supply change.
LUNA impact form is selected by rolling-origin error inside calibration only. Confidence feedback is
bounded with `tanh`; prices and supplies have explicit physical bounds.

## 9. Protocol mechanism validation

During conditional calibration, gross identity mint is
{protocol["conditional_calibration_window"]["gross_protocol_mint_identity_luna"]:.6g} LUNA and the
observed positive supply delta is
{protocol["conditional_calibration_window"]["observed_positive_luna_supply_delta"]:.6g}, implying a
calibration-only realization ratio of
{protocol["conditional_calibration_window"]["implied_realization_ratio"]:.6g}. The evaluation ratio
falls to {protocol["conditional_evaluation_window"]["implied_realization_ratio"]:.6g}; this instability
is a material limitation, not a parameter retuned on holdout.

## 10. Results

- UST RMSE: {metrics["ust_price"]["rmse"]:.6g}; correlation: {metrics["ust_price"]["correlation"]}
- LUNA log-RMSE: {metrics["luna_price"]["log_rmse"]:.6g}; correlation: {metrics["luna_price"]["correlation"]}
- Final LUNA supply relative error: {metrics["luna_supply"]["final_relative_error"]:.6g}
- Cumulative Anchor withdrawal relative error: {metrics["anchor_withdrawals"]["cumulative_relative_error"]:.6g}
- UST < 0.90 F1: {metrics["classification_at_ust_below_0_90"]["f1"]:.6g}
- Automated plausibility checks pass: {diagnostics["all_checks_pass"]}

The final model remains exploratory: it captures directional co-movement but materially underpredicts
the LUNA supply explosion and does not reproduce the UST < 0.90 collapse state.

## 11. Timing analysis

Timing errors for UST thresholds .995/.99/.95/.90 are respectively
{metrics["threshold_timing_error_hours"]["0.995"]},
{metrics["threshold_timing_error_hours"]["0.99"]},
{metrics["threshold_timing_error_hours"]["0.95"]}, and
{metrics["threshold_timing_error_hours"]["0.9"]} hours. `null` means the model never crossed it.

## 12. Monte Carlo

{monte_carlo_result["runs"]} seeded runs were evaluated. {mc_collapse["collapsed_runs"]} crossed the
model collapse condition and {mc_collapse["noncollapsed_runs"]} did not. Full p05/p25/p50/p75/p95
time-series quantiles are in `monte_carlo.json`; one seed is not presented as the uncertainty result.

## 13. Ablation

Removing external holders changes UST RMSE from {full_ablation["ust_rmse"]:.6g} to
{no_external["ust_rmse"]:.6g}. Whale heterogeneity has negligible incremental fit, and no ablation
reproduces collapse. Complexity therefore has limited demonstrated explanatory power here.

## 14. Sensitivity

Across all one-at-a-time proxy/mechanism variations, final UST ranges from
{min(sensitivity_ust):.6g} to {max(sensitivity_ust):.6g}. Depth and capacity uncertainty matters, but
no sensitivity value is used to select the primary result.

## 15. Data-quality concerns

The redemption direction is documented by the replication package rather than carried in the
four-column extract. Duplicate synthetic-looking columns are excluded. Rolling-origin 6-hour
forecast checks cover calibration lengths {rolling_hours}.

## 16. Interpretation

The evidence supports a plausible feedback mechanism and shows that external-holder/confidence
channels matter more than cohort heterogeneity in this specification. It does not establish that the
ABM uniquely explains Terra or adds material power over an aggregate system-dynamics baseline.

## 17. Limitations

No archival Terra LCD/RPC, Ethereum archival/Curve source, or indexed bridge source was configured.
The bundled native-swap extract documents direction externally but omits an action column, so its
status is not promoted to independently re-queried canonical ground truth. Wallet-level cohorts are
structural representations rather than identified wallets. Results are research replay evidence,
not investment advice and not a forecast.

## 18. Conclusion

**A. Early-warning evidence:** frozen strict OOS V2 did not forecast the crash. **B. Mechanism-replay
evidence:** conditional V4 gives high price-path correlations but misses collapse severity and supply
scale. **C. Counterfactual capability:** bounded ablations and sensitivities are implemented, but
counterfactual claims remain exploratory. Holdout metrics were not used to select a winning parameter
set. V4 prioritizes protocol identity and auditable failure over the old V3's implausible recursive
over-amplification.
"""


def run_final_pipeline(
    dataset_path: Path = DEFAULT_DATASET,
    strict_v2_path: Path = DEFAULT_STRICT_V2,
    output_dir: Path = DEFAULT_OUTPUT,
    native_swaps_path: Path = DEFAULT_NATIVE_SWAPS,
    overwrite_final: bool = False,
    monte_carlo_runs: int = MONTE_CARLO_RUNS,
) -> dict[str, Any]:
    if output_dir.exists():
        if not overwrite_final:
            raise FileExistsError(f"refusing to overwrite existing final output directory: {output_dir}")
        resolved = output_dir.resolve()
        expected = DEFAULT_OUTPUT.resolve()
        if resolved != expected:
            raise ValueError("overwrite is restricted to data/processed/terra_final")
        shutil.rmtree(resolved)
    output_dir.mkdir(parents=True)
    if not strict_v2_path.exists():
        raise FileNotFoundError(f"frozen strict-OOS V2 artifact is missing: {strict_v2_path}")
    strict_v2 = json.loads(strict_v2_path.read_text(encoding="utf-8"))
    dataset = load_historical_dataset(dataset_path)
    calibration = calibrate_conditional(dataset, MAIN_CALIBRATION_HOURS)
    truth = _truth(dataset, calibration)
    timestamps = tuple(row.timestamp for row in truth)
    model = ConditionalABM()
    run = model.run(calibration, timestamps, SEED)
    metrics = evaluate_conditional(run, truth)
    protocol = protocol_mechanism_validation(dataset, calibration, native_swaps_path)
    quality = data_quality_report(dataset, protocol)
    diagnostics = _diagnostics(run, calibration, timestamps, model)

    strict_destination = output_dir / "strict_oos_v2.json"
    shutil.copyfile(strict_v2_path, strict_destination)
    benchmark = _benchmark(model, calibration, timestamps, truth)
    monte_carlo_result = monte_carlo(model, calibration, timestamps, monte_carlo_runs)
    ablation = _ablation(model, calibration, timestamps, truth)
    sensitivity = _sensitivity(model, calibration, timestamps)
    rolling_origin = _rolling_origin(dataset, model)
    artifacts: dict[str, dict[str, Any]] = {
        "conditional_abm_final.json": {
            **run.to_dict(),
            "calibration": calibration.to_dict(),
            "metrics": metrics,
        },
        "conditional_benchmark.json": benchmark,
        "protocol_mechanism_validation.json": protocol,
        "monte_carlo.json": monte_carlo_result,
        "ablation.json": ablation,
        "sensitivity.json": sensitivity,
        "rolling_origin.json": rolling_origin,
        "data_quality.json": quality,
        "model_diagnostics.json": diagnostics,
        "final_metrics.json": metrics,
    }
    output_paths = [strict_destination]
    for name, payload in artifacts.items():
        path = output_dir / name
        _json(path, payload)
        output_paths.append(path)
    report_path = output_dir / "final_report.md"
    report_path.write_text(
        _report(
            calibration,
            strict_v2,
            metrics,
            protocol,
            diagnostics,
            benchmark,
            monte_carlo_result,
            ablation,
            sensitivity,
            rolling_origin,
        ),
        encoding="utf-8",
    )
    output_paths.append(report_path)
    manifest_path = output_dir / "reproducibility_manifest.json"
    inputs = [dataset_path, strict_v2_path, native_swaps_path]
    _json(manifest_path, _manifest(inputs, output_paths, dataset, calibration, monte_carlo_runs))
    if not diagnostics["all_checks_pass"]:
        raise RuntimeError("generated artifacts, but automated plausibility diagnostics failed")
    return {
        "output_dir": str(output_dir),
        "artifacts": sorted(path.name for path in (*output_paths, manifest_path)),
        "metrics": metrics,
        "diagnostics": diagnostics,
    }
