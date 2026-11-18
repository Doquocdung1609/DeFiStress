"""Independent Issue56 synthetic vectors and adversarial time/unit/lineage controls."""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta
from decimal import localcontext
from fractions import Fraction
from pathlib import Path

import pytest

from defistress_v2.contracts import canonical_json_bytes
from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.terra_pit import (
    AdmissionPolicy,
    AssetUnit,
    DatasetVintage,
    EvidenceOrigin,
    Measurement,
    SourceFrequency,
    SourceProvenance,
    TemporalObservation,
    TerraChainId,
    TimeInterval,
    UtcInstant,
    ValueStatus,
    VerificationLevel,
    content_sha256,
    trailing_mean,
)
from defistress_v2.terra_warning import (
    DecisionContext,
    ExactRatio,
    ModelId,
    RiskLevel,
    WarningInputs,
    evaluate,
    toy_config,
)
from defistress_v2.terra_warning.contracts import MAX_OBSERVATIONS, digest

BASE = "c51d4d06d8b560a149e32ade922f8ed62da1a589"


def at(hour: int, minute: int = 0) -> UtcInstant:
    # Artificial 2030 clock, deliberately unrelated to historical Terra rows.
    return UtcInstant(datetime(2030, 1, 1, hour, minute, tzinfo=UTC))


def observation(asset: str, hour: int, value: str) -> TemporalObservation:
    source = f"synthetic-{asset.lower()}"
    name = f"{asset}-{hour}"
    return TemporalObservation(
        name, TerraChainId("columbus-5"), at(hour), TimeInterval(at(hour), at(hour + 1)),
        DatasetVintage(f"v-{name}", at(hour + 1), at(hour + 1), at(hour + 1)),
        Measurement(ValueStatus.AVAILABLE, value, AssetUnit(asset, "USD", f"USD/{asset}"), f"complete-{name}"),
        SourceProvenance(
            source, BASE, hashlib.sha256(f"SYNTHETIC:{asset}:{hour}:{value}".encode()).hexdigest(),
            VerificationLevel.FULL_BYTES_VERIFIED, EvidenceOrigin.SYNTHETIC,
        ), SourceFrequency.HOURLY_AGGREGATE,
    )


def inputs(ust: str = "1", previous: str = "100", current: str = "100") -> WarningInputs:
    return WarningInputs((observation("UST", 2, ust),), (
        observation("LUNA", 1, previous), observation("LUNA", 2, current),
    ))


def context(cutoff: UtcInstant | None = None) -> DecisionContext:
    cutoff = cutoff or at(3)
    return DecisionContext(cutoff, cutoff, cutoff)


@pytest.mark.parametrize(("ust", "luna", "d", "loss", "composite", "b1", "b2", "b3"), [
    ("1", "100", (0, 1), (0, 1), (0, 1), "NORMAL", "NORMAL", "NORMAL"),
    ("0.99", "100", (1, 100), (0, 1), (1, 4), "HIGH", "NORMAL", "NORMAL"),
    ("1", "90", (0, 1), (1, 10), (1, 4), "NORMAL", "HIGH", "NORMAL"),
    ("0.99", "90", (1, 100), (1, 10), (1, 2), "HIGH", "HIGH", "WATCH"),
    ("0.98", "80", (1, 50), (1, 5), (1, 1), "HIGH", "HIGH", "HIGH"),
])
def test_m01_to_m05_independent_reference_vectors(ust, luna, d, loss, composite, b1, b2, b3):
    fixture = inputs(ust, current=luna)
    # Literal independent expected fractions; never calculate expected using engine helpers.
    for model, expected, level in ((ModelId.B1, d, b1), (ModelId.B2, loss, b2), (ModelId.B3, composite, b3)):
        result = evaluate(model, fixture, context(), toy_config())
        assert result.score == ExactRatio(*expected)
        assert result.level.value == level
    b0 = evaluate(ModelId.B0, fixture, context(), toy_config())
    assert b0.score == ExactRatio(0) and b0.level is RiskLevel.NORMAL


