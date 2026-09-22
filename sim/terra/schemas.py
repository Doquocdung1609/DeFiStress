from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

D = Decimal


class DataStatus(StrEnum):
    REAL_HISTORICAL = "REAL_HISTORICAL"
    FIXTURE = "FIXTURE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    QUALITY_WARNING = "QUALITY_WARNING"


class ExperimentMode(StrEnum):
    IN_SAMPLE_REPLAY = "IN_SAMPLE_REPLAY"
    OUT_OF_SAMPLE_REPLAY = "OUT_OF_SAMPLE_REPLAY"
    COUNTERFACTUAL_STRESS = "COUNTERFACTUAL_STRESS"


def parse_utc(value: str | datetime) -> datetime:
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include an explicit UTC offset")
    return parsed.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class SourceProvenance:
    source_name: str
    source_type: str
    chain_id: str
    retrieved_at: datetime
    dataset_version: str
    raw_reference: str
    quality_flag: str
    block_height: int | None = None
    block_hash: str | None = None
    tx_hash: str | None = None
    contract_address: str | None = None
    event_name: str | None = None


@dataclass(frozen=True, slots=True)
class TerraObservation:
    timestamp: datetime
    block_height: int
    ust_price: Decimal
    luna_price: Decimal
    ust_supply: Decimal
    luna_supply: Decimal
    anchor_total_deposits: Decimal
    anchor_deposit_flow: Decimal
    anchor_withdrawal_flow: Decimal
    ust_native_redemption_volume: Decimal
    luna_minted_from_redemption: Decimal
    luna_burned: Decimal
    ust_dex_sell_volume: Decimal
    terra_dex_liquidity: Decimal
    terra_dex_depth: Decimal
    top10_anchor_share: Decimal
    top100_anchor_share: Decimal
    curve_ust_liquidity: Decimal | None = None
    curve_pool_imbalance: Decimal | None = None
    curve_ust_price: Decimal | None = None
    bridge_outflow_terra_to_ethereum: Decimal | None = None
    bridge_inflow_ethereum_to_terra: Decimal | None = None
    btc_reserve_value: Decimal | None = None
    reserve_intervention_volume: Decimal | None = None
    source_name: str = "UNAVAILABLE"
    source_type: str = "UNAVAILABLE"
    chain_id: str = "columbus-5"
    block_hash: str | None = None
    raw_reference: str = ""
    quality_flag: str = "UNAVAILABLE"

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        nonnegative = (
            self.ust_price,
            self.luna_price,
            self.ust_supply,
            self.luna_supply,
            self.anchor_total_deposits,
            self.anchor_deposit_flow,
            self.anchor_withdrawal_flow,
            self.ust_native_redemption_volume,
            self.luna_minted_from_redemption,
            self.luna_burned,
            self.ust_dex_sell_volume,
            self.terra_dex_liquidity,
            self.terra_dex_depth,
        )
        if any(value < 0 for value in nonnegative):
            raise ValueError("prices, supplies, flows, and liquidity cannot be negative")
        if not D("0") <= self.top10_anchor_share <= D("1"):
            raise ValueError("top10_anchor_share must be between 0 and 1")
        if not D("0") <= self.top100_anchor_share <= D("1"):
            raise ValueError("top100_anchor_share must be between 0 and 1")

    @property
    def ust_market_cap(self) -> Decimal:
        return self.ust_supply * self.ust_price

    @property
    def luna_market_cap(self) -> Decimal:
        return self.luna_supply * self.luna_price

    @property
    def anchor_net_flow(self) -> Decimal:
        return self.anchor_deposit_flow - self.anchor_withdrawal_flow

    @property
    def ust_depeg_bps(self) -> Decimal:
        return max(D("0"), (D("1") - self.ust_price) * D("10000"))

    @property
    def backing_ratio(self) -> Decimal:
        return D("0") if self.ust_supply <= 0 else self.luna_market_cap / self.ust_supply

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["timestamp"] = self.timestamp.isoformat().replace("+00:00", "Z")
        for key, value in list(row.items()):
            if isinstance(value, Decimal):
                row[key] = float(value)
        row.update(
            {
                "ust_market_cap": float(self.ust_market_cap),
                "luna_market_cap": float(self.luna_market_cap),
                "anchor_net_flow": float(self.anchor_net_flow),
                "ust_depeg_bps": float(self.ust_depeg_bps),
                "backing_ratio": float(self.backing_ratio),
            }
        )
        return row

    @classmethod
    def from_mapping(cls, row: dict[str, Any]) -> TerraObservation:
        field_names = set(cls.__dataclass_fields__)
        decimal_fields = {
            item.name
            for item in cls.__dataclass_fields__.values()
            if item.name
            not in {
                "timestamp",
                "block_height",
                "source_name",
                "source_type",
                "chain_id",
                "block_hash",
                "raw_reference",
                "quality_flag",
            }
        }
        values = {key: value for key, value in row.items() if key in field_names}
        values["timestamp"] = parse_utc(values["timestamp"])
        values["block_height"] = int(values["block_height"])
        for name in decimal_fields:
            if name in values and values[name] not in {None, ""}:
                values[name] = D(str(values[name]))
            elif name in values:
                values[name] = None
        return cls(**values)


