from decimal import Decimal

from sim.dex import V3Pool
from sim.dex.uniswap_v3 import sqrt_price_x96_from_weth_price, tick_from_sqrt_price_x96
from sim.fixtures import fixture_dex

D = Decimal


def test_zero_trade_has_zero_impact() -> None:
    pool = V3Pool(fixture_dex())
    quote = pool.sell_weth(D("0"))
    assert quote.price_before == quote.price_after
    assert quote.slippage == 0


def test_weth_sale_reduces_weth_usdc_price() -> None:
    pool = V3Pool(fixture_dex())
    quote = pool.sell_weth(D("10"))
    assert quote.amount_usdc_out > 0
    assert quote.price_after < quote.price_before
    assert quote.execution_price < quote.price_before


def test_larger_sell_does_not_improve_execution_price() -> None:
    pool = V3Pool(fixture_dex())
    small = pool.quote_sell_weth(D("5"))
    large = pool.quote_sell_weth(D("50"))
    assert large.execution_price <= small.execution_price


def test_tick_crossing_updates_liquidity_without_nan() -> None:
    quote = V3Pool(fixture_dex()).sell_weth(D("100"))
    assert quote.price_after.is_finite()
    assert quote.amount_usdc_out.is_finite()


def test_arbitrage_reposition_updates_active_liquidity_across_ticks() -> None:
    pool = V3Pool(fixture_dex())
    initial_tick = pool.state.tick
    initial_liquidity = pool.state.liquidity
    target_price = pool.spot_price * D("0.90")
    target_tick = tick_from_sqrt_price_x96(sqrt_price_x96_from_weth_price(target_price))
    expected = initial_liquidity + sum(
        (tick.liquidity_net for tick in pool.state.ticks if initial_tick < tick.tick <= target_tick),
        D(0),
    )

    pool.arbitrage_toward(target_price, D("100"))

    assert pool.state.tick == target_tick
    assert pool.state.liquidity == expected


def test_arbitrage_round_trip_restores_active_liquidity() -> None:
    pool = V3Pool(fixture_dex())
    initial_price = pool.spot_price
    initial_tick = pool.state.tick
    initial_liquidity = pool.state.liquidity

    pool.arbitrage_toward(initial_price * D("0.80"), D("100"))
    pool.arbitrage_toward(initial_price, D("100"))

    assert pool.state.tick == initial_tick
    assert pool.state.liquidity == initial_liquidity
