from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from decimal import Decimal
from pathlib import Path
from statistics import NormalDist
from typing import Any

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

from backend.app.services.snapshots import simulation_inputs
from sim.engine.run import MODEL_VERSION, run_simulation
from sim.presets import scenario_presets
from sim.research.aave_suite import CANONICAL_SNAPSHOT, load_canonical_snapshot, sha256_file
from sim.schemas import BorrowerPosition, DexState, Scenario

D = Decimal
ROOT = Path("data/processed/research_final/level3_extension")
SOURCE_COMMIT = "423bcfd4ebf910ef73b94d9deaf7cf746d8ed71c"
PRIMARY_SEED = 20_260_914
ROBUSTNESS_SEEDS = (20_260_914, 20_261_014, 20_261_114)
MC_STAGES = (200, 1_000, 5_000, 10_000)
SHOCKS = (-5, -10, -15, -20, -25, -30, -35, -40, -45, -50)
HAIRCUTS = (0, 25, 50, 75, 90, 95)
WAVE_CAPS = (12, 24, 48, 100)

_POSITIONS: list[BorrowerPosition] | None = None
_DEX: DexState | None = None
_PRICE: Decimal | None = None


def _worker_init(snapshot_path: str) -> None:
    global _POSITIONS, _DEX, _PRICE
    snapshot = load_canonical_snapshot(Path(snapshot_path))
    _POSITIONS, _DEX, _PRICE = simulation_inputs(snapshot)


def monte_carlo_draws(base: Scenario, seed: int, count: int) -> list[Scenario]:
    if not 1 <= count <= 10_000:
        raise ValueError("Monte Carlo count must be between 1 and 10000")
    rng = np.random.default_rng(seed)
    result: list[Scenario] = []
    for index in range(count):
        shock = min(0.0, max(-50.0, float(base.shock_pct) + rng.normal(0, float(base.volatility_pct))))
        haircut = min(95.0, max(0.0, float(base.liquidity_haircut_pct) + rng.normal(0, 4.0)))
        gas = float(base.gas_multiplier) * float(rng.lognormal(0, 0.12))
        result.append(
            replace(
                base,
                name=f"{base.name} MC {index + 1}",
                shock_pct=D(str(shock)),
                liquidity_haircut_pct=D(str(haircut)),
                gas_multiplier=D(str(gas)),
                seed=seed + index,
            )
        )
    return result


