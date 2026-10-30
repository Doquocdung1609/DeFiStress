"""Pure adapters to accepted PIT admission; no data readers, fit, or evaluator."""

from __future__ import annotations

from datetime import timedelta
from fractions import Fraction

from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.terra_pit import (
    EvidenceOrigin,
    SourceFrequency,
    TemporalObservation,
    UtcInstant,
    VerificationLevel,
    admissible_at,
    completed_interval_time,
    derived_availability,
    latest_eligible_vintage,
    validate_observation_order,
)
from defistress_v2.terra_warning.contracts import (
    DecisionContext,
    ExactRatio,
    InputSlot,
    ModelId,
    RiskLevel,
    SeriesSpec,
    SignalContribution,
    WarningConfig,
    WarningInputs,
    WarningResult,
)

HOUR = timedelta(hours=1)


def _validate_series(observations: tuple[TemporalObservation, ...], spec: SeriesSpec) -> None:
    validate_observation_order(observations)
    vintages: set[str] = set()
    identities: dict[str, UtcInstant] = {}
    for item in observations:
        if item.provenance.origin is not EvidenceOrigin.SYNTHETIC:
            raise TypeContractError("SYNTHETIC_INPUTS_ONLY")
        if item.provenance.verification is not VerificationLevel.FULL_BYTES_VERIFIED:
            raise TypeContractError("SYNTHETIC_BYTES_VERIFICATION_REQUIRED")
        if item.chain != spec.chain or item.provenance.source_id != spec.source_id:
            raise TypeContractError("SOURCE_IDENTITY_MISMATCH")
        spec.unit.assert_compatible(item.measurement.unit)
        if item.source_frequency is not SourceFrequency.HOURLY_AGGREGATE:
            raise TypeContractError("ONLY_DISTINCT_COMPLETED_HOURLY_SYNTHETIC_BARS")
        if (
            item.interval is None or item.observed_at != item.interval.start
            or item.interval.end.value - item.interval.start.value != HOUR
            or item.observed_at.value.minute or item.observed_at.value.second or item.observed_at.value.microsecond
        ):
            raise TypeContractError("EXPLICIT_HOUR_START_AND_COMPLETED_INTERVAL_REQUIRED")
        if item.vintage.vintage_id in vintages:
            raise TypeContractError("DUPLICATE_SOURCE_VINTAGE")
        vintages.add(item.vintage.vintage_id)
        if item.observation_id in identities and identities[item.observation_id] != item.observed_at:
            raise TypeContractError("OBSERVATION_ID_REUSED_ACROSS_TIME")
        identities[item.observation_id] = item.observed_at


def _slot(
    component: str, expected: UtcInstant, group: tuple[TemporalObservation, ...],
    cutoff: UtcInstant, spec: SeriesSpec,
) -> InputSlot:
    if not group:
        return InputSlot(component, expected, (), None, ("REQUIRED_OBSERVATION_MISSING",))
    # Accepted linear revision validation and retraction/no-fallback selection.
    chosen = latest_eligible_vintage(group, cutoff, spec.policy)
    if chosen is not None:
        ancestry = group[:group.index(chosen) + 1]
        if chosen.measurement.value is None or Fraction(chosen.measurement.value) <= 0:
            return InputSlot(component, expected, ancestry, None, ("PRICE_MUST_BE_POSITIVE",))
        return InputSlot(component, expected, ancestry, chosen, ())
    visible: list[TemporalObservation] = []
    for item in group:
        vintage = item.vintage
        if vintage.publication_time is not None and vintage.availability_time is not None:
            ready = derived_availability(
                (vintage.publication_time, vintage.availability_time, completed_interval_time(item, timedelta(0))),
                spec.policy.additional_delay,
            )
            if ready <= cutoff:
                visible.append(item)
    if visible:
        latest = visible[-1]
        admission = admissible_at(latest, cutoff, spec.policy)
        return InputSlot(component, expected, group[:group.index(latest) + 1], None, admission.reason_codes)
    # Never bind values/IDs from unused unpublished future descendants to a past output.
    unknown = tuple(item for item in group if item.vintage.availability_time is None)
    reason = "SOURCE_CLOCK_UNPROVEN" if unknown else "NOT_YET_AVAILABLE"
    return InputSlot(component, expected, unknown, None, (reason,))


