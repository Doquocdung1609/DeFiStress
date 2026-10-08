import type { ContagionEdge, ContagionFrame, ContagionGraph, ContagionNode } from "./api";

export type RelationFilter = "ALL" | "EXPOSURE" | "LIQUIDATION" | "PRICE_IMPACT" | "FEEDBACK";

export function graphBadge(graph: ContagionGraph): { label: string; tone: string } {
  if (graph.evidence_mode === "REAL_MAINNET") return { label: "REAL MAINNET EVIDENCE", tone: "real" };
  if (graph.evidence_mode === "CACHED_MAINNET") return { label: "CACHED MAINNET EVIDENCE", tone: "cached" };
  return { label: "FIXTURE / SYNTHETIC", tone: "fixture" };
}

export function visibleNodes(nodes: ContagionNode[], showAgents: boolean): ContagionNode[] {
  return showAgents ? nodes : nodes.filter((node) => node.layer !== "AGENT_ROLE");
}

export function visibleEdges(
  edges: ContagionEdge[],
  nodeIds: Set<string>,
  relation: RelationFilter,
): ContagionEdge[] {
  return edges.filter((edge) => {
    const nodesVisible = nodeIds.has(edge.source) && nodeIds.has(edge.target);
    const relationVisible = relation === "ALL" || edge.layer === relation;
    return nodesVisible && relationVisible;
  });
}

export function frameNarrative(frame: ContagionFrame): string {
  if (frame.wave === 0) return "Initial snapshot topology before any modeled liquidation event.";
  const impact = frameImpactRatio(frame);
  const nextWave = frame.cascade_depth_so_far > frame.wave ? " A later wave followed." : "";
  return `${frame.label}: ${formatUsd(frame.liquidation_volume_usd)} liquidated, ${frame.forced_weth.toFixed(4)} WETH forced through the selected pool, ${(impact * 100).toFixed(2)}% execution-price impact.${nextWave}`;
}

export function frameImpactRatio(frame: ContagionFrame): number {
  const impactEdge = frame.active_edges.find((edge) => edge.relation_type === "EXECUTION_PRICE_IMPACT");
  const eventDerivedImpact = impactEdge?.raw_value.price_impact_ratio;
  if (typeof eventDerivedImpact === "number" && Number.isFinite(eventDerivedImpact)) return eventDerivedImpact;
  const before = frame.price_state.dex_price_before ?? 0;
  const after = frame.price_state.dex_price_after ?? before;
  return before > 0 ? Math.abs(after - before) / before : 0;
}

export function playbackNarrative(frame: ContagionFrame, totalFrames: number): string {
  const narrative = frameNarrative(frame);
  return totalFrames === 2 && frame.wave === 1
    ? `${narrative} No second-wave liquidation occurred.`
    : narrative;
}

export function scientificMetricSignature(graph: ContagionGraph): string {
  return JSON.stringify({
    edges: graph.edges.map((edge) => [edge.id, edge.raw_value, edge.normalized_strength]),
    matrix: graph.contagion_matrix.values,
    centrality: graph.centrality,
  });
}

export function formatUsd(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}