@pytest.mark.parametrize(("model", "peg", "luna", "level"), [
    (ModelId.B1, "0.9950000001", "100", "NORMAL"),
    (ModelId.B1, "0.995", "100", "WATCH"),
    (ModelId.B1, "0.9949999999", "100", "WATCH"),
    (ModelId.B1, "0.9900000001", "100", "WATCH"),
    (ModelId.B1, "0.99", "100", "HIGH"),
    (ModelId.B1, "0.9899999999", "100", "HIGH"),
    (ModelId.B2, "1", "95.00000001", "NORMAL"),
    (ModelId.B2, "1", "95", "WATCH"),
    (ModelId.B2, "1", "94.99999999", "WATCH"),
    (ModelId.B2, "1", "90.00000001", "WATCH"),
    (ModelId.B2, "1", "90", "HIGH"),
    (ModelId.B2, "1", "89.99999999", "HIGH"),
    (ModelId.B3, "0.9900000001", "90", "NORMAL"),
    (ModelId.B3, "0.99", "90", "WATCH"),
    (ModelId.B3, "0.9899999999", "90", "WATCH"),
    (ModelId.B3, "0.9900000001", "80", "WATCH"),
    (ModelId.B3, "0.99", "80", "HIGH"),
    (ModelId.B3, "0.9899999999", "80", "HIGH"),
])
def test_m12_inclusive_equality_and_one_exact_step(model, peg, luna, level):
    hashes = []
    for precision in (2, 8, 28, 80):
        with localcontext() as decimal_context:
            decimal_context.prec = precision
            result = evaluate(model, inputs(peg, current=luna), context(), toy_config())
            assert result.level.value == level
            hashes.append(result.output_hash)
    assert len(set(hashes)) == 1


@pytest.mark.parametrize("model", list(ModelId))
@pytest.mark.parametrize("status", [ValueStatus.MISSING, ValueStatus.QUARANTINED, ValueStatus.UNSUPPORTED])
def test_m06_required_missingness_never_becomes_safe_zero(model, status):
    fixture = inputs("0.98", current="80")
    component = "LUNA" if model is ModelId.B2 else "UST"
    old = fixture.luna[-1] if component == "LUNA" else fixture.ust[-1]
    absent = replace(old, measurement=Measurement(status, None, old.measurement.unit, reason="synthetic absence"))
    fixture = replace(fixture, luna=fixture.luna[:-1] + (absent,)) if component == "LUNA" else replace(
        fixture, ust=(absent,),
    )
    result = evaluate(model, fixture, context(), toy_config())
    assert result.level is RiskLevel.ABSTAIN and result.score is None
    assert result.signals == () and result.reasons


@pytest.mark.parametrize("model", list(ModelId))
def test_empty_required_support_abstains(model):
    result = evaluate(model, WarningInputs((), ()), context(), toy_config())
    assert result.level is RiskLevel.ABSTAIN
    assert result.score is None


def test_m06_unknown_availability_is_not_historical_admission():
    fixture = inputs()
    unknown = replace(fixture.ust[0], vintage=DatasetVintage("unknown", None, None, at(4),
                                                              unknown_clock_reason="unproved"))
    result = evaluate(ModelId.B3, replace(fixture, ust=(unknown,)), context(), toy_config())
    assert result.level is RiskLevel.ABSTAIN
    assert "UST:SOURCE_CLOCK_UNPROVEN" in result.reasons


def test_m07_future_revision_and_future_value_do_not_rewrite_output():
    fixture = inputs("0.99", current="90")
    original = fixture.ust[0]
    future = replace(original, vintage=DatasetVintage("revision", at(4), at(4), at(4), original.vintage.vintage_id),
                     measurement=replace(original.measurement, value="0.5"))
    expected = evaluate(ModelId.B3, fixture, context(), toy_config())
    for extra in (future, replace(future, measurement=replace(future.measurement, value="0.8"))):
        changed = replace(fixture, ust=(original, extra, observation("UST", 4, "0.4")))
        assert evaluate(ModelId.B3, changed, context(), toy_config()) == expected
        assert evaluate(ModelId.B3, changed, context(), toy_config()).output_hash == expected.output_hash


def test_m07_equal_value_selected_evidence_and_revision_ancestry_change_hash():
    fixture = inputs()
    original = fixture.ust[0]
    first = evaluate(ModelId.B3, fixture, context(), toy_config())
    changed = replace(original, provenance=replace(original.provenance, raw_sha256="a" * 64))
    second = evaluate(ModelId.B3, replace(fixture, ust=(changed,)), context(), toy_config())
    assert first.score == second.score and first.input_lineage_hash != second.input_lineage_hash
    revision = replace(original, vintage=DatasetVintage("revision", at(3), at(3), at(3), original.vintage.vintage_id))
    third = evaluate(ModelId.B3, replace(fixture, ust=(original, revision)), context(), toy_config())
    assert third.score == first.score and third.input_lineage_hash != first.input_lineage_hash
    assert third.slots[0].ancestry == (original, revision)


