# ruff: noqa: E501, SIM105
"""Build and audit the extended Terra historical data layer.

This module intentionally does not import or modify the Terra simulation model.
It consumes the immutable Liu--Makarov--Schoar replication package and writes
only derived artifacts below ``data/processed/terra_{extended,data_completion}``.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import zipfile
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / "data" / "raw" / "terra_may2022_v1"
REPLICATION_ROOT = RAW_ROOT / "replication" / "terra-luna-run-replication"
REPLICATION_DATA = REPLICATION_ROOT / "data"
COMPLETION_DIR = ROOT / "data" / "processed" / "terra_data_completion"
EXTENDED_DIR = ROOT / "data" / "processed" / "terra_extended"
START = pd.Timestamp("2022-03-01T00:00:00Z")
END = pd.Timestamp("2022-05-13T23:00:00Z")
DOI = "10.17632/j5d8n7hzdy.4"
DATASET_VERSION = "terra_extended_20220301_20220513_v1"

QUALITY_CLASSES = {
    "HISTORICAL_DIRECT",
    "HISTORICAL_DERIVED",
    "HISTORICAL_STATE_CARRIED_FORWARD",
    "PARTIAL_HISTORICAL",
    "LEGACY_PROXY",
    "SYNTHETIC_FIXTURE",
    "UNAVAILABLE",
    "QUARANTINED",
}

CORE_COLUMNS = [
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
    "gross_luna_issuance_from_native_swaps",
    "backing_ratio",
    "top10_anchor_share",
    "top100_anchor_share",
]


@dataclass(frozen=True)
class InventoryRow:
    file_path: str
    file_format: str
    row_count: int | None
    column_names: str
    index_type: str
    timestamp_column: str
    start_timestamp: str
    end_timestamp: str
    estimated_frequency: str
    file_size_bytes: int
    candidate_use: str
    source_provenance: str


def _utc(values: Any) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(pd.to_datetime(values, utc=True, errors="coerce")).as_unit("ns")


def hourly_index() -> pd.DatetimeIndex:
    """Return the exact inclusive target index (74 days, 1,776 hours)."""
    return pd.date_range(START, END, freq="h", name="timestamp")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str:
    """Return the code commit, not the later commit that merely bundles outputs."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", "scripts/terra/complete_historical_data.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def carry_state_backward(
    source: pd.Series,
    target: pd.DatetimeIndex,
    *,
    valid_from: pd.Timestamp | None = None,
    valid_through: pd.Timestamp | None = None,
) -> pd.Series:
    """As-of carry a sampled state without using any observation after a target."""
    clean = source.copy()
    clean.index = _utc(clean.index)
    clean = clean[~clean.index.isna()].sort_index()
    clean = clean[~clean.index.duplicated(keep="last")]
    left = pd.DataFrame({"timestamp": target})
    right = pd.DataFrame({"source_timestamp": clean.index, "value": clean.to_numpy()})
    merged = pd.merge_asof(
        left.sort_values("timestamp"),
        right.sort_values("source_timestamp"),
        left_on="timestamp",
        right_on="source_timestamp",
        direction="backward",
    )
    out = pd.Series(merged["value"].to_numpy(), index=target, dtype="float64")
    if valid_from is not None:
        out.loc[target < valid_from] = np.nan
    if valid_through is not None:
        out.loc[target > valid_through] = np.nan
    return out


def source_timestamp_asof(source_index: Iterable[Any], target: pd.DatetimeIndex) -> pd.Series:
    """Expose source timestamps used by an as-of mapping for leakage tests/audit."""
    source = _utc(source_index).dropna().sort_values().unique()
    left = pd.DataFrame({"timestamp": target})
    right = pd.DataFrame({"source_timestamp": source})
    merged = pd.merge_asof(left, right, left_on="timestamp", right_on="source_timestamp", direction="backward")
    return pd.Series(merged["source_timestamp"].to_numpy(), index=target)


def aggregate_event_flows(
    events: pd.DataFrame,
    *,
    timestamp_column: str,
    value_columns: Sequence[str],
    target: pd.DatetimeIndex,
    coverage_start: pd.Timestamp,
    coverage_end: pd.Timestamp,
) -> pd.DataFrame:
    """Aggregate real events; zero only inside documented complete coverage."""
    data = events.copy()
    data[timestamp_column] = pd.to_datetime(data[timestamp_column], utc=True)
    data["timestamp"] = data[timestamp_column].dt.floor("h")
    grouped = data.groupby("timestamp", sort=True)[list(value_columns)].sum()
    output = grouped.reindex(target)
    covered = (target >= coverage_start) & (target <= coverage_end)
    output.loc[covered, list(value_columns)] = output.loc[covered, list(value_columns)].fillna(0.0)
    return output


def detect_duplicate_mappings(
    frame: pd.DataFrame,
    *,
    correlation_threshold: float = 0.999999,
    relative_tolerance: float = 1e-12,
) -> list[dict[str, Any]]:
    """Find numeric columns that are near-identical on their common support."""
    numeric = frame.select_dtypes(include=[np.number])
    findings: list[dict[str, Any]] = []
    for left_index, left in enumerate(numeric.columns):
        for right in numeric.columns[left_index + 1 :]:
            pair = numeric[[left, right]].dropna()
            if len(pair) < 2:
                continue
            corr = float(pair[left].corr(pair[right]))
            scale = max(float(pair[[left, right]].abs().to_numpy().max()), 1.0)
            max_abs = float((pair[left] - pair[right]).abs().max())
            if corr >= correlation_threshold and max_abs <= relative_tolerance * scale:
                findings.append(
                    {
                        "left": left,
                        "right": right,
                        "correlation": corr,
                        "max_absolute_difference": max_abs,
                        "overlap_rows": len(pair),
                    }
                )
    return findings


def _read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def _source_paths() -> dict[str, Path]:
    return {
        "block_anchor_state": REPLICATION_DATA / "anchor" / "Anchor_global_stats_fullnode.parquet",
        "anchor_daily": REPLICATION_DATA / "anchor" / "Anchor_daily_stats.parquet",
        "anchor_concentration": REPLICATION_DATA / "anchor" / "anchor_deposit_concentration.parquet",
        "anchor_events": REPLICATION_DATA / "anchor_run" / "anchor_run_tx_cleaned.parquet",
        "anchor_epoch": REPLICATION_DATA / "anchor_run" / "epoch_state_fig10.parquet",
        "anchor_cashflow": REPLICATION_DATA / "anchor" / "anchor_cashflow_transfers.parquet",
        "anchor_labels": REPLICATION_DATA / "labels" / "anchor_contracts.csv",
        "daily_balances": REPLICATION_DATA
        / "daily_balances"
        / "columbus-5-lunaust-supply-breakdown-fullnode.parquet",
        "luna_supply": REPLICATION_DATA / "native_swaps" / "luna_total_supply_run.parquet",
        "native_swaps": REPLICATION_DATA / "native_swaps" / "ust_luna_swaps_run.parquet",
        "ust_price_daily": REPLICATION_DATA / "external" / "ustc-usd-max.csv",
        "luna_price_daily": REPLICATION_DATA / "external" / "lunc-usd-max.csv",
        "ust_price_minute": REPLICATION_DATA / "prices" / "ust_price_may2022.parquet",
        "luna_price_minute": REPLICATION_DATA / "prices" / "luna_price_may2022.parquet",
        "curve": REPLICATION_DATA / "curve" / "curve_ust_3pool_may7.parquet",
    }


def _daily_price(path: Path) -> pd.Series:
    frame = pd.read_csv(path)
    index = _utc(frame["snapped_at"])
    return pd.Series(frame["price"].to_numpy(), index=index, dtype="float64").sort_index()


def _minute_price(path: Path, column: str) -> pd.Series:
    frame = _read_parquet(path)
    index = _utc(frame["time"])
    return pd.Series(frame[column].to_numpy(), index=index, dtype="float64").sort_index()


def _composite_price(daily_path: Path, minute_path: Path, minute_column: str, target: pd.DatetimeIndex) -> pd.Series:
    daily = carry_state_backward(_daily_price(daily_path), target)
    minute = carry_state_backward(_minute_price(minute_path, minute_column), target)
    minute_start = pd.Timestamp("2022-05-01T00:00:00Z")
    daily.loc[target >= minute_start] = minute.loc[target >= minute_start]
    return daily