def _select(
    component: str, observations: tuple[TemporalObservation, ...],
    spec: SeriesSpec, count: int, cutoff: UtcInstant,
) -> tuple[InputSlot, ...]:
    by_time: dict[UtcInstant, list[TemporalObservation]] = {}
    for item in observations:
        by_time.setdefault(item.observed_at, []).append(item)
    anchor = cutoff.value.replace(minute=0, second=0, microsecond=0)
    result: list[InputSlot] = []
    for offset in range(count, 0, -1):
        expected = UtcInstant(anchor - offset * HOUR)
        result.append(_slot(component, expected, tuple(by_time.get(expected, ())), cutoff, spec))
    return tuple(result)


def _level(score: Fraction, watch: Fraction, high: Fraction) -> RiskLevel:
    return RiskLevel.HIGH if score >= high else RiskLevel.WATCH if score >= watch else RiskLevel.NORMAL


def _compute_result_fields(
    model_id: ModelId, inputs: WarningInputs, context: DecisionContext, config: WarningConfig,
) -> tuple[tuple[InputSlot, ...], tuple[SignalContribution, ...], ExactRatio | None, RiskLevel, tuple[str, ...]]:
    """Compute fields without constructing a result, so the public contract can recheck them."""
    if type(model_id) is not ModelId or type(inputs) is not WarningInputs:
        raise TypeContractError("model and inputs must be typed immutable contracts")
    if type(context) is not DecisionContext or type(config) is not WarningConfig:
        raise TypeContractError("context/configuration must be typed immutable contracts")
    _validate_series(inputs.ust, config.ust)
    _validate_series(inputs.luna, config.luna)
    ust = () if model_id is ModelId.B2 else _select(
        "UST", inputs.ust, config.ust, config.peg_persistence, context.information_cutoff,
    )
    luna = () if model_id is ModelId.B1 else _select(
        "LUNA", inputs.luna, config.luna, config.luna_return_window + 1, context.information_cutoff,
    )
    slots = ust + luna
    reasons = tuple(sorted({f"{slot.component}:{reason}" for slot in slots for reason in slot.reasons}))
    if reasons:
        return slots, (), None, RiskLevel.ABSTAIN, reasons
    if model_id is ModelId.B0:
        return slots, (), ExactRatio(0), RiskLevel.NORMAL, ()
    signals: list[SignalContribution] = []

    def signal(name: str, value: Fraction, role: str = "DERIVED_FEATURE") -> None:
        signals.append(SignalContribution(name, ExactRatio.from_fraction(value), role))

    def prices(selected: tuple[InputSlot, ...]) -> tuple[Fraction, ...]:
        values: list[Fraction] = []
        for slot in selected:
            if slot.selected is None or slot.selected.measurement.value is None:
                raise TypeContractError("internal selection invariant violated")
            values.append(Fraction(slot.selected.measurement.value))
        return tuple(values)

    d = Fraction(0)
    loss = Fraction(0)
    if ust:
        deviations = tuple(max(Fraction(0), 1 - value / config.reference_price.fraction) for value in prices(ust))
        d = min(deviations)
        signal("ust_current_downside", deviations[-1])
        signal("ust_persistent_downside", d)
    if luna:
        series = prices(luna)
        returns = tuple(series[i] / series[i - 1] - 1 for i in range(1, len(series)))
        loss = max(Fraction(0), -returns[-1])
        mean = sum(returns, Fraction(0)) / len(returns)
        variance = sum(((value - mean) ** 2 for value in returns), Fraction(0)) / len(returns)
        signal("luna_current_downside", loss)
        signal("luna_trailing_signed_mean", mean)
        signal("luna_trailing_population_variance", variance)
    if model_id is ModelId.B1:
        score, level = d, _level(d, Fraction(1, 200), Fraction(1, 100))
    elif model_id is ModelId.B2:
        score, level = loss, _level(loss, Fraction(1, 20), Fraction(1, 10))
    else:
        peg_part = min(Fraction(1), d / Fraction(1, 50)) / 2
        luna_part = min(Fraction(1), loss / Fraction(1, 5)) / 2
        signal("ust_score_contribution", peg_part, "SCORE_CONTRIBUTION")
        signal("luna_score_contribution", luna_part, "SCORE_CONTRIBUTION")
        score = peg_part + luna_part
        level = _level(score, Fraction(1, 2), Fraction(3, 4))
    return slots, tuple(signals), ExactRatio.from_fraction(score), level, ()


def evaluate(
    model_id: ModelId, inputs: WarningInputs, context: DecisionContext, config: WarningConfig,
) -> WarningResult:
    """Evaluate one frozen synthetic decision; every invocation rechecks admission."""
    slots, signals, score, level, reasons = _compute_result_fields(model_id, inputs, context, config)
    return WarningResult(model_id, context, config, slots, signals, score, level, reasons)
