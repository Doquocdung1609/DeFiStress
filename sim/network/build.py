from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

import networkx as nx

from sim.dex import V3Pool
from sim.network.metrics import (
    add_edges,
    bounded_ratio,
    build_contagion_matrix,
    compute_structural_centrality,
    impact_score,
    pressure_score,
)
from sim.network.schemas import (
    GRAPH_MODEL_VERSION,
    EvidenceStatus,
    GraphEdge,
    GraphFrame,
    GraphNode,
    NodeLayer,
    RelationType,
)
from sim.schemas import DexState, LiquidityTick

CORE_NODE_ORDER = [
    "protocol:aave-v3",
    "protocol:uniswap-v3",
    "asset:weth",
    "asset:usdc",
    "agent:borrower-cohort",
    "agent:liquidator",
    "agent:arbitrageur",
    "market:reference",
]

CLAIM_BOUNDARIES = [
    "The evidence-backed core contains Aave V3 and Uniswap V3; it is not a full map of DeFi.",
    "Normalized strength is a bounded visualization/comparison index, not a probability or correlation.",
    "Centrality measures position inside this modeled sub-network, not total importance across all DeFi.",
    "Simulated transmission does not establish observed historical causality.",
    "Scenario controls are assumptions, not observed market probabilities.",
]

NORMALIZATION_FORMULAS = {
    "COLLATERAL_EXPOSURE": "modeled WETH collateral USD / total modeled collateral USD",
    "DEBT_EXPOSURE": "modeled USDC debt USD / total modeled debt USD",
    "BORROWER_POSITION_EXPOSURE": "verified active borrowers / discovered candidate borrowers",
    "LIQUIDATION_FLOW": "pressure / (1 + pressure), pressure = execution value USD / selected pool 2%-depth USD",
    "EXECUTION_PRICE_IMPACT": "min(1, absolute price impact ratio / 0.02); 2% is a visualization reference",
    "REVALUATION_FEEDBACK": "model-attributed later-wave liquidated debt / sampled total debt",
    "ARBITRAGE_STABILIZATION": "recovered absolute spread / pre-arbitrage absolute spread",
    "LIQUIDATION_EXECUTION": "wave debt repaid / sampled total debt",
}
type MultiGraph = nx.MultiDiGraph[str, dict[str, Any], dict[str, Any]]


def build_snapshot_contagion_graph(snapshot: dict[str, Any]) -> dict[str, Any]:
    graph, nodes, edges, context = _build_structural_graph(snapshot)
    return _response(
        snapshot=snapshot,
        graph=graph,
        nodes=nodes,
        edges=edges,
        frames=[_initial_frame(edges, context)],
        mode="STRUCTURAL",
        run=None,
        scenario=None,
        aggregate_summary=None,
    )


def build_run_contagion_graph(
    snapshot: dict[str, Any],
    run: dict[str, Any],
    scenario: dict[str, Any] | None = None,
) -> dict[str, Any]:
    graph, nodes, edges, context = _build_structural_graph(snapshot)
    result = run.get("result") or {}
    if result.get("monte_carlo") is not None:
        return _response(
            snapshot=snapshot,
            graph=graph,
            nodes=nodes,
            edges=edges,
            frames=[_initial_frame(edges, context)],
            mode="AGGREGATE_SIMULATION_SUMMARY",
            run=run,
            scenario=scenario,
            aggregate_summary=result.get("metrics", {}),
        )

    dynamic_edges, frames = _dynamic_edges_and_frames(result, context, scenario or {})
    edges.extend(dynamic_edges)
    add_edges(graph, dynamic_edges)
    return _response(
        snapshot=snapshot,
        graph=graph,
        nodes=nodes,
        edges=edges,
        frames=[_initial_frame(edges[: len(edges) - len(dynamic_edges)], context), *frames],
        mode="RUN_WEIGHTED",
        run=run,
        scenario=scenario,
        aggregate_summary=None,
    )


