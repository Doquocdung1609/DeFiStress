"""Reproduce synthetic examples and saved-metadata/source-byte delivery checks.

No historical observation is passed into a model. Runtime QA/JUnit comes from the
explicit external evidence directory, with original failures retained separately.
"""

from __future__ import annotations

import argparse
import ast
import csv
import gzip
import hashlib
import json
import platform
import runpy
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = Path(__file__).resolve().parent
BASE = "c51d4d06d8b560a149e32ade922f8ed62da1a589"
sys.path.insert(0, str(ROOT))


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write(name: str, payload: object) -> None:
    (DOCS / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-c", "core.autocrlf=false", *args], cwd=ROOT)


def junit(path: Path) -> dict[str, object]:
    root = ET.fromstring(path.read_bytes())
    cases = list(root.iter("testcase"))
    failures = sum(case.find("failure") is not None for case in cases)
    errors = sum(case.find("error") is not None for case in cases)
    skipped = sum(case.find("skipped") is not None for case in cases)
    counts: dict[str, object] = {
        "tests": len(cases),
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "passed": len(cases) - failures - errors - skipped,
        "sha256": sha(path.read_bytes()),
    }
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    for key in ("tests", "failures", "errors", "skipped"):
        assert sum(int(suite.attrib[key]) for suite in suites) == counts[key], path
    return counts


def clock_witness() -> list[dict[str, object]]:
    """Only the eight registered cells, no onset search, feature, or scoring."""
    import pyarrow.parquet as pq

    processed = ROOT / "data/processed"
    raw = ROOT / "data/raw/terra_may2022_v1/replication/terra-luna-run-replication/data/prices"
    records = []
    for asset in ("ust", "luna"):
        table = pq.read_table(raw / f"{asset}_price_may2022.parquet").to_pylist()
        values = {str(row["time"]): row[f"{asset}_price"] for row in table}
        for file, minute in (
            ("terra_may2022_v1.csv", "59"),
            ("terra_extended/terra_state_hourly_20220301_20220513.csv", "00"),
        ):
            rows = list(csv.DictReader((processed / file).open(encoding="utf-8", newline="")))
            for hour in (22, 23):
                label = f"2022-05-07 {hour}:00:00"
                selected = [row for row in rows if row["timestamp"].replace("T", " ").startswith(label)]
                assert len(selected) == 1
                expected = values[f"2022-05-07 {hour}:{minute}:00"]
                actual = float(selected[0][f"{asset}_price"])
                assert actual == expected
                records.append(
                    {
                        "asset": asset,
                        "processed_path": file,
                        "hour_label": label,
                        "raw_minute_label": f"2022-05-07 {hour}:{minute}:00",
                        "same_saved_value": True,
                        "vendor_timezone_verified": False,
                        "claim": "SAVED_CLOCK_MAPPING_ONLY_NO_ONSET_OR_WARNING",
                    }
                )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence_dir

    from defistress_v2.contracts import canonical_json_bytes
    from defistress_v2.terra_warning import ModelId, evaluate, toy_config
    from defistress_v2.terra_warning.contracts import PROFILES, SCHEMA

    helpers = runpy.run_path(str(ROOT / "tests/v2/terra_warning/test_warning.py"))
    fixture = helpers["inputs"]("0.99", current="90")
    ctx = helpers["context"]()
    config = toy_config()
    example = evaluate(ModelId.B3, fixture, ctx, config)
    write(
        "SYNTHETIC_EXAMPLE.json",
        json.loads(
            canonical_json_bytes(
                {
                    "fixture": {"ust": fixture.ust, "luna": fixture.luna},
                    "output": example,
                    "output_hash": example.output_hash,
                    "fixture_hash": sha(
                        canonical_json_bytes({"ust": fixture.ust, "luna": fixture.luna}, schema_version=SCHEMA)
                    ),
                },
                schema_version=SCHEMA,
            )
        ),
    )
    summaries = []
    for control, ust, luna, expected in (
        ("M01", "1", "100", (0, 1)),
        ("M02", "0.99", "100", (1, 4)),
        ("M03", "1", "90", (1, 4)),
        ("M04", "0.99", "90", (1, 2)),
        ("M05", "0.98", "80", (1, 1)),
    ):
        decision = evaluate(ModelId.B3, helpers["inputs"](ust, current=luna), ctx, config)
        assert decision.score is not None
        assert (decision.score.numerator, decision.score.denominator) == expected
        summaries.append(
            {
                "control": control,
                "fixture_origin": "SYNTHETIC",
                "ust": ust,
                "luna_previous": "100",
                "luna_current": luna,
                "composite_expected": list(expected),
                "risk_level": decision.level.value,
                "output_hash": decision.output_hash,
            }
        )
    write("REFERENCE_VECTORS.json", summaries)

    matrix = []
    for number in range(1, 13):
        deferred = number in (9, 10)
        matrix.append(
            {
                "id": f"P04-M{number:02}",
                "disposition": "EVALUATION_SEMANTICS_DEFERRED_P04_04" if deferred else "IMPLEMENTED_SYNTHETIC_CONTROLS",
                "test_file": "tests/v2/terra_warning/test_warning.py",
                "test_name_contains": f"m{number:02}" if number not in (1, 2, 3, 4, 5) else "m01_to_m05",
                "historical_evaluation_executed": False,
                "note": "Quiet model behavior tested; metrics/episodes are design-only"
                if deferred
                else "Independent synthetic expectations; not a historical capability claim",
            }
        )
    write("CONTROL_MATRIX.json", matrix)

    pit = ROOT / "docs/research_v2/terra_early_warning/p04_01"
    manifest = json.loads((pit / "P04_01_POINT_IN_TIME_MANIFEST.json").read_bytes())
    registry = json.loads((pit / "P04_01_DATASET_REGISTRY.json").read_bytes())
    assert len(manifest["field_admission"]) == 14
    assert all(row["approved_forecast_use"] is False for row in manifest["field_admission"])
    write(
        "HISTORICAL_FIELD_MAPPING.json",
        {
            "scope": "COPIED_ACCEPTED_METADATA_NO_HISTORICAL_SCORING",
            "approved_fields": 0,
            "source_commit": registry["source_commit"],
            "integration_base": BASE,
            "manifest_sha256": sha((pit / "P04_01_POINT_IN_TIME_MANIFEST.json").read_bytes()),
            "registry_sha256": sha((pit / "P04_01_DATASET_REGISTRY.json").read_bytes()),
            "field_admission": manifest["field_admission"],
            "source_byte_records": registry["verified_inputs"],
        },
    )
    write("PR53_CLOCK_WITNESS.json", clock_witness())

    preserved = []
    for line in git("ls-tree", "-r", "-z", BASE).split(b"\0"):
        if not line:
            continue
        metadata, path_bytes = line.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        assert kind == "blob" and mode in {"100644", "100755"}
        path = path_bytes.decode()
        raw_bytes = (ROOT / path).read_bytes()
        calculated = hashlib.sha1(b"blob " + str(len(raw_bytes)).encode() + b"\0" + raw_bytes).hexdigest()
        assert calculated == oid, (path, "BASELINE_SOURCE_BYTES_CHANGED")
        preserved.append({"path": path, "git_blob_sha1": oid})
    write(
        "SOURCE_PRESERVATION.json",
        {
            "base": BASE,
            "original_blob_count": len(preserved),
            "changed_original_paths": [],
            "original_blob_manifest_sha256": sha(json.dumps(preserved, sort_keys=True).encode()),
            "claim": "Every baseline path verified from exact Git blob bytes, including frozen evidence",
        },
    )

    wheel = next((evidence / "wheel").glob("*.whl"))
    wheel_sources = sorted((ROOT / "defistress_v2").rglob("*.py")) + [ROOT / "defistress_v2/py.typed"]
    with zipfile.ZipFile(wheel) as archive:
        for path in wheel_sources:
            assert archive.read(path.relative_to(ROOT).as_posix()) == path.read_bytes(), path

    test_reports = {path.name: junit(path) for path in sorted(evidence.glob("*.xml"))}
    for name in ("linux-warning.xml", "linux-accepted-regressions.xml", "linux-pr55.xml"):
        report = test_reports[name]
        assert report["failures"] == report["errors"] == report["skipped"] == 0
    linux = json.loads((evidence / "linux-execution.json").read_bytes())
    assert all(item["exit_code"] == 0 for item in linux["results"])
    # Published independent controls are source-equivalent, not a rewritten easier version.
    published = ast.dump(ast.parse((evidence / "pr55-published-independent-controls.py").read_text()))
    actual = ast.dump(ast.parse((evidence / "pr55/tests/v2/test_valuation_independent_review.py").read_text()))
    assert published == actual
    snapshot_sources = []
    downloads = Path.home() / "Downloads"
    for name in ("# DEFISTRESS V2 - COMMANDER PRIORIT.txt", "# DEFISTRESS V2 - COLLABORATOR CODE.txt"):
        path = downloads / name
        snapshot_sources.append({"filename": name, "sha256": sha(path.read_bytes()), "size": path.stat().st_size})
    runtime_hashes = {path.name: sha(path.read_bytes()) for path in sorted(evidence.iterdir()) if path.is_file()}
    retained = DOCS / "evidence"
    retained.mkdir(exist_ok=True)
    portable_names = (
        "linux-warning.xml",
        "linux-accepted-regressions.xml",
        "linux-pr55.xml",
        "linux-prephase.xml",
        "linux-execution.json",
        "linux-L1-L2.json",
        "linux-pit-smoke.json",
        "linux-source-audit.json",
        "static-reviews.json",
        "pr55-independent-recalculation.json",
        "accepted-regressions.xml",
        "warning.xml",
        "warning-coverage.json",
        "run_linux.py",
    )
    for name in portable_names:
        raw_evidence = (evidence / name).read_bytes()
        if b"\r\n" in raw_evidence:
            # Preserve raw evidence bytes without letting Git normalize CRLF.
            (retained / (name + ".gz")).write_bytes(gzip.compress(raw_evidence, mtime=0))
            if (retained / name).exists():
                (retained / name).unlink()
        else:
            shutil.copyfile(evidence / name, retained / name)
    for name in ("linux-L1-L2.json", "linux-pit-smoke.json", "linux-source-audit.json"):
        shutil.copyfile(evidence / "crlf-attempt" / name, retained / ("initial-crlf-" + name))
    sources = list((ROOT / "defistress_v2/terra_warning").glob("*.py")) + list(
        (ROOT / "tests/v2/terra_warning").glob("*.py")
    )
    write(
        "EVIDENCE.json",
        {
            "integration_base": BASE,
            "validated_source_commit": git("rev-parse", "HEAD").decode().strip(),
            "validated_source_tree": git("rev-parse", "HEAD^{tree}").decode().strip(),
            "delivery_head_location": "Exact final delivery HEAD is in the Draft PR description (no self-reference)",
            "source_hashes": {path.relative_to(ROOT).as_posix(): sha(path.read_bytes()) for path in sources},
            "authorization_inputs": snapshot_sources,
            "issue56_snapshot_sha256": sha((DOCS / "ISSUE56_SNAPSHOT.md").read_bytes()),
            "profiles": list(PROFILES),
            "configuration_hash": config.config_hash,
            "profile_hash": config.profile_hash,
            "model_output_example_hash": example.output_hash,
            "windows_environment": {"python": sys.version, "os": platform.platform()},
            "tool_versions": {
                name: version(name) for name in ("pytest", "ruff", "mypy", "build", "pyarrow", "pytest-cov")
            },
            "linux_environment_and_commands": linux,
            "junit": test_reports,
            "coverage": json.loads((evidence / "warning-coverage.json").read_bytes())["totals"],
            "wheel": {
                "filename": wheel.name,
                "sha256": sha(wheel.read_bytes()),
                "exact_v2_entries": len(wheel_sources),
            },
            "source_preservation": {"base": BASE, "original_blobs": len(preserved), "changed_paths": []},
            "local_evidence_directory": str(evidence),
            "external_evidence_sha256": runtime_hashes,
            "portable_evidence_sha256": {
                path.relative_to(DOCS).as_posix(): sha(path.read_bytes()) for path in retained.iterdir()
            },
            "known_initial_failures": [
                "Windows PIT regression: symlink WinError1314, one failure/two skips; unmodified tests pass in Linux",
                (
                    "First git archive inherited core.autocrlf=true: L1 3 hash failures and P04-01 27 failures; "
                    "raw Git-LF resolved all; original reports retained under crlf-attempt"
                ),
                "First warning lint: one unused import and one 121-character line; corrected before final QA",
            ],
            "scientific_status": [
                "GATE_A_BLOCKED",
                "GATE_B_SCOPED_PASS",
                "PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED",
                "TERRA_POINT_IN_TIME_ELIGIBILITY_BLOCKED",
                "HISTORICAL_BACKTEST_NOT_AUTHORIZED",
            ],
            "historical_approved_fields": 0,
            "historical_backtest_executed": False,
            "exit_experiment_executed": False,
            "hosted_ci": "CI_BLOCKED_BY_FREE_TIER_LIMIT_OR_BILLING_NO_RERUN_REQUESTED",
            "implementation_disposition": "P04_03_SYNTHETIC_WARNING_READY_FOR_INDEPENDENT_REVIEW",
        },
    )
    print(
        json.dumps(
            {
                "source_preservation": len(preserved),
                "wheel_exact_entries": len(wheel_sources),
                "warning_tests": test_reports["linux-warning.xml"],
                "source_byte_checks": "PASS",
            }
        )
    )


if __name__ == "__main__":
    main()
