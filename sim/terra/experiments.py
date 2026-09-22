from __future__ import annotations

from dataclasses import replace
from time import perf_counter
from typing import Any

from sim.terra.datasets import ResearchDataset
from sim.terra.replay import HistoricalReplayExperiment, run_historical_replay
from sim.terra.schemas import ValidationResult
from sim.terra.validation import benchmark_row


def run_benchmark(dataset: ResearchDataset, base: HistoricalReplayExperiment) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    replays: dict[str, dict[str, Any]] = {}
    for model_name in ("THRESHOLD", "HAZARD", "SYSTEM_DYNAMICS", "ABM"):
        started = perf_counter()
        replay = run_historical_replay(dataset, replace(base, model_name=model_name))
        elapsed = perf_counter() - started
        validation = ValidationResult(model_name, replay["validation_metrics"])
        rows.append(benchmark_row(validation, elapsed))
        replays[model_name] = replay
    return {
        "benchmark_results": rows,
        "replays": replays,
        "interpretation": "Metrics are presented neutrally; no automatic winner is declared.",
        "dataset_status": dataset.manifest.status.value,
    }


def run_ablation(dataset: ResearchDataset, base: HistoricalReplayExperiment) -> dict[str, Any]:
    variants = {
        "ABM_FULL": {},
        "NO_WHALE_HETEROGENEITY": {"whale_heterogeneity": False},
        "NO_ARBITRAGE": {"arbitrage_enabled": False},
        "NO_LIQUIDITY_FEEDBACK": {"liquidity_feedback": False},
        "NO_CONFIDENCE_CONTAGION": {"confidence_feedback": False},
        "NO_RESERVE_INTERVENTION": {"reserve_intervention_enabled": False},
    }
    results = []
    for name, overrides in variants.items():
        parameters = {**base.parameters, **overrides}
        replay = run_historical_replay(dataset, replace(base, model_name="ABM", parameters=parameters))
        results.append({"variant": name, "metrics": replay["validation_metrics"], "parameters": parameters})
    return {"ablation_results": results, "dataset_status": dataset.manifest.status.value}


def run_counterfactual(
    dataset: ResearchDataset, base: HistoricalReplayExperiment, overrides: dict[str, Any]
) -> dict[str, Any]:
    from sim.terra.schemas import ExperimentMode

    historical = run_historical_replay(dataset, replace(base, model_name="ABM"))
    counterfactual = run_historical_replay(
        dataset,
        replace(
            base,
            model_name="ABM",
            mode=ExperimentMode.COUNTERFACTUAL_STRESS,
            parameters={**base.parameters, **overrides},
        ),
    )
    return {
        "label": "COUNTERFACTUAL — not historical reality",
        "historical_replay": historical,
        "counterfactual_replay": counterfactual,
    }


def run_sensitivity(
    dataset: ResearchDataset,
    base: HistoricalReplayExperiment,
    parameter: str,
    values: list[float],
) -> dict[str, Any]:
    allowed = {
        "reaction_delay_hours",
        "arbitrage_capacity",
        "redemption_friction",
        "confidence_sensitivity",
        "reserve_capacity",
        "price_impact_coefficient",
        "initial_withdrawal_shock_pct",
    }
    if parameter not in allowed:
        raise ValueError(f"unsupported sensitivity parameter: {parameter}")
    rows = []
    for value in values:
        replay = run_historical_replay(
            dataset,
            replace(base, model_name="ABM", parameters={**base.parameters, parameter: value}),
        )
        rows.append({"parameter": parameter, "value": value, "metrics": replay["validation_metrics"]})
    return {"method": "ONE_AT_A_TIME", "results": rows}