def _worker_run(task: tuple[int, Scenario]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    index, scenario = task
    if _POSITIONS is None or _DEX is None or _PRICE is None:
        raise RuntimeError("Monte Carlo worker was not initialized")
    result = run_simulation(
        _POSITIONS, _DEX, _PRICE, scenario, run_id=f"level3-mc-{scenario.seed}-{index}"
    )
    liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
    borrowers = [str(event.borrower_hash) for event in liquidations]
    positive_waves = sorted({int(event.wave) for event in liquidations})
    initial_reference_price = result.metrics["final_reference_price"]
    initial_hf = {
        position.borrower_hash: position.health_factor(
            D(str(initial_reference_price)),
            scenario.liquidation_threshold_override,
            scenario.usdc_price_usd,
        )
        for position in _POSITIONS
    }
    later_wave_valid = all(
        event.wave == 1
        or (
            initial_hf[str(event.borrower_hash)] >= 1
            and event.health_factor_before < 1
        )
        for event in liquidations
    )
    finite_metrics = all(
        value is None or isinstance(value, int) or D(str(value)).is_finite()
        for value in result.metrics.values()
    )
    metrics = {
        key: (None if value is None else float(value))
        for key, value in result.metrics.items()
    }
    row = {
        "path_index": index,
        "path_seed": scenario.seed,
        "shock_pct": float(scenario.shock_pct),
        "liquidity_haircut_pct": float(scenario.liquidity_haircut_pct),
        "gas_multiplier": float(scenario.gas_multiplier),
        "cascade_depth": int(result.metrics["cascade_depth"] or 0),
        "completed_positive_liquidation_waves": len(positive_waves),
        "liquidation_events": len(liquidations),
        "total_liquidated_debt": metrics["total_liquidated_debt"],
        "bad_debt": metrics["bad_debt"],
        "unliquidated_debt": metrics["unliquidated_debt"],
        "forced_weth_sold": metrics["forced_weth_sold"],
        "max_intrawave_liquidation_price_impact": metrics[
            "max_intrawave_liquidation_price_impact"
        ],
        "max_post_arbitrage_spread": metrics["max_post_arbitrage_spread"],
        "time_to_recovery_seconds": metrics["time_to_recovery_seconds"],
        "capital_binding": any(
            event.payload.get("reason") in {"CAPACITY_EXCEEDED", "CAPITAL_EXCEEDED"}
            for event in result.events
            if event.event_type == "LIQUIDATION_SKIPPED"
        ),
        "no_duplicate_borrower": len(borrowers) == len(set(borrowers)),
        "later_wave_new_eligibility": later_wave_valid,
        "finite_metrics": finite_metrics,
        "cap_hit": int(result.metrics["cascade_depth"] or 0) >= scenario.max_waves,
        "no_wave_stop": "NO_ELIGIBLE_OR_NOT_EXECUTABLE" if not liquidations else "POSITIVE_LIQUIDATION_STOP",
    }
    path = None
    if int(result.metrics["cascade_depth"] or 0) >= 2:
        path = {
            "path_index": index,
            "path_seed": scenario.seed,
            "scenario": {
                "shock_pct": str(scenario.shock_pct),
                "liquidity_haircut_pct": str(scenario.liquidity_haircut_pct),
                "gas_multiplier": str(scenario.gas_multiplier),
                "max_waves": scenario.max_waves,
                "horizon_steps": scenario.horizon_steps,
            },
            "invariants": {
                "no_duplicate_borrower": row["no_duplicate_borrower"],
                "later_wave_new_eligibility": later_wave_valid,
                "positive_wave_count_matches_depth": len(positive_waves) == row["cascade_depth"],
            },
            "waves": [
                {
                    "wave": wave,
                    "borrowers": [
                        {
                            "borrower_hash": event.borrower_hash,
                            "health_factor_before": float(event.health_factor_before),
                            "debt_repaid": float(event.debt_repaid),
                            "forced_weth": float(event.forced_sell_amount),
                            "dex_price_before": float(event.dex_price_before),
                            "dex_price_after": float(event.dex_price_after),
                            "ticks_crossed": int(event.payload.get("ticks_crossed", 0)),
                        }
                        for event in liquidations
                        if event.wave == wave
                    ],
                }
                for wave in positive_waves
            ],
        }
    return row, path


def _json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _scenario_payload(scenario: Scenario) -> dict[str, Any]:
    return {
        key: str(value) if isinstance(value, Decimal) else value
        for key, value in asdict(scenario).items()
    }


def _stable_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_checkpoint_payload(
    payload: dict[str, Any],
    *,
    label: str,
    seed: int,
    checkpoint_target: int,
    scenario: Scenario,
) -> dict[str, Any]:
    rows = payload.get("rows")
    paths = payload.get("cascade_paths")
    if not isinstance(rows, list) or not isinstance(paths, list):
        raise ValueError("checkpoint rows/cascade_paths must be lists")
    expected_scenario = _scenario_payload(scenario)
    expected_snapshot_hash = sha256_file(CANONICAL_SNAPSHOT)
    expected = {
        "label": label,
        "seed": seed,
        "target": checkpoint_target,
        "completed": len(rows),
        "scenario": expected_scenario,
        "canonical_snapshot_sha256": expected_snapshot_hash,
        "model_version": MODEL_VERSION,
        "scenario_sha256": _stable_sha256(expected_scenario),
        "rows_sha256": _stable_sha256(rows),
        "cascade_paths_sha256": _stable_sha256(paths),
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise ValueError(f"checkpoint {key} does not match the requested run")
    if payload.get("status") != "PASS" or len(rows) != checkpoint_target:
        raise ValueError("checkpoint is not a completed PASS stage")
    indices = [int(row["path_index"]) for row in rows]
    if indices != list(range(checkpoint_target)):
        raise ValueError("checkpoint path indices are not unique, ordered, and complete")
    if any(int(row["path_seed"]) != seed + index for index, row in enumerate(rows)):
        raise ValueError("checkpoint path seeds do not match seed + path_index")
    return {
        "validated_path_count": len(rows),
        "rows_sha256": expected["rows_sha256"],
        "cascade_paths_sha256": expected["cascade_paths_sha256"],
        "checkpoint_payload_sha256": _stable_sha256(payload),
    }


def _checkpoint_payload(
    *,
    status: str,
    label: str,
    seed: int,
    target: int,
    scenario: Scenario,
    rows: list[dict[str, Any]],
    paths: list[dict[str, Any]],
    reused_checkpoint_count: int,
    executed_this_invocation: int,
    invocation_runtime_seconds: float,
    historical_execution_duration_seconds: float | None,
) -> dict[str, Any]:
    scenario_payload = _scenario_payload(scenario)
    return {
        "status": status,
        "label": label,
        "seed": seed,
        "target": target,
        "completed": len(rows),
        "scenario": scenario_payload,
        "canonical_snapshot_sha256": sha256_file(CANONICAL_SNAPSHOT),
        "model_version": MODEL_VERSION,
        "scenario_sha256": _stable_sha256(scenario_payload),
        "rows_sha256": _stable_sha256(rows),
        "cascade_paths_sha256": _stable_sha256(paths),
        "reused_checkpoint_count": reused_checkpoint_count,
        "executed_in_current_invocation": executed_this_invocation,
        "invocation_runtime_seconds": invocation_runtime_seconds,
        "historical_execution_duration_seconds": historical_execution_duration_seconds,
        "rows": rows,
        "cascade_paths": paths,
    }


def _deterministic_summary(
    name: str,
    scenario: Scenario,
    positions: list[BorrowerPosition],
    dex: DexState,
    price: Decimal,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    started = time.perf_counter()
    result = run_simulation(positions, dex, price, scenario, run_id=f"level3-{name}")
    liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
    borrowers = [str(event.borrower_hash) for event in liquidations]
    waves = sorted({event.wave for event in liquidations})
    row = {
        "scenario": name,
        "shock_pct": float(scenario.shock_pct),
        "liquidity_haircut_pct": float(scenario.liquidity_haircut_pct),
        "arbitrage_capacity_pct": float(scenario.arbitrage_capacity_pct),
        "liquidator_capital_usdc": float(scenario.liquidator_capital_usdc),
        "liquidator_capacity_usdc": float(scenario.liquidator_capacity_usdc),
        "liquidator_delay_steps": scenario.liquidator_delay_steps,
        "max_waves": scenario.max_waves,
        "horizon_steps": scenario.horizon_steps,
        "cascade_depth": int(result.metrics["cascade_depth"] or 0),
        "completed_positive_liquidation_waves": len(waves),
        "liquidation_events": len(liquidations),
        "total_liquidated_debt": float(result.metrics["total_liquidated_debt"] or 0),
        "direct_shock_liquidated_debt": float(result.metrics["direct_shock_liquidated_debt"] or 0),
        "bad_debt": float(result.metrics["bad_debt"] or 0),
        "unliquidated_debt": float(result.metrics["unliquidated_debt"] or 0),
        "forced_weth_sold": float(result.metrics["forced_weth_sold"] or 0),
        "max_intrawave_liquidation_price_impact": float(
            result.metrics["max_intrawave_liquidation_price_impact"] or 0
        ),
        "max_post_arbitrage_spread": float(result.metrics["max_post_arbitrage_spread"] or 0),
        "time_to_recovery_seconds": result.metrics["time_to_recovery_seconds"],
        "ticks_crossed": sum(int(event.payload.get("ticks_crossed", 0)) for event in liquidations),
        "capital_binding": any(
            event.payload.get("reason") in {"CAPACITY_EXCEEDED", "CAPITAL_EXCEEDED"}
            for event in result.events
            if event.event_type == "LIQUIDATION_SKIPPED"
        ),
        "no_duplicate_borrower": len(borrowers) == len(set(borrowers)),
        "cap_hit": int(result.metrics["cascade_depth"] or 0) >= scenario.max_waves,
        "runtime_seconds": time.perf_counter() - started,
    }
    path = None
    if waves:
        path = {
            "kind": "DETERMINISTIC",
            "scenario": name,
            "scenario_spec": _scenario_payload(scenario),
            "waves": [
                {
                    "wave": wave,
                    "borrower_hashes": [event.borrower_hash for event in liquidations if event.wave == wave],
                    "liquidation_count": sum(event.wave == wave for event in liquidations),
                    "debt_repaid": sum(
                        float(event.debt_repaid) for event in liquidations if event.wave == wave
                    ),
                    "forced_weth": sum(
                        float(event.forced_sell_amount) for event in liquidations if event.wave == wave
                    ),
                }
                for wave in waves
            ],
        }
    return row, path


def _wilson(successes: int, runs: int) -> dict[str, float]:
    z = NormalDist().inv_cdf(0.975)
    p = successes / runs if runs else 0.0
    denominator = 1 + z * z / runs if runs else 1.0
    center = (p + z * z / (2 * runs)) / denominator if runs else 0.0
    margin = (
        z * math.sqrt(p * (1 - p) / runs + z * z / (4 * runs * runs)) / denominator
        if runs
        else 0.0
    )
    return {"lower": max(0.0, center - margin), "upper": min(1.0, center + margin)}


def summarize_paths(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("cannot summarize an empty Monte Carlo batch")
    depths = np.asarray([row["cascade_depth"] for row in rows], dtype=float)
    losses = np.asarray(
        [row["bad_debt"] + row["total_liquidated_debt"] for row in rows], dtype=float
    )
    cutoff = float(np.quantile(losses, 0.95))
    tail = losses[losses >= cutoff]
    frequencies: dict[str, Any] = {}
    for threshold in (2, 3, 5, 10):
        successes = int(np.sum(depths >= threshold))
        frequencies[str(threshold)] = {
            "successes": successes,
            "runs": len(rows),
            "frequency": successes / len(rows),
            "wilson_95": _wilson(successes, len(rows)),
        }
    return {
        "actual_runs": len(rows),
        "max_observed_cascade_depth": int(np.max(depths)),
        "cascade_frequencies": frequencies,
        "cascade_depth_quantiles": {
            "p50": float(np.quantile(depths, 0.50)),
            "p95": float(np.quantile(depths, 0.95)),
            "p99": float(np.quantile(depths, 0.99)),
        },
        "loss_definition": (
            "modeled uncovered debt + executed liquidated repayment; neither realized "
            "financial loss nor market Expected Shortfall"
        ),
        "loss_quantiles": {
            "p50": float(np.quantile(losses, 0.50)),
            "p95": cutoff,
            "p99": float(np.quantile(losses, 0.99)),
            "composite_tail_mean_95": float(np.mean(tail)),
        },
        "invariants": {
            "all_finite": all(row["finite_metrics"] for row in rows),
            "no_duplicate_borrower_all_paths": all(row["no_duplicate_borrower"] for row in rows),
            "later_wave_new_eligibility_all_paths": all(
                row["later_wave_new_eligibility"] for row in rows
            ),
            "cap_hits": sum(bool(row["cap_hit"]) for row in rows),
        },
    }


def _run_mc_stage(
    *,
    label: str,
    base: Scenario,
    seed: int,
    target: int,
    checkpoint: Path,
    prefix_checkpoint: Path | None,
    workers: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []
    reused = 0
    prior_historical_duration: float | None = None
    if checkpoint.exists():
        payload = json.loads(checkpoint.read_text(encoding="utf-8"))
        validation = validate_checkpoint_payload(
            payload,
            label=label,
            seed=seed,
            checkpoint_target=target,
            scenario=base,
        )
        rows = list(payload["rows"])
        paths = list(payload["cascade_paths"])
        reused = validation["validated_path_count"]
        prior_historical_duration = payload.get("historical_execution_duration_seconds")
    elif prefix_checkpoint and prefix_checkpoint.exists():
        payload = json.loads(prefix_checkpoint.read_text(encoding="utf-8"))
        prefix_target = int(payload.get("target", -1))
        validation = validate_checkpoint_payload(
            payload,
            label=label,
            seed=seed,
            checkpoint_target=prefix_target,
            scenario=base,
        )
        rows = list(payload["rows"])
        paths = list(payload["cascade_paths"])
        reused = validation["validated_path_count"]
        prior_historical_duration = payload.get("historical_execution_duration_seconds")
    if len(rows) > target:
        raise ValueError("checkpoint contains more paths than the target stage")
    draws = monte_carlo_draws(base, seed, target)
    started = time.perf_counter()
    if len(rows) < target:
        with ProcessPoolExecutor(
            max_workers=workers, initializer=_worker_init, initargs=(str(CANONICAL_SNAPSHOT),)
        ) as executor:
            for chunk_start in range(len(rows), target, 200):
                chunk_end = min(target, chunk_start + 200)
                tasks = [(index, draws[index]) for index in range(chunk_start, chunk_end)]
                for row, path in executor.map(_worker_run, tasks, chunksize=5):
                    rows.append(row)
                    if path is not None:
                        paths.append(path)
                invocation_runtime = time.perf_counter() - started
                historical_duration = (
                    invocation_runtime
                    if reused == 0
                    else (
                        None
                        if prior_historical_duration is None
                        else prior_historical_duration + invocation_runtime
                    )
                )
                _json(
                    checkpoint,
                    _checkpoint_payload(
                        status="IN_PROGRESS" if len(rows) < target else "PASS",
                        label=label,
                        seed=seed,
                        target=target,
                        scenario=base,
                        rows=rows,
                        paths=paths,
                        reused_checkpoint_count=reused,
                        executed_this_invocation=len(rows) - reused,
                        invocation_runtime_seconds=invocation_runtime,
                        historical_execution_duration_seconds=historical_duration,
                    ),
                )
                print(f"[MC] {label} seed={seed} completed={len(rows)}/{target}", flush=True)
    invocation_runtime = time.perf_counter() - started
    executed_this_invocation = len(rows) - reused
    historical_duration = (
        prior_historical_duration
        if executed_this_invocation == 0
        else (
            invocation_runtime
            if reused == 0
            else (
                None
                if prior_historical_duration is None
                else prior_historical_duration + invocation_runtime
            )
        )
    )
    summary = summarize_paths(rows)
    summary.update(
        {
            "status": "PASS",
            "label": label,
            "seed": seed,
            "target_runs": target,
            "actual_runs": len(rows),
            "total_validated_path_count": len(rows),
            "reused_checkpoint_count": reused,
            "executed_in_current_invocation": executed_this_invocation,
            "invocation_runtime_seconds": invocation_runtime,
            "historical_execution_duration_seconds": historical_duration,
            "checkpoint": checkpoint.as_posix(),
            "workers": workers,
            "scenario": _scenario_payload(base),
        }
    )
    return summary, paths


def _figures(
    output: Path,
    grid_rows: list[dict[str, Any]],
    cap_rows: list[dict[str, Any]],
    primary_rows: list[dict[str, Any]],
) -> None:
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 4))
    values = [row["cascade_depth"] for row in primary_rows]
    bins = np.arange(min(values), max(values) + 2) - 0.5
    plt.hist(values, bins=bins, edgecolor="black")
    plt.xlabel("Observed positive-liquidation wave depth")
    plt.ylabel("Monte Carlo paths")
    plt.title("Severe scenario cascade-depth distribution")
    plt.tight_layout()
    plt.savefig(figures / "cascade_depth_histogram.png", dpi=180)
    plt.close()

    matrix = np.asarray(
        [
            [
                next(
                    row["cascade_depth"]
                    for row in grid_rows
                    if row["shock_pct"] == shock and row["liquidity_haircut_pct"] == haircut
                )
                for haircut in HAIRCUTS
            ]
            for shock in SHOCKS
        ]
    )
    plt.figure(figsize=(8, 5))
    plt.imshow(matrix, aspect="auto", cmap="viridis")
    plt.xticks(range(len(HAIRCUTS)), HAIRCUTS)
    plt.yticks(range(len(SHOCKS)), SHOCKS)
    plt.xlabel("Liquidity haircut (%)")
    plt.ylabel("ETH shock (%)")
    plt.colorbar(label="Observed cascade depth")
    plt.title("Predeclared shock–haircut regime map")
    plt.tight_layout()
    plt.savefig(figures / "shock_haircut_regime_map.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(
        [row["max_waves"] for row in cap_rows],
        [row["cascade_depth"] for row in cap_rows],
        marker="o",
    )
    plt.xlabel("Configured wave cap")
    plt.ylabel("Observed positive-liquidation wave depth")
    plt.title("Wave-cap sensitivity (Severe)")
    plt.tight_layout()
    plt.savefig(figures / "wave_cap_sensitivity.png", dpi=180)
    plt.close()


def run(output: Path, max_waves: int, horizon_steps: int, workers: int) -> dict[str, Any]:
    if max_waves != 100 or horizon_steps < 120:
        raise ValueError("research run requires max_waves=100 and horizon_steps>=120")
    if not 1 <= workers <= 4:
        raise ValueError("workers must be between 1 and 4")
    started = time.perf_counter()
    snapshot = load_canonical_snapshot()
    positions, dex, price = simulation_inputs(snapshot)
    presets = scenario_presets()
    base = Scenario(name="Professor Demo", max_waves=max_waves, horizon_steps=horizon_steps)
    severe_research = replace(
        presets["Severe"], max_waves=max_waves, horizon_steps=horizon_steps
    )
    severe_reference = run_simulation(
        positions, dex, price, severe_research, run_id="level3-capital-reference"
    )
    required_capital = D(str(severe_reference.metrics["total_liquidated_debt"] or 0))
    mechanisms = {
        "Professor Demo": base,
        "Baseline": replace(presets["Baseline"], max_waves=max_waves, horizon_steps=horizon_steps),
        "Moderate": replace(presets["Moderate"], max_waves=max_waves, horizon_steps=horizon_steps),
        "Severe": severe_research,
        "Low Liquidity": replace(
            presets["Low Liquidity"], max_waves=max_waves, horizon_steps=horizon_steps
        ),
        "No Arbitrage": replace(
            presets["No Arbitrage"], max_waves=max_waves, horizon_steps=horizon_steps
        ),
        "Strong Arbitrage": replace(
            presets["Strong Arbitrage"], max_waves=max_waves, horizon_steps=horizon_steps
        ),
        "Capital 25pct": replace(
            presets["Severe"],
            name="Capital 25pct",
            liquidator_capital_usdc=required_capital * D("0.25"),
            max_waves=max_waves,
            horizon_steps=horizon_steps,
        ),
        "Capital 200pct": replace(
            presets["Severe"],
            name="Capital 200pct",
            liquidator_capital_usdc=required_capital * D("2"),
            max_waves=max_waves,
            horizon_steps=horizon_steps,
        ),
        "Delay 5": replace(
            presets["Severe"],
            name="Delay 5",
            liquidator_delay_steps=5,
            max_waves=max_waves,
            horizon_steps=horizon_steps,
        ),
    }
    deterministic_rows: list[dict[str, Any]] = []
    cascade_paths: list[dict[str, Any]] = []
    for name, scenario in mechanisms.items():
        row, path = _deterministic_summary(name, scenario, positions, dex, price)
        deterministic_rows.append(row)
        if path:
            cascade_paths.append(path)

    grid_rows: list[dict[str, Any]] = []
    for shock in SHOCKS:
        for haircut in HAIRCUTS:
            scenario = replace(
                base,
                name=f"Grid {shock}/{haircut}",
                shock_pct=D(shock),
                liquidity_haircut_pct=D(haircut),
            )
            row, _ = _deterministic_summary(
                f"grid_{shock}_{haircut}", scenario, positions, dex, price
            )
            grid_rows.append(row)

    cap_rows: list[dict[str, Any]] = []
    for cap in WAVE_CAPS:
        scenario = replace(
            presets["Severe"], max_waves=cap, horizon_steps=max(cap + 20, 32)
        )
        row, _ = _deterministic_summary(f"severe_cap_{cap}", scenario, positions, dex, price)
        cap_rows.append(row)

    deep = output / "deep_stress"
    _csv(deep / "deterministic_grid.csv", grid_rows)
    _csv(deep / "wave_cap_comparison.csv", cap_rows)
    _csv(output / "tables" / "deterministic_mechanisms.csv", deterministic_rows)

    checkpoints = deep / "checkpoints"
    batches: list[dict[str, Any]] = []
    previous: Path | None = None
    primary_paths: list[dict[str, Any]] = []
    for target in MC_STAGES:
        checkpoint = checkpoints / f"severe_seed_{PRIMARY_SEED}_{target}.json"
        summary, paths = _run_mc_stage(
            label="Severe",
            base=replace(
                presets["Severe"], max_waves=max_waves, horizon_steps=horizon_steps
            ),
            seed=PRIMARY_SEED,
            target=target,
            checkpoint=checkpoint,
            prefix_checkpoint=previous,
            workers=workers,
        )
        batches.append(summary)
        previous = checkpoint
        if target == 10_000:
            primary_paths = paths

    for seed in ROBUSTNESS_SEEDS[1:]:
        summary, _ = _run_mc_stage(
            label="Severe seed robustness",
            base=replace(
                presets["Severe"], max_waves=max_waves, horizon_steps=horizon_steps
            ),
            seed=seed,
            target=1_000,
            checkpoint=checkpoints / f"severe_seed_{seed}_1000.json",
            prefix_checkpoint=None,
            workers=workers,
        )
        batches.append(summary)
    low_summary, low_paths = _run_mc_stage(
        label="Low Liquidity prespecified",
        base=replace(
            presets["Low Liquidity"], max_waves=max_waves, horizon_steps=horizon_steps
        ),
        seed=PRIMARY_SEED,
        target=1_000,
        checkpoint=checkpoints / f"low_liquidity_seed_{PRIMARY_SEED}_1000.json",
        prefix_checkpoint=None,
        workers=workers,
    )
    batches.append(low_summary)
    cascade_paths.extend(primary_paths)
    cascade_paths.extend(low_paths)
    _json(deep / "monte_carlo_batches.json", {"status": "PASS", "batches": batches})
    _json(deep / "cascade_paths.json", {"status": "PASS", "paths": cascade_paths})

    primary_checkpoint = json.loads(
        (checkpoints / f"severe_seed_{PRIMARY_SEED}_10000.json").read_text(encoding="utf-8")
    )
    _figures(output, grid_rows, cap_rows, primary_checkpoint["rows"])
    diagnostics = {
        "status": "PASS",
        "model_version": MODEL_VERSION,
        "source_commit": SOURCE_COMMIT,
        "canonical_snapshot_sha256": sha256_file(CANONICAL_SNAPSHOT),
        "canonical_counts": {
            "verified_borrowers": snapshot["coverage"]["positions_loaded"],
            "weth_usdc_cohort": snapshot["coverage"]["weth_usdc_cohort"],
        },
        "largest_configured_wave_cap": max_waves,
        "largest_horizon_steps": horizon_steps,
        "max_deterministic_observed_depth": max(
            row["cascade_depth"] for row in deterministic_rows + grid_rows + cap_rows
        ),
        "max_monte_carlo_observed_depth": max(
            batch["max_observed_cascade_depth"] for batch in batches
        ),
        "tail_assumption_warning": (
            "Haircuts 90% and 95% are counterfactual tail assumptions, not observed Mainnet depth."
        ),
        "configured_cap_is_not_observed_depth": True,
        "all_deterministic_no_duplicates": all(
            row["no_duplicate_borrower"] for row in deterministic_rows + grid_rows + cap_rows
        ),
        "monte_carlo_invariants": [batch["invariants"] for batch in batches],
        "numerical_floor_or_cap_artifacts": sum(
            batch["invariants"]["cap_hits"] for batch in batches
        ),
        "runtime_seconds": time.perf_counter() - started,
        "cpu_count": os.cpu_count(),
        "workers": workers,
    }
    _json(deep / "numerical_diagnostics.json", diagnostics)
    return diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", action="store_true")
    parser.add_argument("--max-waves", type=int, default=100)
    parser.add_argument("--horizon-steps", type=int, default=120)
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    if not args.research:
        raise SystemExit("Use --research to acknowledge the bounded research workload")
    final_artifact = args.output_dir / "deep_stress" / "numerical_diagnostics.json"
    if final_artifact.exists():
        raise SystemExit("Refusing to overwrite completed Level-3 deep-stress artifacts")
    result = run(args.output_dir, args.max_waves, args.horizon_steps, args.workers)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
