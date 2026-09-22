from decimal import Decimal

from sim.agents import Arbitrageur, Liquidator
from sim.dex import V3Pool
from sim.fixtures import fixture_dex
from sim.lending import plan_liquidation
from sim.schemas import BorrowerPosition

D = Decimal


def test_liquidator_profit_equation_and_capital_gate() -> None:
    position = BorrowerPosition("borrower-test", D("1"), D("3000"), D("0.8"))
    pool = V3Pool(fixture_dex())
    plan = plan_liquidation(position, D("2000"), D("1.05"))
    liquidator = Liquidator(D("100000"), D("100000"), D("0"), D("2"))
    decision = liquidator.evaluate(plan, pool)
    expected = (
        decision.quote.amount_usdc_out
        - plan.debt_to_repay
        - decision.gas_cost
        - decision.funding_cost
        - decision.risk_buffer
    )
    assert decision.expected_profit == expected
    assert decision.execute

    constrained = Liquidator(D("10"), D("100000"), D("0"), D("2")).evaluate(plan, pool)
    assert not constrained.execute
    assert constrained.reason == "CAPACITY_EXCEEDED"


def test_arbitrage_capacity_closes_configured_spread_fraction() -> None:
    pool = V3Pool(fixture_dex())
    reference = pool.spot_price
    pool.sell_weth(D("20"))
    before_gap = reference - pool.spot_price
    action = Arbitrageur(D("50")).act(pool, reference)
    assert action is not None
    after_gap = reference - pool.spot_price
    assert abs(after_gap / before_gap - D("0.5")) < D("1e-20")
