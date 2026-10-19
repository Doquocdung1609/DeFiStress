"""Pure synthetic adverse controls; fixtures are NEVER empirical evidence."""
import copy
import hashlib
import json

import pytest

from docs.research_v2.prephase02_offline.validate_offline import (
    borrower_complete, canonical_equal, complete_fields, digest,
    liquidity_consistent, oracle_valid, tick_band, units,
    validate_identity, validate_pool,
)

USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
POOL = "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"
HASH = "0x4dffe3bdf7bbaf24fd1e3b6c3f4795687dccfd3189cbfb61f4dbaf926722220a"


@pytest.mark.parametrize(("test_id", "observed", "expected"), [
    ("bad_chain", lambda: validate_identity(5, 26045352, HASH), False),
    ("bad_hash", lambda: validate_identity(1, 26045352, "0x00"), False),
    ("future_or_wrong_block", lambda: validate_identity(1, 26045353, HASH), False),
    ("wrong_pool", lambda: validate_pool(WETH, 3000, "P3000", USDC, WETH, USDC, WETH), False),
    ("swapped_tokens", lambda: validate_pool(POOL, 3000, "P3000", WETH, USDC, USDC, WETH), False),
    ("good_pool", lambda: validate_pool(POOL, 3000, "P3000", USDC, WETH, USDC, WETH), True),
    ("usdc_decimal_mixup", lambda: units(1000000, 18, 6), False),
    ("weth_decimal_mixup", lambda: units(10**18, 6, 18), False),
    ("negative_raw", lambda: units(-1, 6, 6), False),
    ("fractional_raw", lambda: units(1.5, 6, 6), False),
    ("tuple_list_equal", lambda: canonical_equal((7, -1, True), [7, -1, True]), True),
    ("tuple_content_differs", lambda: canonical_equal((7, -1), [7, -2]), False),
    ("missing_field", lambda: complete_fields({"a": 1, "b": 2}, {"a": 1}), False),
    ("extra_field", lambda: complete_fields({"a": 1}, {"a": 1, "b": 2}), False),
    ("null_not_zero", lambda: canonical_equal({"a": None}, {"a": 0}), False),
    ("field_swapped", lambda: canonical_equal({"a": 1, "b": 2}, {"a": 2, "b": 1}), False),
    ("duplicate_tick", lambda: tick_band([{"index": 60, "gross": 5, "net": 2, "bitmap_initialized": True},
                                           {"index": 60, "gross": 5, "net": 2, "bitmap_initialized": True}],
                                          0, 120, 60), False),
    ("tick_outside_band", lambda: tick_band([{"index": 180, "gross": 5, "net": 2, "bitmap_initialized": True}],
                                             0, 120, 60), False),
    ("bitmap_uninitialized", lambda: tick_band([{"index": 60, "gross": 5, "net": 2, "bitmap_initialized": False}],
                                               0, 120, 60), False),
    ("gross_less_than_net", lambda: tick_band([{"index": 60, "gross": 1, "net": 2, "bitmap_initialized": True}],
                                              0, 120, 60), False),
    ("active_above_total", lambda: liquidity_consistent(101, 100), False),
    ("negative_active", lambda: liquidity_consistent(-1, 100), False),
    ("dex_spot_for_oracle", lambda: oracle_valid("aave", "aave", 4, 90, 100, True), False),
    ("oracle_wrong_source", lambda: oracle_valid("dex", "aave", 4, 90, 100), False),
    ("oracle_future_timestamp", lambda: oracle_valid("aave", "aave", 4, 101, 100), False),
    ("oracle_zero_round", lambda: oracle_valid("aave", "aave", 0, 90, 100), False),
    ("borrower_wrong_reserve", lambda: borrower_complete([1, 2], [1, 3], {1: 100, 2: 0}, 10**18), False),
    ("borrower_missing_liability", lambda: borrower_complete([1, 2], [1, 2], {1: 100}, 10**18), False),
    ("borrower_duplicate_reserve", lambda: borrower_complete([1, 1], [1], {1: 100}, 10**18), False),
    ("borrower_invalid_hf", lambda: borrower_complete([1], [1], {1: 100}, None), False),
    ("raw_sha_tampered", lambda: digest(b"artifact") == digest(b"artifactX"), False),
    ("json_digest_change", lambda: digest(json.dumps({"a": 1}).encode()) ==
                               digest(json.dumps({"a": 2}).encode()), False),
])
def test_synthetic_control(test_id, observed, expected):
    assert observed() is expected, test_id


def test_registered_control_positive():
    assert validate_identity(1, 26045352, HASH)
    assert units(10**6, 6, 6)
    assert tick_band([{"index": 60, "gross": 5, "net": -2, "bitmap_initialized": True}], 0, 120, 60)
    assert oracle_valid("aave", "aave", 9, 90, 100)
    assert borrower_complete([1], [1], {1: 0}, 10**18)


def test_null_and_zero_remain_distinct_under_deep_copy():
    original = {"a": [0, {"b": None}]}
    modified = copy.deepcopy(original)
    modified["a"][1]["b"] = 0
    assert not canonical_equal(original, modified)


def test_sha256_known_vector():
    assert hashlib.sha256(b"abc").hexdigest() == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
