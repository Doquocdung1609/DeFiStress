"""Type-only future state references; this package deliberately has no executor."""

from __future__ import annotations

from dataclasses import dataclass

from defistress_v2.contracts.canonical import normalize_integer_string
from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.contracts.evidence import DeterministicContentSha256
from defistress_v2.contracts.identity import BlockRef


@dataclass(frozen=True, slots=True)
class FutureStateRef:
    """An immutable reference for future packages, not a transition proposal."""

    block_ref: BlockRef
    state_version: int
    content_sha256: DeterministicContentSha256

    def __post_init__(self) -> None:
        if type(self.block_ref) is not BlockRef:
            raise TypeContractError("block_ref must be a BlockRef")
        if type(self.content_sha256) is not DeterministicContentSha256:
            raise TypeContractError("content_sha256 must use the deterministic-content hash domain")
        if type(self.state_version) is not int or self.state_version < 0:
            raise TypeContractError("state_version must be a nonnegative exact integer")

    def to_canonical(self) -> object:
        return {
            "block_ref": self.block_ref,
            "content_sha256": self.content_sha256,
            "state_version": normalize_integer_string(self.state_version, signed=False),
        }
