"""Failure-evidence and deterministic-report controls for the P04-02 validator."""

from __future__ import annotations

import json
from pathlib import Path

from defistress_v2.terra_pit.validate import main


def test_validation_cli_writes_failure_evidence_before_nonzero_exit(tmp_path: Path) -> None:
    output = tmp_path / "report.json"
    exit_code = main(
        [
            "--repository-root",
            str(tmp_path),
            "--implementation-commit",
            "1" * 40,
            "--output",
            str(output),
        ]
    )
    assert exit_code == 1
    report = json.loads(output.read_bytes())
    assert report["status"] == "FAIL"
    assert report["point_in_time_eligibility"] == "BLOCKED_NOT_CLEARED_FOR_FORECAST"
    assert report["historical_backtest_executed"] is False


def test_validation_cli_reports_output_write_failure(tmp_path: Path, capsys: object) -> None:
    blocked = tmp_path / "blocked"
    blocked.write_text("not a directory", encoding="utf-8")
    assert (
        main(
            [
                "--repository-root",
                str(tmp_path),
                "--implementation-commit",
                "1" * 40,
                "--output",
                str(blocked / "report.json"),
            ]
        )
        == 2
    )
    assert "REPORT_WRITE_FAILED" in capsys.readouterr().out  # type: ignore[attr-defined]
