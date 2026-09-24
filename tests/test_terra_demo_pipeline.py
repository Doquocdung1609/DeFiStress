from __future__ import annotations

import math
from dataclasses import replace

import pandas as pd  # type: ignore[import-untyped]

from sim.terra.demo_data import load_extended_frame
from sim.terra.early_warning_v2 import build_early_warning
from sim.terra.historical_fit import fit_historical, simulate_historical
from sim.terra.mechanism_validation import validate_native_mint_mechanism
from sim.terra.stress_test import StressScenario, run_stress_test


def test_historical_fit_is_reproducible_and_does_not_copy_future_state() -> None:
    left = fit_historical(candidates=12)
    right = fit_historical(candidates=12)
    assert left["parameters"] == right["parameters"]
    assert left["objective"] == right["objective"]
    frame = load_extended_frame()
    parameters = left["parameters"]
    from sim.terra.historical_fit import FitParameters

    baseline = simulate_historical(frame, FitParameters(**parameters))
    changed = frame.copy()
    mask = changed["timestamp"] > pd.Timestamp("2022-05-01T00:00:00Z")
    changed.loc[mask, "ust_price"] = 0.123
    changed.loc[mask, "luna_price"] = 999.0
    changed.loc[mask, "luna_supply"] = 42.0
    rerun = simulate_historical(changed, FitParameters(**parameters))
    pd.testing.assert_frame_equal(baseline, rerun)
    assert all(left["checks"].values())


def test_historical_fit_uses_direct_gross_mint_and_keeps_valid_states() -> None:
    fit = fit_historical(candidates=8)
    frame = load_extended_frame()
    from sim.terra.historical_fit import FitParameters

    parameters = FitParameters(**fit["parameters"])
    simulation = simulate_historical(frame, parameters)
    may = frame.loc[frame["timestamp"] >= pd.Timestamp("2022-05-01T00:00:00Z")].reset_index(drop=True)
    expected_final = float(may["luna_supply"].iloc[0]) + parameters.supply_realization * float(
        may["gross_luna_issuance_from_native_swaps"].fillna(0).sum()
    )
    assert math.isclose(float(simulation["luna_supply"].iloc[-1]), expected_final, rel_tol=1e-12)
    assert (simulation[["ust_price", "luna_price", "luna_supply"]] > 0).all().all()


def test_early_warning_is_hourly_availability_aware_and_leakage_safe() -> None:
    retrospective = build_early_warning(mode="RETROSPECTIVE")
    cutoff = build_early_warning(mode="CUTOFF_SAFE")
    assert len(retrospective["timeline"]) == len(cutoff["timeline"]) == 1776
    assert retrospective["mode"] != cutoff["mode"]
    assert retrospective["weights"] != cutoff["weights"]
    assert cutoff["leakage_audit"] == {
        "status": "PASS",
        "checked_timestamps": 1776,
        "rule": "latest_input_timestamp <= score_timestamp at every row",
        "violations": 0,
    }
    for row in cutoff["timeline"]:
        assert row["leakage_check"] == "PASS"
        assert row["latest_input_timestamp"] == row["timestamp"]
        assert math.isclose(sum(row["normalized_active_weights"].values()), 1.0, rel_tol=1e-12)
    assert cutoff["data_policy"]["synthetic_wallet_data_used"] is False
    assert "after the event" in cutoff["lead_times"]["ust_below_0_9"]["crisis"]["wording"]


def test_stress_reproducibility_scenario_effect_shape_and_wording() -> None:
    baseline = run_stress_test(StressScenario(horizon_hours=24), runs=4, seed=7)
    repeated = run_stress_test(StressScenario(horizon_hours=24), runs=4, seed=7)
    assert baseline == repeated
    severe_scenario = replace(
        StressScenario(horizon_hours=24),
        withdrawal_pressure=4.0,
        liquidity_capacity=0.1,
        arbitrage_capacity=0.05,
        confidence_sensitivity=3.0,
        outside_holder_exit=0.05,
        initial_shock=0.08,
    )
    severe = run_stress_test(severe_scenario, runs=4, seed=7)
    assert severe["summary"]["minimum_ust"]["median"] < baseline["summary"]["minimum_ust"]["median"]
    assert len(severe["fan_chart"]) == 24
    assert len(severe["run_summaries"]) == 4
    assert "not a probability estimate" in severe["summary"]["wording"]
    for run in severe["run_summaries"]:
        assert all(math.isfinite(float(run[field])) for field in ("minimum_ust", "minimum_luna", "final_luna_supply"))


def test_mechanism_check_uses_audited_direct_output() -> None:
    result = validate_native_mint_mechanism()
    assert result["raw_swap_rows"] == 277_342
    assert result["gross_mint_identity"] == "swap_amount + fee_amount"
    assert result["direct_event_output_gross_mint"]["hourly_correlation"] > 0.999
    assert result["direct_event_output_gross_mint"]["final_cumulative_relative_error"] < 0.02
