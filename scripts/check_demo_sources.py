"""Check that demo composition preserves the candidate source Git blobs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "docs/demo/CANDIDATE_SOURCES.json").read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


checked = 0
for number, candidate in manifest["candidate_prs"].items():
    for path in candidate["paths"]:
        expected = git("rev-parse", f"{candidate['head']}:{path}")
        actual = git("rev-parse", f":{path}")
        if actual != expected:
            raise SystemExit(f"PR #{number} candidate changed: {path}")
        checked += 1
if checked != 61:
    raise SystemExit(f"Expected 61 candidate files, checked {checked}")
frozen = git(
    "diff", "--name-only", manifest["integration_base"], "--",
    "sim/terra", "terra_may2022_v1_pack", "data/processed/terra_extended",
)
if frozen:
    raise SystemExit(f"Frozen research paths changed:\n{frozen}")
print(f"PASS: {checked} candidate Git blobs exact; accepted Terra source/data unchanged")
