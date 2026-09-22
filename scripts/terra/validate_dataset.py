from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from _cli import write_json

from backend.app.services.terra_datasets import import_research_dataset
from sim.terra.schemas import DataStatus


def main() -> None:
    parser = ArgumentParser(description="Validate a Terra dataset and emit a quality report without persistence.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument(
        "--status",
        default="QUALITY_WARNING",
        choices=[item.value for item in DataStatus if item.value != "UNAVAILABLE"],
    )
    parser.add_argument("--source-name", default="manual-validation")
    parser.add_argument("--source-type", default="IMPORTED")
    parser.add_argument("--chain-id", default="columbus-5")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    dataset = import_research_dataset(
        args.input,
        args.dataset_version,
        DataStatus(args.status),
        args.source_name,
        args.source_type,
        args.chain_id,
    )
    write_json(args.output, {"manifest": dataset.manifest.to_dict(), "quality_report": dataset.manifest.quality_report})


if __name__ == "__main__":
    main()
