from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from time import perf_counter

from sim import Scenario, run_simulation
from sim.fixtures import FIXTURE_PRICE, fixture_dex, fixture_positions


def position_cohort(size: int):
    base = fixture_positions()
    return [replace(base[index % len(base)], borrower_hash=f"benchmark-{index:06d}") for index in range(size)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark deterministic DeFiStress cohorts")
    parser.add_argument("--sizes", nargs="+", type=int, default=[1_000, 5_000])
    parser.add_argument("--output", type=Path, default=Path("data/benchmarks/latest.json"))
    args = parser.parse_args()
    rows = []
    for size in args.sizes:
        started = perf_counter()
        result = run_simulation(position_cohort(size), fixture_dex(), FIXTURE_PRICE, Scenario())
        duration = perf_counter() - started
        rows.append(
            {
                "positions": size,
                "duration_seconds": round(duration, 6),
                "events": len(result.events),
                "cascade_depth": result.metrics["cascade_depth"],
            }
        )
        print(f"{size} positions: {duration:.4f}s")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
