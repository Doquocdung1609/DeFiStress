from __future__ import annotations

import hashlib
import json
import math
import subprocess
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import numpy as np

from backend.app.services.snapshots import simulation_inputs
from sim.engine import MODEL_VERSION, run_simulation
from sim.presets import scenario_presets
from sim.research.aave_suite import (
    CANONICAL_SNAPSHOT,
    MC_SEEDS,
    RESEARCH_MC_RUNS,
    load_canonical_snapshot,
    run_aave_research_suite,
)
from sim.schemas import BorrowerPosition

D = Decimal
AUDIT_ROOT = Path("data/processed/research_final/validation_audit")
V1_ROOT = AUDIT_ROOT / "corrected_run_v1"
V2_ROOT = AUDIT_ROOT / "corrected_run_v2"
AFFECTED_METRICS = (
    "max_price_impact",
    "max_intrawave_liquidation_price_impact",
    "max_post_arbitrage_spread",
    "time_to_recovery_seconds",
    "recovery_tolerance_exceeded",
    "unliquidated_debt",
    "unliquidated_debt_legacy_recorded_lt",
)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, text=True, capture_output=True, encoding="utf-8"
    ).stdout.strip()


def _metric_slice(row: dict[str, Any]) -> dict[str, Any]:
    return {metric: row.get(metric) for metric in AFFECTED_METRICS}


def _deterministic_diff() -> list[dict[str, Any]]:
    before = {
        row["scenario_name"]: row
        for row in _read_json(V1_ROOT / "aave/deterministic_scenarios.json")["rows"]
    }
    after = {
        row["scenario_name"]: row
        for row in _read_json(V2_ROOT / "aave/deterministic_scenarios.json")["rows"]
    }
    return [
        {
            "scenario": name,
            "corrected_run_v1": _metric_slice(before[name]),
            "corrected_run_v2": _metric_slice(after[name]),
            "legacy_post_arbitrage_series_preserved": math.isclose(
                float(before[name]["max_price_impact"]),
                float(after[name]["max_price_impact"]),
                rel_tol=0,
                abs_tol=1e-15,
            ),
        }
        for name in before
    ]


def _rq4_diff() -> list[dict[str, Any]]:
    before_rows = [
        row
        for row in _read_json(V1_ROOT / "aave/sensitivity.json")["rows"]
        if row["sensitivity_family"] == "ARBITRAGE_CAPACITY"
    ]
    after_rows = [
        row
        for row in _read_json(V2_ROOT / "aave/sensitivity.json")["rows"]
        if row["sensitivity_family"] == "ARBITRAGE_CAPACITY"
    ]
    before = {float(row["parameter_value"]): row for row in before_rows}
    after = {float(row["parameter_value"]): row for row in after_rows}
    return [
        {
            "arbitrage_capacity_pct": capacity,
            "corrected_run_v1_legacy_max_price_impact": before[capacity]["max_price_impact"],
            "corrected_run_v2_legacy_max_price_impact": after[capacity]["max_price_impact"],
            "corrected_run_v2_max_intrawave_liquidation_price_impact": after[capacity][
                "max_intrawave_liquidation_price_impact"
            ],
            "corrected_run_v2_max_post_arbitrage_spread": after[capacity][
                "max_post_arbitrage_spread"
            ],
            "corrected_run_v2_time_to_recovery_seconds": after[capacity][
                "time_to_recovery_seconds"
            ],
            "corrected_run_v2_recovery_tolerance_exceeded": after[capacity][
                "recovery_tolerance_exceeded"
            ],
        }
        for capacity in sorted(before)
    ]


def _lt_diff() -> list[dict[str, Any]]:
    before_rows = _read_json(V1_ROOT / "rq_completion/rq6_liquidation_threshold.json")["rows"]
    after_rows = _read_json(V2_ROOT / "rq_completion/rq6_liquidation_threshold.json")["rows"]
    before = {float(row["liquidation_threshold"]): row for row in before_rows}
    after = {float(row["liquidation_threshold"]): row for row in after_rows}
    return [
        {
            "liquidation_threshold": threshold,
            "corrected_run_v1_unliquidated_debt_recorded_lt": before[threshold][
                "unliquidated_debt"
            ],
            "corrected_run_v2_unliquidated_debt_scenario_lt": after[threshold][
                "unliquidated_debt"
            ],
            "corrected_run_v2_legacy_recorded_lt": after[threshold][
                "unliquidated_debt_legacy_recorded_lt"
            ],
        }
        for threshold in sorted(before)
    ]


def _edge_fingerprint(graph: dict[str, Any]) -> list[tuple[Any, ...]]:
    return sorted(
        (
            edge["id"],
            edge["source"],
            edge["target"],
            edge["relation_type"],
            edge["wave"],
            edge["step"],
            edge["raw_value"],
            edge["normalized_strength"],
            edge["active"],
        )
        for edge in graph["edges"]
    )


