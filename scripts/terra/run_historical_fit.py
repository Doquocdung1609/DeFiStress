from __future__ import annotations

import argparse
import json
from pathlib import Path

from sim.terra.historical_fit import fit_historical


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Terra calibrated historical reconstruction.")
    parser.add_argument("--output", type=Path, default=Path("data/processed/terra_demo/historical_fit.json"))
    parser.add_argument("--candidates", type=int, default=900)
    args = parser.parse_args()
    payload = fit_historical(candidates=args.candidates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Historical Fit: objective={payload['objective']['value']:.6f} -> {args.output}")


if __name__ == "__main__":
    main()
