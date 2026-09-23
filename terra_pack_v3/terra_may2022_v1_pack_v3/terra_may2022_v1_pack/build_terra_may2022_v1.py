from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import sys
import time
import zipfile
from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import httpx
import numpy as np
import pandas as pd

DATASET_ID = "j5d8n7hzdy"
DATASET_VERSION = 4
DOI = "10.17632/j5d8n7hzdy.4"
START = pd.Timestamp("2022-05-01T00:00:00Z")
END = pd.Timestamp("2022-05-13T23:00:00Z")
GRID = pd.date_range(START, END, freq="1h")
EXPECTED_ROWS = len(GRID)

REQUIRED = [
    "timestamp", "block_height", "ust_price", "luna_price", "ust_supply", "luna_supply",
    "anchor_total_deposits", "anchor_deposit_flow", "anchor_withdrawal_flow",
    "ust_native_redemption_volume", "luna_minted_from_redemption", "luna_burned",
    "ust_dex_sell_volume", "terra_dex_liquidity", "terra_dex_depth",
    "top10_anchor_share", "top100_anchor_share",
]
OPTIONAL = [
    "curve_ust_liquidity", "curve_pool_imbalance", "curve_ust_price",
    "bridge_outflow_terra_to_ethereum", "bridge_inflow_ethereum_to_terra",
    "btc_reserve_value", "reserve_intervention_volume",
]

@dataclass
class Evidence:
    field: str
    source_file: str
    source_columns: list[str]
    method: str
    exact: bool
    notes: str = ""


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def safe_float(v: Any) -> float | None:
    try:
        if pd.isna(v):
            return None
        x = float(v)
        return x if math.isfinite(x) else None
    except Exception:
        return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mendeley_download(work: Path) -> Path:
    """Download the V4 replication ZIP with retries and resumable HTTP range requests.

    A partially downloaded file is kept and reused. If the server supports Range,
    the next attempt resumes from the current byte offset. If it does not, the
    attempt safely restarts from byte 0 instead of treating the partial ZIP as
    complete.
    """
    work.mkdir(parents=True, exist_ok=True)
    metadata_url = f"https://data.mendeley.com/public-api/datasets/{DATASET_ID}/files"
    params = {"folder_id": "root", "version": str(DATASET_VERSION)}

    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        r = client.get(metadata_url, params=params)
        r.raise_for_status()
        files = r.json()

    if not isinstance(files, list) or not files:
        raise RuntimeError("Mendeley public API returned no files")

    preferred = None
    for item in files:
        name = str(item.get("name") or item.get("filename") or "")
        if name == "terra-luna-run-replication.zip":
            preferred = item
            break
    preferred = preferred or next((x for x in files if str(x.get("name", "")).lower().endswith(".zip")), files[0])

    details = preferred.get("content_details") or {}
    url = details.get("download_url") or preferred.get("download_url")
    if not url:
        raise RuntimeError("Mendeley file metadata has no download_url")

    expected_size_raw = (
        preferred.get("size")
        or preferred.get("file_size")
        or details.get("size")
        or details.get("file_size")
    )
    try:
        expected_size = int(expected_size_raw) if expected_size_raw not in (None, "") else None
    except (TypeError, ValueError):
        expected_size = None

    out = work / "terra-luna-run-replication.zip"
    max_attempts = 10

    for attempt in range(1, max_attempts + 1):
        current_size = out.stat().st_size if out.exists() else 0
        if expected_size is not None and current_size == expected_size:
            print(f"DOWNLOAD complete: {current_size:,} bytes", flush=True)
            return out
        if expected_size is not None and current_size > expected_size:
            print("Existing ZIP is larger than expected; restarting download.", flush=True)
            out.unlink(missing_ok=True)
            current_size = 0

        headers = {}
        if current_size > 0:
            headers["Range"] = f"bytes={current_size}-"

        print(
            f"DOWNLOAD attempt {attempt}/{max_attempts}: "
            f"starting at {current_size:,} bytes"
            + (f" of {expected_size:,}" if expected_size else ""),
            flush=True,
        )

        try:
            timeout = httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                with client.stream("GET", url, headers=headers) as rr:
                    rr.raise_for_status()
                    resumed = current_size > 0 and rr.status_code == 206
                    if current_size > 0 and not resumed:
                        # Server ignored Range. Start clean instead of appending a full response.
                        print("Server did not honor Range; restarting this attempt from byte 0.", flush=True)
                        current_size = 0
                    mode = "ab" if resumed else "wb"

                    response_total = None
                    content_range = rr.headers.get("content-range", "")
                    if "/" in content_range:
                        tail = content_range.rsplit("/", 1)[-1]
                        if tail.isdigit():
                            response_total = int(tail)
                    if response_total is None and rr.headers.get("content-length", "").isdigit():
                        length = int(rr.headers["content-length"])
                        response_total = current_size + length if resumed else length
                    if expected_size is None and response_total:
                        expected_size = response_total

                    downloaded_this_attempt = 0
                    last_report = current_size
                    with out.open(mode) as f:
                        for chunk in rr.iter_bytes(chunk_size=1024 * 1024):
                            if not chunk:
                                continue
                            f.write(chunk)
                            downloaded_this_attempt += len(chunk)
                            total_now = current_size + downloaded_this_attempt
                            if total_now - last_report >= 5 * 1024 * 1024:
                                pct = (100 * total_now / expected_size) if expected_size else None
                                suffix = f" ({pct:.1f}%)" if pct is not None else ""
                                print(f"  downloaded {total_now:,} bytes{suffix}", flush=True)
                                last_report = total_now

        except httpx.HTTPError as exc:
            saved = out.stat().st_size if out.exists() else 0
            print(
                f"DOWNLOAD interrupted on attempt {attempt}: {exc}. "
                f"Saved {saved:,} bytes; will retry/resume.",
                flush=True,
            )
            if attempt == max_attempts:
                raise RuntimeError(
                    f"Mendeley download failed after {max_attempts} attempts; "
                    f"partial file kept at {out} ({saved:,} bytes)."
                ) from exc
            time.sleep(min(2 * attempt, 15))
            continue

        final_size = out.stat().st_size if out.exists() else 0
        if expected_size is None or final_size == expected_size:
            # Verify it is actually a ZIP before returning.
            if zipfile.is_zipfile(out):
                print(f"DOWNLOAD complete: {final_size:,} bytes", flush=True)
                return out
            print("Downloaded file is not a valid ZIP yet; retrying.", flush=True)
        else:
            print(
                f"DOWNLOAD incomplete: have {final_size:,} bytes, expected {expected_size:,}; retrying.",
                flush=True,
            )

        if attempt < max_attempts:
            time.sleep(min(2 * attempt, 15))

    raise RuntimeError(f"Could not obtain a complete replication ZIP at {out}")


