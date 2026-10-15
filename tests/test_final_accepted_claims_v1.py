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
DISALLOWED_IDS = {
    "CL_FROZEN_RQ1_UNQUALIFIED_WORDING",
    "CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING",
    "CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT",
    "CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION",
}
EXPECTED_SLASH_RQ_MAPPINGS = {
    "C02": ["RQ1", "RQ5", "RQ6"],
    "C03": ["RQ1", "RQ3"],
    "C05": ["RQ3", "RQ6"],
    "C06": ["RQ3", "RQ6"],
    "C08": ["RQ2", "RQ5"],
    "C09": ["RQ1", "RQ2", "RQ4"],
    "C10": ["RQ1", "RQ2"],
    "C11": ["RQ1", "RQ4"],
    "C12": ["RQ3", "RQ6"],
    "C13": ["RQ4", "RQ5"],
    "C19": ["RQ3", "RQ4"],
    "C21": ["RQ2", "RQ3", "RQ6"],
    "C24": ["RQ2", "RQ3", "RQ5", "RQ6"],
    "C32": ["RQ1", "RQ2", "RQ4"],
    "C33": ["RQ1", "RQ3"],
    "C34": ["RQ2", "RQ4"],
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str, binary: bool = False) -> bytes | str:
    value = subprocess.run(["git", *args], check=True, capture_output=True).stdout
    return value if binary else value.decode("utf-8").strip()


def _locked_rq_questions() -> list[str]:
    raw = _git(
        "show",
        f"{SOURCE_HEAD}:docs/research_final/REFERENCE_EVIDENCE_MATRIX.md",
    )
    assert isinstance(raw, str)
    matches = re.findall(r"^\d+\. \*\*RQ([1-6])\.\*\* (.+)$", raw, re.MULTILINE)
    assert [f"RQ{number}" for number, _ in matches] == RQ_ORDER
    return [wording for _, wording in matches]


def test_manifest_has_no_self_hash_and_resolves_all_outputs() -> None:
    manifest = _load(ROOT / "manifest.json")
    assert manifest["status"] == "REGISTRY_TARGETED_REPAIR_COMPLETE"
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
    assert [row["research_question"] for row in rows] == _locked_rq_questions()
    assert [row["full_original_research_question"] for row in rows] == _locked_rq_questions()
    assert all(row["short_display_label"] != row["research_question"] for row in rows)
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


def test_ar01_primary_evidence_tiers_and_background_are_exact() -> None:
    records = _load(ROOT / "accepted_claims_registry.json")["records"]
    by_id = {row["original_claim_id"]: row for row in records}
    expected = {
        "C19": "CODE_OBSERVATION",
        "C24": "PROJECT_METRIC_DEFINITION",
        "C26": "CODE_OBSERVATION",
        "C30": "DERIVED_HISTORICAL_VALIDATION_RESULT",
        "C32": "CODE_OBSERVATION_AND_MODEL_COMPUTED_COUNTERFACTUAL",
        "C34": "CODE_OBSERVATION",
        "C35": "CODE_OBSERVATION_WITH_SCOPED_MODEL_LIMITATION",
        "CL_INT_TERRA_NEGATIVE_PRESERVED": "DERIVED_HISTORICAL_VALIDATION_RESULT",
    }
    assert {claim_id: by_id[claim_id]["primary_evidence_tier"] for claim_id in expected} == expected
    assert by_id["C19"]["supporting_scholarly_background"]["status"] == "NOT_APPLICABLE"
    assert by_id["C24"]["supporting_scholarly_background"]["status"] == "SCHOLARLY_BACKGROUND_ONLY"
    assert by_id["C26"]["supporting_scholarly_background"]["source_ids"] == ["S25", "S26"]
    assert by_id["C32"]["supporting_scholarly_background"]["source_ids"] == ["S05"]
    assert by_id["C34"]["supporting_scholarly_background"]["source_ids"] == ["S08"]
    assert by_id["C35"]["supporting_scholarly_background"]["status"] == "NOT_APPLICABLE"
    assert "ONCHAIN_HISTORICAL_OBSERVATION" in by_id["C09"]["primary_evidence_components"]
    assert "ONCHAIN_HISTORICAL_OBSERVATION" in by_id["C10"]["primary_evidence_components"]


def test_ar02_all_sixteen_slash_rq_mappings_are_restored() -> None:
    records = _load(ROOT / "accepted_claims_registry.json")["records"]
    scholarly = {
        row["original_claim_id"]: row
        for row in records
        if row["namespace"] == "SCHOLARLY_P2"
    }
    assert {
        claim_id: scholarly[claim_id]["rq_mapping"]
        for claim_id in EXPECTED_SLASH_RQ_MAPPINGS
    } == EXPECTED_SLASH_RQ_MAPPINGS
    crosswalk = {
        row["original_claim_id"]: row
        for row in _load(ROOT / "claim_evidence_crosswalk.json")["rows"]
    }
    assert {
        claim_id: crosswalk[claim_id]["rq_mapping"]
        for claim_id in EXPECTED_SLASH_RQ_MAPPINGS
    } == EXPECTED_SLASH_RQ_MAPPINGS
    rq_rows = _load(ROOT / "six_rq_accepted_claims_matrix.json")["research_questions"]
    support = {
        row["rq"]: set(row["scholarly_claim_registry_ids"])
        for row in rq_rows
    }
    for claim_id, mappings in EXPECTED_SLASH_RQ_MAPPINGS.items():
        for rq in mappings:
            assert f"P2:{claim_id}" in support[rq]