def _build_structural_graph(
    snapshot: dict[str, Any],
) -> tuple[MultiGraph, list[GraphNode], list[GraphEdge], dict[str, float]]:
    snapshot_id = str(snapshot["id"])
    evidence = _snapshot_evidence(snapshot)
    borrowers = list(snapshot.get("borrowers", []))
    weth_price = _number(snapshot.get("oracle_prices", {}).get("WETH"))
    usdc_price = _number(snapshot.get("oracle_prices", {}).get("USDC"), 1.0)
    weth_collateral = sum(_number(_read(row, "collateral_weth")) for row in borrowers)
    weth_collateral_usd = weth_collateral * weth_price
    other_collateral_usd = sum(_number(_read(row, "other_collateral_usd")) for row in borrowers)
    usdc_debt = sum(_number(_read(row, "debt_usdc")) for row in borrowers)
    usdc_debt_usd = usdc_debt * usdc_price
    other_debt_usd = sum(_number(_read(row, "other_debt_usd")) for row in borrowers)
    total_collateral_usd = weth_collateral_usd + other_collateral_usd
    total_debt_usd = usdc_debt_usd + other_debt_usd
    active_borrowers = int(snapshot.get("coverage", {}).get("active_borrowers", len(borrowers)))
    candidates = int(snapshot.get("coverage", {}).get("candidates_discovered", active_borrowers))
    research_cohort = int(snapshot.get("coverage", {}).get("weth_usdc_cohort", 0))
    pool = snapshot.get("dex_pool", {})
    pool_address = str(_read(pool, "pool_address", "unknown"))
    fee = int(_number(_read(pool, "fee")))
    spot_price = _number(_read(pool, "spot_price"), weth_price)
    depth_2pct = _selected_depth_2pct(snapshot)
    provenance = {
        "snapshot_id": snapshot_id,
        "snapshot_mode": snapshot["mode"],
        "block_number": snapshot["block_number"],
        "block_hash": snapshot["block_hash"],
    }
    nodes = [
        GraphNode(
            "protocol:aave-v3",
            "Aave V3",
            NodeLayer.PROTOCOL,
            "LENDING_PROTOCOL",
            evidence,
            snapshot_id,
            "Verified lending positions and liquidation rules at the selected snapshot.",
            {
                "active_borrowers": active_borrowers,
                "weth_usdc_cohort": research_cohort,
                "sampled_debt_usd": total_debt_usd,
            },
            {**provenance, "source": "snapshot borrower positions"},
        ),
        GraphNode(
            "protocol:uniswap-v3",
            "Uniswap V3",
            NodeLayer.PROTOCOL,
            "DEX_PROTOCOL",
            evidence,
            snapshot_id,
            "Selected WETH/USDC execution venue and modeled executable depth.",
            {"pool_address": pool_address, "fee": fee, "depth_usdc_2pct": depth_2pct},
            {**provenance, "source": "selected Uniswap V3 pool state"},
        ),
        GraphNode(
            "asset:weth",
            "WETH",
            NodeLayer.ASSET,
            "COLLATERAL_ASSET",
            evidence,
            snapshot_id,
            "Shared collateral and execution-price risk factor.",
            {"oracle_price_usd": weth_price, "modeled_collateral_weth": weth_collateral},
            {**provenance, "source": "Aave oracle and modeled collateral"},
        ),
        GraphNode(
            "asset:usdc",
            "USDC",
            NodeLayer.ASSET,
            "DEBT_ASSET",
            evidence,
            snapshot_id,
            "Modeled debt denomination and Uniswap quote asset.",
            {"oracle_price_usd": usdc_price, "modeled_debt_usdc": usdc_debt},
            {**provenance, "source": "Aave oracle and modeled debt"},
        ),
        GraphNode(
            "agent:borrower-cohort",
            "Borrower Cohort",
            NodeLayer.AGENT_ROLE,
            "AGGREGATED_AGENT_ROLE",
            evidence,
            snapshot_id,
            "Aggregated cohort; no raw borrower addresses are exposed.",
            {"active_borrowers": active_borrowers, "research_cohort": research_cohort},
            {**provenance, "aggregation": "all modeled borrowers; identities pseudonymized upstream"},
        ),
        GraphNode(
            "agent:liquidator",
            "Liquidator",
            NodeLayer.AGENT_ROLE,
            "SIMULATED_AGENT_ROLE",
            EvidenceStatus.SCENARIO_ASSUMPTION,
            snapshot_id,
            "Liquidation execution agent governed by scenario capital, delay and profitability controls.",
            {},
            {"source": "scenario configuration"},
        ),
        GraphNode(
            "agent:arbitrageur",
            "Arbitrageur",
            NodeLayer.AGENT_ROLE,
            "SIMULATED_AGENT_ROLE",
            EvidenceStatus.SCENARIO_ASSUMPTION,
            snapshot_id,
            "Simulated stabilizing agent; not an observed historical actor.",
            {},
            {"source": "scenario configuration"},
        ),
        GraphNode(
            "market:reference",
            "Reference Market",
            NodeLayer.REFERENCE_MARKET,
            "REFERENCE_PRICE",
            EvidenceStatus.SCENARIO_ASSUMPTION,
            snapshot_id,
            "Exogenous reference-price path used by the stress scenario.",
            {"snapshot_weth_price_usd": weth_price},
            {"source": "snapshot oracle price plus scenario shock"},
        ),
    ]
    edges = _structural_edges(
        evidence=evidence,
        provenance=provenance,
        weth_collateral_usd=weth_collateral_usd,
        total_collateral_usd=total_collateral_usd,
        usdc_debt_usd=usdc_debt_usd,
        total_debt_usd=total_debt_usd,
        active_borrowers=active_borrowers,
        candidates=candidates,
        depth_2pct=depth_2pct,
        spot_price=spot_price,
        reference_price=weth_price,
    )
    graph: MultiGraph = nx.MultiDiGraph()
    for node in nodes:
        graph.add_node(node.id, **node.to_dict())
    add_edges(graph, edges)
    context = {
        "reference_price": weth_price,
        "spot_price": spot_price,
        "depth_2pct": depth_2pct,
        "sampled_total_debt": total_debt_usd,
    }
    return graph, nodes, edges, context


