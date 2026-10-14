from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path("data/processed/research_final/scientific_integration_v1")
FROZEN = Path("data/processed/research_final/frozen_v3")
ORACLE = Path("data/processed/research_final/oracle_transmission_diagnostic_v1")
CANONICAL = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
CANONICAL_SHA = "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"
POLICIES = {
    "A_ADVERSE_PASS_THROUGH",
    "B_REFERENCE_ONLY",
    "C_WEAK_LAGGED_SMOOTHED_PROXY",
    "C_MODERATE_LAGGED_SMOOTHED_PROXY",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_integration_manifest_resolves_and_preserves_locked_inputs() -> None:
    manifest = _load(ROOT / "manifest.json")
    assert manifest["status"] == "READY_FOR_COMMANDER_REVIEW"
    assert manifest["decision_is_proposed_not_commander_granted"] is True
    assert manifest["scientific_content_lock_declared"] is False
    assert manifest["large_monte_carlo_rerun"] is False
    assert _sha(CANONICAL) == CANONICAL_SHA
    assert manifest["input_hashes"]["canonical_snapshot"] == CANONICAL_SHA
    assert manifest["input_hashes"]["frozen_v3_manifest"] == _sha(FROZEN / "manifest.json")
    assert manifest["input_hashes"]["oracle_manifest"] == _sha(ORACLE / "manifest.json")
    for relative, expected in manifest["artifact_hashes"].items():
        assert _sha(ROOT / relative) == expected
        catalog_path = f"{ROOT.as_posix()}/{relative}"
        assert manifest["artifact_catalog"][catalog_path]["artifact_sha256"] == expected
        assert manifest["artifact_catalog"][catalog_path]["exact_input_hashes"] == manifest["input_hashes"]
    for relative, expected in manifest["report_hashes"].items():
        assert _sha(Path(relative)) == expected
        assert manifest["artifact_catalog"][relative]["artifact_sha256"] == expected


def test_targeted_replay_and_policy_reconciliation_are_exact() -> None:
    validation = _load(ROOT / "integration_validation_report.json")
    assert validation["status"] == "PASS"
    assert not validation["failed_checks"]
    assert all(validation["checks"].values())
    assert validation["replay_validation"] == {
        "borrower_rows": 18 * 4 * 454,
        "event_rows": 2186,
        "hf_trace_matches": 18 * 4 * 454,
        "new_eligibility_count_matches": 72,
        "replay_hash_matches": 72,
        "targeted_runs": 72,
    }
    summary = _rows(ROOT / "eligible_vs_executed_summary.csv")
    assert len(summary) == 72
    assert len({row["summary_result_id"] for row in summary}) == 72
    assert Counter(row["policy_id"] for row in summary) == {policy: 18 for policy in POLICIES}
    expected = {
        "A_ADVERSE_PASS_THROUGH": (35, 14, 21, Decimal("58574.91415500")),
        "B_REFERENCE_ONLY": (0, 0, 0, Decimal("0")),
        "C_WEAK_LAGGED_SMOOTHED_PROXY": (6, 0, 6, Decimal("0")),
        "C_MODERATE_LAGGED_SMOOTHED_PROXY": (11, 2, 9, Decimal("4952.07991200")),
    }
    for policy, (newly, executed, skipped, debt) in expected.items():
        rows = [row for row in summary if row["policy_id"] == policy]
        assert sum(int(row["newly_eligible_after_wave1_count"]) for row in rows) == newly
        assert sum(int(row["newly_eligible_executed_wave2_count"]) for row in rows) == executed
        assert sum(int(row["newly_eligible_skipped_count"]) for row in rows) == skipped
        assert sum(Decimal(row["positive_debt_repaid_wave2_usdc"]) for row in rows) == debt


def test_eligible_attempted_executed_accounting_has_event_level_proof() -> None:
    audit = _rows(ROOT / "eligible_vs_executed_audit.csv")
    assert len(audit) == 18 * 4 * 454
    assert len({row["audit_row_id"] for row in audit}) == len(audit)
    newly = [row for row in audit if row["newly_eligible_after_wave1"] == "True"]
    executed = [row for row in newly if row["executed_positive_debt_wave2"] == "True"]
    skipped = [row for row in newly if row["executed_positive_debt_wave2"] == "False"]
    assert len(newly) == 52
    assert len(executed) == 16
    assert len(skipped) == 36
    assert all(row["attempted_after_wave1"] == "True" for row in newly)
    assert all(Decimal(row["positive_debt_repaid_wave2_usdc"]) > 0 for row in executed)
    assert all(row["skip_reasons_after_wave1"] == "NOT_ELIGIBLE" for row in skipped)
    assert all(
        row["resolved_skip_reasons_after_wave1"] == "NO_MODELLED_USDC_DEBT"
        and Decimal(row["post_wave1_usdc_debt"]) == 0
        for row in skipped
    )
    events = {
        row["event_id"]: row
        for row in (
            json.loads(line)
            for line in (ROOT / "targeted_event_trace.jsonl").read_text(encoding="utf-8").splitlines()
        )
    }
    assert len(events) == 2186
    for row in newly:
        locators = row["event_locators"].split("|")
        assert locators and all(locator in events for locator in locators)
        if row["executed_positive_debt_wave2"] == "True":
            assert any(
                events[locator]["event_type"] == "LIQUIDATION"
                and events[locator]["wave"] == 2
                and Decimal(events[locator]["debt_repaid_usdc"]) > 0
                for locator in locators
            )


def test_claim_graph_and_six_rq_identity_are_resolved() -> None:
    frozen_ids = {row["result_id"] for row in _load(FROZEN / "results_registry.json")["results"]}
    integration_ids = {
        row["result_id"] for row in _load(ROOT / "integration_result_registry.json")["results"]
    }
    claims = _load(ROOT / "claim_to_result_registry.json")["claims"]
    assert len({claim["claim_id"] for claim in claims}) == len(claims)
    assert all(set(claim["result_ids"]) <= frozen_ids | integration_ids for claim in claims)
    frozen_sources = _load(FROZEN / "evidence_source_matrix.json")
    integration_sources = _load(ROOT / "table_figure_registry.json")
    table_figure_ids = {
        row["table_id"] for row in frozen_sources["table_registry"]
    } | {
        row["figure_id"] for row in frozen_sources["figure_registry"]
    } | {
        row["table_id"] for row in integration_sources["tables"]
    } | {
        row["figure_id"] for row in integration_sources["figures"]
    }
    assert all(set(claim["table_figure"]) <= table_figure_ids for claim in claims)
    status = {claim["claim_id"]: claim["status"] for claim in claims}
    assert status["CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT"] == "UNSUPPORTED"
    assert status["CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION"] == "UNSUPPORTED"
    assert status["CL_FROZEN_RQ1_UNQUALIFIED_WORDING"] == "REQUIRES_CORRECTION"
    assert status["CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING"] == "REQUIRES_CORRECTION"
    rq_rows = _load(ROOT / "six_rq_evidence_matrix.json")["research_questions"]
    assert [row["rq"] for row in rq_rows] == [f"RQ{index}" for index in range(1, 7)]
    assert [row["question"] for row in rq_rows] == [
        "Điều kiện và ngưỡng xuất hiện thanh lý dây chuyền.",
        "Vai trò thanh khoản DEX.",
        "Gas, vốn, công suất và độ trễ thanh lý.",
        "Arbitrage và phục hồi giá.",
        "Mất neo stablecoin và định giá nợ USDC.",
        "Đánh đổi LTV, liquidation threshold, liquidation bonus.",
    ]


def test_integration_artifacts_expose_no_raw_addresses_or_secrets() -> None:
    paths = [*ROOT.rglob("*.json"), *ROOT.rglob("*.jsonl"), *ROOT.rglob("*.csv")]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert re.search(r"0x[a-fA-F0-9]{40}\b", text) is None
    assert re.search(r"(?i)(api[_-]?key|authorization)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{12,}", text) is None
