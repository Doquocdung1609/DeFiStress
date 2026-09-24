from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from dataclasses import replace
from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]

from sim.terra.demo_data import load_extended_frame
from sim.terra.early_warning_v2 import build_early_warning, build_early_warning_from_frame
from sim.terra.historical_fit import fit_historical, simulate_historical
from sim.terra.mechanism_validation import validate_native_mint_mechanism
from sim.terra.stress_test import STRESS_PRESETS, StressScenario, run_stress_test


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
    mask = changed["timestamp"] >= pd.Timestamp("2022-05-07T00:00:00Z")
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
    first_native = may["gross_luna_issuance_from_native_swaps"].first_valid_index()
    assert first_native is not None and first_native > 0
    expected_final = float(may.loc[first_native - 1, "luna_supply"]) + parameters.supply_realization * float(
        may.loc[first_native:, "gross_luna_issuance_from_native_swaps"].sum()
    )
    assert math.isclose(float(simulation["luna_supply"].iloc[-1]), expected_final, rel_tol=1e-12)
    assert (simulation[["ust_price", "luna_price"]] > 0).all().all()
    assert (simulation.loc[simulation["luna_supply"].notna(), "luna_supply"] > 0).all()


def test_historical_fit_preserves_missing_vs_event_zero_semantics() -> None:
    fit = fit_historical(candidates=8)
    actual = pd.DataFrame(fit["actual_timeseries"])
    simulated = pd.DataFrame(fit["simulated_timeseries"])
    pre_anchor = actual["timestamp"] < "2022-05-06T00:00:00Z"
    pre_native = actual["timestamp"] < "2022-05-07T00:00:00Z"
    assert actual.loc[pre_anchor, "anchor_withdrawal_flow"].isna().all()
    assert (~actual.loc[pre_anchor, "anchor_withdrawal_available"]).all()
    assert simulated.loc[pre_anchor, "anchor_channel_status"].eq(
        "CHANNEL_INACTIVE_DUE_TO_NO_HISTORICAL_EVIDENCE"
    ).all()
    assert actual.loc[pre_native, "gross_luna_issuance_from_native_swaps"].isna().all()
    assert (~actual.loc[pre_native, "native_issuance_available"]).all()
    assert simulated.loc[pre_native, "luna_supply"].isna().all()

    covered_anchor_zero = actual[actual["anchor_withdrawal_available"] & (actual["anchor_withdrawal_flow"] == 0)]
    covered_native_zero = actual[
        actual["native_issuance_available"] & (actual["gross_luna_issuance_from_native_swaps"] == 0)
    ]
    assert len(covered_anchor_zero) == 9
    assert len(covered_native_zero) == 22
    assert fit["evaluation_windows"]["anchor_flow"]["rows"] == 192
    assert fit["evaluation_windows"]["luna_supply"]["rows"] == 168


def test_early_warning_is_hourly_availability_aware_and_leakage_safe() -> None:
    retrospective = build_early_warning(mode="RETROSPECTIVE")
    cutoff = build_early_warning(mode="CUTOFF_SAFE")
    assert len(retrospective["timeline"]) == len(cutoff["timeline"]) == 1776
    assert retrospective["mode"] != cutoff["mode"]
    assert retrospective["weights"] != cutoff["weights"]
    assert cutoff["leakage_audit"]["status"] == "PASS"
    assert cutoff["leakage_audit"]["checked_timestamps"] == 1776
    perturbation = cutoff["leakage_audit"]["future_perturbation"]
    assert perturbation["status"] == "PASS"
    assert perturbation["cutoffs_tested"] == 5
    assert all(check["max_prior_score_difference"] == 0 for check in perturbation["checks"])
    for row in cutoff["timeline"]:
        assert row["leakage_check"] == "PASS"
        assert row["latest_input_timestamp"] == row["timestamp"]
        assert math.isclose(sum(row["normalized_active_weights"].values()), 1.0, rel_tol=1e-12)
    assert cutoff["data_policy"]["synthetic_wallet_data_used"] is False
    assert "after the event" in cutoff["lead_times"]["ust_below_0_9"]["crisis"]["wording"]
    assert "anchor_deposit_stress" in cutoff["weights"]
    assert "holder_concentration" in cutoff["weights"]
    may7 = next(row for row in cutoff["timeline"] if row["timestamp"] == "2022-05-07T00:00:00Z")
    assert "holder_concentration" in may7["unavailable_features"]
    assert "holder_concentration" not in may7["components"]


def test_early_warning_future_corruption_cannot_change_past_scores_or_features() -> None:
    frame = load_extended_frame()
    cutoff = pd.Timestamp("2022-05-06T12:00:00Z")
    original = build_early_warning_from_frame(frame, mode="CUTOFF_SAFE")
    corrupted = frame.copy()
    future = corrupted["timestamp"] > cutoff
    for offset, name in enumerate(corrupted.select_dtypes(include="number").columns, start=1):
        corrupted.loc[future, name] = float(offset * 9_999_991)
    changed = build_early_warning_from_frame(corrupted, mode="CUTOFF_SAFE")
    original_prefix = [row for row in original["timeline"] if pd.Timestamp(row["timestamp"]) <= cutoff]
    changed_prefix = [row for row in changed["timeline"] if pd.Timestamp(row["timestamp"]) <= cutoff]
    assert original_prefix == changed_prefix


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
    assert severe["summary"]["wording"] == "0 of 4 simulated runs reached the collapse condition."
    assert severe["summary"]["probability_estimate"] is False
    for run in severe["run_summaries"]:
        assert all(math.isfinite(float(run[field])) for field in ("minimum_ust", "minimum_luna", "final_luna_supply"))


