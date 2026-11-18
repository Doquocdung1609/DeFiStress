"use client";

import {
  Area,
  AreaChart,
  ReferenceArea,
  ReferenceLine,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { TerraExtendedObservation, TerraObservation, TerraReplay } from "@/lib/api";
import type { TerraEarlyWarning, TerraHistoricalFit, TerraStressResult } from "@/lib/api";

const chartTooltip = {
  background: "#0b1e33",
  border: "1px solid #24425f",
  borderRadius: 8,
  color: "#edf7ff",
};

type ChartField = "ust_price" | "luna_price" | "ust_supply" | "luna_supply" | "anchor_total_deposits" | "anchor_withdrawal_flow" | "backing_ratio" | "terra_dex_liquidity" | "top10_anchor_share";

export function HistoricalChart({ rows, field, title, source }: { rows: TerraObservation[]; field: ChartField; title: string; source: string }) {
  const data = rows.map((row, index) => ({ index, value: row[field], timestamp: row.timestamp.slice(5, 13) }));
  return (
    <section className="panel terraChartPanel" title={`Source: ${source}`}>
      <header><div><p className="eyebrow">SOURCE: {source}</p><h3>{title}</h3></div></header>
      <div className="chart">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs><linearGradient id={`fill-${field}`} x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#31d4e8" stopOpacity={0.34} /><stop offset="95%" stopColor="#31d4e8" stopOpacity={0.02} /></linearGradient></defs>
            <CartesianGrid stroke="#16344c" strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" minTickGap={44} stroke="#7892aa" />
            <YAxis stroke="#7892aa" tickFormatter={compact} width={72} />
            <Tooltip contentStyle={chartTooltip} />
            <Area type="monotone" dataKey="value" stroke="#31d4e8" fill={`url(#fill-${field})`} isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

type ExtendedField = "ust_price" | "luna_price" | "ust_supply" | "luna_supply" | "anchor_total_deposits" | "anchor_withdrawal_flow" | "backing_ratio";

export function ExtendedHistoricalChart({ rows, field, title, quality }: { rows: TerraExtendedObservation[]; field: ExtendedField; title: string; quality: string }) {
  const data = rows.map((row) => ({ value: row[field] == null ? null : Number(row[field]), timestamp: row.timestamp.slice(5, 13) }));
  const missing = data.filter((point) => point.value === null).length;
  return <section className="panel terraChartPanel" title={`Quality: ${quality}`}><header><div><p className="eyebrow">{quality}</p><h3>{title}</h3></div><small>{missing} missing hours shown as gaps</small></header><div className="chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={data}><defs><linearGradient id={`extended-${field}`} x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#31d4e8" stopOpacity={0.34} /><stop offset="95%" stopColor="#31d4e8" stopOpacity={0.02} /></linearGradient></defs><CartesianGrid stroke="#16344c" strokeDasharray="3 3" /><XAxis dataKey="timestamp" minTickGap={44} stroke="#7892aa" /><YAxis stroke="#7892aa" tickFormatter={compact} width={72} /><Tooltip contentStyle={chartTooltip} /><Area type="monotone" dataKey="value" stroke="#31d4e8" fill={`url(#extended-${field})`} isAnimationActive={false} connectNulls={false} /></AreaChart></ResponsiveContainer></div></section>;
}

export function ReplayChart({ replay, field, title }: { replay: TerraReplay; field: "ust_price" | "luna_price" | "luna_supply" | "anchor_withdrawal_flow" | "backing_ratio"; title: string }) {
  const actual = new Map(replay.ground_truth_timeseries.map((row) => [row.timestamp, row]));
  const data = replay.simulated_timeseries.map((row, index) => ({
    index,
    timestamp: String(row.timestamp).slice(5, 13),
    simulated: Number(row[field]),
    actual: actual.get(String(row.timestamp))?.[field] == null ? null : Number(actual.get(String(row.timestamp))?.[field]),
  }));
  return (
    <section className="panel terraChartPanel">
      <header><div><p className="eyebrow">GROUND TRUTH VS MODEL OUTPUT</p><h3>{title}</h3></div></header>
      <div className="chart">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke="#16344c" strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" minTickGap={44} stroke="#7892aa" />
            <YAxis stroke="#7892aa" tickFormatter={compact} width={72} />
            <Tooltip contentStyle={chartTooltip} />
            <Legend />
            <Line type="monotone" dataKey="actual" stroke="#45d69a" dot={false} strokeWidth={2} isAnimationActive={false} />
            <Line type="monotone" dataKey="simulated" stroke="#8c96ff" dot={false} strokeWidth={2} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export function FitComparisonChart({
  fit,
  field,
  title,
  logarithmic = false,
}: {
  fit: TerraHistoricalFit;
  field: "ust_price" | "luna_price" | "luna_supply";
  title: string;
  logarithmic?: boolean;
}) {
  const simulated = new Map(fit.simulated_timeseries.map((row) => [String(row.timestamp), Number(row[field])]));
  const data = fit.actual_timeseries.map((row) => ({
    timestamp: String(row.timestamp).slice(5, 13),
    actual: Number(row[field]),
    simulated: simulated.get(String(row.timestamp)),
  }));
  return <section className="panel terraChartPanel"><header><div><p className="eyebrow">ACTUAL VS CALIBRATED RECONSTRUCTION</p><h3>{title}</h3></div></header><div className="chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={data}><CartesianGrid stroke="#16344c" strokeDasharray="3 3" /><XAxis dataKey="timestamp" minTickGap={44} stroke="#7892aa" /><YAxis stroke="#7892aa" tickFormatter={compact} width={72} scale={logarithmic ? "log" : "auto"} domain={logarithmic ? ["auto", "auto"] : undefined} /><Tooltip contentStyle={chartTooltip} /><Legend /><Line type="monotone" dataKey="actual" stroke="#45d69a" dot={false} strokeWidth={2} isAnimationActive={false} /><Line type="monotone" dataKey="simulated" stroke="#8c96ff" dot={false} strokeWidth={2} isAnimationActive={false} /></LineChart></ResponsiveContainer></div></section>;
}

export function EarlyWarningTimeline({ warning }: { warning: TerraEarlyWarning }) {
  const data = warning.timeline.map((row) => ({ timestamp: row.timestamp.slice(5, 13), score: row.risk_score }));
  return <section className="panel terraChartPanel"><header><div><p className="eyebrow">HOURLY RISK SCORE · {warning.mode.replace("_", " ")}</p><h3>Risk rose as depeg and flow stress accumulated</h3></div></header><div className="chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={data}><CartesianGrid stroke="#16344c" strokeDasharray="3 3" /><ReferenceArea y1={0} y2={30} fill="#45d69a" fillOpacity={0.08} /><ReferenceArea y1={30} y2={60} fill="#ffbe55" fillOpacity={0.07} /><ReferenceArea y1={60} y2={80} fill="#ff8d55" fillOpacity={0.08} /><ReferenceArea y1={80} y2={100} fill="#ff657a" fillOpacity={0.10} /><ReferenceLine y={60} stroke="#ffbe55" strokeDasharray="4 4" /><ReferenceLine y={80} stroke="#ff657a" strokeDasharray="4 4" /><XAxis dataKey="timestamp" minTickGap={54} stroke="#7892aa" /><YAxis domain={[0, 100]} stroke="#7892aa" width={48} /><Tooltip contentStyle={chartTooltip} /><Line type="monotone" dataKey="score" stroke="#31d4e8" dot={false} strokeWidth={2} isAnimationActive={false} /></LineChart></ResponsiveContainer></div></section>;
}

export function StressFanChart({ result }: { result: TerraStressResult }) {
  const data = result.fan_chart.map((row) => ({ hour: row.hour, p05: row.ust_price.p05, median: row.ust_price.median, p95: row.ust_price.p95 }));
  return <section className="panel terraChartPanel"><header><div><p className="eyebrow">SEEDED MONTE CARLO · {result.runs} RUNS</p><h3>UST stress paths: p05 / median / p95</h3></div></header><div className="chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={data}><CartesianGrid stroke="#16344c" strokeDasharray="3 3" /><XAxis dataKey="hour" stroke="#7892aa" /><YAxis domain={[0, 1.05]} stroke="#7892aa" width={48} /><Tooltip contentStyle={chartTooltip} /><Legend /><Line type="monotone" dataKey="p05" stroke="#ff657a" dot={false} isAnimationActive={false} /><Line type="monotone" dataKey="median" stroke="#31d4e8" dot={false} strokeWidth={2} isAnimationActive={false} /><Line type="monotone" dataKey="p95" stroke="#45d69a" dot={false} isAnimationActive={false} /></LineChart></ResponsiveContainer></div></section>;
}

function compact(value: number) {
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}
