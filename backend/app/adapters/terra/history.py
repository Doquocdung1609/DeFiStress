from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class HistoricalDataAvailability:
    source: str
    status: str
    reason: str
    expected_schema: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class TerraHistoricalAdapter(Protocol):
    """Boundary for archival Terra Classic/indexed providers; no source is silently substituted."""

    source_name: str

    def fetch(self, start: datetime, end: datetime) -> list[dict[str, Any]]: ...


def unavailable(source: str, reason: str) -> HistoricalDataAvailability:
    return HistoricalDataAvailability(
        source=source,
        status="UNAVAILABLE",
        reason=reason,
        expected_schema="docs/data/terra_hourly_state.csv",
    )
