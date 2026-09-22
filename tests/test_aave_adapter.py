from backend.app.adapters.aave.events import EVENTS
from backend.app.adapters.uniswap.factory import FEE_TIERS


def test_required_aave_discovery_events_are_present() -> None:
    names = " ".join(EVENTS)
    for event in ("Borrow", "Repay", "Supply", "Withdraw", "LiquidationCall"):
        assert event in names


def test_all_uniswap_fee_tiers_are_considered() -> None:
    assert FEE_TIERS == (100, 500, 3000, 10_000)
