from __future__ import annotations

import csv
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from scripts.terra.run_demo_pipeline import run_demo_pipeline
from sim.network import GRAPH_MODEL_VERSION
from sim.research.aave_suite import (
    AAVE_RESEARCH_VERSION,
    CANONICAL_SNAPSHOT,
    load_canonical_snapshot,
    run_aave_research_suite,
    sha256_file,
    snapshot_quality,
)
from sim.research.rq_completion import RQ_COMPLETION_VERSION
from sim.terra.demo_data import EXTENDED_DATASET, NATIVE_SWAPS, dataset_summary, load_extended_frame
from sim.terra.research_pipeline import (
    DEFAULT_DATASET,
    DEFAULT_NATIVE_SWAPS,
    DEFAULT_STRICT_V2,
    FINAL_PIPELINE_VERSION,
    run_final_pipeline,
)

FINAL_RESEARCH_VERSION = "defistress-final-research-orchestrator-1.1.0"
DEFAULT_OUTPUT = Path("data/processed/research_final")
DEFAULT_DOCS = Path("docs/research_final")
REPRODUCE_COMMAND = r".\.venv\Scripts\python.exe scripts\run_full_research_pipeline.py --research"
ADDRESS_RE = re.compile(r"0x[a-fA-F0-9]{40}")
SECRET_MARKERS = ("GRAPH_API_KEY=", "ETH_RPC_URL=", "Authorization: Bearer", "ALCHEMY_API_KEY=")
PREVIOUS_RESEARCH_PACKAGE_COMMIT = "df8df8d24eb257262a8514d233bb59677d162380"
EVIDENCE_REQUIRED_STATUSES = {
    "SUPPORTED",
    "PARTIALLY_SUPPORTED",
    "MODEL_CONDITIONAL",
    "SUPPORTED_WITH_BOUNDARY",
    "SUPPORTED_BOUNDARY",
    "SUPPORTED_NEGATIVE_FINDING",
}


def now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        return "UNAVAILABLE"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def finite(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"non-finite research value: {value}")
    return result


def output_hashes(root: Path, *, exclude: set[str] | None = None) -> dict[str, str]:
    skipped = exclude or set()
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.relative_to(root).as_posix() not in skipped
    }


REGRESSION_CORE_FILES = (
    "terra/demo/early_warning_timeline.json",
    "terra/demo/historical_fit.json",
    "terra/demo/mechanism_check.json",
    "terra/demo/stress_test.json",
    "terra/audit/final_metrics.json",
    "terra/audit/monte_carlo.json",
    "terra/audit/strict_oos_v2.json",
    "aave/deterministic_scenarios.json",
    "aave/sensitivity.json",
    "aave/shock_liquidity_grid.json",
    "aave/monte_carlo.json",
    "network/structural_graph.json",
    "network/professor_demo_graph.json",
    "network/severe_graph.json",
)


