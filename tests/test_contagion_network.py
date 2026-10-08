from __future__ import annotations

import copy
import json
import math
from dataclasses import replace
from decimal import Decimal

import networkx as nx
from fastapi.testclient import TestClient

from backend.app.api import get_repository
from backend.app.db import Repository
from backend.app.main import app
from sim import Scenario, fixture_snapshot, run_simulation
from sim.fixtures import FIXTURE_PRICE, fixture_dex, fixture_positions
from sim.network import build_run_contagion_graph, build_snapshot_contagion_graph
from sim.network.metrics import impact_score, pressure_score


def _completed_run(scenario: Scenario | None = None) -> tuple[dict, dict]:
    scenario = scenario or Scenario()
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, scenario, run_id="run-test").to_dict()
    run = {
        "id": "run-test",
        "scenario_id": "scenario-test",
        "seed": scenario.seed,
        "model_version": result["model_version"],
        "status": "COMPLETE",
        "result": result,
    }
    return run, result


def test_structural_graph_is_deterministic_multilayer_multigraph_with_feedback_cycle() -> None:
    first = build_snapshot_contagion_graph(fixture_snapshot())
    second = build_snapshot_contagion_graph(fixture_snapshot())
    assert first == second
    assert first["graph_type"] == "MULTILAYER_DIRECTED_MULTIGRAPH"
    assert [node["id"] for node in first["nodes"]] == [
        "protocol:aave-v3",
        "protocol:uniswap-v3",
        "asset:weth",
        "asset:usdc",
        "agent:borrower-cohort",
        "agent:liquidator",
        "agent:arbitrageur",
        "market:reference",
    ]
    parallel = [
        edge for edge in first["edges"] if edge["source"] == "asset:weth" and edge["target"] == "protocol:aave-v3"
    ]
    assert {edge["relation_type"] for edge in parallel} == {"COLLATERAL_EXPOSURE", "REVALUATION_CHANNEL"}
    graph = nx.DiGraph((edge["source"], edge["target"]) for edge in first["edges"])
    assert nx.has_path(graph, "asset:weth", "protocol:aave-v3")
    assert nx.has_path(graph, "protocol:aave-v3", "protocol:uniswap-v3")
    assert nx.has_path(graph, "protocol:uniswap-v3", "asset:weth")
    assert first["graph_metadata"]["conceptual_extensions_included"] is False


def test_snapshot_edges_equal_fixture_exposures_and_never_expose_raw_borrower_addresses() -> None:
    snapshot = fixture_snapshot()
    graph = build_snapshot_contagion_graph(snapshot)
    by_relation = {edge["relation_type"]: edge for edge in graph["edges"]}
    positions = fixture_positions()
    expected_weth_usd = float(sum((row.collateral_weth for row in positions), Decimal(0)) * FIXTURE_PRICE)
    expected_debt = float(sum((row.debt_usdc for row in positions), Decimal(0)))
    assert math.isclose(by_relation["COLLATERAL_EXPOSURE"]["raw_value"]["weth_collateral_usd"], expected_weth_usd)
    assert math.isclose(by_relation["DEBT_EXPOSURE"]["raw_value"]["usdc_debt_usd"], expected_debt)
    assert all("borrower_hash" not in node["raw_metrics"] for node in graph["nodes"])


def test_real_and_fixture_evidence_modes_remain_explicit() -> None:
    fixture = fixture_snapshot()
    real = copy.deepcopy(fixture)
    real.update(id="real-network", mode="REAL_MAINNET", label="Ethereum Mainnet snapshot")
    fixture_graph = build_snapshot_contagion_graph(fixture)
    real_graph = build_snapshot_contagion_graph(real)
    assert fixture_graph["evidence_mode"] == "FIXTURE"
    assert real_graph["evidence_mode"] == "REAL_MAINNET"
    assert {node["evidence_status"] for node in fixture_graph["nodes"]} >= {"SCENARIO_ASSUMPTION"}
    assert (
        next(node for node in real_graph["nodes"] if node["id"] == "protocol:aave-v3")["evidence_status"]
        == "OBSERVED_ONCHAIN"
    )


