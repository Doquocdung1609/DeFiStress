export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Snapshot = {
  id: string;
  mode: "FIXTURE" | "REAL_MAINNET" | "CACHED_MAINNET";
  label: string;
  chain_id: number;
  block_number: number;
  block_hash: string;
  block_timestamp: string;
  retrieved_at: string;
  aave_market: string;
  oracle_prices: { WETH: number; USDC: number };
  stablecoin_state: { symbol: string; price: number; depeg_bps: number };
  coverage: Record<string, number | string>;
  dex_pool: Record<string, unknown>;
  data_quality_flags: { code: string; severity: string; message: string }[];
  source_manifest: {
    snapshot_coordination?: {
      graph_head?: number;
      snapshot_block?: number;
    };
    borrower_discovery?: {
      source?: string;
      block_number?: number;
      candidate_count?: number;
    };
    state_verification?: {
      source?: string;
      block_number?: number;
      aave_method?: string;
    };
    uniswap?: {
      pool?: string;
      fee?: number;
    };
    aave?: {
      market?: string;
      pool?: string;
      oracle?: string;
      data_provider?: string;
      address_book_version?: string;
      address_book_commit?: string;
    };
  };
};

export type SnapshotSummary = Pick<
  Snapshot,
  "id" | "mode" | "label" | "chain_id" | "block_number" | "block_hash" | "block_timestamp" | "retrieved_at"
> & {
  coverage: Record<string, number | string | null>;
  selected_uniswap_pool: { pool_address?: string; fee?: number };
  quality_flag_count: number;
};

export type HealthStatus = {
  safety_banner: string;
  mode: string;
  app_mode_role: string;
  selection_policy: string;
  ethereum_rpc: {
    connected: boolean;
    current_block: number | null;
    finalized_block: number | null;
    block_lag: number | null;
    error: string | null;
  };
  eth_rpc_connected: boolean;
  aave_rpc_ready: boolean;
  uniswap_rpc_ready: boolean;
  subgraph_configured: boolean;
  aave: string;
  uniswap: string;
  subgraph: string;
  can_create_real_snapshot: boolean;
  mainnet_artifact: {
    available: boolean;
    loaded: boolean;
    snapshot_id: string | null;
    block_number?: number;
  };
};

export type Position = {
  borrower_hash: string;
  health_factor: number;
  collateral_weth: number;
  debt_usdc: number;
  total_debt: number;
  liquidation_price: number;
  distance_to_liquidation: number | null;
  debt_share: number;
};

export type Run = {
  id: string;
  seed: number;
  status: "PENDING" | "RUNNING" | "COMPLETE" | "FAILED";
  progress_percent: number;
  model_version: string;
  result?: {
    scenario?: Record<string, number | string | null>;
    metrics: Record<string, number | null>;
    events: Array<Record<string, number | string | null | Record<string, unknown>>>;
    timeseries: Array<Record<string, number>>;
    monte_carlo?: { summary: Record<string, unknown>; distributions: Record<string, number[]> };
  };
  error?: string;
};

export type ContagionNode = {
  id: string;
  label: string;
  layer: "PROTOCOL" | "ASSET" | "AGENT_ROLE" | "REFERENCE_MARKET";
  node_type: string;
  evidence_status: string;
  snapshot_id: string;
  description: string;
  raw_metrics: Record<string, number | string | boolean | null>;
  provenance: Record<string, unknown>;
};

export type ContagionEdge = {
  id: string;
  source: string;
  target: string;
  relation_type: string;
  layer: string;
  direction: string;
  raw_value: Record<string, number | string | boolean | null>;
  unit: string;
  normalized_strength: number;
  evidence_status: string;
  provenance: Record<string, unknown>;
  description: string;
  formula: string;
  active: boolean;
  step: number | null;
  wave: number | null;
};