def extract_zip(zip_path: Path, work: Path) -> Path:
    root = work / "replication"
    marker = root / ".extracted"
    if marker.exists():
        return root
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(root)
    marker.write_text(datetime.now(UTC).isoformat(), encoding="utf-8")
    return root


def read_table(path: Path, nrows: int | None = None) -> pd.DataFrame | None:
    try:
        s = path.suffix.lower()
        if s == ".csv":
            return pd.read_csv(path, nrows=nrows, low_memory=False)
        if s in {".parquet", ".pq"}:
            df = pd.read_parquet(path)
            return df.head(nrows) if nrows else df
        if s in {".json", ".jsonl", ".ndjson"}:
            if s in {".jsonl", ".ndjson"}:
                return pd.read_json(path, lines=True, nrows=nrows)
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows = payload.get("observations") if isinstance(payload, dict) else payload
            if isinstance(rows, list):
                return pd.DataFrame(rows[:nrows] if nrows else rows)
        if s in {".pkl", ".pickle"}:
            obj = pd.read_pickle(path)
            if isinstance(obj, pd.DataFrame):
                return obj.head(nrows) if nrows else obj
    except Exception:
        return None
    return None


def inventory(root: Path, out_csv: Path) -> list[dict[str, Any]]:
    rows = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in {".csv", ".parquet", ".pq", ".json", ".jsonl", ".ndjson", ".pkl", ".pickle"}:
            continue
        df = read_table(p, 10)
        rows.append({
            "path": str(p.relative_to(root)),
            "size_bytes": p.stat().st_size,
            "readable": df is not None,
            "columns": "|".join(map(str, df.columns)) if df is not None else "",
            "sample_rows": 0 if df is None else len(df),
        })
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "size_bytes", "readable", "columns", "sample_rows"])
        w.writeheader(); w.writerows(rows)
    return rows


def time_column(df: pd.DataFrame) -> str | None:
    scored: list[tuple[int, str]] = []
    for c in df.columns:
        n = norm(str(c))
        score = 0
        if n in {"timestamp", "datetime", "date_time", "time", "date", "block_time", "block_timestamp"}: score += 8
        if "time" in n or "date" in n: score += 3
        if score: scored.append((score, str(c)))
    for _, c in sorted(scored, reverse=True):
        parsed = pd.to_datetime(df[c], utc=True, errors="coerce")
        if parsed.notna().mean() >= 0.5:
            return c
    return None


def datetime_index_available(df: pd.DataFrame) -> bool:
    """Return True when the DataFrame index is a real historical datetime axis."""
    if isinstance(df.index, pd.DatetimeIndex):
        return True
    try:
        parsed = pd.to_datetime(df.index, utc=True, errors="coerce")
        # RangeIndex integers parse to 1970 nanoseconds; reject those explicitly.
        if isinstance(df.index, pd.RangeIndex):
            return False
        return pd.Series(parsed).notna().mean() >= 0.8
    except Exception:
        return False


def time_values(df: pd.DataFrame, time_col_name: str | None = None) -> tuple[pd.Series | pd.DatetimeIndex, str]:
    tc = time_col_name or time_column(df)
    if tc is not None:
        return pd.to_datetime(df[tc], utc=True, errors="coerce"), tc
    if datetime_index_available(df):
        return pd.to_datetime(df.index, utc=True, errors="coerce"), "__index__"
    raise RuntimeError("No valid historical timestamp column/index")


def find_exact_file(root: Path, name: str) -> Path | None:
    matches = list(root.rglob(name))
    return matches[0] if matches else None


