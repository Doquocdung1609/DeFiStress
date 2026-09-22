from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from sim.dex import V3Pool
from sim.fixtures import fixture_dex


@given(st.decimals(min_value="0", max_value="100", allow_nan=False, allow_infinity=False, places=4))
def test_nonnegative_sell_has_nonnegative_output(amount: Decimal) -> None:
    quote = V3Pool(fixture_dex()).sell_weth(amount)
    assert quote.amount_usdc_out >= 0
    assert quote.price_after > 0
