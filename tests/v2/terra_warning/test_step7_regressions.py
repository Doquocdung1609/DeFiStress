"""Step7 probes, including the four original R58-01 regression witnesses.

No implementation test helper, historical data, collector or fitted parameter is used.
"""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import localcontext

import pytest

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


def instant(hour, microsecond=0):
    return UtcInstant(datetime(2035, 2, 3, hour, tzinfo=UTC).replace(microsecond=microsecond))


def bar(asset, hour, price):
    name = f"step7-{asset}-{hour}"
    return TemporalObservation(
        name,
        TerraChainId("columbus-5"),
        instant(hour),
        TimeInterval(instant(hour), instant(hour + 1)),
        DatasetVintage(name + "-original", instant(hour + 1), instant(hour + 1), instant(hour + 1)),
        Measurement(ValueStatus.AVAILABLE, price, AssetUnit(asset, "USD", f"USD/{asset}"), "step7-complete"),
        SourceProvenance(
            f"synthetic-{asset.lower()}",
            "c755bb3a67e0ee84c89698ad6222aa0b715b3629",
            "e" * 64,
            VerificationLevel.FULL_BYTES_VERIFIED,
            EvidenceOrigin.SYNTHETIC,
        ),
        SourceFrequency.HOURLY_AGGREGATE,
    )


def panel(peg="1", previous="100", current="100"):
    return WarningInputs((bar("UST", 2, peg),), (bar("LUNA", 1, previous), bar("LUNA", 2, current)))


def run(model=ModelId.B3, data=None, config=None, clock=None):
    return evaluate(
        model, data or panel(), clock or DecisionContext(instant(3), instant(3), instant(3)), config or toy_config()
    )


@pytest.mark.parametrize(
    ("peg", "luna", "numerator", "denominator", "level"),
    [
        ("1", "100", 0, 1, RiskLevel.NORMAL),
        ("0.99", "100", 1, 4, RiskLevel.NORMAL),
        ("1", "90", 1, 4, RiskLevel.NORMAL),
        ("0.99", "90", 1, 2, RiskLevel.WATCH),
        ("0.98", "80", 1, 1, RiskLevel.HIGH),
        ("0.99", "80", 3, 4, RiskLevel.HIGH),
        ("0.995", "95", 1, 4, RiskLevel.NORMAL),
        ("1.1", "110", 0, 1, RiskLevel.NORMAL),
    ],
)
def test_independent_literal_composite_references(peg, luna, numerator, denominator, level):
    result = run(data=panel(peg, current=luna))
    assert result.score == ExactRatio(numerator, denominator)
    assert result.level is level


@pytest.mark.parametrize("model", list(ModelId))
def test_never_alert_and_common_support(model):
    result = run(model, panel("0.5", current="10"))
    if model is ModelId.B0:
        assert result.score == ExactRatio(0) and result.level is RiskLevel.NORMAL
    else:
        assert result.level is RiskLevel.HIGH
    missing = run(model, WarningInputs((), ()))
    assert missing.level is RiskLevel.ABSTAIN and missing.score is None


def test_peg_two_consecutive_bars_and_luna_exact_trailing_variance():
    cfg = replace(toy_config(), peg_persistence=2, luna_return_window=2)
    data = WarningInputs(
        (bar("UST", 1, "0.99"), bar("UST", 2, "0.995")), (bar("LUNA", 0, "3"), bar("LUNA", 1, "2"), bar("LUNA", 2, "1"))
    )
    assert run(ModelId.B1, data, cfg).score == ExactRatio(1, 200)
    result = run(ModelId.B2, data, cfg)
    signals = {signal.signal_id: signal.value for signal in result.signals}
    assert signals["luna_trailing_signed_mean"] == ExactRatio(-5, 12)
    assert signals["luna_trailing_population_variance"] == ExactRatio(1, 144)


def test_source_age_equality_and_one_microsecond_later():
    cfg = toy_config()
    cfg = replace(cfg, luna=replace(cfg.luna, policy=AdmissionPolicy(timedelta(0), timedelta(hours=2))))
    assert run(config=cfg).level is RiskLevel.NORMAL
    later = instant(3, 1)
    result = run(config=cfg, clock=DecisionContext(later, later, later))
    assert result.level is RiskLevel.ABSTAIN
    assert "LUNA:SOURCE_STALE" in result.reasons


def test_availability_one_microsecond_after_cutoff_abstains():
    data = panel()
    future = instant(3, 1)
    root = data.ust[0]
    delayed = replace(root, vintage=DatasetVintage("delayed", future, future, future))
    result = run(data=replace(data, ust=(delayed,)))
    assert result.level is RiskLevel.ABSTAIN
    assert result.score is None


