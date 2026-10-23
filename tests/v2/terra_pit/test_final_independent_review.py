"""Independent REC-01..10 controls; numerical observations are synthetic."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import timedelta
from decimal import localcontext
from pathlib import Path

import pytest

from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.terra_pit import (
    AdmissionPolicy,
    EvidenceOrigin,
    MetadataPin,
    SourceFrequency,
    ValueStatus,
    latest_eligible_vintage,
    load_saved_terra_audit_metadata,
    trailing_mean,
)
from defistress_v2.terra_pit.contracts import QualityReport
from defistress_v2.terra_pit.loader import P04_01_PIT_MANIFEST, P04_01_REGISTRY, _bounded_bytes, _strict_json
from tests.v2.terra_pit.test_synthetic_controls import ROOT, ZERO, at, observation


def _saved_fixture(root: Path) -> tuple[MetadataPin, MetadataPin]:
    pins = []
    for path, name in [(P04_01_REGISTRY, "registry.json"), (P04_01_PIT_MANIFEST, "pit.json")]:
        raw = (ROOT / path).read_bytes()
        (root / name).write_bytes(raw)
        pins.append(MetadataPin(name, hashlib.sha256(raw).hexdigest()))
    return pins[0], pins[1]


def _repin(root: Path, pin: MetadataPin, doc: object) -> MetadataPin:
    raw = json.dumps(doc, separators=(",", ":")).encode()
    (root / pin.relative_path).write_bytes(raw)
    return MetadataPin(pin.relative_path, hashlib.sha256(raw).hexdigest())


def test_rec03_equal_time_uses_descendant_not_lexical_name() -> None:
    p = observation("logical", "1", at(9), at(10), vintage_id="z-parent")
    c = observation("logical", "9", at(9), at(10), vintage_id="a-child", revision_of="z-parent")
    assert latest_eligible_vintage((p, c), at(12), AdmissionPolicy(ZERO, None)) is c


@pytest.mark.parametrize("kind", ["second_root", "branch"])
def test_rec03_ambiguous_graph_rejected(kind: str) -> None:
    a = observation("logical", "1", at(9), at(10), vintage_id="v1")
    b = observation("logical", "2", at(9), at(11), vintage_id="v2", revision_of=None if kind == "second_root" else "v1")
    seq = (a, b)
    if kind == "branch":
        seq += (observation("logical", "3", at(9), at(12), vintage_id="v3", revision_of="v1"),)
    with pytest.raises(TypeContractError, match="REVISION"):
        latest_eligible_vintage(seq, at(13), AdmissionPolicy(ZERO, None))


@pytest.mark.parametrize("kind", ["frequency", "origin"])
def test_rec03_direct_selector_rejects_mixed_identity(kind: str) -> None:
    a = observation("logical", "1", at(9), at(10), vintage_id="v1")
    b = observation("logical", "2", at(9), at(11), vintage_id="v2", revision_of="v1")
    if kind == "frequency":
        b = dataclasses.replace(b, source_frequency=SourceFrequency.DAILY_CARRIED_FORWARD)
    else:
        b = dataclasses.replace(b, provenance=dataclasses.replace(b.provenance, origin=EvidenceOrigin.OBSERVED))
    with pytest.raises(TypeContractError, match="IDENTITY"):
        latest_eligible_vintage((a, b), at(13), AdmissionPolicy(ZERO, timedelta(days=1)))


def test_rec03_quarantine_does_not_resurrect_parent() -> None:
    a = observation("logical", "1", at(9), at(10), vintage_id="v1")
    b = observation("logical", None, at(9), at(11), vintage_id="v2", revision_of="v1", status=ValueStatus.QUARANTINED)
    assert latest_eligible_vintage((a, b), at(12), AdmissionPolicy(ZERO, None)) is None


def test_rec06_policy_bound_even_when_value_same() -> None:
    seq = (observation("one", "1", at(8), at(8)), observation("two", "3", at(9), at(9)))
    a = trailing_mean(seq, at(12), 2, AdmissionPolicy(ZERO, timedelta(days=1)))
    b = trailing_mean(seq, at(12), 2, AdmissionPolicy(timedelta(minutes=1), timedelta(days=2)))
    assert a.value == b.value == "2"
    assert a.content_hash != b.content_hash


def test_rec06_future_revision_perturbation_invariant() -> None:
    a = observation("logical", "1", at(8), at(8), vintage_id="v1")
    b = observation("logical", "9", at(8), at(13), vintage_id="v2", revision_of="v1")
    c = observation("other", "3", at(9), at(9))
    p = AdmissionPolicy(ZERO, None)
    before = trailing_mean((a, b, c), at(10), 2, p)
    changed = dataclasses.replace(b, measurement=dataclasses.replace(b.measurement, value="99"))
    after = trailing_mean((a, changed, c), at(10), 2, p)
    assert before.value == after.value == "2" and before.content_hash == after.content_hash


@pytest.mark.parametrize(
    "field,value", [("path", "invented-source"), ("sha256_git_bytes", "f" * 64), ("size_bytes", 123456)]
)
def test_rec07_exact_sources_not_just_shapes(tmp_path: Path, field: str, value: object) -> None:
    r, p = _saved_fixture(tmp_path)
    d = json.loads((tmp_path / r.relative_path).read_bytes())
    d["verified_inputs"][0][field] = value
    r = _repin(tmp_path, r, d)
    with pytest.raises(TypeContractError, match="REGISTERED_SOURCE"):
        load_saved_terra_audit_metadata(tmp_path, r, p)


def test_rec08_duplicate_field_rejected(tmp_path: Path) -> None:
    r, p = _saved_fixture(tmp_path)
    d = json.loads((tmp_path / p.relative_path).read_bytes())
    d["field_admission"][0]["field"] = d["field_admission"][1]["field"]
    p = _repin(tmp_path, p, d)
    with pytest.raises(TypeContractError, match="identit"):
        load_saved_terra_audit_metadata(tmp_path, r, p)


@pytest.mark.parametrize("value", [False, 0.0])
def test_rec09_predictive_count_exact_integer(value: object) -> None:
    with pytest.raises(TypeContractError):
        QualityReport(0, 0, 0, 0, 0, "BLOCKED_NOT_CLEARED_FOR_FORECAST", value, False)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field,value", [("verified_input_count", 35.0), ("field_count", 14.0), ("cleared_predictive_fields", False)]
)
def test_rec09_metadata_types(tmp_path: Path, field: str, value: object) -> None:
    r, p = _saved_fixture(tmp_path)
    m = load_saved_terra_audit_metadata(tmp_path, r, p)
    with pytest.raises(TypeContractError):
        dataclasses.replace(m, **{field: value})


def test_rec01_exact_bound_and_bound_plus_one(tmp_path: Path) -> None:
    p = tmp_path / "payload"
    p.write_bytes(b"abcd")
    assert _bounded_bytes(p, 4) == b"abcd"
    with pytest.raises(TypeContractError, match="bound"):
        _bounded_bytes(p, 3)


def test_rec01_deep_json_typed_failure() -> None:
    with pytest.raises(TypeContractError):
        _strict_json(b"[" * 10000 + b"0" + b"]" * 10000)


def test_rec05_supported_result_context_independent() -> None:
    seq = (observation("one", "-3", at(8), at(8)), observation("two", "1", at(9), at(9)))
    hashes = []
    for precision in [2, 50]:
        with localcontext() as ctx:
            ctx.prec = precision
            r = trailing_mean(seq, at(12), 2, AdmissionPolicy(ZERO, None))
            assert r.value == "-1"
            hashes.append(r.content_hash)
    assert hashes[0] == hashes[1]


def test_rec10_actual_metadata_stays_blocked(tmp_path: Path) -> None:
    r, p = _saved_fixture(tmp_path)
    m = load_saved_terra_audit_metadata(tmp_path, r, p)
    assert (m.verified_input_count, m.field_count, m.cleared_predictive_fields) == (35, 14, 0)
    assert len(m.gate_statuses) == 9 and m.point_in_time_status == "BLOCKED_NOT_CLEARED_FOR_FORECAST"


def test_rec01_descriptor_identity_blocks_swap_and_restore(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inside = tmp_path / "inside"
    outside = tmp_path / "outside"
    backup = tmp_path / "backup"
    inside.write_bytes(b"AAAA")
    outside.write_bytes(b"BBBB")
    real_open = Path.open

    def raced_open(path: Path, mode: str = "r", *args: object, **kwargs: object):
        if path == inside and mode == "rb":
            inside.rename(backup)
            inside.symlink_to(outside)
            stream = real_open(path, mode, *args, **kwargs)
            inside.unlink()
            backup.rename(inside)
            return stream
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", raced_open)
    with pytest.raises(TypeContractError, match="changed|identity"):
        _bounded_bytes(inside, 4)


def test_rec01_read_budget_detects_growth_before_open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "grow"
    target.write_bytes(b"A")
    real_open = Path.open

    def growing_open(path: Path, mode: str = "r", *args: object, **kwargs: object):
        if path == target and mode == "rb":
            with real_open(path, "ab") as stream:
                stream.write(b"BCDE")
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", growing_open)
    with pytest.raises(TypeContractError, match="changed|bound"):
        _bounded_bytes(target, 4)


@pytest.mark.parametrize("field,value", [("observation_ids", ["mutable"]), ("value", []), ("content_hash", [])])
def test_rec09_output_payload_types(field: str, value: object) -> None:
    result = trailing_mean((observation("one", "1", at(8), at(8)),), at(12), 1, AdmissionPolicy(ZERO, None))
    with pytest.raises(TypeContractError):
        dataclasses.replace(result, **{field: value})


@pytest.mark.parametrize("field", ["registry_raw_sha256", "pit_manifest_raw_sha256"])
def test_rec09_metadata_digest_types(tmp_path: Path, field: str) -> None:
    r, p = _saved_fixture(tmp_path)
    m = load_saved_terra_audit_metadata(tmp_path, r, p)
    with pytest.raises(TypeContractError):
        dataclasses.replace(m, **{field: []})
