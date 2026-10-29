"""Immutable synthetic-only price and economic valuation contracts for P02-03-S."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from defistress_v2.contracts.canonical import ExplicitBool, normalize_integer_string
from defistress_v2.contracts.errors import IdentityContractError, TypeContractError
from defistress_v2.contracts.evidence import DeterministicContentSha256, EvidenceRef, OriginKind
from defistress_v2.contracts.identity import AssetId, BlockRef
from defistress_v2.contracts.state import Missing, Quarantined, Unsupported
from defistress_v2.contracts.units import UINT256_MAX, QuantityKind, UnsignedAmount

WAD = 10**18


def _asset_unit_key(asset: AssetId) -> tuple[int, str, int]:
    """Economic asset identity used where raw token quantities are interpreted."""

    return (*asset.identity_key, asset.decimals)


def _identifier(value: object, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise TypeContractError(f"{field} must be a nonempty string")
    return value


def _uint(value: object, field: str, maximum: int = UINT256_MAX) -> int:
    if type(value) is not int or value < 0 or value > maximum:
        raise TypeContractError(f"{field} must be an exact unsigned integer within its declared bound")
    return value


def _uint_string(value: object, field: str, *, positive: bool = False) -> str:
    if type(value) is not str:
        raise TypeContractError(f"{field} must be a canonical unsigned integer string")
    normalized = normalize_integer_string(value, signed=False)
    maximum = str(UINT256_MAX)
    if len(normalized) > len(maximum) or (len(normalized) == len(maximum) and normalized > maximum):
        raise TypeContractError(f"{field} exceeds uint256")
    if positive and normalized == "0":
        raise TypeContractError(f"{field} must be positive")
    return normalized


class EconomicPriceClass(StrEnum):
    HISTORICAL_AAVE_ORACLE_OBSERVATION = "HISTORICAL_AAVE_ORACLE_OBSERVATION"
    DEX_OBSERVATION = "DEX_OBSERVATION"
    COUNTERFACTUAL_POLICY = "COUNTERFACTUAL_POLICY"


class RoundStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    UNSUPPORTED = "UNSUPPORTED"
    MISSING = "MISSING"


class ValuationPurpose(StrEnum):
    ELIGIBILITY_CHECKPOINT = "ELIGIBILITY_CHECKPOINT"
    REPORTING_AFTER_TRADE = "REPORTING_AFTER_TRADE"


class ValuationProfile(StrEnum):
    SYNTHETIC_ECONOMIC_REFERENCE = "SYNTHETIC_ECONOMIC_REFERENCE"


class HealthFactorStatus(StrEnum):
    FINITE_WAD = "FINITE_WAD"
    NO_DEBT = "NO_DEBT"


@dataclass(frozen=True, slots=True)
class BaseUnit:
    currency_id: str
    decimals: int
    unit: str
    conversion_evidence_id: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.currency_id, "currency_id")
        _uint(self.decimals, "decimals", 255)
        _identifier(self.unit, "unit")
        if self.conversion_evidence_id is not None:
            _identifier(self.conversion_evidence_id, "conversion_evidence_id")

    @property
    def scale(self) -> int:
        return int(10**self.decimals)

    def to_canonical(self) -> object:
        return {
            "conversion_evidence_id": self.conversion_evidence_id,
            "currency_id": self.currency_id,
            "decimals": normalize_integer_string(self.decimals, signed=False),
            "unit": self.unit,
        }


@dataclass(frozen=True, slots=True)
class RoundMetadata:
    status: RoundStatus
    phase_id: int | None = None
    round_id: int | None = None
    updated_at_s: int | None = None
    answered_in_round: int | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if type(self.status) is not RoundStatus:
            raise TypeContractError("round status must be typed")
        values = (self.phase_id, self.round_id, self.updated_at_s, self.answered_in_round)
        if self.status is RoundStatus.AVAILABLE:
            if any(type(value) is not int for value in values):
                raise TypeContractError("available round metadata requires exact integer fields")
            phase_id = self.phase_id
            round_id = self.round_id
            updated_at_s = self.updated_at_s
            answered_in_round = self.answered_in_round
            assert phase_id is not None and round_id is not None
            assert updated_at_s is not None and answered_in_round is not None
            _uint(phase_id, "phase_id")
            _uint(round_id, "round_id")
            _uint(updated_at_s, "updated_at_s")
            _uint(answered_in_round, "answered_in_round")
            if phase_id == 0 or round_id == 0 or answered_in_round == 0:
                raise TypeContractError("available round identities must be positive")
            if answered_in_round < round_id:
                raise IdentityContractError("answered_in_round cannot precede round_id")
            if self.reason is not None:
                raise TypeContractError("available round metadata cannot have a missingness reason")
        else:
            if any(value is not None for value in values):
                raise TypeContractError("unavailable round metadata cannot fabricate numeric fields")
            _identifier(self.reason, "round reason")

    def to_canonical(self) -> object:
        return {
            "answered_in_round": (
                None
                if self.answered_in_round is None
                else normalize_integer_string(self.answered_in_round, signed=False)
            ),
            "phase_id": None if self.phase_id is None else normalize_integer_string(self.phase_id, signed=False),
            "reason": self.reason,
            "round_id": None if self.round_id is None else normalize_integer_string(self.round_id, signed=False),
            "status": self.status,
            "updated_at_s": (
                None if self.updated_at_s is None else normalize_integer_string(self.updated_at_s, signed=False)
            ),
        }


@dataclass(frozen=True, slots=True)
class PriceObservation:
    observation_id: str
    asset: AssetId
    base_unit: BaseUnit
    raw_base_per_whole_token: str
    economic_class: EconomicPriceClass
    evidence: EvidenceRef
    effective_at_s: int
    available_at_s: int
    block_ref: BlockRef | None
    source_config_id: str
    adapter_id: str | None
    native_round: RoundMetadata
    upstream_round: RoundMetadata
    heartbeat_s: int | None

    def __post_init__(self) -> None:
        _identifier(self.observation_id, "observation_id")
        if type(self.asset) is not AssetId or type(self.base_unit) is not BaseUnit:
            raise TypeContractError("price asset and base unit must be typed")
        object.__setattr__(
            self,
            "raw_base_per_whole_token",
            _uint_string(self.raw_base_per_whole_token, "raw_base_per_whole_token", positive=True),
        )
        if type(self.economic_class) is not EconomicPriceClass or type(self.evidence) is not EvidenceRef:
            raise TypeContractError("price class and evidence must be typed")
        _uint(self.effective_at_s, "effective_at_s")
        _uint(self.available_at_s, "available_at_s")
        if self.available_at_s < self.effective_at_s:
            raise TypeContractError("price availability cannot precede effective time")
        if self.block_ref is not None and type(self.block_ref) is not BlockRef:
            raise TypeContractError("block_ref must be BlockRef or None")
        if self.block_ref is not None and self.block_ref.chain_id != self.asset.chain_id:
            raise IdentityContractError("price asset and block must share chain identity")
        _identifier(self.source_config_id, "source_config_id")
        if self.adapter_id is not None:
            _identifier(self.adapter_id, "adapter_id")
        if type(self.native_round) is not RoundMetadata or type(self.upstream_round) is not RoundMetadata:
            raise TypeContractError("round metadata must be typed")
        if self.heartbeat_s is not None:
            _uint(self.heartbeat_s, "heartbeat_s")
            if self.heartbeat_s == 0:
                raise TypeContractError("heartbeat_s must be positive when specified")

    @property
    def raw_price(self) -> int:
        return int(self.raw_base_per_whole_token)

    def to_canonical(self) -> object:
        return {
            "adapter_id": self.adapter_id,
            "asset": self.asset,
            "available_at_s": normalize_integer_string(self.available_at_s, signed=False),
            "base_unit": self.base_unit,
            "block_ref": self.block_ref,
            "economic_class": self.economic_class,
            "effective_at_s": normalize_integer_string(self.effective_at_s, signed=False),
            "evidence": self.evidence,
            "heartbeat_s": (
                None if self.heartbeat_s is None else normalize_integer_string(self.heartbeat_s, signed=False)
            ),
            "native_round": self.native_round,
            "observation_id": self.observation_id,
            "raw_base_per_whole_token": self.raw_base_per_whole_token,
            "source_config_id": self.source_config_id,
            "upstream_round": self.upstream_round,
        }


PriceState = PriceObservation | Missing | Unsupported | Quarantined


@dataclass(frozen=True, slots=True)
class PriceSlot:
    asset: AssetId
    state: PriceState

    def __post_init__(self) -> None:
        if type(self.asset) is not AssetId:
            raise TypeContractError("price slot asset must be AssetId")
        if not isinstance(self.state, (PriceObservation, Missing, Unsupported, Quarantined)):
            raise TypeContractError("price slot state must be a typed price or absence state")
        if isinstance(self.state, PriceObservation) and _asset_unit_key(self.state.asset) != _asset_unit_key(
            self.asset
        ):
            raise IdentityContractError("price slot and observation assets differ")

    def to_canonical(self) -> object:
        return {"asset": self.asset, "state": self.state}


@dataclass(frozen=True, slots=True)
class PriceSet:
    price_set_id: str
    checkpoint_id: str
    base_unit: BaseUnit
    slots: tuple[PriceSlot, ...]
    policy_id: str
    profile_version: str

    def __post_init__(self) -> None:
        _identifier(self.price_set_id, "price_set_id")
        _identifier(self.checkpoint_id, "checkpoint_id")
        _identifier(self.policy_id, "policy_id")
        _identifier(self.profile_version, "profile_version")
        if type(self.base_unit) is not BaseUnit or type(self.slots) is not tuple or not self.slots:
            raise TypeContractError("price set requires a base unit and immutable nonempty slots")
        if any(type(slot) is not PriceSlot for slot in self.slots):
            raise TypeContractError("price set slots must be PriceSlot values")
        identities = tuple(slot.asset.identity_key for slot in self.slots)
        if len(identities) != len(set(identities)):
            raise IdentityContractError("price set contains duplicate assets")
        if len({slot.asset.chain_id for slot in self.slots}) != 1:
            raise IdentityContractError("price set cannot join assets from different chains")
        available = tuple(slot.state for slot in self.slots if isinstance(slot.state, PriceObservation))
        if any(item.base_unit != self.base_unit for item in available):
            raise TypeContractError("all price observations must use the price-set base unit")
        observation_ids = tuple(item.observation_id for item in available)
        if len(observation_ids) != len(set(observation_ids)):
            raise IdentityContractError("price set contains duplicate observation identities")
        block_keys = {item.block_ref.identity_key for item in available if item.block_ref is not None}
        if len(block_keys) > 1:
            raise IdentityContractError("price set cannot join different block identities")
        block_timestamps = {item.block_ref.timestamp_s for item in available if item.block_ref is not None}
        if len(block_timestamps) > 1:
            raise IdentityContractError("price set cannot join conflicting timestamps for one block identity")
        if block_keys and any(item.block_ref is None for item in available):
            raise IdentityContractError("price set cannot mix block-bound and unbound observations")

    @property
    def content_hash(self) -> DeterministicContentSha256:
        return DeterministicContentSha256.from_payload(self)

    def to_canonical(self) -> object:
        return {
            "base_unit": self.base_unit,
            "checkpoint_id": self.checkpoint_id,
            "policy_id": self.policy_id,
            "price_set_id": self.price_set_id,
            "profile_version": self.profile_version,
            "slots": self.slots,
        }


@dataclass(frozen=True, slots=True)
class ReservePosition:
    asset: AssetId
    supplied: UnsignedAmount
    stable_debt: UnsignedAmount
    variable_debt: UnsignedAmount
    collateral_enabled: bool
    effective_lt_bps: int
    ltv_bps: int
    liquidation_bonus_bps: int

    def __post_init__(self) -> None:
        if type(self.asset) is not AssetId:
            raise TypeContractError("reserve asset must be AssetId")
        amounts = (self.supplied, self.stable_debt, self.variable_debt)
        if any(type(amount) is not UnsignedAmount for amount in amounts):
            raise TypeContractError("reserve quantities must be UnsignedAmount values")
        if any(_asset_unit_key(amount.asset) != _asset_unit_key(self.asset) for amount in amounts):
            raise IdentityContractError("reserve quantity asset mismatch")
        if self.supplied.kind not in (QuantityKind.BALANCE, QuantityKind.COLLATERAL):
            raise TypeContractError("supplied quantity has the wrong semantic kind")
        if self.stable_debt.kind is not QuantityKind.DEBT or self.variable_debt.kind is not QuantityKind.DEBT:
            raise TypeContractError("debt quantities must use the DEBT kind")
        if type(self.collateral_enabled) is not bool:
            raise TypeContractError("collateral_enabled must be bool")
        _uint(self.effective_lt_bps, "effective_lt_bps", 10_000)
        _uint(self.ltv_bps, "ltv_bps", 10_000)
        _uint(self.liquidation_bonus_bps, "liquidation_bonus_bps", 65_535)

    def to_canonical(self) -> object:
        return {
            "asset": self.asset,
            "collateral_enabled": ExplicitBool(self.collateral_enabled),
            "effective_lt_bps": normalize_integer_string(self.effective_lt_bps, signed=False),
            "liquidation_bonus_bps": normalize_integer_string(self.liquidation_bonus_bps, signed=False),
            "ltv_bps": normalize_integer_string(self.ltv_bps, signed=False),
            "stable_debt": self.stable_debt,
            "supplied": self.supplied,
            "variable_debt": self.variable_debt,
        }


@dataclass(frozen=True, slots=True)
class SyntheticPortfolio:
    portfolio_id: str
    positions: tuple[ReservePosition, ...]
    fixture_evidence: EvidenceRef

    def __post_init__(self) -> None:
        _identifier(self.portfolio_id, "portfolio_id")
        if type(self.positions) is not tuple or not self.positions:
            raise TypeContractError("portfolio requires immutable nonempty positions")
        if any(type(position) is not ReservePosition for position in self.positions):
            raise TypeContractError("portfolio positions must be ReservePosition values")
        identities = tuple(position.asset.identity_key for position in self.positions)
        if len(identities) != len(set(identities)):
            raise IdentityContractError("portfolio contains duplicate reserve assets")
        if len({position.asset.chain_id for position in self.positions}) != 1:
            raise IdentityContractError("portfolio cannot join assets from different chains")
        if type(self.fixture_evidence) is not EvidenceRef:
            raise TypeContractError("portfolio fixture evidence must be typed")

    @property
    def content_hash(self) -> DeterministicContentSha256:
        return DeterministicContentSha256.from_payload(self)

    def to_canonical(self) -> object:
        return {
            "fixture_evidence": self.fixture_evidence,
            "portfolio_id": self.portfolio_id,
            "positions": self.positions,
        }


@dataclass(frozen=True, slots=True)
class ValuationContext:
    context_id: str
    checkpoint_id: str
    as_of_s: int
    purpose: ValuationPurpose
    profile: ValuationProfile
    profile_version: str
    policy_id: str
    assumptions: tuple[str, ...]

    def __post_init__(self) -> None:
        for field in ("context_id", "checkpoint_id", "profile_version", "policy_id"):
            _identifier(getattr(self, field), field)
        _uint(self.as_of_s, "as_of_s")
        if type(self.purpose) is not ValuationPurpose or type(self.profile) is not ValuationProfile:
            raise TypeContractError("valuation purpose and profile must be typed")
        if type(self.assumptions) is not tuple or not self.assumptions:
            raise TypeContractError("valuation context requires immutable explicit assumptions")
        if any(type(value) is not str or not value.strip() for value in self.assumptions):
            raise TypeContractError("valuation assumptions must be nonempty strings")

    @property
    def content_hash(self) -> DeterministicContentSha256:
        return DeterministicContentSha256.from_payload(self)

    def to_canonical(self) -> object:
        return {
            "as_of_s": normalize_integer_string(self.as_of_s, signed=False),
            "assumptions": self.assumptions,
            "checkpoint_id": self.checkpoint_id,
            "context_id": self.context_id,
            "policy_id": self.policy_id,
            "profile": self.profile,
            "profile_version": self.profile_version,
            "purpose": self.purpose,
        }


@dataclass(frozen=True, slots=True)
class ReserveValuation:
    asset: AssetId
    supplied_raw: str
    stable_debt_raw: str
    variable_debt_raw: str
    price_raw: str
    collateral_base_raw: str
    debt_base_raw: str
    effective_lt_bps: int

    def __post_init__(self) -> None:
        if type(self.asset) is not AssetId:
            raise TypeContractError("reserve valuation asset must be AssetId")
        for field in (
            "supplied_raw",
            "stable_debt_raw",
            "variable_debt_raw",
            "price_raw",
            "collateral_base_raw",
            "debt_base_raw",
        ):
            object.__setattr__(self, field, _uint_string(getattr(self, field), field))
        _uint(self.effective_lt_bps, "effective_lt_bps", 10_000)

    def to_canonical(self) -> object:
        return {
            "asset": self.asset,
            "collateral_base_raw": self.collateral_base_raw,
            "debt_base_raw": self.debt_base_raw,
            "effective_lt_bps": normalize_integer_string(self.effective_lt_bps, signed=False),
            "price_raw": self.price_raw,
            "stable_debt_raw": self.stable_debt_raw,
            "supplied_raw": self.supplied_raw,
            "variable_debt_raw": self.variable_debt_raw,
        }


@dataclass(frozen=True, slots=True)
class ValuationResult:
    portfolio_id: str
    context_hash: DeterministicContentSha256
    portfolio_hash: DeterministicContentSha256
    price_set_hash: DeterministicContentSha256
    reserves: tuple[ReserveValuation, ...]
    total_collateral_base_raw: str
    total_debt_base_raw: str
    weighted_lt_numerator_raw: str
    debt_denominator_raw: str
    health_factor_status: HealthFactorStatus
    health_factor_wad: str | None
    below_one: ExplicitBool | None
    rounding_profile: str
    origin: OriginKind

    def __post_init__(self) -> None:
        _identifier(self.portfolio_id, "portfolio_id")
        for value in (self.context_hash, self.portfolio_hash, self.price_set_hash):
            if type(value) is not DeterministicContentSha256:
                raise TypeContractError("valuation parent hashes must use deterministic-content domain")
        if type(self.reserves) is not tuple or any(type(value) is not ReserveValuation for value in self.reserves):
            raise TypeContractError("valuation reserves must be an immutable typed tuple")
        for field in (
            "total_collateral_base_raw",
            "total_debt_base_raw",
            "weighted_lt_numerator_raw",
            "debt_denominator_raw",
        ):
            object.__setattr__(self, field, _uint_string(getattr(self, field), field))
        if type(self.health_factor_status) is not HealthFactorStatus:
            raise TypeContractError("health factor status must be typed")
        if self.health_factor_status is HealthFactorStatus.NO_DEBT:
            if self.health_factor_wad is not None or self.below_one is not None or self.total_debt_base_raw != "0":
                raise TypeContractError("NO_DEBT cannot carry a finite health factor or eligibility")
        else:
            if self.health_factor_wad is None or type(self.below_one) is not ExplicitBool:
                raise TypeContractError("finite health factor requires WAD and typed eligibility")
            object.__setattr__(self, "health_factor_wad", _uint_string(self.health_factor_wad, "health_factor_wad"))
            if self.total_debt_base_raw == "0":
                raise TypeContractError("finite health factor requires positive debt")
        _identifier(self.rounding_profile, "rounding_profile")
        if type(self.origin) is not OriginKind or self.origin not in (
            OriginKind.SYNTHETIC,
            OriginKind.COUNTERFACTUAL,
        ):
            raise TypeContractError("P02-03-S valuation origin must remain SYNTHETIC or COUNTERFACTUAL")

    def to_canonical(self) -> object:
        return {
            "below_one": self.below_one,
            "context_hash": self.context_hash,
            "debt_denominator_raw": self.debt_denominator_raw,
            "health_factor_status": self.health_factor_status,
            "health_factor_wad": self.health_factor_wad,
            "origin": self.origin,
            "portfolio_hash": self.portfolio_hash,
            "portfolio_id": self.portfolio_id,
            "price_set_hash": self.price_set_hash,
            "reserves": self.reserves,
            "rounding_profile": self.rounding_profile,
            "total_collateral_base_raw": self.total_collateral_base_raw,
            "total_debt_base_raw": self.total_debt_base_raw,
            "weighted_lt_numerator_raw": self.weighted_lt_numerator_raw,
        }