def block_column(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        n = norm(str(c))
        if n in {"block_height", "height", "block", "block_number"} or ("block" in n and ("height" in n or "number" in n)):
            return str(c)
    return None


def candidate_score(path: Path, cols: Iterable[str], file_kw: list[str], col_kw: list[str]) -> int:
    pn = norm(path.name)
    cns = [norm(str(c)) for c in cols]
    return sum(4 for k in file_kw if k in pn) + sum(3 for k in col_kw if any(k in c for c in cns))


def find_tables(root: Path, file_kw: list[str], col_kw: list[str]) -> list[tuple[int, Path, pd.DataFrame]]:
    found = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".csv", ".parquet", ".pq", ".json", ".jsonl", ".ndjson", ".pkl", ".pickle"}:
            continue
        sample = read_table(p, 200)
        if sample is None or sample.empty:
            continue
        score = candidate_score(p, sample.columns, file_kw, col_kw)
        if score > 0:
            found.append((score, p, sample))
    return sorted(found, key=lambda x: (x[0], x[1].stat().st_size), reverse=True)


def choose_value_col(df: pd.DataFrame, patterns: list[str], asset: str | None = None) -> str | None:
    scores = []
    for c in df.columns:
        n = norm(str(c)); score = 0
        for p in patterns:
            if p == n: score += 10
            elif p in n: score += 4
        if asset and asset in n: score += 4
        if score:
            vals = pd.to_numeric(df[c], errors="coerce")
            if vals.notna().mean() >= 0.3:
                scores.append((score, str(c)))
    return max(scores)[1] if scores else None


def hourly_series(path: Path, value_col: str, agg: str = "last", time_col_name: str | None = None) -> pd.Series:
    df = read_table(path)
    if df is None or df.empty:
        raise RuntimeError(f"Cannot read {path}")
    ts, _ = time_values(df, time_col_name)
    values = pd.to_numeric(df[value_col], errors="coerce")
    x = pd.DataFrame({"t": list(ts), "v": values.to_numpy()}).dropna().set_index("t").sort_index()
    x = x[(x.index >= START - pd.Timedelta("2D")) & (x.index <= END + pd.Timedelta("2D"))]
    if agg == "sum":
        s = x["v"].resample("1h").sum(min_count=1)
    elif agg == "mean":
        s = x["v"].resample("1h").mean()
    else:
        s = x["v"].resample("1h").last()
    return s.reindex(GRID)


def select_direct_series(root: Path, field: str, file_kw: list[str], col_patterns: list[str], asset: str | None, agg: str, evidence: list[Evidence], report: dict[str, Any]) -> pd.Series | None:
    candidates = find_tables(root, file_kw, col_patterns + ([asset] if asset else []))
    report[field] = []
    for score, path, sample in candidates[:20]:
        vc = choose_value_col(sample, col_patterns, asset)
        tc = time_column(sample)
        index_time = datetime_index_available(sample)
        time_source = tc or ("__index__" if index_time else None)
        report[field].append({"score": score, "file": str(path.relative_to(root)), "value_col": vc, "time_col": time_source, "columns": list(map(str, sample.columns))})
        if vc and time_source:
            try:
                s = hourly_series(path, vc, agg, tc)
                if s.notna().sum() >= 3:
                    evidence.append(Evidence(field, str(path.relative_to(root)), [time_source, vc], f"hourly {agg}", True))
                    return s
            except Exception:
                continue
    return None


def event_flow(root: Path, field: str, file_kw: list[str], action_words: list[str], amount_words: list[str], evidence: list[Evidence], report: dict[str, Any]) -> pd.Series | None:
    candidates = find_tables(root, file_kw, action_words + amount_words)
    report[field] = []
    for score, path, sample in candidates[:30]:
        tc = time_column(sample)
        action_col = next((str(c) for c in sample.columns if any(w in norm(str(c)) for w in ["action", "type", "event", "message", "method", "direction"])), None)
        amount_col = choose_value_col(sample, amount_words)
        report[field].append({"score": score, "file": str(path.relative_to(root)), "time_col": tc, "action_col": action_col, "amount_col": amount_col})
        if not (tc and amount_col):
            continue
        df = read_table(path)
        if df is None: continue
        ts = pd.to_datetime(df[tc], utc=True, errors="coerce")
        amt = pd.to_numeric(df[amount_col], errors="coerce")
        mask = pd.Series(True, index=df.index)
        if action_col:
            text = df[action_col].astype(str).str.lower()
            mask = False
            for w in action_words:
                mask = mask | text.str.contains(w, regex=False)
        sub = pd.DataFrame({"t": ts[mask], "v": amt[mask]}).dropna().set_index("t")
        sub = sub[(sub.index >= START) & (sub.index <= END + pd.Timedelta(hours=1))]
        if len(sub) == 0: continue
        s = sub["v"].resample("1h").sum(min_count=1).reindex(GRID).fillna(0.0)
        evidence.append(Evidence(field, str(path.relative_to(root)), [tc, amount_col] + ([action_col] if action_col else []), "sum qualifying events by hour", True if action_col else False, "Action filter absent" if not action_col else ""))
        return s
    return None


