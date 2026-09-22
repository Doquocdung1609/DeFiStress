from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sim.schemas import BorrowerPosition

D = Decimal
DEFAULT_CLOSE_FACTOR = D("0.50")
MAX_CLOSE_FACTOR = D("1")
CLOSE_FACTOR_HF_THRESHOLD = D("0.95")
MIN_BASE_MAX_CLOSE_FACTOR = D("2000")
MIN_LEFTOVER_BASE = D("1000")


@dataclass(frozen=True, slots=True)
class LiquidationPlan:
    eligible: bool
    close_factor: Decimal
    debt_to_repay: Decimal
    collateral_to_seize: Decimal
    reason: str


def close_factor(health_factor: Decimal, debt_value: Decimal, collateral_value: Decimal) -> Decimal:
    if health_factor >= 1:
        return D("0")
    if (
        health_factor <= CLOSE_FACTOR_HF_THRESHOLD
        or debt_value < MIN_BASE_MAX_CLOSE_FACTOR
        or collateral_value < MIN_BASE_MAX_CLOSE_FACTOR
    ):
        return MAX_CLOSE_FACTOR
    return DEFAULT_CLOSE_FACTOR


def plan_liquidation(
    position: BorrowerPosition,
    weth_price: Decimal,
    liquidation_bonus: Decimal,
    lt_override: Decimal | None = None,
) -> LiquidationPlan:
    hf = position.health_factor(weth_price, lt_override)
    if hf >= 1 or position.debt_usdc <= 0 or position.collateral_weth <= 0:
        return LiquidationPlan(False, D("0"), D("0"), D("0"), "NOT_ELIGIBLE")

    factor = close_factor(hf, position.debt_value(), position.collateral_value(weth_price))
    repay = position.debt_usdc * factor
    seize = repay * liquidation_bonus / weth_price

    if seize > position.collateral_weth:
        seize = position.collateral_weth
        repay = seize * weth_price / liquidation_bonus

    debt_left = position.debt_usdc - repay
    collateral_left_value = (position.collateral_weth - seize) * weth_price
    if D("0") < debt_left < MIN_LEFTOVER_BASE:
        repay = position.debt_usdc
        seize = min(position.collateral_weth, repay * liquidation_bonus / weth_price)
    elif D("0") < collateral_left_value < MIN_LEFTOVER_BASE:
        seize = position.collateral_weth
        repay = min(position.debt_usdc, seize * weth_price / liquidation_bonus)

    return LiquidationPlan(True, factor, max(D("0"), repay), max(D("0"), seize), "ELIGIBLE")
