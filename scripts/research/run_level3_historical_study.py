from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from threading import Lock
from typing import Any

from web3 import Web3

from backend.app.adapters.aave.address_book import load_aave_ethereum_address_book
from backend.app.adapters.aave.contracts import ORACLE_ABI
from backend.app.adapters.aave.oracle import normalized_asset_price
from backend.app.adapters.graph import GraphClient
from backend.app.adapters.rpc import ReadOnlyRpcClient, RpcError
from backend.app.config import Settings
from sim.research.historical_events import (
    LIQUIDATION_TOPIC,
    SWAP_TOPIC,
    assert_unique_chain_order,
    classify_linkage,
    cluster_events,
    decode_liquidation_log,
    decode_uniswap_swap,
    normalize_amount,
    public_event_id,
    select_episodes,
)

ROOT = Path("data/processed/research_final/level3_extension")
HISTORICAL = ROOT / "historical"
FORK = ROOT / "fork"
INVALID_EPOCH_ATTEMPT = ROOT / "historical_invalid_epoch_attempt"
SNAPSHOT = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
START_TIMESTAMP = 1_788_220_800  # 2026-09-01T00:00:00Z
END_TIMESTAMP = 1_788_825_600  # 2026-09-08T00:00:00Z, exclusive
CHAIN_ID = 1
SOURCE_COMMIT = "423bcfd4ebf910ef73b94d9deaf7cf746d8ed71c"
MAX_RPC_CALLS = 25_000
LIQUIDATES_QUERY = """
query Liquidations($first:Int!,$skip:Int!,$start:BigInt!,$end:BigInt!){
  liquidates(
    first:$first, skip:$skip, orderBy:timestamp, orderDirection:asc,
    where:{timestamp_gte:$start,timestamp_lt:$end}
  ){
    id hash logIndex blockNumber timestamp amount amountUSD profitUSD
    asset{id symbol decimals}
    liquidatee{id}
    liquidator{id}
    market{id name}
    positions{id side type isCollateral balance principal asset{id symbol decimals}}
  }
}
"""


class BudgetedRpc:
    def __init__(self, client: ReadOnlyRpcClient, limit: int = MAX_RPC_CALLS) -> None:
        self.client = client
        self.limit = limit
        self.calls = 0
        self._lock = Lock()

    def call(self, method: str, params: list[Any]) -> Any:
        with self._lock:
            if self.calls >= self.limit:
                raise RuntimeError(f"RPC request budget exhausted at {self.calls}/{self.limit}")
            self.calls += 1
        for attempt in range(8):
            try:
                return self.client.call(method, params)
            except (RpcError, RuntimeError):
                if attempt == 7:
                    raise
                time.sleep(min(30.0, 1.0 * (2**attempt)))
        raise AssertionError("unreachable")


def _json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _hex_int(value: str | int | None) -> int:
    if value is None:
        return 0
    return int(value, 16) if isinstance(value, str) and value.startswith("0x") else int(value)


