from __future__ import annotations

import json
import time
import tracemalloc
from argparse import ArgumentParser
from dataclasses import replace
from pathlib import Path

from sim.terra.fixtures import terra_fixture_dataset
from sim.terra.replay import HistoricalReplayExperiment, run_historical_replay


def main() -> None:
    parser = ArgumentParser(description="Benchmark vectorized Terra ABM configurations at 1k, 10k, and 100k agents.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    dataset = terra_fixture_dataset()
    base = HistoricalReplayExperiment(model_name="ABM")
    rows = []
    for agents in (1_000, 10_000, 100_000):
        tracemalloc.start()
        started = time.perf_counter()
        replay = run_historical_replay(dataset, replace(base, parameters={"agent_count": agents}))
        elapsed = time.perf_counter() - started
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        rows.append(
            {
                "configured_agents": agents,
                "execution_mode": replay["model"]["diagnostics"]["agent_mode"],
                "runtime_seconds": elapsed,
                "peak_memory_mb": peak / 1024 / 1024,
            }
        )
    payload = {"benchmark": rows, "note": "Cohort-vectorized execution; representative events retained."}
    rendered = json.dumps(payload, indent=2)
    if args.output:
        if args.output.exists():
            raise SystemExit(f"Refusing to overwrite benchmark output: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
