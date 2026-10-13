import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from sim import Scenario, fixture_snapshot, run_simulation
from sim.engine.threshold import find_cascade_threshold
from sim.fixtures import FIXTURE_PRICE, fixture_dex, fixture_positions
from sim.metrics.risk import unliquidated_debt


def test_golden_fixture_produces_endogenous_wave() -> None:
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario())
    assert result.metrics["cascade_depth"] >= 2
    assert result.metrics["total_liquidated_debt"] > result.metrics["direct_shock_liquidated_debt"]
    assert any(event.wave == 2 and event.event_type == "LIQUIDATION" for event in result.events)


def test_golden_fixture_matches_versioned_metrics() -> None:
    expected = json.loads(Path("data/fixtures/golden_expected.json").read_text(encoding="utf-8"))
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario())
    for metric in (
        "cascade_depth",
        "direct_shock_liquidated_debt",
        "total_liquidated_debt",
        "cascade_amplification",
        "max_price_impact",
        "bad_debt",
    ):
        assert abs(float(result.metrics[metric] or 0) - expected[metric]) < 1e-9


def test_result_is_reproducible() -> None:
    first = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario(), run_id="same")
    second = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario(), run_id="same")
    assert first.to_dict() == second.to_dict()


def test_invariants_hold() -> None:
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario())
    for position in result.final_positions:
        assert position.debt_usdc >= 0
        assert position.collateral_weth >= 0
    liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
    assert all(event.debt_repaid > 0 and event.collateral_seized > 0 for event in liquidations)
    assert [event.step for event in result.events] == sorted(event.step for event in result.events)


def test_no_direct_liquidation_handles_amplification_denominator() -> None:
    scenario = replace(Scenario(), shock_pct=Decimal("0"))
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)
    if result.metrics["direct_shock_liquidated_debt"] == 0:
        assert result.metrics["cascade_amplification"] is None


def test_threshold_search_finds_fixture_boundary() -> None:
    threshold = find_cascade_threshold(
        fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario(), coarse_step_pct=Decimal("2")
    )
    assert threshold is not None
    assert Decimal(0) <= threshold <= Decimal(50)


def test_fixture_is_explicitly_labelled() -> None:
    snapshot = fixture_snapshot()
    assert snapshot["mode"] == "FIXTURE"
    assert "not Mainnet" in snapshot["label"]


def test_liquidator_delay_advances_time_not_wave_identity() -> None:
    scenario = replace(Scenario(), liquidator_delay_steps=2)
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)
    liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
    assert liquidations[0].step == 3
    assert liquidations[0].wave == 1
    assert [point.wave for point in result.timeseries[:3]] == [0, 0, 0]


def test_liquidator_total_capital_is_never_exceeded() -> None:
    capital = Decimal("18000")
    scenario = replace(Scenario(), liquidator_capital_usdc=capital)
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)
    assert result.metrics["total_liquidated_debt"] <= capital


def test_impact_metrics_separate_forced_sale_from_post_arbitrage_spread() -> None:
    scenario = replace(Scenario(), arbitrage_capacity_pct=Decimal("100"))
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)
    reference_price = FIXTURE_PRICE * (Decimal(1) + scenario.shock_pct / Decimal(100))
    liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
    expected_intrawave = max(
        abs(event.dex_price_after - reference_price) / reference_price for event in liquidations
    )
    expected_post_arbitrage = max(
        abs(point.dex_price - reference_price) / reference_price for point in result.timeseries
    )

    intrawave = result.metrics["max_intrawave_liquidation_price_impact"]
    post_arbitrage = result.metrics["max_post_arbitrage_spread"]
    assert intrawave is not None and post_arbitrage is not None
    assert intrawave == expected_intrawave
    assert post_arbitrage == expected_post_arbitrage
    assert intrawave > post_arbitrage
    assert result.metrics["max_price_impact"] == post_arbitrage


def test_recovery_time_is_zero_when_tolerance_was_never_exceeded() -> None:
    scenario = replace(Scenario(), shock_pct=Decimal("0"))
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)

    assert result.metrics["recovery_tolerance_exceeded"] == 0
    assert result.metrics["time_to_recovery_seconds"] == 0


def test_recovery_time_is_first_post_dislocation_return_below_tolerance() -> None:
    scenario = replace(Scenario(), arbitrage_capacity_pct=Decimal("100"))
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)
    first_liquidation_step = min(
        event.step for event in result.events if event.event_type == "LIQUIDATION"
    )

    assert result.metrics["recovery_tolerance_exceeded"] == 1
    assert result.metrics["time_to_recovery_seconds"] == first_liquidation_step * scenario.timestep_seconds


def test_recovery_time_is_null_when_dislocation_never_recovers() -> None:
    scenario = replace(Scenario(), arbitrage_capacity_pct=Decimal("0"))
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)

    assert result.metrics["recovery_tolerance_exceeded"] == 1
    assert result.metrics["time_to_recovery_seconds"] is None


def test_unliquidated_debt_uses_scenario_liquidation_threshold_override() -> None:
    scenario = replace(Scenario(), liquidation_threshold_override=Decimal("0.70"))
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)
    valuation_price = min(
        Decimal(str(result.metrics["final_dex_price"])),
        Decimal(str(result.metrics["final_reference_price"])),
    )

    assert result.metrics["unliquidated_debt"] == unliquidated_debt(
        result.final_positions,
        valuation_price,
        scenario.usdc_price_usd,
        scenario.liquidation_threshold_override,
    )
    assert result.metrics["unliquidated_debt_legacy_recorded_lt"] == unliquidated_debt(
        result.final_positions,
        valuation_price,
        scenario.usdc_price_usd,
    )


def test_endogenous_wave_uses_newly_eligible_borrower_once() -> None:
    scenario = Scenario()
    positions = fixture_positions()
    result = run_simulation(positions, fixture_dex(), FIXTURE_PRICE, scenario)
    liquidations = [event for event in result.events if event.event_type == "LIQUIDATION"]
    hashes = [event.borrower_hash for event in liquidations]
    wave_two = next(event for event in liquidations if event.wave == 2)
    original = next(position for position in positions if position.borrower_hash == wave_two.borrower_hash)
    reference_price = FIXTURE_PRICE * (Decimal(1) + scenario.shock_pct / Decimal(100))
    wave_one_state = next(point for point in result.timeseries if point.wave == 1)
    wave_two_valuation_price = min(reference_price, wave_one_state.dex_price)

    assert len(hashes) == len(set(hashes))
    assert original.health_factor(reference_price, scenario.liquidation_threshold_override) >= 1
    assert original.health_factor(wave_two_valuation_price, scenario.liquidation_threshold_override) < 1
    assert wave_two.health_factor_before == original.health_factor(
        wave_two_valuation_price, scenario.liquidation_threshold_override
    )
