from __future__ import annotations

from dataclasses import dataclass

from sim.terra.schemas import TerraObservation


@dataclass(frozen=True, slots=True)
class GroundTruthState:
    """Evaluation-only observations. Simulation model modules must not import this type."""

    observations: tuple[TerraObservation, ...]
    version: str

    def __post_init__(self) -> None:
        if not self.observations:
            raise ValueError("ground truth cannot be empty")
