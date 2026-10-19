"""Offline evidence validation; no network, simulation or scientific-output mutation."""
from __future__ import annotations

from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def main():
    root = Path(__file__).resolve().parent
    registry = read(root / "SAMPLE_REGISTRATION.json")
    blocks = {b["number"]: b for b in registry["blocks"]}
    hashes = {b["expected_hash"] for b in blocks.values()}
    counts = Counter()
    provenance = read(root / "EVIDENCE_PROVENANCE.json")
    for entry in provenance["files"]:
        raw = (root / entry["path"]).read_bytes()
        assert len(raw) == entry["size_bytes"] and digest(raw) == entry["sha256"]
        if "uncompressed_sha256" in entry:
            decoded = gzip.decompress(raw)
            assert len(decoded) == entry["uncompressed_size"] and digest(decoded) == entry["uncompressed_sha256"]
        counts["preserved_evidence_files_verified"] += 1
    for name in ["full", "borrower_repair"]:
        directory = root / "evidence" / name
        manifest = read(directory / "collection_manifest.json")
        original_input = read(directory / "REGISTERED_INPUT.json")
        assert digest(canonical(original_input)) == manifest["registration_canonical_sha256"]
        for row in manifest["files"]:
            raw = (directory / row["path"]).read_bytes()
            assert len(raw) == row["size_bytes"] and digest(raw) == row["sha256"], row["path"]
            if "uncompressed_sha256" in row:
                decoded = gzip.decompress(raw)
                assert len(decoded) == row["uncompressed_size"] and digest(decoded) == row["uncompressed_sha256"]
            counts["manifest_files_verified"] += 1
        for path in (directory / "raw").glob("*.gz"):
            for record in read(path):
                requests = [record["request"]] if "request" in record else record.get("requests", [])
                for request in requests:
                    if request["method"] == "eth_call":
                        selector = request["params"][1]
                        assert selector["blockHash"] in hashes and selector["requireCanonical"] is True
                        counts["pinned_state_request_records"] += 1
    full = root / "evidence/full"
    for block in blocks:
        for component in ["P3000", "P500", "oracle"]:
            left = read(full / f"components/{block}-pass1-{component}.json.gz")
            right = read(full / f"components/{block}-pass2-{component}.json.gz")
            assert left["status"] == right["status"] == "PASS" and left["data"] == right["data"]
            counts["deterministic_components"] += 1
            if component != "oracle":
                data = left["data"]
                assert not data["missing_words"] and not data["missing_ticks"]
                assert data["required_words"] == list(range(data["required_words"][0], data["required_words"][-1] + 1))
                assert data["initialized_ticks_expected"] == len(data["ticks"]) == len({r["tick"] for r in data["ticks"]})
                assert all(int(t["gross"]) >= abs(int(t["net"])) for t in data["ticks"])
                assert data["liquidity_audit"]["status"] == "PASS"
                counts["initialized_tick_instances"] += len(data["ticks"])
            else:
                for asset in left["data"]["assets"]:
                    assert asset["effective_price_check"] == asset["round_trace_status"] == "PASS"
                    trace = asset["trace"].get("asset_to_usd_upstream") or asset["trace"]
                    round_data = trace["round"]
                    assert 0 < round_data["started_at"] <= round_data["updated_at"] <= blocks[block]["timestamp_unix"]
                    counts["asset_block_oracle_traces"] += 1
    users = set()
    for block in blocks:
        directory = root / "evidence/borrower_repair"
        left = read(directory / f"components/{block}-pass1-borrowers.json.gz")
        right = read(directory / f"components/{block}-pass2-borrowers.json.gz")
        assert left["status"] == right["status"] == "PASS" and left["data"] == right["data"]
        data = left["data"]
        coverage = data["discovery_coverage"]
        headers = coverage["contiguous_headers"]
        assert coverage["window_blocks"] == len(headers) == 1024 and not coverage["missing_blocks"]
        assert headers[0]["number"] == block - 1023 and headers[-1]["hash"] == blocks[block]["expected_hash"]
        for prev, cur in zip(headers, headers[1:]):
            assert cur["number"] == prev["number"] + 1 and cur["parent_hash"] == prev["hash"]
            assert prev["timestamp"] < cur["timestamp"] <= blocks[block]["timestamp_unix"]
        header_map = {h["number"]: h["hash"] for h in headers}
        candidates = set()
        for event in data["discovery_logs"]:
            assert event["blockHash"] == header_map[int(event["blockNumber"], 16)] and not event.get("removed", False)
            candidates.add("0x" + event["topics"][2][-40:].lower())
        selected = sorted(candidates, key=lambda a: (digest(("1:" + a).encode()), a))[:8]
        assert selected == data["selected_users"]
        assert not data["reserve_id_coverage"]["missing_assets"]
        for account in data["portfolios"]:
            users.add(account["address"])
            assert account["block_hash"] == blocks[block]["expected_hash"] and not account["missing_data_flags"]
            assert account["user_configuration_raw"] is not None and account["user_emode"] is not None
            assert len(account["reserves"]) == data["reserves_count"]
            for reserve in account["reserves"]:
                assert reserve["status"] == reserve["source_status"] == reserve["token_decimals_status"] == "AVAILABLE"
                assert reserve["source"] is not None and reserve["configuration_raw"] is not None
                assert reserve["reserve_id"] is not None and reserve["price"] is not None
                assert reserve["data"][7] <= blocks[block]["timestamp_unix"]
            hf = account["hf_reconstruction"]
            assert hf["status"] == "PASS"
            assert int(hf["hf_difference_raw"]) == int(hf["collateral_base_difference"]) == int(hf["debt_base_difference"]) == 0
            counts["borrower_block_instances"] += 1
        counts["deterministic_components"] += 1
    assert read(full / "cross_provider_comparison.json")["overall"] == "INDEPENDENT_ARCHIVE_VALIDATION_BLOCKED"
    counts["unique_borrower_addresses"] = len(users)
    print(json.dumps({"offline_saved_evidence": "PASS", "counts": counts,
                      "independent_archive": "BLOCKED", "phase02_ready": False}, indent=2))


if __name__ == "__main__":
    main()
