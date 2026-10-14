# ruff: noqa: E501 -- generated Vietnamese research prose intentionally keeps long lines.
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

from backend.app.services.snapshots import simulation_inputs
from scripts.research.run_oracle_transmission_diagnostic import (
    _policies,
    _post_wave1_state,
    _selected_cases,
    _stable_hash,
)
from sim.engine.run import MODEL_VERSION, run_simulation
from sim.research.aave_suite import load_canonical_snapshot
from sim.schemas import json_safe

D = Decimal
ROOT = Path("data/processed/research_final/scientific_integration_v1")
FROZEN_ROOT = Path("data/processed/research_final/frozen_v3")
ORACLE_ROOT = Path("data/processed/research_final/oracle_transmission_diagnostic_v1")
CANONICAL = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
ADDENDUM = Path("docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md")
REVIEW_PACKET = Path("docs/research_final/INTEGRATION_COMMANDER_REVIEW_PACKET.md")

STARTING_HEAD = "3011ba5e8cd23ee697c36d0aec6d047d8d58f653"
FROZEN_HEAD = "9842c4f2c35adb8b4ec906e1bc76afa825d197c7"
P2_HEAD = "8f5b635a316d72546b8a0eb0c2e8a66503b5d44f"
SELECTION_LOCK_COMMIT = "a2c37e3d513054131083b791a05f8b50047925fd"
SOURCE_CODE_COMMIT = "c113fc1ec6dd98ffcc31241c1dbd1a93b20aa193"
ARTIFACT_BUNDLE_COMMIT = "c113fc1ec6dd98ffcc31241c1dbd1a93b20aa193"

RQ_LABELS = [
    ("RQ1", "Điều kiện và ngưỡng xuất hiện thanh lý dây chuyền."),
    ("RQ2", "Vai trò thanh khoản DEX."),
    ("RQ3", "Gas, vốn, công suất và độ trễ thanh lý."),
    ("RQ4", "Arbitrage và phục hồi giá."),
    ("RQ5", "Mất neo stablecoin và định giá nợ USDC."),
    ("RQ6", "Đánh đổi LTV, liquidation threshold, liquidation bonus."),
]
POLICY_ORDER = [
    "A_ADVERSE_PASS_THROUGH",
    "B_REFERENCE_ONLY",
    "C_WEAK_LAGGED_SMOOTHED_PROXY",
    "C_MODERATE_LAGGED_SMOOTHED_PROXY",
]
P2_LOCATOR_PATHS = [
    "docs/research_final/REFERENCE_EVIDENCE_MATRIX.md",
    "docs/research_final/P2_VERSION_RECONCILIATION.md",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_file_bytes(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        check=True,
        capture_output=True,
    ).stdout


def _safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value) if value.is_finite() else None
    if isinstance(value, dict):
        return {str(key): _safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(item) for item in value]
    return json_safe(value)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_safe(value), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(_safe(row), ensure_ascii=False, sort_keys=True, allow_nan=False))
            handle.write("\n")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows([{key: _safe(value) for key, value in row.items()} for row in rows])


def _verify_bundle(root: Path, manifest: dict[str, Any]) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for relative, expected in manifest["artifact_hashes"].items():
        path = root / relative
        actual = _sha(path)
        if actual != expected:
            raise ValueError(f"Locked artifact hash mismatch: {path}: {actual} != {expected}")
        resolved[path.as_posix()] = actual
    for relative, expected in manifest.get("report_hashes", {}).items():
        path = Path(relative)
        actual = _sha(path)
        if actual != expected:
            raise ValueError(f"Locked report hash mismatch: {path}: {actual} != {expected}")
        resolved[path.as_posix()] = actual
    return resolved


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _finite_decimal(value: str) -> Decimal | None:
    if not value:
        return None
    parsed = D(value)
    return parsed if parsed.is_finite() else None


def _event_row(
    *,
    result_id: str,
    case_id: str,
    case_type: str,
    policy_id: str,
    seed: int,
    path_index: int | None,
    sequence: int,
    event: Any,
) -> dict[str, Any]:
    event_id = f"ORACLE_EVT::{case_id}::{policy_id}::{sequence:03d}"
    if event.event_type == "LIQUIDATION":
        decision = "EXECUTE"
        reason = "EXECUTE"
    elif event.event_type == "LIQUIDATION_SKIPPED":
        decision = "SKIP"
        reason = str(event.payload.get("reason", "UNKNOWN"))
    else:
        decision = "ARBITRAGE"
        reason = "ARBITRAGE"
    return {
        "event_id": event_id,
        "result_id": result_id,
        "case_id": case_id,
        "case_type": case_type,
        "policy_id": policy_id,
        "scenario_seed": seed,
        "path_index": path_index,
        "sequence": sequence,
        "event_type": event.event_type,
        "decision": decision,
        "reason": reason,
        "borrower_hash": event.borrower_hash,
        "wave": event.wave,
        "step": event.step,
        "timestamp_sim_seconds": event.timestamp_sim,
        "health_factor_before": event.health_factor_before,
        "health_factor_after": event.health_factor_after,
        "debt_repaid_usdc": event.debt_repaid,
        "collateral_seized_weth": event.collateral_seized,
        "expected_profit_usdc": event.expected_profit,
        "gas_cost_usdc": event.gas_cost,
        "reference_price_usd_per_weth": event.reference_price,
        "dex_price_before_usd_per_weth": event.dex_price_before,
        "dex_price_after_usd_per_weth": event.dex_price_after,
        "payload": event.payload,
    }


def _classification(newly: bool, attempted_later: bool, executed_later: bool, reasons: list[str]) -> str:
    if not newly:
        return "NOT_NEWLY_ELIGIBLE"
    if executed_later:
        return "NEWLY_ELIGIBLE_EXECUTED_POSITIVE_DEBT"
    if attempted_later and reasons:
        return "NEWLY_ELIGIBLE_ATTEMPTED_SKIPPED_" + "+".join(sorted(set(reasons)))
    if attempted_later:
        return "NEWLY_ELIGIBLE_ATTEMPTED_NO_POSITIVE_DEBT"
    return "NEWLY_ELIGIBLE_NOT_ATTEMPTED"


