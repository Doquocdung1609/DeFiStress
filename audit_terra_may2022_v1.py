from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

CSV = Path("data/processed/terra_may2022_v1.csv")
MAPPING = Path("data/raw/terra_may2022_v1/mapping_report.json")
OUT = Path("data/processed/terra_may2022_v1_audit.json")

START = pd.Timestamp("2022-05-01T00:00:00Z")
END = pd.Timestamp("2022-05-13T23:00:00Z")
CUTOFF = pd.Timestamp("2022-05-06T23:59:59Z")
EXPECTED_ROWS = 312

REQUIRED = [
    "timestamp",
    "block_height",
    "ust_price",
    "luna_price",
    "ust_supply",
    "luna_supply",
    "anchor_total_deposits",
    "anchor_deposit_flow",
    "anchor_withdrawal_flow",
    "ust_native_redemption_volume",
    "luna_minted_from_redemption",
    "luna_burned",
    "ust_dex_sell_volume",
    "terra_dex_liquidity",
    "terra_dex_depth",
    "top10_anchor_share",
    "top100_anchor_share",
]

NONNEG = [
    c for c in REQUIRED
    if c not in {"timestamp", "block_height", "top10_anchor_share", "top100_anchor_share"}
]

def main():
    if not CSV.exists():
        raise SystemExit(f"Missing dataset: {CSV.resolve()}")

    df = pd.read_csv(CSV)
    result = {
        "dataset": str(CSV),
        "rows": int(len(df)),
        "expected_rows": EXPECTED_ROWS,
        "checks": {},
        "summaries": {},
        "warnings": [],
    }

    missing_cols = [c for c in REQUIRED if c not in df.columns]
    result["checks"]["required_columns_present"] = not missing_cols
    result["checks"]["missing_columns"] = missing_cols

    if "timestamp" not in df.columns:
        OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        raise SystemExit("timestamp column missing")

    ts = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    result["checks"]["timestamp_parse_ok"] = bool(ts.notna().all())
    result["checks"]["row_count_312"] = len(df) == EXPECTED_ROWS
    result["checks"]["start_ok"] = bool(len(df) and ts.iloc[0] == START)
    result["checks"]["end_ok"] = bool(len(df) and ts.iloc[-1] == END)
    result["checks"]["timestamps_sorted"] = bool(ts.is_monotonic_increasing)
    result["checks"]["duplicate_timestamps"] = int(ts.duplicated().sum())

    if ts.notna().all() and len(ts) > 1:
        diffs = ts.sort_values().diff().dropna()
        expected = pd.Timedelta(hours=1)
        bad = diffs[diffs != expected]
        result["checks"]["hourly_grid_ok"] = len(bad) == 0
        result["checks"]["non_hourly_gap_count"] = int(len(bad))
        if len(bad):
            result["warnings"].append(
                f"{len(bad)} timestamp gaps are not exactly 1 hour"
            )
    else:
        result["checks"]["hourly_grid_ok"] = False

    numeric_cols = [c for c in REQUIRED if c != "timestamp" and c in df.columns]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    result["checks"]["required_na_counts"] = {
        c: int(df[c].isna().sum()) for c in numeric_cols
    }
    result["checks"]["no_required_na"] = all(
        df[c].isna().sum() == 0 for c in numeric_cols
    )

    neg_counts = {
        c: int((df[c] < 0).sum()) for c in NONNEG if c in df.columns
    }
    result["checks"]["negative_counts"] = neg_counts
    result["checks"]["no_negative_required_values"] = all(v == 0 for v in neg_counts.values())

    for c in ["top10_anchor_share", "top100_anchor_share"]:
        if c in df.columns:
            outside = (~df[c].between(0, 1)).sum()
            result["checks"][f"{c}_outside_0_1"] = int(outside)

    if {"top10_anchor_share", "top100_anchor_share"}.issubset(df.columns):
        bad_order = (df["top10_anchor_share"] > df["top100_anchor_share"]).sum()
        result["checks"]["top10_le_top100"] = int(bad_order) == 0
        result["checks"]["top10_gt_top100_count"] = int(bad_order)

    if "block_height" in df.columns:
        bh = df["block_height"]
        result["checks"]["block_height_non_decreasing"] = bool(bh.is_monotonic_increasing)
        flat = (bh.diff() == 0)
        flat_times = ts[flat.fillna(False)]
        result["summaries"]["block_height_flat_hours"] = [
            t.isoformat() for t in flat_times.tolist()
        ]

    for c in [
        "ust_price",
        "luna_price",
        "ust_supply",
        "luna_supply",
        "anchor_total_deposits",
        "terra_dex_liquidity",
        "terra_dex_depth",
        "ust_native_redemption_volume",
        "anchor_withdrawal_flow",
    ]:
        if c in df.columns:
            s = df[c]
            result["summaries"][c] = {
                "min": float(s.min()),
                "max": float(s.max()),
                "median": float(s.median()),
                "first": float(s.iloc[0]),
                "last": float(s.iloc[-1]),
                "unique_values": int(s.nunique(dropna=True)),
            }

    # Proxy integrity: expected to be fixed through replay in V6.
    for c in ["terra_dex_liquidity", "terra_dex_depth"]:
        if c in df.columns:
            result["checks"][f"{c}_constant_through_replay"] = int(df[c].nunique()) == 1

    # Useful checkpoint rows around the pre-crisis/evaluation boundary and collapse.
    checkpoints = [
        "2022-05-01T00:00:00Z",
        "2022-05-06T23:00:00Z",
        "2022-05-07T00:00:00Z",
        "2022-05-09T00:00:00Z",
        "2022-05-11T00:00:00Z",
        "2022-05-13T00:00:00Z",
        "2022-05-13T23:00:00Z",
    ]
    df2 = df.copy()
    df2["_ts"] = ts
    cols = [
        c for c in [
            "timestamp", "block_height", "ust_price", "luna_price",
            "ust_supply", "luna_supply", "anchor_total_deposits",
            "ust_native_redemption_volume", "terra_dex_liquidity",
            "terra_dex_depth", "top10_anchor_share", "top100_anchor_share"
        ] if c in df2.columns
    ]
    result["checkpoints"] = []
    for cp in checkpoints:
        t = pd.Timestamp(cp)
        row = df2.loc[df2["_ts"] == t, cols]
        if not row.empty:
            result["checkpoints"].append(row.iloc[0].to_dict())

    # Mapping/provenance audit.
    if MAPPING.exists():
        mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
        dex = mapping.get("dex_proxy", [])
        result["provenance"] = {"dex_proxy": dex}
        used = [x for x in dex if x.get("result") == "used"]
        result["checks"]["dex_proxy_has_used_entry"] = bool(used)
        if used:
            entry = used[-1]
            result["checks"]["dex_proxy_pre_cutoff_only"] = (
                int(entry.get("pre_cutoff_days", 999)) <= 6
            )
            result["checks"]["dex_proxy_positive"] = (
                float(entry.get("liquidity_proxy_hourly_equivalent", 0)) > 0
                and float(entry.get("depth_proxy_hourly_equivalent_q25", 0)) > 0
            )
    else:
        result["warnings"].append(f"Mapping report not found: {MAPPING}")

    # Split counts for anti-lookahead reporting.
    cal_mask = ts <= CUTOFF
    eval_mask = ts > CUTOFF
    result["summaries"]["split"] = {
        "calibration_rows": int(cal_mask.sum()),
        "evaluation_rows": int(eval_mask.sum()),
        "cutoff": CUTOFF.isoformat(),
    }

    # Overall verdict.
    hard_checks = [
        result["checks"].get("required_columns_present", False),
        result["checks"].get("row_count_312", False),
        result["checks"].get("start_ok", False),
        result["checks"].get("end_ok", False),
        result["checks"].get("timestamps_sorted", False),
        result["checks"].get("duplicate_timestamps", 1) == 0,
        result["checks"].get("hourly_grid_ok", False),
        result["checks"].get("no_required_na", False),
        result["checks"].get("no_negative_required_values", False),
        result["checks"].get("top10_le_top100", False),
        result["checks"].get("dex_proxy_has_used_entry", False),
        result["checks"].get("dex_proxy_pre_cutoff_only", False),
        result["checks"].get("dex_proxy_positive", False),
    ]
    result["audit_pass"] = all(hard_checks)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(f"WROTE {OUT}")
    print("AUDIT_PASS =", result["audit_pass"])
    print("ROWS =", result["rows"])
    print("CALIBRATION_ROWS =", result["summaries"]["split"]["calibration_rows"])
    print("EVALUATION_ROWS =", result["summaries"]["split"]["evaluation_rows"])
    print("REQUIRED_NA =", result["checks"]["required_na_counts"])
    print("NEGATIVE_COUNTS =", result["checks"]["negative_counts"])
    print("DEX_LIQUIDITY_UNIQUE =", result["summaries"].get("terra_dex_liquidity", {}).get("unique_values"))
    print("DEX_DEPTH_UNIQUE =", result["summaries"].get("terra_dex_depth", {}).get("unique_values"))

if __name__ == "__main__":
    main()