def _iso(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _discover(graph: GraphClient) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for skip in range(0, 10_000, 1_000):
        page = graph.query(
            LIQUIDATES_QUERY,
            {"first": 1_000, "skip": skip, "start": START_TIMESTAMP, "end": END_TIMESTAMP},
        ).get("liquidates", [])
        if not isinstance(page, list):
            raise RuntimeError("The Graph returned an invalid liquidates payload")
        rows.extend(page)
        if len(page) < 1_000:
            break
    return rows


def _position_asset(row: dict[str, Any], side: str) -> dict[str, Any] | None:
    for position in row.get("positions", []):
        if position.get("side") == side:
            return position.get("asset")
    return None


def _verified_events(
    rows: list[dict[str, Any]], rpc: BudgetedRpc, pool: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    block_cache: dict[int, dict[str, Any]] = {}
    for row in rows:
        block_number = int(row["blockNumber"])
        tx_hash = str(row["hash"]).lower()
        log_index = int(row["logIndex"])
        event_id = public_event_id(CHAIN_ID, block_number, tx_hash, log_index)
        try:
            logs = rpc.call(
                "eth_getLogs",
                [
                    {
                        "address": pool,
                        "fromBlock": hex(block_number),
                        "toBlock": hex(block_number),
                        "topics": [LIQUIDATION_TOPIC],
                    }
                ],
            )
            match = next(
                item
                for item in logs
                if str(item["transactionHash"]).lower() == tx_hash
                and _hex_int(item["logIndex"]) == log_index
            )
            receipt = rpc.call("eth_getTransactionReceipt", [tx_hash])
            block = block_cache.setdefault(
                block_number,
                rpc.call("eth_getBlockByNumber", [hex(block_number), False]),
            )
            decoded = decode_liquidation_log(match)
            collateral = _position_asset(row, "COLLATERAL") or row["asset"]
            debt = _position_asset(row, "BORROWER")
            if debt is None:
                raise ValueError("Graph row has no BORROWER position/debt asset")
            collateral_decimals = int(collateral["decimals"])
            debt_decimals = int(debt["decimals"])
            block_hash = str(block["hash"]).lower()
            if str(match["blockHash"]).lower() != block_hash:
                raise ValueError("log block hash disagrees with canonical block")
            if str(receipt["blockHash"]).lower() != block_hash:
                raise ValueError("receipt block hash disagrees with canonical block")
            timestamp = _hex_int(block["timestamp"])
            if not START_TIMESTAMP <= timestamp < END_TIMESTAMP:
                raise ValueError("RPC block timestamp is outside preregistered window")
            graph_timestamp_matches = timestamp == int(row["timestamp"])
            events.append(
                {
                    "event_id": event_id,
                    "status": "PASS",
                    "chain_id": CHAIN_ID,
                    "protocol": "Aave V3 Ethereum",
                    "pool_address": pool,
                    "abi_event": "LiquidationCall",
                    "block_number": block_number,
                    "block_hash": block_hash,
                    "timestamp": timestamp,
                    "timestamp_utc": _iso(timestamp),
                    "tx_hash": tx_hash,
                    "transaction_index": _hex_int(receipt.get("transactionIndex")),
                    "log_index": log_index,
                    "receipt_status": _hex_int(receipt.get("status")),
                    "collateral_asset": decoded["collateral_asset"],
                    "collateral_symbol": collateral["symbol"],
                    "collateral_decimals": collateral_decimals,
                    "debt_asset": decoded["debt_asset"],
                    "debt_symbol": debt["symbol"],
                    "debt_decimals": debt_decimals,
                    "debt_to_cover_raw": decoded["debt_to_cover_raw"],
                    "debt_to_cover": str(
                        normalize_amount(decoded["debt_to_cover_raw"], debt_decimals)
                    ),
                    "liquidated_collateral_raw": decoded["liquidated_collateral_raw"],
                    "liquidated_collateral": str(
                        normalize_amount(decoded["liquidated_collateral_raw"], collateral_decimals)
                    ),
                    "receive_a_token": decoded["receive_a_token"],
                    "borrower_hash": decoded["borrower_hash"],
                    "liquidator_hash": decoded["liquidator_hash"],
                    "graph_amount_usd": str(row["amountUSD"]),
                    "graph_timestamp_matches_rpc": graph_timestamp_matches,
                    "graph_tx_log_matches_rpc": True,
                    "source_retrieval": {
                        "discovery": "THE_GRAPH_MESSARI_AAVE_V3",
                        "verification": "ETHEREUM_ARCHIVE_RPC_LOG_RECEIPT_BLOCK",
                    },
                }
            )
        except Exception as exc:
            exclusions.append(
                {
                    "event_id": event_id,
                    "graph_block_number": block_number,
                    "graph_tx_hash": tx_hash,
                    "graph_log_index": log_index,
                    "status": "EXCLUDED",
                    "reason": str(exc),
                }
            )
    assert_unique_chain_order(events)
    return events, exclusions


def _merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def _subtract_intervals(
    requested: list[tuple[int, int]], covered: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    remaining: list[tuple[int, int]] = []
    merged_covered = _merge_intervals(covered)
    for start, end in _merge_intervals(requested):
        fragments = [(start, end)]
        for covered_start, covered_end in merged_covered:
            next_fragments: list[tuple[int, int]] = []
            for fragment_start, fragment_end in fragments:
                if covered_end < fragment_start or covered_start > fragment_end:
                    next_fragments.append((fragment_start, fragment_end))
                    continue
                if fragment_start < covered_start:
                    next_fragments.append((fragment_start, covered_start - 1))
                if covered_end < fragment_end:
                    next_fragments.append((covered_end + 1, fragment_end))
            fragments = next_fragments
        remaining.extend(fragments)
    return remaining


def _cached_swaps(
    requested: list[tuple[int, int]], invalid_root: Path
) -> tuple[list[dict[str, Any]], list[tuple[int, int]]]:
    swap_path = invalid_root / "raw_swap_index.json"
    event_path = invalid_root / "raw_event_index.json"
    selection_path = invalid_root / "episode_selection.json"
    if not swap_path.exists() or not event_path.exists() or not selection_path.exists():
        return [], requested
    invalid_events = json.loads(event_path.read_text(encoding="utf-8"))["events"]
    invalid_selection = json.loads(selection_path.read_text(encoding="utf-8"))["selected_episodes"]
    event_map = {event["event_id"]: event for event in invalid_events}
    covered = [
        (max(0, int(event["block_number"]) - 160), int(event["block_number"]) + 160)
        for event in invalid_events
    ]
    for cluster in invalid_selection:
        blocks = [int(event_map[event_id]["block_number"]) for event_id in cluster["event_ids"]]
        covered.append((max(0, min(blocks) - 460), max(blocks) - 140))
    merged_requested = _merge_intervals(requested)
    cached = [
        row
        for row in json.loads(swap_path.read_text(encoding="utf-8"))["swaps"]
        if any(start <= int(row["block_number"]) <= end for start, end in merged_requested)
    ]
    return cached, _subtract_intervals(requested, covered)


def _swap_price_usdc_weth(sqrt_price_x96: int) -> str:
    ratio = Decimal(sqrt_price_x96) / (Decimal(2) ** 96)
    return str((Decimal(10) ** 12) / (ratio * ratio))


def _collect_swaps(
    rpc: BudgetedRpc,
    pools: list[dict[str, Any]],
    intervals: list[tuple[int, int]],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    tasks: list[tuple[dict[str, Any], int, int]] = []
    for pool in pools:
        for start, end in _merge_intervals(intervals):
            for chunk_start in range(start, end + 1, 10):
                chunk_end = min(end, chunk_start + 9)
                tasks.append((pool, chunk_start, chunk_end))

    def fetch_logs(task: tuple[dict[str, Any], int, int]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        pool, chunk_start, chunk_end = task
        logs = rpc.call(
                    "eth_getLogs",
                    [
                        {
                            "address": pool["pool_address"],
                            "fromBlock": hex(chunk_start),
                            "toBlock": hex(chunk_end),
                            "topics": [SWAP_TOPIC],
                        }
                    ],
        )
        return pool, logs

    raw_logs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        for pool, logs in executor.map(fetch_logs, tasks):
                for log in logs:
                    raw_logs.append((pool, log))

    block_numbers = sorted({_hex_int(log["blockNumber"]) for _, log in raw_logs})
    with ThreadPoolExecutor(max_workers=2) as executor:
        blocks = executor.map(
            lambda number: rpc.call("eth_getBlockByNumber", [hex(number), False]),
            block_numbers,
        )
        block_cache = dict(zip(block_numbers, blocks, strict=True))

    for pool, log in raw_logs:
                    tx_hash = str(log["transactionHash"]).lower()
                    log_index = _hex_int(log["logIndex"])
                    if (tx_hash, log_index) in seen:
                        continue
                    seen.add((tx_hash, log_index))
                    block_number = _hex_int(log["blockNumber"])
                    block = block_cache[block_number]
                    decoded = decode_uniswap_swap(log)
                    timestamp = _hex_int(block["timestamp"])
                    swap_id = "swap-" + hashlib.sha256(
                        f"{CHAIN_ID}:{tx_hash}:{log_index}".encode()
                    ).hexdigest()[:20]
                    result.append(
                        {
                            "swap_id": swap_id,
                            "chain_id": CHAIN_ID,
                            "pool_address": str(pool["pool_address"]).lower(),
                            "fee": int(pool["fee"]),
                            "block_number": block_number,
                            "block_hash": str(block["hash"]).lower(),
                            "timestamp": timestamp,
                            "timestamp_utc": _iso(timestamp),
                            "tx_hash": tx_hash,
                            "log_index": log_index,
                            "amount0_raw": decoded["amount0_raw"],
                            "amount1_raw": decoded["amount1_raw"],
                            "weth_amount_abs": str(
                                normalize_amount(abs(decoded["amount1_raw"]), 18)
                            ),
                            "sqrt_price_x96": decoded["sqrt_price_x96"],
                            "price_usdc_per_weth": _swap_price_usdc_weth(
                                decoded["sqrt_price_x96"]
                            ),
                            "liquidity": decoded["liquidity"],
                            "tick": decoded["tick"],
                        }
                    )
    return sorted(result, key=lambda row: (row["block_number"], row["log_index"]))


def _episode_rows(
    clusters_by_window: dict[int, list[Any]],
    selected: list[Any],
    events: list[dict[str, Any]],
    swaps: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    event_map = {event["event_id"]: event for event in events}
    selected_ids = {cluster.cluster_id for cluster in selected}
    event_to_selected = {
        event_id: cluster.cluster_id for cluster in selected for event_id in cluster.event_ids
    }
    linkage: list[dict[str, Any]] = []
    for event in events:
        match = classify_linkage(event, swaps)
        linkage.append(
            {
                "event_id": event["event_id"],
                "episode_id": event_to_selected.get(event["event_id"]),
                **match,
                "causal_claim": False,
                "interpretation": (
                    "Receipt-level same-transaction path."
                    if match["tier"] == "DIRECT_TRANSACTION_LINK"
                    else "Quan sát lịch sử có liên hệ theo thời gian, chưa chứng minh vòng lây lan nội sinh"
                ),
            }
        )
    rows: list[dict[str, Any]] = []
    for cluster in clusters_by_window[300]:
        cluster_events_rows = [event_map[event_id] for event_id in cluster.event_ids]
        center = (cluster.start_timestamp + cluster.end_timestamp) // 2
        row: dict[str, Any] = {
            "episode_id": cluster.cluster_id,
            "selected_for_deep_review": cluster.cluster_id in selected_ids,
            "start_timestamp_utc": _iso(cluster.start_timestamp),
            "end_timestamp_utc": _iso(cluster.end_timestamp),
            "liquidation_count": len(cluster.event_ids),
            "debt_assets": ";".join(sorted({event["debt_symbol"] for event in cluster_events_rows})),
            "collateral_assets": ";".join(
                sorted({event["collateral_symbol"] for event in cluster_events_rows})
            ),
            "direct_transaction_links": sum(
                1
                for item in linkage
                if item["event_id"] in cluster.event_ids
                and item["tier"] == "DIRECT_TRANSACTION_LINK"
            ),
            "same_block_associations": sum(
                1
                for item in linkage
                if item["event_id"] in cluster.event_ids
                and item["tier"] == "SAME_BLOCK_ASSOCIATION"
            ),
            "time_window_associations": sum(
                1
                for item in linkage
                if item["event_id"] in cluster.event_ids
                and item["tier"] == "TIME_WINDOW_ASSOCIATION"
            ),
            "unlinked_or_unobservable": sum(
                1
                for item in linkage
                if item["event_id"] in cluster.event_ids
                and item["tier"] == "UNLINKED/UNOBSERVABLE"
            ),
        }
        for minutes in (1, 5, 15, 30):
            row[f"uniswap_swaps_within_{minutes}m"] = sum(
                abs(int(swap["timestamp"]) - center) <= minutes * 60 for swap in swaps
            )
            control_center = center - 60 * 60
            row[f"control_swaps_within_{minutes}m"] = (
                sum(
                    abs(int(swap["timestamp"]) - control_center) <= minutes * 60
                    for swap in swaps
                )
                if cluster.cluster_id in selected_ids
                else None
            )
        rows.append(row)
    return rows, linkage


def _oracle_observations(
    settings: Settings,
    selected: list[Any],
    events: list[dict[str, Any]],
    oracle_address: str,
    weth: str,
) -> list[dict[str, Any]]:
    event_map = {event["event_id"]: event for event in events}
    web3 = Web3(Web3.HTTPProvider(settings.eth_archive_rpc_url, request_kwargs={"timeout": 30}))
    oracle = web3.eth.contract(address=Web3.to_checksum_address(oracle_address), abi=ORACLE_ABI)
    rows: list[dict[str, Any]] = []
    for cluster in selected:
        blocks = [int(event_map[event_id]["block_number"]) for event_id in cluster.event_ids]
        for label, block in (
            ("pre", max(0, min(blocks) - 5)),
            ("event", min(blocks)),
            ("post", max(blocks) + 5),
        ):
            price = normalized_asset_price(oracle, Web3.to_checksum_address(weth), block)
            rows.append(
                {
                    "episode_id": cluster.cluster_id,
                    "phase": label,
                    "block_number": block,
                    "weth_oracle_price_usd": str(price),
                    "status": "PASS_RPC_ETH_CALL",
                }
            )
    return rows


def run(output_root: Path) -> dict[str, Any]:
    started = time.perf_counter()
    settings = Settings()
    if not settings.eth_archive_rpc_url:
        raise RuntimeError("ETH_ARCHIVE_RPC_URL is required for historical verification")
    graph = GraphClient(settings.graph_api_key, settings.aave_v3_subgraph_id)
    rpc = BudgetedRpc(ReadOnlyRpcClient(settings.eth_archive_rpc_url, timeout=30))
    if _hex_int(rpc.call("eth_chainId", [])) != CHAIN_ID:
        raise RuntimeError("archive RPC is not Ethereum Mainnet")
    addresses = load_aave_ethereum_address_book()
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    pools = [
        {"pool_address": pool["pool_address"], "fee": pool["fee"]}
        for pool in snapshot["dex_pools"]
    ]
    discovered = _discover(graph)
    events, exclusions = _verified_events(discovered, rpc, addresses.pool)
    clusters_by_window = {
        seconds: cluster_events(events, window_seconds=seconds)
        for seconds in (60, 300, 900, 1800)
    }
    graph_usd_values = [Decimal(str(event["graph_amount_usd"])) for event in events]
    usd_values_comparable = bool(graph_usd_values) and all(
        value.is_finite() and value >= 0 for value in graph_usd_values
    ) and max(graph_usd_values, default=Decimal(0)) < Decimal("100000000")
    # The indexer's amountUSD field is not used for selection because its amount/profit fields show
    # known unit inconsistencies for this deployment. The preregistered deterministic fallback applies.
    usd_values_comparable = False
    selected = select_episodes(
        clusters_by_window[300], max_episodes=5, usd_values_comparable=usd_values_comparable
    )
    intervals = [
        (max(0, int(event["block_number"]) - 160), int(event["block_number"]) + 160)
        for event in events
    ]
    # Include preregistered controls centered about one hour (300 blocks) earlier.
    intervals.extend(
        (
            max(0, min(int(event["block_number"]) for event in events if event["event_id"] in cluster.event_ids) - 460),
            max(int(event["block_number"]) for event in events if event["event_id"] in cluster.event_ids) - 140,
        )
        for cluster in selected
    )
    cached_swaps, missing_intervals = _cached_swaps(intervals, INVALID_EPOCH_ATTEMPT)
    collected_swaps = _collect_swaps(rpc, pools, missing_intervals) if missing_intervals else []
    swaps_by_key = {
        (row["tx_hash"], int(row["log_index"])): row
        for row in [*cached_swaps, *collected_swaps]
    }
    swaps = sorted(
        swaps_by_key.values(), key=lambda row: (row["block_number"], row["log_index"])
    )
    episode_rows, linkage = _episode_rows(clusters_by_window, selected, events, swaps)
    oracle_rows = _oracle_observations(
        settings, selected, events, addresses.oracle, addresses.weth
    )

    historical_root = output_root / "historical"
    raw_json = historical_root / "raw_event_index.json"
    raw_csv = historical_root / "raw_event_index.csv"
    _json(
        raw_json,
        {
            "status": "PASS",
            "source_commit": SOURCE_COMMIT,
            "chain_id": CHAIN_ID,
            "window": {"start": _iso(START_TIMESTAMP), "end_exclusive": _iso(END_TIMESTAMP)},
            "events": events,
        },
    )
    csv_rows = [
        {
            key: event[key]
            for key in (
                "event_id",
                "status",
                "chain_id",
                "block_number",
                "block_hash",
                "timestamp_utc",
                "tx_hash",
                "transaction_index",
                "log_index",
                "collateral_symbol",
                "debt_symbol",
                "debt_to_cover",
                "liquidated_collateral",
                "borrower_hash",
                "liquidator_hash",
            )
        }
        for event in events
    ]
    _csv(raw_csv, csv_rows)
    _json(historical_root / "raw_swap_index.json", {"status": "PASS", "swaps": swaps})
    _json(historical_root / "observation_linkage.json", {"status": "PASS", "rows": linkage})
    _csv(historical_root / "historical_event_study.csv", episode_rows)
    _csv(historical_root / "oracle_observations.csv", oracle_rows)
    selection = {
        "status": "PASS",
        "source_commit": SOURCE_COMMIT,
        "pre_registered_window": {"start": _iso(START_TIMESTAMP), "end_exclusive": _iso(END_TIMESTAMP)},
        "attempted_graph_rows": len(discovered),
        "rpc_verified_events": len(events),
        "excluded_events": exclusions,
        "primary_cluster_window_seconds": 300,
        "sensitivity_cluster_counts": {
            str(seconds): len(clusters) for seconds, clusters in clusters_by_window.items()
        },
        "usd_values_comparable_for_selection": False,
        "selection_rule_applied": "first five chronological 5-minute clusters; preregistered fallback",
        "selected_episodes": [
            {
                "episode_id": cluster.cluster_id,
                "start_timestamp_utc": _iso(cluster.start_timestamp),
                "end_timestamp_utc": _iso(cluster.end_timestamp),
                "event_ids": list(cluster.event_ids),
            }
            for cluster in selected
        ],
        "population_boundary": "event-level Aave V3 liquidations; not a historical borrower census",
    }
    _json(historical_root / "episode_selection.json", selection)
    tier_counts = Counter(row["tier"] for row in linkage)
    result = {
        "status": "LIMITED",
        "source_commit": SOURCE_COMMIT,
        "address_book": {
            "source": addresses.source_url,
            "version": addresses.version,
            "commit": addresses.commit,
            "pool": addresses.pool,
            "oracle": addresses.oracle,
        },
        "attempted": len(discovered),
        "verified": len(events),
        "excluded": len(exclusions),
        "selected_episodes": len(selected),
        "tier_counts": dict(tier_counts),
        "swap_count": len(swaps),
        "oracle_observation_count": len(oracle_rows),
        "rpc_calls": rpc.calls,
        "rpc_budget": rpc.limit,
        "cache_reuse": {
            "invalid_epoch_attempt_excluded_from_findings": True,
            "cached_swap_rows_reused_after_timestamp_filter": len(cached_swaps),
            "new_swap_rows_collected": len(collected_swaps),
            "missing_intervals_queried": len(missing_intervals),
        },
        "runtime_seconds": time.perf_counter() - started,
        "limitations": [
            "The Graph supplied deterministic discovery; every published liquidation was "
            "rechecked by RPC log, receipt and block hash.",
            "This is one preregistered calendar week and event-level coverage, not a full historical borrower census.",
            "Receipt-level linkage can establish a same-transaction path but cannot by itself "
            "prove market-wide endogenous causality.",
            "Graph amountUSD/profit fields showed unit inconsistencies and were excluded from episode ranking.",
            "Aave oracle states were sampled around selected episodes; underlying Chainlink "
            "AnswerUpdated logs were not enumerated.",
        ],
        "artifact_hashes": {
            raw_json.as_posix(): _sha256(raw_json),
            raw_csv.as_posix(): _sha256(raw_csv),
        },
    }
    _json(historical_root / "summary.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    if (args.output_dir / "historical" / "summary.json").exists():
        raise SystemExit("Refusing to overwrite existing Level-3 historical artifacts")
    result = run(args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
