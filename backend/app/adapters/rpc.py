from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

READ_ONLY_METHODS = {
    "eth_blockNumber",
    "eth_call",
    "eth_chainId",
    "eth_getBlockByNumber",
    "eth_getLogs",
    "net_version",
}


class RpcError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RpcHealth:
    connected: bool
    chain_id: int | None
    current_block: int | None
    finalized_block: int | None
    block_lag: int | None
    latency_ms: float | None
    error: str | None


class ReadOnlyRpcClient:
    """Small JSON-RPC client with an explicit Mainnet read-method allowlist."""

    def __init__(self, url: str, timeout: float = 20.0):
        self.url = url
        self.timeout = timeout
        self._id = 0

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        if method not in READ_ONLY_METHODS:
            raise ValueError(f"RPC method is not permitted by read-only policy: {method}")
        if not self.url:
            raise RpcError("ETH_RPC_URL is not configured")
        self._id += 1
        response = httpx.post(
            self.url,
            json={"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or []},
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"RPC HTTP {response.status_code}\n"
                f"Request: {response.request.content.decode()}\n"
                f"Response: {response.text}"
            )
        payload = response.json()
        if "error" in payload:
            raise RpcError(str(payload["error"]))
        return payload["result"]

    def health(self) -> RpcHealth:
        started = time.perf_counter()
        try:
            chain_id = int(self.call("eth_chainId"), 16)
            block = int(self.call("eth_blockNumber"), 16)
            try:
                finalized_payload = self.call("eth_getBlockByNumber", ["finalized", False])
                finalized = int(finalized_payload["number"], 16)
            except Exception:
                finalized = None
            latency = (time.perf_counter() - started) * 1000
            return RpcHealth(
                chain_id == 1,
                chain_id,
                block,
                finalized,
                None if finalized is None else max(0, block - finalized),
                round(latency, 2),
                None if chain_id == 1 else "RPC is not Ethereum Mainnet",
            )
        except Exception as exc:  # surfaced as an actionable health result
            return RpcHealth(False, None, None, None, None, None, str(exc))

    @staticmethod
    def block_tag(block_number: int | None) -> str:
        return "finalized" if block_number is None else hex(block_number)
