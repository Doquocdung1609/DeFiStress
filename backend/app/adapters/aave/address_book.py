from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

MANIFEST_URL = "https://assets.aave.com/address-book/releases/latest/manifest.json"
MODULE_URL = "https://assets.aave.com/address-book/releases/latest/modules/AaveV3Ethereum.json"


@dataclass(frozen=True, slots=True)
class AaveAddressBook:
    chain_id: int
    pool: str
    pool_addresses_provider: str
    oracle: str
    data_provider: str
    ui_pool_data_provider: str
    weth: str
    usdc: str
    version: str
    commit: str
    source_url: str = MODULE_URL


def load_aave_ethereum_address_book(timeout: float = 20.0) -> AaveAddressBook:
    manifest: dict[str, Any] = httpx.get(MANIFEST_URL, timeout=timeout).json()
    module: dict[str, Any] = httpx.get(MODULE_URL, timeout=timeout).json()
    assets = module["ASSETS"]
    version = str(manifest.get("packageVersion") or manifest.get("version") or "latest")
    return AaveAddressBook(
        chain_id=int(module["CHAIN_ID"]),
        pool=module["POOL"],
        pool_addresses_provider=module["POOL_ADDRESSES_PROVIDER"],
        oracle=module["ORACLE"],
        data_provider=module["AAVE_PROTOCOL_DATA_PROVIDER"],
        ui_pool_data_provider=module["UI_POOL_DATA_PROVIDER"],
        weth=assets["WETH"]["UNDERLYING"],
        usdc=assets["USDC"]["UNDERLYING"],
        version=version,
        commit=str(manifest.get("commit", "unknown")),
    )