def test_unused_old_evidence_is_not_selected_lineage():
    fixture = inputs()
    before = evaluate(ModelId.B3, fixture, context(), toy_config())
    after = evaluate(ModelId.B3, replace(fixture, ust=(observation("UST", 0, "0.1"), *fixture.ust)),
                     context(), toy_config())
    assert before == after


def test_m08_future_publication_cannot_enter_required_current_bar():
    fixture = inputs()
    old = fixture.ust[0]
    future = replace(old, vintage=DatasetVintage("future", at(4), at(4), at(4)))
    result = evaluate(ModelId.B3, replace(fixture, ust=(future,)), context(), toy_config())
    assert result.level is RiskLevel.ABSTAIN and "UST:NOT_YET_AVAILABLE" in result.reasons
    assert result.slots[0].ancestry == ()


def test_m08_incomplete_current_hour_is_excluded():
    fixture = inputs()
    before = evaluate(ModelId.B3, fixture, context(at(3, 30)), toy_config())
    extra = observation("UST", 3, "0.5")  # [03:00,04:00) cannot enter 03:30.
    after = evaluate(ModelId.B3, replace(fixture, ust=fixture.ust + (extra,)), context(at(3, 30)), toy_config())
    assert before == after


def test_m08_duplicate_vintages_do_not_fill_warmup():
    fixture = inputs()
    old = fixture.ust[0]
    revision = replace(old, vintage=DatasetVintage("rev", at(3), at(3), at(3), old.vintage.vintage_id))
    result = evaluate(ModelId.B1, replace(fixture, ust=(old, revision)), context(),
                      replace(toy_config(), peg_persistence=2))
    assert result.level is RiskLevel.ABSTAIN
    assert "UST:REQUIRED_OBSERVATION_MISSING" in result.reasons


def test_persistence_uses_consecutive_required_hours_not_any_available_older_values():
    fixture = inputs("0.99")
    config = replace(toy_config(), peg_persistence=2)
    sustained = replace(fixture, ust=(observation("UST", 1, "0.99"), *fixture.ust))
    broken = replace(fixture, ust=(observation("UST", 1, "1"), *fixture.ust))
    assert evaluate(ModelId.B1, sustained, context(), config).level is RiskLevel.HIGH
    assert evaluate(ModelId.B1, broken, context(), config).level is RiskLevel.NORMAL
    gap = replace(fixture, ust=(observation("UST", 0, "0.99"), *fixture.ust))
    assert evaluate(ModelId.B1, gap, context(), config).level is RiskLevel.ABSTAIN


def test_published_retraction_never_resurrects_old_value():
    fixture = inputs()
    old = fixture.ust[0]
    withdrawn = replace(
        old, vintage=DatasetVintage("withdrawn", at(3), at(3), at(3), old.vintage.vintage_id),
        measurement=Measurement(ValueStatus.QUARANTINED, None, old.measurement.unit, reason="retracted"),
    )
    result = evaluate(ModelId.B3, replace(fixture, ust=(old, withdrawn)), context(), toy_config())
    assert result.level is RiskLevel.ABSTAIN and result.slots[0].selected is None
    assert result.slots[0].ancestry == (old, withdrawn)
    assert "UST:VALUE_QUARANTINED" in result.reasons


def test_staleness_and_policy_are_explicit_and_bound_in_lineage():
    fixture = inputs()
    config = toy_config()
    stale = replace(config, ust=replace(config.ust, policy=AdmissionPolicy(timedelta(0), timedelta(minutes=59))))
    result = evaluate(ModelId.B3, fixture, context(), stale)
    assert result.level is RiskLevel.ABSTAIN and "UST:SOURCE_STALE" in result.reasons
    changed = replace(config, ust=replace(config.ust, policy=AdmissionPolicy(timedelta(0), timedelta(hours=25))))
    a, b = (evaluate(ModelId.B3, fixture, context(), cfg) for cfg in (config, changed))
    assert a.score == b.score and a.input_lineage_hash != b.input_lineage_hash
    assert a.config.config_hash != b.config.config_hash


