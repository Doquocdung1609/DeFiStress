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
