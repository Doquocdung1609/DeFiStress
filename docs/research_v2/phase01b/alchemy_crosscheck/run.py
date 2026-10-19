"""Credential-safe Alchemy versus dRPC historical state comparison.

Does not persist endpoint URL, API key, raw transport records or exception messages.
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

from docs.research_v2.phase01b import collector as core


def canonical_hash(data: object) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()


def compare(expected: dict, observed: dict) -> dict:
    previous = expected.get("data") or {}
    current = observed.get("data") or {}
    old_fields = previous.get("fields") or {}
    new_fields = current.get("fields") or {}
    matches = sum(key in new_fields and new_fields[key] == value for key, value in old_fields.items())
    mismatches = sorted(key for key, value in old_fields.items()
                        if key in new_fields and new_fields[key] != value)
    missing = sorted(key for key in old_fields if key not in new_fields)
    extra = sorted(key for key in new_fields if key not in old_fields)
    return {"agreeing_fields": matches, "mismatch_fields": mismatches,
            "missing_fields": missing, "additional_fields": extra,
            "reference_field_count": len(old_fields), "observed_field_count": len(new_fields),
            "observed_fields_sha256": canonical_hash(new_fields) if new_fields else None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    url = os.environ.get("ALCHEMY_ETH_RPC_URL", "")
    if not url or urlsplit(url).scheme.lower() != "https" or not urlsplit(url).hostname:
        print("BLOCKED: RPC secret missing or HTTPS URL invalid (value not disclosed)", flush=True)
        return 2
    directory = Path(__file__).resolve().parents[1]
    registration = json.loads((directory / "SAMPLE_REGISTRATION.json").read_text(encoding="utf-8"))
    # No endpoint URL is serialized in source identity or output.
    source = {"id": "alchemy", "url": url, "max_batch": 1}
    items = []
    for block in registration["blocks"]:
        expected_file = directory / "evidence" / "full" / "core" / f"drpc-{block['number']}-pass1.json.gz"
        expected = json.loads(gzip.decompress(expected_file.read_bytes()))
        repeats = []
        for repetition in (1, 2):
            rpc = core.Rpc(source, block, budget=150)
            try:
                value = core.safe(lambda: core.core_observation(rpc, registration))
                # WARNING: never write rpc.records, value.reason or exception text.
                status = value.get("status")
                available = status == "PASS" and (value.get("data") or {}).get("status") == "AVAILABLE"
                comparison = compare(expected, value) if status == "PASS" else None
                repeats.append({"pass": repetition, "status": status, "complete": available,
                                "comparison": comparison})
            finally:
                rpc.client.close()
        hashes = [p["comparison"]["observed_fields_sha256"] if p["comparison"] else None for p in repeats]
        stable = hashes[0] is not None and hashes[0] == hashes[1]
        items.append({"block": block["number"], "block_hash": block["expected_hash"],
                      "repeats": repeats, "repeatability_pass": stable})
        print(f"BLOCK {block['number']}: complete={all(p['complete'] for p in repeats)} repeatable={stable}; "
              f"matching-fields={repeats[0]['comparison']['agreeing_fields'] if repeats[0]['comparison'] else 0}", flush=True)
        # Only public ABI field names and counts; never expose endpoint or raw values.
        for item in repeats:
            c = item.get("comparison")
            if c:
                print(f"CHECK block={block['number']} pass={item['pass']} "
                      f"reference={c['reference_field_count']} observed={c['observed_field_count']} "
                      f"mismatch_fields={c['mismatch_fields']} missing_fields={c['missing_fields']} "
                      f"additional_fields={c['additional_fields']}", flush=True)
    complete = all(x["repeatability_pass"] and all(p["complete"] for p in x["repeats"]) for x in items)
    mismatch = any(p["comparison"] and p["comparison"]["mismatch_fields"] for x in items for p in x["repeats"])
    missing = any(p["comparison"] and p["comparison"]["missing_fields"] for x in items for p in x["repeats"])
    result = {"schema": "alchemy-vs-drpc-core-v1", "collected_at_utc": datetime.now(UTC).isoformat(),
              "provider": "Alchemy", "reference": "dRPC saved Phase01-B",
              "same_block_registered": True, "results": items,
              "data_comparison": "FAIL_MISMATCH" if mismatch else "BLOCKED_MISSING" if missing or not complete else "PASS_FIELDS_MATCH",
              "backend_independence": "UNVERIFIED_REQUIRES_PROVENANCE",
              "independent_archive_gate": "BLOCKED_BACKEND_UNATTESTED",
              "no_v1_modification": True, "phase02_authorized": False,
              "security": "No RPC URL, API key, HTTP body, response headers, raw errors or credentials persisted"}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "ALCHEMY_CROSSCHECK_RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print("Result saved without endpoint credentials; backend independence remains unverified", flush=True)
    return 1 if mismatch else 0 if complete and not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
