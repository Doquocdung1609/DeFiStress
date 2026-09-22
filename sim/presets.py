from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from sim.schemas import Scenario


def scenario_presets() -> dict[str, Scenario]:
    """Named, reproducible starting points for the scenario builder."""
    baseline = Scenario()
    return {
        "Baseline": replace(
            baseline,
            name="Baseline",
            shock_pct=Decimal("-10"),
            liquidity_haircut_pct=Decimal("0"),
            gas_multiplier=Decimal("1"),
            arbitrage_capacity_pct=Decimal("100"),
        ),
        "Moderate": replace(
            baseline,
            name="Moderate",
            shock_pct=Decimal("-15"),
            liquidity_haircut_pct=Decimal("25"),
            gas_multiplier=Decimal("1.5"),
            arbitrage_capacity_pct=Decimal("75"),
        ),
        "Severe": replace(
            baseline,
            name="Severe",
            shock_pct=Decimal("-30"),
            liquidity_haircut_pct=Decimal("60"),
            gas_multiplier=Decimal("4"),
            arbitrage_capacity_pct=Decimal("25"),
        ),
        "Low Liquidity": replace(baseline, name="Low Liquidity", liquidity_haircut_pct=Decimal("75")),
        "High Gas": replace(baseline, name="High Gas", gas_multiplier=Decimal("8")),
        "No Arbitrage": replace(baseline, name="No Arbitrage", arbitrage_capacity_pct=Decimal("0")),
        "Strong Arbitrage": replace(baseline, name="Strong Arbitrage", arbitrage_capacity_pct=Decimal("100")),
        "Policy Experiment": replace(
            baseline,
            name="Policy Experiment",
            liquidation_threshold_override=Decimal("0.8"),
            liquidation_bonus_override=Decimal("1.04"),
        ),
    }
