from __future__ import annotations

from dataclasses import replace
from random import Random
from statistics import mean
from typing import Any

from sim.terra.datasets import ResearchDataset
from sim.terra.replay import HistoricalReplayExperiment, run_historical_replay


def run_terra_monte_carlo(
    dataset: ResearchDataset,
    base: HistoricalReplayExperiment,
    runs: int = 100,
) -> dict[str, Any]:
    if not 1 <= runs <= 10_000:
        raise ValueError("runs must be between 1 and 10000")
    rng = Random(base.seed)
    distributions: dict[str, list[float]] = {
        "minimum_ust_price": [],
        "maximum_luna_supply_expansion": [],
        "maximum_luna_drawdown": [],
        "time_to_severe_depeg_hours": [],
        "time_to_death_spiral_hours": [],
        "cumulative_withdrawals": [],
    }
    severe_count = 0
    collapse_count = 0
    for index in range(runs):
        parameters = {
            **base.parameters,
            "initial_withdrawal_shock_pct": max(0.0, rng.gauss(0.014, 0.004)),
            "reaction_delay_hours": max(0, round(rng.gauss(3, 2))),
            "price_impact_coefficient": max(0.01, rng.gauss(0.24, 0.05)),
            "confidence_sensitivity": max(0.1, rng.gauss(1.2, 0.15)),
            "redemption_friction": min(0.5, max(0.0, rng.gauss(0.02, 0.01))),
            "arbitrage_capital": max(0.0, rng.gauss(900_000_000, 150_000_000)),
        }
        replay = run_historical_replay(
            dataset,
            replace(base, model_name="ABM", parameters=parameters, seed=base.seed + index),
        )
        rows = replay["simulated_timeseries"]
        initial_luna_price = float(rows[0]["luna_price"])
        initial_luna_supply = float(rows[0]["luna_supply"])
        minimum_ust = min(float(row["ust_price"]) for row in rows)
        maximum_supply = max(float(row["luna_supply"]) for row in rows)
        minimum_luna = min(float(row["luna_price"]) for row in rows)
        severe_time = next((idx for idx, row in enumerate(rows) if float(row["ust_price"]) < 0.90), len(rows))
        collapse_time = next((idx for idx, row in enumerate(rows) if bool(row["collapse_signal"])), len(rows))
        withdrawals = sum(float(row["anchor_withdrawal_flow"]) for row in rows)
        distributions["minimum_ust_price"].append(minimum_ust)
        distributions["maximum_luna_supply_expansion"].append(maximum_supply / max(initial_luna_supply, 1.0))
        distributions["maximum_luna_drawdown"].append(1 - minimum_luna / max(initial_luna_price, 0.000001))
        distributions["time_to_severe_depeg_hours"].append(float(severe_time))
        distributions["time_to_death_spiral_hours"].append(float(collapse_time))
        distributions["cumulative_withdrawals"].append(withdrawals)
        severe_count += int(severe_time < len(rows))
        collapse_count += int(collapse_time < len(rows))
    return {
        "seed": base.seed,
        "runs": runs,
        "label": "MODEL-IMPLIED probabilities conditional on the configured ABM",
        "summary": {
            key: {"mean": mean(values), "min": min(values), "max": max(values)} for key, values in distributions.items()
        },
        "probability_of_severe_depeg": severe_count / runs,
        "probability_of_modeled_collapse": collapse_count / runs,
        "distributions": distributions,
    }
