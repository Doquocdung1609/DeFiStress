from decimal import Decimal
from typing import Any

from sim.schemas import LiquidityTick


def bitmap_ticks(word: int, word_position: int, tick_spacing: int) -> list[int]:
    """Decode initialized ticks from one Uniswap V3 bitmap word."""
    ticks: list[int] = []
    remaining = word
    while remaining:
        least_significant = remaining & -remaining
        bit = least_significant.bit_length() - 1
        compressed = (word_position << 8) + bit
        ticks.append(compressed * tick_spacing)
        remaining ^= least_significant
    return ticks


def read_initialized_ticks(
    pool: Any,
    current_tick: int,
    tick_spacing: int,
    block_identifier: int,
    word_radius: int = 4,
) -> tuple[list[LiquidityTick], dict[str, Any]]:
    """Read a symmetric bitmap window at exactly one pinned block."""
    compressed = current_tick // tick_spacing
    center_word = compressed >> 8
    initialized: list[LiquidityTick] = []
    first_word = center_word - word_radius
    last_word = center_word + word_radius
    for word_position in range(first_word, last_word + 1):
        word = int(pool.functions.tickBitmap(word_position).call(block_identifier=block_identifier))
        for tick in bitmap_ticks(word, word_position, tick_spacing):
            raw = pool.functions.ticks(tick).call(block_identifier=block_identifier)
            if bool(raw[7]):
                initialized.append(
                    LiquidityTick(
                        tick=tick,
                        liquidity_net=Decimal(int(raw[1])),
                        liquidity_gross=Decimal(int(raw[0])),
                    )
                )
    return sorted(initialized, key=lambda item: item.tick), {
        "status": "COMPLETE_WINDOW",
        "first_word": first_word,
        "last_word": last_word,
        "word_radius": word_radius,
        "initialized_ticks": len(initialized),
    }


def tick_data_status(graph_api_key: str) -> dict[str, Any]:
    if not graph_api_key:
        return {
            "status": "UNAVAILABLE",
            "flag": "TICK_DATA_INCOMPLETE",
            "message": "GRAPH_API_KEY is required for indexed initialized ticks.",
        }
    return {
        "status": "NOT_IMPLEMENTED",
        "flag": "TICK_DATA_INCOMPLETE",
        "message": "Direct pool state is available; indexed tick ingestion requires schema configuration.",
    }
