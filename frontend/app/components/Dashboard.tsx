"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { API_URL, Position, Run, Snapshot, api, money, percent } from "@/lib/api";

const nav = [
  ["overview", "Overview"],
  ["positions", "Positions"],
  ["liquidity", "Liquidity"],
  ["scenarios", "Scenarios"],
  ["simulator", "Simulator"],
  ["compare", "Compare"],
  ["validation", "Validation"],
  ["provenance", "Provenance"],
] as const;

type Health = {
  safety_banner: string;
  ethereum_rpc: { connected: boolean; current_block: number | null; finalized_block: number | null; block_lag: number | null; error: string | null };
  aave: string;
  uniswap: string;
  subgraph: string;
};

type Liquidity = {
  pool: Record<string, unknown>;
  pools: Array<Record<string, unknown>>;
  spot_price: number;
  depth_usdc: Record<string, number>;
  quality_flags: Snapshot["data_quality_flags"];
};

type ScenarioForm = {
  name: string;
  shock_pct: number;
  liquidity_haircut_pct: number;
  gas_multiplier: number;
  liquidator_capital_usdc: number;
  arbitrage_capacity_pct: number;
  liquidator_capacity_usdc: number;
  liquidator_delay_steps: number;
  liquidator_min_profit_usdc: number;
  arbitrage_delay_steps: number;
  horizon_steps: number;
  timestep_seconds: number;
  monte_carlo_runs: number;
  seed: number;
  volatility_pct: number;
  liquidation_threshold_override: number;
  liquidation_bonus_override: number;
  max_waves: number;
};

type ScenarioNumericKey = Exclude<keyof ScenarioForm, "name">;

const professorPreset: ScenarioForm = {
  name: "Professor Demo",
  shock_pct: -20,
  liquidity_haircut_pct: 40,
  gas_multiplier: 2,
  liquidator_capital_usdc: 10_000_000,
  arbitrage_capacity_pct: 50,
  liquidator_capacity_usdc: 2_500_000,
  liquidator_delay_steps: 0,
  liquidator_min_profit_usdc: 0,
  arbitrage_delay_steps: 0,
  horizon_steps: 12,
  timestep_seconds: 60,
  monte_carlo_runs: 100,
  seed: 20260914,
  volatility_pct: 2,
  liquidation_threshold_override: 0.825,
  liquidation_bonus_override: 1.05,
  max_waves: 12,
};

const scenarioPresets: Record<string, ScenarioForm> = {
  Baseline: { ...professorPreset, name: "Baseline", shock_pct: -10, liquidity_haircut_pct: 0, gas_multiplier: 1, arbitrage_capacity_pct: 100 },
  Moderate: { ...professorPreset, name: "Moderate", shock_pct: -15, liquidity_haircut_pct: 25, gas_multiplier: 1.5, arbitrage_capacity_pct: 75 },
  Severe: { ...professorPreset, name: "Severe", shock_pct: -30, liquidity_haircut_pct: 60, gas_multiplier: 4, arbitrage_capacity_pct: 25 },
  "Low Liquidity": { ...professorPreset, name: "Low Liquidity", liquidity_haircut_pct: 75 },
  "High Gas": { ...professorPreset, name: "High Gas", gas_multiplier: 8 },
  "No Arbitrage": { ...professorPreset, name: "No Arbitrage", arbitrage_capacity_pct: 0 },
  "Strong Arbitrage": { ...professorPreset, name: "Strong Arbitrage", arbitrage_capacity_pct: 100 },
  "Policy Experiment": { ...professorPreset, name: "Policy Experiment", liquidation_threshold_override: 0.8, liquidation_bonus_override: 1.04 },
};

