from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from statistics import NormalDist
from typing import Any, cast

import numpy as np

from backend.app.services.snapshots import simulation_inputs
from sim.engine import MODEL_VERSION, run_simulation
from sim.monte_carlo import run_monte_carlo
from sim.network import GRAPH_MODEL_VERSION, build_run_contagion_graph, build_snapshot_contagion_graph
from sim.presets import scenario_presets
from sim.research.rq_completion import RQ_COMPLETION_VERSION, run_rq_completion
from sim.schemas import Scenario, json_safe

AAVE_RESEARCH_VERSION = "aave-mainnet-research-suite-1.1.0"
CANONICAL_SNAPSHOT = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
DEFAULT_OUTPUT = Path("data/processed/research_final/aave")
RESEARCH_MC_RUNS = 200
FAST_MC_RUNS = 30
MC_SEEDS = (20260914, 20260915, 20260916)
SHOCKS = (-5, -10, -15, -20, -25, -30, -35, -40)
LIQUIDITY_HAIRCUTS = (0, 25, 50, 75)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _finite(value: Any) -> float:
    number = float(value or 0)
    if not math.isfinite(number):
        raise ValueError(f"non-finite research result: {value}")
    return number


def load_canonical_snapshot(path: Path = CANONICAL_SNAPSHOT) -> dict[str, Any]:
    snapshot = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    if snapshot.get("mode") != "REAL_MAINNET" or snapshot.get("chain_id") != 1:
        raise ValueError("canonical Aave evidence must be a REAL_MAINNET Ethereum snapshot")
    if snapshot.get("block_number") != snapshot.get("source_manifest", {}).get("snapshot_coordination", {}).get(
        "snapshot_block"
    ):
        raise ValueError("canonical Aave snapshot has inconsistent same-block provenance")
    if not snapshot.get("borrowers") or not snapshot.get("dex_pool", {}).get("ticks"):
        raise ValueError("canonical Aave snapshot is missing borrowers or Uniswap ticks")
    raw = path.read_text(encoding="utf-8")
    for marker in ("GRAPH_API_KEY=", "ETH_RPC_URL=", "Authorization: Bearer"):
        if marker in raw:
            raise ValueError(f"secret-like marker found in canonical snapshot: {marker}")
    return snapshot


def snapshot_quality(snapshot: dict[str, Any], path: Path = CANONICAL_SNAPSHOT) -> dict[str, Any]:
    errors = [
        _finite(row.get("provenance", {}).get("health_factor_absolute_error"))
        for row in snapshot["borrowers"]
        if row.get("provenance", {}).get("health_factor_absolute_error") is not None
    ]
    relative = [
        _finite(row.get("provenance", {}).get("health_factor_relative_error_ratio"))
        for row in snapshot["borrowers"]
        if row.get("provenance", {}).get("health_factor_relative_error_ratio") is not None
    ]
    pool = snapshot["dex_pool"]
    selected: dict[str, Any] = next(
        (
            row
            for row in snapshot.get("dex_pools", [])
            if str(row.get("pool_address", "")).lower() == str(pool["pool_address"]).lower()
        ),
        {},
    )
    coverage = snapshot["coverage"]
    candidates = int(coverage["candidates_discovered"])
    verified = int(coverage["positions_loaded"])
    return {
        "artifact": path.as_posix(),
        "sha256": sha256_file(path),
        "mode": snapshot["mode"],
        "chain_id": snapshot["chain_id"],
        "block_number": snapshot["block_number"],
        "block_hash": snapshot["block_hash"],
        "block_timestamp": snapshot["block_timestamp"],
        "candidates_discovered": candidates,
        "verified_borrowers": verified,
        "candidate_verification_rate": verified / candidates if candidates else 0.0,
        "candidate_verification_rate_boundary": (
            "Rate within the top Graph-discovered debt candidates; not total-market coverage."
        ),
        "failed_reads": int(coverage["failed_reads"]),
        "weth_collateral_borrowers": int(coverage["weth_collateral_borrowers"]),
        "usdc_borrowers": int(coverage["usdc_borrowers"]),
        "weth_usdc_cohort": int(coverage["weth_usdc_cohort"]),
        "health_factor_validation": {
            "compared_borrowers": len(errors),
            "max_absolute_error": max(errors, default=0.0),
            "median_absolute_error": float(np.median(errors)) if errors else 0.0,
            "max_relative_error_ratio": max(relative, default=0.0),
            "median_relative_error_ratio": float(np.median(relative)) if relative else 0.0,
            "quality_flag_count": sum(flag.get("code") == "HF_MISMATCH" for flag in snapshot["data_quality_flags"]),
        },
        "uniswap": {
            "pool_address": pool["pool_address"],
            "fee": pool["fee"],
            "tick": pool["tick"],
            "tick_count": len(pool["ticks"]),
            "spot_price": pool["spot_price"],
            "depth_usdc_2pct": selected.get("depth_usdc_2pct"),
            "source": pool["source"],
        },
        "source_manifest": snapshot["source_manifest"],
    }


