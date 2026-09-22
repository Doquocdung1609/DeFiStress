from collections.abc import Iterable
from decimal import Decimal

from sim.schemas import BorrowerPosition


def bad_debt(positions: Iterable[BorrowerPosition], weth_price: Decimal) -> Decimal:
    total = Decimal(0)
    for position in positions:
        total += max(Decimal(0), position.debt_value() - position.collateral_value(weth_price))
    return total


def unliquidated_debt(positions: Iterable[BorrowerPosition], weth_price: Decimal) -> Decimal:
    return sum(
        (position.debt_value() for position in positions if position.health_factor(weth_price) < 1),
        Decimal(0),
    )


def cascade_amplification(total_liquidated: Decimal, direct_liquidated: Decimal) -> Decimal | None:
    if direct_liquidated <= 0:
        return None
    return total_liquidated / direct_liquidated
