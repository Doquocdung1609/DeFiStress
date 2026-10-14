from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path("data/processed/research_final/level3_p1_targeted_repair")
REPORTS = (
    Path("docs/research_final/LEVEL3_P1_TARGETED_REPAIR_REPORT.md"),
    Path("docs/research_final/SCIENTIFIC_VALIDATION_AUDIT.md"),
)
LOCKED_LEVEL3 = Path("data/processed/research_final/level3_extension")
CANONICAL = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
EXPECTED_CANONICAL_SHA256 = "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(
    root: Path,
    *,
    implementation_commit: str,
    artifact_bundle_commit: str,
) -> dict[str, Any]:
    summary = _load(root / "summary.json")
    census = _load(root / "historical" / "census_reconciliation.json")
    linkage = _load(root / "historical" / "linkage_route_audit.json")
    controls = _load(root / "historical" / "control_window_audit.json")
    checkpoints = _load(root / "monte_carlo" / "checkpoint_validation.json")
    reproduction = _load(root / "monte_carlo" / "sample_reproduction.json")
    wave2 = _load(root / "monte_carlo" / "wave2_eligibility_audit.json")
    canonical_hash = _sha256(CANONICAL)
    checks = {
        "canonical_snapshot_unchanged": canonical_hash == EXPECTED_CANONICAL_SHA256,
        "rpc_census_completed": census["census_execution_status"] == "PASS",
        "graph_discrepancy_disclosed": (
            census["rpc_census_count"] == 28
            and census["graph_candidate_count"] == 27
            and len(census["rpc_only"]) == 1
        ),
        "linkage_semantics_repaired": linkage["tier_counts"]
        == {
            "DIRECT_TRANSFER_PATH_VERIFIED": 1,
            "SAME_TRANSACTION_CO_OCCURRENCE": 2,
            "SAME_BLOCK_ASSOCIATION": 23,
            "TIME_WINDOW_ASSOCIATION": 1,
        },
        "control_windows_complete": controls["status"] == "PASS",
        "all_controls_liquidation_free": controls["all_30m_controls_liquidation_free"],
        "checkpoint_validation_passed": checkpoints["status"] == "PASS",
        "independent_paths_equal_13000": (
            checkpoints["independent_batch_unique_path_count"] == 13_000
        ),
        "sample_reproduction_passed": reproduction["status"] == "PASS",
        "wave2_eligibility_passed": wave2["status"] == "PASS",
        "large_research_not_rerun": summary["large_research_rerun"] is False,
        "fork_still_unavailable": summary["fork_status"] == "UNAVAILABLE_UNCHANGED",
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"P1 evidence quality gate failed: {failed}")
    artifact_hashes = {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }
    report_hashes = {path.as_posix(): _sha256(path) for path in REPORTS}
    manifest = {
        "status": "LIMITED",
        "review_state": "READY_FOR_COMMANDER_RE_REVIEW_NOT_SCIENTIFIC_LOCK",
        "source_head": summary["source_head"],
        "implementation_commit": implementation_commit,
        "artifact_bundle_commit": artifact_bundle_commit,
        "canonical_snapshot_sha256": canonical_hash,
        "locked_level3_manifest_sha256": _sha256(LOCKED_LEVEL3 / "manifest.json"),
        "artifact_hashes": artifact_hashes,
        "report_hashes": report_hashes,
        "quality_gate": checks,
        "key_corrections": {
            "graph_candidates": 27,
            "rpc_census_events": 28,
            "rpc_only_events": 1,
            "linkage_tier_counts": linkage["tier_counts"],
            "validated_independent_paths": 13_000,
            "large_paths_executed_in_repair": 0,
            "sample_paths_reproduced": len(reproduction["sample_rows"]),
        },
        "scientific_boundaries": {
            "historical_causality": "NOT_ESTABLISHED",
            "fork_transactions": "UNAVAILABLE",
            "haircuts_90_95": "UNOBSERVED_COUNTERFACTUAL_TAILS",
            "composite_tail_quantity": "NOT_REALIZED_LOSS_OR_MARKET_ES",
        },
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--artifact-bundle-commit", required=True)
    args = parser.parse_args()
    manifest = build(
        args.root,
        implementation_commit=args.implementation_commit,
        artifact_bundle_commit=args.artifact_bundle_commit,
    )
    print(json.dumps({"status": manifest["status"], "quality_gate": manifest["quality_gate"]}, indent=2))


if __name__ == "__main__":
    main()