def _hourly_anchor_state(target: pd.DatetimeIndex) -> tuple[pd.Series, pd.Series, pd.Series]:
    paths = _source_paths()
    global_state = _read_parquet(paths["block_anchor_state"]).sort_index()
    global_index = _utc(global_state.index)
    block = carry_state_backward(pd.Series(global_state["height"].to_numpy(), index=global_index), target)
    cached_deposits = pd.Series(
        global_state["prev_aterra_supply"].to_numpy()
        * global_state["prev_exchange_rate"].to_numpy()
        / 1e6,
        index=global_index,
    )
    deposits = carry_state_backward(cached_deposits, target)

    epoch = _read_parquet(paths["anchor_epoch"])
    epoch_index = _utc(epoch["time_utc"])
    epoch_deposits = pd.Series(epoch["deposit_b_ust"].to_numpy() * 1e9, index=epoch_index)
    live = carry_state_backward(
        epoch_deposits,
        target,
        valid_from=pd.Timestamp("2022-05-06T00:14:00Z"),
        valid_through=pd.Timestamp("2022-05-15T23:59:00Z"),
    )
    deposits.loc[live.notna()] = live.loc[live.notna()]
    source_time = source_timestamp_asof(global_index, target)
    return block, deposits, source_time


def _daily_supply(target: pd.DatetimeIndex) -> tuple[pd.Series, pd.Series]:
    balances = _read_parquet(_source_paths()["daily_balances"])
    balances["date"] = pd.to_datetime(balances["date"], utc=True)
    grouped = balances.groupby(["date", "denom"], sort=True)["balance"].sum().unstack()
    ust = carry_state_backward(grouped["UST"], target, valid_through=pd.Timestamp("2022-05-13T23:00:00Z"))
    holder_luna = carry_state_backward(
        grouped["LUNA"], target, valid_through=pd.Timestamp("2022-05-13T23:00:00Z")
    )
    return ust, holder_luna


def _luna_total_supply(target: pd.DatetimeIndex) -> pd.Series:
    supply = _read_parquet(_source_paths()["luna_supply"])["luna_supply"].copy()
    supply.index = _utc(supply.index)
    exact = supply.reindex(target)
    exact.loc[target < pd.Timestamp("2022-05-01T00:00:00Z")] = np.nan
    return exact.astype("float64")


def _anchor_flows(target: pd.DatetimeIndex) -> pd.DataFrame:
    events = _read_parquet(_source_paths()["anchor_events"])
    selected = events[events["action"].isin(["deposit", "withdraw"])].copy()
    selected["anchor_deposit_flow"] = np.where(selected["action"].eq("deposit"), selected["ust_vol"], 0.0)
    selected["anchor_withdrawal_flow"] = np.where(
        selected["action"].eq("withdraw"), selected["ust_vol"], 0.0
    )
    return aggregate_event_flows(
        selected,
        timestamp_column="time",
        value_columns=["anchor_deposit_flow", "anchor_withdrawal_flow"],
        target=target,
        coverage_start=pd.Timestamp("2022-05-06T00:00:00Z"),
        coverage_end=END,
    )


def _native_swap_flows(target: pd.DatetimeIndex) -> pd.DataFrame:
    swaps = _read_parquet(_source_paths()["native_swaps"])
    swaps["time"] = pd.to_datetime(swaps["time"], utc=True)
    swaps = swaps[(swaps["time"] >= pd.Timestamp("2022-05-07T00:00:00Z")) & (swaps["time"] <= END)].copy()
    swaps["ust_native_redemption_volume"] = swaps["offer_amount"]
    swaps["gross_luna_issuance_from_native_swaps"] = swaps["swap_amount"] + swaps["fee_amount"]
    return aggregate_event_flows(
        swaps,
        timestamp_column="time",
        value_columns=["ust_native_redemption_volume", "gross_luna_issuance_from_native_swaps"],
        target=target,
        coverage_start=pd.Timestamp("2022-05-07T00:00:00Z"),
        coverage_end=END,
    )


def _concentration(target: pd.DatetimeIndex) -> pd.DataFrame:
    concentration = _read_parquet(_source_paths()["anchor_concentration"])
    concentration.index = _utc(concentration.index)
    valid_through = pd.Timestamp("2022-05-06T23:00:00Z")
    return pd.DataFrame(
        {
            "top10_anchor_share": carry_state_backward(
                concentration["Top 10"] / 100.0, target, valid_through=valid_through
            ),
            "top100_anchor_share": carry_state_backward(
                concentration["Top 100"] / 100.0, target, valid_through=valid_through
            ),
        },
        index=target,
    )


def build_hourly_state() -> tuple[pd.DataFrame, dict[str, Any]]:
    target = hourly_index()
    block, anchor_deposits, block_source_time = _hourly_anchor_state(target)
    ust_supply, luna_holder_sum = _daily_supply(target)
    luna_supply = _luna_total_supply(target)
    frame = pd.DataFrame(index=target)
    frame["block_height"] = block.round().astype("Int64")
    frame["ust_price"] = _composite_price(
        _source_paths()["ust_price_daily"], _source_paths()["ust_price_minute"], "ust_price", target
    )
    frame["luna_price"] = _composite_price(
        _source_paths()["luna_price_daily"], _source_paths()["luna_price_minute"], "luna_price", target
    )
    frame["ust_supply"] = ust_supply
    frame["luna_supply"] = luna_supply
    frame["anchor_total_deposits"] = anchor_deposits
    frame = frame.join(_anchor_flows(target)).join(_native_swap_flows(target)).join(_concentration(target))
    denominator = frame["ust_price"] * frame["ust_supply"]
    frame["backing_ratio"] = (frame["luna_price"] * frame["luna_supply"] / denominator).where(denominator > 0)
    frame = frame.reset_index()[CORE_COLUMNS]
    diagnostics = {
        "block_source_timestamp": block_source_time,
        "luna_holder_balance_sum": luna_holder_sum,
    }
    return frame, diagnostics


def build_native_swaps() -> pd.DataFrame:
    swaps = _read_parquet(_source_paths()["native_swaps"]).copy()
    swaps["timestamp"] = pd.to_datetime(swaps.pop("time"), utc=True)
    swaps["gross_luna_issuance"] = swaps["swap_amount"] + swaps["fee_amount"]
    swaps["source_file"] = str(_source_paths()["native_swaps"].relative_to(ROOT)).replace("\\", "/")
    swaps["raw_reference"] = f"doi:{DOI}"
    swaps["quality_class"] = "HISTORICAL_DIRECT"
    return swaps[
        [
            "timestamp",
            "offer_amount",
            "swap_amount",
            "fee_amount",
            "gross_luna_issuance",
            "source_file",
            "raw_reference",
            "quality_class",
        ]
    ].sort_values("timestamp", kind="stable")


def _asof_heights(timestamps: pd.Series) -> pd.Series:
    global_state = _read_parquet(_source_paths()["block_anchor_state"]).sort_index()
    right = pd.DataFrame(
        {
            "source_timestamp": _utc(global_state.index),
            "block_height": global_state["height"].to_numpy(),
        }
    ).sort_values("source_timestamp")
    left = pd.DataFrame({"timestamp": _utc(timestamps), "_order": np.arange(len(timestamps))})
    merged = pd.merge_asof(
        left.sort_values("timestamp"),
        right,
        left_on="timestamp",
        right_on="source_timestamp",
        direction="backward",
    ).sort_values("_order")
    return pd.Series(merged["block_height"].to_numpy(), index=timestamps.index, dtype="Int64")


def build_wallet_events() -> pd.DataFrame:
    events = _read_parquet(_source_paths()["anchor_events"]).copy()
    events["timestamp"] = pd.to_datetime(events.pop("time"), utc=True)
    events = events[
        (events["timestamp"] >= START) & (events["timestamp"] < END + timedelta(hours=1))
    ].copy()
    events["block_height"] = _asof_heights(events["timestamp"])
    events["wallet_id"] = events["sender"].map(
        lambda address: hashlib.sha256(f"terra-anchor:{address}".encode()).hexdigest()
    )
    events["event_type"] = events["action"].str.upper()
    events["amount_ust"] = events["ust_vol"]
    events["anchor_balance_before"] = np.nan
    events["anchor_balance_after"] = np.nan
    events["source_file"] = str(_source_paths()["anchor_events"].relative_to(ROOT)).replace("\\", "/")
    events["raw_reference"] = f"doi:{DOI}"
    events["quality_class"] = "PARTIAL_HISTORICAL"
    return events[
        [
            "timestamp",
            "block_height",
            "wallet_id",
            "event_type",
            "amount_ust",
            "anchor_balance_before",
            "anchor_balance_after",
            "source_file",
            "raw_reference",
            "quality_class",
        ]
    ].sort_values("timestamp", kind="stable")


