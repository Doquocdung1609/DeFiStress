from __future__ import annotations

import io
import zipfile

from fastapi.testclient import TestClient

from backend.app.config import Settings, get_settings
from backend.app.db import Repository
from backend.app.main import app
from backend.app.terra_api import terra_repository


def test_terra_api_lifecycle_and_export(tmp_path) -> None:
    repository = Repository(f"sqlite:///{tmp_path / 'terra.db'}")
    app.dependency_overrides[terra_repository] = lambda: repository
    app.dependency_overrides[get_settings] = lambda: Settings(\n        terra_archive_lcd_url="",\n        terra_history_data_url="",\n        eth_archive_rpc_url="",\n        curve_history_data_url="",\n        bridge_flow_data_url="",\n    )\n    api = TestClient(app)\n    status = api.get("/api/v1/terra/status")
    assert status.status_code == 200
    assert status.json()["datasets"][0]["status"] == "FIXTURE"
    assert all(item["status"] == "UNAVAILABLE" for item in status.json()["historical_sources"])

    replay = api.post("/api/v1/terra/replays", json={"model_name": "ABM", "seed": 19})
    assert replay.status_code == 201
    payload = replay.json()
    assert payload["metadata"]["leakage_check_status"]["status"] == "PASS"
    assert payload["dataset"]["status"] == "FIXTURE"
    replay_id = payload["id"]
    assert api.get(f"/api/v1/terra/replays/{replay_id}/metrics").status_code == 200

    exported = api.get(f"/api/v1/terra/export/{replay_id}")
    assert exported.status_code == 200
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        names = set(archive.namelist())
    assert {
        "manifest.json",
        "data_sources.json",
        "cutoff.json",
        "parameters.json",
        "simulation_timeseries.csv",
        "ground_truth_timeseries.csv",
        "validation_metrics.csv",
        "quality_report.json",
    } <= names
    app.dependency_overrides.clear()


def test_case_study_api_preserves_aave_and_terra(tmp_path) -> None:
    repository = Repository(f"sqlite:///{tmp_path / 'cases.db'}")
    app.dependency_overrides[terra_repository] = lambda: repository
    api = TestClient(app)
    cases = api.get("/api/v1/case-studies").json()
    assert {item["id"] for item in cases} == {"aave-v3", "terra-2022"}
    app.dependency_overrides.clear()


def test_terra_source_status_reflects_configured_providers(tmp_path) -> None:
    repository = Repository(f"sqlite:///{tmp_path / 'configured.db'}")
    app.dependency_overrides[terra_repository] = lambda: repository
    app.dependency_overrides[get_settings] = lambda: Settings(
        terra_archive_lcd_url="https://terra.example.invalid",
        terra_history_data_url="https://data.example.invalid/terra.json",
        eth_archive_rpc_url="https://ethereum.example.invalid",
        curve_history_data_url="https://data.example.invalid/curve.json",
        bridge_flow_data_url="https://data.example.invalid/bridge.json",
    )
    api = TestClient(app)

    payload = api.get("/api/v1/terra/status").json()

    assert [item["status"] for item in payload["historical_sources"]] == [
        "CONFIGURED",
        "CONFIGURED",
        "CONFIGURED",
    ]
    build = api.post("/api/v1/terra/datasets/build")
    assert build.status_code == 200
    assert build.json()["status"] == "CONFIGURED"
    app.dependency_overrides.clear()
