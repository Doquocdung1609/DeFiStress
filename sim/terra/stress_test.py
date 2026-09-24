from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random
from typing import Any

import numpy as np

from sim.terra.demo_data import EXTENDED_DATASET

MODEL_VERSION = "terra-stress-test-1.0.0"
DEFAULT_SEED = 20220506


@dataclass(frozen=True, slots=True)
class StressScenario:
    withdrawal_pressure: float = 1.0
    liquidity_capacity: float = 0.55
    arbitrage_capacity: float = 0.55
    confidence_sensitivity: float = 1.0
    outside_holder_exit: float = 0.004
    reserve_intervention: float = 0.0
    horizon_hours: int = 168
    initial_shock: float = 0.015

    def validate(self) -> None:
        if self.horizon_hours < 1 or self.horizon_hours > 720:
            raise ValueError("horizon_hours must be between 1 and 720")
        for name, value in asdict(self).items():
            if name != "horizon_hours" and (not math.isfinite(float(value)) or float(value) < 0):
                raise ValueError(f"{name} must be finite and non-negative")


def _run(scenario: StressScenario, seed: int) -> dict[str, Any]:
    scenario.validate()
    rng = Random(seed)
    ust = 1.0 - min(0.30, scenario.initial_shock)
    luna = 80.0
    supply = 750_000_000.0
    deposits = 14_000_000_000.0
    rows: list[dict[str, float | int]] = []
    collapse_time: int | None = None
    max_withdrawal = 0.0
    for hour in range(scenario.horizon_hours):
        confidence = max(0.0, 1.0 - ust) * scenario.confidence_sensitivity
        random_variation = rng.uniform(0.85, 1.15)
        withdrawal_rate = min(0.25, 0.0025 * scenario.withdrawal_pressure * (1.0 + 8.0 * confidence))
        withdrawal = min(deposits, deposits * withdrawal_rate * random_variation)
        outside_stock = max(0.0, 16_000_000_000.0 - deposits)
        outside_sell = outside_stock * min(0.20, scenario.outside_holder_exit * (1.0 + 10.0 * confidence))
        gross_sell = withdrawal * 0.60 + outside_sell
        reserve = min(gross_sell, scenario.reserve_intervention * 50_000_000.0)
        executable_arb = min(
            max(0.0, gross_sell - reserve),
            scenario.arbitrage_capacity * 150_000_000.0 * max(0.0, 1.0 - 0.2 * confidence),
        )
        net_sell = max(0.0, gross_sell - reserve - executable_arb)
        depth = max(1_000_000.0, scenario.liquidity_capacity * 1_000_000_000.0)
        market_impact = min(0.65, 0.045 * math.sqrt(net_sell / depth))
        recovery = min(0.08, executable_arb / 3_000_000_000.0)
        ust = min(1.01, max(0.005, ust * math.exp(-market_impact) + recovery))
        redemption = executable_arb if ust < 0.985 else 0.0
        minted = redemption / max(luna, 1e-8)
        previous_supply = supply
        supply += minted
        dilution = math.log(max(supply, 1.0) / max(previous_supply, 1.0))
        luna = max(1e-8, luna * math.exp(-1.2 * dilution - 0.10 * confidence - 0.20 * market_impact))
        deposits = max(0.0, deposits - withdrawal)
        max_withdrawal = max(max_withdrawal, withdrawal)
        collapsed = ust < 0.90 and supply > 1_500_000_000.0
        if collapsed and collapse_time is None:
            collapse_time = hour
        rows.append(
            {
                "hour": hour,
                "ust_price": ust,
                "luna_price": luna,
                "luna_supply": supply,
                "anchor_deposits": deposits,
                "withdrawal": withdrawal,
                "net_ust_sell": net_sell,
                "redemption": redemption,
            }
        )
    return {
        "seed": seed,
        "scenario": asdict(scenario),
        "parameters": asdict(scenario),
        "collapse_flag": collapse_time is not None,
        "collapse_time_hours": collapse_time,
        "minimum_ust": min(float(row["ust_price"]) for row in rows),
        "minimum_luna": min(float(row["luna_price"]) for row in rows),
        "final_luna_supply": float(rows[-1]["luna_supply"]),
        "max_withdrawal_stress": max_withdrawal,
        "timeseries": rows,
    }


def run_stress_test(
    scenario: StressScenario | None = None,
    *,
    runs: int = 100,
    seed: int = DEFAULT_SEED,
    dataset_path: Path = EXTENDED_DATASET,
) -> dict[str, Any]:
    del dataset_path  # Historical values are context only; stress paths are scenario generated.
    selected = scenario or StressScenario()
    if runs < 1 or runs > 1000:
        raise ValueError("runs must be between 1 and 1000")
    simulations = [_run(selected, seed + index) for index in range(runs)]
    fan: list[dict[str, Any]] = []
    for hour in range(selected.horizon_hours):
        row: dict[str, Any] = {"hour": hour}
        for field in ("ust_price", "luna_price", "luna_supply"):
            sample = np.asarray([run["timeseries"][hour][field] for run in simulations], dtype=float)
            row[field] = {
                "p05": float(np.quantile(sample, 0.05)),
                "median": float(np.quantile(sample, 0.50)),
                "p95": float(np.quantile(sample, 0.95)),
            }
        fan.append(row)
    collapsed = sum(bool(run["collapse_flag"]) for run in simulations)
    return {
        "analysis_type": "COUNTERFACTUAL_STRESS_TEST",
        "model_version": MODEL_VERSION,
        "scenario": asdict(selected),
        "runs": runs,
        "seed_start": seed,
        "seed_end": seed + runs - 1,
        "random_variation": "Seeded per-run behavioral multiplier; structural assumptions fixed.",
        "model_assumption_uncertainty": (
            "Run separate scenarios to vary liquidity, arbitrage, confidence, exits, or reserves."
        ),
        "summary": {
            "collapse_count": collapsed,
            "noncollapse_count": runs - collapsed,
            "wording": (
                f"{collapsed} of {runs} simulated runs crossed the collapse condition; "
                "this is not a probability estimate."
            ),
            "minimum_ust": {
                "p05": float(np.quantile([run["minimum_ust"] for run in simulations], 0.05)),
                "median": float(np.quantile([run["minimum_ust"] for run in simulations], 0.50)),
                "p95": float(np.quantile([run["minimum_ust"] for run in simulations], 0.95)),
            },
            "final_luna_supply": {
                "p05": float(np.quantile([run["final_luna_supply"] for run in simulations], 0.05)),
                "median": float(np.quantile([run["final_luna_supply"] for run in simulations], 0.50)),
                "p95": float(np.quantile([run["final_luna_supply"] for run in simulations], 0.95)),
            },
        },
        "fan_chart": fan,
        "run_summaries": [{key: value for key, value in run.items() if key != "timeseries"} for run in simulations],
        "representative_timeseries": simulations[0]["timeseries"],
        "data_policy": {
            "dex_liquidity": "Scenario assumption, not observed historical Terra DEX depth.",
            "reserve_intervention": "Scenario assumption; audited LFG peg-defense flow is unavailable.",
        },
    }