export function Dashboard({ section, runId }: { section: string; runId?: string }) {
  const router = useRouter();
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [liquidity, setLiquidity] = useState<Liquidity | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [scenario, setScenario] = useState<ScenarioForm>(professorPreset);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(true);

  const loadSnapshot = useCallback(async () => {
    try {
      setBusy(true);
      const savedId = window.localStorage.getItem("defi-snapshot-id");
      let selected: Snapshot;
      if (savedId) {
        selected = await api<Snapshot>(`/api/v1/snapshots/${savedId}`).catch(() =>
          api<Snapshot>("/api/v1/snapshots", { method: "POST", body: JSON.stringify({ mode: "FIXTURE" }) }),
        );
      } else {
        selected = await api<Snapshot>("/api/v1/snapshots", {
          method: "POST",
          body: JSON.stringify({ mode: "FIXTURE" }),
        });
      }
      window.localStorage.setItem("defi-snapshot-id", selected.id);
      const [positionData, liquidityData, healthData] = await Promise.all([
        api<{ positions: Position[] }>(`/api/v1/snapshots/${selected.id}/positions`),
        api<Liquidity>(`/api/v1/snapshots/${selected.id}/liquidity`),
        api<Health>("/api/v1/health"),
      ]);
      setSnapshot(selected);
      setPositions(positionData.positions);
      setLiquidity(liquidityData);
      setHealth(healthData);
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The API is unavailable.");
    } finally {
      setBusy(false);
    }
  }, []);

  const loadRun = useCallback(async (id: string) => {
    const current = await api<Run>(`/api/v1/runs/${id}`);
    setRun(current);
    return current;
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => void loadSnapshot(), 0);
    return () => window.clearTimeout(timer);
  }, [loadSnapshot]);

  useEffect(() => {
    if (!runId) return;
    let active = true;
    const poll = async () => {
      try {
        const current = await loadRun(runId);
        if (active && (current.status === "PENDING" || current.status === "RUNNING")) {
          window.setTimeout(poll, 1200);
        }
      } catch (cause) {
        if (active) setError(cause instanceof Error ? cause.message : "Run could not be loaded.");
      }
    };
    void poll();
    return () => {
      active = false;
    };
  }, [loadRun, runId]);

  async function execute(mode: "DETERMINISTIC" | "MONTE_CARLO") {
    if (!snapshot) return;
    try {
      setBusy(true);
      const created = await api<{ id: string }>("/api/v1/scenarios", {
        method: "POST",
        body: JSON.stringify({ snapshot_id: snapshot.id, ...scenario }),
      });
      const started = await api<Run>("/api/v1/runs", {
        method: "POST",
        body: JSON.stringify({ scenario_id: created.id, mode }),
      });
      const ids = JSON.parse(window.localStorage.getItem("defi-run-ids") ?? "[]") as string[];
      window.localStorage.setItem("defi-run-ids", JSON.stringify([started.id, ...ids.filter((id) => id !== started.id)].slice(0, 12)));
      router.push(`/results/${started.id}`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The simulation could not start.");
      setBusy(false);
    }
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brandMark">DS</span>
          <div><strong>DeFiStress</strong><small>LAB / RESEARCH</small></div>
        </div>
        <div className="caseSwitch" aria-label="Case study selector">
          <Link href="/terra/overview">Terra 2022</Link>
          <span className="activeCase">Aave V3</span>
        </div>
        <nav>
          {nav.map(([path, label]) => (
            <Link key={path} href={`/${path}`} className={section === path ? "active" : ""}>
              <span className="navDot" />{label}
            </Link>
          ))}
        </nav>
        <div className="sidebarFoot">
          <span className="statusDot green" /> API {error ? "offline" : "connected"}
          <small>Model 0.1.0</small>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <div>
            <p className="eyebrow">AAVE V3 × UNISWAP V3</p>
            <h1>{title(section)}</h1>
          </div>
          <div className="headerMeta">
            <span className={`modeBadge ${snapshot?.mode === "FIXTURE" ? "fixture" : "real"}`}>
              {snapshot?.mode ?? "LOADING"}
            </span>
            <span className="safety">Research Simulation — Mainnet Read-Only</span>
          </div>
        </header>
        {error && (
          <div className="errorBanner">
            <strong>API unavailable.</strong> {error} Start FastAPI on port 8000 and retry.
            <button onClick={() => void loadSnapshot()}>Retry</button>
          </div>
        )}
        {busy && !snapshot ? <Loading /> : null}
        {snapshot && (
          <section className="content">
            {snapshot.mode === "FIXTURE" && (
              <div className="fixtureBanner"><strong>FIXTURE DATA</strong> Synthetic deterministic cohort for development and tests. It is not Mainnet evidence.</div>
            )}
            {section === "overview" && <Overview snapshot={snapshot} positions={positions} liquidity={liquidity} health={health} />}
            {section === "positions" && <Positions positions={positions} coverage={snapshot.coverage} />}
            {section === "liquidity" && <LiquidityScreen liquidity={liquidity} snapshot={snapshot} />}
            {section === "scenarios" && <ScenarioBuilder value={scenario} onChange={setScenario} onRun={execute} busy={busy} />}
            {section === "simulator" && <Simulator onRun={execute} busy={busy} />}
            {section === "results" && <Results run={run} />}
            {section === "compare" && <Compare />}
            {section === "validation" && <Validation snapshot={snapshot} />}
            {section === "provenance" && <Provenance snapshot={snapshot} />}
          </section>
        )}
      </main>
    </div>
  );
}