def block_height_series(root: Path, evidence: list[Evidence], report: dict[str, Any]) -> pd.Series | None:
    # Prefer the Anchor full-node state file because it carries real Terra block heights
    # on a minute-resolution DatetimeIndex through the target window.
    preferred = find_exact_file(root, "Anchor_global_stats_fullnode.parquet")
    candidates: list[tuple[int, Path, pd.DataFrame]] = []
    if preferred is not None:
        sample = read_table(preferred, 200)
        if sample is not None:
            candidates.append((999, preferred, sample))
    candidates.extend(find_tables(root, ["terra", "block", "transaction", "anchor", "swap"], ["block", "height", "timestamp"]))

    report["block_height"] = []
    best = None
    evidence_file = None
    ev_cols: list[str] = []
    seen: set[str] = set()
    for score, path, sample in candidates[:40]:
        if str(path) in seen:
            continue
        seen.add(str(path))
        tc = time_column(sample)
        time_source = tc or ("__index__" if datetime_index_available(sample) else None)
        bc = block_column(sample)
        report["block_height"].append({"score": score, "file": str(path.relative_to(root)), "time_col": time_source, "block_col": bc})
        if not (time_source and bc):
            continue
        df = read_table(path)
        if df is None:
            continue
        try:
            ts, source_name = time_values(df, tc)
        except Exception:
            continue
        bh = pd.to_numeric(df[bc], errors="coerce")
        x = pd.DataFrame({"t": list(ts), "v": bh.to_numpy()}).dropna().sort_values("t")
        x = x[(x["t"] >= START - pd.Timedelta("6h")) & (x["t"] <= END + pd.Timedelta("6h"))]
        if len(x) < 10:
            continue
        hourly = pd.merge_asof(
            pd.DataFrame({"t": GRID}),
            x,
            on="t",
            direction="backward",
            tolerance=pd.Timedelta("6h"),
        ).set_index("t")["v"]
        if hourly.notna().sum() > (best.notna().sum() if best is not None else 0):
            best = hourly
            evidence_file = path
            ev_cols = [source_name, bc]
    if best is not None and evidence_file is not None:
        evidence.append(Evidence(
            "block_height",
            str(evidence_file.relative_to(root)),
            ev_cols,
            "last observed Terra block height at or before each UTC hour",
            True,
        ))
    return best


def concentration_series(root: Path, field: str, top_n: int, evidence: list[Evidence], report: dict[str, Any]) -> pd.Series | None:
    candidates = find_tables(root, ["anchor", "wallet", "address", "balance", "deposit"], ["address", "balance", "deposit", "time"])
    report[field] = []
    for score, path, sample in candidates[:30]:
        tc = time_column(sample)
        addr = next((str(c) for c in sample.columns if "address" in norm(str(c)) or "wallet" in norm(str(c))), None)
        bal = choose_value_col(sample, ["anchor_balance", "deposit_balance", "balance", "amount", "deposit"])
        report[field].append({"score": score, "file": str(path.relative_to(root)), "time_col": tc, "address_col": addr, "balance_col": bal})
        if not (tc and addr and bal): continue
        df = read_table(path)
        if df is None: continue
        df = df[[tc, addr, bal]].copy()
        df[tc] = pd.to_datetime(df[tc], utc=True, errors="coerce")
        df[bal] = pd.to_numeric(df[bal], errors="coerce")
        df = df.dropna()
        if len(df) < 20: continue
        df["hour"] = df[tc].dt.floor("h")
        grp = df.groupby(["hour", addr], observed=True)[bal].last().reset_index()
        vals = {}
        for hour, g in grp.groupby("hour"):
            a = g[bal].clip(lower=0).sort_values(ascending=False)
            total = a.sum()
            if total > 0: vals[hour] = a.head(top_n).sum() / total
        s = pd.Series(vals, dtype=float).reindex(GRID)
        if s.notna().sum() >= 1:
            s = s.ffill().bfill()
            evidence.append(Evidence(field, str(path.relative_to(root)), [tc, addr, bal], f"top {top_n} wallet balance share per hour; forward-filled between balance snapshots", True))
            return s
    return None



def ust_supply_from_fullnode(root: Path, evidence: list[Evidence], report: dict[str, Any]) -> pd.Series | None:
    """Reconstruct UST supply from the Columbus-5 full-node supply breakdown.

    The source uses Terra native denom `uusd`, i.e. micro-UST. Summing balances
    across addresses/modules for each daily snapshot and dividing by 1e6 yields
    UST units. Daily state is carried forward within the same/next day to the
    hourly research grid.
    """
    path = find_exact_file(root, "columbus-5-lunaust-supply-breakdown-fullnode.parquet")
    report.setdefault("ust_supply_exact", [])
    if path is None:
        report["ust_supply_exact"].append({"error": "source file not found"})
        return None
    df = read_table(path)
    if df is None or df.empty:
        return None
    required = {"denom", "balance", "date"}
    if not required.issubset(df.columns):
        report["ust_supply_exact"].append({"file": str(path.relative_to(root)), "error": "missing denom/balance/date"})
        return None

    denom = df["denom"].astype(str).str.lower().str.strip()
    # Terra Classic native UST micro-denom.
    mask = denom.eq("uusd")
    if not mask.any():
        # Conservative fallback only if the package spells it explicitly as UST/USTC.
        mask = denom.isin({"ust", "ustc"})
    sub = df.loc[mask, ["date", "balance", "denom"]].copy()
    sub["date"] = pd.to_datetime(sub["date"], utc=True, errors="coerce").dt.floor("D")
    sub["balance"] = pd.to_numeric(sub["balance"], errors="coerce")
    sub = sub.dropna(subset=["date", "balance"])
    if sub.empty:
        return None

    daily = sub.groupby("date", observed=True)["balance"].sum().sort_index()
    micro = sub["denom"].astype(str).str.lower().eq("uusd").all()
    if micro:
        daily = daily / 1_000_000.0

    # Daily snapshots are state variables, not flows.
    hourly = daily.reindex(daily.index.union(GRID)).sort_index().ffill().reindex(GRID)
    report["ust_supply_exact"].append({
        "file": str(path.relative_to(root)),
        "denom": "uusd" if micro else "UST/USTC",
        "daily_points": int(daily.notna().sum()),
        "window_min": str(daily.index.min()),
        "window_max": str(daily.index.max()),
        "method": "sum address/module balances by date; micro-denom conversion; forward-fill daily state to hourly grid",
    })
    if hourly.notna().sum() == len(GRID):
        evidence.append(Evidence(
            "ust_supply",
            str(path.relative_to(root)),
            ["date", "denom", "balance"],
            "sum Columbus-5 uusd balances by daily snapshot; divide microUST by 1e6; forward-fill state within day",
            True,
            "Protocol-native denom conversion; no market-price inference.",
        ))
        return hourly
    return None


