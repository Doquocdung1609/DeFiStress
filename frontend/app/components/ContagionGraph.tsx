"use client";

import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";

import type { ContagionEdge, ContagionFrame, ContagionGraph as GraphData, Snapshot } from "@/lib/api";
import { API_URL, api } from "@/lib/api";
import {
  formatUsd,
  graphBadge,
  playbackNarrative,
  type RelationFilter,
  visibleEdges,
  visibleNodes,
} from "@/lib/contagion";

const NODE_COORDINATES: Record<string, [number, number]> = {
  "asset:weth": [250, 80],
  "asset:usdc": [690, 80],
  "market:reference": [875, 230],
  "protocol:aave-v3": [335, 265],
  "protocol:uniswap-v3": [630, 265],
  "agent:borrower-cohort": [160, 475],
  "agent:liquidator": [430, 475],
  "agent:arbitrageur": [710, 475],
};

const RELATION_FILTERS: Array<{ value: RelationFilter; label: string }> = [
  { value: "ALL", label: "All relations" },
  { value: "EXPOSURE", label: "Exposures" },
  { value: "LIQUIDATION", label: "Liquidation" },
  { value: "PRICE_IMPACT", label: "Price impact" },
  { value: "FEEDBACK", label: "Feedback" },
];

type GraphOption = { id: string; label: string; graph: GraphData };