def test_run_edges_and_wave_frames_are_exact_derivations_of_saved_events() -> None:
    run, result = _completed_run()
    original = copy.deepcopy(run)
    graph = build_run_contagion_graph(fixture_snapshot(), run, result["scenario"])
    assert run == original
    liquidation_events = [event for event in result["events"] if event["event_type"] == "LIQUIDATION"]
    frames_by_wave = {frame["wave"]: frame for frame in graph["frames"]}
    assert frames_by_wave[0]["label"] == "Initial State"
    assert len(graph["frames"]) == int(result["metrics"]["cascade_depth"]) + 1
    for wave in sorted({int(event["wave"]) for event in liquidation_events}):
        events = [event for event in liquidation_events if int(event["wave"]) == wave]
        expected_debt = sum(float(event["debt_repaid"]) for event in events)
        expected_weth = sum(float(event["forced_sell_amount"]) for event in events)
        frame = frames_by_wave[wave]
        assert math.isclose(frame["liquidation_volume_usd"], expected_debt)
        assert math.isclose(frame["forced_weth"], expected_weth)
        liquidation_edge = next(edge for edge in frame["active_edges"] if edge["relation_type"] == "LIQUIDATION_FLOW")
        assert math.isclose(liquidation_edge["raw_value"]["liquidated_debt_usd"], expected_debt)
        assert math.isclose(liquidation_edge["raw_value"]["forced_weth"], expected_weth)
        impact_edge = next(edge for edge in frame["active_edges"] if edge["relation_type"] == "EXECUTION_PRICE_IMPACT")
        expected_impact = abs(float(events[-1]["dex_price_after"]) - float(events[0]["dex_price_before"])) / float(
            events[0]["dex_price_before"]
        )
        assert math.isclose(impact_edge["raw_value"]["price_impact_ratio"], expected_impact)
    assert any(edge["relation_type"] == "REVALUATION_FEEDBACK" for edge in frames_by_wave[2]["active_edges"])


def test_arbitrage_recovery_is_derived_from_saved_arbitrage_events() -> None:
    run, result = _completed_run()
    graph = build_run_contagion_graph(fixture_snapshot(), run, result["scenario"])
    arbitrage_events = [event for event in result["events"] if event["event_type"] == "ARBITRAGE"]
    edges = [edge for edge in graph["edges"] if edge["relation_type"] == "ARBITRAGE_STABILIZATION" and edge["wave"]]
    assert len(edges) == len(arbitrage_events)
    for edge, event in zip(edges, arbitrage_events, strict=True):
        before = abs(float(event["dex_price_before"]) - float(event["reference_price"]))
        after = abs(float(event["dex_price_after"]) - float(event["reference_price"]))
        expected = max(before - after, 0) / before if before else 0
        assert math.isclose(edge["normalized_strength"], expected)


def test_normalization_is_bounded_finite_and_monotonic() -> None:
    assert pressure_score(0) == 0
    assert 0 < pressure_score(0.5) < pressure_score(2) < 1
    assert impact_score(0) == 0
    assert impact_score(0.01) <= impact_score(0.02) == impact_score(0.20) == 1
    run, result = _completed_run()
    for graph in (
        build_snapshot_contagion_graph(fixture_snapshot()),
        build_run_contagion_graph(fixture_snapshot(), run, result["scenario"]),
    ):
        assert all(math.isfinite(edge["normalized_strength"]) for edge in graph["edges"])
        assert all(0 <= edge["normalized_strength"] <= 1 for edge in graph["edges"])