def _structural_edges(
    *,
    evidence: EvidenceStatus,
    provenance: dict[str, Any],
    weth_collateral_usd: float,
    total_collateral_usd: float,
    usdc_debt_usd: float,
    total_debt_usd: float,
    active_borrowers: int,
    candidates: int,
    depth_2pct: float,
    spot_price: float,
    reference_price: float,
) -> list[GraphEdge]:
    base = {**provenance, "source": "immutable selected snapshot"}
    return [
        _edge(
            "structural:collateral-exposure",
            "asset:weth",
            "protocol:aave-v3",
            RelationType.COLLATERAL_EXPOSURE,
            "EXPOSURE",
            {"weth_collateral_usd": weth_collateral_usd, "total_modeled_collateral_usd": total_collateral_usd},
            "USD",
            bounded_ratio(weth_collateral_usd, total_collateral_usd),
            evidence,
            base,
            "Modeled WETH liquidation collateral supplied to Aave V3.",
            NORMALIZATION_FORMULAS["COLLATERAL_EXPOSURE"],
        ),
        _edge(
            "structural:revaluation-channel",
            "asset:weth",
            "protocol:aave-v3",
            RelationType.REVALUATION_CHANNEL,
            "FEEDBACK",
            {"weth_collateral_usd": weth_collateral_usd},
            "USD",
            bounded_ratio(weth_collateral_usd, total_collateral_usd),
            EvidenceStatus.DERIVED_METRIC,
            base,
            "Structural WETH repricing channel into Aave borrower Health Factors; no realized flow is claimed.",
            NORMALIZATION_FORMULAS["COLLATERAL_EXPOSURE"],
        ),
        _edge(
            "structural:debt-exposure",
            "asset:usdc",
            "protocol:aave-v3",
            RelationType.DEBT_EXPOSURE,
            "EXPOSURE",
            {"usdc_debt_usd": usdc_debt_usd, "total_modeled_debt_usd": total_debt_usd},
            "USD",
            bounded_ratio(usdc_debt_usd, total_debt_usd),
            evidence,
            base,
            "Modeled USDC-denominated Aave debt exposure.",
            NORMALIZATION_FORMULAS["DEBT_EXPOSURE"],
        ),
        _edge(
            "structural:borrower-position-exposure",
            "agent:borrower-cohort",
            "protocol:aave-v3",
            RelationType.BORROWER_POSITION_EXPOSURE,
            "EXPOSURE",
            {
                "active_borrowers": active_borrowers,
                "candidate_borrowers": candidates,
                "sampled_debt_usd": total_debt_usd,
            },
            "borrowers_and_USD",
            bounded_ratio(active_borrowers, candidates),
            evidence,
            base,
            "Aggregated borrower cohort verified in the selected snapshot.",
            NORMALIZATION_FORMULAS["BORROWER_POSITION_EXPOSURE"],
        ),
        _edge(
            "structural:liquidation-route",
            "protocol:aave-v3",
            "protocol:uniswap-v3",
            RelationType.LIQUIDATION_ROUTE,
            "LIQUIDATION",
            {"realized_execution_value_usd": 0.0},
            "USD",
            0.0,
            EvidenceStatus.DERIVED_METRIC,
            base,
            "Potential liquidation execution route; structural only until a deterministic run activates it.",
            "inactive structural route; realized strength is derived from run events",
        ),
        _edge(
            "structural:execution-price-channel",
            "protocol:uniswap-v3",
            "asset:weth",
            RelationType.EXECUTION_PRICE_CHANNEL,
            "PRICE_IMPACT",
            {"executable_depth_usdc_2pct": depth_2pct, "spot_price_usd": spot_price},
            "USD",
            1.0 if depth_2pct > 0 else 0.0,
            evidence,
            base,
            "Observed/fixture pool state supporting a WETH execution-price channel.",
            "1 when positive selected-pool 2%-depth is available; 0 otherwise",
        ),
        _edge(
            "structural:liquidator-route",
            "agent:liquidator",
            "protocol:aave-v3",
            RelationType.LIQUIDATION_EXECUTION,
            "LIQUIDATION",
            {"realized_debt_repaid_usd": 0.0},
            "USD",
            0.0,
            EvidenceStatus.SCENARIO_ASSUMPTION,
            {"source": "scenario controls"},
            "Potential liquidator execution role; no observed actor is claimed.",
            "inactive before deterministic run events",
        ),
        _edge(
            "structural:arbitrage-route",
            "agent:arbitrageur",
            "protocol:uniswap-v3",
            RelationType.ARBITRAGE_STABILIZATION,
            "STABILIZATION",
            {"realized_recovery_ratio": 0.0},
            "ratio",
            0.0,
            EvidenceStatus.SCENARIO_ASSUMPTION,
            {"source": "scenario controls"},
            "Potential simulated arbitrage stabilization route.",
            "inactive before deterministic run events",
        ),
        _edge(
            "structural:reference-price-link",
            "market:reference",
            "asset:weth",
            RelationType.REFERENCE_PRICE_LINK,
            "PRICE_IMPACT",
            {"snapshot_reference_price_usd": reference_price},
            "USD",
            1.0 if reference_price > 0 else 0.0,
            EvidenceStatus.SCENARIO_ASSUMPTION,
            {"source": "scenario reference price"},
            "Reference price used to measure DEX divergence and arbitrage recovery.",
            "1 when a positive reference price is available; 0 otherwise",
        ),
    ]


