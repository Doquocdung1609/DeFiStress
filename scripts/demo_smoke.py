"""Exercise the running local API through its public HTTP boundary."""

from __future__ import annotations

import argparse
import io
import json
import urllib.request
import zipfile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8100")
    args = parser.parse_args()
    base = args.base.rstrip("/")

    def call(path: str, body: dict | None = None) -> dict | bytes:
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(base + path, data=data)
        if data is not None:
            request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request, timeout=90) as response:
            if response.headers.get_content_type() == "application/zip":
                return response.read()
            return json.load(response)

    health = call("/api/v1/health")
    assert isinstance(health, dict) and health["service"] == "healthy"
    print("1 health: healthy")
    snapshot = call("/api/v1/snapshots", {"mode": "FIXTURE"})
    assert isinstance(snapshot, dict) and snapshot["id"]
    print("2 Aave fixture snapshot:", snapshot["id"])
    scenario = call("/api/v1/scenarios", {"snapshot_id": snapshot["id"]})
    assert isinstance(scenario, dict)
    run = call("/api/v1/runs", {"scenario_id": scenario["id"], "mode": "DETERMINISTIC"})
    assert isinstance(run, dict) and run["id"] and run["status"] == "COMPLETE"
    result = run["result"]
    assert result["metrics"]["total_liquidated_debt"] > 0
    assert result["metrics"]["cascade_depth"] >= 1
    assert result["events"] and result["timeseries"]
    print("3 Aave scenario and run:", run["id"])
    history = call("/api/v1/terra/demo/historical-data")
    assert isinstance(history, dict) and len(history["observations"]) == 1776
    print("4 Terra historical rows: 1776")
    retrospective = call("/api/v1/terra/early-warning?mode=RETROSPECTIVE")
    assert isinstance(retrospective, dict) and retrospective["mode"] == "RETROSPECTIVE"
    print("5 Terra retrospective warning: timeline", len(retrospective["timeline"]))
    warning = call("/api/v1/terra/demo/warnings", {
        "ust_price": "0.99", "luna_previous_price": "100", "luna_current_price": "90",
    })
    assert isinstance(warning, dict) and warning["origin"] == "SYNTHETIC"
    assert {name: model["level"] for name, model in warning["models"].items()} == {
        "B0": "NORMAL", "B1": "HIGH", "B2": "HIGH", "B3": "WATCH",
    }
    missing = call("/api/v1/terra/demo/warnings", {"ust_price": None})
    assert isinstance(missing, dict) and missing["models"]["B3"]["level"] == "ABSTAIN"
    print("6 synthetic B0-B3: WATCH and ABSTAIN verified")
    stress = call("/api/v1/terra/stress-test", {"runs": 2, "horizon_hours": 4})
    assert isinstance(stress, dict) and stress["runs"] == 2 and stress["summary"]
    print("7 Terra stress: 2 seeded runs")
    exit_run = call("/api/v1/terra/demo/exits", {
        "quantity_ust": "1000", "price_usd": "0.8", "capacity_ust": "600",
        "fee_percent": "1", "slippage_percent": "2", "latency_minutes": 15,
    })
    assert isinstance(exit_run, dict) and exit_run["execution_status"] == "CAPACITY_ASSUMED_PARTIAL"
    assert exit_run["calculation"]["net_usd"] == "465.6"
    assert exit_run["calculation"]["filled_ust"] == "600"
    assert exit_run["calculation"]["unfilled_ust"] == "400"
    assert exit_run["calculation"]["modeled_loss_usd"] == "134.4"
    print("8 illustrative exit: 465.6 USD")
    saved = call(f"/api/v1/terra/demo/runs/{exit_run['id']}")
    assert saved == exit_run
    listing = call("/api/v1/terra/demo/runs")
    assert isinstance(listing, list) and any(row["id"] == exit_run["id"] for row in listing)
    archive = call(f"/api/v1/terra/demo/runs/{exit_run['id']}/export")
    assert isinstance(archive, bytes)
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        assert json.loads(zf.read("result.json")) == exit_run
    print("9 persistence, history, ZIP export: verified")


if __name__ == "__main__":
    main()
