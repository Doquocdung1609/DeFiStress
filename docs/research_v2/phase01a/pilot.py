"""Read-only historical feasibility/pilot; no simulation or transaction methods."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path


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
    from backend.app.adapters.rpc import ReadOnlyRpcClient

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


class HistoricalSession:
    """Reuse V1 transport, restrict state calls to EIP-1898 registered hash."""

    def __init__(self, url: str, block: dict, rpc=None):
        if rpc is None:
            from backend.app.adapters.rpc import ReadOnlyRpcClient

            rpc = ReadOnlyRpcClient(url, timeout=15)
        self.rpc = rpc
        self.block = block
        self.records = []
        self.chain = self.read("eth_chainId", [])
        if int(self.chain, 16) != 1:
            raise ValueError("CHAIN_ID_MISMATCH")

    def read(self, method: str, params: list):
        if method not in {"eth_chainId", "eth_call", "eth_getBlockByNumber", "eth_getLogs"}:
            raise ValueError("METHOD_NOT_PERMITTED")
        if len(self.records) >= 800:
            raise ValueError("PILOT_REQUEST_BUDGET_EXCEEDED")
        try:
            value = self.rpc.call(method, params)
            self.records.append({"method": method, "params": params, "result": value})
            if value is None:
                raise ValueError("MISSING_RPC_RESULT")
            return value
        except Exception as exc:
            self.records.append({"method": method, "params": params, "error": str(exc)[:1000]})
            raise

    def state_call(self, params: list):
        if len(params) != 2 or params[1] not in (hex(self.block["number"]), self.block["number"]):
            raise ValueError("UNPINNED_STATE_CALL")
        # No fallback to latest or another height when the provider lacks EIP-1898.
        return self.read("eth_call", [params[0], {"blockHash": self.block["expected_hash"], "requireCanonical": True}])

    def header(self):
        return validate_header(self.read("eth_getBlockByNumber", [hex(self.block["number"]), False]),
                               self.block["number"], self.block["expected_hash"])

    def logs(self, address: str, topic: str) -> list:
        records = self.read("eth_getLogs", [{"address": address, "topics": [topic],
                                            "blockHash": self.block["expected_hash"]}])
        if not isinstance(records, list):
            raise ValueError("MISSING_LOG_LIST")
        for row in records:
            if (int(row["blockNumber"], 16) != self.block["number"]
                    or row["blockHash"].lower() != self.block["expected_hash"].lower()
                    or row["address"].lower() != address.lower() or row.get("removed", False)
                    or not row["topics"] or row["topics"][0].lower() != topic.lower()):
                raise ValueError("LOG_BLOCK_OR_ADDRESS_LEAKAGE")
        return sorted(records, key=lambda r: (int(r["transactionIndex"], 16), int(r["logIndex"], 16)))


def safe_component(fn) -> dict:
    try:
        return {"status": "AVAILABLE", "data": fn()}
    except Exception as exc:
        return {"status": "QUARANTINED", "data": None,
                "reason": f"{type(exc).__name__}: {str(exc)[:1000]}"}


def validate_pool_metadata(token0: str, token1: str, fee: int, decimals: list, expected: dict, tokens: dict):
    if token0.lower() != tokens["USDC"]["address"].lower() or token1.lower() != tokens["WETH"]["address"].lower():
        raise ValueError("POOL_TOKEN_ORDER_MISMATCH")
    if fee != expected["fee"]:
        raise ValueError("POOL_FEE_MISMATCH")
    if decimals != [tokens["USDC"]["decimals"], tokens["WETH"]["decimals"]]:
        raise ValueError("TOKEN_DECIMALS_MISMATCH")


def repeat_verdict(first: dict, second: dict) -> dict:
    identical = digest(first) == digest(second)
    complete = all(x["status"] == "AVAILABLE" for sweep in [first, second] for x in sweep["components"].values())
    return {"first_content_sha256": digest(first), "second_content_sha256": digest(second),
            "identical": identical,
            "status": ("PASS" if identical else "FAIL_CONTENT_MISMATCH") if complete else "NOT_EVALUABLE_INCOMPLETE"}


def make_web3(session: HistoricalSession):
    from web3 import Web3
    from web3.providers import BaseProvider

    class PinnedProvider(BaseProvider):
        def make_request(self, method, params):
            if method == "eth_call":
                value = session.state_call(list(params))
            elif method == "eth_chainId":
                value = session.chain  # Verified actual chain ID; no synthetic network identity.
            else:
                raise ValueError("WEB3_METHOD_NOT_PERMITTED: " + str(method))
            return {"jsonrpc": "2.0", "id": 1, "result": value}

    return Web3(PinnedProvider())


def function_abi(name: str, outputs: list, inputs: list | None = None) -> dict:
    return {"type": "function", "name": name, "stateMutability": "view",
            "inputs": inputs or [], "outputs": [{"type": typ} for typ in outputs]}


def read_contract(web3, address: str, name: str, outputs: list, block_number: int, args=(), inputs=None):
    contract = web3.eth.contract(address=web3.to_checksum_address(address),
                               abi=[function_abi(name, outputs, inputs)])
    return getattr(contract.functions, name)(*args).call(block_identifier=block_number)


def collect_pool(web3, registered: dict, registry: dict, number: int) -> dict:
    from backend.app.adapters.uniswap.contracts import FACTORY_ABI, POOL_ABI
    from backend.app.adapters.uniswap.ticks import bitmap_ticks

    checksum = web3.to_checksum_address
    tokens = registry["tokens"]
    factory = web3.eth.contract(address=checksum(registry["factory"]), abi=FACTORY_ABI)
    actual = factory.functions.getPool(checksum(tokens["USDC"]["address"]),
                                      checksum(tokens["WETH"]["address"]), registered["fee"]).call(block_identifier=number)
    if actual.lower() != registered["address"].lower():
        raise ValueError("FACTORY_POOL_ADDRESS_MISMATCH")
    pool = web3.eth.contract(address=checksum(actual), abi=POOL_ABI)
    token0 = pool.functions.token0().call(block_identifier=number)
    token1 = pool.functions.token1().call(block_identifier=number)
    fee = int(pool.functions.fee().call(block_identifier=number))
    decimals = [int(read_contract(web3, t, "decimals", ["uint8"], number)) for t in [token0, token1]]
    validate_pool_metadata(token0, token1, fee, decimals, registered, tokens)
    spacing = int(pool.functions.tickSpacing().call(block_identifier=number))
    if spacing != {500: 10, 3000: 60}[fee]:
        raise ValueError("TICK_SPACING_MISMATCH")
    liquidity = int(pool.functions.liquidity().call(block_identifier=number))
    slot0 = list(pool.functions.slot0().call(block_identifier=number))
    if not 0 < int(slot0[0]) < 2**160 or not -887272 <= int(slot0[1]) <= 887272:
        raise ValueError("INVALID_SLOT0")
    word_position = (int(slot0[1]) // spacing) >> 8
    bitmap = int(pool.functions.tickBitmap(word_position).call(block_identifier=number))
    initialized = bitmap_ticks(bitmap, word_position, spacing)
    selected = sorted(sorted(initialized, key=lambda t: (abs(t - int(slot0[1])), t))[:registry["tick_scope"]["max_tick_reads"]])
    ticks = []
    for tick in selected:
        raw = list(pool.functions.ticks(tick).call(block_identifier=number))
        if not raw[7] or raw[0] <= 0 or abs(raw[1]) > raw[0]:
            raise ValueError("INVALID_INITIALIZED_TICK")
        ticks.append({"tick": tick, "raw": [str(v) if not isinstance(v, bool) else v for v in raw]})
    return {"address": actual.lower(), "token0": token0.lower(), "token1": token1.lower(),
            "fee_millionths": fee, "decimals": decimals, "tick_spacing": spacing,
            "liquidity_raw": str(liquidity), "slot0_raw": [str(v) if not isinstance(v, bool) else v for v in slot0],
            "tick_sample": {"scope": "CURRENT_BITMAP_WORD_NEAREST_8_ONLY", "word_position": word_position,
                            "bitmap_raw": str(bitmap), "initialized_in_word": initialized, "ticks": ticks,
                            "all_initialized_ticks_read": len(initialized) == len(ticks),
                            "full_pool_reconstruction": False}}


def historical_aave_config(web3, registry: dict, number: int) -> dict:
    pool = registry["aave_pool"]
    provider = read_contract(web3, pool, "ADDRESSES_PROVIDER", ["address"], number)
    historical_pool = read_contract(web3, provider, "getPool", ["address"], number)
    if historical_pool.lower() != pool.lower():
        raise ValueError("HISTORICAL_AAVE_POOL_MISMATCH")
    oracle = read_contract(web3, provider, "getPriceOracle", ["address"], number)
    data_provider = read_contract(web3, provider, "getPoolDataProvider", ["address"], number)
    for value in [provider, oracle, data_provider]:
        if int(value, 16) == 0:
            raise ValueError("HISTORICAL_AAVE_CONFIG_ZERO_ADDRESS")
    base = read_contract(web3, oracle, "BASE_CURRENCY", ["address"], number)
    unit = int(read_contract(web3, oracle, "BASE_CURRENCY_UNIT", ["uint256"], number))
    if unit <= 0:
        raise ValueError("INVALID_ORACLE_BASE_UNIT")
    return {"pool": pool.lower(), "provider": provider.lower(), "oracle": oracle.lower(),
            "data_provider": data_provider.lower(), "base_currency": base.lower(), "base_unit_raw": str(unit),
            "configuration_source": "HISTORICAL_POOL_AND_ADDRESSES_PROVIDER_CALLS"}


def collect_aave(web3, session: HistoricalSession, registry: dict, header: dict) -> dict:
    from decimal import Decimal

    from backend.app.adapters.aave.contracts import DATA_PROVIDER_ABI, POOL_ABI

    number = header["number"]
    config = historical_aave_config(web3, registry, number)
    provider = web3.eth.contract(address=web3.to_checksum_address(config["data_provider"]), abi=DATA_PROVIDER_ABI)
    pool = web3.eth.contract(address=web3.to_checksum_address(config["pool"]), abi=POOL_ABI)
    assets = {}
    for symbol, token in registry["tokens"].items():
        asset = web3.to_checksum_address(token["address"])
        decimals = int(read_contract(web3, asset, "decimals", ["uint8"], number))
        if decimals != token["decimals"]:
            raise ValueError("RESERVE_DECIMALS_MISMATCH")
        reserve_config = list(provider.functions.getReserveConfigurationData(asset).call(block_identifier=number))
        if int(reserve_config[0]) != decimals:
            raise ValueError("RESERVE_CONFIG_DECIMALS_MISMATCH")
        reserve = list(provider.functions.getReserveData(asset).call(block_identifier=number))
        if int(reserve[-1]) > header["timestamp"]:
            raise ValueError("RESERVE_TIMESTAMP_LEAKAGE")
        source = read_contract(web3, config["oracle"], "getSourceOfAsset", ["address"], number,
                               args=(asset,), inputs=[{"name": "asset", "type": "address"}])
        price = int(read_contract(web3, config["oracle"], "getAssetPrice", ["uint256"], number,
                                  args=(asset,), inputs=[{"name": "asset", "type": "address"}]))
        if price <= 0 or int(source, 16) == 0:
            raise ValueError("ORACLE_SOURCE_OR_PRICE_UNAVAILABLE")
        assets[symbol] = {"asset": asset.lower(), "decimals": decimals,
                          "reserve_configuration_raw": [str(v) if not isinstance(v, bool) else v for v in reserve_config],
                          "reserve_data_raw": [str(v) for v in reserve],
                          "price_raw": str(price), "price_in_base_currency": str(Decimal(price) / Decimal(config["base_unit_raw"])),
                          "price_source_address": source.lower(),
                          "source_trace_scope": "AAVE_CONFIG_TO_SOURCE_ADDRESS_AND_EFFECTIVE_PRICE_ONLY",
                          "underlying_aggregator_round_history": "NOT_VERIFIED"}
    borrowers = []
    for user in registry["borrowers"]:
        account = list(pool.functions.getUserAccountData(web3.to_checksum_address(user)).call(block_identifier=number))
        per_asset = {}
        for symbol, token in registry["tokens"].items():
            raw = list(provider.functions.getUserReserveData(web3.to_checksum_address(token["address"]),
                       web3.to_checksum_address(user)).call(block_identifier=number))
            per_asset[symbol] = [str(v) if not isinstance(v, bool) else v for v in raw]
        borrowers.append({"address": user, "account_raw": [str(v) for v in account], "user_reserve_raw": per_asset})
    return {"configuration": config, "assets": assets, "borrowers": borrowers,
            "portfolio_base_unit": config["base_unit_raw"], "health_factor_unit": "1e18",
            "debt_quantities": "Token raw amounts; no assumed USDC/USD=1 conversion",
            "availability_scope": "Three fixed V1-address sentinels; not a market census"}


def collect_once(url: str, block: dict, registry: dict) -> tuple[dict, list]:
    from web3 import Web3

    from backend.app.adapters.aave.events import EVENTS

    session = HistoricalSession(url, block)
    header = session.header()
    web3 = make_web3(session)
    components = {}
    for pool in registry["pools"]:
        components[pool["id"]] = safe_component(lambda p=pool: collect_pool(web3, p, registry, block["number"]))
    components["aave"] = safe_component(lambda: collect_aave(web3, session, registry, header))
    liquidation = next(s for s in EVENTS if s.startswith("LiquidationCall("))
    swap = "Swap(address,address,int256,int256,uint160,uint128,int24)"
    for name, address, signature in [("liquidation_logs", registry["aave_pool"], liquidation)] + [
        ("swap_logs_" + p["id"], p["address"], swap) for p in registry["pools"]
    ]:
        topic = "0x" + Web3.keccak(text=signature).hex().removeprefix("0x")
        components[name] = safe_component(lambda a=address, t=topic: session.logs(a, t))
    if session.header() != header or int(session.read("eth_chainId", []), 16) != 1:
        raise ValueError("END_OF_SWEEP_IDENTITY_CHANGED")
    return {"chain_id": 1, "block": header, "components": components}, session.records


def collect(registry: dict, output: Path) -> None:
    if registry["status"] != "REGISTERED_HASHES_LOCKED":
        raise ValueError("SAMPLE_HASH_REGISTRATION_NOT_LOCKED")
    if any(not b["expected_hash"] for b in registry["blocks"]):
        raise ValueError("MISSING_REGISTERED_HASH")
    catalog = []
    quarantine = []
    for source in registry["providers"]:
        for block in registry["blocks"]:
            ident = f"{source['id']}-{block['number']}"
            row = {"id": ident, "provider_id": source["id"], "block_number": block["number"],
                   "block_hash": block["expected_hash"], "registry_sha256": digest(registry)}
            sweeps = []
            for repeat in [1, 2]:
                try:
                    data, transcript = collect_once(source["url"], block, registry)
                    write_json(output / "raw" / f"{ident}-pass{repeat}.json", transcript)
                    write_json(output / "snapshots" / f"{ident}-pass{repeat}.json", data)
                    sweeps.append(data)
                    for name, component in data["components"].items():
                        if component["status"] != "AVAILABLE":
                            quarantine.append({"id": ident, "pass": repeat, "component": name, **component})
                except Exception as exc:
                    quarantine.append({"id": ident, "pass": repeat, "component": "snapshot_identity_or_transport",
                                       "status": "QUARANTINED", "data": None, "reason": str(exc)[:1000]})
                    # Retain one failed sweep per source/block; do not manufacture repeat equality.
                    break
            row["repeatability"] = repeat_verdict(*sweeps) if len(sweeps) == 2 else {"status": "NOT_EVALUABLE_DATA_ACCESS_BLOCKED"}
            row["component_statuses"] = ({k: v["status"] for k, v in sweeps[0]["components"].items()} if sweeps else None)
            catalog.append(row)
    write_json(output / "catalog.json", {"schema_version": "phase01a-historical-catalog-v1", "rows": catalog})
    write_json(output / "quarantine.json", quarantine)
    files = []
    for path in sorted(output.rglob("*.json")):
        data = path.read_bytes()
        files.append({"path": path.relative_to(output).as_posix(), "size_bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest(), "hash_domain": "ACTUAL_UTF8_CANONICAL_JSON_FILE_BYTES"})
    write_json(output / "collection_provenance.json", {"registry_sha256": digest(registry),
               "source_commit": os.environ.get("GITHUB_SHA"), "run_id": os.environ.get("GITHUB_RUN_ID"),
               "collected_at_utc": datetime.now(UTC).isoformat(), "records": files,
               "raw_scope": "Canonical JSON-RPC requests/parsed results, not original HTTP wire bytes",
               "new_stress_or_monte_carlo_run": False})
    print(json.dumps({"rows": len(catalog), "repeat_pass": sum(r["repeatability"]["status"] == "PASS" for r in catalog),
                      "quarantined_components": len(quarantine)}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    if registry["status"] == "REGISTERED_HASHES_LOCKED":
        collect(registry, args.output)
    else:
        discover(registry, args.output)


if __name__ == "__main__":
    main()
