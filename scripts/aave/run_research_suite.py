from __future__ import annotations

import argparse
import json
from pathlib import Path

from sim.research.aave_suite import CANONICAL_SNAPSHOT, DEFAULT_OUTPUT, run_aave_research_suite


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the canonical REAL_MAINNET Aave research suite.")
    parser.add_argument("--snapshot", type=Path, default=CANONICAL_SNAPSHOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--fast", action="store_true")
    args = parser.parse_args()
    result = run_aave_research_suite(snapshot_path=args.snapshot, output_dir=args.output_dir, fast=args.fast)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
