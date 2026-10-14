from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path("data/processed/research_final/level3_p1_targeted_repair")
CANONICAL = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
CANONICAL_SHA256 = "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_independent_census_discloses_graph_omission() -> None:
    census = _load(ROOT / "historical" / "census_reconciliation.json")
    assert census["census_execution_status"] == "PASS"
    assert census["reconciliation_status"] == "DISCREPANCY"
    assert census["graph_candidate_count"] == census["matched_count"] == 27
    assert census["rpc_census_count"] == 28
    assert len(census["graph_only"]) == 0
    assert len(census["rpc_only"]) == len(census["rpc_only_details"]) == 1
    detail = census["rpc_only_details"][0]
    assert detail["receipt_status"] == 1
    assert detail["collateral_asset"] == "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    assert detail["debt_asset"] == "0xdac17f958d2ee523a2206206994597c13d831ec7"
    with gzip.open(ROOT / "historical" / "census_cache.json.gz", "rt", encoding="utf-8") as handle:
        cache = json.load(handle)
    assert len(cache["chunks"]) == 5_022
    assert cache["chunks"][0]["from_block"] == census["start_block"]
    assert cache["chunks"][-1]["to_block"] == census["end_block"]
    assert all(
        right["from_block"] == left["to_block"] + 1
        for left, right in zip(cache["chunks"], cache["chunks"][1:], strict=False)
    )


def test_linkage_requires_an_exact_ordered_transfer_path() -> None:
    linkage = _load(ROOT / "historical" / "linkage_route_audit.json")
    assert linkage["tier_counts"] == {
        "DIRECT_TRANSFER_PATH_VERIFIED": 1,
        "SAME_TRANSACTION_CO_OCCURRENCE": 2,
        "SAME_BLOCK_ASSOCIATION": 23,
        "TIME_WINDOW_ASSOCIATION": 1,
    }
    direct = [
        row
        for row in linkage["route_audits"]
        if row["verified_transfer_swap_ids"]
    ]
    assert len(direct) == 1
    route = next(
        check for check in direct[0]["swap_route_checks"] if check["ordered_exact_transfer_path"]
    )
    assert route["exact_amount_match"] is True
    assert len(route["transfer_path"]) == 2
    assert all(item["amount_raw"] == route["liquidated_collateral_raw"] for item in route["transfer_path"])
    assert all(item["status"] == "UNAVAILABLE" for item in linkage["trace_status_by_transaction"].values())


def test_control_windows_are_complete_and_liquidation_free() -> None:
    controls = _load(ROOT / "historical" / "control_window_audit.json")
    assert controls["status"] == "PASS"
    assert controls["all_30m_controls_liquidation_free"] is True
    assert controls["control_exclusions"] == []
    assert len(controls["rows"]) == 40
    assert all(row["all_four_pool_block_ranges_scanned"] for row in controls["rows"])
    assert all(row["missing_from_locked_index"] == 0 for row in controls["rows"])
    assert all(row["extra_in_locked_index"] == 0 for row in controls["rows"])
    control_rows = [row for row in controls["rows"] if row["window_kind"] == "control"]
    assert len(control_rows) == 20
    assert all(row["liquidation_free_control"] for row in control_rows)


def test_checkpoint_counts_reproduction_and_wave2_semantics() -> None:
    checkpoints = _load(ROOT / "monte_carlo" / "checkpoint_validation.json")
    reproduction = _load(ROOT / "monte_carlo" / "sample_reproduction.json")
    wave2 = _load(ROOT / "monte_carlo" / "wave2_eligibility_audit.json")
    assert checkpoints["status"] == "PASS"
    assert checkpoints["independent_batch_unique_path_count"] == 13_000
    assert checkpoints["duplicate_batch_identities"] == []
    accounting = checkpoints["accounting_correction"]
    assert accounting["large_paths_executed_in_this_repair_invocation"] == 0
    assert accounting["reused_checkpoint_count_for_primary_10k"] == 10_000
    assert accounting["historical_execution_duration_seconds"].startswith("UNAVAILABLE")
    assert reproduction["status"] == "PASS"
    assert len(reproduction["sample_rows"]) == 21
    assert all(row["exact_match"] for row in reproduction["sample_rows"])
    assert wave2["status"] == "PASS"
    deterministic_rows = wave2["deterministic_case"]["wave2_borrowers"]
    assert deterministic_rows
    assert all(row["direct_shock_not_eligible"] for row in deterministic_rows)
    assert all(row["newly_eligible_after_prior_wave"] for row in deterministic_rows)
    assert len(wave2["stratified_monte_carlo_cases"]) == 10
    assert all(row["all_genuinely_newly_eligible"] for row in wave2["stratified_monte_carlo_cases"])


def test_locked_canonical_and_repair_manifest_hashes() -> None:
    assert hashlib.sha256(CANONICAL.read_bytes()).hexdigest() == CANONICAL_SHA256
    manifest_path = ROOT / "manifest.json"
    if not manifest_path.exists():
        return
    manifest = _load(manifest_path)
    assert all(manifest["quality_gate"].values())
    for relative, expected in manifest["artifact_hashes"].items():
        path = ROOT / relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    for relative, expected in manifest["report_hashes"].items():
        path = Path(relative)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
