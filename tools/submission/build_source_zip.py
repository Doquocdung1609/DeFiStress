"""Package tracked demo source with bounded evidence, excluding bulky raw research inputs."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

REPO = Path(__file__).resolve().parents[2]
EXCLUDED_PREFIXES = (
    "data/raw/",
    "data/processed/research_final/level3_extension/deep_stress/checkpoints/",
)
MAX_SINGLE_FILE = 8_000_000


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=REPO).split(b"\0")
    files = [path.decode("utf-8") for path in tracked if path]
    included: list[str] = []
    excluded: list[dict[str, object]] = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for relative in files:
            source = REPO / relative
            excluded_prefix = any(relative.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
            if excluded_prefix or source.stat().st_size > MAX_SINGLE_FILE:
                excluded.append({"path": relative, "reason": "raw/large research evidence distributed separately"})
                continue
            archive.write(source, relative)
            included.append(relative)
        archive.writestr(
            "SOURCE_ZIP_SCOPE.json",
            json.dumps(
                {
                    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
                    "hash_domain": "working-tree checkout bytes; Git blobs may use LF instead of Windows CRLF",
                    "included_tracked_files": len(included),
                    "excluded": excluded,
                    "note": (
                        "Raw historical replication inputs and large locked research artifacts remain in the GitHub "
                        "repository; local demo fixture and code are included."
                    ),
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
    print(json.dumps({
        "zip": str(args.output), "bytes": args.output.stat().st_size,
        "included": len(included), "excluded": len(excluded),
    }))


if __name__ == "__main__":
    main()