def build_lfg_reserve_events() -> pd.DataFrame:
    labels = pd.read_csv(_source_paths()["anchor_labels"])
    lfg = set(labels.loc[labels["address_name"].str.contains("LFG", case=False, na=False), "address"])
    transfers = _read_parquet(_source_paths()["anchor_cashflow"])
    selected = transfers[transfers["sender"].isin(lfg) | transfers["recipient"].isin(lfg)].copy()
    selected["timestamp"] = pd.to_datetime(selected.pop("time"), utc=True)
    selected["block_height"] = _asof_heights(selected["timestamp"])
    selected["asset"] = selected["denom"].replace({"uusd": "UST", "uluna": "LUNA"})
    selected["direction"] = np.where(
        selected["sender"].isin(lfg), "OUTFLOW_FROM_LFG_TO_ANCHOR_RESERVE", "INFLOW_TO_LFG"
    )
    selected["reserve_balance_if_known"] = np.nan
    selected["intervention_volume_if_known"] = np.nan
    selected["tx_hash"] = pd.NA
    selected["source"] = str(_source_paths()["anchor_cashflow"].relative_to(ROOT)).replace("\\", "/")
    selected["quality_class"] = "PARTIAL_HISTORICAL"
    selected["notes"] = "Author-labelled LFG funding of Anchor yield reserve; not evidence of peg-defense execution."
    return selected[
        [
            "timestamp",
            "block_height",
            "asset",
            "amount",
            "direction",
            "reserve_balance_if_known",
            "intervention_volume_if_known",
            "tx_hash",
            "source",
            "quality_class",
            "notes",
        ]
    ].sort_values("timestamp", kind="stable")


def _frequency(index: pd.DatetimeIndex) -> str:
    clean = index.dropna().sort_values().unique()
    if len(clean) < 2:
        return "UNKNOWN"
    median_ns = int(np.median(np.diff(clean.asi8)))
    if median_ns <= 60_000_000_000:
        return "MINUTE_OR_EVENT"
    if median_ns <= 3_600_000_000_000:
        return "INTRADAY_OR_EVENT"
    if median_ns <= 86_400_000_000_000:
        return "DAILY"
    return f"IRREGULAR_MEDIAN_{pd.Timedelta(median_ns, unit='ns')}"


def _candidate_use(path: str) -> str:
    lowered = path.lower()
    rules = [
        ("native_swap", "native-swap event and issuance evidence"),
        ("anchor_run", "Anchor run events/state or depositor analysis"),
        ("anchor", "Anchor state, flow, concentration, or labels"),
        ("daily_balances", "daily UST/LUNA holder-balance reconstruction"),
        ("price", "historical market price"),
        ("curve", "secondary Ethereum Curve trade channel"),
        ("exchange", "centralized-exchange trade evidence"),
        ("label", "author-curated address/entity labels"),
        ("hazard", "published hazard-analysis derivative"),
        ("loss", "wallet loss/depositor derivative"),
        ("terra_pack", "prior ingestion/build implementation or documentation"),
        ("model", "existing model artifact; audit only"),
    ]
    return next((description for needle, description in rules if needle in lowered), "metadata/code/audit context")


def _provenance(path: str) -> str:
    lowered = path.lower()
    if "terra-luna-run-replication" in lowered:
        return f"Liu-Makarov-Schoar replication package; doi:{DOI}; see Datasets.md"
    if "terra_pack" in lowered or "terra_may2022_v1_pack" in lowered:
        return "Local prior Terra data-pack implementation"
    if "data/processed" in lowered:
        return "Existing repository processed artifact"
    return "Repository source/documentation"


def _read_profile(path: Path) -> tuple[int | None, list[str], str, str, str, str, str]:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        frame = pd.read_parquet(path)
    elif suffix == ".csv":
        try:
            frame = pd.read_csv(path)
        except (pd.errors.ParserError, UnicodeDecodeError):
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                return None, [], "N/A", "", "", "", "UNKNOWN"
            columns = next(csv.reader([lines[0]]), []) if lines else []
            return max(len(lines) - 1, 0), columns, "N/A", "", "", "", "UNKNOWN"
    elif suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None, [], "N/A", "", "", "", "UNKNOWN"
        if isinstance(payload, list):
            cols = list(payload[0].keys()) if payload and isinstance(payload[0], dict) else []
            return len(payload), [str(column) for column in cols], "N/A", "", "", "", "UNKNOWN"
        if isinstance(payload, dict):
            return 1, [str(column) for column in payload], "N/A", "", "", "", "UNKNOWN"
        return 1, [], "N/A", "", "", "", "UNKNOWN"
    else:
        row_count: int | None = None
        if suffix in {".md", ".py", ".ps1", ".txt", ".toml", ".r", ".tex"}:
            try:
                row_count = len(path.read_text(encoding="utf-8").splitlines())
            except UnicodeDecodeError:
                pass
        return row_count, [], "N/A", "", "", "", "N/A"

    timestamp_name = ""
    timestamp = pd.DatetimeIndex([])
    if isinstance(frame.index, pd.DatetimeIndex):
        timestamp_name = "__index__"
        timestamp = _utc(frame.index)
    else:
        for candidate in ("timestamp", "time_utc", "time", "minute", "hour", "date", "snapped_at"):
            if candidate not in frame.columns:
                continue
            parsed = _utc(frame[candidate])
            if parsed.notna().any():
                timestamp_name = candidate
                timestamp = parsed
                break
    start = timestamp.min().isoformat() if len(timestamp) and timestamp.notna().any() else ""
    end = timestamp.max().isoformat() if len(timestamp) and timestamp.notna().any() else ""
    frequency = _frequency(timestamp) if len(timestamp) else "UNKNOWN"
    return (
        len(frame),
        [str(column) for column in frame.columns],
        str(frame.index.dtype),
        timestamp_name,
        start,
        end,
        frequency,
    )


def _terra_repository_files() -> list[Path]:
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    selected: set[Path] = set()
    for item in tracked:
        normalized = item.replace("\\", "/")
        lowered = normalized.lower()
        if lowered.startswith("data/processed/terra_extended/") or lowered.startswith(
            "data/processed/terra_data_completion/"
        ):
            continue
        if (
            "terra" in lowered
            or lowered.startswith("data/raw/terra_may2022_v1/")
            or lowered.startswith("scripts/terra/")
            or lowered.startswith("sim/terra/")
        ):
            path = ROOT / normalized
            if path.is_file():
                selected.add(path)
    for path in RAW_ROOT.rglob("*"):
        if path.is_file():
            selected.add(path)
    return sorted(selected, key=lambda item: str(item.relative_to(ROOT)).lower())


def build_inventory() -> list[InventoryRow]:
    rows: list[InventoryRow] = []
    local_profiles: dict[str, tuple[int | None, list[str], str, str, str, str, str]] = {}
    for path in _terra_repository_files():
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        profile = _read_profile(path)
        local_profiles[relative] = profile
        count, columns, index_type, timestamp_column, start, end, frequency = profile
        rows.append(
            InventoryRow(
                file_path=relative,
                file_format=path.suffix.lower().lstrip(".") or "NO_EXTENSION",
                row_count=count,
                column_names=json.dumps(columns, ensure_ascii=False),
                index_type=index_type,
                timestamp_column=timestamp_column,
                start_timestamp=start,
                end_timestamp=end,
                estimated_frequency=frequency,
                file_size_bytes=path.stat().st_size,
                candidate_use=_candidate_use(relative),
                source_provenance=_provenance(relative),
            )
        )

    archive = RAW_ROOT / "terra-luna-run-replication.zip"
    if archive.exists():
        with zipfile.ZipFile(archive) as bundle:
            for member in sorted(bundle.infolist(), key=lambda item: item.filename.lower()):
                if member.is_dir():
                    continue
                virtual = f"zip://{archive.relative_to(ROOT).as_posix()}!/{member.filename}"
                extracted_suffix = member.filename.split("terra-luna-run-replication/", 1)[-1]
                extracted = f"data/raw/terra_may2022_v1/replication/terra-luna-run-replication/{extracted_suffix}"
                profile = local_profiles.get(extracted, (None, [], "N/A", "", "", "", "UNKNOWN"))
                count, columns, index_type, timestamp_column, start, end, frequency = profile
                rows.append(
                    InventoryRow(
                        file_path=virtual,
                        file_format=Path(member.filename).suffix.lower().lstrip(".") or "NO_EXTENSION",
                        row_count=count,
                        column_names=json.dumps(columns, ensure_ascii=False),
                        index_type=index_type,
                        timestamp_column=timestamp_column,
                        start_timestamp=start,
                        end_timestamp=end,
                        estimated_frequency=frequency,
                        file_size_bytes=member.file_size,
                        candidate_use=_candidate_use(member.filename),
                        source_provenance=f"ZIP member of Liu-Makarov-Schoar package; doi:{DOI}",
                    )
                )
    return rows


