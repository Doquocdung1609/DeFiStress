from __future__ import annotations

import argparse
import csv
import hashlib
import json
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import Any

from backend.app.services.snapshots import simulation_inputs
from scripts.research.run_deep_cascade_study import (
    PRIMARY_SEED,
    _worker_init,
    _worker_run,
    monte_carlo_draws,
)
from sim.engine.run import run_simulation
from sim.oracle import ADVERSE_PASS_THROUGH, REFERENCE_ONLY, OraclePolicy, lagged_smoothed_proxy
from sim.presets import scenario_presets
from sim.research.aave_suite import CANONICAL_SNAPSHOT, load_canonical_snapshot
from sim.schemas import BorrowerPosition, Scenario, json_safe

D = Decimal
ROOT = Path("data/processed/research_final/oracle_transmission_diagnostic_v1")
SELECTION = ROOT / "selection_manifest.json"
GRID = Path("data/processed/research_final/level3_extension/deep_stress/deterministic_grid.csv")
CHECKPOINT = Path(
    "data/processed/research_final/level3_extension/deep_stress/checkpoints/"
    "severe_seed_20260914_10000.json"
)
REPORT = Path("docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md")
NUMERIC_FIELDS = (
    "total_liquidated_debt",
    "direct_shock_liquidated_debt",
    "forced_weth_sold",
    "bad_debt",
    "unliquidated_debt",
    "max_intrawave_liquidation_price_impact",
    "max_post_arbitrage_spread",
    "time_to_recovery_seconds",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_hash(value: Any) -> str:
    payload = json.dumps(json_safe(value), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(json_safe(value), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _verify_inputs(selection: dict[str, Any]) -> dict[str, str]:
    verified: dict[str, str] = {}
    for input_id, item in selection["input_hashes"].items():
        path = Path(item["path"])
        actual = _sha(path)
        if actual != item["sha256"]:
            raise ValueError(f"Input hash changed: {input_id}: {actual}")
        verified[input_id] = actual
    return verified


def _grid_rows() -> dict[tuple[str, str], dict[str, str]]:
    with GRID.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {
        (str(int(float(row["shock_pct"]))), str(int(float(row["liquidity_haircut_pct"])))): row
        for row in rows
    }


def _deterministic_scenario(case: dict[str, Any]) -> Scenario:
    return Scenario(
        name=case["case_id"],
        shock_pct=D(case["shock_pct"]),
        liquidity_haircut_pct=D(case["liquidity_haircut_pct"]),
        max_waves=100,
        horizon_steps=120,
    )


def _selected_cases(selection: dict[str, Any]) -> list[tuple[str, str, Scenario, int | None]]:
    cases = [
        (case["case_id"], "DETERMINISTIC_DEPTH2", _deterministic_scenario(case), None)
        for case in selection["deterministic_depth2_cases"]
    ]
    cases.extend(
        (case["case_id"], "DETERMINISTIC_CONTROL", _deterministic_scenario(case), None)
        for case in selection["deterministic_controls"]
    )
    severe = replace(scenario_presets()["Severe"], max_waves=100, horizon_steps=120)
    indices = selection["audited_monte_carlo_paths"]["path_indices"]
    draws = monte_carlo_draws(severe, PRIMARY_SEED, max(indices) + 1)
    cases.extend(
        (f"MC_PATH_{index:04d}", "AUDITED_MONTE_CARLO", draws[index], index)
        for index in indices
    )
    return cases


def _policies() -> list[OraclePolicy]:
    return [
        ADVERSE_PASS_THROUGH,
        REFERENCE_ONLY,
        lagged_smoothed_proxy(
            policy_id="C_WEAK_LAGGED_SMOOTHED_PROXY",
            transmission_coefficient=D("0.25"),
            lag_steps=1,
            smoothing_window=3,
        ),
        lagged_smoothed_proxy(
            policy_id="C_MODERATE_LAGGED_SMOOTHED_PROXY",
            transmission_coefficient=D("0.50"),
            lag_steps=1,
            smoothing_window=2,
        ),
    ]


def _summary(result: Any) -> dict[str, Any]:
    liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
    return {
        **{key: result.metrics[key] for key in NUMERIC_FIELDS},
        "cascade_depth": int(result.metrics["cascade_depth"] or 0),
        "liquidation_events": len(liquidations),
        "ticks_crossed": sum(int(event.payload.get("ticks_crossed", 0)) for event in liquidations),
        "final_dex_price": result.metrics["final_dex_price"],
        "final_reference_price": result.metrics["final_reference_price"],
    }


def _close(actual: Decimal, expected: Decimal, absolute: Decimal, relative: Decimal) -> bool:
    return abs(actual - expected) <= max(absolute, relative * abs(expected))


def run_policy_a_gate(output: Path) -> dict[str, Any]:
    selection = _load(SELECTION)
    verified = _verify_inputs(selection)
    snapshot = load_canonical_snapshot()
    positions, dex, price = simulation_inputs(snapshot)
    grid = _grid_rows()
    checkpoint = _load(CHECKPOINT)
    checkpoint_rows = {int(row["path_index"]): row for row in checkpoint["rows"]}
    absolute = D(selection["comparison_rules"]["deterministic_numeric_absolute_tolerance"])
    relative = D(selection["comparison_rules"]["deterministic_numeric_relative_tolerance"])
    deterministic_checks: list[dict[str, Any]] = []
    mc_checks: list[dict[str, Any]] = []
    _worker_init(str(CANONICAL_SNAPSHOT))

    for case_id, case_type, scenario, path_index in _selected_cases(selection):
        if path_index is None:
            result = run_simulation(
                positions,
                dex,
                price,
                scenario,
                run_id=f"oracle-a-gate-{case_id}",
            )
            actual = _summary(result)
            expected = grid[(str(int(scenario.shock_pct)), str(int(scenario.liquidity_haircut_pct)))]
            field_checks: dict[str, bool] = {
                "cascade_depth": actual["cascade_depth"] == int(expected["cascade_depth"]),
                "liquidation_events": actual["liquidation_events"] == int(expected["liquidation_events"]),
                "ticks_crossed": actual["ticks_crossed"] == int(expected["ticks_crossed"]),
            }
            for field in NUMERIC_FIELDS:
                expected_value = D(expected[field] or "0")
                actual_value = D(str(actual[field] or 0))
                field_checks[field] = _close(actual_value, expected_value, absolute, relative)
            deterministic_checks.append(
                {
                    "case_id": case_id,
                    "case_type": case_type,
                    "status": "PASS" if all(field_checks.values()) else "FAIL",
                    "field_checks": field_checks,
                    "actual": actual,
                    "locked_source_row": expected,
                }
            )
        else:
            reproduced, _ = _worker_run((path_index, scenario))
            expected = checkpoint_rows[path_index]
            mc_checks.append(
                {
                    "case_id": case_id,
                    "path_index": path_index,
                    "status": "PASS" if reproduced == expected else "FAIL",
                    "reproduced_sha256": _stable_hash(reproduced),
                    "locked_sha256": _stable_hash(expected),
                    "exact_match": reproduced == expected,
                }
            )

    passed = all(row["status"] == "PASS" for row in [*deterministic_checks, *mc_checks])
    payload = {
        "status": "PASS" if passed else "FAIL_STOP_B_C",
        "selection_manifest_sha256": _sha(SELECTION),
        "verified_input_hashes": verified,
        "policy": "A_ADVERSE_PASS_THROUGH",
        "deterministic_checks": deterministic_checks,
        "monte_carlo_checks": mc_checks,
        "comparison_tolerances": {
            "deterministic_absolute": str(absolute),
            "deterministic_relative": str(relative),
            "monte_carlo": "exact serialized row equality",
        },
    }
    _write_json(output / "baseline_reproduction.json", payload)
    if not passed:
        raise RuntimeError("Policy A baseline reproduction failed; B/C are prohibited")
    return payload


def _post_wave1_state(
    positions: list[BorrowerPosition],
    result: Any,
) -> tuple[list[BorrowerPosition], set[str]]:
    state = deepcopy(positions)
    by_id = {position.borrower_hash: position for position in state}
    attempted: set[str] = set()
    for event in result.events:
        if event.wave != 1 or event.borrower_hash is None:
            continue
        if not (
            event.event_type == "LIQUIDATION_SKIPPED"
            and event.payload.get("reason") == "CAPACITY_EXCEEDED"
        ):
            attempted.add(event.borrower_hash)
        if event.event_type != "LIQUIDATION":
            continue
        position = by_id[event.borrower_hash]
        position.debt_usdc = max(D(0), position.debt_usdc - event.debt_repaid)
        position.collateral_weth = max(D(0), position.collateral_weth - event.collateral_seized)
    return state, attempted


def _run_case(
    *,
    case_id: str,
    case_type: str,
    path_index: int | None,
    scenario: Scenario,
    policy: OraclePolicy,
    positions: list[BorrowerPosition],
    dex: Any,
    price: Decimal,
) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    run_id = f"oracle-diagnostic-{case_id}-{policy.policy_id}"
    result = run_simulation(
        positions,
        dex,
        price,
        scenario,
        run_id=run_id,
        oracle_policy=policy,
    )
    repeated = run_simulation(
        positions,
        dex,
        price,
        scenario,
        run_id=run_id,
        oracle_policy=policy,
    )
    result_hash = _stable_hash(result.to_dict())
    repeated_hash = _stable_hash(repeated.to_dict())
    if result_hash != repeated_hash:
        raise ValueError(f"Non-deterministic result: {case_id}/{policy.policy_id}")

    reference = price * (D(1) + scenario.shock_pct / D(100))
    wave1_points = [point for point in result.timeseries if point.wave == 1]
    post_wave1_dex = wave1_points[0].dex_price if wave1_points else reference
    post_wave1_valuation = policy.next_valuation_price(reference, [reference, post_wave1_dex])
    post_positions, attempted_wave1 = _post_wave1_state(positions, result)
    borrower_rows: list[dict[str, Any]] = []
    newly_eligible: list[str] = []
    for initial, post in zip(positions, post_positions, strict=True):
        direct_hf = initial.health_factor(
            reference,
            scenario.liquidation_threshold_override,
            scenario.usdc_price_usd,
        )
        post_hf = post.health_factor(
            post_wave1_valuation,
            scenario.liquidation_threshold_override,
            scenario.usdc_price_usd,
        )
        newly = (
            initial.borrower_hash not in attempted_wave1
            and direct_hf >= 1
            and post_hf < 1
        )
        if newly:
            newly_eligible.append(initial.borrower_hash)
        borrower_rows.append(
            {
                "case_id": case_id,
                "case_type": case_type,
                "path_index": "" if path_index is None else path_index,
                "policy_id": policy.policy_id,
                "borrower_hash": initial.borrower_hash,
                "direct_shock_hf": direct_hf,
                "post_wave1_hf": post_hf,
                "attempted_in_wave1": initial.borrower_hash in attempted_wave1,
                "newly_eligible_after_wave1": newly,
                "direct_shock_valuation_price_usd_per_weth": reference,
                "post_wave1_borrower_valuation_price_usd_per_weth": post_wave1_valuation,
                "post_wave1_dex_trade_price_usd_per_weth": post_wave1_dex,
                "post_wave1_hf_delta_vs_policy_a": D(0),
            }
        )

    summary = _summary(result)
    liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
    borrower_ids = [str(event.borrower_hash) for event in liquidations]
    later_wave_valid = all(
        event.wave == 1
        or (
            next(
                row["direct_shock_hf"]
                for row in borrower_rows
                if row["borrower_hash"] == event.borrower_hash
            )
            >= 1
            and event.health_factor_before < 1
        )
        for event in liquidations
    )
    aggregate = {
        "result_id": f"ORACLE_DIAG::{case_id}::{policy.policy_id}",
        "case_id": case_id,
        "case_type": case_type,
        "path_index": path_index,
        "path_seed": scenario.seed,
        "policy_id": policy.policy_id,
        "shock_pct": scenario.shock_pct,
        "liquidity_haircut_pct": scenario.liquidity_haircut_pct,
        "direct_shock_valuation_price_usd_per_weth": reference,
        "post_wave1_dex_trade_price_usd_per_weth": post_wave1_dex,
        "post_wave1_borrower_valuation_price_usd_per_weth": post_wave1_valuation,
        "newly_eligible_borrowers": newly_eligible,
        "newly_eligible_count": len(newly_eligible),
        **summary,
        "no_duplicate_liquidated_borrower": len(borrower_ids) == len(set(borrower_ids)),
        "later_wave_direct_shock_not_eligible": later_wave_valid,
        "all_numeric_finite": all(
            value is None or isinstance(value, int) or D(str(value)).is_finite()
            for value in summary.values()
        ),
        "deterministic_repeat_sha256": result_hash,
        "deterministic_repeat_match": result_hash == repeated_hash,
    }
    return aggregate, borrower_rows, result_hash


def run_comparison(output: Path) -> dict[str, Any]:
    selection = _load(SELECTION)
    verified = _verify_inputs(selection)
    baseline = _load(output / "baseline_reproduction.json")
    if baseline["status"] != "PASS" or baseline["selection_manifest_sha256"] != _sha(SELECTION):
        raise RuntimeError("Policy A gate is absent, failed, or belongs to a different selection manifest")

    snapshot = load_canonical_snapshot()
    positions, dex, price = simulation_inputs(snapshot)
    policies = _policies()
    aggregates: list[dict[str, Any]] = []
    borrower_rows: list[dict[str, Any]] = []
    for case_id, case_type, scenario, path_index in _selected_cases(selection):
        case_aggregates: list[dict[str, Any]] = []
        case_borrowers: list[dict[str, Any]] = []
        for policy in policies:
            aggregate, borrowers, _ = _run_case(
                case_id=case_id,
                case_type=case_type,
                path_index=path_index,
                scenario=scenario,
                policy=policy,
                positions=positions,
                dex=dex,
                price=price,
            )
            case_aggregates.append(aggregate)
            case_borrowers.extend(borrowers)
        policy_a = next(row for row in case_aggregates if row["policy_id"] == "A_ADVERSE_PASS_THROUGH")
        policy_a_borrowers = {
            row["borrower_hash"]: row
            for row in case_borrowers
            if row["policy_id"] == "A_ADVERSE_PASS_THROUGH"
        }
        for row in case_aggregates:
            row["delta_vs_a"] = {
                "cascade_depth": row["cascade_depth"] - policy_a["cascade_depth"],
                "total_liquidated_debt_usdc": row["total_liquidated_debt"]
                - policy_a["total_liquidated_debt"],
                "modeled_bad_debt_usd": row["bad_debt"] - policy_a["bad_debt"],
                "immediate_dex_price_impact_ratio": row["max_intrawave_liquidation_price_impact"]
                - policy_a["max_intrawave_liquidation_price_impact"],
                "post_arbitrage_residual_spread_ratio": row["max_post_arbitrage_spread"]
                - policy_a["max_post_arbitrage_spread"],
                "final_dex_price_usd_per_weth": row["final_dex_price"] - policy_a["final_dex_price"],
                "post_wave1_borrower_valuation_price_usd_per_weth": (
                    row["post_wave1_borrower_valuation_price_usd_per_weth"]
                    - policy_a["post_wave1_borrower_valuation_price_usd_per_weth"]
                ),
            }
            row["post_wave1_dex_state_matches_a"] = _close(
                D(str(row["post_wave1_dex_trade_price_usd_per_weth"])),
                D(str(policy_a["post_wave1_dex_trade_price_usd_per_weth"])),
                D("1e-18"),
                D("1e-18"),
            )
        for row in case_borrowers:
            row["post_wave1_hf_delta_vs_policy_a"] = (
                row["post_wave1_hf"]
                - policy_a_borrowers[row["borrower_hash"]]["post_wave1_hf"]
            )
        aggregates.extend(case_aggregates)
        borrower_rows.extend(case_borrowers)

    aggregate_columns = [
        "result_id",
        "case_id",
        "case_type",
        "path_index",
        "path_seed",
        "policy_id",
        "shock_pct",
        "liquidity_haircut_pct",
        "direct_shock_valuation_price_usd_per_weth",
        "post_wave1_dex_trade_price_usd_per_weth",
        "post_wave1_borrower_valuation_price_usd_per_weth",
        "newly_eligible_count",
        "cascade_depth",
        "total_liquidated_debt",
        "bad_debt",
        "max_intrawave_liquidation_price_impact",
        "max_post_arbitrage_spread",
        "final_dex_price",
        "post_wave1_dex_state_matches_a",
        "no_duplicate_liquidated_borrower",
        "later_wave_direct_shock_not_eligible",
        "all_numeric_finite",
        "deterministic_repeat_match",
    ]
    _write_csv(
        output / "comparison_matrix.csv",
        [{key: row[key] for key in aggregate_columns} for row in aggregates],
    )
    _write_json(output / "comparison_matrix.json", {"rows": aggregates})
    _write_csv(output / "borrower_level_evidence.csv", borrower_rows)

    all_invariants = all(
        row["post_wave1_dex_state_matches_a"]
        and row["no_duplicate_liquidated_borrower"]
        and row["later_wave_direct_shock_not_eligible"]
        and row["all_numeric_finite"]
        and row["deterministic_repeat_match"]
        for row in aggregates
    )
    d2_ids = {case["case_id"] for case in selection["deterministic_depth2_cases"]}
    d2_rows = [row for row in aggregates if row["case_id"] in d2_ids]
    policy_depths = {
        policy.policy_id: [row["cascade_depth"] for row in d2_rows if row["policy_id"] == policy.policy_id]
        for policy in policies
    }
    interpretation = {
        "status": "LIMITED_TARGETED_MODEL_DIAGNOSTIC",
        "code_observation": (
            "The baseline engine feeds min(reference_price, DEX spot) into next-wave borrower HF. "
            "That is an adverse counterfactual pass-through, not evidence about Aave's actual oracle."
        ),
        "computed_model_finding": {
            "depth2_cases_by_policy": policy_depths,
            "policy_a_depth2_count": sum(depth >= 2 for depth in policy_depths["A_ADVERSE_PASS_THROUGH"]),
            "policy_b_depth2_count": sum(depth >= 2 for depth in policy_depths["B_REFERENCE_ONLY"]),
            "policy_c_weak_depth2_count": sum(
                depth >= 2 for depth in policy_depths["C_WEAK_LAGGED_SMOOTHED_PROXY"]
            ),
            "policy_c_moderate_depth2_count": sum(
                depth >= 2 for depth in policy_depths["C_MODERATE_LAGGED_SMOOTHED_PROXY"]
            ),
        },
        "external_empirical_inference": "NOT_ESTABLISHED",
        "rq1_impact": (
            "Observed depth-2 results are oracle-policy-dependent model findings and cannot be "
            "reported as an oracle-agnostic cascade threshold."
        ),
        "rq2_impact": (
            "Liquidity remains the DEX absorption mechanism, but transmission from DEX state to "
            "borrower eligibility depends on the valuation policy."
        ),
        "reference_only_boundary": (
            "No Wave 2 under B follows structurally from fixed reference valuation plus the engine's "
            "one-attempt eligibility ordering; it is not external empirical proof."
        ),
        "policy_c_boundary": "Hypothetical causal sensitivity proxy; not Aave or Chainlink.",
    }
    regression = {
        "status": "PASS" if all_invariants else "FAIL",
        "selection_manifest_sha256": _sha(SELECTION),
        "baseline_reproduction_sha256": _sha(output / "baseline_reproduction.json"),
        "verified_input_hashes": verified,
        "case_count": len(_selected_cases(selection)),
        "policy_count": len(policies),
        "run_count": len(aggregates),
        "large_monte_carlo_rerun": False,
        "selected_monte_carlo_paths_executed": 10 * len(policies),
        "invariants": {
            "common_post_wave1_dex_state_across_policies": all(
                row["post_wave1_dex_state_matches_a"] for row in aggregates
            ),
            "no_duplicate_liquidated_borrower": all(
                row["no_duplicate_liquidated_borrower"] for row in aggregates
            ),
            "later_wave_not_directly_eligible": all(
                row["later_wave_direct_shock_not_eligible"] for row in aggregates
            ),
            "all_numeric_finite": all(row["all_numeric_finite"] for row in aggregates),
            "deterministic_repeat_match": all(
                row["deterministic_repeat_match"] for row in aggregates
            ),
        },
    }
    _write_json(output / "scientific_interpretation.json", interpretation)
    _write_json(output / "regression_report.json", regression)
    if regression["status"] != "PASS":
        raise RuntimeError("Oracle diagnostic invariants failed")
    return {
        "aggregates": aggregates,
        "borrower_rows": borrower_rows,
        "interpretation": interpretation,
        "regression": regression,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("a", "bc"), required=True)
    parser.add_argument("--output", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.phase == "a":
        result = run_policy_a_gate(args.output)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "deterministic": len(result["deterministic_checks"]),
                    "monte_carlo": len(result["monte_carlo_checks"]),
                },
                indent=2,
            )
        )
    else:
        result = run_comparison(args.output)
        print(
            json.dumps(
                {
                    "status": result["regression"]["status"],
                    "runs": result["regression"]["run_count"],
                    "finding": result["interpretation"]["computed_model_finding"],
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
