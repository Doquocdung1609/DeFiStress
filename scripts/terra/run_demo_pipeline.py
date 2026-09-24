from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
from importlib import metadata
from pathlib import Path
from typing import Any

from sim.terra.demo_data import (
    DEMO_OUTPUT,
    DEMO_VERSION,
    EXTENDED_DATASET,
    NATIVE_SWAPS,
    dataset_summary,
    load_extended_frame,
    sha256_file,
)
from sim.terra.early_warning_v2 import build_early_warning
from sim.terra.historical_fit import fit_historical
from sim.terra.mechanism_validation import validate_native_mint_mechanism
from sim.terra.stress_test import run_stress_presets


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        return "UNAVAILABLE"


def run_demo_pipeline(*, fast: bool = False, output_dir: Path = DEMO_OUTPUT) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = load_extended_frame()
    if len(frame) != 1776:
        raise ValueError(f"expected 1776 hourly observations, found {len(frame)}")
    if not NATIVE_SWAPS.exists():
        raise FileNotFoundError(f"audited native swap extract is missing: {NATIVE_SWAPS}")
    runs, candidates = (30, 250) if fast else (100, 900)
    availability = {
        "anchor_event_hours": int(frame["anchor_withdrawal_flow"].notna().sum()),
        "native_issuance_hours": int(frame["gross_luna_issuance_from_native_swaps"].notna().sum()),
        "holder_concentration_hours": int(frame["top10_anchor_share"].notna().sum()),
        "luna_supply_hours": int(frame["luna_supply"].notna().sum()),
    }
    expected_availability = {
        "anchor_event_hours": 192,
        "native_issuance_hours": 168,
        "holder_concentration_hours": 1608,
        "luna_supply_hours": 312,
    }
    if availability != expected_availability:
        raise ValueError(f"source availability contract changed: {availability}")
    print(f"[1/9] Historical dataset and source availability verified: {len(frame)} hourly rows")
    mechanism = validate_native_mint_mechanism()
    _write(output_dir / "mechanism_check.json", mechanism)
    print(f"[2/9] Native swaps and mechanism window verified: {mechanism['raw_swap_rows']:,} events")
    historical = fit_historical(candidates=candidates)
    _write(output_dir / "historical_fit.json", historical)
    print(f"[3/9] Historical Fit objective: {historical['objective']['value']:.6f}")
    warning = {
        "retrospective": build_early_warning(mode="RETROSPECTIVE"),
        "cutoff_safe": build_early_warning(mode="CUTOFF_SAFE"),
    }
    _write(output_dir / "early_warning_timeline.json", warning)
    print(f"[4/9] Early Warning built: {len(warning['cutoff_safe']['timeline'])} scores per mode")
    if warning["cutoff_safe"]["leakage_audit"]["future_perturbation"]["status"] != "PASS":
        raise ValueError("cutoff-safe future-perturbation leakage audit failed")
    print("[5/9] Future-perturbation leakage audit passed at 5 deterministic cutoffs")
    preset_runs = run_stress_presets(runs=runs)
    stress = preset_runs["baseline"]
    stress["preset_results"] = {
        name: {
            "scenario": result["scenario"],
            "initial_state": result["initial_state"],
            "summary": result["summary"],
        }
        for name, result in preset_runs.items()
    }
    _write(output_dir / "stress_test.json", stress)
    print(f"[6/9] Baseline, Adverse, Severe Stress Tests: {runs} seeded runs each")
    presentation = {
        "title": "DeFiStress Lab — Terra 2022 historical validation and counterfactual stress",
        "three_layers": [
            {
                "name": "Historical Fit — Calibrated Feedback Reconstruction",
                "question": "Can a feedback model conditioned on available historical flows reconstruct the crisis?",
            },
            {"name": "Early Warning", "question": "Did measurable warning signs rise before severe depeg?"},
            {"name": "Stress Test", "question": "What happens under altered market assumptions?"},
        ],
        "dataset": dataset_summary(),
        "source_availability": availability,
        "historical_fit_metrics": historical["metrics"],
        "early_warning_lead_times": {
            "retrospective": warning["retrospective"]["lead_times"],
            "cutoff_safe": warning["cutoff_safe"]["lead_times"],
        },
        "stress_summary": stress["summary"],
        "stress_preset_summaries": {
            name: result["summary"] for name, result in preset_runs.items()
        },
        "mechanism_summary": mechanism,
        "limitations": [
            (
                "Historical Fit is a calibrated feedback reconstruction conditioned on observed historical "
                "flows where available; it is neither a pure ABM nor forecasting."
            ),
            "Retrospective Early Warning uses weights developed with knowledge of the event.",
            "DEX depth and LFG peg-defense are scenario assumptions, not observed historical channels.",
            "March-April market prices include lower-frequency carried state.",
            (
                "Counterfactual UST-to-LUNA conversion is calibrated from historical swaps but is not an "
                "audited future accounting identity."
            ),
        ],
    }
    _write(output_dir / "presentation_summary.json", presentation)
    print("[7/9] Presentation summary written")
    outputs = [
        output_dir / name
        for name in (
            "historical_fit.json",
            "early_warning_timeline.json",
            "stress_test.json",
            "mechanism_check.json",
            "presentation_summary.json",
        )
    ]
    packages: dict[str, str] = {}
    for name in ("numpy", "pandas", "pyarrow", "fastapi"):
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = "UNAVAILABLE"
    source_commit = _git("rev-parse", "HEAD")
    previous_manifest_path = output_dir / "reproducibility_manifest.json"
    previous_manifest = (
        json.loads(previous_manifest_path.read_text(encoding="utf-8"))
        if previous_manifest_path.exists()
        else {}
    )
    previous_bundle_commit = previous_manifest.get("artifact_bundle_commit")
    artifact_bundle_commit = (
        previous_bundle_commit
        if isinstance(previous_bundle_commit, str) and re.fullmatch(r"[0-9a-f]{40}", previous_bundle_commit)
        else source_commit
    )
    manifest: dict[str, Any] = {
        "pipeline_version": DEMO_VERSION,
        "source_code_commit": source_commit,
        "artifact_bundle_commit": artifact_bundle_commit,
        "artifact_bundle_commit_note": (
            "Commit whose tree first contains this generated artifact bundle. A later metadata-only manifest "
            "correction may record that commit without changing model logic, parameters, metrics, or artifacts."
        ),
        "mode": "FAST_30_RUNS" if fast else "RESEARCH_100_RUNS",
        "inputs": {
            EXTENDED_DATASET.as_posix(): sha256_file(EXTENDED_DATASET),
            NATIVE_SWAPS.as_posix(): sha256_file(NATIVE_SWAPS),
        },
        "outputs": {path.name: sha256_file(path) for path in outputs},
        "python": sys.version,
        "platform": platform.platform(),
        "packages": packages,
        "reproduce_command": ".\\.venv\\Scripts\\python.exe scripts\\terra\\run_demo_pipeline.py --research",
        "frozen_artifacts_policy": "Existing V1/V2/V4 artifacts are read-only and were not overwritten.",
    }
    _write(output_dir / "reproducibility_manifest.json", manifest)
    for path in (*outputs, output_dir / "reproducibility_manifest.json"):
        json.loads(path.read_text(encoding="utf-8"))
    for name, expected_hash in manifest["outputs"].items():
        if sha256_file(output_dir / name) != expected_hash:
            raise ValueError(f"artifact hash validation failed: {name}")
    print(f"[8/9] Artifact schemas and hashes validated -> {output_dir}")
    print(
        "[9/9] Limitations: Terra DEX depth, LFG peg-defense executions, and verified bridge flow remain unavailable."
    )
    return {
        "output_dir": str(output_dir),
        "mode": manifest["mode"],
        "artifacts": sorted(path.name for path in output_dir.glob("*.json")),
        "summary": presentation,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare every Terra artifact required for the presentation.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fast", action="store_true", help="Use 30 stress runs and a smaller fit search.")
    mode.add_argument("--research", action="store_true", help="Use 100 stress runs and the full fit search (default).")
    args = parser.parse_args()
    result = run_demo_pipeline(fast=args.fast)
    print(json.dumps({"mode": result["mode"], "artifacts": result["artifacts"]}, indent=2))


if __name__ == "__main__":
    main()
