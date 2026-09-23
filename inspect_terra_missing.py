from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path("data/raw/terra_may2022_v1/replication")
OUT = Path("data/raw/terra_may2022_v1/missing_source_detail.json")

TARGETS = [
    "Anchor_daily_stats.parquet",
    "Anchor_global_stats_fullnode.parquet",
    "columbus-5-lunaust-supply-breakdown-fullnode.parquet",
    "luna_total_supply_run.parquet",
    "curve_ust_3pool_may7.parquet",
    "ust_luna_swaps_run.parquet",
]

def norm_value(v: Any) -> Any:
    if isinstance(v, pd.Timestamp):
        return v.isoformat()
    if pd.isna(v):
        return None
    if hasattr(v, "item"):
        try:
            return v.item()
        except Exception:
            pass
    return str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v

def inspect_file(path: Path) -> dict[str, Any]:
    df = pd.read_parquet(path)
    result: dict[str, Any] = {
        "path": str(path),
        "shape": list(df.shape),
        "columns": [str(c) for c in df.columns],
        "dtypes": {str(c): str(df[c].dtype) for c in df.columns},
        "index_type": type(df.index).__name__,
        "index_name": None if df.index.name is None else str(df.index.name),
        "index_dtype": str(df.index.dtype),
        "head": [
            {str(k): norm_value(v) for k, v in row.items()}
            for row in df.head(5).reset_index().to_dict(orient="records")
        ],
        "tail": [
            {str(k): norm_value(v) for k, v in row.items()}
            for row in df.tail(5).reset_index().to_dict(orient="records")
        ],
    }

    # Time candidates.
    time_info = {}
    for c in list(df.columns):
        name = str(c).lower()
        if any(k in name for k in ["time", "date", "timestamp"]):
            parsed = pd.to_datetime(df[c], utc=True, errors="coerce")
            if parsed.notna().any():
                time_info[str(c)] = {
                    "valid_ratio": float(parsed.notna().mean()),
                    "min": parsed.min().isoformat(),
                    "max": parsed.max().isoformat(),
                }
    try:
        idx_parsed = pd.to_datetime(df.index, utc=True, errors="coerce")
        if pd.Series(idx_parsed).notna().any():
            time_info["__index__"] = {
                "valid_ratio": float(pd.Series(idx_parsed).notna().mean()),
                "min": pd.Series(idx_parsed).min().isoformat(),
                "max": pd.Series(idx_parsed).max().isoformat(),
            }
    except Exception:
        pass
    result["time_candidates"] = time_info

    # Numeric summaries for likely useful columns.
    summaries = {}
    for c in df.columns:
        vals = pd.to_numeric(df[c], errors="coerce")
        if vals.notna().mean() >= 0.5:
            summaries[str(c)] = {
                "count": int(vals.notna().sum()),
                "min": norm_value(vals.min()),
                "max": norm_value(vals.max()),
                "median": norm_value(vals.median()),
            }
    result["numeric_summary"] = summaries

    # Useful categories.
    for col in ["denom", "action", "quote_asset"]:
        if col in df.columns:
            vc = df[col].astype(str).value_counts(dropna=False).head(30)
            result[f"{col}_values"] = {str(k): int(v) for k, v in vc.items()}

    return result

def code_references(root: Path, needles: list[str]) -> dict[str, list[dict[str, Any]]]:
    out = {n: [] for n in needles}
    exts = {".py", ".md", ".txt", ".rst"}
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        try:
            lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines):
            low = line.lower()
            for n in needles:
                if n.lower() in low:
                    start = max(0, i - 3)
                    end = min(len(lines), i + 4)
                    out[n].append({
                        "file": str(p),
                        "line": i + 1,
                        "context": lines[start:end],
                    })
    return out

def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"Replication folder not found: {ROOT.resolve()}")

    files = {}
    for target in TARGETS:
        matches = list(ROOT.rglob(target))
        if not matches:
            files[target] = {"error": "NOT_FOUND"}
            continue
        try:
            files[target] = inspect_file(matches[0])
        except Exception as exc:
            files[target] = {"path": str(matches[0]), "error": repr(exc)}

    refs = code_references(
        ROOT,
        [
            "Anchor_daily_stats.parquet",
            "Anchor_global_stats_fullnode.parquet",
            "columbus-5-lunaust-supply-breakdown-fullnode.parquet",
            "luna_total_supply_run.parquet",
            "curve_ust_3pool_may7.parquet",
        ],
    )

    payload = {"files": files, "code_references": refs}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"WROTE {OUT}")
    for name, info in files.items():
        print("\n==", name, "==")
        if "error" in info:
            print(info["error"])
            continue
        print("shape:", info["shape"])
        print("index:", info["index_type"], info["index_name"], info["index_dtype"])
        print("columns:", ", ".join(info["columns"]))
        print("time candidates:", info["time_candidates"])

if __name__ == "__main__":
    main()