export function ContagionGraph({ snapshot }: { snapshot: Snapshot }) {
  const [options, setOptions] = useState<GraphOption[]>([]);
  const [selectedId, setSelectedId] = useState("snapshot");
  const [frameIndex, setFrameIndex] = useState(0);
  const [relationFilter, setRelationFilter] = useState<RelationFilter>("ALL");
  const [showAgents, setShowAgents] = useState(false);
  const [showFuture, setShowFuture] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [selectedEdge, setSelectedEdge] = useState<ContagionEdge | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function loadGraphs() {
      try {
        setError(null);
        const runIds = readSavedRunIds();
        const [structural, ...runResults] = await Promise.all([
          api<GraphData>(`/api/v1/snapshots/${snapshot.id}/contagion-graph`),
          ...runIds.map(async (runId) => {
            try {
              return await api<GraphData>(`/api/v1/runs/${runId}/contagion-graph`);
            } catch {
              return null;
            }
          }),
        ]);
        if (!active) return;
        const matchingRuns = runResults.filter(
          (graph): graph is GraphData => graph !== null && graph.snapshot_id === snapshot.id,
        );
        const loaded: GraphOption[] = [
          { id: "snapshot", label: "Structural snapshot", graph: structural },
          ...matchingRuns.map((graph) => ({
            id: graph.run_id ?? "unknown-run",
            label: `${graph.mode === "RUN_WEIGHTED" ? "Deterministic run" : "Monte Carlo summary"} · ${(graph.run_id ?? "").slice(0, 8)}`,
            graph,
          })),
        ];
        setOptions(loaded);
        const preferred = loaded.find((option) => option.graph.mode === "RUN_WEIGHTED");
        setSelectedId(preferred?.id ?? "snapshot");
        setFrameIndex(0);
      } catch (cause) {
        if (active) setError(cause instanceof Error ? cause.message : "Contagion graph could not be loaded.");
      }
    }

    void loadGraphs();
    return () => {
      active = false;
    };
  }, [snapshot.id]);

  const graph = options.find((option) => option.id === selectedId)?.graph ?? options[0]?.graph;
  const frames = graph?.frames ?? [];
  const frame = frames[Math.min(frameIndex, Math.max(frames.length - 1, 0))];

  useEffect(() => {
    if (!playing || frames.length < 2) return;
    const timer = window.setInterval(() => {
      setFrameIndex((current) => {
        if (current >= frames.length - 1) {
          setPlaying(false);
          return current;
        }
        return current + 1;
      });
    }, 1400);
    return () => window.clearInterval(timer);
  }, [frames.length, playing]);

  const rendered = useMemo(() => {
    if (!graph) return { nodes: [], edges: [] };
    const nodes = visibleNodes(graph.nodes, showAgents);
    const nodeIds = new Set(nodes.map((node) => node.id));
    const activeDynamicIds = new Set(frame?.active_edge_ids ?? []);
    const edgesForFrame = graph.edges.filter(
      (edge) => edge.wave == null || activeDynamicIds.has(edge.id),
    );
    return {
      nodes,
      edges: visibleEdges(edgesForFrame, nodeIds, relationFilter),
    };
  }, [frame?.active_edge_ids, graph, relationFilter, showAgents]);

  if (error) {
    return <div className="errorBanner"><strong>Contagion graph unavailable.</strong> {error}</div>;
  }
  if (!graph || !frame) return <div className="loading"><span />Loading evidence-backed network…</div>;

  const badge = graphBadge(graph);
  const bridgeLabel = graph.nodes.find((node) => node.id === graph.centrality.structural_bridge_node)?.label ?? "Unavailable";
  const dynamicEdges = graph.edges.filter((edge) => edge.wave != null);
  const totalLiquidated = graph.frames.reduce((sum, item) => sum + item.liquidation_volume_usd, 0);
  const currentImpact = framePriceImpact(frame);

  return (
    <div className="contagionPage">
      <div className="sectionLead">
        <div>
          <p className="eyebrow">MULTILAYER DIRECTED MULTIGRAPH</p>
          <h2>Evidence-backed contagion pathways</h2>
          <p>Derived from immutable snapshots and saved simulation events. This graph does not run a second simulator.</p>
        </div>
        <span className={`modeBadge ${badge.tone}`}>{badge.label}</span>
      </div>

      <div className="networkEvidenceBanner">
        <strong>{graph.evidence_mode === "FIXTURE" ? "FIXTURE NETWORK" : "REAL MAINNET CONTAGION NETWORK"} · {graph.mode.replaceAll("_", " ")}</strong>
        <span>Snapshot {graph.snapshot_id} · Block {Number(graph.provenance.block_number).toLocaleString()}</span>
        <span>Graph model {graph.graph_model_version}</span>
      </div>

      <div className="networkKpis">
        <NetworkKpi label="Active protocols" value="2" detail="Aave V3 + Uniswap V3" />
        <NetworkKpi label="Edges in evidence" value={String(graph.edges.length)} detail={`${dynamicEdges.length} run-weighted`} />
        <NetworkKpi label="Cascade depth" value={String(graph.graph_metadata.cascade_depth ?? 0)} detail="saved run metric" />
        <NetworkKpi label="Structural bridge" value={bridgeLabel} detail="deterministic betweenness rule" />
        <NetworkKpi label="Current frame" value={frame.label} detail={`${frame.liquidation_event_count} liquidation events`} />
        <NetworkKpi label="Wave debt" value={formatUsd(frame.liquidation_volume_usd)} detail={`${formatUsd(totalLiquidated)} total`} />
        <NetworkKpi label="Forced WETH" value={frame.forced_weth.toFixed(4)} detail="event-derived volume" />
        <NetworkKpi label="DEX impact" value={`${(currentImpact * 100).toFixed(2)}%`} detail="first/last wave prices" />
      </div>

      <section className="networkPanel" aria-label="Contagion network visualization">
        <div className="networkToolbar">
          <label>
            Evidence view
            <select
              value={selectedId}
              onChange={(event) => {
                setSelectedId(event.target.value);
                setFrameIndex(0);
                setPlaying(false);
                setSelectedEdge(null);
              }}
            >
              {options.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
            </select>
          </label>
          <label>
            Relation filter
            <select value={relationFilter} onChange={(event) => setRelationFilter(event.target.value as RelationFilter)}>
              {RELATION_FILTERS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
          <label className="toggleControl">
            <input type="checkbox" checked={showAgents} onChange={(event) => setShowAgents(event.target.checked)} />
            Agent roles
          </label>
          <label className="toggleControl">
            <input type="checkbox" checked={showFuture} onChange={(event) => setShowFuture(event.target.checked)} />
            Show Future Expansion
          </label>
        </div>

        {showFuture ? (
          <div className="conceptualBanner"><strong>Conceptual extension only.</strong> Compound, Maker and Curve are not ingested, scored, or included in any metric.</div>
        ) : null}

        <div className="networkCanvas">
          <svg viewBox="0 0 980 590" role="img" aria-labelledby="network-title network-description">
            <title id="network-title">Aave and Uniswap contagion multigraph</title>
            <desc id="network-description">Directed evidence pathways connecting protocols, assets, and optional agent roles.</desc>
            <defs>
              <marker id="network-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" />
              </marker>
            </defs>
            {rendered.edges.map((edge, index) => (
              <GraphEdgePath
                edge={edge}
                index={index}
                key={edge.id}
                selected={selectedEdge?.id === edge.id}
                onSelect={setSelectedEdge}
              />
            ))}
            {rendered.nodes.map((node) => {
              const [x, y] = NODE_COORDINATES[node.id] ?? [490, 295];
              return (
                <g className={`networkNode ${node.layer.toLowerCase()}`} key={node.id} transform={`translate(${x} ${y})`}>
                  <rect x="-86" y="-39" width="172" height="78" rx="10" />
                  <text className="nodeLabel" textAnchor="middle" y="-16">{node.label}</text>
                  <text className="nodeType" textAnchor="middle" y="0">{node.node_type.replaceAll("_", " ")}</text>
                  <text className="nodeMetric" textAnchor="middle" y="15">{nodeMetric(node.id, node.raw_metrics)}</text>
                  <text className="nodeEvidence" textAnchor="middle" y="29">{node.evidence_status.replaceAll("_", " ")}</text>
                </g>
              );
            })}
            {showFuture ? <FutureNodes /> : null}
          </svg>
        </div>

        <Playback frame={frame} frames={frames} frameIndex={frameIndex} playing={playing} onFrame={setFrameIndex} onPlay={setPlaying} />
      </section>

      {selectedEdge ? <EdgeEvidence edge={selectedEdge} onClose={() => setSelectedEdge(null)} /> : null}

      <div className="twoCol networkAnalysis">
        <ContagionMatrix graph={graph} />
        <CentralityPanel graph={graph} />
      </div>

      <section className="networkPanel claimBoundary">
        <div className="panelHeading"><div><p className="eyebrow">SCIENTIFIC BOUNDARY</p><h3>What this graph does and does not claim</h3></div></div>
        <ul className="claimList">{graph.claim_boundaries.map((claim) => <li key={claim}>{claim}</li>)}</ul>
        <div className="exportLinks">
          <a href={`${API_URL}/api/v1/snapshots/${graph.snapshot_id}/contagion-graph`} target="_blank" rel="noreferrer">Graph JSON</a>
          {graph.run_id ? <a href={`${API_URL}/api/v1/runs/${graph.run_id}/export`}>Run export: graph JSON + matrix CSV + centrality JSON</a> : null}
        </div>
      </section>
    </div>
  );
}

function GraphEdgePath({
  edge,
  index,
  selected,
  onSelect,
}: {
  edge: ContagionEdge;
  index: number;
  selected: boolean;
  onSelect: (edge: ContagionEdge) => void;
}) {
  const source = NODE_COORDINATES[edge.source];
  const target = NODE_COORDINATES[edge.target];
  if (!source || !target) return null;
  const [sx, sy] = source;
  const [tx, ty] = target;
  const parallelOffset = edge.id.includes("revaluation-channel") ? 28 : index % 2 === 0 ? 0 : 8;
  const midpointX = (sx + tx) / 2 + (sy - ty) * 0.08;
  const midpointY = (sy + ty) / 2 + (tx - sx) * 0.04 + parallelOffset;
  const style = { "--edge-strength": Math.max(edge.normalized_strength, 0.08) } as CSSProperties;
  return (
    <g
      className={`networkEdge ${edge.layer.toLowerCase()} ${edge.evidence_status.toLowerCase()} ${selected ? "selected" : ""} ${edge.active ? "active" : "inactive"}`}
      role="button"
      tabIndex={0}
      aria-label={`${edge.relation_type} from ${edge.source} to ${edge.target}`}
      onClick={() => onSelect(edge)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") onSelect(edge);
      }}
      style={style}
    >
      <path d={`M ${sx} ${sy} Q ${midpointX} ${midpointY} ${tx} ${ty}`} markerEnd="url(#network-arrow)" />
      <text className="edgeLabel" textAnchor="middle" x={midpointX} y={midpointY - 5}>{shortRelation(edge.relation_type)}</text>
      <text className="edgeValue" textAnchor="middle" x={midpointX} y={midpointY + 8}>{edgeMetric(edge)}</text>
      <title>{edge.relation_type}: {edge.description}</title>
    </g>
  );
}

