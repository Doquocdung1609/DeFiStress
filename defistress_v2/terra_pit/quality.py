"""Dataset quality summaries that preserve all typed missingness states."""

from __future__ import annotations

from collections import Counter

from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.terra_pit.contracts import Measurement, QualityReport, ValueStatus


def dataset_quality_report(measurements: tuple[Measurement, ...]) -> QualityReport:
    if type(measurements) is not tuple or any(type(item) is not Measurement for item in measurements):
        raise TypeContractError("measurements must be an immutable typed tuple")
    counts = Counter(item.status for item in measurements)
    return QualityReport(
        total=len(measurements),
        available=counts[ValueStatus.AVAILABLE],
        missing=counts[ValueStatus.MISSING],
        unsupported=counts[ValueStatus.UNSUPPORTED],
        quarantined=counts[ValueStatus.QUARANTINED],
        historical_pit_status="BLOCKED_NOT_CLEARED_FOR_FORECAST",
        historical_predictive_fields=0,
        backtest_executed=False,
    )