def _dynamic_edges_and_frames(
    result: dict[str, Any], context: dict[str, float], scenario: dict[str, Any]
) -> tuple[list[GraphEdge], list[GraphFrame]]:
    events_by_wave: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in result.get("events", []):
        wave = int(event.get("wave", 0))
        if wave > 0 and event.get("event_type") in {"LIQUIDATION", "ARBITRAGE"}:
            events_by_wave[wave].append(event)
    edges: list[GraphEdge] = []
    frames: list[GraphFrame] = []
    cumulative_debt = 0.0
    for wave in sorted(events_by_wave):
        wave_events = events_by_wave[wave]
        liquidations = [event for event in wave_events if event.get("event_type") == "LIQUIDATION"]
        arbitrages = [event for event in wave_events if event.get("event_type") == "ARBITRAGE"]
        wave_edges: list[GraphEdge] = []
        debt = sum(_number(event.get("debt_repaid")) for event in liquidations)
        forced_weth = sum(_number(event.get("forced_sell_amount")) for event in liquidations)
        execution_value = sum(
            _number(event.get("forced_sell_amount")) * _number(event.get("execution_price")) for event in liquidations
        )
        pressure = execution_value / context["depth_2pct"] if context["depth_2pct"] > 0 else 0.0
        step = max((int(event.get("step", wave)) for event in wave_events), default=wave)
        provenance = {
            "source": "saved deterministic run events",
            "event_type": "LIQUIDATION",
            "wave": wave,
            "event_count": len(liquidations),
        }
        if liquidations:
            wave_edges.append(
                _edge(
                    f"wave:{wave}:liquidation-flow",
                    "protocol:aave-v3",
                    "protocol:uniswap-v3",
                    RelationType.LIQUIDATION_FLOW,
                    "LIQUIDATION",
                    {
                        "forced_weth": forced_weth,
                        "liquidated_debt_usd": debt,
                        "execution_value_usd": execution_value,
                        "liquidation_pressure_ratio": pressure,
                    },
                    "WETH_and_USD",
                    pressure_score(pressure),
                    EvidenceStatus.SIMULATED_RUN,
                    provenance,
                    "Forced WETH from saved Aave liquidation events, executed through the modeled Uniswap V3 pool.",
                    NORMALIZATION_FORMULAS["LIQUIDATION_FLOW"],
                    step,
                    wave,
                )
            )
            price_before = _number(liquidations[0].get("dex_price_before"))
            price_after = _number(liquidations[-1].get("dex_price_after"))
            impact = abs(price_after - price_before) / price_before if price_before > 0 else 0.0
            wave_edges.append(
                _edge(
                    f"wave:{wave}:execution-price-impact",
                    "protocol:uniswap-v3",
                    "asset:weth",
                    RelationType.EXECUTION_PRICE_IMPACT,
                    "PRICE_IMPACT",
                    {
                        "price_before_usd": price_before,
                        "price_after_usd": price_after,
                        "price_impact_ratio": impact,
                        "price_impact_bps": impact * 10_000,
                    },
                    "USD_and_ratio",
                    impact_score(impact),
                    EvidenceStatus.DERIVED_METRIC,
                    {**provenance, "source": "first/last LIQUIDATION event DEX prices in wave"},
                    "Absolute within-wave WETH execution-price movement caused by the saved forced-sale sequence.",
                    NORMALIZATION_FORMULAS["EXECUTION_PRICE_IMPACT"],
                    step,
                    wave,
                )
            )
            wave_edges.append(
                _edge(
                    f"wave:{wave}:liquidation-execution",
                    "agent:liquidator",
                    "protocol:aave-v3",
                    RelationType.LIQUIDATION_EXECUTION,
                    "LIQUIDATION",
                    {
                        "positions_processed": len(liquidations),
                        "debt_repaid_usd": debt,
                        "waves_active": 1,
                        "capital_usdc": _number(scenario.get("liquidator_capital_usdc")),
                        "gas_multiplier": _number(scenario.get("gas_multiplier")),
                        "delay_steps": int(scenario.get("liquidator_delay_steps", 0)),
                    },
                    "positions_and_USD",
                    bounded_ratio(debt, context["sampled_total_debt"]),
                    EvidenceStatus.SIMULATED_RUN,
                    {
                        **provenance,
                        "scenario_fields": ["liquidator_capital_usdc", "gas_multiplier", "liquidator_delay_steps"],
                    },
                    "Saved liquidation executions; capital, gas and delay fields remain scenario assumptions.",
                    NORMALIZATION_FORMULAS["LIQUIDATION_EXECUTION"],
                    step,
                    wave,
                )
            )
            if wave >= 2:
                wave_edges.append(
                    _edge(
                        f"wave:{wave}:revaluation-feedback",
                        "asset:weth",
                        "protocol:aave-v3",
                        RelationType.REVALUATION_FEEDBACK,
                        "FEEDBACK",
                        {
                            "model_attributed_liquidated_debt_usd": debt,
                            "incremental_liquidation_count": len(liquidations),
                        },
                        "USD_and_positions",
                        bounded_ratio(debt, context["sampled_total_debt"]),
                        EvidenceStatus.DERIVED_METRIC,
                        {
                            **provenance,
                            "causal_boundary": "model-attributed later-wave liquidation, not observed causality",
                        },
                        "Later-wave liquidation following prior modeled price feedback.",
                        NORMALIZATION_FORMULAS["REVALUATION_FEEDBACK"],
                        step,
                        wave,
                    )
                )
        if arbitrages:
            distance_before = sum(
                abs(_number(event.get("dex_price_before")) - _number(event.get("reference_price")))
                for event in arbitrages
            )
            distance_after = sum(
                abs(_number(event.get("dex_price_after")) - _number(event.get("reference_price")))
                for event in arbitrages
            )
            recovered = max(distance_before - distance_after, 0.0)
            recovery = bounded_ratio(recovered, distance_before)
            wave_edges.append(
                _edge(
                    f"wave:{wave}:arbitrage-stabilization",
                    "agent:arbitrageur",
                    "protocol:uniswap-v3",
                    RelationType.ARBITRAGE_STABILIZATION,
                    "STABILIZATION",
                    {
                        "distance_before_usd": distance_before,
                        "distance_after_usd": distance_after,
                        "recovered_spread_usd": recovered,
                        "recovery_ratio": recovery,
                    },
                    "USD_and_ratio",
                    recovery,
                    EvidenceStatus.SIMULATED_RUN,
                    {"source": "saved deterministic ARBITRAGE events", "wave": wave, "event_count": len(arbitrages)},
                    "Simulated arbitrage movement toward the reference price; not an observed historical action.",
                    NORMALIZATION_FORMULAS["ARBITRAGE_STABILIZATION"],
                    step,
                    wave,
                )
            )
        cumulative_debt += debt
        edges.extend(wave_edges)
        active_nodes = sorted({node_id for edge in wave_edges for node_id in (edge.source, edge.target)})
        last_event = arbitrages[-1] if arbitrages else liquidations[-1] if liquidations else {}
        first_liquidation = liquidations[0] if liquidations else last_event
        frames.append(
            GraphFrame(
                index=len(frames) + 1,
                label=f"Wave {wave}",
                wave=wave,
                step=step,
                active_nodes=active_nodes,
                active_edge_ids=[edge.id for edge in wave_edges],
                active_edges=[edge.to_dict() for edge in wave_edges],
                price_state={
                    "reference_price": _number(last_event.get("reference_price"), context["reference_price"]),
                    "dex_price_before": _number(first_liquidation.get("dex_price_before"), context["spot_price"]),
                    "dex_price_after": _number(last_event.get("dex_price_after"), context["spot_price"]),
                },
                liquidation_volume_usd=debt,
                forced_weth=forced_weth,
                liquidation_event_count=len(liquidations),
                cumulative_liquidated_debt_usd=cumulative_debt,
                cascade_depth_so_far=wave if debt > 0 else max(0, wave - 1),
            )
        )
    return edges, frames


