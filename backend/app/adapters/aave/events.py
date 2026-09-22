from __future__ import annotations

from collections.abc import Callable
from typing import Any

from eth_utils import keccak

from backend.app.adapters.rpc import ReadOnlyRpcClient, RpcError

EVENTS = {
    "Borrow(address,address,address,uint256,uint8,uint256,uint16)": 2,
    "Supply(address,address,address,uint256,uint16)": 2,
    "Withdraw(address,address,address,uint256)": 2,
    "Repay(address,address,address,uint256,bool)": 2,
    "LiquidationCall(address,address,address,uint256,uint256,address,bool)": 3,
}


def discover_borrowers(
    rpc: ReadOnlyRpcClient,
    pool_address: str,
    from_block: int,
    to_block: int,
    chunk_size: int,
    max_users: int,
    progress: Callable[[int, int], None] | None = None,
) -> list[str]:
    users: set[str] = set()
    current = from_block
    dynamic_chunk = max(10, chunk_size)
    while current <= to_block and len(users) < max_users:
        end = min(to_block, current + dynamic_chunk - 1)
        try:
            for signature, user_topic_index in EVENTS.items():
                logs: list[dict[str, Any]] = rpc.call(
                    "eth_getLogs",
                    [
                        {
                            "address": pool_address,
                            "fromBlock": hex(current),
                            "toBlock": hex(end),
                            "topics": ["0x" + keccak(text=signature).hex()],
                        }
                    ],
                )
                for item in logs:
                    topics = item.get("topics", [])
                    if len(topics) > user_topic_index:
                        users.add("0x" + topics[user_topic_index][-40:])
                        if len(users) >= max_users:
                            break
            if progress:
                progress(end, to_block)
            current = end + 1
            dynamic_chunk = min(chunk_size, dynamic_chunk * 2)
        except RpcError:
            if dynamic_chunk <= 10:
                raise
            dynamic_chunk = max(10, dynamic_chunk // 2)
    return sorted(users)
