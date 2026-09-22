from decimal import Decimal

from sim.lending.health_factor import health_factor

D = Decimal


def test_health_factor_uses_weighted_collateral() -> None:
    hf = health_factor([(D("2"), D("3000"), D("0.8")), (D("1000"), D("1"), D("0.9"))], [(D("4000"), D("1"))])
    assert hf == D("1.425")


def test_no_debt_is_infinite() -> None:
    assert health_factor([(D("1"), D("1"), D("0.8"))], []).is_infinite()
