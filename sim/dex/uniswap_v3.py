from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, localcontext
from math import log

from sim.schemas import DexState

D = Decimal
Q96 = D(2) ** 96
ONE_MILLION = D(1_000_000)


@dataclass(frozen=True, slots=True)
class SwapQuote:
    amount_weth_in: Decimal
    amount_usdc_out: Decimal
    execution_price: Decimal
    price_before: Decimal
    price_after: Decimal
    slippage: Decimal
    ticks_crossed: int


def sqrt_price_x96_from_weth_price(price: Decimal, token0_decimals: int = 6, token1_decimals: int = 18) -> Decimal:
    if price <= 0:
        raise ValueError("price must be positive")
    scale = D(10) ** (token1_decimals - token0_decimals)
    with localcontext() as ctx:
        ctx.prec = 60
        return (scale / price).sqrt() * Q96


def tick_from_sqrt_price_x96(sqrt_price_x96: Decimal) -> int:
    ratio = float((sqrt_price_x96 / Q96) ** 2)
    return int(log(ratio) / log(1.0001))


def sqrt_price_x96_from_tick(tick: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 60
        return Q96 * (D("1.0001") ** (D(tick) / D(2)))


class V3Pool:
    """Token1-in V3 swap math for a USDC(token0)/WETH(token1) pool.

    The implementation moves square-root price across initialized ticks and adjusts active
    liquidity by liquidityNet. Raw token amounts remain Decimal/integer-scale values.
    """

    def __init__(self, state: DexState):
        self.state = deepcopy(state)

    def clone(self) -> V3Pool:
        return V3Pool(self.state)

    @property
    def spot_price(self) -> Decimal:
        raw_ratio = (self.state.sqrt_price_x96 / Q96) ** 2
        scale = D(10) ** (self.state.token1_decimals - self.state.token0_decimals)
        return scale / raw_ratio

    def apply_liquidity_haircut(self, haircut_pct: Decimal) -> None:
        multiplier = max(D("0.01"), D(1) - haircut_pct / D(100))
        self.state.liquidity *= multiplier
        self.state.ticks = [
            type(tick)(tick.tick, tick.liquidity_net * multiplier, tick.liquidity_gross * multiplier)
            for tick in self.state.ticks
        ]

    def quote_sell_weth(self, amount_weth: Decimal) -> SwapQuote:
        copy = self.clone()
        return copy.sell_weth(amount_weth)

    def sell_weth(self, amount_weth: Decimal) -> SwapQuote:
        if amount_weth < 0:
            raise ValueError("amount_weth cannot be negative")
        before = self.spot_price
        if amount_weth == 0:
            return SwapQuote(D(0), D(0), before, before, before, D(0), 0)
        fee_fraction = D(self.state.fee) / ONE_MILLION
        remaining_net_raw = amount_weth * (D(10) ** self.state.token1_decimals) * (D(1) - fee_fraction)
        amount0_out_raw = D(0)
        crossed = 0

        upper_ticks = sorted((tick for tick in self.state.ticks if tick.tick > self.state.tick), key=lambda x: x.tick)
        for tick in upper_ticks:
            if remaining_net_raw <= 0:
                break
            target = sqrt_price_x96_from_tick(tick.tick)
            if target <= self.state.sqrt_price_x96:
                continue
            required = self.state.liquidity * (target - self.state.sqrt_price_x96) / Q96
            used = min(remaining_net_raw, required)
            new_sqrt = self.state.sqrt_price_x96 + used * Q96 / self.state.liquidity
            amount0_out_raw += (
                self.state.liquidity
                * Q96
                * (new_sqrt - self.state.sqrt_price_x96)
                / (new_sqrt * self.state.sqrt_price_x96)
            )
            self.state.sqrt_price_x96 = new_sqrt
            remaining_net_raw -= used
            if used == required:
                self.state.liquidity += tick.liquidity_net
                if self.state.liquidity <= 0:
                    raise ValueError("tick crossing exhausted active liquidity")
                self.state.tick = tick.tick
                crossed += 1

        if remaining_net_raw > 0:
            new_sqrt = self.state.sqrt_price_x96 + remaining_net_raw * Q96 / self.state.liquidity
            amount0_out_raw += (
                self.state.liquidity
                * Q96
                * (new_sqrt - self.state.sqrt_price_x96)
                / (new_sqrt * self.state.sqrt_price_x96)
            )
            self.state.sqrt_price_x96 = new_sqrt

        self.state.tick = tick_from_sqrt_price_x96(self.state.sqrt_price_x96)
        out = amount0_out_raw / (D(10) ** self.state.token0_decimals)
        after = self.spot_price
        execution = out / amount_weth
        slippage = max(D(0), (before - execution) / before)
        return SwapQuote(amount_weth, out, execution, before, after, slippage, crossed)

    def arbitrage_toward(self, reference_price: Decimal, capacity_pct: Decimal) -> tuple[Decimal, Decimal]:
        before = self.spot_price
        fraction = max(D(0), min(D(1), capacity_pct / D(100)))
        target = before + (reference_price - before) * fraction
        self.state.sqrt_price_x96 = sqrt_price_x96_from_weth_price(
            target, self.state.token0_decimals, self.state.token1_decimals
        )
        self.state.tick = tick_from_sqrt_price_x96(self.state.sqrt_price_x96)
        return before, self.spot_price

    def depth_to_price_drop_usdc(self, drop_pct: Decimal) -> Decimal:
        if not D(0) < drop_pct < D(100):
            raise ValueError("drop_pct must be between 0 and 100")
        target_price = self.spot_price * (D(1) - drop_pct / D(100))
        target_sqrt = sqrt_price_x96_from_weth_price(
            target_price, self.state.token0_decimals, self.state.token1_decimals
        )
        current_sqrt = self.state.sqrt_price_x96
        current_liquidity = self.state.liquidity
        net_raw = D(0)
        upper_ticks = sorted(
            (tick for tick in self.state.ticks if tick.tick > self.state.tick),
            key=lambda item: item.tick,
        )
        for tick in upper_ticks:
            boundary = sqrt_price_x96_from_tick(tick.tick)
            if boundary >= target_sqrt:
                break
            if boundary <= current_sqrt:
                continue
            net_raw += current_liquidity * (boundary - current_sqrt) / Q96
            current_sqrt = boundary
            current_liquidity += tick.liquidity_net
            if current_liquidity <= 0:
                return D(0)
        net_raw += max(D(0), current_liquidity * (target_sqrt - current_sqrt) / Q96)
        fee_fraction = D(self.state.fee) / ONE_MILLION
        weth = net_raw / (D(10) ** self.state.token1_decimals) / (D(1) - fee_fraction)
        return self.quote_sell_weth(weth).amount_usdc_out
