"""Unit tests for strict canonical ABI state comparisons and saved CI evidence."""
import json
from pathlib import Path

from docs.research_v2.phase01b.alchemy_crosscheck.run import compare


def observed(fields):
    return {"status": "PASS", "data": {"fields": fields, "status": "AVAILABLE"}}


def test_slot0_tuple_and_json_list_equal():
    expected = observed({"pool:slot0()": [1234, -3, 0, 0, 0, 0, True]})
    actual = observed({"pool:slot0()": (1234, -3, 0, 0, 0, 0, True)})
    report = compare(expected, actual)
    assert report["agreeing_fields"] == 1
    assert report["mismatch_fields"] == []
    assert report["missing_fields"] == []


def test_actual_mismatch_must_be_reported():
    expected = observed({"pool:slot0()": [1234, -3]})
    actual = observed({"pool:slot0()": (1234, -4)})
    report = compare(expected, actual)
    assert report["agreeing_fields"] == 0
    assert report["mismatch_fields"] == ["pool:slot0()"]


def test_missing_fields_are_not_misclassified_as_agreement():
    report = compare(observed({"a": 1, "b": 2}), observed({"a": 1}))
    assert report["agreeing_fields"] == 1
    assert report["missing_fields"] == ["b"]
    assert report["mismatch_fields"] == []


def test_additional_fields_not_discarded_silently():
    report = compare(observed({"a": 1}), observed({"a": 1, "new": 8}))
    assert report["additional_fields"] == ["new"]


def test_repeatability_hash_detects_different_values():
    first = compare(observed({"a": 1}), observed({"a": 1}))
    second = compare(observed({"a": 1}), observed({"a": 2}))
    assert first["observed_fields_sha256"] != second["observed_fields_sha256"]


def test_persisted_evidence_is_limited_and_consistent():
    path = Path(__file__).resolve().parents[1] / "docs/research_v2/phase01b/alchemy_crosscheck/VERIFIED_CI_EVIDENCE.json"
    evidence = json.loads(path.read_text(encoding="utf-8"))
    assert evidence["summary"]["total_field_comparisons"] == 174
    assert evidence["summary"]["agreeing"] == 174
    assert evidence["summary"]["mismatch"] == 0
    assert evidence["summary"]["missing"] == 0
    assert len(evidence["blocks"]) == 3
    assert len({row["field_hash"] for row in evidence["blocks"]}) == 3
    assert evidence["verdicts"]["independent_backend"] == "UNVERIFIED"
    assert evidence["verdicts"]["independent_archive_gate"] == "BLOCKED"
    assert evidence["verdicts"]["phase02_authorized"] is False