def anchor_total_deposits_from_protocol_state(root: Path, evidence: list[Evidence], report: dict[str, Any]) -> pd.Series | None:
    """Build hourly Anchor deposits from aTerra supply × exchange rate.

    Scale is validated using only PRE-CUTOFF daily `deposit balance` observations,
    so the unit-normalization step does not use evaluation-period outcomes.
    """
    global_path = find_exact_file(root, "Anchor_global_stats_fullnode.parquet")
    daily_path = find_exact_file(root, "Anchor_daily_stats.parquet")
    report.setdefault("anchor_total_deposits_exact", [])
    if global_path is None or daily_path is None:
        report["anchor_total_deposits_exact"].append({"error": "required Anchor source file missing"})
        return None

    g = read_table(global_path)
    d = read_table(daily_path)
    if g is None or d is None:
        return None
    if not {"prev_aterra_supply", "prev_exchange_rate"}.issubset(g.columns) or "deposit balance" not in d.columns:
        return None
    if not datetime_index_available(g) or not datetime_index_available(d):
        return None

    g_ts = pd.to_datetime(g.index, utc=True, errors="coerce")
    a_supply = pd.to_numeric(g["prev_aterra_supply"], errors="coerce")
    exch = pd.to_numeric(g["prev_exchange_rate"], errors="coerce")
    gx = pd.DataFrame({"t": g_ts, "raw": a_supply.to_numpy() * exch.to_numpy()}).dropna().set_index("t").sort_index()
    gx = gx[(gx.index >= START - pd.Timedelta("2D")) & (gx.index <= END + pd.Timedelta("1D"))]
    raw_hourly = gx["raw"].resample("1h").last().reindex(GRID)

    d_ts = pd.to_datetime(d.index, utc=True, errors="coerce").floor("D")
    direct = pd.Series(pd.to_numeric(d["deposit balance"], errors="coerce").to_numpy(), index=d_ts).dropna().sort_index()
    direct = direct[~direct.index.duplicated(keep="last")]

    # Cross-check scale using PRE-CUTOFF dates only.
    raw_daily = gx["raw"].resample("1D").last()
    cutoff_day = pd.Timestamp("2022-05-06T00:00:00Z")
    joined = pd.concat(
        [direct.rename("direct"), raw_daily.rename("raw")],
        axis=1,
        join="inner",
    ).dropna()
    joined = joined[(joined.index >= START.floor("D")) & (joined.index <= cutoff_day)]
    joined = joined[(joined["direct"] > 0) & (joined["raw"] > 0)]
    if len(joined) < 3:
        report["anchor_total_deposits_exact"].append({"error": "insufficient pre-cutoff overlap for unit validation"})
        return None

    ratio = (joined["direct"] / joined["raw"]).median()
    # Unit conversions should be powers of ten in this protocol export.
    candidates = [10.0 ** p for p in range(-12, 13, 3)]
    scale = min(candidates, key=lambda x: abs(math.log10(max(ratio, 1e-30)) - math.log10(x)))
    predicted = joined["raw"] * scale
    rel_error = ((predicted - joined["direct"]).abs() / joined["direct"]).median()

    report["anchor_total_deposits_exact"].append({
        "global_file": str(global_path.relative_to(root)),
        "daily_validation_file": str(daily_path.relative_to(root)),
        "derived_from": "prev_aterra_supply * prev_exchange_rate",
        "pre_cutoff_overlap_days": int(len(joined)),
        "median_raw_to_direct_ratio": float(ratio),
        "chosen_power_of_ten_scale": float(scale),
        "median_relative_error_pre_cutoff": float(rel_error),
    })

    # Reject the derivation if protocol-state arithmetic does not reproduce the
    # independently supplied daily deposit-balance series closely enough.
    if not math.isfinite(float(rel_error)) or float(rel_error) > 0.05:
        return None

    hourly = raw_hourly * scale
    if hourly.notna().sum() != len(GRID):
        # Full-node series is minute-level; short holes may be carried forward,
        # but never across more than six hours.
        hourly = hourly.ffill(limit=6)
    if hourly.notna().sum() != len(GRID):
        return None

    evidence.append(Evidence(
        "anchor_total_deposits",
        str(global_path.relative_to(root)),
        ["__index__", "prev_aterra_supply", "prev_exchange_rate"],
        "hourly protocol state: prev_aterra_supply × prev_exchange_rate; unit scale validated pre-cutoff against Anchor_daily_stats deposit balance",
        True,
        f"scale={scale:g}; pre-cutoff median relative validation error={float(rel_error):.4%}",
    ))
    return hourly


