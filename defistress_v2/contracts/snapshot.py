"""Immutable, block-bound values exposed by the saved-state adapter."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from defistress_v2.contracts.canonical import ExplicitBool, FrozenMap, normalize_integer_string
from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.contracts.evidence import DeterministicContentSha256, EvidenceRef, OriginKind
from defistress_v2.contracts.identity import BlockRef


class CoverageStatus(StrEnum):
    COMPLETE_REGISTERED_SCOPE = "COMPLETE_REGISTERED_SCOPE"
    PARTIAL_REGISTERED_SCOPE = "PARTIAL_REGISTERED_SCOPE"
    MISSING = "MISSING"
    UNSUPPORTED = "UNSUPPORTED"
    QUARANTINED = "QUARANTINED"


class TimePrecision(StrEnum):
    BLOCK_TIMESTAMP = "BLOCK_TIMESTAMP"
    COLLECTION_END_UPPER_BOUND = "COLLECTION_END_UPPER_BOUND"


class ComponentKind(StrEnum):
    POOL = "POOL"
    ORACLE = "ORACLE"
    BORROWERS = "BORROWERS"


@dataclass(frozen=True, slots=True)
class QuarantineRecord:
    artifact_path: str
    json_pointer: str
    reason_code: str
    reason: str
    parent_raw_sha256: str

    def to_canonical(self) -> object:
        return {
            "artifact_path": self.artifact_path,
            "json_pointer": self.json_pointer,
            "parent_raw_sha256": self.parent_raw_sha256,
            "reason": self.reason,
            "reason_code": self.reason_code,
        }


@dataclass(frozen=True, slots=True)
class ComponentSnapshot:
    component_id: str
    kind: ComponentKind
    origin: OriginKind
    coverage: CoverageStatus
    source_declared_status: str
    source_declared_content_sha256: str | None
    effective_at_s: int
    available_at_s: int
    available_time_precision: TimePrecision
    payload: FrozenMap
    field_origins: FrozenMap
    capabilities: tuple[str, ...]
    evidence: EvidenceRef
    quarantines: tuple[QuarantineRecord, ...] = ()

    def __post_init__(self) -> None:
        if (
            not self.component_id
            or type(self.payload) is not FrozenMap
            or type(self.field_origins) is not FrozenMap
            or type(self.evidence) is not EvidenceRef
        ):
            raise TypeContractError("component snapshot identity, payload and evidence must be typed")
        if not self.capabilities or len(set(self.capabilities)) != len(self.capabilities):
            raise TypeContractError("component capabilities must be nonempty and unique")
        if self.effective_at_s > self.available_at_s:
            raise TypeContractError("component cannot be available before it is effective")

    def to_canonical(self) -> object:
        return {
            "available_at_s": normalize_integer_string(self.available_at_s, signed=False),
            "available_time_precision": self.available_time_precision,
            "component_id": self.component_id,
            "capabilities": self.capabilities,
            "coverage": self.coverage,
            "effective_at_s": normalize_integer_string(self.effective_at_s, signed=False),
            "evidence": self.evidence,
            "kind": self.kind,
            "field_origins": self.field_origins,
            "origin": self.origin,
            "payload": self.payload,
            "quarantines": self.quarantines,
            "source_declared_content_sha256": self.source_declared_content_sha256,
            "source_declared_status": self.source_declared_status,
        }


@dataclass(frozen=True, slots=True)
class SnapshotProvenance:
    artifact_git_ref: str
    adapter_source_commit: str
    full_pack_source_commit: str
    borrower_pack_source_commit: str
    selection_manifest_hash: DeterministicContentSha256

    def to_canonical(self) -> object:
        return {
            "adapter_source_commit": self.adapter_source_commit,
            "artifact_git_ref": self.artifact_git_ref,
            "borrower_pack_source_commit": self.borrower_pack_source_commit,
            "full_pack_source_commit": self.full_pack_source_commit,
            "selection_manifest_hash": self.selection_manifest_hash,
        }


@dataclass(frozen=True, slots=True)
class HistoricalSnapshot:
    block_ref: BlockRef
    read_pass: int
    components: tuple[ComponentSnapshot, ...]
    complete: ExplicitBool
    provenance: SnapshotProvenance
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.read_pass not in (1, 2):
            raise TypeContractError("read_pass must be 1 or 2")
        if not self.components:
            raise TypeContractError("snapshot must contain components")
        ids = [item.component_id for item in self.components]
        if ids != sorted(ids) or len(ids) != len(set(ids)):
            raise TypeContractError("components must be unique and sorted")
        if any(item.evidence.block_ref != self.block_ref for item in self.components):
            raise TypeContractError("every component must bind the snapshot block")

    def to_canonical(self) -> object:
        return {
            "block_ref": self.block_ref,
            "complete": self.complete,
            "components": self.components,
            "limitations": self.limitations,
            "provenance": self.provenance,
            "read_pass": normalize_integer_string(self.read_pass, signed=False),
        }

    def to_content_canonical(self) -> object:
        document = self.to_canonical()
        assert isinstance(document, dict)
        provenance = self.provenance.to_canonical()
        assert isinstance(provenance, dict)
        document["provenance"] = {
            key: value for key, value in provenance.items() if key not in {"adapter_source_commit", "artifact_git_ref"}
        }
        projected_components: list[dict[str, object]] = []
        for item in self.components:
            component = item.to_canonical()
            assert isinstance(component, dict)
            component["evidence"] = item.evidence.to_content_canonical()
            projected_components.append(component)
        document["components"] = tuple(projected_components)
        return document

    @property
    def content_sha256(self) -> DeterministicContentSha256:
        return DeterministicContentSha256.from_payload(self.to_content_canonical())
