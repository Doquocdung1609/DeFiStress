from decimal import Decimal
from typing import Any

from web3 import Web3

from backend.app.adapters.uniswap.contracts import POOL_ABI
from backend.app.adapters.uniswap.ticks import read_initialized_ticks
from sim.schemas import DexState


def read_pool_state(
    web3: Web3,
    pool_address: str,
    block_identifier: int,
    tick_word_radius: int = 4,
) -> tuple[DexState, dict[str, Any]]:
    pool = web3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=POOL_ABI)
    token0 = pool.functions.token0().call(block_identifier=block_identifier)
    token1 = pool.functions.token1().call(block_identifier=block_identifier)
    fee = int(pool.functions.fee().call(block_identifier=block_identifier))
    spacing = int(pool.functions.tickSpacing().call(block_identifier=block_identifier))
    liquidity = int(pool.functions.liquidity().call(block_identifier=block_identifier))
    slot0 = pool.functions.slot0().call(block_identifier=block_identifier)
    try:
        ticks, tick_window = read_initialized_ticks(pool, int(slot0[1]), spacing, block_identifier, tick_word_radius)
    except Exception as exc:
        ticks = []
        tick_window = {
            "status": "INCOMPLETE",
            "word_radius": tick_word_radius,
            "error": f"{type(exc).__name__}: initialized tick reads failed at the pinned block",
        }
    state = DexState(
        pool_address=pool_address,
        token0=token0,
        token1=token1,
        fee=fee,
        tick_spacing=spacing,
        sqrt_price_x96=Decimal(int(slot0[0])),
        tick=int(slot0[1]),
        liquidity=Decimal(liquidity),
        ticks=ticks,
        source="REAL_MAINNET",
    )
    return state, {
        "observation_index": int(slot0[2]),
        "observation_cardinality": int(slot0[3]),
        "observation_cardinality_next": int(slot0[4]),
        "fee_protocol": int(slot0[5]),
        "unlocked": bool(slot0[6]),
        "tick_window": tick_window,
    }