def _numeric_leaves(value: Any, path: str = "") -> dict[str, float | int]:
    leaves: dict[str, float | int] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}" if path else str(key)
            leaves.update(_numeric_leaves(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            leaves.update(_numeric_leaves(item, f"{path}[{index}]"))
    elif isinstance(value, bool):
        return leaves
    elif isinstance(value, (int, float)):
        finite(value)
        leaves[path] = value
    return leaves


def capture_regression_baseline(output_dir: Path) -> dict[str, dict[str, float | int]]:
    baseline: dict[str, dict[str, float | int]] = {}
    if not output_dir.exists():
        return baseline
    for relative in REGRESSION_CORE_FILES:
        path = output_dir / relative
        if path.exists():
            baseline[relative] = _numeric_leaves(read_json(path))
    return baseline


def compare_regression_baseline(
    baseline: dict[str, dict[str, float | int]], output_dir: Path
) -> dict[str, Any]:
    if not baseline:
        return {
            "previous_research_package_commit": PREVIOUS_RESEARCH_PACKAGE_COMMIT,
            "comparison_policy": "No previous package was present in this output directory.",
            "status": "SKIPPED_NO_BASELINE",
            "all_passed": True,
            "files": [],
        }
    files: list[dict[str, Any]] = []
    all_passed = bool(baseline)
    for relative, old_values in baseline.items():
        path = output_dir / relative
        new_values = _numeric_leaves(read_json(path)) if path.exists() else {}
        changed = [
            key
            for key, old_value in old_values.items()
            if key not in new_values or new_values[key] != old_value
        ]
        status = "PASS" if not changed else "FAIL"
        all_passed = all_passed and status == "PASS"
        files.append(
            {
                "artifact": relative,
                "status": status,
                "old_numeric_leaves": len(old_values),
                "compared_numeric_leaves": len(old_values) - len(changed),
                "changed_paths": changed[:50],
            }
        )
    return {
        "previous_research_package_commit": PREVIOUS_RESEARCH_PACKAGE_COMMIT,
        "comparison_policy": (
            "Every numeric leaf present in the previous core artifact must remain exactly equal; additive fields "
            "in the new artifacts are permitted."
        ),
        "all_passed": all_passed,
        "status": "PASS" if all_passed else "FAIL",
        "files": files,
    }


def _package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "UNAVAILABLE"


def run_command(command: list[str], cwd: Path | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
        return {
            "command": subprocess.list2cmdline(command),
            "status": "PASS" if completed.returncode == 0 else "FAIL",
            "return_code": completed.returncode,
            "runtime_seconds": time.perf_counter() - started,
            "stdout_tail": completed.stdout[-6000:],
            "stderr_tail": completed.stderr[-6000:],
        }
    except OSError as exc:
        return {
            "command": subprocess.list2cmdline(command),
            "status": "UNAVAILABLE",
            "return_code": None,
            "runtime_seconds": time.perf_counter() - started,
            "error": str(exc),
        }


def run_preflight(*, skip_tests: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    if skip_tests:
        checks.append({"name": "automated checks", "status": "SKIPPED_BY_FLAG"})
    else:
        commands = [
            ("pytest", [sys.executable, "-m", "pytest"]),
            ("ruff", [sys.executable, "-m", "ruff", "check", "."]),
            ("mypy", [sys.executable, "-m", "mypy"]),
            ("vitest", ["pnpm.cmd", "test", "--", "--run"]),
            ("eslint", ["pnpm.cmd", "lint"]),
            ("next_build", ["pnpm.cmd", "build"]),
        ]
        next_env = Path("frontend/next-env.d.ts")
        original_next_env = next_env.read_bytes() if next_env.exists() else None
        for name, command in commands:
            result = run_command(command, Path("frontend") if name in {"vitest", "eslint", "next_build"} else None)
            result["name"] = name
            checks.append(result)
        if original_next_env is not None and next_env.exists() and next_env.read_bytes() != original_next_env:
            next_env.write_bytes(original_next_env)
    node_version = run_command(["node", "--version"])
    return {
        "generated_at": now_iso(),
        "source_code_commit": git("rev-parse", "HEAD"),
        "python": sys.version,
        "platform": platform.platform(),
        "node": node_version.get("stdout_tail", "").strip() or "UNAVAILABLE",
        "packages": {
            name: _package_version(name)
            for name in ("numpy", "pandas", "matplotlib", "networkx", "pytest", "ruff", "mypy")
        },
        "checks": checks,
        "all_required_passed": bool(checks) and all(row["status"] in {"PASS", "SKIPPED_BY_FLAG"} for row in checks),
    }


def validate_inputs() -> tuple[dict[str, Any], dict[str, Any], set[str]]:
    frame = load_extended_frame()
    if len(frame) != 1776:
        raise ValueError(f"canonical Terra frame has {len(frame)} rows instead of 1776")
    swaps = pd.read_parquet(NATIVE_SWAPS)
    required_swaps = {"timestamp", "offer_amount", "swap_amount", "fee_amount"}
    if len(swaps) != 277342 or not required_swaps.issubset(swaps.columns):
        raise ValueError("canonical processed Terra native-swap evidence changed")
    snapshot = load_canonical_snapshot()
    aave = snapshot_quality(snapshot)
    terra = dataset_summary()
    terra["frequency"] = "hourly"
    terra["missingness"] = {
        column: {"missing_rows": int(frame[column].isna().sum()), "missing_share": float(frame[column].isna().mean())}
        for column in frame.columns
    }
    terra["native_swaps"] = {
        "path": NATIVE_SWAPS.as_posix(),
        "rows": len(swaps),
        "columns": sorted(required_swaps),
        "sha256": sha256_file(NATIVE_SWAPS),
    }
    borrower_addresses = {
        str(row.get("provenance", {}).get("raw_address", "")).lower()
        for row in snapshot["borrowers"]
        if row.get("provenance", {}).get("raw_address")
    }
    return terra, aave, borrower_addresses


def _clean_output(output_dir: Path, docs_dir: Path) -> None:
    default_output = DEFAULT_OUTPUT.resolve()
    default_docs = DEFAULT_DOCS.resolve()
    for target, expected in ((output_dir, default_output), (docs_dir, default_docs)):
        if target.exists():
            if target.resolve() != expected and not (target / ".defistress_research_output").exists():
                raise ValueError(f"refusing to replace unmarked custom output directory: {target}")
            shutil.rmtree(target.resolve())
        target.mkdir(parents=True)
        (target / ".defistress_research_output").write_text(FINAL_RESEARCH_VERSION + "\n", encoding="utf-8")


class Registry:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(
        self,
        result_id: str,
        case: str,
        metric: str,
        value: Any,
        unit: str,
        artifact: str,
        interpretation: str,
        boundary: str,
        status: str = "SUPPORTED",
    ) -> None:
        if isinstance(value, (int, float)):
            finite(value)
        self.rows.append(
            {
                "result_id": result_id,
                "case": case,
                "metric": metric,
                "value": value,
                "unit": unit,
                "artifact": artifact,
                "status": status,
                "interpretation": interpretation,
                "claim_boundary": boundary,
            }
        )

    def values(self) -> dict[str, Any]:
        return {row["result_id"]: row["value"] for row in self.rows}


def build_registry(output_dir: Path, terra_quality: dict[str, Any], aave_quality: dict[str, Any]) -> Registry:
    registry = Registry()
    hist = read_json(output_dir / "terra/demo/historical_fit.json")
    warning = read_json(output_dir / "terra/demo/early_warning_timeline.json")
    mechanism = read_json(output_dir / "terra/demo/mechanism_check.json")
    stress = read_json(output_dir / "terra/demo/stress_test.json")
    terra_artifact = "terra/demo/historical_fit.json"
    for key, metric, unit in (
        ("objective", hist["objective"]["value"], "objective units"),
        ("ust_rmse", hist["metrics"]["ust_price"]["rmse"], "USD"),
        ("ust_correlation", hist["metrics"]["ust_price"]["correlation"], "correlation"),
        ("luna_log_rmse", hist["metrics"]["luna_price"]["log_rmse"], "log-price"),
        ("luna_correlation", hist["metrics"]["luna_price"]["correlation"], "correlation"),
        ("supply_final_relative_error", hist["metrics"]["luna_supply"]["final_relative_error"], "ratio"),
    ):
        registry.add(
            f"TERRA_HF_{key.upper()}", "TERRA", key, metric, unit, terra_artifact,
            "Chỉ số tái dựng có điều kiện trên dòng lịch sử quan sát.",
            "Không phải bằng chứng dự báo ngoài mẫu hay suy luận nhân quả.",
        )
    for threshold, row in hist["metrics"]["event_timing"].items():
        registry.add(
            f"TERRA_TIMING_{threshold.replace('.', '_')}", "TERRA", f"timing_error_ust_below_{threshold}",
            row["error_hours"], "hours", terra_artifact, row["interpretation"],
            "Sai số âm nghĩa là mô phỏng chạm ngưỡng sớm hơn lịch sử.",
        )
    for mode in ("retrospective", "cutoff_safe"):
        for event, levels in warning[mode]["lead_times"].items():
            for level, row in levels.items():
                registry.add(
                    f"TERRA_EW_{mode.upper()}_{event.upper()}_{level.upper()}", "TERRA",
                    f"{mode}_{event}_{level}_lead_time", row["lead_time_hours"], "hours",
                    "terra/demo/early_warning_timeline.json", row["wording"],
                    "Âm là cảnh báo xuất hiện sau sự kiện; retrospective không phải kiểm định triển khai thời gian thực.",
                )
    registry.add(
        "TERRA_EW_LEAKAGE", "TERRA", "cutoff_safe_future_perturbation",
        warning["cutoff_safe"]["leakage_audit"]["future_perturbation"]["status"], "status",
        "terra/demo/early_warning_timeline.json", "Kiểm tra bất biến trước cutoff.",
        "PASS chỉ loại trừ dạng rò rỉ được kiểm tra, không chứng minh sức dự báo.",
    )
    direct = mechanism["direct_event_output_gross_mint"]
    old = mechanism["old_offchain_approximation"]
    for key, value, unit in (
        ("EVENT_COUNT", mechanism["raw_swap_rows"], "events"),
        ("DIRECT_CORRELATION", direct["hourly_correlation"], "correlation"),
        ("DIRECT_CUMULATIVE_ERROR", direct["final_cumulative_relative_error"], "ratio"),
        ("OLD_CORRELATION", old["hourly_correlation"], "correlation"),
        ("OLD_CUMULATIVE_ERROR", old["final_cumulative_relative_error"], "ratio"),
    ):
        registry.add(
            f"TERRA_MECH_{key}", "TERRA", key.lower(), value, unit, "terra/demo/mechanism_check.json",
            "Kiểm tra nhất quán cơ chế phát hành gộp.", "Không phải kiểm định quan hệ nhân quả với giá.",
        )
    for name, result in stress["preset_results"].items():
        summary = result["summary"]
        for key in ("collapse_count", "minimum_ust", "minimum_luna", "final_luna_supply", "max_withdrawal_stress"):
            value = summary[key] if key == "collapse_count" else summary[key]["median"]
            registry.add(
                f"TERRA_STRESS_{name.upper()}_{key.upper()}", "TERRA", f"{name}_{key}", value,
                "runs" if key == "collapse_count" else "model units", "terra/demo/stress_test.json",
                "Kết quả phản thực có điều kiện trên preset.",
                "Tần suất đường mô phỏng không phải xác suất sụp đổ ngoài đời.",
            )
    registry.add(
        "TERRA_ROWS", "TERRA", "canonical_hourly_rows", terra_quality["row_count"], "hours",
        "data_quality_summary.json", "Chuỗi giờ liên tục.", "Bao gồm biến quan sát, suy dẫn và unavailable.",
    )
    registry.add(
        "TERRA_SWAPS", "TERRA", "native_swap_events", terra_quality["native_swaps"]["rows"], "events",
        "data_quality_summary.json", "Bằng chứng giao dịch native swap đã đóng băng.",
        "Extract có giới hạn trường giao dịch như ghi trong provenance.",
    )
    for key in (
        "block_number", "candidates_discovered", "verified_borrowers", "failed_reads", "weth_collateral_borrowers",
        "usdc_borrowers", "weth_usdc_cohort", "candidate_verification_rate",
    ):
        registry.add(
            f"AAVE_DATA_{key.upper()}", "AAVE", key, aave_quality[key], "ratio" if "rate" in key else "count",
            "aave/snapshot_quality.json", "Provenance của snapshot REAL_MAINNET.",
            aave_quality.get("candidate_verification_rate_boundary", "Không đại diện toàn bộ thị trường Aave."),
        )
    hf = aave_quality["health_factor_validation"]
    for key, value in hf.items():
        registry.add(
            f"AAVE_HF_{key.upper()}", "AAVE", key, value, "ratio" if "error" in key else "count",
            "aave/snapshot_quality.json", "Đối chiếu adapter với Pool.getUserAccountData.",
            "Một số cờ sai khác còn lại được giữ lại, không loại borrower thủ công.",
        )
    aave_summary = read_json(output_dir / "aave/research_summary.json")
    for row in aave_summary["deterministic_scenarios"]:
        slug = re.sub(r"[^A-Z0-9]+", "_", row["scenario_name"].upper()).strip("_")
        for key in (
            "liquidation_at_risk", "direct_shock_liquidated_debt", "total_liquidated_debt", "cascade_amplification",
            "max_price_impact", "max_intrawave_liquidation_price_impact", "max_post_arbitrage_spread",
            "bad_debt", "cascade_depth", "liquidation_events", "number_of_waves",
            "forced_weth_volume", "wave_1_liquidated_debt", "wave_2_plus_liquidated_debt", "later_wave_share",
            "time_to_recovery_seconds", "recovery_tolerance_exceeded", "unliquidated_debt",
            "unliquidated_debt_legacy_recorded_lt",
        ):
            if key in row:
                registry.add(
                    f"AAVE_DET_{slug}_{key.upper()}", "AAVE", f"{row['scenario_name']}_{key}", row[key],
                    "model units", "aave/deterministic_scenarios.json", "Kết quả deterministic trên snapshot cố định.",
                    "Kết quả phụ thuộc kịch bản và mô hình; không phải dự báo thị trường.",
                )
    mc = read_json(output_dir / "aave/monte_carlo.json")
    for name, payload in mc["scenarios"].items():
        slug = re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")
        summary = payload["summary"]
        for key, value in (
            ("CASCADE_FREQUENCY", summary["model_implied_cascade_frequency"]),
            ("CASCADE_WILSON_LOWER", summary["cascade_frequency_wilson_95"]["lower"]),
            ("CASCADE_WILSON_UPPER", summary["cascade_frequency_wilson_95"]["upper"]),
            ("EXPECTED_SHORTFALL_95", summary["expected_shortfall_95"]),
            ("LIQUIDATED_DEBT_MEDIAN", summary["total_liquidated_debt"]["median"]),
            ("LIQUIDATED_DEBT_P95", summary["total_liquidated_debt"]["p95"]),
        ):
            registry.add(
                f"AAVE_MC_{slug}_{key}", "AAVE", f"{name}_{key.lower()}", value, "model units",
                "aave/monte_carlo.json", "Phân phối lấy mẫu có điều kiện trên mô hình.",
                "Không được diễn giải là xác suất thực tế.",
            )
    sensitivity = read_json(output_dir / "aave/sensitivity.json")["rows"]
    for family in ("GAS_MULTIPLIER", "LIQUIDATOR_CAPACITY", "ARBITRAGE_CAPACITY", "LIQUIDITY_HAIRCUT"):
        family_rows = [row for row in sensitivity if row["sensitivity_family"] == family]
        for metric in (
            "total_liquidated_debt", "bad_debt", "max_price_impact",
            "max_intrawave_liquidation_price_impact",
            "max_post_arbitrage_spread", "cascade_depth",
        ):
            if not all(metric in row for row in family_rows):
                continue
            values = [row[metric] for row in family_rows]
            registry.add(
                f"AAVE_SENS_{family}_{metric.upper()}_RANGE", "AAVE", f"{family}_{metric}_range",
                max(values) - min(values), "model units", "aave/sensitivity.json",
                "Observed response range in the one-factor sweep.",
                "Canonical snapshot and tested parameter values only.",
            )
    grid = read_json(output_dir / "aave/shock_liquidity_grid.json")["rows"]
    registry.add(
        "RQ1_GRID_MAX_CASCADE_DEPTH", "AAVE", "maximum_cascade_depth_in_tested_grid",
        max(row["cascade_depth"] for row in grid), "waves", "aave/shock_liquidity_grid.json",
        "Maximum observed cascade depth across the discrete shock × liquidity grid.",
        "Shocks −5% to −40% and liquidity haircuts 0%, 25%, 50%, 75%; no extrapolation.",
    )
    structural = read_json(output_dir / "network/structural_graph.json")
    aave_node = structural["centrality"]["nodes"]["protocol:aave-v3"]
    registry.add(
        "NETWORK_AAVE_BETWEENNESS", "NETWORK_EXTENSION", "aave_v3_betweenness_centrality",
        aave_node["betweenness_centrality"], "normalized centrality", "network/structural_graph.json",
        "Aave V3 là structural bridge theo centrality trong topology đã mô hình hóa.",
        "Không đại diện total DeFi importance.",
    )
    registry.add(
        "CROSS_CASE_SYNTHESIS_BOUNDARY", "CROSS_CASE", "legitimate_synthesis_boundary",
        read_json(output_dir / "cross_case/synthesis.json")["legitimate_synthesis"], "statement",
        "cross_case/synthesis.json", "Hai extension chia sẻ lens phản hồi phi tuyến.",
        "Không có kiểm định cơ chế chéo định lượng.",
    )

    rq_dir = output_dir / "rq_completion"
    rq_specs = (
        ("RQ3_DELAY", "rq3_reaction_delay.json", "delay_steps", (
            "delay_seconds", "total_liquidated_debt", "unliquidated_debt", "bad_debt",
            "time_to_recovery_seconds", "recovery_tolerance_exceeded", "cascade_depth",
            "number_of_liquidation_events", "max_intrawave_liquidation_price_impact",
            "max_post_arbitrage_spread",
        )),
        ("RQ3_CAPITAL", "rq3_capital_constraint.json", "capital_ratio", (
            "capital_usdc", "total_liquidated_debt", "unliquidated_debt", "bad_debt", "cascade_depth",
        )),
        ("RQ5_USDC", "rq5_usdc_depeg.json", "usdc_price_usd", (
            "borrowers_hf_below_1_00", "borrowers_hf_below_1_05", "borrowers_hf_below_1_10",
            "borrowers_hf_below_1_20", "liquidation_at_risk", "total_liquidated_debt_usdc",
            "total_liquidated_debt_usd", "bad_debt", "cascade_depth", "max_price_impact",
            "max_intrawave_liquidation_price_impact", "max_post_arbitrage_spread",
        )),
        ("RQ6_LTV", "rq6_ltv_capital_efficiency.json", "ltv_policy", (
            "aggregate_max_borrowing_capacity_usd", "median_borrower_max_borrowing_capacity_usd",
            "aggregate_current_debt_to_capacity", "median_current_debt_to_capacity",
            "borrowers_above_counterfactual_borrowing_capacity",
        )),
        ("RQ6_LT", "rq6_liquidation_threshold.json", "liquidation_threshold", (
            "borrowers_hf_below_1_00", "borrowers_hf_below_1_05", "borrowers_hf_below_1_10",
            "borrowers_hf_below_1_20", "liquidation_at_risk", "total_liquidated_debt", "bad_debt",
            "cascade_depth", "max_price_impact", "max_intrawave_liquidation_price_impact",
            "max_post_arbitrage_spread",
            "wave_2_plus_liquidated_debt", "unliquidated_debt", "unliquidated_debt_legacy_recorded_lt",
        )),
        ("RQ6_BONUS", "rq6_liquidation_bonus.json", "liquidation_bonus", (
            "number_of_liquidation_events", "total_liquidated_debt", "collateral_seized_weth",
            "forced_weth_volume", "liquidator_expected_profit_usdc", "liquidator_gas_cost_usdc",
            "bad_debt", "max_price_impact", "max_intrawave_liquidation_price_impact",
            "max_post_arbitrage_spread",
            "cascade_depth", "unliquidated_debt", "unliquidated_debt_legacy_recorded_lt",
        )),
    )
    for prefix, artifact_name, parameter, metrics in rq_specs:
        payload = read_json(rq_dir / artifact_name)
        for row in payload["rows"]:
            parameter_slug = str(row[parameter]).replace("-", "NEG_").replace(".", "_")
            for metric in metrics:
                if metric not in row:
                    continue
                unit = "count" if metric.startswith(("borrowers_", "number_")) or metric == "cascade_depth" else "model units"
                registry.add(
                    f"{prefix}_{parameter_slug}_{metric.upper()}", "AAVE", metric, row[metric], unit,
                    f"rq_completion/{artifact_name}", "Controlled one-factor analysis on the canonical snapshot.",
                    payload.get("claim_boundary", payload.get("limitation", "Tested range and model only.")),
                )
    rq_summary = read_json(rq_dir / "rq_completion_summary.json")
    registry.add(
        "RQ3_DELAY_STATUS", "AAVE", "reaction_delay_status", rq_summary["rq3"]["reaction_delay_status"],
        "status", "rq_completion/rq_completion_summary.json", "Delay result under the tested range.",
        rq_summary["claim_boundary"],
    )
    capital = read_json(rq_dir / "rq3_capital_constraint.json")
    registry.add(
        "RQ3_REQUIRED_CAPITAL_REFERENCE", "AAVE", "required_capital_reference_usdc",
        capital["required_capital_reference_usdc"], "USDC", "rq_completion/rq3_capital_constraint.json",
        capital["unconstrained_reference"]["definition"], capital["claim_boundary"],
    )
    usdc = read_json(rq_dir / "rq5_usdc_depeg.json")
    registry.add(
        "RQ5_USDC_BASELINE_COMPATIBLE", "AAVE", "usdc_price_1_matches_legacy",
        usdc["backward_compatibility"]["usdc_price_1_matches_legacy"], "boolean",
        "rq_completion/rq5_usdc_depeg.json", "Explicit USDC=$1 preserves legacy output.", usdc["limitation"],
    )
    bonus = read_json(rq_dir / "rq6_liquidation_bonus.json")
    registry.add(
        "RQ6_BONUS_STATUS", "AAVE", "liquidation_bonus_status", bonus["status"], "status",
        "rq_completion/rq6_liquidation_bonus.json", bonus["mechanism"], bonus["claim_boundary"],
    )
    return registry


def _md_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "_Không có hàng dữ liệu._\n"
    fields = list(rows[0])
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")).replace("|", "\\|") for field in fields) + " |")
    return "\n".join(lines) + "\n"


def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["status"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows or [{"status": "NO_ROWS"}])


def write_table(base: Path, table_id: str, slug: str, title: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    csv_path = base / f"{table_id}_{slug}.csv"
    md_path = base / f"{table_id}_{slug}.md"
    _csv(csv_path, rows)
    md_path.write_text(f"# {table_id} — {title}\n\n" + _md_table(rows), encoding="utf-8")
    return {"id": table_id, "title": title, "csv": csv_path.as_posix(), "markdown": md_path.as_posix(), "rows": len(rows)}


def build_rq_answer_matrix(output_dir: Path) -> list[dict[str, Any]]:
    rows = [
        {
            "rq": "RQ1",
            "research_question": "Cú sốc ETH tối thiểu nào bắt đầu cascade depth ≥ 2?",
            "analysis_method": "Lưới rời rạc shock −5% đến −40% × liquidity haircut 0/25/50/75%.",
            "main_result": "Không quan sát được ngưỡng liquidation cascade trong miền stress đã thử.",
            "answer_status": "NOT_OBSERVED_IN_TEST_RANGE",
            "key_evidence_ids": ["RQ1_GRID_MAX_CASCADE_DEPTH"],
            "claim_boundary": "Không nội suy threshold ra ngoài miền hoặc giữa các cell.",
            "limitation": "Một snapshot, một venue thực thi và lưới hữu hạn.",
        },
        {
            "rq": "RQ2",
            "research_question": "DEX depth/haircut ảnh hưởng price impact, amplification và bad debt thế nào?",
            "analysis_method": "Sweep liquidity haircut và shock × liquidity grid.",
            "main_result": "Haircut làm tăng intrawave impact/bad debt trong range, nhưng không tạo Wave 2.",
            "answer_status": "SUPPORTED",
            "key_evidence_ids": [
                "AAVE_SENS_LIQUIDITY_HAIRCUT_MAX_INTRAWAVE_LIQUIDATION_PRICE_IMPACT_RANGE",
                "AAVE_SENS_LIQUIDITY_HAIRCUT_BAD_DEBT_RANGE",
                "RQ1_GRID_MAX_CASCADE_DEPTH",
            ],
            "claim_boundary": "Khuếch đại hậu quả khác với tạo wave liquidation mới.",
            "limitation": "Thanh khoản tĩnh, một Uniswap V3 pool.",
        },
        {
            "rq": "RQ3",
            "research_question": "Gas, capital/capacity và reaction delay ảnh hưởng xử lý vị thế thế nào?",
            "analysis_method": "One-factor sweeps cộng delay 0/1/2/4 và capital 25/50/100/200% demand.",
            "main_result": "Capital 25%/50% binding; gas/capacity không binding; recovery dùng first-return semantics.",
            "answer_status": "PARTIALLY_SUPPORTED",
            "key_evidence_ids": [
                "RQ3_DELAY_STATUS", "RQ3_REQUIRED_CAPITAL_REFERENCE",
                "RQ3_CAPITAL_0_25_TOTAL_LIQUIDATED_DEBT", "RQ3_CAPITAL_1_0_TOTAL_LIQUIDATED_DEBT",
                "AAVE_SENS_GAS_MULTIPLIER_TOTAL_LIQUIDATED_DEBT_RANGE",
                "AAVE_SENS_LIQUIDATOR_CAPACITY_TOTAL_LIQUIDATED_DEBT_RANGE",
            ],
            "claim_boundary": "Professor Demo, canonical snapshot và tested ranges.",
            "limitation": "Engine dùng capital cộng dồn, không tái sử dụng.",
        },
        {
            "rq": "RQ4",
            "research_question": "Năng lực arbitrage ảnh hưởng deviation, waves và recovery thế nào?",
            "analysis_method": "One-factor arbitrage-capacity sweep 0–100%.",
            "main_result": (
                "Intrawave forced-sale impact không đổi theo arbitrage capacity; residual post-arbitrage "
                "spread giảm khi capacity tăng."
            ),
            "answer_status": "SUPPORTED_WITH_MODEL_BOUNDARY",
            "key_evidence_ids": [
                "AAVE_SENS_ARBITRAGE_CAPACITY_MAX_INTRAWAVE_LIQUIDATION_PRICE_IMPACT_RANGE",
                "AAVE_SENS_ARBITRAGE_CAPACITY_MAX_POST_ARBITRAGE_SPREAD_RANGE",
                "AAVE_SENS_ARBITRAGE_CAPACITY_CASCADE_DEPTH_RANGE",
            ],
            "claim_boundary": "Không suy ra arbitrage ngoài đời không quan trọng.",
            "limitation": "Price deviation nhỏ và agent/routing đơn giản.",
        },
        {
            "rq": "RQ5",
            "research_question": "USDC depeg thay đổi stress khi USDC là debt asset thế nào?",
            "analysis_method": "Pure USDC debt-valuation sensitivity, $0.90–$1.10.",
            "main_result": "Upward depeg làm HF yếu hơn; downward depeg làm HF mạnh hơn hoặc không xấu đi.",
            "answer_status": "SUPPORTED",
            "key_evidence_ids": [
                "RQ5_USDC_BASELINE_COMPATIBLE", "RQ5_USDC_1_1_BORROWERS_HF_BELOW_1_00",
                "RQ5_USDC_1_0_BORROWERS_HF_BELOW_1_00", "RQ5_USDC_0_9_BORROWERS_HF_BELOW_1_20",
            ],
            "claim_boundary": "This experiment isolates the USDC debt-valuation channel.",
            "limitation": "Không mô hình market liquidity, redemption, settlement hay confidence.",
        },
        {
            "rq": "RQ6",
            "research_question": "LTV, LT và bonus tạo trade-off capital efficiency/tail risk nào?",
            "analysis_method": "LTV ex-ante capacity; LT HF boundary; bonus execution economics.",
            "main_result": "LTV tăng capacity nhưng giảm origination buffer; LT dịch boundary; bonus đổi seizure/profit.",
            "answer_status": "SUPPORTED",
            "key_evidence_ids": [
                "RQ6_LTV_0_755_AGGREGATE_MAX_BORROWING_CAPACITY_USD",
                "RQ6_LTV_0_825_AGGREGATE_MAX_BORROWING_CAPACITY_USD",
                "RQ6_LT_0_83_TOTAL_LIQUIDATED_DEBT", "RQ6_LT_0_855_TOTAL_LIQUIDATED_DEBT",
                "RQ6_BONUS_STATUS",
            ],
            "claim_boundary": "LTV không phải direct frozen-snapshot liquidation trigger.",
            "limitation": "Policy counterfactual trên frozen cohort, không dự báo hành vi tái underwrite.",
        },
    ]
    write_json(output_dir / "rq_answer_matrix.json", {"research_questions": rows})
    return rows


def generate_tables(output_dir: Path, terra_quality: dict[str, Any], aave_quality: dict[str, Any]) -> list[dict[str, Any]]:
    hist = read_json(output_dir / "terra/demo/historical_fit.json")
    warning = read_json(output_dir / "terra/demo/early_warning_timeline.json")
    mechanism = read_json(output_dir / "terra/demo/mechanism_check.json")
    stress = read_json(output_dir / "terra/demo/stress_test.json")
    deterministic = read_json(output_dir / "aave/deterministic_scenarios.json")["rows"]
    sensitivity = read_json(output_dir / "aave/sensitivity.json")
    grid = read_json(output_dir / "aave/shock_liquidity_grid.json")
    mc = read_json(output_dir / "aave/monte_carlo.json")
    structural = read_json(output_dir / "network/structural_graph.json")
    professor = read_json(output_dir / "network/professor_demo_graph.json")
    audit = read_json(output_dir / "terra/audit/final_metrics.json")
    rq_dir = output_dir / "rq_completion"
    rq_matrix = read_json(output_dir / "rq_answer_matrix.json")["research_questions"]
    tables: list[tuple[str, str, str, list[dict[str, Any]]]] = []
    tables.append(("Table_01", "data_sources", "Nguồn dữ liệu và độ phủ", [
        {"case": "Terra", "source": EXTENDED_DATASET.as_posix(), "rows": terra_quality["row_count"], "status": terra_quality["status"]},
        {"case": "Terra swaps", "source": NATIVE_SWAPS.as_posix(), "rows": terra_quality["native_swaps"]["rows"], "status": "OBSERVED_EXTRACT"},
        {"case": "Aave", "source": CANONICAL_SNAPSHOT.as_posix(), "rows": aave_quality["verified_borrowers"], "status": "REAL_MAINNET"},
    ]))
    tables.append(("Table_02", "aave_provenance", "Provenance Aave Mainnet", [{
        key: aave_quality[key] for key in ("mode", "chain_id", "block_number", "block_hash", "block_timestamp", "candidates_discovered", "verified_borrowers", "weth_usdc_cohort")
    }]))
    tables.append(("Table_03", "aave_hf_validation", "Đối chiếu Health Factor", [aave_quality["health_factor_validation"]]))
    tables.append(("Table_04", "aave_deterministic", "Kịch bản Aave deterministic", deterministic))
    tables.append(("Table_05", "aave_sensitivity", "Độ nhạy một yếu tố", sensitivity["spearman"]))
    tables.append(("Table_06", "aave_monte_carlo", "Tóm tắt Monte Carlo", [
        {"scenario": name, "runs": payload["runs"], "cascade_frequency": payload["summary"]["model_implied_cascade_frequency"],
         "wilson_lower": payload["summary"]["cascade_frequency_wilson_95"]["lower"], "wilson_upper": payload["summary"]["cascade_frequency_wilson_95"]["upper"],
         "expected_shortfall_95": payload["summary"]["expected_shortfall_95"]}
        for name, payload in mc["scenarios"].items()
    ]))
    tables.append(("Table_07", "aave_grid_thresholds", "Ngưỡng shock × thanh khoản", grid["thresholds"]))
    tables.append(("Table_08", "network_centrality", "Centrality mạng cấu trúc", [
        {"node": node, **values} for node, values in structural["centrality"]["nodes"].items()
    ]))
    tables.append(("Table_09", "network_waves", "Các khung truyền dẫn theo wave", [
        {
            "frame": index + 1,
            "nodes": len(frame.get("active_nodes", [])),
            "edges": len(frame.get("active_edge_ids", [])),
        }
        for index, frame in enumerate(professor.get("frames", []))
    ]))
    tables.append(("Table_10", "terra_fit", "Chỉ số Historical Fit Terra", [
        {"metric": "objective", "value": hist["objective"]["value"]},
        *[{"metric": f"ust_{key}", "value": value} for key, value in hist["metrics"]["ust_price"].items()],
        *[{"metric": f"luna_{key}", "value": value} for key, value in hist["metrics"]["luna_price"].items()],
        *[{"metric": f"supply_{key}", "value": value} for key, value in hist["metrics"]["luna_supply"].items()],
    ]))
    tables.append(("Table_11", "terra_early_warning", "Lead/lag cảnh báo sớm", [
        {"mode": mode, "event": event, "level": level, "lead_time_hours": row["lead_time_hours"], "warning_time": row["warning_time"], "event_time": row["event_time"]}
        for mode in ("retrospective", "cutoff_safe") for event, levels in warning[mode]["lead_times"].items() for level, row in levels.items()
    ]))
    tables.append(("Table_12", "terra_mechanism", "Kiểm tra cơ chế phát hành", [
        {"method": "direct event output", **mechanism["direct_event_output_gross_mint"]},
        {"method": "old off-chain approximation", **mechanism["old_offchain_approximation"]},
    ]))
    tables.append(("Table_13", "terra_stress", "Preset stress Terra", [
        {"preset": name, "runs": result["summary"]["collapse_count"] + result["summary"]["noncollapse_count"],
         "collapse_count": result["summary"]["collapse_count"], "minimum_ust_median": result["summary"]["minimum_ust"]["median"],
         "minimum_luna_median": result["summary"]["minimum_luna"]["median"], "final_supply_median": result["summary"]["final_luna_supply"]["median"]}
        for name, result in stress["preset_results"].items()
    ]))
    tables.append(("Table_14", "terra_robustness", "Độ bền Terra", [
        {"test": "strict OOS V2", "purpose": "forecast audit", "finding": "negative evidence retained", "supports_claim": "NO", "limitation": "frozen historical window"},
        {"test": "conditional replay", "purpose": "mechanism reconstruction", "finding": f"UST RMSE={audit['ust_price']['rmse']:.6g}", "supports_claim": "PARTIAL", "limitation": "not prediction"},
        {"test": "rolling origin", "purpose": "short-horizon robustness", "finding": "four expanding windows", "supports_claim": "PARTIAL", "limitation": "six-hour horizon"},
        {"test": "ablation/sensitivity", "purpose": "component dependence", "finding": "reported without holdout selection", "supports_claim": "PARTIAL", "limitation": "model-dependent"},
    ]))
    tables.append(("Table_15", "cross_case", "Tổng hợp hai ca nghiên cứu", [
        {"dimension": "empirical role", "Terra": "historical mechanism/reconstruction", "Aave_Uniswap": "contemporary Mainnet stress"},
        {"dimension": "feedback", "Terra": "peg-redemption-issuance-confidence", "Aave_Uniswap": "price-HF-liquidation-DEX-price"},
        {"dimension": "boundary", "Terra": "does not validate Aave mechanics", "Aave_Uniswap": "does not prove Terra causality"},
    ]))
    for table_id, slug, title in (
        ("Table_16", "rq3_reaction_delay", "RQ3 — Liquidator reaction-delay sensitivity"),
        ("Table_17", "rq3_capital_constraint", "RQ3 — Binding liquidator-capital sensitivity"),
        ("Table_18", "rq5_usdc_depeg", "RQ5 — USDC debt-valuation sensitivity"),
        ("Table_19", "rq6_ltv_capital_efficiency", "RQ6 — LTV capital-efficiency counterfactual"),
        ("Table_20", "rq6_liquidation_threshold", "RQ6 — Liquidation Threshold sensitivity"),
        ("Table_21", "rq6_liquidation_bonus", "RQ6 — Liquidation Bonus sensitivity"),
    ):
        tables.append((table_id, slug, title, read_json(rq_dir / f"{slug}.json")["rows"]))
    tables.append((
        "Table_22", "rq_answer_matrix", "Final RQ1–RQ6 answer matrix",
        [{**row, "key_evidence_ids": ";".join(row["key_evidence_ids"])} for row in rq_matrix],
    ))
    registry = [write_table(output_dir / "tables", *spec) for spec in tables]
    rq_map = {
        "Table_01": "RQ1–RQ6 / Extensions", "Table_02": "RQ1–RQ6", "Table_03": "RQ1/RQ5/RQ6",
        "Table_04": "RQ1–RQ4", "Table_05": "RQ1–RQ4", "Table_06": "RQ1–RQ4",
        "Table_07": "RQ1/RQ2", "Table_08": "Network Analysis Extension",
        "Table_09": "Network Analysis Extension", "Table_10": "Historical Validation Extension",
        "Table_11": "Historical Validation Extension", "Table_12": "Historical Validation Extension",
        "Table_13": "Historical Validation Extension", "Table_14": "Historical Validation Extension",
        "Table_15": "Cross-case extension", "Table_16": "RQ3", "Table_17": "RQ3",
        "Table_18": "RQ5", "Table_19": "RQ6", "Table_20": "RQ6", "Table_21": "RQ6",
        "Table_22": "RQ1–RQ6",
    }
    for row in registry:
        row.update(
            {
                "research_question": rq_map[row["id"]],
                "main_takeaway": "Numerical evidence; interpretation and boundary are in the RQ matrix/report.",
                "data_status": "GENERATED_FROM_FROZEN_EVIDENCE",
                "claim_boundary": "Canonical inputs and tested ranges only.",
                "presentation_priority": "CORE" if row["id"] in {f"Table_{index:02d}" for index in range(16, 23)} else "APPENDIX",
            }
        )
    write_json(output_dir / "table_registry.json", registry)
    return registry


def _save_figure(fig: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    if path.stat().st_size < 1000:
        raise ValueError(f"empty or implausibly small figure: {path}")


def _figure_meta(
    figure_id: str,
    title: str,
    path: Path,
    question: str,
    takeaway: str,
    status: str,
    priority: str,
    claim_boundary: str = "Canonical inputs, modeled mechanisms and tested ranges only.",
) -> dict[str, Any]:
    return {
        "id": figure_id,
        "title": title,
        "path": path.as_posix(),
        "research_question": question,
        "main_takeaway": takeaway,
        "data_status": status,
        "caption": f"{title}. {takeaway}",
        "claim_boundary": claim_boundary,
        "presentation_priority": priority,
    }


def generate_figures(output_dir: Path) -> list[dict[str, Any]]:
    figure_dir = output_dir / "figures"
    hist = read_json(output_dir / "terra/demo/historical_fit.json")
    warning = read_json(output_dir / "terra/demo/early_warning_timeline.json")
    stress = read_json(output_dir / "terra/demo/stress_test.json")
    mechanism = read_json(output_dir / "terra/demo/mechanism_check.json")
    snapshot = load_canonical_snapshot()
    deterministic = read_json(output_dir / "aave/deterministic_scenarios.json")["rows"]
    sensitivity = read_json(output_dir / "aave/sensitivity.json")
    grid = read_json(output_dir / "aave/shock_liquidity_grid.json")["rows"]
    mc = read_json(output_dir / "aave/monte_carlo.json")
    structural = read_json(output_dir / "network/structural_graph.json")
    professor = read_json(output_dir / "network/professor_demo_graph.json")
    rq_dir = output_dir / "rq_completion"
    figures: list[dict[str, Any]] = []

    actual = pd.DataFrame(hist["actual_timeseries"])
    simulated = pd.DataFrame(hist["simulated_timeseries"])
    actual["timestamp"] = pd.to_datetime(actual["timestamp"], utc=True)
    simulated["timestamp"] = pd.to_datetime(simulated["timestamp"], utc=True)

    def add_line(
        figure_id: str,
        slug: str,
        title: str,
        lines: list[tuple[Any, Any, str]],
        ylabel: str,
        question: str,
        takeaway: str,
        status: str = "OBSERVED_AND_SIMULATED",
        priority: str = "CORE",
        logy: bool = False,
    ) -> None:
        fig, axis = plt.subplots(figsize=(9, 4.8))
        for x, y, label in lines:
            axis.plot(x, y, label=label, linewidth=1.5)
        axis.set_title(title)
        axis.set_ylabel(ylabel)
        if logy:
            axis.set_yscale("log")
        axis.grid(alpha=0.25)
        axis.legend(loc="best")
        path = figure_dir / f"{figure_id}_{slug}.png"
        _save_figure(fig, path)
        figures.append(_figure_meta(figure_id, title, path, question, takeaway, status, priority))

    add_line(
        "T01", "terra_prices", "Terra: giá UST và LUNA lịch sử",
        [(actual["timestamp"], actual["ust_price"], "UST"), (actual["timestamp"], actual["luna_price"], "LUNA")],
        "USD", "RQ3", "Hai tài sản giảm theo thang đo rất khác nhau; hình này chỉ mô tả lịch sử.", "OBSERVED", "CORE",
    )
    add_line(
        "T02", "terra_supply", "Terra: nguồn cung LUNA",
        [(actual["timestamp"], actual["luna_supply"], "Quan sát")], "LUNA", "RQ3",
        "Nguồn cung tăng mạnh trong cửa sổ sụp đổ.", "OBSERVED", "CORE", True,
    )
    withdrawal = actual.get("anchor_withdrawal_flow", pd.Series(np.zeros(len(actual))))
    deposits = actual.get("anchor_total_deposits", pd.Series(np.zeros(len(actual))))
    add_line(
        "T03", "anchor_flows", "Anchor: tiền gửi và dòng rút",
        [(actual["timestamp"], deposits, "Tiền gửi"), (actual["timestamp"], withdrawal.fillna(0), "Dòng rút")],
        "token units", "RQ4", "Dòng rút chỉ được coi là quan sát trong khoảng availability đã công bố.", "MIXED_AVAILABILITY", "APPENDIX",
    )
    backing = actual.get("backing_ratio", pd.Series(np.nan, index=actual.index))
    add_line(
        "T04", "backing_ratio", "Terra: tỷ lệ bảo chứng khả dụng",
        [(actual["timestamp"], backing, "Tỷ lệ bảo chứng")], "ratio", "RQ3",
        "Chuỗi có khoảng unavailable; không nội suy thành quan sát.", "PARTIALLY_OBSERVED", "APPENDIX",
    )
    add_line(
        "T05", "ust_fit", "Historical Fit: UST quan sát và mô phỏng",
        [(actual["timestamp"], actual["ust_price"], "Quan sát"), (simulated["timestamp"], simulated["ust_price"], "Mô phỏng")],
        "USD", "RQ3", "Mô hình tái dựng hướng đi nhưng chạm các ngưỡng quá sớm.", "OBSERVED_AND_SIMULATED", "CORE",
    )
    add_line(
        "T06", "luna_fit", "Historical Fit: LUNA quan sát và mô phỏng",
        [(actual["timestamp"], actual["luna_price"], "Quan sát"), (simulated["timestamp"], simulated["luna_price"], "Mô phỏng")],
        "USD (log)", "RQ3", "Tương quan cao không đồng nghĩa dự báo đúng thời điểm.", "OBSERVED_AND_SIMULATED", "CORE", True,
    )
    add_line(
        "T07", "supply_fit", "Historical Fit: nguồn cung LUNA",
        [(actual["timestamp"], actual["luna_supply"], "Quan sát"), (simulated["timestamp"], simulated["luna_supply"], "Mô phỏng")],
        "LUNA (log)", "RQ3", "Tái dựng nguồn cung tốt trong cửa sổ có dữ liệu nhưng vẫn là fit có điều kiện.",
        "OBSERVED_AND_SIMULATED", "CORE", True,
    )
    ew_lines = []
    for mode in ("retrospective", "cutoff_safe"):
        timeline = pd.DataFrame(warning[mode]["timeline"])
        ew_lines.append((pd.to_datetime(timeline["timestamp"], utc=True), timeline["risk_score"], mode))
    add_line(
        "T08", "early_warning", "Điểm cảnh báo sớm Terra",
        ew_lines, "risk score", "RQ4", "Cutoff-safe cảnh báo muộn cho depeg ban đầu nhưng sớm hơn ngưỡng 0,90 ở mức High Risk.",
        "DERIVED_INDICATOR", "CORE",
    )
    fig, axis = plt.subplots(figsize=(9, 5))
    timing_rows = []
    for mode in ("retrospective", "cutoff_safe"):
        for event, levels in warning[mode]["lead_times"].items():
            for level, row in levels.items():
                timing_rows.append((f"{mode[:3]}:{event[-5:]}:{level}", row["lead_time_hours"]))
    axis.barh([row[0] for row in timing_rows], [row[1] for row in timing_rows])
    axis.axvline(0, color="black", linewidth=1)
    axis.set_title("Lead/lag của cảnh báo sớm (dương = sớm)")
    axis.set_xlabel("giờ")
    path = figure_dir / "T09_warning_timing.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("T09", "Lead/lag cảnh báo", path, "RQ4", "Cảnh báo cutoff-safe không đi trước depeg ban đầu.", "DERIVED_INDICATOR", "CORE"))
    fan = pd.DataFrame(stress["fan_chart"])
    fig, axis = plt.subplots(figsize=(9, 4.8))
    for key in ("p05", "median", "p95"):
        if isinstance(fan["ust_price"].iloc[0], dict):
            axis.plot(fan["hour"], [row[key] for row in fan["ust_price"]], label=key)
    axis.set_title("Stress Terra baseline: fan chart UST")
    axis.set_xlabel("giờ")
    axis.set_ylabel("UST")
    axis.legend()
    path = figure_dir / "T10_stress_fan.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("T10", "Fan chart stress Terra", path, "RQ3", "Phân phối là bất định trong mô hình, không phải xác suất thị trường.", "SIMULATED", "APPENDIX"))
    fig, axis = plt.subplots(figsize=(8, 4.8))
    labels = ["Direct output", "Old approximation"]
    axis.bar(labels, [mechanism["direct_event_output_gross_mint"]["hourly_correlation"], mechanism["old_offchain_approximation"]["hourly_correlation"]])
    axis.set_title("Kiểm tra cơ chế: tương quan theo giờ")
    axis.set_ylabel("correlation")
    path = figure_dir / "T11_mechanism_comparison.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("T11", "So sánh kiểm tra cơ chế", path, "RQ3", "Direct event output kiểm tra nhất quán kế toán, không chứng minh nhân quả giá.", "OBSERVED_DERIVED", "CORE"))
    audit = read_json(output_dir / "terra/audit/final_metrics.json")
    fig, axis = plt.subplots(figsize=(8, 4.8))
    axis.bar(["UST RMSE", "LUNA log-RMSE", "Supply final error"], [audit["ust_price"]["rmse"], audit["luna_price"]["log_rmse"], abs(audit["luna_supply"]["final_relative_error"])])
    axis.set_title("Terra: chỉ số kiểm tra độ bền (khác đơn vị)")
    path = figure_dir / "T12_robustness.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("T12", "Tóm tắt độ bền Terra", path, "RQ3", "Các chỉ số có đơn vị khác nhau; dùng để định vị sai số, không xếp hạng chung.", "DERIVED", "APPENDIX"))

    hf_values = [finite(row.get("health_factor", 0)) for row in snapshot["borrowers"] if math.isfinite(float(row.get("health_factor", 0)))]
    fig, axis = plt.subplots(figsize=(8, 4.8))
    axis.hist(np.clip(hf_values, 0, 10), bins=40)
    axis.axvline(1, color="red", linestyle="--")
    axis.set_title("Phân phối Health Factor (cắt hiển thị tại 10)")
    path = figure_dir / "A01_health_factor_distribution.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("A01", "Phân phối Health Factor", path, "RQ1", "Phân phối mô tả cohort đã xác minh, không phải toàn thị trường.", "REAL_MAINNET", "CORE"))
    debts = sorted([finite(row.get("debt_usdc", 0)) + finite(row.get("other_debt_usd", 0)) for row in snapshot["borrowers"]], reverse=True)[:20]
    fig, axis = plt.subplots(figsize=(9, 4.8))
    axis.bar(range(1, len(debts) + 1), debts)
    axis.set_title("Tập trung nợ: 20 vị thế lớn nhất (không lộ địa chỉ)")
    axis.set_xlabel("xếp hạng ẩn danh")
    path = figure_dir / "A02_debt_concentration.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("A02", "Tập trung nợ", path, "RQ1", "Chỉ dùng xếp hạng ẩn danh; địa chỉ borrower không được xuất.", "REAL_MAINNET", "APPENDIX"))
    pools = snapshot.get("dex_pools", [])
    fig, axis = plt.subplots(figsize=(8, 4.8))
    axis.bar([str(row.get("fee")) for row in pools], [finite(row.get("depth_usdc_2pct") or 0) for row in pools])
    axis.set_title("Độ sâu 2% theo fee tier Uniswap V3")
    axis.set_ylabel("USDC")
    path = figure_dir / "A03_pool_depth.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("A03", "Độ sâu pool Uniswap", path, "RQ3", "Venue thực thi được chọn theo dữ liệu snapshot cùng block.", "REAL_MAINNET", "CORE"))

    def scenario_bar(figure_id: str, slug: str, metric: str, title: str, takeaway: str) -> None:
        fig, axis = plt.subplots(figsize=(10, 5))
        axis.bar([row["scenario_name"] for row in deterministic], [finite(row.get(metric, 0)) for row in deterministic])
        axis.tick_params(axis="x", rotation=35)
        axis.set_title(title)
        path = figure_dir / f"{figure_id}_{slug}.png"
        _save_figure(fig, path)
        figures.append(_figure_meta(figure_id, title, path, "RQ1/RQ2", takeaway, "SIMULATED_ON_REAL_MAINNET_STATE", "CORE"))

    scenario_bar("A04", "scenario_comparison", "total_liquidated_debt", "Nợ thanh lý theo kịch bản", "Mức thanh lý phụ thuộc mạnh vào giả định cú sốc.")
    shock_rows = [row for row in sensitivity["rows"] if row["sensitivity_family"] == "ETH_SHOCK"]
    add_line("A05", "liquidation_vs_shock", "Thanh lý theo cú sốc ETH", [( [abs(row["parameter_value"]) for row in shock_rows], [row["total_liquidated_debt"] for row in shock_rows], "liquidated debt")], "USDC", "RQ1", "Bề mặt phản ứng có thể phi tuyến và chỉ được đánh giá tại các điểm thử.", "SIMULATED", "CORE")
    add_line("A06", "bad_debt_vs_shock", "Nợ xấu theo cú sốc ETH", [([abs(row["parameter_value"]) for row in shock_rows], [row["bad_debt"] for row in shock_rows], "bad debt")], "USDC", "RQ1", "Nợ xấu là model-implied dưới năng lực liquidator đã đặt.", "SIMULATED", "CORE")

    def heatmap(figure_id: str, slug: str, metric: str, title: str, takeaway: str) -> None:
        shocks = sorted({int(row["shock_pct"]) for row in grid}, reverse=True)
        haircuts = sorted({int(row["liquidity_haircut_pct"]) for row in grid})
        matrix = np.asarray([[next(finite(row[metric]) for row in grid if int(row["shock_pct"]) == shock and int(row["liquidity_haircut_pct"]) == haircut) for haircut in haircuts] for shock in shocks])
        fig, axis = plt.subplots(figsize=(7, 5))
        image = axis.imshow(matrix, aspect="auto", cmap="magma")
        axis.set_xticks(range(len(haircuts)), haircuts)
        axis.set_yticks(range(len(shocks)), shocks)
        axis.set_xlabel("liquidity haircut (%)")
        axis.set_ylabel("ETH shock (%)")
        axis.set_title(title)
        fig.colorbar(image, ax=axis)
        path = figure_dir / f"{figure_id}_{slug}.png"
        _save_figure(fig, path)
        figures.append(_figure_meta(figure_id, title, path, "RQ1/RQ2", takeaway, "SIMULATED_GRID", "CORE"))

    heatmap("A07", "cascade_heatmap", "cascade_depth", "Độ sâu cascade: shock × liquidity", "Ngưỡng chỉ là chuyển tiếp rời rạc trong lưới thử.")
    heatmap("A08", "bad_debt_heatmap", "bad_debt", "Nợ xấu: shock × liquidity", "Thanh khoản thấp có thể khuếch đại hậu quả tùy vùng kịch bản.")
    prof_mc = mc["scenarios"]["PROFESSOR_DEMO"]
    fig, axis = plt.subplots(figsize=(8, 4.8))
    axis.hist(prof_mc["distributions"]["bad_debt"], bins=30)
    axis.set_title("Monte Carlo Professor Demo: phân phối nợ xấu")
    path = figure_dir / "A09_mc_bad_debt.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("A09", "Phân phối nợ xấu Monte Carlo", path, "RQ1", "Đây là phân phối trong mô hình, không phải phân phối xác suất thực tế.", "SIMULATED", "CORE"))
    values = np.sort(np.asarray(prof_mc["distributions"]["total_liquidated_debt"], dtype=float))
    fig, axis = plt.subplots(figsize=(8, 4.8))
    axis.plot(values, np.arange(1, len(values) + 1) / len(values))
    axis.set_title("CDF nợ thanh lý — Professor Demo")
    axis.set_xlabel("USDC")
    path = figure_dir / "A10_liquidation_cdf.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("A10", "CDF nợ thanh lý", path, "RQ1", "CDF phản ánh biến thiên theo nhiễu mô phỏng với seed/runs đã công bố.", "SIMULATED", "APPENDIX"))
    corr_rows = sensitivity["spearman"]
    fig, axis = plt.subplots(figsize=(10, 5))
    labels = [f"{row['sensitivity_family']}:{row['metric']}" for row in corr_rows]
    vals = [0 if row["spearman_rank_correlation"] is None else row["spearman_rank_correlation"] for row in corr_rows]
    axis.bar(range(len(vals)), vals)
    axis.set_xticks(range(len(vals)), labels, rotation=90, fontsize=6)
    axis.set_ylim(-1.05, 1.05)
    axis.set_title("Tương quan hạng trong sweep một yếu tố")
    path = figure_dir / "A11_sensitivity_summary.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("A11", "Tóm tắt độ nhạy", path, "RQ2", "Tương quan sweep là association trong mô hình, không phải quan hệ nhân quả.", "SIMULATED", "APPENDIX"))

    def network_figure(figure_id: str, slug: str, graph: dict[str, Any], frame_index: int | None, title: str, takeaway: str) -> None:
        active_ids = None
        if frame_index is not None and frame_index < len(graph.get("frames", [])):
            active_ids = set(graph["frames"][frame_index].get("active_edge_ids", []))
        g = nx.DiGraph()
        for node in graph["nodes"]:
            g.add_node(node["id"])
        for edge in graph["edges"]:
            if active_ids is None or edge["id"] in active_ids:
                g.add_edge(edge["source"], edge["target"], weight=max(float(edge.get("normalized_strength", 0)), 0.1))
        fig, axis = plt.subplots(figsize=(9, 6))
        if g.number_of_edges():
            pos = nx.spring_layout(g, seed=20260914)
            nx.draw_networkx(g, pos=pos, ax=axis, node_size=1100, font_size=7, arrows=True, width=1.2)
        else:
            axis.text(0.5, 0.5, "Không có cạnh hoạt hóa trong wave này", ha="center", va="center")
        axis.set_title(title)
        axis.axis("off")
        path = figure_dir / f"{figure_id}_{slug}.png"
        _save_figure(fig, path)
        figures.append(_figure_meta(figure_id, title, path, "RQ5", takeaway, "EVIDENCE_BACKED_MODELED_SUBNETWORK", "CORE" if figure_id in {"A12", "A13"} else "ADVANCED"))

    network_figure("A12", "structural_network", structural, None, "Mạng contagion cấu trúc", "Centrality chỉ áp dụng cho sub-network Aave–Uniswap đã mô hình hóa.")
    network_figure("A13", "professor_wave1", professor, 1, "Professor Demo — Wave 1", "Wave 1 biểu diễn thanh lý trực tiếp sau cú sốc.")
    network_figure("A14", "professor_wave2", professor, 2, "Professor Demo — Wave 2", "Nếu không có wave thứ hai, hình ghi nhận bằng chứng âm thay vì tạo cascade giả.")
    matrix = professor["contagion_matrix"]
    fig, axis = plt.subplots(figsize=(7, 6))
    image = axis.imshow(np.asarray(matrix["values"], dtype=float), cmap="viridis", vmin=0, vmax=1)
    axis.set_xticks(range(len(matrix["node_order"])), matrix["node_order"], rotation=90, fontsize=6)
    axis.set_yticks(range(len(matrix["node_order"])), matrix["node_order"], fontsize=6)
    axis.set_title("Ma trận contagion chuẩn hóa")
    fig.colorbar(image, ax=axis)
    path = figure_dir / "A15_contagion_matrix.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("A15", "Ma trận contagion", path, "RQ5", "Điểm chuẩn hóa không phải xác suất truyền nhiễm.", "MODELED_SCORE", "ADVANCED"))
    centrality = structural["centrality"]["nodes"]
    fig, axis = plt.subplots(figsize=(9, 5))
    nodes = list(centrality)
    axis.barh(nodes, [centrality[node]["betweenness_centrality"] for node in nodes])
    axis.set_title("Betweenness centrality trong sub-network")
    path = figure_dir / "A16_centrality.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("A16", "Centrality mạng", path, "RQ5", "Aave là cầu nối cấu trúc trong topology nhỏ; không suy rộng toàn DeFi.", "MODELED_SUBNETWORK", "CORE"))

    delay_rows = read_json(rq_dir / "rq3_reaction_delay.json")["rows"]
    add_line(
        "A17", "reaction_delay_sensitivity", "RQ3: reaction delay và recovery time",
        [([row["delay_minutes"] for row in delay_rows], [row["time_to_recovery_seconds"] for row in delay_rows], "recovery seconds")],
        "seconds", "RQ3", "Recovery là first return sau breach; 0 nghĩa tolerance chưa từng bị vượt.",
        "SIMULATED_ON_REAL_MAINNET_STATE", "CORE",
    )
    capital_rows = read_json(rq_dir / "rq3_capital_constraint.json")["rows"]
    add_line(
        "A18", "binding_capital_sensitivity", "RQ3: liquidator capital constraint",
        [([row["capital_ratio"] for row in capital_rows], [row["total_liquidated_debt"] for row in capital_rows], "liquidated debt")],
        "USDC", "RQ3", "25% và 50% demand reference là binding; 100% và 200% không binding.",
        "SIMULATED_ON_REAL_MAINNET_STATE", "CORE",
    )
    usdc_rows = read_json(rq_dir / "rq5_usdc_depeg.json")["rows"]
    add_line(
        "A19", "usdc_depeg_hf", "RQ5: USDC price và số borrower dưới HF threshold",
        [
            ([row["usdc_price_usd"] for row in usdc_rows], [row["borrowers_hf_below_1_00"] for row in usdc_rows], "HF<1.00"),
            ([row["usdc_price_usd"] for row in usdc_rows], [row["borrowers_hf_below_1_20"] for row in usdc_rows], "HF<1.20"),
        ],
        "borrowers", "RQ5", "Upward USDC depeg weakens HF through debt valuation; downward depeg does the reverse.",
        "SIMULATED_DEBT_VALUATION_ONLY", "CORE",
    )
    lt_rows = read_json(rq_dir / "rq6_liquidation_threshold.json")["rows"]
    add_line(
        "A20", "lt_policy_sensitivity", "RQ6: liquidation-threshold sensitivity",
        [([row["liquidation_threshold"] for row in lt_rows], [row["total_liquidated_debt"] for row in lt_rows], "liquidated debt")],
        "USDC", "RQ6", "LT trực tiếp dịch Health Factor/liquidation boundary trong policy counterfactual.",
        "SIMULATED_POLICY_COUNTERFACTUAL", "CORE",
    )
    bonus_rows = read_json(rq_dir / "rq6_liquidation_bonus.json")["rows"]
    add_line(
        "A21", "liquidation_bonus_sensitivity", "RQ6: liquidation bonus và expected profit",
        [([row["liquidation_bonus"] for row in bonus_rows], [row["liquidator_expected_profit_usdc"] for row in bonus_rows], "expected profit")],
        "USDC", "RQ6", "Bonus đổi collateral seized và profitability path; không tạo thêm event trong range này.",
        "SIMULATED_POLICY_COUNTERFACTUAL", "CORE",
    )
    ltv_rows = read_json(rq_dir / "rq6_ltv_capital_efficiency.json")["rows"]
    add_line(
        "A22", "ltv_capital_efficiency", "RQ6: LTV và aggregate borrowing capacity",
        [([row["ltv_policy"] for row in ltv_rows], [row["aggregate_max_borrowing_capacity_usd"] for row in ltv_rows], "max capacity")],
        "USD", "RQ6", "LTV cao tăng ex-ante capacity; không được diễn giải là direct liquidation trigger.",
        "ANALYTICAL_POLICY_COUNTERFACTUAL", "CORE",
    )
    fig, axis = plt.subplots(figsize=(10, 5))
    axis.axis("off")
    axis.text(0.22, 0.65, "Terra 2022\npeg → redemption → issuance\n→ confidence", ha="center", va="center", bbox={"boxstyle": "round", "facecolor": "#f6d7c3"})
    axis.text(0.78, 0.65, "Aave × Uniswap\nprice → HF → liquidation\n→ DEX impact", ha="center", va="center", bbox={"boxstyle": "round", "facecolor": "#cfe8f3"})
    axis.text(0.5, 0.25, "Điểm chung hợp lệ: phản hồi phi tuyến và khuếch đại nội sinh\nKhông có kiểm định cơ chế chéo giữa hai thời kỳ", ha="center", va="center", bbox={"boxstyle": "round", "facecolor": "#e7e7e7"})
    axis.annotate("", xy=(0.42, 0.3), xytext=(0.27, 0.58), arrowprops={"arrowstyle": "->"})
    axis.annotate("", xy=(0.58, 0.3), xytext=(0.73, 0.58), arrowprops={"arrowstyle": "->"})
    path = figure_dir / "C01_cross_case_feedback.png"
    _save_figure(fig, path)
    figures.append(_figure_meta("C01", "Tổng hợp vòng phản hồi hai ca", path, "RQ1–RQ5", "Hai ca minh họa nguyên lý chung nhưng dùng dữ liệu và cơ chế riêng biệt.", "SYNTHESIS", "CORE"))
    for row in figures:
        if row["id"].startswith("T"):
            row["research_question"] = "Historical Validation Extension"
        elif row["id"] in {"A12", "A13", "A14", "A15", "A16"}:
            row["research_question"] = "Multilayer Network Analysis Extension"
        elif row["id"] == "C01":
            row["research_question"] = "Cross-case extension"
        elif row["id"] == "A03":
            row["research_question"] = "RQ2"
        elif row["id"] == "A11":
            row["research_question"] = "RQ2–RQ4"
        elif row["id"] == "A01":
            row["research_question"] = "RQ1/RQ5/RQ6"
    write_json(output_dir / "figure_registry.json", figures)
    return figures


def build_claims(registry: Registry) -> list[dict[str, Any]]:
    available = set(registry.values())
    claims = [
        ("C01", "Terra Historical Fit tái dựng được hướng biến động nhưng chạm các ngưỡng UST sớm hơn lịch sử.",
         ["TERRA_HF_UST_CORRELATION", "TERRA_TIMING_0_995", "TERRA_TIMING_0_9"], "PARTIALLY_SUPPORTED",
         "Fit có điều kiện; không phải dự báo ngoài mẫu."),
        ("C02", "Chỉ báo cutoff-safe không cảnh báo trước depeg ban đầu ở ngưỡng High Risk.",
         ["TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH", "TERRA_EW_LEAKAGE"], "SUPPORTED_NEGATIVE_FINDING",
         "Kết luận giới hạn ở định nghĩa chỉ báo và cutoff đã triển khai."),
        ("C03", "Chỉ báo cutoff-safe High Risk xuất hiện trước severe depeg UST dưới 0,90.",
         ["TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_9_HIGH"], "SUPPORTED",
         "Không đồng nghĩa dự báo khủng hoảng nói chung."),
        ("C04", "Native-swap event output hỗ trợ nhất quán kế toán gross mint swap_amount + fee_amount.",
         ["TERRA_MECH_EVENT_COUNT", "TERRA_MECH_DIRECT_CORRELATION", "TERRA_MECH_DIRECT_CUMULATIVE_ERROR"], "SUPPORTED",
         "Không chứng minh gross mint gây ra biến động giá."),
        ("C05", "Các preset stress Terra cho thấy regime bình thường và runaway khác nhau rõ rệt.",
         ["TERRA_STRESS_BASELINE_COLLAPSE_COUNT", "TERRA_STRESS_SEVERE_COLLAPSE_COUNT"], "MODEL_CONDITIONAL",
         "Tần suất đường mô phỏng không phải xác suất ngoài đời."),
        ("C06", "Snapshot Aave chính là REAL_MAINNET cùng block và không dùng Fixture làm bằng chứng chính.",
         ["AAVE_DATA_BLOCK_NUMBER", "AAVE_DATA_VERIFIED_BORROWERS", "AAVE_DATA_WETH_USDC_COHORT"], "SUPPORTED",
         "Cohort ứng viên không phải toàn bộ thị trường Aave."),
        ("C07", "Professor Demo cho thấy mức thanh lý và cascade theo chính giả định kịch bản đã đóng băng.",
         ["AAVE_DET_PROFESSOR_DEMO_TOTAL_LIQUIDATED_DEBT", "AAVE_DET_PROFESSOR_DEMO_CASCADE_DEPTH",
          "AAVE_DET_PROFESSOR_DEMO_WAVE_2_PLUS_LIQUIDATED_DEBT"], "MODEL_CONDITIONAL",
         "Không suy rộng thành dự báo Mainnet tương lai."),
        ("C08", "Độ nhạy Aave được đánh giá bằng sweep một yếu tố và bề mặt shock × liquidity.",
         [
             "AAVE_DET_PROFESSOR_DEMO_MAX_INTRAWAVE_LIQUIDATION_PRICE_IMPACT"
             if "AAVE_DET_PROFESSOR_DEMO_MAX_INTRAWAVE_LIQUIDATION_PRICE_IMPACT" in available
             else "AAVE_DET_PROFESSOR_DEMO_MAX_PRICE_IMPACT",
             "AAVE_DET_PROFESSOR_DEMO_BAD_DEBT",
         ], "MODEL_CONDITIONAL",
         "Association trong mô hình, không phải quan hệ nhân quả."),
        ("C09", "Tần suất cascade Monte Carlo có khoảng Wilson nhưng vẫn là tần suất lấy mẫu trong mô hình.",
         ["AAVE_MC_PROFESSOR_DEMO_CASCADE_FREQUENCY", "AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_LOWER",
          "AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_UPPER"], "MODEL_CONDITIONAL",
         "Không gọi là xác suất thực tế."),
        ("C10", "Centrality chỉ mô tả vai trò cầu nối trong sub-network Aave–Uniswap nhỏ.", ["NETWORK_AAVE_BETWEENNESS"], "SUPPORTED_WITH_BOUNDARY",
         "Không đại diện tầm quan trọng hệ thống trên toàn DeFi."),
        ("C11", "Terra không định lượng kiểm chứng cơ chế Aave và Aave không chứng minh cơ chế Terra.", ["CROSS_CASE_SYNTHESIS_BOUNDARY"],
         "SUPPORTED_BOUNDARY", "Tổng hợp chéo chỉ ở mức phản hồi phi tuyến và khuếch đại nội sinh."),
        ("C12", "Mô hình dự báo được chính xác vụ sụp đổ Terra.", ["TERRA_TIMING_0_995", "TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH"], "UNSUPPORTED",
         "Strict OOS âm và cảnh báo depeg ban đầu muộn; không được sử dụng claim này."),
        ("C13", "Recovery time dùng first-return semantics; 0 nghĩa spread chưa từng breach tolerance.",
         ["RQ3_DELAY_STATUS", "RQ3_DELAY_0_TIME_TO_RECOVERY_SECONDS", "RQ3_DELAY_4_TIME_TO_RECOVERY_SECONDS"],
         "MODEL_CONDITIONAL", "Canonical snapshot và Professor Demo; không khái quát ngoài 0–4 bước."),
        ("C14", "Liquidator capital 25% và 50% demand reference là binding; 100% và 200% không binding.",
         ["RQ3_REQUIRED_CAPITAL_REFERENCE", "RQ3_CAPITAL_0_25_TOTAL_LIQUIDATED_DEBT",
          "RQ3_CAPITAL_0_5_TOTAL_LIQUIDATED_DEBT", "RQ3_CAPITAL_1_0_TOTAL_LIQUIDATED_DEBT",
          "RQ3_CAPITAL_2_0_TOTAL_LIQUIDATED_DEBT"], "MODEL_CONDITIONAL",
         "Capital là funding cộng dồn không tái sử dụng theo engine hiện tại."),
        ("C15", "USDC upward depeg làm HF yếu hơn còn downward depeg làm HF mạnh hơn qua debt valuation.",
         ["RQ5_USDC_BASELINE_COMPATIBLE", "RQ5_USDC_1_1_BORROWERS_HF_BELOW_1_00",
          "RQ5_USDC_1_0_BORROWERS_HF_BELOW_1_00", "RQ5_USDC_0_9_BORROWERS_HF_BELOW_1_20"],
         "MODEL_CONDITIONAL", "This experiment isolates the USDC debt-valuation channel."),
        ("C16", "LTV cao hơn tăng ex-ante borrowing capacity nhưng giảm origination safety buffer.",
         ["RQ6_LTV_0_755_AGGREGATE_MAX_BORROWING_CAPACITY_USD",
          "RQ6_LTV_0_825_AGGREGATE_MAX_BORROWING_CAPACITY_USD"], "MODEL_CONDITIONAL",
         "Above counterfactual capacity không đồng nghĩa liquidatable; frozen debt không đổi."),
        ("C17", "Liquidation Threshold trực tiếp dịch Health Factor và liquidation boundary.",
         ["RQ6_LT_0_83_TOTAL_LIQUIDATED_DEBT", "RQ6_LT_0_855_TOTAL_LIQUIDATED_DEBT"],
         "MODEL_CONDITIONAL", "WETH override không gán lại threshold của other collateral."),
        ("C18", "Liquidation bonus thay đổi collateral seized và liquidator expected profit trong tested range.",
         ["RQ6_BONUS_STATUS", "RQ6_BONUS_1_03_COLLATERAL_SEIZED_WETH",
          "RQ6_BONUS_1_07_COLLATERAL_SEIZED_WETH"], "MODEL_CONDITIONAL",
         "Kết quả policy counterfactual; không suy ra execution behavior ngoài mô hình."),
    ]
    rows = []
    for claim_id, statement, result_ids, status, boundary in claims:
        missing = sorted(set(result_ids).difference(available))
        if missing:
            raise ValueError(f"claim {claim_id} references missing result IDs: {missing}")
        rows.append(
            {
                "claim_id": claim_id,
                "statement_vi": statement,
                "result_ids": result_ids,
                "status": status,
                "claim_boundary": boundary,
                "allowed_wording": statement,
                "prohibited_wording": (
                    "Không được bỏ claim boundary, nâng model-implied thành observed fact, hoặc khái quát ngoài "
                    "snapshot/range đã thử."
                ),
                "evidence_type": "OBSERVED" if claim_id in {"C02", "C04", "C06"} else "DERIVED_OR_SIMULATED",
            }
        )
    unsupported_evidence = [row for row in rows if row["status"] in EVIDENCE_REQUIRED_STATUSES and not row["result_ids"]]
    if unsupported_evidence:
        raise ValueError(
            "supported claims require result IDs: "
            + ", ".join(row["claim_id"] for row in unsupported_evidence)
        )
    return rows


def _fmt(value: Any, digits: int = 4) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if abs(value) >= 1_000_000:
            return f"{value:,.2f}"
        return f"{value:.{digits}g}"
    return str(value)


def generate_documents_legacy(
    output_dir: Path,
    docs_dir: Path,
    registry: Registry,
    claims: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    figures: list[dict[str, Any]],
    terra_quality: dict[str, Any],
    aave_quality: dict[str, Any],
    preflight: dict[str, Any],
) -> dict[str, list[str]]:
    docs_dir.mkdir(parents=True, exist_ok=True)
    values = registry.values()

    def v(key: str) -> str:
        return _fmt(values[key])

    professor = {
        key: values[f"AAVE_DET_PROFESSOR_DEMO_{key}"]
        for key in ("TOTAL_LIQUIDATED_DEBT", "BAD_DEBT", "CASCADE_DEPTH", "WAVE_1_LIQUIDATED_DEBT", "WAVE_2_PLUS_LIQUIDATED_DEBT", "LATER_WAVE_SHARE")
    }
    core_findings = f"""
1. Historical Fit Terra đạt UST RMSE {v('TERRA_HF_UST_RMSE')} và tương quan {v('TERRA_HF_UST_CORRELATION')}, nhưng sai số thời điểm tại ngưỡng 0,995 là {v('TERRA_TIMING_0_995')} giờ (dấu âm nghĩa là mô phỏng sớm); do đó bằng chứng chỉ hỗ trợ tái dựng có điều kiện, không hỗ trợ claim dự báo chính xác.
2. Cảnh báo cutoff-safe High Risk cho ngưỡng 0,995 có lead time {v('TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH')} giờ: cảnh báo xuất hiện sau depeg ban đầu. Với ngưỡng 0,90, lead time là {v('TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_9_HIGH')} giờ.
3. Kiểm tra {v('TERRA_MECH_EVENT_COUNT')} native swaps hỗ trợ identity `swap_amount + fee_amount`; đây là nhất quán kế toán, không phải bằng chứng nhân quả giá.
4. Snapshot Aave REAL_MAINNET tại block {v('AAVE_DATA_BLOCK_NUMBER')} xác minh {v('AAVE_DATA_VERIFIED_BORROWERS')} borrower; cohort WETH/USDC là {v('AAVE_DATA_WETH_USDC_COHORT')}. Tỷ lệ xác minh ứng viên không được gọi là độ phủ thị trường.
5. Professor Demo tạo tổng nợ thanh lý {_fmt(professor['TOTAL_LIQUIDATED_DEBT'])}, nợ xấu {_fmt(professor['BAD_DEBT'])}, cascade depth {_fmt(professor['CASCADE_DEPTH'])}; Wave 2+ là {_fmt(professor['WAVE_2_PLUS_LIQUIDATED_DEBT'])}. Đây là kết quả model-implied.
6. Monte Carlo Professor Demo có tần suất cascade {v('AAVE_MC_PROFESSOR_DEMO_CASCADE_FREQUENCY')}, khoảng Wilson 95% [{v('AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_LOWER')}, {v('AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_UPPER')}]. Khoảng này chỉ mô tả lấy mẫu trong mô hình.
""".strip()
    limitations = """
- Terra không có độ sâu DEX lịch sử canonical và không có kênh can thiệp LFG quan sát được.
- Dữ liệu bridge bị quarantine; giá tháng 3–4 có giai đoạn carry-forward tần suất thấp.
- Historical Fit sai thời điểm và cảnh báo cutoff-safe muộn đối với depeg ban đầu.
- Chuyển đổi phản thực Terra có sai số; preset Severe chạm numerical floors nên chỉ biểu diễn runaway regime.
- Aave dùng sample ứng viên, trọng tâm WETH/USDC và một venue Uniswap V3 được chọn; không phải toàn thị trường.
- Centrality được tính trên topology nhỏ; protocol tương lai chưa được ingest.
- Monte Carlo và mọi kết quả stress phụ thuộc cấu trúc mô hình, phân phối nhiễu và giả định kịch bản.
""".strip()
    rq = """
## Đề xuất chuẩn hóa câu hỏi nghiên cứu từ mô hình hiện tại

- RQ1: Cú sốc giá tài sản thế chấp tạo vòng thanh lý giữa Aave V3 và Uniswap V3 như thế nào?
- RQ2: Thanh khoản DEX, năng lực liquidator và arbitrage ảnh hưởng đến khuếch đại rủi ro ra sao?
- RQ3: Mô hình phản hồi tái dựng được và chưa tái dựng tốt đặc điểm nào của Terra 2022?
- RQ4: Chỉ báo cutoff-safe có cảnh báo trước severe depeg hay không?
- RQ5: Mạng đa lớp cho thấy kênh truyền dẫn và node cầu nối nào trong sub-network Aave–Uniswap?
""".strip()
    method = f"""# PHƯƠNG PHÁP NGHIÊN CỨU

{rq}

## Thiết kế hai ca

Terra là ca lịch sử dùng dữ liệu giờ từ {terra_quality['start_timestamp']} đến {terra_quality['end_timestamp']}, gồm {terra_quality['row_count']} timestamp và {terra_quality['native_swaps']['rows']} native swaps. Aave–Uniswap là ca stress hiện đại dùng snapshot REAL_MAINNET cùng block {aave_quality['block_number']}. Hai ca không được xem là cùng thời điểm và không kiểm chứng cơ chế lẫn nhau.

## Phân lớp bằng chứng

- **Quan sát:** giá, state protocol, event extract và trạng thái pool có provenance.
- **Suy dẫn:** Health Factor kiểm tra lại, độ sâu, điểm cảnh báo, centrality và ma trận chuẩn hóa.
- **Mô phỏng:** liquidation waves, bad debt, price impact và stress paths.
- **Phản thực:** các preset và sweep thay đổi shock, thanh khoản, gas, arbitrage, liquidator.

## Terra

Historical Fit được hiệu chỉnh trên luồng lịch sử quan sát và được gọi là tái dựng có điều kiện, không phải forecast. Early Warning gồm retrospective và cutoff-safe; kiểm tra future perturbation yêu cầu dữ liệu sau cutoff không làm thay đổi điểm trước cutoff. Mechanism Check dùng gross mint trực tiếp `swap_amount + fee_amount`. Stress Test giữ mapping tham số đã đóng băng rồi thay đổi giả định preset.

## Aave–Uniswap

The Graph chỉ phục vụ discovery trong snapshot gốc; state cuối cùng được xác minh bằng Ethereum RPC cùng block. `Pool.getUserAccountData` là chuẩn đối chiếu Health Factor. WETH chỉ được tính collateral khi `usageAsCollateralEnabled=true`. Engine hiện hữu mô phỏng shock → HF → liquidator → forced WETH sale → Uniswap price impact → tái định giá; arbitrage là agent ổn định theo capacity giả định.

## Monte Carlo và độ bền

Mỗi kịch bản research dùng {read_json(output_dir / 'aave/monte_carlo.json')['runs_per_scenario']} lần chạy do benchmark thời gian đã ghi; seed chính 20260914 và kiểm tra seed 20260915–20260916. Tần suất cascade và Wilson interval là thống kê lấy mẫu có điều kiện trên mô hình, không phải xác suất ngoài đời. Sweep một yếu tố và grid 8×4 không tạo suy luận nhân quả.

## Mạng đa lớp

Đồ thị chỉ chứa node và cạnh có nguồn từ snapshot, engine hoặc giả định kịch bản. Điểm cạnh chuẩn hóa, ma trận contagion và centrality chỉ có nghĩa trong sub-network này. Compound, Maker và Curve không được đưa vào metric khi chưa ingest dữ liệu.

## Tái lập

Lệnh chuẩn: `{REPRODUCE_COMMAND}`. Hash input/output, phiên bản, seed, scenario và kết quả kiểm tra được ghi trong manifest và preflight.
"""
    results = f"""# KẾT QUẢ VÀ THẢO LUẬN

## 5.1 Độ tin cậy dữ liệu — Table_01, Table_02; T01, A01

Terra và Aave được đóng băng bằng hash. Aave có {v('AAVE_DATA_CANDIDATES_DISCOVERED')} ứng viên và {v('AAVE_DATA_VERIFIED_BORROWERS')} borrower xác minh, tương ứng tỷ lệ ứng viên {v('AAVE_DATA_CANDIDATE_VERIFICATION_RATE')}; đây không phải độ phủ thị trường. Terra giữ missingness theo availability thay vì điền unavailable thành zero.

## 5.2 Cơ chế Terra — Table_12; T11

{v('TERRA_MECH_EVENT_COUNT')} event hỗ trợ identity gross mint trực tiếp. Tương quan theo giờ là {v('TERRA_MECH_DIRECT_CORRELATION')} và sai số tích lũy tương đối {v('TERRA_MECH_DIRECT_CUMULATIVE_ERROR')}. Kết quả là accounting consistency, không phải price causality.

## 5.3 Historical Fit Terra — Table_10; T05–T07

{core_findings.splitlines()[0]}

## 5.4 Early Warning — Table_11; T08–T09

{core_findings.splitlines()[1]}

## 5.5 Stress phản thực Terra — Table_13; T10

Baseline có {v('TERRA_STRESS_BASELINE_COLLAPSE_COUNT')} đường chạm điều kiện collapse; Severe có {v('TERRA_STRESS_SEVERE_COLLAPSE_COUNT')}. Cách viết đúng là số đường mô phỏng đạt điều kiện, không phải xác suất crash thực tế. Severe chạm floor biểu diễn runaway regime, không phải dự báo tail chính xác.

## 5.6 Vulnerability Aave Mainnet — Table_02–Table_04; A01–A03

Snapshot block {v('AAVE_DATA_BLOCK_NUMBER')} có cohort WETH/USDC {v('AAVE_DATA_WETH_USDC_COHORT')}. Sai khác HF lớn nhất được giữ ở mức {v('AAVE_HF_MAX_ABSOLUTE_ERROR')}; cờ mismatch không bị che hoặc loại borrower thủ công.

## 5.7 Cascade lending–DEX — Table_04; A04–A08

Professor Demo có Wave 1 {_fmt(professor['WAVE_1_LIQUIDATED_DEBT'])} và Wave 2+ {_fmt(professor['WAVE_2_PLUS_LIQUIDATED_DEBT'])}. Nếu Wave 2+ bằng zero, kết luận là **NO ENDOGENOUS SECOND WAVE**.

## 5.8 Thanh khoản như kênh khuếch đại — Table_05, Table_07; A07–A08

Grid rời rạc đánh giá shock từ −5% đến −40% và haircut 0/25/50/75%. Chỉ báo ngưỡng không được nội suy ngoài các cell thử.

## 5.9 Arbitrage như cơ chế ổn định — Table_05; A11

Sweep arbitrage so sánh capacity trong khi giữ các giả định khác. Đây là phản ứng mô hình, không chứng minh arbitrage quan sát được đã gây ổn định lịch sử.

## 5.10 Monte Carlo tail behavior — Table_06; A09–A10

{core_findings.splitlines()[5]}

## 5.11 Mạng contagion đa lớp — Table_08–Table_09; A12–A16

Aave có vai trò cầu nối cấu trúc giữa exposure và execution venue trong topology đã mô hình hóa. Centrality không phải “tầm quan trọng hệ thống toàn DeFi”; score ma trận không phải xác suất.

## 5.12 Độ bền và độ nhạy — Table_05, Table_14; T12, A11

Strict OOS âm được giữ nguyên. Conditional replay, rolling origin, ablation, parameter uncertainty và seed robustness bổ sung kiểm tra nhưng không biến fit thành forecast.

## 5.13 Tổng hợp hai ca — Table_15; C01

Điểm chung hợp lệ là vòng phản hồi phi tuyến và khuếch đại nội sinh. Terra không định lượng xác thực engine Aave; snapshot Aave 2026 không chứng minh cơ chế Terra 2022.

## 5.14 Mô hình có thể và không thể thiết lập

Mô hình có thể tái lập stress có điều kiện, kiểm tra consistency, so sánh scenario và làm rõ kênh truyền dẫn. Mô hình không thiết lập causal effect lịch sử, xác suất khủng hoảng thực tế, forecast chính xác hoặc systemic importance toàn DeFi.
"""
    abstract = f"""# DỰ THẢO TÓM TẮT

Nghiên cứu xây dựng một quy trình kiểm định sức chịu đựng DeFi có thể tái lập bằng hai ca bổ sung nhưng không đồng nhất: Terra Classic tháng 5/2022 để kiểm tra tái dựng lịch sử, cảnh báo sớm và cơ chế phát hành; Aave V3 × Uniswap V3 để mô phỏng thanh lý dây chuyền trên snapshot Ethereum Mainnet. Dữ liệu Terra gồm {v('TERRA_ROWS')} giờ và {v('TERRA_SWAPS')} native swaps; ca Aave dùng {v('AAVE_DATA_VERIFIED_BORROWERS')} borrower xác minh tại block {v('AAVE_DATA_BLOCK_NUMBER')}.

Historical Fit Terra đạt UST RMSE {v('TERRA_HF_UST_RMSE')}, nhưng sai số timing tại ngưỡng 0,995 là {v('TERRA_TIMING_0_995')} giờ (mô phỏng sớm). Chỉ báo cutoff-safe High Risk có lead time {v('TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH')} giờ, tức xuất hiện sau depeg ban đầu, nên không hỗ trợ claim dự báo sớm sự kiện này; ngược lại, nó đi trước severe depeg 0,90 khoảng {v('TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_9_HIGH')} giờ. Bằng chứng transaction hỗ trợ nhất quán kế toán gross issuance nhưng không xác lập nhân quả giá.

Trong ca Aave, Professor Demo tạo nợ thanh lý {_fmt(professor['TOTAL_LIQUIDATED_DEBT'])} và cascade depth {_fmt(professor['CASCADE_DEPTH'])}. Monte Carlo cho tần suất cascade model-implied {v('AAVE_MC_PROFESSOR_DEMO_CASCADE_FREQUENCY')} với khoảng Wilson [{v('AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_LOWER')}, {v('AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_UPPER')}]. Các kết quả này phụ thuộc snapshot, giả định và engine; chúng không phải xác suất thị trường.

Đóng góp chính là kiến trúc evidence-first liên kết dữ liệu, mô hình, bảng, hình và claim ledger. Hạn chế gồm availability Terra, single-venue Aave/Uniswap, sample borrower, topology nhỏ và model dependence. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]
"""
    executive = f"""# TÓM TẮT ĐIỀU HÀNH

## Các phát hiện mạnh nhất

{core_findings}

## Các hạn chế mạnh nhất

{limitations}

Mọi số liệu trên ánh xạ tới `results_registry.json`; các claim ánh xạ tới `claim_ledger.json` và `document_claim_index.json`.
"""
    final_report = f"""# NỀN TẢNG BÁO CÁO NGHIÊN CỨU CUỐI CÙNG

## TÓM TẮT

{abstract.split('# DỰ THẢO TÓM TẮT', 1)[1].strip()}

# 1. GIỚI THIỆU

## 1.1 Bối cảnh

DeFi kết nối tín dụng, thanh khoản và định giá bằng hợp đồng thông minh; vì vậy cú sốc có thể lan qua vòng phản hồi. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

## 1.2 Vấn đề, mục tiêu và đóng góp

Mục tiêu là tách dữ liệu quan sát khỏi metric suy dẫn và kết quả mô phỏng, đồng thời giữ bằng chứng âm. Đóng góp là pipeline evidence-first, không phải một tuyên bố dự báo phổ quát.

{rq}

# 2. CƠ SỞ LÝ THUYẾT VÀ KHUNG RỦI RO

Các chủ đề DeFi, lending, DEX, stablecoin, liquidation, liquidity, contagion, agent-based modeling và multilayer graph cần được neo bằng tài liệu học thuật. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

# 3. DỮ LIỆU VÀ PHƯƠNG PHÁP

Xem `METHODOLOGY.md`. Thiết kế phân biệt quan sát, suy dẫn, mô phỏng và phản thực; snapshot Aave cùng block; Early Warning cutoff-safe; kiểm tra fixed-seed reproducibility.

# 4. MÔ HÌNH

Vòng Aave–Uniswap đi từ shock giá tới HF, thanh lý, bán WETH, price impact và tái định giá; arbitrage/liquidator bị giới hạn bởi capacity. Vòng Terra đi từ peg stress tới redemption, issuance, dilution và confidence. Agent là vai trò mô phỏng, không phải danh tính thực.

# 5. KẾT QUẢ

{results.split('# KẾT QUẢ VÀ THẢO LUẬN', 1)[1].strip()}

# 6. THẢO LUẬN

Hai ca hỗ trợ cách nghiên cứu feedback-driven stress bằng provenance và claim boundary. Chúng không tạo một phép kiểm định chéo định lượng. Kết quả âm về timing và early warning là phần cốt lõi của tính phòng thủ khoa học.

# 7. HẠN CHẾ

{limitations}

# 8. HƯỚNG NGHIÊN CỨU TIẾP THEO

Mở rộng borrower/protocol, thêm venue execution, ingest bridge/LFG khi có nguồn canonical, kiểm định calibration ngoài mẫu và so sánh topology theo thời gian.

# 9. KẾT LUẬN

Package này cung cấp một chuỗi tái lập từ input hash đến claim. Kết luận mạnh nhất là về cơ chế mô hình và tính minh bạch bằng chứng, không phải khả năng tiên tri khủng hoảng.

# PHỤ LỤC

Xem `TABLE_FIGURE_INDEX.md`, `EVIDENCE_CLAIM_MATRIX.md`, `REPRODUCIBILITY.md` và các registry máy đọc được.
"""
    data_quality = f"""# CHẤT LƯỢNG DỮ LIỆU

## Terra

- Coverage: {terra_quality['start_timestamp']} → {terra_quality['end_timestamp']}, {terra_quality['row_count']} giờ.
- Native swaps: {terra_quality['native_swaps']['rows']} rows, hash `{terra_quality['native_swaps']['sha256']}`.
- Các trường unavailable được giữ missing, không đổi thành observed zero.
- Anchor event flow và native issuance có availability window; March–April price có carry-forward chất lượng thấp.
- DEX depth, LFG defense và bridge flow không được nâng cấp thành dữ liệu quan sát khi chưa có nguồn.

## Aave–Uniswap

- Mode: {aave_quality['mode']}; chain {aave_quality['chain_id']}; block {aave_quality['block_number']}.
- Candidate: {aave_quality['candidates_discovered']}; verified: {aave_quality['verified_borrowers']}; failed reads: {aave_quality['failed_reads']}.
- WETH collateral: {aave_quality['weth_collateral_borrowers']}; USDC debt: {aave_quality['usdc_borrowers']}; joint cohort: {aave_quality['weth_usdc_cohort']}.
- Candidate verification rate: {_fmt(aave_quality['candidate_verification_rate'])}; đây **không phải market coverage**.
- HF max absolute error: {_fmt(aave_quality['health_factor_validation']['max_absolute_error'])}; quality flags được giữ lại.
- Pool fee tier: {aave_quality['uniswap']['fee']}; ticks: {aave_quality['uniswap']['tick_count']}; depth 2%: {_fmt(aave_quality['uniswap']['depth_usdc_2pct'])} USDC.
"""
    limitations_doc = f"# HẠN CHẾ\n\n{limitations}\n\nCác boundary này có hiệu lực cho mọi bảng, hình và bài thuyết trình.\n"
    reproducibility = f"""# TÁI LẬP

## Lệnh chuẩn

```powershell
{REPRODUCE_COMMAND}
```

## Provenance

- Source code commit: `{git('rev-parse', 'HEAD')}`
- Artifact bundle commit: được điền sau commit bundle bằng bước finalization, không tự tham chiếu giả.
- Canonical Aave: `{CANONICAL_SNAPSHOT.as_posix()}`; SHA-256 `{aave_quality['sha256']}`.
- Canonical Terra: `{EXTENDED_DATASET.as_posix()}`; SHA-256 `{terra_quality['sha256']}`.
- Native swaps: `{NATIVE_SWAPS.as_posix()}`; SHA-256 `{terra_quality['native_swaps']['sha256']}`.
- Python: `{preflight['python'].splitlines()[0]}`; Node: `{preflight['node']}`.
- Seeds: 20260914, 20260915, 20260916; Terra fixed seeds nằm trong manifest con.
- Pipeline mode: research; Aave MC runs/scenario: {read_json(output_dir / 'aave/monte_carlo.json')['runs_per_scenario']}.

`manifest.json` chứa hash output. Deterministic Professor Demo và Monte Carlo fixed-seed được chạy hai lần và phải identical.
"""
    literature = """# KHOẢNG TRỐNG TÀI LIỆU CẦN BỔ SUNG

Không có tác giả/năm/DOI nào được tạo tự động. Bản luận văn cần bổ sung nguồn học thuật đã kiểm tra cho:

- contagion và systemic risk trong DeFi;
- cơ chế Aave V3, Health Factor và liquidation;
- AMM/Uniswap V3 liquidity và price impact;
- agent-based financial modeling;
- multilayer network và centrality;
- lịch sử khủng hoảng Terra/LUNA;
- thiết kế early-warning và kiểm định ngoài mẫu;
- Monte Carlo uncertainty và Wilson interval;
- giới hạn suy luận nhân quả từ simulation.
"""
    future = """# HƯỚNG NGHIÊN CỨU TIẾP THEO

1. Mở rộng Aave sang nhiều collateral/debt pair và kiểm tra toàn bộ reserve.
2. Ingest Compound, Maker và nhiều DEX bằng nguồn cùng block trước khi đưa vào network metrics.
3. Xây dựng time-varying liquidity và multi-venue routing.
4. Bổ sung bridge/LFG/DEX lịch sử Terra khi có dữ liệu canonical, không backfill bằng giả định.
5. Tách calibration/validation dài hơn và benchmark forecast nghiêm ngặt.
6. Ước lượng uncertainty tham số từ dữ liệu thay vì chỉ range policy.
7. Thực hiện causal design riêng nếu mục tiêu chuyển từ stress mechanism sang tác động lịch sử.
"""
    presentation_sections = [
        ("1. Vấn đề", "C01", "DeFi có vòng phản hồi; mục tiêu là đo stress có provenance.", "Từ vấn đề, chuyển sang thiết kế hai ca."),
        ("2. Thiết kế", "C01", "Terra là historical validation; Aave là Mainnet stress.", "Hai ca bổ sung nhưng không xác thực lẫn nhau."),
        ("3. Dữ liệu", "T01 + A01", f"{v('TERRA_ROWS')} giờ Terra; {v('AAVE_DATA_VERIFIED_BORROWERS')} borrower Aave.", "Tiếp theo là cơ chế Aave."),
        ("4. Vòng Aave", "A12", "shock → HF → liquidation → DEX → repricing.", "Cơ chế này được chạy trên snapshot cùng block."),
        ("5. Terra lịch sử", "T01", "Quan sát collapse nhưng không gọi fit là forecast.", "Đầu tiên kiểm tra mechanism."),
        ("6. Mechanism", "T11", f"{v('TERRA_MECH_EVENT_COUNT')} swaps; accounting consistency.", "Sau đó đánh giá Historical Fit."),
        ("7. Historical Fit", "T05", f"UST RMSE {v('TERRA_HF_UST_RMSE')}; timing sớm.", "Fit tốt về hướng chưa đủ cho cảnh báo."),
        ("8. Early Warning", "T09", f"Initial depeg lead {v('TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH')} giờ.", "Chuyển sang stress Aave."),
        ("9. Aave stress", "A04", f"Professor liquidated {_fmt(professor['TOTAL_LIQUIDATED_DEBT'])}.", "Thanh khoản quyết định vòng khuếch đại."),
        ("10. Contagion graph", "A12–A16", "Aave là bridge trong sub-network nhỏ.", "Độ bền cần MC và sensitivity."),
        ("11. MC/sensitivity", "A09 + A11", f"Cascade frequency {v('AAVE_MC_PROFESSOR_DEMO_CASCADE_FREQUENCY')} model-implied.", "Tổng hợp phát hiện."),
        ("12. Phát hiện", "C01", "Phản hồi nội sinh là điểm chung hợp lệ.", "Nhưng boundary là bắt buộc."),
        ("13. Hạn chế", "Table_14", "Availability, sample, venue, topology, model dependence.", "Kết luận ở mức phòng thủ được."),
        ("14. Kết luận", "C01", "Evidence-first, reproducible, giữ kết quả âm.", "Mời hội đồng đặt câu hỏi."),
    ]
    presentation = "# BRIEF THUYẾT TRÌNH 10–12 PHÚT\n\n" + "\n\n".join(
        f"## {title}\n\n- Mục đích: {finding}\n- Màn hình/hình: {visual}\n- Điểm nói: claim có boundary; không suy rộng ngoài dữ liệu.\n- Chuyển ý: {transition}"
        for title, visual, finding, transition in presentation_sections
    ) + "\n"
    script = f"""# KỊCH BẢN BẢO VỆ 10 PHÚT

Kính thưa Hội đồng, nghiên cứu này bắt đầu từ câu hỏi: khi các giao thức DeFi nối tín dụng với thanh khoản, một cú sốc có thể tự khuếch đại như thế nào? Em không cố xây dựng một mô hình dự báo giá vạn năng. Em xây dựng một pipeline evidence-first, trong đó mọi con số đều quay lại được artifact và source hash.

Thiết kế có hai ca. Terra tháng 5/2022 là ca lịch sử để kiểm tra cơ chế, Historical Fit và Early Warning. Aave V3 × Uniswap V3 là ca stress hiện đại trên snapshot REAL_MAINNET block {v('AAVE_DATA_BLOCK_NUMBER')}. Hai ca không cùng thời điểm và Terra không xác thực định lượng Aave.

Về dữ liệu, Terra có {v('TERRA_ROWS')} giờ và {v('TERRA_SWAPS')} native swaps. Aave có {v('AAVE_DATA_VERIFIED_BORROWERS')} borrower xác minh và cohort WETH/USDC {v('AAVE_DATA_WETH_USDC_COHORT')}. Tỷ lệ xác minh ứng viên không phải độ phủ toàn thị trường.

Đối với Terra, identity gross issuance được kiểm tra trực tiếp bằng `swap_amount + fee_amount`. Kết quả hỗ trợ nhất quán kế toán, nhưng em không diễn giải thành bằng chứng minting gây sụp giá. Historical Fit đạt UST RMSE {v('TERRA_HF_UST_RMSE')}, song sai số timing tại ngưỡng 0,995 là {v('TERRA_TIMING_0_995')} giờ, nghĩa là mô phỏng chạm ngưỡng sớm.

Kết quả này không cho thấy mô hình dự báo được cú depeg ban đầu. Cảnh báo cutoff-safe High Risk có lead time {v('TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH')} giờ tại ngưỡng 0,995, tức là muộn; ở severe depeg 0,90, lead time là {v('TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_9_HIGH')} giờ. Đây là bằng chứng âm cần giữ lại.

Ở Aave, vòng mô phỏng là shock giá, giảm HF, liquidator trả nợ và thu collateral, bán WETH vào Uniswap, price impact rồi tái định giá. Professor Demo tạo nợ thanh lý {_fmt(professor['TOTAL_LIQUIDATED_DEBT'])} và Wave 2+ {_fmt(professor['WAVE_2_PLUS_LIQUIDATED_DEBT'])}. Nếu số sau bằng zero, kết luận đúng là không có second wave nội sinh.

Monte Carlo cho tần suất cascade {v('AAVE_MC_PROFESSOR_DEMO_CASCADE_FREQUENCY')} với Wilson [{v('AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_LOWER')}, {v('AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_UPPER')}]. Em nhấn mạnh: đây là tần suất lấy mẫu trong mô hình, không phải xác suất khủng hoảng thực tế.

Mạng đa lớp giúp nhìn đường truyền exposure, liquidation, price impact và stabilization. Aave là bridge trong topology nhỏ này; centrality không đại diện toàn bộ DeFi và điểm 0,8 không phải xác suất 80%.

Đóng góp chính là một quy trình tái lập từ data quality tới claim ledger, figures và defense package. Hạn chế quan trọng là dữ liệu Terra còn unavailable, sample Aave không phải toàn thị trường, một venue Uniswap, topology nhỏ và model dependence.

Kết luận, nghiên cứu cho thấy cách phân tích phản hồi phi tuyến một cách có boundary. Giá trị của nó nằm ở khả năng audit và giữ cả kết quả không thuận lợi, chứ không ở một lời hứa dự báo chắc chắn. Em xin cảm ơn Hội đồng.
"""
    qa_pairs = [
        ("Vì sao Terra và Aave cùng một nghiên cứu?", "Chúng là hai ca khác nhau cho cùng workflow nghiên cứu feedback-driven stress; không phải một ca xác thực ca kia."),
        ("Terra có validate Aave không?", "Không. Terra kiểm tra workflow lịch sử; Aave kiểm tra cơ chế lending–DEX riêng trên Mainnet."),
        ("Vì sao không chỉ dự báo giá?", "Mục tiêu là cơ chế truyền stress, liquidation và liquidity; dự báo giá không quan sát trực tiếp các kênh này."),
        ("Vì sao ABM?", "ABM biểu diễn vai trò borrower, liquidator và arbitrage theo sequence; kết quả vẫn phụ thuộc đặc tả."),
        ("Vì sao Monte Carlo?", "Để mô tả biến thiên trong mô hình dưới nhiễu có seed, không để ước lượng xác suất thực tế."),
        ("Vì sao Health Factor?", "Đó là điều kiện protocol trực tiếp liên hệ collateral, debt và liquidation threshold."),
        ("Vì sao Uniswap V3?", "Snapshot có state/ticks cùng block và đây là venue execution được chứng minh; không khẳng định duy nhất trên thị trường."),
        ("Wave 2 hình thành thế nào?", "Price impact sau Wave 1 làm thêm vị thế xuống dưới ngưỡng và bị thanh lý ở wave sau."),
        ("Cascade amplification là gì?", "Tỷ lệ model metric giữa tổng thanh lý và direct shock; định nghĩa cụ thể nằm trong engine/artifact."),
        ("Centrality có nghĩa gì?", "Vai trò topology trong sub-network mô hình hóa, không phải tổng systemic importance."),
        ("Vì sao Aave là bridge?", "Trong topology này, Aave nối exposure borrower/assets với liquidation route tới DEX."),
        ("Score ma trận 0,8 là xác suất 80%?", "Không. Đó là normalized strength theo policy của graph."),
        ("MC cascade frequency là probability?", "Không. Là sampling frequency có điều kiện trên model/scenario và số run."),
        ("Mô hình dự báo Terra crash được không?", "Không có bằng chứng hỗ trợ; strict OOS âm và initial-depeg warning muộn."),
        ("Historical Fit có overfit không?", "Có rủi ro vì conditioning/calibration; vì vậy được gọi là fit, không phải forecast."),
        ("Vì sao collapse bắt đầu quá sớm?", "Feedback calibration tái dựng hướng nhưng không nhận dạng chính xác timing; sai số được công bố."),
        ("Vì sao thiếu Terra DEX depth?", "Không có nguồn archival canonical được cấu hình/đóng băng; pipeline giữ UNAVAILABLE thay vì bịa."),
        ("Vì sao không có Compound/Maker/Curve?", "Chưa ingest dữ liệu evidence-backed cùng scope; node khái niệm không được dùng trong scientific metrics."),
        ("Hạn chế quan trọng nhất?", "Availability Terra, sample/venue Aave, topology nhỏ, scenario và model dependence."),
        ("Nếu có thêm thời gian?", "Mở rộng multi-protocol/multi-venue, time-varying data và validation ngoài mẫu."),
        ("Ứng dụng thực tiễn?", "Hỗ trợ scenario comparison, provenance audit và thảo luận kênh truyền stress; không phải lời khuyên đầu tư."),
    ]
    qa = "# HỎI–ĐÁP HỘI ĐỒNG\n\n" + "\n\n".join(f"## {index}. {question}\n\n{answer}" for index, (question, answer) in enumerate(qa_pairs, 1)) + "\n"
    evidence_matrix = "# MA TRẬN BẰNG CHỨNG–CLAIM\n\n" + _md_table([
        {"claim_id": row["claim_id"], "statement": row["statement_vi"], "result_ids": ", ".join(row["result_ids"]), "status": row["status"], "boundary": row["claim_boundary"]}
        for row in claims
    ])
    tf_index_rows = [
        {"ID": row["id"], "title": row["title"], "path": row.get("path", row.get("csv")), "RQ": row.get("research_question", "RQ1–RQ5"),
         "takeaway": row.get("main_takeaway", "Dữ liệu chi tiết trong file"), "status": row.get("data_status", "GENERATED"), "priority": row.get("presentation_priority", "APPENDIX")}
        for row in [*tables, *figures]
    ]
    tf_index = "# CHỈ MỤC BẢNG VÀ HÌNH\n\n" + _md_table(tf_index_rows)
    files = {
        "ABSTRACT_DRAFT.md": abstract,
        "EXECUTIVE_SUMMARY.md": executive,
        "METHODOLOGY.md": method,
        "RESULTS_AND_DISCUSSION.md": results,
        "FINAL_RESEARCH_REPORT.md": final_report,
        "DATA_QUALITY.md": data_quality,
        "LIMITATIONS.md": limitations_doc,
        "REPRODUCIBILITY.md": reproducibility,
        "LITERATURE_GAPS.md": literature,
        "FUTURE_RESEARCH.md": future,
        "PRESENTATION_BRIEF.md": presentation,
        "DEFENSE_SCRIPT_10_MIN.md": script,
        "DEFENSE_QA.md": qa,
        "EVIDENCE_CLAIM_MATRIX.md": evidence_matrix,
        "TABLE_FIGURE_INDEX.md": tf_index,
    }
    for name, content in files.items():
        (docs_dir / name).write_text(content.strip() + "\n", encoding="utf-8")
    index = {
        "FINAL_RESEARCH_REPORT.md": [row["result_id"] for row in registry.rows],
        "EXECUTIVE_SUMMARY.md": sorted({result_id for row in claims[:11] for result_id in row["result_ids"]}),
        "PRESENTATION_BRIEF.md": [
            "TERRA_ROWS", "AAVE_DATA_VERIFIED_BORROWERS", "TERRA_MECH_EVENT_COUNT", "TERRA_HF_UST_RMSE",
            "TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH", "AAVE_DET_PROFESSOR_DEMO_TOTAL_LIQUIDATED_DEBT",
            "AAVE_MC_PROFESSOR_DEMO_CASCADE_FREQUENCY",
        ],
        "DEFENSE_SCRIPT_10_MIN.md": [
            "AAVE_DATA_BLOCK_NUMBER", "TERRA_ROWS", "TERRA_SWAPS", "AAVE_DATA_VERIFIED_BORROWERS",
            "AAVE_DATA_WETH_USDC_COHORT", "TERRA_HF_UST_RMSE", "TERRA_TIMING_0_995",
            "TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH", "TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_9_HIGH",
            "AAVE_DET_PROFESSOR_DEMO_TOTAL_LIQUIDATED_DEBT", "AAVE_DET_PROFESSOR_DEMO_WAVE_2_PLUS_LIQUIDATED_DEBT",
            "AAVE_MC_PROFESSOR_DEMO_CASCADE_FREQUENCY", "AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_LOWER",
            "AAVE_MC_PROFESSOR_DEMO_CASCADE_WILSON_UPPER",
        ],
    }
    write_json(output_dir / "document_claim_index.json", index)
    return index


def generate_documents(
    output_dir: Path,
    docs_dir: Path,
    registry: Registry,
    claims: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    figures: list[dict[str, Any]],
    terra_quality: dict[str, Any],
    aave_quality: dict[str, Any],
    preflight: dict[str, Any],
) -> dict[str, list[str]]:
    docs_dir.mkdir(parents=True, exist_ok=True)
    values = registry.values()

    def v(result_id: str) -> str:
        return _fmt(values[result_id])

    matrix = read_json(output_dir / "rq_answer_matrix.json")["research_questions"]
    matrix_markdown = _md_table(
        [
            {
                "RQ": row["rq"],
                "Question": row["research_question"],
                "Method": row["analysis_method"],
                "Result": row["main_result"],
                "Status": row["answer_status"],
                "Evidence": ", ".join(row["key_evidence_ids"]),
                "Boundary": row["claim_boundary"],
                "Limitation": row["limitation"],
            }
            for row in matrix
        ]
    )
    rq_text = """## 1.4 Sáu câu hỏi nghiên cứu chính

- **RQ1.** Với một snapshot borrower và liquidity thực, cú sốc giá ETH tối thiểu ở mức nào bắt đầu tạo liquidation cascade (cascade depth ≥ 2)?
- **RQ2.** Độ sâu thanh khoản DEX và liquidity haircut ảnh hưởng như thế nào đến price impact, cascade amplification và bad debt?
- **RQ3.** Gas cost, capital/capacity và reaction delay của liquidator ảnh hưởng như thế nào đến tốc độ xử lý vị thế mất an toàn và phần debt chưa được thanh lý?
- **RQ4.** Năng lực arbitrage ảnh hưởng như thế nào đến mức lệch giá, số wave liquidation và thời gian phục hồi?
- **RQ5.** Stablecoin depeg làm thay đổi kết quả stress test như thế nào khi stablecoin đóng vai trò debt/settlement asset?
- **RQ6.** Các counterfactual của LTV, liquidation threshold và liquidation bonus có tạo ra trade-off nào giữa capital efficiency và tail risk?
"""
    extension_text = """## 1.6 Kiểm chứng và mở rộng nghiên cứu

### A. Historical Validation Extension — Terra 2022

Terra cung cấp historical mechanism validation, conditional reconstruction, cutoff-safe early warning và historical stress evidence. Extension này không thay thế hoặc trả lời hộ sáu RQ Aave.

### B. Multilayer Network Analysis Extension — Aave × Uniswap

Đồ thị biểu diễn transmission channel, contagion topology, centrality, structural bridge và wave visualization. Centrality chỉ có nghĩa trong sub-network đã mô hình hóa, không phải total DeFi importance.
"""
    rq_summary = f"""- **RQ1 — NOT OBSERVED.** Không quan sát được ngưỡng liquidation cascade trong lưới shock −5% đến −40% và haircut 0/25/50/75%; cascade depth lớn nhất là {v('RQ1_GRID_MAX_CASCADE_DEPTH')}. Không được ngoại suy ra ngoài miền đã thử.
- **RQ2 — SUPPORTED WITH BOUNDARY.** Liquidity haircut làm price impact và bad debt thay đổi, nhưng không tạo wave mới trong lưới; consequence amplification khác cascade creation.
- **RQ3 — PARTIAL.** Gas và capacity sweep không binding; recovery dùng first-return semantics và không thay processing delay; capital 25% và 50% của reference {v('RQ3_REQUIRED_CAPITAL_REFERENCE')} USDC binding, 100% và 200% non-binding.
- **RQ4 — SUPPORTED WITH MODEL BOUNDARY.** Arbitrage capacity không đổi intrawave forced-sale impact vì agent chạy sau liquidation, nhưng làm giảm post-arbitrage residual spread trong abstraction.
- **RQ5 — SUPPORTED FOR ONE CHANNEL.** Tại USDC $1.10 có {v('RQ5_USDC_1_1_BORROWERS_HF_BELOW_1_00')} borrower HF<1, so với {v('RQ5_USDC_1_0_BORROWERS_HF_BELOW_1_00')} ở $1.00. Downward depeg không làm HF xấu hơn trong pure valuation semantics.
- **RQ6 — SUPPORTED AS THREE DISTINCT MECHANISMS.** LTV tăng ex-ante borrowing capacity; LT dịch HF/liquidation boundary; bonus đổi collateral seized và expected profit. LTV không phải direct frozen-snapshot liquidation trigger.
"""
    rq_results = f"""## 5.2 RQ1 — Shock threshold / cascade

**Question.** Shock tối thiểu nào tạo cascade depth ≥2?

**Method.** Lưới shock −5%…−40% × haircut 0/25/50/75%.

**Evidence/Finding.** `RQ1_GRID_MAX_CASCADE_DEPTH` = {v('RQ1_GRID_MAX_CASCADE_DEPTH')}. Không quan sát được ngưỡng liquidation cascade trong miền stress đã thử.

**Interpretation/Limitation/Answer.** Đây là negative finding trên lưới rời rạc, không phải bằng chứng threshold nằm ngoài −40%.

## 5.3 RQ2 — Liquidity

**Question/Method.** Sweep haircut và shock × liquidity grid kiểm tra price impact, bad debt, liquidated debt và depth.

**Evidence/Finding.** Range response của intrawave forced-sale impact và bad debt lần lượt được ghi ở `AAVE_SENS_LIQUIDITY_HAIRCUT_MAX_INTRAWAVE_LIQUIDATION_PRICE_IMPACT_RANGE` và `AAVE_SENS_LIQUIDITY_HAIRCUT_BAD_DEBT_RANGE`; depth vẫn dưới 2.

**Interpretation/Limitation/Answer.** Liquidity làm khuếch đại hậu quả nhưng chưa tạo liquidation wave mới trong range/snapshot/venue này.

## 5.4 RQ3 — Liquidator frictions

**Question/Method.** Kết hợp gas/capacity sweep, delay 0/1/2/4 và capital bằng 25/50/100/200% funding reference.

**Evidence/Finding.** Delay status `{v('RQ3_DELAY_STATUS')}`; recovery time dùng first-return semantics và bằng 0 khi tolerance chưa từng bị vượt. Required capital reference = {v('RQ3_REQUIRED_CAPITAL_REFERENCE')} USDC. Capital 25/50% làm total liquidated debt bằng {v('RQ3_CAPITAL_0_25_TOTAL_LIQUIDATED_DEBT')}/{v('RQ3_CAPITAL_0_5_TOTAL_LIQUIDATED_DEBT')}; 100% khôi phục {v('RQ3_CAPITAL_1_0_TOTAL_LIQUIDATED_DEBT')}.

**Interpretation/Limitation/Answer.** Binding: capital 25/50%. Non-binding: gas/capacity ranges cũ. Recovery time không được dùng thay cho processing delay khi spread chưa breach tolerance. Engine dùng funding cộng dồn, không tái sử dụng.

## 5.5 RQ4 — Arbitrage

**Question/Method.** Arbitrage-capacity one-factor sweep.

**Evidence/Finding.** Range response intrawave impact = {v('AAVE_SENS_ARBITRAGE_CAPACITY_MAX_INTRAWAVE_LIQUIDATION_PRICE_IMPACT_RANGE')}; range response post-arbitrage spread = {v('AAVE_SENS_ARBITRAGE_CAPACITY_MAX_POST_ARBITRAGE_SPREAD_RANGE')}; cascade depth range = {v('AAVE_SENS_ARBITRAGE_CAPACITY_CASCADE_DEPTH_RANGE')}.

**Interpretation/Limitation/Answer.** Arbitrage capacity không thay instantaneous forced-sale impact vì agent chạy sau liquidation, nhưng làm giảm residual spread trong abstraction. Không suy ra hiệu quả arbitrage thị trường thực.

## 5.6 RQ5 — Stablecoin debt valuation

**Question/Method.** USDC/USD $0.90, $0.95, $0.99, $1.00, $1.01, $1.05, $1.10; chỉ revalue USDC debt tokens, không reprice `other_debt_usd`.

**Evidence/Finding.** Explicit $1 baseline tương thích legacy = {v('RQ5_USDC_BASELINE_COMPATIBLE')}. HF<1 là {v('RQ5_USDC_1_1_BORROWERS_HF_BELOW_1_00')} tại $1.10 và {v('RQ5_USDC_1_0_BORROWERS_HF_BELOW_1_00')} tại $1.00; HF<1.20 tại $0.90 là {v('RQ5_USDC_0_9_BORROWERS_HF_BELOW_1_20')}.

**Interpretation/Limitation/Answer.** Upward depeg làm USDC debt đắt hơn theo USD và làm HF yếu đi; downward depeg làm debt value giảm và HF mạnh lên hoặc không xấu đi. **This experiment isolates the USDC debt-valuation channel.** It does not represent the full market-liquidity, redemption, settlement or confidence consequences of a real stablecoin depeg.

## 5.7 RQ6 — Policy parameters

### LTV — ex-ante capital efficiency

Capacity aggregate tăng từ {v('RQ6_LTV_0_755_AGGREGATE_MAX_BORROWING_CAPACITY_USD')} USD ở LTV 0.755 lên {v('RQ6_LTV_0_825_AGGREGATE_MAX_BORROWING_CAPACITY_USD')} USD ở 0.825. Higher LTV tăng capacity nhưng giảm origination buffer. Borrower above counterfactual capacity không được gọi là liquidatable.

### Liquidation Threshold — Health Factor boundary

Total liquidated debt là {v('RQ6_LT_0_83_TOTAL_LIQUIDATED_DEBT')} tại LT 0.83 và {v('RQ6_LT_0_855_TOTAL_LIQUIDATED_DEBT')} tại LT 0.855. LT trực tiếp thay đổi WETH collateral term trong HF; other collateral giữ threshold quan sát.

### Liquidation Bonus — execution economics

Status `{v('RQ6_BONUS_STATUS')}`. Collateral seized tăng từ {v('RQ6_BONUS_1_03_COLLATERAL_SEIZED_WETH')} WETH tại 1.03 lên {v('RQ6_BONUS_1_07_COLLATERAL_SEIZED_WETH')} WETH tại 1.07; bonus đi qua quote/profitability path.

**Answer.** Ba parameter không thể gộp: LTV điều khiển ex-ante capital efficiency; LT điều khiển liquidation boundary; bonus điều khiển execution incentive/collateral economics.
"""
    methodology = f"""# PHƯƠNG PHÁP NGHIÊN CỨU

{rq_text}

## Thiết kế evidence-first

Canonical Aave REAL_MAINNET tại block {aave_quality['block_number']} được dùng cho RQ1–RQ6. Mọi counterfactual giữ snapshot và các trường ngoài one-factor cố định. Terra và multilayer network được tách thành extension.

## RQ3

Reaction delay được suy ra theo `timestep_seconds`, không hard-code đơn vị thời gian. Capital reference là tổng USDC funding được engine tiêu thụ trong finite unconstrained run; capital bị trừ và không recycle, còn per-step capacity reset mỗi wave.

## RQ5

`usdc_price_usd` mặc định 1.0. Debt value = USDC token quantity × USDC/USD + other debt đã được ghi bằng USD. Higher/lower price chỉ kiểm tra debt-valuation channel; settlement, liquidity, redemption và confidence nằm ngoài mô hình.

## RQ6 và lý do tách LTV khỏi LT

LTV là constraint phát sinh khoản vay, nên frozen debt không được viết lại. Phân tích LTV tính ex-ante max capacity/utilization. LT đi trực tiếp vào tử số Health Factor và eligibility. Bonus đi vào collateral seize, DEX quote và liquidator profitability. Các mức policy xuất phát từ WETH reserve canonical (LTV 0.805, LT 0.83, bonus 1.05) và chỉ dùng mức protocol-valid.

## Robustness và tái lập

USDC=$1 phải khớp legacy; delay không mutate input; capital không overspend; LT override không reweight other collateral; LTV không mutate debt. Lệnh chuẩn: `{REPRODUCE_COMMAND}`.
"""
    results = f"""# KẾT QUẢ VÀ THẢO LUẬN

## 5.1 Data validation

Snapshot Aave block {v('AAVE_DATA_BLOCK_NUMBER')} có {v('AAVE_DATA_VERIFIED_BORROWERS')} borrower xác minh và cohort WETH/USDC {v('AAVE_DATA_WETH_USDC_COHORT')}; đây không phải market coverage.

{rq_results}

## 5.8 Terra Historical Validation Extension

Terra giữ vai trò historical mechanism validation, reconstruction, cutoff-safe warning và counterfactual stress. Initial-depeg warning muộn và timing fit chưa hoàn hảo được giữ như negative evidence; Terra không trả lời thay RQ5 Aave.

## 5.9 Multilayer Network Analysis Extension

`NETWORK_AAVE_BETWEENNESS` = {v('NETWORK_AAVE_BETWEENNESS')}; kết luận chỉ là structural bridge trong modeled sub-network.

## 5.10 Robustness / Monte Carlo

Fixed-seed Monte Carlo là model-implied sampling, không phải real-world probability.

## 5.11 Cross-case discussion

Điểm chung hợp lệ là phản hồi phi tuyến. `CROSS_CASE_SYNTHESIS_BOUNDARY` ngăn suy luận Terra kiểm chứng Aave hoặc ngược lại.
"""
    executive = f"""# TÓM TẮT ĐIỀU HÀNH

## Trả lời RQ1–RQ6

{rq_summary}

## Historical Validation Extension — Terra 2022

Historical Fit hỗ trợ reconstruction có điều kiện nhưng timing chưa hoàn hảo; cutoff-safe warning muộn cho depeg ban đầu; mechanism accounting được hỗ trợ mà không nâng thành price causality.

## Multilayer Network Analysis Extension

Aave là bridge trong topology nhỏ đã mô hình hóa. Kết quả không đại diện total DeFi importance.

Mọi con số ánh xạ đến `results_registry.json`; claim và boundary nằm trong `claim_ledger.json`.
"""
    abstract = f"""# DỰ THẢO TÓM TẮT

Nghiên cứu trả lời sáu câu hỏi về cascade threshold, liquidity, liquidator frictions, arbitrage, USDC debt valuation và policy parameters trên snapshot Aave V3 × Uniswap V3 REAL_MAINNET block {v('AAVE_DATA_BLOCK_NUMBER')}. Không quan sát cascade depth ≥2 trong lưới đã thử; liquidity khuếch đại hậu quả nhưng chưa tạo wave mới; capital thấp là friction binding; USDC depeg có hướng phụ thuộc vai trò debt; LTV, LT và bonus có cơ chế khác nhau. Terra 2022 được giữ như Historical Validation Extension và graph như Multilayer Network Analysis Extension. Kết quả có provenance, claim boundary và regression comparison; không phải forecast hay xác suất thị trường. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]
"""
    final_report = f"""# NỀN TẢNG BÁO CÁO NGHIÊN CỨU CUỐI CÙNG

## TÓM TẮT

{abstract.splitlines()[2]}

# 1. GIỚI THIỆU

## 1.1 Bối cảnh

DeFi nối tín dụng, thanh khoản và định giá, tạo khả năng phản hồi nội sinh. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

## 1.2 Vấn đề nghiên cứu

Vấn đề là xác định channel nào tạo hoặc khuếch đại stress mà không biến output mô hình thành observed fact.

## 1.3 Mục tiêu nghiên cứu

Đo threshold, liquidity, frictions, arbitrage, stablecoin valuation và policy trade-offs trên evidence frozen.

{rq_text}

## 1.5 Đóng góp

Pipeline nối input hash → simulation → registry → claim → table/figure/document, giữ cả negative findings.

{extension_text}

# 2. CƠ SỞ LÝ THUYẾT

Khung gồm lending risk, HF, liquidation, AMM liquidity, stablecoin balance-sheet role và contagion. [CẦN BỔ SUNG NGUỒN HỌC THUẬT]

# 3. DỮ LIỆU VÀ PHƯƠNG PHÁP

Xem `METHODOLOGY.md`; dữ liệu observed, derived và simulated được phân lớp, với snapshot/hash/seed cố định.

# 4. MÔ HÌNH

Engine mô phỏng shock → HF → liquidation → forced WETH sale → DEX impact → revaluation; parameter semantics được kiểm thử từ implementation thực tế.

# 5. KẾT QUẢ

{results.split('# KẾT QUẢ VÀ THẢO LUẬN', 1)[1].strip()}

# 6. THẢO LUẬN

Negative result không phải lỗi mô hình: nó xác định những mechanism không binding trong snapshot/range, còn capital và một số policy channels có response rõ.

# 7. HẠN CHẾ

Một snapshot, cohort không phải toàn market, một execution venue, capital không recycle, stablecoin chỉ có valuation channel, topology nhỏ và model dependence.

# 8. HƯỚNG NGHIÊN CỨU

Mở rộng multi-collateral/debt, multi-venue, time-varying liquidity, capital recycling, stablecoin settlement/liquidity và out-of-sample validation.

# 9. KẾT LUẬN

Sáu RQ gốc đã có evidence và boundary. Terra/network là extension, không thay thế RQ chính.
"""
    data_quality = f"""# CHẤT LƯỢNG DỮ LIỆU

- Aave: REAL_MAINNET block {aave_quality['block_number']}, {aave_quality['verified_borrowers']} verified borrowers; cohort không phải market coverage.
- Terra: {terra_quality['row_count']} hourly rows và {terra_quality['native_swaps']['rows']} native swaps; unavailable vẫn là unavailable.
- Canonical input hashes được giữ trong manifest; regression comparison yêu cầu mọi numeric leaf cũ bất biến.
"""
    limitations = """# HẠN CHẾ

- Aave dùng một frozen snapshot, sample candidate và một Uniswap V3 venue.
- Reaction delay không mô hình price path phát sinh trong thời gian chờ; capital không recycle.
- USDC experiment chỉ revalue debt, không mô hình redemption/settlement/liquidity/confidence.
- LTV là ex-ante analytical counterfactual; không re-underwrite frozen debt.
- LT/bonus là policy counterfactual, không forecast governance.
- Terra data availability, timing fit và cutoff-safe warning limitations vẫn nguyên.
- Network centrality chỉ thuộc modeled sub-network.
"""
    reproducibility = f"""# TÁI LẬP

## Lệnh chuẩn

```powershell
{REPRODUCE_COMMAND}
```

## Provenance

- Previous research package commit: `{PREVIOUS_RESEARCH_PACKAGE_COMMIT}`
- Source code commit: `{git('rev-parse', 'HEAD')}`
- Artifact bundle commit: được finalization sau artifact commit, không tự tham chiếu giả.
- Metadata finalization commit: được ghi sau bước finalization.
- Orchestrator: `{FINAL_RESEARCH_VERSION}`; RQ completion: `{RQ_COMPLETION_VERSION}`.
- Python: `{preflight['python'].splitlines()[0]}`; Node: `{preflight['node']}`.

`manifest.json` giữ input/output/document hashes, seeds, scenario definitions và ba commit role riêng biệt.
"""
    literature = """# KHOẢNG TRỐNG TÀI LIỆU CẦN BỔ SUNG

Không tạo tác giả/năm/DOI. Cần bổ sung nguồn đã kiểm tra cho Aave V3/HF/liquidation, Uniswap V3 liquidity, stablecoin balance-sheet role, liquidator capital, ABM, Terra 2022, early-warning, Monte Carlo và multilayer networks.
"""
    future = """# HƯỚNG NGHIÊN CỨU TIẾP THEO

1. Multi-collateral/debt và toàn bộ reserve Aave.
2. Multi-venue routing và time-varying liquidity.
3. Capital recycling, competition và delay-dependent price paths.
4. USDC liquidity/redemption/settlement channels riêng.
5. Re-underwriting dynamics cho LTV và governance transition cho LT/bonus.
6. Multi-protocol evidence-backed network và out-of-sample validation.
"""
    presentation = f"""# BRIEF THUYẾT TRÌNH 10–12 PHÚT

1. Sáu RQ gốc — hiển thị Table_22.
2. Data/provenance — block {v('AAVE_DATA_BLOCK_NUMBER')}, cohort boundary.
3. RQ1 — không quan sát cascade depth≥2, không ngoại suy.
4. RQ2 — liquidity khuếch đại consequence, không tạo wave.
5. RQ3 — A17/A18: first-return recovery semantics; capital 25/50% binding.
6. RQ4 — intrawave impact tách khỏi post-arbitrage stabilization.
7. RQ5 — A19: upward/downward USDC debt valuation và limitation.
8. RQ6 — A20–A22: LTV ≠ LT ≠ bonus.
9. Terra Historical Validation Extension.
10. Multilayer Network Analysis Extension.
11. Regression/quality gate.
12. Limitations và conclusion.
"""
    defense_script = f"""# KỊCH BẢN BẢO VỆ 10 PHÚT

Sáu RQ ban đầu nằm ở trung tâm thiết kế. RQ1 không tìm thấy cascade depth≥2 trong shock −5%…−40% và haircut 0…75%, nên không bịa threshold. RQ2 cho thấy thanh khoản khuếch đại intrawave impact/bad debt nhưng không tạo Wave 2. RQ3 tách gas, capacity, reaction delay và capital; recovery là first return sau khi breach tolerance, còn capital 25/50% của reference {v('RQ3_REQUIRED_CAPITAL_REFERENCE')} USDC mới là binding. RQ4 cho thấy arbitrage capacity không đổi forced-sale impact xảy ra trước agent, nhưng giảm post-arbitrage residual spread trong abstraction.

RQ5 được kiểm tra trực tiếp ở Aave, không dùng Terra trả lời hộ: USDC upward depeg làm debt USD lớn hơn và HF yếu hơn; downward depeg làm ngược lại trong pure valuation channel. Thí nghiệm không mô hình redemption, settlement, market liquidity hay confidence.

RQ6 phân biệt LTV, LT và bonus. LTV là ex-ante capacity nên không sửa frozen debt/HF. LT trực tiếp đổi liquidation boundary. Bonus đổi collateral seized và profitability. Terra là Historical Validation Extension; graph là Network Analysis Extension. Negative findings là kết quả phòng thủ được, không phải mô hình thất bại.
"""
    qa_pairs = [
        ("6 RQ ban đầu của nhóm đâu?", "Nằm ở mục 1.4 và Table_22; Terra/network đã chuyển thành extension."),
        ("RQ3 đã kiểm tra delay/capital chưa?", "Có: delay 0/1/2/4 và capital 25/50/100/200% engine-derived demand reference."),
        ("Stablecoin depeg được test ở Aave hay chỉ nói Terra?", "Aave USDC được test trực tiếp từ $0.90 đến $1.10 qua debt-valuation channel."),
        ("LTV và liquidation threshold khác nhau thế nào?", "LTV giới hạn origination capacity; LT vào Health Factor và liquidation eligibility."),
        ("Tại sao LTV không trực tiếp làm HF đổi?", "Frozen snapshot giữ debt; nếu không re-underwrite, LTV mới chỉ là ex-ante capacity rule."),
        ("Tại sao không tìm thấy cascade?", "Forced sale/price impact chưa đẩy thêm borrower qua HF<1 trong lưới và venue đã thử."),
        ("Negative findings có phải mô hình thất bại không?", "Không; chúng xác định parameter nào không binding trong scope, miễn boundary được công bố."),
        ("Capital reference là gì?", "Cumulative USDC funding consumed vì engine trừ capital và không recycle."),
        ("USDC downward depeg luôn tốt?", "Không; chỉ pure debt-valuation channel cho debt-holder cohort này, không phải full depeg."),
        ("Centrality có phải total DeFi importance?", "Không; chỉ vị trí trong evidence-backed modeled sub-network."),
    ]
    defense_qa = "# HỎI–ĐÁP HỘI ĐỒNG\n\n" + "\n\n".join(
        f"## {index}. {question}\n\n{answer}" for index, (question, answer) in enumerate(qa_pairs, 1)
    )
    evidence_matrix = "# MA TRẬN BẰNG CHỨNG–CLAIM\n\n" + _md_table(
        [
            {
                "claim_id": row["claim_id"],
                "statement": row["statement_vi"],
                "status": row["status"],
                "result_ids": ", ".join(row["result_ids"]),
                "boundary": row["claim_boundary"],
                "allowed": row["allowed_wording"],
                "prohibited": row["prohibited_wording"],
            }
            for row in claims
        ]
    )
    tf_index = "# CHỈ MỤC BẢNG VÀ HÌNH\n\n" + _md_table(
        [
            {
                "ID": row["id"],
                "title": row["title"],
                "path": row.get("path", row.get("csv")),
                "RQ": row["research_question"],
                "takeaway": row["main_takeaway"],
                "status": row["data_status"],
                "boundary": row["claim_boundary"],
                "priority": row["presentation_priority"],
            }
            for row in [*tables, *figures]
        ]
    )
    rq_matrix_doc = "# RQ1–RQ6 ANSWER MATRIX\n\n" + matrix_markdown
    files = {
        "ABSTRACT_DRAFT.md": abstract,
        "EXECUTIVE_SUMMARY.md": executive,
        "METHODOLOGY.md": methodology,
        "RESULTS_AND_DISCUSSION.md": results,
        "FINAL_RESEARCH_REPORT.md": final_report,
        "DATA_QUALITY.md": data_quality,
        "LIMITATIONS.md": limitations,
        "REPRODUCIBILITY.md": reproducibility,
        "LITERATURE_GAPS.md": literature,
        "FUTURE_RESEARCH.md": future,
        "PRESENTATION_BRIEF.md": presentation,
        "DEFENSE_SCRIPT_10_MIN.md": defense_script,
        "DEFENSE_QA.md": defense_qa,
        "EVIDENCE_CLAIM_MATRIX.md": evidence_matrix,
        "TABLE_FIGURE_INDEX.md": tf_index,
        "RQ_ANSWER_MATRIX.md": rq_matrix_doc,
    }
    for name, content in files.items():
        (docs_dir / name).write_text(content.strip() + "\n", encoding="utf-8")

    matrix_ids = sorted({result_id for row in matrix for result_id in row["key_evidence_ids"]})
    extension_ids = [
        "TERRA_HF_UST_RMSE", "TERRA_TIMING_0_995", "TERRA_EW_CUTOFF_SAFE_UST_BELOW_0_995_HIGH",
        "TERRA_MECH_EVENT_COUNT", "NETWORK_AAVE_BETWEENNESS", "CROSS_CASE_SYNTHESIS_BOUNDARY",
    ]
    major_ids = sorted(set(matrix_ids + extension_ids + ["AAVE_DATA_BLOCK_NUMBER", "AAVE_DATA_VERIFIED_BORROWERS"]))
    index = {
        "FINAL_RESEARCH_REPORT.md": [row["result_id"] for row in registry.rows],
        "RESULTS_AND_DISCUSSION.md": major_ids,
        "EXECUTIVE_SUMMARY.md": major_ids,
        "PRESENTATION_BRIEF.md": major_ids,
        "DEFENSE_SCRIPT_10_MIN.md": major_ids,
        "RQ_ANSWER_MATRIX.md": matrix_ids,
    }
    write_json(output_dir / "document_claim_index.json", index)
    return index


def write_cross_case(output_dir: Path) -> None:
    write_json(
        output_dir / "cross_case/synthesis.json",
        {
            "cases": {
                "Terra_Classic_May_2022": {
                    "role": "historical validation, mechanism validation, reconstruction, warning and counterfactual stress",
                    "feedback": "peg stress -> redemption -> gross issuance -> dilution/confidence",
                },
                "Aave_V3_Uniswap_V3": {
                    "role": "contemporary REAL_MAINNET stress test and modeled contagion",
                    "feedback": "WETH shock -> Health Factor -> liquidation -> DEX impact -> revaluation",
                },
            },
            "legitimate_synthesis": "Both cases illustrate nonlinear financial feedback and endogenous amplification.",
            "forbidden_inference": [
                "Terra numerically validates Aave mechanics.",
                "Aave proves the Terra historical mechanism.",
                "The two case studies are contemporaneous.",
            ],
        },
    )


def run_fresh_appendix(requested: bool, output_dir: Path) -> dict[str, Any]:
    required = ("ETH_RPC_URL", "GRAPH_API_KEY", "AAVE_V3_SUBGRAPH_ID")
    configured = {name: bool(os.getenv(name)) for name in required}
    if not requested:
        result = {"status": "NOT_REQUESTED", "configured_presence_only": configured}
    elif not all(configured.values()):
        result = {
            "status": "UNAVAILABLE",
            "configured_presence_only": configured,
            "message": "Fresh appendix requires ETH_RPC_URL, GRAPH_API_KEY and AAVE_V3_SUBGRAPH_ID; frozen evidence remains primary.",
        }
    else:
        command = [sys.executable, "scripts/create_real_snapshot.py"]
        result = run_command(command)
        result["status"] = "CREATED_IN_REPOSITORY" if result["status"] == "PASS" else "UNAVAILABLE"
        result["claim_boundary"] = "Optional freshness appendix only; it does not replace the frozen canonical snapshot."
    write_json(output_dir / "aave/fresh_mainnet_appendix.json", result)
    return result


def quality_gate(
    output_dir: Path,
    docs_dir: Path,
    registry: Registry,
    claims: list[dict[str, Any]],
    borrower_addresses: set[str],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    json_count = 0
    for path in [*output_dir.rglob("*.json")]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        serialized = json.dumps(payload, allow_nan=False)
        if "NaN" in serialized or "Infinity" in serialized:
            raise ValueError(f"non-finite value in {path}")
        json_count += 1
    checks.append({"check": "json_parse_and_finite", "status": "PASS", "files": json_count})
    csv_count = 0
    for path in output_dir.rglob("*.csv"):
        pd.read_csv(path)
        csv_count += 1
    checks.append({"check": "csv_parse", "status": "PASS", "files": csv_count})
    figure_paths = list((output_dir / "figures").glob("*.png"))
    if len(figure_paths) != 35 or any(path.stat().st_size < 1000 for path in figure_paths):
        raise ValueError(f"expected 35 non-empty figures, found {len(figure_paths)}")
    checks.append({"check": "required_figures", "status": "PASS", "files": len(figure_paths)})
    table_csv = list((output_dir / "tables").glob("*.csv"))
    if len(table_csv) != 22:
        raise ValueError(f"expected 22 tables, found {len(table_csv)}")
    checks.append({"check": "required_tables", "status": "PASS", "files": len(table_csv)})
    valid_result_ids = set(registry.values())
    index = read_json(output_dir / "document_claim_index.json")
    indexed = {result_id for ids in index.values() for result_id in ids}
    missing = sorted(indexed.difference(valid_result_ids))
    if missing:
        raise ValueError(f"document claim index contains unknown result IDs: {missing}")
    claim_missing = sorted(
        {result_id for row in claims for result_id in row["result_ids"]}.difference(valid_result_ids)
    )
    if claim_missing:
        raise ValueError(f"claim ledger contains unknown result IDs: {claim_missing}")
    missing_supported_evidence = [
        row["claim_id"]
        for row in claims
        if row["status"] in EVIDENCE_REQUIRED_STATUSES and not row["result_ids"]
    ]
    if missing_supported_evidence:
        raise ValueError(f"supported claims lack result IDs: {missing_supported_evidence}")
    checks.append({"check": "claim_traceability", "status": "PASS", "indexed_results": len(indexed)})
    rq5 = read_json(output_dir / "rq_completion/rq5_usdc_depeg.json")
    if not rq5["backward_compatibility"]["usdc_price_1_matches_legacy"]:
        raise ValueError("USDC=$1 backward compatibility failed")
    if not all(rq5["directional_checks"].values()):
        raise ValueError("USDC directional sanity check failed")
    checks.append({"check": "usdc_baseline_and_direction", "status": "PASS"})
    regression = read_json(output_dir / "regression_comparison.json")
    if not regression["all_passed"]:
        raise ValueError("old-vs-new core numerical regression comparison failed")
    checks.append(
        {
            "check": "legacy_core_numerical_regression",
            "status": regression.get("status", "PASS"),
            "files": len(regression["files"]),
        }
    )
    generated_files = [path for root in (output_dir, docs_dir) for path in root.rglob("*") if path.is_file()]
    for path in generated_files:
        if path.suffix.lower() in {".png", ".parquet"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(marker in text for marker in SECRET_MARKERS):
            raise ValueError(f"secret-like marker in generated artifact: {path}")
        lower = text.lower()
        leaked = next((address for address in borrower_addresses if address and address in lower), None)
        if leaked:
            raise ValueError(f"raw borrower address leaked in generated artifact: {path}")
    checks.append({"check": "secret_and_borrower_address_scan", "status": "PASS", "files": len(generated_files)})
    prose = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in docs_dir.rglob("*.md")
    ).lower()
    prohibited_patterns = {
        "ltv_direct_trigger": r"ltv\s+(directly|trực tiếp)\s+(causes?|gây|làm).*liquidat",
        "terra_answers_aave_rq5": r"terra.*(direct answer|trả lời trực tiếp).*rq5",
        "cascade_threshold_extrapolation": r"threshold\s*>\s*40%|ngưỡng\s*>\s*40%",
        "network_total_defi_importance": r"centrality\s+(đại diện|represents)\s+(cho\s+)?(total|toàn bộ)",
    }
    violations = [name for name, pattern in prohibited_patterns.items() if re.search(pattern, prose)]
    if violations:
        raise ValueError(f"prohibited research wording detected: {violations}")
    checks.append({"check": "scientific_claim_boundaries", "status": "PASS"})
    required_docs = {
        "FINAL_RESEARCH_REPORT.md", "ABSTRACT_DRAFT.md", "EXECUTIVE_SUMMARY.md", "METHODOLOGY.md",
        "RESULTS_AND_DISCUSSION.md", "REPRODUCIBILITY.md", "LIMITATIONS.md", "EVIDENCE_CLAIM_MATRIX.md",
        "TABLE_FIGURE_INDEX.md", "PRESENTATION_BRIEF.md", "DEFENSE_SCRIPT_10_MIN.md", "DEFENSE_QA.md",
        "FUTURE_RESEARCH.md", "LITERATURE_GAPS.md", "DATA_QUALITY.md",
        "RQ_ANSWER_MATRIX.md",
    }
    missing_docs = sorted(name for name in required_docs if not (docs_dir / name).exists())
    if missing_docs:
        raise ValueError(f"required research documents missing: {missing_docs}")
    checks.append({"check": "required_documents", "status": "PASS", "files": len(required_docs)})
    return {"generated_at": now_iso(), "all_passed": True, "checks": checks}


def run_full_research_pipeline(
    *,
    output_dir: Path = DEFAULT_OUTPUT,
    fast: bool = False,
    fresh_mainnet: bool = False,
    skip_tests: bool = False,
) -> dict[str, Any]:
    total_started = time.perf_counter()
    docs_dir = DEFAULT_DOCS if output_dir.resolve() == DEFAULT_OUTPUT.resolve() else output_dir.parent / f"{output_dir.name}_docs"
    regression_baseline = capture_regression_baseline(output_dir)
    _clean_output(output_dir, docs_dir)
    source_commit = git("rev-parse", "HEAD")
    execution: list[dict[str, Any]] = []

    stage_started = time.perf_counter()
    preflight = run_preflight(skip_tests=skip_tests)
    execution.append({"stage": "preflight", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS" if preflight["all_required_passed"] else "FAIL"})
    write_json(output_dir / "preflight.json", preflight)
    if not preflight["all_required_passed"]:
        raise RuntimeError("preflight contains failed required checks; see preflight.json")

    stage_started = time.perf_counter()
    terra_quality, aave_quality, borrower_addresses = validate_inputs()
    write_json(output_dir / "data_quality_summary.json", {"terra": terra_quality, "aave": aave_quality})
    execution.append({"stage": "canonical_data_validation", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS"})

    stage_started = time.perf_counter()
    run_demo_pipeline(fast=fast, output_dir=output_dir / "terra/demo")
    execution.append({"stage": "terra_demo", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS"})

    stage_started = time.perf_counter()
    terra_mc_runs = 30 if fast else 100
    run_final_pipeline(
        dataset_path=DEFAULT_DATASET,
        strict_v2_path=DEFAULT_STRICT_V2,
        output_dir=output_dir / "terra/audit",
        native_swaps_path=DEFAULT_NATIVE_SWAPS,
        monte_carlo_runs=terra_mc_runs,
    )
    execution.append({"stage": "terra_final_audit", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS", "monte_carlo_runs": terra_mc_runs})

    stage_started = time.perf_counter()
    aave_summary = run_aave_research_suite(output_dir=output_dir / "aave", fast=fast)
    execution.append({"stage": "aave_deterministic_sensitivity_monte_carlo_network", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS"})
    run_fresh_appendix(fresh_mainnet, output_dir)
    write_cross_case(output_dir)
    regression_comparison = compare_regression_baseline(regression_baseline, output_dir)
    write_json(output_dir / "regression_comparison.json", regression_comparison)
    if not regression_comparison["all_passed"]:
        raise RuntimeError("existing core numerical results changed; see regression_comparison.json")

    stage_started = time.perf_counter()
    registry = build_registry(output_dir, terra_quality, aave_quality)
    write_json(output_dir / "results_registry.json", {"pipeline_version": FINAL_RESEARCH_VERSION, "results": registry.rows})
    claims = build_claims(registry)
    write_json(output_dir / "claim_ledger.json", {"claims": claims})
    claim_csv_rows = [{**row, "result_ids": ";".join(row["result_ids"])} for row in claims]
    _csv(output_dir / "claim_ledger.csv", claim_csv_rows)
    build_rq_answer_matrix(output_dir)
    execution.append({"stage": "results_and_claim_registries", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS"})

    stage_started = time.perf_counter()
    tables = generate_tables(output_dir, terra_quality, aave_quality)
    execution.append({"stage": "tables", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS", "count": len(tables)})

    stage_started = time.perf_counter()
    figures = generate_figures(output_dir)
    execution.append({"stage": "figures", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS", "count": len(figures)})

    stage_started = time.perf_counter()
    generate_documents(output_dir, docs_dir, registry, claims, tables, figures, terra_quality, aave_quality, preflight)
    execution.append({"stage": "documents", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS", "count": len(list(docs_dir.glob("*.md")))})

    stage_started = time.perf_counter()
    gate = quality_gate(output_dir, docs_dir, registry, claims, borrower_addresses)
    write_json(output_dir / "quality_gate.json", gate)
    execution.append({"stage": "quality_gate", "runtime_seconds": time.perf_counter() - stage_started, "status": "PASS"})
    total_runtime = time.perf_counter() - total_started
    execution_log = {"started_from_commit": source_commit, "finished_at": now_iso(), "total_runtime_seconds": total_runtime, "stages": execution}
    write_json(output_dir / "execution_log.json", execution_log)
    scenario_definitions = {row["scenario_name"]: row["scenario"] for row in aave_summary["deterministic_scenarios"]}
    manifest = {
        "pipeline_version": FINAL_RESEARCH_VERSION,
        "previous_research_package_commit": PREVIOUS_RESEARCH_PACKAGE_COMMIT,
        "execution_time": now_iso(),
        "source_code_commit": source_commit,
        "generated_artifact_commit": None,
        "metadata_finalization_commit": None,
        "provenance_note": "Artifact and metadata commit fields are finalized only after the corresponding Git commits; no SHA is fabricated.",
        "canonical_aave_snapshot": {"path": CANONICAL_SNAPSHOT.as_posix(), "sha256": aave_quality["sha256"], "block": aave_quality["block_number"], "mode": aave_quality["mode"]},
        "canonical_terra_dataset": {"path": EXTENDED_DATASET.as_posix(), "sha256": terra_quality["sha256"], "rows": terra_quality["row_count"]},
        "input_hashes": {
            CANONICAL_SNAPSHOT.as_posix(): aave_quality["sha256"],
            EXTENDED_DATASET.as_posix(): terra_quality["sha256"],
            NATIVE_SWAPS.as_posix(): terra_quality["native_swaps"]["sha256"],
            DEFAULT_DATASET.as_posix(): sha256_file(DEFAULT_DATASET),
            DEFAULT_STRICT_V2.as_posix(): sha256_file(DEFAULT_STRICT_V2),
            DEFAULT_NATIVE_SWAPS.as_posix(): sha256_file(DEFAULT_NATIVE_SWAPS),
        },
        "output_hashes": output_hashes(output_dir, exclude={"manifest.json"}),
        "document_hashes": output_hashes(docs_dir),
        "scenario_definitions": scenario_definitions,
        "seeds": {"aave": [20260914, 20260915, 20260916], "terra": "recorded in child manifests"},
        "monte_carlo_run_counts": {"aave_per_scenario": aave_summary["mc_runs_per_scenario"], "terra_final": terra_mc_runs},
        "versions": {
            "orchestrator": FINAL_RESEARCH_VERSION,
            "aave_suite": AAVE_RESEARCH_VERSION,
            "rq_completion": RQ_COMPLETION_VERSION,
            "terra_final": FINAL_PIPELINE_VERSION,
            "graph": GRAPH_MODEL_VERSION,
        },
        "regression_comparison": regression_comparison,
        "tests": preflight,
        "limitations": [
            "Terra historical DEX depth and observed LFG defense unavailable.",
            "Aave borrower candidate sample is not whole-market coverage.",
            "One selected Uniswap execution venue and a small modeled topology.",
            "Monte Carlo frequencies and graph scores are model-dependent, not real-world probabilities.",
        ],
        "reproduce_command": REPRODUCE_COMMAND,
        "fast_mode": fast,
        "total_runtime_seconds": total_runtime,
    }
    write_json(output_dir / "manifest.json", manifest)
    return {
        "output_dir": output_dir.as_posix(),
        "docs_dir": docs_dir.as_posix(),
        "source_code_commit": source_commit,
        "runtime_seconds": total_runtime,
        "figures": len(figures),
        "tables": len(tables),
        "documents": len(list(docs_dir.glob("*.md"))),
        "claims": len(claims),
        "quality_gate": gate["all_passed"],
        "rq_completion_version": RQ_COMPLETION_VERSION,
    }


__all__ = ["DEFAULT_OUTPUT", "FINAL_RESEARCH_VERSION", "run_full_research_pipeline"]