def source_lineage() -> list[dict[str, Any]]:
    base = "data/raw/terra_may2022_v1/replication/terra-luna-run-replication/"
    return [
        {
            "field": "block_height",
            "source_file": base + "data/anchor/Anchor_global_stats_fullnode.parquet",
            "source_columns": ["minute index", "height"],
            "source_code_reference": "Datasets.md §2",
            "raw_unit": "Terra block height",
            "final_unit": "integer block height",
            "transformation": "backward as-of at each UTC hour; no linear interpolation",
            "aggregation": "latest source record at or before timestamp",
            "quality": "HISTORICAL_DIRECT",
            "notes": "Source samples approximately every 15 minutes; carry during no-block intervals is state carry.",
        },
        {
            "field": "ust_price",
            "source_file": base + "data/external/ustc-usd-max.csv; data/prices/ust_price_may2022.parquet",
            "source_columns": ["snapped_at", "price", "time", "ust_price"],
            "source_code_reference": "Datasets.md §§external,35; figures/fig05_market_cap.py; figures/fig10_run_outflows.py",
            "raw_unit": "USD/UST",
            "final_unit": "USD/UST",
            "transformation": "CoinGecko daily point carried backward-as-of through April; Kaiko minute point as-of from May 1",
            "aggregation": "latest observation at or before each UTC hour",
            "quality": "HISTORICAL_STATE_CARRIED_FORWARD",
            "notes": "No interpolation and no future-day value is used.",
        },
        {
            "field": "luna_price",
            "source_file": base + "data/external/lunc-usd-max.csv; data/prices/luna_price_may2022.parquet",
            "source_columns": ["snapped_at", "price", "time", "luna_price"],
            "source_code_reference": "Datasets.md §§external,33; figures/fig05_market_cap.py; figures/fig12_death_spiral.py",
            "raw_unit": "USD/LUNA",
            "final_unit": "USD/LUNA",
            "transformation": "CoinGecko daily point carried backward-as-of through April; Kaiko minute point as-of from May 1",
            "aggregation": "latest observation at or before each UTC hour",
            "quality": "HISTORICAL_STATE_CARRIED_FORWARD",
            "notes": "No interpolation and no future-day value is used.",
        },
        {
            "field": "ust_supply",
            "source_file": base + "data/daily_balances/columbus-5-lunaust-supply-breakdown-fullnode.parquet",
            "source_columns": ["date", "denom", "balance", "address"],
            "source_code_reference": "Datasets.md §§16-17; figures/fig02_ust_supply_by_entity.py",
            "raw_unit": "normalized UST per address (not micro-UST)",
            "final_unit": "UST",
            "transformation": "filter denom=UST and sum per-address balances by date; no 1e6 rescaling",
            "aggregation": "daily state carried forward within its day",
            "quality": "HISTORICAL_STATE_CARRIED_FORWARD",
            "notes": "Figure code divides the summed token-unit value by 1e9 only for its billion-UST display axis.",
        },
        {
            "field": "luna_supply",
            "source_file": base + "data/native_swaps/luna_total_supply_run.parquet",
            "source_columns": ["time index", "luna_supply"],
            "source_code_reference": "Datasets.md §30; figures/fig12_death_spiral.py",
            "raw_unit": "LUNA",
            "final_unit": "LUNA",
            "transformation": "direct hourly series; no pre-May backfill",
            "aggregation": "none",
            "quality": "PARTIAL_HISTORICAL",
            "notes": "Coverage starts May 1. Daily holder-balance sums are not substituted because overlap is not identity.",
        },
        {
            "field": "anchor_total_deposits",
            "source_file": base
            + "data/anchor/Anchor_global_stats_fullnode.parquet; data/anchor_run/epoch_state_fig10.parquet",
            "source_columns": ["prev_aterra_supply", "prev_exchange_rate", "deposit_b_ust"],
            "source_code_reference": "Datasets.md §§2,13a; figures/fig10_run_outflows.py",
            "raw_unit": "micro-aUST × UST/aUST; billion UST in epoch derivative",
            "final_unit": "UST",
            "transformation": "prev_aterra_supply × prev_exchange_rate / 1e6 through May 6 00:00; deposit_b_ust × 1e9 thereafter",
            "aggregation": "backward as-of state",
            "quality": "HISTORICAL_DERIVED",
            "notes": "The live epoch-state series replaces stale cached prev_* fields during the run.",
        },
        {
            "field": "anchor_deposit_flow / anchor_withdrawal_flow",
            "source_file": base + "data/anchor_run/anchor_run_tx_cleaned.parquet",
            "source_columns": ["time", "action", "ust_vol"],
            "source_code_reference": "Datasets.md §10; figures/fig07_wallet_A_B.py",
            "raw_unit": "UST",
            "final_unit": "UST/hour",
            "transformation": "filter explicit deposit/withdraw actions and sum ust_vol",
            "aggregation": "event-to-UTC-hour sum",
            "quality": "PARTIAL_HISTORICAL",
            "notes": "EVENT_ZERO only May 6-13; earlier hours remain missing.",
        },
        {
            "field": "ust_native_redemption_volume",
            "source_file": base + "data/native_swaps/ust_luna_swaps_run.parquet",
            "source_columns": ["time", "offer_amount"],
            "source_code_reference": "Datasets.md §31; figures/fig11_swap_arbitrage.py",
            "raw_unit": "UST",
            "final_unit": "UST/hour",
            "transformation": "sum UST offered into the native market module",
            "aggregation": "event-to-UTC-hour sum",
            "quality": "PARTIAL_HISTORICAL",
            "notes": "2022 extract is UST-to-LUNA redemptions; no zeros before the documented May 7 run window.",
        },
        {
            "field": "gross_luna_issuance_from_native_swaps",
            "source_file": base + "data/native_swaps/ust_luna_swaps_run.parquet",
            "source_columns": ["time", "swap_amount", "fee_amount"],
            "source_code_reference": "Datasets.md §31; figures/fig11_swap_arbitrage.py",
            "raw_unit": "LUNA",
            "final_unit": "LUNA/hour",
            "transformation": "sum(swap_amount + fee_amount)",
            "aggregation": "event-to-UTC-hour sum",
            "quality": "HISTORICAL_DERIVED",
            "notes": "Direct event-output accounting; offer_amount / off-chain LUNA price is not used.",
        },
        {
            "field": "top10_anchor_share / top100_anchor_share",
            "source_file": base + "data/anchor/anchor_deposit_concentration.parquet",
            "source_columns": ["date index", "Top 10", "Top 100"],
            "source_code_reference": "Datasets.md §3; prep/prep_fig06_concentration.py; figures/fig06_anchor_concentration.py",
            "raw_unit": "percent of non-intermediary aUST balance",
            "final_unit": "fraction [0,1]",
            "transformation": "divide by 100",
            "aggregation": "daily state carried forward; stops after May 6",
            "quality": "HISTORICAL_STATE_CARRIED_FORWARD",
            "notes": "Denominator excludes author-labelled intermediaries.",
        },
        {
            "field": "backing_ratio",
            "source_file": "derived from luna_price, luna_supply, ust_price, ust_supply",
            "source_columns": ["luna_price", "luna_supply", "ust_price", "ust_supply"],
            "source_code_reference": "scripts/terra/complete_historical_data.py",
            "raw_unit": "USD / USD",
            "final_unit": "ratio",
            "transformation": "(luna_price × luna_supply) / (ust_price × ust_supply)",
            "aggregation": "hourly aligned inputs",
            "quality": "PARTIAL_HISTORICAL",
            "notes": "Risk indicator only; Terra was not literally collateralized one-for-one by LUNA.",
        },
        {
            "field": "anchor_wallet_events",
            "source_file": base + "data/anchor_run/anchor_run_tx_cleaned.parquet",
            "source_columns": ["time", "sender", "action", "ust_vol"],
            "source_code_reference": "Datasets.md §10; figures/fig07_wallet_A_B.py",
            "raw_unit": "wallet address, event type, UST",
            "final_unit": "SHA-256 wallet ID, event type, UST",
            "transformation": "deterministic address pseudonymization; backward-as-of block mapping",
            "aggregation": "event level; none",
            "quality": "PARTIAL_HISTORICAL",
            "notes": "All May 6-13 deposit/withdraw events retained; balances before/after remain missing.",
        },
        {
            "field": "terra_dex_liquidity / terra_dex_depth",
            "source_file": "none found",
            "source_columns": [],
            "source_code_reference": "repository-wide Terraswap/Astroport/pool/reserve search",
            "raw_unit": "N/A",
            "final_unit": "N/A",
            "transformation": "none",
            "aggregation": "none",
            "quality": "UNAVAILABLE",
            "notes": "The prior CoinGecko-volume construction is retained only as a LEGACY_PROXY description.",
        },
        {
            "field": "bridge_outflow / bridge_inflow",
            "source_file": "data/raw/terra_may2022_v1/evidence_map.json (invalid prior mapping)",
            "source_columns": ["epoch_state_fig10.deposit_b_ust"],
            "source_code_reference": "terra_pack_v6 build and repository duplicate audit",
            "raw_unit": "not a bridge-flow unit",
            "final_unit": "N/A",
            "transformation": "omitted",
            "aggregation": "none",
            "quality": "QUARANTINED",
            "notes": "Both directions were identical and came from Anchor state without an action filter.",
        },
        {
            "field": "lfg_reserve_events",
            "source_file": base
            + "data/anchor/anchor_cashflow_transfers.parquet; data/labels/anchor_contracts.csv",
            "source_columns": ["time", "sender", "recipient", "denom", "amount", "address_name"],
            "source_code_reference": "Datasets.md §§8,26; figures/fig03_anchor_cashflow.py",
            "raw_unit": "UST transfer event",
            "final_unit": "UST transfer event",
            "transformation": "filter author-labelled reserve funder (LFG)",
            "aggregation": "event level; none",
            "quality": "PARTIAL_HISTORICAL",
            "notes": "Three February Anchor yield-reserve funding events; not classified as peg defense.",
        },
    ]


