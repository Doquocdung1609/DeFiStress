"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import type { TerraBenchmark, TerraManifest, TerraObservation, TerraReplay } from "@/lib/api";
import { API_URL, api, money } from "@/lib/api";
import { terraStatusLabel } from "@/lib/terra";
import { HistoricalChart, ReplayChart } from "./TerraCharts";

const nav = [
  ["overview", "Event Overview"],
  ["historical-data", "Historical Data"],
  ["wallet-dynamics", "Wallet / Run Dynamics"],
  ["model-lab", "Model Lab"],
  ["replay", "Replay"],
  ["benchmark", "Model Benchmark"],
  ["ablation", "Ablation"],
  ["counterfactual", "Counterfactual"],
  ["provenance", "Data Provenance"],
] as const;

const defaultRequest = {
  dataset_version: "terra_fixture_v1",
  calibration_start: "2022-05-01T00:00:00Z",
  calibration_end: "2022-05-06T23:59:59Z",
  cutoff_timestamp: "2022-05-06T23:59:59Z",
  evaluation_start: "2022-05-07T00:00:00Z",
  evaluation_end: "2022-05-13T23:59:59Z",
  model_name: "ABM",
  mode: "OUT_OF_SAMPLE_REPLAY",
  seed: 20220506,
  parameters: { reaction_delay_hours: 0, price_impact_coefficient: 0.24 },
};

type Status = {
  default_cutoff: string;
  default_evaluation: string[];
  datasets: TerraManifest[];
  historical_sources: Array<{ source: string; status: string; reason: string }>;
  fixture_warning: string;
};

type Cohorts = { status: string; warning?: string; cohorts: Array<{ cohort: string; anchor_balance: number; share: number }> };
type ExperimentResult = { id: string; status: string; ablation_results?: Array<{ variant: string; metrics: Record<string, number | null> }>; label?: string; historical_replay?: TerraReplay; counterfactual_replay?: TerraReplay };