function title(section: string) {
  return ({
    overview: "System Overview",
    positions: "Borrower Positions",
    liquidity: "Liquidity Surface",
    scenarios: "Scenario Builder",
    simulator: "Cascade Simulator",
    results: "Experiment Results",
    compare: "Scenario Comparison",
    validation: "Validation Evidence",
    provenance: "Data Provenance",
  } as Record<string, string>)[section] ?? "System Overview";
}

function Loading() {
  return <div className="loading"><span />Loading snapshot and model state…</div>;
}

function Card({ label, value, detail, tone }: { label: string; value: string; detail?: string; tone?: "risk" | "safe" }) {
  return <article className={`metricCard ${tone ?? ""}`}><p>{label}</p><strong>{value}</strong>{detail && <small>{detail}</small>}</article>;
}

function Overview({ snapshot, positions, liquidity, health }: { snapshot: Snapshot; positions: Position[]; liquidity: Liquidity | null; health: Health | null }) {
  const totalDebt = positions.reduce((sum, item) => sum + item.total_debt, 0);
  const hist = hfHistogram(positions);
  const debt = [...positions].sort((a, b) => b.total_debt - a.total_debt).slice(0, 10).map((item, index) => ({ name: `B${index + 1}`, debt: item.total_debt }));
  return <>
    <div className="sectionLead"><div><p className="eyebrow">SNAPSHOT / {snapshot.id}</p><h2>Contagion risk at a reproducible state</h2><p>{snapshot.label}</p></div><div className="blockRef">Block <strong>{snapshot.block_number.toLocaleString()}</strong><small>{snapshot.block_hash.slice(0, 18)}…</small></div></div>
    <div className="metricGrid">
      <Card label="WETH oracle price" value={money(snapshot.oracle_prices.WETH)} detail="Aave valuation channel" />
      <Card label="USDC oracle price" value={money(snapshot.oracle_prices.USDC)} detail={`${snapshot.stablecoin_state.depeg_bps.toFixed(1)} bps depeg monitor`} />
      <Card label="Sampled debt" value={money(totalDebt)} detail={`${positions.length} borrowers`} />
      <Card label="Borrower cohort" value={String(positions.length)} detail={String(snapshot.coverage.cohort_label ?? "snapshot cohort")} />
      <Card label="HF below 1.05" value={String(positions.filter((p) => p.health_factor < 1.05).length)} detail="critical risk" tone="risk" />
      <Card label="HF below 1.10" value={String(positions.filter((p) => p.health_factor < 1.1).length)} detail="immediate risk cohort" tone="risk" />
      <Card label="HF below 1.20" value={String(positions.filter((p) => p.health_factor < 1.2).length)} detail="watch cohort" />
      <Card label="DEX spot" value={money(liquidity?.spot_price)} detail={`${String(liquidity?.pool.fee ?? "—")} fee tier`} />
    </div>
    <div className="twoCol">
      <Panel title="Health Factor distribution" eyebrow="BORROWER SAFETY">
        <Chart><BarChart data={hist}><CartesianGrid strokeDasharray="3 3" stroke="#1b3553" /><XAxis dataKey="bin" stroke="#7590aa" /><YAxis stroke="#7590aa" allowDecimals={false} /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="count" fill="#31d4e8" radius={[4, 4, 0, 0]} /></BarChart></Chart>
      </Panel>
      <Panel title="Debt concentration" eyebrow="TOP 10 POSITIONS">
        <Chart><AreaChart data={debt}><defs><linearGradient id="debt" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#6f7cff" stopOpacity={0.8}/><stop offset="95%" stopColor="#6f7cff" stopOpacity={0.05}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" stroke="#1b3553" /><XAxis dataKey="name" stroke="#7590aa" /><YAxis stroke="#7590aa" tickFormatter={(v) => `${Math.round(v / 1000)}k`} /><Tooltip contentStyle={tooltipStyle} formatter={(v) => money(Number(v))} /><Area type="monotone" dataKey="debt" stroke="#8c96ff" fill="url(#debt)" /></AreaChart></Chart>
      </Panel>
    </div>
    <Panel title="Source health" eyebrow="OBSERVABILITY">
      <div className="healthRow"><HealthItem label="Ethereum RPC" value={health?.ethereum_rpc.connected ? `Block ${health.ethereum_rpc.current_block} · finalized lag ${health.ethereum_rpc.block_lag ?? "—"}` : "Not configured"} ok={Boolean(health?.ethereum_rpc.connected)} /><HealthItem label="Aave" value={health?.aave ?? "—"} ok={health?.aave === "HEALTHY"} /><HealthItem label="Uniswap" value={health?.uniswap ?? "—"} ok={health?.uniswap === "HEALTHY"} /><HealthItem label="Subgraph" value={health?.subgraph ?? "—"} ok={health?.subgraph === "CONFIGURED"} /></div>
    </Panel>
  </>;
}

