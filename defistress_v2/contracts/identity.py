"""Immutable block and asset identities for offline evidence joins."""

from __future__ import annotations

import re
from dataclasses import dataclass

from defistress_v2.contracts.canonical import normalize_integer_string
from defistress_v2.contracts.errors import IdentityContractError, TypeContractError

_BYTES32 = re.compile(r"0x[0-9a-fA-F]{64}")
_ADDRESS = re.compile(r"0x[0-9a-fA-F]{40}")


def _strict_int(value: object, field: str, *, minimum: int, maximum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeContractError(f"{field} must be an exact integer")
    if value < minimum or (maximum is not None and value > maximum):
        raise TypeContractError(f"{field} is outside its declared range")
    return value


def _nonempty(value: object, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise TypeContractError(f"{field} must be a nonempty string")
    return value


@dataclass(frozen=True, slots=True)
class BlockRef:
    chain_id: int
    number: int
    hash: str
    timestamp_s: int
    canonicality_evidence_id: str
    canonicality_observed_at_s: int

    def __post_init__(self) -> None:
        _strict_int(self.chain_id, "chain_id", minimum=1, maximum=2**256 - 1)
        _strict_int(self.number, "number", minimum=0, maximum=2**256 - 1)
        _strict_int(self.timestamp_s, "timestamp_s", minimum=0, maximum=2**256 - 1)
        observed = _strict_int(
            self.canonicality_observed_at_s,
            "canonicality_observed_at_s",
            minimum=0,
            maximum=2**256 - 1,
        )
        if type(self.hash) is not str or _BYTES32.fullmatch(self.hash) is None:
            raise IdentityContractError("block hash must be an exact bytes32 hex string")
        _nonempty(self.canonicality_evidence_id, "canonicality_evidence_id")
        if observed < self.timestamp_s:
            raise IdentityContractError("canonicality cannot be observed before the block timestamp")
        object.__setattr__(self, "hash", self.hash.lower())

    @property
    def identity_key(self) -> tuple[int, int, str]:
        return (self.chain_id, self.number, self.hash)

    def to_canonical(self) -> object:
        return {
            "canonicality_evidence_id": self.canonicality_evidence_id,
            "canonicality_observed_at_s": normalize_integer_string(self.canonicality_observed_at_s, signed=False),
            "chain_id": normalize_integer_string(self.chain_id, signed=False),
            "hash": self.hash,
            "number": normalize_integer_string(self.number, signed=False),
            "timestamp_s": normalize_integer_string(self.timestamp_s, signed=False),
        }


@dataclass(frozen=True, slots=True)
class AssetId:
    chain_id: int
    address: str
    decimals: int
    decimals_evidence_id: str
    symbol: str | None = None

    def __post_init__(self) -> None:
        _strict_int(self.chain_id, "chain_id", minimum=1, maximum=2**256 - 1)
        _strict_int(self.decimals, "decimals", minimum=0, maximum=255)
        if type(self.address) is not str or _ADDRESS.fullmatch(self.address) is None:
            raise IdentityContractError("asset address must be an exact 20-byte hex string")
        _nonempty(self.decimals_evidence_id, "decimals_evidence_id")
        if self.symbol is not None:
            _nonempty(self.symbol, "symbol")
        object.__setattr__(self, "address", self.address.lower())

    @property
    def identity_key(self) -> tuple[int, str]:
        return (self.chain_id, self.address)

    def to_canonical(self) -> object:
        return {
            "address": self.address,
            "chain_id": normalize_integer_string(self.chain_id, signed=False),
            "decimals": normalize_integer_string(self.decimals, signed=False),
            "decimals_evidence_id": self.decimals_evidence_id,
            "symbol": self.symbol,
        }
