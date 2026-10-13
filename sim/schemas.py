from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from decimal import Decimal
from typing import Any, cast

D = Decimal
ONE = D(1)


@dataclass(slots=True)
class BorrowerPosition:
    borrower_hash: str
    collateral_weth: Decimal
    debt_usdc: Decimal
    liquidation_threshold: Decimal
    ltv: Decimal = D("0.80")
    other_collateral_usd: Decimal = D("0")
    other_debt_usd: Decimal = D("0")
    status: str = "ACTIVE"

    def collateral_value(self, weth_price: Decimal) -> Decimal:
        return self.collateral_weth * weth_price + self.other_collateral_usd

    def debt_value(self, usdc_price_usd: Decimal = ONE) -> Decimal:
        """Return debt value in USD without repricing non-USDC debt."""
        return self.debt_usdc * usdc_price_usd + self.other_debt_usd

    def health_factor(
        self,
        weth_price: Decimal,
        lt_override: Decimal | None = None,
        usdc_price_usd: Decimal = ONE,
    ) -> Decimal:
        debt = self.debt_value(usdc_price_usd)
        if debt <= 0:
            return D("Infinity")
        threshold = lt_override if lt_override is not None else self.liquidation_threshold
        adjusted = self.collateral_weth * weth_price * threshold
        adjusted += self.other_collateral_usd * self.liquidation_threshold
        return max(D("0"), adjusted / debt)

    def liquidation_price(self, usdc_price_usd: Decimal = ONE) -> Decimal | None:
        if self.collateral_weth <= 0:
            return None
        uncovered = self.debt_value(usdc_price_usd) - self.other_collateral_usd * self.liquidation_threshold
        if uncovered <= 0:
            return D("0")
        return uncovered / (self.collateral_weth * self.liquidation_threshold)


@dataclass(frozen=True, slots=True)
class LiquidityTick:
    tick: int
    liquidity_net: Decimal
    liquidity_gross: Decimal


@dataclass(slots=True)
class DexState:
    pool_address: str
    token0: str
    token1: str
    fee: int
    tick_spacing: int
    sqrt_price_x96: Decimal
    tick: int
    liquidity: Decimal
    ticks: list[LiquidityTick] = field(default_factory=list)
    token0_decimals: int = 6
    token1_decimals: int = 18
    source: str = "FIXTURE"


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str = "Professor Demo"
    shock_pct: Decimal = D("-20")
    liquidity_haircut_pct: Decimal = D("40")
    gas_multiplier: Decimal = D("2")
    liquidator_capital_usdc: Decimal = D("10000000")
    liquidator_capacity_usdc: Decimal = D("2500000")
    liquidator_delay_steps: int = 0
    liquidator_min_profit_usdc: Decimal = D("0")
    arbitrage_capacity_pct: Decimal = D("50")
    arbitrage_delay_steps: int = 0
    horizon_steps: int = 12
    timestep_seconds: int = 60
    monte_carlo_runs: int = 100
    seed: int = 20260914
    volatility_pct: Decimal = D("2")
    liquidation_bonus: Decimal = D("1.05")
    usdc_price_usd: Decimal = D("1")
    ltv_override: Decimal | None = None
    liquidation_threshold_override: Decimal | None = None
    liquidation_bonus_override: Decimal | None = None
    max_waves: int = 12

    def validate(self) -> None:
        if not D("-50") <= self.shock_pct <= D("0"):
            raise ValueError("shock_pct must be between -50 and 0")
        if not D("0") <= self.liquidity_haircut_pct <= D("95"):
            raise ValueError("liquidity_haircut_pct must be between 0 and 95")
        if not D("0") <= self.arbitrage_capacity_pct <= D("100"):
            raise ValueError("arbitrage_capacity_pct must be between 0 and 100")
        if self.gas_multiplier <= 0 or self.liquidator_capital_usdc <= 0 or self.liquidator_capacity_usdc <= 0:
            raise ValueError("gas multiplier and liquidator capital/capacity must be positive")
        if self.usdc_price_usd <= 0:
            raise ValueError("usdc_price_usd must be positive")
        if self.liquidator_delay_steps < 0 or self.arbitrage_delay_steps < 0:
            raise ValueError("agent delays cannot be negative")
        if self.horizon_steps < 1 or self.timestep_seconds < 1:
            raise ValueError("horizon and timestep must be positive")
        if not 1 <= self.monte_carlo_runs <= 10_000:
            raise ValueError("monte_carlo_runs must be between 1 and 10000")
        if not 1 <= self.max_waves <= 100:
            raise ValueError("max_waves must be between 1 and 100")


@dataclass(slots=True)
class SimulationEvent:
    run_id: str
    step: int
    wave: int
    event_type: str
    agent: str
    borrower_hash: str | None = None
    debt_asset: str | None = None
    collateral_asset: str | None = None
    debt_repaid: Decimal = D("0")
    collateral_seized: Decimal = D("0")
    forced_sell_amount: Decimal = D("0")
    gas_cost: Decimal = D("0")
    expected_profit: Decimal = D("0")
    execution_price: Decimal = D("0")
    reference_price: Decimal = D("0")
    slippage: Decimal = D("0")
    dex_price_before: Decimal = D("0")
    dex_price_after: Decimal = D("0")
    health_factor_before: Decimal = D("0")
    health_factor_after: Decimal = D("0")
    timestamp_sim: int = 0
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TimePoint:
    step: int
    wave: int
    reference_price: Decimal
    dex_price: Decimal
    liquidatable_positions: int
    liquidation_volume: Decimal
    forced_weth_sell: Decimal
    bad_debt: Decimal


@dataclass(slots=True)
class SimulationResult:
    run_id: str
    model_version: str
    seed: int
    scenario: Scenario
    metrics: dict[str, Decimal | int | None]
    events: list[SimulationEvent]
    timeseries: list[TimePoint]
    final_positions: list[BorrowerPosition]

    def to_dict(self) -> dict[str, Any]:
        return cast(dict[str, Any], json_safe(asdict(self)))


def json_safe(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return json_safe(asdict(value))
    if isinstance(value, Decimal):
        if not value.is_finite():
            return str(value)
        return float(value)
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value