def test_matrix_orientation_parallel_aggregation_and_centrality_are_deterministic() -> None:
    graph = build_snapshot_contagion_graph(fixture_snapshot())
    matrix = graph["contagion_matrix"]
    order = matrix["node_order"]
    assert len(matrix["values"]) == len(order)
    assert all(len(row) == len(order) for row in matrix["values"])
    assert all(matrix["values"][index][index] == 0 for index in range(len(order)))
    weth = order.index("asset:weth")
    aave = order.index("protocol:aave-v3")
    cell = matrix["cells"][weth][aave]
    assert set(cell["relation_types"]) == {"COLLATERAL_EXPOSURE", "REVALUATION_CHANNEL"}
    assert cell["max_normalized_strength"] == matrix["values"][weth][aave]
    assert all("conceptual" not in node_id for node_id in order)
    centrality = graph["centrality"]
    assert centrality == build_snapshot_contagion_graph(fixture_snapshot())["centrality"]
    assert centrality["structural_bridge_node"] in order
    for row in centrality["nodes"].values():
        assert all(value is None or math.isfinite(value) for value in row.values())
    assert centrality["eigenvector_unavailable_reason"] is None or centrality[
        "eigenvector_unavailable_reason"
    ].startswith("Unavailable:")


def test_no_second_wave_frame_is_invented_when_run_depth_is_one() -> None:
    scenario = replace(Scenario(), max_waves=1)
    run, result = _completed_run(scenario)
    graph = build_run_contagion_graph(fixture_snapshot(), run, result["scenario"])
    assert result["metrics"]["cascade_depth"] == 1
    assert [frame["wave"] for frame in graph["frames"]] == [0, 1]


def test_api_structural_run_pending_monte_carlo_and_missing_behavior(tmp_path) -> None:
    repository = Repository(f"sqlite:///{tmp_path / 'network.db'}")
    repository.save_snapshot(fixture_snapshot())
    app.dependency_overrides[get_repository] = lambda: repository
    api = TestClient(app)
    structural = api.get("/api/v1/snapshots/fixture-main-v1/contagion-graph")
    assert structural.status_code == 200
    assert structural.json()["evidence_mode"] == "FIXTURE"
    assert api.get("/api/v1/snapshots/missing/contagion-graph").status_code == 404

    scenario = api.post("/api/v1/scenarios", json={"snapshot_id": "fixture-main-v1"}).json()
    deterministic = api.post("/api/v1/runs", json={"scenario_id": scenario["id"], "mode": "DETERMINISTIC"}).json()
    weighted = api.get(f"/api/v1/runs/{deterministic['id']}/contagion-graph")
    assert weighted.status_code == 200
    assert weighted.json()["mode"] == "RUN_WEIGHTED"
    assert weighted.json()["provenance"]["scenario_id"] == scenario["id"]

    pending_id = repository.create_run(scenario["id"], 1, "test", status="PENDING")
    assert api.get(f"/api/v1/runs/{pending_id}/contagion-graph").status_code == 409

    monte_carlo = api.post("/api/v1/runs", json={"scenario_id": scenario["id"], "mode": "MONTE_CARLO"}).json()
    monte_graph = api.get(f"/api/v1/runs/{monte_carlo['id']}/contagion-graph")
    assert monte_graph.status_code == 200
    assert monte_graph.json()["mode"] == "AGGREGATE_SIMULATION_SUMMARY"
    assert [frame["wave"] for frame in monte_graph.json()["frames"]] == [0]
    app.dependency_overrides.clear()


def test_real_artifact_graph_does_not_leak_raw_borrower_addresses() -> None:
    with open("data/processed/mainnet/aave_uniswap_snapshot_26045352.json", encoding="utf-8") as source:
        snapshot = json.load(source)
    raw_address = snapshot["borrowers"][0]["provenance"]["raw_address"]
    graph = build_snapshot_contagion_graph(snapshot)
    assert graph["evidence_mode"] == "REAL_MAINNET"
    assert graph["provenance"]["block_number"] == 26_045_352
    assert raw_address not in json.dumps(graph)
