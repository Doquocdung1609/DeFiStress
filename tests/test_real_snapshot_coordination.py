from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest

from backend.app.adapters.rpc import RpcHealth
from backend.app.config import Settings
from backend.app.services import real_snapshot
from sim.schemas import DexState


def test_snapshot_block_uses_confirmed_rpc_and_graph_minimum() -> None:
    assert (
        real_snapshot._select_snapshot_block(
            rpc_head=1_000,
            graph_head=995,
            confirmations=12,
            requested_block=None,
        )
        == 988
    )
    assert (
        real_snapshot._select_snapshot_block(
            rpc_head=1_000,
            graph_head=980,
            confirmations=12,
            requested_block=None,
        )
        == 980
    )


def test_snapshot_block_rejects_uncoordinated_explicit_block() -> None:
    with pytest.raises(ValueError, match="exceeds coordinated snapshot head"):
        real_snapshot._select_snapshot_block(
            rpc_head=1_000,
            graph_head=995,
            confirmations=12,
            requested_block=989,
        )


def test_real_snapshot_uses_graph_discovery_and_one_block(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, int]] = []

    class FakeRpc:
        def __init__(self, url: str) -> None:
            assert url == "https://rpc.example"

        def health(self) -> RpcHealth:
            return RpcHealth(True, 1, 1_000, 990, 10, 1.0, None)

    class FakeGraph:
        def __init__(self, api_key: str, subgraph_id: str) -> None:
            assert api_key == "graph-secret"
            assert subgraph_id == "subgraph-id"

        def indexed_block(self) -> int:
            return 995

    class FakeEth:
        def get_block(self, block_number: int) -> dict[str, Any]:
            calls.append(("block", block_number))
            return {"number": block_number, "hash": bytes.fromhex("12" * 32), "timestamp": 1_700_000_000}

    class FakeWeb3:
        def __init__(self, provider: Any) -> None:
            self.eth = FakeEth()

    addresses = SimpleNamespace(
        chain_id=1,
        pool="0xpool",
        weth="0xweth",
        usdc="0xusdc",
        oracle="0xoracle",
        data_provider="0xprovider",
        source_url="https://example.invalid/address-book",
        version="test",
        commit="abc123",
    )

    class FakeAave:
        def __init__(self, web3: Any, address_book: Any) -> None:
            pass

        def reserve(self, symbol: str, asset: str, block_identifier: int) -> dict[str, Any]:
            calls.append((f"reserve-{symbol}", block_identifier))
            return {"symbol": symbol, "oracle_price": "2000" if symbol == "WETH" else "1"}

        def positions(self, users: list[str], block_identifier: int) -> tuple[list[Any], list[dict[str, Any]], int]:
            calls.append(("positions", block_identifier))
            assert users == ["0xborrower"]
            return [], [], 0

    class FakeV3Pool:
        def __init__(self, state: DexState) -> None:
            self.spot_price = Decimal("2000")

        def depth_to_price_drop_usdc(self, drop: Decimal) -> Decimal:
            return Decimal("1000000")

    pool_state = DexState(
        pool_address="0xpool-address",
        token0=addresses.usdc,
        token1=addresses.weth,
        fee=500,
        tick_spacing=10,
        sqrt_price_x96=Decimal(1),
        tick=0,
        liquidity=Decimal(1),
    )
    pool_metadata = {"tick_window": {"status": "COMPLETE_WINDOW"}}

    def fake_discovery(graph: Any, **kwargs: int) -> list[str]:
        calls.append(("graph", kwargs["block_number"]))
        return ["0xborrower"]

    def fake_find_pools(web3: Any, weth: str, usdc: str, block_identifier: int) -> list[dict[str, Any]]:
        calls.append(("find-pools", block_identifier))
        return [{"pool_address": pool_state.pool_address, "fee": pool_state.fee}]

    def fake_read_pool(
        web3: Any, pool_address: str, block_identifier: int, tick_word_radius: int
    ) -> tuple[DexState, dict[str, Any]]:
        calls.append(("pool-state", block_identifier))
        return pool_state, pool_metadata

    monkeypatch.setattr(real_snapshot, "ReadOnlyRpcClient", FakeRpc)
    monkeypatch.setattr(real_snapshot, "GraphClient", FakeGraph)
    monkeypatch.setattr(real_snapshot, "HTTPProvider", lambda *args, **kwargs: object())
    monkeypatch.setattr(real_snapshot, "Web3", FakeWeb3)
    monkeypatch.setattr(real_snapshot, "load_aave_ethereum_address_book", lambda: addresses)
    monkeypatch.setattr(real_snapshot, "discover_borrowers_from_graph", fake_discovery)
    monkeypatch.setattr(real_snapshot, "AaveMarketReader", FakeAave)
    monkeypatch.setattr(real_snapshot, "find_weth_usdc_pools", fake_find_pools)
    monkeypatch.setattr(real_snapshot, "read_pool_state", fake_read_pool)
    monkeypatch.setattr(real_snapshot, "V3Pool", FakeV3Pool)

    snapshot = real_snapshot.create_real_snapshot(
        Settings(
            eth_rpc_url="https://rpc.example",
            graph_api_key="graph-secret",
            aave_v3_subgraph_id="subgraph-id",
            snapshot_confirmations=12,
        )
    )

    assert snapshot["block_number"] == 988
    assert {block for _, block in calls} == {988}
    assert snapshot["source_manifest"]["borrower_discovery"] == {
        "source": "The Graph",
        "subgraph_id": "subgraph-id",
        "block_number": 988,
        "candidate_count": 1,
    }
    assert snapshot["source_manifest"]["state_verification"]["source"] == "Ethereum Mainnet RPC"
    assert snapshot["source_manifest"]["state_verification"]["aave_method"] == "Pool.getUserAccountData"
