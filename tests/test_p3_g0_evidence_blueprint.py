from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, cast

ARTIFACT_ROOT = Path("artifacts/manuscript_p3")
DOC_ROOT = Path("docs/manuscript_p3/codex")
REGISTRY_ROOT = Path("data/processed/research_final/final_accepted_claims_v1")
SOURCE_LOCK = "3f6e5302483681209e2408531eb5a15389f9fded"
RQ_ORDER = [f"RQ{index}" for index in range(1, 7)]
DISALLOWED = {
    "INT:CL_FROZEN_RQ1_UNQUALIFIED_WORDING",
    "INT:CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING",
    "INT:CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT",
    "INT:CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION",
}


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _result_ids() -> set[str]:
    paths = [
        Path("data/processed/research_final/frozen_v3/results_registry.json"),
        Path("data/processed/research_final/scientific_integration_v1/integration_result_registry.json"),
    ]
    return {row["result_id"] for path in paths for row in _load(path)["results"]}


def test_source_lock_and_locked_tree_objects() -> None:
    assert _git("merge-base", "HEAD", SOURCE_LOCK) == SOURCE_LOCK
    expected = _load(REGISTRY_ROOT / "manifest.json")["source_tree_ids"]
    assert _git("rev-parse", f"{SOURCE_LOCK}:data/processed/research_final/frozen_v3") == expected["frozen_v3"]
    assert (
        _git("rev-parse", f"{SOURCE_LOCK}:data/processed/research_final/oracle_transmission_diagnostic_v1")
        == expected["oracle_diagnostic_v1"]
    )
    assert (
        _git("rev-parse", f"{SOURCE_LOCK}:data/processed/research_final/scientific_integration_v1")
        == expected["scientific_integration_v1"]
    )


def test_inventory_preserves_registry_counts_and_unique_technical_ids() -> None:
    inventory = _load(ARTIFACT_ROOT / "P3_LOCKED_EVIDENCE_INVENTORY.json")
    assert inventory["source_lock_commit"] == SOURCE_LOCK
    assert inventory["locked_claim_counts"] == {
        "affirmative": 44,
        "disallowed": 4,
        "integration_scientific": 13,
        "scholarly": 35,
    }
    ids = [row["evidence_id"] for row in inventory["records"]]
    assert len(ids) == len(set(ids))
    assert all(row["read_verification_level"] for row in inventory["records"])
    assert all(row["mandatory_limitations"] for row in inventory["records"])


def test_catalog_claims_results_and_sources_resolve_without_disallowed_claims() -> None:
    catalog = _load(ARTIFACT_ROOT / "P3_EXHIBIT_CATALOG_v1.json")
    inventory = _load(ARTIFACT_ROOT / "P3_LOCKED_EVIDENCE_INVENTORY.json")
    claims = _load(REGISTRY_ROOT / "accepted_claims_registry.json")["records"]
    affirmative = {
        row["registry_id"] for row in claims if row["final_gate_status"] in {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"}
    }
    result_ids = _result_ids()
    paths = set(inventory["path_to_p3_evidence_id"])
    assert len(catalog["records"]) == 11
    for exhibit in catalog["records"]:
        assert set(exhibit["accepted_claim_ids"]) <= affirmative
        assert not set(exhibit["accepted_claim_ids"]) & DISALLOWED
        assert set(exhibit["result_ids"]) <= result_ids
        assert {row["path"] for row in exhibit["source_artifact_locators"]} <= paths
        assert exhibit["proposed_chapter"] == "WORK_TO_ASSIGN_AFTER_BLUEPRINT"
        assert exhibit["commander_approval_state"] == "PENDING"


def test_six_rq_order_and_limitations_are_locked() -> None:
    matrix = _load(REGISTRY_ROOT / "six_rq_accepted_claims_matrix.json")["research_questions"]
    assert [row["rq"] for row in matrix] == RQ_ORDER
    assert all(row["required_limitations"] for row in matrix)
    assert all(row["scientific_decision_status"] == "ACCEPTED_WITH_LIMITATIONS" for row in matrix)


def test_handoff_stops_before_chapter_production_or_lock() -> None:
    handoff = _load(ARTIFACT_ROOT / "P3_WORK_CODEX_EVIDENCE_HANDOFF.json")
    assert handoff["stage_rule"] == "No record may be set to CHAPTER_LOCKED without Commander approval."
    assert all(row["current_status"] == "SOURCE_VERIFIED" for row in handoff["requests"])
    assert all(row["work_review_state"] == "AWAITING_BLUEPRINT" for row in handoff["requests"])
    assert all(row["commander_approval_state"] == "PENDING" for row in handoff["requests"])


def test_locked_numerical_semantics_are_explicit() -> None:
    validation = _load(REGISTRY_ROOT / "validation_report.json")["numerical_claim_lock"]
    assert validation["eligible_vs_executed"] == {
        "A": {"executed_wave2": 14, "newly_eligible": 35, "skipped": 21},
        "B": {"executed_wave2": 0, "newly_eligible": 0, "skipped": 0},
        "C_MODERATE": {"executed_wave2": 2, "newly_eligible": 11, "skipped": 9},
        "C_WEAK": {"executed_wave2": 0, "newly_eligible": 6, "skipped": 6},
    }
    assert validation["severe_policy_a"]["denominator"] == 10_000
    assert validation["severe_policy_a"]["depth_gte_2"] == 280
    assert validation["severe_policy_a"]["policy"] == "A_ADVERSE_PASS_THROUGH"
    assert "not Ethereum crisis probability" in validation["severe_policy_a"]["population_semantics"]
    assert validation["historical"]["pool_events"] == 28
    assert validation["historical"]["graph_matched_events"] == 27
    assert validation["historical"]["tiers_direct_same_tx_same_block_time"] == [1, 2, 23, 1]
    assert validation["terra_negative"]["successful_oos_forecast_established"] is False


def test_generated_json_and_markdown_checksums() -> None:
    for path in ARTIFACT_ROOT.glob("*.json"):
        value = _load(path)
        expected = value["output_provenance"].pop("content_sha256")
        assert hashlib.sha256(_canonical_bytes(value)).hexdigest() == expected
    for path in DOC_ROOT.glob("*.md"):
        raw = path.read_text(encoding="utf-8")
        body, checksum_line = raw.rsplit("\nContent SHA-256 (UTF-8, excluding this checksum line): `", 1)
        expected = checksum_line.removesuffix("`\n")
        assert hashlib.sha256(body.encode()).hexdigest() == expected


def test_builder_check_mode_is_byte_deterministic() -> None:
    subprocess.run(
        [
            str(Path(".venv/Scripts/python.exe")),
            "scripts/research/build_p3_g0_evidence_blueprint.py",
            "--check",
            "--docx-root",
            "C:/Users/Admin/Downloads",
        ],
        check=True,
    )


def test_stage_g0_does_not_write_work_owned_paths() -> None:
    status = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout
    assert "docs/manuscript_p3/work/" not in status
    assert "data/processed/research_final/final_accepted_claims_v1/" not in status
