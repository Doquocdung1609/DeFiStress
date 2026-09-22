from decimal import Decimal
from typing import Any


def normalized_asset_price(oracle_contract: Any, asset: str, block_identifier: int) -> Decimal:
    raw = int(oracle_contract.functions.getAssetPrice(asset).call(block_identifier=block_identifier))
    unit = int(oracle_contract.functions.BASE_CURRENCY_UNIT().call(block_identifier=block_identifier))
    if unit <= 0:
        raise ValueError("Aave oracle BASE_CURRENCY_UNIT is invalid")
    return Decimal(raw) / Decimal(unit)
