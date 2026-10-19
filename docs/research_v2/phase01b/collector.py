"""Phase01-B read-only historical validation. Never invokes a simulation engine."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from decimal import Decimal, localcontext
import gzip
import hashlib
import json
import os
from pathlib import Path
from threading import Lock
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
    if any(s in text for s in ["limit", "429", "timeout", "timed out", "method not found", "not supported",
                               "batch of more", "free plan", "paid account"]):
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
        self.lock = Lock()
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
        payload = []
        with self.lock:
            if self.next_id + len(calls) > self.budget:
                raise DataIssue("PROVIDER_CAPABILITY_LIMIT", "PREREGISTERED_REQUEST_BUDGET_EXHAUSTED")
            if len(calls) > self.source.get("max_batch", 40):
                raise DataIssue("SOFTWARE_ERROR", "KNOWN_PROVIDER_BATCH_LIMIT_EXCEEDED")
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
    maximum = min(40, rpc.source.get("max_batch", 40))
    selected_batches = [specs[start:start + maximum] for start in range(0, len(specs), maximum)]
    batches = []
    for selected in selected_batches:
        calls = []
        for spec in selected:
            selector = bytes(Web3.keccak(text=spec["signature"]))[:4]
            data = "0x" + (selector + codec.encode(spec["inputs"], spec["args"])).hex()
            calls.append(("eth_call", [{"to": spec["to"], "data": data},
                                     {"blockHash": rpc.block["expected_hash"], "requireCanonical": True}]))
        batches.append(calls)
    with ThreadPoolExecutor(max_workers=min(4, max(1, len(batches)))) as executor:
        responses = list(executor.map(rpc.request, batches))
    for selected, batch_results in zip(selected_batches, responses, strict=True):
        for spec, result in zip(selected, batch_results, strict=True):
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


def tick_bounds(current: int, spacing: int, delta: int = 6932) -> tuple[int, int, list[int]]:
    low = max(-887272, current - delta)
    high = min(887272, current + delta)
    low = -((-low) // spacing) * spacing
    high = (high // spacing) * spacing
    return low, high, list(range((low // spacing) >> 8, ((high // spacing) >> 8) + 1))


def liquidity_audit(ticks: list, current: int, active: int) -> dict:
    indices = [t["tick"] for t in ticks]
    if len(indices) != len(set(indices)) or indices != sorted(indices):
        raise ValueError("DUPLICATE_OR_UNSORTED_TICKS")
    for t in ticks:
        if int(t["gross"]) <= 0 or abs(int(t["net"])) > int(t["gross"]):
            raise ValueError("LIQUIDITY_GROSS_NET_INCONSISTENCY")
    boundary = active - sum(int(t["net"]) for t in ticks if t["tick"] <= current)
    running = boundary
    minimum = running
    for t in ticks:
        running += int(t["net"])
        minimum = min(minimum, running)
    if minimum < 0:
        raise ValueError("NEGATIVE_ANCHORED_INTERVAL_LIQUIDITY")
    return {"status": "PASS", "active_liquidity_raw": str(active), "derived_lower_boundary_liquidity": str(boundary),
            "minimum_interval_liquidity_raw": str(minimum),
            "boundary_status": "DERIVED_FROM_ACTIVE_LIQUIDITY_NOT_INDEPENDENT_BOUNDARY_OBSERVATION",
            "net_sum_zero_test": "NOT_APPLICABLE_PARTIAL_PRICE_BAND"}


def pool_full_range(rpc: Rpc, pool: dict, registry: dict) -> dict:
    from backend.app.adapters.uniswap.ticks import bitmap_ticks

    address = pool["address"]
    usdc, weth = registry["tokens"]["USDC"], registry["tokens"]["WETH"]
    specs = [query(registry["factory"], "getPool(address,address,uint24)", ["address"],
                   ["address", "address", "uint24"], [usdc["address"], weth["address"], pool["fee"]]),
             query(address, "token0()", ["address"]), query(address, "token1()", ["address"]),
             query(address, "fee()", ["uint24"]), query(address, "tickSpacing()", ["int24"]),
             query(address, "liquidity()", ["uint128"]),
             query(address, "slot0()", ["uint160", "int24", "uint16", "uint16", "uint16", "uint8", "bool"]),
             query(usdc["address"], "decimals()", ["uint8"]), query(weth["address"], "decimals()", ["uint8"])]
    values = [required(r) for r in read_many(rpc, specs)]
    factory_pool, token0, token1, fee, spacing, active, slot0, d0, d1 = values
    if factory_pool.lower() != address.lower():
        raise ValueError("FACTORY_POOL_MISMATCH")
    a.validate_pool_metadata(token0, token1, fee, [d0, d1], pool, registry["tokens"])
    if spacing != {500: 10, 3000: 60}[fee]:
        raise ValueError("TICK_SPACING_MISMATCH")
    sqrt_price, current = int(slot0[0]), int(slot0[1])
    with localcontext() as ctx:
        ctx.prec = 80
        ratio = Decimal(sqrt_price) ** 2 / Decimal(2) ** 192
        lower = Decimal("1.0001") ** current
        upper = Decimal("1.0001") ** (current + 1)
        tolerance = max(abs(ratio), abs(lower)) * Decimal("1e-12")
        if ratio + tolerance < lower or ratio - tolerance > upper:
            raise ValueError("SQRT_PRICE_TICK_INCONSISTENCY")
    low, high, words = tick_bounds(current, spacing, registry["tick_scope"]["delta_ticks"])
    bitmap_rows = read_many(rpc, [query(address, "tickBitmap(int16)", ["uint256"], ["int16"], [w]) for w in words])
    missing_words = [w for w, r in zip(words, bitmap_rows, strict=True) if r["status"] != "AVAILABLE"]
    bitmaps = [{"word": w, "bitmap": str(required(r))} for w, r in zip(words, bitmap_rows, strict=True)
               if r["status"] == "AVAILABLE"]
    initialized = sorted({t for row in bitmaps for t in bitmap_ticks(int(row["bitmap"]), row["word"], spacing)
                          if low <= t <= high})
    raw_ticks = read_many(rpc, [query(address, "ticks(int24)",
                 ["uint128", "int128", "uint256", "uint256", "int56", "uint160", "uint32", "bool"],
                 ["int24"], [t]) for t in initialized])
    missing_ticks = []
    ticks = []
    for t, row in zip(initialized, raw_ticks, strict=True):
        if row["status"] != "AVAILABLE":
            missing_ticks.append(t)
            continue
        raw = row["value"]
        if not raw[7]:
            raise ValueError("BITMAP_AND_INITIALIZED_FLAG_MISMATCH")
        ticks.append({"tick": t, "gross": str(raw[0]), "net": str(raw[1]), "raw": [str(v) for v in raw]})
    result = {"pool": address.lower(), "fee_millionths": fee, "token0": token0.lower(), "token1": token1.lower(),
              "decimals": [d0, d1], "spacing": spacing, "current_tick": current,
              "sqrt_price_x96": str(sqrt_price), "active_liquidity_raw": str(active),
              "required_lower_tick": low, "required_upper_tick": high, "required_words": words,
              "bitmaps": bitmaps, "initialized_ticks_expected": len(initialized), "ticks": ticks,
              "missing_words": missing_words, "missing_ticks": missing_ticks,
              "coverage_status": "PASS_REGISTERED_RANGE_COMPLETE" if not missing_words and not missing_ticks else "BLOCKED_INCOMPLETE_RANGE",
              "outside_registered_range": [[-887272, low - 1], [high + 1, 887272]],
              "outside_status": "OUT_OF_SCOPE_NOT_RECONSTRUCTED", "full_legal_pool_tick_coverage": False}
    result["liquidity_audit"] = (liquidity_audit(ticks, current, int(active)) if not missing_words and not missing_ticks
                                  else {"status": "BLOCKED", "reason": "INCOMPLETE_REQUIRED_RANGE"})
    return result


def oracle_config(rpc: Rpc, registry: dict) -> dict:
    pool = registry["aave_pool"]
    provider = read_one(rpc, query(pool, "ADDRESSES_PROVIDER()", ["address"]))
    specs = [query(provider, "getPool()", ["address"]), query(provider, "getPriceOracle()", ["address"]),
             query(provider, "getPoolDataProvider()", ["address"]), query(pool, "POOL_REVISION()", ["uint256"])]
    rows = read_many(rpc, specs)
    actual_pool, oracle, data_provider = [required(r) for r in rows[:3]]
    if actual_pool.lower() != pool.lower() or any(int(v, 16) == 0 for v in [provider, oracle, data_provider]):
        raise ValueError("HISTORICAL_AAVE_CONFIGURATION_MISMATCH")
    base, unit = [required(r) for r in read_many(rpc, [query(oracle, "BASE_CURRENCY()", ["address"]),
                                                                    query(oracle, "BASE_CURRENCY_UNIT()", ["uint256"])])]
    if unit <= 0:
        raise ValueError("INVALID_BASE_CURRENCY_UNIT")
    return {"pool": pool.lower(), "provider": provider.lower(), "oracle": oracle.lower(),
            "data_provider": data_provider.lower(), "base_currency": base.lower(), "base_unit": str(unit),
            "pool_revision": rows[3].get("value"), "revision_status": rows[3]["status"]}


def optional_value(row: dict) -> dict:
    return {"status": row["status"] if row["status"] == "AVAILABLE" else "UNSUPPORTED_OR_UNAVAILABLE",
            "value": row.get("value"), "kind": row.get("kind")}


def validate_round(round_data, block_timestamp: int) -> dict:
    round_id, answer, started, updated, answered = [int(v) for v in round_data]
    if answer <= 0 or not 0 < started <= updated <= block_timestamp or answered < round_id:
        raise ValueError("INVALID_ROUND_OR_TIMESTAMP_LEAKAGE")
    return {"round_id": str(round_id), "answer": str(answer), "started_at": started,
            "updated_at": updated, "answered_in_round": str(answered),
            "age_seconds_at_block": block_timestamp - updated,
            "freshness_heartbeat_status": "NOT_EVALUATED_NO_REGISTERED_HEARTBEAT"}


def compare_proxy_round(proxy_round, aggregator_round) -> None:
    mask = (1 << 64) - 1
    if (int(aggregator_round[0]) != (int(proxy_round[0]) & mask)
            or tuple(aggregator_round[1:4]) != tuple(proxy_round[1:4])
            or int(aggregator_round[4]) != (int(proxy_round[4]) & mask)):
        raise ValueError("PROXY_AND_AGGREGATOR_ROUND_MISMATCH")


def trace_feed(rpc: Rpc, address: str) -> dict:
    signatures = [("decimals()", ["uint8"]), ("description()", ["string"]), ("latestAnswer()", ["int256"]),
                  ("latestRoundData()", ["uint80", "int256", "uint256", "uint256", "uint80"]),
                  ("aggregator()", ["address"]), ("ASSET_TO_USD_AGGREGATOR()", ["address"]),
                  ("getPriceCap()", ["int256"]), ("isCapped()", ["bool"])]
    rows = read_many(rpc, [query(address, s, o) for s, o in signatures])
    fields = {s: optional_value(row) for (s, _), row in zip(signatures, rows, strict=True)}
    result = {"address": address.lower(), "interfaces": fields, "round": None,
              "round_status": "UNSUPPORTED_OR_UNAVAILABLE"}
    if fields["latestRoundData()"]["status"] == "AVAILABLE":
        observed = fields["latestRoundData()"]["value"]
        result["round"] = validate_round(observed, rpc.block["timestamp_unix"])
        lookup = read_many(rpc, [query(address, "getRoundData(uint80)",
                    ["uint80", "int256", "uint256", "uint256", "uint80"], ["uint80"], [int(observed[0])])])[0]
        result["same_round_lookup"] = optional_value(lookup)
        if lookup["status"] == "AVAILABLE" and tuple(lookup["value"]) != tuple(observed):
            raise ValueError("HISTORICAL_ROUND_LOOKUP_MISMATCH")
        result["round_status"] = "PASS" if lookup["status"] == "AVAILABLE" else "BLOCKED_ROUND_LOOKUP"
        aggregator = fields["aggregator()"]["value"]
        if aggregator and int(aggregator, 16):
            phase = int(observed[0]) >> 64
            phase_row = read_many(rpc, [query(address, "phaseAggregators(uint16)", ["address"], ["uint16"], [phase])])[0]
            result["phase_id"] = phase
            result["phase_aggregator"] = optional_value(phase_row)
            if phase_row["status"] == "AVAILABLE" and phase_row["value"].lower() != aggregator.lower():
                raise ValueError("HISTORICAL_PHASE_AGGREGATOR_MISMATCH")
            underlying = read_many(rpc, [query(aggregator, "decimals()", ["uint8"]),
                        query(aggregator, "latestRoundData()", ["uint80", "int256", "uint256", "uint256", "uint80"])])
            result["aggregator_interface"] = [optional_value(v) for v in underlying]
            if underlying[1]["status"] == "AVAILABLE":
                low_round = underlying[1]["value"]
                validate_round(low_round, rpc.block["timestamp_unix"])
                compare_proxy_round(observed, low_round)
    return result


def oracle_trace(rpc: Rpc, registry: dict) -> dict:
    config = oracle_config(rpc, registry)
    assets = []
    for symbol, token in registry["tokens"].items():
        address = token["address"]
        rows = read_many(rpc, [query(config["oracle"], "getSourceOfAsset(address)", ["address"], ["address"], [address]),
                    query(config["oracle"], "getAssetPrice(address)", ["uint256"], ["address"], [address])])
        source, actual_price = [required(r) for r in rows]
        if int(source, 16) == 0 or actual_price <= 0:
            raise ValueError("ORACLE_SOURCE_OR_VALUE_INVALID")
        trace = trace_feed(rpc, source)
        fields = trace["interfaces"]
        source_decimals = fields["decimals()"]["value"]
        answer = fields["latestAnswer()"]["value"]
        if source_decimals is None or answer is None:
            raise DataIssue("INTERFACE_OR_DATA_UNAVAILABLE", "SOURCE_PRICE_INTERFACE_UNAVAILABLE")
        if int(answer) * int(config["base_unit"]) != actual_price * 10 ** int(source_decimals):
            raise ValueError("AAVE_EFFECTIVE_AND_SOURCE_PRICE_MISMATCH")
        underlying_address = fields["ASSET_TO_USD_AGGREGATOR()"]["value"]
        cap_check = None
        if underlying_address and int(underlying_address, 16):
            upstream = trace_feed(rpc, underlying_address)
            trace["asset_to_usd_upstream"] = upstream
            up_answer = upstream["interfaces"]["latestAnswer()"]["value"]
            up_decimals = upstream["interfaces"]["decimals()"]["value"]
            cap = fields["getPriceCap()"]["value"]
            if up_answer is None or cap is None or up_decimals != source_decimals:
                raise DataIssue("INTERFACE_OR_DATA_UNAVAILABLE", "CAP_ADAPTER_DEPENDENCY_UNAVAILABLE")
            if min(int(up_answer), int(cap)) != int(answer):
                raise ValueError("CAP_ADAPTER_EFFECTIVE_PRICE_MISMATCH")
            cap_check = {"status": "PASS", "cap_raw": str(cap), "underlying_answer_raw": str(up_answer),
                         "effective_answer_raw": str(answer)}
            round_status = upstream["round_status"]
        else:
            round_status = trace["round_status"]
        assets.append({"symbol": symbol, "asset": address.lower(), "source": source.lower(),
                       "aave_price_raw": str(actual_price), "base_unit": config["base_unit"],
                       "source_decimals": source_decimals, "source_answer_raw": str(answer),
                       "effective_price_check": "PASS", "round_trace_status": round_status,
                       "cap_adapter_check": cap_check, "trace": trace})
    return {"configuration": config, "assets": assets,
            "observation_type": "HISTORICAL_AAVE_ORACLE_OBSERVATION_NOT_DEX_OR_COUNTERFACTUAL_POLICY"}


def choose_borrowers(logs: list, block: dict, pool: str, signature: str, limit: int) -> list[str]:
    users = set()
    for log in logs:
        number = int(log["blockNumber"], 16)
        if (len(log.get("topics", [])) < 3 or not block["number"] - 1023 <= number <= block["number"]
                or log.get("removed", False) or log["address"].lower() != pool.lower()
                or log["topics"][0].lower() != signature.lower() or not log.get("blockHash")):
            raise ValueError("BORROW_DISCOVERY_LOG_LEAKAGE")
        users.add("0x" + log["topics"][2][-40:].lower())
    return sorted(users, key=lambda address: (hashlib.sha256(("1:" + address).encode()).hexdigest(), address))[:limit]


def reconstruct_account(reserves: list, account: list, mode: dict | None, tolerance: int) -> dict:
    if any(r["status"] != "AVAILABLE" for r in reserves):
        return {"status": "BLOCKED", "reason": "MISSING_USER_RESERVE_STATE", "hf_raw": None}
    collateral = debt = weighted = participating = 0
    for row in reserves:
        data = row["data"]
        supplied, stable, variable = map(int, data[:3])
        enabled = bool(data[8])
        if not supplied and not stable and not variable:
            continue
        participating += 1
        if row.get("price") is None or row.get("decimals") is None or row.get("lt") is None:
            return {"status": "BLOCKED", "reason": "MISSING_ACTIVE_RESERVE_DEPENDENCY", "hf_raw": None}
        if int(row["price"]) <= 0 or not 0 <= int(row["decimals"]) <= 36:
            return {"status": "BLOCKED", "reason": "INVALID_ACTIVE_PRICE_OR_DECIMALS", "hf_raw": None}
        price, unit, lt = int(row["price"]), 10 ** int(row["decimals"]), int(row["lt"])
        if enabled:
            if mode is not None:
                if mode.get("status") != "AVAILABLE" or row.get("reserve_id") is None:
                    return {"status": "BLOCKED", "reason": "EMODE_CONFIG_OR_RESERVE_ID_UNAVAILABLE", "hf_raw": None}
                if int(mode["collateral_bitmap"]) & (1 << row["reserve_id"]):
                    lt = int(mode["lt"])
            value = supplied * price // unit
            collateral += value
            weighted += value * lt
        # Conservative integer debt valuation matches the current protocol's ceil division.
        debt += ((stable + variable) * price + unit - 1) // unit
    hf = (1 << 256) - 1 if debt == 0 else weighted * 10 ** 18 // (debt * 10000)
    col_difference = collateral - int(account[0])
    debt_difference = debt - int(account[1])
    hf_difference = hf - int(account[5])
    base_tolerance = max(1, participating)
    ok = abs(col_difference) <= base_tolerance and abs(debt_difference) <= base_tolerance and abs(hf_difference) <= tolerance
    return {"status": "PASS" if ok else "FAIL", "collateral_base_raw": str(collateral), "debt_base_raw": str(debt),
            "weighted_collateral_lt_raw": str(weighted), "hf_raw": str(hf), "contract_hf_raw": str(account[5]),
            "hf_difference_raw": str(hf_difference), "collateral_base_difference": str(col_difference),
            "debt_base_difference": str(debt_difference), "base_tolerance_raw": base_tolerance,
            "hf_tolerance_wad_raw": str(tolerance), "participating_reserves": participating,
            "method": "FULL_PORTFOLIO_INTEGER_PRICE_VALUATION_WEIGHTED_LT; HALF_OPEN_BASE_UNIT_ROUNDING",
            "zero_debt_hf": "UINT256_MAX_SENTINEL" if debt == 0 else None}


def borrowers(rpc: Rpc, registry: dict) -> dict:
    from web3 import Web3

    config = oracle_config(rpc, registry)
    pool, provider, oracle = config["pool"], config["data_provider"], config["oracle"]
    signature = "0x" + bytes(Web3.keccak(text=registry["borrower_sample"]["event"])).hex()
    logs = rpc.call("eth_getLogs", [{"address": pool, "topics": [signature],
                    "fromBlock": hex(rpc.block["number"] - 1023), "toBlock": hex(rpc.block["number"])}])
    logs = sorted(logs, key=lambda r: (int(r["blockNumber"], 16), int(r["transactionIndex"], 16), int(r["logIndex"], 16)))
    locators = [(r["blockHash"], r["transactionHash"], r["logIndex"]) for r in logs]
    if len(locators) != len(set(locators)):
        raise ValueError("DUPLICATE_BORROW_EVENT_LOCATOR")
    users = choose_borrowers(logs, rpc.block, pool, signature, registry["borrower_sample"]["per_block_max"])
    if len(users) <= 3:
        raise DataIssue("DATA_COVERAGE_LIMIT", "EVENT_WINDOW_YIELDED_NO_EXPANSION_BEYOND_SENTINELS")
    assets = read_one(rpc, query(pool, "getReservesList()", ["address[]"]))
    assets = [v.lower() for v in assets]
    if len(assets) != len(set(assets)) or not assets:
        raise ValueError("INVALID_RESERVE_LIST")
    id_rows = read_many(rpc, [query(pool, "getReserveAddressById(uint16)", ["address"], ["uint16"], [i]) for i in range(128)])
    ids = {r["value"].lower(): i for i, r in enumerate(id_rows) if r["status"] == "AVAILABLE" and int(r["value"], 16)}
    config_rows = read_many(rpc, [query(provider, "getReserveConfigurationData(address)",
                          ["uint256"] * 5 + ["bool"] * 5, ["address"], [asset]) for asset in assets])
    price_rows = read_many(rpc, [query(oracle, "getAssetPrice(address)", ["uint256"], ["address"], [asset]) for asset in assets])
    source_rows = read_many(rpc, [query(oracle, "getSourceOfAsset(address)", ["address"], ["address"], [asset]) for asset in assets])
    token_decimals = read_many(rpc, [query(asset, "decimals()", ["uint8"]) for asset in assets])
    reserve_meta = []
    for asset, cr, pr, sr, dr in zip(assets, config_rows, price_rows, source_rows, token_decimals, strict=True):
        configuration = cr.get("value")
        decimals = configuration[0] if configuration is not None else None
        if decimals is not None and dr["status"] == "AVAILABLE" and dr["value"] != decimals:
            raise ValueError("RESERVE_TOKEN_DECIMALS_MISMATCH")
        reserve_meta.append({"asset": asset, "reserve_id": ids.get(asset), "decimals": decimals,
                             "lt": configuration[2] if configuration is not None else None,
                             "configuration_raw": configuration, "price": pr.get("value"), "price_status": pr["status"],
                             "source": sr.get("value"), "source_status": sr["status"], "token_decimals_status": dr["status"]})
    account_rows = read_many(rpc, [query(pool, "getUserAccountData(address)", ["uint256"] * 6, ["address"], [user]) for user in users])
    modes = read_many(rpc, [query(pool, "getUserEMode(address)", ["uint256"], ["address"], [user]) for user in users])
    configs = read_many(rpc, [query(pool, "getUserConfiguration(address)", ["uint256"], ["address"], [user]) for user in users])
    categories = sorted({int(required(r)) for r in modes if r["status"] == "AVAILABLE" and int(r["value"])})
    e_modes = {}
    for category in categories:
        mode_rows = read_many(rpc, [query(pool, "getEModeCategoryCollateralConfig(uint8)", ["uint16"] * 3, ["uint8"], [category]),
                              query(pool, "getEModeCategoryCollateralBitmap(uint8)", ["uint128"], ["uint8"], [category])])
        e_modes[category] = ({"status": "AVAILABLE", "lt": mode_rows[0]["value"][1],
                              "collateral_bitmap": str(mode_rows[1]["value"]), "raw_config": mode_rows[0]["value"]}
                            if all(r["status"] == "AVAILABLE" for r in mode_rows)
                            else {"status": "BLOCKED", "reason": "UNSUPPORTED_HISTORICAL_EMODE_INTERFACE"})
    user_specs = [query(provider, "getUserReserveData(address,address)", ["uint256"] * 7 + ["uint40", "bool"],
                         ["address", "address"], [asset, user]) for user in users for asset in assets]
    user_rows = read_many(rpc, user_specs)
    portfolios = []
    for index, user in enumerate(users):
        observations = []
        for metadata, raw in zip(reserve_meta, user_rows[index * len(assets):(index + 1) * len(assets)], strict=True):
            observations.append({**metadata, "status": raw["status"], "data": raw.get("value")})
        account = account_rows[index]
        mode = modes[index]
        flags_valid = True
        if configs[index]["status"] == "AVAILABLE":
            user_bits = int(configs[index]["value"])
            for observation in observations:
                data = observation.get("data")
                reserve_id = observation["reserve_id"]
                if data is not None:
                    if int(data[7]) > rpc.block["timestamp_unix"]:
                        raise ValueError("BORROWER_RESERVE_TIMESTAMP_LEAKAGE")
                    if reserve_id is not None:
                        collateral_flag = bool(user_bits & (1 << (2 * reserve_id + 1)))
                        borrow_flag = bool(user_bits & (1 << (2 * reserve_id)))
                        flags_valid &= collateral_flag == bool(data[8])
                        flags_valid &= borrow_flag or not (int(data[1]) + int(data[2]))
        if account["status"] != "AVAILABLE" or mode["status"] != "AVAILABLE":
            reconstruction = {"status": "BLOCKED", "hf_raw": None, "reason": "ACCOUNT_OR_EMODE_MISSING"}
        else:
            reconstruction = reconstruct_account(observations, account["value"],
                           e_modes.get(int(mode["value"])) if int(mode["value"]) else None,
                           registry["gates"]["hf_abs_tolerance_wad_raw"])
        if not flags_valid:
            reconstruction.update(status="FAIL", reason="USER_CONFIGURATION_AND_RESERVE_FLAGS_MISMATCH")
        portfolios.append({"address": user, "block_number": rpc.block["number"], "block_hash": rpc.block["expected_hash"],
                           "account_raw": account.get("value"), "user_emode": mode.get("value"),
                           "user_configuration_raw": configs[index].get("value"), "reserves": observations,
                           "hf_reconstruction": reconstruction,
                           "missing_data_flags": [r["asset"] for r in observations if r["status"] != "AVAILABLE"]})
    return {"configuration": config, "event_window": [rpc.block["number"] - 1023, rpc.block["number"]],
            "discovery_logs": logs, "selected_users": users, "reserves_count": len(assets),
            "reserve_id_coverage": {"available_ids": len(ids), "missing_assets": sorted(set(assets) - set(ids))},
            "emode_configurations": e_modes, "portfolios": portfolios,
            "sample_scope": "RECENT_BORROW_EVENT_SAMPLE_NOT_MARKET_CENSUS; NO_STRESS_SELECTION"}


def core_observation(rpc: Rpc, registry: dict) -> dict:
    header = identity(rpc)
    fields = {"chain_id": 1, "block_number": header["number"], "block_hash": header["hash"],
              "timestamp": header["timestamp"]}
    unavailable = {}
    specs = []
    for pool in registry["pools"]:
        for signature, outputs in [("slot0()", ["uint160", "int24", "uint16", "uint16", "uint16", "uint8", "bool"]),
                                   ("liquidity()", ["uint128"]), ("token0()", ["address"]),
                                   ("token1()", ["address"]), ("fee()", ["uint24"]), ("tickSpacing()", ["int24"])]:
            specs.append(query(pool["address"], signature, outputs, label=pool["id"] + ":" + signature))
    for symbol, token in registry["tokens"].items():
        specs.append(query(token["address"], "decimals()", ["uint8"], label=symbol + ":decimals()"))
    for row in read_many(rpc, specs):
        key = row["query"]["label"]
        if row["status"] == "AVAILABLE":
            fields[key] = row["value"]
        else:
            unavailable[key] = {"kind": row["kind"], "error": row["error"]}
    config = safe(lambda: oracle_config(rpc, registry))
    if config["status"] == "PASS":
        fields.update({"aave:" + k: v for k, v in config["data"].items()
                       if k != "revision_status" and v is not None})
        if config["data"]["pool_revision"] is None:
            unavailable["aave:pool_revision"] = {"kind": "INTERFACE_OR_DATA_UNAVAILABLE"}
        specs = []
        for symbol, token in registry["tokens"].items():
            specs.extend([query(config["data"]["oracle"], "getAssetPrice(address)", ["uint256"], ["address"],
                                [token["address"]], label=symbol + ":aave_price"),
                          query(config["data"]["oracle"], "getSourceOfAsset(address)", ["address"], ["address"],
                                [token["address"]], label=symbol + ":aave_source")])
        for row in read_many(rpc, specs):
            key = row["query"]["label"]
            if row["status"] == "AVAILABLE":
                fields[key] = row["value"]
            else:
                unavailable[key] = {"kind": row["kind"], "error": row["error"]}
    else:
        unavailable["aave_configuration"] = {k: v for k, v in config.items() if k != "data"}
    if identity(rpc) != header:
        raise ValueError("END_OF_PASS_IDENTITY_CHANGED")
    return {"fields": fields, "unavailable": unavailable,
            "status": "AVAILABLE" if not unavailable else "INCOMPLETE"}


def compare_fields(first: dict, second: dict) -> dict:
    keys = sorted(set(first["fields"]) | set(second["fields"]) | set(first["unavailable"]) | set(second["unavailable"]))
    rows = []
    for key in keys:
        if key not in first["fields"] or key not in second["fields"]:
            status = "BLOCKED_MISSING_DATA"
        else:
            status = "AGREES" if first["fields"][key] == second["fields"][key] else "MISMATCH"
        rows.append({"field": key, "observed": status, "reference": first["fields"].get(key),
                     "comparison": second["fields"].get(key)})
    return {"fields": rows, "mismatches": sum(r["observed"] == "MISMATCH" for r in rows),
            "missing_fields": sum(r["observed"] == "BLOCKED_MISSING_DATA" for r in rows),
            "agreeing_fields": sum(r["observed"] == "AGREES" for r in rows),
            "independent_validation_status": "INDEPENDENT_ARCHIVE_VALIDATION_BLOCKED",
            "independence_reason": "No request-level distinct-backend attestation; gateway/client strings do not prove independence"}


def dump_gzip(path: Path, data) -> dict:
    raw = a.canonical(data)
    packed = gzip.compress(raw, mtime=0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(packed)
    return {"file": path.name, "sha256_gzip_bytes": hashlib.sha256(packed).hexdigest(),
            "sha256_canonical_json_bytes": hashlib.sha256(raw).hexdigest(),
            "gzip_size": len(packed), "uncompressed_size": len(raw)}


def save_journal(output: Path, name: str, records: list) -> None:
    for index, start in enumerate(range(0, len(records), 256)):
        dump_gzip(output / "raw" / f"{name}-{index:03}.json.gz", records[start:start + 256])


def run_validation(registry: dict, output: Path) -> None:
    observations = {}
    core_catalog = []
    for source in registry["providers"]:
        for block in registry["blocks"]:
            key = f"{source['id']}-{block['number']}"
            passes = []
            for repeat in [1, 2]:
                rpc = Rpc(source, block, 2000)
                result = safe(lambda: core_observation(rpc, registry))
                save_journal(output, f"core-{key}-pass{repeat}", rpc.records)
                dump_gzip(output / "core" / f"{key}-pass{repeat}.json.gz", result)
                passes.append(result)
                rpc.client.close()
            complete = all(p["status"] == "PASS" and p["data"]["status"] == "AVAILABLE" for p in passes)
            hashes = [a.digest(p["data"]["fields"]) if p["status"] == "PASS" else None for p in passes]
            row = {"provider": source["id"], "block": block["number"], "pass_hashes": hashes,
                   "complete": complete, "repeatability": "PASS" if complete and hashes[0] == hashes[1] else "BLOCKED_OR_MISMATCH",
                   "independence": "UNVERIFIED"}
            core_catalog.append(row)
            observations[key] = passes[0]
            print("CORE", key, row["repeatability"], flush=True)
    comparisons = []
    for block in registry["blocks"]:
        first = observations[f"{registry['primary_provider']}-{block['number']}"]
        for source in registry["providers"]:
            if source["id"] == registry["primary_provider"]:
                continue
            other = observations[f"{source['id']}-{block['number']}"]
            row = {"reference": registry["primary_provider"], "comparison_provider": source["id"], "block": block["number"]}
            if first["status"] == other["status"] == "PASS":
                row.update(compare_fields(first["data"], other["data"]))
            else:
                row.update(independent_validation_status="INDEPENDENT_ARCHIVE_VALIDATION_BLOCKED", fields=[],
                           reason="REFERENCE_OR_COMPARISON_IDENTITY_UNAVAILABLE")
            comparisons.append(row)
    a.write_json(output / "cross_provider_comparison.json", {"core_catalog": core_catalog, "comparisons": comparisons,
                 "overall": "INDEPENDENT_ARCHIVE_VALIDATION_BLOCKED"})
    primary = next(p for p in registry["providers"] if p["id"] == registry["primary_provider"])
    catalog = []
    for block in registry["blocks"]:
        passes = []
        for repeat in [1, 2]:
            rpc = Rpc(primary, block, registry["limits"]["max_rpc_calls_per_primary_block_pass"])
            ident = safe(lambda: identity(rpc))
            components = {}
            if ident["status"] == "PASS":
                for pool in registry["pools"]:
                    components[pool["id"]] = safe(lambda p=pool: pool_full_range(rpc, p, registry))
                    print("TICKS", block["number"], repeat, pool["id"], components[pool["id"]]["status"], flush=True)
                components["oracle"] = safe(lambda: oracle_trace(rpc, registry))
                print("ORACLE", block["number"], repeat, components["oracle"]["status"], flush=True)
                components["borrowers"] = safe(lambda: borrowers(rpc, registry))
                print("BORROWERS", block["number"], repeat, components["borrowers"]["status"], flush=True)
                end = safe(lambda: identity(rpc))
                if end != ident:
                    ident = {"status": "FAIL", "kind": "DATA_IDENTITY_FAILURE", "data": None, "reason": "HEADER_CHANGED_DURING_PASS"}
            hashes = {}
            for name, result in components.items():
                metadata = dump_gzip(output / "components" / f"{block['number']}-pass{repeat}-{name}.json.gz", result)
                hashes[name] = {"status": result["status"], "content_sha256": a.digest(result["data"]) if result["status"] == "PASS" else None,
                                "file": "components/" + metadata["file"], "kind": result.get("kind")}
            save_journal(output, f"primary-{block['number']}-pass{repeat}", rpc.records)
            passes.append({"identity": ident, "components": hashes, "rpc_requests": rpc.next_id})
            rpc.client.close()
        statuses = {}
        for name in sorted(set(passes[0]["components"]) | set(passes[1]["components"])):
            left, right = [p["components"].get(name) for p in passes]
            if left and right and left["status"] == right["status"] == "PASS":
                statuses[name] = "PASS" if left["content_sha256"] == right["content_sha256"] else "FAIL_CONTENT_MISMATCH"
            else:
                statuses[name] = "BLOCKED_OR_FAILED_COMPONENT"
        catalog.append({"block": block, "provider": primary["id"], "passes": passes, "repeatability": statuses})
        a.write_json(output / "validation_catalog.json", catalog)
    files = []
    for path in sorted(output.rglob("*")):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        row = {"path": path.relative_to(output).as_posix(), "size_bytes": len(raw),
               "sha256": hashlib.sha256(raw).hexdigest(), "hash_domain": "ACTUAL_SAVED_FILE_BYTES"}
        if path.suffix == ".gz":
            decoded = gzip.decompress(raw)
            row.update(uncompressed_size=len(decoded), uncompressed_sha256=hashlib.sha256(decoded).hexdigest())
        files.append(row)
    a.write_json(output / "collection_manifest.json", {"source_commit": os.getenv("GITHUB_SHA"),
                 "run_id": os.getenv("GITHUB_RUN_ID"), "registration_canonical_sha256": a.digest(registry),
                 "collected_at_utc": datetime.now(UTC).isoformat(), "files": files,
                 "raw_capture": "Canonical parsed JSON-RPC requests/results; not original HTTP wire bytes",
                 "new_stress_or_monte_carlo": False, "V2_scientifically_validated": False})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    if registry["stage"] == "REGISTERED_COLLECTION":
        run_validation(registry, args.output)
    else:
        probe(registry, args.output)


if __name__ == "__main__":
    main()
