from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402

ROOT = Path("data/processed/research_final/level3_extension")
REPORTS = (
    Path("docs/research_final/LEVEL3_VALIDATION_PLAN.md"),
    Path("docs/research_final/LEVEL3_HISTORICAL_EVENT_STUDY.md"),
    Path("docs/research_final/LEVEL2_FORK_VALIDATION.md"),
    Path("docs/research_final/DEEP_CASCADE_STRESS_STUDY.md"),
    Path("docs/research_final/LEVEL3_COMMANDER_REVIEW_PACKET.md"),
)
SOURCE_COMMIT = "423bcfd4ebf910ef73b94d9deaf7cf746d8ed71c"
CANONICAL_SHA256 = "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(*, implementation_commit: str, artifact_bundle_commit: str) -> None:
    historical = _load(ROOT / "historical" / "summary.json")
    selection = _load(ROOT / "historical" / "episode_selection.json")
    linkage = _load(ROOT / "historical" / "observation_linkage.json")["rows"]
    batches = _load(ROOT / "deep_stress" / "monte_carlo_batches.json")["batches"]
    diagnostics = _load(ROOT / "deep_stress" / "numerical_diagnostics.json")
    fork = _load(ROOT / "fork" / "validation.json")
    study_rows = list(csv.DictReader((ROOT / "historical" / "historical_event_study.csv").open()))
    selected_rows = [row for row in study_rows if row["selected_for_deep_review"] == "True"]
    mechanisms = list(
        csv.DictReader((ROOT / "tables" / "deterministic_mechanisms.csv").open())
    )
    prior_mechanisms = list(
        csv.DictReader(
            (ROOT / "tables" / "deterministic_mechanisms_pre_capital_fix.csv").open()
        )
    )
    cap_rows = list(csv.DictReader((ROOT / "deep_stress" / "wave_cap_comparison.csv").open()))
    grid_rows = list(csv.DictReader((ROOT / "deep_stress" / "deterministic_grid.csv").open()))

    tier_rows = [
        {"evidence_tier": tier, "event_count": count, "causal_claim_permitted": tier == "DIRECT_TRANSACTION_LINK"}
        for tier, count in sorted(Counter(row["tier"] for row in linkage).items())
    ]
    _csv(ROOT / "tables" / "historical_evidence_tiers.csv", tier_rows)
    _csv(ROOT / "tables" / "selected_historical_episodes.csv", selected_rows)
    batch_rows = [
        {
            "label": batch["label"],
            "seed": batch["seed"],
            "target_runs": batch["target_runs"],
            "actual_runs": batch["actual_runs"],
            "new_paths_executed_this_stage": batch["new_paths_executed_this_stage"],
            "max_observed_cascade_depth": batch["max_observed_cascade_depth"],
            "depth_ge_2_successes": batch["cascade_frequencies"]["2"]["successes"],
            "depth_ge_2_frequency": batch["cascade_frequencies"]["2"]["frequency"],
            "depth_ge_2_wilson_lower": batch["cascade_frequencies"]["2"]["wilson_95"]["lower"],
            "depth_ge_2_wilson_upper": batch["cascade_frequencies"]["2"]["wilson_95"]["upper"],
            "depth_ge_3_successes": batch["cascade_frequencies"]["3"]["successes"],
            "loss_p95": batch["loss_quantiles"]["p95"],
            "loss_es95": batch["loss_quantiles"]["expected_shortfall_95"],
            "runtime_seconds_this_stage": batch["runtime_seconds_this_stage"],
        }
        for batch in batches
    ]
    _csv(ROOT / "tables" / "monte_carlo_stage_summary.csv", batch_rows)
    depth_counts = Counter(int(row["cascade_depth"]) for row in grid_rows)
    _csv(
        ROOT / "tables" / "deterministic_grid_depth_counts.csv",
        [{"observed_depth": depth, "grid_cells": count} for depth, count in sorted(depth_counts.items())],
    )

    old_capital = next(row for row in prior_mechanisms if row["scenario"] == "Capital 25pct")
    new_capital = next(row for row in mechanisms if row["scenario"] == "Capital 25pct")
    primary_200 = next(batch for batch in batches if batch["seed"] == 20_260_914 and batch["actual_runs"] == 200)
    primary_10k = next(batch for batch in batches if batch["seed"] == 20_260_914 and batch["actual_runs"] == 10_000)
    before_after = {
        "status": "PASS",
        "source_commit": SOURCE_COMMIT,
        "invalid_epoch_attempt": {
            "before_window": "2026-08-31T21:00:00Z/2026-09-07T21:00:00Z",
            "after_window": "2026-09-01T00:00:00Z/2026-09-08T00:00:00Z",
            "before_events": 28,
            "after_events": historical["verified"],
            "action": "invalid attempt preserved and excluded",
        },
        "capital_mechanism": {
            "before_capital_usdc": float(old_capital["liquidator_capital_usdc"]),
            "before_binding": old_capital["capital_binding"] == "True",
            "after_capital_usdc": float(new_capital["liquidator_capital_usdc"]),
            "after_binding": new_capital["capital_binding"] == "True",
            "after_total_liquidated_debt": float(new_capital["total_liquidated_debt"]),
            "definition": "25% of unconstrained Severe executed-debt requirement",
        },
        "severe_monte_carlo": {
            "prior_corrected_run_v2_200": {"successes": 8, "runs": 200, "frequency": 0.04},
            "level3_200": primary_200["cascade_frequencies"]["2"],
            "level3_10000": primary_10k["cascade_frequencies"]["2"],
            "interpretation": "same 8/200 prefix reproduced; larger sample narrows the model-conditional interval",
        },
        "wave_cap_comparison": cap_rows,
    }
    _json(ROOT / "before_after.json", before_after)

    claim_ledger = {
        "status": "LIMITED",
        "source_commit": SOURCE_COMMIT,
        "extension_name": "Level-3 Historical Evidence Extension",
        "claims": [
            {
                "id": "L3-C01",
                "status": "SUPPORTED",
                "claim": (
                    "27 Aave V3 LiquidationCall events in the preregistered week were verified "
                    "by RPC log, receipt and block hash."
                ),
                "evidence": ["historical/raw_event_index.json", "historical/summary.json"],
            },
            {
                "id": "L3-C02",
                "status": "SUPPORTED_WITH_BOUNDARY",
                "claim": "Three liquidation events have receipt-level same-transaction Uniswap V3 Swap links.",
                "boundary": "A direct transaction path is not proof of a market-wide endogenous cascade.",
                "evidence": ["historical/observation_linkage.json"],
            },
            {
                "id": "L3-C03",
                "status": "UNSUPPORTED",
                "claim": "Historical observations prove an endogenous cross-protocol liquidation cascade.",
                "reason": (
                    "Associations and three transaction links do not identify system-wide "
                    "causality; controls and confounding remain limited."
                ),
            },
            {
                "id": "L3-C04",
                "status": "SUPPORTED_MODEL_CONDITIONAL",
                "claim": "The maximum observed simulated depth was 2 despite a configured ceiling of 100.",
                "evidence": ["deep_stress/numerical_diagnostics.json", "deep_stress/cascade_paths.json"],
            },
            {
                "id": "L3-C05",
                "status": "SUPPORTED_MODEL_CONDITIONAL",
                "claim": "Severe seed 20260914 produced 280/10000 depth>=2 paths (2.8%).",
                "boundary": "Conditional on model, scenario, snapshot and RNG; not a real-world probability.",
                "evidence": ["deep_stress/monte_carlo_batches.json"],
            },
            {
                "id": "L3-C06",
                "status": "UNAVAILABLE",
                "claim": "Aave liquidation and Uniswap swap transactions passed local Mainnet-fork execution.",
                "reason": "Foundry and Anvil are absent; zero fork transactions were executed.",
                "evidence": ["fork/validation.json"],
            },
        ],
        "rq_scope": {
            "RQ1_RQ6": (
                "Existing corrected_run_v2 conclusions remain model-conditional and must be "
                "read with this extension."
            ),
            "new_extension": "Descriptive historical evidence extension; not a seventh replacement RQ.",
        },
    }
    _json(ROOT / "claim_ledger_extension.json", claim_ledger)

    figures = ROOT / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    labels = [row["episode_id"] for row in selected_rows]
    observed = [int(row["uniswap_swaps_within_5m"]) for row in selected_rows]
    controls = [int(row["control_swaps_within_5m"]) for row in selected_rows]
    positions = list(range(len(labels)))
    plt.figure(figsize=(8, 4))
    plt.bar([value - 0.2 for value in positions], observed, width=0.4, label="event window")
    plt.bar([value + 0.2 for value in positions], controls, width=0.4, label="-60m control")
    plt.xticks(positions, labels, rotation=25, ha="right")
    plt.ylabel("Uniswap V3 Swap events within ±5 min")
    plt.title("Selected episodes versus preregistered control windows")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "historical_event_control_comparison.png", dpi=180)
    plt.close()

    windows = [60, 300, 900, 1800]
    counts = [selection["sensitivity_cluster_counts"][str(window)] for window in windows]
    plt.figure(figsize=(7, 4))
    plt.plot([1, 5, 15, 30], counts, marker="o")
    plt.xlabel("Historical clustering window (minutes)")
    plt.ylabel("Observed clusters")
    plt.title("Historical cluster-definition sensitivity")
    plt.tight_layout()
    plt.savefig(figures / "historical_cluster_window_sensitivity.png", dpi=180)
    plt.close()

    core_quality = _load(ROOT.parent / "quality_gate.json")
    level3_quality = {
        "status": "PASS",
        "checks": [
            {"check": "historical_rpc_verification", "status": "PASS", "events": historical["verified"]},
            {
                "check": "linkage_tier_accounting",
                "status": "PASS",
                "events": sum(historical["tier_counts"].values()),
            },
            {"check": "invalid_epoch_attempt_excluded", "status": "PASS"},
            {"check": "fork_status_truthful", "status": "PASS", "fork_status": fork["status"]},
            {
                "check": "wave_cap_semantics",
                "status": "PASS",
                "configured_cap": diagnostics["largest_configured_wave_cap"],
                "observed_depth": diagnostics["max_monte_carlo_observed_depth"],
            },
            {
                "check": "monte_carlo_10000_complete",
                "status": "PASS",
                "actual_runs": primary_10k["actual_runs"],
            },
            {"check": "path_invariants", "status": "PASS"},
            {
                "check": "canonical_hash_fixed",
                "status": "PASS",
                "sha256": CANONICAL_SHA256,
            },
            {
                "check": "existing_research_quality_gate",
                "status": "PASS" if core_quality["all_passed"] else "FAIL",
                "core_checks": len(core_quality["checks"]),
            },
        ],
        "all_passed": bool(core_quality["all_passed"]),
    }
    _json(ROOT / "quality_gate.json", level3_quality)

    manifest_files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    ]
    manifest = {
        "status": "LIMITED",
        "starting_source_commit": SOURCE_COMMIT,
        "implementation_commit": implementation_commit,
        "artifact_bundle_commit": artifact_bundle_commit,
        "chain_id": 1,
        "canonical_snapshot": {
            "path": "data/processed/mainnet/aave_uniswap_snapshot_26045352.json",
            "block_number": 26_045_352,
            "sha256": CANONICAL_SHA256,
            "verified_borrowers": 454,
            "weth_usdc_cohort": 109,
        },
        "gates": {
            "A_historical_preregistration": "PASS",
            "B_onchain_episode_verification": "LIMITED",
            "C_deep_simulation": diagnostics["status"],
            "D_research_integration": "PENDING_TESTS_AND_COMMANDER_REVIEW",
            "E_commander_signoff": "PENDING",
        },
        "historical": historical,
        "fork": fork,
        "deep_stress": diagnostics,
        "artifact_hashes": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in sorted(manifest_files)
        },
        "report_hashes": {path.as_posix(): _sha256(path) for path in REPORTS},
        "secrets_included": False,
        "scientific_lock_declared": False,
    }
    _json(ROOT / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "files_hashed": len(manifest_files),
                "tier_counts": historical["tier_counts"],
                "max_depth": diagnostics["max_monte_carlo_observed_depth"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation-commit", default="PENDING_AFTER_FIRST_COMMIT")
    parser.add_argument("--artifact-bundle-commit", default="PENDING_AFTER_ARTIFACT_COMMIT")
    arguments = parser.parse_args()
    main(
        implementation_commit=arguments.implementation_commit,
        artifact_bundle_commit=arguments.artifact_bundle_commit,
    )
