from __future__ import annotations

import argparse
import json
import platform
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
from sim.terra.stress_test import StressScenario, run_stress_test


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
    print(f"[1/7] Historical dataset verified: {len(frame)} hourly rows")
    mechanism = validate_native_mint_mechanism()
    _write(output_dir / "mechanism_check.json", mechanism)
    print(f"[2/7] Native swaps verified: {mechanism['raw_swap_rows']:,} events")
    historical = fit_historical(candidates=candidates)
    _write(output_dir / "historical_fit.json", historical)
    print(f"[3/7] Historical Fit objective: {historical['objective']['value']:.6f}")
    warning = {
        "retrospective": build_early_warning(mode="RETROSPECTIVE"),
        "cutoff_safe": build_early_warning(mode="CUTOFF_SAFE"),
    }
    _write(output_dir / "early_warning_timeline.json", warning)
    print(f"[4/7] Early Warning built: {len(warning['cutoff_safe']['timeline'])} scores per mode")
    stress = run_stress_test(StressScenario(), runs=runs)
    _write(output_dir / "stress_test.json", stress)
    print(f"[5/7] Stress Test: {stress['summary']['wording']}")
    presentation = {
        "title": "DeFiStress Lab — Terra 2022 historical validation and counterfactual stress",
        "three_layers": [
            {"name": "Historical Fit", "question": "Can the mechanism reconstruct the known crisis?"},
            {"name": "Early Warning", "question": "Did measurable warning signs rise before severe depeg?"},
            {"name": "Stress Test", "question": "What happens under altered market assumptions?"},
        ],
        "dataset": dataset_summary(),
        "historical_fit_metrics": historical["metrics"],
        "early_warning_lead_times": {
            "retrospective": warning["retrospective"]["lead_times"],
            "cutoff_safe": warning["cutoff_safe"]["lead_times"],
        },
        "stress_summary": stress["summary"],
        "mechanism_summary": mechanism,
        "limitations": [
            "Historical Fit is reconstruction, not forecasting.",
            "Retrospective Early Warning uses weights developed with knowledge of the event.",
            "DEX depth and LFG peg-defense are scenario assumptions, not observed historical channels.",
            "March-April market prices include lower-frequency carried state.",
        ],
    }
    _write(output_dir / "presentation_summary.json", presentation)
    print("[6/7] Presentation summary written")
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
    manifest = {
        "pipeline_version": DEMO_VERSION,
        "source_code_commit": _git("rev-parse", "HEAD"),
        "artifact_bundle_commit": None,
        "artifact_bundle_commit_resolution": (
            "Resolve after committing with: git log -1 --format=%H -- "
            "data/processed/terra_demo/reproducibility_manifest.json"
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
    print(f"[7/7] Artifact validation passed -> {output_dir}")
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
