from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from sim.terra.ground_truth import GroundTruthState
from sim.terra.schemas import DataStatus, TerraObservation, parse_utc


@dataclass(frozen=True, slots=True)
class CalibrationDatasetView:
    observations: tuple[TerraObservation, ...]
    cutoff_timestamp: datetime

    def __post_init__(self) -> None:
        if not self.observations:
            raise ValueError("calibration dataset is empty")
        if any(row.timestamp > self.cutoff_timestamp for row in self.observations):
            raise ValueError("LEAKAGE_BLOCKED: calibration view contains post-cutoff data")


@dataclass(frozen=True, slots=True)
class EvaluationDatasetView:
    timestamps: tuple[datetime, ...]
    evaluation_start: datetime
    evaluation_end: datetime

    def __post_init__(self) -> None:
        if any(not self.evaluation_start <= item <= self.evaluation_end for item in self.timestamps):
            raise ValueError("evaluation timestamp outside configured window")


@dataclass(frozen=True, slots=True)
class DatasetManifest:
    dataset_version: str
    status: DataStatus
    row_count: int
    start_timestamp: datetime
    end_timestamp: datetime
    dataset_hash: str
    source_manifest: dict[str, Any]
    quality_report: dict[str, Any]
    transformation_version: str
    git_commit: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_version": self.dataset_version,
            "status": self.status.value,
            "row_count": self.row_count,
            "start_timestamp": self.start_timestamp.isoformat().replace("+00:00", "Z"),
            "end_timestamp": self.end_timestamp.isoformat().replace("+00:00", "Z"),
            "dataset_hash": self.dataset_hash,
            "source_manifest": self.source_manifest,
            "quality_report": self.quality_report,
            "transformation_version": self.transformation_version,
            "git_commit": self.git_commit,
        }


@dataclass(frozen=True, slots=True)
class ResearchDataset:
    manifest: DatasetManifest
    observations: tuple[TerraObservation, ...]

    def __post_init__(self) -> None:
        if not self.observations:
            raise ValueError("dataset cannot be empty")
        timestamps = [item.timestamp for item in self.observations]
        if timestamps != sorted(timestamps):
            raise ValueError("timestamps must be monotonic")
        if len(timestamps) != len(set(timestamps)):
            raise ValueError("duplicate timestamps are not allowed")
        if self.manifest.row_count != len(self.observations):
            raise ValueError("manifest row_count does not match observations")

    def calibration_view(self, cutoff_timestamp: datetime | str) -> CalibrationDatasetView:
        cutoff = parse_utc(cutoff_timestamp)
        return CalibrationDatasetView(tuple(row for row in self.observations if row.timestamp <= cutoff), cutoff)

    def evaluation_view(
        self, evaluation_start: datetime | str, evaluation_end: datetime | str
    ) -> EvaluationDatasetView:
        start = parse_utc(evaluation_start)
        end = parse_utc(evaluation_end)
        return EvaluationDatasetView(
            tuple(row.timestamp for row in self.observations if start <= row.timestamp <= end), start, end
        )


class GroundTruthRepository:
    """The only component allowed to expose evaluation values to validators."""

    def __init__(self, dataset: ResearchDataset):
        self._dataset = dataset

    def load(self, evaluation_start: datetime | str, evaluation_end: datetime | str) -> GroundTruthState:
        start = parse_utc(evaluation_start)
        end = parse_utc(evaluation_end)
        rows = tuple(row for row in self._dataset.observations if start <= row.timestamp <= end)
        return GroundTruthState(rows, self._dataset.manifest.dataset_version)


def dataset_hash(observations: tuple[TerraObservation, ...]) -> str:
    encoded = json.dumps([row.to_dict() for row in observations], sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def quality_report(observations: tuple[TerraObservation, ...]) -> dict[str, Any]:
    timestamps = [row.timestamp for row in observations]
    gaps: list[str] = []
    for previous, current in zip(timestamps, timestamps[1:], strict=False):
        if current - previous > timedelta(hours=1, minutes=1):
            gaps.append(f"{previous.isoformat()} -> {current.isoformat()}")
    warning_rows = sum(1 for row in observations if row.quality_flag not in {"OK", "FIXTURE"})
    return {
        "missing_intervals": gaps,
        "duplicate_timestamps": len(timestamps) - len(set(timestamps)),
        "quality_warning_rows": warning_rows,
        "monotonic": timestamps == sorted(timestamps),
        "negative_supply_rows": sum(1 for row in observations if row.ust_supply < 0 or row.luna_supply < 0),
    }
