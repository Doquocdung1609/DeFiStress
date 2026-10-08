from __future__ import annotations

import math
from typing import Any

import networkx as nx

from sim.network.schemas import GraphEdge

COLLAPSE_POLICY = "Parallel channels collapse with max normalized strength per directed node pair."
type MultiGraph = nx.MultiDiGraph[str, dict[str, Any], dict[str, Any]]
type DirectedGraph = nx.DiGraph[str, dict[str, Any], dict[str, Any]]


def bounded_ratio(numerator: float, denominator: float) -> float:
    if numerator <= 0 or denominator <= 0:
        return 0.0
    value = numerator / denominator
    return min(1.0, max(0.0, value)) if math.isfinite(value) else 0.0


def pressure_score(pressure_ratio: float) -> float:
    if pressure_ratio <= 0 or not math.isfinite(pressure_ratio):
        return 0.0
    return pressure_ratio / (1.0 + pressure_ratio)


def impact_score(impact_ratio: float, reference_ratio: float = 0.02) -> float:
    return bounded_ratio(impact_ratio, reference_ratio)


def collapse_multigraph(graph: MultiGraph, *, active_only: bool = False) -> DirectedGraph:
    collapsed: DirectedGraph = nx.DiGraph()
    for node_id, attributes in graph.nodes(data=True):
        if attributes.get("evidence_status") != "CONCEPTUAL_EXTENSION":
            collapsed.add_node(node_id)
    for source, target, attributes in graph.edges(data=True):
        if source not in collapsed or target not in collapsed:
            continue
        if active_only and not attributes.get("active", True):
            continue
        strength = _finite_strength(attributes.get("normalized_strength", 0.0))
        previous = collapsed.get_edge_data(source, target, {}).get("weight", 0.0)
        if not collapsed.has_edge(source, target) or strength > previous:
            collapsed.add_edge(source, target, weight=strength)
    return collapsed


def compute_structural_centrality(graph: MultiGraph) -> dict[str, Any]:
    collapsed = collapse_multigraph(graph)
    nodes = sorted(collapsed.nodes)
    if len(nodes) < 2:
        empty = {node_id: 0.0 for node_id in nodes}
        return _centrality_payload(empty, empty, empty, empty, {}, "At least two nodes are required.")
    in_degree = nx.in_degree_centrality(collapsed)
    out_degree = nx.out_degree_centrality(collapsed)
    betweenness = nx.betweenness_centrality(collapsed, normalized=True, weight=None)
    eigenvector: dict[str, float] = {}
    eigenvector_reason: str | None = None
    try:
        eigenvector = nx.eigenvector_centrality(collapsed, max_iter=1_000, tol=1e-12)
        if not all(math.isfinite(value) for value in eigenvector.values()):
            raise nx.NetworkXError("non-finite eigenvector result")
    except (nx.NetworkXException, ZeroDivisionError) as exc:
        eigenvector = {}
        eigenvector_reason = f"Unavailable: {exc}"
    weighted_graph = collapse_multigraph(graph, active_only=True)
    denominator = max(1, len(nodes) - 1)
    weighted = {
        node_id: sum(float(data["weight"]) for _, _, data in weighted_graph.out_edges(node_id, data=True)) / denominator
        for node_id in nodes
    }
    return _centrality_payload(in_degree, out_degree, betweenness, weighted, eigenvector, eigenvector_reason)


def _centrality_payload(
    in_degree: dict[str, float],
    out_degree: dict[str, float],
    betweenness: dict[str, float],
    weighted: dict[str, float],
    eigenvector: dict[str, float],
    eigenvector_reason: str | None,
) -> dict[str, Any]:
    node_ids = sorted(in_degree)
    rows = {
        node_id: {
            "in_degree_centrality": _finite_strength(in_degree.get(node_id, 0.0)),
            "out_degree_centrality": _finite_strength(out_degree.get(node_id, 0.0)),
            "betweenness_centrality": _finite_strength(betweenness.get(node_id, 0.0)),
            "eigenvector_centrality": (_finite_strength(eigenvector[node_id]) if node_id in eigenvector else None),
            "weighted_influence_strength": _finite_strength(weighted.get(node_id, 0.0)),
        }
        for node_id in node_ids
    }
    bridge = (
        min(
            node_ids,
            key=lambda node_id: (-float(rows[node_id]["betweenness_centrality"] or 0.0), node_id),
        )
        if node_ids
        else None
    )
    return {
        "aggregation_policy": COLLAPSE_POLICY,
        "weighted_influence_interpretation": "Exploratory outgoing channel strength inside this modeled network.",
        "nodes": rows,
        "structural_bridge_node": bridge,
        "eigenvector_unavailable_reason": eigenvector_reason,
    }


def build_contagion_matrix(graph: MultiGraph, node_order: list[str]) -> dict[str, Any]:
    values: list[list[float]] = []
    cells: list[list[dict[str, Any]]] = []
    for source in node_order:
        value_row: list[float] = []
        cell_row: list[dict[str, Any]] = []
        for target in node_order:
            edge_data = [] if source == target else list((graph.get_edge_data(source, target) or {}).values())
            details = sorted(edge_data, key=lambda item: (str(item["relation_type"]), str(item["id"])))
            maximum = max((_finite_strength(item.get("normalized_strength", 0.0)) for item in details), default=0.0)
            value_row.append(maximum)
            cell_row.append(
                {
                    "source": source,
                    "target": target,
                    "relation_types": sorted({str(item["relation_type"]) for item in details}),
                    "raw_edges": [
                        {
                            "id": item["id"],
                            "relation_type": item["relation_type"],
                            "raw_value": item["raw_value"],
                            "unit": item["unit"],
                            "evidence_status": item["evidence_status"],
                            "formula": item["formula"],
                        }
                        for item in details
                    ],
                    "max_normalized_strength": maximum,
                }
            )
        values.append(value_row)
        cells.append(cell_row)
    return {
        "node_order": node_order,
        "values": values,
        "cells": cells,
        "metric": "MAX_ACTIVE_NORMALIZED_TRANSMISSION_STRENGTH",
        "aggregation_policy": COLLAPSE_POLICY,
    }


def add_edges(graph: MultiGraph, edges: list[GraphEdge]) -> None:
    for edge in edges:
        graph.add_edge(edge.source, edge.target, key=edge.id, **edge.to_dict())


def _finite_strength(value: Any) -> float:
    number = float(value)
    if not math.isfinite(number):
        return 0.0
    return min(1.0, max(0.0, number))
