from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path("data/processed/research_final/final_accepted_claims_v1")
SOURCE_HEAD = "6560f799f81223cd4a720bd3f6b798aeef1732b9"
RQ_ORDER = [f"RQ{index}" for index in range(1, 7)]
RQ_QUESTIONS = [
    "Điều kiện và ngưỡng xuất hiện thanh lý dây chuyền.",
    "Vai trò thanh khoản DEX.",
    "Gas, vốn, công suất và độ trễ thanh lý.",
    "Arbitrage và phục hồi giá.",
    "Mất neo stablecoin và định giá nợ USDC.",
    "Đánh đổi LTV, liquidation threshold, liquidation bonus.",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str, binary: bool = False) -> bytes | str:
    value = subprocess.run(["git", *args], check=True, capture_output=True).stdout
    return value if binary else value.decode("utf-8").strip()


def test_manifest_has_no_self_hash_and_resolves_all_outputs() -> None:
    manifest = _load(ROOT / "manifest.json")
    assert manifest["status"] == "FINAL_REGISTRY_READY_FOR_COMMANDER_REVIEW"
    assert manifest["source_integration_head"] == SOURCE_HEAD
    assert manifest["output_commit"] == "RECORDED_IN_GIT_HANDOFF_NOT_SELF_EMBEDDED"
    assert manifest["self_hash_excluded"] is True
    assert manifest["manifest_hash_embedded"] is False
    assert "manifest.json" not in manifest["artifact_hashes"]
    assert manifest["scientific_content_lock_declared"] is False
    assert manifest["large_monte_carlo_rerun"] is False
    assert manifest["model_retuned"] is False
    for relative, expected in manifest["artifact_hashes"].items():
        assert _sha(ROOT / relative) == expected
    for relative, expected in manifest["report_hashes"].items():
        assert _sha(Path(relative)) == expected


def test_two_namespaces_are_complete_and_unique() -> None:
    records = _load(ROOT / "accepted_claims_registry.json")["records"]
    scholarly = [row for row in records if row["namespace"] == "SCHOLARLY_P2"]
    integration = [row for row in records if row["namespace"] == "INTEGRATION_SCIENTIFIC"]
    assert len(records) == 48
    assert len(scholarly) == 35
    assert len(integration) == 13
    assert {row["registry_id"] for row in scholarly} == {
        f"P2:C{index:02d}" for index in range(1, 36)
    }
    source_integration = _load(
        Path("data/processed/research_final/scientific_integration_v1/claim_to_result_registry.json")
    )["claims"]
    assert {row["original_claim_id"] for row in integration} == {
        row["claim_id"] for row in source_integration
    }
    assert len({row["registry_id"] for row in records}) == 48


def test_six_rq_matrix_preserves_questions_and_limitations() -> None:
    rows = _load(ROOT / "six_rq_accepted_claims_matrix.json")["research_questions"]
    assert [row["rq"] for row in rows] == RQ_ORDER
    assert [row["research_question"] for row in rows] == RQ_QUESTIONS
    assert all(row["required_limitations"] for row in rows)
    assert all(row["results_prohibited_from_extrapolation"] for row in rows)
    assert all(row["scientific_decision_status"] == "ACCEPTED_WITH_LIMITATIONS" for row in rows)
    assert "funded executable swap" in rows[3]["results_prohibited_from_extrapolation"]
    assert "settlement" in rows[4]["results_prohibited_from_extrapolation"]
    assert "LTV" in rows[5]["recommended_vietnamese_conclusion"]


def test_claim_crosswalk_result_and_table_ids_resolve() -> None:
    frozen = _load(Path("data/processed/research_final/frozen_v3/results_registry.json"))
    integration = _load(
        Path("data/processed/research_final/scientific_integration_v1/integration_result_registry.json")
    )
    result_ids = {
        *[row["result_id"] for row in frozen["results"]],
        *[row["result_id"] for row in integration["results"]],
    }
    frozen_sources = _load(
        Path("data/processed/research_final/frozen_v3/evidence_source_matrix.json")
    )
    integration_sources = _load(
        Path("data/processed/research_final/scientific_integration_v1/table_figure_registry.json")
    )
    table_figure_ids = {
        *[row["table_id"] for row in frozen_sources["table_registry"]],
        *[row["figure_id"] for row in frozen_sources["figure_registry"]],
        *[row["table_id"] for row in integration_sources["tables"]],
        *[row["figure_id"] for row in integration_sources["figures"]],
    }
    rows = _load(ROOT / "claim_evidence_crosswalk.json")["rows"]
    assert all(set(row["scientific_result_ids"]) <= result_ids for row in rows)
    assert all(set(row["table_figure_ids"]) <= table_figure_ids for row in rows)
    assert "INT_T01_ELIGIBLE_VS_EXECUTED" in table_figure_ids


def test_source_provenance_hashes_exact_git_objects() -> None:
    provenance = _load(ROOT / "source_provenance_registry.json")
    assert provenance["source_integration_head"] == SOURCE_HEAD
    assert "LF" in provenance["hash_semantics"]["sha256"]
    assert "CRLF" in provenance["hash_semantics"]["windows_checkout"]
    assert any(
        source["path"].endswith("eligible_vs_executed_audit.csv")
        for source in provenance["sources"]
    )
    for source in provenance["sources"]:
        spec = f"{source['source_commit']}:{source['path']}"
        raw = _git("show", spec, binary=True)
        assert isinstance(raw, bytes)
        assert hashlib.sha256(raw).hexdigest() == source["sha256"]
        assert _git("rev-parse", spec) == source["git_blob_sha"]
        assert len(raw) == source["size_bytes"]


