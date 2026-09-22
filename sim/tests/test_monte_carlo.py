from dataclasses import replace

from sim import Scenario
from sim.fixtures import FIXTURE_PRICE, fixture_dex, fixture_positions
from sim.monte_carlo import run_monte_carlo


def test_monte_carlo_seed_reproducibility() -> None:
    scenario = replace(Scenario(), monte_carlo_runs=12)
    first = run_monte_carlo(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)
    second = run_monte_carlo(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario)
    assert first.to_dict() == second.to_dict()
    assert 0 <= first.summary["probability_of_cascade"] <= 1