export type ContagionFrame = {
  index: number;
  label: string;
  step: number;
  wave: number;
  active_nodes: string[];
  active_edge_ids: string[];
  active_edges: ContagionEdge[];
  price_state: Record<string, number | null>;
  liquidation_volume_usd: number;
  forced_weth: number;
  liquidation_event_count: number;
  cumulative_liquidated_debt_usd: number;
  cascade_depth_so_far: number;
};

export type ContagionGraph = {
  graph_model_version: string;
  graph_type: string;
  mode: "STRUCTURAL" | "RUN_WEIGHTED" | "AGGREGATE_SIMULATION_SUMMARY";
  evidence_mode: Snapshot["mode"];
  snapshot_id: string;
  run_id: string | null;
  nodes: ContagionNode[];
  edges: ContagionEdge[];
  frames: ContagionFrame[];
  contagion_matrix: {
    metric: string;
    aggregation_policy: string;
    node_order: string[];
    values: number[][];
    cells: Array<Array<{
      source: string;
      target: string;
      max_normalized_strength: number;
      relation_types: string[];
      raw_edges: ContagionEdge[];
    }>>;
  };
  centrality: {
    structural_bridge_node: string | null;
    aggregation_policy: string;
    weighted_influence_interpretation: string;
    eigenvector_unavailable_reason: string | null;
    nodes: Record<string, Record<string, number | null>>;
  };
  graph_metadata: Record<string, unknown>;
  provenance: Record<string, unknown>;
  claim_boundaries: string[];
};

export type TerraManifest = {
  dataset_version: string;
  status: "REAL_HISTORICAL" | "FIXTURE" | "PARTIAL" | "UNAVAILABLE" | "QUALITY_WARNING";
  row_count: number;
  start_timestamp: string;
  end_timestamp: string;
  dataset_hash: string;
  source_manifest: Record<string, unknown>;
  quality_report: Record<string, unknown>;
  transformation_version: string;
  git_commit: string;
};

export type TerraObservation = {
  timestamp: string;
  block_height: number;
  ust_price: number;
  luna_price: number;
  ust_supply: number;
  luna_supply: number;
  anchor_total_deposits: number;
  anchor_withdrawal_flow: number;
  ust_native_redemption_volume: number;
  terra_dex_liquidity: number;
  backing_ratio: number;
  ust_depeg_bps: number;
  top10_anchor_share: number;
  top100_anchor_share: number;
};

export type TerraReplay = {
  id: string;
  status: string;
  metadata: Record<string, unknown> & {
    cutoff_timestamp: string;
    evaluation_start: string;
    evaluation_end: string;
    mode: string;
    leakage_check_status: { status: string; checked_rows: number };
  };
  dataset: TerraManifest;
  model: { name: string; version: string; status: string; diagnostics: Record<string, unknown> };
  simulated_timeseries: Array<Record<string, number | string | boolean>>;
  ground_truth_timeseries: TerraObservation[];
  validation_metrics: Record<string, number | boolean | null>;
  validation_warnings: string[];
  agent_events: Array<Record<string, unknown>>;
  early_warning: {
    score: number;
    contributions: Record<string, number>;
    calibration_policy: string;
    label: string;
  };
  evidence_warning?: string | null;
};

export type TerraBenchmark = {
  id: string;
  status: string;
  benchmark_results: Array<Record<string, number | string | boolean | null>>;
  interpretation: string;
  dataset_status: string;
};

export type TerraExtendedObservation = {
  timestamp: string;
  block_height: number;
  ust_price: number;
  luna_price: number;
  ust_supply: number;
  luna_supply: number | null;
  anchor_total_deposits: number;
  anchor_deposit_flow: number | null;
  anchor_withdrawal_flow: number | null;
  ust_native_redemption_volume: number | null;
  gross_luna_issuance_from_native_swaps: number | null;
  backing_ratio: number | null;
  top10_anchor_share: number | null;
  top100_anchor_share: number | null;
};