@dataclass(frozen=True, slots=True)
class WalletCohort:
    wallet_id_hash: str
    cohort: str
    ust_balance: Decimal
    anchor_balance: Decimal
    recent_withdrawal: Decimal
    historical_activity: Decimal
    sophistication_score: Decimal
    last_action_timestamp: datetime


@dataclass(frozen=True, slots=True)
class ModelInputState:
    timestamp: datetime
    ust_price: Decimal
    luna_price: Decimal
    ust_supply: Decimal
    luna_supply: Decimal
    anchor_total_deposits: Decimal
    terra_dex_liquidity: Decimal
    terra_dex_depth: Decimal
    backing_ratio: Decimal
    top10_anchor_share: Decimal
    realized_volatility: Decimal

    @classmethod
    def from_observation(cls, row: TerraObservation, realized_volatility: Decimal | None = None) -> ModelInputState:
        return cls(
            row.timestamp,
            row.ust_price,
            row.luna_price,
            row.ust_supply,
            row.luna_supply,
            row.anchor_total_deposits,
            row.terra_dex_liquidity,
            row.terra_dex_depth,
            row.backing_ratio,
            row.top10_anchor_share,
            realized_volatility or D("0"),
        )


@dataclass(slots=True)
class SimulationState:
    timestamp: datetime
    ust_price: Decimal
    luna_price: Decimal
    ust_supply: Decimal
    luna_supply: Decimal
    anchor_total_deposits: Decimal
    anchor_withdrawal_flow: Decimal
    redemption_volume: Decimal
    terra_dex_liquidity: Decimal
    backing_ratio: Decimal
    risk_score: Decimal
    collapse_signal: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "ust_price": float(self.ust_price),
            "luna_price": float(self.luna_price),
            "ust_supply": float(self.ust_supply),
            "luna_supply": float(self.luna_supply),
            "anchor_total_deposits": float(self.anchor_total_deposits),
            "anchor_withdrawal_flow": float(self.anchor_withdrawal_flow),
            "redemption_volume": float(self.redemption_volume),
            "terra_dex_liquidity": float(self.terra_dex_liquidity),
            "backing_ratio": float(self.backing_ratio),
            "risk_score": float(self.risk_score),
            "collapse_signal": self.collapse_signal,
        }


@dataclass(frozen=True, slots=True)
class AgentEvent:
    timestamp: datetime
    agent: str
    cohort: str
    action: str
    amount: Decimal
    explanation: dict[str, Decimal] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "agent": self.agent,
            "cohort": self.cohort,
            "action": self.action,
            "amount": float(self.amount),
            "explanation": {key: float(value) for key, value in self.explanation.items()},
        }


@dataclass(frozen=True, slots=True)
class ValidationResult:
    model_name: str
    metrics: dict[str, float | int | bool | None]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ModelRun:
    model_name: str
    model_version: str
    states: tuple[SimulationState, ...]
    events: tuple[AgentEvent, ...]
    model_status: str
    parameters: dict[str, Any]
    diagnostics: dict[str, Any] = field(default_factory=dict)
