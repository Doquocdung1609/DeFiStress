"""Immutable Terra point-in-time contracts with explicit clock and value semantics."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from defistress_v2.contracts import ExplicitBool, normalize_integer_string
from defistress_v2.contracts.errors import IdentityContractError, TypeContractError

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}")
_DECIMAL = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?")


def _identifier(value: object, field: str) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise TypeContractError(f"{field} must be a nonempty canonical identifier")
    return value


class EvidenceOrigin(StrEnum):
    OBSERVED = "OBSERVED"
    RECONSTRUCTED = "RECONSTRUCTED"
    SYNTHETIC = "SYNTHETIC"
    COUNTERFACTUAL = "COUNTERFACTUAL"


class ValueStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"
    UNSUPPORTED = "UNSUPPORTED"
    QUARANTINED = "QUARANTINED"


class AdmissionStatus(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"
    ABSTAIN = "ABSTAIN"


class VerificationLevel(StrEnum):
    FULL_BYTES_VERIFIED = "FULL_BYTES_VERIFIED"
    METADATA_ONLY_BYTES_UNVERIFIED = "METADATA_ONLY_BYTES_UNVERIFIED"
    SOURCE_DECLARED = "SOURCE_DECLARED"
    NOT_VERIFIED = "NOT_VERIFIED"


class IntervalClosure(StrEnum):
    LEFT_CLOSED_RIGHT_OPEN = "LEFT_CLOSED_RIGHT_OPEN"


class RiskOutputStatus(StrEnum):
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


@dataclass(frozen=True, slots=True, order=True)
class UtcInstant:
    """Timezone-aware instant normalized to UTC; naive clocks are forbidden."""

    value: datetime

    def __post_init__(self) -> None:
        if type(self.value) is not datetime or self.value.tzinfo is None or self.value.utcoffset() is None:
            raise TypeContractError("instant must be an exact timezone-aware datetime")
        object.__setattr__(self, "value", self.value.astimezone(UTC))

    @classmethod
    def parse(cls, text: str) -> UtcInstant:
        if type(text) is not str or not text:
            raise TypeContractError("instant text must be nonempty")
        normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
        try:
            return cls(datetime.fromisoformat(normalized))
        except ValueError as exc:
            raise TypeContractError("instant text must be ISO-8601 with timezone") from exc

    def add(self, delay: timedelta) -> UtcInstant:
        if type(delay) is not timedelta or delay < timedelta(0):
            raise TypeContractError("delay must be a nonnegative timedelta")
        return UtcInstant(self.value + delay)

    def to_canonical(self) -> object:
        return self.value.isoformat(timespec="microseconds").replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class TerraChainId:
    """Terra network identity; deliberately independent of EVM numeric chain IDs."""

    network: str

    def __post_init__(self) -> None:
        _identifier(self.network, "Terra network")
        if self.network != "columbus-5":
            raise IdentityContractError("P04-02 supports only the registered Terra columbus-5 identity")

    def to_canonical(self) -> object:
        return {"namespace": "terra", "network": self.network}


@dataclass(frozen=True, slots=True)
class AssetUnit:
    base_asset: str
    quote_asset: str | None
    unit: str

    def __post_init__(self) -> None:
        _identifier(self.base_asset, "base_asset")
        if self.quote_asset is not None:
            _identifier(self.quote_asset, "quote_asset")
        _identifier(self.unit, "unit")

    def assert_compatible(self, other: AssetUnit) -> None:
        if self != other:
            raise TypeContractError("unit/source promotion requires an explicit conversion contract")

    def to_canonical(self) -> object:
        return {"base_asset": self.base_asset, "quote_asset": self.quote_asset, "unit": self.unit}


@dataclass(frozen=True, slots=True)
class TimeInterval:
    start: UtcInstant
    end: UtcInstant
    closure: IntervalClosure = IntervalClosure.LEFT_CLOSED_RIGHT_OPEN

    def __post_init__(self) -> None:
        if type(self.start) is not UtcInstant or type(self.end) is not UtcInstant:
            raise TypeContractError("interval bounds must be UtcInstant values")
        if self.end <= self.start:
            raise TypeContractError("interval end must be strictly after start")
        if self.closure is not IntervalClosure.LEFT_CLOSED_RIGHT_OPEN:
            raise TypeContractError("only [start,end) interval closure is supported")

    def to_canonical(self) -> object:
        return {"closure": self.closure, "end": self.end, "start": self.start}


@dataclass(frozen=True, slots=True)
class Measurement:
    status: ValueStatus
    value: str | None
    unit: AssetUnit
    completeness_evidence_id: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, ValueStatus) or type(self.unit) is not AssetUnit:
            raise TypeContractError("measurement status and unit must be typed")
        if self.status is ValueStatus.AVAILABLE:
            if type(self.value) is not str or _DECIMAL.fullmatch(self.value) is None:
                raise TypeContractError("available measurement requires a canonical decimal string")
            if self.completeness_evidence_id is None:
                raise TypeContractError("available measurement requires completeness evidence")
            _identifier(self.completeness_evidence_id, "completeness_evidence_id")
            if self.reason is not None:
                raise TypeContractError("available measurement cannot have a failure reason")
        else:
            if self.value is not None or self.completeness_evidence_id is not None:
                raise TypeContractError("non-available measurement cannot contain a value or completeness evidence")
            if type(self.reason) is not str or not self.reason.strip():
                raise TypeContractError("non-available measurement requires a reason")

    def to_canonical(self) -> object:
        return {
            "completeness_evidence_id": self.completeness_evidence_id,
            "reason": self.reason,
            "status": self.status,
            "unit": self.unit,
            "value": self.value,
        }


@dataclass(frozen=True, slots=True)
class DatasetVintage:
    vintage_id: str
    publication_time: UtcInstant | None
    availability_time: UtcInstant | None
    ingestion_time: UtcInstant
    revision_of: str | None = None
    unknown_clock_reason: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.vintage_id, "vintage_id")
        if type(self.ingestion_time) is not UtcInstant:
            raise TypeContractError("ingestion_time must be UtcInstant")
        for clock in (self.publication_time, self.availability_time):
            if clock is not None and type(clock) is not UtcInstant:
                raise TypeContractError("vintage clocks must be UtcInstant or explicit unknown")
        if (self.publication_time is None) != (self.availability_time is None):
            raise TypeContractError("publication and availability must both be known or both be unknown")
        if self.publication_time is None:
            if type(self.unknown_clock_reason) is not str or not self.unknown_clock_reason.strip():
                raise TypeContractError("unknown source clocks require an explicit reason")
        else:
            if self.unknown_clock_reason is not None:
                raise TypeContractError("known source clocks cannot have unknown_clock_reason")
            if self.availability_time is None or self.publication_time > self.availability_time:
                raise TypeContractError("publication cannot follow availability")
            if self.availability_time > self.ingestion_time:
                raise TypeContractError("availability cannot follow ingestion")
        if self.revision_of is not None:
            _identifier(self.revision_of, "revision_of")
            if self.revision_of == self.vintage_id:
                raise TypeContractError("vintage cannot revise itself")

    def to_canonical(self) -> object:
        return {
            "availability_time": self.availability_time,
            "ingestion_time": self.ingestion_time,
            "publication_time": self.publication_time,
            "revision_of": self.revision_of,
            "unknown_clock_reason": self.unknown_clock_reason,
            "vintage_id": self.vintage_id,
        }


@dataclass(frozen=True, slots=True)
class SourceProvenance:
    source_id: str
    source_commit: str
    raw_sha256: str
    verification: VerificationLevel
    origin: EvidenceOrigin

    def __post_init__(self) -> None:
        _identifier(self.source_id, "source_id")
        if type(self.source_commit) is not str or re.fullmatch(r"[0-9a-f]{40}", self.source_commit) is None:
            raise TypeContractError("source_commit must be a full lowercase Git SHA")
        if type(self.raw_sha256) is not str or re.fullmatch(r"[0-9a-f]{64}", self.raw_sha256) is None:
            raise TypeContractError("raw_sha256 must be lowercase SHA-256")
        if not isinstance(self.verification, VerificationLevel) or not isinstance(self.origin, EvidenceOrigin):
            raise TypeContractError("provenance enums must be typed")

    def to_canonical(self) -> object:
        return {
            "origin": self.origin,
            "raw_sha256": self.raw_sha256,
            "source_commit": self.source_commit,
            "source_id": self.source_id,
            "verification": self.verification,
        }


@dataclass(frozen=True, slots=True)
class TemporalObservation:
    observation_id: str
    chain: TerraChainId
    observed_at: UtcInstant
    interval: TimeInterval | None
    vintage: DatasetVintage
    measurement: Measurement
    provenance: SourceProvenance
    source_frequency: str

    def __post_init__(self) -> None:
        _identifier(self.observation_id, "observation_id")
        if type(self.chain) is not TerraChainId or type(self.observed_at) is not UtcInstant:
            raise TypeContractError("observation identity/time must be typed")
        if self.interval is not None and type(self.interval) is not TimeInterval:
            raise TypeContractError("interval must be TimeInterval or None")
        if type(self.vintage) is not DatasetVintage or type(self.measurement) is not Measurement:
            raise TypeContractError("vintage and measurement must be typed")
        if type(self.provenance) is not SourceProvenance:
            raise TypeContractError("provenance must be typed")
        _identifier(self.source_frequency, "source_frequency")
        if self.interval is not None and not (self.interval.start <= self.observed_at < self.interval.end):
            raise TypeContractError("observation time must lie in its [start,end) interval")

    def to_canonical(self) -> object:
        return {
            "chain": self.chain,
            "interval": self.interval,
            "measurement": self.measurement,
            "observation_id": self.observation_id,
            "observed_at": self.observed_at,
            "provenance": self.provenance,
            "source_frequency": self.source_frequency,
            "vintage": self.vintage,
        }


@dataclass(frozen=True, slots=True)
class AdmissionPolicy:
    additional_delay: timedelta
    max_source_age: timedelta | None = None

    def __post_init__(self) -> None:
        if type(self.additional_delay) is not timedelta or self.additional_delay < timedelta(0):
            raise TypeContractError("additional_delay must be nonnegative")
        if self.max_source_age is not None and (
            type(self.max_source_age) is not timedelta or self.max_source_age < timedelta(0)
        ):
            raise TypeContractError("max_source_age must be nonnegative or explicitly unresolved")

    def to_canonical(self) -> object:
        return {
            "additional_delay_us": normalize_integer_string(
                self.additional_delay // timedelta(microseconds=1), signed=False
            ),
            "max_source_age_us": (
                None
                if self.max_source_age is None
                else normalize_integer_string(self.max_source_age // timedelta(microseconds=1), signed=False)
            ),
        }


@dataclass(frozen=True, slots=True)
class AdmissionDecision:
    status: AdmissionStatus
    reason_codes: tuple[str, ...]
    decision_time: UtcInstant
    eligible_at: UtcInstant | None
    observation_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.status, AdmissionStatus) or type(self.reason_codes) is not tuple:
            raise TypeContractError("admission status/reasons must be immutable typed values")
        if not self.reason_codes or any(type(reason) is not str or not reason for reason in self.reason_codes):
            raise TypeContractError("admission requires one or more reason codes")
        if type(self.decision_time) is not UtcInstant:
            raise TypeContractError("decision_time must be UtcInstant")
        if self.eligible_at is not None and type(self.eligible_at) is not UtcInstant:
            raise TypeContractError("eligible_at must be UtcInstant or None")
        _identifier(self.observation_id, "observation_id")

    def to_canonical(self) -> object:
        return {
            "decision_time": self.decision_time,
            "eligible_at": self.eligible_at,
            "observation_id": self.observation_id,
            "reason_codes": self.reason_codes,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class QualityReport:
    total: int
    available: int
    missing: int
    unsupported: int
    quarantined: int
    historical_pit_status: str
    historical_predictive_fields: int
    backtest_executed: bool

    def __post_init__(self) -> None:
        values = (self.total, self.available, self.missing, self.unsupported, self.quarantined)
        if any(type(value) is not int or value < 0 for value in values):
            raise TypeContractError("quality counts must be nonnegative exact integers")
        if sum(values[1:]) != self.total:
            raise TypeContractError("quality status counts must equal total")
        if self.historical_pit_status != "BLOCKED_NOT_CLEARED_FOR_FORECAST":
            raise TypeContractError("P04-02 cannot promote historical PIT status")
        if self.historical_predictive_fields != 0 or self.backtest_executed is not False:
            raise TypeContractError("P04-02 historical predictive use and backtest must remain disabled")

    def to_canonical(self) -> object:
        return {
            "available": normalize_integer_string(self.available, signed=False),
            "backtest_executed": ExplicitBool(self.backtest_executed),
            "historical_pit_status": self.historical_pit_status,
            "historical_predictive_fields": normalize_integer_string(self.historical_predictive_fields, signed=False),
            "missing": normalize_integer_string(self.missing, signed=False),
            "quarantined": normalize_integer_string(self.quarantined, signed=False),
            "total": normalize_integer_string(self.total, signed=False),
            "unsupported": normalize_integer_string(self.unsupported, signed=False),
        }


@dataclass(frozen=True, slots=True)
class RiskOutputPlaceholder:
    """Explicit boundary: P04-02 has no warning/risk model output."""

    status: RiskOutputStatus = RiskOutputStatus.NOT_IMPLEMENTED

    def __post_init__(self) -> None:
        if self.status is not RiskOutputStatus.NOT_IMPLEMENTED:
            raise TypeContractError("P04-02 risk output must remain NOT_IMPLEMENTED")

    def to_canonical(self) -> object:
        return {"status": self.status}
