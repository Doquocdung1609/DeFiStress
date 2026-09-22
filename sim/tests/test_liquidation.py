from decimal import Decimal

from sim.lending.liquidation import close_factor, plan_liquidation
from sim.schemas import BorrowerPosition

D = Decimal


def position() -> BorrowerPosition:
    return BorrowerPosition("borrower-test", D("1"), D("3000"), D("0.8"))


def test_close_factor_is_half_near_boundary() -> None:
    assert close_factor(D("0.97"), D("3000"), D("3500")) == D("0.5")


def test_close_factor_is_full_below_threshold() -> None:
    assert close_factor(D("0.95"), D("3000"), D("3500")) == D("1")


def test_liquidation_never_seizes_more_than_collateral() -> None:
    plan = plan_liquidation(position(), D("2000"), D("1.05"))
    assert plan.eligible
    assert plan.collateral_to_seize <= position().collateral_weth
    assert plan.debt_to_repay <= position().debt_usdc
