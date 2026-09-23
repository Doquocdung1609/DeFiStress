from __future__ import annotations

import json
from pathlib import Path
import math

import numpy as np
import pandas as pd

ROOT = Path("data/raw/terra_may2022_v1/replication")
OUT = Path("data/raw/terra_may2022_v1/v4_remaining_diagnostics.json")

START = pd.Timestamp("2022-05-01T00:00:00Z")
END = pd.Timestamp("2022-05-13T23:00:00Z")
CUTOFF = pd.Timestamp("2022-05-06T23:59:59Z")
GRID = pd.date_range(START, END, freq="1h", tz="UTC")

def find(name: str) -> Path:
    matches = list(ROOT.rglob(name))
    if not matches:
        raise FileNotFoundError(f"Cannot find {name} under {ROOT.resolve()}")
    return matches[0]

def fnum(x):
    try:
        if pd.isna(x):
            return None
        return float(x)
    except Exception:
        return str(x)

def ts(x):
    if x is None or pd.isna(x):
        return None
    return pd.Timestamp(x).isoformat()

def describe_series(s: pd.Series) -> dict:
    x = pd.to_numeric(s, errors="coerce")
    return {
        "count": int(x.notna().sum()),
        "missing": int(x.isna().sum()),
        "min": fnum(x.min()) if x.notna().any() else None,
        "max": fnum(x.max()) if x.notna().any() else None,
        "median": fnum(x.median()) if x.notna().any() else None,
    }

def block_diag() -> dict:
    path = find("Anchor_global_stats_fullnode.parquet")
    df = pd.read_parquet(path)
    idx = pd.to_datetime(df.index, utc=True, errors="coerce")
    height = pd.to_numeric(df["height"], errors="coerce")
    x = pd.DataFrame({"t": idx, "height": height.to_numpy()}).dropna().sort_values("t")
    win = x[(x["t"] >= START - pd.Timedelta(hours=24)) & (x["t"] <= END + pd.Timedelta(hours=24))].copy()

    diffs = win["t"].diff().dropna()
    hourly_last = win.set_index("t")["height"].resample("1h").last().reindex(GRID)
    ff = hourly_last.ffill()

    asof6 = pd.merge_asof(
        pd.DataFrame({"t": GRID}),
        win,
        on="t",
        direction="backward",
        tolerance=pd.Timedelta(hours=6),
    ).set_index("t")["height"]

    return {
        "file": str(path),
        "raw_window_rows": int(len(win)),
        "raw_min_time": ts(win["t"].min()) if len(win) else None,
        "raw_max_time": ts(win["t"].max()) if len(win) else None,
        "max_raw_gap_minutes": fnum(diffs.max() / pd.Timedelta(minutes=1)) if len(diffs) else None,
        "height_summary": describe_series(win["height"]),
        "height_monotonic_non_decreasing": bool(win["height"].dropna().is_monotonic_increasing),
        "hourly_last_missing_count": int(hourly_last.isna().sum()),
        "hourly_last_missing_timestamps": [t.isoformat() for t in hourly_last[hourly_last.isna()].index[:50]],
        "hourly_ffill_missing_count": int(ff.isna().sum()),
        "asof_6h_missing_count": int(asof6.isna().sum()),
        "asof_6h_missing_timestamps": [t.isoformat() for t in asof6[asof6.isna()].index[:50]],
        "first_5_window": [
            {"t": r.t.isoformat(), "height": fnum(r.height)}
            for r in win.head(5).itertuples()
        ],
        "last_5_window": [
            {"t": r.t.isoformat(), "height": fnum(r.height)}
            for r in win.tail(5).itertuples()
        ],
    }

def compare_formula(direct: pd.Series, raw: pd.Series, label: str) -> dict:
    joined = pd.concat([direct.rename("direct"), raw.rename("raw")], axis=1, join="inner").dropna()
    joined = joined[(joined.index >= START.floor("D")) & (joined.index <= CUTOFF.floor("D"))]
    joined = joined[(joined["direct"] > 0) & (joined["raw"] > 0)]
    if joined.empty:
        return {"formula": label, "overlap_days": 0}

    ratios = joined["direct"] / joined["raw"]
    free_scale = float(ratios.median())
    free_pred = joined["raw"] * free_scale
    free_mre = float(((free_pred - joined["direct"]).abs() / joined["direct"]).median())

    powers = [10.0 ** p for p in range(-18, 19, 3)]
    nearest_pow = min(
        powers,
        key=lambda z: abs(math.log10(max(free_scale, 1e-300)) - math.log10(z)),
    )
    pow_pred = joined["raw"] * nearest_pow
    pow_mre = float(((pow_pred - joined["direct"]).abs() / joined["direct"]).median())

    rows = []
    for idx, row in joined.iterrows():
        rows.append({
            "date": idx.isoformat(),
            "direct": fnum(row["direct"]),
            "raw": fnum(row["raw"]),
            "ratio_direct_over_raw": fnum(row["direct"] / row["raw"]),
        })

    return {
        "formula": label,
        "overlap_days": int(len(joined)),
        "median_ratio_direct_over_raw": free_scale,
        "median_relative_error_free_scale": free_mre,
        "nearest_power_of_10_scale": nearest_pow,
        "median_relative_error_power10_scale": pow_mre,
        "rows": rows,
    }

