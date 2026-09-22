"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { TerraObservation, TerraReplay } from "@/lib/api";

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

export function ReplayChart({ replay, field, title }: { replay: TerraReplay; field: "ust_price" | "luna_price" | "luna_supply" | "anchor_withdrawal_flow" | "backing_ratio"; title: string }) {
  const actual = new Map(replay.ground_truth_timeseries.map((row) => [row.timestamp, row]));
  const data = replay.simulated_timeseries.map((row, index) => ({
    index,
    timestamp: String(row.timestamp).slice(5, 13),
    simulated: Number(row[field]),
    actual: Number(actual.get(String(row.timestamp))?.[field] ?? 0),
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

function compact(value: number) {
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}
