from __future__ import annotations

import argparse
import json
from pathlib import Path

from sim.terra.stress_test import DEFAULT_STRESS_START, StressScenario, run_stress_test


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Terra counterfactual stress scenario.")
    parser.add_argument("--output", type=Path, default=Path("data/processed/terra_demo/stress_test.json"))
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20220506)
    parser.add_argument("--start", default=DEFAULT_STRESS_START)
    args = parser.parse_args()
    payload = run_stress_test(StressScenario(), runs=args.runs, seed=args.seed, start_timestamp=args.start)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Stress Test: {payload['summary']['wording']} -> {args.output}")


if __name__ == "__main__":
    main()