def test_ar03_accepted_wording_and_rq3_route_semantics_are_exact() -> None:
    records = _load(ROOT / "accepted_claims_registry.json")["records"]
    by_id = {row["original_claim_id"]: row for row in records}
    expected = {
        "C07": (
            "Thanh khoản Uniswap V3 phụ thuộc các khoảng tick. Trong mô phỏng, suy giảm độ sâu "
            "làm thay đổi khả năng hấp thụ bán thế chấp và tác động giá; eligibility mới còn phụ thuộc "
            "chính sách định giá."
        ),
        "C11": (
            "S13 không tìm thấy tác động giá kéo dài có ý nghĩa thống kê trong thiết kế đã xét; "
            "DeFiStress mô phỏng thanh lý vòng hai ở những trường hợp stress được chọn dưới Policy A. "
            "Hai kết quả có phạm vi và chuẩn đối chiếu khác nhau."
        ),
        "C19": (
            "Nhánh Aave của DeFiStress sử dụng một tác nhân thanh lý và một tác nhân kinh doanh "
            "chênh lệch giá đại diện."
        ),
        "C23": (
            "Trong cấu hình baseline Policy A, Severe ghi nhận 8/200 đường mô phỏng ở P0 v2 và "
            "280/10.000 đường ở Level-3 có độ sâu thanh lý từ hai vòng trở lên; Low Liquidity ghi nhận "
            "0/1.000. Khoảng Wilson mô tả bất định lấy mẫu có điều kiện trong từng cấu hình."
        ),
        "C32": (
            "Policy A của mô hình lấy giá trị nhỏ hơn giữa giá tham chiếu và giá DEX; Policy B chỉ dùng "
            "giá tham chiếu; các Policy C là giả định truyền giá có độ trễ và làm trơn. Các chính sách này "
            "chưa được xác minh là cơ chế oracle thực tế của Aave hoặc Chainlink."
        ),
        "C33": (
            "Kiểm toán HF trong mô hình theo Policy A ghi nhận các vị thế mới mất an toàn sau Wave 1; "
            "việc mới đủ điều kiện theo HF được đối chiếu riêng với các lần thanh lý vòng hai có hoàn trả "
            "nợ dương."
        ),
    }
    for claim_id, wording in expected.items():
        assert by_id[claim_id]["accepted_vietnamese_wording"] == wording
        assert by_id[claim_id]["accepted_vietnamese_wording"] != by_id[claim_id]["original_source_wording"]
    rq3 = _load(ROOT / "six_rq_accepted_claims_matrix.json")["research_questions"][2]
    conclusion = rq3["recommended_vietnamese_conclusion"]
    assert "36 trường hợp mới đủ điều kiện theo HF danh mục" in conclusion
    assert "không có khoản nợ USDC thuộc tuyến thanh lý WETH/USDC" in conclusion
    assert "borrower-case-policy instances" in conclusion
    assert "không còn modeled USDC debt" not in conclusion
    assert "đã được trả hết" not in conclusion


def test_ar03_c23_denominators_resolve_from_locked_artifact() -> None:
    batches = _load(
        Path(
            "data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json"
        )
    )["batches"]
    observed = {
        (row["scenario"]["name"], int(row["actual_runs"])): (
            int(row["cascade_frequencies"]["2"]["successes"]),
            int(row["cascade_frequencies"]["2"]["runs"]),
        )
        for row in batches
    }
    assert observed[("Severe", 200)] == (8, 200)
    assert observed[("Severe", 10000)] == (280, 10000)
    assert observed[("Low Liquidity", 1000)] == (0, 1000)


def test_ar04_superseded_wording_is_not_mislabeled_as_historical_quote() -> None:
    records = _load(ROOT / "accepted_claims_registry.json")["records"]
    by_id = {row["original_claim_id"]: row for row in records}
    for claim_id in {
        "CL_FROZEN_RQ1_UNQUALIFIED_WORDING",
        "CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING",
    }:
        assert by_id[claim_id]["original_source_wording"] == "NOT_VERBATIM_HISTORICAL_QUOTATION"
        assert by_id[claim_id]["historical_disposition_summary"] != "NOT_APPLICABLE"


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
    rq_rows = _load(ROOT / "six_rq_accepted_claims_matrix.json")["research_questions"]
    affirmative = {
        claim_id
        for row in rq_rows
        for claim_id in row["accepted_integration_claim_ids"]
    }
    disallowed = {
        claim_id
        for row in rq_rows
        for claim_id in row["disallowed_or_superseded_claim_ids"]
    }
    assert affirmative.isdisjoint(DISALLOWED_IDS)
    assert disallowed >= DISALLOWED_IDS
    assert all(
        reference["claim_id"] not in DISALLOWED_IDS
        or reference["final_gate_status"]
        in {"REJECTED_AS_WORDED_SUPERSEDED", "UNSUPPORTED"}
        for row in rq_rows
        for reference in row["integration_scientific_claim_references"]
    )


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
    assert readiness["proposed_status"] == "REGISTRY_TARGETED_REPAIR_COMPLETE"
    assert readiness["scientific_content_lock_declared"] is False
    assert readiness["commander_decision_required"] is True
    assert readiness["blocking_conflicts"] == []
    assert len(readiness["rejected_or_unsupported_integration_records"]) == 4
    assert set(readiness["academic_repair_status"].values()) == {"PASS"}


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