def test_cutoff_not_later_decision_or_issue_clock_controls_admission():
    fixture = inputs()
    old = fixture.ust[0]
    delayed = replace(old, vintage=DatasetVintage("delayed", at(3, 30), at(3, 30), at(4)))
    ctx = DecisionContext(at(4), at(3), at(5))
    assert evaluate(ModelId.B3, replace(fixture, ust=(delayed,)), ctx, toy_config()).level is RiskLevel.ABSTAIN


@pytest.mark.parametrize("kind", ["units", "source", "origin", "verification", "frequency", "interval"])
def test_m11_wrong_identity_and_unapproved_origins_are_rejected(kind):
    fixture = inputs()
    old = fixture.ust[0]
    replacements = {
        "units": replace(old, measurement=replace(old.measurement, unit=AssetUnit("UST", "USDT", "USDT/UST"))),
        "source": replace(old, provenance=replace(old.provenance, source_id="unapproved-source")),
        "origin": replace(old, provenance=replace(old.provenance, origin=EvidenceOrigin.OBSERVED)),
        "verification": replace(old, provenance=replace(old.provenance, verification=VerificationLevel.NOT_VERIFIED)),
        "frequency": replace(old, source_frequency=SourceFrequency.DAILY_CARRIED_FORWARD),
        "interval": replace(old, interval=None),
    }
    with pytest.raises(TypeContractError):
        evaluate(ModelId.B3, replace(fixture, ust=(replacements[kind],)), context(), toy_config())


@pytest.mark.parametrize("kind", ["duplicate", "fork", "wrong_parent", "identity_change"])
def test_revision_and_duplicate_boundaries(kind):
    fixture = inputs()
    old = fixture.ust[0]
    revision = replace(old, vintage=DatasetVintage("rev", at(3), at(3), at(3), old.vintage.vintage_id))
    cases = {
        "duplicate": (old, old),
        "fork": (old, revision, replace(revision, vintage=replace(revision.vintage, vintage_id="fork"))),
        "wrong_parent": (old, replace(revision, vintage=replace(revision.vintage, revision_of="unknown"))),
        "identity_change": (old, replace(revision, observation_id="changed-id")),
    }
    with pytest.raises(TypeContractError):
        evaluate(ModelId.B3, replace(fixture, ust=cases[kind]), context(), toy_config())


@pytest.mark.parametrize(("asset", "value"), [("UST", "0"), ("UST", "-1"), ("LUNA", "0"), ("LUNA", "-1")])
def test_nonpositive_price_blocks_before_division(asset, value):
    fixture = inputs()
    fixture = replace(fixture, ust=(observation("UST", 2, value),)) if asset == "UST" else replace(
        fixture, luna=(observation("LUNA", 1, value), fixture.luna[1]),
    )
    result = evaluate(ModelId.B3, fixture, context(), toy_config())
    assert result.score is None and result.level is RiskLevel.ABSTAIN


def test_m12_nonterminating_returns_use_explicit_reduced_ratios_not_decimal_context():
    fixture = WarningInputs((observation("UST", 2, "1"),), tuple(
        observation("LUNA", hour, value) for hour, value in ((0, "3"), (1, "2"), (2, "1"))
    ))
    config = replace(toy_config(), luna_return_window=2)
    result = evaluate(ModelId.B2, fixture, context(), config)
    signals = {signal.signal_id: signal.value for signal in result.signals}
    assert signals["luna_trailing_signed_mean"] == ExactRatio(-5, 12)
    assert signals["luna_trailing_population_variance"] == ExactRatio(1, 144)
    assert result.score == ExactRatio(1, 2)
    assert ExactRatio(2, 6) == ExactRatio(1, 3)
    # Accepted PIT helper is unchanged; do not force it to support this arithmetic profile.
    bars = tuple(observation("UST", hour, value) for hour, value in ((0, "1"), (1, "1"), (2, "2")))
    with pytest.raises(TypeContractError, match="NON_TERMINATING_MEAN_UNSUPPORTED"):
        trailing_mean(bars, at(3), 3, config.ust.policy)


