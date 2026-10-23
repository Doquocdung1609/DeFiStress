"""P04-S01..S12 independently specified synthetic temporal controls."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.terra_pit import (
    AdmissionPolicy,
    AdmissionStatus,
    AssetUnit,
    DatasetVintage,
    EvidenceOrigin,
    Measurement,
    MetadataPin,
    RiskOutputPlaceholder,
    RiskOutputStatus,
    SourceFrequency,
    SourceProvenance,
    TemporalObservation,
    TemporalSplit,
    TerraChainId,
    TimeInterval,
    TransformFitLineage,
    UtcInstant,
    ValueStatus,
    VerificationLevel,
    admissible_at,
    assert_fit_is_train_only,
    dataset_quality_report,
    derived_availability,
    latest_eligible_vintage,
    load_saved_terra_audit_metadata,
    trailing_mean,
    validate_observation_order,
)
from defistress_v2.terra_pit.loader import (
    EXPECTED_FIELD_NAMES,
    EXPECTED_GATE_STATUSES,
    P04_01_PIT_MANIFEST,
    P04_01_REGISTRY,
    _strict_json,
)
from scripts.research.terra_v2.audit_p04_01 import csv_profile

ROOT = Path(__file__).resolve().parents[3]
COMMIT = "9207ead7db3acf1332b34cebcd19981c2f7bd9cc"
CHAIN = TerraChainId("columbus-5")
UNIT = AssetUnit("UST", None, "UST/hour")
PRICE_USDT = AssetUnit("UST", "USDT", "USDT/UST")
PRICE_USD = AssetUnit("UST", "USD", "USD/UST")
ZERO = timedelta(0)


def at(hour: int, minute: int = 0, *, tz: timezone = UTC) -> UtcInstant:
    return UtcInstant(datetime(2022, 5, 1, hour, minute, tzinfo=tz))


def provenance(origin: EvidenceOrigin = EvidenceOrigin.SYNTHETIC) -> SourceProvenance:
    return SourceProvenance(
        "fixture-source",
        COMMIT,
        "1" * 64,
        VerificationLevel.FULL_BYTES_VERIFIED,
        origin,
    )


def observation(
    name: str,
    value: str | None,
    observed: UtcInstant,
    available: UtcInstant | None,
    *,
    status: ValueStatus = ValueStatus.AVAILABLE,
    interval: TimeInterval | None = None,
    vintage_id: str | None = None,
    revision_of: str | None = None,
    source_frequency: SourceFrequency = SourceFrequency.HOURLY_AGGREGATE,
    ingestion: UtcInstant | None = None,
    unit: AssetUnit = UNIT,
) -> TemporalObservation:
    if available is None:
        vintage = DatasetVintage(
            vintage_id or f"v-{name}",
            None,
            None,
            ingestion or at(23),
            revision_of,
            "historical publication and availability are unproven",
        )
    else:
        vintage = DatasetVintage(
            vintage_id or f"v-{name}",
            available,
            available,
            ingestion or at(23),
            revision_of,
        )
    measurement = (
        Measurement(status, value, unit, "complete-fixture")
        if status is ValueStatus.AVAILABLE
        else Measurement(status, None, unit, reason="fixture missingness")
    )
    return TemporalObservation(
        name,
        CHAIN,
        observed,
        interval,
        vintage,
        measurement,
        provenance(),
        source_frequency,
    )


def test_p04_s01_publication_after_forecast_cutoff() -> None:
    item = observation("s01", "1", at(10), at(10, 5))
    policy = AdmissionPolicy(ZERO, timedelta(hours=1))
    assert admissible_at(item, at(10, 2), policy).status is AdmissionStatus.BLOCKED
    assert admissible_at(item, at(10, 5), policy).status is AdmissionStatus.ELIGIBLE


def test_p04_s02_future_interval_closure() -> None:
    interval = TimeInterval(at(0), at(1))
    item = observation("s02", "3", at(0, 30), at(0, 30), interval=interval)
    policy = AdmissionPolicy(ZERO, timedelta(hours=2))
    assert admissible_at(item, at(0), policy, interval_delay=timedelta(minutes=5)).status is AdmissionStatus.BLOCKED
    decision = admissible_at(item, at(1, 5), policy, interval_delay=timedelta(minutes=5))
    assert decision.status is AdmissionStatus.ELIGIBLE
    assert decision.eligible_at == at(1, 5)


def test_p04_s03_revised_vintage_does_not_rewrite_past() -> None:
    first = observation("s03", "1", at(9), at(10), vintage_id="v1")
    revised = observation("s03", "9", at(9), at(12), vintage_id="v2", revision_of="v1")
    chosen = latest_eligible_vintage((first, revised), at(11), AdmissionPolicy(ZERO, timedelta(days=1)))
    assert chosen is first
    assert chosen.measurement.value == "1"


def test_p04_s04_acquisition_does_not_backdate_unknown_source_clock() -> None:
    item = observation("s04", "1", at(9), None, ingestion=at(23))
    decision = admissible_at(item, at(23), AdmissionPolicy(ZERO, timedelta(days=1)))
    assert decision.status is AdmissionStatus.BLOCKED
    assert decision.reason_codes == ("SOURCE_CLOCK_UNPROVEN",)


def test_p04_s05_observed_zero_is_not_missing() -> None:
    zero = observation("s05-zero", "0", at(9), at(9))
    missing = observation("s05-missing", None, at(10), at(10), status=ValueStatus.MISSING)
    policy = AdmissionPolicy(ZERO, timedelta(days=1))
    assert admissible_at(zero, at(11), policy).status is AdmissionStatus.ELIGIBLE
    assert zero.measurement.value == "0"
    assert admissible_at(missing, at(11), policy).status is AdmissionStatus.BLOCKED
    report = dataset_quality_report((zero.measurement, missing.measurement))
    assert (report.available, report.missing, report.historical_predictive_fields) == (1, 1, 0)


def test_p04_s06_derived_availability_uses_latest_dependency_plus_delay() -> None:
    assert derived_availability((at(10, 1), at(10, 3)), timedelta(minutes=2)) == at(10, 5)


def test_p04_s07_trailing_window_is_future_perturbation_invariant() -> None:
    values = (
        observation("s07-1", "1", at(9), at(9)),
        observation("s07-2", "2", at(10), at(10)),
        observation("s07-3", "4", at(11), at(11)),
    )
    policy = AdmissionPolicy(ZERO, timedelta(days=1))
    before = trailing_mean(values, at(10), 2, policy)
    changed = (
        *values[:2],
        dataclasses.replace(values[2], measurement=Measurement(ValueStatus.AVAILABLE, "999", UNIT, "complete-fixture")),
    )
    after = trailing_mean(changed, at(10), 2, policy)
    assert before.value == "1.5"
    assert before.content_hash == after.content_hash


def test_p04_s08_duplicate_out_of_order_and_ambiguous_clocks_rejected() -> None:
    one = observation("s08", "1", at(9), at(9))
    duplicate = dataclasses.replace(one, observation_id="s08-other")
    with pytest.raises(TypeContractError, match="DUPLICATE"):
        validate_observation_order((one, duplicate))
    earlier = observation("s08-early", "1", at(8), at(8))
    with pytest.raises(TypeContractError, match="OUT_OF_ORDER"):
        validate_observation_order((one, earlier))
    with pytest.raises(TypeContractError, match="timezone-aware"):
        UtcInstant(datetime(2022, 5, 1, 9))
    with pytest.raises(TypeContractError, match="datetime"):
        UtcInstant(True)  # type: ignore[arg-type]
    assert UtcInstant(datetime(2022, 5, 1, 17, tzinfo=timezone(timedelta(hours=7)))) == at(10)


def test_p04_s09_quote_pair_cannot_be_promoted_without_conversion() -> None:
    with pytest.raises(TypeContractError, match="conversion"):
        PRICE_USDT.assert_compatible(PRICE_USD)


def test_p04_s10_daily_carry_requires_staleness_policy_and_warmup() -> None:
    item = observation("s10", "1", at(9), at(9), source_frequency=SourceFrequency.DAILY_CARRIED_FORWARD)
    unresolved = AdmissionPolicy(ZERO, None)
    decision = admissible_at(item, at(10), unresolved)
    assert decision.status is AdmissionStatus.ABSTAIN
    assert decision.reason_codes == ("STALENESS_POLICY_UNRESOLVED",)
    with pytest.raises(TypeContractError, match="WARMUP"):
        trailing_mean((item,), at(10), 2, AdmissionPolicy(ZERO, timedelta(days=1)))


def test_p04_s11_split_purge_and_fit_lineage_leak() -> None:
    split = TemporalSplit(at(0), at(10), at(10), at(20), timedelta(hours=2))
    assert split.purge_required is True
    heldout_fit = TransformFitLineage("standardizer", at(11), "HOLDOUT")
    with pytest.raises(TypeContractError, match="FIT_LINEAGE_LEAK"):
        assert_fit_is_train_only(heldout_fit, split)


@pytest.mark.parametrize(
    "payload",
    [b'{"a":1,"a":2}', b'{"a":NaN}', b"not-json"],
)
def test_p04_s12_strict_json_rejects_duplicate_nonfinite_or_malformed(payload: bytes) -> None:
    with pytest.raises(TypeContractError):
        _strict_json(payload)


def test_p04_s12_csv_width_failure_remains_a_quarantine_condition() -> None:
    with pytest.raises(ValueError, match="WIDTH"):
        csv_profile(b"timestamp,x\n2022-05-01T00:00:00Z,1,2\n")


def _minimal_metadata(root: Path) -> tuple[MetadataPin, MetadataPin]:
    registry = json.loads((ROOT / P04_01_REGISTRY).read_bytes())
    pit = {
        "schema": "defistress-terra-pit-admission/1",
        "source_commit": COMMIT,
        "status": "BLOCKED_NOT_CLEARED_FOR_FORECAST",
        "cleared_predictive_fields": 0,
        "field_admission": [
            {
                "field": field,
                "approved_forecast_use": False,
                "point_in_time_status": "BLOCKED_AVAILABILITY",
            }
            for field in EXPECTED_FIELD_NAMES
        ],
        "gates": EXPECTED_GATE_STATUSES,
    }
    pins = []
    for name, document in (("registry.json", registry), ("pit.json", pit)):
        raw = json.dumps(document, separators=(",", ":")).encode()
        (root / name).write_bytes(raw)
        pins.append(MetadataPin(name, hashlib.sha256(raw).hexdigest()))
    return pins[0], pins[1]


@pytest.mark.parametrize("mutation", ["tamper", "oversize", "traversal", "unsupported", "duplicate_path"])
def test_p04_s12_bounded_metadata_failures_are_quarantined(tmp_path: Path, mutation: str) -> None:
    registry_pin, pit_pin = _minimal_metadata(tmp_path)
    if mutation == "tamper":
        (tmp_path / "registry.json").write_bytes(b"{}")
    elif mutation == "oversize":
        (tmp_path / "registry.json").write_bytes(b" " * 2_000_001)
    elif mutation == "traversal":
        registry_pin = MetadataPin("../registry.json", registry_pin.sha256_git_bytes)
    elif mutation == "unsupported":
        raw = (
            (tmp_path / "pit.json")
            .read_bytes()
            .replace(b"defistress-terra-pit-admission/1", b"unknown-schema------------------")
        )
        (tmp_path / "pit.json").write_bytes(raw)
        pit_pin = MetadataPin("pit.json", hashlib.sha256(raw).hexdigest())
    else:
        document = json.loads((tmp_path / "registry.json").read_bytes())
        document["verified_inputs"][1]["path"] = document["verified_inputs"][0]["path"]
        raw = json.dumps(document, separators=(",", ":")).encode()
        (tmp_path / "registry.json").write_bytes(raw)
        registry_pin = MetadataPin("registry.json", hashlib.sha256(raw).hexdigest())
    with pytest.raises(TypeContractError):
        load_saved_terra_audit_metadata(tmp_path, registry_pin, pit_pin)


def test_p04_s12_symlink_escape_rejected_when_supported(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    registry_pin, pit_pin = _minimal_metadata(target)
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink not supported: {exc}")
    with pytest.raises(TypeContractError, match="symlink"):
        load_saved_terra_audit_metadata(
            tmp_path,
            MetadataPin(f"link/{registry_pin.relative_path}", registry_pin.sha256_git_bytes),
            MetadataPin(f"link/{pit_pin.relative_path}", pit_pin.sha256_git_bytes),
        )


def test_registered_metadata_is_audit_only_and_remains_blocked() -> None:
    registry = ROOT / P04_01_REGISTRY
    pit = ROOT / P04_01_PIT_MANIFEST
    result = load_saved_terra_audit_metadata(
        ROOT,
        MetadataPin(P04_01_REGISTRY, hashlib.sha256(registry.read_bytes()).hexdigest()),
        MetadataPin(P04_01_PIT_MANIFEST, hashlib.sha256(pit.read_bytes()).hexdigest()),
    )
    assert result.verified_input_count == 35
    assert result.field_count == 14
    assert result.cleared_predictive_fields == 0
    assert len(result.gate_statuses) == 9
    assert result.point_in_time_status == "BLOCKED_NOT_CLEARED_FOR_FORECAST"


@pytest.mark.parametrize("value", ["1.0", "1.00", "-0", "0.0", "00", "1e2", "1" * 79])
def test_measurement_rejects_noncanonical_or_unbounded_decimal(value: str) -> None:
    with pytest.raises(TypeContractError, match="canonical|bound"):
        Measurement(ValueStatus.AVAILABLE, value, UNIT, "complete")


def test_source_frequency_requires_typed_closed_vocabulary() -> None:
    item = observation("typed-frequency", "1", at(9), at(9))
    with pytest.raises(TypeContractError, match="SourceFrequency"):
        dataclasses.replace(item, source_frequency="daily-carried-hourly")  # type: ignore[arg-type]


def test_latest_vintage_rejects_cross_series_or_invalid_revision_chain() -> None:
    first = observation("series", "1", at(9), at(10), vintage_id="v1")
    cross_series = observation("other", "2", at(9), at(11), vintage_id="v2", revision_of="v1")
    with pytest.raises(TypeContractError, match="VINTAGE_IDENTITY_MISMATCH"):
        latest_eligible_vintage((first, cross_series), at(12), AdmissionPolicy(ZERO, timedelta(days=1)))

    unknown_parent = observation("series", "2", at(9), at(11), vintage_id="v2", revision_of="missing")
    with pytest.raises(TypeContractError, match="REVISION_CHAIN_INVALID"):
        latest_eligible_vintage((first, unknown_parent), at(12), AdmissionPolicy(ZERO, timedelta(days=1)))

    later_first = observation("series", "1", at(9), at(12), vintage_id="v1")
    earlier_revision = observation("series", "2", at(9), at(11), vintage_id="v2", revision_of="v1")
    with pytest.raises(TypeContractError, match="VINTAGE_AVAILABILITY_OUT_OF_ORDER"):
        latest_eligible_vintage((later_first, earlier_revision), at(13), AdmissionPolicy(ZERO, timedelta(days=1)))


def test_trailing_hash_commits_to_full_selected_input_lineage() -> None:
    original = (
        observation("lineage-1", "1", at(8), at(8)),
        observation("lineage-2", "3", at(9), at(9)),
    )
    changed = (
        dataclasses.replace(original[0], measurement=Measurement(ValueStatus.AVAILABLE, "0", UNIT, "complete")),
        dataclasses.replace(original[1], measurement=Measurement(ValueStatus.AVAILABLE, "4", UNIT, "complete")),
    )
    policy = AdmissionPolicy(ZERO, timedelta(days=1))
    before = trailing_mean(original, at(10), 2, policy)
    after = trailing_mean(changed, at(10), 2, policy)
    assert before.value == after.value == "2"
    assert before.content_hash != after.content_hash


def test_trailing_mean_rejects_nonterminating_decimal_result() -> None:
    values = (
        observation("nonterm-1", "1", at(7), at(7)),
        observation("nonterm-2", "1", at(8), at(8)),
        observation("nonterm-3", "2", at(9), at(9)),
    )
    with pytest.raises(TypeContractError, match="NON_TERMINATING_MEAN_UNSUPPORTED"):
        trailing_mean(values, at(10), 3, AdmissionPolicy(ZERO, timedelta(days=1)))


def test_trailing_window_counts_distinct_observation_times_and_selects_latest_vintage() -> None:
    first = observation("distinct-1", "1", at(8), at(8), vintage_id="v1")
    revised = observation("distinct-1", "3", at(8), at(9), vintage_id="v2", revision_of="v1")
    second = observation("distinct-2", "5", at(9), at(9), vintage_id="v3")
    values = (first, revised, second)
    policy = AdmissionPolicy(ZERO, timedelta(days=1))

    result = trailing_mean(values, at(10), 2, policy)

    assert result.value == "4"
    assert result.observation_ids == ("distinct-1", "distinct-2")
    with pytest.raises(TypeContractError, match="WARMUP_NOT_SATISFIED"):
        trailing_mean(values, at(10), 3, policy)


def test_trailing_window_rejects_mixed_source_identity() -> None:
    first = observation("source-1", "1", at(8), at(8))
    second = observation("source-2", "3", at(9), at(9))
    second = dataclasses.replace(
        second,
        provenance=SourceProvenance(
            "other-source",
            COMMIT,
            "2" * 64,
            VerificationLevel.FULL_BYTES_VERIFIED,
            EvidenceOrigin.SYNTHETIC,
        ),
    )

    with pytest.raises(TypeContractError, match="TRAILING_SERIES_IDENTITY_MISMATCH"):
        trailing_mean((first, second), at(10), 2, AdmissionPolicy(ZERO, timedelta(days=1)))


@pytest.mark.parametrize("mutation", ["field_identity", "gate_identity", "gate_status", "input_integrity"])
def test_loader_rejects_metadata_identity_or_status_drift(tmp_path: Path, mutation: str) -> None:
    registry_pin, pit_pin = _minimal_metadata(tmp_path)
    registry = json.loads((tmp_path / "registry.json").read_bytes())
    pit = json.loads((tmp_path / "pit.json").read_bytes())
    if mutation == "field_identity":
        pit["field_admission"][0]["field"] = "substituted"
    elif mutation == "gate_identity":
        pit["gates"]["SUBSTITUTED"] = pit["gates"].pop("DATA_AUDITED")
    elif mutation == "gate_status":
        pit["gates"]["DATA_AUDITED"] = "PASS"
    else:
        registry["verified_inputs"][0]["sha256_git_bytes"] = "A" * 64
    for name, document in (("registry.json", registry), ("pit.json", pit)):
        raw = json.dumps(document, separators=(",", ":")).encode()
        (tmp_path / name).write_bytes(raw)
        pin = MetadataPin(name, hashlib.sha256(raw).hexdigest())
        if name == "registry.json":
            registry_pin = pin
        else:
            pit_pin = pin
    with pytest.raises(TypeContractError):
        load_saved_terra_audit_metadata(tmp_path, registry_pin, pit_pin)


@pytest.mark.parametrize("path,digest", [("", "0" * 64), ("registry.json", "A" * 64), ("registry.json", "0" * 63)])
def test_metadata_pin_rejects_malformed_identity(path: str, digest: str) -> None:
    with pytest.raises(TypeContractError):
        MetadataPin(path, digest)


def test_contracts_are_frozen_and_terra_chain_is_not_evm_identity() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        CHAIN.network = "1"  # type: ignore[misc]
    with pytest.raises(TypeContractError):
        TerraChainId(1)  # type: ignore[arg-type]
    with pytest.raises(Exception, match="columbus-5"):
        TerraChainId("1")


def test_all_missingness_states_remain_distinct_in_quality_report() -> None:
    values = (
        Measurement(ValueStatus.AVAILABLE, "0", UNIT, "complete"),
        Measurement(ValueStatus.MISSING, None, UNIT, reason="not covered"),
        Measurement(ValueStatus.UNSUPPORTED, None, UNIT, reason="semantics unsupported"),
        Measurement(ValueStatus.QUARANTINED, None, UNIT, reason="integrity mismatch"),
    )
    report = dataset_quality_report(values)
    assert (report.available, report.missing, report.unsupported, report.quarantined) == (1, 1, 1, 1)
    assert report.historical_pit_status == "BLOCKED_NOT_CLEARED_FOR_FORECAST"


def test_risk_output_is_explicitly_not_implemented() -> None:
    placeholder = RiskOutputPlaceholder()
    assert placeholder.status is RiskOutputStatus.NOT_IMPLEMENTED
