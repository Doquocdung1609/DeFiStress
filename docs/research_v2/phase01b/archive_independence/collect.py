"""Narrow same-method archive comparison; no reconstruction or simulation."""
from __future__ import annotations

import argparse
import base64
from datetime import UTC, datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
from threading import Lock

from docs.research_v2.phase01b import collector as b


class CaptureClient:
    """Retain response entity bytes and timestamps, without credentials or cookies."""
    def __init__(self, client):
        self.client = client
        self.records = []
        self.lock = Lock()

    def post(self, url, **kwargs):
        started = datetime.now(UTC).isoformat()
        response = self.client.post(url, **kwargs)
        raw = response.content  # Decoded HTTP entity bytes, not TLS/chunk wire bytes.
        row = {"started_at_utc": started, "completed_at_utc": datetime.now(UTC).isoformat(),
               "url": url, "request_body_base64": base64.b64encode(response.request.content).decode(),
               "response_entity_base64": base64.b64encode(raw).decode(),
               "response_entity_sha256": hashlib.sha256(raw).hexdigest(),
               "response_size_bytes": len(raw), "http_status": response.status_code,
               "headers": {k: v for k, v in response.headers.items()
                           if k.lower().startswith(("qr", "x-drpc", "x-provider", "x-upstream", "x-served"))
                           or k.lower() in {"server", "via", "content-type", "x-request-id"}}}
        with self.lock:
            self.records.append(row)
        return response

    def close(self):
        self.client.close()


def field_comparison(expected, observed):
    expected_fields = expected["data"]["fields"]
    actual = observed.get("data") or {"fields": {}, "unavailable": {}}
    actual = json.loads(b.a.canonical(actual))
    rows = []
    for key, value in sorted(expected_fields.items()):
        present = key in actual["fields"]
        status = ("AGREES" if value == actual["fields"][key] else "MISMATCH") if present else "BLOCKED_MISSING_DATA"
        rows.append({"field": key, "expected": value, "observed": actual["fields"].get(key), "status": status,
                     "missing_reason": actual.get("unavailable", {}).get(key) if not present else None})
    return rows


def gate(rows, complete_twice, independent):
    if any(r["status"] == "MISMATCH" for r in rows):
        return "FAIL"
    if not rows or not complete_twice or not independent or any(r["status"] == "BLOCKED_MISSING_DATA" for r in rows):
        return "BLOCKED"
    return "PASS"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError("OUTPUT_MUST_BE_EMPTY_NO_PRIOR_EVIDENCE_OVERWRITE")
    args.output.mkdir(parents=True, exist_ok=True)
    folder = Path(__file__).resolve().parent
    root = folder.parent
    plan = json.loads((folder / "REQUEST_PLAN.json").read_text())
    registry = json.loads((root / "SAMPLE_REGISTRATION.json").read_text())
    observations, rows = {}, []
    for source in plan["providers"]:
        for block in registry["blocks"]:
            expected = json.loads(gzip.decompress((root / "evidence/full/core" /
                       f"drpc-{block['number']}-pass1.json.gz").read_bytes()))
            passes = []
            for repeat in [1, 2]:
                rpc = b.Rpc(source, block, budget=150)
                rpc.client = CaptureClient(rpc.client)
                observed = b.safe(lambda: b.core_observation(rpc, registry))
                name = f"{source['id']}-{block['number']}-pass{repeat}"
                b.dump_gzip(args.output / f"{name}-decoded.json.gz", observed)
                b.dump_gzip(args.output / f"{name}-requests.json.gz", rpc.records)
                b.dump_gzip(args.output / f"{name}-response-entities.json.gz", rpc.client.records)
                comparisons = field_comparison(expected, observed)
                passes.append({"observed": observed, "fields": comparisons})
                rpc.client.close()
                print(name, observed["status"], {s: sum(r["status"] == s for r in comparisons)
                                               for s in ["AGREES", "MISMATCH", "BLOCKED_MISSING_DATA"]}, flush=True)
            complete = all(p["observed"]["status"] == "PASS" and p["observed"]["data"]["status"] == "AVAILABLE" for p in passes)
            equal = complete and passes[0]["observed"]["data"]["fields"] == passes[1]["observed"]["data"]["fields"]
            row = {"provider": source, "block": block, "passes": passes, "complete_twice": complete,
                   "repeatability": "PASS" if equal else "BLOCKED_OR_MISMATCH",
                   "backend_independence": "UNVERIFIED", "independence_evidence": None,
                   "gate": "FAIL" if any(p["observed"]["status"] == "FAIL" for p in passes)
                           else gate([r for p in passes for r in p["fields"]], equal, False)}
            rows.append(row)
            observations[source["id"], block["number"]] = row
    # Also compare each new source directly with the contemporaneous dRPC reads, not just the saved baseline.
    pairwise = []
    for source in plan["providers"]:
        if source["id"] == "drpc":
            continue
        for block in registry["blocks"]:
            ref = observations["drpc", block["number"]]
            other = observations[source["id"], block["number"]]
            for index in [0, 1]:
                first = ref["passes"][index]["observed"]
                second = other["passes"][index]["observed"]
                reference_complete = first["status"] == "PASS" and first["data"]["status"] == "AVAILABLE"
                comparison = field_comparison(first, second) if reference_complete else []
                pairwise.append({"reference": "drpc", "comparison": source["id"], "block": block["number"],
                                 "pass": index + 1, "reference_available": reference_complete,
                                 "fields": comparison, "backend_independence": "UNVERIFIED"})
    result = {"source_commit": os.getenv("GITHUB_SHA"), "run_id": os.getenv("GITHUB_RUN_ID"),
              "starting_commit": plan["starting_commit"], "registration_unchanged": True,
              "observations": rows, "pairwise_contemporaneous": pairwise,
              "overall_gate": "FAIL" if any(r["gate"] == "FAIL" for r in rows) else "BLOCKED",
              "decision_reason": "No request-level distinct-serving-backend evidence has been established; do not infer independence from URLs/client versions/agreeing state",
              "phase02_authorized": False, "new_simulation": False}
    b.a.write_json(args.output / "INDEPENDENT_ARCHIVE_COMPARISON.json", result)
    b.manifest(args.output, registry)


if __name__ == "__main__":
    main()