def _scenario_payload(scenario: Scenario) -> dict[str, Any]:
    return cast(dict[str, Any], json_safe(scenario))


def _summarize_result(name: str, scenario: Scenario, result: dict[str, Any]) -> dict[str, Any]:
    events = result["events"]
    liquidations = [event for event in events if event["event_type"] == "LIQUIDATION"]
    wave_one = [event for event in liquidations if int(event["wave"]) == 1]
    later = [event for event in liquidations if int(event["wave"]) >= 2]
    total = sum(_finite(event["debt_repaid"]) for event in liquidations)
    direct = sum(_finite(event["debt_repaid"]) for event in wave_one)
    later_debt = sum(_finite(event["debt_repaid"]) for event in later)
    forced = sum(_finite(event["forced_sell_amount"]) for event in liquidations)
    metrics = {key: value for key, value in result["metrics"].items()}
    return {
        "scenario_name": name,
        "scenario": _scenario_payload(scenario),
        **metrics,
        "liquidation_events": len(liquidations),
        "number_of_waves": len({int(event["wave"]) for event in liquidations}),
        "forced_weth_volume": forced,
        "wave_1_liquidated_debt": direct,
        "wave_2_plus_liquidated_debt": later_debt,
        "later_wave_share": later_debt / total if total > 0 else 0.0,
        "cascade_interpretation": "ENDOGENOUS_SECOND_WAVE" if later_debt > 0 else "NO_ENDOGENOUS_SECOND_WAVE",
    }


def _run_deterministic(
    positions: list[Any],
    dex: Any,
    price: Decimal,
    name: str,
    scenario: Scenario,
) -> tuple[dict[str, Any], dict[str, Any]]:
    result = run_simulation(
        positions,
        dex,
        price,
        scenario,
        run_id=f"research-{name.lower().replace(' ', '-')}",
    ).to_dict()
    return result, _summarize_result(name, scenario, result)


def _spearman(x_values: list[float], y_values: list[float]) -> float | None:
    if len(x_values) < 2 or len(set(x_values)) < 2 or len(set(y_values)) < 2:
        return None
    x_ranks = _rank(x_values)
    y_ranks = _rank(y_values)
    value = float(np.corrcoef(np.asarray(x_ranks), np.asarray(y_ranks))[0, 1])
    return value if math.isfinite(value) else None


def _rank(values: list[float]) -> list[float]:
    ordered = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    cursor = 0
    while cursor < len(ordered):
        end = cursor + 1
        while end < len(ordered) and values[ordered[end]] == values[ordered[cursor]]:
            end += 1
        rank = (cursor + end - 1) / 2 + 1
        for index in ordered[cursor:end]:
            ranks[index] = rank
        cursor = end
    return ranks


