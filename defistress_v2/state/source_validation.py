"""Schema/coverage checks of saved fields, never a historical reconstruction engine.

Bounds and identities here describe only the registered Phase01B saved schema.
Imported economic checks remain SOURCE_DECLARED. No price/HF/swap calculation.
"""

from __future__ import annotations

import re
from typing import Any

from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.contracts.identity import BlockRef

ADDRESS = re.compile(r"0x[0-9a-fA-F]{40}")
HASH = re.compile(r"0x[0-9a-fA-F]{64}")
INTEGER = re.compile(r"0|-?[1-9][0-9]*")
POOL = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"


def exact(value: object, label: str, lower: int = 0, upper: int = 2**256 - 1) -> int:
    if type(value) is not int or not lower <= value <= upper:
        raise TypeContractError(f"{label}: exact integer outside schema bounds")
    return value


def integer_string(value: object, label: str, *, signed: bool = False, positive: bool = False) -> int:
    if type(value) is not str or len(value) > 79 or INTEGER.fullmatch(value) is None:
        raise TypeContractError(f"{label}: noncanonical integer string")
    number = int(value)
    if not (-(2**255) if signed else (1 if positive else 0)) <= number <= (2**255 - 1 if signed else 2**256 - 1):
        raise TypeContractError(f"{label}: integer string outside schema bounds")
    return number


def obj(value: object, label: str) -> dict[str, Any]:
    if type(value) is not dict:
        raise TypeContractError(f"{label}: expected object")
    return value


def array(value: object, label: str) -> list[Any]:
    if type(value) is not list:
        raise TypeContractError(f"{label}: expected array")
    return value


def address(value: object, label: str) -> str:
    if type(value) is not str or ADDRESS.fullmatch(value) is None:
        raise TypeContractError(f"{label}: invalid address")
    return value.lower()


def configuration(value: object) -> dict[str, Any]:
    config = obj(value, "configuration")
    if address(config.get("pool"), "Aave Pool") != POOL:
        raise TypeContractError("configuration Aave Pool mismatch")
    for key in ("provider", "data_provider", "oracle", "base_currency"):
        address(config.get(key), key)
    integer_string(config.get("base_unit"), "base unit", positive=True)
    exact(config.get("pool_revision"), "pool revision")
    if config.get("revision_status") != "AVAILABLE":
        raise TypeContractError("configuration revision is not available")
    return config


