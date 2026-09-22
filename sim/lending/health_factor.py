from collections.abc import Iterable
from decimal import Decimal


def health_factor(
    collateral: Iterable[tuple[Decimal, Decimal, Decimal]],
    debt: Iterable[tuple[Decimal, Decimal]],
) -> Decimal:
    """Calculate Aave-style HF from (amount, price, LT) and (amount, price) tuples."""
    adjusted_collateral = sum((amount * price * threshold for amount, price, threshold in collateral), Decimal(0))
    debt_value = sum((amount * price for amount, price in debt), Decimal(0))
    if debt_value <= 0:
        return Decimal("Infinity")
    return max(Decimal(0), adjusted_collateral / debt_value)


def distance_to_liquidation(hf: Decimal) -> Decimal:
    if not hf.is_finite():
        return Decimal("Infinity")
    return hf - Decimal(1)