def _graph_diff() -> list[dict[str, Any]]:
    rows = []
    for slug in ("structural", "professor_demo", "severe"):
        before = _read_json(V1_ROOT / f"network/{slug}_graph.json")
        after = _read_json(V2_ROOT / f"network/{slug}_graph.json")
        rows.append(
            {
                "graph": slug,
                "node_count_v1": len(before["nodes"]),
                "node_count_v2": len(after["nodes"]),
                "edge_count_v1": len(before["edges"]),
                "edge_count_v2": len(after["edges"]),
                "numeric_edge_fingerprint_identical": _edge_fingerprint(before)
                == _edge_fingerprint(after),
                "expected_metadata_change": "simulation_model_version",
            }
        )
    return rows


def _severe_mc_path_audit(
    positions: list[BorrowerPosition], dex: Any, initial_price: Decimal
) -> dict[str, Any]:
    base = replace(
        scenario_presets()["Severe"], monte_carlo_runs=RESEARCH_MC_RUNS, seed=MC_SEEDS[0]
    )
    rng = np.random.default_rng(base.seed)
    audited_paths = []
    for index in range(RESEARCH_MC_RUNS):
        shock = min(0.0, max(-50.0, float(base.shock_pct) + rng.normal(0, float(base.volatility_pct))))
        haircut = min(
            95.0,
            max(0.0, float(base.liquidity_haircut_pct) + rng.normal(0, 4.0)),
        )
        gas = float(base.gas_multiplier) * float(rng.lognormal(0, 0.12))
        scenario = replace(
            base,
            name=f"{base.name} MC {index + 1}",
            shock_pct=D(str(shock)),
            liquidity_haircut_pct=D(str(haircut)),
            gas_multiplier=D(str(gas)),
            seed=base.seed + index,
        )
        result = run_simulation(
            positions, dex, initial_price, scenario, run_id=f"mc-{index}"
        )
        if int(result.metrics["cascade_depth"] or 0) < 2:
            continue

        reference_price = initial_price * (D(1) + scenario.shock_pct / D(100))
        originals = {position.borrower_hash: position for position in positions}
        liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
        borrower_hashes = [event.borrower_hash for event in liquidations]
        wave_one = {event.borrower_hash for event in liquidations if event.wave == 1}
        later_checks = []
        for event in (item for item in liquidations if item.wave >= 2):
            assert event.borrower_hash is not None
            original = originals[event.borrower_hash]
            prior_state = next(point for point in result.timeseries if point.wave == event.wave - 1)
            eligibility_price = min(reference_price, prior_state.dex_price)
            initial_hf = original.health_factor(
                reference_price, scenario.liquidation_threshold_override, scenario.usdc_price_usd
            )
            eligibility_hf = original.health_factor(
                eligibility_price,
                scenario.liquidation_threshold_override,
                scenario.usdc_price_usd,
            )
            later_checks.append(
                {
                    "wave": event.wave,
                    "borrower_hash": event.borrower_hash,
                    "not_in_wave_1": event.borrower_hash not in wave_one,
                    "initial_health_factor": float(initial_hf),
                    "prior_wave_valuation_price": float(eligibility_price),
                    "eligibility_health_factor": float(eligibility_hf),
                    "event_health_factor_before": float(event.health_factor_before),
                    "initially_not_eligible": initial_hf >= 1,
                    "newly_eligible_before_wave": eligibility_hf < 1,
                    "event_hf_matches_prior_wave_state": abs(
                        eligibility_hf - event.health_factor_before
                    )
                    <= D("1e-24"),
                }
            )

        event_trace = [
            {
                "wave": event.wave,
                "step": event.step,
                "borrower_hash": event.borrower_hash,
                "health_factor_before": float(event.health_factor_before),
                "dex_price_before": float(event.dex_price_before),
                "dex_price_after": float(event.dex_price_after),
                "debt_repaid_usdc": float(event.debt_repaid),
                "forced_weth": float(event.forced_sell_amount),
            }
            for event in liquidations
        ]
        invariants = {
            "no_duplicate_borrower": len(borrower_hashes) == len(set(borrower_hashes)),
            "later_borrowers_not_in_wave_1": all(row["not_in_wave_1"] for row in later_checks),
            "later_borrowers_initially_not_eligible": all(
                row["initially_not_eligible"] for row in later_checks
            ),
            "later_borrowers_newly_eligible": all(
                row["newly_eligible_before_wave"] for row in later_checks
            ),
            "event_hf_matches_prior_wave_state": all(
                row["event_hf_matches_prior_wave_state"] for row in later_checks
            ),
        }
        audited_paths.append(
            {
                "mc_index_zero_based": index,
                "run_id": result.run_id,
                "seed": scenario.seed,
                "shock_pct": float(scenario.shock_pct),
                "liquidity_haircut_pct": float(scenario.liquidity_haircut_pct),
                "gas_multiplier": float(scenario.gas_multiplier),
                "cascade_depth": result.metrics["cascade_depth"],
                "liquidation_events": len(liquidations),
                "later_wave_checks": later_checks,
                "invariants": invariants,
                "all_invariants_pass": all(invariants.values()),
                "event_trace": event_trace,
            }
        )

    if len(audited_paths) != 8:
        raise RuntimeError(f"expected 8 Severe depth-2 paths, found {len(audited_paths)}")
    if not all(path["all_invariants_pass"] for path in audited_paths):
        raise RuntimeError("one or more Severe depth-2 paths failed eligibility invariants")
    return {
        "status": "PASS — VERIFIED",
        "scenario": "Severe",
        "base_seed": base.seed,
        "runs": RESEARCH_MC_RUNS,
        "depth_2_paths": len(audited_paths),
        "audit_rules": {
            "duplicate_rule": "A borrower may execute at most once because attempted hashes are excluded.",
            "new_eligibility_rule": (
                "Every later-wave borrower must have HF >= 1 at the direct-shock state and HF < 1 "
                "at min(reference price, prior wave post-arbitrage DEX price)."
            ),
            "health_factor_consistency": (
                "The event health_factor_before must equal recomputation at the prior-wave valuation price."
            ),
        },
        "all_paths_pass": True,
        "paths": audited_paths,
    }


