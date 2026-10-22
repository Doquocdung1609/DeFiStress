"""Pure synthetic-only temporal admission and no-lookahead primitives."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from fractions import Fraction

from defistress_v2.contracts import canonical_json_bytes, normalize_integer_string
from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.terra_pit.contracts import (
    AdmissionDecision,
    AdmissionPolicy,
    AdmissionStatus,
    AssetUnit,
    EvidenceOrigin,
    SourceFrequency,
    TemporalObservation,
    UtcInstant,
    ValueStatus,
)

TERRA_PIT_SCHEMA_VERSION = "defistress-terra-pit-contracts/0.1"


def content_sha256(payload: object) -> str:
    return hashlib.sha256(canonical_json_bytes(payload, schema_version=TERRA_PIT_SCHEMA_VERSION)).hexdigest()


def completed_interval_time(observation: TemporalObservation, processing_delay: timedelta) -> UtcInstant:
    if type(processing_delay) is not timedelta or processing_delay < timedelta(0):
        raise TypeContractError("processing_delay must be nonnegative")
    base = observation.interval.end if observation.interval is not None else observation.observed_at
    return base.add(processing_delay)


def admissible_at(
    observation: TemporalObservation,
    decision_time: UtcInstant,
    policy: AdmissionPolicy,
    *,
    interval_delay: timedelta = timedelta(0),
) -> AdmissionDecision:
    if type(observation) is not TemporalObservation or type(decision_time) is not UtcInstant:
        raise TypeContractError("admission inputs must be typed")
    if type(policy) is not AdmissionPolicy:
        raise TypeContractError("policy must be AdmissionPolicy")
    if observation.measurement.status is ValueStatus.QUARANTINED:
        return AdmissionDecision(
            AdmissionStatus.REJECTED, ("VALUE_QUARANTINED",), decision_time, None, observation.observation_id
        )
    if observation.measurement.status is not ValueStatus.AVAILABLE:
        return AdmissionDecision(
            AdmissionStatus.BLOCKED,
            (f"VALUE_{observation.measurement.status.value}",),
            decision_time,
            None,
            observation.observation_id,
        )
    if observation.vintage.availability_time is None or observation.vintage.publication_time is None:
        return AdmissionDecision(
            AdmissionStatus.BLOCKED, ("SOURCE_CLOCK_UNPROVEN",), decision_time, None, observation.observation_id
        )
    interval_ready = completed_interval_time(observation, interval_delay)
    source_ready = max(observation.vintage.publication_time, observation.vintage.availability_time, interval_ready)
    eligible_at = source_ready.add(policy.additional_delay)
    if decision_time < eligible_at:
        return AdmissionDecision(
            AdmissionStatus.BLOCKED, ("NOT_YET_AVAILABLE",), decision_time, eligible_at, observation.observation_id
        )
    if policy.max_source_age is None and observation.source_frequency is SourceFrequency.DAILY_CARRIED_FORWARD:
        return AdmissionDecision(
            AdmissionStatus.ABSTAIN,
            ("STALENESS_POLICY_UNRESOLVED",),
            decision_time,
            eligible_at,
            observation.observation_id,
        )
    if (
        policy.max_source_age is not None
        and decision_time.value - observation.observed_at.value > policy.max_source_age
    ):
        return AdmissionDecision(
            AdmissionStatus.ABSTAIN, ("SOURCE_STALE",), decision_time, eligible_at, observation.observation_id
        )
    return AdmissionDecision(
        AdmissionStatus.ELIGIBLE, ("PIT_ELIGIBLE",), decision_time, eligible_at, observation.observation_id
    )


def latest_eligible_vintage(
    observations: tuple[TemporalObservation, ...], decision_time: UtcInstant, policy: AdmissionPolicy
) -> TemporalObservation | None:
    validate_observation_order(observations)
    if not observations:
        return None
    first = observations[0]
    known_vintages: set[str] = set()
    prior_availability: UtcInstant | None = None
    for item in observations:
        if (
            item.observation_id != first.observation_id
            or item.observed_at != first.observed_at
            or item.interval != first.interval
            or item.measurement.unit != first.measurement.unit
            or item.provenance.source_id != first.provenance.source_id
        ):
            raise TypeContractError("VINTAGE_IDENTITY_MISMATCH")
        if item.vintage.revision_of is not None and item.vintage.revision_of not in known_vintages:
            raise TypeContractError("REVISION_CHAIN_INVALID")
        availability = item.vintage.availability_time
        if availability is not None and prior_availability is not None and availability < prior_availability:
            raise TypeContractError("VINTAGE_AVAILABILITY_OUT_OF_ORDER")
        known_vintages.add(item.vintage.vintage_id)
        if availability is not None:
            prior_availability = availability
    eligible = [
        item for item in observations if admissible_at(item, decision_time, policy).status is AdmissionStatus.ELIGIBLE
    ]
    if not eligible:
        return None
    return max(eligible, key=lambda item: (item.vintage.availability_time, item.vintage.vintage_id))


def derived_availability(dependencies: tuple[UtcInstant, ...], processing_delay: timedelta) -> UtcInstant:
    if type(dependencies) is not tuple or not dependencies:
        raise TypeContractError("derived value requires immutable nonempty dependencies")
    if any(type(item) is not UtcInstant for item in dependencies):
        raise TypeContractError("dependencies must be UtcInstant values")
    if type(processing_delay) is not timedelta or processing_delay < timedelta(0):
        raise TypeContractError("processing_delay must be nonnegative")
    return max(dependencies).add(processing_delay)


def validate_observation_order(observations: tuple[TemporalObservation, ...]) -> None:
    if type(observations) is not tuple:
        raise TypeContractError("observations must be an immutable tuple")
    seen: set[tuple[UtcInstant, str]] = set()
    prior: UtcInstant | None = None
    for item in observations:
        if type(item) is not TemporalObservation:
            raise TypeContractError("observation sequence contains an invalid member")
        key = (item.observed_at, item.vintage.vintage_id)
        if key in seen:
            raise TypeContractError("DUPLICATE_OBSERVATION")
        if prior is not None and item.observed_at < prior:
            raise TypeContractError("OUT_OF_ORDER_OBSERVATION")
        seen.add(key)
        prior = item.observed_at


@dataclass(frozen=True, slots=True)
class TrailingWindowResult:
    decision_time: UtcInstant
    observation_ids: tuple[str, ...]
    value: str
    unit: AssetUnit
    content_hash: str

    def to_canonical(self) -> object:
        return {
            "decision_time": self.decision_time,
            "observation_ids": self.observation_ids,
            "unit": self.unit,
            "value": self.value,
        }


def trailing_mean(
    observations: tuple[TemporalObservation, ...],
    decision_time: UtcInstant,
    window: int,
    policy: AdmissionPolicy,
) -> TrailingWindowResult:
    if type(window) is not int or window <= 0:
        raise TypeContractError("window must be a positive exact integer")
    validate_observation_order(observations)
    if observations:
        first = observations[0]
        for item in observations[1:]:
            if (
                item.chain != first.chain
                or item.measurement.unit != first.measurement.unit
                or item.provenance.source_id != first.provenance.source_id
                or item.provenance.origin is not first.provenance.origin
                or item.source_frequency is not first.source_frequency
            ):
                raise TypeContractError("TRAILING_SERIES_IDENTITY_MISMATCH")
    eligible_by_time: list[TemporalObservation] = []
    vintage_group: list[TemporalObservation] = []
    for item in observations:
        if item.provenance.origin is not EvidenceOrigin.SYNTHETIC:
            raise TypeContractError("P04-02 trailing functions accept synthetic observations only")
        if vintage_group and item.observed_at != vintage_group[0].observed_at:
            chosen = latest_eligible_vintage(tuple(vintage_group), decision_time, policy)
            if chosen is not None:
                eligible_by_time.append(chosen)
            vintage_group = []
        vintage_group.append(item)
    if vintage_group:
        chosen = latest_eligible_vintage(tuple(vintage_group), decision_time, policy)
        if chosen is not None:
            eligible_by_time.append(chosen)
    if len(eligible_by_time) < window:
        raise TypeContractError("WARMUP_NOT_SATISFIED")
    selected = tuple(eligible_by_time[-window:])
    unit = selected[0].measurement.unit
    for item in selected[1:]:
        unit.assert_compatible(item.measurement.unit)
    values = [Fraction(Decimal(item.measurement.value or "NaN")) for item in selected]
    mean = sum(values, Fraction(0, 1)) / window
    normalized = _exact_decimal(mean)
    observation_ids = tuple(item.observation_id for item in selected)
    payload = {
        "decision_time": decision_time,
        "inputs": selected,
        "observation_ids": observation_ids,
        "unit": unit,
        "value": normalized,
        "window": normalize_integer_string(window, signed=False),
    }
    return TrailingWindowResult(decision_time, observation_ids, normalized, unit, content_sha256(payload))


def _exact_decimal(value: Fraction) -> str:
    """Render a terminating rational exactly, independent of mutable Decimal context."""

    denominator = value.denominator
    twos = 0
    fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        raise TypeContractError("NON_TERMINATING_MEAN_UNSUPPORTED")
    scale = max(twos, fives)
    scaled = value.numerator * (10**scale) // value.denominator
    sign = "-" if scaled < 0 else ""
    digits = str(abs(scaled)).zfill(scale + 1)
    rendered = (
        f"{sign}{digits[:-scale]}.{digits[-scale:]}".rstrip("0").rstrip(".")
        if scale
        else f"{sign}{digits}"
    )
    return "0" if rendered == "-0" else rendered


@dataclass(frozen=True, slots=True)
class TemporalSplit:
    train_start: UtcInstant
    train_end: UtcInstant
    holdout_start: UtcInstant
    holdout_end: UtcInstant
    forecast_horizon: timedelta

    def __post_init__(self) -> None:
        if any(
            type(value) is not UtcInstant
            for value in (self.train_start, self.train_end, self.holdout_start, self.holdout_end)
        ):
            raise TypeContractError("split clocks must be UtcInstant values")
        if not (self.train_start < self.train_end <= self.holdout_start < self.holdout_end):
            raise TypeContractError("split clocks must be ordered and non-overlapping")
        if type(self.forecast_horizon) is not timedelta or self.forecast_horizon < timedelta(0):
            raise TypeContractError("forecast_horizon must be nonnegative")

    @property
    def purge_required(self) -> bool:
        return self.train_end.value + self.forecast_horizon > self.holdout_start.value


@dataclass(frozen=True, slots=True)
class TransformFitLineage:
    transform_id: str
    fitted_through: UtcInstant
    partition: str

    def __post_init__(self) -> None:
        if type(self.transform_id) is not str or not self.transform_id:
            raise TypeContractError("transform_id must be nonempty")
        if self.partition not in {"TRAIN", "HOLDOUT"}:
            raise TypeContractError("partition must be TRAIN or HOLDOUT")
        if type(self.fitted_through) is not UtcInstant:
            raise TypeContractError("fitted_through must be UtcInstant")


def assert_fit_is_train_only(lineage: TransformFitLineage, split: TemporalSplit) -> None:
    if lineage.partition != "TRAIN" or lineage.fitted_through > split.train_end:
        raise TypeContractError("FIT_LINEAGE_LEAK")