def dex_execution_capacity_proxies(
    redemption_flow: pd.Series | None,
    evidence: list[Evidence],
) -> tuple[pd.Series | None, pd.Series | None]:
    """Create pre-cutoff model-input proxies only when --allow-proxy is requested.

    These are NOT observed Terra DEX TVL/depth. They are fixed, no-lookahead
    execution-capacity proxies calibrated solely from historical native UST
    redemption flow at/before T0. Dataset status must therefore be QUALITY_WARNING.
    """
    if redemption_flow is None:
        return None, None
    cutoff_hour = pd.Timestamp("2022-05-06T23:00:00Z")
    pre = pd.to_numeric(redemption_flow.loc[redemption_flow.index <= cutoff_hour], errors="coerce").dropna().clip(lower=0)
    if len(pre) < 24:
        return None, None

    rolling_24h = pre.rolling(24, min_periods=12).sum().dropna()
    liquidity = float(rolling_24h.median()) if len(rolling_24h) else float(pre.sum())
    depth = float(pre.quantile(0.95))
    if not math.isfinite(liquidity) or liquidity <= 0 or not math.isfinite(depth) or depth <= 0:
        return None, None

    liq_series = pd.Series(liquidity, index=GRID, dtype=float)
    depth_series = pd.Series(depth, index=GRID, dtype=float)
    note = (
        "MODEL-INPUT PROXY ONLY; not observed DEX pool TVL/depth. "
        "Calibrated exclusively with t<=2022-05-06 23:00 UTC native UST redemption flow."
    )
    evidence.append(Evidence(
        "terra_dex_liquidity",
        "derived pre-cutoff execution-capacity proxy",
        ["ust_native_redemption_volume"],
        "median trailing-24h pre-cutoff redemption turnover, held fixed through replay",
        False,
        note,
    ))
    evidence.append(Evidence(
        "terra_dex_depth",
        "derived pre-cutoff execution-capacity proxy",
        ["ust_native_redemption_volume"],
        "95th percentile hourly pre-cutoff redemption flow, held fixed through replay",
        False,
        note,
    ))
    return liq_series, depth_series


def direct_or_marketcap_supply(root: Path, asset: str, price: pd.Series | None, evidence: list[Evidence], report: dict[str, Any]) -> pd.Series | None:
    field = f"{asset}_supply"
    direct = select_direct_series(root, field, [asset, "supply", "coingecko", "market"], [f"{asset}_supply", "circulating_supply", "total_supply", "supply"], asset, "last", evidence, report)
    if direct is not None: return direct
    # Strictly documented derivation if market cap exists in historical file.
    mc_field = f"{asset}_market_cap"
    mc = select_direct_series(root, mc_field, [asset, "market", "coingecko"], [f"{asset}_market_cap", "market_cap", "marketcap"], asset, "last", evidence, report)
    if mc is not None and price is not None:
        s = mc / price.replace(0, np.nan)
        evidence.append(Evidence(field, "derived from historical market-cap and price series", [mc_field, f"{asset}_price"], "supply = market_cap / price", True, "Derived circulating-supply proxy only if source market cap definition matches"))
        return s
    return None