export function TerraDashboard({ section }: { section: string }) {
  const [status, setStatus] = useState<Status | null>(null);
  const [datasetVersion, setDatasetVersion] = useState(defaultRequest.dataset_version);
  const [observations, setObservations] = useState<TerraObservation[]>([]);
  const [cohorts, setCohorts] = useState<Cohorts | null>(null);
  const [replay, setReplay] = useState<TerraReplay | null>(null);
  const [benchmark, setBenchmark] = useState<TerraBenchmark | null>(null);
  const [experiment, setExperiment] = useState<ExperimentResult | null>(null);
  const [model, setModel] = useState("ABM");
  const [seed, setSeed] = useState(20220506);
  const [reactionDelay, setReactionDelay] = useState(0);
  const [priceImpact, setPriceImpact] = useState(0.24);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDataset = useCallback(async (version: string) => {
    const encoded = encodeURIComponent(version);
    const [seriesData, cohortData] = await Promise.all([
      api<{ dataset: TerraManifest; observations: TerraObservation[] }>(`/api/v1/terra/timeseries?dataset_version=${encoded}`),
      api<Cohorts>(`/api/v1/terra/wallet-cohorts?dataset_version=${encoded}`),
    ]);
    setObservations(seriesData.observations);
    setCohorts(cohortData);
  }, []);

  const load = useCallback(async () => {
    try {
      setBusy(true);
      const statusData = await api<Status>("/api/v1/terra/status");
      const preferred = preferredDataset(statusData.datasets);
      setStatus(statusData);
      setDatasetVersion(preferred.dataset_version);
      await loadDataset(preferred.dataset_version);
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Terra research API is unavailable.");
    } finally {
      setBusy(false);
    }
  }, [loadDataset]);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const request = useMemo(() => ({
    ...defaultRequest,
    dataset_version: datasetVersion,
    model_name: model,
    seed,
    parameters: { reaction_delay_hours: reactionDelay, price_impact_coefficient: priceImpact },
  }), [datasetVersion, model, priceImpact, reactionDelay, seed]);

  async function runReplay() {
    await perform(async () => setReplay(await api<TerraReplay>("/api/v1/terra/replays", { method: "POST", body: JSON.stringify(request) })));
  }

  async function runBenchmark() {
    await perform(async () => setBenchmark(await api<TerraBenchmark>("/api/v1/terra/benchmark", { method: "POST", body: JSON.stringify(request) })));
  }

  async function runAblation() {
    await perform(async () => setExperiment(await api<ExperimentResult>("/api/v1/terra/ablation", { method: "POST", body: JSON.stringify(request) })));
  }

  async function runCounterfactual() {
    const body = { ...request, overrides: { reaction_delay_hours: 6, price_impact_coefficient: 0.18 } };
    await perform(async () => setExperiment(await api<ExperimentResult>("/api/v1/terra/counterfactual", { method: "POST", body: JSON.stringify(body) })));
  }

  async function perform(action: () => Promise<void>) {
    try {
      setBusy(true);
      setError(null);
      await action();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Experiment failed.");
    } finally {
      setBusy(false);
    }
  }

  const manifest = status?.datasets.find((dataset) => dataset.dataset_version === datasetVersion) ?? status?.datasets[0] ?? null;
  const latest = observations.at(-1);
  return (
    <div className="shell terraShell">
      <aside className="sidebar terraSidebar">
        <div className="brand"><span className="brandMark">DS</span><div><strong>DeFiStress</strong><small>HISTORICAL LAB</small></div></div>
        <div className="caseSwitch" aria-label="Case study selector">
          <span className="activeCase">Terra 2022</span>
          <Link href="/overview">Aave V3</Link>
        </div>
        <nav>
          {nav.map(([path, label]) => <Link key={path} href={`/terra/${path}`} className={section === path ? "active" : ""}><span className="navDot" />{label}</Link>)}
        </nav>
        <div className="sidebarFoot"><span className={`statusDot ${error ? "amber" : "green"}`} />API {error ? "attention" : "connected"}<small>Terra model 2.0</small></div>
      </aside>
      <main>
        <header className="topbar terraTopbar">
          <div><p className="eyebrow">TERRA CLASSIC · MAY 2022</p><h1>{title(section)}</h1></div>
          <div className="headerMeta"><span className={`modeBadge ${(manifest?.status ?? "FIXTURE").toLowerCase()}`}>{manifest ? terraStatusLabel(manifest.status) : "LOADING"}</span><span className="safety">Historical replay — not a prediction</span></div>
        </header>
        {error ? <div className="errorBanner"><strong>Research API error.</strong> {error}<button onClick={() => void load()}>Retry</button></div> : null}
        {busy && !status ? <div className="loading"><span />Loading cutoff-safe research state…</div> : null}
        {status && manifest ? (
          <section className="content">
            <div className={`dataBanner ${manifest.status.toLowerCase()}`}>
              <strong>{terraStatusLabel(manifest.status)}</strong>
              {manifest.status === "FIXTURE"
                ? status.fixture_warning
                : `Dataset ${manifest.dataset_version} is selected. Inspect provenance before presenting empirical claims.`}
            </div>
            <div className="datasetToolbar">
              <label>
                Research dataset
                <select
                  value={datasetVersion}
                  onChange={(event) => {
                    const next = event.target.value;
                    setDatasetVersion(next);
                    setReplay(null);
                    setBenchmark(null);
                    setExperiment(null);
                    void perform(() => loadDataset(next));
                  }}
                >
                  {status.datasets.map((dataset) => (
                    <option key={dataset.dataset_version} value={dataset.dataset_version}>
                      {dataset.dataset_version} · {terraStatusLabel(dataset.status)}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            {section === "overview" ? <Overview manifest={manifest} latest={latest} sources={status.historical_sources} /> : null}
            {section === "historical-data" ? <HistoricalData rows={observations} manifest={manifest} /> : null}
            {section === "wallet-dynamics" ? <WalletDynamics cohorts={cohorts} rows={observations} replay={replay} /> : null}
            {section === "model-lab" ? <ModelLab model={model} setModel={setModel} seed={seed} setSeed={setSeed} reactionDelay={reactionDelay} setReactionDelay={setReactionDelay} priceImpact={priceImpact} setPriceImpact={setPriceImpact} busy={busy} onRun={runReplay} replay={replay} /> : null}
            {section === "replay" ? <ReplayScreen replay={replay} busy={busy} onRun={runReplay} /> : null}
            {section === "benchmark" ? <BenchmarkScreen benchmark={benchmark} busy={busy} onRun={runBenchmark} /> : null}
            {section === "ablation" ? <AblationScreen experiment={experiment} busy={busy} onRun={runAblation} /> : null}
            {section === "counterfactual" ? <CounterfactualScreen experiment={experiment} busy={busy} onRun={runCounterfactual} /> : null}
            {section === "provenance" ? <Provenance manifest={manifest} sources={status.historical_sources} /> : null}
          </section>
        ) : null}
      </main>
    </div>
  );
}

function Overview({ manifest, latest, sources }: { manifest: TerraManifest; latest?: TerraObservation; sources: Status["historical_sources"] }) {
  return <><SectionLead title="TerraUSD / LUNA — May 2022" text="Can models frozen before the collapse reproduce the subsequent nonlinear dynamics without seeing evaluation-period ground truth?" /><div className="researchFlow"><span>PRE-CRISIS DATA</span><b>→</b><span>FREEZE AT T0</span><b>→</b><span>REPLAY</span><b>→</b><span>GROUND TRUTH</span><b>→</b><span>VALIDATION</span></div><div className="metricGrid wide"><Metric label="Calibration cutoff" value="May 06 · 23:59 UTC" detail="Configurable T0" /><Metric label="Evaluation" value="May 07 → May 13" detail="168 hourly observations" /><Metric label="Data status" value={manifest.status} detail="Read this badge before presenting" /><Metric label="UST price" value={latest ? `$${latest.ust_price.toFixed(3)}` : "—"} detail="Latest selected dataset row" /><Metric label="LUNA price" value={latest ? `$${latest.luna_price.toFixed(4)}` : "—"} /><Metric label="Backing ratio" value={latest ? latest.backing_ratio.toFixed(3) : "—"} detail="Risk indicator, not a guarantee" /></div><section className="panel"><header><div><p className="eyebrow">SOURCE AVAILABILITY</p><h3>Canonical-on-chain first</h3></div></header><div className="sourceGrid">{sources.map((source) => <div className="sourceCard" key={source.source}><span className={`modeBadge ${source.status.toLowerCase()}`}>{source.status}</span><strong>{source.source}</strong><p>{source.reason}</p></div>)}</div></section></>;
}

function HistoricalData({ rows, manifest }: { rows: TerraObservation[]; manifest: TerraManifest }) {
  const source = manifest.status === "FIXTURE" ? "Synthetic fixture" : "Dataset manifest";
  return <><SectionLead title="Historical Data" text="Every chart carries its source status. Fixture charts demonstrate the software and must not be cited as historical evidence." /><div className="twoCol"><HistoricalChart rows={rows} field="ust_price" title="UST / USD" source={source} /><HistoricalChart rows={rows} field="luna_price" title="LUNA / USD" source={source} /><HistoricalChart rows={rows} field="ust_supply" title="UST supply" source={source} /><HistoricalChart rows={rows} field="luna_supply" title="LUNA supply" source={source} /><HistoricalChart rows={rows} field="anchor_total_deposits" title="Anchor deposits" source={source} /><HistoricalChart rows={rows} field="anchor_withdrawal_flow" title="Anchor withdrawals" source={source} /><HistoricalChart rows={rows} field="backing_ratio" title="Backing ratio" source={source} /><HistoricalChart rows={rows} field="terra_dex_liquidity" title="Terra DEX liquidity" source={source} /></div></>;
}

function WalletDynamics({ cohorts, rows, replay }: { cohorts: Cohorts | null; rows: TerraObservation[]; replay: TerraReplay | null }) {
  return <><SectionLead title="Wallet and Run Dynamics" text="Addresses are pseudonymized by default. The bundled cohort split is synthetic and explicitly labelled." />{cohorts ? <section className="panel"><header><div><p className="eyebrow">{cohorts.status}</p><h3>Anchor balances by cohort</h3></div></header>{cohorts.warning ? <p className="researchWarning">{cohorts.warning}</p> : null}<div className="cohortGrid">{cohorts.cohorts.map((row) => <Metric key={row.cohort} label={row.cohort} value={money(row.anchor_balance)} detail={`${(row.share * 100).toFixed(0)}% modeled share`} />)}</div></section> : null}<div className="twoCol"><HistoricalChart rows={rows} field="anchor_withdrawal_flow" title="Aggregate withdrawals" source="Fixture cohort layer" /><HistoricalChart rows={rows} field="top10_anchor_share" title="Top-10 holder concentration" source="Fixture cohort layer" /></div>{replay ? <section className="panel"><header><div><p className="eyebrow">WHY DID THIS HAPPEN?</p><h3>Representative agent explanations</h3></div></header><div className="eventList">{replay.agent_events.slice(0, 12).map((event, index) => <div key={`${String(event.timestamp)}-${index}`}><span>{String(event.timestamp).slice(5, 16)}</span><strong>{String(event.cohort)}</strong><code>{String(event.action)}</code><b>{money(Number(event.amount))}</b></div>)}</div></section> : null}</>;
}

function ModelLab(props: { model: string; setModel: (value: string) => void; seed: number; setSeed: (value: number) => void; reactionDelay: number; setReactionDelay: (value: number) => void; priceImpact: number; setPriceImpact: (value: number) => void; busy: boolean; onRun: () => Promise<void>; replay: TerraReplay | null }) {
  return <><SectionLead title="Model Lab" text="All calibration inputs are frozen at or before T0. Post-cutoff observations remain inaccessible until validation." /><section className="panel"><header><div><p className="eyebrow">TERRA MAY 2022 HISTORICAL REPLAY</p><h3>Experiment configuration</h3></div></header><div className="formGrid"><label className="formField">Model<select value={props.model} onChange={(event) => props.setModel(event.target.value)}><option>THRESHOLD</option><option>HAZARD</option><option>SYSTEM_DYNAMICS</option><option>ABM</option></select></label><label className="formField">Seed<input type="number" value={props.seed} onChange={(event) => props.setSeed(Number(event.target.value))} /></label><label className="formField">Reaction delay (hours)<input type="number" min="0" max="72" value={props.reactionDelay} onChange={(event) => props.setReactionDelay(Number(event.target.value))} /></label><label className="formField">Price-impact coefficient<input type="number" min="0" max="2" step="0.01" value={props.priceImpact} onChange={(event) => props.setPriceImpact(Number(event.target.value))} /></label></div><div className="definition"><div><dt>Cutoff</dt><dd>2022-05-06 23:59:59 UTC</dd></div><div><dt>Evaluation</dt><dd>2022-05-07 → 2022-05-13 UTC</dd></div><div><dt>Mode</dt><dd>OUT_OF_SAMPLE_REPLAY</dd></div></div><button className="primary" disabled={props.busy} onClick={() => void props.onRun()}>{props.busy ? "Running…" : "Run Terra May 2022 Historical Replay"}</button></section>{props.replay ? <RunSummary replay={props.replay} /> : null}</>;
}

function ReplayScreen({ replay, busy, onRun }: { replay: TerraReplay | null; busy: boolean; onRun: () => Promise<void> }) {
  if (!replay) return <Empty title="No replay yet" text="Run the default cutoff-safe ABM preset, then reveal ground truth and validation metrics." action="Run historical replay" busy={busy} onRun={onRun} />;
  return <><RunSummary replay={replay} /><div className="twoCol"><ReplayChart replay={replay} field="ust_price" title="Actual vs simulated UST" /><ReplayChart replay={replay} field="luna_price" title="Actual vs simulated LUNA" /><ReplayChart replay={replay} field="luna_supply" title="LUNA supply" /><ReplayChart replay={replay} field="anchor_withdrawal_flow" title="Anchor withdrawals" /><ReplayChart replay={replay} field="backing_ratio" title="Backing ratio" /></div><a className="download" href={`${API_URL}/api/v1/terra/export/${replay.id}`}>Download reproducible experiment ZIP</a></>;
}

function BenchmarkScreen({ benchmark, busy, onRun }: { benchmark: TerraBenchmark | null; busy: boolean; onRun: () => Promise<void> }) {
  return <><SectionLead title="Model Benchmark" text="Models share one cutoff and ground truth. Metrics are neutral; no composite score or automatic winner is used." /><button className="primary" disabled={busy} onClick={() => void onRun()}>{busy ? "Running four models…" : "Run all four model families"}</button>{benchmark ? <section className="panel benchmarkPanel"><div className="tableWrap"><table><thead><tr><th>Model</th><th>UST RMSE</th><th>LUNA RMSE</th><th>Supply error</th><th>Withdrawal RMSE</th><th>Depeg timing</th><th>Death spiral timing</th><th>Runtime</th></tr></thead><tbody>{benchmark.benchmark_results.map((row) => <tr key={String(row.model)}><td><strong>{String(row.model)}</strong></td><td>{formatMetric(row.RMSE_UST)}</td><td>{formatMetric(row.RMSE_LUNA)}</td><td>{formatMetric(row.supply_error)}</td><td>{formatMetric(row.withdrawal_error)}</td><td>{formatHours(row.depeg_timing_error)}</td><td>{formatHours(row.death_spiral_timing_error)}</td><td>{formatMetric(row.runtime_seconds)}s</td></tr>)}</tbody></table></div><p className="researchWarning">{benchmark.interpretation}</p></section> : null}</>;
}

function AblationScreen({ experiment, busy, onRun }: { experiment: ExperimentResult | null; busy: boolean; onRun: () => Promise<void> }) {
  return <><SectionLead title="Ablation Study" text="Remove one mechanism at a time while holding the dataset, cutoff, seed, and validation definitions fixed." /><button className="primary" disabled={busy} onClick={() => void onRun()}>{busy ? "Running variants…" : "Run six ABM variants"}</button>{experiment?.ablation_results ? <section className="panel"><div className="tableWrap"><table><thead><tr><th>Variant</th><th>UST RMSE</th><th>Withdrawal RMSE</th><th>Death spiral timing</th></tr></thead><tbody>{experiment.ablation_results.map((row) => <tr key={row.variant}><td>{row.variant}</td><td>{formatMetric(row.metrics.RMSE_UST)}</td><td>{formatMetric(row.metrics.RMSE_WITHDRAWAL)}</td><td>{formatHours(row.metrics.death_spiral_timing_error_hours)}</td></tr>)}</tbody></table></div></section> : null}</>;
}

function CounterfactualScreen({ experiment, busy, onRun }: { experiment: ExperimentResult | null; busy: boolean; onRun: () => Promise<void> }) {
  const counterfactual = experiment?.counterfactual_replay;
  return <><SectionLead title="Counterfactual" text="What if large holders reacted six hours later and liquidity impact were lower? This changes assumptions, never historical ground truth." /><section className="panel counterfactualCallout"><p className="eyebrow">WHAT-IF CONTROLS</p><h3>Reaction delay +6h · price impact 0.18</h3><p>Historical replay is preserved beside the altered simulation.</p><button className="primary" disabled={busy} onClick={() => void onRun()}>{busy ? "Running…" : "Run counterfactual"}</button></section>{experiment?.label ? <div className="fixtureBanner"><strong>COUNTERFACTUAL</strong>{experiment.label}</div> : null}{counterfactual ? <div className="twoCol"><ReplayChart replay={counterfactual} field="ust_price" title="Counterfactual UST vs ground truth" /><ReplayChart replay={counterfactual} field="luna_supply" title="Counterfactual LUNA supply" /></div> : null}</>;
}

function Provenance({ manifest, sources }: { manifest: TerraManifest; sources: Status["historical_sources"] }) {
  return <><SectionLead title="Data Provenance" text="Every dataset is versioned, hashed, quality-checked, and linked to source metadata. Unavailable sources remain visible." /><section className="panel"><dl className="definition"><div><dt>Status</dt><dd>{manifest.status}</dd></div><div><dt>Version</dt><dd>{manifest.dataset_version}</dd></div><div><dt>Rows</dt><dd>{manifest.row_count}</dd></div><div><dt>Time range</dt><dd>{manifest.start_timestamp} → {manifest.end_timestamp}</dd></div><div><dt>Dataset hash</dt><dd>{manifest.dataset_hash}</dd></div><div><dt>Transform</dt><dd>{manifest.transformation_version}</dd></div><div><dt>Git commit</dt><dd>{manifest.git_commit}</dd></div></dl></section><section className="panel"><header><div><p className="eyebrow">QUALITY REPORT</p><h3>Validation and missingness</h3></div></header><pre>{JSON.stringify(manifest.quality_report, null, 2)}</pre></section><section className="panel"><header><div><p className="eyebrow">INTEGRATION BOUNDARIES</p><h3>Historical source status</h3></div></header>{sources.map((source) => <div className="quality" key={source.source}><strong>{source.status} · {source.source}</strong>{source.reason}</div>)}</section></>;
}

function RunSummary({ replay }: { replay: TerraReplay }) {
  return <section className="panel runSummary"><header><div><p className="eyebrow">{replay.metadata.mode}</p><h3>{replay.model.name} replay complete</h3></div><span className="modeBadge real">LEAKAGE {replay.metadata.leakage_check_status.status}</span></header><div className="metricGrid"><Metric label="Early-warning risk" value={`${replay.early_warning.score.toFixed(0)} / 100`} detail="Model-implied signal" /><Metric label="UST RMSE" value={formatMetric(replay.validation_metrics.RMSE_UST)} /><Metric label="LUNA RMSE" value={formatMetric(replay.validation_metrics.RMSE_LUNA)} /><Metric label="Death spiral timing" value={formatHours(replay.validation_metrics.death_spiral_timing_error_hours)} /></div><div className="contributionGrid">{Object.entries(replay.early_warning.contributions).map(([name, value]) => <div key={name}><span>{name.replaceAll("_", " ")}</span><strong>+{value.toFixed(1)}</strong></div>)}</div><p className="researchWarning">{replay.early_warning.label}. Dataset status: {replay.dataset.status}.</p></section>;
}

function SectionLead({ title: heading, text }: { title: string; text: string }) { return <div className="sectionLead"><div><p className="eyebrow">REPRODUCIBLE RESEARCH WORKFLOW</p><h2>{heading}</h2><p>{text}</p></div></div>; }
function Metric({ label, value, detail }: { label: string; value: string; detail?: string }) { return <article className="metricCard"><p>{label}</p><strong>{value}</strong>{detail ? <small>{detail}</small> : null}</article>; }
function Empty({ title: heading, text, action, busy, onRun }: { title: string; text: string; action: string; busy: boolean; onRun: () => Promise<void> }) { return <div className="emptyState"><div className="pulse"><i /></div><p className="eyebrow">HISTORICAL REPLAY</p><h2>{heading}</h2><p>{text}</p><button className="primary" disabled={busy} onClick={() => void onRun()}>{action}</button></div>; }
function title(section: string) { return ({ overview: "Event Overview", "historical-data": "Historical Data", "wallet-dynamics": "Wallet / Run Dynamics", "model-lab": "Model Lab", replay: "Historical Replay", benchmark: "Model Benchmark", ablation: "Ablation Study", counterfactual: "Counterfactual", provenance: "Data Provenance" } as Record<string, string>)[section] ?? "Event Overview"; }
function formatMetric(value: unknown) { return typeof value === "number" && Number.isFinite(value) ? new Intl.NumberFormat("en-US", { maximumFractionDigits: 4 }).format(value) : "—"; }
function formatHours(value: unknown) { return typeof value === "number" && Number.isFinite(value) ? `${value > 0 ? "+" : ""}${value.toFixed(1)}h` : "Not detected"; }


function preferredDataset(datasets: TerraManifest[]): TerraManifest {
  const priority: TerraManifest["status"][] = ["REAL_HISTORICAL", "PARTIAL", "QUALITY_WARNING", "FIXTURE", "UNAVAILABLE"];
  for (const status of priority) {
    const match = datasets.find((dataset) => dataset.status === status);
    if (match) return match;
  }
  throw new Error("No Terra research dataset is available.");
}
