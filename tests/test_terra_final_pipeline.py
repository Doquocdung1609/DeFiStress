from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from sim.terra.conditional import (
    QUARANTINED_VARIABLES,
    ArbitrageThroughput,
    ConditionalABM,
    TerraProtocolMechanism,
    calibrate_conditional,
)
from sim.terra.datasets import ResearchDataset
from sim.terra.research_pipeline import (
    DEFAULT_DATASET,
    DEFAULT_NATIVE_SWAPS,
    DEFAULT_STRICT_V2,
    data_quality_report,
    load_historical_dataset,
    monte_carlo,
    protocol_mechanism_validation,
    run_final_pipeline,
)


@pytest.fixture(scope="module")
def historical_dataset() -> ResearchDataset:
    return load_historical_dataset()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_conditional_window_is_exact_and_sealed(historical_dataset: ResearchDataset) -> None:
    calibration = calibrate_conditional(historical_dataset)
    assert calibration.trigger_timestamp.isoformat() == "2022-05-07T22:00:00+00:00"
    assert calibration.calibration_end.isoformat() == "2022-05-08T09:00:00+00:00"
    assert calibration.evaluation_start.isoformat() == "2022-05-08T10:00:00+00:00"
    assert calibration.calibration_rows == 12
    assert calibration.evaluation_rows == 134

    changed = tuple(
        replace(row, ust_price=row.ust_price / 2, luna_price=row.luna_price / 3)
        if row.timestamp >= calibration.evaluation_start
        else row
        for row in historical_dataset.observations
    )
    mutated = ResearchDataset(historical_dataset.manifest, changed)
    recalibrated = calibrate_conditional(mutated)
    assert recalibrated.parameters == calibration.parameters
    assert recalibrated.initial_state == calibration.initial_state


def test_simulation_uses_only_initial_state_and_timestamps(historical_dataset: ResearchDataset) -> None:
    calibration = calibrate_conditional(historical_dataset)
    timestamps = tuple(
        row.timestamp for row in historical_dataset.observations if row.timestamp >= calibration.evaluation_start
    )
    model = ConditionalABM()
    left = model.run(calibration, timestamps, seed=77)
    right = model.run(calibration, timestamps, seed=77)
    assert left.states == right.states
    different = model.run(calibration, timestamps, seed=78)
    assert left.states != different.states
    assert left.label == "CONDITIONAL_HISTORICAL_REPLAY"
    assert left.not_prediction is True
    assert calibration.dataset_status == "QUALITY_WARNING"
    assert left.diagnostics["quarantined_variables_consumed"] == []
    assert not set(QUARANTINED_VARIABLES) & set(left.parameters.to_dict())


def test_net_sell_and_protocol_conservation(historical_dataset: ResearchDataset) -> None:
    calibration = calibrate_conditional(historical_dataset)
    parameters = calibration.parameters
    absorption = ArbitrageThroughput().absorb(10_000_000.0, 0.90, parameters, True, 1.0)
    assert 0.0 <= absorption <= min(10_000_000.0, parameters.arbitrage_hourly_capacity)
    repeated = ArbitrageThroughput().absorb(10_000_000.0, 0.90, parameters, True, 1.0)
    assert repeated == absorption  # hourly throughput resets; it is not a depleting wallet balance

    protocol = TerraProtocolMechanism()
    new_ust, new_luna, minted = protocol.redeem(100.0, 10.0, 25.0, 5.0, 0.8)
    assert new_ust == 75.0
    assert minted == 4.0
    assert new_luna == 14.0


def test_bounds_and_nonnegative_state(historical_dataset: ResearchDataset) -> None:
    calibration = calibrate_conditional(historical_dataset)
    timestamps = tuple(
        row.timestamp for row in historical_dataset.observations if row.timestamp >= calibration.evaluation_start
    )
    run = ConditionalABM().run(calibration, timestamps, overrides={"execution_depth_multiplier": 0.01})
    assert all(row.ust_price >= run.parameters.price_floor_ust for row in run.states)
    assert all(row.luna_price >= run.parameters.price_floor_luna for row in run.states)
    assert all(row.ust_supply >= 0 and row.luna_supply >= 0 for row in run.states)
    assert all(
        row.net_ust_sell == max(0.0, row.gross_ust_sell - row.reserve_support - row.arbitrage_absorption)
        for row in run.states
    )


def test_native_redemption_aggregation_and_duplicate_quarantine(historical_dataset: ResearchDataset) -> None:
    calibration = calibrate_conditional(historical_dataset)
    validation = protocol_mechanism_validation(historical_dataset, calibration)
    source = validation["source_validation"]
    assert source["status"] == "PROVENANCE_SUPPORTED_WITH_EXTRACT_LIMITATION"
    assert source["hourly_aggregation_mismatches"] == 0
    assert source["raw_rows"] == 277_342
    quality = data_quality_report(historical_dataset, validation)
    assert all(quality["duplicate_or_suspect_field_checks"].values())
    assert quality["source_availability"]["ethereum_archival_rpc_curve"]["status"] == "UNAVAILABLE"


def test_monte_carlo_is_seeded_and_reports_quantiles(historical_dataset: ResearchDataset) -> None:
    calibration = calibrate_conditional(historical_dataset)
    timestamps = tuple(
        row.timestamp for row in historical_dataset.observations if row.timestamp >= calibration.evaluation_start
    )[:4]
    left = monte_carlo(ConditionalABM(), calibration, timestamps, runs=3)
    right = monte_carlo(ConditionalABM(), calibration, timestamps, runs=3)
    assert left == right
    assert set(left["time_series_quantiles"]) == {
        "ust_price",
        "luna_price",
        "luna_supply",
        "anchor_withdrawal_flow",
    }
    assert set(left["time_series_quantiles"]["ust_price"][0]["quantiles"]) == {
        "p05",
        "p25",
        "p50",
        "p75",
        "p95",
    }


def test_pipeline_writes_complete_bundle_without_touching_frozen_v2(tmp_path: Path) -> None:
    before = _sha256(DEFAULT_STRICT_V2)
    v1_path = Path("data/processed/terra_model_benchmark_v1.json")
    v1_before = _sha256(v1_path)
    output = tmp_path / "terra_final"
    result = run_final_pipeline(
        DEFAULT_DATASET,
        DEFAULT_STRICT_V2,
        output,
        DEFAULT_NATIVE_SWAPS,
        monte_carlo_runs=3,
    )
    expected = {
        "strict_oos_v2.json",
        "conditional_abm_final.json",
        "conditional_benchmark.json",
        "protocol_mechanism_validation.json",
        "monte_carlo.json",
        "ablation.json",
        "sensitivity.json",
        "rolling_origin.json",
        "data_quality.json",
        "model_diagnostics.json",
        "final_metrics.json",
        "final_report.md",
        "reproducibility_manifest.json",
    }
    assert set(result["artifacts"]) == expected
    assert {path.name for path in output.iterdir()} == expected
    assert _sha256(DEFAULT_STRICT_V2) == before
    assert _sha256(v1_path) == v1_before
    assert _sha256(output / "strict_oos_v2.json") == before
    assert result["diagnostics"]["all_checks_pass"] is True


def test_pipeline_refuses_existing_output(tmp_path: Path) -> None:
    output = tmp_path / "terra_final"
    output.mkdir()
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        run_final_pipeline(output_dir=output, monte_carlo_runs=1)
