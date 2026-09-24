from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
from typing import Any

from sim.schemas import BorrowerPosition

D = Decimal


def load_position(
    pool: Any,
    data_provider: Any,
    user: str,
    weth: str,
    usdc: str,
    block_identifier: int,
    weth_decimals: int = 18,
    usdc_decimals: int = 6,
) -> tuple[BorrowerPosition, dict[str, Any]] | None:
    account = pool.functions.getUserAccountData(user).call(block_identifier=block_identifier)
    if int(account[1]) <= 0:
        return None
    weth_user = data_provider.functions.getUserReserveData(weth, user).call(block_identifier=block_identifier)
    usdc_user = data_provider.functions.getUserReserveData(usdc, user).call(block_identifier=block_identifier)
    supplied_weth = D(int(weth_user[0])) / (D(10) ** weth_decimals)
    weth_usage_as_collateral_enabled = bool(weth_user[8])
    collateral_weth = supplied_weth if weth_usage_as_collateral_enabled else D(0)
    usdc_debt = D(int(usdc_user[1]) + int(usdc_user[2])) / (D(10) ** usdc_decimals)
    # Aave base currency uses 8 decimals on Ethereum V3.
    total_collateral = D(int(account[0])) / D("1e8")
    total_debt = D(int(account[1])) / D("1e8")
    known_collateral = D(0)  # filled by market service after the WETH oracle read
    other_debt = max(D(0), total_debt - usdc_debt)
    borrower_hash = "borrower-" + sha256(user.lower().encode()).hexdigest()[:12]
    position = BorrowerPosition(
        borrower_hash=borrower_hash,
        collateral_weth=collateral_weth,
        debt_usdc=usdc_debt,
        liquidation_threshold=D(int(account[3])) / D(10_000),
        ltv=D(int(account[4])) / D(10_000),
        other_collateral_usd=max(D(0), total_collateral - known_collateral),
        other_debt_usd=other_debt,
    )
    provenance = {
        "raw_address": user,
        "total_collateral_base": str(account[0]),
        "total_debt_base": str(account[1]),
        "available_borrows_base": str(account[2]),
        "current_liquidation_threshold_bps": int(account[3]),
        "ltv_bps": int(account[4]),
        "aave_health_factor_ray": str(account[5]),
        "aave_health_factor": str(D(int(account[5])) / D("1e18")),
        "supplied_weth": str(supplied_weth),
        "collateral_weth": str(collateral_weth),
        "weth_usage_as_collateral_enabled": weth_usage_as_collateral_enabled,
    }
    return position, provenance
