export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Snapshot = {
  id: string;
  mode: "FIXTURE" | "REAL_MAINNET" | "CACHED_MAINNET";
  label: string;
  block_number: number;
  block_hash: string;
  block_timestamp: string;
  aave_market: string;
  oracle_prices: { WETH: number; USDC: number };
  stablecoin_state: { symbol: string; price: number; depeg_bps: number };
  coverage: Record<string, number | string>;
  dex_pool: Record<string, unknown>;
  data_quality_flags: { code: string; severity: string; message: string }[];
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
};

export type TerraEarlyWarning = {
  mode: "RETROSPECTIVE" | "CUTOFF_SAFE";
  interpretation: string;
  weights: Record<string, number>;
  event_markers: Record<string, string | null>;
  lead_times: Record<string, Record<string, { lead_time_hours: number | null; wording: string }>>;
  leakage_audit: { status: string; checked_timestamps: number; violations: number };
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
  scenario: Record<string, number>;
  runs: number;
  summary: {
    collapse_count: number;
    noncollapse_count: number;
    wording: string;
    minimum_ust: Record<string, number>;
    final_luna_supply: Record<string, number>;
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
    throw new Error(payload.detail ?? `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
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
