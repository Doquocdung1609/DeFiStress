from __future__ import annotations

import csv
import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from statistics import median
from typing import Any, cast

from sim.engine import run_simulation
from sim.schemas import BorrowerPosition, DexState, Scenario, SimulationResult, json_safe

D = Decimal
ONE = D(1)
RQ_COMPLETION_VERSION = "aave-rq-completion-1.0.0"
DELAY_STEPS = (0, 1, 2, 4)
USDC_PRICES = (D("1.10"), D("1.05"), D("1.01"), D("1.00"), D("0.99"), D("0.95"), D("0.90"))
HF_THRESHOLDS = (D("1.00"), D("1.05"), D("1.10"), D("1.20"))
CAPITAL_RATIOS = (D("0.25"), D("0.50"), D("1.00"), D("2.00"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flat_rows = []
    for row in rows:
        flat_rows.append(
            {
                key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value
                for key, value in row.items()
            }
        )
    fieldnames = sorted({key for row in flat_rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_rows)


def _number(value: Any) -> float:
    return float(value or 0)


def _summarize_result(name: str, result: SimulationResult) -> dict[str, Any]:
    payload = result.to_dict()
    liquidations = [event for event in payload["events"] if event["event_type"] == "LIQUIDATION"]
    wave_one = [event for event in liquidations if int(event["wave"]) == 1]
    later = [event for event in liquidations if int(event["wave"]) >= 2]
    summary = cast(dict[str, Any], dict(payload["metrics"]))
    summary.update(
        {
            "scenario_name": name,
            "scenario": payload["scenario"],
            "number_of_liquidation_events": len(liquidations),
            "number_of_waves": len({int(event["wave"]) for event in liquidations}),
            "forced_weth_volume": sum(_number(event["forced_sell_amount"]) for event in liquidations),
            "collateral_seized_weth": sum(_number(event["collateral_seized"]) for event in liquidations),
            "liquidator_expected_profit_usdc": sum(
                _number(event["expected_profit"]) for event in liquidations
            ),
            "liquidator_gas_cost_usdc": sum(_number(event["gas_cost"]) for event in liquidations),
            "wave_1_liquidated_debt": sum(_number(event["debt_repaid"]) for event in wave_one),
            "wave_2_plus_liquidated_debt": sum(_number(event["debt_repaid"]) for event in later),
        }
    )
    return summary


def _run(
    positions: list[BorrowerPosition],
    dex: DexState,
    weth_price: Decimal,
    name: str,
    scenario: Scenario,
) -> tuple[SimulationResult, dict[str, Any]]:
    result = run_simulation(positions, dex, weth_price, scenario, run_id=f"rq-completion-{name.lower()}")
    return result, _summarize_result(name, result)


def _hf_counts(
    positions: list[BorrowerPosition],
    weth_price: Decimal,
    *,
    usdc_price_usd: Decimal = ONE,
    lt_override: Decimal | None = None,
) -> dict[str, int]:
    cohort = [position for position in positions if position.collateral_weth > 0 and position.debt_usdc > 0]
    return {
        f"borrowers_hf_below_{str(threshold).replace('.', '_')}": sum(
            position.health_factor(weth_price, lt_override, usdc_price_usd) < threshold
            for position in cohort
        )
        for threshold in HF_THRESHOLDS
    }


def _differences(row: dict[str, Any], baseline: dict[str, Any], metrics: tuple[str, ...]) -> dict[str, float | None]:
    return {
        metric: None
        if row.get(metric) is None or baseline.get(metric) is None
        else _number(row[metric]) - _number(baseline[metric])
        for metric in metrics
    }


def run_reaction_delay_sensitivity(
    positions: list[BorrowerPosition],
    dex: DexState,
    weth_price: Decimal,
    professor: Scenario,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for delay_steps in DELAY_STEPS:
        scenario = replace(professor, name=f"RQ3_DELAY_{delay_steps}", liquidator_delay_steps=delay_steps)
        _, summary = _run(positions, dex, weth_price, scenario.name, scenario)
        rows.append(
            {
                "delay_steps": delay_steps,
                "delay_seconds": delay_steps * scenario.timestep_seconds,
                "delay_minutes": delay_steps * scenario.timestep_seconds / 60,
                **summary,
            }
        )
    baseline = rows[0]
    comparison_metrics = (
        "liquidation_at_risk",
        "direct_shock_liquidated_debt",
        "total_liquidated_debt",
        "unliquidated_debt",
        "bad_debt",
        "number_of_liquidation_events",
        "cascade_depth",
        "number_of_waves",
        "max_price_impact",
        "time_to_recovery_seconds",
        "forced_weth_volume",
        "final_dex_price",
    )
    for row in rows:
        row["change_vs_delay_0"] = _differences(row, baseline, comparison_metrics)
    severity_metrics = tuple(metric for metric in comparison_metrics if metric != "time_to_recovery_seconds")
    severity_unchanged = all(
        all(row["change_vs_delay_0"][metric] in {0} for metric in severity_metrics) for row in rows
    )
    timing_changes = any(row["change_vs_delay_0"]["time_to_recovery_seconds"] not in {0} for row in rows)
    status = (
        "REACTION_DELAY_TIME_SHIFT_ONLY_NOT_SEVERITY_BINDING"
        if severity_unchanged and timing_changes
        else "REACTION_DELAY_NOT_BINDING_IN_TESTED_RANGE"
        if severity_unchanged
        else "REACTION_DELAY_BINDING_IN_TESTED_RANGE"
    )
    return {
        "analysis": "RQ3_REACTION_DELAY",
        "scenario_base": cast(dict[str, Any], json_safe(professor)),
        "timestep_seconds": professor.timestep_seconds,
        "tested_delay_steps": list(DELAY_STEPS),
        "rows": rows,
        "status": status,
        "interpretation": (
            "Delay is binding only for simulated processing/recovery time when severity metrics are unchanged."
        ),
        "claim_boundary": "Canonical snapshot, Professor Demo assumptions and tested delays only.",
    }


def derive_required_liquidator_capital(
    positions: list[BorrowerPosition],
    dex: DexState,
    weth_price: Decimal,
    professor: Scenario,
) -> tuple[dict[str, Any], Decimal]:
    cohort_debt_tokens = sum(
        (position.debt_usdc for position in positions if position.collateral_weth > 0 and position.debt_usdc > 0),
        D(0),
    )
    finite_upper_bound = max(D("1"), cohort_debt_tokens * D("2"))
    scenario = replace(
        professor,
        name="RQ3_UNCONSTRAINED_REFERENCE",
        liquidator_capital_usdc=finite_upper_bound,
        liquidator_capacity_usdc=finite_upper_bound,
    )
    result, summary = _run(positions, dex, weth_price, scenario.name, scenario)
    required = sum(
        (event.debt_repaid for event in result.events if event.event_type == "LIQUIDATION"),
        D(0),
    )
    payload = {
        **summary,
        "finite_unconstrained_resource_usdc": float(finite_upper_bound),
        "cohort_total_usdc_debt_tokens": float(cohort_debt_tokens),
        "required_capital_reference_usdc": float(required),
        "definition": (
            "Cumulative USDC funding consumed by executed liquidations in the finite unconstrained reference run. "
            "The engine subtracts repaid USDC from capital and does not recycle it."
        ),
        "non_binding_rationale": (
            "The configured finite resource is twice total modeled WETH-collateral/USDC-debt token debt, "
            "which is above the maximum repayable model demand."
        ),
    }
    return payload, required


def run_capital_constraint_sensitivity(
    positions: list[BorrowerPosition],
    dex: DexState,
    weth_price: Decimal,
    professor: Scenario,
) -> dict[str, Any]:
    unconstrained, reference = derive_required_liquidator_capital(positions, dex, weth_price, professor)
    if reference <= 0:
        raise ValueError("unconstrained reference produced no liquidation funding demand")
    rows = []
    for ratio in CAPITAL_RATIOS:
        capital = reference * ratio
        scenario = replace(
            professor,
            name=f"RQ3_CAPITAL_{ratio}",
            liquidator_capital_usdc=capital,
            liquidator_capacity_usdc=max(capital, reference * D("2")),
        )
        _, summary = _run(positions, dex, weth_price, scenario.name, scenario)
        spent = D(str(summary["total_liquidated_debt_usdc"]))
        binding = spent < reference
        rows.append(
            {
                "capital_ratio": float(ratio),
                "capital_usdc": float(capital),
                "required_capital_reference_usdc": float(reference),
                "constraint_status": "BINDING" if binding else "NON_BINDING",
                "capital_spent_within_limit": spent <= capital,
                **summary,
            }
        )
    return {
        "analysis": "RQ3_BINDING_LIQUIDATOR_CAPITAL",
        "unconstrained_reference": unconstrained,
        "required_capital_reference_usdc": float(reference),
        "capital_ratios": [float(value) for value in CAPITAL_RATIOS],
        "rows": rows,
        "claim_boundary": (
            "Capital is cumulative and non-recycled in this engine; results apply only to the canonical snapshot "
            "and Professor Demo scenario."
        ),
    }


def run_usdc_depeg_sensitivity(
    positions: list[BorrowerPosition],
    dex: DexState,
    weth_price: Decimal,
    professor: Scenario,
) -> dict[str, Any]:
    post_shock_weth_price = weth_price * (D(1) + professor.shock_pct / D(100))
    explicit_baseline = replace(professor, name="RQ5_USDC_1.00", usdc_price_usd=D("1.00"))
    legacy_result = run_simulation(positions, dex, weth_price, professor, run_id="rq5-baseline")
    explicit_result = run_simulation(positions, dex, weth_price, explicit_baseline, run_id="rq5-baseline")
    legacy_payload = legacy_result.to_dict()
    explicit_payload = explicit_result.to_dict()
    legacy_scenario = cast(dict[str, Any], legacy_payload["scenario"])
    explicit_scenario = cast(dict[str, Any], explicit_payload["scenario"])
    legacy_scenario.pop("name", None)
    explicit_scenario.pop("name", None)
    baseline_compatible = (
        legacy_payload["metrics"] == explicit_payload["metrics"]
        and legacy_payload["events"] == explicit_payload["events"]
        and legacy_payload["timeseries"] == explicit_payload["timeseries"]
        and legacy_payload["final_positions"] == explicit_payload["final_positions"]
        and legacy_scenario == explicit_scenario
    )
    rows = []
    for usdc_price in USDC_PRICES:
        scenario = replace(
            professor,
            name=f"RQ5_USDC_{usdc_price}",
            usdc_price_usd=usdc_price,
        )
        _, summary = _run(positions, dex, weth_price, scenario.name, scenario)
        rows.append(
            {
                "usdc_price_usd": float(usdc_price),
                "depeg_direction": "UPWARD" if usdc_price > 1 else "DOWNWARD" if usdc_price < 1 else "BASELINE",
                **_hf_counts(positions, post_shock_weth_price, usdc_price_usd=usdc_price),
                **summary,
            }
        )
    rows_by_price = {D(str(row["usdc_price_usd"])): row for row in rows}
    baseline_hf = rows_by_price[D("1.0")]["borrowers_hf_below_1_00"]
    upward_directional_pass = all(
        row["borrowers_hf_below_1_00"] >= baseline_hf for price, row in rows_by_price.items() if price > 1
    )
    downward_directional_pass = all(
        row["borrowers_hf_below_1_00"] <= baseline_hf for price, row in rows_by_price.items() if price < 1
    )
    return {
        "analysis": "RQ5_USDC_DEBT_VALUATION",
        "channel": "USDC_DEBT_VALUATION_ONLY",
        "rows": rows,
        "backward_compatibility": {
            "usdc_price_1_matches_legacy": baseline_compatible,
            "comparison": "metrics, events, timeseries and final positions",
        },
        "directional_checks": {
            "upward_depeg_does_not_improve_hf": upward_directional_pass,
            "downward_depeg_does_not_worsen_hf": downward_directional_pass,
        },
        "mandatory_wording": "This experiment isolates the USDC debt-valuation channel.",
        "limitation": (
            "It does not represent the full market-liquidity, redemption, settlement or confidence consequences "
            "of a real stablecoin depeg."
        ),
    }


def _reserve(snapshot: dict[str, Any], symbol: str) -> dict[str, Any]:
    try:
        return next(row for row in snapshot["aave_reserves"] if row["symbol"] == symbol)
    except StopIteration as exc:
        raise ValueError(f"canonical reserve evidence missing for {symbol}") from exc


def run_ltv_capital_efficiency_analysis(
    positions: list[BorrowerPosition],
    weth_price: Decimal,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    reserve = _reserve(snapshot, "WETH")
    baseline = D(str(reserve["ltv"]))
    liquidation_threshold = D(str(reserve["liquidation_threshold"]))
    requested = (baseline - D("0.05"), baseline - D("0.025"), baseline, baseline + D("0.01"), baseline + D("0.02"))
    levels = tuple(value for value in requested if D(0) < value < liquidation_threshold)
    cohort = [position for position in positions if position.collateral_weth > 0 and position.debt_value() > 0]
    rows = []
    for level in levels:
        capacities = []
        utilization = []
        above_capacity = 0
        for position in cohort:
            capacity = position.collateral_weth * weth_price * level
            capacity += position.other_collateral_usd * position.ltv
            debt = position.debt_value()
            capacities.append(capacity)
            ratio = debt / capacity if capacity > 0 else D("Infinity")
            if ratio.is_finite():
                utilization.append(ratio)
            if debt > capacity:
                above_capacity += 1
        aggregate_capacity = sum(capacities, D(0))
        aggregate_debt = sum((position.debt_value() for position in cohort), D(0))
        rows.append(
            {
                "ltv_policy": float(level),
                "change_from_baseline_percentage_points": float((level - baseline) * D(100)),
                "aggregate_max_borrowing_capacity_usd": float(aggregate_capacity),
                "median_borrower_max_borrowing_capacity_usd": float(median(capacities)),
                "aggregate_current_debt_to_capacity": float(aggregate_debt / aggregate_capacity),
                "median_current_debt_to_capacity": float(median(utilization)),
                "borrowers_above_counterfactual_borrowing_capacity": above_capacity,
                "liquidatable_interpretation": "NOT_INFERRED_FROM_LTV",
            }
        )
    return {
        "analysis": "RQ6_LTV_EX_ANTE_CAPITAL_EFFICIENCY",
        "canonical_weth_ltv": float(baseline),
        "canonical_weth_liquidation_threshold": float(liquidation_threshold),
        "cohort_size": len(cohort),
        "rows": rows,
        "method": (
            "Counterfactual WETH capacity uses the WETH policy LTV; other collateral capacity remains at each "
            "borrower's observed weighted LTV proxy. Frozen debt is never mutated."
        ),
        "claim_boundary": (
            "Above counterfactual borrowing capacity means an ex-ante origination constraint, not liquidatability."
        ),
    }


def run_liquidation_threshold_sensitivity(
    positions: list[BorrowerPosition],
    dex: DexState,
    weth_price: Decimal,
    professor: Scenario,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    reserve = _reserve(snapshot, "WETH")
    baseline = D(str(reserve["liquidation_threshold"]))
    ltv = D(str(reserve["ltv"]))
    levels = (baseline - D("0.02"), baseline - D("0.01"), baseline, baseline + D("0.025"), baseline + D("0.05"))
    if any(not (ltv < level <= 1) for level in levels):
        raise ValueError("derived liquidation-threshold levels violate canonical WETH LTV < LT <= 1")
    post_shock_weth_price = weth_price * (D(1) + professor.shock_pct / D(100))
    rows = []
    for level in levels:
        scenario = replace(
            professor,
            name=f"RQ6_LT_{level}",
            liquidation_threshold_override=level,
        )
        _, summary = _run(positions, dex, weth_price, scenario.name, scenario)
        rows.append(
            {
                "liquidation_threshold": float(level),
                "change_from_baseline_percentage_points": float((level - baseline) * D(100)),
                **_hf_counts(positions, post_shock_weth_price, lt_override=level),
                "direct_shock_liquidatable_borrowers": _hf_counts(
                    positions, post_shock_weth_price, lt_override=level
                )["borrowers_hf_below_1_00"],
                **summary,
            }
        )
    return {
        "analysis": "RQ6_LIQUIDATION_THRESHOLD",
        "canonical_weth_ltv": float(ltv),
        "canonical_weth_liquidation_threshold": float(baseline),
        "rows": rows,
        "override_semantics": (
            "The override changes the WETH collateral term in Health Factor; other_collateral_usd retains the "
            "borrower's observed liquidation threshold."
        ),
        "claim_boundary": "Frozen canonical snapshot and Professor Demo shock; policy counterfactual, not forecast.",
    }


def run_liquidation_bonus_sensitivity(
    positions: list[BorrowerPosition],
    dex: DexState,
    weth_price: Decimal,
    professor: Scenario,
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    reserve = _reserve(snapshot, "WETH")
    baseline = D(str(reserve["liquidation_bonus"]))
    levels = (baseline - D("0.02"), baseline - D("0.01"), baseline, baseline + D("0.01"), baseline + D("0.02"))
    if any(level < 1 for level in levels):
        raise ValueError("derived liquidation-bonus level is below 1.0")
    rows = []
    for level in levels:
        scenario = replace(
            professor,
            name=f"RQ6_BONUS_{level}",
            liquidation_bonus_override=level,
        )
        _, summary = _run(positions, dex, weth_price, scenario.name, scenario)
        rows.append(
            {
                "liquidation_bonus": float(level),
                "change_from_baseline_percentage_points": float((level - baseline) * D(100)),
                **summary,
            }
        )
    outcome_metrics = (
        "number_of_liquidation_events",
        "total_liquidated_debt",
        "collateral_seized_weth",
        "forced_weth_volume",
        "liquidator_expected_profit_usdc",
        "liquidator_gas_cost_usdc",
        "bad_debt",
        "max_price_impact",
        "cascade_depth",
        "unliquidated_debt",
    )
    baseline_row = next(row for row in rows if D(str(row["liquidation_bonus"])) == baseline)
    changed = any(
        any(row[metric] != baseline_row[metric] for metric in outcome_metrics)
        for row in rows
        if row is not baseline_row
    )
    return {
        "analysis": "RQ6_LIQUIDATION_BONUS",
        "canonical_weth_liquidation_bonus": float(baseline),
        "rows": rows,
        "status": "LIQUIDATION_BONUS_BINDING_IN_TESTED_RANGE"
        if changed
        else "LIQUIDATION_BONUS_NOT_BINDING_IN_TESTED_RANGE",
        "mechanism": "Bonus changes collateral seized and therefore the liquidator quote/profitability path.",
        "claim_boundary": "Frozen canonical snapshot and tested bonus range only.",
    }


def run_rq_completion(
    *,
    positions: list[BorrowerPosition],
    dex: DexState,
    weth_price: Decimal,
    snapshot: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    professor = Scenario(name="PROFESSOR_DEMO")
    delay = run_reaction_delay_sensitivity(positions, dex, weth_price, professor)
    capital = run_capital_constraint_sensitivity(positions, dex, weth_price, professor)
    usdc = run_usdc_depeg_sensitivity(positions, dex, weth_price, professor)
    ltv = run_ltv_capital_efficiency_analysis(positions, weth_price, snapshot)
    threshold = run_liquidation_threshold_sensitivity(positions, dex, weth_price, professor, snapshot)
    bonus = run_liquidation_bonus_sensitivity(positions, dex, weth_price, professor, snapshot)
    artifacts = {
        "rq3_reaction_delay": delay,
        "rq3_capital_constraint": capital,
        "rq5_usdc_depeg": usdc,
        "rq6_ltv_capital_efficiency": ltv,
        "rq6_liquidation_threshold": threshold,
        "rq6_liquidation_bonus": bonus,
    }
    for name, payload in artifacts.items():
        _write_json(output_dir / f"{name}.json", payload)
        _write_csv(output_dir / f"{name}.csv", cast(list[dict[str, Any]], payload["rows"]))
    summary = {
        "version": RQ_COMPLETION_VERSION,
        "rq3": {
            "reaction_delay_status": delay["status"],
            "binding_capital_levels": [
                row["capital_ratio"] for row in capital["rows"] if row["constraint_status"] == "BINDING"
            ],
            "non_binding_capital_levels": [
                row["capital_ratio"] for row in capital["rows"] if row["constraint_status"] == "NON_BINDING"
            ],
        },
        "rq5": {
            "channel": usdc["channel"],
            "backward_compatibility": usdc["backward_compatibility"],
            "directional_checks": usdc["directional_checks"],
        },
        "rq6": {
            "ltv_role": "EX_ANTE_CAPITAL_EFFICIENCY_NOT_FROZEN_SNAPSHOT_LIQUIDATION_TRIGGER",
            "liquidation_threshold_role": "HEALTH_FACTOR_AND_LIQUIDATION_BOUNDARY",
            "liquidation_bonus_status": bonus["status"],
        },
        "claim_boundary": "All results are conditional on the canonical snapshot and tested ranges.",
    }
    _write_json(output_dir / "rq_completion_summary.json", summary)
    return summary


__all__ = [
    "RQ_COMPLETION_VERSION",
    "derive_required_liquidator_capital",
    "run_capital_constraint_sensitivity",
    "run_liquidation_bonus_sensitivity",
    "run_liquidation_threshold_sensitivity",
    "run_ltv_capital_efficiency_analysis",
    "run_reaction_delay_sensitivity",
    "run_rq_completion",
    "run_usdc_depeg_sensitivity",
]
