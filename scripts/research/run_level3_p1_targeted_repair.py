from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import time
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from threading import Lock
from typing import Any

from backend.app.adapters.aave.address_book import load_aave_ethereum_address_book
from backend.app.adapters.rpc import ReadOnlyRpcClient, RpcError
from backend.app.config import Settings
from backend.app.services.snapshots import simulation_inputs
from scripts.research.run_deep_cascade_study import (
    MC_STAGES,
    PRIMARY_SEED,
    ROBUSTNESS_SEEDS,
    _scenario_payload,
    _worker_init,
    _worker_run,
    monte_carlo_draws,
)
from sim.engine.run import MODEL_VERSION, run_simulation
from sim.presets import scenario_presets
from sim.research.aave_suite import CANONICAL_SNAPSHOT, load_canonical_snapshot, sha256_file
from sim.research.historical_events import (
    LIQUIDATION_TOPIC,
    SWAP_TOPIC,
    TRANSFER_TOPIC,
    classify_linkage,
    decode_liquidation_log,
    decode_transfer_log,
    interval_is_covered,
    pseudonymize_address,
    reconcile_event_keys,
)
from sim.schemas import Scenario

D = Decimal
ROOT = Path("data/processed/research_final/level3_p1_targeted_repair")
LOCKED = Path("data/processed/research_final/level3_extension")
START_TIMESTAMP = 1_788_220_800
END_TIMESTAMP = 1_788_825_600
CHAIN_ID = 1
MAX_RPC_CALLS = 18_000
CHUNK_SIZE = 10
TRANSFER_EXACT_TOLERANCE_RAW = 0


