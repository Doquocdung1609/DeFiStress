from __future__ import annotations

import json
from dataclasses import replace

import pytest

from scripts.research.run_deep_cascade_study import (
    _checkpoint_payload,
    _run_mc_stage,
    monte_carlo_draws,
    summarize_paths,
    validate_checkpoint_payload,
)
from sim.presets import scenario_presets


def test_predeclared_monte_carlo_draws_are_deterministic_and_bounded() -> None:
    base = replace(scenario_presets()["Severe"], max_waves=100, horizon_steps=120)
    first = monte_carlo_draws(base, 20_260_914, 10)
    second = monte_carlo_draws(base, 20_260_914, 10)
    assert first == second
    assert all(-50 <= scenario.shock_pct <= 0 for scenario in first)
    assert all(0 <= scenario.liquidity_haircut_pct <= 95 for scenario in first)
    assert all(scenario.max_waves == 100 and scenario.horizon_steps == 120 for scenario in first)


def test_monte_carlo_hard_cap_is_enforced() -> None:
    with pytest.raises(ValueError, match="between 1 and 10000"):
        monte_carlo_draws(scenario_presets()["Severe"], 1, 10_001)


def test_summary_reports_observed_depth_and_strict_invariants() -> None:
    rows = [
        {
            "cascade_depth": depth,
            "bad_debt": 10.0,
            "total_liquidated_debt": 20.0,
            "finite_metrics": True,
            "no_duplicate_borrower": True,
            "later_wave_new_eligibility": True,
            "cap_hit": False,
        }
        for depth in (1, 2, 2, 3)
    ]
    summary = summarize_paths(rows)
    assert summary["max_observed_cascade_depth"] == 3
    assert summary["cascade_frequencies"]["2"]["successes"] == 3
    assert summary["cascade_frequencies"]["5"]["successes"] == 0
    assert summary["invariants"]["no_duplicate_borrower_all_paths"] is True
    assert "neither realized financial loss nor market Expected Shortfall" in summary["loss_definition"]
    assert "composite_tail_mean_95" in summary["loss_quantiles"]


def _checkpoint_row() -> dict[str, object]:
    return {
        "path_index": 0,
        "path_seed": 20_260_914,
        "cascade_depth": 1,
        "bad_debt": 10.0,
        "total_liquidated_debt": 20.0,
        "finite_metrics": True,
        "no_duplicate_borrower": True,
        "later_wave_new_eligibility": True,
        "cap_hit": False,
    }


def test_checkpoint_validation_rejects_tampering_and_accounts_for_reuse(tmp_path) -> None:
    base = replace(scenario_presets()["Severe"], max_waves=100, horizon_steps=120)
    payload = _checkpoint_payload(
        status="PASS",
        label="Severe",
        seed=20_260_914,
        target=1,
        scenario=base,
        rows=[_checkpoint_row()],
        paths=[],
        reused_checkpoint_count=0,
        executed_this_invocation=1,
        invocation_runtime_seconds=12.5,
        historical_execution_duration_seconds=12.5,
    )
    validation = validate_checkpoint_payload(
        payload,
        label="Severe",
        seed=20_260_914,
        checkpoint_target=1,
        scenario=base,
    )
    assert validation["validated_path_count"] == 1
    tampered = dict(payload, seed=7)
    with pytest.raises(ValueError, match="seed"):
        validate_checkpoint_payload(
            tampered,
            label="Severe",
            seed=20_260_914,
            checkpoint_target=1,
            scenario=base,
        )
    checkpoint = tmp_path / "checkpoint.json"
    checkpoint.write_text(json.dumps(payload), encoding="utf-8")
    summary, paths = _run_mc_stage(
        label="Severe",
        base=base,
        seed=20_260_914,
        target=1,
        checkpoint=checkpoint,
        prefix_checkpoint=None,
        workers=1,
    )
    assert paths == []
    assert summary["total_validated_path_count"] == 1
    assert summary["reused_checkpoint_count"] == 1
    assert summary["executed_in_current_invocation"] == 0
    assert summary["historical_execution_duration_seconds"] == 12.5
