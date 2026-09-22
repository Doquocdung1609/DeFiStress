from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any

from sim.terra.datasets import GroundTruthRepository, ResearchDataset
from sim.terra.leakage import enforce_cutoff
from sim.terra.models import TERRA_MODEL_VERSION, build_model, early_warning_for
from sim.terra.schemas import ExperimentMode, ModelInputState, TerraObservation, parse_utc
from sim.terra.validation import validate_model_run


@dataclass(frozen=True, slots=True)
class HistoricalReplayExperiment:
    case_study: str = "TERRA_2022"
    dataset_version: str = "terra_fixture_v1"
    calibration_start: str = "2022-05-01T00:00:00Z"
    calibration_end: str = "2022-05-06T23:59:59Z"
    cutoff_timestamp: str = "2022-05-06T23:59:59Z"
    evaluation_start: str = "2022-05-07T00:00:00Z"
    evaluation_end: str = "2022-05-13T23:59:59Z"
    model_name: str = "ABM"
    model_version: str = TERRA_MODEL_VERSION
    parameters: dict[str, Any] = field(default_factory=dict)
    seed: int = 20220506
    ground_truth_version: str = "terra_fixture_v1"
    mode: ExperimentMode = ExperimentMode.OUT_OF_SAMPLE_REPLAY

    def __post_init__(self) -> None:
        cutoff = parse_utc(self.cutoff_timestamp)
        calibration_end = parse_utc(self.calibration_end)
        evaluation_start = parse_utc(self.evaluation_start)
        evaluation_end = parse_utc(self.evaluation_end)
        if calibration_end > cutoff:
            raise ValueError("calibration_end cannot exceed cutoff_timestamp")
        if self.mode == ExperimentMode.OUT_OF_SAMPLE_REPLAY and evaluation_start <= cutoff:
            raise ValueError("out-of-sample evaluation must begin after cutoff")
        if evaluation_end < evaluation_start:
            raise ValueError("evaluation_end cannot precede evaluation_start")

    def metadata(self, data_source_manifest: dict[str, Any], leakage_status: dict[str, Any]) -> dict[str, Any]:
        payload = asdict(self)
        payload["mode"] = self.mode.value
        payload["git_commit"] = _git_commit()
        payload["random_seed"] = payload.pop("seed")
        payload["scenario_parameters"] = payload.pop("parameters")
        payload["data_source_manifest"] = data_source_manifest
        payload["leakage_check_status"] = leakage_status
        return payload


def run_historical_replay(dataset: ResearchDataset, experiment: HistoricalReplayExperiment) -> dict[str, Any]:
    if dataset.manifest.dataset_version != experiment.dataset_version:
        raise ValueError("dataset version does not match experiment")
    calibration = dataset.calibration_view(experiment.cutoff_timestamp)
    calibration_start = parse_utc(experiment.calibration_start)
    calibration_end = parse_utc(experiment.calibration_end)
    filtered = tuple(row for row in calibration.observations if calibration_start <= row.timestamp <= calibration_end)
    calibration = type(calibration)(filtered, calibration.cutoff_timestamp)
    leakage = enforce_cutoff(calibration, experiment.cutoff_timestamp, experiment.mode)
    evaluation = dataset.evaluation_view(experiment.evaluation_start, experiment.evaluation_end)
    if not evaluation.timestamps:
        raise ValueError("evaluation window has no observations")
    initial_row = calibration.observations[-1]
    model_input = ModelInputState.from_observation(initial_row, _realized_volatility(calibration.observations))

    # Model execution sees only ModelInputState, evaluation timestamps, frozen parameters, and seed.
    model = build_model(experiment.model_name, calibration)
    model_run = model.run(model_input, evaluation.timestamps, dict(experiment.parameters), experiment.seed)

    # Ground truth is loaded only after model execution and is passed only to the validator.
    ground_truth = GroundTruthRepository(dataset).load(experiment.evaluation_start, experiment.evaluation_end)
    validation = validate_model_run(model_run, ground_truth)
    warning = (
        "IN-SAMPLE — NOT VALID EVIDENCE OF PREDICTIVE PERFORMANCE"
        if experiment.mode == ExperimentMode.IN_SAMPLE_REPLAY
        else None
    )
    return {
        "metadata": experiment.metadata(dataset.manifest.source_manifest, leakage.to_dict()),
        "dataset": dataset.manifest.to_dict(),
        "model": {
            "name": model_run.model_name,
            "version": model_run.model_version,
            "status": model_run.model_status,
            "parameters": model_run.parameters,
            "diagnostics": model_run.diagnostics,
        },
        "simulated_timeseries": [row.to_dict() for row in model_run.states],
        "ground_truth_timeseries": [row.to_dict() for row in ground_truth.observations],
        "validation_metrics": validation.metrics,
        "validation_warnings": list(validation.warnings),
        "agent_events": [event.to_dict() for event in model_run.events],
        "early_warning": early_warning_for(calibration),
        "evidence_warning": warning,
    }


def _realized_volatility(observations: tuple[TerraObservation, ...]) -> Decimal:
    if len(observations) < 2:
        return Decimal("0")
    returns = [
        abs(observations[index].ust_price / observations[index - 1].ust_price - Decimal("1"))
        for index in range(1, len(observations))
        if observations[index - 1].ust_price > 0
    ]
    return sum(returns, Decimal("0")) / Decimal(max(1, len(returns)))


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        return "UNCOMMITTED"