def test_upside_is_not_downside_and_composite_saturates():
    result = evaluate(ModelId.B3, inputs("1.1", current="110"), context(), toy_config())
    assert result.score == ExactRatio(0)
    result = evaluate(ModelId.B3, inputs("0.5", current="10"), context(), toy_config())
    assert result.score == ExactRatio(1)
    parts = [signal.value.fraction for signal in result.signals if signal.role == "SCORE_CONTRIBUTION"]
    assert sum(parts) == Fraction(1)


@pytest.mark.parametrize("bad", [True, False, 0, -1, 17, 1.0, "1"])
def test_bounded_config_rejects_bool_integer_confusion(bad):
    with pytest.raises(TypeContractError):
        replace(toy_config(), peg_persistence=bad)


@pytest.mark.parametrize(("n", "d"), [(True, 1), (1, True), (1, 0), (1, -1), (1.0, 1), (1 << 12001, 1)])
def test_ratio_runtime_and_size_bounds(n, d):
    with pytest.raises(TypeContractError):
        ExactRatio(n, d)


def test_m11_mutable_input_rejected_and_outputs_frozen():
    fixture = inputs()
    with pytest.raises(TypeContractError):
        WarningInputs(list(fixture.ust), fixture.luna)
    with pytest.raises(TypeContractError):
        WarningInputs(fixture.ust * (MAX_OBSERVATIONS + 1), fixture.luna)
    result = evaluate(ModelId.B3, fixture, context(), toy_config())
    with pytest.raises(FrozenInstanceError):
        result.score = ExactRatio(1)
    with pytest.raises(TypeContractError):
        replace(result, slots=list(result.slots))
    with pytest.raises(TypeContractError):
        replace(result, level="NORMAL")
    with pytest.raises(TypeContractError):
        replace(result, level=RiskLevel.ABSTAIN)


def test_config_and_clock_validation():
    config = toy_config()
    with pytest.raises(TypeContractError):
        replace(config, reference_price=ExactRatio(0))
    with pytest.raises(TypeContractError):
        replace(config, profile_id="fitted-on-holdout")
    with pytest.raises(TypeContractError):
        replace(config, ust=replace(config.ust, policy=AdmissionPolicy(timedelta(0))))
    with pytest.raises(TypeContractError):
        DecisionContext(at(2), at(3), at(4))
    with pytest.raises(TypeContractError):
        DecisionContext(at(3), at(2), at(1))
    with pytest.raises(TypeContractError):
        evaluate("B3", inputs(), context(), config)


def test_m09_m10_deferred_metrics_and_quiet_model_only():
    # Runtime obligation only: 24 synthetic quiet decisions. No evaluation metrics or labels API.
    for _ in range(24):
        for model in ModelId:
            assert evaluate(model, inputs(), context(), toy_config()).level is RiskLevel.NORMAL
    package = Path(__file__).resolve().parents[3] / "defistress_v2" / "terra_warning"
    assert not (package / "evaluator.py").exists()


def test_output_domain_and_native_observation_separation():
    result = evaluate(ModelId.B3, inputs(), context(), toy_config())
    payload = json.loads(canonical_json_bytes(result, schema_version="test-export/1"))["payload"]
    assert payload["origin"] == "SYNTHETIC"
    assert payload["record_kind"] == "SYNTHETIC_MODEL_WARNING_NOT_NATIVE_OBSERVATION"
    assert payload["validation_status"] == "SYNTHETIC_CONTROLS_ONLY"
    assert payload["required_observations"] == payload["available_observations"] == "3"
    assert digest("one", "same") != digest("two", "same")
    assert content_sha256("same") != digest("selected-causal-inputs", "same")
    assert not isinstance(result, TemporalObservation)


def test_deterministic_repeated_runs_and_no_external_runtime_imports():
    expected = evaluate(ModelId.B3, inputs("0.99", current="90"), context(), toy_config()).output_hash
    assert {evaluate(ModelId.B3, inputs("0.99", current="90"), context(), toy_config()).output_hash
            for _ in range(20)} == {expected}
    package = Path(__file__).resolve().parents[3] / "defistress_v2" / "terra_warning"
    assert len(list(package.glob("*.py"))) == 3
    forbidden = {"os", "pathlib", "requests", "httpx", "socket", "subprocess", "sim", "backend"}
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not ({name.name.split(".")[0] for name in node.names} & forbidden)
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in forbidden
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"open", "eval", "exec", "compile"}
