from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.research.package_builder import DEFAULT_OUTPUT, run_full_research_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the complete DeFiStress scientific research package.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--research", action="store_true", help="Run the default scientific workload (default).")
    mode.add_argument("--fast", action="store_true", help="Use reduced candidate/run counts for pipeline validation.")
    parser.add_argument("--fresh-mainnet", action="store_true", help="Attempt an optional live Mainnet appendix.")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip preflight test/build commands (recorded in manifest).",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT, help="Generated research output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_full_research_pipeline(
        output_dir=args.output_dir,
        fast=args.fast,
        fresh_mainnet=args.fresh_mainnet,
        skip_tests=args.skip_tests,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
