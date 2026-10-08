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

import {
  API_URL,
  HealthStatus,
  Position,
  Run,
  Snapshot,
  SnapshotSummary,
  api,
  money,
  percent,
} from "@/lib/api";
import {
  persistSnapshotSelection,
  resolveSnapshotSelection,
  shouldShowFixtureBanner,
  shouldShowMainnetBanner,
} from "@/lib/snapshot-selection";
import { ContagionGraph } from "./ContagionGraph";

const nav = [
  ["overview", "Overview"],
  ["positions", "Positions"],
  ["liquidity", "Liquidity"],
  ["scenarios", "Scenarios"],
  ["simulator", "Simulator"],
  ["contagion", "Contagion Graph"],
  ["compare", "Compare"],
  ["validation", "Validation"],
  ["provenance", "Provenance"],
] as const;

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
  const [snapshots, setSnapshots] = useState<SnapshotSummary[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [liquidity, setLiquidity] = useState<Liquidity | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [scenario, setScenario] = useState<ScenarioForm>(professorPreset);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [activity, setActivity] = useState<string | null>(null);
  const [busy, setBusy] = useState(true);

  const activateSnapshot = useCallback(async (selected: Snapshot, persist = true) => {
    const [positionData, liquidityData] = await Promise.all([
      api<{ positions: Position[] }>(`/api/v1/snapshots/${selected.id}/positions`),
      api<Liquidity>(`/api/v1/snapshots/${selected.id}/liquidity`),
    ]);
    setSnapshot(selected);
    setPositions(positionData.positions);
    setLiquidity(liquidityData);
    if (persist) persistSnapshotSelection(window.localStorage, selected.id);
  }, []);

  const refreshSnapshotOptions = useCallback(async () => {
    const available = await api<SnapshotSummary[]>("/api/v1/snapshots");
    setSnapshots(available);
    return available;
  }, []);

  const loadSnapshot = useCallback(async () => {
    try {
      setBusy(true);
      setActivity("Discovering stored snapshots and live source capabilities…");
      setError(null);
      const savedId = window.localStorage.getItem("defi-snapshot-id");
      let selected: Snapshot | null = null;
      let staleSavedId = false;
      if (savedId) {
        try {
          selected = await api<Snapshot>(`/api/v1/snapshots/${savedId}`);
        } catch {
          window.localStorage.removeItem("defi-snapshot-id");
          staleSavedId = true;
        }
      }
      const [available, healthData] = await Promise.all([
        refreshSnapshotOptions(),
        api<HealthStatus>("/api/v1/health"),
      ]);
      setHealth(healthData);
      if (!selected) {
        const decision = resolveSnapshotSelection(available, savedId, healthData.can_create_real_snapshot);
        staleSavedId ||= decision.staleSavedId;
        if (decision.snapshot) {
          selected = await api<Snapshot>(`/api/v1/snapshots/${decision.snapshot.id}`);
        } else if (decision.shouldCreateFixture) {
          selected = await api<Snapshot>("/api/v1/snapshots", {
            method: "POST",
            body: JSON.stringify({ mode: "FIXTURE" }),
          });
          await refreshSnapshotOptions();
        }
      }
      if (selected) {
        await activateSnapshot(selected);
        setNotice(
          staleSavedId
            ? `Previously selected snapshot is no longer available. Using ${sourceLabel(selected.mode)}.`
            : selected.mode === "FIXTURE" && !healthData.can_create_real_snapshot
              ? "No Mainnet snapshot or live Mainnet creation capability is available. Using the Fixture fallback."
              : null,
        );
      } else {
        setSnapshot(null);
        setPositions([]);
        setLiquidity(null);
        setNotice(
          staleSavedId
            ? "Previously selected snapshot is no longer available. No Mainnet snapshot is currently loaded."
            : "Mainnet sources are configured. No Mainnet snapshot is currently loaded.",
        );
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The API is unavailable.");
    } finally {
      setActivity(null);
      setBusy(false);
    }
  }, [activateSnapshot, refreshSnapshotOptions]);

  async function chooseSnapshot(snapshotId: string) {
    try {
      setBusy(true);
      setActivity("Loading selected snapshot evidence…");
      setError(null);
      const selected = await api<Snapshot>(`/api/v1/snapshots/${snapshotId}`);
      await activateSnapshot(selected);
      setNotice(`Selected ${sourceLabel(selected.mode)} at block ${selected.block_number.toLocaleString()}.`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The selected snapshot could not be loaded.");
    } finally {
      setActivity(null);
      setBusy(false);
    }
  }

  async function createFreshMainnet() {
    try {
      setBusy(true);
      setActivity("Building coordinated Mainnet snapshot…");
      setError(null);
      const selected = await api<Snapshot>("/api/v1/snapshots", {
        method: "POST",
        body: JSON.stringify({ mode: "REAL_MAINNET" }),
      });
      await activateSnapshot(selected);
      await refreshSnapshotOptions();
      setNotice(`Created and selected REAL MAINNET snapshot at block ${selected.block_number.toLocaleString()}.`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The Mainnet snapshot could not be created.");
    } finally {
      setActivity(null);
      setBusy(false);
    }
  }

  async function useFixture() {
    try {
      setBusy(true);
      setActivity("Loading synthetic Fixture dataset…");
      setError(null);
      const existing = snapshots.find((item) => item.mode === "FIXTURE");
      const selected = existing
        ? await api<Snapshot>(`/api/v1/snapshots/${existing.id}`)
        : await api<Snapshot>("/api/v1/snapshots", {
            method: "POST",
            body: JSON.stringify({ mode: "FIXTURE" }),
          });
      await activateSnapshot(selected);
      await refreshSnapshotOptions();
      setNotice("Fixture data are synthetic and must not be cited as Mainnet evidence.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The Fixture dataset could not be loaded.");
    } finally {
      setActivity(null);
      setBusy(false);
    }
  }

  async function importMainnetArtifact() {
    try {
      setBusy(true);
      setActivity("Importing the approved verified Mainnet artifact…");
      setError(null);
      const result = await api<{ imported: boolean; snapshot: SnapshotSummary }>(
        "/api/v1/snapshots/import-mainnet-artifact",
        { method: "POST" },
      );
      await refreshSnapshotOptions();
      const selected = await api<Snapshot>(`/api/v1/snapshots/${result.snapshot.id}`);
      await activateSnapshot(selected);
      setNotice(
        result.imported
          ? "Imported and selected the approved verified Mainnet artifact."
          : "The approved Mainnet artifact was already loaded and is now selected.",
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "The Mainnet artifact could not be imported.");
    } finally {
      setActivity(null);
      setBusy(false);
    }
  }

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
          <span className={`statusDot ${health ? "green" : "amber"}`} /> API {health ? "connected" : "status pending"}
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
            <span className={`modeBadge sourceBadge ${snapshotBadge(snapshot).tone}`}>
              <strong>{snapshotBadge(snapshot).label}</strong>
              <small>{snapshotBadge(snapshot).detail}</small>
            </span>
            <span className="safety">Research Simulation — Mainnet Read-Only</span>
          </div>
        </header>
        {error && (
          <div className="errorBanner">
            <strong>Request failed.</strong> {error}
            <button onClick={() => void loadSnapshot()}>Retry</button>
          </div>
        )}
        {busy && !snapshot ? <Loading /> : null}
        {!busy || snapshot ? (
          <section className="content">
            <DataSourceSelector
              snapshots={snapshots}
              selectedId={snapshot?.id ?? null}
              health={health}
              busy={busy}
              onSelect={chooseSnapshot}
              onCreateMainnet={createFreshMainnet}
              onUseFixture={useFixture}
              onImportArtifact={importMainnetArtifact}
            />
            {notice && <div className="noticeBanner" role="status">{notice}</div>}
            {activity && <div className="activityBanner"><span />{activity}</div>}
            {shouldShowFixtureBanner(snapshot?.mode ?? null) && (
              <div className="fixtureBanner"><strong>FIXTURE DATA</strong> Synthetic deterministic dataset for development and tests. This snapshot is not Mainnet evidence.</div>
            )}
            {snapshot && shouldShowMainnetBanner(snapshot.mode) && <MainnetEvidenceBanner snapshot={snapshot} />}
            {!snapshot && <MainnetReadyState health={health} />}
            {snapshot && section === "overview" && <Overview snapshot={snapshot} positions={positions} liquidity={liquidity} health={health} />}
            {snapshot && section === "positions" && <Positions positions={positions} coverage={snapshot.coverage} />}
            {snapshot && section === "liquidity" && <LiquidityScreen liquidity={liquidity} snapshot={snapshot} />}
            {snapshot && section === "scenarios" && <ScenarioBuilder value={scenario} onChange={setScenario} onRun={execute} busy={busy} />}
            {snapshot && section === "simulator" && <Simulator onRun={execute} busy={busy} />}
            {snapshot && section === "contagion" && <ContagionGraph snapshot={snapshot} />}
            {snapshot && section === "results" && <Results run={run} />}
            {snapshot && section === "compare" && <Compare />}
            {snapshot && section === "validation" && <Validation snapshot={snapshot} />}
            {snapshot && section === "provenance" && <Provenance snapshot={snapshot} />}
          </section>
        ) : null}
      </main>
    </div>
  );
}

function sourceLabel(mode: Snapshot["mode"]): string {
  return mode === "REAL_MAINNET"
    ? "REAL MAINNET"
    : mode === "CACHED_MAINNET"
      ? "CACHED MAINNET"
      : "FIXTURE";
}

function snapshotBadge(snapshot: Snapshot | null): { label: string; detail: string; tone: string } {
  if (!snapshot) return { label: "SELECT SOURCE", detail: "No snapshot selected", tone: "configured" };
  if (snapshot.mode === "REAL_MAINNET") {
    return { label: "REAL MAINNET", detail: "Verified on-chain snapshot", tone: "real" };
  }
  if (snapshot.mode === "CACHED_MAINNET") {
    return { label: "CACHED MAINNET", detail: "Verified historical Mainnet snapshot", tone: "cached" };
  }
  return { label: "FIXTURE", detail: "Synthetic development dataset", tone: "fixture" };
}

function DataSourceSelector({
  snapshots,
  selectedId,
  health,
  busy,
  onSelect,
  onCreateMainnet,
  onUseFixture,
  onImportArtifact,
}: {
  snapshots: SnapshotSummary[];
  selectedId: string | null;
  health: HealthStatus | null;
  busy: boolean;
  onSelect: (snapshotId: string) => Promise<void>;
  onCreateMainnet: () => Promise<void>;
  onUseFixture: () => Promise<void>;
  onImportArtifact: () => Promise<void>;
}) {
  return (
    <Panel title="Selected Data Source" eyebrow="SNAPSHOT EVIDENCE · SEPARATE FROM LIVE HEALTH">
      <div className="snapshotOptions">
        {snapshots.map((item) => (
          <button
            type="button"
            key={item.id}
            className={`snapshotOption ${selectedId === item.id ? "selected" : ""} ${item.mode.toLowerCase()}`}
            disabled={busy}
            onClick={() => void onSelect(item.id)}
          >
            <span>{sourceLabel(item.mode)}</span>
            <strong>Block {item.block_number.toLocaleString()}</strong>
            <small>
              {item.mode === "FIXTURE"
                ? "Synthetic development / testing dataset"
                : `${Number(item.coverage.active_borrowers ?? item.coverage.positions_loaded ?? 0).toLocaleString()} verified borrowers · ${Number(item.coverage.weth_usdc_cohort ?? 0).toLocaleString()} research cohort`}
            </small>
          </button>
        ))}
        {!snapshots.length && <p className="emptySourceList">No stored snapshots are currently loaded.</p>}
      </div>
      <div className="actionRow sourceActions">
        <button
          type="button"
          className="primary"
          disabled={busy || !health?.can_create_real_snapshot}
          onClick={() => void onCreateMainnet()}
        >
          Create Fresh Mainnet Snapshot
        </button>
        {health?.mainnet_artifact.available && !health.mainnet_artifact.loaded && (
          <button type="button" disabled={busy} onClick={() => void onImportArtifact()}>
            Import Verified Mainnet Artifact
          </button>
        )}
        <button type="button" disabled={busy} onClick={() => void onUseFixture()}>
          Use Fixture Dataset
        </button>
      </div>
      <p className="sourceHelp">
        {health?.can_create_real_snapshot
          ? "Mainnet sources are configured. Creating a fresh snapshot requires an explicit action and may take several minutes."
          : "Fresh Mainnet creation is unavailable. Stored REAL/CACHED snapshots remain reproducible and selectable while live sources are offline."}
        {" "}Fixture data are synthetic and must not be cited as Mainnet evidence.
      </p>
    </Panel>
  );
}

function MainnetEvidenceBanner({ snapshot }: { snapshot: Snapshot }) {
  return (
    <div className="mainnetBanner">
      <div>
        <strong>{sourceLabel(snapshot.mode)} SNAPSHOT</strong>
        <span>Ethereum block {snapshot.block_number.toLocaleString()} · Snapshot ID {snapshot.id}</span>
      </div>
      <div>
        <span>Verified borrowers</span>
        <strong>{String(snapshot.coverage.positions_loaded ?? snapshot.coverage.active_borrowers ?? "—")}</strong>
      </div>
      <div>
        <span>Target WETH/USDC cohort</span>
        <strong>{String(snapshot.coverage.weth_usdc_cohort ?? "—")}</strong>
      </div>
      <p>Data sources: The Graph discovery · Aave contract verification · Uniswap V3 state</p>
    </div>
  );
}

function MainnetReadyState({ health }: { health: HealthStatus | null }) {
  return (
    <div className="emptyState sourceEmptyState">
      <span className="pulse"><i /></span>
      <p className="eyebrow">MAINNET-READY STATE</p>
      <h2>No saved Mainnet snapshot is available</h2>
      <p>
        {health?.can_create_real_snapshot
          ? "Mainnet sources are configured. Create a fresh Mainnet snapshot or deliberately use the Fixture dataset."
          : "Live Mainnet creation is unavailable. Import the approved artifact if offered above, or use Fixture for development only."}
      </p>
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
    contagion: "Contagion Graph",
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

function Overview({ snapshot, positions, liquidity, health }: { snapshot: Snapshot; positions: Position[]; liquidity: Liquidity | null; health: HealthStatus | null }) {
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
    <Panel title="Live source availability" eyebrow="CONNECTIVITY · NOT SNAPSHOT SELECTION">
      <div className="healthRow"><HealthItem label="Ethereum RPC" value={health?.eth_rpc_connected ? `Connected · head ${health.ethereum_rpc.current_block?.toLocaleString() ?? "—"}` : "Unavailable or not configured"} ok={Boolean(health?.eth_rpc_connected)} /><HealthItem label="Aave RPC" value={health?.aave_rpc_ready ? "RPC ready" : "Unavailable"} ok={Boolean(health?.aave_rpc_ready)} /><HealthItem label="Uniswap RPC" value={health?.uniswap_rpc_ready ? "RPC ready" : "Unavailable"} ok={Boolean(health?.uniswap_rpc_ready)} /><HealthItem label="The Graph" value={health?.subgraph_configured ? "Configured" : "Not configured"} ok={Boolean(health?.subgraph_configured)} /></div>
      <p className="sourceHealthNote">These indicators describe current source connectivity. They do not change or invalidate the stored snapshot selected above.</p>
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
  const coverageItems = [
    ["Verified active borrowers", coverage.active_borrowers ?? coverage.positions_loaded ?? positions.length],
    ["WETH collateral borrowers", coverage.weth_collateral_borrowers ?? "—"],
    ["USDC borrowers", coverage.usdc_borrowers ?? "—"],
    ["WETH / USDC research cohort", coverage.weth_usdc_cohort ?? "—"],
    ["Candidate verification rate", coverage.coverage_pct == null ? "—" : `${coverage.coverage_pct}%`],
  ];
  return <>
    <div className="coverageStrip researchCoverage">{coverageItems.map(([label, value]) => <div key={String(label)}><span>{label}</span><strong>{String(value)}</strong></div>)}</div>
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
    <Panel title="Pool identity and quality" eyebrow={snapshot.mode}><dl className="definition"><div><dt>Pool</dt><dd>{String(liquidity.pool.pool_address)}</dd></div><div><dt>sqrtPriceX96</dt><dd>{String(liquidity.pool.sqrt_price_x96)}</dd></div><div><dt>Tick spacing</dt><dd>{String(liquidity.pool.tick_spacing)}</dd></div><div><dt>Source</dt><dd>{String(liquidity.pool.source)}</dd></div></dl>{liquidity.quality_flags.map((flag, index) => <div className="quality" key={`${flag.code}-${index}`}><strong>{flag.code}</strong>{flag.message}</div>)}</Panel>
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
  const manifest = snapshot.source_manifest;
  const discovery = manifest.borrower_discovery;
  const verification = manifest.state_verification;
  const uniswap = manifest.uniswap;
  return <>
    <Panel title="Snapshot identity" eyebrow="IMMUTABLE RESEARCH EVIDENCE">
      <dl className="definition"><div><dt>Mode</dt><dd>{sourceLabel(snapshot.mode)}</dd></div><div><dt>Chain ID</dt><dd>{snapshot.chain_id}</dd></div><div><dt>Block</dt><dd>{snapshot.block_number}</dd></div><div><dt>Block hash</dt><dd>{snapshot.block_hash}</dd></div><div><dt>Block timestamp</dt><dd>{snapshot.block_timestamp}</dd></div><div><dt>Retrieved at</dt><dd>{snapshot.retrieved_at}</dd></div></dl>
    </Panel>
    <Panel title="Coordinated Mainnet sources" eyebrow="ONE BLOCK ACROSS DISCOVERY AND VERIFICATION">
      <dl className="definition"><div><dt>Borrower discovery</dt><dd>{discovery?.source ?? "Not recorded"}</dd></div><div><dt>Graph discovery block</dt><dd>{discovery?.block_number ?? manifest.snapshot_coordination?.graph_head ?? "—"}</dd></div><div><dt>Candidate borrowers</dt><dd>{discovery?.candidate_count ?? snapshot.coverage.candidates_discovered ?? "—"}</dd></div><div><dt>Aave verification</dt><dd>{verification?.source ?? "Not recorded"} · {verification?.aave_method ?? "—"}</dd></div><div><dt>Aave verification block</dt><dd>{verification?.block_number ?? "—"}</dd></div><div><dt>Uniswap V3 pool</dt><dd>{uniswap?.pool ?? String(snapshot.dex_pool.pool_address ?? "—")}</dd></div><div><dt>Uniswap fee tier</dt><dd>{uniswap?.fee ?? String(snapshot.dex_pool.fee ?? "—")}</dd></div></dl>
    </Panel>
    <Panel title="Coverage and interpretation" eyebrow="COHORT, NOT MARKET-WIDE COVERAGE">
      <dl className="definition"><div><dt>Candidate set</dt><dd>{String(snapshot.coverage.candidates_discovered ?? "—")}</dd></div><div><dt>Verified active borrowers</dt><dd>{String(snapshot.coverage.active_borrowers ?? snapshot.coverage.positions_loaded ?? "—")}</dd></div><div><dt>WETH collateral borrowers</dt><dd>{String(snapshot.coverage.weth_collateral_borrowers ?? "—")}</dd></div><div><dt>USDC borrowers</dt><dd>{String(snapshot.coverage.usdc_borrowers ?? "—")}</dd></div><div><dt>WETH / USDC research cohort</dt><dd>{String(snapshot.coverage.weth_usdc_cohort ?? "—")}</dd></div><div><dt>Candidate verification rate</dt><dd>{snapshot.coverage.coverage_pct == null ? "—" : `${snapshot.coverage.coverage_pct}%`}</dd></div><div><dt>Cohort definition</dt><dd>{String(snapshot.coverage.cohort_label ?? "—")}</dd></div></dl>
      <p className="sourceHealthNote">The candidate verification rate describes this bounded discovery cohort; it is not a claim of market-wide borrower coverage.</p>
      {snapshot.data_quality_flags.map((flag, index) => <div className="quality" key={`${flag.code}-${index}`}><strong>{flag.code}</strong>{flag.message}</div>)}
    </Panel>
    <Panel title="Metric formulas and sources" eyebrow="CLICK-THROUGH EXPLAINABILITY"><div className="formula"><strong>Health Factor</strong><code>Σ collateral × price × liquidation threshold / Σ debt × price</code><p>Cross-check: Aave Pool.getUserAccountData at the snapshot block.</p></div><div className="formula"><strong>Cascade amplification</strong><code>Total liquidated debt / direct-shock liquidated debt</code><p>A zero denominator returns null.</p></div><div className="formula"><strong>Bad debt</strong><code>Σ max(remaining debt − recoverable collateral, 0)</code><p>Reported separately from unliquidated debt.</p></div></Panel>
  </>;
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
