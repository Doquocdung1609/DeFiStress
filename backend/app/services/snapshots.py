from __future__ import annotations

from dataclasses import fields
from decimal import Decimal
from typing import Any

from backend.app.db import Repository
from sim.fixtures import fixture_snapshot
from sim.schemas import BorrowerPosition, DexState, LiquidityTick


def ensure_fixture_snapshot(repository: Repository) -> dict[str, Any]:
    existing = repository.get_snapshot("fixture-main-v1")
    return existing or repository.save_snapshot(fixture_snapshot())


def simulation_inputs(snapshot: dict[str, Any]) -> tuple[list[BorrowerPosition], DexState, Decimal]:
    borrower_fields = {item.name for item in fields(BorrowerPosition)}
    positions = [
        BorrowerPosition(
            **{key: _decimal_if_numeric(key, value) for key, value in raw.items() if key in borrower_fields}
        )
        for raw in snapshot["borrowers"]
    ]
    pool = snapshot["dex_pool"]
    ticks = [
        LiquidityTick(int(raw["tick"]), Decimal(str(raw["liquidity_net"])), Decimal(str(raw["liquidity_gross"])))
        for raw in pool.get("ticks", snapshot.get("dex_ticks", []))
    ]
    dex_state = DexState(
        pool_address=pool["pool_address"],
        token0=pool["token0"],
        token1=pool["token1"],
        fee=int(pool["fee"]),
        tick_spacing=int(pool["tick_spacing"]),
        sqrt_price_x96=Decimal(str(pool["sqrt_price_x96"])),
        tick=int(pool["tick"]),
        liquidity=Decimal(str(pool["liquidity"])),
        ticks=ticks,
        token0_decimals=int(pool.get("token0_decimals", 6)),
        token1_decimals=int(pool.get("token1_decimals", 18)),
        source=pool.get("source", snapshot["mode"]),
    )
    initial_price = Decimal(str(snapshot["oracle_prices"]["WETH"]))
    return positions, dex_state, initial_price


def _decimal_if_numeric(key: str, value: Any) -> Any:
    decimal_fields = {
        "collateral_weth",
        "debt_usdc",
        "liquidation_threshold",
        "ltv",
        "other_collateral_usd",
        "other_debt_usd",
    }
    return Decimal(str(value)) if key in decimal_fields else value