function FutureNodes() {
  return (
    <g className="futureNodes" aria-label="Conceptual nodes excluded from metrics">
      {["Compound", "Maker", "Curve"].map((label, index) => (
        <g key={label} transform={`translate(${805 + index * 75} ${420 + index * 55})`}>
          <rect x="-52" y="-23" width="104" height="46" rx="8" />
          <text textAnchor="middle" y="-2">{label}</text>
          <text className="nodeEvidence" textAnchor="middle" y="13">NOT INGESTED</text>
        </g>
      ))}
    </g>
  );
}

function Playback({
  frame,
  frames,
  frameIndex,
  playing,
  onFrame,
  onPlay,
}: {
  frame: ContagionFrame;
  frames: ContagionFrame[];
  frameIndex: number;
  playing: boolean;
  onFrame: (index: number) => void;
  onPlay: (value: boolean) => void;
}) {
  return (
    <div className="playbackControls">
      <div className="playbackButtons">
        <button type="button" onClick={() => { onPlay(false); onFrame(Math.max(0, frameIndex - 1)); }} disabled={frameIndex === 0}>Previous</button>
        <button type="button" onClick={() => onPlay(!playing)} disabled={frames.length < 2}>{playing ? "Pause" : "Play"}</button>
        <button type="button" onClick={() => { onPlay(false); onFrame(Math.min(frames.length - 1, frameIndex + 1)); }} disabled={frameIndex >= frames.length - 1}>Next</button>
        <button type="button" onClick={() => { onPlay(false); onFrame(0); }} disabled={frameIndex === 0}>Reset</button>
      </div>
      <label>
        Wave frame {frameIndex} / {frames.length - 1}
        <input type="range" min="0" max={Math.max(frames.length - 1, 0)} value={frameIndex} onChange={(event) => { onPlay(false); onFrame(Number(event.target.value)); }} />
      </label>
      <div className="pathNarrative">
        <strong>{frame.label}</strong>
        <span>{playbackNarrative(frame, frames.length)}</span>
      </div>
    </div>
  );
}