def _wilson(successes: int, runs: int, confidence: float = 0.95) -> dict[str, float]:
    if runs <= 0:
        return {"lower": 0.0, "upper": 0.0, "confidence": confidence}
    z = NormalDist().inv_cdf(0.5 + confidence / 2)
    p = successes / runs
    denominator = 1 + z * z / runs
    center = (p + z * z / (2 * runs)) / denominator
    margin = z * math.sqrt(p * (1 - p) / runs + z * z / (4 * runs * runs)) / denominator
    return {"lower": max(0.0, center - margin), "upper": min(1.0, center + margin), "confidence": confidence}


def _mc_payload(result: Any) -> dict[str, Any]:
    payload = result.to_dict()
    cascades = sum(value >= 2 for value in payload["distributions"]["cascade_depth"])
    payload["summary"]["model_implied_cascade_frequency"] = payload["summary"].pop("probability_of_cascade")
    payload["summary"]["cascade_frequency_wilson_95"] = {
        **_wilson(cascades, payload["runs"]),
        "successes": cascades,
        "runs": payload["runs"],
        "interpretation": (
            "Monte Carlo sampling interval conditional on this model/scenario; "
            "not a real-world probability interval."
        ),
    }
    return cast(dict[str, Any], payload)


def _matrix_csv(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    order = matrix["node_order"]
    return [
        {"source": source, **dict(zip(order, values, strict=True))}
        for source, values in zip(order, matrix["values"], strict=True)
    ]


def _replace_sensitivity(scenario: Scenario, field: str, value: float, name: str) -> Scenario:
    decimal_value = Decimal(str(value))
    if field == "shock_pct":
        return replace(scenario, name=name, shock_pct=decimal_value)
    if field == "liquidity_haircut_pct":
        return replace(scenario, name=name, liquidity_haircut_pct=decimal_value)
    if field == "gas_multiplier":
        return replace(scenario, name=name, gas_multiplier=decimal_value)
    if field == "arbitrage_capacity_pct":
        return replace(scenario, name=name, arbitrage_capacity_pct=decimal_value)
    if field == "liquidator_capacity_usdc":
        return replace(scenario, name=name, liquidator_capacity_usdc=decimal_value)
    raise ValueError(f"unsupported sensitivity field: {field}")


def run_aave_research_suite(
    *,
    snapshot_path: Path = CANONICAL_SNAPSHOT,
    output_dir: Path = DEFAULT_OUTPUT,
    fast: bool = False,
) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = load_canonical_snapshot(snapshot_path)
    quality = snapshot_quality(snapshot, snapshot_path)
    positions, dex, price = simulation_inputs(snapshot)
    presets = scenario_presets()
    professor = Scenario(name="PROFESSOR_DEMO")
    deterministic_scenarios = {**presets, "PROFESSOR_DEMO": professor}
    deterministic_rows: list[dict[str, Any]] = []
    deterministic_results: dict[str, dict[str, Any]] = {}
    for name, scenario in deterministic_scenarios.items():
        result, summary = _run_deterministic(positions, dex, price, name, scenario)
        deterministic_results[name] = result
        deterministic_rows.append(summary)

    sensitivity_specs: dict[str, tuple[str, tuple[float, ...]]] = {
        "ETH_SHOCK": ("shock_pct", tuple(float(value) for value in SHOCKS)),
        "LIQUIDITY_HAIRCUT": ("liquidity_haircut_pct", tuple(float(value) for value in LIQUIDITY_HAIRCUTS)),
        "GAS_MULTIPLIER": ("gas_multiplier", (1.0, 2.0, 4.0, 8.0)),
        "ARBITRAGE_CAPACITY": ("arbitrage_capacity_pct", (0.0, 25.0, 50.0, 75.0, 100.0)),
        "LIQUIDATOR_CAPACITY": ("liquidator_capacity_usdc", (500_000.0, 2_500_000.0, 10_000_000.0)),
    }
    sensitivity_rows: list[dict[str, Any]] = []
    sensitivity_correlations: list[dict[str, Any]] = []
    metric_names = ("total_liquidated_debt", "bad_debt", "max_price_impact", "cascade_depth")
    for family, (field, values) in sensitivity_specs.items():
        family_rows: list[dict[str, Any]] = []
        for value in values:
            scenario = _replace_sensitivity(professor, field, value, f"{family}_{value:g}")
            _, summary = _run_deterministic(positions, dex, price, scenario.name, scenario)
            row = {"sensitivity_family": family, "parameter": field, "parameter_value": value, **summary}
            sensitivity_rows.append(row)
            family_rows.append(row)
        for metric in metric_names:
            sensitivity_correlations.append(
                {
                    "sensitivity_family": family,
                    "parameter": field,
                    "metric": metric,
                    "spearman_rank_correlation": _spearman(
                        [float(row["parameter_value"]) for row in family_rows],
                        [_finite(row[metric]) for row in family_rows],
                    ),
                    "claim_boundary": "Association within a controlled one-factor sweep; not causal inference.",
                }
            )

    grid_rows: list[dict[str, Any]] = []
    for shock in SHOCKS:
        for haircut in LIQUIDITY_HAIRCUTS:
            scenario = replace(
                professor,
                name=f"GRID_{shock}_{haircut}",
                shock_pct=Decimal(str(shock)),
                liquidity_haircut_pct=Decimal(str(haircut)),
            )
            _, summary = _run_deterministic(positions, dex, price, scenario.name, scenario)
            grid_rows.append({"shock_pct": shock, "liquidity_haircut_pct": haircut, **summary})
    thresholds = []
    for haircut in LIQUIDITY_HAIRCUTS:
        candidates = [
            row for row in grid_rows if row["liquidity_haircut_pct"] == haircut and int(row["cascade_depth"]) >= 2
        ]
        first = next((shock for shock in SHOCKS if any(row["shock_pct"] == shock for row in candidates)), None)
        thresholds.append(
            {
                "liquidity_haircut_pct": haircut,
                "smallest_tested_shock_with_cascade": first,
                "status": "OBSERVED_IN_TEST_GRID" if first is not None else "NOT_OBSERVED_IN_TEST_GRID",
                "claim_boundary": (
                    "Discrete model-implied transition under the selected Mainnet snapshot; no interpolation."
                ),
            }
        )

    mc_runs = FAST_MC_RUNS if fast else RESEARCH_MC_RUNS
    mc_reason = (
        "FAST mode requested."
        if fast
        else (
            "Reduced from preferred 500 to 200 after measured 20-run benchmark implied more than "
            "15 minutes for 11 batches."
        )
    )
    mc_scenarios = {
        "PROFESSOR_DEMO": professor,
        "Moderate": presets["Moderate"],
        "Severe": presets["Severe"],
        "Low Liquidity": presets["Low Liquidity"],
        "No Arbitrage": presets["No Arbitrage"],
    }
    monte_carlo: dict[str, dict[str, Any]] = {}
    for name, scenario in mc_scenarios.items():
        selected = replace(scenario, monte_carlo_runs=mc_runs, seed=MC_SEEDS[0])
        monte_carlo[name] = _mc_payload(run_monte_carlo(positions, dex, price, selected, runs=mc_runs))
    repeated = _mc_payload(run_monte_carlo(positions, dex, price, replace(professor, seed=MC_SEEDS[0]), runs=mc_runs))
    reproducible_mc = repeated == monte_carlo["PROFESSOR_DEMO"]
    seed_robustness: dict[str, list[dict[str, Any]]] = {}
    for name, base in {"PROFESSOR_DEMO": professor, "Severe": presets["Severe"]}.items():
        rows = []
        for seed in MC_SEEDS:
            payload = monte_carlo[name] if seed == MC_SEEDS[0] else _mc_payload(
                run_monte_carlo(positions, dex, price, replace(base, seed=seed), runs=mc_runs)
            )
            summary = payload["summary"]
            rows.append(
                {
                    "seed": seed,
                    "runs": mc_runs,
                    "model_implied_cascade_frequency": summary["model_implied_cascade_frequency"],
                    "expected_shortfall_95": summary["expected_shortfall_95"],
                    "median_liquidated_debt": summary["total_liquidated_debt"]["median"],
                    "p95_liquidated_debt": summary["total_liquidated_debt"]["p95"],
                }
            )
        seed_robustness[name] = rows

    repeated_result = run_simulation(positions, dex, price, professor, run_id="research-professor_demo").to_dict()
    deterministic_reproducible = repeated_result == deterministic_results["PROFESSOR_DEMO"]
    structural_graph = build_snapshot_contagion_graph(snapshot)
    network_graphs: dict[str, dict[str, Any]] = {"STRUCTURAL": structural_graph}
    for name in ("PROFESSOR_DEMO", "Severe"):
        result = deterministic_results[name]
        run = {
            "id": f"research-{name.lower().replace(' ', '-')}",
            "scenario_id": f"research-{name.lower().replace(' ', '-')}",
            "seed": int(result["seed"]),
            "model_version": result["model_version"],
            "status": "COMPLETE",
            "result": result,
        }
        network_graphs[name] = build_run_contagion_graph(snapshot, run, result["scenario"])

    _write_json(output_dir / "snapshot_quality.json", quality)
    _write_json(output_dir / "deterministic_scenarios.json", {"rows": deterministic_rows})
    _write_csv(output_dir / "deterministic_scenarios.csv", deterministic_rows)
    _write_json(
        output_dir / "sensitivity.json",
        {"rows": sensitivity_rows, "spearman": sensitivity_correlations},
    )
    _write_csv(output_dir / "sensitivity.csv", sensitivity_rows)
    _write_json(output_dir / "shock_liquidity_grid.json", {"rows": grid_rows, "thresholds": thresholds})
    _write_csv(output_dir / "shock_liquidity_grid.csv", grid_rows)
    _write_json(
        output_dir / "monte_carlo.json",
        {
            "runs_per_scenario": mc_runs,
            "run_count_policy": mc_reason,
            "scenarios": monte_carlo,
            "frequency_claim_boundary": "Model-implied sampling frequency; not real-world probability.",
        },
    )
    _write_json(output_dir / "seed_robustness.json", seed_robustness)
    _write_json(
        output_dir / "reproducibility_check.json",
        {
            "deterministic_professor_demo_identical": deterministic_reproducible,
            "monte_carlo_professor_demo_identical": reproducible_mc,
            "fixed_seed": MC_SEEDS[0],
        },
    )
    network_dir = output_dir.parent / "network"
    for name, graph in network_graphs.items():
        slug = name.lower().replace(" ", "_")
        _write_json(network_dir / f"{slug}_graph.json", graph)
        _write_json(network_dir / f"{slug}_centrality.json", graph["centrality"])
        _write_csv(network_dir / f"{slug}_matrix.csv", _matrix_csv(graph["contagion_matrix"]))
    rq_completion = run_rq_completion(
        positions=positions,
        dex=dex,
        weth_price=price,
        snapshot=snapshot,
        output_dir=output_dir.parent / "rq_completion",
    )
    summary = {
        "suite_version": AAVE_RESEARCH_VERSION,
        "simulation_model_version": MODEL_VERSION,
        "graph_model_version": GRAPH_MODEL_VERSION,
        "rq_completion_version": RQ_COMPLETION_VERSION,
        "canonical_snapshot": quality,
        "mc_runs_per_scenario": mc_runs,
        "mc_run_count_policy": mc_reason,
        "deterministic_scenarios": deterministic_rows,
        "cascade_thresholds": thresholds,
        "sensitivity_spearman": sensitivity_correlations,
        "seed_robustness": seed_robustness,
        "reproducibility": {
            "deterministic": deterministic_reproducible,
            "monte_carlo": reproducible_mc,
        },
        "rq_completion": rq_completion,
        "runtime_seconds": time.perf_counter() - started,
    }
    _write_json(output_dir / "research_summary.json", summary)
    return summary


__all__ = [
    "AAVE_RESEARCH_VERSION",
    "CANONICAL_SNAPSHOT",
    "DEFAULT_OUTPUT",
    "load_canonical_snapshot",
    "run_aave_research_suite",
    "snapshot_quality",
]
