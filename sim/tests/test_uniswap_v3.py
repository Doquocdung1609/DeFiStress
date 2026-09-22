from decimal import Decimal

from sim.dex import V3Pool
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