def test_issued_clock_cannot_move_information_cutoff():
    data = panel()
    root = data.ust[0]
    delayed = replace(root, vintage=DatasetVintage("delayed", instant(4), instant(4), instant(4)))
    result = run(data=replace(data, ust=(delayed,)), clock=DecisionContext(instant(5), instant(3), instant(6)))
    assert result.level is RiskLevel.ABSTAIN


@pytest.mark.parametrize("status", [ValueStatus.MISSING, ValueStatus.QUARANTINED, ValueStatus.UNSUPPORTED])
def test_published_unavailable_revision_cannot_resurrect_parent(status):
    data = panel("0.98", current="80")
    root = data.ust[0]
    revision = replace(
        root,
        vintage=DatasetVintage("child", instant(3), instant(3), instant(3), root.vintage.vintage_id),
        measurement=Measurement(status, None, root.measurement.unit, reason="step7 withdrawal"),
    )
    result = run(data=replace(data, ust=(root, revision)))
    assert result.level is RiskLevel.ABSTAIN and result.score is None
    assert result.slots[0].ancestry == (root, revision)


def test_revision_parent_order_and_unused_future_perturbation():
    data = panel()
    root = data.ust[0]
    root = replace(root, vintage=replace(root.vintage, vintage_id="zzz-parent"))
    revision = replace(
        root,
        vintage=DatasetVintage("aaa-child", instant(3), instant(3), instant(3), "zzz-parent"),
        measurement=replace(root.measurement, value="0.99"),
    )
    selected = run(data=replace(data, ust=(root, revision)))
    assert selected.slots[0].selected == revision
    future = replace(
        revision,
        vintage=DatasetVintage("future-child", instant(4), instant(4), instant(4), "aaa-child"),
        measurement=replace(root.measurement, value="0.5"),
    )
    assert run(data=replace(data, ust=(root, revision, future))) == selected
    assert run(data=replace(data, ust=(root, revision, future))).output_hash == selected.output_hash


@pytest.mark.parametrize(
    "origin", [EvidenceOrigin.OBSERVED, EvidenceOrigin.RECONSTRUCTED, EvidenceOrigin.COUNTERFACTUAL]
)
def test_no_origin_promotion(origin):
    data = panel()
    root = data.ust[0]
    with pytest.raises(TypeContractError):
        run(data=replace(data, ust=(replace(root, provenance=replace(root.provenance, origin=origin)),)))


def test_units_source_identity_and_unknown_clock():
    data = panel()
    root = data.ust[0]
    wrong_quote = replace(root, measurement=replace(root.measurement, unit=AssetUnit("UST", "USDT", "USDT/UST")))
    with pytest.raises(TypeContractError):
        run(data=replace(data, ust=(wrong_quote,)))
    wrong_source = replace(root, provenance=replace(root.provenance, source_id="other"))
    with pytest.raises(TypeContractError):
        run(data=replace(data, ust=(wrong_source,)))
    unknown = replace(
        root, vintage=DatasetVintage("unknown", None, None, instant(3), unknown_clock_reason="no publication proof")
    )
    assert run(data=replace(data, ust=(unknown,))).level is RiskLevel.ABSTAIN


def test_low_decimal_context_does_not_flip_exact_high_threshold():
    hashes = []
    for precision in (1, 2, 50):
        with localcontext() as ctx:
            ctx.prec = precision
            result = run(data=panel("0.99", current="80"))
            assert result.score == ExactRatio(3, 4) and result.level is RiskLevel.HIGH
            hashes.append(result.output_hash)
    assert len(set(hashes)) == 1


def test_changed_selected_provenance_changes_lineage_without_changing_score():
    data = panel()
    original = run(data=data)
    item = replace(data.ust[0], provenance=replace(data.ust[0].provenance, raw_sha256="f" * 64))
    revised = run(data=replace(data, ust=(item,)))
    assert original.score == revised.score
    assert original.input_lineage_hash != revised.input_lineage_hash


# R58-01: unchanged ordinary assertions from the Step7 review; no xfail or skip.
def test_r58_01_result_constructor_should_reject_b0_high_score():
    result = run(ModelId.B0)
    with pytest.raises(TypeContractError):
        replace(result, level=RiskLevel.HIGH, score=ExactRatio(1))


def test_r58_01_result_constructor_should_reject_partial_composite_support():
    result = run()
    with pytest.raises(TypeContractError):
        replace(result, slots=result.slots[:1])


def test_r58_01_result_constructor_should_reject_future_selected_slot():
    result = run()
    slot = result.slots[0]
    selected = slot.selected
    assert selected is not None
    future = replace(selected, vintage=DatasetVintage("late", instant(4), instant(4), instant(4)))
    forged = replace(slot, selected=future, ancestry=(future,))
    with pytest.raises(TypeContractError):
        replace(result, slots=(forged,) + result.slots[1:])


def test_r58_01_result_constructor_should_reject_level_score_mismatch():
    result = run()
    with pytest.raises(TypeContractError):
        replace(result, level=RiskLevel.HIGH)
