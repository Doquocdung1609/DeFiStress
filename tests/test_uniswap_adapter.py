from backend.app.adapters.uniswap.ticks import bitmap_ticks


def test_bitmap_word_decodes_positive_ticks() -> None:
    assert bitmap_ticks((1 << 0) | (1 << 3), word_position=2, tick_spacing=10) == [5120, 5150]


def test_bitmap_word_decodes_negative_word_positions() -> None:
    assert bitmap_ticks(1 << 255, word_position=-1, tick_spacing=60) == [-60]