def _anchor_validation() -> dict[str, Any]:
    paths = _source_paths()
    global_state = _read_parquet(paths["block_anchor_state"]).sort_index()
    reconstructed = (
        global_state["prev_aterra_supply"] * global_state["prev_exchange_rate"] / 1e6
    ).resample("D").first().rename("reconstructed")
    daily = _read_parquet(paths["anchor_daily"])["deposit balance"].rename("independent_daily")
    overlap = pd.concat([reconstructed, daily], axis=1).dropna()
    relative = (overlap["reconstructed"] - overlap["independent_daily"]).abs() / overlap[
        "independent_daily"
    ].abs()
    pre_run = overlap.loc["2022-03-01":"2022-05-05"]
    pre_relative = (pre_run["reconstructed"] - pre_run["independent_daily"]).abs() / pre_run[
        "independent_daily"
    ].abs()
    return {
        "formula": "prev_aterra_supply * prev_exchange_rate / 1e6",
        "overlap_rows": len(overlap),
        "mean_relative_error": float(relative.mean()),
        "median_relative_error": float(relative.median()),
        "max_relative_error": float(relative.max()),
        "correlation": float(overlap.corr().iloc[0, 1]),
        "pre_run_through_2022_05_05_overlap_rows": len(pre_run),
        "pre_run_mean_relative_error": float(pre_relative.mean()),
        "pre_run_median_relative_error": float(pre_relative.median()),
        "pre_run_max_relative_error": float(pre_relative.max()),
        "pre_run_correlation": float(pre_run.corr().iloc[0, 1]),
        "decision": "Use cached state before the run; use live epoch_state from May 6 because prev_* is stale during run.",
    }


def _supply_validation(frame: pd.DataFrame, diagnostics: dict[str, Any]) -> dict[str, Any]:
    indexed = frame.set_index("timestamp")
    holder = diagnostics["luna_holder_balance_sum"]
    direct_daily_end = indexed["luna_supply"].resample("D").last()
    holder_daily = holder.resample("D").last()
    overlap = pd.concat([holder_daily.rename("holder_sum"), direct_daily_end.rename("direct")], axis=1).dropna()
    relative = (overlap["holder_sum"] - overlap["direct"]).abs() / overlap["direct"].abs()

    balances = _read_parquet(_source_paths()["daily_balances"])
    balances["date"] = pd.to_datetime(balances["date"], utc=True)
    node_ust = balances[balances["denom"].eq("UST")].groupby("date")["balance"].sum().rename("node")
    market = pd.read_csv(_source_paths()["ust_price_daily"])
    market["date"] = pd.to_datetime(market["snapped_at"], utc=True)
    market["implied"] = market["market_cap"] / market["price"]
    ust_overlap = pd.concat([node_ust, market.set_index("date")["implied"]], axis=1).loc[START:END].dropna()
    ust_relative = (ust_overlap["node"] - ust_overlap["implied"]).abs() / ust_overlap["node"].abs()
    return {
        "luna_daily_holder_sum_vs_direct_total": {
            "overlap_rows": len(overlap),
            "mean_relative_error": float(relative.mean()),
            "median_relative_error": float(relative.median()),
            "max_relative_error": float(relative.max()),
            "correlation": float(overlap.corr().iloc[0, 1]),
            "decision": "Do not use holder-balance sum as total supply before May 1.",
        },
        "ust_node_supply_vs_coingecko_implied_supply": {
            "overlap_rows": len(ust_overlap),
            "mean_relative_error": float(ust_relative.mean()),
            "median_relative_error": float(ust_relative.median()),
            "max_relative_error": float(ust_relative.max()),
            "correlation": float(ust_overlap.corr().iloc[0, 1]),
            "decision": "Use node holder-balance sum; CoinGecko comparison is validation only.",
        },
    }


def _issuance_validation(frame: pd.DataFrame) -> dict[str, Any]:
    indexed = frame.set_index("timestamp")
    pairs = indexed[["gross_luna_issuance_from_native_swaps", "luna_supply"]].copy()
    pairs["supply_change"] = pairs["luna_supply"].diff()
    pairs = pairs.dropna()
    pairs = pairs[pairs["gross_luna_issuance_from_native_swaps"].notna()]
    discrepancy = pairs["gross_luna_issuance_from_native_swaps"] - pairs["supply_change"]
    largest = discrepancy.abs().nlargest(10)
    cumulative_issuance = float(pairs["gross_luna_issuance_from_native_swaps"].sum())
    cumulative_supply = float(pairs["supply_change"].sum())
    return {
        "formula": "gross LUNA issuance = swap_amount + fee_amount",
        "overlap_hours": len(pairs),
        "hourly_correlation": float(pairs["gross_luna_issuance_from_native_swaps"].corr(pairs["supply_change"])),
        "cumulative_issuance_luna": cumulative_issuance,
        "cumulative_supply_increase_luna": cumulative_supply,
        "final_cumulative_relative_error": abs(cumulative_issuance - cumulative_supply)
        / abs(cumulative_supply),
        "largest_absolute_discrepancy_hours": [
            {"timestamp": timestamp.isoformat(), "absolute_discrepancy_luna": float(value)}
            for timestamp, value in largest.items()
        ],
        "old_offchain_approximation_used": False,
    }


def _known_duplicate_audit() -> dict[str, Any]:
    old = pd.read_csv(ROOT / "data" / "processed" / "terra_may2022_v1.csv")
    named_pairs = [
        ("ust_dex_sell_volume", "luna_minted_from_redemption"),
        ("ust_dex_sell_volume", "luna_burned"),
        ("luna_minted_from_redemption", "luna_burned"),
        ("bridge_outflow_terra_to_ethereum", "bridge_inflow_ethereum_to_terra"),
        ("curve_ust_price", "ust_price"),
    ]
    results: list[dict[str, Any]] = []
    for left, right in named_pairs:
        pair = old[[left, right]].dropna()
        same = bool(np.allclose(pair[left], pair[right], rtol=1e-12, atol=1e-12)) if len(pair) else False
        results.append(
            {
                "left": left,
                "right": right,
                "overlap_rows": len(pair),
                "correlation": float(pair[left].corr(pair[right])) if len(pair) > 1 else None,
                "near_identical": same,
                "disposition": "QUARANTINED" if same else "REVIEWED_NOT_IDENTICAL",
            }
        )
    automatic = detect_duplicate_mappings(old.select_dtypes(include=[np.number]))
    return {
        "source": "data/processed/terra_may2022_v1.csv",
        "named_pair_results": results,
        "automatic_near_identical_pairs": automatic,
        "bridge_provenance_finding": (
            "Prior evidence_map mapped both bridge directions to epoch_state_fig10.deposit_b_ust without an action filter; "
            "both fields are quarantined and omitted from the extended core table."
        ),
    }


def _field_stats(frame: pd.DataFrame) -> dict[str, Any]:
    stats: dict[str, Any] = {}
    for column in frame.columns:
        if column == "timestamp":
            continue
        series = frame[column]
        valid = frame.loc[series.notna(), "timestamp"]
        stats[column] = {
            "first_valid_timestamp": valid.iloc[0].isoformat() if len(valid) else None,
            "last_valid_timestamp": valid.iloc[-1].isoformat() if len(valid) else None,
            "missing_count": int(series.isna().sum()),
            "valid_count": int(series.notna().sum()),
            "positive_count": int((pd.to_numeric(series, errors="coerce") > 0).sum()),
        }
    return stats


