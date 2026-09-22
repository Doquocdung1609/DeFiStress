from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Any, cast

import numpy as np

from sim.engine.run import run_simulation
from sim.schemas import BorrowerPosition, DexState, Scenario, json_safe

D = Decimal


@dataclass(frozen=True, slots=True)
class MonteCarloResult:
    seed: int
    runs: int
    summary: dict[str, Any]
    distributions: dict[str, list[float]]

    def to_dict(self) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            json_safe(
                {"seed": self.seed, "runs": self.runs, "summary": self.summary, "distributions": self.distributions}
            ),
        )


def _summary(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "p5": float(np.quantile(values, 0.05)),
        "p50": float(np.quantile(values, 0.50)),
        "p95": float(np.quantile(values, 0.95)),
        "p99": float(np.quantile(values, 0.99)),
    }


def run_monte_carlo(
    positions: list[BorrowerPosition],
    dex_state: DexState,
    initial_price: Decimal,
    scenario: Scenario,
    runs: int | None = None,
    progress: Callable[[int, int], None] | None = None,
) -> MonteCarloResult:
    count = runs or scenario.monte_carlo_runs
    if not 1 <= count <= 10_000:
        raise ValueError("runs must be between 1 and 10000")
    rng = np.random.default_rng(scenario.seed)
    collections: dict[str, list[float]] = {
        "bad_debt": [],
        "total_liquidated_debt": [],
        "cascade_depth": [],
        "max_price_impact": [],
    }
    progress_interval = max(1, count // 20)
    for index in range(count):
        shock = float(scenario.shock_pct) + rng.normal(0, float(scenario.volatility_pct))
        shock = min(0.0, max(-50.0, shock))
        haircut = float(scenario.liquidity_haircut_pct) + rng.normal(0, 4.0)
        haircut = min(95.0, max(0.0, haircut))
        gas = float(scenario.gas_multiplier) * float(rng.lognormal(0, 0.12))
        run_scenario = replace(
            scenario,
            name=f"{scenario.name} MC {index + 1}",
            shock_pct=D(str(shock)),
            liquidity_haircut_pct=D(str(haircut)),
            gas_multiplier=D(str(gas)),
            seed=scenario.seed + index,
        )
        result = run_simulation(positions, dex_state, initial_price, run_scenario, run_id=f"mc-{index}")
        for metric in collections:
            value = result.metrics[metric]
            collections[metric].append(float(value or 0))
        if progress and ((index + 1) % progress_interval == 0 or index + 1 == count):
            progress(index + 1, count)

    arrays = {key: np.asarray(values, dtype=float) for key, values in collections.items()}
    loss = arrays["bad_debt"] + arrays["total_liquidated_debt"]
    tail_cutoff = np.quantile(loss, 0.95)
    tail = loss[loss >= tail_cutoff]
    summary: dict[str, Any] = {key: _summary(values) for key, values in arrays.items()}
    summary["probability_of_cascade"] = float(np.mean(arrays["cascade_depth"] >= 2))
    summary["expected_shortfall_95"] = float(np.mean(tail)) if len(tail) else 0.0
    return MonteCarloResult(scenario.seed, count, summary, collections)
