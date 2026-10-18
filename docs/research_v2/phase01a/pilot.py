"""Read-only historical feasibility/pilot; no simulation or transaction methods."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path

from backend.app.adapters.rpc import ReadOnlyRpcClient


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def validate_header(raw: object, number: int, expected: str | None = None) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("MISSING_BLOCK_HEADER")
    if int(raw["number"], 16) != number:
        raise ValueError("BLOCK_NUMBER_MISMATCH")
    block_hash = raw["hash"].lower()
    if not block_hash.startswith("0x") or len(block_hash) != 66:
        raise ValueError("INVALID_BLOCK_HASH")
    int(block_hash[2:], 16)
    if expected is not None and block_hash != expected.lower():
        raise ValueError("BLOCK_HASH_MISMATCH")
    return {"number": number, "hash": block_hash, "timestamp": int(raw["timestamp"], 16),
            "parent_hash": raw["parentHash"].lower()}


def discover(registry: dict, output: Path) -> None:
    results = []
    for source in registry["providers"]:
        rpc = ReadOnlyRpcClient(source["url"], timeout=15)
        records = []
        result = {"provider_id": source["id"], "url": source["url"], "headers": [], "quarantine": []}
        try:
            chain = rpc.call("eth_chainId")
            records.append({"method": "eth_chainId", "params": [], "result": chain})
            if int(chain, 16) != 1:
                raise ValueError("CHAIN_ID_MISMATCH")
            finalized = rpc.call("eth_getBlockByNumber", ["finalized", False])
            records.append({"method": "eth_getBlockByNumber", "params": ["finalized", False], "result": finalized})
            if finalized is None:
                raise ValueError("FINALIZED_HEADER_UNAVAILABLE")
            result["finalized_number_at_collection"] = int(finalized["number"], 16)
            for block in registry["blocks"]:
                try:
                    if block["number"] > result["finalized_number_at_collection"]:
                        raise ValueError("BLOCK_NOT_FINALIZED")
                    params = [hex(block["number"]), False]
                    raw = rpc.call("eth_getBlockByNumber", params)
                    records.append({"method": "eth_getBlockByNumber", "params": params, "result": raw})
                    header = validate_header(raw, block["number"], block["expected_hash"])
                    result["headers"].append(header)
                except Exception as exc:
                    result["quarantine"].append({"block_number": block["number"], "reason": str(exc)[:1000]})
            result["status"] = "HEADERS_AVAILABLE" if len(result["headers"]) == 3 else "PARTIAL_OR_IDENTITY_CONFLICT"
        except Exception as exc:
            result["status"] = "DATA_ACCESS_BLOCKED"
            result["quarantine"].append({"reason": str(exc)[:1000]})
        result["transcript_sha256"] = digest(records)
        write_json(output / "raw" / f"discovery-{source['id']}.json", records)
        results.append(result)
    write_json(output / "discovery.json", {"registry_input_sha256": digest(registry),
               "source_commit": os.environ.get("GITHUB_SHA"), "run_id": os.environ.get("GITHUB_RUN_ID"),
               "collected_at_utc": datetime.now(UTC).isoformat(), "providers": results})
    print(json.dumps([{k: v for k, v in r.items() if k != "headers"} for r in results]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    discover(registry, args.output)


if __name__ == "__main__":
    main()
