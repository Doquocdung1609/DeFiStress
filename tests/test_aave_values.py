from decimal import Decimal
from unittest.mock import MagicMock

from backend.app.adapters.aave.oracle import normalized_asset_price
from backend.app.adapters.aave.positions import load_position


def test_oracle_price_uses_reported_base_currency_unit() -> None:
    oracle = MagicMock()
    oracle.functions.getAssetPrice.return_value.call.return_value = 320_000_000_000
    oracle.functions.BASE_CURRENCY_UNIT.return_value.call.return_value = 100_000_000
    assert normalized_asset_price(oracle, "0xasset", 123) == Decimal("3200")


def test_position_normalizes_weth_and_usdc_token_decimals() -> None:
    pool = MagicMock()
    provider = MagicMock()
    pool.functions.getUserAccountData.return_value.call.return_value = (
        10_000 * 10**8,
        3_000 * 10**8,
        7_000 * 10**8,
        8_250,
        8_000,
        275 * 10**16,
    )
    provider.functions.getUserReserveData.side_effect = [
        MagicMock(call=MagicMock(return_value=(2 * 10**18, 0, 0, 0, 0, 0, 0, 0, True))),
        MagicMock(call=MagicMock(return_value=(0, 500 * 10**6, 2_500 * 10**6, 0, 0, 0, 0, 0, False))),
    ]
    loaded = load_position(pool, provider, "0xuser", "0xweth", "0xusdc", 123)
    assert loaded is not None
    position, evidence = loaded
    assert position.collateral_weth == Decimal("2")
    assert position.debt_usdc == Decimal("3000")
    assert Decimal(evidence["aave_health_factor"]) == Decimal("2.75")
