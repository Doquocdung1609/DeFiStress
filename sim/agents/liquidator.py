from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sim.dex.uniswap_v3 import SwapQuote, V3Pool
from sim.lending.liquidation import LiquidationPlan

D = Decimal


@dataclass(frozen=True, slots=True)
class LiquidatorDecision:
    execute: bool
    expected_profit: Decimal
    gas_cost: Decimal
    funding_cost: Decimal
    risk_buffer: Decimal
    quote: SwapQuote
    reason: str


@dataclass(slots=True)
class Liquidator:
    capital_limit: Decimal
    capacity_per_step: Decimal
    minimum_profit: Decimal
    gas_multiplier: Decimal
    base_gas_cost: Decimal = D("8")
    funding_rate: Decimal = D("0.0005")
    execution_risk_rate: Decimal = D("0.0005")

    def evaluate(self, plan: LiquidationPlan, pool: V3Pool) -> LiquidatorDecision:
        quote = pool.quote_sell_weth(plan.collateral_to_seize)
        gas = self.base_gas_cost * self.gas_multiplier
        funding = plan.debt_to_repay * self.funding_rate
        risk = plan.debt_to_repay * self.execution_risk_rate
        profit = quote.amount_usdc_out - plan.debt_to_repay - gas - funding - risk
        within_capacity = plan.debt_to_repay <= min(self.capital_limit, self.capacity_per_step)
        execute = plan.eligible and within_capacity and profit > self.minimum_profit
        if not plan.eligible:
            reason = "NOT_ELIGIBLE"
        elif not within_capacity:
            reason = "CAPACITY_EXCEEDED"
        elif profit <= self.minimum_profit:
            reason = "UNPROFITABLE"
        else:
            reason = "EXECUTE"
        return LiquidatorDecision(execute, profit, gas, funding, risk, quote, reason)
