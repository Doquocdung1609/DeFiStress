from __future__ import annotations

import json
from pathlib import Path

ROOT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "research_final"
    / "scientific_premerge_audit_v1"
)


def _audit() -> dict[str, object]:
    return json.loads((ROOT / "audit_results.json").read_text(encoding="utf-8"))


def test_independent_premerge_checks_pass() -> None:
    audit = _audit()
    assert audit["status"] == "PASS_WITH_DISCLOSED_EOL_HASH_SEMANTICS"
    assert audit["failed_checks"] == []
    assert all(audit["checks"].values())
    assert audit["row_counts"] == {
        "borrower_case_policy_rows": 32_688,
        "claims": 13,
        "controls_case_policy_rows": 16,
        "event_rows": 2_186,
        "summary_rows": 72,
    }


def test_eligible_route_and_execution_reconciliation_is_frozen() -> None:
    rows = _audit()["eligible_attempted_executed"]
    expected = {
        "A_ADVERSE_PASS_THROUGH": (35, 35, 14, 21, "58574.91415500"),
        "B_REFERENCE_ONLY": (0, 0, 0, 0, "0"),
        "C_WEAK_LAGGED_SMOOTHED_PROXY": (6, 6, 0, 6, "0"),
        "C_MODERATE_LAGGED_SMOOTHED_PROXY": (11, 11, 2, 9, "4952.07991200"),
    }
    for policy, values in expected.items():
        row = rows[policy]
        assert (
            row["newly_eligible"],
            row["attempted_later"],
            row["executed_wave2"],
            row["newly_route_ineligible"],
            row["positive_debt_repaid_wave2_usdc"],
        ) == values


def test_hash_semantics_are_explicit_and_content_equivalent() -> None:
    integrity = _audit()["hash_integrity"]
    worktree = integrity["worktree_byte_sha256"]
    blobs = integrity["repository_git_blob_sha256_lf"]
    equivalent = integrity[
        "worktree_equals_git_blob_after_crlf_to_lf_normalization"
    ]
    assert worktree["canonical_snapshot"] == (
        "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"
    )
    assert blobs["canonical_snapshot_at_frozen_head"] == (
        "76dae833c5b1a6e620cf116e332f1f47c53454a1f3530a02fefacd800cb3b329"
    )
    assert all(equivalent.values())
    assert worktree["canonical_snapshot"] != blobs["canonical_snapshot_at_frozen_head"]


def test_predeclared_samples_join_hf_decision_and_event() -> None:
    samples = _audit()["specific_samples"]
    executed = samples["newly_eligible_executed"]
    skipped = samples["newly_eligible_skipped"]
    moderate = samples["c_moderate_executed_wave2"]

    assert executed["route_eligible"] is True
    assert executed["executed_wave2"] is True
    assert executed["events"][0]["debt_repaid_usdc"] == "15356.18268950"

    assert skipped["portfolio_newly_eligible"] is True
    assert skipped["route_eligible"] is False
    assert skipped["usdc_debt"] == "0.0"
    assert skipped["resolved_skip_reason"] == "NO_MODELLED_USDC_DEBT"

    assert moderate["executed_wave2"] is True
    assert moderate["events"][0]["debt_repaid_usdc"] == "2476.03995600"
