from __future__ import annotations

import json
from argparse import ArgumentParser
from pathlib import Path

from sim.terra.research_pipeline import (
    DEFAULT_DATASET,
    DEFAULT_NATIVE_SWAPS,
    DEFAULT_OUTPUT,
    DEFAULT_STRICT_V2,
    MONTE_CARLO_RUNS,
    run_final_pipeline,
)


def main() -> None:
    parser = ArgumentParser(description="Build the auditable Terra May 2022 final research bundle.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--strict-v2", type=Path, default=DEFAULT_STRICT_V2)
    parser.add_argument("--native-swaps", type=Path, default=DEFAULT_NATIVE_SWAPS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--monte-carlo-runs", type=int, default=MONTE_CARLO_RUNS)
    parser.add_argument(
        "--overwrite-final",
        action="store_true",
        help="Replace only data/processed/terra_final; frozen V1/V2 artifacts are never modified.",
    )
    args = parser.parse_args()
    result = run_final_pipeline(
        args.dataset,
        args.strict_v2,
        args.output_dir,
        args.native_swaps,
        args.overwrite_final,
        args.monte_carlo_runs,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
