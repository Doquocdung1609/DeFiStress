"""The presentation API must execute the unchanged synthetic warning engine."""

from __future__ import annotations

import io
import zipfile

from fastapi.testclient import TestClient

from backend.app.db import Repository
from backend.app.main import app
from backend.app.terra_api import terra_repository


def client(tmp_path):
    repository = Repository(f"sqlite:///{tmp_path / 'demo-warning.db'}")
    app.dependency_overrides[terra_repository] = lambda: repository
    return TestClient(app)


def test_b0_b1_b2_b3_are_computed_and_saved(tmp_path):
    api = client(tmp_path)
    try:
        response = api.post(
            "/api/v1/terra/demo/warnings",
            json={"ust_price": "0.99", "luna_previous_price": "100", "luna_current_price": "90"},
        )
        assert response.status_code == 201, response.text
        run = response.json()
        assert run["status"] == "COMPLETE" and run["origin"] == "SYNTHETIC"
        assert run["mode"] == "SYNTHETIC_WARNING"
        assert {name: value["level"] for name, value in run["models"].items()} == {
            "B0": "NORMAL", "B1": "HIGH", "B2": "HIGH", "B3": "WATCH",
        }
        assert run["models"]["B3"]["score"] == {"numerator": "1", "denominator": "2"}
        assert run["models"]["B3"]["input_lineage_hash"]
        assert run["models"]["B3"]["slots"][0]["selected"]["provenance"]["origin"] == "SYNTHETIC"
        assert api.get(f"/api/v1/terra/demo/runs/{run['id']}").json() == run
        exported = api.get(f"/api/v1/terra/demo/runs/{run['id']}/export")
        assert exported.status_code == 200
        with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
            assert "result.json" in archive.namelist()
            assert b'SYNTHETIC_WARNING' in archive.read("result.json")
    finally:
        app.dependency_overrides.clear()


def test_missing_and_future_inputs_abstain_without_partial_score(tmp_path):
    api = client(tmp_path)
    try:
        missing = api.post("/api/v1/terra/demo/warnings", json={"ust_price": None}).json()
        assert missing["models"]["B1"]["level"] == "ABSTAIN"
        assert missing["models"]["B1"]["score"] is None
        assert missing["models"]["B3"]["level"] == "ABSTAIN"
        delayed = api.post("/api/v1/terra/demo/warnings", json={"ust_delay_minutes": 1}).json()
        assert delayed["models"]["B1"]["level"] == "ABSTAIN"
        assert delayed["models"]["B3"]["level"] == "ABSTAIN"
        assert delayed["models"]["B2"]["level"] == "NORMAL"
        high = api.post("/api/v1/terra/demo/warnings", json={
            "ust_price": "0.96", "luna_previous_price": "100", "luna_current_price": "50",
        }).json()
        assert high["models"]["B3"]["level"] == "HIGH"
        assert high["models"]["B3"]["signals"]
        assert high["models"]["B3"]["context"]["information_cutoff"] == "2030-01-01T03:00:00.000000Z"
    finally:
        app.dependency_overrides.clear()


def test_invalid_or_nonfinite_inputs_are_rejected(tmp_path):
    api = client(tmp_path)
    try:
        for payload in ({"ust_price": "NaN"}, {"ust_price": "0"}, {"ust_price": 0.99},
                        {"ust_delay_minutes": -1}, {"cutoff": "2022-05-07T03:00:00Z"}):
            assert api.post("/api/v1/terra/demo/warnings", json=payload).status_code == 422
    finally:
        app.dependency_overrides.clear()
