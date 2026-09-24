"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import type {
  TerraBenchmark,
  TerraEarlyWarning,
  TerraExtendedObservation,
  TerraHistoricalFit,
  TerraManifest,
  TerraMechanismCheck,
  TerraObservation,
  TerraReplay,
  TerraStressResult,
} from "@/lib/api";
import { API_URL, api, money } from "@/lib/api";
import { terraStatusLabel } from "@/lib/terra";
import {
  EarlyWarningTimeline,
  ExtendedHistoricalChart,
  FitComparisonChart,
  HistoricalChart,
  ReplayChart,
  StressFanChart,
} from "./TerraCharts";

const nav = [
  ["overview", "Overview"],
  ["historical-data", "Historical Data"],
  ["historical-fit", "Historical Fit"],
  ["early-warning", "Early Warning"],
  ["stress-test", "Stress Test"],
  ["model-comparison", "Model Comparison"],
  ["mechanism-check", "Mechanism Check"],
  ["data-sources", "Data Sources"],
  ["model-lab", "Advanced · Model Lab"],
  ["replay", "Advanced · Strict Replay"],
  ["ablation", "Advanced · Ablation"],
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

type DemoData = {
  dataset: { dataset_version: string; status: string; row_count: number; quality_classes: Record<string, string>; quarantined_variables: string[] };
  observations: TerraExtendedObservation[];
};

const defaultStress = {
  withdrawal_pressure: 1,
  liquidity_capacity: 0.55,
  arbitrage_capacity: 0.55,
  confidence_sensitivity: 1,
  outside_holder_exit: 0.004,
  reserve_intervention: 0,
  horizon_hours: 168,
  initial_shock: 0.015,
  redemption_friction: 0.02,
  runs: 100,
  seed: 20220506,
};

export function TerraDashboard({ section }: { section: string }) {
  const [status, setStatus] = useState<Status | null>(null);
  const [datasetVersion, setDatasetVersion] = useState(defaultRequest.dataset_version);
  const [observations, setObservations] = useState<TerraObservation[]>([]);
  const [cohorts, setCohorts] = useState<Cohorts | null>(null);
  const [replay, setReplay] = useState<TerraReplay | null>(null);
  const [benchmark, setBenchmark] = useState<TerraBenchmark | null>(null);
  const [experiment, setExperiment] = useState<ExperimentResult | null>(null);
  const [demoData, setDemoData] = useState<DemoData | null>(null);
  const [historicalFit, setHistoricalFit] = useState<TerraHistoricalFit | null>(null);
  const [earlyWarning, setEarlyWarning] = useState<TerraEarlyWarning | null>(null);
  const [earlyWarningMode, setEarlyWarningMode] = useState<"RETROSPECTIVE" | "CUTOFF_SAFE">("RETROSPECTIVE");
  const [stress, setStress] = useState<TerraStressResult | null>(null);
  const [stressForm, setStressForm] = useState(defaultStress);
  const [mechanism, setMechanism] = useState<TerraMechanismCheck | null>(null);
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
      const [statusData, data, fit, warning, stressResult, mechanismResult] = await Promise.all([
        api<Status>("/api/v1/terra/status"),
        api<DemoData>("/api/v1/terra/demo/historical-data"),
        api<TerraHistoricalFit>("/api/v1/terra/historical-fit/latest"),
        api<TerraEarlyWarning>("/api/v1/terra/early-warning?mode=RETROSPECTIVE"),
        api<TerraStressResult>("/api/v1/terra/stress-test/latest"),
        api<TerraMechanismCheck>("/api/v1/terra/mechanism-check"),
      ]);
      const preferred = preferredDataset(statusData.datasets);
      setStatus(statusData);
      setDemoData(data);
      setHistoricalFit(fit);
      setEarlyWarning(warning);
      setStress(stressResult);
      setMechanism(mechanismResult);
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

  async function changeEarlyWarningMode(mode: "RETROSPECTIVE" | "CUTOFF_SAFE") {
    setEarlyWarningMode(mode);
    await perform(async () => setEarlyWarning(await api<TerraEarlyWarning>(`/api/v1/terra/early-warning?mode=${mode}`)));
  }

  async function runHistoricalFit() {
    await perform(async () => setHistoricalFit(await api<TerraHistoricalFit>("/api/v1/terra/historical-fit", { method: "POST" })));
  }

  async function runStress(runs: number) {
    const body = { ...stressForm, runs };
    await perform(async () => setStress(await api<TerraStressResult>("/api/v1/terra/stress-test", { method: "POST", body: JSON.stringify(body) })));
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
          <div className="headerMeta"><span className="modeBadge partial">READY WITH LIMITATIONS</span><span className="safety">Historical reconstruction and counterfactual stress — not a forecast</span></div>
        </header>
        {error ? <div className="errorBanner"><strong>Research API error.</strong> {error}<button onClick={() => void load()}>Retry</button></div> : null}
        {busy && !status ? <div className="loading"><span />Loading cutoff-safe research state…</div> : null}
        {status && manifest ? (
          <section className="content">
            <div className="dataBanner partial">
              <strong>HISTORICAL DATA · READY WITH LIMITATIONS</strong>
              1,776 hourly rows are available. Missing DEX depth and LFG peg-defense remain explicitly unavailable.
            </div>
            {section === "model-lab" || section === "replay" || section === "ablation" ? <div className="datasetToolbar">
              <label>
                Advanced legacy dataset
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
            </div> : null}
            {section === "overview" && demoData ? <DemoOverview data={demoData} fit={historicalFit} warning={earlyWarning} stress={stress} /> : null}
            {section === "historical-data" && demoData ? <DemoHistoricalData data={demoData} /> : null}
            {section === "historical-fit" ? <HistoricalFitScreen fit={historicalFit} busy={busy} onRun={runHistoricalFit} /> : null}
            {section === "early-warning" ? <EarlyWarningScreen warning={earlyWarning} mode={earlyWarningMode} busy={busy} onMode={changeEarlyWarningMode} /> : null}
            {section === "stress-test" ? <StressTestScreen result={stress} form={stressForm} setForm={setStressForm} busy={busy} onRun={runStress} /> : null}
            {section === "model-comparison" ? <ModelComparisonScreen fit={historicalFit} /> : null}
            {section === "mechanism-check" ? <MechanismCheckScreen result={mechanism} /> : null}
            {section === "data-sources" && demoData ? <DataSourcesScreen data={demoData} sources={status.historical_sources} /> : null}
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

function DemoOverview({ data, fit, warning, stress }: { data: DemoData; fit: TerraHistoricalFit | null; warning: TerraEarlyWarning | null; stress: TerraStressResult | null }) {
  const latest = data.observations.at(-1);
  return <><SectionLead title="Three questions, three separate layers" text="Terra validates the crisis-modeling workflow against history; Aave V3 remains the contemporary lending–DEX stress-testing case." /><div className="researchFlow"><span>WHAT HAPPENED?</span><b>→</b><span>CAN THE MODEL RECONSTRUCT IT?</span><b>→</b><span>WHAT IF CONDITIONS CHANGE?</span></div><div className="layerGrid"><article className="layerCard"><p className="eyebrow">01 · HISTORICAL FIT</p><h3>Reconstruct the known crisis</h3><p>Jointly compares UST, LUNA and supply paths. This is calibration, not forecasting.</p><strong>{fit ? `UST RMSE ${fit.metrics.ust_price.rmse.toFixed(3)}` : "Loading…"}</strong></article><article className="layerCard"><p className="eyebrow">02 · EARLY WARNING</p><h3>Measure rising risk</h3><p>Retrospective and cutoff-safe scores remain distinct, including failed or late warnings.</p><strong>{warning ? `${warning.leakage_audit.checked_timestamps.toLocaleString()} hourly checks` : "Loading…"}</strong></article><article className="layerCard"><p className="eyebrow">03 · STRESS TEST</p><h3>Change market assumptions</h3><p>Liquidity, arbitrage, confidence, holder exits and reserve support are scenario controls.</p><strong>{stress ? `${stress.runs} seeded runs` : "Loading…"}</strong></article></div><div className="metricGrid wide"><Metric label="Historical hours" value={data.dataset.row_count.toLocaleString()} detail="Mar 1 → May 13" /><Metric label="Latest UST" value={latest ? `$${latest.ust_price.toFixed(3)}` : "—"} /><Metric label="Latest LUNA" value={latest ? `$${latest.luna_price.toFixed(6)}` : "—"} /><Metric label="LUNA supply" value={latest?.luna_supply ? new Intl.NumberFormat("en-US", { notation: "compact" }).format(latest.luna_supply) : "—"} /><Metric label="Data status" value="READY" detail="With documented limitations" /><Metric label="Mainnet case" value="Aave V3" detail="Preserved and functional" /></div></>;
}

function DemoHistoricalData({ data }: { data: DemoData }) {
  const rows = data.observations;
  return <><SectionLead title="What actually happened?" text="Observed state and event-flow series are shown with their quality class. Missing history stays missing; fixture cohorts never appear here." /><div className="eventStrip"><span>May 7 · UST &lt; $0.995</span><span>May 9 · UST &lt; $0.95</span><span>May 11–13 · supply explosion</span></div><div className="twoCol"><ExtendedHistoricalChart rows={rows} field="ust_price" title="UST / USD" quality="OBSERVED + LOWER-FREQUENCY CARRY BEFORE MAY" /><ExtendedHistoricalChart rows={rows} field="luna_price" title="LUNA / USD" quality="OBSERVED + LOWER-FREQUENCY CARRY BEFORE MAY" /><ExtendedHistoricalChart rows={rows} field="luna_supply" title="LUNA supply" quality="OBSERVED MAY 1 ONWARD" /><ExtendedHistoricalChart rows={rows} field="anchor_total_deposits" title="Anchor deposits" quality="OBSERVED STATE" /><ExtendedHistoricalChart rows={rows} field="anchor_withdrawal_flow" title="Anchor withdrawal events" quality="OBSERVED MAY 6 ONWARD · MISSING EARLIER" /><ExtendedHistoricalChart rows={rows} field="backing_ratio" title="Backing ratio" quality="DERIVED MAY 1 ONWARD" /></div></>;
}

function HistoricalFitScreen({ fit, busy, onRun }: { fit: TerraHistoricalFit | null; busy: boolean; onRun: () => Promise<void> }) {
  if (!fit) return <Empty title="Historical Fit is not built" text="Run the bounded deterministic calibration against the known crisis." action="Build Historical Fit" busy={busy} onRun={onRun} />;
  return <><SectionLead title="Historical Fit — Calibrated Feedback Reconstruction" text="Observed historical flows are used where available. This is in-sample historical reconstruction, not forecasting; unavailable pre-coverage events are not treated as observed zero." /><div className="actionRow"><button className="primary" disabled={busy} onClick={() => void onRun()}>{busy ? "Calibrating…" : "Rebuild Historical Fit"}</button><span className="modeBadge partial">FEEDBACK RECONSTRUCTION · NOT FORECAST</span></div><div className="metricGrid"><Metric label="UST RMSE" value={fit.metrics.ust_price.rmse.toFixed(4)} /><Metric label="UST correlation" value={fit.metrics.ust_price.correlation.toFixed(3)} /><Metric label="LUNA log-RMSE" value={fit.metrics.luna_price.log_rmse.toFixed(3)} /><Metric label="Final supply error" value={`${(fit.metrics.luna_supply.final_relative_error * 100).toFixed(2)}%`} /></div><div className="twoCol"><FitComparisonChart fit={fit} field="ust_price" title="UST price" /><FitComparisonChart fit={fit} field="luna_price" title="LUNA price" logarithmic /><FitComparisonChart fit={fit} field="luna_supply" title="LUNA supply" logarithmic /></div><section className="panel"><header><div><p className="eyebrow">CALIBRATION RECORD</p><h3>Bounded, interpretable parameters</h3></div></header><div className="parameterGrid">{Object.entries(fit.parameters).map(([name, value]) => <div key={name}><span>{name.replaceAll("_", " ")}</span><strong>{value.toPrecision(4)}</strong><small>{fit.bounds[name]?.join(" → ")}</small></div>)}</div><p className="researchWarning">Objective: {fit.objective.formula}. No observed future price or supply is used as the next simulated state.</p></section></>;
}

function EarlyWarningScreen({ warning, mode, busy, onMode }: { warning: TerraEarlyWarning | null; mode: "RETROSPECTIVE" | "CUTOFF_SAFE"; busy: boolean; onMode: (mode: "RETROSPECTIVE" | "CUTOFF_SAFE") => Promise<void> }) {
  if (!warning) return <div className="loading"><span />Loading hourly warning timeline…</div>;
  const severe = warning.lead_times.ust_below_0_9;
  const latest = warning.timeline.at(-1);
  const featureValue = (name: string) => latest?.components[name] === undefined ? "Not available" : latest.components[name].toFixed(3);
  return <><SectionLead title="Did warning signs appear before the severe depeg?" text="Every hourly score records active and unavailable components, then renormalizes weights only across available evidence." /><div className="presetRow" role="group" aria-label="Early-warning mode"><button className={mode === "RETROSPECTIVE" ? "selected" : ""} disabled={busy} onClick={() => void onMode("RETROSPECTIVE")}>Retrospective</button><button className={mode === "CUTOFF_SAFE" ? "selected" : ""} disabled={busy} onClick={() => void onMode("CUTOFF_SAFE")}>Cutoff-Safe</button></div><EarlyWarningTimeline warning={warning} /><div className="metricGrid"><Metric label="Leakage audit" value={warning.leakage_audit.status} detail={`${warning.leakage_audit.future_perturbation.cutoffs_tested} future-perturbation cutoffs`} /><Metric label="Anchor Deposit Stress" value={featureValue("anchor_deposit_stress")} detail="Trailing 24h deterioration" /><Metric label="Holder Concentration" value={featureValue("holder_concentration")} detail="Evidence ends May 6" /><Metric label="High warning vs UST < $0.90" value={severe?.high.wording ?? "Not detected"} /><Metric label="Crisis warning vs UST < $0.90" value={severe?.crisis.wording ?? "Not detected"} /><Metric label="Mode" value={warning.mode.replace("_", " ")} /></div><section className="panel"><p className="researchWarning">{warning.interpretation}</p><div className="parameterGrid">{Object.entries(warning.weights).map(([name, value]) => <div key={name}><span>{name.replaceAll("_", " ")}</span><strong>{(value * 100).toFixed(0)}%</strong></div>)}</div></section></>;
}

function StressTestScreen({ result, form, setForm, busy, onRun }: { result: TerraStressResult | null; form: typeof defaultStress; setForm: (value: typeof defaultStress) => void; busy: boolean; onRun: (runs: number) => Promise<void> }) {
  const controls: Array<[keyof typeof defaultStress, string, number, number, number]> = [["withdrawal_pressure", "Withdrawal pressure", 0, 5, 0.1], ["liquidity_capacity", "Liquidity capacity", 0, 2, 0.05], ["arbitrage_capacity", "Arbitrage capacity", 0, 2, 0.05], ["confidence_sensitivity", "Confidence sensitivity", 0, 5, 0.1], ["outside_holder_exit", "Outside-holder exit", 0, 0.1, 0.001], ["reserve_intervention", "Reserve intervention", 0, 1, 0.05], ["redemption_friction", "Redemption friction", 0, 0.2, 0.005]];
  const applyPreset = (name: "BASELINE" | "ADVERSE" | "SEVERE") => {
    const preset = result?.preset_definitions[name];
    if (preset) setForm({ ...form, ...preset });
  };
  return <><SectionLead title="What happens if conditions get worse?" text="Initial state comes from historical Terra data. Liquidity, outside-holder selling, redemption friction, and reserve support are scenario assumptions." /><section className="panel"><div className="presetRow" role="group" aria-label="Stress presets"><button disabled={busy || !result} onClick={() => applyPreset("BASELINE")}>Baseline</button><button disabled={busy || !result} onClick={() => applyPreset("ADVERSE")}>Adverse</button><button disabled={busy || !result} onClick={() => applyPreset("SEVERE")}>Severe</button></div><div className="formGrid">{controls.map(([name, label, min, max, step]) => <label className="formField" key={name}>{label}<input aria-label={label} type="number" min={min} max={max} step={step} value={form[name]} onChange={(event) => setForm({ ...form, [name]: Number(event.target.value) })} /></label>)}</div><div className="actionRow"><button disabled={busy} onClick={() => void onRun(1)}>Run one scenario</button><button className="primary" disabled={busy} onClick={() => void onRun(100)}>Run 100 scenarios</button></div></section>{result ? <><div className="metricGrid"><Metric label="Historical start" value={result.initial_state_timestamp.slice(0, 16).replace("T", " ")} detail="Audited Terra state" /><Metric label="Runs" value={String(result.runs)} /><Metric label="Collapse count" value={`${result.summary.collapse_count} / ${result.runs}`} detail="Count, not probability" /><Metric label="Median minimum UST" value={`$${result.summary.minimum_ust.median.toFixed(3)}`} /><Metric label="Median minimum LUNA" value={`$${result.summary.minimum_luna.median.toPrecision(4)}`} /><Metric label="Median final supply" value={new Intl.NumberFormat("en-US", { notation: "compact" }).format(result.summary.final_luna_supply.median)} /></div><StressFanChart result={result} /><section className="panel"><header><div><p className="eyebrow">ADVANCED DETAILS</p><h3>{result.counterfactual_conversion.name.replaceAll("_", " ")}</h3></div></header><p>{result.counterfactual_conversion.claim_boundary}</p><code>{result.counterfactual_conversion.formula}</code></section><p className="researchWarning">{result.summary.wording} This is not a probability estimate.</p></> : null}</>;
}

function ModelComparisonScreen({ fit }: { fit: TerraHistoricalFit | null }) {
  return <><SectionLead title="What does each model result establish?" text="The dashboard does not auto-declare a winner. Each layer answers a different research question and carries a different evidence standard." /><section className="panel"><div className="tableWrap"><table><thead><tr><th>Model layer</th><th>Evaluation role</th><th>Main result</th><th>Claim boundary</th></tr></thead><tbody><tr><td>Strict OOS V2</td><td>Frozen pre-crisis replay</td><td>Preserved negative early-warning evidence</td><td>Does not forecast the historical collapse</td></tr><tr><td>Conditional V4</td><td>Post-trigger mechanism replay</td><td>High directional co-movement; misses severity</td><td>Not a prediction</td></tr><tr><td>Historical Fit</td><td>Full-event calibration</td><td>{fit ? `UST RMSE ${fit.metrics.ust_price.rmse.toFixed(4)}` : "Loading…"}</td><td>In-sample reconstruction</td></tr><tr><td>Stress Test</td><td>Counterfactual scenarios</td><td>Assumption-dependent path distribution</td><td>Collapse count is not probability</td></tr></tbody></table></div></section></>;
}

function MechanismCheckScreen({ result }: { result: TerraMechanismCheck | null }) {
  if (!result) return <div className="loading"><span />Loading audited swap evidence…</div>;
  const direct = result.direct_event_output_gross_mint;
  const old = result.old_offchain_approximation;
  return <><SectionLead title="Does on-chain evidence support the modeled mint mechanism?" text="Terra Core burns the UST offer and mints the LUNA recipient output plus fee output. This validates accounting identity, not price causality." /><div className="metricGrid"><Metric label="Audited swaps" value={result.raw_swap_rows.toLocaleString()} /><Metric label="Validation period" value={`${result.validation_window.start.slice(0, 10)} → ${result.validation_window.end.slice(0, 10)}`} detail={`${result.validation_window.aligned_hours} aligned hours`} /><Metric label="Gross mint identity" value={result.gross_mint_identity} /><Metric label="Direct-output correlation" value={direct.hourly_correlation.toFixed(6)} /><Metric label="Direct cumulative error" value={`${(direct.final_cumulative_relative_error * 100).toFixed(2)}%`} /></div><section className="panel"><div className="comparisonCallout"><div><span>Old off-chain approximation</span><strong>{(old.final_cumulative_relative_error * 100).toFixed(2)}% cumulative error</strong></div><b>→</b><div><span>Direct event output</span><strong>{(direct.final_cumulative_relative_error * 100).toFixed(2)}% cumulative error</strong></div></div><p className="researchWarning">{result.interpretation}</p></section></>;
}

function DataSourcesScreen({ data, sources }: { data: DemoData; sources: Status["historical_sources"] }) {
  return <><SectionLead title="Where does the evidence come from?" text="Observed, derived, proxy and unavailable channels remain visibly separate. Unavailable sources are limitations, not application failures." /><section className="panel"><header><div><p className="eyebrow">EXTENDED DATASET</p><h3>{data.dataset.dataset_version}</h3></div><span className="modeBadge partial">{data.dataset.status}</span></header><div className="sourceGrid">{Object.entries(data.dataset.quality_classes).map(([name, quality]) => <div className="sourceCard" key={name}><span className="modeBadge configured">{quality}</span><strong>{name.replaceAll("_", " ")}</strong></div>)}</div></section><section className="panel"><header><div><p className="eyebrow">UNAVAILABLE / SECONDARY CHANNELS</p><h3>Kept outside the primary historical fit</h3></div></header>{sources.slice(1).map((source) => <div className="quality" key={source.source}><strong>{source.status} · {source.source}</strong>{source.reason}</div>)}<div className="quality"><strong>UNAVAILABLE · Terra DEX depth</strong>No audited historical liquidity/depth series is available; stress controls are scenario assumptions.</div><div className="quality"><strong>UNAVAILABLE · LFG peg-defense flow</strong>Available reserve transfers do not identify actual peg-defense intervention.</div></section><section className="panel"><header><div><p className="eyebrow">QUARANTINED</p><h3>Legacy duplicate mappings excluded</h3></div></header><div className="runChips">{data.dataset.quarantined_variables.map((name) => <span key={name}>{name}</span>)}</div></section></>;
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
function title(section: string) { return ({ overview: "Research Overview", "historical-data": "Historical Data", "historical-fit": "Historical Fit", "early-warning": "Early Warning", "stress-test": "Stress Test", "model-comparison": "Model Comparison", "mechanism-check": "Mechanism Check", "data-sources": "Data Sources", "wallet-dynamics": "Wallet / Run Dynamics", "model-lab": "Model Lab", replay: "Strict Historical Replay", benchmark: "Model Benchmark", ablation: "Ablation Study", counterfactual: "Counterfactual", provenance: "Data Provenance" } as Record<string, string>)[section] ?? "Research Overview"; }
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
