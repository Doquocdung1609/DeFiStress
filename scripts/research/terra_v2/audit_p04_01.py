"""Read-only byte/CSV inventory audit. Never generates features, scores or forecasts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

MAX_FILE_BYTES = 1_048_576


def _pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in items:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def strict_json(text: str) -> dict[str, Any]:
    def invalid(value: str) -> None:
        raise ValueError("NONFINITE_JSON:" + value)

    result = json.loads(text, object_pairs_hook=_pairs, parse_constant=invalid)
    if not isinstance(result, dict):
        raise ValueError("REGISTRY_NOT_OBJECT")
    return result


def csv_profile(data: bytes) -> dict[str, Any]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    fields = reader.fieldnames
    if not fields or len(set(fields)) != len(fields):
        raise ValueError("CSV_HEADER_INVALID")
    rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("CSV_ROW_WIDTH_INVALID")
    result: dict[str, Any] = dict(
        rows=len(rows),
        fields=fields,
        missing={k: sum(row[k] in ("", "NA", "NaN", "nan", "null") for row in rows) for k in fields},
    )
    if "timestamp" in fields:
        times = [datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")) for row in rows]
        if any(t.tzinfo is None or t.utcoffset() is None for t in times):
            raise ValueError("CSV_TIMEZONE_UNSPECIFIED")
        if len(set(times)) != len(times) or times != sorted(times):
            raise ValueError("CSV_TIMESTAMP_ORDER_OR_DUPLICATE")
        result.update(first=times[0].isoformat() if times else None, last=times[-1].isoformat() if times else None)
    return result


def audit(root: Path, registry: dict[str, Any]) -> dict[str, Any]:
    root = root.resolve(strict=True)
    checks: list[dict[str, Any]] = []
    rows = registry.get("verified_inputs")
    if not isinstance(rows, list) or not rows or len(rows) > 100:
        raise ValueError("VERIFIED_INPUTS_INVALID")
    seen: set[str] = set()
    for row in rows:
        entry: dict[str, Any] = {"path": row.get("path") if isinstance(row, dict) else None}
        try:
            if not isinstance(row, dict):
                raise ValueError("INPUT_RECORD_INVALID")
            path = row["path"]
            if not isinstance(path, str) or not path or path in seen:
                raise ValueError("DUPLICATE_OR_INVALID_PATH")
            seen.add(path)
            relative = Path(path)
            if relative.is_absolute() or ".." in relative.parts or "\\" in path or ":" in path:
                raise ValueError("PATH_ESCAPE")
            target = root / relative
            if any(p.is_symlink() for p in [target, *target.parents] if p != root and root in p.parents):
                raise ValueError("SYMLINK_INPUT")
            resolved = target.resolve(strict=True)
            if not resolved.is_relative_to(root) or not resolved.is_file():
                raise ValueError("PATH_ESCAPE_OR_NOT_FILE")
            expected_size = row["size_bytes"]
            if type(expected_size) is not int or not 0 <= expected_size <= MAX_FILE_BYTES:
                raise ValueError("DECLARED_SIZE_INVALID")
            if resolved.stat().st_size > MAX_FILE_BYTES:
                raise ValueError("INPUT_TOO_LARGE")
            data = resolved.read_bytes()
            actual = dict(
                size_bytes=len(data),
                sha256_git_bytes=hashlib.sha256(data).hexdigest(),
                git_blob_sha1=hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
            )
            if any(row[k] != actual[k] for k in actual):
                raise ValueError("BYTE_DOMAIN_MISMATCH")
            entry.update(actual)
            if "csv_profile" in row:
                measured = csv_profile(data)
                if measured != row["csv_profile"]:
                    raise ValueError("CSV_PROFILE_MISMATCH")
                entry["csv_profile"] = measured
            entry["status"] = "PASS"
        except (KeyError, ValueError, OSError, UnicodeError, csv.Error) as exc:
            entry.update(status="FAIL", reason=str(exc))
        checks.append(entry)
    return dict(
        scope="READ_ONLY_BYTES_AND_CSV_COUNTS_NOT_FORECAST_VALIDATION",
        source_commit=registry.get("source_commit"),
        checks=checks,
        counts={k: sum(x["status"] == k for x in checks) for k in ("PASS", "FAIL")},
        status="PASS" if all(x["status"] == "PASS" for x in checks) else "FAIL",
        point_in_time_eligible="BLOCKED",
        point_in_time_eligible_fields=0,
        historical_backtest_executed=False,
        exit_simulation_executed=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.registry.stat().st_size > 2_097_152:
            raise ValueError("REGISTRY_TOO_LARGE")
        report = audit(args.repo_root, strict_json(args.registry.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        report = dict(status="FAIL", reason=str(exc), historical_backtest_executed=False)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    except OSError:
        print(json.dumps(dict(status="FAIL", reason="REPORT_WRITE_FAILED")))
        return 2
    print(json.dumps({k: v for k, v in report.items() if k != "checks"}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
