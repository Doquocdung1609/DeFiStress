"""Tagged availability/results and pure temporal consistency guards."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from defistress_v2.contracts.canonical import deep_freeze, normalize_integer_string
from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.contracts.evidence import EvidenceRef, SourceKind
from defistress_v2.contracts.identity import BlockRef


def _reason(value: object, field: str = "reason") -> str:
    if type(value) is not str or not value.strip():
        raise TypeContractError(f"{field} must be a nonempty string")
    return value


def _refs(value: tuple[EvidenceRef, ...]) -> tuple[EvidenceRef, ...]:
    refs = tuple(value)
    if not refs:
        raise TypeContractError("at least one evidence reference is required")
    if any(type(reference) is not EvidenceRef for reference in refs):
        raise TypeContractError("evidence references must be EvidenceRef values")
    return refs


class ValueStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"
    UNSUPPORTED = "UNSUPPORTED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True, slots=True)
class Available[T]:
    value: T
    refs: tuple[EvidenceRef, ...]
    status: ValueStatus = field(default=ValueStatus.AVAILABLE, init=False)

    def __post_init__(self) -> None:
        if self.value is None:
            raise TypeContractError("AVAILABLE cannot carry None")
        object.__setattr__(self, "value", deep_freeze(self.value))
        object.__setattr__(self, "refs", _refs(self.refs))


@dataclass(frozen=True, slots=True)
class Missing:
    reason: str
    refs: tuple[EvidenceRef, ...]
    status: ValueStatus = field(default=ValueStatus.MISSING, init=False)

    def __post_init__(self) -> None:
        _reason(self.reason)
        object.__setattr__(self, "refs", _refs(self.refs))


@dataclass(frozen=True, slots=True)
class Unsupported:
    interface: str
    reason: str
    refs: tuple[EvidenceRef, ...]
    status: ValueStatus = field(default=ValueStatus.UNSUPPORTED, init=False)

    def __post_init__(self) -> None:
        _reason(self.interface, "interface")
        _reason(self.reason)
        object.__setattr__(self, "refs", _refs(self.refs))


@dataclass(frozen=True, slots=True)
class Quarantined:
    reason: str
    refs: tuple[EvidenceRef, ...]
    status: ValueStatus = field(default=ValueStatus.QUARANTINED, init=False)

    def __post_init__(self) -> None:
        _reason(self.reason)
        object.__setattr__(self, "refs", _refs(self.refs))


class ResultStatus(StrEnum):
    OK = "OK"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class Ok[T]:
    payload: T
    warnings: tuple[str, ...] = ()
    status: ResultStatus = field(default=ResultStatus.OK, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", deep_freeze(self.payload))
        object.__setattr__(self, "warnings", tuple(_reason(item, "warning") for item in self.warnings))


@dataclass(frozen=True, slots=True)
class Blocked:
    code: str
    reason: str
    affected_refs: tuple[EvidenceRef, ...]
    status: ResultStatus = field(default=ResultStatus.BLOCKED, init=False)

    def __post_init__(self) -> None:
        _reason(self.code, "code")
        _reason(self.reason)
        object.__setattr__(self, "affected_refs", _refs(self.affected_refs))


@dataclass(frozen=True, slots=True)
class Rejected:
    code: str
    reason: str
    affected_refs: tuple[EvidenceRef, ...]
    status: ResultStatus = field(default=ResultStatus.REJECTED, init=False)

    def __post_init__(self) -> None:
        _reason(self.code, "code")
        _reason(self.reason)
        object.__setattr__(self, "affected_refs", _refs(self.affected_refs))


@dataclass(frozen=True, slots=True)
class AsOfContext:
    block_ref: BlockRef
    available_at_s: int

    def __post_init__(self) -> None:
        if type(self.block_ref) is not BlockRef:
            raise TypeContractError("block_ref must be a BlockRef")
        if type(self.available_at_s) is not int or self.available_at_s < self.block_ref.timestamp_s:
            raise TypeContractError("as-of availability must be an exact timestamp at or after the block")


@dataclass(frozen=True, slots=True)
class ObservationContext:
    block_ref: BlockRef
    effective_at_s: int
    available_at_s: int
    evidence_ref: EvidenceRef

    def __post_init__(self) -> None:
        if type(self.block_ref) is not BlockRef:
            raise TypeContractError("block_ref must be a BlockRef")
        if type(self.evidence_ref) is not EvidenceRef:
            raise TypeContractError("evidence_ref must be an EvidenceRef")
        for field_name in ("effective_at_s", "available_at_s"):
            value = getattr(self, field_name)
            if type(value) is not int or value < 0:
                raise TypeContractError(f"{field_name} must be a nonnegative exact timestamp")

    def to_canonical(self) -> object:
        return {
            "available_at_s": normalize_integer_string(self.available_at_s, signed=False),
            "block_ref": self.block_ref,
            "effective_at_s": normalize_integer_string(self.effective_at_s, signed=False),
            "evidence_ref": self.evidence_ref,
        }


def guard_same_block_and_time(
    as_of: AsOfContext, observations: tuple[ObservationContext, ...]
) -> Ok[tuple[ObservationContext, ...]] | Rejected:
    """Reject cross-block or look-ahead joins without mutating inputs."""

    for observation in observations:
        if observation.block_ref.identity_key != as_of.block_ref.identity_key:
            return Rejected(
                code="TIMESTAMP_OR_BLOCK_LEAKAGE",
                reason="observation block identity differs from the as-of block",
                affected_refs=(observation.evidence_ref,),
            )
        if observation.effective_at_s > as_of.available_at_s or observation.available_at_s > as_of.available_at_s:
            return Rejected(
                code="TIMESTAMP_OR_BLOCK_LEAKAGE",
                reason="observation was not effective and available by the as-of timestamp",
                affected_refs=(observation.evidence_ref,),
            )
    return Ok(tuple(observations))


def guard_source_kind(evidence: EvidenceRef, expected: SourceKind) -> Ok[EvidenceRef] | Rejected:
    if evidence.source_kind is not expected:
        return Rejected(
            code="ORACLE_SOURCE_CONFUSION",
            reason=f"expected {expected.value}, received {evidence.source_kind.value}",
            affected_refs=(evidence,),
        )
    return Ok(evidence)


def guard_canonicality_evidence(block_ref: BlockRef, evidence: EvidenceRef) -> Ok[EvidenceRef] | Rejected:
    """Bind a reorg/canonicality assertion to its evidence and observation time."""

    if evidence.evidence_id != block_ref.canonicality_evidence_id:
        return Rejected(
            code="INPUT_IDENTITY_MISMATCH",
            reason="canonicality evidence identity does not match the block reference",
            affected_refs=(evidence,),
        )
    if evidence.retrieved_at_s != block_ref.canonicality_observed_at_s:
        return Rejected(
            code="TIMESTAMP_OR_BLOCK_LEAKAGE",
            reason="canonicality evidence observation time does not match the block reference",
            affected_refs=(evidence,),
        )
    if evidence.block_ref is None or evidence.block_ref.identity_key != block_ref.identity_key:
        return Rejected(
            code="INPUT_IDENTITY_MISMATCH",
            reason="canonicality evidence does not bind the same block identity",
            affected_refs=(evidence,),
        )
    return Ok(evidence)
