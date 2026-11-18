"""Illustrative exit arithmetic must never imply guaranteed liquidity."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.db import Repository
from backend.app.main import app
from backend.app.terra_api import terra_repository


def test_exit_capacity_and_readback(tmp_path):
    repository = Repository(f"sqlite:///{tmp_path / 'exit.db'}")
    app.dependency_overrides[terra_repository] = lambda: repository
    try:
        api = TestClient(app)
        result = api.post("/api/v1/terra/demo/exits", json={
            "quantity_ust": "1000", "price_usd": "0.8", "capacity_ust": "600",
            "fee_percent": "1", "slippage_percent": "2", "latency_minutes": 15,
        })
        assert result.status_code == 201, result.text
        run = result.json()
        assert run["mode"] == "ILLUSTRATIVE_EXIT"
        assert run["origin"] == "SYNTHETIC"
        assert run["execution_status"] == "CAPACITY_ASSUMED_PARTIAL"
        assert run["calculation"] == {
            "requested_ust": "1000", "filled_ust": "600", "unfilled_ust": "400",
            "gross_usd": "480", "fee_usd": "4.8", "slippage_usd": "9.6",
            "net_usd": "465.6", "latency_minutes": 15,
            "estimated_execution_time": "2030-01-01T03:15:00Z",
            "warning_timestamp": "2030-01-01T03:00:00Z",
            "warning_price_usd": "1", "price_move_percent": "-20",
            "modeled_loss_usd": "134.4",
        }
        assert api.get(f"/api/v1/terra/demo/runs/{run['id']}").json() == run
        assert api.get(f"/api/v1/terra/demo/runs/{run['id']}/export").status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_unknown_capacity_is_not_verifiable(tmp_path):
    repository = Repository(f"sqlite:///{tmp_path / 'unknown.db'}")
    app.dependency_overrides[terra_repository] = lambda: repository
    try:
        run = TestClient(app).post("/api/v1/terra/demo/exits", json={
            "quantity_ust": "1000", "price_usd": "0.8",
        }).json()
        assert run["execution_status"] == "NOT_VERIFIABLE"
        assert run["calculation"]["filled_ust"] is None
        assert run["calculation"]["net_usd"] is None
    finally:
        app.dependency_overrides.clear()


def test_exit_invalid_numbers_rejected(tmp_path):
    repository = Repository(f"sqlite:///{tmp_path / 'invalid.db'}")
    app.dependency_overrides[terra_repository] = lambda: repository
    try:
        api = TestClient(app)
        for body in ({"quantity_ust": "NaN"}, {"quantity_ust": "0"},
                     {"price_usd": -1}, {"capacity_ust": "-2"},
                     {"fee_percent": "101"}, {"slippage_percent": "Infinity"},
                     {"latency_minutes": -1}):
            assert api.post("/api/v1/terra/demo/exits", json=body).status_code == 422
    finally:
        app.dependency_overrides.clear()
