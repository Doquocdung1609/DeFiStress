"use client";

import { useEffect, useState } from "react";

import { API_URL, api } from "@/lib/api";

type Ratio = { numerator: string; denominator: string };
type Model = {
  level: string; score: Ratio | null; reasons?: string[]; output_hash: string;
  context: { decision_at: string; information_cutoff: string; issued_at: string };
  signals: Array<{ signal_id: string; role: string; value: Ratio }>;
  slots: Array<{ component: string; expected_at: string; selected: null | {
    observation_id: string; measurement: { value: string }; provenance: { source_id: string; origin: string };
  } }>;
  configuration: { thresholds: Array<[string, Ratio]> };
  input_lineage_hash: string;
};
type WarningRun = { id: string; mode: "SYNTHETIC_WARNING"; status: string; origin: string; models: Record<string, Model>; assumptions: Record<string, unknown> };
type ExitRun = { id: string; mode: "ILLUSTRATIVE_EXIT"; status: string; execution_status: string; calculation: Record<string, string | number | null>; assumptions: Record<string, unknown> };
type DemoRun = WarningRun | ExitRun;
type RunIndex = { id: string; experiment_type: string; status: string; created_at: string };

function ResultLink({ id }: { id: string }) {
  return <div className="exportLinks"><a href={`${API_URL}/api/v1/terra/demo/runs/${id}/export`}>Tải kết quả ZIP</a><a href={`/terra/demo-runs?run=${encodeURIComponent(id)}`}>Mở kết quả đã lưu</a></div>;
}