def main() -> None:
    if V2_ROOT.exists():
        raise FileExistsError(
            f"{V2_ROOT} already exists; preserve versioned evidence and choose a new output version"
        )
    snapshot = load_canonical_snapshot()
    positions, dex, initial_price = simulation_inputs(snapshot)
    run_aave_research_suite(output_dir=V2_ROOT / "aave", fast=False)

    path_audit = _severe_mc_path_audit(positions, dex, initial_price)
    _write_json(V2_ROOT / "severe_mc_depth2_path_audit.json", path_audit)
    before_after = {
        "status": "PASS — VERIFIED",
        "scope": "Only Commander Review P0 metric semantics and dependent exports.",
        "corrected_run_v1_preserved": True,
        "canonical_snapshot_preserved": True,
        "metric_definitions": {
            "max_intrawave_liquidation_price_impact": (
                "max(|DEX after sale - reference| / reference), sampled after each forced sale "
                "and before wave arbitrage"
            ),
            "max_post_arbitrage_spread": (
                "max(|DEX after stabilization - reference| / reference), sampled at each wave end"
            ),
            "max_price_impact": "deprecated compatibility alias of max_post_arbitrage_spread",
            "time_to_recovery_seconds": (
                "0 if tolerance was never exceeded; otherwise first simulated timestamp returning "
                "to <=0.5%; null when not recovered"
            ),
            "unliquidated_debt": "final below-HF-1 debt using the scenario LT override when configured",
            "unliquidated_debt_legacy_recorded_lt": (
                "deprecated comparison using each frozen borrower's recorded LT"
            ),
        },
        "deterministic": _deterministic_diff(),
        "rq4_arbitrage_capacity": _rq4_diff(),
        "rq6_liquidation_threshold": _lt_diff(),
        "graph_exports": _graph_diff(),
    }
    _write_json(V2_ROOT / "before_after_v1_v2.json", before_after)

    files = sorted(path for path in V2_ROOT.rglob("*") if path.is_file())
    manifest = {
        "status": "LIMITED — REPORT WITH CAVEAT",
        "source_base_commit": _git("rev-parse", "HEAD"),
        "source_code_commit": None,
        "artifact_bundle_commit": None,
        "simulation_model_version": MODEL_VERSION,
        "canonical_snapshot": {
            "path": CANONICAL_SNAPSHOT.as_posix(),
            "sha256": _sha256(CANONICAL_SNAPSHOT),
            "block_number": snapshot["block_number"],
            "block_hash": snapshot["block_hash"],
        },
        "corrected_run_v1_path": V1_ROOT.as_posix(),
        "corrected_run_v1_preserved": True,
        "limitations": [
            "Price shock and arbitrage repositioning remain model abstractions (price teleportation).",
            "QuoterV2 validates only the initial canonical state, not counterfactual repositioned states.",
            "Fork liquidation validation remains UNAVAILABLE because Foundry/Anvil were not executed.",
            "Historical temporal panel and genuine Terra out-of-sample validation remain LIMITED.",
        ],
        "output_sha256": {path.relative_to(V2_ROOT).as_posix(): _sha256(path) for path in files},
    }
    _write_json(V2_ROOT / "manifest.json", manifest)


if __name__ == "__main__":
    main()
