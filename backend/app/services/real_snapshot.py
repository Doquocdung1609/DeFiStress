from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from typing import Any

from web3 import HTTPProvider, Web3

from backend.app.adapters.aave import AaveMarketReader, discover_borrowers, load_aave_ethereum_address_book
from backend.app.adapters.rpc import ReadOnlyRpcClient
from backend.app.adapters.uniswap import find_weth_usdc_pools, read_pool_state
from backend.app.adapters.uniswap.factory import UNISWAP_V3_FACTORY
from backend.app.config import Settings
from sim.dex import V3Pool
from sim.schemas import json_safe

D = Decimal


def create_real_snapshot(
    settings: Settings,
    block_number: int | None = None,
    candidate_users: list[str] | None = None,
) -> dict[str, Any]:
    if not settings.eth_rpc_url:
        raise ValueError("ETH_RPC_URL is required for REAL_MAINNET mode")
    rpc_url = (
        settings.eth_archive_rpc_url
        if block_number is not None and settings.eth_archive_rpc_url
        else settings.eth_rpc_url
    )
    rpc = ReadOnlyRpcClient(rpc_url)
    health = rpc.health()
    if not health.connected or health.chain_id != 1:
        raise ValueError(health.error or "Ethereum Mainnet RPC is unavailable")

    web3 = Web3(HTTPProvider(rpc_url, request_kwargs={"timeout": 30}))
    addresses = load_aave_ethereum_address_book()
    if addresses.chain_id != 1:
        raise ValueError("Aave address-book module is not Ethereum Mainnet")
    block = web3.eth.get_block(block_number if block_number is not None else "finalized")
    pinned_block = int(block["number"])
    block_hash = block["hash"].hex()
    block_time = datetime.fromtimestamp(int(block["timestamp"]), UTC).isoformat()

    if candidate_users is None:
        start = max(0, pinned_block - settings.discovery_lookback_blocks)
        candidate_users = discover_borrowers(
            rpc,
            addresses.pool,
            start,
            pinned_block,
            settings.rpc_block_chunk_size,
            settings.borrower_max_users,
        )
    else:
        candidate_users = candidate_users[: settings.borrower_max_users]

    aave = AaveMarketReader(web3, addresses)
    weth_reserve = aave.reserve("WETH", addresses.weth, pinned_block)
    usdc_reserve = aave.reserve("USDC", addresses.usdc, pinned_block)
    positions, position_provenance, failed_reads = aave.positions(candidate_users, pinned_block)
    weth_price = D(weth_reserve["oracle_price"])
    for position, provenance in zip(positions, position_provenance, strict=False):
        total_collateral = D(provenance["total_collateral_base"]) / D("1e8")
        position.other_collateral_usd = max(D(0), total_collateral - position.collateral_weth * weth_price)

    pool_candidates = find_weth_usdc_pools(web3, addresses.weth, addresses.usdc, pinned_block)
    if not pool_candidates:
        raise ValueError("No Uniswap V3 WETH/USDC pool was resolved from the official factory")
    pool_states = [
        read_pool_state(web3, item["pool_address"], pinned_block, settings.uniswap_tick_word_radius)
        for item in pool_candidates
    ]
    selected_state, selected_meta = max(
        pool_states,
        key=lambda item: V3Pool(item[0]).depth_to_price_drop_usdc(D("2")),
    )
    if (
        selected_state.token0.lower() != addresses.usdc.lower()
        or selected_state.token1.lower() != addresses.weth.lower()
    ):
        raise ValueError("Unexpected WETH/USDC token ordering")
    dex_price = V3Pool(selected_state).spot_price
    selected_pool = json_safe(selected_state)
    selected_pool["spot_price"] = float(dex_price)
    selected_pool["selection_rule"] = "largest modeled executable USDC depth to a 2% WETH price drop"
    selected_pool["slot0_metadata"] = selected_meta

    all_pools = []
    for state, metadata in pool_states:
        modeled_pool = V3Pool(state)
        all_pools.append(
            {
                **json_safe(state),
                "spot_price": float(modeled_pool.spot_price),
                "depth_usdc_2pct": float(modeled_pool.depth_to_price_drop_usdc(D("2"))),
                "slot0_metadata": metadata,
            }
        )

    active = [position for position in positions if position.debt_value() > 0]
    cohort = [position for position in active if position.collateral_weth > 0 and position.debt_usdc > 0]
    data_quality = []
    if selected_meta["tick_window"]["status"] != "COMPLETE_WINDOW":
        data_quality.append(
            {
                "code": "TICK_DATA_INCOMPLETE",
                "severity": "YELLOW",
                "message": (
                    "Initialized tick bitmap reads failed; large-trade results require a Quoter/fork cross-check."
                ),
            }
        )
    if failed_reads:
        data_quality.append(
            {
                "code": "POSITION_READ_FAILED",
                "severity": "YELLOW",
                "message": f"{failed_reads} candidate position reads failed at the snapshot block.",
            }
        )
    if not settings.eth_archive_rpc_url:
        data_quality.append(
            {
                "code": "ARCHIVE_UNAVAILABLE",
                "severity": "INFO",
                "message": "Archive RPC is not configured; local-fork and historical validation are unavailable.",
            }
        )
    for position, provenance in zip(positions, position_provenance, strict=False):
        internal = position.health_factor(weth_price)
        protocol_hf = D(provenance["aave_health_factor"])
        if protocol_hf.is_finite() and abs(internal - protocol_hf) > D("0.02"):
            data_quality.append(
                {
                    "code": "HF_MISMATCH",
                    "severity": "YELLOW",
                    "message": (
                        f"{position.borrower_hash}: portfolio approximation differs from "
                        f"Pool.getUserAccountData by {abs(internal - protocol_hf):.6f}."
                    ),
                }
            )

    snapshot_id = "real-" + sha256(f"{pinned_block}:{block_hash}:{addresses.commit}".encode()).hexdigest()[:20]
    retrieved_at = datetime.now(UTC).isoformat()
    snapshot = {
        "id": snapshot_id,
        "mode": "REAL_MAINNET",
        "label": "Ethereum Mainnet snapshot",
        "chain_id": 1,
        "block_number": pinned_block,
        "block_hash": block_hash,
        "block_timestamp": block_time,
        "retrieved_at": retrieved_at,
        "source_manifest": {
            "chain_id": 1,
            "block_number": pinned_block,
            "block_hash": block_hash,
            "rpc_provider": _redacted_provider(rpc_url),
            "aave": {
                "market": "Aave V3 Ethereum",
                "address_book_source": addresses.source_url,
                "address_book_version": addresses.version,
                "address_book_commit": addresses.commit,
                "pool": addresses.pool,
                "oracle": addresses.oracle,
                "data_provider": addresses.data_provider,
            },
            "uniswap": {"factory": UNISWAP_V3_FACTORY, "pool": selected_state.pool_address, "fee": selected_state.fee},
            "application": {"model_version": "0.1.0-aave-v3.7-approx"},
        },
        "aave_market": "Aave V3 Ethereum",
        "aave_reserves": [weth_reserve, usdc_reserve],
        "borrowers": [
            {
                **json_safe(position),
                "health_factor": float(position.health_factor(weth_price)),
                "liquidation_price": float(position.liquidation_price() or 0),
                "provenance": evidence,
            }
            for position, evidence in zip(positions, position_provenance, strict=False)
        ],
        "dex_pool": selected_pool,
        "dex_pools": all_pools,
        "dex_ticks": json_safe(selected_state.ticks),
        "oracle_prices": {"WETH": float(weth_price), "USDC": float(D(usdc_reserve["oracle_price"]))},
        "external_prices": {"WETH": float(dex_price), "USDC": 1.0},
        "stablecoin_state": {
            "symbol": "USDC",
            "price": float(D(usdc_reserve["oracle_price"])),
            "depeg_bps": float((D(usdc_reserve["oracle_price"]) - 1) * 10_000),
        },
        "coverage": {
            "candidates_discovered": len(candidate_users),
            "positions_loaded": len(positions),
            "active_borrowers": len(active),
            "weth_collateral_borrowers": sum(position.collateral_weth > 0 for position in active),
            "usdc_borrowers": sum(position.debt_usdc > 0 for position in active),
            "weth_usdc_cohort": len(cohort),
            "failed_reads": failed_reads,
            "excluded_positions": len(candidate_users) - len(positions) - failed_reads,
            "coverage_pct": 0 if not candidate_users else round(len(positions) / len(candidate_users) * 100, 2),
            "cohort_label": f"Top {settings.borrower_max_users} event-discovered candidates within lookback"
            if len(candidate_users) >= settings.borrower_max_users
            else "Event-discovered lookback cohort",
        },
        "data_quality_flags": data_quality,
    }
    return json_safe(snapshot)


def _redacted_provider(url: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.hostname or 'configured-provider'}"
