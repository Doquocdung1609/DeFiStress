"""Evidence, hash-domain and immutable lineage contracts."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from typing import ClassVar

from defistress_v2.contracts.canonical import (
    CONTRACT_SCHEMA_VERSION,
    CanonicalSerializable,
    canonical_json_bytes,
    deep_freeze,
    normalize_integer_string,
)
from defistress_v2.contracts.errors import (
    DigestMismatchError,
    LineageContractError,
    TypeContractError,
)
from defistress_v2.contracts.identity import BlockRef

_HEX = re.compile(r"[0-9a-f]+")
_FULL_COMMIT = re.compile(r"[0-9a-f]{40}")
_SECRET_PATTERN = re.compile(r"(?i)(authorization\s*:|bearer\s+|api[_-]?key=|token=|://[^/\s]+:[^/\s]+@)")


@dataclass(frozen=True, slots=True)
class HexDigest:
    value: str
    LENGTH: ClassVar[int] = 0

    def __post_init__(self) -> None:
        if type(self.value) is not str or len(self.value) != type(self).LENGTH or _HEX.fullmatch(self.value) is None:
            raise TypeContractError(f"{type(self).__name__} must be {type(self).LENGTH} lowercase hex characters")

    def to_canonical(self) -> object:
        return self.value


@dataclass(frozen=True, slots=True)
class ArtifactBytesSha256(HexDigest):
    LENGTH: ClassVar[int] = 64

    @classmethod
    def from_bytes(cls, raw: bytes) -> ArtifactBytesSha256:
        if type(raw) is not bytes:
            raise TypeContractError("artifact input must be exact bytes")
        return cls(hashlib.sha256(raw).hexdigest())


@dataclass(frozen=True, slots=True)
class DecodedBytesSha256(HexDigest):
    LENGTH: ClassVar[int] = 64

    @classmethod
    def from_bytes(cls, raw: bytes) -> DecodedBytesSha256:
        if type(raw) is not bytes:
            raise TypeContractError("decoded input must be exact bytes")
        return cls(hashlib.sha256(raw).hexdigest())


@dataclass(frozen=True, slots=True)
class DeterministicContentSha256(HexDigest):
    LENGTH: ClassVar[int] = 64

    @classmethod
    def from_payload(cls, payload: object) -> DeterministicContentSha256:
        return cls(hashlib.sha256(canonical_json_bytes(payload)).hexdigest())


@dataclass(frozen=True, slots=True)
class GitBlobSha1(HexDigest):
    LENGTH: ClassVar[int] = 40

    @classmethod
    def from_bytes(cls, raw: bytes) -> GitBlobSha1:
        if type(raw) is not bytes:
            raise TypeContractError("Git blob input must be exact bytes")
        header = f"blob {len(raw)}\0".encode()
        return cls(hashlib.sha1(header + raw).hexdigest())


def verify_artifact_bytes(raw: bytes, expected: ArtifactBytesSha256) -> None:
    """Verify the bytes supplied by the caller without any decoding/normalization."""

    if type(raw) is not bytes:
        raise TypeContractError("artifact input must be exact bytes")
    if ArtifactBytesSha256.from_bytes(raw) != expected:
        raise DigestMismatchError("raw artifact bytes do not match the declared SHA-256")


def verify_decoded_bytes(raw: bytes, expected: DecodedBytesSha256) -> None:
    """Verify caller-provided decoded bytes in their distinct hash domain."""

    if type(raw) is not bytes:
        raise TypeContractError("decoded input must be exact bytes")
    if DecodedBytesSha256.from_bytes(raw) != expected:
        raise DigestMismatchError("decoded bytes do not match the declared SHA-256")


class OriginKind(StrEnum):
    OBSERVED = "OBSERVED"
    RECONSTRUCTED = "RECONSTRUCTED"
    SYNTHETIC = "SYNTHETIC"
    COUNTERFACTUAL = "COUNTERFACTUAL"


class SourceKind(StrEnum):
    ONCHAIN_CONTRACT = "ONCHAIN_CONTRACT"
    ORACLE_ADAPTER = "ORACLE_ADAPTER"
    DEX_SPOT = "DEX_SPOT"
    SAVED_ARTIFACT = "SAVED_ARTIFACT"
    SYNTHETIC_FIXTURE = "SYNTHETIC_FIXTURE"


def _nonempty(value: object, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise TypeContractError(f"{field} must be a nonempty string")
    if _SECRET_PATTERN.search(value):
        raise TypeContractError(f"{field} appears to contain secret-bearing material")
    return value


@dataclass(frozen=True, slots=True)
class EvidenceRef:
    evidence_id: str
    origin: OriginKind
    source_kind: SourceKind
    source_commit: str
    artifact_path: str
    locator: str
    source_schema: str
    verification_scope: str
    retrieved_at_s: int
    raw_sha256: ArtifactBytesSha256
    block_ref: BlockRef | None = None
    method_args_hash: DeterministicContentSha256 | None = None
    decoded_sha256: DecodedBytesSha256 | None = None
    git_blob_sha1: GitBlobSha1 | None = None

    def __post_init__(self) -> None:
        if type(self.origin) is not OriginKind:
            raise TypeContractError("origin must be an OriginKind")
        if type(self.source_kind) is not SourceKind:
            raise TypeContractError("source_kind must be a SourceKind")
        if type(self.raw_sha256) is not ArtifactBytesSha256:
            raise TypeContractError("raw_sha256 must use the artifact-bytes hash domain")
        optional_types = (
            (self.block_ref, BlockRef, "block_ref"),
            (self.method_args_hash, DeterministicContentSha256, "method_args_hash"),
            (self.decoded_sha256, DecodedBytesSha256, "decoded_sha256"),
            (self.git_blob_sha1, GitBlobSha1, "git_blob_sha1"),
        )
        for value, expected, field in optional_types:
            if value is not None and type(value) is not expected:
                raise TypeContractError(f"{field} has the wrong nominal type")
        for field in (
            "evidence_id",
            "source_commit",
            "artifact_path",
            "locator",
            "source_schema",
            "verification_scope",
        ):
            _nonempty(getattr(self, field), field)
        if self.origin is not OriginKind.SYNTHETIC and _FULL_COMMIT.fullmatch(self.source_commit) is None:
            raise TypeContractError("non-synthetic source_commit must be a full lowercase Git SHA")
        if self.origin is not OriginKind.SYNTHETIC and self.source_kind is SourceKind.SYNTHETIC_FIXTURE:
            raise LineageContractError("non-synthetic evidence cannot use the synthetic fixture source kind")
        artifact = PurePosixPath(self.artifact_path)
        if artifact.is_absolute() or ".." in artifact.parts or "\\" in self.artifact_path:
            raise TypeContractError("artifact_path must be a safe repository-relative POSIX path")
        if type(self.retrieved_at_s) is not int or self.retrieved_at_s < 0:
            raise TypeContractError("retrieved_at_s must be a nonnegative exact integer")
        if self.block_ref is not None and self.retrieved_at_s < self.block_ref.timestamp_s:
            raise LineageContractError("evidence cannot be retrieved before its referenced block")
        if self.origin is OriginKind.SYNTHETIC and (
            self.source_kind is not SourceKind.SYNTHETIC_FIXTURE or not self.evidence_id.startswith("synthetic:")
        ):
            raise LineageContractError("synthetic evidence must use a visible synthetic fixture identity")

    @classmethod
    def synthetic(cls, fixture_id: str, raw: bytes, *, retrieved_at_s: int = 0) -> EvidenceRef:
        _nonempty(fixture_id, "fixture_id")
        evidence_id = fixture_id if fixture_id.startswith("synthetic:") else f"synthetic:{fixture_id}"
        return cls(
            evidence_id=evidence_id,
            origin=OriginKind.SYNTHETIC,
            source_kind=SourceKind.SYNTHETIC_FIXTURE,
            source_commit="SYNTHETIC_NO_COMMIT",
            artifact_path=f"synthetic/{fixture_id}",
            locator="/",
            source_schema="synthetic-fixture/1",
            verification_scope="SYNTHETIC_CONTRACT_CONTROL_ONLY",
            retrieved_at_s=retrieved_at_s,
            raw_sha256=ArtifactBytesSha256.from_bytes(raw),
        )

    def to_canonical(self) -> object:
        return {
            "artifact_path": self.artifact_path,
            "block_ref": self.block_ref,
            "decoded_sha256": self.decoded_sha256,
            "evidence_id": self.evidence_id,
            "git_blob_sha1": self.git_blob_sha1,
            "locator": self.locator,
            "method_args_hash": self.method_args_hash,
            "origin": self.origin,
            "raw_sha256": self.raw_sha256,
            "retrieved_at_s": normalize_integer_string(self.retrieved_at_s, signed=False),
            "source_commit": self.source_commit,
            "source_kind": self.source_kind,
            "source_schema": self.source_schema,
            "verification_scope": self.verification_scope,
        }

    def to_content_canonical(self) -> object:
        """Project stable content; full acquisition metadata remains serialized above."""

        document = self.to_canonical()
        assert isinstance(document, dict)
        return {key: value for key, value in document.items() if key != "retrieved_at_s"}


def _content_projection(value: object) -> object:
    """Exclude only typed acquisition timestamps, never similarly named payload keys."""

    if isinstance(value, (EvidenceRef, EvidenceEnvelope)):
        return _content_projection(value.to_content_canonical())
    if isinstance(value, CanonicalSerializable):
        return _content_projection(value.to_canonical())
    if isinstance(value, Mapping):
        return {key: _content_projection(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return tuple(_content_projection(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class EvidenceEnvelope:
    payload: object
    block_ref: BlockRef
    origin: OriginKind
    sources: tuple[EvidenceRef, ...]
    derivation_id: str | None = None
    parent_content_hashes: tuple[DeterministicContentSha256, ...] = ()
    parent_origins: tuple[OriginKind, ...] = ()
    schema_version: str = CONTRACT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if type(self.block_ref) is not BlockRef:
            raise TypeContractError("block_ref must be a BlockRef")
        if type(self.origin) is not OriginKind:
            raise TypeContractError("origin must be an OriginKind")
        for field in ("sources", "parent_content_hashes", "parent_origins"):
            values = getattr(self, field)
            if type(values) not in (tuple, list):
                raise TypeContractError(f"{field} must be an explicit tuple or list, not a single-use iterator")
            object.__setattr__(self, field, tuple(values))
        if any(type(source) is not EvidenceRef for source in self.sources):
            raise TypeContractError("sources must contain only EvidenceRef values")
        if any(type(value) is not DeterministicContentSha256 for value in self.parent_content_hashes):
            raise TypeContractError("parent_content_hashes use the deterministic-content hash domain")
        if any(type(value) is not OriginKind for value in self.parent_origins):
            raise TypeContractError("parent_origins must contain only OriginKind values")
        if self.schema_version != CONTRACT_SCHEMA_VERSION:
            raise LineageContractError("unsupported evidence-envelope schema version")
        if not self.sources:
            raise LineageContractError("evidence envelope requires at least one source")
        if len(self.parent_content_hashes) != len(self.parent_origins):
            raise LineageContractError("parent hashes and parent origins must align")
        if self.origin is OriginKind.OBSERVED:
            if self.derivation_id is not None or self.parent_content_hashes:
                raise LineageContractError("derived evidence cannot be promoted to OBSERVED")
            if any(source.origin is not OriginKind.OBSERVED for source in self.sources):
                raise LineageContractError("OBSERVED envelope requires observed source evidence")
            if any(
                source.block_ref is None
                or source.block_ref.identity_key != self.block_ref.identity_key
                or source.block_ref.timestamp_s != self.block_ref.timestamp_s
                for source in self.sources
            ):
                raise LineageContractError("OBSERVED sources must bind the envelope block identity and timestamp")
        elif self.origin in (OriginKind.RECONSTRUCTED, OriginKind.COUNTERFACTUAL):
            if self.derivation_id is None or not self.parent_content_hashes:
                raise LineageContractError("derived evidence requires derivation and parent content hashes")
            _nonempty(self.derivation_id, "derivation_id")
        elif not any(source.origin is OriginKind.SYNTHETIC for source in self.sources):
            raise LineageContractError("SYNTHETIC envelope requires a visible synthetic source")
        object.__setattr__(self, "payload", deep_freeze(self.payload))
        canonical_json_bytes(self.to_canonical())

    @property
    def content_sha256(self) -> DeterministicContentSha256:
        return DeterministicContentSha256.from_payload(self.to_content_canonical())

    def to_content_canonical(self) -> object:
        """Hash stable state/lineage, retaining economic and canonicality timestamps."""

        return _content_projection(self.to_canonical())

    def to_canonical(self) -> object:
        return {
            "block_ref": self.block_ref,
            "derivation_id": self.derivation_id,
            "origin": self.origin,
            "parent_content_hashes": self.parent_content_hashes,
            "parent_origins": self.parent_origins,
            "payload": self.payload,
            "schema_version": self.schema_version,
            "sources": self.sources,
        }
