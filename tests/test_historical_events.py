from __future__ import annotations

from eth_abi import encode

from sim.research.historical_events import (
    LIQUIDATION_TOPIC,
    SWAP_TOPIC,
    assert_unique_chain_order,
    classify_linkage,
    cluster_events,
    decode_liquidation_log,
    decode_uniswap_swap,
    normalize_amount,
    select_episodes,
)


def _topic(address: str) -> str:
    return "0x" + address.removeprefix("0x").lower().rjust(64, "0")


def _event(index: int, timestamp: int) -> dict[str, object]:
    return {
        "event_id": f"event-{index}",
        "chain_id": 1,
        "timestamp": timestamp,
        "block_number": 100 + index,
        "transaction_index": 0,
        "log_index": index,
        "tx_hash": f"0x{index:064x}",
    }


def test_decode_liquidation_call_and_normalized_units() -> None:
    log = {
        "topics": [
            LIQUIDATION_TOPIC,
            _topic("0x0000000000000000000000000000000000000011"),
            _topic("0x0000000000000000000000000000000000000022"),
            _topic("0x0000000000000000000000000000000000000033"),
        ],
        "data": "0x"
        + encode(
            ["uint256", "uint256", "address", "bool"],
            [2_000_000, 10**18, "0x0000000000000000000000000000000000000044", False],
        ).hex(),
    }
    decoded = decode_liquidation_log(log)
    assert decoded["debt_to_cover_raw"] == 2_000_000
    assert decoded["liquidated_collateral_raw"] == 10**18
    assert decoded["receive_a_token"] is False
    assert decoded["borrower_hash"].startswith("address-")
    assert normalize_amount(decoded["debt_to_cover_raw"], 6) == 2
    assert normalize_amount(decoded["liquidated_collateral_raw"], 18) == 1


def test_decode_uniswap_swap_signed_amounts() -> None:
    log = {
        "topics": [
            SWAP_TOPIC,
            _topic("0x0000000000000000000000000000000000000011"),
            _topic("0x0000000000000000000000000000000000000022"),
        ],
        "data": "0x"
        + encode(
            ["int256", "int256", "uint160", "uint128", "int24"],
            [-2_000_000, 10**18, 2**96, 1234, -7],
        ).hex(),
    }
    decoded = decode_uniswap_swap(log)
    assert decoded == {
        "amount0_raw": -2_000_000,
        "amount1_raw": 10**18,
        "sqrt_price_x96": 2**96,
        "liquidity": 1234,
        "tick": -7,
    }


def test_cluster_windows_and_chronological_fallback_selection() -> None:
    events = [_event(1, 100), _event(2, 159), _event(3, 461), _event(4, 462)]
    clusters = cluster_events(events, window_seconds=300)
    assert [len(cluster.event_ids) for cluster in clusters] == [2, 2]
    selected = select_episodes(clusters, max_episodes=1, usd_values_comparable=False)
    assert selected[0].event_ids == ("event-1", "event-2")


def test_linkage_tiers_are_exact_and_not_causal_by_proximity() -> None:
    liquidation = {"tx_hash": "0x01", "block_number": 100, "timestamp": 1_000}
    direct = {"swap_id": "direct", "tx_hash": "0x01", "block_number": 100, "timestamp": 1_000}
    same_block = {"swap_id": "block", "tx_hash": "0x02", "block_number": 100, "timestamp": 1_001}
    nearby = {"swap_id": "near", "tx_hash": "0x03", "block_number": 101, "timestamp": 1_100}
    assert classify_linkage(liquidation, [direct, same_block, nearby])["tier"] == "DIRECT_TRANSACTION_LINK"
    assert classify_linkage(liquidation, [same_block, nearby])["tier"] == "SAME_BLOCK_ASSOCIATION"
    assert classify_linkage(liquidation, [nearby])["tier"] == "TIME_WINDOW_ASSOCIATION"
    assert classify_linkage(liquidation, [dict(nearby, timestamp=3_000)])["tier"] == "UNLINKED/UNOBSERVABLE"


def test_chain_mixing_and_duplicate_tx_log_are_rejected() -> None:
    event = _event(1, 100)
    assert_unique_chain_order([event])
    try:
        assert_unique_chain_order([event, event])
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate event was accepted")
    try:
        assert_unique_chain_order([dict(event, chain_id=10)])
    except ValueError as exc:
        assert "mixing" in str(exc)
    else:
        raise AssertionError("mixed-chain event was accepted")