function EdgeEvidence({ edge, onClose }: { edge: ContagionEdge; onClose: () => void }) {
  return (
    <section className="networkPanel edgeEvidence">
      <div className="panelHeading">
        <div><p className="eyebrow">EDGE EVIDENCE</p><h3>{edge.relation_type.replaceAll("_", " ")}</h3></div>
        <button type="button" onClick={onClose}>Close</button>
      </div>
      <p>{edge.description}</p>
      <dl className="definition">
        <div><dt>Direction</dt><dd>{edge.source} → {edge.target}</dd></div>
        <div><dt>Evidence</dt><dd>{edge.evidence_status}</dd></div>
        <div><dt>Normalized score</dt><dd>{edge.normalized_strength.toFixed(6)} (bounded score, not probability)</dd></div>
        <div><dt>Raw value</dt><dd>{JSON.stringify(edge.raw_value)}</dd></div>
        <div><dt>Formula</dt><dd>{edge.formula}</dd></div>
      </dl>
    </section>
  );
}

function ContagionMatrix({ graph }: { graph: GraphData }) {
  const matrix = graph.contagion_matrix;
  return (
    <section className="networkPanel">
      <div className="panelHeading"><div><p className="eyebrow">SOURCE → TARGET</p><h3>Contagion Matrix</h3></div></div>
      <p className="networkNote">Scores are normalized transmission indicators, not probabilities. {matrix.aggregation_policy}</p>
      <div className="matrixWrap">
        <table className="networkMatrix">
          <thead><tr><th>Source \ Target</th>{matrix.node_order.map((id) => <th key={id}>{shortNode(id)}</th>)}</tr></thead>
          <tbody>
            {matrix.node_order.map((source, row) => (
              <tr key={source}>
                <th>{shortNode(source)}</th>
                {matrix.values[row].map((value, column) => {
                  const cell = matrix.cells[row][column];
                  const style = { "--cell-strength": value } as CSSProperties;
                  const evidence = cell.raw_edges.map((edge) => `${edge.relation_type}: ${JSON.stringify(edge.raw_value)} [${edge.evidence_status}] ${edge.formula}`).join(" | ");
                  return <td key={`${source}-${matrix.node_order[column]}`} className={value > 0 ? "hasValue" : ""} style={style} title={evidence}>{value ? value.toFixed(2) : "·"}</td>;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function CentralityPanel({ graph }: { graph: GraphData }) {
  return (
    <section className="networkPanel">
      <div className="panelHeading"><div><p className="eyebrow">DETERMINISTIC ANALYSIS</p><h3>Centrality</h3></div></div>
      <p className="bridgeRow">Structural bridge: <strong>{graph.centrality.structural_bridge_node ?? "Unavailable"}</strong></p>
      <div className="tableWrap">
        <table>
          <thead><tr><th>Node</th><th>In</th><th>Out</th><th>Betweenness</th><th>Eigenvector</th><th>Influence</th></tr></thead>
          <tbody>
            {Object.entries(graph.centrality.nodes).map(([id, values]) => (
              <tr key={id}>
                <td>{shortNode(id)}</td>
                <td>{formatMetric(values.in_degree_centrality)}</td>
                <td>{formatMetric(values.out_degree_centrality)}</td>
                <td>{formatMetric(values.betweenness_centrality)}</td>
                <td>{formatMetric(values.eigenvector_centrality)}</td>
                <td>{formatMetric(values.weighted_influence_strength)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="networkNote">Centrality measures position inside this modeled sub-network. It does not measure total importance across all DeFi. {graph.centrality.aggregation_policy}</p>
      {graph.centrality.eigenvector_unavailable_reason ? <p className="networkNote">{graph.centrality.eigenvector_unavailable_reason}</p> : null}
    </section>
  );
}

function NetworkKpi({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <article><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

function readSavedRunIds(): string[] {
  try {
    const value = JSON.parse(window.localStorage.getItem("defi-run-ids") ?? "[]") as unknown;
    return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string").slice(0, 12) : [];
  } catch {
    return [];
  }
}

function shortNode(id: string): string {
  return id.split(":").at(-1)?.replaceAll("-", " ") ?? id;
}

function formatMetric(value: number | null | undefined): string {
  return value == null || !Number.isFinite(value) ? "—" : value.toFixed(3);
}

function framePriceImpact(frame: ContagionFrame): number {
  const before = frame.price_state.dex_price_before ?? 0;
  const after = frame.price_state.dex_price_after ?? before;
  return before > 0 ? Math.abs(after - before) / before : 0;
}

function nodeMetric(nodeId: string, metrics: Record<string, number | string | boolean | null>): string {
  if (nodeId === "asset:weth") return shortMoney(Number(metrics.oracle_price_usd ?? 0));
  if (nodeId === "asset:usdc") return `${shortMoney(Number(metrics.modeled_debt_usdc ?? 0))} debt`;
  if (nodeId === "protocol:aave-v3") return `${Number(metrics.weth_usdc_cohort ?? 0).toLocaleString()} cohort positions`;
  if (nodeId === "protocol:uniswap-v3") return `2% depth ${shortMoney(Number(metrics.depth_usdc_2pct ?? 0))}`;
  if (nodeId === "agent:borrower-cohort") return `${Number(metrics.active_borrowers ?? 0).toLocaleString()} borrowers`;
  return nodeId === "market:reference" ? "exogenous price path" : "scenario-controlled role";
}

function edgeMetric(edge: ContagionEdge): string {
  const raw = edge.raw_value;
  if ("execution_value_usd" in raw) return shortMoney(Number(raw.execution_value_usd));
  if ("price_impact_ratio" in raw) return `${(Number(raw.price_impact_ratio) * 100).toFixed(2)}%`;
  if ("model_attributed_liquidated_debt_usd" in raw) return shortMoney(Number(raw.model_attributed_liquidated_debt_usd));
  if ("weth_collateral_usd" in raw) return shortMoney(Number(raw.weth_collateral_usd));
  if ("usdc_debt_usd" in raw) return shortMoney(Number(raw.usdc_debt_usd));
  if ("sampled_debt_usd" in raw) return `${Number(raw.active_borrowers ?? 0).toLocaleString()} positions`;
  if ("executable_depth_usdc_2pct" in raw) return `depth ${shortMoney(Number(raw.executable_depth_usdc_2pct))}`;
  if ("debt_repaid_usd" in raw) return shortMoney(Number(raw.debt_repaid_usd));
  if ("recovery_ratio" in raw) return `${(Number(raw.recovery_ratio) * 100).toFixed(1)}% recovered`;
  return edge.active ? edge.normalized_strength.toFixed(2) : "inactive";
}

function shortRelation(relation: string): string {
  return relation.replaceAll("_", " ").toLowerCase();
}

function shortMoney(value: number): string {
  if (!Number.isFinite(value)) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}
