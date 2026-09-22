from __future__ import annotations

from decimal import Decimal

from sim.terra.agents import ArbitrageurAgent, TerraProtocolAgent, depositor_exit_probability
from sim.terra.experiments import run_ablation, run_benchmark, run_counterfactual
from sim.terra.fixtures import terra_fixture_dataset
from sim.terra.monte_carlo import run_terra_monte_carlo
from sim.terra.replay import HistoricalReplayExperiment, run_historical_replay
from sim.terra.validation import mae, rmse, timing_error_hours

D = Decimal


def test_terra_mint_burn_accounting_and_nonnegative_supply() -> None:
    protocol = TerraProtocolAgent(D("1000"), D("100"), D("0.02"))
    minted = protocol.redeem(D("50"), D("5"))
    assert minted == D("9.8")
    assert protocol.ust_supply == D("950")
    assert protocol.luna_supply == D("109.8")
    protocol.redeem(D("5000"), D("1"))
    assert protocol.ust_supply == 0
    assert protocol.luna_supply >= 0


def test_arbitrage_profitability_and_capital_gate() -> None:
    agent = ArbitrageurAgent(D("100"), D("0.10"))
    decision = agent.evaluate(D("0.90"), D("1000"), D("10"))
    assert decision.execute
    assert decision.amount <= D("100") / D("0.90")
    assert decision.expected_profit > 0


def test_depositor_behavior_is_decomposable_and_bounded() -> None:
    probability, explanation = depositor_exit_probability(
        D("0.20"), D("0.30"), D("0.10"), D("0.40"), D("1.2"), D("0.03")
    )
    assert D("0") <= probability <= D("0.98")
    assert {
        "ust_depeg",
        "large_holder_activity",
        "backing_deterioration",
        "liquidity_stress",
        "cohort_baseline",
    } == set(explanation)


def test_replay_is_deterministic_and_events_are_monotonic() -> None:
    dataset = terra_fixture_dataset()
    experiment = HistoricalReplayExperiment(seed=77, model_name="ABM")
    first = run_historical_replay(dataset, experiment)
    second = run_historical_replay(dataset, experiment)
    assert first["simulated_timeseries"] == second["simulated_timeseries"]
    assert first["agent_events"] == second["agent_events"]
    timestamps = [row["timestamp"] for row in first["agent_events"]]
    assert timestamps == sorted(timestamps)
    assert all(row["ust_supply"] >= 0 and row["luna_supply"] >= 0 for row in first["simulated_timeseries"])
    assert all(
        row["anchor_withdrawal_flow"] <= row["anchor_total_deposits"] + row["anchor_withdrawal_flow"]
        for row in first["simulated_timeseries"]
    )


def test_validation_metrics_and_timing_error() -> None:
    assert mae([1.0, 2.0], [1.0, 4.0]) == 1.0
    assert rmse([1.0, 2.0], [1.0, 4.0]) == 2**0.5
    dataset = terra_fixture_dataset()
    times = [row.timestamp for row in dataset.observations[:3]]
    assert timing_error_hours(times, [1.0, 0.9, 0.8], times, [1.0, 1.0, 0.8], 0.95) == 1


def test_all_four_model_families_and_ablation_run() -> None:
    dataset = terra_fixture_dataset()
    experiment = HistoricalReplayExperiment()
    benchmark = run_benchmark(dataset, experiment)
    assert [row["model"] for row in benchmark["benchmark_results"]] == [
        "THRESHOLD",
        "HAZARD",
        "SYSTEM_DYNAMICS",
        "ABM",
    ]
    ablation = run_ablation(dataset, experiment)
    assert len(ablation["ablation_results"]) == 6
    assert {row["variant"] for row in ablation["ablation_results"]} >= {"ABM_FULL", "NO_ARBITRAGE"}


def test_counterfactual_is_visibly_labelled() -> None:
    result = run_counterfactual(terra_fixture_dataset(), HistoricalReplayExperiment(), {"reaction_delay_hours": 6})
    assert result["label"].startswith("COUNTERFACTUAL")
    assert result["counterfactual_replay"]["metadata"]["mode"] == "COUNTERFACTUAL_STRESS"


def test_terra_monte_carlo_is_seeded_and_model_implied() -> None:
    dataset = terra_fixture_dataset()
    experiment = HistoricalReplayExperiment(seed=42)
    first = run_terra_monte_carlo(dataset, experiment, runs=3)
    second = run_terra_monte_carlo(dataset, experiment, runs=3)
    assert first == second
    assert first["label"].startswith("MODEL-IMPLIED")
    assert 0 <= first["probability_of_severe_depeg"] <= 1
