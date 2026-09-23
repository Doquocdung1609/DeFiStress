from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "terra_final" / "test_evidence.json"


def _display(command: list[str]) -> str:
    return subprocess.list2cmdline(command) if os.name == "nt" else shlex.join(command)


def _counts(name: str, output: str) -> dict[str, Any]:
    if name == "pytest":
        match = re.search(r"(\d+) passed", output)
        return {"passed": int(match.group(1)) if match else None}
    if name == "frontend_tests":
        match = re.search(r"Tests\s+(\d+) passed", output)
        files = re.search(r"Test Files\s+(\d+) passed", output)
        return {
            "passed": int(match.group(1)) if match else None,
            "test_files_passed": int(files.group(1)) if files else None,
        }
    if name == "frontend_build":
        return {"compiled_successfully": "Compiled successfully" in output}
    return {}


def main() -> None:
    output_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUTPUT
    pnpm = "pnpm.cmd" if os.name == "nt" else "pnpm"
    checks = [
        ("ruff", [sys.executable, "-m", "ruff", "check", "backend", "sim", "tests", "scripts"], ROOT),
        ("mypy", [sys.executable, "-m", "mypy", "sim"], ROOT),
        ("pytest", [sys.executable, "-m", "pytest", "-q"], ROOT),
        ("frontend_tests", [pnpm, "test"], ROOT / "frontend"),
        ("frontend_lint", [pnpm, "lint"], ROOT / "frontend"),
        ("frontend_build", [pnpm, "build"], ROOT / "frontend"),
    ]
    results = []
    started_at = datetime.now(UTC)
    for name, command, cwd in checks:
        started = time.perf_counter()
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        rendered = completed.stdout
        results.append(
            {
                "name": name,
                "command": _display(command),
                "cwd": str(cwd),
                "exit_code": completed.returncode,
                "duration_seconds": round(time.perf_counter() - started, 3),
                "counts": _counts(name, rendered),
                "output_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                "output_tail": rendered[-4000:],
            }
        )
    payload = {
        "evidence_type": "LOCAL_TEST_RUN",
        "remote_ci_claimed": False,
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(UTC).isoformat(),
        "source_code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "all_passed": all(item["exit_code"] == 0 for item in results),
        "checks": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output_path)
    if not payload["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