def temporal_report(frame: pd.DataFrame, diagnostics: dict[str, Any]) -> dict[str, Any]:
    timestamps = pd.DatetimeIndex(frame["timestamp"])
    global_state = _read_parquet(_source_paths()["block_anchor_state"])
    source_index = _utc(global_state.index).sort_values()
    gaps = pd.Series(source_index[1:] - source_index[:-1])
    expected = hourly_index()
    missing_rows = expected.difference(timestamps)
    block_source = diagnostics["block_source_timestamp"]
    no_future = bool((pd.to_datetime(block_source.dropna(), utc=True) <= block_source.dropna().index).all())
    return {
        "target_start": START.isoformat(),
        "target_end": END.isoformat(),
        "expected_hourly_rows": len(expected),
        "actual_rows": len(frame),
        "missing_hourly_rows": len(missing_rows),
        "missing_hourly_timestamps": [item.isoformat() for item in missing_rows],
        "duplicate_timestamp_count": int(frame["timestamp"].duplicated().sum()),
        "timestamps_monotonic": bool(frame["timestamp"].is_monotonic_increasing),
        "timezone": str(timestamps.tz),
        "longest_output_gap": str(timestamps.to_series().diff().max()),
        "block_height_coverage": {
            "min_height": int(frame["block_height"].min()),
            "max_height": int(frame["block_height"].max()),
            "missing_hourly_rows": int(frame["block_height"].isna().sum()),
            "largest_source_gap": str(gaps.max()),
            "halt_handling_rows": int((pd.Timestamp("2022-05-12T10:00:00Z") <= timestamps).sum()),
            "handling_note": "Backward state carry only; a constant height means no newer sampled block, not interpolation.",
            "no_future_source_timestamp": no_future,
        },
        "per_field": _field_stats(frame),
        "missing_policies": {
            "daily_prices": "STATE_FFILL until the next actual daily observation; no interpolation",
            "ust_supply": "STATE_FFILL of daily on-chain balance state",
            "luna_supply": "MISSING before direct hourly source begins",
            "anchor_total_deposits": "STATE_FFILL/backward-as-of protocol state",
            "anchor_flows": "MISSING outside May 6-13; EVENT_ZERO only inside coverage",
            "native_swaps": "MISSING before May 7; EVENT_ZERO inside documented run extract",
            "concentration": "STATE_FFILL through May 6; MISSING after source ends",
        },
    }


def _dictionary(frame: pd.DataFrame) -> list[dict[str, Any]]:
    stats = _field_stats(frame)
    specs: dict[str, tuple[str, str, str, str, str, str]] = {
        "timestamp": ("UTC hourly key", "UTC timestamp", "constructed target index", "inclusive hourly grid", "HOURLY", "HISTORICAL_DIRECT"),
        "block_height": ("Latest observed Terra block height", "block", "Anchor_global_stats_fullnode.height", "backward as-of", "~15-minute → hourly", "HISTORICAL_DIRECT"),
        "ust_price": ("UST market price", "USD/UST", "CoinGecko price; Kaiko ust_price", "backward as-of; Kaiko from May 1", "daily/minute → hourly", "HISTORICAL_STATE_CARRIED_FORWARD"),
        "luna_price": ("LUNA market price", "USD/LUNA", "CoinGecko price; Kaiko luna_price", "backward as-of; Kaiko from May 1", "daily/minute → hourly", "HISTORICAL_STATE_CARRIED_FORWARD"),
        "ust_supply": ("UST circulating holder-balance sum", "UST", "Columbus-5 denom,balance", "sum daily UST address balances", "daily → hourly", "HISTORICAL_STATE_CARRIED_FORWARD"),
        "luna_supply": ("Direct reconstructed LUNA total supply", "LUNA", "luna_total_supply_run.luna_supply", "none", "hourly", "PARTIAL_HISTORICAL"),
        "anchor_total_deposits": ("Anchor total deposit state", "UST", "prev_aterra_supply,prev_exchange_rate; deposit_b_ust", "cached formula then live epoch state", "~15-minute → hourly", "HISTORICAL_DERIVED"),
        "anchor_deposit_flow": ("Observed Anchor deposits", "UST/hour", "anchor_run_tx_cleaned action,ust_vol", "sum deposit events", "event → hourly", "PARTIAL_HISTORICAL"),
        "anchor_withdrawal_flow": ("Observed Anchor withdrawals", "UST/hour", "anchor_run_tx_cleaned action,ust_vol", "sum withdrawal events", "event → hourly", "PARTIAL_HISTORICAL"),
        "ust_native_redemption_volume": ("UST offered for LUNA in native swaps", "UST/hour", "ust_luna_swaps_run.offer_amount", "sum events", "event → hourly", "PARTIAL_HISTORICAL"),
        "gross_luna_issuance_from_native_swaps": ("Gross LUNA event output", "LUNA/hour", "swap_amount,fee_amount", "sum(swap_amount + fee_amount)", "event → hourly", "HISTORICAL_DERIVED"),
        "backing_ratio": ("LUNA market cap / UST supply value risk indicator", "ratio", "four aligned price/supply fields", "(LUNA price×supply)/(UST price×supply)", "hourly", "PARTIAL_HISTORICAL"),
        "top10_anchor_share": ("Top-10 non-intermediary Anchor share", "fraction", "anchor_deposit_concentration.Top 10", "divide percent by 100", "daily → hourly", "HISTORICAL_STATE_CARRIED_FORWARD"),
        "top100_anchor_share": ("Top-100 non-intermediary Anchor share", "fraction", "anchor_deposit_concentration.Top 100", "divide percent by 100", "daily → hourly", "HISTORICAL_STATE_CARRIED_FORWARD"),
    }
    missing = {
        "timestamp": "NONE",
        "block_height": "STATE_FFILL/backward as-of",
        "ust_price": "STATE_FFILL; no interpolation",
        "luna_price": "STATE_FFILL; no interpolation",
        "ust_supply": "STATE_FFILL of daily state",
        "luna_supply": "MISSING before May 1",
        "anchor_total_deposits": "STATE_FFILL/backward as-of",
        "anchor_deposit_flow": "MISSING outside coverage; EVENT_ZERO inside",
        "anchor_withdrawal_flow": "MISSING outside coverage; EVENT_ZERO inside",
        "ust_native_redemption_volume": "MISSING outside coverage; EVENT_ZERO inside",
        "gross_luna_issuance_from_native_swaps": "MISSING outside coverage; EVENT_ZERO inside",
        "backing_ratio": "MISSING if any required input is missing",
        "top10_anchor_share": "STATE_FFILL through May 6; then MISSING",
        "top100_anchor_share": "STATE_FFILL through May 6; then MISSING",
    }
    notes = {
        "backing_ratio": "Risk indicator only; not a claim of one-for-one collateralization.",
        "luna_supply": "Daily holder-balance sums were rejected as a pre-May total-supply substitute.",
        "anchor_total_deposits": "Live epoch state replaces stale cached fields during the run.",
    }
    rows: list[dict[str, Any]] = []
    for field in CORE_COLUMNS:
        description, unit, source, transformation, frequency, quality = specs[field]
        field_stats = stats.get(field, {})
        rows.append(
            {
                "field": field,
                "description": description,
                "final_unit": unit,
                "source": source,
                "source_column": source,
                "transformation": transformation,
                "frequency": frequency,
                "coverage_start": field_stats.get("first_valid_timestamp", START.isoformat() if field == "timestamp" else None),
                "coverage_end": field_stats.get("last_valid_timestamp", END.isoformat() if field == "timestamp" else None),
                "quality_class": quality,
                "missing_policy": missing[field],
                "notes": notes.get(field, ""),
            }
        )
    return rows