def pool_fields(data: dict[str, Any], pool_id: str, max_ticks: int) -> None:
    spacing = exact(data.get("spacing"), "tick spacing", 1)
    if spacing != (60 if pool_id == "P3000" else 10):
        raise TypeContractError("registered pool spacing mismatch")
    if type(data.get("fee_millionths")) is not int or data["fee_millionths"] != (3000 if pool_id == "P3000" else 500):
        raise TypeContractError("pool fee must be an exact registered integer")
    decimals = array(data.get("decimals"), "pool decimals")
    if any(type(x) is not int for x in decimals) or decimals != [6, 18]:
        raise TypeContractError("registered token decimals mismatch")
    exact(data.get("current_tick"), "current tick", -887272, 887272)
    integer_string(data.get("sqrt_price_x96"), "sqrtPriceX96", positive=True)
    if int(data["sqrt_price_x96"]) >= 2**160:
        raise TypeContractError("sqrtPriceX96 exceeds uint160")
    if integer_string(data.get("active_liquidity_raw"), "active liquidity") >= 2**128:
        raise TypeContractError("active liquidity exceeds uint128")
    lower = exact(data.get("required_lower_tick"), "lower tick", -887272, 887272)
    upper = exact(data.get("required_upper_tick"), "upper tick", -887272, 887272)
    if lower > upper or lower % spacing or upper % spacing or not lower <= data["current_tick"] <= upper:
        raise TypeContractError("registered tick band/spacing is inconsistent")
    if (
        data.get("coverage_status") != "PASS_REGISTERED_RANGE_COMPLETE"
        or data.get("missing_ticks") != []
        or data.get("missing_words") != []
    ):
        raise TypeContractError("registered tick band has missing/unverified fields")
    if (
        data.get("full_legal_pool_tick_coverage") is not False
        or data.get("outside_status") != "OUT_OF_SCOPE_NOT_RECONSTRUCTED"
    ):
        raise TypeContractError("partial registered band must not be promoted to full pool")
    required_words = array(data.get("required_words"), "required words")
    if required_words != list(range((lower // spacing) >> 8, ((upper // spacing) >> 8) + 1)) or any(
        type(x) is not int for x in required_words
    ):
        raise TypeContractError("registered bitmap word coverage is not contiguous")
    words: dict[int, int] = {}
    for record in array(data.get("bitmaps"), "bitmap records"):
        item = obj(record, "bitmap")
        word = exact(item.get("word"), "bitmap word", -32768, 32767)
        if word in words:
            raise TypeContractError("duplicate bitmap word")
        words[word] = integer_string(item.get("bitmap"), "bitmap")
    if sorted(words) != required_words:
        raise TypeContractError("missing or extraneous bitmap word")
    ticks = array(data.get("ticks"), "ticks")
    if len(ticks) > max_ticks:
        raise TypeContractError("pool tick count exceeds resource limit")
    indices: set[int] = set()
    for record in ticks:
        item = obj(record, "tick")
        tick = exact(item.get("tick"), "tick index", lower, upper)
        if tick in indices or tick % spacing:
            raise TypeContractError("duplicate or misaligned tick")
        indices.add(tick)
        gross = integer_string(item.get("gross"), "liquidity gross")
        net = integer_string(item.get("net"), "liquidity net", signed=True)
        if gross >= 2**128 or not -(2**127) <= net < 2**127 or gross < abs(net):
            raise TypeContractError("tick liquidity gross/net schema inconsistency")
        compressed = tick // spacing
        if not words[compressed >> 8] & (1 << (compressed & 255)):
            raise TypeContractError("tick has no matching initialized bitmap bit")
    # Coverage membership only: no liquidity reconstruction or price math.
    expected = {
        compressed * spacing
        for word, bitmap in words.items()
        for bit in range(256)
        if bitmap & (1 << bit) and lower <= (compressed := word * 256 + bit) * spacing <= upper
    }
    if indices != expected or exact(data.get("initialized_ticks_expected"), "initialized tick count") != len(indices):
        raise TypeContractError("initialized tick/bitmap coverage mismatch")


def oracle_fields(data: dict[str, Any], block: BlockRef | None) -> None:
    config = configuration(data.get("configuration"))
    assets = array(data.get("assets"), "oracle assets")
    if len(assets) != 2 or len({obj(x, "asset").get("symbol") for x in assets}) != 2:
        raise TypeContractError("oracle assets must be unique")
    for record in assets:
        asset = obj(record, "asset")
        integer_string(asset.get("aave_price_raw"), "Aave price", positive=True)
        integer_string(asset.get("source_answer_raw"), "source answer", positive=True)
        if integer_string(asset.get("base_unit"), "asset base unit", positive=True) != int(config["base_unit"]):
            raise TypeContractError("oracle base-unit mismatch")
        exact(asset.get("source_decimals"), "source decimals", 0, 255)
        trace = obj(asset.get("trace"), "source trace")
        if address(asset.get("source"), "source") != address(trace.get("address"), "trace address"):
            raise TypeContractError("oracle source/trace mismatch")
        source_decimals = obj(
            obj(trace.get("interfaces"), "source interfaces").get("decimals()"), "source decimals interface"
        )
        if (
            source_decimals.get("status") != "AVAILABLE"
            or exact(source_decimals.get("value"), "source interface decimals", 0, 255) != asset["source_decimals"]
        ):
            raise TypeContractError("oracle source decimal scale mismatch")
        for trace_record in [trace] + (
            [obj(trace["asset_to_usd_upstream"], "upstream")] if "asset_to_usd_upstream" in trace else []
        ):
            interfaces = obj(trace_record.get("interfaces"), "oracle interfaces")
            native = obj(interfaces.get("latestRoundData()"), "native round interface")
            round_value = trace_record.get("round")
            if native.get("status") != "AVAILABLE":
                if (
                    native.get("value") is not None
                    or round_value is not None
                    or trace_record.get("round_status") != "UNSUPPORTED_OR_UNAVAILABLE"
                ):
                    raise TypeContractError("unsupported native round promoted to observation")
                continue
            raw = array(native.get("value"), "native round vector")
            if len(raw) != 5:
                raise TypeContractError("invalid native round vector")
            for value in raw:
                exact(value, "round value")
            derived = obj(round_value, "normalized round trace")
            for key, position in (("round_id", 0), ("answer", 1), ("answered_in_round", 4)):
                if integer_string(derived.get(key), key) != raw[position]:
                    raise TypeContractError("round observation/normalized trace mismatch")
            for key, position in (("started_at", 2), ("updated_at", 3)):
                if exact(derived.get(key), key, 1) != raw[position]:
                    raise TypeContractError("round time trace mismatch")
            if raw[2] > raw[3] or (block is not None and raw[3] > block.timestamp_s):
                raise TypeContractError("oracle round timestamp leakage")
            if (
                trace_record.get("round_status") != "PASS"
                or derived.get("freshness_heartbeat_status") != "NOT_EVALUATED_NO_REGISTERED_HEARTBEAT"
            ):
                raise TypeContractError("round availability must not imply heartbeat freshness")


def borrower_fields(data: dict[str, Any], block: BlockRef, max_headers: int) -> None:
    configuration(data.get("configuration"))
    selected = array(data.get("selected_users"), "selected users")
    identities = [address(x, "selected borrower") for x in selected]
    if not identities or len(identities) > 8 or len(set(identities)) != len(identities):
        raise TypeContractError("selected borrower sample must be nonempty and unique")
    portfolios = array(data.get("portfolios"), "portfolios")
    if [address(obj(x, "portfolio").get("address"), "borrower") for x in portfolios] != identities:
        raise TypeContractError("portfolio coverage differs from the selected sample")
    count = exact(data.get("reserves_count"), "registered reserve count", 1, 128)
    coverage = obj(data.get("reserve_id_coverage"), "reserve coverage")
    if coverage.get("missing_assets") != [] or exact(coverage.get("available_ids"), "available reserve ids") != count:
        raise TypeContractError("source reserve coverage is incomplete")
    asset_sets: list[set[str]] = []
    id_sets: list[set[int]] = []
    for record in portfolios:
        portfolio = obj(record, "portfolio")
        if portfolio.get("missing_data_flags") != []:
            raise TypeContractError("portfolio declares missing dependencies")
        exact(portfolio.get("block_number"), "portfolio block")
        reserves = array(portfolio.get("reserves"), "reserves")
        if len(reserves) != count:
            raise TypeContractError("portfolio reserve coverage differs from declaration")
        assets: set[str] = set()
        ids: set[int] = set()
        for item_value in reserves:
            item = obj(item_value, "reserve")
            asset = address(item.get("asset"), "reserve asset")
            reserve_id = exact(item.get("reserve_id"), "reserve id", 0, 255)
            if asset in assets or reserve_id in ids:
                raise TypeContractError("duplicate reserve identity")
            assets.add(asset)
            ids.add(reserve_id)
            if any(
                item.get(k) != "AVAILABLE" for k in ("status", "price_status", "source_status", "token_decimals_status")
            ):
                raise TypeContractError("reserve dependency is unavailable")
            decimals = exact(item.get("decimals"), "reserve decimals", 0, 255)
            config_raw = array(item.get("configuration_raw"), "reserve configuration")
            balances = array(item.get("data"), "reserve balances")
            if len(config_raw) != 10 or len(balances) != 9:
                raise TypeContractError("unsupported reserve ABI vector schema")
            for x in config_raw[:5] + balances[:8]:
                exact(x, "reserve ABI integer")
            if any(type(x) is not bool for x in config_raw[5:] + balances[8:]):
                raise TypeContractError("reserve flags must be exact booleans")
            if config_raw[0] != decimals or config_raw[2] != exact(item.get("lt"), "reserve LT", 0, 10000):
                raise TypeContractError("reserve units/configuration mismatch")
            exact(item.get("price"), "reserve price", 1)
            address(item.get("source"), "reserve oracle source")
        asset_sets.append(assets)
        id_sets.append(ids)
        reconstruction = obj(portfolio.get("hf_reconstruction"), "source reconstruction trace")
        account_raw = array(portfolio.get("account_raw"), "account raw")
        if (
            len(account_raw) != 6
            or integer_string(reconstruction.get("contract_hf_raw"), "contract HF") != account_raw[5]
        ):
            raise TypeContractError("source HF observation/trace disagreement")
        if account_raw[1] == 0 and (
            account_raw[5] != 2**256 - 1 or reconstruction.get("zero_debt_hf") != "UINT256_MAX_SENTINEL"
        ):
            raise TypeContractError("zero-debt sentinel must remain distinct from finite HF")
    if any(assets != asset_sets[0] for assets in asset_sets):
        raise TypeContractError("selected portfolios have inconsistent reserve sets")
    if any(ids != id_sets[0] for ids in id_sets):
        raise TypeContractError("selected portfolios have inconsistent reserve IDs")
    window = array(data.get("event_window"), "event window")
    if window != [block.number - 1023, block.number] or any(type(x) is not int for x in window):
        raise TypeContractError("borrower discovery window mismatch")
    discovery = obj(data.get("discovery_coverage"), "discovery coverage")
    headers = array(discovery.get("contiguous_headers"), "discovery headers")
    if len(headers) > max_headers or len(headers) != 1024 or discovery.get("missing_blocks") != []:
        raise TypeContractError("registered discovery header coverage is incomplete")
    previous_hash: str | None = None
    previous_time = -1
    for offset, item_value in enumerate(headers):
        header = obj(item_value, "header")
        if exact(header.get("number"), "header number") != window[0] + offset:
            raise TypeContractError("discovery header gap/duplicate")
        timestamp = exact(header.get("timestamp"), "header timestamp")
        if timestamp <= previous_time or timestamp > block.timestamp_s:
            raise TypeContractError("discovery timestamp leakage")
        for key in ("hash", "parent_hash"):
            if type(header.get(key)) is not str or HASH.fullmatch(header[key]) is None:
                raise TypeContractError("invalid discovery block hash")
        if previous_hash is not None and header["parent_hash"].lower() != previous_hash:
            raise TypeContractError("discovery parent linkage mismatch")
        previous_hash = header["hash"].lower()
        previous_time = timestamp
    if previous_hash != block.hash or previous_time != block.timestamp_s:
        raise TypeContractError("discovery history ends at another snapshot block")
