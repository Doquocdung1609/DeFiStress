from __future__ import annotations

import json
from argparse import ArgumentParser
from pathlib import Path

from backend.app.services.terra_datasets import import_research_dataset
from sim.terra.schemas import DataStatus


def main() -> None:
    parser = ArgumentParser(description="Normalize an imported Terra source into a versioned hourly JSON dataset.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--start", help="Documented source window start; filtering belongs upstream.")
    parser.add_argument("--end", help="Documented source window end; filtering belongs upstream.")
    parser.add_argument("--status", default="PARTIAL", choices=["REAL_HISTORICAL", "PARTIAL", "QUALITY_WARNING"])
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite processed data: {args.output}")
    dataset = import_research_dataset(
        args.input,
        args.dataset_version,
        DataStatus(args.status),
        "hourly-build-input",
        "IMPORTED",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {"manifest": dataset.manifest.to_dict(), "observations": [row.to_dict() for row in dataset.observations]},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(args.output)


if __name__ == "__main__":
    main()
