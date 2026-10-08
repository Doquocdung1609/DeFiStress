import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import type { ContagionEdge, ContagionGraph, ContagionNode } from "./api";
import {
  frameNarrative,
  graphBadge,
  playbackNarrative,
  scientificMetricSignature,
  visibleEdges,
  visibleNodes,
} from "./contagion";

const protocolNode: ContagionNode = {
  id: "protocol:aave-v3",
  label: "Aave V3",
  layer: "PROTOCOL",
  node_type: "LENDING_PROTOCOL",
  evidence_status: "OBSERVED_ONCHAIN",
  snapshot_id: "real-test",
  description: "test",
  raw_metrics: {},
  provenance: {},
};

const agentNode: ContagionNode = {
  ...protocolNode,
  id: "agent:liquidator",
  label: "Liquidator",
  layer: "AGENT_ROLE",
  evidence_status: "SCENARIO_ASSUMPTION",
};

const liquidationEdge: ContagionEdge = {
  id: "run:wave-1:liquidation",
  source: "agent:liquidator",
  target: "protocol:aave-v3",
  relation_type: "LIQUIDATION_EXECUTION",
  layer: "LIQUIDATION",
  direction: "DIRECTED",
  raw_value: { debt_repaid_usd: 100 },
  unit: "USD",
  normalized_strength: 0.4,
  evidence_status: "SIMULATED_OUTPUT",
  provenance: {},
  description: "test",
  formula: "test",
  active: true,
  step: 1,
  wave: 1,
};

function graph(mode: ContagionGraph["evidence_mode"]): ContagionGraph {
  return {
    graph_model_version: "test",
    graph_type: "MULTILAYER_DIRECTED_MULTIGRAPH",
    mode: "RUN_WEIGHTED",
    evidence_mode: mode,
    snapshot_id: "real-test",
    run_id: "run-test",
    nodes: [protocolNode, agentNode],
    edges: [liquidationEdge],
    frames: [{
      index: 1,
      label: "Wave 1",
      step: 1,
      wave: 1,
      active_edge_ids: [liquidationEdge.id],
      active_edges: [liquidationEdge],
      active_nodes: [agentNode.id, protocolNode.id],
      price_state: { reference_price: 2_500, dex_price_before: 2_500, dex_price_after: 2_475 },
      liquidation_volume_usd: 100,
      forced_weth: 0.04,
      liquidation_event_count: 1,
      cumulative_liquidated_debt_usd: 100,
      cascade_depth_so_far: 1,
    }],
    contagion_matrix: {
      metric: "MAX_ACTIVE_NORMALIZED_TRANSMISSION_STRENGTH",
      aggregation_policy: "maximum",
      node_order: [protocolNode.id, agentNode.id],
      values: [[0, 0], [0.4, 0]],
      cells: [
        [
          { source: protocolNode.id, target: protocolNode.id, max_normalized_strength: 0, relation_types: [], raw_edges: [] },
          { source: protocolNode.id, target: agentNode.id, max_normalized_strength: 0, relation_types: [], raw_edges: [] },
        ],
        [
          { source: agentNode.id, target: protocolNode.id, max_normalized_strength: 0.4, relation_types: [liquidationEdge.relation_type], raw_edges: [liquidationEdge] },
          { source: agentNode.id, target: agentNode.id, max_normalized_strength: 0, relation_types: [], raw_edges: [] },
        ],
      ],
    },
    centrality: {
      structural_bridge_node: protocolNode.id,
      aggregation_policy: "maximum",
      weighted_influence_interpretation: "exploratory",
      eigenvector_unavailable_reason: null,
      nodes: { [protocolNode.id]: { betweenness_centrality: 1 } },
    },
    graph_metadata: {},
    provenance: {},
    claim_boundaries: ["not a probability"],
  };
}

describe("contagion graph view helpers", () => {
  it("keeps real and fixture evidence badges explicit", () => {
    expect(graphBadge(graph("REAL_MAINNET")).label).toBe("REAL MAINNET EVIDENCE");
    expect(graphBadge(graph("FIXTURE")).label).toBe("FIXTURE / SYNTHETIC");
  });

  it("hides agent nodes and their edges unless explicitly enabled", () => {
    expect(visibleNodes([protocolNode, agentNode], false)).toEqual([protocolNode]);
    const ids = new Set(visibleNodes([protocolNode, agentNode], false).map((node) => node.id));
    expect(visibleEdges([liquidationEdge], ids, "ALL")).toEqual([]);
    const allIds = new Set([protocolNode.id, agentNode.id]);
    expect(visibleEdges([liquidationEdge], allIds, "LIQUIDATION")).toEqual([liquidationEdge]);
    expect(visibleEdges([liquidationEdge], allIds, "FEEDBACK")).toEqual([]);
  });

  it("describes an event-derived wave without changing scientific metrics", () => {
    const data = graph("REAL_MAINNET");
    const before = scientificMetricSignature(data);
    expect(frameNarrative(data.frames[0])).toContain("$100");
    expect(playbackNarrative(data.frames[0], 2)).toContain("No second-wave liquidation occurred.");
    visibleNodes(data.nodes, false);
    visibleEdges(data.edges, new Set(data.nodes.map((node) => node.id)), "LIQUIDATION");
    expect(scientificMetricSignature(data)).toBe(before);
  });

  it("ships the required playback, matrix, centrality and conceptual-boundary UI", () => {
    const component = readFileSync(resolve(process.cwd(), "app/components/ContagionGraph.tsx"), "utf8");
    expect(component).toContain("Wave frame");
    expect(component).toContain("Contagion Matrix");
    expect(component).toContain("Centrality");
    expect(component).toContain("Show Future Expansion");
    expect(component).toContain("Conceptual extension only");
    expect(component).not.toContain("/health");
  });
});
