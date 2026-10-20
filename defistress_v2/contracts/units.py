"""Exact unit-bound quantities; no floating point or implicit coercion."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from defistress_v2.contracts.canonical import normalize_integer_string
from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.contracts.identity import AssetId

UINT256_MAX = 2**256 - 1
INT256_MIN = -(2**255)
INT256_MAX = 2**255 - 1


class QuantityKind(StrEnum):
    BALANCE = "BALANCE"
    DEBT = "DEBT"
    COLLATERAL = "COLLATERAL"
    DELTA = "DELTA"
    NET_LIQUIDITY = "NET_LIQUIDITY"


@dataclass(frozen=True, slots=True)
class UnsignedAmount:
    asset: AssetId
    raw_amount: str
    kind: QuantityKind

    def __post_init__(self) -> None:
        if type(self.asset) is not AssetId:
            raise TypeContractError("asset must be an AssetId")
        if type(self.kind) is not QuantityKind:
            raise TypeContractError("kind must be a QuantityKind")
        if self.kind in (QuantityKind.DELTA, QuantityKind.NET_LIQUIDITY):
            raise TypeContractError("signed quantity kind cannot use UnsignedAmount")
        normalized = normalize_integer_string(self.raw_amount, signed=False)
        if int(normalized) > UINT256_MAX:
            raise TypeContractError("unsigned amount exceeds uint256")
        object.__setattr__(self, "raw_amount", normalized)

    @classmethod
    def from_int(cls, asset: AssetId, raw_amount: int, kind: QuantityKind) -> UnsignedAmount:
        if type(raw_amount) is not int:
            raise TypeContractError("raw_amount must be an exact integer")
        return cls(asset=asset, raw_amount=normalize_integer_string(raw_amount, signed=False), kind=kind)

    def to_canonical(self) -> object:
        return {"asset": self.asset, "kind": self.kind, "raw_amount": self.raw_amount}


@dataclass(frozen=True, slots=True)
class SignedDelta:
    asset: AssetId
    raw_delta: str
    kind: QuantityKind

    def __post_init__(self) -> None:
        if type(self.asset) is not AssetId:
            raise TypeContractError("asset must be an AssetId")
        if type(self.kind) is not QuantityKind:
            raise TypeContractError("kind must be a QuantityKind")
        if self.kind not in (QuantityKind.DELTA, QuantityKind.NET_LIQUIDITY):
            raise TypeContractError("unsigned quantity kind cannot use SignedDelta")
        normalized = normalize_integer_string(self.raw_delta, signed=True)
        numeric = int(normalized)
        if numeric < INT256_MIN or numeric > INT256_MAX:
            raise TypeContractError("signed delta exceeds int256")
        object.__setattr__(self, "raw_delta", normalized)

    @classmethod
    def from_int(cls, asset: AssetId, raw_delta: int, kind: QuantityKind) -> SignedDelta:
        if type(raw_delta) is not int:
            raise TypeContractError("raw_delta must be an exact integer")
        return cls(asset=asset, raw_delta=normalize_integer_string(raw_delta, signed=True), kind=kind)

    def to_canonical(self) -> object:
        return {"asset": self.asset, "kind": self.kind, "raw_delta": self.raw_delta}
