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


def availability(source: str, status: str, reason: str) -> HistoricalDataAvailability:
    return HistoricalDataAvailability(
        source=source,
        status=status,
        reason=reason,
        expected_schema="docs/data/terra_hourly_state.csv",
    )


def unavailable(source: str, reason: str) -> HistoricalDataAvailability:
    return availability(source, "UNAVAILABLE", reason)


def configured(source: str, reason: str) -> HistoricalDataAvailability:
    """A provider URL/RPC is configured, but no historical evidence has been ingested yet."""

    return availability(source, "CONFIGURED", reason)


def historical(source: str, reason: str) -> HistoricalDataAvailability:
    """Verified historical evidence is present in an imported/versioned dataset."""

    return availability(source, "REAL_HISTORICAL", reason)


def partial(source: str, reason: str) -> HistoricalDataAvailability:
    return availability(source, "PARTIAL", reason)