def _early_warning_readiness(frame: pd.DataFrame) -> list[dict[str, Any]]:
    first = _field_stats(frame)
    return [
        {"feature": "UST depeg", "status": "AVAILABLE", "first_without_lookahead": first["ust_price"]["first_valid_timestamp"], "basis": "1 - ust_price"},
        {"feature": "depeg persistence", "status": "AVAILABLE", "first_without_lookahead": (START + timedelta(hours=1)).isoformat(), "basis": "lagged UST price"},
        {"feature": "Anchor outflow stress", "status": "PARTIAL", "first_without_lookahead": first["anchor_withdrawal_flow"]["first_valid_timestamp"], "basis": "explicit withdrawal events only from May 6"},
        {"feature": "Anchor outflow acceleration", "status": "PARTIAL", "first_without_lookahead": (pd.Timestamp(first["anchor_withdrawal_flow"]["first_valid_timestamp"]) + timedelta(hours=1)).isoformat(), "basis": "lagged explicit withdrawals"},
        {"feature": "native redemption stress", "status": "PARTIAL", "first_without_lookahead": first["ust_native_redemption_volume"]["first_valid_timestamp"], "basis": "native UST→LUNA events from May 7"},
        {"feature": "LUNA return 1h", "status": "AVAILABLE", "first_without_lookahead": (START + timedelta(hours=1)).isoformat(), "basis": "lagged market price"},
        {"feature": "LUNA return 6h", "status": "AVAILABLE", "first_without_lookahead": (START + timedelta(hours=6)).isoformat(), "basis": "lagged market price"},
        {"feature": "LUNA return 24h", "status": "AVAILABLE", "first_without_lookahead": (START + timedelta(hours=24)).isoformat(), "basis": "lagged market price"},
        {"feature": "LUNA volatility", "status": "AVAILABLE", "first_without_lookahead": (START + timedelta(hours=24)).isoformat(), "basis": "trailing returns only"},
        {"feature": "backing ratio", "status": "PARTIAL", "first_without_lookahead": first["backing_ratio"]["first_valid_timestamp"], "basis": "direct LUNA supply starts May 1"},
        {"feature": "backing deterioration", "status": "PARTIAL", "first_without_lookahead": (pd.Timestamp(first["backing_ratio"]["first_valid_timestamp"]) + timedelta(hours=1)).isoformat(), "basis": "lagged backing ratio"},
        {"feature": "DEX liquidity stress", "status": "UNAVAILABLE", "first_without_lookahead": None, "basis": "no Terra pool reserve/depth history"},
        {"feature": "large-holder concentration", "status": "PARTIAL", "first_without_lookahead": first["top10_anchor_share"]["first_valid_timestamp"], "basis": "daily series ends May 6"},
        {"feature": "reserve-defense activity", "status": "UNAVAILABLE", "first_without_lookahead": None, "basis": "LFG Anchor funding is not peg-defense execution"},
    ]


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def _write_inventory(rows: list[InventoryRow]) -> None:
    payload = [asdict(row) for row in rows]
    _write_json(COMPLETION_DIR / "raw_inventory.json", payload)
    pd.DataFrame(payload).to_csv(COMPLETION_DIR / "raw_inventory.csv", index=False, lineterminator="\n")
    formats = pd.Series([row.file_format for row in rows]).value_counts().sort_index()
    markdown = [
        "# Terra raw/source inventory",
        "",
        f"Inventory entries: **{len(rows)}** (including ZIP members as `zip://` virtual paths).",
        "",
        "Raw files and the original ZIP were read only. Generated completion outputs are deliberately excluded so reruns remain stable.",
        "",
        "## Formats",
        "",
        "| Format | Files |",
        "|---|---:|",
    ]
    markdown.extend(f"| {fmt} | {count} |" for fmt, count in formats.items())
    markdown.extend(
        [
            "",
            "## Inventory",
            "",
            "| Path | Format | Rows | Time field | Start | End | Candidate use |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for row in rows:
        markdown.append(
            f"| `{row.file_path}` | {row.file_format} | {row.row_count if row.row_count is not None else ''} | "
            f"{row.timestamp_column} | {row.start_timestamp} | {row.end_timestamp} | {row.candidate_use} |"
        )
    (COMPLETION_DIR / "raw_inventory.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")


def _write_dictionary(rows: list[dict[str, Any]]) -> None:
    pd.DataFrame(rows).to_csv(EXTENDED_DIR / "data_dictionary.csv", index=False, lineterminator="\n")
    headers = list(rows[0])
    lines = ["# Terra extended data dictionary", "", "| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        values = [str(row.get(header, "") or "").replace("|", "\\|").replace("\n", " ") for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    (EXTENDED_DIR / "data_dictionary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_report(
    frame: pd.DataFrame,
    issuance: dict[str, Any],
    supply: dict[str, Any],
    anchor: dict[str, Any],
    duplicate: dict[str, Any],
    readiness: list[dict[str, Any]],
) -> None:
    stats = _field_stats(frame)
    table = [
        ("UST price", "READY WITH LIMITATIONS", f"{START.date()}–{END.date()}", "CoinGecko daily + Kaiko minute", "Fit + warning"),
        ("LUNA price", "READY WITH LIMITATIONS", f"{START.date()}–{END.date()}", "CoinGecko daily + Kaiko minute", "Fit + warning"),
        ("UST supply", "READY WITH LIMITATIONS", f"{START.date()}–{END.date()}", "Columbus-5 daily address balances", "Fit + warning"),
        ("LUNA total supply", "READY WITH LIMITATIONS", "2022-05-01–2022-05-13", "native-swap total-supply reconstruction", "Fit + mechanism"),
        ("Anchor deposits", "READY WITH LIMITATIONS", f"{START.date()}–{END.date()}", "Anchor contract state + live epoch state", "Fit + warning"),
        ("Anchor deposit/withdraw events", "READY WITH LIMITATIONS", "2022-05-06–2022-05-13", "archive-node event extract", "Warning + wallet analysis"),
        ("Native UST→LUNA swaps", "READY", "2022-05-07–2022-05-13", "market-module swap events", "Mechanism"),
        ("Anchor holder concentration", "READY WITH LIMITATIONS", "2022-03-01–2022-05-06", "aUST balance concentration", "Warning"),
        ("Anchor wallet events", "READY WITH LIMITATIONS", "2022-05-06–2022-05-13", "hashed archive-node events", "ABM evidence"),
        ("Terra DEX reserves/depth", "MISSING / UNAVAILABLE", "none", "no pool-state source found", "Stress only"),
        ("Legacy DEX proxy", "PROXY ONLY", "prior May dataset", "CoinGecko total_volume / 24", "Explicit opt-in only"),
        ("LFG reserve funding", "READY WITH LIMITATIONS", "3 events in Feb 2022", "author-labelled Anchor cash-flow address", "Context only"),
        ("LFG peg defense", "MISSING / UNAVAILABLE", "none", "no identified intervention ledger", "Defense unavailable"),
        ("Curve", "OPTIONAL / PARTIAL", "2022-05-07", "Ethereum Curve trade extract", "Secondary channel"),
        ("Bridge flows", "QUARANTINED", "prior May dataset", "invalid identical mapping", "Do not use"),
    ]
    lines = [
        "# Terra historical data-completion report",
        "",
        f"Dataset: `{DATASET_VERSION}`  ",
        f"Window: `{START.isoformat()}` through `{END.isoformat()}`  ",
        f"Rows: **{len(frame)}**",
        "",
        "## Summary",
        "",
        "| Data channel | Status | Coverage | Source | Use |",
        "|---|---|---|---|---|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in table)
    lines.extend(
        [
            "",
            "## A. READY",
            "",
            "- The hourly UTC grid, block heights, May native-swap events, and direct event-output issuance accounting are usable.",
            "- Native swap events are preserved separately; gross issuance is `swap_amount + fee_amount`.",
            "",
            "## B. READY WITH LIMITATIONS",
            "",
            "- March–April prices are real CoinGecko daily observations carried forward within the day; May uses Kaiko minute observations.",
            "- UST supply is a daily on-chain address-balance sum carried forward, not an hourly observation.",
            "- Direct LUNA total supply starts May 1; earlier core rows remain missing.",
            "- Anchor events start May 6 and native redemptions start May 7; unknown earlier hours are missing, never zero.",
            "- Concentration ends May 6 and is not extrapolated through the collapse.",
            "",
            "## C. PROXY ONLY",
            "",
            "- Prior `terra_dex_liquidity` and `terra_dex_depth` are `LEGACY_EXECUTION_CAPACITY_PROXY`: median and lower-quartile CoinGecko UST 24h market-wide volume divided by 24, held fixed. They are omitted from the new core table.",
            "- Future model code must explicitly opt in; these values are neither Terraswap/Astroport reserves nor executable depth.",
            "",
            "## D. MISSING / UNAVAILABLE",
            "",
            "- **Terra DEX liquidity/depth:** package data, scripts, transaction extracts, prior builders, Terraswap/Astroport/pool/reserve keywords were searched. No historical pool reserve/state snapshots exist. This does not block price/Anchor Historical Fit; it limits liquidity Early Warning and parameterized Stress Testing.",
            "- **LFG peg-defense execution:** LFG-labelled Anchor reserve funding exists, but no BTC reserve ledger or identified peg-defense executions exist. This does not block core Historical Fit; reserve-defense Early Warning is unavailable and reserve Stress Tests remain scenario-based.",
            "- **Pre-May direct LUNA total supply:** the daily holder-balance table is not accounting-identical to direct total supply and is not substituted. This makes backing ratio partial from May 1.",
            "- **Bridge flows:** prior directions were both mapped from the same Anchor deposit-state column without action filters. They are quarantined. Bridge is optional for current Historical Fit and Early Warning.",
            "",
            "## Validation",
            "",
            f"- Native issuance hourly correlation: **{issuance['hourly_correlation']:.9f}** over {issuance['overlap_hours']} hours.",
            f"- Native cumulative issuance: **{issuance['cumulative_issuance_luna']:.6f} LUNA**; supply increase: **{issuance['cumulative_supply_increase_luna']:.6f} LUNA**; relative error: **{issuance['final_cumulative_relative_error']:.6%}**.",
            f"- Anchor cached-state validation: {anchor['overlap_rows']} overlap days; mean/median/max relative error **{anchor['mean_relative_error']:.6%} / {anchor['median_relative_error']:.6%} / {anchor['max_relative_error']:.6%}**; correlation **{anchor['correlation']:.9f}**.",
            f"- Pre-run Anchor validation through May 5: mean/median/max **{anchor['pre_run_mean_relative_error']:.6%} / {anchor['pre_run_median_relative_error']:.6%} / {anchor['pre_run_max_relative_error']:.6%}**; correlation **{anchor['pre_run_correlation']:.9f}**. Live epoch state is used during the run.",
            f"- UST node supply vs CoinGecko-implied supply: median relative error **{supply['ust_node_supply_vs_coingecko_implied_supply']['median_relative_error']:.6%}** over {supply['ust_node_supply_vs_coingecko_implied_supply']['overlap_rows']} days.",
            f"- LUNA holder-balance sum vs direct total supply: median relative error **{supply['luna_daily_holder_sum_vs_direct_total']['median_relative_error']:.6%}**; it is not used as total supply.",
            f"- Duplicate audit found {len(duplicate['automatic_near_identical_pairs'])} near-identical numeric pairs in the legacy May dataset; suspect mappings are quarantined rather than copied.",
            "",
            "## Core-field availability",
            "",
            "| Field | First valid | Last valid | Missing | Positive |",
            "|---|---|---|---:|---:|",
        ]
    )
    for field, values in stats.items():
        lines.append(
            f"| {field} | {values['first_valid_timestamp'] or ''} | {values['last_valid_timestamp'] or ''} | "
            f"{values['missing_count']} | {values['positive_count']} |"
        )
    lines.extend(
        [
            "",
            "## Early-warning readiness",
            "",
            "| Feature | Status | First calculable without look-ahead | Basis |",
            "|---|---|---|---|",
        ]
    )
    for item in readiness:
        lines.append(
            f"| {item['feature']} | {item['status']} | {item['first_without_lookahead'] or ''} | {item['basis']} |"
        )
    lines.extend(
        [
            "",
            "## Scientific interpretation",
            "",
            "The `backing_ratio` is only a risk indicator: LUNA market capitalization divided by UST supply value. It must not be described as literal one-for-one collateralization.",
            "",
            "The data layer is defensible for core price, supply (with explicit LUNA coverage limits), Anchor state, partial flow, and mechanism analyses. It is not complete for Terra-native DEX liquidity, bridge flows, or LFG peg-defense behavior; later model work must keep those channels optional or explicitly proxy/scenario based.",
        ]
    )
    (EXTENDED_DIR / "data_completion_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _manifest(
    frame: pd.DataFrame,
    native: pd.DataFrame,
    wallets: pd.DataFrame,
    lfg: pd.DataFrame,
    issuance: dict[str, Any],
    anchor: dict[str, Any],
    supply: dict[str, Any],
    duplicate: dict[str, Any],
    readiness: list[dict[str, Any]],
) -> dict[str, Any]:
    source_files = []
    raw_units = {
        "block_anchor_state": "contract-native numeric fields; aTerra supply in micro-aUST",
        "anchor_daily": "UST, rates, ratios",
        "anchor_concentration": "percent",
        "anchor_events": "aUST and UST token units",
        "anchor_epoch": "micro-aUST, exchange ratio, billion UST derivative",
        "anchor_cashflow": "normalized token amount",
        "anchor_labels": "address labels",
        "daily_balances": "normalized UST/LUNA token units per address",
        "luna_supply": "LUNA",
        "native_swaps": "UST offer and LUNA output/fee",
        "ust_price_daily": "USD/UST and USD market values",
        "luna_price_daily": "USD/LUNA and USD market values",
        "ust_price_minute": "USD/UST",
        "luna_price_minute": "USD/LUNA",
        "curve": "Ethereum Curve trade units",
    }
    for name, path in _source_paths().items():
        count, _columns, _index, timestamp_column, start, end, _frequency_value = _read_profile(path)
        source_files.append(
            {
                "role": name,
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
                "row_count": count,
                "timestamp_column": timestamp_column,
                "source_start": start or None,
                "source_end": end or None,
                "raw_units": raw_units[name],
            }
        )
    output_hashes = {}
    for path in sorted(EXTENDED_DIR.glob("*.parquet")) + sorted(EXTENDED_DIR.glob("*.csv")):
        output_hashes[path.name] = sha256_file(path)
    return {
        "dataset_version": DATASET_VERSION,
        "git_commit": git_commit(),
        "git_commit_meaning": "source-code commit used to build this artifact bundle",
        "replication_package": {
            "title": "Anatomy of a Run: The Terra Luna Crash replication package",
            "doi": DOI,
            "version": "UNKNOWN (the local README and Datasets.md do not state a release version)",
            "locally_recorded_raw_reference": f"doi:{DOI}",
            "local_readme": str((REPLICATION_ROOT / "README.md").relative_to(ROOT)).replace("\\", "/"),
        },
        "target_window": {"start": START.isoformat(), "end": END.isoformat(), "rows": len(frame)},
        "source_files": source_files,
        "outputs": {
            "terra_state_hourly": {"rows": len(frame), "columns": list(frame.columns)},
            "terra_native_swaps": {"rows": len(native), "columns": list(native.columns)},
            "anchor_wallet_events": {"rows": len(wallets), "addresses_pseudonymized": True},
            "lfg_reserve_events": {
                "rows": len(lfg),
                "scope": "Anchor yield-reserve funding only; not peg-defense executions",
            },
            "terra_dex_hourly": {"quality_class": "UNAVAILABLE", "created": False},
            "hashes": output_hashes,
        },
        "quality_classes": sorted(QUALITY_CLASSES),
        "transformations": source_lineage(),
        "missing_data_rules": temporal_report(frame, {"block_source_timestamp": source_timestamp_asof(_read_parquet(_source_paths()["block_anchor_state"]).index, hourly_index())})["missing_policies"],
        "validation": {
            "native_issuance": issuance,
            "anchor_deposits": anchor,
            "supply": supply,
            "duplicate_identity_audit": duplicate,
        },
        "early_warning_readiness": readiness,
        "known_limitations": [
            "Direct LUNA total supply starts 2022-05-01.",
            "March-April prices are daily market observations carried forward within day.",
            "Anchor event flows start 2022-05-06; native swap flows start 2022-05-07.",
            "No actual Terra DEX reserve/depth history was found.",
            "No LFG peg-defense execution ledger was found.",
            "Bridge fields from the prior dataset are quarantined.",
        ],
    }


def build_all() -> None:
    COMPLETION_DIR.mkdir(parents=True, exist_ok=True)
    EXTENDED_DIR.mkdir(parents=True, exist_ok=True)

    inventory = build_inventory()
    _write_inventory(inventory)
    _write_json(COMPLETION_DIR / "source_lineage.json", source_lineage())

    frame, diagnostics = build_hourly_state()
    native = build_native_swaps()
    wallets = build_wallet_events()
    lfg = build_lfg_reserve_events()

    frame.to_parquet(EXTENDED_DIR / "terra_state_hourly_20220301_20220513.parquet", index=False)
    frame.to_csv(EXTENDED_DIR / "terra_state_hourly_20220301_20220513.csv", index=False, lineterminator="\n")
    native.to_parquet(EXTENDED_DIR / "terra_native_swaps.parquet", index=False)
    wallets.to_parquet(EXTENDED_DIR / "anchor_wallet_events.parquet", index=False)
    lfg.to_parquet(EXTENDED_DIR / "lfg_reserve_events.parquet", index=False)

    temporal = temporal_report(frame, diagnostics)
    issuance = _issuance_validation(frame)
    anchor = _anchor_validation()
    supply = _supply_validation(frame, diagnostics)
    duplicate = _known_duplicate_audit()
    readiness = _early_warning_readiness(frame)
    temporal["anchor_deposit_validation"] = anchor
    temporal["supply_validation"] = supply
    temporal["native_issuance_validation"] = issuance
    temporal["duplicate_identity_audit"] = duplicate
    _write_json(COMPLETION_DIR / "temporal_quality_report.json", temporal)
    _write_json(COMPLETION_DIR / "block_height_coverage.json", temporal["block_height_coverage"])

    dictionary = _dictionary(frame)
    _write_dictionary(dictionary)
    _write_report(frame, issuance, supply, anchor, duplicate, readiness)
    manifest = _manifest(frame, native, wallets, lfg, issuance, anchor, supply, duplicate, readiness)
    _write_json(EXTENDED_DIR / "provenance_manifest.json", manifest)

    print(f"Built {DATASET_VERSION}: {len(frame)} hourly rows")
    print(f"Native swaps: {len(native)} events")
    print(f"Anchor wallet events: {len(wallets)} events (wallet IDs hashed)")
    print(f"LFG Anchor reserve-funding events: {len(lfg)}")
    print("Terra DEX hourly: UNAVAILABLE (no file created)")


if __name__ == "__main__":
    build_all()