export type TerraHistoricalFit = {
  label: string;
  model_family: string;
  objective: { formula: string; value: number; component_losses: Record<string, number> };
  parameters: Record<string, number>;
  bounds: Record<string, [number, number]>;
  metrics: {
    ust_price: Record<string, number>;
    luna_price: Record<string, number>;
    luna_supply: Record<string, number>;
    event_timing: Record<string, { actual: string | null; simulated: string | null; error_hours: number | null }>;
  };
  actual_timeseries: Array<Record<string, number | string>>;
  simulated_timeseries: Array<Record<string, number | string>>;
  input_policy: Record<string, string | string[]>;
  evaluation_windows: Record<string, { start: string | null; end: string | null; rows: number; mask_rule: string }>;
};

export type TerraEarlyWarning = {
  mode: "RETROSPECTIVE" | "CUTOFF_SAFE";
  interpretation: string;
  weights: Record<string, number>;
  event_markers: Record<string, string | null>;
  lead_times: Record<string, Record<string, { lead_time_hours: number | null; wording: string }>>;
  leakage_audit: {
    status: string;
    checked_timestamps: number;
    violations: number;
    future_perturbation: { status: string; cutoffs_tested: number; violations: number };
  };
  timeline: Array<{
    timestamp: string;
    risk_score: number;
    risk_band: string;
    active_features: string[];
    unavailable_features: string[];
    normalized_active_weights: Record<string, number>;
    components: Record<string, number>;
  }>;
};

export type TerraStressResult = {
  initial_state_timestamp: string;
  initial_state_source: string;
  initial_state: Record<string, number | string | null>;
  preset_definitions: Record<string, Record<string, number>>;
  frozen_parameter_mapping: Record<string, unknown>;
  counterfactual_conversion: {
    name: string;
    claim_boundary: string;
    formula: string;
    validation_metrics: Record<string, number>;
  };
  scenario: Record<string, number>;
  runs: number;
  summary: {
    collapse_count: number;
    noncollapse_count: number;
    probability_estimate: false;
    wording: string;
    minimum_ust: Record<string, number>;
    minimum_luna: Record<string, number>;
    final_luna_supply: Record<string, number>;
    max_withdrawal_stress: Record<string, number>;
  };
  fan_chart: Array<{
    hour: number;
    ust_price: { p05: number; median: number; p95: number };
    luna_price: { p05: number; median: number; p95: number };
    luna_supply: { p05: number; median: number; p95: number };
  }>;
  data_policy: Record<string, string>;
};

export type TerraMechanismCheck = {
  raw_swap_rows: number;
  gross_mint_identity: string;
  old_offchain_approximation: Record<string, number>;
  direct_event_output_gross_mint: Record<string, number>;
  validation_window: {
    start: string;
    end: string;
    aligned_hours: number;
    supply_delta_definition: string;
    event_aggregation: string;
  };
  interpretation: string;
  limitations: string[];
};

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const request = () => fetch(`${API_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
      cache: "no-store",
    });
  let response: Response;
  try {
    response = await request();
  } catch (error) {
    const isRead = !init?.method || init.method.toUpperCase() === "GET";
    if (!isRead || !(error instanceof TypeError)) throw error;
    await new Promise((resolve) => setTimeout(resolve, 150));
    response = await request();
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(apiErrorMessage(payload, response.status));
  }
  return response.json() as Promise<T>;
}

export function apiErrorMessage(payload: unknown, status: number): string {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = payload.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((entry: unknown) => {
        if (!entry || typeof entry !== "object") return "Invalid input";
        const item = entry as { loc?: unknown; msg?: unknown };
        const location = Array.isArray(item.loc) ? item.loc.slice(1).join(".") : "Input";
        return `${location}: ${typeof item.msg === "string" ? item.msg : "Invalid value"}`;
      }).join("; ");
    }
  }
  return `Request failed with status ${status}`;
}

export function money(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return "—";
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

export function percent(value: number | null | undefined, inputIsRatio = true): string {
  if (value == null || !Number.isFinite(value)) return "—";
  const amount = inputIsRatio ? value * 100 : value;
  return `${amount.toFixed(2)}%`;
}