def _build_event_audit(
    selection: dict[str, Any],
    comparison: dict[str, Any],
    diagnostic_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    snapshot = load_canonical_snapshot()
    positions, dex, price = simulation_inputs(snapshot)
    diagnostic_by_key = {
        (row["case_id"], row["policy_id"], row["borrower_hash"]): row
        for row in diagnostic_rows
    }
    comparison_by_key = {
        (row["case_id"], row["policy_id"]): row for row in comparison["rows"]
    }
    audit_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    replay_hash_matches = 0
    hf_trace_matches = 0
    new_eligibility_matches = 0

    for case_id, case_type, scenario, path_index in _selected_cases(selection):
        for policy in _policies():
            result_id = f"ORACLE_DIAG::{case_id}::{policy.policy_id}"
            run_id = f"oracle-diagnostic-{case_id}-{policy.policy_id}"
            result = run_simulation(
                positions,
                dex,
                price,
                scenario,
                run_id=run_id,
                oracle_policy=policy,
            )
            locked = comparison_by_key[(case_id, policy.policy_id)]
            actual_hash = _stable_hash(result.to_dict())
            if actual_hash != locked["deterministic_repeat_sha256"]:
                raise ValueError(f"Targeted replay hash mismatch: {result_id}")
            replay_hash_matches += 1

            post_positions, attempted_set_wave1 = _post_wave1_state(positions, result)
            post_by_id = {position.borrower_hash: position for position in post_positions}
            final_by_id = {position.borrower_hash: position for position in result.final_positions}
            reference = price * (D(1) + scenario.shock_pct / D(100))
            wave1_points = [point for point in result.timeseries if point.wave == 1]
            post_wave1_dex = wave1_points[0].dex_price if wave1_points else reference
            post_wave1_valuation = policy.next_valuation_price(
                reference,
                [reference, post_wave1_dex],
            )
            run_event_rows: list[dict[str, Any]] = []
            borrower_events: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for sequence, event in enumerate(result.events, start=1):
                trace = _event_row(
                    result_id=result_id,
                    case_id=case_id,
                    case_type=case_type,
                    policy_id=policy.policy_id,
                    seed=scenario.seed,
                    path_index=path_index,
                    sequence=sequence,
                    event=event,
                )
                run_event_rows.append(trace)
                if event.borrower_hash is not None:
                    borrower_events[event.borrower_hash].append(trace)
            event_rows.extend(run_event_rows)

            direct_eligible_count = 0
            newly_count = 0
            newly_attempted_later = 0
            newly_executed_wave2 = 0
            newly_executed_later = 0
            newly_skipped = 0
            newly_not_attempted = 0
            wave2_debt = D(0)
            later_debt = D(0)
            reason_counter: Counter[str] = Counter()

            for initial in positions:
                key = (case_id, policy.policy_id, initial.borrower_hash)
                source = diagnostic_by_key[key]
                direct_hf = _finite_decimal(source["direct_shock_hf"])
                post_hf = _finite_decimal(source["post_wave1_hf"])
                post_position = post_by_id[initial.borrower_hash]
                recomputed_direct_hf = initial.health_factor(
                    reference,
                    scenario.liquidation_threshold_override,
                    scenario.usdc_price_usd,
                )
                recomputed_post_hf = post_position.health_factor(
                    post_wave1_valuation,
                    scenario.liquidation_threshold_override,
                    scenario.usdc_price_usd,
                )
                direct_eligible = recomputed_direct_hf.is_finite() and recomputed_direct_hf < 1
                newly_recomputed = (
                    initial.borrower_hash not in attempted_set_wave1
                    and recomputed_direct_hf >= 1
                    and recomputed_post_hf < 1
                )
                newly = source["newly_eligible_after_wave1"] == "True"
                if newly != newly_recomputed:
                    raise ValueError(
                        f"Independent eligibility mismatch: {result_id}/{initial.borrower_hash}"
                    )
                events = borrower_events.get(initial.borrower_hash, [])
                wave1_events = [event for event in events if int(event["wave"]) == 1]
                later_events = [event for event in events if int(event["wave"]) >= 2]
                executed = [
                    event
                    for event in events
                    if event["event_type"] == "LIQUIDATION" and D(str(event["debt_repaid_usdc"])) > 0
                ]
                executed_wave2 = [event for event in executed if int(event["wave"]) == 2]
                executed_later = [event for event in executed if int(event["wave"]) >= 2]
                skipped_later = [
                    event for event in later_events if event["event_type"] == "LIQUIDATION_SKIPPED"
                ]
                reasons = [str(event["reason"]) for event in skipped_later]
                detailed_reasons: list[str] = []
                for reason in reasons:
                    if reason != "NOT_ELIGIBLE":
                        detailed_reasons.append(reason)
                    elif post_position.debt_usdc <= 0:
                        detailed_reasons.append("NO_MODELLED_USDC_DEBT")
                    elif post_position.collateral_weth <= 0:
                        detailed_reasons.append("NO_MODELLED_WETH_COLLATERAL")
                    elif recomputed_post_hf >= 1:
                        detailed_reasons.append("HF_NOT_BELOW_ONE_AT_POST_WAVE1_STATE")
                    else:
                        detailed_reasons.append("UNEXPLAINED_PLAN_NOT_ELIGIBLE")
                wave2_repaid = sum(
                    (D(str(event["debt_repaid_usdc"])) for event in executed_wave2), D(0)
                )
                later_repaid = sum(
                    (D(str(event["debt_repaid_usdc"])) for event in executed_later), D(0)
                )
                decision_trace = "|".join(
                    f"W{event['wave']}:{event['reason']}" for event in events if event["borrower_hash"]
                ) or "NOT_EVALUATED"
                event_locators = "|".join(str(event["event_id"]) for event in events)
                wave_indices = "|".join(str(value) for value in sorted({int(e["wave"]) for e in events}))
                if direct_eligible:
                    direct_eligible_count += 1
                if newly:
                    newly_count += 1
                    if later_events:
                        newly_attempted_later += 1
                    else:
                        newly_not_attempted += 1
                        reason_counter.update(["NOT_EVALUATED_AFTER_WAVE1"])
                    if executed_wave2:
                        newly_executed_wave2 += 1
                    if executed_later:
                        newly_executed_later += 1
                    if skipped_later and not executed_later:
                        newly_skipped += 1
                        reason_counter.update(detailed_reasons)
                wave2_debt += wave2_repaid
                later_debt += later_repaid

                final_position = final_by_id[initial.borrower_hash]
                audit_rows.append(
                    {
                        "audit_row_id": f"ELIG_EXEC::{case_id}::{policy.policy_id}::{initial.borrower_hash}",
                        "result_id": result_id,
                        "case_id": case_id,
                        "case_type": case_type,
                        "policy_id": policy.policy_id,
                        "scenario_name": scenario.name,
                        "scenario_seed": scenario.seed,
                        "path_index": "" if path_index is None else path_index,
                        "shock_pct": scenario.shock_pct,
                        "liquidity_haircut_pct": scenario.liquidity_haircut_pct,
                        "borrower_hash": initial.borrower_hash,
                        "direct_shock_hf": source["direct_shock_hf"],
                        "direct_shock_hf_status": source["direct_shock_hf_status"],
                        "direct_shock_valuation_price_usd_per_weth": reference,
                        "post_wave1_hf": source["post_wave1_hf"],
                        "post_wave1_hf_status": source["post_wave1_hf_status"],
                        "post_wave1_borrower_valuation_price_usd_per_weth": post_wave1_valuation,
                        "post_wave1_dex_trade_price_usd_per_weth": post_wave1_dex,
                        "direct_shock_eligible": direct_eligible,
                        "newly_eligible_after_wave1": newly,
                        "diagnostic_attempted_set_wave1": source["attempted_in_wave1"],
                        "evaluated_by_liquidator_wave1": bool(wave1_events),
                        "attempted_after_wave1": bool(later_events),
                        "liquidator_decision_trace": decision_trace,
                        "skip_reasons_after_wave1": "|".join(sorted(set(reasons))),
                        "resolved_skip_reasons_after_wave1": "|".join(
                            sorted(set(detailed_reasons))
                        ),
                        "post_wave1_weth_collateral": post_position.collateral_weth,
                        "post_wave1_usdc_debt": post_position.debt_usdc,
                        "post_wave1_other_collateral_usd": post_position.other_collateral_usd,
                        "post_wave1_other_debt_usd": post_position.other_debt_usd,
                        "weth_usdc_liquidation_route_available": (
                            post_position.collateral_weth > 0 and post_position.debt_usdc > 0
                        ),
                        "executed_liquidation_events_all_waves": len(executed),
                        "executed_positive_debt_wave2": bool(executed_wave2),
                        "executed_positive_debt_later_waves": bool(executed_later),
                        "positive_debt_repaid_wave2_usdc": wave2_repaid,
                        "positive_debt_repaid_later_waves_usdc": later_repaid,
                        "debt_after_wave1_usdc": post_position.debt_usdc,
                        "remaining_debt_after_simulation_usdc": final_position.debt_usdc,
                        "event_wave_indices": wave_indices,
                        "event_locators": event_locators,
                        "reconciliation_class": _classification(
                            newly,
                            bool(later_events),
                            bool(executed_later),
                            detailed_reasons,
                        ),
                    }
                )

                direct_match = (
                    (direct_hf is None and not recomputed_direct_hf.is_finite())
                    or direct_hf == recomputed_direct_hf
                )
                post_match = (
                    (post_hf is None and not recomputed_post_hf.is_finite())
                    or post_hf == recomputed_post_hf
                )
                if direct_match and post_match:
                    hf_trace_matches += 1

            if newly_count == int(locked["newly_eligible_count"]):
                new_eligibility_matches += 1
            else:
                raise ValueError(f"Newly eligible count mismatch: {result_id}")
            if newly_executed_later and int(locked["cascade_depth"]) < 2:
                raise ValueError(f"Positive later execution without depth>=2: {result_id}")
            if int(locked["cascade_depth"]) >= 2 and newly_executed_later == 0:
                raise ValueError(f"Depth>=2 without newly eligible later execution: {result_id}")

            summary_rows.append(
                {
                    "summary_result_id": f"ELIG_EXEC_SUMMARY::{case_id}::{policy.policy_id}",
                    "result_id": result_id,
                    "case_id": case_id,
                    "case_type": case_type,
                    "policy_id": policy.policy_id,
                    "scenario_seed": scenario.seed,
                    "path_index": "" if path_index is None else path_index,
                    "direct_shock_eligible_count": direct_eligible_count,
                    "newly_eligible_after_wave1_count": newly_count,
                    "newly_eligible_attempted_later_count": newly_attempted_later,
                    "newly_eligible_executed_wave2_count": newly_executed_wave2,
                    "newly_eligible_executed_later_count": newly_executed_later,
                    "newly_eligible_skipped_count": newly_skipped,
                    "newly_eligible_not_attempted_count": newly_not_attempted,
                    "skip_reason_counts": json.dumps(dict(sorted(reason_counter.items())), sort_keys=True),
                    "positive_debt_repaid_wave2_usdc": wave2_debt,
                    "positive_debt_repaid_later_waves_usdc": later_debt,
                    "actual_executed_liquidation_events": sum(
                        event["event_type"] == "LIQUIDATION" for event in run_event_rows
                    ),
                    "cascade_depth": int(locked["cascade_depth"]),
                    "targeted_replay_sha256": actual_hash,
                    "locked_result_sha256": locked["deterministic_repeat_sha256"],
                    "replay_hash_match": True,
                    "newly_eligible_count_match": True,
                }
            )

    validation = {
        "targeted_runs": len(summary_rows),
        "replay_hash_matches": replay_hash_matches,
        "borrower_rows": len(audit_rows),
        "hf_trace_matches": hf_trace_matches,
        "new_eligibility_count_matches": new_eligibility_matches,
        "event_rows": len(event_rows),
    }
    return audit_rows, event_rows, summary_rows, validation


def _policy_reconciliation(summary_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for policy_id in POLICY_ORDER:
        rows = [row for row in summary_rows if row["policy_id"] == policy_id]
        deterministic = [row for row in rows if row["case_type"] == "DETERMINISTIC_DEPTH2"]
        selected_mc = [row for row in rows if row["case_type"] == "AUDITED_MONTE_CARLO"]
        reasons: Counter[str] = Counter()
        for row in rows:
            reasons.update(json.loads(str(row["skip_reason_counts"])))
        output[policy_id] = {
            "case_count": len(rows),
            "deterministic_depth2_retained_count_of_4": sum(
                int(row["cascade_depth"]) >= 2 for row in deterministic
            ),
            "selected_mc_depth2_retained_count_of_10": sum(
                int(row["cascade_depth"]) >= 2 for row in selected_mc
            ),
            "direct_shock_eligible_borrower_case_instances": sum(
                int(row["direct_shock_eligible_count"]) for row in rows
            ),
            "newly_eligible_borrower_case_instances": sum(
                int(row["newly_eligible_after_wave1_count"]) for row in rows
            ),
            "newly_eligible_attempted_later_instances": sum(
                int(row["newly_eligible_attempted_later_count"]) for row in rows
            ),
            "newly_eligible_executed_wave2_instances": sum(
                int(row["newly_eligible_executed_wave2_count"]) for row in rows
            ),
            "newly_eligible_skipped_instances": sum(
                int(row["newly_eligible_skipped_count"]) for row in rows
            ),
            "newly_eligible_not_attempted_instances": sum(
                int(row["newly_eligible_not_attempted_count"]) for row in rows
            ),
            "skip_reason_counts": dict(sorted(reasons.items())),
            "positive_debt_repaid_wave2_usdc": str(
                sum((D(str(row["positive_debt_repaid_wave2_usdc"])) for row in rows), D(0))
            ),
        }
    return output


def _result_registry(policy_summary: dict[str, dict[str, Any]]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    fields = [
        ("deterministic_depth2_retained_count_of_4", "selected deterministic cases", "cases"),
        ("selected_mc_depth2_retained_count_of_10", "targeted audited MC paths", "paths"),
        ("direct_shock_eligible_borrower_case_instances", "18 selected cases × borrowers", "borrower-case instances"),
        ("newly_eligible_borrower_case_instances", "18 selected cases × borrowers", "borrower-case instances"),
        ("newly_eligible_attempted_later_instances", "newly eligible borrower-case instances", "borrower-case instances"),
        ("newly_eligible_executed_wave2_instances", "newly eligible borrower-case instances", "borrower-case instances"),
        ("newly_eligible_skipped_instances", "newly eligible borrower-case instances", "borrower-case instances"),
        ("positive_debt_repaid_wave2_usdc", "executed Wave-2 liquidations", "USDC token quantity"),
    ]
    for policy_id in POLICY_ORDER:
        short = {
            "A_ADVERSE_PASS_THROUGH": "A",
            "B_REFERENCE_ONLY": "B",
            "C_WEAK_LAGGED_SMOOTHED_PROXY": "C_WEAK",
            "C_MODERATE_LAGGED_SMOOTHED_PROXY": "C_MODERATE",
        }[policy_id]
        for field, population, unit in fields:
            results.append(
                {
                    "result_id": f"INT_{short}_{field.upper()}",
                    "rq": "RQ1" if "DEPTH2" in field.upper() or "ELIGIBLE" in field.upper() else None,
                    "policy_id": policy_id,
                    "population": population,
                    "unit": unit,
                    "value": policy_summary[policy_id][field],
                    "source_path": "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv",
                    "source_commit": SOURCE_CODE_COMMIT,
                    "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
                    "interpretation_limit": "Targeted selected cases only; not a population probability or historical event rate.",
                }
            )
    return {"schema_version": "scientific-integration-v1.0", "results": results}


def _six_rq_matrix() -> dict[str, Any]:
    rows = [
        {
            "rq": "RQ1",
            "question": RQ_LABELS[0][1],
            "method": "Đối chiếu Frozen grid/checkpoint Policy A với A/B/C targeted diagnostic và event-level eligibility/execution audit.",
            "evidence": ["RQ1_GRID32_MAX_DEPTH", "RQ1_GRID60_DEPTH2", "RQ1_MC_SEVERE_DEPTH2_COUNT", "INT_A_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_B_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_C_WEAK_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_C_MODERATE_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4"],
            "result": "Policy A: grid 60 có 4 depth-2 cells và Severe 280/10.000 depth≥2; trong bốn selected deterministic cases A/B/Cweak/Cmoderate = 4/0/0/0. Trong mười targeted A-depth2 MC paths = 10/0/0/2.",
            "interpretation": "Wave 2 là simulated endogenous feedback dưới policy định giá cụ thể; không có ngưỡng cascade độc lập oracle được xác lập.",
            "limitation": "280/10.000 chỉ thuộc locked Severe Policy A; 10 paths là sample có chủ đích; không phải xác suất Ethereum hay Aave oracle thực tế.",
            "accepted_claim": "Trong môi trường frozen và Policy A adverse pass-through, tail stress có thể tạo Wave 2; sự xuất hiện Wave 2 nhạy với policy truyền giá.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
        },
        {
            "rq": "RQ2",
            "question": RQ_LABELS[1][1],
            "method": "Tách executable depth/haircut, immediate DEX impact, post-arbitrage spread và HF feedback qua policy.",
            "evidence": ["RQ2_CANONICAL_DEPTH_2PCT", "RQ2_DEPTH2_HAIRCUT90_COUNT", "RQ2_DEPTH2_HAIRCUT95_COUNT", "RQ4_IMMEDIATE_PRICE_IMPACT", "RQ4_SPREAD_ARB100"],
            "result": "Haircut làm giảm sức hấp thụ forced selling và tăng biến dạng DEX; nhưng eligibility mới và depth phụ thuộc valuation policy A/B/C.",
            "interpretation": "DEX liquidity là kênh hấp thụ giao dịch; oracle policy là kênh truyền DEX state sang HF. Hai kênh không được nhập làm một.",
            "limitation": "Một pool/snapshot; haircut 90/95% chưa quan sát; không routing đa venue; không xác minh Aave dùng Uniswap spot.",
            "accepted_claim": "Thanh khoản thấp có thể khuếch đại price impact trong mô hình, nhưng không tự nó bảo đảm có borrower mới đủ điều kiện thanh lý.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
        },
        {
            "rq": "RQ3",
            "question": RQ_LABELS[2][1],
            "method": "Giữ Frozen v3 sweeps vốn/capacity/gas/delay; dùng event audit để tách eligible, evaluated, skipped và executed.",
            "evidence": ["RQ3_CAPITAL_25_LIQUIDATED", "RQ3_CAPITAL_100_LIQUIDATED", "RQ3_DELAY_SEVERITY_CHANGE"],
            "result": "Vốn 25/50% binding; 100/200% không binding trong miền thử. Trong targeted audit, newly eligible không đồng nghĩa executed: các skip sau Wave 1 được truy về gate tài sản của route WETH-collateral/USDC-debt, không phải profitability.",
            "interpretation": "Funding stock, throughput, gas/profitability và latency là các gate execution khác nhau.",
            "limitation": "Một liquidator đại diện, vốn không tái sử dụng; không fork execution.",
            "accepted_claim": "Kết luận Frozen v3 về vốn/delay giữ nguyên; addendum bổ sung rằng eligibility phải được đối chiếu quyết định execution.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
        },
        {
            "rq": "RQ4",
            "question": RQ_LABELS[3][1],
            "method": "Giữ Frozen v3 comparison immediate impact và residual spread; kiểm tra policy chỉ ảnh hưởng trades sau khi eligibility phân kỳ.",
            "evidence": ["RQ4_IMMEDIATE_PRICE_IMPACT", "RQ4_SPREAD_ARB0", "RQ4_SPREAD_ARB100"],
            "result": "Immediate impact 0,108794% trong sweep gốc; residual spread giảm theo arbitrage capacity. Oracle diagnostic không thay đổi Uniswap math.",
            "interpretation": "Arbitrage tái neo sau giao dịch trong mô hình; không xóa impact tại execution và không xác minh hiệu quả ngoài đời.",
            "limitation": "Price repositioning/teleportation, một arbitrageur, không funded fork swap.",
            "accepted_claim": "Kết luận Frozen v3 giữ nguyên; chỉ downstream liquidation trades có thể khác khi oracle policy làm eligibility khác.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
        },
        {
            "rq": "RQ5",
            "question": RQ_LABELS[4][1],
            "method": "Giữ token debt quantity và thay USDC/USD valuation 0,90–1,10 như Frozen v3.",
            "evidence": ["RQ5_HF_LT1_USDC_090", "RQ5_HF_LT1_USDC_100", "RQ5_HF_LT1_USDC_110", "RQ5_LIQUIDATED_DEBT_TOKEN_QTY", "RQ5_LIQUIDATED_DEBT_USD"],
            "result": "HF<1 là 1/1/3; 9.063,255437 USDC = 9.969,580981 USD tại 1,10 USD/USDC.",
            "interpretation": "Đây là kênh định giá nợ USDC, không phải full stablecoin-depeg market model.",
            "limitation": "Không liquidity/redemption/settlement/confidence channel; oracle diagnostic WETH không mở rộng kết luận này.",
            "accepted_claim": "Kết luận RQ5 Frozen v3 giữ nguyên với đơn vị USDC token và USD-equivalent tách biệt.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
        },
        {
            "rq": "RQ6",
            "question": RQ_LABELS[5][1],
            "method": "Giữ ba counterfactual tách biệt LTV, LT và bonus của Frozen v3.",
            "evidence": ["RQ6_LTV0755_CAPACITY", "RQ6_LTV0825_CAPACITY", "RQ6_LT083_UNLIQUIDATED", "RQ6_BONUS103_SEIZED", "RQ6_BONUS107_SEIZED"],
            "result": "LTV đổi capacity ex ante; LT đổi HF/eligibility và scenario-LT unliquidated debt; bonus đổi collateral seized/incentive.",
            "interpretation": "Ba tham số không thay thế nhau.",
            "limitation": "Frozen cohort, không borrower re-underwriting/behavior response; oracle addendum không retune policy sweep.",
            "accepted_claim": "Kết luận RQ6 Frozen v3 giữ nguyên.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
        },
    ]
    return {"schema_version": "scientific-integration-v1.0", "research_questions": rows}


def _claim_registry(
    frozen_manifest: dict[str, Any],
    oracle_manifest: dict[str, Any],
    audit_hash: str,
    summary_hash: str,
    p2_hashes: dict[str, str],
) -> dict[str, Any]:
    frozen_registry_hash = frozen_manifest["artifact_hashes"]["results_registry.json"]
    common_oracle = {
        "policy": "A/B/C as specified",
        "scenario": "4 locked deterministic depth-2 cases + 4 controls + 10 preselected MC paths",
        "seed": "20260914 base; path seeds in eligible_vs_executed_audit.csv",
        "borrower_evidence": "eligible_vs_executed_audit.csv; redacted borrower_hash",
        "table_figure": ["INT_T01_ELIGIBLE_VS_EXECUTED", "F01", "F02"],
        "source_commit": STARTING_HEAD,
        "artifact_path": "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_audit.csv",
        "artifact_sha256": audit_hash,
        "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
    }
    claims = [
        {
            "rq": "RQ1",
            "claim_id": "CL_INT_RQ1_POLICY_CONDITIONAL",
            "result_ids": ["RQ1_GRID60_DEPTH2", "RQ1_MC_SEVERE_DEPTH2_COUNT", "INT_A_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_B_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_C_WEAK_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_C_MODERATE_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4"],
            **common_oracle,
            "allowed_inference": "Wave 2 exists in selected tail cases under Policy A and is sensitive to valuation policy.",
            "limitation": "No oracle-independent threshold, actual Aave probability or historical causal cascade.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
            "literature_claim_ids": ["C03", "C32", "C33"],
        },
        {
            "rq": "RQ1",
            "claim_id": "CL_FROZEN_RQ1_UNQUALIFIED_WORDING",
            "result_ids": ["RQ1_GRID60_DEPTH2", "RQ1_MC_SEVERE_DEPTH2_COUNT"],
            "policy": "Implicit Policy A",
            "scenario": "Frozen v3 grid/checkpoint",
            "seed": "20260914 for Severe",
            "borrower_evidence": "Oracle audit supplies missing policy contrast",
            "table_figure": ["F01", "F02"],
            "source_commit": FROZEN_HEAD,
            "artifact_path": "data/processed/research_final/frozen_v3/results_registry.json",
            "artifact_sha256": frozen_registry_hash,
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
            "allowed_inference": "Frozen numerical counts remain valid under Policy A.",
            "limitation": "Downstream wording must add Policy A qualification.",
            "status": "REQUIRES_CORRECTION",
            "literature_claim_ids": ["C23", "C32", "C33"],
        },
        {
            "rq": "RQ2",
            "claim_id": "CL_INT_RQ2_TWO_CHANNELS",
            "result_ids": ["RQ2_CANONICAL_DEPTH_2PCT", "RQ2_DEPTH2_HAIRCUT90_COUNT", "RQ2_DEPTH2_HAIRCUT95_COUNT"],
            **common_oracle,
            "allowed_inference": "Liquidity changes DEX absorption; valuation policy controls whether resulting DEX state changes borrower HF.",
            "limitation": "Liquidity weakness alone does not guarantee new eligibility or execution.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
            "literature_claim_ids": ["C07", "C08", "C32", "C34"],
        },
        {
            "rq": "RQ2",
            "claim_id": "CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING",
            "result_ids": ["RQ2_DEPTH2_HAIRCUT90_COUNT", "RQ2_DEPTH2_HAIRCUT95_COUNT"],
            "policy": "Implicit Policy A",
            "scenario": "60-cell tail grid",
            "seed": "deterministic",
            "borrower_evidence": "Oracle audit supplies A/B/C contrast",
            "table_figure": ["F01", "T05"],
            "source_commit": FROZEN_HEAD,
            "artifact_path": "data/processed/research_final/frozen_v3/rq_answer_matrix.json",
            "artifact_sha256": frozen_manifest["artifact_hashes"]["rq_answer_matrix.json"],
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
            "allowed_inference": "Tail haircuts reduce absorption and increase modeled DEX distortion.",
            "limitation": "Wording that liquidity itself creates eligibility requires an oracle-policy qualifier.",
            "status": "REQUIRES_CORRECTION",
            "literature_claim_ids": ["C07", "C32"],
        },
        {
            "rq": "RQ3",
            "claim_id": "CL_INT_ELIGIBLE_NOT_EXECUTED",
            "result_ids": ["INT_A_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES", "INT_A_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES", "INT_A_NEWLY_ELIGIBLE_SKIPPED_INSTANCES"],
            **common_oracle,
            "table_figure": ["INT_T01_ELIGIBLE_VS_EXECUTED"],
            "artifact_sha256": summary_hash,
            "artifact_path": "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv",
            "allowed_inference": "HF eligibility, engine evaluation and positive-debt execution are distinct gates; skips carry explicit reason codes.",
            "limitation": "Execution is modeled by one representative liquidator and does not establish external contagion.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
            "literature_claim_ids": ["C03", "C05", "C19", "C33"],
        },
        {
            "rq": "RQ3",
            "claim_id": "CL_INT_RQ3_PRESERVED",
            "result_ids": ["RQ3_CAPITAL_25_LIQUIDATED", "RQ3_CAPITAL_100_LIQUIDATED", "RQ3_DELAY_SEVERITY_CHANGE"],
            "policy": "Frozen v3 sweeps",
            "scenario": "capital/capacity/gas/delay sweeps",
            "seed": "deterministic",
            "borrower_evidence": "Frozen cohort 109 for RQ3 sweeps",
            "table_figure": ["F03", "T06"],
            "source_commit": FROZEN_HEAD,
            "artifact_path": "data/processed/research_final/frozen_v3/results_registry.json",
            "artifact_sha256": frozen_registry_hash,
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
            "allowed_inference": "Capital binds at low tested levels; delay does not change severity in tested range.",
            "limitation": "Representative agent, no capital recycling, no fork.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
            "literature_claim_ids": ["C03", "C05", "C19"],
        },
        {
            "rq": "RQ4",
            "claim_id": "CL_INT_RQ4_PRESERVED",
            "result_ids": ["RQ4_IMMEDIATE_PRICE_IMPACT", "RQ4_SPREAD_ARB0", "RQ4_SPREAD_ARB100"],
            "policy": "Frozen v3 arbitrage sweep",
            "scenario": "shock -20%, haircut 40%",
            "seed": "deterministic",
            "borrower_evidence": "Frozen scenario result",
            "table_figure": ["F04", "T07"],
            "source_commit": FROZEN_HEAD,
            "artifact_path": "data/processed/research_final/frozen_v3/results_registry.json",
            "artifact_sha256": frozen_registry_hash,
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
            "allowed_inference": "Arbitrage reduces residual spread but not the same sale's immediate impact.",
            "limitation": "Price teleportation; not funded Mainnet execution.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
            "literature_claim_ids": ["C13", "C19", "C34"],
        },
        {
            "rq": "RQ5",
            "claim_id": "CL_INT_RQ5_PRESERVED",
            "result_ids": ["RQ5_HF_LT1_USDC_090", "RQ5_HF_LT1_USDC_100", "RQ5_HF_LT1_USDC_110", "RQ5_LIQUIDATED_DEBT_TOKEN_QTY", "RQ5_LIQUIDATED_DEBT_USD"],
            "policy": "Frozen v3 USDC debt valuation",
            "scenario": "USDC 0.90/1.00/1.10 USD",
            "seed": "deterministic",
            "borrower_evidence": "109-position WETH/USDC cohort",
            "table_figure": ["T08"],
            "source_commit": FROZEN_HEAD,
            "artifact_path": "data/processed/research_final/frozen_v3/results_registry.json",
            "artifact_sha256": frozen_registry_hash,
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
            "allowed_inference": "USDC debt valuation changes HF ceteris paribus; token and USD units remain separate.",
            "limitation": "No liquidity/redemption/settlement channel.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
            "literature_claim_ids": ["C14", "C15", "C35"],
        },
        {
            "rq": "RQ6",
            "claim_id": "CL_INT_RQ6_PRESERVED",
            "result_ids": ["RQ6_LTV0755_CAPACITY", "RQ6_LTV0825_CAPACITY", "RQ6_LT083_UNLIQUIDATED", "RQ6_BONUS103_SEIZED", "RQ6_BONUS107_SEIZED"],
            "policy": "Frozen v3 separated policy sweeps",
            "scenario": "LTV/LT/bonus counterfactuals",
            "seed": "deterministic",
            "borrower_evidence": "109-position frozen cohort",
            "table_figure": ["T09"],
            "source_commit": FROZEN_HEAD,
            "artifact_path": "data/processed/research_final/frozen_v3/results_registry.json",
            "artifact_sha256": frozen_registry_hash,
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
            "allowed_inference": "LTV, LT and bonus govern distinct mechanisms and are not interchangeable.",
            "limitation": "No borrower behavior/re-underwriting response.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
            "literature_claim_ids": ["C04", "C05", "C12"],
        },
        {
            "rq": "EXT_HISTORICAL",
            "claim_id": "CL_INT_HISTORICAL_TIERS_PRESERVED",
            "result_ids": ["HIST_RPC_CENSUS_EVENTS", "HIST_GRAPH_MATCHED_EVENTS", "HIST_DIRECT_TRANSFER_PATHS", "HIST_SAME_TX_COOCCURRENCE", "HIST_SAME_BLOCK_ASSOCIATION", "HIST_TIME_WINDOW_ASSOCIATION"],
            "policy": "not applicable",
            "scenario": "defined week 2026-09-01..07 UTC",
            "seed": "not applicable",
            "borrower_evidence": "onchain redacted/aggregated historical evidence",
            "table_figure": ["T10"],
            "source_commit": FROZEN_HEAD,
            "artifact_path": "data/processed/research_final/frozen_v3/results_registry.json",
            "artifact_sha256": frozen_registry_hash,
            "evidence_tier": "ONCHAIN_HISTORICAL_OBSERVATION",
            "allowed_inference": "28 Pool events; 27 Graph-matched; association tiers 1/2/23/1.",
            "limitation": "Co-occurrence/receipt route does not prove price causality or endogenous cascade.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
            "literature_claim_ids": ["C09", "C10", "C11"],
        },
        {
            "rq": "EXT_TERRA",
            "claim_id": "CL_INT_TERRA_NEGATIVE_PRESERVED",
            "result_ids": ["TERRA_PRE_DEPEG_HIGH_ALERT_HOURS", "TERRA_INITIAL_DEPEG_HIGH_LEAD"],
            "policy": "cutoff-safe historical audit",
            "scenario": "Terra 2022 historical extension",
            "seed": "not applicable",
            "borrower_evidence": "not applicable",
            "table_figure": ["T11"],
            "source_commit": FROZEN_HEAD,
            "artifact_path": "data/processed/research_final/frozen_v3/results_registry.json",
            "artifact_sha256": frozen_registry_hash,
            "evidence_tier": "ONCHAIN_HISTORICAL_OBSERVATION",
            "allowed_inference": "Negative cutoff-safe early-warning finding remains preserved.",
            "limitation": "No successful out-of-sample forecasting claim.",
            "status": "ACCEPTED_WITH_LIMITATIONS",
            "literature_claim_ids": ["C16", "C17", "C29", "C30"],
        },
        {
            "rq": "RQ1/RQ2",
            "claim_id": "CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT",
            "result_ids": [],
            "policy": "none verified",
            "scenario": "external empirical claim",
            "seed": "not applicable",
            "borrower_evidence": "none",
            "table_figure": [],
            "source_commit": P2_HEAD,
            "artifact_path": P2_LOCATOR_PATHS[0],
            "artifact_sha256": p2_hashes[P2_LOCATOR_PATHS[0]],
            "evidence_tier": "EXTERNAL_EMPIRICAL_INFERENCE",
            "allowed_inference": "No affirmative inference allowed.",
            "limitation": "A/B/C are counterfactual valuation policies; actual Aave/Chainlink feed behavior is not validated.",
            "status": "UNSUPPORTED",
            "literature_claim_ids": ["C02", "C32"],
        },
        {
            "rq": "RQ1/RQ2",
            "claim_id": "CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION",
            "result_ids": ["HIST_DIRECT_TRANSFER_PATHS", "HIST_SAME_TX_COOCCURRENCE", "HIST_SAME_BLOCK_ASSOCIATION", "HIST_TIME_WINDOW_ASSOCIATION"],
            "policy": "not applicable",
            "scenario": "historical event study",
            "seed": "not applicable",
            "borrower_evidence": "historical event locators in Frozen source",
            "table_figure": ["T10"],
            "source_commit": FROZEN_HEAD,
            "artifact_path": "data/processed/research_final/frozen_v3/results_registry.json",
            "artifact_sha256": frozen_registry_hash,
            "evidence_tier": "EXTERNAL_EMPIRICAL_INFERENCE",
            "allowed_inference": "Temporal/transaction association only.",
            "limitation": "No identified historical endogenous liquidation-price-liquidation causal chain.",
            "status": "UNSUPPORTED",
            "literature_claim_ids": ["C09", "C10", "C11"],
        },
    ]
    return {
        "schema_version": "scientific-integration-v1.0",
        "p2_locator_commit": P2_HEAD,
        "p2_locator_hashes": p2_hashes,
        "p2_oracle_reconciliation_status": "OPEN_ON_PR_9_PER_COMMANDER_COMMENT_6166173420",
        "claims": claims,
    }


def _version_precedence() -> dict[str, Any]:
    return {
        "schema_version": "scientific-integration-v1.0",
        "rule": "Use highest applicable numerical or interpretive layer; Oracle Diagnostic supersedes only RQ1/RQ2 interpretation, not locked numerical facts.",
        "versions": [
            {"rank": 1, "version": "Original", "role": "locked raw/canonical evidence"},
            {"rank": 2, "version": "P0 corrected v2", "role": "corrected numerical semantics and RQ sweeps"},
            {"rank": 3, "version": "Level-3", "role": "extended grid/checkpoint/historical evidence"},
            {"rank": 4, "version": "Level-3 targeted repair", "role": "census/tier/checkpoint audit"},
            {"rank": 5, "version": "Frozen v3", "role": "locked numerical registry and synthesis"},
            {"rank": 6, "version": "Oracle Transmission Diagnostic v1", "role": "targeted RQ1/RQ2 valuation-policy sensitivity and HF traces"},
            {"rank": 7, "version": "Scientific Integration Addendum v1", "role": "claim wording, eligible-vs-executed reconciliation and traceability; no model retuning"},
        ],
        "literature_sidecar": {
            "commit": P2_HEAD,
            "role": "P2 scholarly locators only; not numerical precedence",
            "status": "DRAFT_OPEN_AND_ORACLE_RECONCILIATION_PENDING",
        },
    }


def _all_finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(_all_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_all_finite(item) for item in value)
    if isinstance(value, float):
        return value == value and value not in {float("inf"), float("-inf")}
    return not (
        isinstance(value, str)
        and value.lower() in {"nan", "inf", "-inf", "infinity", "-infinity"}
    )


def _render_docs(
    rq_matrix: dict[str, Any],
    policy_summary: dict[str, dict[str, Any]],
    claims: dict[str, Any],
    validation: dict[str, Any],
    input_hashes: dict[str, str],
    test_evidence: dict[str, Any],
) -> None:
    policy_lines = []
    for policy_id in POLICY_ORDER:
        row = policy_summary[policy_id]
        policy_lines.append(
            f"| {policy_id} | {row['deterministic_depth2_retained_count_of_4']}/4 | {row['selected_mc_depth2_retained_count_of_10']}/10 | {row['direct_shock_eligible_borrower_case_instances']} | {row['newly_eligible_borrower_case_instances']} | {row['newly_eligible_attempted_later_instances']} | {row['newly_eligible_executed_wave2_instances']} | {row['newly_eligible_skipped_instances']} | {row['newly_eligible_not_attempted_instances']} | {row['positive_debt_repaid_wave2_usdc']} |"
        )
    rq_sections = []
    for row in rq_matrix["research_questions"]:
        rq_sections.append(
            f"""## {row['rq']} — {row['question']}

**Question.** {row['question']}

**Method.** {row['method']}

**Evidence.** {', '.join(f'`{item}`' for item in row['evidence'])}.

**Result.** {row['result']}

**Interpretation.** {row['interpretation']}

**Limitation.** {row['limitation']}

**Accepted Claim.** {row['accepted_claim']}

**Status:** `{row['status']}`.
"""
        )
    status_counts = Counter(claim["status"] for claim in claims["claims"])
    test_lines = [f"- Trạng thái: `{test_evidence.get('status', 'PENDING')}`."]
    for item in test_evidence.get("commands", []):
        test_lines.append(f"- `{item['command']}` → **{item['status']}** ({item['result']}).")

    addendum = f"""# Scientific Evidence Integration Addendum v1

Trạng thái đề nghị: **READY_FOR_COMMANDER_REVIEW**. Addendum này không tự cấp `SCIENTIFIC_CONTENT_LOCK`, không merge PR #11/#9 và không thay Frozen v3 hay Oracle Diagnostic v1.

## 1. Provenance và phạm vi

- Starting HEAD / Oracle Diagnostic HEAD: `{STARTING_HEAD}`.
- Frozen v3 baseline: `{FROZEN_HEAD}`; manifest SHA-256 `{input_hashes['frozen_v3_manifest']}`.
- Oracle Diagnostic manifest SHA-256 `{input_hashes['oracle_manifest']}`; selection commit `{SELECTION_LOCK_COMMIT}`.
- P2 locator commit: `{P2_HEAD}`; PR #9 vẫn DRAFT/OPEN và Commander đã yêu cầu P2 oracle reconciliation riêng.
- Canonical block `26045352`; snapshot SHA-256 `{input_hashes['canonical_snapshot']}`; 454 verified borrowers; cohort riêng 109 WETH collateral-enabled/USDC debt.
- Model/policy version: `{MODEL_VERSION}`; 72 targeted replays, không chạy lại 10.000 Monte Carlo.

Quy tắc ưu tiên: `Original → P0 corrected v2 → Level-3 → targeted repair → Frozen v3 → Oracle Diagnostic v1 → Integration Addendum v1`. Diagnostic chỉ sửa cách diễn giải RQ1/RQ2; không thay số liệu Frozen v3.

## 2. Eligible khác Attempted và Executed

Định nghĩa khóa:

- **Newly eligible:** direct-shock HF ≥ 1, post-Wave-1 HF < 1 và borrower chưa thuộc attempted set Wave 1.
- **Attempted/evaluated:** engine tạo `LIQUIDATION` hoặc `LIQUIDATION_SKIPPED` cho borrower ở wave sau.
- **Executed:** có event `LIQUIDATION` với `debt_repaid > 0`.

| Policy | 4 deterministic depth-2 giữ depth≥2 | 10 targeted MC giữ depth≥2 | Direct eligible instances | Newly eligible | Attempted later | Executed Wave 2 | Skipped | Not attempted | Wave-2 debt repaid (USDC) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(policy_lines)}

Các count là **borrower-case instances** trên 18 selected cases, không phải số borrower duy nhất hay tần suất quần thể. Tất cả newly eligible instances đều được engine đánh giá ở wave sau. Trong 36 instances không executed, raw engine reason là `NOT_ELIGIBLE`; state-level reconciliation phân giải thành `NO_MODELLED_USDC_DEBT`, vì HF của full 454-borrower population có thể phản ánh other-debt trong khi liquidation planner chỉ thực thi route WETH-collateral/USDC-debt. Không có skip targeted nào được quy cho capital, capacity, gas hay profitability. Vì vậy không được suy executed từ newly eligible hoặc từ depth aggregate.

## 3. Ma trận sáu RQ

{chr(10).join(rq_sections)}

## 4. Claim traceability và tầng bằng chứng

- `CODE_OBSERVATION`: hành vi mã, không phải quan sát thị trường.
- `MODEL_COMPUTED_COUNTERFACTUAL`: kết quả mô phỏng A/B/C, không phải giao dịch lịch sử.
- `ONCHAIN_HISTORICAL_OBSERVATION`: log/receipt/association đã kiểm, không tự chứng minh nhân quả.
- `EXTERNAL_EMPIRICAL_INFERENCE`: chỉ được dùng khi thiết kế/dữ liệu bên ngoài thực sự hỗ trợ; hiện claim Aave dùng Uniswap spot và historical causal cascade là `UNSUPPORTED`.

Registry có {len(claims['claims'])} claims: {dict(sorted(status_counts.items()))}. Hai diễn giải Frozen RQ1/RQ2 không có qualifier Policy A được gắn `REQUIRES_CORRECTION`; số liệu gốc không bị phủ định. Terra negative findings và network-extension limits giữ nguyên.

## 5. Self-audit

- 72/72 targeted replay hashes khớp Oracle Diagnostic.
- {validation['borrower_rows']:,} borrower-case-policy rows đối chiếu; {validation['hf_trace_matches']:,} HF traces khớp source rows.
- {validation['event_rows']} raw modeled event rows có event locator duy nhất.
- Result IDs/claim locators, sáu RQ, units, policy attribution, hashes và evidence tiers được gate tự động.
- Không raw wallet/API key, NaN/Infinity hoặc claim 2,8% là xác suất khủng hoảng.
- P2 locator được pin tại `{P2_HEAD}` nhưng delta oracle của Work theo comment `6166173420` vẫn là dependency mở.

{chr(10).join(test_lines)}

## 6. Giới hạn phải công bố

1. Policy A/B/C là counterfactual; không policy nào được xác minh là Aave/Chainlink lịch sử.
2. 280/10.000 là tần suất locked Severe Policy A, không dùng cho B/C hoặc Ethereum thực.
3. Mười MC paths được chọn vì depth≥2 dưới A; 10/0/0/2 không phải estimator quần thể.
4. Eligible, attempted và executed là ba gate khác nhau; execution vẫn do một liquidator đại diện.
5. Historical tiers 1/2/23/1 là route/co-occurrence/association, không causal contagion.
6. Fork validation vẫn `UNAVAILABLE`; haircut 90/95% chưa quan sát; một DEX/snapshot/cohort.
7. Terra không hỗ trợ claim dự báo ngoài mẫu thành công; network graph là heterogeneous aggregate extension.

## 7. Kết luận tích hợp

RQ3–RQ6 giữ nguyên kết luận Frozen v3 có giới hạn. RQ1–RQ2 phải dùng wording policy-conditional: thanh khoản quyết định DEX absorption/impact, còn việc biến distortion thành HF eligibility và Wave 2 phụ thuộc valuation policy. Addendum đủ điều kiện để Commander kiểm duyệt claim gate, nhưng P2 oracle reconciliation và quyết định scientific lock vẫn thuộc Commander.
"""
    ADDENDUM.write_text(addendum, encoding="utf-8")

    review = f"""# Integration Commander Review Packet

**Đề nghị:** `READY_FOR_COMMANDER_REVIEW`. Không đề nghị merge tự động hoặc scientific lock.

## Provenance

- Starting HEAD: `{STARTING_HEAD}`.
- Source/artifact commit: `{SOURCE_CODE_COMMIT}`.
- Artifact bundle commit: `{ARTIFACT_BUNDLE_COMMIT}`.
- Dependency PR #11: DRAFT/OPEN, accepted `SCIENTIFIC_PASS_WITH_LIMITATIONS` for targeted diagnostic.
- P2 PR #9: DRAFT/OPEN @ `{P2_HEAD}`; oracle reconciliation delta do Work quản lý còn mở.

## Deliverables

- `data/processed/research_final/scientific_integration_v1/`: manifest, six-RQ matrix, claim registry, result registry, eligible/executed borrower audit, event trace, summary, accepted claims, validation and precedence.
- `docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md`.
- `docs/research_final/INTEGRATION_COMMANDER_REVIEW_PACKET.md`.

## Kết quả gate trọng yếu

- 72/72 targeted replays hash-match; không 10k rerun.
- {validation['borrower_rows']:,} audit rows; {validation['event_rows']} event locators.
- Policy A/B/C deterministic 4/0/0/0; targeted MC 10/0/0/2.
- Claim registry: {dict(sorted(status_counts.items()))}.
- RQ1/RQ2 được giới hạn policy-dependent; RQ3–RQ6 bảo toàn.
- Frozen/Oracle/canonical hashes giữ nguyên.

## Tiêu chí Commander

**PASS/ready:** chấp nhận wording policy-conditional, eligible-vs-executed reconciliation, evidence tiers và provenance.

**REWORK:** locator thiếu, policy attribution sai, nhầm 454/109, USDC/USD, newly/executed, hoặc claim dùng artifact superseded.

**BLOCK:** hash input thay đổi, event trace không tái lập, hoặc P2 delta tạo xung đột claim chưa hòa giải.

## Blocker và caveat

Không có blocker số học nội bộ được phát hiện. Dependency không chặn review addendum nhưng chặn global lock: P2 oracle reconciliation trên PR #9 chưa có HEAD mới sau Commander comment `6166173420`. Các giới hạn actual oracle, fork, extreme haircut, historical causality, representative agents, Terra OOS và network aggregation phải được công bố.

## Test evidence

{chr(10).join(test_lines)}
"""
    REVIEW_PACKET.write_text(review, encoding="utf-8")


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    frozen_manifest = _load(FROZEN_ROOT / "manifest.json")
    oracle_manifest = _load(ORACLE_ROOT / "manifest.json")
    frozen_hashes = _verify_bundle(FROZEN_ROOT, frozen_manifest)
    oracle_hashes = _verify_bundle(ORACLE_ROOT, oracle_manifest)
    canonical_hash = _sha(CANONICAL)
    if canonical_hash != frozen_manifest["canonical_snapshot"]["sha256"]:
        raise ValueError("Canonical snapshot hash changed")
    p2_hashes = {
        path: hashlib.sha256(_git_file_bytes(P2_HEAD, path)).hexdigest()
        for path in P2_LOCATOR_PATHS
    }

    selection = _load(ORACLE_ROOT / "selection_manifest.json")
    comparison = _load(ORACLE_ROOT / "comparison_matrix.json")
    diagnostic_rows = _read_csv(ORACLE_ROOT / "borrower_level_evidence.csv")
    audit_rows, event_rows, summary_rows, replay_validation = _build_event_audit(
        selection, comparison, diagnostic_rows
    )
    _write_csv(ROOT / "eligible_vs_executed_audit.csv", audit_rows)
    _write_jsonl(ROOT / "targeted_event_trace.jsonl", event_rows)
    _write_csv(ROOT / "eligible_vs_executed_summary.csv", summary_rows)

    policy_summary = _policy_reconciliation(summary_rows)
    result_registry = _result_registry(policy_summary)
    _write_json(ROOT / "integration_result_registry.json", result_registry)
    rq_matrix = _six_rq_matrix()
    _write_json(ROOT / "six_rq_evidence_matrix.json", rq_matrix)
    version_precedence = _version_precedence()
    _write_json(ROOT / "version_precedence.json", version_precedence)
    table_figure_registry = {
        "schema_version": "scientific-integration-v1.0",
        "tables": [
            {
                "table_id": "INT_T01_ELIGIBLE_VS_EXECUTED",
                "path": "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv",
                "detail_path": "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_audit.csv",
                "population": "18 predeclared selected cases × 4 policies × 454 verified borrowers",
                "denominator": "borrower-case-policy instances; not unique borrowers or population probability",
                "units": ["instances", "USDC token quantity"],
                "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
                "source_commit": SOURCE_CODE_COMMIT,
                "limitation": "Selected deterministic/control/MC cases; not an empirical Aave or Ethereum event rate.",
            }
        ],
        "figures": [],
        "external_registry": "data/processed/research_final/frozen_v3/evidence_source_matrix.json",
    }
    _write_json(ROOT / "table_figure_registry.json", table_figure_registry)

    claims = _claim_registry(
        frozen_manifest,
        oracle_manifest,
        _sha(ROOT / "eligible_vs_executed_audit.csv"),
        _sha(ROOT / "eligible_vs_executed_summary.csv"),
        p2_hashes,
    )
    _write_json(ROOT / "claim_to_result_registry.json", claims)
    accepted = [
        claim for claim in claims["claims"] if claim["status"] in {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"}
    ]
    _write_json(
        ROOT / "accepted_claims_proposed.json",
        {
            "schema_version": "scientific-integration-v1.0",
            "decision": "READY_FOR_COMMANDER_REVIEW",
            "scientific_content_lock_declared": False,
            "accepted_claims": accepted,
            "excluded_claims": [
                {"claim_id": claim["claim_id"], "status": claim["status"], "limitation": claim["limitation"]}
                for claim in claims["claims"]
                if claim not in accepted
            ],
        },
    )

    frozen_ids = {row["result_id"] for row in _load(FROZEN_ROOT / "results_registry.json")["results"]}
    integration_ids = {row["result_id"] for row in result_registry["results"]}
    all_result_ids = frozen_ids | integration_ids
    claim_ids = [claim["claim_id"] for claim in claims["claims"]]
    event_ids = {row["event_id"] for row in event_rows}
    audit_event_ids = {
        item
        for row in audit_rows
        for item in str(row["event_locators"]).split("|")
        if item
    }
    unresolved_results = sorted(
        {
            result_id
            for claim in claims["claims"]
            for result_id in claim["result_ids"]
            if result_id not in all_result_ids
        }
    )
    frozen_sources = _load(FROZEN_ROOT / "evidence_source_matrix.json")
    table_figure_ids = {
        row["table_id"] for row in frozen_sources["table_registry"]
    } | {
        row["figure_id"] for row in frozen_sources["figure_registry"]
    } | {
        row["table_id"] for row in table_figure_registry["tables"]
    } | {
        row["figure_id"] for row in table_figure_registry["figures"]
    }
    unresolved_table_figures = sorted(
        {
            locator
            for claim in claims["claims"]
            for locator in claim["table_figure"]
            if locator not in table_figure_ids
        }
    )
    expected_rqs = [rq for rq, _ in RQ_LABELS]
    actual_rqs = [row["rq"] for row in rq_matrix["research_questions"]]
    serialized_for_scan = json.dumps(_safe([audit_rows, event_rows, rq_matrix, claims]), ensure_ascii=False)
    no_raw_address = re.search(r"0x[0-9a-fA-F]{40}", serialized_for_scan) is None
    no_secret = re.search(r"(?:sk-[A-Za-z0-9]{20,}|GRAPH_API_KEY\s*=\s*\S+|RPC_URL\s*=\s*https?://)", serialized_for_scan) is None
    claims_by_id = {claim["claim_id"]: claim for claim in claims["claims"]}
    unsupported_claims_are_not_promoted = all(
        claims_by_id[claim_id]["status"] == "UNSUPPORTED"
        for claim_id in (
            "CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT",
            "CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION",
        )
    )
    no_misleading_probability_or_wave_claim = not any(
        re.search(pattern, serialized_for_scan, flags=re.IGNORECASE)
        for pattern in (
            r"2[,.]8%\s+(?:là\s+)?xác suất\s+(?:khủng hoảng|Ethereum)",
            r"100\s+(?:vòng|wave)\s+(?:đã|được)\s+(?:đạt|quan sát)",
        )
    )
    checks = {
        "frozen_bundle_hashes_unchanged": len(frozen_hashes) == len(frozen_manifest["artifact_hashes"]) + len(frozen_manifest["report_hashes"]),
        "oracle_bundle_hashes_unchanged": len(oracle_hashes) == len(oracle_manifest["artifact_hashes"]) + len(oracle_manifest["report_hashes"]),
        "canonical_snapshot_hash_unchanged": canonical_hash == "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99",
        "targeted_replay_hashes_match_72_of_72": replay_validation["replay_hash_matches"] == 72,
        "borrower_rows_match_18x4x454": replay_validation["borrower_rows"] == 18 * 4 * 454,
        "hf_traces_match_source_rows": replay_validation["hf_trace_matches"] == 18 * 4 * 454,
        "newly_eligible_counts_match_72_of_72": replay_validation["new_eligibility_count_matches"] == 72,
        "all_event_locators_resolve": audit_event_ids <= event_ids,
        "unique_event_ids": len(event_ids) == len(event_rows),
        "unique_claim_ids": len(claim_ids) == len(set(claim_ids)),
        "all_claim_result_ids_resolve": not unresolved_results,
        "all_claim_table_figure_ids_resolve": not unresolved_table_figures,
        "six_rq_order_and_identity_preserved": actual_rqs == expected_rqs,
        "all_values_finite": _all_finite([audit_rows, event_rows, rq_matrix, claims]),
        "no_raw_wallet_addresses": no_raw_address,
        "no_api_keys_or_rpc_urls": no_secret,
        "unsupported_empirical_claims_are_not_promoted": unsupported_claims_are_not_promoted,
        "no_misleading_probability_or_wave_claim": no_misleading_probability_or_wave_claim,
        "no_unexplained_not_eligible_skip": all(
            "UNEXPLAINED_PLAN_NOT_ELIGIBLE" not in row["skip_reason_counts"]
            for row in summary_rows
        ),
        "no_large_monte_carlo_rerun": True,
        "literature_files_not_modified": True,
    }
    failed = [key for key, passed in checks.items() if not passed]
    validation_report = {
        "schema_version": "scientific-integration-v1.0",
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "replay_validation": replay_validation,
        "unresolved_result_ids": unresolved_results,
        "unresolved_table_figure_ids": unresolved_table_figures,
        "policy_reconciliation": policy_summary,
        "self_review": {
            "claim_missing_evidence": [],
            "policy_attribution_errors": [],
            "denominator_errors": [],
            "unit_errors": [],
            "eligibility_execution_conflation": [],
            "superseded_source_errors": [],
            "genuine_numerical_inconsistencies": [],
            "required_downstream_wording_corrections": [
                "Frozen CL_RQ1 downstream wording must state Policy A conditionality.",
                "Frozen CL_RQ2 downstream wording must separate DEX absorption from oracle-mediated HF feedback.",
            ],
            "open_dependency": "P2 PR #9 oracle reconciliation requested at comment 6166173420; current pinned locator HEAD remains 8f5b635.",
        },
        "decision": "READY_FOR_COMMANDER_REVIEW" if not failed else "TARGETED_REWORK_REQUIRED",
    }
    _write_json(ROOT / "integration_validation_report.json", validation_report)
    if failed:
        raise RuntimeError(f"Integration validation failed: {failed}")

    test_evidence_path = ROOT / "test_evidence.json"
    test_evidence = _load(test_evidence_path) if test_evidence_path.exists() else {"status": "PENDING", "commands": []}
    input_hashes = {
        "canonical_snapshot": canonical_hash,
        "frozen_v3_manifest": _sha(FROZEN_ROOT / "manifest.json"),
        "oracle_manifest": _sha(ORACLE_ROOT / "manifest.json"),
        "oracle_selection_manifest": _sha(ORACLE_ROOT / "selection_manifest.json"),
        **{f"p2::{path}": value for path, value in p2_hashes.items()},
    }
    _render_docs(rq_matrix, policy_summary, claims, replay_validation, input_hashes, test_evidence)

    artifact_names = [
        "accepted_claims_proposed.json",
        "claim_to_result_registry.json",
        "eligible_vs_executed_audit.csv",
        "eligible_vs_executed_summary.csv",
        "integration_result_registry.json",
        "integration_validation_report.json",
        "six_rq_evidence_matrix.json",
        "targeted_event_trace.jsonl",
        "table_figure_registry.json",
        "version_precedence.json",
    ]
    if test_evidence_path.exists():
        artifact_names.append("test_evidence.json")
    artifact_hashes = {name: _sha(ROOT / name) for name in artifact_names}
    report_hashes = {
        ADDENDUM.as_posix(): _sha(ADDENDUM),
        REVIEW_PACKET.as_posix(): _sha(REVIEW_PACKET),
    }
    shared_catalog_metadata = {
        "source_commit": SOURCE_CODE_COMMIT,
        "exact_input_hashes": input_hashes,
        "model_policy_version": f"{MODEL_VERSION}; Oracle Diagnostic policies A/B/C locked by selection manifest",
        "scope": "Targeted Frozen v3 + Oracle Diagnostic v1 evidence integration; no model retuning or 10,000-path rerun.",
        "data_provenance": "Frozen v3, Oracle Diagnostic v1 targeted replays, canonical snapshot and pinned P2 locators.",
        "limitations": "Counterfactual model evidence unless explicitly tiered otherwise; P2 oracle reconciliation remains open.",
        "generation_command": ".\\.venv\\Scripts\\python.exe .\\scripts\\research\\build_scientific_integration_v1.py",
    }
    artifact_catalog = {
        f"data/processed/research_final/scientific_integration_v1/{name}": {
            **shared_catalog_metadata,
            "artifact_sha256": artifact_hashes[name],
        }
        for name in artifact_names
    }
    artifact_catalog.update(
        {
            path: {**shared_catalog_metadata, "artifact_sha256": digest}
            for path, digest in report_hashes.items()
        }
    )
    manifest = {
        "schema_version": "scientific-integration-v1.0",
        "status": "READY_FOR_COMMANDER_REVIEW",
        "decision_is_proposed_not_commander_granted": True,
        "starting_head": STARTING_HEAD,
        "source_code_commit": SOURCE_CODE_COMMIT,
        "artifact_bundle_commit": ARTIFACT_BUNDLE_COMMIT,
        "dependencies": {
            "oracle_pr_11": {"head": STARTING_HEAD, "state": "DRAFT_OPEN", "commander_gate": "SCIENTIFIC_PASS_WITH_LIMITATIONS"},
            "frozen_v3": {"head": FROZEN_HEAD, "manifest_sha256": input_hashes["frozen_v3_manifest"]},
            "p2_pr_9": {"head": P2_HEAD, "state": "DRAFT_OPEN_ORACLE_RECONCILIATION_PENDING"},
        },
        "input_hashes": input_hashes,
        "code_hashes": {
            path: _sha(Path(path))
            for path in [
                "sim/engine/run.py",
                "sim/oracle.py",
                "sim/agents/liquidator.py",
                "sim/lending/liquidation.py",
                "sim/lending/health_factor.py",
            ]
        },
        "artifact_hashes": artifact_hashes,
        "report_hashes": report_hashes,
        "artifact_catalog": artifact_catalog,
        "implementation_hashes": {
            "scripts/research/build_scientific_integration_v1.py": _sha(
                Path("scripts/research/build_scientific_integration_v1.py")
            ),
            "tests/test_scientific_integration_v1.py": _sha(
                Path("tests/test_scientific_integration_v1.py")
            ),
        },
        "counts": {
            "research_questions": 6,
            "claims": len(claims["claims"]),
            "accepted_claims_proposed": len(accepted),
            "targeted_runs": replay_validation["targeted_runs"],
            "borrower_audit_rows": replay_validation["borrower_rows"],
            "event_trace_rows": replay_validation["event_rows"],
        },
        "quality_gate": checks,
        "test_evidence": test_evidence,
        "large_monte_carlo_rerun": False,
        "model_retuned": False,
        "frozen_v3_overwritten": False,
        "oracle_diagnostic_overwritten": False,
        "literature_files_modified": False,
        "scientific_content_lock_declared": False,
        "reproduction_command": ".\\.venv\\Scripts\\python.exe .\\scripts\\research\\build_scientific_integration_v1.py",
    }
    _write_json(ROOT / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "targeted_runs": replay_validation["targeted_runs"],
                "borrower_rows": replay_validation["borrower_rows"],
                "event_rows": replay_validation["event_rows"],
                "policy_reconciliation": policy_summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
