from __future__ import annotations

from decimal import Decimal
from typing import Any

from web3 import Web3

from backend.app.adapters.aave.address_book import AaveAddressBook
from backend.app.adapters.aave.contracts import DATA_PROVIDER_ABI, ORACLE_ABI, POOL_ABI
from backend.app.adapters.aave.oracle import normalized_asset_price
from backend.app.adapters.aave.positions import load_position
from sim.schemas import BorrowerPosition

D = Decimal


class AaveMarketReader:
    def __init__(self, web3: Web3, addresses: AaveAddressBook):
        self.web3 = web3
        self.addresses = addresses
        self.pool = web3.eth.contract(address=Web3.to_checksum_address(addresses.pool), abi=POOL_ABI)
        self.data_provider = web3.eth.contract(
            address=Web3.to_checksum_address(addresses.data_provider), abi=DATA_PROVIDER_ABI
        )
        self.oracle = web3.eth.contract(address=Web3.to_checksum_address(addresses.oracle), abi=ORACLE_ABI)

    def reserve(self, symbol: str, asset: str, block_identifier: int) -> dict[str, Any]:
        config = self.data_provider.functions.getReserveConfigurationData(asset).call(block_identifier=block_identifier)
        caps = self.data_provider.functions.getReserveCaps(asset).call(block_identifier=block_identifier)
        reserve = self.data_provider.functions.getReserveData(asset).call(block_identifier=block_identifier)
        price = normalized_asset_price(self.oracle, asset, block_identifier)
        decimals = int(config[0])
        scale = D(10) ** decimals
        return {
            "symbol": symbol,
            "address": asset,
            "decimals": decimals,
            "ltv": str(D(int(config[1])) / D(10_000)),
            "liquidation_threshold": str(D(int(config[2])) / D(10_000)),
            "liquidation_bonus": str(D(int(config[3])) / D(10_000)),
            "reserve_factor": str(D(int(config[4])) / D(10_000)),
            "borrow_cap": int(caps[0]),
            "supply_cap": int(caps[1]),
            "oracle_price": str(price),
            "total_supply": str(D(int(reserve[2])) / scale),
            "total_stable_debt": str(D(int(reserve[3])) / scale),
            "total_variable_debt": str(D(int(reserve[4])) / scale),
            "liquidity_rate_ray": str(reserve[5]),
            "variable_borrow_rate_ray": str(reserve[6]),
            "liquidity_index_ray": str(reserve[9]),
            "variable_borrow_index_ray": str(reserve[10]),
            "last_update_timestamp": int(reserve[11]),
            "usage_as_collateral_enabled": bool(config[5]),
            "borrowing_enabled": bool(config[6]),
            "active": bool(config[8]),
            "frozen": bool(config[9]),
        }

    def positions(
        self, users: list[str], block_identifier: int
    ) -> tuple[list[BorrowerPosition], list[dict[str, Any]], int]:
        positions: list[BorrowerPosition] = []
        provenance: list[dict[str, Any]] = []
        failed = 0
        for user in users:
            try:
                loaded = load_position(
                    self.pool,
                    self.data_provider,
                    Web3.to_checksum_address(user),
                    self.addresses.weth,
                    self.addresses.usdc,
                    block_identifier,
                )
                if loaded:
                    position, evidence = loaded
                    positions.append(position)
                    provenance.append({"borrower_hash": position.borrower_hash, **evidence})
            except Exception:
                failed += 1
        return positions, provenance, failed
