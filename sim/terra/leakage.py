from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sim.terra.datasets import CalibrationDatasetView
from sim.terra.schemas import ExperimentMode, parse_utc


@dataclass(frozen=True, slots=True)
class LeakageCheck:
    status: str
    checked_rows: int
    latest_calibration_timestamp: datetime
    cutoff_timestamp: datetime

    def to_dict(self) -> dict[str, str | int]:
        return {
            "status": self.status,
            "checked_rows": self.checked_rows,
            "latest_calibration_timestamp": self.latest_calibration_timestamp.isoformat().replace("+00:00", "Z"),
            "cutoff_timestamp": self.cutoff_timestamp.isoformat().replace("+00:00", "Z"),
        }


def enforce_cutoff(
    calibration: CalibrationDatasetView, cutoff_timestamp: datetime | str, mode: ExperimentMode
) -> LeakageCheck:
    cutoff = parse_utc(cutoff_timestamp)
    latest = max(row.timestamp for row in calibration.observations)
    if mode in {ExperimentMode.OUT_OF_SAMPLE_REPLAY, ExperimentMode.COUNTERFACTUAL_STRESS} and latest > cutoff:
        raise ValueError("LEAKAGE_BLOCKED: post-cutoff observation reached model calibration")
    return LeakageCheck("PASS", len(calibration.observations), latest, cutoff)
