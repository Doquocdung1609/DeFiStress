from __future__ import annotations

import logging
from decimal import Decimal
from time import perf_counter
from typing import Any

from backend.app.db import Repository
from backend.app.services.snapshots import simulation_inputs
from sim.engine import MODEL_VERSION, run_simulation
from sim.monte_carlo import run_monte_carlo
from sim.schemas import Scenario

logger = logging.getLogger("defi_stress.simulation")


def scenario_from_dict(config: dict[str, Any]) -> Scenario:
    decimal_names = {
        "shock_pct",
        "liquidity_haircut_pct",
        "gas_multiplier",
        "liquidator_capital_usdc",
        "liquidator_capacity_usdc",
        "liquidator_min_profit_usdc",
        "arbitrage_capacity_pct",
        "volatility_pct",
        "liquidation_bonus",
        "ltv_override",
        "liquidation_threshold_override",
        "liquidation_bonus_override",
    }
    values = {
        key: (Decimal(str(value)) if key in decimal_names and value is not None else value)
        for key, value in config.items()
    }
    return Scenario(**values)


def execute_run(repository: Repository, run_id: str, mode: str) -> dict[str, Any]:
    started = perf_counter()
    run = repository.get_run(run_id)
    if not run:
        raise KeyError("run not found")
    scenario_row = repository.get_scenario(run["scenario_id"])
    if not scenario_row:
        raise KeyError("scenario not found")
    snapshot = repository.get_snapshot(scenario_row["snapshot_id"])
    if not snapshot:
        raise KeyError("snapshot not found")
    positions, dex_state, initial_price = simulation_inputs(snapshot)
    scenario = scenario_from_dict(scenario_row["config"])
    try:
        if mode == "MONTE_CARLO":
            monte_carlo = run_monte_carlo(
                positions,
                dex_state,
                initial_price,
                scenario,
                progress=lambda current, total: repository.update_run_progress(run_id, int(current / total * 95)),
            )
            payload = {
                "run_id": run_id,
                "model_version": MODEL_VERSION,
                "seed": scenario.seed,
                "scenario": scenario_row["config"],
                "metrics": {
                    "probability_of_cascade": monte_carlo.summary["probability_of_cascade"],
                    "expected_shortfall_95": monte_carlo.summary["expected_shortfall_95"],
                },
                "monte_carlo": monte_carlo.to_dict(),
                "events": [],
                "timeseries": [],
            }
        else:
            payload = run_simulation(positions, dex_state, initial_price, scenario, run_id=run_id).to_dict()
        repository.complete_run(run_id, payload)
        logger.info(
            "simulation complete",
            extra={
                "run_id": run_id,
                "snapshot_id": scenario_row["snapshot_id"],
                "duration_ms": round((perf_counter() - started) * 1000, 3),
                "positions_processed": len(positions),
            },
        )
        return payload
    except Exception as exc:
        repository.fail_run(run_id, str(exc))
        raise
