"""Immutable, block-bound values exposed by the saved-state adapter."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
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

    def __post_init__(self) -> None:
        for value in (self.artifact_path, self.json_pointer, self.reason_code, self.reason):
            if type(value) is not str or not value.strip():
                raise TypeContractError("quarantine fields must be nonempty strings")
        if type(self.parent_raw_sha256) is not str or re.fullmatch(r"[0-9a-f]{64}", self.parent_raw_sha256) is None:
            raise TypeContractError("quarantine parent must be a SHA256")

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
    field_availability: FrozenMap = field(default_factory=lambda: FrozenMap.from_mapping({}))

    def __post_init__(self) -> None:
        if (
            type(self.component_id) is not str
            or not self.component_id
            or type(self.payload) is not FrozenMap
            or type(self.field_origins) is not FrozenMap
            or type(self.evidence) is not EvidenceRef
        ):
            raise TypeContractError("component snapshot identity, payload and evidence must be typed")
        if (
            type(self.kind) is not ComponentKind
            or type(self.origin) is not OriginKind
            or type(self.coverage) is not CoverageStatus
        ):
            raise TypeContractError("component kind/origin/coverage must be typed enums")
        if type(self.available_time_precision) is not TimePrecision or type(self.field_availability) is not FrozenMap:
            raise TypeContractError("component availability metadata must be immutable and typed")
        for timestamp in (self.effective_at_s, self.available_at_s):
            if type(timestamp) is not int or timestamp < 0:
                raise TypeContractError("component timestamps must be exact nonnegative integers")
        if type(self.source_declared_status) is not str or not self.source_declared_status:
            raise TypeContractError("source status must be explicit")
        if self.source_declared_content_sha256 is not None and (
            type(self.source_declared_content_sha256) is not str
            or re.fullmatch(r"[0-9a-f]{64}", self.source_declared_content_sha256) is None
        ):
            raise TypeContractError("source content hash must be a SHA256 or explicitly absent")
        allowed = {
            "ACTIVE_LIQUIDITY_READ",
            "POOL_SLOT0_READ",
            "REGISTERED_TICK_BAND_READ",
            "AAVE_ORACLE_PRICE_READ",
            "SOURCE_TRACE_READ",
            "HF_RECONSTRUCTION_TRACE_READ",
            "SELECTED_PORTFOLIO_READ",
            "SOURCE_HEALTH_FACTOR_READ",
        }
        if type(self.capabilities) is not tuple or any(
            type(x) is not str or x not in allowed for x in self.capabilities
        ):
            raise TypeContractError("saved snapshots support only explicit immutable read capabilities")
        if type(self.quarantines) is not tuple or any(type(x) is not QuarantineRecord for x in self.quarantines):
            raise TypeContractError("quarantine records must be an immutable typed tuple")
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
            "field_availability": self.field_availability,
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

    def __post_init__(self) -> None:
        for value in (
            self.artifact_git_ref,
            self.adapter_source_commit,
            self.full_pack_source_commit,
            self.borrower_pack_source_commit,
        ):
            if type(value) is not str or re.fullmatch(r"[0-9a-f]{40}", value) is None:
                raise TypeContractError("provenance commits must be full Git SHAs")
        if type(self.selection_manifest_hash) is not DeterministicContentSha256:
            raise TypeContractError("selection hash must use its typed content domain")

    def to_canonical(self) -> object:
        return {
            "adapter_source_commit": self.adapter_source_commit,
            "artifact_git_ref": self.artifact_git_ref,
            "borrower_pack_source_commit": self.borrower_pack_source_commit,
            "full_pack_source_commit": self.full_pack_source_commit,
            "selection_manifest_hash": self.selection_manifest_hash,
            "artifact_ref_verification": "CALLER_DECLARED_REF;CONTENT_ANCHORED_TO_ACCEPTED_PHASE01B_BLOBS",
        }


@dataclass(frozen=True, slots=True)
class HistoricalSnapshot:
    block_ref: BlockRef
    read_pass: int
    components: tuple[ComponentSnapshot, ...]
    complete: ExplicitBool
    provenance: SnapshotProvenance
    limitations: tuple[str, ...]
    canonicality_evidence: EvidenceRef | None = None

    def __post_init__(self) -> None:
        if type(self.read_pass) is not int or self.read_pass not in (1, 2):
            raise TypeContractError("read_pass must be 1 or 2")
        if (
            type(self.block_ref) is not BlockRef
            or type(self.provenance) is not SnapshotProvenance
            or type(self.complete) is not ExplicitBool
        ):
            raise TypeContractError("snapshot block/completeness/provenance must be typed")
        if (
            type(self.components) is not tuple
            or not self.components
            or any(type(x) is not ComponentSnapshot for x in self.components)
        ):
            raise TypeContractError("snapshot must contain components")
        ids = [item.component_id for item in self.components]
        if ids != sorted(ids) or len(ids) != len(set(ids)):
            raise TypeContractError("components must be unique and sorted")
        if any(item.evidence.block_ref != self.block_ref for item in self.components):
            raise TypeContractError("every component must bind the snapshot block")
        if type(self.limitations) is not tuple or any(type(x) is not str or not x for x in self.limitations):
            raise TypeContractError("snapshot limitations must be immutable strings")
        if self.complete.value != all(x.coverage is CoverageStatus.COMPLETE_REGISTERED_SCOPE for x in self.components):
            raise TypeContractError("snapshot completeness contradicts component coverage")
        if (
            type(self.canonicality_evidence) is not EvidenceRef
            or self.canonicality_evidence.block_ref != self.block_ref
        ):
            raise TypeContractError("snapshot canonicality must retain its block-bound source evidence")

    def to_canonical(self) -> object:
        return {
            "schema_version": "defistress-v2-saved-snapshot/1",
            "block_ref": self.block_ref,
            "canonicality_evidence": self.canonicality_evidence,
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
        assert self.canonicality_evidence is not None
        document["canonicality_evidence"] = self.canonicality_evidence.to_content_canonical()
        return document

    @property
    def content_sha256(self) -> DeterministicContentSha256:
        return DeterministicContentSha256.from_payload(self.to_content_canonical())
