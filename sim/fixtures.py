from __future__ import annotations

from decimal import Decimal
from hashlib import sha256

from sim.dex.uniswap_v3 import sqrt_price_x96_from_weth_price, tick_from_sqrt_price_x96
from sim.schemas import BorrowerPosition, DexState, LiquidityTick

D = Decimal
FIXTURE_BLOCK = 22_000_000
FIXTURE_PRICE = D("3200")


def fixture_positions(count: int = 40) -> list[BorrowerPosition]:
    target_hfs = [
        "1.03",
        "1.07",
        "1.10",
        "1.14",
        "1.18",
        "1.21",
        "1.23",
        "1.24",
        "1.255",
        "1.265",
        "1.275",
        "1.29",
        "1.31",
        "1.34",
        "1.38",
        "1.42",
    ]
    target_hfs.extend(
        str(Decimal("1.45") + Decimal(i) * Decimal("0.035")) for i in range(max(0, count - len(target_hfs)))
    )
    positions: list[BorrowerPosition] = []
    for index, hf_text in enumerate(target_hfs[:count]):
        debt = D(18_000 + index * 2_100)
        threshold = D("0.825")
        other_collateral = D("2500") if index % 9 == 0 else D("0")
        other_debt = D("1500") if index % 11 == 0 else D("0")
        collateral = (D(hf_text) * (debt + other_debt) / threshold - other_collateral) / FIXTURE_PRICE
        digest = sha256(f"defi-stress-fixture-{index}".encode()).hexdigest()[:12]
        positions.append(
            BorrowerPosition(
                borrower_hash=f"borrower-{digest}",
                collateral_weth=collateral,
                debt_usdc=debt,
                liquidation_threshold=threshold,
                ltv=D("0.80"),
                other_collateral_usd=other_collateral,
                other_debt_usd=other_debt,
            )
        )
    return positions


def fixture_dex() -> DexState:
    sqrt = sqrt_price_x96_from_weth_price(FIXTURE_PRICE)
    tick = tick_from_sqrt_price_x96(sqrt)
    liquidity = D("4.2e17")
    spacing = 60
    upper_one = ((tick // spacing) + 3) * spacing
    upper_two = upper_one + 6 * spacing
    return DexState(
        pool_address="0x00000000000000000000000000000000F17E0001",
        token0="USDC",
        token1="WETH",
        fee=3000,
        tick_spacing=spacing,
        sqrt_price_x96=sqrt,
        tick=tick,
        liquidity=liquidity,
        ticks=[
            LiquidityTick(upper_one, D("1.1e17"), D("1.1e17")),
            LiquidityTick(upper_two, D("-0.8e17"), D("0.8e17")),
        ],
        source="FIXTURE",
    )


def fixture_snapshot() -> dict[str, object]:
    positions = fixture_positions()
    dex = fixture_dex()
    return {
        "id": "fixture-main-v1",
        "mode": "FIXTURE",
        "label": "Synthetic deterministic fixture — not Mainnet data",
        "chain_id": 1,
        "block_number": FIXTURE_BLOCK,
        "block_hash": "0x" + sha256(b"defi-stress-fixture-block").hexdigest(),
        "block_timestamp": "2026-09-14T00:00:00Z",
        "retrieved_at": "2026-09-14T00:00:00Z",
        "source_manifest": {
            "application": {"model_version": "0.1.0", "fixture_version": "golden-v1"},
            "aave": {"market": "FIXTURE patterned after Aave V3 Ethereum"},
            "uniswap": {"model": "V3 sqrtPriceX96 and initialized-tick fixture"},
        },
        "aave_market": "Aave V3 Ethereum (fixture semantics)",
        "aave_reserves": [
            {"symbol": "WETH", "decimals": 18, "ltv": 0.80, "liquidation_threshold": 0.825, "liquidation_bonus": 1.05},
            {"symbol": "USDC", "decimals": 6, "oracle_price": 1.0},
        ],
        "borrowers": positions,
        "dex_pool": dex,
        "dex_pools": [dex],
        "dex_ticks": dex.ticks,
        "oracle_prices": {"WETH": FIXTURE_PRICE, "USDC": D("1")},
        "external_prices": {"WETH": FIXTURE_PRICE, "USDC": D("1")},
        "stablecoin_state": {"symbol": "USDC", "price": D("1"), "depeg_bps": D("0")},
        "coverage": {
            "candidates_discovered": len(positions),
            "positions_loaded": len(positions),
            "active_borrowers": len(positions),
            "weth_collateral_borrowers": len(positions),
            "usdc_borrowers": len(positions),
            "weth_usdc_cohort": len(positions),
            "failed_reads": 0,
            "excluded_positions": 0,
            "coverage_pct": 100,
            "cohort_label": "Deterministic fixture cohort",
        },
        "data_quality_flags": [
            {
                "code": "FIXTURE_DATA",
                "severity": "INFO",
                "message": "This snapshot is synthetic and must not be labelled Mainnet.",
            }
        ],
    }