def _json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _gzip_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(value, handle, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _stable_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hex_int(value: str | int | None) -> int:
    if value is None:
        return 0
    return int(value, 16) if isinstance(value, str) and value.startswith("0x") else int(value)


def _merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


class AuditRpc:
    def __init__(self, client: ReadOnlyRpcClient, limit: int = MAX_RPC_CALLS) -> None:
        self.client = client
        self.limit = limit
        self.calls = 0
        self._lock = Lock()

    def call(self, method: str, params: list[Any]) -> Any:
        with self._lock:
            if self.calls >= self.limit:
                raise RuntimeError(f"RPC budget exhausted at {self.calls}/{self.limit}")
            self.calls += 1
        for attempt in range(8):
            try:
                return self.client.call(method, params)
            except (RpcError, RuntimeError):
                if attempt == 7:
                    raise
                time.sleep(min(30.0, 2**attempt))
        raise AssertionError("unreachable")

    def call_once(self, method: str, params: list[Any]) -> Any:
        """Use once for deterministic capability errors that retrying cannot repair."""
        with self._lock:
            if self.calls >= self.limit:
                raise RuntimeError(f"RPC budget exhausted at {self.calls}/{self.limit}")
            self.calls += 1
        return self.client.call(method, params)


class BlockIndex:
    def __init__(self, rpc: AuditRpc) -> None:
        self.rpc = rpc
        self.blocks: dict[int, dict[str, Any]] = {}
        self._lock = Lock()

    def get(self, number: int) -> dict[str, Any]:
        with self._lock:
            cached = self.blocks.get(number)
        if cached is not None:
            return cached
        block = self.rpc.call("eth_getBlockByNumber", [hex(number), False])
        if block is None:
            raise RuntimeError(f"block {number} is unavailable")
        with self._lock:
            self.blocks[number] = block
        return block

    def timestamp(self, number: int) -> int:
        return _hex_int(self.get(number)["timestamp"])

    def first_at_or_after(self, timestamp: int, high: int) -> int:
        low = 0
        while low < high:
            middle = (low + high) // 2
            if self.timestamp(middle) < timestamp:
                low = middle + 1
            else:
                high = middle
        return low


def _log_key(log: dict[str, Any]) -> tuple[int, str, int]:
    return (
        _hex_int(log["blockNumber"]),
        str(log["transactionHash"]).lower(),
        _hex_int(log["logIndex"]),
    )


def _scan_logs(
    rpc: AuditRpc,
    *,
    address: str,
    topic: str,
    intervals: list[tuple[int, int]],
    workers: int = 2,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tasks = [
        (start, min(end, start + CHUNK_SIZE - 1))
        for interval_start, end in _merge_intervals(intervals)
        for start in range(interval_start, end + 1, CHUNK_SIZE)
    ]

    def fetch(task: tuple[int, int]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        start, end = task
        logs = rpc.call(
            "eth_getLogs",
            [
                {
                    "address": address,
                    "fromBlock": hex(start),
                    "toBlock": hex(end),
                    "topics": [topic],
                }
            ],
        )
        return {"from_block": start, "to_block": end, "log_count": len(logs)}, logs

    chunks: list[dict[str, Any]] = []
    logs: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for index, (chunk, found) in enumerate(executor.map(fetch, tasks), start=1):
            chunks.append(chunk)
            logs.extend(found)
            if index % 500 == 0:
                print(f"[P1] scanned {index}/{len(tasks)} log chunks", flush=True)
    unique = {_log_key(log): log for log in logs}
    return sorted(unique.values(), key=_log_key), chunks


def _census_audit(
    output: Path,
    rpc: AuditRpc,
    blocks: BlockIndex,
    pool: str,
    graph_events: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    latest = _hex_int(rpc.call("eth_blockNumber", []))
    start_block = blocks.first_at_or_after(START_TIMESTAMP, latest)
    end_block = blocks.first_at_or_after(END_TIMESTAMP, latest) - 1
    logs, chunks = _scan_logs(
        rpc,
        address=pool,
        topic=LIQUIDATION_TOPIC,
        intervals=[(start_block, end_block)],
    )
    census_events: list[dict[str, Any]] = []
    for log in logs:
        block_number, tx_hash, log_index = _log_key(log)
        block = blocks.get(block_number)
        if str(log["blockHash"]).lower() != str(block["hash"]).lower():
            raise ValueError("census log block hash does not match canonical block")
        census_events.append(
            {
                "block_number": block_number,
                "block_hash": str(block["hash"]).lower(),
                "timestamp": _hex_int(block["timestamp"]),
                "tx_hash": tx_hash,
                "log_index": log_index,
            }
        )
    reconciliation = reconcile_event_keys(graph_events, census_events)
    raw_by_key = {_log_key(log): log for log in logs}
    rpc_only_details: list[dict[str, Any]] = []
    for key in reconciliation["rpc_only"]:
        block_number, tx_hash, log_index = key
        decoded = decode_liquidation_log(raw_by_key[key])
        receipt = rpc.call("eth_getTransactionReceipt", [tx_hash])
        rpc_only_details.append(
            {
                "block_number": block_number,
                "block_hash": str(blocks.get(block_number)["hash"]).lower(),
                "timestamp": blocks.timestamp(block_number),
                "tx_hash": tx_hash,
                "transaction_index": _hex_int(receipt.get("transactionIndex")),
                "log_index": log_index,
                "receipt_status": _hex_int(receipt.get("status")),
                **decoded,
            }
        )
    cache_path = output / "historical" / "census_cache.json.gz"
    _gzip_json(
        cache_path,
        {
            "status": "PASS",
            "pool": pool.lower(),
            "topic": LIQUIDATION_TOPIC,
            "start_block": start_block,
            "end_block": end_block,
            "chunks": chunks,
            "events": census_events,
        },
    )
    result = {
        "status": (
            "PASS"
            if not reconciliation["graph_only"] and not reconciliation["rpc_only"]
            else "PASS_WITH_DISCLOSED_DISCREPANCY"
        ),
        "census_execution_status": "PASS",
        "reconciliation_status": (
            "MATCH" if not reconciliation["graph_only"] and not reconciliation["rpc_only"] else "DISCREPANCY"
        ),
        "scope": "independent full-window Aave V3 Pool LiquidationCall log census",
        "window": {"start_timestamp": START_TIMESTAMP, "end_timestamp_exclusive": END_TIMESTAMP},
        "start_block": start_block,
        "start_block_hash": str(blocks.get(start_block)["hash"]).lower(),
        "end_block": end_block,
        "end_block_hash": str(blocks.get(end_block)["hash"]).lower(),
        "chunk_size_blocks": CHUNK_SIZE,
        "chunks_scanned": len(chunks),
        "graph_candidate_count": len(graph_events),
        "rpc_census_count": len(census_events),
        "matched_count": len(reconciliation["matched"]),
        "graph_only": reconciliation["graph_only"],
        "rpc_only": reconciliation["rpc_only"],
        "rpc_only_details": rpc_only_details,
        "graph_recall_against_rpc_census": (
            len(reconciliation["matched"]) / len(census_events) if census_events else None
        ),
        "cache_path": cache_path.as_posix(),
        "cache_sha256": _file_sha256(cache_path),
        "interpretation": (
            "The independent Pool log census completed for the full window. Any Graph/RPC "
            "discrepancy is retained explicitly; this is not a borrower-state census."
        ),
    }
    _json(output / "historical" / "census_reconciliation.json", result)
    return result, census_events


def _trace_status(rpc: AuditRpc, tx_hash: str) -> dict[str, Any]:
    try:
        trace = rpc.call_once(
            "debug_traceTransaction",
            [tx_hash, {"tracer": "callTracer", "timeout": "20s"}],
        )

        def count_calls(node: dict[str, Any]) -> int:
            return 1 + sum(count_calls(child) for child in node.get("calls", []))

        return {"status": "PASS", "call_count": count_calls(trace)}
    except Exception as exc:
        message = str(exc)
        if "debug_traceTransaction is not available" in message:
            message = "debug_traceTransaction is unavailable on the configured RPC tier"
        return {
            "status": "UNAVAILABLE",
            "reason": message[:500],
        }


def _exact_transfer_path(
    *,
    event: dict[str, Any],
    receipt: dict[str, Any],
    swaps: list[dict[str, Any]],
) -> tuple[list[str], dict[str, Any]]:
    transfers = [
        decode_transfer_log(log)
        for log in receipt["logs"]
        if log.get("topics") and str(log["topics"][0]).lower() == TRANSFER_TOPIC.lower()
    ]
    collateral = str(event["collateral_asset"]).lower()
    amount = int(event["liquidated_collateral_raw"])
    event_index = int(event["log_index"])
    liquidator_hash = str(event["liquidator_hash"])
    inbound = [
        transfer
        for transfer in transfers
        if transfer["token"] == collateral
        and transfer["amount_raw"] == amount
        and transfer["log_index"] < event_index
        and pseudonymize_address(transfer["to"]) == liquidator_hash
    ]
    verified_swap_ids: list[str] = []
    route_rows: list[dict[str, Any]] = []
    for swap in swaps:
        if int(swap["amount1_raw"]) <= 0 or int(swap["log_index"]) <= event_index:
            continue
        swap_amount = int(swap["amount1_raw"])
        pool = str(swap["pool_address"]).lower()
        exact_amount = abs(swap_amount - amount) <= TRANSFER_EXACT_TOLERANCE_RAW
        route: list[dict[str, Any]] = []
        if inbound and exact_amount:
            start_address = inbound[-1]["to"]
            eligible = [
                transfer
                for transfer in transfers
                if transfer["token"] == collateral
                and transfer["amount_raw"] == amount
                and inbound[-1]["log_index"] < transfer["log_index"] < int(swap["log_index"])
            ]
            queue: deque[tuple[str, list[dict[str, Any]]]] = deque([(start_address, [])])
            visited = {start_address}
            while queue and not route:
                address, path = queue.popleft()
                for transfer in eligible:
                    if transfer["from"] != address:
                        continue
                    next_path = [*path, transfer]
                    if transfer["to"] == pool:
                        route = next_path
                        break
                    if transfer["to"] not in visited:
                        visited.add(transfer["to"])
                        queue.append((transfer["to"], next_path))
        if route:
            verified_swap_ids.append(str(swap["swap_id"]))
        route_rows.append(
            {
                "swap_id": swap["swap_id"],
                "swap_log_index": int(swap["log_index"]),
                "weth_direction": "INTO_POOL" if int(swap["amount1_raw"]) > 0 else "OUT_OF_POOL",
                "swap_weth_raw": abs(int(swap["amount1_raw"])),
                "liquidated_collateral_raw": amount,
                "exact_amount_match": exact_amount,
                "ordered_exact_transfer_path": bool(route),
                "transfer_path": [
                    {
                        "log_index": transfer["log_index"],
                        "from_hash": pseudonymize_address(transfer["from"]),
                        "to_hash": pseudonymize_address(transfer["to"]),
                        "amount_raw": transfer["amount_raw"],
                    }
                    for transfer in route
                ],
            }
        )
    audit = {
        "event_id": event["event_id"],
        "tx_hash": event["tx_hash"],
        "liquidation_log_index": event_index,
        "collateral_symbol": event["collateral_symbol"],
        "liquidated_collateral_raw": amount,
        "exact_inbound_collateral_transfer": bool(inbound),
        "inbound_transfer_log_indices": [transfer["log_index"] for transfer in inbound],
        "verified_transfer_swap_ids": verified_swap_ids,
        "swap_route_checks": route_rows,
        "criterion": (
            "Exact collateral amount, ordered receipt Transfer path from the liquidation "
            "recipient to the declared Uniswap pool, followed by the matched Swap log."
        ),
    }
    return verified_swap_ids, audit


def _linkage_audit(
    output: Path,
    rpc: AuditRpc,
    events: list[dict[str, Any]],
    swaps: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    swaps_by_tx: dict[str, list[dict[str, Any]]] = {}
    for swap in swaps:
        swaps_by_tx.setdefault(str(swap["tx_hash"]).lower(), []).append(swap)
    route_audits: list[dict[str, Any]] = []
    verified_by_event: dict[str, list[str]] = {}
    trace_by_tx: dict[str, dict[str, Any]] = {}
    candidate_events = [event for event in events if event["tx_hash"] in swaps_by_tx]
    receipts: dict[str, dict[str, Any]] = {}
    for event in candidate_events:
        tx_hash = str(event["tx_hash"])
        receipt = receipts.setdefault(
            tx_hash, rpc.call("eth_getTransactionReceipt", [tx_hash])
        )
        verified, audit = _exact_transfer_path(
            event=event,
            receipt=receipt,
            swaps=swaps_by_tx[tx_hash],
        )
        verified_by_event[event["event_id"]] = verified
        route_audits.append(audit)
        if tx_hash not in trace_by_tx:
            trace_by_tx[tx_hash] = _trace_status(rpc, tx_hash)
    linkage_rows: list[dict[str, Any]] = []
    for event in events:
        match = classify_linkage(
            event,
            swaps,
            verified_transfer_swap_ids=verified_by_event.get(event["event_id"], []),
        )
        linkage_rows.append(
            {
                "event_id": event["event_id"],
                **match,
                "causal_claim": False,
                "interpretation": (
                    "Receipt Transfer path verified; this remains transaction-level route "
                    "evidence, not proof of market-wide endogenous causality."
                    if match["tier"] == "DIRECT_TRANSFER_PATH_VERIFIED"
                    else "Association/co-occurrence only; no endogenous causal claim."
                ),
            }
        )
    result = {
        "status": "PASS",
        "tier_counts": dict(Counter(row["tier"] for row in linkage_rows)),
        "trace_status_by_transaction": trace_by_tx,
        "route_audits": route_audits,
        "linkage_rows": linkage_rows,
        "previous_claim_correction": (
            "Same transaction alone is no longer classified as direct. Only an exact, ordered "
            "collateral Transfer path into the matched pool qualifies."
        ),
    }
    _json(output / "historical" / "linkage_route_audit.json", result)
    return result, linkage_rows


def _control_window_audit(
    output: Path,
    rpc: AuditRpc,
    blocks: BlockIndex,
    pools: list[str],
    selected: list[dict[str, Any]],
    graph_events: list[dict[str, Any]],
    census_events: list[dict[str, Any]],
    locked_swaps: list[dict[str, Any]],
) -> dict[str, Any]:
    event_map = {event["event_id"]: event for event in graph_events}
    centers = {
        episode["episode_id"]: sum(
            int(event_map[event_id]["timestamp"]) for event_id in episode["event_ids"]
        )
        // len(episode["event_ids"])
        for episode in selected
    }
    latest = _hex_int(rpc.call("eth_blockNumber", []))
    requested: dict[tuple[str, str], tuple[int, int]] = {}
    for episode_id, center in centers.items():
        for kind, window_center in (("event", center), ("control", center - 3600)):
            start = blocks.first_at_or_after(window_center - 1800, latest)
            end = blocks.first_at_or_after(window_center + 1800 + 1, latest) - 1
            requested[(episode_id, kind)] = (start, end)
    merged = _merge_intervals(list(requested.values()))
    all_logs: list[dict[str, Any]] = []
    scanned_by_pool: dict[str, list[tuple[int, int]]] = {}
    chunk_count = 0
    for pool in pools:
        logs, chunks = _scan_logs(
            rpc,
            address=pool,
            topic=SWAP_TOPIC,
            intervals=merged,
        )
        all_logs.extend(logs)
        scanned_by_pool[pool.lower()] = [
            (int(chunk["from_block"]), int(chunk["to_block"])) for chunk in chunks
        ]
        chunk_count += len(chunks)
    scanned_swaps: dict[tuple[str, int], dict[str, Any]] = {}
    for log in all_logs:
        block_number, tx_hash, log_index = _log_key(log)
        scanned_swaps[(tx_hash, log_index)] = {
            "block_number": block_number,
            "timestamp": blocks.timestamp(block_number),
            "tx_hash": tx_hash,
            "log_index": log_index,
        }
    rows: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for episode_id, center in centers.items():
        for kind, window_center in (("event", center), ("control", center - 3600)):
            block_start, block_end = requested[(episode_id, kind)]
            complete = all(
                interval_is_covered(block_start, block_end, scanned_by_pool[pool.lower()])
                for pool in pools
            )
            for minutes in (1, 5, 15, 30):
                seconds = minutes * 60
                scanned_keys = {
                    key
                    for key, swap in scanned_swaps.items()
                    if abs(int(swap["timestamp"]) - window_center) <= seconds
                }
                locked_keys = {
                    (str(swap["tx_hash"]).lower(), int(swap["log_index"]))
                    for swap in locked_swaps
                    if abs(int(swap["timestamp"]) - window_center) <= seconds
                }
                liquidation_count = sum(
                    abs(int(event["timestamp"]) - window_center) <= seconds
                    for event in census_events
                )
                row = {
                    "episode_id": episode_id,
                    "window_kind": kind,
                    "center_offset_seconds_from_event": 0 if kind == "event" else -3600,
                    "half_width_minutes": minutes,
                    "block_start": block_start,
                    "block_end": block_end,
                    "all_four_pool_block_ranges_scanned": complete,
                    "rescanned_swap_count": len(scanned_keys),
                    "locked_index_swap_count": len(locked_keys),
                    "missing_from_locked_index": len(scanned_keys - locked_keys),
                    "extra_in_locked_index": len(locked_keys - scanned_keys),
                    "liquidation_count": liquidation_count,
                    "liquidation_free_control": kind != "control" or liquidation_count == 0,
                }
                rows.append(row)
                if kind == "control" and minutes == 30 and liquidation_count:
                    exclusions.append(
                        {
                            "episode_id": episode_id,
                            "reason": "control ±30 minute window contains an Aave liquidation",
                        }
                    )
    status = "PASS" if all(
        row["all_four_pool_block_ranges_scanned"]
        and row["missing_from_locked_index"] == 0
        and row["extra_in_locked_index"] == 0
        for row in rows
    ) else "FAIL"
    result = {
        "status": status,
        "pool_count": len(pools),
        "exact_log_scan_chunk_count": chunk_count,
        "declared_control_offset_seconds": -3600,
        "rows": rows,
        "control_exclusions": exclusions,
        "all_30m_controls_liquidation_free": not exclusions,
        "swap_universe_boundary": (
            "Counts cover the four declared WETH/USDC pools only inside exact event/control "
            "windows; they are not a full-week exchange universe."
        ),
    }
    _json(output / "historical" / "control_window_audit.json", result)
    return result


def _validate_legacy_checkpoint(
    path: Path,
    *,
    label: str,
    seed: int,
    target: int,
    expected_scenario: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _load(path)
    rows = payload.get("rows", [])
    paths = payload.get("cascade_paths", [])
    errors: list[str] = []
    for key, expected in {
        "status": "PASS",
        "label": label,
        "seed": seed,
        "target": target,
        "completed": target,
        "scenario": expected_scenario,
    }.items():
        if payload.get(key) != expected:
            errors.append(f"{key} mismatch")
    indices = [int(row.get("path_index", -1)) for row in rows]
    if indices != list(range(target)):
        errors.append("path indices are not ordered, unique, and complete")
    if any(int(row.get("path_seed", -1)) != seed + index for index, row in enumerate(rows)):
        errors.append("path seeds do not equal seed + path_index")
    if len(rows) != target:
        errors.append("row count differs from target")
    validation = {
        "status": "PASS" if not errors else "FAIL",
        "path": path.as_posix(),
        "label": label,
        "seed": seed,
        "target": target,
        "validated_path_count": len(rows) if not errors else 0,
        "file_sha256": _file_sha256(path),
        "rows_sha256": _stable_sha256(rows),
        "cascade_paths_sha256": _stable_sha256(paths),
        "scenario_sha256": _stable_sha256(expected_scenario),
        "canonical_snapshot_sha256": sha256_file(CANONICAL_SNAPSHOT),
        "model_version": MODEL_VERSION,
        "embedded_canonical_model_attestation": False,
        "external_attestation_method": (
            "Locked file hash + exact scenario/seed/index validation + independent deterministic "
            "sample reproduction against the locked canonical snapshot and current model version."
        ),
        "errors": errors,
    }
    return validation, payload


def _eligibility_rows(
    result: Any, positions: list[Any], reference_price: D, scenario: Scenario
) -> list[dict[str, Any]]:
    liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
    wave2 = [event for event in liquidations if int(event.wave) == 2]
    if not wave2:
        return []
    position_map = {position.borrower_hash: position for position in positions}
    wave2_start_price = min(reference_price, D(str(wave2[0].dex_price_before)))
    rows: list[dict[str, Any]] = []
    for event in wave2:
        position = position_map[str(event.borrower_hash)]
        direct_hf = position.health_factor(
            reference_price,
            scenario.liquidation_threshold_override,
            scenario.usdc_price_usd,
        )
        prior_wave_hf = position.health_factor(
            wave2_start_price,
            scenario.liquidation_threshold_override,
            scenario.usdc_price_usd,
        )
        rows.append(
            {
                "borrower_hash": event.borrower_hash,
                "direct_shock_reference_price": str(reference_price),
                "direct_shock_hf": str(direct_hf),
                "prior_wave_post_arbitrage_valuation_price": str(wave2_start_price),
                "hf_at_prior_wave_price": str(prior_wave_hf),
                "event_health_factor_before": str(event.health_factor_before),
                "direct_shock_not_eligible": direct_hf >= 1,
                "newly_eligible_after_prior_wave": prior_wave_hf < 1,
                "event_hf_no_greater_than_wave_start_hf": event.health_factor_before <= prior_wave_hf,
            }
        )
    return rows


def _monte_carlo_audit(output: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    snapshot = load_canonical_snapshot()
    positions, dex, initial_price = simulation_inputs(snapshot)
    presets = scenario_presets()
    severe = replace(presets["Severe"], max_waves=100, horizon_steps=120)
    low = replace(presets["Low Liquidity"], max_waves=100, horizon_steps=120)
    checkpoint_root = LOCKED / "deep_stress" / "checkpoints"
    specifications: list[tuple[Path, str, int, int, Scenario]] = []
    for target in MC_STAGES:
        specifications.append(
            (
                checkpoint_root / f"severe_seed_{PRIMARY_SEED}_{target}.json",
                "Severe",
                PRIMARY_SEED,
                target,
                severe,
            )
        )
    for seed in ROBUSTNESS_SEEDS[1:]:
        specifications.append(
            (
                checkpoint_root / f"severe_seed_{seed}_1000.json",
                "Severe seed robustness",
                seed,
                1000,
                severe,
            )
        )
    specifications.append(
        (
            checkpoint_root / f"low_liquidity_seed_{PRIMARY_SEED}_1000.json",
            "Low Liquidity prespecified",
            PRIMARY_SEED,
            1000,
            low,
        )
    )
    validations: list[dict[str, Any]] = []
    payloads: dict[tuple[str, int, int], dict[str, Any]] = {}
    for path, label, seed, target, scenario in specifications:
        validation, payload = _validate_legacy_checkpoint(
            path,
            label=label,
            seed=seed,
            target=target,
            expected_scenario=_scenario_payload(scenario),
        )
        validations.append(validation)
        payloads[(label, seed, target)] = payload
    primary = payloads[("Severe", PRIMARY_SEED, 10_000)]
    prefix_checks: list[dict[str, Any]] = []
    for target in MC_STAGES[:-1]:
        prefix_rows = payloads[("Severe", PRIMARY_SEED, target)]["rows"]
        expected_rows = primary["rows"][:target]
        prefix_checks.append(
            {
                "target": target,
                "prefix_rows_sha256": _stable_sha256(prefix_rows),
                "primary_prefix_sha256": _stable_sha256(expected_rows),
                "identical": prefix_rows == expected_rows,
            }
        )
    independent_batches = [
        ("Severe", PRIMARY_SEED, 10_000),
        ("Severe seed robustness", ROBUSTNESS_SEEDS[1], 1000),
        ("Severe seed robustness", ROBUSTNESS_SEEDS[2], 1000),
        ("Low Liquidity prespecified", PRIMARY_SEED, 1000),
    ]
    identities: set[tuple[str, int, int]] = set()
    duplicate_identities: list[tuple[str, int, int]] = []
    for label, seed, target in independent_batches:
        scenario_hash = _stable_sha256(payloads[(label, seed, target)]["scenario"])
        for row in payloads[(label, seed, target)]["rows"]:
            identity = (scenario_hash + f":{label}", seed, int(row["path_index"]))
            if identity in identities:
                duplicate_identities.append(identity)
            identities.add(identity)
    fixed_indices = list(range(0, 10_000, 1000)) + [9999]
    depth2_rows = [row for row in primary["rows"] if int(row["cascade_depth"]) >= 2]
    stratified_indices: list[int] = []
    for start in range(0, 10_000, 1000):
        candidate = next(
            row for row in depth2_rows if start <= int(row["path_index"]) < start + 1000
        )
        stratified_indices.append(int(candidate["path_index"]))
    sample_indices = sorted(set(fixed_indices + stratified_indices))
    draws = monte_carlo_draws(severe, PRIMARY_SEED, 10_000)
    _worker_init(str(CANONICAL_SNAPSHOT))
    sample_rows: list[dict[str, Any]] = []
    wave2_samples: list[dict[str, Any]] = []
    for index in sample_indices:
        reproduced, _ = _worker_run((index, draws[index]))
        stored = primary["rows"][index]
        sample_rows.append(
            {
                "path_index": index,
                "selection": (
                    "fixed_decile_boundary" if index in fixed_indices else "first_depth2_in_decile"
                ),
                "stored_row_sha256": _stable_sha256(stored),
                "reproduced_row_sha256": _stable_sha256(reproduced),
                "exact_match": stored == reproduced,
            }
        )
        if index in stratified_indices:
            result = run_simulation(
                positions,
                dex,
                initial_price,
                draws[index],
                run_id=f"level3-p1-wave2-{index}",
            )
            reference = initial_price * (D(1) + draws[index].shock_pct / D(100))
            eligibility = _eligibility_rows(result, positions, reference, draws[index])
            wave2_samples.append(
                {
                    "path_index": index,
                    "decile_start": (index // 1000) * 1000,
                    "wave2_borrowers": eligibility,
                    "all_genuinely_newly_eligible": bool(eligibility)
                    and all(
                        row["direct_shock_not_eligible"]
                        and row["newly_eligible_after_prior_wave"]
                        for row in eligibility
                    ),
                }
            )
    deterministic = replace(
        Scenario(name="P1 deterministic depth2", max_waves=100, horizon_steps=120),
        shock_pct=D("-40"),
        liquidity_haircut_pct=D("90"),
    )
    deterministic_result = run_simulation(
        positions,
        dex,
        initial_price,
        deterministic,
        run_id="level3-p1-deterministic-wave2",
    )
    deterministic_reference = initial_price * (D(1) + deterministic.shock_pct / D(100))
    deterministic_eligibility = _eligibility_rows(
        deterministic_result, positions, deterministic_reference, deterministic
    )
    checkpoint_result = {
        "status": "PASS" if all(row["status"] == "PASS" for row in validations) else "FAIL",
        "canonical_snapshot_sha256": sha256_file(CANONICAL_SNAPSHOT),
        "model_version": MODEL_VERSION,
        "validations": validations,
        "primary_prefix_checks": prefix_checks,
        "independent_batch_unique_path_count": len(identities),
        "expected_independent_batch_unique_path_count": 13_000,
        "duplicate_batch_identities": duplicate_identities,
        "accounting_correction": {
            "locked_checkpoint_rows_validated": 13_000,
            "large_paths_executed_in_this_repair_invocation": 0,
            "independent_sample_paths_executed_in_this_repair_invocation": len(sample_indices),
            "reused_checkpoint_count_for_primary_10k": 10_000,
            "historical_execution_duration_seconds": "UNAVAILABLE_NOT_EMBEDDED_IN_LEGACY_CHECKPOINT",
            "prohibited_claim": "The previous ~0.006 second restore time is not 10k execution time.",
        },
    }
    sample_result = {
        "status": "PASS" if all(row["exact_match"] for row in sample_rows) else "FAIL",
        "sampling_rule": (
            "Fixed 1,000-index boundaries plus the first depth>=2 path in each 1,000-index "
            "stratum; selected without optimizing any metric."
        ),
        "sample_rows": sample_rows,
    }
    wave_result = {
        "status": "PASS"
        if deterministic_eligibility
        and all(
            row["direct_shock_not_eligible"] and row["newly_eligible_after_prior_wave"]
            for row in deterministic_eligibility
        )
        and all(row["all_genuinely_newly_eligible"] for row in wave2_samples)
        else "FAIL",
        "definition": (
            "A wave-2 borrower must have HF >= 1 at the direct-shock reference price and HF < 1 "
            "at the post-wave-1/post-arbitrage valuation price used to start wave 2."
        ),
        "deterministic_case": {
            "shock_pct": -40,
            "liquidity_haircut_pct": 90,
            "observed_depth": int(deterministic_result.metrics["cascade_depth"] or 0),
            "wave2_borrowers": deterministic_eligibility,
        },
        "stratified_monte_carlo_cases": wave2_samples,
    }
    _json(output / "monte_carlo" / "checkpoint_validation.json", checkpoint_result)
    _json(output / "monte_carlo" / "sample_reproduction.json", sample_result)
    _json(output / "monte_carlo" / "wave2_eligibility_audit.json", wave_result)
    return checkpoint_result, wave_result


def run(output: Path) -> dict[str, Any]:
    started = time.perf_counter()
    settings = Settings()
    rpc_url = settings.eth_archive_rpc_url or settings.eth_rpc_url
    if not rpc_url:
        raise RuntimeError("Ethereum archive/mainnet RPC is required")
    rpc = AuditRpc(ReadOnlyRpcClient(rpc_url, timeout=30))
    if _hex_int(rpc.call("eth_chainId", [])) != CHAIN_ID:
        raise RuntimeError("RPC is not Ethereum Mainnet")
    blocks = BlockIndex(rpc)
    addresses = load_aave_ethereum_address_book()
    raw_events_payload = _load(LOCKED / "historical" / "raw_event_index.json")
    graph_events = raw_events_payload["events"]
    with gzip.open(
        LOCKED / "historical" / "raw_swap_index.json.gz", "rt", encoding="utf-8"
    ) as handle:
        locked_swaps = json.load(handle)["swaps"]
    selection = _load(LOCKED / "historical" / "episode_selection.json")
    snapshot = _load(Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json"))
    pools = [str(pool["pool_address"]).lower() for pool in snapshot["dex_pools"]]

    census, census_events = _census_audit(
        output, rpc, blocks, addresses.pool, graph_events
    )
    linkage, linkage_rows = _linkage_audit(output, rpc, graph_events, locked_swaps)
    controls = _control_window_audit(
        output,
        rpc,
        blocks,
        pools,
        selection["selected_episodes"],
        graph_events,
        census_events,
        locked_swaps,
    )
    checkpoints, wave2 = _monte_carlo_audit(output)
    evidence_matrix = {
        "status": "LIMITED",
        "gates": [
            {"gate": "full-window Pool log census", "status": census["status"]},
            {"gate": "receipt transfer-route semantics", "status": linkage["status"]},
            {"gate": "exact control-window completeness", "status": controls["status"]},
            {"gate": "checkpoint provenance", "status": checkpoints["status"]},
            {"gate": "wave-2 newly eligible semantics", "status": wave2["status"]},
            {"gate": "local Mainnet fork transactions", "status": "UNAVAILABLE"},
        ],
        "historical_claim_boundary": (
            "Historical clusters are timestamp groupings and are not modeled newly-eligible waves."
        ),
        "causal_boundary": (
            "Receipt routes and temporal associations do not prove endogenous historical contagion."
        ),
        "tail_boundary": (
            "90%/95% liquidity haircuts are unobserved counterfactual tails."
        ),
        "loss_boundary": (
            "Uncovered debt + liquidated repayment is a composite model output, not realized "
            "economic loss and not market Expected Shortfall."
        ),
    }
    _json(output / "evidence_matrix.json", evidence_matrix)
    claim_ledger = {
        "status": "PASS",
        "corrections": [
            {
                "old": "Any same-transaction Uniswap swap was DIRECT_TRANSACTION_LINK.",
                "new": (
                    "Only an exact ordered collateral Transfer path is direct; otherwise "
                    "SAME_TRANSACTION_CO_OCCURRENCE."
                ),
            },
            {
                "old": "27/27 candidate verification implied full-week completeness.",
                "new": "Graph candidates are reported separately from an independent Pool log census.",
            },
            {
                "old": "10k restored checkpoint runtime could be read as execution duration.",
                "new": "Validated/reused/executed-now counts are separate; legacy historical duration is unavailable.",
            },
            {
                "old": "Composite tail mean was labeled Expected Shortfall.",
                "new": "It is a composite modeled tail mean, not realized loss or market ES.",
            },
        ],
    }
    _json(output / "claim_ledger_repair.json", claim_ledger)
    summary = {
        "status": "LIMITED",
        "commander_review_comment": "issuecomment-6152110805",
        "source_head": "26cd58489d726a6c98678c725650020edcc1a3f4",
        "canonical_snapshot_sha256": sha256_file(CANONICAL_SNAPSHOT),
        "locked_level3_bundle_sha256": _file_sha256(LOCKED / "manifest.json"),
        "census_status": census["status"],
        "linkage_tier_counts": linkage["tier_counts"],
        "control_window_status": controls["status"],
        "checkpoint_status": checkpoints["status"],
        "wave2_eligibility_status": wave2["status"],
        "rpc_calls": rpc.calls,
        "rpc_budget": rpc.limit,
        "runtime_seconds": time.perf_counter() - started,
        "large_research_rerun": False,
        "fork_status": "UNAVAILABLE_UNCHANGED",
    }
    _json(output / "summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT)
    args = parser.parse_args()
    if (args.output_dir / "summary.json").exists():
        raise SystemExit("Refusing to overwrite completed P1 targeted-repair artifacts")
    result = run(args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
