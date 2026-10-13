from collections.abc import Iterable
from decimal import Decimal

from sim.schemas import BorrowerPosition

ONE = Decimal(1)


def bad_debt(
    positions: Iterable[BorrowerPosition],
    weth_price: Decimal,
    usdc_price_usd: Decimal = ONE,
) -> Decimal:
    total = Decimal(0)
    for position in positions:
        total += max(Decimal(0), position.debt_value(usdc_price_usd) - position.collateral_value(weth_price))
    return total


def unliquidated_debt(
    positions: Iterable[BorrowerPosition],
    weth_price: Decimal,
    usdc_price_usd: Decimal = ONE,
    lt_override: Decimal | None = None,
) -> Decimal:
    return sum(
        (
            position.debt_value(usdc_price_usd)
            for position in positions
            if position.health_factor(weth_price, lt_override, usdc_price_usd) < 1
        ),
        Decimal(0),
    )


def cascade_amplification(total_liquidated: Decimal, direct_liquidated: Decimal) -> Decimal | None:
    if direct_liquidated <= 0:
        return None
    return total_liquidated / direct_liquidated
