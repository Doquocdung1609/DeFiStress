from __future__ import annotations

from dataclasses import replace

import pytest

from scripts.research.run_deep_cascade_study import monte_carlo_draws, summarize_paths
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
    assert "not realized financial loss" in summary["loss_definition"]
