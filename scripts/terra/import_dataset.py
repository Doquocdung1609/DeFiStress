from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from _cli import import_file, write_json


def main() -> None:
    parser = ArgumentParser(description="Import a versioned Terra hourly CSV, Parquet, or JSON dataset.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--status", required=True, choices=["REAL_HISTORICAL", "FIXTURE", "PARTIAL", "QUALITY_WARNING"])
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-type", required=True)
    parser.add_argument("--chain-id", default="columbus-5")
    parser.add_argument("--raw-reference", default="manual-import")
    parser.add_argument("--database-url", default=None, help="Defaults to DATABASE_URL from .env / application settings.")
    parser.add_argument("--manifest-output", type=Path)
    args = parser.parse_args()
    write_json(args.manifest_output, import_file(args))


if __name__ == "__main__":
    main()
