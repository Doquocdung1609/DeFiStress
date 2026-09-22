from typing import Any

from web3 import Web3

from backend.app.adapters.uniswap.contracts import FACTORY_ABI

UNISWAP_V3_FACTORY = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
FEE_TIERS = (100, 500, 3000, 10_000)


def find_weth_usdc_pools(web3: Web3, weth: str, usdc: str, block_identifier: int) -> list[dict[str, Any]]:
    factory = web3.eth.contract(address=Web3.to_checksum_address(UNISWAP_V3_FACTORY), abi=FACTORY_ABI)
    found = []
    for fee in FEE_TIERS:
        address = factory.functions.getPool(weth, usdc, fee).call(block_identifier=block_identifier)
        if int(address, 16) != 0:
            found.append({"pool_address": address, "fee": fee})
    return found
