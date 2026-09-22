from __future__ import annotations

import argparse
import csv
import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt

from sim import Scenario, run_simulation
from sim.fixtures import FIXTURE_PRICE, fixture_dex, fixture_positions
from sim.monte_carlo import run_monte_carlo
from sim.schemas import json_safe

EXPERIMENTS = {
    "E1": [("shock_pct", value) for value in (-5, -10, -15, -20, -25, -30, -35, -40)],
    "E2": [("liquidity_haircut_pct", 100 - value) for value in (100, 75, 50, 25)],
    "E3": [
        *[("gas_multiplier", value) for value in (1, 2, 4)],
        *[("liquidator_capacity_usdc", value) for value in (500_000, 2_500_000, 10_000_000)],
    ],
    "E4": [("arbitrage_capacity_pct", value) for value in (0, 25, 50, 100)],
    "E5": [
        *[("ltv_override", Decimal(value)) for value in ("0.75", "0.80", "0.825")],
        *[("liquidation_threshold_override", Decimal(value)) for value in ("0.78", "0.80", "0.825", "0.85")],
        *[("liquidation_bonus_override", Decimal(value)) for value in ("1.03", "1.05", "1.08")],
    ],
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a reproducible DeFiStress experiment matrix")
    parser.add_argument("--snapshot", default="fixture-main-v1")
    parser.add_argument("--experiment", choices=sorted(EXPERIMENTS), default="E1")
    parser.add_argument("--output", type=Path, default=Path("data/experiments"))
    args = parser.parse_args()
    if args.snapshot != "fixture-main-v1":
        raise SystemExit(
            "This CLI currently accepts fixture-main-v1; use the API/database for cached Mainnet snapshots."
        )
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for parameter, value in EXPERIMENTS[args.experiment]:
        scenario = replace(Scenario(), **{parameter: value})
        result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)
        monte_carlo = run_monte_carlo(
            fixture_positions(), fixture_dex(), FIXTURE_PRICE, replace(scenario, monte_carlo_runs=100)
        )
        rows.append(
            {
                "parameter": parameter,
                "value": json_safe(value),
                **json_safe(result.metrics),
                "probability_of_cascade": monte_carlo.summary["probability_of_cascade"],
                "expected_shortfall_95": monte_carlo.summary["expected_shortfall_95"],
            }
        )
    stem = args.output / f"{args.experiment.lower()}_fixture"
    with stem.with_suffix(".json").open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)
    with stem.with_suffix(".csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    figure, axis = plt.subplots(figsize=(10, 5.5), dpi=140)
    x_values = list(range(len(rows)))
    axis.plot(x_values, [row["total_liquidated_debt"] for row in rows], marker="o", label="Liquidated debt")
    axis.plot(x_values, [row["bad_debt"] for row in rows], marker="o", label="Bad debt")
    labels = [f"{row['parameter']}={row['value']}" for row in rows]
    axis.set_xticks(x_values, labels, rotation=35, ha="right")
    axis.set_xlabel("Scenario parameter")
    axis.set_ylabel("USDC")
    axis.set_title(f"{args.experiment} fixture sensitivity")
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(stem.with_suffix(".png"))
    plt.close(figure)
    print(f"Wrote {stem.with_suffix('.json')}, {stem.with_suffix('.csv')}, and {stem.with_suffix('.png')}")


if __name__ == "__main__":
    main()