def anchor_diag() -> dict:
    gp = find("Anchor_global_stats_fullnode.parquet")
    dp = find("Anchor_daily_stats.parquet")
    ap = find("aust_supply_col5.parquet")

    g = pd.read_parquet(gp)
    d = pd.read_parquet(dp)
    a = pd.read_parquet(ap)

    gidx = pd.to_datetime(g.index, utc=True, errors="coerce")
    g = g.copy()
    g.index = gidx

    didx = pd.to_datetime(d.index, utc=True, errors="coerce").floor("D")
    direct = pd.Series(
        pd.to_numeric(d["deposit balance"], errors="coerce").to_numpy(),
        index=didx,
        name="deposit_balance",
    ).dropna().sort_index()
    direct = direct[~direct.index.duplicated(keep="last")]

    prev_supply = pd.to_numeric(g["prev_aterra_supply"], errors="coerce")
    prev_rate = pd.to_numeric(g["prev_exchange_rate"], errors="coerce")

    raw_mul_daily = (prev_supply * prev_rate).resample("1D").last()
    raw_div_daily = (prev_supply / prev_rate.replace(0, np.nan)).resample("1D").last()
    raw_supply_daily = prev_supply.resample("1D").last()

    adate = pd.to_datetime(a["date"], utc=True, errors="coerce").dt.floor("D")
    asupply = pd.Series(
        pd.to_numeric(a["supply"], errors="coerce").to_numpy(),
        index=adate,
        name="aust_supply",
    ).dropna().sort_index()
    asupply = asupply[~asupply.index.duplicated(keep="last")]

    rate_daily = prev_rate.resample("1D").last()
    aust_mul = pd.concat([asupply, rate_daily.rename("rate")], axis=1).dropna()
    aust_mul_series = aust_mul["aust_supply"] * aust_mul["rate"]
    aust_div_series = aust_mul["aust_supply"] / aust_mul["rate"].replace(0, np.nan)

    gwin = g[(g.index >= START) & (g.index <= END + pd.Timedelta(hours=1))]
    raw_hourly = (pd.to_numeric(gwin["prev_aterra_supply"], errors="coerce")
                  * pd.to_numeric(gwin["prev_exchange_rate"], errors="coerce")).resample("1h").last().reindex(GRID)

    return {
        "global_file": str(gp),
        "daily_file": str(dp),
        "aust_supply_file": str(ap),
        "global_index_min": ts(g.index.min()),
        "global_index_max": ts(g.index.max()),
        "daily_index_min": ts(direct.index.min()),
        "daily_index_max": ts(direct.index.max()),
        "aust_supply_date_min": ts(asupply.index.min()),
        "aust_supply_date_max": ts(asupply.index.max()),
        "direct_deposit_balance_summary": describe_series(direct),
        "prev_aterra_supply_summary_target_window": describe_series(gwin["prev_aterra_supply"]),
        "prev_exchange_rate_summary_target_window": describe_series(gwin["prev_exchange_rate"]),
        "raw_mul_hourly_missing_count": int(raw_hourly.isna().sum()),
        "raw_mul_hourly_missing_timestamps": [t.isoformat() for t in raw_hourly[raw_hourly.isna()].index[:50]],
        "formula_tests_pre_cutoff": [
            compare_formula(direct, raw_mul_daily, "prev_aterra_supply * prev_exchange_rate"),
            compare_formula(direct, raw_div_daily, "prev_aterra_supply / prev_exchange_rate"),
            compare_formula(direct, raw_supply_daily, "prev_aterra_supply only"),
            compare_formula(direct, aust_mul_series, "aust_supply_col5.supply * prev_exchange_rate_daily"),
            compare_formula(direct, aust_div_series, "aust_supply_col5.supply / prev_exchange_rate_daily"),
            compare_formula(direct, asupply, "aust_supply_col5.supply only"),
        ],
        "daily_tail": [
            {"date": i.isoformat(), "deposit_balance": fnum(v)}
            for i, v in direct.tail(12).items()
        ],
        "aust_supply_tail": [
            {"date": i.isoformat(), "supply": fnum(v)}
            for i, v in asupply.tail(12).items()
        ],
    }

def main():
    if not ROOT.exists():
        raise SystemExit(f"Replication root not found: {ROOT.resolve()}")
    payload = {
        "block_height": block_diag(),
        "anchor_total_deposits": anchor_diag(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"WROTE {OUT}")
    b = payload["block_height"]
    print("\nBLOCK:")
    print("  max raw gap minutes:", b["max_raw_gap_minutes"])
    print("  asof 6h missing:", b["asof_6h_missing_count"])
    print("  hourly ffill missing:", b["hourly_ffill_missing_count"])

    a = payload["anchor_total_deposits"]
    print("\nANCHOR:")
    print("  raw hourly missing:", a["raw_mul_hourly_missing_count"])
    for test in a["formula_tests_pre_cutoff"]:
        print(
            " ",
            test["formula"],
            "| overlap=", test.get("overlap_days"),
            "| free-scale MRE=", test.get("median_relative_error_free_scale"),
            "| power10 MRE=", test.get("median_relative_error_power10_scale"),
        )

if __name__ == "__main__":
    main()