def test_locked_sources_remain_byte_identical_to_integrated_head() -> None:
    provenance = _load(ROOT / "source_provenance_registry.json")
    for name, expected in provenance["locked_tree_ids"].items():
        path = {
            "frozen_v3": "data/processed/research_final/frozen_v3",
            "oracle_diagnostic_v1": "data/processed/research_final/oracle_transmission_diagnostic_v1",
            "scientific_integration_v1": "data/processed/research_final/scientific_integration_v1",
        }[name]
        assert _git("rev-parse", f"HEAD:{path}") == expected
        assert _git("rev-parse", f"{SOURCE_HEAD}:{path}") == expected
    for path, expected in provenance["locked_p2_blob_ids"].items():
        assert _git("rev-parse", f"HEAD:{path}") == expected
        assert _git("rev-parse", f"{SOURCE_HEAD}:{path}") == expected


def test_numerical_claim_lock_is_exact_and_scoped() -> None:
    numerical = _load(ROOT / "validation_report.json")["numerical_claim_lock"]
    assert numerical["deterministic_depth2_retained_of_4"] == {
        "A": 4,
        "B": 0,
        "C_MODERATE": 0,
        "C_WEAK": 0,
    }
    assert numerical["targeted_mc_depth2_retained_of_10"] == {
        "A": 10,
        "B": 0,
        "C_MODERATE": 2,
        "C_WEAK": 0,
    }
    assert numerical["eligible_vs_executed"] == {
        "A": {"newly_eligible": 35, "executed_wave2": 14, "skipped": 21},
        "B": {"newly_eligible": 0, "executed_wave2": 0, "skipped": 0},
        "C_MODERATE": {"newly_eligible": 11, "executed_wave2": 2, "skipped": 9},
        "C_WEAK": {"newly_eligible": 6, "executed_wave2": 0, "skipped": 6},
    }
    assert numerical["severe_policy_a"]["depth_gte_2"] == 280
    assert numerical["severe_policy_a"]["denominator"] == 10000
    assert numerical["historical"] == {
        "pool_events": 28,
        "graph_matched_events": 27,
        "tiers_direct_same_tx_same_block_time": [1, 2, 23, 1],
        "causal_contagion_established": False,
    }
    assert numerical["terra_negative"]["successful_oos_forecast_established"] is False


def test_unsupported_and_superseded_claims_are_not_promoted() -> None:
    records = _load(ROOT / "accepted_claims_registry.json")["records"]
    status = {row["original_claim_id"]: row["final_gate_status"] for row in records}
    assert status["CL_FROZEN_RQ1_UNQUALIFIED_WORDING"] == "REJECTED_AS_WORDED_SUPERSEDED"
    assert status["CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING"] == "REJECTED_AS_WORDED_SUPERSEDED"
    assert status["CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT"] == "UNSUPPORTED"
    assert status["CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION"] == "UNSUPPORTED"
    for row in records:
        if row["final_gate_status"] == "UNSUPPORTED":
            assert row["not_established_semantics"].startswith("No affirmative")
        if row["namespace"] == "SCHOLARLY_P2" and row["not_applicable_semantics"].startswith("No project"):
            assert "not a numerical PASS" in row["not_applicable_semantics"]


def test_validation_gates_and_readiness_are_proposed_not_granted() -> None:
    validation = _load(ROOT / "validation_report.json")
    readiness = _load(ROOT / "scientific_lock_readiness.json")
    assert validation["status"] == "PASS"
    assert not validation["failed_gates"]
    assert all(validation["gates"].values())
    assert validation["metrics"]["active_locator_hash_checks"] == validation["metrics"][
        "active_locator_hash_matches"
    ]
    assert validation["locator_hash_mismatches"] == []
    assert readiness["proposed_status"] == "FINAL_REGISTRY_READY_FOR_COMMANDER_REVIEW"
    assert readiness["scientific_content_lock_declared"] is False
    assert readiness["commander_decision_required"] is True
    assert readiness["blocking_conflicts"] == []
    assert len(readiness["rejected_or_unsupported_integration_records"]) == 4


def test_registry_exposes_no_raw_wallet_or_secret() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.glob("*.json"))
    assert re.search(r"0x[a-fA-F0-9]{40}\b", text) is None
    assert re.search(
        r"(?i)(api[_-]?key|authorization)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{12,}", text
    ) is None


def test_builder_is_deterministic_for_versioned_outputs() -> None:
    tracked = [
        *ROOT.glob("*.json"),
        Path("docs/research_final/FINAL_ACCEPTED_CLAIMS_REGISTRY_v1.md"),
        Path("docs/research_final/SCIENTIFIC_CONTENT_LOCK_REVIEW_PACKET.md"),
    ]
    before = {path: _sha(path) for path in tracked}
    subprocess.run(
        [
            str(Path(".venv/Scripts/python.exe")),
            "scripts/research/build_final_accepted_claims_v1.py",
        ],
        check=True,
        capture_output=True,
    )
    after = {path: _sha(path) for path in tracked}
    assert after == before
