from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.research.terra_v2.audit_p04_01 import audit, csv_profile, main, strict_json


def fixture(root: Path) -> dict:
    data = b"timestamp,x\n2022-05-01T00:00:00Z,0\n2022-05-01T01:00:00Z,\n"
    (root / "data.csv").write_bytes(data)
    return dict(
        source_commit="synthetic-fixture",
        verified_inputs=[
            dict(
                path="data.csv",
                size_bytes=len(data),
                sha256_git_bytes=hashlib.sha256(data).hexdigest(),
                git_blob_sha1=hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
                csv_profile=dict(
                    rows=2,
                    fields=["timestamp", "x"],
                    missing={"timestamp": 0, "x": 1},
                    first="2022-05-01T00:00:00+00:00",
                    last="2022-05-01T01:00:00+00:00",
                ),
            )
        ],
    )


def test_zero_missing_and_no_pit_promotion(tmp_path):
    result = audit(tmp_path, fixture(tmp_path))
    assert result["counts"] == {"PASS": 1, "FAIL": 0}
    assert result["checks"][0]["csv_profile"]["missing"]["x"] == 1
    assert result["point_in_time_eligible_fields"] == 0
    assert result["historical_backtest_executed"] is False


@pytest.mark.parametrize(
    "mutation", ["tamper", "crlf", "bool_size", "missing", "duplicate", "profile", "escape", "malformed"]
)
def test_invalid_source_is_not_silently_passed(tmp_path, mutation):
    registry = fixture(tmp_path)
    row = registry["verified_inputs"][0]
    if mutation == "tamper":
        (tmp_path / "data.csv").write_bytes(b"changed")
    elif mutation == "crlf":
        p = tmp_path / "data.csv"
        p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
    elif mutation == "bool_size":
        row["size_bytes"] = True
    elif mutation == "missing":
        (tmp_path / "data.csv").unlink()
    elif mutation == "duplicate":
        registry["verified_inputs"].append(row.copy())
    elif mutation == "profile":
        row["csv_profile"]["rows"] = 3
    elif mutation == "escape":
        row["path"] = "../data.csv"
    else:
        registry["verified_inputs"] = [None]
    result = audit(tmp_path, registry)
    assert result["status"] == "FAIL"
    assert result["counts"]["FAIL"] >= 1
    assert result["historical_backtest_executed"] is False


@pytest.mark.parametrize("payload", ['{"a":1,"a":2}', '{"a":NaN}', "[]"])
def test_strict_json(payload):
    with pytest.raises(ValueError):
        strict_json(payload)


@pytest.mark.parametrize(
    "data",
    [
        b"timestamp,x\n2022-05-01T00:00:00,1\n",
        b"timestamp,x\n2022-05-01T00:00:00Z,1\n2022-05-01T00:00:00Z,2\n",
        b"timestamp,x\n2022-05-01T01:00:00Z,1\n2022-05-01T00:00:00Z,2\n",
        b"timestamp,x,x\n2022-05-01T00:00:00Z,1,2\n",
        b"timestamp,x\n2022-05-01T00:00:00Z,1,2\n",
    ],
)
def test_bad_csv_clock_or_shape(data):
    with pytest.raises(ValueError):
        csv_profile(data)


def test_failure_report_written(tmp_path):
    registry = fixture(tmp_path)
    (tmp_path / "data.csv").unlink()
    p = tmp_path / "registry.json"
    p.write_text(json.dumps(registry))
    out = tmp_path / "report.json"
    assert main(["--repo-root", str(tmp_path), "--registry", str(p), "--output", str(out)]) == 1
    assert json.loads(out.read_text())["checks"][0]["status"] == "FAIL"


def test_malformed_registry_report_written(tmp_path):
    p = tmp_path / "registry.json"
    p.write_text("{bad")
    out = tmp_path / "report.json"
    assert main(["--repo-root", str(tmp_path), "--registry", str(p), "--output", str(out)]) == 1
    assert json.loads(out.read_text())["status"] == "FAIL"


def test_report_write_failure_returns_nonzero(tmp_path, capsys):
    p = tmp_path / "registry.json"
    p.write_text(json.dumps(fixture(tmp_path)))
    block = tmp_path / "parent"
    block.write_text("not a directory")
    assert main(["--repo-root", str(tmp_path), "--registry", str(p), "--output", str(block / "out.json")]) == 2
    assert "REPORT_WRITE_FAILED" in capsys.readouterr().out
