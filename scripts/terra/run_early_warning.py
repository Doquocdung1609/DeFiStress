from __future__ import annotations

import argparse
import json
from pathlib import Path

from sim.terra.early_warning_v2 import build_early_warning


def main() -> None:
    parser = argparse.ArgumentParser(description="Build hourly Terra early-warning timelines.")
    parser.add_argument("--output", type=Path, default=Path("data/processed/terra_demo/early_warning_timeline.json"))
    args = parser.parse_args()
    payload = {
        "retrospective": build_early_warning(mode="RETROSPECTIVE"),
        "cutoff_safe": build_early_warning(mode="CUTOFF_SAFE"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Early Warning: {len(payload['cutoff_safe']['timeline'])} hourly scores -> {args.output}")


if __name__ == "__main__":
    main()
