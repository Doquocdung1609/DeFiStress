import io
import zipfile

from fastapi.testclient import TestClient

from backend.app.api import get_repository
from backend.app.config import Settings, get_settings
from backend.app.db import Repository
from backend.app.main import app
from sim import fixture_snapshot


def client(tmp_path) -> TestClient:
    repository = Repository(f"sqlite:///{tmp_path / 'test.db'}")
    app.dependency_overrides[get_repository] = lambda: repository
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None,
        eth_rpc_url="",
        eth_archive_rpc_url="",
        graph_api_key="",
    )
    return TestClient(app)


def test_fixture_scenario_run_and_export(tmp_path) -> None:
    api = client(tmp_path)
    snapshot = api.post("/api/v1/snapshots", json={"mode": "FIXTURE"})
    assert snapshot.status_code == 201
    assert snapshot.json()["mode"] == "FIXTURE"
    assert snapshot.json()["stablecoin_state"]["depeg_bps"] == 0

    scenario = api.post("/api/v1/scenarios", json={"snapshot_id": "fixture-main-v1"})
    assert scenario.status_code == 201
    run = api.post("/api/v1/runs", json={"scenario_id": scenario.json()["id"], "mode": "DETERMINISTIC"})
    assert run.status_code == 201
    payload = run.json()
    assert payload["status"] == "COMPLETE"
    assert payload["result"]["metrics"]["cascade_depth"] >= 2

    events = api.get(f"/api/v1/runs/{payload['id']}/events")
    assert events.status_code == 200
    assert any(item["event_type"] == "LIQUIDATION" for item in events.json())

    exported = api.get(f"/api/v1/runs/{payload['id']}/export")
    assert exported.status_code == 200
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        names = set(archive.namelist())
        assert {"manifest.json", "metrics.json", "events.csv", "timeseries.csv", "charts/price.png"} <= names

    provenance = api.get("/api/v1/provenance/fixture-main-v1")
    assert provenance.status_code == 200
    assert provenance.json()["block_hash"] == snapshot.json()["block_hash"]

    second_scenario = api.post(
        "/api/v1/scenarios",
        json={"snapshot_id": "fixture-main-v1", "name": "No Arbitrage", "arbitrage_capacity_pct": 0},
    )
    second_run = api.post(
        "/api/v1/runs",
        json={"scenario_id": second_scenario.json()["id"], "mode": "DETERMINISTIC"},
    )
    comparison = api.post(
        "/api/v1/runs/compare",
        json={"run_ids": [payload["id"], second_run.json()["id"]]},
    )
    assert comparison.status_code == 200
    assert len(comparison.json()["runs"]) == 2


def test_health_is_actionable_without_rpc(tmp_path) -> None:
    response = client(tmp_path).get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "healthy"
    assert payload["can_create_real_snapshot"] is False
    assert "ETH_RPC_URL" in payload["ethereum_rpc"]["error"]


def test_fork_validation_never_fakes_pass(tmp_path) -> None:
    api = client(tmp_path)
    api.post("/api/v1/snapshots", json={"mode": "FIXTURE"})
    response = api.post("/api/v1/validate/fork", json={"snapshot_id": "fixture-main-v1"})
    assert response.status_code == 200
    assert response.json()["status"] == "UNAVAILABLE"


def test_scenario_presets_cover_operational_and_policy_cases(tmp_path) -> None:
    response = client(tmp_path).get("/api/v1/scenario-presets")
    assert response.status_code == 200
    assert {
        "Baseline",
        "Moderate",
        "Severe",
        "Low Liquidity",
        "High Gas",
        "No Arbitrage",
        "Strong Arbitrage",
        "Policy Experiment",
    } <= set(response.json())


def test_local_monte_carlo_run_completes_with_seeded_tail_metrics(tmp_path) -> None:
    api = client(tmp_path)
    api.post("/api/v1/snapshots", json={"mode": "FIXTURE"})
    scenario = api.post(
        "/api/v1/scenarios",
        json={"snapshot_id": "fixture-main-v1", "monte_carlo_runs": 4, "seed": 73},
    )
    run = api.post(
        "/api/v1/runs",
        json={"scenario_id": scenario.json()["id"], "mode": "MONTE_CARLO"},
    )
    result = api.get(f"/api/v1/runs/{run.json()['id']}").json()
    assert result["status"] == "COMPLETE"
    assert result["progress_percent"] == 100
    assert result["result"]["monte_carlo"]["seed"] == 73
    assert 0 <= result["result"]["metrics"]["probability_of_cascade"] <= 1


def test_cached_mainnet_snapshot_keeps_real_provenance_and_explicit_mode(tmp_path) -> None:
    repository = Repository(f"sqlite:///{tmp_path / 'cached.db'}")
    mainnet = fixture_snapshot()
    mainnet["id"] = "real-test"
    mainnet["mode"] = "REAL_MAINNET"
    mainnet["label"] = "Ethereum Mainnet snapshot"
    repository.save_snapshot(mainnet)
    app.dependency_overrides[get_repository] = lambda: repository
    api = TestClient(app)
    response = api.post(
        "/api/v1/snapshots",
        json={"mode": "CACHED_MAINNET", "cached_snapshot_id": "real-test"},
    )
    assert response.status_code == 201
    assert response.json()["mode"] == "CACHED_MAINNET"
    assert response.json()["source_manifest"]["application"]["cached_from_snapshot_id"] == "real-test"
