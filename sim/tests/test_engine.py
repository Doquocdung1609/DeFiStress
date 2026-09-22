import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from sim import Scenario, fixture_snapshot, run_simulation
from sim.engine.threshold import find_cascade_threshold
from sim.fixtures import FIXTURE_PRICE, fixture_dex, fixture_positions


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