def test_stress_uses_observed_initial_state_frozen_fit_and_no_future_observations() -> None:
    result = run_stress_test(StressScenario(horizon_hours=3), runs=2, seed=11)
    initial = result["initial_state"]
    assert initial["timestamp"] == "2022-05-06T23:00:00Z"
    assert math.isclose(initial["ust_price"], 0.999478102440526)
    assert math.isclose(initial["luna_price"], 78.47970310197206)
    assert initial["source"].endswith("terra_state_hourly_20220301_20220513.parquet")
    assert result["analysis_type"] == "CALIBRATED_COUNTERFACTUAL_STRESS_TEST"
    assert result["counterfactual_conversion"]["name"].startswith("COUNTERFACTUAL")
    assert "not a protocol accounting identity" in result["counterfactual_conversion"]["claim_boundary"]
    assert "No future observed" in result["data_policy"]["future_observations"]
    assert result["frozen_parameter_mapping"]["not_reused"]["supply_realization"]


def test_stress_start_timestamp_changes_observed_initial_state() -> None:
    first = run_stress_test(StressScenario(horizon_hours=1), runs=1, start_timestamp="2022-05-06T22:00:00Z")
    second = run_stress_test(StressScenario(horizon_hours=1), runs=1, start_timestamp="2022-05-06T23:00:00Z")
    assert first["initial_state_timestamp"] != second["initial_state_timestamp"]
    assert first["initial_state"]["luna_price"] != second["initial_state"]["luna_price"]
    assert first["frozen_parameter_mapping"] == second["frozen_parameter_mapping"]


def test_stress_one_factor_directions_are_not_sign_inverted() -> None:
    base = StressScenario(horizon_hours=24)
    lower_liquidity = replace(base, liquidity_capacity=0.20)
    higher_selling = replace(base, outside_holder_exit=0.02)
    higher_reserve = replace(base, reserve_intervention=0.40)
    results = {
        "base": run_stress_test(base, runs=4, seed=29),
        "lower_liquidity": run_stress_test(lower_liquidity, runs=4, seed=29),
        "higher_selling": run_stress_test(higher_selling, runs=4, seed=29),
        "higher_reserve": run_stress_test(higher_reserve, runs=4, seed=29),
    }
    def minimum(name: str) -> float:
        return float(results[name]["summary"]["minimum_ust"]["median"])

    assert minimum("lower_liquidity") <= minimum("base")
    assert minimum("higher_selling") <= minimum("base")
    assert minimum("higher_reserve") >= minimum("base")
    assert all(
        result["frozen_parameter_mapping"] == results["base"]["frozen_parameter_mapping"]
        for result in results.values()
    )


def test_stress_presets_have_directional_severity() -> None:
    outputs = {
        name: run_stress_test(replace(scenario, horizon_hours=24), runs=4, seed=17)
        for name, scenario in STRESS_PRESETS.items()
    }
    assert (
        outputs["SEVERE"]["summary"]["minimum_ust"]["median"]
        < outputs["ADVERSE"]["summary"]["minimum_ust"]["median"]
    )
    assert (
        outputs["ADVERSE"]["summary"]["minimum_ust"]["median"]
        < outputs["BASELINE"]["summary"]["minimum_ust"]["median"]
    )
    assert (
        outputs["SEVERE"]["summary"]["final_luna_supply"]["median"]
        >= outputs["ADVERSE"]["summary"]["final_luna_supply"]["median"]
    )


def test_mechanism_check_uses_audited_direct_output() -> None:
    result = validate_native_mint_mechanism()
    assert result["raw_swap_rows"] == 277_342
    assert result["gross_mint_identity"] == "swap_amount + fee_amount"
    assert result["direct_event_output_gross_mint"]["hourly_correlation"] > 0.999
    assert result["direct_event_output_gross_mint"]["final_cumulative_relative_error"] < 0.02
    assert result["validation_window"] == {
        "start": "2022-05-07T00:00:00Z",
        "end": "2022-05-13T23:00:00Z",
        "aligned_hours": 168,
        "supply_delta_definition": (
            "hourly observed LUNA supply first difference within the aligned window; "
            "the first aligned hour has zero within-window delta"
        ),
        "event_aggregation": "hourly",
    }


def test_demo_manifest_has_real_commits_and_matching_artifact_hashes() -> None:
    output = Path("data/processed/terra_demo")
    manifest = json.loads((output / "reproducibility_manifest.json").read_text(encoding="utf-8"))
    for field in ("source_code_commit", "artifact_bundle_commit"):
        value = manifest[field]
        assert re.fullmatch(r"[0-9a-f]{40}", value)
        subprocess.run(["git", "cat-file", "-e", f"{value}^{{commit}}"], check=True)
    for name, expected in manifest["outputs"].items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == expected