def build(root: Path, allow_proxy: bool, report: dict[str, Any]) -> tuple[pd.DataFrame, list[Evidence], list[str], list[str]]:
    evidence: list[Evidence] = []
    out = pd.DataFrame(index=GRID)
    out.index.name = "timestamp"

    out["block_height"] = block_height_series(root, evidence, report)
    out["ust_price"] = select_direct_series(root, "ust_price", ["ust", "price", "coingecko", "market"], ["ust_price", "price", "usd"], "ust", "last", evidence, report)
    out["luna_price"] = select_direct_series(root, "luna_price", ["luna", "price", "coingecko", "market"], ["luna_price", "price", "usd"], "luna", "last", evidence, report)
    out["ust_supply"] = ust_supply_from_fullnode(root, evidence, report) or direct_or_marketcap_supply(root, "ust", out["ust_price"], evidence, report)
    out["luna_supply"] = direct_or_marketcap_supply(root, "luna", out["luna_price"], evidence, report)

    out["anchor_total_deposits"] = anchor_total_deposits_from_protocol_state(root, evidence, report) or select_direct_series(root, "anchor_total_deposits", ["anchor", "deposit", "balance"], ["anchor_total_deposits", "total_ust_deposits", "deposit_balance", "outstanding_deposit", "deposits"], None, "last", evidence, report)
    out["anchor_deposit_flow"] = event_flow(root, "anchor_deposit_flow", ["anchor", "deposit", "transaction", "flow"], ["deposit", "mint"], ["amount", "ust", "value"], evidence, report)
    out["anchor_withdrawal_flow"] = event_flow(root, "anchor_withdrawal_flow", ["anchor", "withdraw", "redeem", "transaction", "flow"], ["withdraw", "redeem"], ["amount", "ust", "value"], evidence, report)

    out["ust_native_redemption_volume"] = event_flow(root, "ust_native_redemption_volume", ["terra", "market", "swap", "redeem", "mint", "burn"], ["redeem", "market", "swap", "ust"], ["ust_amount", "amount", "offer_amount", "value"], evidence, report)
    out["luna_minted_from_redemption"] = event_flow(root, "luna_minted_from_redemption", ["terra", "market", "mint", "swap", "redeem"], ["mint", "luna", "redeem"], ["luna_amount", "minted", "amount", "value"], evidence, report)
    out["luna_burned"] = event_flow(root, "luna_burned", ["terra", "market", "burn", "swap"], ["burn", "luna"], ["luna_amount", "burned", "amount", "value"], evidence, report)

    out["ust_dex_sell_volume"] = event_flow(root, "ust_dex_sell_volume", ["curve", "terraswap", "astroport", "dex", "swap", "ust"], ["sell", "swap", "ust"], ["ust_amount", "amount", "volume", "sold"], evidence, report)
    out["terra_dex_liquidity"] = select_direct_series(root, "terra_dex_liquidity", ["terraswap", "astroport", "dex", "pool", "liquidity"], ["liquidity", "tvl", "pool_balance", "reserve"], None, "last", evidence, report)
    out["terra_dex_depth"] = select_direct_series(root, "terra_dex_depth", ["terraswap", "astroport", "dex", "depth", "pool"], ["depth", "market_depth", "executable_depth"], None, "last", evidence, report)
    if allow_proxy and (out["terra_dex_liquidity"].isna().all() or out["terra_dex_depth"].isna().all()):
        proxy_liq, proxy_depth = dex_execution_capacity_proxies(out["ust_native_redemption_volume"], evidence)
        if proxy_liq is not None and out["terra_dex_liquidity"].isna().all():
            out["terra_dex_liquidity"] = proxy_liq
        if proxy_depth is not None and out["terra_dex_depth"].isna().all():
            out["terra_dex_depth"] = proxy_depth

    out["top10_anchor_share"] = concentration_series(root, "top10_anchor_share", 10, evidence, report)
    out["top100_anchor_share"] = concentration_series(root, "top100_anchor_share", 100, evidence, report)

    # Optional secondary channels
    out["curve_ust_liquidity"] = select_direct_series(root, "curve_ust_liquidity", ["curve", "ust", "liquidity", "3crv"], ["liquidity", "tvl", "reserve"], None, "last", evidence, report)
    out["curve_pool_imbalance"] = select_direct_series(root, "curve_pool_imbalance", ["curve", "ust", "imbalance", "3crv"], ["imbalance", "pool_imbalance"], None, "last", evidence, report)
    out["curve_ust_price"] = select_direct_series(root, "curve_ust_price", ["curve", "ust", "price", "swap"], ["ust_price", "price"], "ust", "last", evidence, report)
    out["bridge_outflow_terra_to_ethereum"] = event_flow(root, "bridge_outflow_terra_to_ethereum", ["bridge", "wormhole", "ethereum", "terra"], ["out", "terra", "ethereum", "bridge"], ["amount", "ust", "value"], evidence, report)
    out["bridge_inflow_ethereum_to_terra"] = event_flow(root, "bridge_inflow_ethereum_to_terra", ["bridge", "wormhole", "ethereum", "terra"], ["in", "ethereum", "terra", "bridge"], ["amount", "ust", "value"], evidence, report)
    out["btc_reserve_value"] = select_direct_series(root, "btc_reserve_value", ["btc", "reserve", "lfg"], ["reserve_value", "btc_value", "value_usd"], None, "last", evidence, report)
    out["reserve_intervention_volume"] = event_flow(root, "reserve_intervention_volume", ["reserve", "lfg", "intervention", "defend"], ["intervention", "sell", "buy", "defend"], ["amount", "value", "ust"], evidence, report)

    missing = [c for c in REQUIRED[1:] if c not in out or out[c].isna().any()]
    proxy_fields: list[str] = [
        ev.field for ev in evidence
        if not ev.exact and ev.field in {"terra_dex_liquidity", "terra_dex_depth"}
    ]

    if allow_proxy:
        # Fill *only* mathematically explicit proxies and mark the entire dataset QUALITY_WARNING.
        # Never use 0 as an "unknown" filler.
        if "block_height" in missing and out["block_height"].notna().any():
            out["block_height"] = out["block_height"].interpolate(limit_direction="both").round()
            proxy_fields.append("block_height") if "block_height" not in proxy_fields else None
        # State variables may be forward/backward filled between observed hourly snapshots.
        for c in ["ust_price", "luna_price", "ust_supply", "luna_supply", "anchor_total_deposits", "terra_dex_liquidity", "terra_dex_depth", "top10_anchor_share", "top100_anchor_share"]:
            if out[c].notna().any() and out[c].isna().any():
                out[c] = out[c].ffill().bfill()
                proxy_fields.append(c) if c not in proxy_fields else None
        # Flow variables may use zero only when source events are known and the series exists; absence of source remains NaN.
        flow_cols = ["anchor_deposit_flow", "anchor_withdrawal_flow", "ust_native_redemption_volume", "luna_minted_from_redemption", "luna_burned", "ust_dex_sell_volume"]
        for c in flow_cols:
            if out[c].notna().any():
                out[c] = out[c].fillna(0.0)
        missing = [c for c in REQUIRED[1:] if out[c].isna().any()]

    return out, evidence, missing, proxy_fields


