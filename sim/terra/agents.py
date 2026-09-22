from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

D = Decimal


@dataclass(frozen=True, slots=True)
class ArbitrageDecision:
    execute: bool
    expected_profit: Decimal
    amount: Decimal


@dataclass(slots=True)
class ArbitrageurAgent:
    capital: Decimal
    minimum_profit: Decimal
    trading_cost_bps: Decimal = D("12")
    risk_buffer_bps: Decimal = D("25")

    def evaluate(self, ust_price: Decimal, requested_amount: Decimal, slippage_bps: Decimal) -> ArbitrageDecision:
        amount = min(max(D("0"), requested_amount), self.capital / max(ust_price, D("0.0001")))
        purchase_cost = amount * ust_price
        gross_redemption = amount
        costs = purchase_cost * (self.trading_cost_bps + self.risk_buffer_bps + slippage_bps) / D("10000")
        profit = gross_redemption - purchase_cost - costs
        return ArbitrageDecision(profit > self.minimum_profit and amount > 0, profit, amount)


@dataclass(slots=True)
class TerraProtocolAgent:
    ust_supply: Decimal
    luna_supply: Decimal
    redemption_friction: Decimal

    def redeem(self, ust_amount: Decimal, luna_price: Decimal) -> Decimal:
        redeemable = min(max(D("0"), ust_amount), self.ust_supply)
        effective_value = redeemable * max(D("0"), D("1") - self.redemption_friction)
        minted_luna = effective_value / max(luna_price, D("0.0000001"))
        self.ust_supply = max(D("0"), self.ust_supply - redeemable)
        self.luna_supply = max(D("0"), self.luna_supply + minted_luna)
        return minted_luna


@dataclass(slots=True)
class ReserveDefenderAgent:
    capital: Decimal
    threshold: Decimal
    efficiency: Decimal

    def intervene(self, ust_price: Decimal, requested: Decimal) -> Decimal:
        if ust_price >= self.threshold or self.capital <= 0:
            return D("0")
        spent = min(self.capital, max(D("0"), requested))
        self.capital -= spent
        return spent * min(D("1"), max(D("0"), self.efficiency))


def depositor_exit_probability(
    depeg: Decimal,
    backing_stress: Decimal,
    large_holder_flow: Decimal,
    liquidity_stress: Decimal,
    confidence_sensitivity: Decimal,
    cohort_baseline: Decimal,
) -> tuple[Decimal, dict[str, Decimal]]:
    explanation = {
        "ust_depeg": depeg * D("0.32"),
        "large_holder_activity": large_holder_flow * D("0.18"),
        "backing_deterioration": backing_stress * D("0.22"),
        "liquidity_stress": liquidity_stress * D("0.16"),
        "cohort_baseline": cohort_baseline,
    }
    probability = sum(explanation.values(), D("0")) * confidence_sensitivity
    return min(D("0.98"), max(D("0"), probability)), explanation
