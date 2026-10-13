from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize non-self-referential research artifact provenance.")
    parser.add_argument("artifact_commit", help="Commit that first contains the generated artifact bundle.")
    parser.add_argument("--manifest", type=Path, default=Path("data/processed/research_final/manifest.json"))
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest["generated_artifact_commit"] = args.artifact_commit
    manifest["metadata_finalization_commit"] = None
    manifest["provenance_note"] = (
        "source_code_commit identifies executable source; generated_artifact_commit identifies the first "
        "bundle commit; the metadata finalization commit is the Git commit containing this update and is "
        "intentionally not self-recorded."
    )
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