def _response(
    *,
    snapshot: dict[str, Any],
    graph: MultiGraph,
    nodes: list[GraphNode],
    edges: list[GraphEdge],
    frames: list[GraphFrame],
    mode: str,
    run: dict[str, Any] | None,
    scenario: dict[str, Any] | None,
    aggregate_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    centrality = compute_structural_centrality(graph)
    source_manifest = snapshot.get("source_manifest", {})
    simulation_version = (
        run.get("model_version") if run else source_manifest.get("application", {}).get("model_version")
    )
    return {
        "graph_type": "MULTILAYER_DIRECTED_MULTIGRAPH",
        "graph_model_version": GRAPH_MODEL_VERSION,
        "simulation_model_version": simulation_version,
        "snapshot_id": snapshot["id"],
        "run_id": run.get("id") if run else None,
        "scenario_id": run.get("scenario_id") if run else None,
        "seed": run.get("seed") if run else None,
        "mode": mode,
        "evidence_mode": snapshot["mode"],
        "provenance": {
            "chain_id": snapshot["chain_id"],
            "block_number": snapshot["block_number"],
            "block_hash": snapshot["block_hash"],
            "block_timestamp": snapshot["block_timestamp"],
            "snapshot_mode": snapshot["mode"],
            "snapshot_id": snapshot["id"],
            "run_id": run.get("id") if run else None,
            "scenario_id": run.get("scenario_id") if run else None,
            "seed": run.get("seed") if run else None,
            "graph_model_version": GRAPH_MODEL_VERSION,
            "simulation_model_version": simulation_version,
        },
        "nodes": [node.to_dict() for node in nodes],
        "edges": [edge.to_dict() for edge in edges],
        "layers": [layer.value for layer in NodeLayer],
        "relation_types": sorted({edge.relation_type.value for edge in edges}),
        "centrality": centrality,
        "contagion_matrix": build_contagion_matrix(graph, CORE_NODE_ORDER),
        "frames": [frame.to_dict() for frame in frames],
        "aggregate_summary": aggregate_summary,
        "graph_metadata": {
            "active_protocol_count": sum(node.layer == NodeLayer.PROTOCOL for node in nodes),
            "edge_count": len(edges),
            "cascade_depth": int((run or {}).get("result", {}).get("metrics", {}).get("cascade_depth") or 0),
            "multiedges_preserved": True,
            "borrowers_aggregated": True,
            "conceptual_extensions_included": False,
            "normalization_formulas": NORMALIZATION_FORMULAS,
            "scenario_assumptions": scenario or {},
        },
        "claim_boundaries": CLAIM_BOUNDARIES,
    }


def _initial_frame(edges: list[GraphEdge], context: dict[str, float]) -> GraphFrame:
    return GraphFrame(
        index=0,
        label="Initial State",
        wave=0,
        step=0,
        active_nodes=CORE_NODE_ORDER,
        active_edge_ids=[edge.id for edge in edges],
        active_edges=[edge.to_dict() for edge in edges],
        price_state={
            "reference_price": context["reference_price"],
            "dex_price_before": context["spot_price"],
            "dex_price_after": context["spot_price"],
        },
        liquidation_volume_usd=0.0,
        forced_weth=0.0,
        liquidation_event_count=0,
        cumulative_liquidated_debt_usd=0.0,
        cascade_depth_so_far=0,
    )


def _edge(
    edge_id: str,
    source: str,
    target: str,
    relation: RelationType,
    layer: str,
    raw_value: dict[str, float | int | str | None],
    unit: str,
    strength: float,
    evidence: EvidenceStatus,
    provenance: dict[str, Any],
    description: str,
    formula: str,
    step: int | None = None,
    wave: int | None = None,
) -> GraphEdge:
    return GraphEdge(
        id=edge_id,
        source=source,
        target=target,
        relation_type=relation,
        layer=layer,
        direction="DIRECTED",
        raw_value=raw_value,
        unit=unit,
        normalized_strength=min(1.0, max(0.0, float(strength))),
        evidence_status=evidence,
        provenance=provenance,
        description=description,
        formula=formula,
        active=strength > 0,
        step=step,
        wave=wave,
    )


def _snapshot_evidence(snapshot: dict[str, Any]) -> EvidenceStatus:
    return (
        EvidenceStatus.OBSERVED_ONCHAIN
        if snapshot.get("mode") in {"REAL_MAINNET", "CACHED_MAINNET"}
        else EvidenceStatus.SCENARIO_ASSUMPTION
    )


def _selected_depth_2pct(snapshot: dict[str, Any]) -> float:
    selected = snapshot.get("dex_pool", {})
    selected_address = str(_read(selected, "pool_address", "")).lower()
    for pool in snapshot.get("dex_pools", []):
        if str(_read(pool, "pool_address", "")).lower() == selected_address:
            depth = _number(_read(pool, "depth_usdc_2pct"))
            if depth > 0:
                return depth
    try:
        dex_state = selected if isinstance(selected, DexState) else _dex_state_from_mapping(selected)
        return float(V3Pool(dex_state).depth_to_price_drop_usdc(Decimal("2")))
    except (AttributeError, ArithmeticError, KeyError, TypeError, ValueError):
        return 0.0


def _dex_state_from_mapping(pool: dict[str, Any]) -> DexState:
    return DexState(
        pool_address=str(pool["pool_address"]),
        token0=str(pool["token0"]),
        token1=str(pool["token1"]),
        fee=int(pool["fee"]),
        tick_spacing=int(pool["tick_spacing"]),
        sqrt_price_x96=Decimal(str(pool["sqrt_price_x96"])),
        tick=int(pool["tick"]),
        liquidity=Decimal(str(pool["liquidity"])),
        ticks=[
            LiquidityTick(
                tick=int(row["tick"]),
                liquidity_net=Decimal(str(row["liquidity_net"])),
                liquidity_gross=Decimal(str(row["liquidity_gross"])),
            )
            for row in pool.get("ticks", [])
        ],
        token0_decimals=int(pool.get("token0_decimals", 6)),
        token1_decimals=int(pool.get("token1_decimals", 18)),
        source=str(pool.get("source", "UNKNOWN")),
    )


def _read(value: Any, key: str, default: Any = 0) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _number(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if number == number and number not in {float("inf"), float("-inf")} else default
