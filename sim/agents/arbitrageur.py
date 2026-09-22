from dataclasses import dataclass
from decimal import Decimal

from sim.dex.uniswap_v3 import V3Pool


@dataclass(frozen=True, slots=True)
class Arbitrageur:
    capacity_pct: Decimal
    minimum_spread_pct: Decimal = Decimal("0.05")

    def act(self, pool: V3Pool, reference_price: Decimal) -> tuple[Decimal, Decimal] | None:
        if reference_price <= 0:
            return None
        spread_pct = abs(pool.spot_price - reference_price) / reference_price * Decimal(100)
        if spread_pct < self.minimum_spread_pct or self.capacity_pct <= 0:
            return None
        return pool.arbitrage_toward(reference_price, self.capacity_pct)
