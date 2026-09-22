from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from backend.app.services.terra_datasets import import_research_dataset
from sim.terra.datasets import CalibrationDatasetView, dataset_hash
from sim.terra.fixtures import terra_fixture_dataset
from sim.terra.leakage import enforce_cutoff
from sim.terra.models import AgentBasedModel
from sim.terra.schemas import DataStatus, ExperimentMode, parse_utc


def test_data_timestamp_parsing_requires_timezone() -> None:
    assert parse_utc("2022-05-06T23:59:59Z").tzinfo == UTC
    with pytest.raises(ValueError, match="UTC offset"):
        parse_utc("2022-05-06T23:59:59")


def test_dataset_manifest_hash_is_stable_and_fixture_is_explicit() -> None:
    dataset = terra_fixture_dataset()
    assert dataset.manifest.dataset_hash == dataset_hash(dataset.observations)
    assert dataset.manifest.status.value == "FIXTURE"
    assert all(row.quality_flag == "FIXTURE" for row in dataset.observations)


def test_cutoff_enforcement_rejects_future_observation() -> None:
    dataset = terra_fixture_dataset()
    cutoff = parse_utc("2022-05-06T23:59:59Z")
    future = next(row for row in dataset.observations if row.timestamp > cutoff)
    with pytest.raises(ValueError, match="LEAKAGE_BLOCKED"):
        CalibrationDatasetView((future,), cutoff)


def test_model_cannot_access_post_cutoff_ground_truth() -> None:
    dataset = terra_fixture_dataset()
    cutoff = parse_utc("2022-05-06T23:59:59Z")
    calibration = dataset.calibration_view(cutoff)
    check = enforce_cutoff(calibration, cutoff, ExperimentMode.OUT_OF_SAMPLE_REPLAY)
    assert check.status == "PASS"
    assert check.latest_calibration_timestamp <= cutoff
    assert "ground_truth" not in AgentBasedModel.run.__annotations__


def test_missing_interval_is_reported_without_fabrication() -> None:
    dataset = terra_fixture_dataset()
    rows = dataset.observations[:2] + dataset.observations[3:4]
    from sim.terra.datasets import quality_report

    report = quality_report(rows)
    assert report["missing_intervals"]


def test_naive_post_cutoff_copy_cannot_enter_calibration_view() -> None:
    dataset = terra_fixture_dataset()
    cutoff = parse_utc("2022-05-06T23:59:59Z")
    row = dataset.observations[0]
    post_cutoff = replace(row, timestamp=cutoff + timedelta(hours=1))
    with pytest.raises(ValueError, match="LEAKAGE_BLOCKED"):
        CalibrationDatasetView((row, post_cutoff), cutoff)


def test_fixture_window_is_hourly_and_monotonic() -> None:
    rows = terra_fixture_dataset().observations
    assert all(
        right.timestamp - left.timestamp == timedelta(hours=1) for left, right in zip(rows, rows[1:], strict=False)
    )
    assert rows[0].timestamp == datetime(2022, 5, 1, tzinfo=UTC)


@pytest.mark.parametrize("suffix", [".csv", ".json", ".parquet"])
def test_dataset_import_supports_documented_formats(tmp_path: Path, suffix: str) -> None:
    source = Path("docs/data/terra_hourly_state.csv")
    frame = pd.read_csv(source)
    destination = tmp_path / f"terra{suffix}"
    if suffix == ".csv":
        frame.to_csv(destination, index=False)
    elif suffix == ".json":
        destination.write_text(json.dumps(frame.to_dict(orient="records")), encoding="utf-8")
    else:
        frame.to_parquet(destination, index=False)

    dataset = import_research_dataset(
        destination,
        "import-smoke-v1",
        DataStatus.FIXTURE,
        "DOCUMENTED_SCHEMA_EXAMPLE",
        "LOCAL_FILE",
    )

    assert dataset.manifest.row_count == 2
    assert dataset.manifest.status == DataStatus.FIXTURE
    assert dataset.manifest.dataset_hash == dataset_hash(dataset.observations)