def write_outputs(df: pd.DataFrame, evidence: list[Evidence], missing: list[str], proxy_fields: list[str], output: Path, work: Path, strict: bool, allow_proxy: bool, zip_path: Path, mapping_report: dict[str, Any]) -> None:
    work.mkdir(parents=True, exist_ok=True)
    evidence_csv = work / "terra_may2022_v1_evidence.csv"
    temp = df.reset_index().copy()
    temp["timestamp"] = temp["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    temp.to_csv(evidence_csv, index=False)

    (work / "mapping_report.json").write_text(json.dumps(mapping_report, indent=2, default=str), encoding="utf-8")
    (work / "evidence_map.json").write_text(json.dumps([asdict(x) for x in evidence], indent=2), encoding="utf-8")
    (work / "missing_fields.json").write_text(json.dumps({"missing_required_fields": missing, "proxy_fields": proxy_fields}, indent=2), encoding="utf-8")

    status = "REAL_HISTORICAL"
    if missing:
        status = "PARTIAL"
    elif proxy_fields or allow_proxy:
        status = "QUALITY_WARNING"

    manifest = {
        "dataset_version": "terra_may2022_v1",
        "status": status,
        "window": {"start": str(START), "end": str(END), "frequency": "1h", "rows": EXPECTED_ROWS},
        "primary_source": {"doi": DOI, "dataset_id": DATASET_ID, "version": DATASET_VERSION, "zip_sha256": sha256(zip_path)},
        "evidence_map": [asdict(x) for x in evidence],
        "missing_required_fields": missing,
        "proxy_fields": proxy_fields,
        "generated_at": datetime.now(UTC).isoformat(),
        "scientific_integrity": "REAL_HISTORICAL is only emitted when no required field is missing and no proxy mode is used."
    }
    (work / "provenance_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if strict and missing:
        raise SystemExit(
            "Strict build stopped: required historical fields are missing. "
            f"See {work / 'missing_fields.json'} and {work / 'mapping_report.json'}."
        )
    if strict and proxy_fields:
        raise SystemExit("Strict build stopped because proxy fields were used.")

    if missing:
        raise SystemExit(
            "No import-ready file written because required fields are still missing. "
            "Use the audit files to resolve source mappings; do not fabricate values."
        )

    final = df.reset_index().copy()
    final["timestamp"] = final["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    final["block_height"] = pd.to_numeric(final["block_height"], errors="raise").round().astype("int64")
    final["source_name"] = "Liu-Makarov-Schoar Terra/LUNA replication package"
    final["source_type"] = "REPLICATION_ONCHAIN_WITH_PRECRISIS_PROXIES" if proxy_fields else "REPLICATION_ONCHAIN"
    final["chain_id"] = "columbus-5"
    final["raw_reference"] = f"doi:{DOI}"
    final["quality_flag"] = status
    ordered = REQUIRED + OPTIONAL + ["source_name", "source_type", "chain_id", "raw_reference", "quality_flag"]
    final = final[[c for c in ordered if c in final.columns]]
    output.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(output, index=False)
    print(f"WROTE {output}")
    print(f"STATUS {status}")
    print(f"ROWS {len(final)}")


def main() -> None:
    p = argparse.ArgumentParser(description="Build DeFiStress terra_may2022_v1 from the Terra/LUNA replication package without fabricating missing data.")
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--work-dir", type=Path, default=Path("data/raw/terra_may2022_v1"))
    p.add_argument("--output", type=Path, default=Path("data/processed/terra_may2022_v1.csv"))
    p.add_argument("--replication-zip", type=Path)
    group = p.add_mutually_exclusive_group()
    group.add_argument("--strict", action="store_true", help="Require complete exact historical mapping; emit REAL_HISTORICAL only.")
    group.add_argument("--allow-proxy", action="store_true", help="Allow documented gap-filling/proxies; output can only be QUALITY_WARNING.")
    args = p.parse_args()

    repo = args.repo_root.resolve()
    work = (repo / args.work_dir).resolve() if not args.work_dir.is_absolute() else args.work_dir.resolve()
    output = (repo / args.output).resolve() if not args.output.is_absolute() else args.output.resolve()
    work.mkdir(parents=True, exist_ok=True)

    zip_path = args.replication_zip.resolve() if args.replication_zip else mendeley_download(work)
    if not zip_path.exists():
        raise SystemExit(f"Replication zip not found: {zip_path}")
    root = extract_zip(zip_path, work)
    inventory(root, work / "source_inventory.csv")
    mapping_report: dict[str, Any] = {}
    df, evidence, missing, proxy_fields = build(root, args.allow_proxy, mapping_report)
    write_outputs(df, evidence, missing, proxy_fields, output, work, args.strict, args.allow_proxy, zip_path, mapping_report)


if __name__ == "__main__":
    main()
