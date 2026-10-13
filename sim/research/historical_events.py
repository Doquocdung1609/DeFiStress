from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from eth_abi.abi import decode
from eth_utils.crypto import keccak

LIQUIDATION_SIGNATURE = "LiquidationCall(address,address,address,uint256,uint256,address,bool)"
SWAP_SIGNATURE = "Swap(address,address,int256,int256,uint160,uint128,int24)"
LIQUIDATION_TOPIC = "0x" + keccak(text=LIQUIDATION_SIGNATURE).hex()
SWAP_TOPIC = "0x" + keccak(text=SWAP_SIGNATURE).hex()


@dataclass(frozen=True, slots=True)
class EventCluster:
    cluster_id: str
    start_timestamp: int
    end_timestamp: int
    event_ids: tuple[str, ...]


def public_event_id(chain_id: int, block_number: int, tx_hash: str, log_index: int) -> str:
    payload = f"{chain_id}:{block_number}:{tx_hash.lower()}:{log_index}"
    return "event-" + hashlib.sha256(payload.encode()).hexdigest()[:20]


def pseudonymize_address(address: str) -> str:
    return "address-" + hashlib.sha256(f"defistress-level3:{address.lower()}".encode()).hexdigest()[:16]


def topic_address(topic: str) -> str:
    clean = topic.removeprefix("0x")
    if len(clean) != 64:
        raise ValueError("indexed address topic must contain exactly 32 bytes")
    return "0x" + clean[-40:].lower()


def decode_liquidation_log(log: Mapping[str, Any]) -> dict[str, Any]:
    topics = list(log.get("topics", []))
    if len(topics) != 4 or str(topics[0]).lower() != LIQUIDATION_TOPIC.lower():
        raise ValueError("log is not an Aave V3 LiquidationCall")
    data = bytes.fromhex(str(log["data"]).removeprefix("0x"))
    debt_to_cover, collateral_amount, liquidator, receive_a_token = decode(
        ["uint256", "uint256", "address", "bool"], data
    )
    return {
        "collateral_asset": topic_address(str(topics[1])),
        "debt_asset": topic_address(str(topics[2])),
        "borrower_hash": pseudonymize_address(topic_address(str(topics[3]))),
        "liquidator_hash": pseudonymize_address(str(liquidator)),
        "debt_to_cover_raw": int(debt_to_cover),
        "liquidated_collateral_raw": int(collateral_amount),
        "receive_a_token": bool(receive_a_token),
    }


def decode_uniswap_swap(log: Mapping[str, Any]) -> dict[str, Any]:
    topics = list(log.get("topics", []))
    if len(topics) != 3 or str(topics[0]).lower() != SWAP_TOPIC.lower():
        raise ValueError("log is not a Uniswap V3 Swap")
    data = bytes.fromhex(str(log["data"]).removeprefix("0x"))
    amount0, amount1, sqrt_price_x96, liquidity, tick = decode(
        ["int256", "int256", "uint160", "uint128", "int24"], data
    )
    return {
        "amount0_raw": int(amount0),
        "amount1_raw": int(amount1),
        "sqrt_price_x96": int(sqrt_price_x96),
        "liquidity": int(liquidity),
        "tick": int(tick),
    }


def normalize_amount(raw_amount: int, decimals: int) -> Decimal:
    if decimals < 0 or decimals > 255:
        raise ValueError("token decimals are outside the uint8 domain")
    return Decimal(raw_amount) / (Decimal(10) ** decimals)


def cluster_events(
    events: Iterable[Mapping[str, Any]], *, window_seconds: int
) -> list[EventCluster]:
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    ordered = sorted(
        events,
        key=lambda item: (
            int(item["timestamp"]),
            int(item["block_number"]),
            int(item.get("transaction_index", 0)),
            int(item["log_index"]),
        ),
    )
    clusters: list[list[Mapping[str, Any]]] = []
    for event in ordered:
        if not clusters or int(event["timestamp"]) - int(clusters[-1][-1]["timestamp"]) > window_seconds:
            clusters.append([event])
        else:
            clusters[-1].append(event)
    result: list[EventCluster] = []
    for index, cluster in enumerate(clusters, start=1):
        result.append(
            EventCluster(
                cluster_id=f"cluster-{window_seconds}s-{index:03d}",
                start_timestamp=int(cluster[0]["timestamp"]),
                end_timestamp=int(cluster[-1]["timestamp"]),
                event_ids=tuple(str(item["event_id"]) for item in cluster),
            )
        )
    return result


def select_episodes(
    clusters: list[EventCluster], *, max_episodes: int = 5, usd_values_comparable: bool
) -> list[EventCluster]:
    if max_episodes < 1:
        raise ValueError("max_episodes must be positive")
    if usd_values_comparable:
        raise ValueError("volume-stratified selection requires explicit cluster volume inputs")
    return sorted(clusters, key=lambda cluster: (cluster.start_timestamp, cluster.cluster_id))[
        :max_episodes
    ]


def classify_linkage(
    liquidation: Mapping[str, Any], swaps: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    swap_rows = list(swaps)
    same_tx = [row for row in swap_rows if row["tx_hash"] == liquidation["tx_hash"]]
    if same_tx:
        return {"tier": "DIRECT_TRANSACTION_LINK", "matched_swap_ids": [r["swap_id"] for r in same_tx]}
    same_block = [
        row for row in swap_rows if int(row["block_number"]) == int(liquidation["block_number"])
    ]
    if same_block:
        return {"tier": "SAME_BLOCK_ASSOCIATION", "matched_swap_ids": [r["swap_id"] for r in same_block]}
    timestamp = int(liquidation["timestamp"])
    within = [row for row in swap_rows if abs(int(row["timestamp"]) - timestamp) <= 30 * 60]
    if within:
        nearest = min(within, key=lambda row: abs(int(row["timestamp"]) - timestamp))
        return {
            "tier": "TIME_WINDOW_ASSOCIATION",
            "matched_swap_ids": [nearest["swap_id"]],
            "nearest_seconds": abs(int(nearest["timestamp"]) - timestamp),
        }
    return {"tier": "UNLINKED/UNOBSERVABLE", "matched_swap_ids": []}


def assert_unique_chain_order(events: Iterable[Mapping[str, Any]], chain_id: int = 1) -> None:
    seen: set[tuple[str, int]] = set()
    previous: tuple[int, int, int] | None = None
    for event in sorted(
        events,
        key=lambda item: (
            int(item["block_number"]),
            int(item.get("transaction_index", 0)),
            int(item["log_index"]),
        ),
    ):
        if int(event["chain_id"]) != chain_id:
            raise ValueError("event chain mixing detected")
        key = (str(event["tx_hash"]).lower(), int(event["log_index"]))
        if key in seen:
            raise ValueError("duplicate transaction/log event detected")
        seen.add(key)
        current = (
            int(event["block_number"]),
            int(event.get("transaction_index", 0)),
            int(event["log_index"]),
        )
        if previous is not None and current < previous:
            raise ValueError("event ordering is not monotonic")
        previous = current


__all__ = [
    "LIQUIDATION_TOPIC",
    "SWAP_TOPIC",
    "EventCluster",
    "assert_unique_chain_order",
    "classify_linkage",
    "cluster_events",
    "decode_liquidation_log",
    "decode_uniswap_swap",
    "normalize_amount",
    "pseudonymize_address",
    "public_event_id",
    "select_episodes",
]
