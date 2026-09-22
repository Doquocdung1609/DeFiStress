from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SnapshotCreate(BaseModel):
    mode: Literal["FIXTURE", "REAL_MAINNET", "CACHED_MAINNET"] = "FIXTURE"
    block_number: int | None = Field(default=None, ge=0)
    candidate_users: list[str] | None = Field(default=None, max_length=5_000)
    cached_snapshot_id: str | None = None


class ScenarioCreate(BaseModel):
    snapshot_id: str = "fixture-main-v1"
    name: str = Field(default="Professor Demo", min_length=1, max_length=100)
    shock_pct: Decimal = Field(default=Decimal("-20"), ge=-50, le=0)
    liquidity_haircut_pct: Decimal = Field(default=Decimal("40"), ge=0, le=95)
    gas_multiplier: Decimal = Field(default=Decimal("2"), gt=0, le=20)
    liquidator_capital_usdc: Decimal = Field(default=Decimal("10000000"), gt=0)
    liquidator_capacity_usdc: Decimal = Field(default=Decimal("2500000"), gt=0)
    liquidator_delay_steps: int = Field(default=0, ge=0, le=100)
    liquidator_min_profit_usdc: Decimal = Field(default=Decimal("0"), ge=0)
    arbitrage_capacity_pct: Decimal = Field(default=Decimal("50"), ge=0, le=100)
    arbitrage_delay_steps: int = Field(default=0, ge=0, le=100)
    horizon_steps: int = Field(default=12, ge=1, le=1000)
    timestep_seconds: int = Field(default=60, ge=1, le=86_400)
    monte_carlo_runs: int = Field(default=100, ge=1, le=10_000)
    seed: int = 20260914
    volatility_pct: Decimal = Field(default=Decimal("2"), ge=0, le=100)
    liquidation_bonus: Decimal = Field(default=Decimal("1.05"), ge=1, le=2)
    ltv_override: Decimal | None = Field(default=None, ge=0, le=1)
    liquidation_threshold_override: Decimal | None = Field(default=None, gt=0, le=1)
    liquidation_bonus_override: Decimal | None = Field(default=None, ge=1, le=2)
    max_waves: int = Field(default=12, ge=1, le=100)

    @field_validator("snapshot_id")
    @classmethod
    def nonempty_snapshot(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("snapshot_id is required")
        return value


class RunCreate(BaseModel):
    scenario_id: str
    mode: Literal["DETERMINISTIC", "MONTE_CARLO"] = "DETERMINISTIC"


class CompareRuns(BaseModel):
    run_ids: list[str] = Field(min_length=2, max_length=4)


class CascadeThresholdRequest(BaseModel):
    scenario_id: str


class ForkValidationRequest(BaseModel):
    snapshot_id: str | None = None
    borrower_hash: str | None = None
