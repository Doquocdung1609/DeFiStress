from decimal import Decimal

from sim.dex.uniswap_v3 import SwapQuote, V3Pool


def quote_weth_sale(pool: V3Pool, amount_weth: Decimal) -> SwapQuote:
    return pool.quote_sell_weth(amount_weth)