function HealthItem({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return <div className="healthItem"><span className={`statusDot ${ok ? "green" : "amber"}`} /><div><strong>{label}</strong><small>{value}</small></div></div>;
}

function Positions({ positions, coverage }: { positions: Position[]; coverage: Snapshot["coverage"] }) {
  const [limit, setLimit] = useState(1.2);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<"hf" | "debt">("hf");
  const filtered = positions.filter((p) => p.health_factor < limit && p.borrower_hash.includes(search.trim().toLowerCase())).sort((a, b) => sort === "debt" ? b.total_debt - a.total_debt : a.health_factor - b.health_factor);
  return <>
    <div className="coverageStrip">{Object.entries(coverage).slice(0, 8).map(([key, value]) => <div key={key}><span>{key.replaceAll("_", " ")}</span><strong>{String(value)}</strong></div>)}</div>
    <Panel title="Position cohort" eyebrow="PSEUDONYMIZED PUBLIC ADDRESSES">
      <div className="controls"><label>HF threshold<select value={limit} onChange={(e) => setLimit(Number(e.target.value))}><option value={1.05}>Below 1.05</option><option value={1.1}>Below 1.10</option><option value={1.2}>Below 1.20</option><option value={10}>All</option></select></label><label>Order<select value={sort} onChange={(e) => setSort(e.target.value as "hf" | "debt")}><option value="hf">Lowest HF</option><option value="debt">Top debt</option></select></label><label>Search<input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="borrower-…" /></label></div>
      <div className="tableWrap"><table><thead><tr><th>Borrower</th><th>HF</th><th>WETH collateral</th><th>USDC debt</th><th>Liquidation price</th><th>Distance</th><th>Debt share</th></tr></thead><tbody>{filtered.map((p) => <tr key={p.borrower_hash}><td><code>{p.borrower_hash}</code></td><td><span className={`hf ${p.health_factor < 1.05 ? "danger" : p.health_factor < 1.2 ? "warn" : "ok"}`}>{p.health_factor.toFixed(3)}</span></td><td>{p.collateral_weth.toFixed(3)}</td><td>{money(p.debt_usdc)}</td><td>{money(p.liquidation_price)}</td><td>{percent(p.distance_to_liquidation)}</td><td>{percent(p.debt_share)}</td></tr>)}</tbody></table></div>
    </Panel>
    <Panel title="Filtered Health Factor distribution" eyebrow={`${filtered.length} POSITIONS`}><Chart><BarChart data={hfHistogram(filtered)}><CartesianGrid strokeDasharray="3 3" stroke="#1b3553" /><XAxis dataKey="bin" stroke="#7590aa" /><YAxis stroke="#7590aa" allowDecimals={false} /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="count" fill="#31d4e8" radius={[4, 4, 0, 0]} /></BarChart></Chart></Panel>
  </>;
}

function LiquidityScreen({ liquidity, snapshot }: { liquidity: Liquidity | null; snapshot: Snapshot }) {
  if (!liquidity) return <Loading />;
  const depth = Object.entries(liquidity.depth_usdc).map(([deviation, value]) => ({ deviation: `±${deviation}%`, depth: value }));
  return <>
    <div className="metricGrid"><Card label="Spot price" value={money(liquidity.spot_price)} /><Card label="Fee tier" value={String(liquidity.pool.fee ?? "—")} /><Card label="Current tick" value={String(liquidity.pool.tick ?? "—")} /><Card label="Active liquidity" value={compact(Number(liquidity.pool.liquidity ?? 0))} /></div>
    <Panel title="Executable depth" eyebrow="V3 SQUARE-ROOT-PRICE MODEL"><Chart><BarChart data={depth}><CartesianGrid strokeDasharray="3 3" stroke="#1b3553" /><XAxis dataKey="deviation" stroke="#7590aa" /><YAxis stroke="#7590aa" tickFormatter={(v) => compact(v)} /><Tooltip contentStyle={tooltipStyle} formatter={(v) => money(Number(v))} /><Bar dataKey="depth" fill="#31d4e8" radius={[5, 5, 0, 0]} /></BarChart></Chart></Panel>
    <Panel title="Resolved fee tiers" eyebrow="SELECTED BY ±2% EXECUTABLE DEPTH"><div className="tableWrap"><table><thead><tr><th>Pool</th><th>Fee</th><th>Spot</th><th>Active liquidity</th><th>Depth at 2%</th></tr></thead><tbody>{liquidity.pools.map((pool) => <tr key={String(pool.pool_address)}><td><code>{String(pool.pool_address)}</code></td><td>{String(pool.fee)}</td><td>{money(Number(pool.spot_price ?? liquidity.spot_price))}</td><td>{compact(Number(pool.liquidity ?? 0))}</td><td>{pool.depth_usdc_2pct == null ? "Selected fixture" : money(Number(pool.depth_usdc_2pct))}</td></tr>)}</tbody></table></div></Panel>
    <Panel title="Pool identity and quality" eyebrow={snapshot.mode}><dl className="definition"><div><dt>Pool</dt><dd>{String(liquidity.pool.pool_address)}</dd></div><div><dt>sqrtPriceX96</dt><dd>{String(liquidity.pool.sqrt_price_x96)}</dd></div><div><dt>Tick spacing</dt><dd>{String(liquidity.pool.tick_spacing)}</dd></div><div><dt>Source</dt><dd>{String(liquidity.pool.source)}</dd></div></dl>{liquidity.quality_flags.map((flag) => <div className="quality" key={flag.code}><strong>{flag.code}</strong>{flag.message}</div>)}</Panel>
  </>;
}

function ScenarioBuilder({ value, onChange, onRun, busy }: { value: ScenarioForm; onChange: (next: ScenarioForm) => void; onRun: (mode: "DETERMINISTIC" | "MONTE_CARLO") => Promise<void>; busy: boolean }) {
  const field = (key: ScenarioNumericKey, label: string, min: number, max: number, step = 1) => <label className="formField"><span>{label}</span><input type="number" min={min} max={max} step={step} value={value[key]} onChange={(e) => onChange({ ...value, [key]: Number(e.target.value) })} /></label>;
  return <div className="scenarioLayout"><Panel title="Stress parameters" eyebrow={`IMMUTABLE AFTER RUN · ${value.name.toUpperCase()}`}><div className="presetRow">{Object.entries(scenarioPresets).map(([name, preset]) => <button className={value.name === name ? "selected" : ""} key={name} onClick={() => onChange(preset)}>{name}</button>)}</div><div className="formGrid">{field("shock_pct", "ETH shock %", -50, 0)}{field("liquidity_haircut_pct", "Liquidity haircut %", 0, 95)}{field("gas_multiplier", "Gas multiplier", 0.1, 20, 0.1)}{field("liquidator_capital_usdc", "Liquidator capital USDC", 1, 100_000_000)}{field("liquidator_capacity_usdc", "Capacity / step USDC", 1, 100_000_000)}{field("liquidator_delay_steps", "Liquidator delay steps", 0, 100)}{field("liquidator_min_profit_usdc", "Minimum profit USDC", 0, 1_000_000)}{field("arbitrage_capacity_pct", "Arbitrage capacity %", 0, 100)}{field("arbitrage_delay_steps", "Arbitrage delay steps", 0, 100)}{field("horizon_steps", "Horizon steps", 1, 1000)}{field("timestep_seconds", "Timestep seconds", 1, 86_400)}{field("monte_carlo_runs", "Monte Carlo runs", 1, 10_000)}{field("volatility_pct", "Volatility %", 0, 100, 0.1)}{field("liquidation_threshold_override", "Liquidation threshold", 0.01, 1, 0.001)}{field("liquidation_bonus_override", "Liquidation bonus", 1, 2, 0.001)}{field("max_waves", "Maximum waves", 1, 100)}{field("seed", "Random seed", 0, 2_147_483_647)}</div><div className="actionRow"><button className="primary" disabled={busy} onClick={() => void onRun("DETERMINISTIC")}>Run deterministic</button><button disabled={busy} onClick={() => void onRun("MONTE_CARLO")}>Run Monte Carlo</button></div></Panel><Panel title="Feedback loop" eyebrow="MODEL SEQUENCE"><ol className="timeline"><li>Exogenous ETH shock</li><li>Portfolio revaluation and HF</li><li>Liquidator profit and capacity</li><li>Forced WETH execution through V3</li><li>Arbitrage response</li><li>Newly liquidatable cohort</li></ol></Panel></div>;
}

function Simulator({ onRun, busy }: { onRun: (mode: "DETERMINISTIC" | "MONTE_CARLO") => Promise<void>; busy: boolean }) {
  return <div className="emptyState"><span className="pulse"><i /></span><p className="eyebrow">DETERMINISTIC EVENT ENGINE</p><h2>Run the professor scenario</h2><p>The timeline is produced from snapshot + scenario + model version + seed. Events are never hard-coded.</p><button className="primary" disabled={busy} onClick={() => void onRun("DETERMINISTIC")}>Start cascade simulation</button></div>;
}

function Results({ run }: { run: Run | null }) {
  if (!run) return <Loading />;
  if (run.status !== "COMPLETE" || !run.result) return <div className="emptyState"><span className="pulse"><i /></span><h2>{run.status}</h2><p>{run.error ?? `Progress ${run.progress_percent}%`}</p></div>;
  if (run.result.monte_carlo) return <MonteCarloResults run={run} />;
  const metrics = run.result.metrics;
  const series = run.result.timeseries;
  const waves = [...new Set(run.result.events.filter((event) => event.event_type === "LIQUIDATION").map((event) => Number(event.wave)))];
  return <>
    <div className="metricGrid wide"><Card label="Liquidation at risk" value={money(metrics.liquidation_at_risk)} /><Card label="Total liquidated" value={money(metrics.total_liquidated_debt)} /><Card label="Amplification" value={metrics.cascade_amplification == null ? "No denominator" : `${metrics.cascade_amplification.toFixed(2)}×`} tone="risk" /><Card label="Max price impact" value={percent(metrics.max_price_impact)} /><Card label="Bad debt" value={money(metrics.bad_debt)} /><Card label="Cascade depth" value={`${metrics.cascade_depth ?? 0} waves`} /></div>
    <div className="waveRow">{waves.length ? waves.map((wave) => <span key={wave}>Wave {wave}</span>) : <strong>No endogenous cascade detected.</strong>}<a className="download" href={`${API_URL}/api/v1/runs/${run.id}/export`}>Download experiment</a></div>
    <Panel title="Price and liquidation timeline" eyebrow={`RUN ${run.id.slice(0, 8)}`}><Chart><LineChart data={series}><CartesianGrid strokeDasharray="3 3" stroke="#1b3553" /><XAxis dataKey="step" stroke="#7590aa" /><YAxis stroke="#7590aa" domain={["auto", "auto"]} /><Tooltip contentStyle={tooltipStyle} /><Line type="monotone" dataKey="reference_price" stroke="#8c96ff" strokeWidth={2} dot /><Line type="monotone" dataKey="dex_price" stroke="#31d4e8" strokeWidth={2} dot /></LineChart></Chart></Panel>
    <Panel title="Event audit trail" eyebrow={`${run.result.events.length} EVENTS`}><div className="eventList">{run.result.events.map((event, index) => <div key={`${String(event.event_type)}-${index}`}><span>t{String(event.step)} / W{String(event.wave)}</span><strong>{String(event.event_type).replaceAll("_", " ")}</strong><code>{String(event.borrower_hash ?? event.agent ?? "system")}</code><b>{event.debt_repaid ? money(Number(event.debt_repaid)) : ""}</b></div>)}</div></Panel>
  </>;
}

function MonteCarloResults({ run }: { run: Run }) {
  const monteCarlo = run.result?.monte_carlo;
  if (!monteCarlo) return <Loading />;
  const probability = Number(monteCarlo.summary.probability_of_cascade ?? 0);
  const expectedShortfall = Number(monteCarlo.summary.expected_shortfall_95 ?? 0);
  const badDebt = monteCarlo.distributions.bad_debt ?? [];
  const losses = monteCarlo.distributions.total_liquidated_debt ?? [];
  const cdf = [...losses].sort((a, b) => a - b).map((loss, index) => ({ loss, probability: (index + 1) / losses.length }));
  return <>
    <div className="metricGrid wide"><Card label="P(Cascade)" value={percent(probability)} tone="risk" /><Card label="Expected shortfall 95" value={money(expectedShortfall)} /><Card label="Monte Carlo runs" value={String(badDebt.length)} /><Card label="Seed" value={String(run.seed)} /></div>
    <div className="waveRow"><strong>Seeded stochastic paths use the same deterministic cascade engine.</strong><a className="download" href={`${API_URL}/api/v1/runs/${run.id}/export`}>Download experiment</a></div>
    <div className="twoCol"><Panel title="Bad debt distribution" eyebrow="MONTE CARLO HISTOGRAM"><Chart><BarChart data={histogram(badDebt, 12)}><CartesianGrid strokeDasharray="3 3" stroke="#1b3553" /><XAxis dataKey="label" stroke="#7590aa" /><YAxis stroke="#7590aa" /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="count" fill="#ef5a72" radius={[5, 5, 0, 0]} /></BarChart></Chart></Panel><Panel title="Liquidation-loss CDF" eyebrow="TAIL RISK"><Chart><LineChart data={cdf}><CartesianGrid strokeDasharray="3 3" stroke="#1b3553" /><XAxis dataKey="loss" stroke="#7590aa" tickFormatter={(value) => compact(Number(value))} /><YAxis stroke="#7590aa" domain={[0, 1]} tickFormatter={(value) => percent(Number(value))} /><Tooltip contentStyle={tooltipStyle} formatter={(value) => percent(Number(value))} /><Line type="monotone" dataKey="probability" stroke="#31d4e8" dot={false} strokeWidth={2} /></LineChart></Chart></Panel></div>
  </>;
}

function Compare() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [comparison, setComparison] = useState<{ runs: Array<{ run_id: string; metrics: Record<string, number | null>; delta_vs_first: Record<string, number | null> }> } | null>(null);
  const [message, setMessage] = useState("");
  useEffect(() => {
    const ids = JSON.parse(window.localStorage.getItem("defi-run-ids") ?? "[]") as string[];
    void Promise.all(ids.slice(0, 8).map((id) => api<Run>(`/api/v1/runs/${id}`))).then((items) => setRuns(items.filter((item) => item.status === "COMPLETE" && !item.result?.monte_carlo).slice(0, 4))).catch((error: Error) => setMessage(error.message));
  }, []);
  async function compare() {
    if (runs.length < 2) return setMessage("Create at least two runs from the same snapshot.");
    try {
      setComparison(await api("/api/v1/runs/compare", { method: "POST", body: JSON.stringify({ run_ids: runs.slice(0, 4).map((run) => run.id) }) }));
      setMessage("");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Comparison failed."); }
  }
  return <Panel title="Compare 2–4 completed runs" eyebrow="SAME SNAPSHOT REQUIRED"><div className="runChips">{runs.map((item) => <span key={item.id}>{item.id.slice(0, 8)} · {item.status}</span>)}</div><button className="primary" onClick={() => void compare()}>Compare recent runs</button>{message && <p className="inlineError">{message}</p>}{comparison && <div className="tableWrap"><table><thead><tr><th>Run</th><th>Liquidated</th><th>Amplification</th><th>Bad debt</th><th>Depth</th></tr></thead><tbody>{comparison.runs.map((item) => <tr key={item.run_id}><td>{item.run_id.slice(0, 8)}</td><td>{money(item.metrics.total_liquidated_debt)}</td><td>{item.metrics.cascade_amplification?.toFixed(2) ?? "—"}</td><td>{money(item.metrics.bad_debt)}</td><td>{item.metrics.cascade_depth}</td></tr>)}</tbody></table></div>}</Panel>;
}

function Validation({ snapshot }: { snapshot: Snapshot }) {
  const [report, setReport] = useState<{ status: string; report: { reason: string } } | null>(null);
  async function validate() { setReport(await api("/api/v1/validate/fork", { method: "POST", body: JSON.stringify({ snapshot_id: snapshot.id }) })); }
  return <><Panel title="Validation matrix" eyebrow="EVIDENCE, NOT CLAIMS"><div className="validationGrid"><HealthItem label="Formula and invariant suite" value="Automated locally" ok /><HealthItem label="Direct contract state" value={snapshot.mode === "FIXTURE" ? "Not applicable" : "Snapshot evidence"} ok={snapshot.mode !== "FIXTURE"} /><HealthItem label="Quoter / V3 fork" value="Environment dependent" ok={false} /><HealthItem label="Aave liquidation fork" value="Environment dependent" ok={false} /></div><button className="primary" onClick={() => void validate()}>Check fork prerequisites</button>{report && <div className="validationResult"><strong>{report.status}</strong><p>{report.report.reason}</p></div>}</Panel><Panel title="Tolerance policy" eyebrow="MODEL VS REFERENCE"><p>Health Factor raises a mismatch flag above absolute error 0.02. V3 quote error must be recorded by trade size; no tolerance is silently converted into PASS.</p></Panel></>;
}

function Provenance({ snapshot }: { snapshot: Snapshot }) {
  return <><Panel title="Snapshot identity" eyebrow="IMMUTABLE"><dl className="definition"><div><dt>Mode</dt><dd>{snapshot.mode}</dd></div><div><dt>Block</dt><dd>{snapshot.block_number}</dd></div><div><dt>Block hash</dt><dd>{snapshot.block_hash}</dd></div><div><dt>Timestamp</dt><dd>{snapshot.block_timestamp}</dd></div></dl></Panel><Panel title="Metric formulas and sources" eyebrow="CLICK-THROUGH EXPLAINABILITY"><div className="formula"><strong>Health Factor</strong><code>Σ collateral × price × liquidation threshold / Σ debt × price</code><p>Cross-check: Aave Pool.getUserAccountData at the snapshot block.</p></div><div className="formula"><strong>Cascade amplification</strong><code>Total liquidated debt / direct-shock liquidated debt</code><p>A zero denominator returns null.</p></div><div className="formula"><strong>Bad debt</strong><code>Σ max(remaining debt − recoverable collateral, 0)</code><p>Reported separately from unliquidated debt.</p></div></Panel><Panel title="Source manifest" eyebrow="PROTOCOL ADDRESSES AND VERSIONS"><pre>{JSON.stringify(snapshot, ["mode", "block_number", "block_hash", "data_quality_flags"], 2)}</pre>{snapshot.data_quality_flags.map((flag) => <div className="quality" key={flag.code}><strong>{flag.code}</strong>{flag.message}</div>)}</Panel></>;
}

function Panel({ title, eyebrow, children }: { title: string; eyebrow: string; children: React.ReactNode }) {
  return <section className="panel"><header><div><p className="eyebrow">{eyebrow}</p><h3>{title}</h3></div></header>{children}</section>;
}

function Chart({ children }: { children: React.ReactNode }) {
  return <div className="chart"><ResponsiveContainer width="100%" height="100%">{children}</ResponsiveContainer></div>;
}

function hfHistogram(positions: Position[]) {
  const bins = [{ bin: "<1.05", min: 0, max: 1.05 }, { bin: "1.05–1.10", min: 1.05, max: 1.1 }, { bin: "1.10–1.20", min: 1.1, max: 1.2 }, { bin: "1.20–1.40", min: 1.2, max: 1.4 }, { bin: ">1.40", min: 1.4, max: Infinity }];
  return bins.map((bin) => ({ bin: bin.bin, count: positions.filter((p) => p.health_factor >= bin.min && p.health_factor < bin.max).length }));
}

function histogram(values: number[], bins: number) {
  if (!values.length) return [];
  const low = Math.min(...values);
  const high = Math.max(...values);
  const width = high === low ? 1 : (high - low) / bins;
  const rows = Array.from({ length: bins }, (_, index) => ({
    label: compact(low + index * width),
    count: 0,
  }));
  for (const value of values) {
    const index = Math.min(bins - 1, Math.floor((value - low) / width));
    rows[index].count += 1;
  }
  return rows;
}

function compact(value: number) {
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 2 }).format(value);
}

const tooltipStyle = { background: "#0b1e33", border: "1px solid #24425f", borderRadius: 8, color: "#edf7ff" };
