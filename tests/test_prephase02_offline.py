"""Pure synthetic adverse controls; fixtures are NEVER empirical evidence."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from docs.research_v2.prephase02_offline import validate_offline as validator
from docs.research_v2.prephase02_offline.validate_offline import (
    borrower_complete,
    canonical_equal,
    complete_fields,
    digest,
    liquidity_consistent,
    oracle_valid,
    tick_band,
    units,
    validate_identity,
    validate_pool,
)

USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
POOL = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"
HASH = "0x4dffe3bdf7bbaf24fd1e3b6c3f4795687dccfd3189cbfb61f4dbaf926722220a"


@pytest.mark.parametrize(
    ("test_id", "observed", "expected"),
    [
        ("bad_chain", lambda: validate_identity(5, 26045352, HASH), False),
        ("bad_hash", lambda: validate_identity(1, 26045352, "0x00"), False),
        ("future_or_wrong_block", lambda: validate_identity(1, 26045353, HASH), False),
        ("wrong_pool", lambda: validate_pool(WETH, 3000, "P3000", USDC, WETH, USDC, WETH), False),
        ("swapped_tokens", lambda: validate_pool(POOL, 3000, "P3000", WETH, USDC, USDC, WETH), False),
        ("good_pool", lambda: validate_pool(POOL, 3000, "P3000", USDC, WETH, USDC, WETH), True),
        ("usdc_decimal_mixup", lambda: units(1000000, 18, 6), False),
        ("weth_decimal_mixup", lambda: units(10**18, 6, 18), False),
        ("negative_raw", lambda: units(-1, 6, 6), False),
        ("fractional_raw", lambda: units(1.5, 6, 6), False),
        ("tuple_list_equal", lambda: canonical_equal((7, -1, True), [7, -1, True]), True),
        ("tuple_content_differs", lambda: canonical_equal((7, -1), [7, -2]), False),
        ("missing_field", lambda: complete_fields({"a": 1, "b": 2}, {"a": 1}), False),
        ("extra_field", lambda: complete_fields({"a": 1}, {"a": 1, "b": 2}), False),
        ("null_not_zero", lambda: canonical_equal({"a": None}, {"a": 0}), False),
        ("field_swapped", lambda: canonical_equal({"a": 1, "b": 2}, {"a": 2, "b": 1}), False),
        (
            "duplicate_tick",
            lambda: tick_band(
                [
                    {"index": 60, "gross": 5, "net": 2, "bitmap_initialized": True},
                    {"index": 60, "gross": 5, "net": 2, "bitmap_initialized": True},
                ],
                0,
                120,
                60,
            ),
            False,
        ),
        (
            "tick_outside_band",
            lambda: tick_band([{"index": 180, "gross": 5, "net": 2, "bitmap_initialized": True}], 0, 120, 60),
            False,
        ),
        (
            "bitmap_uninitialized",
            lambda: tick_band([{"index": 60, "gross": 5, "net": 2, "bitmap_initialized": False}], 0, 120, 60),
            False,
        ),
        (
            "gross_less_than_net",
            lambda: tick_band([{"index": 60, "gross": 1, "net": 2, "bitmap_initialized": True}], 0, 120, 60),
            False,
        ),
        ("active_above_total", lambda: liquidity_consistent(101, 100), False),
        ("negative_active", lambda: liquidity_consistent(-1, 100), False),
        ("dex_spot_for_oracle", lambda: oracle_valid("aave", "aave", 4, 90, 100, True), False),
        ("oracle_wrong_source", lambda: oracle_valid("dex", "aave", 4, 90, 100), False),
        ("oracle_future_timestamp", lambda: oracle_valid("aave", "aave", 4, 101, 100), False),
        ("oracle_zero_round", lambda: oracle_valid("aave", "aave", 0, 90, 100), False),
        ("borrower_wrong_reserve", lambda: borrower_complete([1, 2], [1, 3], {1: 100, 2: 0}, 10**18), False),
        ("borrower_missing_liability", lambda: borrower_complete([1, 2], [1, 2], {1: 100}, 10**18), False),
        ("borrower_duplicate_reserve", lambda: borrower_complete([1, 1], [1], {1: 100}, 10**18), False),
        ("borrower_invalid_hf", lambda: borrower_complete([1], [1], {1: 100}, None), False),
        ("raw_sha_tampered", lambda: digest(b"artifact") == digest(b"artifactX"), False),
        (
            "json_digest_change",
            lambda: digest(json.dumps({"a": 1}).encode()) == digest(json.dumps({"a": 2}).encode()),
            False,
        ),
    ],
)
def test_synthetic_control(test_id, observed, expected):
    assert observed() is expected, test_id


def test_registered_control_positive():
    assert validate_identity(1, 26045352, HASH)
    assert units(10**6, 6, 6)
    assert tick_band([{"index": 60, "gross": 5, "net": -2, "bitmap_initialized": True}], 0, 120, 60)
    assert oracle_valid("aave", "aave", 9, 90, 100)
    assert borrower_complete([1], [1], {1: 0}, 10**18)


def test_null_and_zero_remain_distinct_under_deep_copy():
    original = {"a": [0, {"b": None}]}
    modified = copy.deepcopy(original)
    modified["a"][1]["b"] = 0
    assert not canonical_equal(original, modified)


def test_sha256_known_vector():
    assert hashlib.sha256(b"abc").hexdigest() == ("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")


def test_registered_p500_identity_not_the_old_truncated_address():
    address = "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"
    assert validate_pool(address, 500, "P500", USDC, WETH, USDC, WETH)
    assert not validate_pool("0x88e6a0c2dd26feeb64f039a2c41296fcb3f5640", 500, "P500", USDC, WETH, USDC, WETH)
    assert all(len(address) == 42 for address, _ in validator.POOLS.values())


def artifact_row(raw=b"SYNTHETIC"):
    return {"path": "fixture.bin", "size_bytes": len(raw), "sha256": digest(raw)}


def test_file_check_has_id_and_aggregates_without_keyerror(tmp_path):
    (tmp_path / "fixture.bin").write_bytes(b"SYNTHETIC")
    check = validator.file_record(tmp_path, artifact_row(), check_id="FILE:fixture:0")
    assert check["id"] == "FILE:fixture:0"
    assert check["scope"] == "L1_INTEGRITY"
    report = validator.build_report([check])
    assert report["L1_INTEGRITY"] == "PASS"
    assert report["counts"] == {"PASS": 1, "FAIL": 0, "BLOCKED": 0}


@pytest.mark.parametrize(
    "record",
    [
        {"path": "fixture.bin", "scope": "L1_INTEGRITY", "status": "PASS", "reason": "CHECKED"},
        {"id": "", "scope": "L1_INTEGRITY", "status": "PASS", "reason": "CHECKED"},
        {"id": "BAD", "scope": "L1_INTEGRITY", "status": "UNKNOWN", "reason": "CHECKED"},
        {"id": "BAD", "scope": "UNKNOWN", "status": "PASS", "reason": "CHECKED"},
        {"id": "BAD", "scope": "L1_INTEGRITY", "status": "PASS"},
        {"id": 1, "scope": "L1_INTEGRITY", "status": "PASS", "reason": "CHECKED"},
        None,
        [],
        "not a check",
    ],
)
def test_malformed_check_is_explicit_fail_not_a_fallback(record):
    original = copy.deepcopy(record)
    with pytest.raises(validator.CheckSchemaError):
        validator.validate_check(record)
    report = validator.build_report([record])
    assert report["L1_INTEGRITY"] == "FAIL"
    assert report["report_errors"][0]["check_index"] == 0
    assert report["checks"][0]["reason"] == "INVALID_CHECK_RECORD"
    assert report["counts"]["PASS"] == 0
    assert record == original


def test_duplicate_id_is_rejected():
    check = validator.check_record("DUPLICATE", "PASS", "CHECKED")
    report = validator.build_report([check, dict(check)])
    assert report["L1_INTEGRITY"] == "FAIL"
    assert report["report_errors"] == [{"check_index": 1, "error": "duplicate check.id"}]


@pytest.mark.parametrize("checks", [[], {}, None])
def test_empty_or_invalid_container_cannot_pass(checks):
    assert validator.build_report(checks)["L1_INTEGRITY"] == "FAIL"


def test_only_registered_limitations_can_be_excluded_from_integrity():
    passed = validator.check_record("FILE:0", "PASS", "CHECKED")
    limits = [validator.check_record(k, "BLOCKED", v, scope="LIMITATION") for k, v in validator.LIMITATIONS.items()]
    report = validator.build_report([passed, *limits])
    assert report["L1_INTEGRITY"] == "PASS"
    assert report["counts"]["BLOCKED"] == 2
    assert report["L1_counts"]["BLOCKED"] == 0
    fake = {"id": "FILE:bad", "scope": "LIMITATION", "status": "BLOCKED", "reason": "FILE_MISSING"}
    assert validator.build_report([passed, fake])["L1_INTEGRITY"] == "FAIL"
    missing = validator.check_record("FILE:missing", "BLOCKED", "FILE_MISSING")
    assert validator.build_report([passed, *limits, missing])["L1_INTEGRITY"] == "BLOCKED"


@pytest.mark.parametrize(
    "row",
    [
        None,
        {},
        {"path": "fixture.bin"},
        {"path": "fixture.bin", "size_bytes": True, "sha256": "0" * 64},
        {"path": "fixture.bin", "size_bytes": 0, "sha256": "bad"},
        {**artifact_row(), "uncompressed_sha256": "0" * 64},
    ],
)
def test_malformed_manifest_rows_emit_typed_failure(tmp_path, row):
    record = validator.file_record(tmp_path, row, check_id="FILE:bad")
    validator.validate_check(record)
    assert record["status"] == "FAIL"


def test_missing_and_tampered_file_are_not_pass(tmp_path):
    row = artifact_row()
    record = validator.file_record(tmp_path, row, check_id="FILE:missing")
    assert record["status"] == "BLOCKED" and record["reason"] == "FILE_MISSING"
    (tmp_path / "fixture.bin").write_bytes(b"tampered")
    record = validator.file_record(tmp_path, row, check_id="FILE:bad")
    assert record["status"] == "FAIL" and record["reason"] == "DIGEST_MISMATCH"


def test_invalid_gzip_and_path_escape_are_rejected(tmp_path):
    raw = b"not a gzip stream"
    (tmp_path / "fixture.bin").write_bytes(raw)
    row = {**artifact_row(raw), "uncompressed_size": 1, "uncompressed_sha256": "0" * 64}
    assert validator.file_record(tmp_path, row, check_id="FILE:gzip")["reason"] == "GZIP_INVALID"
    row = {**artifact_row(), "path": "../outside"}
    assert validator.file_record(tmp_path, row, check_id="FILE:escape")["reason"] == "PATH_ESCAPE"


@pytest.mark.parametrize(
    ("payload", "status", "reason"),
    [
        (None, "BLOCKED", "JSON_INPUT_MISSING"),
        ("{", "FAIL", "JSON_INPUT_INVALID"),
        ("[]", "FAIL", "JSON_ROOT_NOT_OBJECT"),
    ],
)
def test_missing_or_malformed_source_produces_report_check(tmp_path, payload, status, reason):
    path = tmp_path / "source.json"
    if payload is not None:
        path.write_text(payload)
    checks = []
    assert validator.load_object(path, "SOURCE", checks) is None
    assert checks[0]["status"] == status and checks[0]["reason"] == reason
    assert validator.build_report(checks)["L1_INTEGRITY"] == status


def test_invalid_source_shape_fails_named_check_without_exception():
    checks = []
    validator.evaluate("REG-DECIMALS", lambda: {}["tokens"]["USDC"], checks)
    assert checks[0]["status"] == "FAIL" and checks[0]["reason"] == "INPUT_SCHEMA_INVALID"


def test_main_writes_failure_report_for_internal_producer_error(tmp_path, monkeypatch):
    def broken(_commit):
        raise KeyError("id")

    monkeypatch.setattr(validator, "run_offline", broken)
    output = tmp_path / "report.json"
    assert validator.main(["--output", str(output)]) == 1
    report = json.loads(output.read_text())
    assert report["L1_INTEGRITY"] == "FAIL"
    assert report["checks"][0]["reason"] == "VALIDATOR_INTERNAL_ERROR"
    assert report["internal_error_type"] == "KeyError"


def test_main_writes_fail_for_invalid_check_producer(tmp_path, monkeypatch):
    monkeypatch.setattr(validator, "run_offline", lambda _commit: validator.build_report([{"path": "old"}]))
    output = tmp_path / "report.json"
    assert validator.main(["--output", str(output)]) == 1
    assert json.loads(output.read_text())["report_errors"]


def test_serialization_error_produces_explicit_failure_report(tmp_path, monkeypatch):
    def bad_report(_commit):
        report = validator.build_report([validator.check_record("OK", "PASS", "CHECKED")])
        report["bad"] = object()
        return report

    monkeypatch.setattr(validator, "run_offline", bad_report)
    output = tmp_path / "report.json"
    assert validator.main(["--output", str(output)]) == 1
    assert json.loads(output.read_text())["checks"][0]["reason"] == "REPORT_SERIALIZATION_ERROR"


def test_output_write_error_is_nonzero_not_silent_success(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        validator,
        "run_offline",
        lambda _commit: validator.build_report([validator.check_record("OK", "PASS", "CHECKED")]),
    )

    def denied(_self, *_args, **_kwargs):
        raise PermissionError("synthetic write denial")

    monkeypatch.setattr(Path, "write_text", denied)
    assert validator.main(["--output", str(tmp_path / "report.json")]) == 1
    assert "REPORT_WRITE_ERROR" in capsys.readouterr().err


def junit_fixture(tmp_path, *, fail=0, skip=0):
    child = "<failure/>" if fail else "<skipped/>" if skip else ""
    path = tmp_path / "junit.xml"
    path.write_text(
        f'<testsuites><testsuite tests="1" failures="{fail}" errors="0" skipped="{skip}">'
        f'<testcase name="synthetic">{child}</testcase></testsuite></testsuites>'
    )
    return path


@pytest.mark.parametrize(
    ("fail", "skip", "exit_code", "status"),
    [
        (0, 0, 0, "PASS"),
        (1, 0, 1, "FAIL"),
        (0, 1, 0, "BLOCKED"),
        (0, 0, 1, "FAIL"),
    ],
)
def test_l2_status_comes_from_actual_junit_and_process(tmp_path, fail, skip, exit_code, status):
    report = validator.build_report([validator.check_record("L1", "FAIL", "BAD_HASH")])
    path = junit_fixture(tmp_path, fail=fail, skip=skip)
    updated = validator.attach_l2(report, path, exit_code)
    assert updated["L2_CONTRACTS"] == status
    assert updated["L1_INTEGRITY"] == "FAIL"  # L2 cannot mask failed L1.
    assert updated["L2_TEST_RESULTS"]["sha256"] == digest(path.read_bytes())
    assert updated["GATE_A"] == "BLOCKED_BACKEND_INDEPENDENCE"
    assert updated["GATE_B"] == "PASS_REGISTERED_CORE_SCOPE"
    assert updated["PHASE02_AUTHORIZATION"] == "NOT_AUTHORIZED"


@pytest.mark.parametrize(
    "payload",
    [
        "<bad",
        "<testsuite/>",
        '<testsuite tests="1" failures="0" errors="0" skipped="0"/>',
        '<testsuite tests="0" failures="0" errors="0" skipped="0"><testcase/></testsuite>',
    ],
)
def test_invalid_or_empty_junit_cannot_pass(tmp_path, payload):
    path = tmp_path / "invalid.xml"
    path.write_text(payload)
    report = validator.build_report([validator.check_record("L1", "PASS", "CHECKED")])
    assert validator.attach_l2(report, path, 0)["L2_CONTRACTS"] == "FAIL"


def test_missing_junit_blocks_l2_and_cli_exit(tmp_path, monkeypatch):
    monkeypatch.setattr(
        validator,
        "run_offline",
        lambda _commit: validator.build_report([validator.check_record("L1", "PASS", "CHECKED")]),
    )
    output = tmp_path / "report.json"
    assert validator.main(["--output", str(output), "--l2-junit", str(tmp_path / "absent.xml")]) == 2
    assert json.loads(output.read_text())["L2_TEST_RESULTS"]["reason"] == "JUNIT_MISSING"


def test_missing_l1_evidence_has_blocked_exit_even_when_limitations_are_expected(tmp_path, monkeypatch):
    monkeypatch.setattr(
        validator,
        "run_offline",
        lambda _commit: validator.build_report([validator.check_record("FILE:missing", "BLOCKED", "FILE_MISSING")]),
    )
    assert validator.main(["--output", str(tmp_path / "report.json")]) == 2


def test_run_offline_missing_sources_preserves_blocked_checks(tmp_path, monkeypatch):
    monkeypatch.setattr(validator, "PHASE", tmp_path)
    report = validator.run_offline()
    assert report["L1_INTEGRITY"] == "BLOCKED"
    assert report["L1_counts"]["BLOCKED"] == 5
    assert report["report_errors"] == []
    assert all(c["reason"] == "JSON_INPUT_MISSING" for c in report["checks"] if c["scope"] == "L1_INTEGRITY")
    for check in report["checks"]:
        validator.validate_check(check)


def test_run_offline_malformed_registration_is_named_input_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(validator, "PHASE", tmp_path)
    (tmp_path / "SAMPLE_REGISTRATION.json").write_text('{"tokens": null}')
    report = validator.run_offline()
    assert report["L1_INTEGRITY"] == "FAIL"
    assert any(c["id"] == "REG-DECIMALS" and c["reason"] == "INPUT_SCHEMA_INVALID" for c in report["checks"])
    assert not any(c["id"] == "VALIDATOR-INTERNAL" for c in report["checks"])


def test_real_malformed_manifest_producer_still_persists_report(tmp_path, monkeypatch):
    phase = tmp_path / "inputs"
    path = phase / "evidence/full/collection_manifest.json"
    path.parent.mkdir(parents=True)
    path.write_text('{"files": [null, {}]}')
    monkeypatch.setattr(validator, "PHASE", phase)
    output = tmp_path / "VALIDATION_GATES.json"
    assert validator.main(["--output", str(output)]) == 1
    report = json.loads(output.read_text())
    failed = [c for c in report["checks"] if c["id"].startswith("FILE:")]
    assert len(failed) == 2 and all(c["status"] == "FAIL" for c in failed)
    assert all(c["scope"] == "L1_INTEGRITY" for c in failed)
    assert not any(c["id"] == "VALIDATOR-INTERNAL" for c in report["checks"])