export function SyntheticWarningDemo() {
  const [ust, setUst] = useState("0.99");
  const [lunaBefore, setLunaBefore] = useState("100");
  const [lunaNow, setLunaNow] = useState("90");
  const [delay, setDelay] = useState(0);
  const [run, setRun] = useState<WarningRun | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  function preset(name: "NORMAL" | "WATCH" | "HIGH" | "MISSING" | "LATE") {
    setUst(name === "MISSING" ? "" : name === "NORMAL" ? "1" : name === "HIGH" ? "0.96" : "0.99");
    setLunaBefore("100");
    setLunaNow(name === "NORMAL" ? "100" : name === "HIGH" ? "50" : "90");
    setDelay(name === "LATE" ? 1 : 0);
    setRun(null);
  }
  async function execute() {
    setBusy(true); setError(""); setRun(null);
    try {
      const body = { ust_price: ust || null, luna_previous_price: lunaBefore || null, luna_current_price: lunaNow || null, ust_delay_minutes: delay };
      setRun(await api<WarningRun>("/api/v1/terra/demo/warnings", { method: "POST", body: JSON.stringify(body) }));
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Không chạy được mô hình."); }
    finally { setBusy(false); }
  }
  return <>
    <div className="sectionLead"><div><p className="eyebrow">P04-03-S · SYNTHETIC</p><h2>Thử cảnh báo B0–B3</h2><p>Giá do bạn nhập là dữ liệu tổng hợp. Bốn mô hình chạy với cùng mốc thời gian và nguồn; đầu vào thiếu hoặc đến trễ sẽ hiện ABSTAIN.</p></div></div>
    <section className="panel"><div className="presetRow" role="group" aria-label="Synthetic warning scenarios">{(["NORMAL", "WATCH", "HIGH", "MISSING", "LATE"] as const).map((name) => <button key={name} onClick={() => preset(name)}>{name}</button>)}</div><div className="formGrid">
      <label className="formField">UST/USD (để trống = thiếu)<input aria-label="UST price" value={ust} onChange={(e) => setUst(e.target.value)} inputMode="decimal" /></label>
      <label className="formField">LUNA/USD giờ trước<input aria-label="LUNA previous price" value={lunaBefore} onChange={(e) => setLunaBefore(e.target.value)} inputMode="decimal" /></label>
      <label className="formField">LUNA/USD giờ này<input aria-label="LUNA current price" value={lunaNow} onChange={(e) => setLunaNow(e.target.value)} inputMode="decimal" /></label>
      <label className="formField">UST công bố trễ (phút)<input aria-label="UST delay minutes" type="number" min="0" max="60" value={delay} onChange={(e) => setDelay(Number(e.target.value))} /></label>
    </div><div className="actionRow"><button className="primary" disabled={busy} onClick={() => void execute()}>{busy ? "Đang tính…" : "Chạy B0–B3"}</button></div></section>
    {error && <p role="alert" className="researchWarning">{error}</p>}
    {run && <><div className="metricGrid">{Object.entries(run.models).map(([name, model]) => <article className="metricCard" key={name}><p>{name}</p><strong>{model.level}</strong><small>{model.score ? `${model.score.numerator}/${model.score.denominator}` : "Không đủ chứng cứ để chấm điểm"}</small></article>)}</div><section className="panel"><p>Run {run.id} · {run.status} · {run.origin}</p><p className="researchWarning">Chỉ kiểm thử điều khiển tổng hợp. Không phải dự báo lịch sử Terra 2022.</p>{Object.entries(run.models).map(([name, model]) => <details key={name} className="demoDetails"><summary>{name} · {model.level} · đóng góp, ngưỡng và nguồn</summary><p>Quyết định: {model.context.decision_at} · cutoff: {model.context.information_cutoff} · phát cảnh báo: {model.context.issued_at}</p><p>Tín hiệu: {model.signals.map((signal) => `${signal.signal_id} ${signal.value.numerator}/${signal.value.denominator}`).join(" · ") || "Không có"}</p><p>Ngưỡng: {model.configuration.thresholds.map(([key, value]) => `${key} ${value.numerator}/${value.denominator}`).join(" · ")}</p><p>Quan sát chọn: {model.slots.map((slot) => slot.selected ? `${slot.component} ${slot.selected.measurement.value} (${slot.selected.provenance.source_id}, ${slot.selected.provenance.origin})` : `${slot.component}: thiếu ở ${slot.expected_at}`).join(" · ")}</p><p>Lý do: {model.reasons?.join(", ") || "Không có"}</p><code>Lineage: {model.input_lineage_hash}<br />Output: {model.output_hash}</code></details>)}<ResultLink id={run.id} /></section></>}
  </>;
}

export function IllustrativeExitDemo() {
  const [quantity, setQuantity] = useState("1000");
  const [warningTime, setWarningTime] = useState("2030-01-01T03:00:00Z");
  const [warningPrice, setWarningPrice] = useState("1");
  const [price, setPrice] = useState("0.8");
  const [capacity, setCapacity] = useState("");
  const [fee, setFee] = useState("1");
  const [slippage, setSlippage] = useState("2");
  const [latency, setLatency] = useState(15);
  const [run, setRun] = useState<ExitRun | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function execute() {
    setBusy(true); setError(""); setRun(null);
    try {
      const body = { quantity_ust: quantity, warning_timestamp: warningTime, warning_price_usd: warningPrice, price_usd: price, capacity_ust: capacity || null, fee_percent: fee, slippage_percent: slippage, latency_minutes: latency };
      setRun(await api<ExitRun>("/api/v1/terra/demo/exits", { method: "POST", body: JSON.stringify(body) }));
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Không tính được kế hoạch."); }
    finally { setBusy(false); }
  }
  return <><div className="sectionLead"><div><p className="eyebrow">ILLUSTRATIVE EXIT</p><h2>Ước tính thoát vị thế</h2><p>Công cụ tính theo giả định bạn nhập. Không có dữ liệu độ sâu thị trường hoặc cam kết khớp lệnh.</p></div></div><section className="panel"><div className="formGrid">
    <label className="formField">Số UST muốn bán<input aria-label="UST quantity" value={quantity} onChange={(e) => setQuantity(e.target.value)} inputMode="decimal" /></label>
    <label className="formField">Mốc cảnh báo giả định (UTC, ISO 8601)<input aria-label="Warning timestamp" value={warningTime} onChange={(e) => setWarningTime(e.target.value)} /></label>
    <label className="formField">Giá UST lúc cảnh báo<input aria-label="Warning price" value={warningPrice} onChange={(e) => setWarningPrice(e.target.value)} inputMode="decimal" /></label>
    <label className="formField">Giá USD/UST<input aria-label="Exit price" value={price} onChange={(e) => setPrice(e.target.value)} inputMode="decimal" /></label>
    <label className="formField">Dung lượng khớp giả định (UST; để trống nếu không biết)<input aria-label="Assumed capacity" value={capacity} onChange={(e) => setCapacity(e.target.value)} inputMode="decimal" /></label>
    <label className="formField">Phí (%)<input aria-label="Fee percent" value={fee} onChange={(e) => setFee(e.target.value)} inputMode="decimal" /></label>
    <label className="formField">Trượt giá (%)<input aria-label="Slippage percent" value={slippage} onChange={(e) => setSlippage(e.target.value)} inputMode="decimal" /></label>
    <label className="formField">Độ trễ (phút)<input aria-label="Latency minutes" type="number" min="0" value={latency} onChange={(e) => setLatency(Number(e.target.value))} /></label>
  </div><div className="actionRow"><button className="primary" disabled={busy} onClick={() => void execute()}>{busy ? "Đang tính…" : "Tính phương án"}</button></div></section>
    {error && <p role="alert" className="researchWarning">{error}</p>}
    {run && <section className="panel"><h3>{run.execution_status}</h3><div className="metricGrid"><article className="metricCard"><p>UST khớp theo giả định</p><strong>{run.calculation.filled_ust ?? "Không xác minh"}</strong></article><article className="metricCard"><p>UST chưa khớp</p><strong>{run.calculation.unfilled_ust ?? "Không xác minh"}</strong></article><article className="metricCard"><p>USD ròng</p><strong>{run.calculation.net_usd ?? "Không xác minh"}</strong></article><article className="metricCard"><p>Tổn thất mô hình</p><strong>{run.calculation.modeled_loss_usd ?? "Không xác minh"}</strong></article></div><p>Giờ thực hiện ước tính: {run.calculation.estimated_execution_time} · Biến động giá: {run.calculation.price_move_percent}%</p><p className="researchWarning">Kết quả chỉ minh họa; không có đảm bảo thanh khoản, giá hay thời gian thực thi.</p><ResultLink id={run.id} /></section>}
  </>;
}

export function DemoRunHistory() {
  const [rows, setRows] = useState<RunIndex[]>([]);
  const [selected, setSelected] = useState<DemoRun | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("run");
    void api<RunIndex[]>("/api/v1/terra/demo/runs").then(setRows).catch((cause) => setError(String(cause)));
    if (id) void api<DemoRun>(`/api/v1/terra/demo/runs/${encodeURIComponent(id)}`).then(setSelected).catch((cause) => setError(String(cause)));
  }, []);
  return <><div className="sectionLead"><div><p className="eyebrow">SAVED RESULTS</p><h2>Lịch sử chạy demo</h2><p>Kết quả được lưu trong cơ sở dữ liệu cục bộ và có thể xuất thành ZIP.</p></div></div>{error && <p role="alert">{error}</p>}{rows.length === 0 ? <p>Chưa có kết quả. Hãy chạy cảnh báo hoặc phương án thoát.</p> : <section className="panel"><div className="tableWrap"><table><thead><tr><th>Thời gian UTC</th><th>Loại</th><th>Trạng thái</th><th>Kết quả</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id}><td>{row.created_at}</td><td>{row.experiment_type}</td><td>{row.status}</td><td><button onClick={() => void api<DemoRun>(`/api/v1/terra/demo/runs/${row.id}`).then(setSelected).catch((cause) => setError(String(cause)))}>Xem</button></td></tr>)}</tbody></table></div></section>}{selected && <section className="panel"><h3>{selected.mode} · {selected.id}</h3><pre>{JSON.stringify(selected, null, 2)}</pre><ResultLink id={selected.id} /></section>}</>;
}
