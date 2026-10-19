"""Phase01-B read-only historical validation. Never invokes a simulation engine."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import time

from docs.research_v2.phase01a import pilot as a


class DataIssue(RuntimeError):
    def __init__(self, kind: str, message: str):
        self.kind = kind
        super().__init__(message)


def issue_kind(message: str) -> str:
    text = message.lower()
    if any(s in text for s in ["pruned", "missing trie", "historical state", "unauthorized", "forbidden", "api key", "http 403", "http 401"]):
        return "DATA_ACCESS_BLOCKED"
    if any(s in text for s in ["limit", "429", "timeout", "timed out", "method not found", "not supported"]):
        return "PROVIDER_CAPABILITY_LIMIT"
    if any(s in text for s in ["revert", "no data present"]):
        return "INTERFACE_OR_DATA_UNAVAILABLE"
    return "PROVIDER_REQUEST_FAILURE"


class Rpc:
    """Persistent read-only transport; bounded batches, exact historical selectors."""

    def __init__(self, source: dict, block: dict, budget: int = 30000):
        import httpx

        self.client = httpx.Client(timeout=25, follow_redirects=False)
        self.source = source
        self.block = block
        self.budget = budget
        self.next_id = 0
        self.records = []

    def check(self, method: str, params: list) -> None:
        if method not in {"eth_chainId", "web3_clientVersion", "eth_getBlockByNumber", "eth_call", "eth_getLogs"}:
            raise DataIssue("SOFTWARE_ERROR", "READ_ONLY_METHOD_VIOLATION")
        if method == "eth_call" and (len(params) != 2 or params[1] != {
                "blockHash": self.block["expected_hash"], "requireCanonical": True}):
            raise DataIssue("SOFTWARE_ERROR", "UNPINNED_STATE_CALL")
        if method == "eth_getBlockByNumber" and params != [hex(self.block["number"]), False]:
            raise DataIssue("SOFTWARE_ERROR", "UNPINNED_HEADER")
        if method == "eth_getLogs":
            f = params[0]
            same_hash = f.get("blockHash") == self.block["expected_hash"]
            bounded = ("blockHash" not in f and int(f.get("toBlock", "0x0"), 16) == self.block["number"]
                       and self.block["number"] - 1023 <= int(f.get("fromBlock", "0x0"), 16) <= self.block["number"])
            if not same_hash and not bounded:
                raise DataIssue("SOFTWARE_ERROR", "LOG_WINDOW_LEAKAGE")

    def request(self, calls: list[tuple[str, list]]) -> list[dict]:
        if self.next_id + len(calls) > self.budget:
            raise DataIssue("PROVIDER_CAPABILITY_LIMIT", "PREREGISTERED_REQUEST_BUDGET_EXHAUSTED")
        payload = []
        for method, params in calls:
            self.check(method, params)
            self.next_id += 1
            payload.append({"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params})
        response = None
        for attempt in range(3):
            try:
                response = self.client.post(self.source["url"], json=payload[0] if len(payload) == 1 else payload)
                if response.status_code in {429, 502, 503, 504} and attempt < 2:
                    self.records.append({"attempt": attempt, "requests": payload, "http_status": response.status_code,
                                         "body": response.text[:2000], "status": "RETRYABLE_TRANSPORT"})
                    time.sleep(0.5 * (attempt + 1))
                    continue
                if response.status_code >= 400:
                    raise DataIssue(issue_kind(f"HTTP {response.status_code}: {response.text}"),
                                    f"HTTP {response.status_code}: {response.text[:1500]}")
                data = response.json()
                if not isinstance(data, list):
                    data = [data]
                ids = [r.get("id") for r in data if isinstance(r, dict)]
                if len(ids) != len(set(ids)) or set(ids) != {r["id"] for r in payload}:
                    raise DataIssue("PROVIDER_RESPONSE_INVALID", "MISSING_OR_DUPLICATE_RPC_RESPONSE_ID")
                by_id = {r["id"]: r for r in data}
                results = []
                for req in payload:
                    raw = by_id[req["id"]]
                    if "error" in raw or raw.get("result") is None:
                        message = str(raw.get("error", "MISSING_RPC_RESULT"))
                        result = {"status": "BLOCKED", "kind": issue_kind(message), "error": message}
                    else:
                        result = {"status": "AVAILABLE", "result": raw["result"]}
                    self.records.append({"request": req, "response": raw, "http_status": response.status_code,
                                         "routing_headers": {k: v for k, v in response.headers.items()
                                                              if k.lower().startswith(("qr", "x-drpc", "x-provider"))}})
                    results.append(result)
                return results
            except DataIssue as exc:
                self.records.append({"requests": payload, "http_status": None if response is None else response.status_code,
                                     "error": str(exc), "kind": exc.kind})
                return [{"status": "BLOCKED", "kind": exc.kind, "error": str(exc)} for _ in payload]
            except Exception as exc:
                if attempt < 2:
                    self.records.append({"requests": payload, "attempt": attempt,
                                         "error": type(exc).__name__ + ": " + str(exc), "status": "TRANSPORT_RETRY"})
                    time.sleep(0.5 * (attempt + 1))
                    continue
                error = type(exc).__name__ + ": " + str(exc)
                self.records.append({"requests": payload, "error": error, "kind": "PROVIDER_TRANSPORT_FAILURE"})
                return [{"status": "BLOCKED", "kind": "PROVIDER_TRANSPORT_FAILURE", "error": error} for _ in payload]
        raise AssertionError("unreachable")

    def call(self, method: str, params: list):
        result = self.request([(method, params)])[0]
        if result["status"] != "AVAILABLE":
            raise DataIssue(result["kind"], result["error"])
        return result["result"]


def query(address: str, signature: str, outputs: list, inputs=None, args=(), label=None) -> dict:
    return {"to": address.lower(), "signature": signature, "outputs": outputs,
            "inputs": inputs or [], "args": list(args), "label": label or signature}


def read_many(rpc: Rpc, specs: list[dict]) -> list[dict]:
    from web3 import Web3

    codec = Web3().codec
    rows = []
    for start in range(0, len(specs), 40):
        selected = specs[start:start + 40]
        calls = []
        for spec in selected:
            selector = bytes(Web3.keccak(text=spec["signature"]))[:4]
            data = "0x" + (selector + codec.encode(spec["inputs"], spec["args"])).hex()
            calls.append(("eth_call", [{"to": spec["to"], "data": data},
                                     {"blockHash": rpc.block["expected_hash"], "requireCanonical": True}]))
        for spec, result in zip(selected, rpc.request(calls), strict=True):
            row = {"query": spec, **result}
            if result["status"] == "AVAILABLE":
                try:
                    decoded = codec.decode(spec["outputs"], bytes.fromhex(result["result"].removeprefix("0x")))
                    row["value"] = decoded[0] if len(decoded) == 1 else decoded
                except Exception as exc:
                    row.update(status="BLOCKED", kind="ABI_DECODE_OR_INTERFACE_UNAVAILABLE", value=None,
                               error=type(exc).__name__ + ": " + str(exc))
            else:
                row["value"] = None
            rows.append(row)
    return rows


def required(row: dict):
    if row["status"] != "AVAILABLE":
        raise DataIssue(row.get("kind", "DATA_UNAVAILABLE"), row.get("error", "unavailable"))
    return row["value"]


def read_one(rpc: Rpc, spec: dict):
    return required(read_many(rpc, [spec])[0])


def safe(fn):
    try:
        return {"status": "PASS", "data": fn()}
    except DataIssue as exc:
        return {"status": "BLOCKED", "kind": exc.kind, "data": None, "reason": str(exc)}
    except (AssertionError, ValueError) as exc:
        return {"status": "FAIL", "kind": "DATA_VALIDATION_FAILURE", "data": None, "reason": str(exc)}
    except Exception as exc:
        return {"status": "FAIL", "kind": "SOFTWARE_ERROR", "data": None,
                "reason": type(exc).__name__ + ": " + str(exc)}


def identity(rpc: Rpc) -> dict:
    chain = int(rpc.call("eth_chainId", []), 16)
    if chain != 1:
        raise ValueError("CHAIN_ID_MISMATCH")
    header = a.validate_header(rpc.call("eth_getBlockByNumber", [hex(rpc.block["number"]), False]),
                               rpc.block["number"], rpc.block["expected_hash"])
    if header["timestamp"] != rpc.block["timestamp_unix"]:
        raise ValueError("BLOCK_TIMESTAMP_MISMATCH")
    return {"chain_id": chain, **header}


def probe(registry: dict, output: Path) -> None:
    results = []
    for source in registry["providers"]:
        for block in registry["blocks"]:
            rpc = Rpc(source, block, 1000)
            row = {"provider": source["id"], "block": block["number"], "identity": safe(lambda: identity(rpc))}
            row["client_version"] = safe(lambda: rpc.call("web3_clientVersion", []))
            specs = []
            for pool in registry["pools"]:
                for signature, outputs in [("slot0()", ["uint160", "int24", "uint16", "uint16", "uint16", "uint8", "bool"]),
                                           ("liquidity()", ["uint128"])]:
                    specs.append(query(pool["address"], signature, outputs, label=pool["id"] + ":" + signature))
            specs.append(query(registry["aave_pool"], "ADDRESSES_PROVIDER()", ["address"]))
            passes = []
            for _ in range(2):
                passes.append(read_many(rpc, specs))
            row["passes"] = passes
            complete = all(x["status"] == "AVAILABLE" for sweep in passes for x in sweep)
            row["repeatability"] = "PASS" if complete and a.digest(passes[0]) == a.digest(passes[1]) else "BLOCKED_OR_MISMATCH"
            row["backend_independence"] = "UNVERIFIED_NO_REQUEST_LEVEL_BACKEND_ATTESTATION"
            results.append(row)
            a.write_json(output / "raw" / f"probe-{source['id']}-{block['number']}.json", rpc.records)
            print(source["id"], block["number"], row["repeatability"], flush=True)
            rpc.client.close()
    a.write_json(output / "source_probe.json", {"registration_canonical_sha256": a.digest(registry),
                 "commit": os.getenv("GITHUB_SHA"), "run_id": os.getenv("GITHUB_RUN_ID"), "results": results,
                 "independent_archive_status": "INDEPENDENT_ARCHIVE_VALIDATION_BLOCKED"})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    probe(registry, args.output)


if __name__ == "__main__":
    main()
