"""Read-only Phase 01 evidence guard and isolated synthetic negative controls."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zlib
from collections.abc import Callable
from pathlib import Path

BASE = Path(__file__).resolve().parents[3]
PHASE = BASE / "docs/research_v2/phase01b"
REGISTERED = (26045352, 26038152, 26030952)
POOLS = {
    "P3000": ("0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8", 3000),
    "P500": ("0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640", 500),
}
EXPECTED_HASH = {
    26045352: "0x4dffe3bdf7bbaf24fd1e3b6c3f4795687dccfd3189cbfb61f4dbaf926722220a",
    26038152: "0xbb108203815f257e9f9b023f92a30e67d946799355ceffc4bef0e0e16a1e87bd",
    26030952: "0xeeb12db7f31e86507bb4be7a1a2953d19c11165c99a75ebc7aa589d65d0b9625",
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate_identity(chain: int, block: int, block_hash: str) -> bool:
    return chain == 1 and block in REGISTERED and block_hash.lower() == EXPECTED_HASH[block]


def validate_pool(address: str, fee: int, pool_id: str, token0: str, token1: str, usdc: str, weth: str) -> bool:
    return (
        pool_id in POOLS
        and (address.lower(), fee) == POOLS[pool_id]
        and token0.lower() == usdc.lower()
        and token1.lower() == weth.lower()
    )


def units(raw: int, decimals: int, expected_decimals: int) -> bool:
    return isinstance(raw, int) and not isinstance(raw, bool) and raw >= 0 and decimals == expected_decimals


def canonical_equal(expected: object, actual: object) -> bool:
    def normal(value):
        if isinstance(value, (tuple, list)):
            return [normal(x) for x in value]
        if isinstance(value, dict):
            return {k: normal(v) for k, v in value.items()}
        return value

    return normal(expected) == normal(actual)


def complete_fields(expected: dict, observed: dict) -> bool:
    return set(expected) == set(observed) and all(v is not None for v in observed.values())


def tick_band(ticks: list[dict], lower: int, upper: int, spacing: int) -> bool:
    values = [t["index"] for t in ticks]
    return (
        spacing > 0
        and lower <= upper
        and len(values) == len(set(values))
        and all(lower <= i <= upper and i % spacing == 0 for i in values)
        and all(t["gross"] >= abs(t["net"]) for t in ticks)
        and all(t["gross"] > 0 and t["bitmap_initialized"] for t in ticks)
    )


def liquidity_consistent(active: int, total: int) -> bool:
    return isinstance(active, int) and isinstance(total, int) and 0 <= active <= total


def oracle_valid(
    source: str,
    expected_source: str,
    round_id: int,
    timestamp: int,
    block_timestamp: int,
    spot_substituted: bool = False,
) -> bool:
    return (
        source.lower() == expected_source.lower()
        and not spot_substituted
        and isinstance(round_id, int)
        and round_id > 0
        and 0 < timestamp <= block_timestamp
    )


def borrower_complete(
    reserve_ids: list[int], required: list[int], debt_raw: dict[int, int], hf_wad: int | None
) -> bool:
    return (
        len(reserve_ids) == len(set(reserve_ids))
        and set(required).issubset(reserve_ids)
        and all(k in debt_raw and isinstance(debt_raw[k], int) and debt_raw[k] >= 0 for k in required)
        and isinstance(hf_wad, int)
        and hf_wad >= 0
    )


# Only these two explicitly documented scientific limitations are excluded from L1.
LIMITATIONS = {
    "ALCHEMY-VALUE-REPLAY": "NOT_REPLAYABLE_FROM_PERSISTED_SUMMARY",
    "BACKEND-INDEPENDENCE": "NO_REQUEST_LEVEL_DISTINCT_BACKEND_ATTESTATION",
}
STATUSES = ("PASS", "FAIL", "BLOCKED")


class CheckSchemaError(ValueError):
    """A producer emitted an invalid check; it must fail, never be repaired silently."""


def validate_check(record: object) -> None:
    if not isinstance(record, dict):
        raise CheckSchemaError("check must be an object")
    for field in ("id", "scope", "status", "reason"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise CheckSchemaError(f"check.{field} must be a nonempty string")
    if record["scope"] not in ("L1_INTEGRITY", "LIMITATION") or record["status"] not in STATUSES:
        raise CheckSchemaError("invalid check.scope or check.status")
    if "path" in record and not isinstance(record["path"], str):
        raise CheckSchemaError("check.path must be a string")
    if record["scope"] == "LIMITATION":
        if (
            record["id"] not in LIMITATIONS
            or record["status"] != "BLOCKED"
            or record["reason"] != LIMITATIONS[record["id"]]
        ):
            raise CheckSchemaError("unregistered or changed scientific limitation")
    elif record["id"] in LIMITATIONS:
        raise CheckSchemaError("registered limitation has wrong scope")


def check_record(
    check_id: str, status: str, reason: str, *, scope: str = "L1_INTEGRITY", path: str | None = None
) -> dict:
    record = {"id": check_id, "scope": scope, "status": status, "reason": reason}
    if path is not None:
        record["path"] = path
    validate_check(record)
    return record


def build_report(checks: object, validator_commit: str = "LOCAL_UNCOMMITTED") -> dict:
    valid = []
    errors = []
    seen = set()
    if isinstance(checks, list):
        candidates = checks
    else:
        candidates = []
        errors.append({"check_index": None, "error": "checks must be a list"})
        valid.append(check_record("REPORT-CONTAINER", "FAIL", "INVALID_CHECK_CONTAINER"))
    for index, record in enumerate(candidates):
        try:
            validate_check(record)
            if record["id"] in seen:
                raise CheckSchemaError("duplicate check.id")
            seen.add(record["id"])
        except CheckSchemaError as exc:
            # Reject the malformed producer record. This diagnostic is a NEW failed check,
            # not a fallback id assigned to the original record.
            errors.append({"check_index": index, "error": str(exc)})
            valid.append(check_record(f"REPORT-SCHEMA:{index}", "FAIL", "INVALID_CHECK_RECORD"))
        else:
            valid.append(record)
    if not valid:
        valid.append(check_record("REPORT-EMPTY", "FAIL", "NO_CHECKS_PRODUCED"))
    integrity = [x for x in valid if x["scope"] == "L1_INTEGRITY"]
    if not integrity:
        integrity = [check_record("REPORT-NO-L1", "FAIL", "NO_INTEGRITY_CHECKS")]
        valid.extend(integrity)
    status = (
        "FAIL"
        if any(x["status"] == "FAIL" for x in integrity)
        else ("BLOCKED" if any(x["status"] == "BLOCKED" for x in integrity) else "PASS")
    )
    return {
        "schema": "defistress-prephase02-offline-v1.1",
        "source_commit": "2e0ec142c475f8d1362f90c4ca8d2f0718e41f77",
        "validator_commit": validator_commit,
        "validator_bytes_sha256": digest(Path(__file__).read_bytes()),
        "L1_INTEGRITY": status,
        "L2_CONTRACTS": "REQUIRES_TEST_EXECUTION",
        "GATE_A": "BLOCKED_BACKEND_INDEPENDENCE",
        "GATE_B": "PASS_REGISTERED_CORE_SCOPE",
        "PHASE02_AUTHORIZATION": "NOT_AUTHORIZED",
        "checks": valid,
        "report_errors": errors,
        "counts": {s: sum(x["status"] == s for x in valid) for s in STATUSES},
        "L1_counts": {s: sum(x["status"] == s for x in integrity) for s in STATUSES},
    }


def file_record(root: Path, row: object, *, check_id: str) -> dict:
    def result(status: str, reason: str, path: str | None = None) -> dict:
        return check_record(check_id, status, reason, path=path)

    if not isinstance(row, dict):
        return result("FAIL", "MANIFEST_ROW_NOT_OBJECT")
    required = {"path": str, "size_bytes": int, "sha256": str}
    if any(type(row.get(k)) is not t for k, t in required.items()):
        return result("FAIL", "MANIFEST_ROW_SCHEMA_INVALID")
    if not row["path"] or row["size_bytes"] < 0 or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
        return result("FAIL", "MANIFEST_ROW_SCHEMA_INVALID")
    compressed = "uncompressed_sha256" in row or "uncompressed_size" in row
    if compressed and (
        type(row.get("uncompressed_size")) is not int
        or row["uncompressed_size"] < 0
        or not isinstance(row.get("uncompressed_sha256"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", row["uncompressed_sha256"])
    ):
        return result("FAIL", "MANIFEST_GZIP_SCHEMA_INVALID")
    relative = Path(row["path"])
    target = root / relative
    if relative.is_absolute() or ".." in relative.parts or not target.resolve().is_relative_to(root.resolve()):
        return result("FAIL", "PATH_ESCAPE", str(relative))
    if not target.is_file():
        return result("BLOCKED", "FILE_MISSING", str(relative))
    try:
        raw = target.read_bytes()
    except OSError:
        return result("BLOCKED", "FILE_READ_ERROR", str(relative))
    if len(raw) != row["size_bytes"] or digest(raw) != row["sha256"]:
        return result("FAIL", "DIGEST_MISMATCH", str(relative))
    if compressed:
        try:
            decoded = gzip.decompress(raw)
        except (OSError, EOFError, zlib.error):
            return result("FAIL", "GZIP_INVALID", str(relative))
        if digest(decoded) != row["uncompressed_sha256"] or len(decoded) != row["uncompressed_size"]:
            return result("FAIL", "DECODED_DIGEST_MISMATCH", str(relative))
    return result("PASS", "BYTE_HASH_AND_SIZE", str(relative))


def load_object(path: Path, check_id: str, checks: list) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        checks.append(check_record(check_id, "BLOCKED", "JSON_INPUT_MISSING", path=str(path)))
        return None
    except OSError:
        checks.append(check_record(check_id, "BLOCKED", "JSON_INPUT_UNREADABLE", path=str(path)))
        return None
    except (UnicodeError, json.JSONDecodeError):
        checks.append(check_record(check_id, "FAIL", "JSON_INPUT_INVALID", path=str(path)))
        return None
    if not isinstance(value, dict):
        checks.append(check_record(check_id, "FAIL", "JSON_ROOT_NOT_OBJECT", path=str(path)))
        return None
    return value


def evaluate(check_id: str, predicate: Callable[[], bool], checks: list) -> None:
    try:
        passed = predicate()
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
        # External JSON shape is invalid; retain an explicit failing diagnostic.
        record = check_record(check_id, "FAIL", "INPUT_SCHEMA_INVALID")
        record["error_type"] = type(exc).__name__
        checks.append(record)
    else:
        checks.append(
            check_record(
                check_id,
                "PASS" if passed else "FAIL",
                "REGISTERED_CHECK_PASSED" if passed else "REGISTERED_CHECK_FAILED",
            )
        )


def run_offline(validator_commit: str = "LOCAL_UNCOMMITTED") -> dict:
    checks = []
    reg = load_object(PHASE / "SAMPLE_REGISTRATION.json", "REG-INPUT", checks)
    alchemy = load_object(PHASE / "alchemy_crosscheck/VERIFIED_CI_EVIDENCE.json", "ALCHEMY-INPUT", checks)
    provenance = load_object(PHASE / "EVIDENCE_PROVENANCE.json", "PROVENANCE-INPUT", checks)
    if reg is not None:
        evaluate("REG-CHAIN", lambda: reg["chain_id"] == 1, checks)
        evaluate(
            "REG-BLOCKS",
            lambda: (
                tuple(b["number"] for b in reg["blocks"]) == REGISTERED
                and all(validate_identity(reg["chain_id"], b["number"], b["expected_hash"]) for b in reg["blocks"])
            ),
            checks,
        )
        evaluate(
            "REG-POOLS",
            lambda: (
                all((p["address"].lower(), p["fee"]) == POOLS[p["id"]] for p in reg["pools"]) and len(reg["pools"]) == 2
            ),
            checks,
        )
        evaluate(
            "REG-DECIMALS",
            lambda: (reg["tokens"]["USDC"]["decimals"], reg["tokens"]["WETH"]["decimals"]) == (6, 18),
            checks,
        )
        evaluate("REG-V1", lambda: reg["v1_tag"] == "v1.0.0-scientific-baseline", checks)
    if alchemy is not None:
        evaluate(
            "ALCHEMY-SUMMARY",
            lambda: (
                alchemy["summary"]["agreeing"] == alchemy["summary"]["total_field_comparisons"] == 174
                and alchemy["summary"]["missing"] == alchemy["summary"]["mismatch"] == 0
                and alchemy["verdicts"]["independent_backend"] == "UNVERIFIED"
                and not alchemy["verdicts"]["phase02_authorized"]
                and all(b["hash"] == EXPECTED_HASH[b["number"]] for b in alchemy["blocks"])
            ),
            checks,
        )
    for manifest_path in (
        "evidence/full/collection_manifest.json",
        "evidence/borrower_repair/collection_manifest.json",
    ):
        manifest_file = PHASE / manifest_path
        manifest = load_object(manifest_file, f"MANIFEST:{manifest_path}", checks)
        if manifest is None:
            continue
        if not isinstance(manifest.get("files"), list) or not manifest["files"]:
            checks.append(check_record(f"MANIFEST:{manifest_path}", "FAIL", "MANIFEST_FILES_INVALID"))
            continue
        for index, row in enumerate(manifest["files"]):
            checks.append(file_record(manifest_file.parent, row, check_id=f"FILE:{manifest_path}:{index}"))
    if provenance is not None:
        evaluate(
            "PROVENANCE-SIZE",
            lambda: isinstance(provenance["files"], list) and len(provenance["files"]) == provenance["file_count"],
            checks,
        )
    for check_id, reason in LIMITATIONS.items():
        checks.append(check_record(check_id, "BLOCKED", reason, scope="LIMITATION"))
    return build_report(checks, validator_commit)


def attach_l2(report: dict, junit_path: Path, exit_code: int) -> dict:
    """Read actual JUnit; never infer L2 PASS from an earlier L1 exit code."""
    report["L2_CONTRACTS"] = "BLOCKED"
    report["L2_TEST_RESULTS"] = {"reason": "JUNIT_MISSING"}
    try:
        raw = junit_path.read_bytes()
    except FileNotFoundError:
        return report
    except OSError:
        report["L2_TEST_RESULTS"]["reason"] = "JUNIT_UNREADABLE"
        return report
    try:
        root = ET.fromstring(raw)
        if root.tag not in ("testsuites", "testsuite"):
            raise ValueError("invalid JUnit root")
        cases = list(root.iter("testcase"))
        suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
        failed = sum(c.find("failure") is not None for c in cases)
        errors = sum(c.find("error") is not None for c in cases)
        skipped = sum(c.find("skipped") is not None for c in cases)
        if (
            not cases
            or not suites
            or any(sum(c.find(k) is not None for k in ("failure", "error", "skipped")) > 1 for c in cases)
        ):
            raise ValueError("empty or inconsistent test cases")
        observed = (len(cases), failed, errors, skipped)
        declared = tuple(sum(int(s.attrib[k]) for s in suites) for k in ("tests", "failures", "errors", "skipped"))
        if observed != declared:
            raise ValueError("JUnit counters disagree with cases")
    except (ET.ParseError, KeyError, TypeError, ValueError):
        report["L2_CONTRACTS"] = "FAIL"
        report["L2_TEST_RESULTS"] = {"reason": "JUNIT_INVALID", "sha256": digest(raw)}
        return report
    status = "FAIL" if failed or errors or exit_code else "BLOCKED" if skipped else "PASS"
    report["L2_CONTRACTS"] = status
    report["L2_TEST_RESULTS"] = {
        "tests": len(cases),
        "passed": len(cases) - failed - errors - skipped,
        "failures": failed,
        "errors": errors,
        "skipped": skipped,
        "pytest_exit_code": exit_code,
        "sha256": digest(raw),
        "path": str(junit_path),
        "reason": "TEST_FAILURE" if status == "FAIL" else "TESTS_SKIPPED" if skipped else "EXECUTED_JUNIT_PASS",
        "scope": "SYNTHETIC_GUARDS_AND_VALIDATOR_REGRESSION_TESTS_NOT_MAINNET_VALIDATION",
    }
    return report


def write_report(report: dict, output: Path) -> None:
    # Serialize first; a failure cannot leave a partial success report behind.
    raw = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(raw, encoding="utf-8")
    temporary.replace(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validator-commit", default="LOCAL_UNCOMMITTED")
    parser.add_argument("--l2-junit", type=Path)
    parser.add_argument("--l2-exit-code", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        report = run_offline(args.validator_commit)
    except Exception as exc:
        # A software defect is an explicit FAIL, not a successful empty/fallback run.
        report = build_report(
            [check_record("VALIDATOR-INTERNAL", "FAIL", "VALIDATOR_INTERNAL_ERROR")], args.validator_commit
        )
        report["internal_error_type"] = type(exc).__name__
    if args.l2_junit is not None:
        report = attach_l2(report, args.l2_junit, args.l2_exit_code)
    if args.output:
        try:
            write_report(report, args.output)
        except (TypeError, ValueError):
            report = build_report(
                [check_record("REPORT-SERIALIZE", "FAIL", "REPORT_SERIALIZATION_ERROR")], args.validator_commit
            )
            try:
                write_report(report, args.output)
            except OSError:
                print("REPORT_WRITE_ERROR: cannot persist diagnostic report", file=sys.stderr)
                return 1
        except OSError:
            print("REPORT_WRITE_ERROR: cannot persist validation report", file=sys.stderr)
            return 1
    print(
        json.dumps(
            {
                "L1": report["L1_INTEGRITY"],
                "L2": report["L2_CONTRACTS"],
                "counts": report["counts"],
                "GATE_A": report["GATE_A"],
                "GATE_B": report["GATE_B"],
            }
        )
    )
    states = [report["L1_INTEGRITY"]]
    if args.l2_junit is not None:
        states.append(report["L2_CONTRACTS"])
    return 1 if "FAIL" in states else 2 if "BLOCKED" in states else 0


if __name__ == "__main__":
    raise SystemExit(main())
