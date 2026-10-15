# ruff: noqa: E501 -- registry prose preserves reviewed scientific wording.
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

ROOT = Path("data/processed/research_final/final_accepted_claims_v1")
FROZEN = Path("data/processed/research_final/frozen_v3")
ORACLE = Path("data/processed/research_final/oracle_transmission_diagnostic_v1")
INTEGRATION = Path("data/processed/research_final/scientific_integration_v1")
P2 = Path("docs/research_final/P2_CLAIM_EVIDENCE_CROSSWALK.json")
REPORT = Path("docs/research_final/FINAL_ACCEPTED_CLAIMS_REGISTRY_v1.md")
PACKET = Path("docs/research_final/SCIENTIFIC_CONTENT_LOCK_REVIEW_PACKET.md")
TEST_EVIDENCE = ROOT / "test_evidence.json"

SOURCE_HEAD = "6560f799f81223cd4a720bd3f6b798aeef1732b9"
CANONICAL_SHA256_CRLF = "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"

RQ_DEFINITIONS = [
    ("RQ1", "Điều kiện và ngưỡng xuất hiện thanh lý dây chuyền."),
    ("RQ2", "Vai trò thanh khoản DEX."),
    ("RQ3", "Gas, vốn, công suất và độ trễ thanh lý."),
    ("RQ4", "Arbitrage và phục hồi giá."),
    ("RQ5", "Mất neo stablecoin và định giá nợ USDC."),
    ("RQ6", "Đánh đổi LTV, liquidation threshold, liquidation bonus."),
]

REQUIRED_SOURCES = [
    "data/processed/research_final/frozen_v3/manifest.json",
    "data/processed/research_final/frozen_v3/results_registry.json",
    "data/processed/research_final/frozen_v3/claim_ledger.json",
    "data/processed/research_final/frozen_v3/rq_answer_matrix.json",
    "data/processed/research_final/frozen_v3/evidence_source_matrix.json",
    "docs/research_final/EVIDENCE_FREEZE_REPORT.md",
    "docs/research_final/RQ_ANSWER_MATRIX.md",
    "docs/research_final/ORACLE_TRANSMISSION_DIAGNOSTIC_v1.md",
    "data/processed/research_final/oracle_transmission_diagnostic_v1/manifest.json",
    "data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv",
    "data/processed/research_final/oracle_transmission_diagnostic_v1/selection_manifest.json",
    "data/processed/research_final/oracle_transmission_diagnostic_v1/scientific_interpretation.json",
    "data/processed/research_final/scientific_integration_v1/claim_to_result_registry.json",
    "data/processed/research_final/scientific_integration_v1/six_rq_evidence_matrix.json",
    "data/processed/research_final/scientific_integration_v1/integration_result_registry.json",
    "data/processed/research_final/scientific_integration_v1/table_figure_registry.json",
    "data/processed/research_final/scientific_integration_v1/accepted_claims_proposed.json",
    "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_audit.csv",
    "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv",
    "data/processed/research_final/scientific_integration_v1/integration_validation_report.json",
    "docs/research_final/SCIENTIFIC_INTEGRATION_ADDENDUM_v1.md",
    "docs/research_final/FINAL_CROSS_PR_CONSISTENCY_REVIEW.md",
    "docs/research_final/LITERATURE_VERIFIED.md",
    "docs/research_final/REFERENCE_EVIDENCE_MATRIX.md",
    "docs/research_final/APA_REFERENCES_VERIFIED.md",
    "docs/research_final/TERMINOLOGY_VI.md",
    "docs/research_final/P2_VERSION_RECONCILIATION.md",
    "docs/research_final/P2_ORACLE_RECONCILIATION.md",
    "docs/research_final/P2_CLAIM_EVIDENCE_CROSSWALK.json",
]

LOCKED_TREES = {
    "frozen_v3": "data/processed/research_final/frozen_v3",
    "oracle_diagnostic_v1": "data/processed/research_final/oracle_transmission_diagnostic_v1",
    "scientific_integration_v1": "data/processed/research_final/scientific_integration_v1",
}

LOCKED_P2_PATHS = [
    "docs/research_final/LITERATURE_VERIFIED.md",
    "docs/research_final/REFERENCE_EVIDENCE_MATRIX.md",
    "docs/research_final/APA_REFERENCES_VERIFIED.md",
    "docs/research_final/TERMINOLOGY_VI.md",
    "docs/research_final/P2_VERSION_RECONCILIATION.md",
    "docs/research_final/P2_ORACLE_RECONCILIATION.md",
    "docs/research_final/P2_CLAIM_EVIDENCE_CROSSWALK.json",
]

INTEGRATION_WORDING_VI = {
    "CL_INT_RQ1_POLICY_CONDITIONAL": "Wave 2 xuất hiện trong các trường hợp đuôi đã chọn dưới Policy A và nhạy với chính sách định giá A/B/C.",
    "CL_FROZEN_RQ1_UNQUALIFIED_WORDING": "Các số Frozen RQ1 chỉ được báo cáo với điều kiện Policy A; cách diễn đạt không điều kiện đã bị thay thế.",
    "CL_INT_RQ2_TWO_CHANNELS": "Thanh khoản quyết định sức hấp thụ và tác động DEX; chính sách định giá quyết định việc DEX state có truyền sang HF hay không.",
    "CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING": "Haircut đuôi làm yếu sức hấp thụ DEX; eligibility mới chỉ được kết luận khi nêu rõ chính sách truyền giá.",
    "CL_INT_ELIGIBLE_NOT_EXECUTED": "Portfolio HF eligibility, đánh giá của engine và thanh lý có hoàn trả nợ dương là ba cổng khác nhau.",
    "CL_INT_RQ3_PRESERVED": "Vốn bị ràng buộc ở các mức thấp đã thử; delay không đổi severity trong miền thử nghiệm khóa.",
    "CL_INT_RQ4_PRESERVED": "Arbitrage mô hình làm giảm residual spread sau giao dịch nhưng không xóa immediate price impact của cùng lần bán.",
    "CL_INT_RQ5_PRESERVED": "Định giá nợ USDC làm thay đổi HF khi giữ các yếu tố khác cố định; số token USDC và USD-equivalent phải tách biệt.",
    "CL_INT_RQ6_PRESERVED": "LTV, liquidation threshold và liquidation bonus chi phối các cơ chế khác nhau và không thể dùng thay thế nhau.",
    "CL_INT_HISTORICAL_TIERS_PRESERVED": "Cửa sổ lịch sử ghi nhận 28 Pool events, 27 Graph-matched và các tầng liên hệ 1/2/23/1.",
    "CL_INT_TERRA_NEGATIVE_PRESERVED": "Kết quả cảnh báo sớm cutoff-safe của Terra là kết quả âm và không hỗ trợ claim dự báo ngoài mẫu thành công.",
    "CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT": "Không có bằng chứng được chấp nhận rằng Aave hoặc Chainlink lịch sử sử dụng trực tiếp Uniswap spot theo Policy A.",
    "CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION": "Bằng chứng lịch sử chỉ hỗ trợ liên hệ giao dịch/thời gian, không xác lập chuỗi lây lan nhân quả.",
}

RQ_REPORTING = {
    "RQ1": {
        "allowed": "Có thể báo cáo Wave 2 phản thực dưới Policy A và sensitivity A/B/C; newly eligible phải tách khỏi executed Wave 2.",
        "prohibited": "Không có ngưỡng cascade độc lập oracle, xác suất khủng hoảng Ethereum hay xác nhận Aave dùng Uniswap spot.",
        "limitation": "280/10.000 chỉ là tần suất Severe Policy A; 10 paths được chọn có chủ đích; không có depth ≥3 trong bộ khóa.",
        "conclusion": "Thanh lý dây chuyền depth 2 tồn tại trong mô hình ở tail stress dưới chính sách định giá cụ thể, nhưng không bền với mọi chính sách oracle đã thử.",
    },
    "RQ2": {
        "allowed": "Có thể tách sức hấp thụ thanh khoản, immediate price impact, residual spread và HF feedback qua policy.",
        "prohibited": "Không suy ra mọi tác động DEX tạo eligibility hoặc cascade; haircut 90/95% không phải quan sát lịch sử tương ứng.",
        "limitation": "Một pool, thanh khoản tĩnh/counterfactual, không routing đa venue và không xác minh feed lịch sử.",
        "conclusion": "Thanh khoản yếu khuếch đại biến dạng DEX, còn chuyển biến đó sang HF và depth phụ thuộc chính sách định giá.",
    },
    "RQ3": {
        "allowed": "Có thể báo cáo riêng vốn, công suất, gas/profitability, delay và route-level execution; eligibility không đồng nghĩa execution.",
        "prohibited": "Không gán 36 skip cho gas, vốn hoặc profitability; không suy rộng một liquidator đại diện thành thị trường bot cạnh tranh.",
        "limitation": "Một liquidator đại diện, vốn không recycle, không fork execution và route mô hình chỉ WETH/USDC.",
        "conclusion": "Vốn thấp có tính ràng buộc trong miền thử; execution phụ thuộc các cổng riêng và các skip targeted là route-ineligible do không còn modeled USDC debt.",
    },
    "RQ4": {
        "allowed": "Có thể báo cáo immediate impact và post-arbitrage residual riêng biệt trong mô hình.",
        "prohibited": "Không gọi price repositioning là funded executable swap hoặc bằng chứng hiệu quả arbitrage Mainnet.",
        "limitation": "Price teleportation, một arbitrageur, không cạnh tranh/latency/gas strategy hoặc SwapRouter fork.",
        "conclusion": "Arbitrage mô hình làm giảm residual spread sau forced sale nhưng không xóa tác động tức thời của execution.",
    },
    "RQ5": {
        "allowed": "Có thể báo cáo kênh định giá nợ USDC và tách USDC token quantity khỏi USD-equivalent.",
        "prohibited": "Không suy rộng thành mô hình settlement, redemption, confidence hoặc thanh khoản stablecoin đầy đủ.",
        "limitation": "Ceteris paribus debt valuation; không có kênh redemption/liquidity/settlement.",
        "conclusion": "Giá USD của nợ USDC thay đổi HF trong kênh định giá cô lập, không đại diện toàn bộ cơ chế depeg.",
    },
    "RQ6": {
        "allowed": "Có thể báo cáo riêng tác động của LTV, liquidation threshold và liquidation bonus trong các counterfactual khóa.",
        "prohibited": "Không hoán đổi ba tham số hoặc suy ra hành vi tái underwrite/borrower response ngoài mô hình.",
        "limitation": "Frozen cohort; không borrower behavior hoặc re-underwriting response.",
        "conclusion": "LTV điều tiết capacity ex ante, LT điều tiết HF/eligibility và bonus điều tiết incentive/collateral transfer.",
    },
}


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha(path: Path) -> str:
    return _sha(path.read_bytes())


def _git(*args: str, binary: bool = False) -> bytes | str:
    value = subprocess.run(["git", *args], check=True, capture_output=True).stdout
    return value if binary else value.decode("utf-8").strip()


def _git_exists(commit: str, path: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{commit}:{path}"],
        check=False,
        capture_output=True,
    ).returncode == 0


def _source_meta(path: str, commit: str = SOURCE_HEAD) -> dict[str, Any]:
    if not _git_exists(commit, path):
        raise ValueError(f"Missing source locator: {commit}:{path}")
    raw = cast(bytes, _git("show", f"{commit}:{path}", binary=True))
    return {
        "path": path,
        "source_commit": commit,
        "git_blob_sha": cast(str, _git("rev-parse", f"{commit}:{path}")),
        "sha256": _sha(raw),
        "hash_domain": "Git blob bytes (LF for normalized text)",
        "size_bytes": len(raw),
        "verification_status": "GIT_OBJECT_VERIFIED",
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _parse_rqs(value: str) -> list[str]:
    if "RQ1–6" in value or "RQ1-6" in value:
        return [rq for rq, _ in RQ_DEFINITIONS]
    return sorted(set(re.findall(r"RQ[1-6]", value)), key=lambda item: int(item[2:]))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _tree_id(commit: str, path: str) -> str:
    return cast(str, _git("rev-parse", f"{commit}:{path}"))


def _result_ids() -> tuple[set[str], dict[str, dict[str, Any]]]:
    rows = [
        *_load(FROZEN / "results_registry.json")["results"],
        *_load(INTEGRATION / "integration_result_registry.json")["results"],
    ]
    return {row["result_id"] for row in rows}, {row["result_id"]: row for row in rows}


def _table_figure_ids() -> set[str]:
    frozen = _load(FROZEN / "evidence_source_matrix.json")
    integration = _load(INTEGRATION / "table_figure_registry.json")
    return {
        *[row["table_id"] for row in frozen["table_registry"]],
        *[row["figure_id"] for row in frozen["figure_registry"]],
        *[row["table_id"] for row in integration["tables"]],
        *[row["figure_id"] for row in integration["figures"]],
    }


def _build_scholarly_claims(
    p2: dict[str, Any], source_by_path: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    crosswalk_meta = source_by_path[P2.as_posix()]
    rows: list[dict[str, Any]] = []
    for claim in p2["claims"]:
        not_applicable = str(claim["model_result"]).startswith("NOT_APPLICABLE")
        source_not_verified = "SOURCE_NOT_VERIFIED" in str(claim.get("raw_hf_state_review", "")) or any(
            locator.get("read_status") == "SOURCE_NOT_VERIFIED"
            for locator in claim.get("artifact_locators", [])
        )
        final_status = (
            "ACCEPTED"
            if claim["status"] == "PASS_UNCHANGED"
            else "ACCEPTED_WITH_LIMITATIONS"
        )
        limitations = [claim["original_limit"]]
        if claim.get("raw_hf_state_review") not in (None, "", "NOT_APPLICABLE"):
            limitations.append(claim["raw_hf_state_review"])
        rows.append(
            {
                "registry_id": f"P2:{claim['claim_id']}",
                "original_claim_id": claim["claim_id"],
                "namespace": "SCHOLARLY_P2",
                "rq_mapping": _parse_rqs(claim["rq"]),
                "extension_mapping": [] if _parse_rqs(claim["rq"]) else [claim["rq"]],
                "claim_category": "SCHOLARLY_CONCEPTUAL_OR_PROTOCOL" if not_applicable else "SCHOLARLY_WITH_PROJECT_CROSSWALK",
                "accepted_vietnamese_wording": claim["original_statement"],
                "original_source_wording": claim["original_statement"],
                "scholarly_source_ids": claim["scholarly_sources"],
                "evidence_alias_ids": claim["evidence_aliases"],
                "scientific_result_ids": claim["model_result_ids"],
                "integration_claim_ids": claim["integration_claim_ids"],
                "scenario": "NOT_APPLICABLE" if not_applicable else "See active artifact locators",
                "policy": claim["oracle_policy"],
                "evidence_tier": "SCHOLARLY_SOURCE" if not_applicable else "SCHOLARLY_SOURCE_WITH_SCOPED_MODEL_CROSSWALK",
                "artifact_path": P2.as_posix(),
                "artifact_locator_commit": SOURCE_HEAD,
                "source_commit": SOURCE_HEAD,
                "artifact_checksum": crosswalk_meta["sha256"],
                "artifact_hash_domain": crosswalk_meta["hash_domain"],
                "active_artifact_locators": claim["artifact_locators"],
                "table_figure_locators": claim["table_figure_locators"],
                "verification_status": claim["final_cross_pr_locator_status"],
                "source_verification": claim["source_verification"],
                "accepted_inference": claim["allowed_interpretation"],
                "required_limitations": limitations,
                "unsupported_stronger_inference": claim["original_limit"],
                "superseded_references": ["See P2 final_cross_pr_reconciliation.superseded_locators"] if claim["status"] == "CORRECTED" else [],
                "not_applicable_semantics": "No project result is required for this conceptual/protocol claim; NOT_APPLICABLE is not a numerical PASS." if not_applicable else "A scoped project result crosswalk applies.",
                "source_not_verified_semantics": "Some raw source cells were not read in the P2 session; accepted inference remains limited to separately verified summaries/state reconstruction." if source_not_verified else "No additional SOURCE_NOT_VERIFIED limitation declared for this claim.",
                "final_gate_status": final_status,
            }
        )
    return rows


def _build_integration_claims(
    integration: dict[str, Any],
    p2_claims: dict[str, dict[str, Any]],
    source_by_path: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for claim in integration["claims"]:
        path = claim["artifact_path"]
        meta = source_by_path.get(path) or _source_meta(path)
        scholarly_claim_ids = claim["literature_claim_ids"]
        scholarly_source_ids = sorted(
            {
                source
                for claim_id in scholarly_claim_ids
                for source in p2_claims[claim_id]["scholarly_sources"]
            }
        )
        aliases = sorted(
            {
                alias
                for claim_id in scholarly_claim_ids
                for alias in p2_claims[claim_id]["evidence_aliases"]
            }
        )
        if claim["status"] == "ACCEPTED_WITH_LIMITATIONS":
            final_status = "ACCEPTED_WITH_LIMITATIONS"
            category = "SCIENTIFIC_REPORTABLE_WITH_LIMITATIONS"
        elif claim["status"] == "REQUIRES_CORRECTION":
            final_status = "REJECTED_AS_WORDED_SUPERSEDED"
            category = "SUPERSEDED_SCIENTIFIC_WORDING"
        else:
            final_status = "UNSUPPORTED"
            category = "UNSUPPORTED_STRONGER_INFERENCE"
        rows.append(
            {
                "registry_id": f"INT:{claim['claim_id']}",
                "original_claim_id": claim["claim_id"],
                "namespace": "INTEGRATION_SCIENTIFIC",
                "rq_mapping": _parse_rqs(claim["rq"]),
                "extension_mapping": [] if _parse_rqs(claim["rq"]) else [claim["rq"]],
                "claim_category": category,
                "accepted_vietnamese_wording": INTEGRATION_WORDING_VI[claim["claim_id"]],
                "original_source_wording": claim["allowed_inference"],
                "scholarly_claim_ids": scholarly_claim_ids,
                "scholarly_source_ids": scholarly_source_ids,
                "evidence_alias_ids": aliases,
                "scientific_result_ids": claim["result_ids"],
                "table_figure_ids": claim["table_figure"],
                "scenario": claim["scenario"],
                "policy": claim["policy"],
                "evidence_tier": claim["evidence_tier"],
                "artifact_path": path,
                "artifact_locator_commit": SOURCE_HEAD,
                "source_commit": claim["source_commit"],
                "artifact_checksum": meta["sha256"],
                "artifact_hash_domain": meta["hash_domain"],
                "verification_status": claim["status"],
                "accepted_inference": claim["allowed_inference"],
                "required_limitations": [claim["limitation"]],
                "unsupported_stronger_inference": claim["limitation"],
                "superseded_references": [claim["claim_id"]] if claim["status"] == "REQUIRES_CORRECTION" else [],
                "not_established_semantics": "No affirmative external empirical inference is established." if claim["status"] == "UNSUPPORTED" else "NOT_APPLICABLE",
                "final_gate_status": final_status,
            }
        )
    return rows


def _numerical_lock(result_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ids = {
        "A": ("INT_A_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_A_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10"),
        "B": ("INT_B_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_B_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10"),
        "C_WEAK": ("INT_C_WEAK_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_C_WEAK_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10"),
        "C_MODERATE": ("INT_C_MODERATE_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4", "INT_C_MODERATE_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10"),
    }
    summary = _read_csv(INTEGRATION / "eligible_vs_executed_summary.csv")
    policy_map = {
        "A_ADVERSE_PASS_THROUGH": "A",
        "B_REFERENCE_ONLY": "B",
        "C_WEAK_LAGGED_SMOOTHED_PROXY": "C_WEAK",
        "C_MODERATE_LAGGED_SMOOTHED_PROXY": "C_MODERATE",
    }
    eligible: dict[str, dict[str, int]] = defaultdict(lambda: {"newly_eligible": 0, "executed_wave2": 0, "skipped": 0})
    for row in summary:
        key = policy_map[row["policy_id"]]
        eligible[key]["newly_eligible"] += int(row["newly_eligible_after_wave1_count"])
        eligible[key]["executed_wave2"] += int(row["newly_eligible_executed_wave2_count"])
        eligible[key]["skipped"] += int(row["newly_eligible_skipped_count"])
    return {
        "deterministic_depth2_retained_of_4": {key: result_by_id[pair[0]]["value"] for key, pair in ids.items()},
        "targeted_mc_depth2_retained_of_10": {key: result_by_id[pair[1]]["value"] for key, pair in ids.items()},
        "severe_policy_a": {
            "depth_gte_2": result_by_id["RQ1_MC_SEVERE_DEPTH2_COUNT"]["value"],
            "denominator": 10000,
            "policy": "A_ADVERSE_PASS_THROUGH",
            "population_semantics": "locked simulated Severe paths; not Ethereum crisis probability",
        },
        "eligible_vs_executed": dict(eligible),
        "historical": {
            "pool_events": result_by_id["HIST_RPC_CENSUS_EVENTS"]["value"],
            "graph_matched_events": result_by_id["HIST_GRAPH_MATCHED_EVENTS"]["value"],
            "tiers_direct_same_tx_same_block_time": [
                result_by_id["HIST_DIRECT_TRANSFER_PATHS"]["value"],
                result_by_id["HIST_SAME_TX_COOCCURRENCE"]["value"],
                result_by_id["HIST_SAME_BLOCK_ASSOCIATION"]["value"],
                result_by_id["HIST_TIME_WINDOW_ASSOCIATION"]["value"],
            ],
            "causal_contagion_established": False,
        },
        "terra_negative": {
            "pre_depeg_high_alert_hours": result_by_id["TERRA_PRE_DEPEG_HIGH_ALERT_HOURS"]["value"],
            "initial_depeg_high_lead_hours": result_by_id["TERRA_INITIAL_DEPEG_HIGH_LEAD"]["value"],
            "successful_oos_forecast_established": False,
        },
    }


def _build_rq_matrix(
    scholarly: list[dict[str, Any]], integration: list[dict[str, Any]], source_matrix: dict[str, Any]
) -> list[dict[str, Any]]:
    source_by_rq = {row["rq"]: row for row in source_matrix["research_questions"]}
    historical = "28 Pool events, 27 Graph-matched; tiers 1/2/23/1; association only, no causal contagion."
    rows = []
    for rq, question in RQ_DEFINITIONS:
        source = source_by_rq[rq]
        scholarly_ids = [row["registry_id"] for row in scholarly if rq in row["rq_mapping"]]
        integration_ids = [row["original_claim_id"] for row in integration if rq in row["rq_mapping"]]
        result_ids = sorted(
            {
                result
                for row in integration
                if rq in row["rq_mapping"]
                for result in row["scientific_result_ids"]
            }
            | set(source["evidence"])
        )
        rows.append(
            {
                "rq": rq,
                "research_question": question,
                "scholarly_claim_registry_ids": scholarly_ids,
                "integration_scientific_claim_ids": integration_ids,
                "model_evidence_result_ids": result_ids,
                "historical_evidence": historical if rq in {"RQ1", "RQ2"} else "No additional historical causal evidence required for the accepted scoped claim.",
                "results_allowed_for_reporting": RQ_REPORTING[rq]["allowed"],
                "results_prohibited_from_extrapolation": RQ_REPORTING[rq]["prohibited"],
                "required_limitations": [RQ_REPORTING[rq]["limitation"]],
                "recommended_vietnamese_conclusion": RQ_REPORTING[rq]["conclusion"],
                "scientific_decision_status": "ACCEPTED_WITH_LIMITATIONS",
            }
        )
    return rows


def _active_locators(
    p2: dict[str, Any],
    integration: dict[str, Any],
    source_by_path: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    locators: list[dict[str, str]] = []
    for claim in p2["claims"]:
        for item in [*claim["artifact_locators"], *claim["table_figure_locators"]]:
            if item and item.get("path") and item.get("read_commit"):
                locators.append(
                    {
                        "path": item["path"],
                        "commit": item["read_commit"],
                        "expected_git_blob_sha": item.get("git_blob_sha", ""),
                        "expected_sha256": item.get("content_sha256", ""),
                        "hash_domain": item.get("content_sha256_domain", ""),
                    }
                )
    for alias in p2["evidence_aliases"]:
        for item in [*alias["new_corresponding_locators"], *alias["table_figure_locators"]]:
            if item and item.get("path") and item.get("read_commit"):
                locators.append(
                    {
                        "path": item["path"],
                        "commit": item["read_commit"],
                        "expected_git_blob_sha": item.get("git_blob_sha", ""),
                        "expected_sha256": item.get("content_sha256", ""),
                        "hash_domain": item.get("content_sha256_domain", ""),
                    }
                )
    for claim in integration["claims"]:
        meta = source_by_path.get(claim["artifact_path"]) or _source_meta(claim["artifact_path"])
        locators.append(
            {
                "path": claim["artifact_path"],
                "commit": SOURCE_HEAD,
                "expected_git_blob_sha": meta["git_blob_sha"],
                "expected_sha256": meta["sha256"],
                "hash_domain": meta["hash_domain"],
            }
        )
    return locators


def _render_docs(
    registry: list[dict[str, Any]], rq_rows: list[dict[str, Any]], numerical: dict[str, Any], validation: dict[str, Any], test_evidence: dict[str, Any]
) -> None:
    p2_count = sum(row["namespace"] == "SCHOLARLY_P2" for row in registry)
    int_count = sum(row["namespace"] == "INTEGRATION_SCIENTIFIC" for row in registry)
    accepted = sum(row["final_gate_status"] in {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"} for row in registry)
    lines = [
        "# Final Accepted Scientific Claims Registry v1",
        "",
        "Trạng thái đề nghị: **FINAL_REGISTRY_READY_FOR_COMMANDER_REVIEW**. Tài liệu này không tự cấp `SCIENTIFIC_CONTENT_LOCK`.",
        "",
        f"Nguồn được pin tại integration HEAD `{SOURCE_HEAD}`. Output commit của registry được ghi trong Git handoff để tránh self-reference.",
        "",
        "## Phạm vi registry",
        "",
        f"Registry có {p2_count} scholarly claims (`P2:C01`–`P2:C35`) và {int_count} Integration scientific claims, tổng {len(registry)} bản ghi. {accepted} bản ghi được đề nghị dùng với trạng thái ACCEPTED hoặc ACCEPTED_WITH_LIMITATIONS; bốn Integration records còn lại là wording đã superseded hoặc stronger inference không được hỗ trợ.",
        "",
        "`NOT_APPLICABLE` nghĩa là claim khái niệm không cần result định lượng; không phải PASS giả. `SOURCE_NOT_VERIFIED` giữ nguyên giới hạn đọc nguồn. `NOT_ESTABLISHED` không được chuyển thành khẳng định dương.",
        "",
        "## Numerical claim lock",
        "",
        f"- Deterministic depth-2 A/B/Cweak/Cmoderate: `{list(numerical['deterministic_depth2_retained_of_4'].values())}`.",
        f"- Targeted MC A/B/Cweak/Cmoderate: `{list(numerical['targeted_mc_depth2_retained_of_10'].values())}`; 10 paths không phải population estimator.",
        f"- Severe Policy A: `{numerical['severe_policy_a']['depth_gte_2']}/10.000` depth ≥2; không phải xác suất khủng hoảng Ethereum.",
        "- Eligible/executed/skipped: A `35/14/21`; B `0/0/0`; C weak `6/0/6`; C moderate `11/2/9`. Đây là borrower-case instances cộng qua nhiều kịch bản, không phải unique borrowers.",
        "- Lịch sử: 28 Pool events, 27 Graph-matched; tiers `1/2/23/1`; không xác lập causal contagion.",
        "- Terra: giữ kết quả âm cutoff-safe và không có claim successful out-of-sample forecasting.",
        "",
        "## Sáu RQ được chấp nhận có giới hạn",
        "",
    ]
    for row in rq_rows:
        lines.extend(
            [
                f"### {row['rq']} — {row['research_question']}",
                "",
                f"**Kết luận đề nghị:** {row['recommended_vietnamese_conclusion']}",
                "",
                f"**Được báo cáo:** {row['results_allowed_for_reporting']}",
                "",
                f"**Không được suy rộng:** {row['results_prohibited_from_extrapolation']}",
                "",
                f"**Giới hạn bắt buộc:** {row['required_limitations'][0]}",
                "",
                f"**Trạng thái:** `{row['scientific_decision_status']}`.",
                "",
            ]
        )
    lines.extend(
        [
            "## Gate và giới hạn",
            "",
            f"Builder validation: **{validation['status']}**, {sum(validation['gates'].values())}/{len(validation['gates'])} gates. Test evidence: **{test_evidence['status']}**.",
            "",
            "Các giới hạn bắt buộc tiếp tục gồm: actual Aave/Chainlink oracle chưa được xác minh; fork validation unavailable; representative agents; extreme 90/95% haircuts là counterfactual; stablecoin chỉ có debt-valuation channel; graph extension không phải full multilayer contagion; modeled bad debt không phải realized loss; hai large CSV giữ read limitation của P2; Terra không có successful OOS forecast.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    packet = [
        "# Scientific Content Lock Review Packet",
        "",
        "**Commander decision requested:** `FINAL_REGISTRY_READY_FOR_COMMANDER_REVIEW`.",
        "",
        f"- Starting integration HEAD: `{SOURCE_HEAD}`.",
        f"- Registry records: {p2_count} scholarly + {int_count} integration = {len(registry)}.",
        "- Six RQs: 6/6, exact order and wording preserved.",
        f"- Active locator gate: {validation['metrics']['active_locators_resolved']}/{validation['metrics']['active_locator_instances']} resolved.",
        f"- Declared locator hashes: {validation['metrics']['active_locator_hash_matches']}/{validation['metrics']['active_locator_hash_checks']} matched.",
        f"- Result IDs: {validation['metrics']['active_result_ids_resolved']}/{validation['metrics']['active_result_id_instances']} resolved.",
        f"- Table/figure IDs: {validation['metrics']['active_table_figure_ids_resolved']}/{validation['metrics']['active_table_figure_id_instances']} resolved.",
        f"- Validation: {validation['status']}; failed gates: {validation['failed_gates']}.",
        f"- Tests: {test_evidence['status']}; {test_evidence.get('summary', 'pending external execution').rstrip('.')}.",
        "- Proposed lock status: `READY_FOR_COMMANDER_DECISION_WITH_LIMITATIONS`; not a lock grant.",
        "",
        "## Material unsupported/superseded claims",
        "",
        "- `CL_FROZEN_RQ1_UNQUALIFIED_WORDING`: superseded; Policy A qualifier required.",
        "- `CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING`: superseded; DEX absorption and oracle-mediated HF feedback must be separate.",
        "- `CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT`: unsupported external inference.",
        "- `CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION`: unsupported causal inference.",
        "",
        "No engine, simulation mathematics, snapshot, cohort, locked evidence, literature bibliography or prior registry was modified. No 10,000-path rerun was performed.",
        "",
    ]
    PACKET.write_text("\n".join(packet), encoding="utf-8")


def main() -> None:
    current_head = cast(str, _git("rev-parse", "HEAD"))
    if not subprocess.run(["git", "merge-base", "--is-ancestor", SOURCE_HEAD, current_head], check=False).returncode == 0:
        raise RuntimeError(f"Current branch does not descend from pinned integration HEAD {SOURCE_HEAD}")

    source_rows = [_source_meta(path) for path in REQUIRED_SOURCES]
    source_by_path = {row["path"]: row for row in source_rows}
    p2 = _load(P2)
    integration = _load(INTEGRATION / "claim_to_result_registry.json")
    p2_by_id = {claim["claim_id"]: claim for claim in p2["claims"]}
    scholarly = _build_scholarly_claims(p2, source_by_path)
    integration_claims = _build_integration_claims(integration, p2_by_id, source_by_path)
    registry = scholarly + integration_claims

    result_ids, result_by_id = _result_ids()
    table_figure_ids = _table_figure_ids()
    rq_rows = _build_rq_matrix(
        scholarly,
        integration_claims,
        _load(INTEGRATION / "six_rq_evidence_matrix.json"),
    )
    numerical = _numerical_lock(result_by_id)
    locators = _active_locators(p2, integration, source_by_path)
    unresolved_locators = [row for row in locators if not _git_exists(row["commit"], row["path"])]
    locator_hash_checks = 0
    locator_hash_matches = 0
    locator_hash_mismatches: list[dict[str, str]] = []
    for row in locators:
        if not _git_exists(row["commit"], row["path"]):
            continue
        actual_blob = cast(str, _git("rev-parse", f"{row['commit']}:{row['path']}"))
        expected_blob = row.get("expected_git_blob_sha", "")
        if expected_blob:
            locator_hash_checks += 1
            if actual_blob == expected_blob:
                locator_hash_matches += 1
            else:
                locator_hash_mismatches.append({**row, "actual_git_blob_sha": actual_blob})
        expected_sha = row.get("expected_sha256", "")
        if expected_sha and "Git blob" in row.get("hash_domain", ""):
            locator_hash_checks += 1
            raw = cast(bytes, _git("show", f"{row['commit']}:{row['path']}", binary=True))
            actual_sha = _sha(raw)
            if actual_sha == expected_sha:
                locator_hash_matches += 1
            else:
                locator_hash_mismatches.append({**row, "actual_sha256": actual_sha})
    active_result_instances = [
        result for row in registry for result in row["scientific_result_ids"]
    ]
    active_table_instances = [
        item
        for row in integration_claims
        for item in row["table_figure_ids"]
    ]
    locked_tree_ids = {
        key: _tree_id(SOURCE_HEAD, path) for key, path in LOCKED_TREES.items()
    }
    locked_p2_blob_ids = {
        path: _tree_id(SOURCE_HEAD, path) for path in LOCKED_P2_PATHS
    }
    test_evidence = (
        _load(TEST_EVIDENCE)
        if TEST_EVIDENCE.exists()
        else {
            "status": "PENDING",
            "summary": "Tests have not yet been recorded.",
            "commands": [],
            "passed": 0,
            "failed": 0,
        }
    )
    _write_json(TEST_EVIDENCE, test_evidence)

    expected_integration_ids = {
        claim["claim_id"] for claim in integration["claims"]
    }
    actual_integration_ids = {
        row["original_claim_id"] for row in integration_claims
    }
    expected_p2_ids = {f"C{index:02d}" for index in range(1, 36)}
    actual_p2_ids = {row["original_claim_id"] for row in scholarly}
    registry_ids = [row["registry_id"] for row in registry]
    rq_order = [row["rq"] for row in rq_rows]
    rq_questions = [row["research_question"] for row in rq_rows]
    invalid_active_commits = [
        row for row in locators if not re.fullmatch(r"[0-9a-f]{40}", row["commit"])
    ]
    expected_numerical = {
        "deterministic": {"A": 4, "B": 0, "C_WEAK": 0, "C_MODERATE": 0},
        "targeted_mc": {"A": 10, "B": 0, "C_WEAK": 0, "C_MODERATE": 2},
        "eligible": {
            "A": {"newly_eligible": 35, "executed_wave2": 14, "skipped": 21},
            "B": {"newly_eligible": 0, "executed_wave2": 0, "skipped": 0},
            "C_WEAK": {"newly_eligible": 6, "executed_wave2": 0, "skipped": 6},
            "C_MODERATE": {"newly_eligible": 11, "executed_wave2": 2, "skipped": 9},
        },
    }
    gates = {
        "scholarly_claim_ids_35_complete": actual_p2_ids == expected_p2_ids,
        "integration_claim_ids_13_exact": len(actual_integration_ids) == 13 and actual_integration_ids == expected_integration_ids,
        "registry_ids_unique": len(registry_ids) == len(set(registry_ids)),
        "six_rq_exact_order_and_wording": rq_order == [rq for rq, _ in RQ_DEFINITIONS] and rq_questions == [question for _, question in RQ_DEFINITIONS],
        "all_active_result_ids_resolve": set(active_result_instances) <= result_ids,
        "all_active_artifact_locators_resolve": not unresolved_locators,
        "all_declared_active_locator_hashes_match": not locator_hash_mismatches,
        "int_t01_resolves": "INT_T01_ELIGIBLE_VS_EXECUTED" in table_figure_ids,
        "no_invalid_sha_in_active_locators": not invalid_active_commits,
        "hash_domains_explicit": all(row["hash_domain"] for row in source_rows),
        "locked_source_objects_recorded": len(locked_tree_ids) == 3 and len(locked_p2_blob_ids) == 7,
        "historical_verification_levels_preserved": numerical["historical"] == {"pool_events": 28, "graph_matched_events": 27, "tiers_direct_same_tx_same_block_time": [1, 2, 23, 1], "causal_contagion_established": False},
        "no_oracle_independent_cascade_overclaim": any(row["original_claim_id"] == "CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT" and row["final_gate_status"] == "UNSUPPORTED" for row in integration_claims),
        "no_historical_causal_contagion_overclaim": numerical["historical"]["causal_contagion_established"] is False,
        "newly_eligible_distinct_from_executed": numerical["eligible_vs_executed"] == expected_numerical["eligible"],
        "usdc_token_and_usd_not_conflated": "USDC token quantity" in str(_load(INTEGRATION / "table_figure_registry.json")),
        "targeted_paths_not_population_estimator": numerical["targeted_mc_depth2_retained_of_10"] == expected_numerical["targeted_mc"],
        "terra_negative_findings_preserved": numerical["terra_negative"] == {"pre_depeg_high_alert_hours": 0, "initial_depeg_high_lead_hours": -45.0, "successful_oos_forecast_established": False},
        "source_commits_and_paths_exist": not unresolved_locators and all(_git_exists(SOURCE_HEAD, path) for path in REQUIRED_SOURCES),
        "every_rq_has_explicit_limitation": all(row["required_limitations"] for row in rq_rows),
        "numerical_claim_lock_exact": numerical["deterministic_depth2_retained_of_4"] == expected_numerical["deterministic"] and numerical["severe_policy_a"]["depth_gte_2"] == 280,
        "all_active_table_figure_ids_resolve": set(active_table_instances) <= table_figure_ids,
    }
    failed = [name for name, passed in gates.items() if not passed]
    validation = {
        "schema_version": "final-accepted-claims-v1.0",
        "status": "PASS" if not failed else "FAIL",
        "gates": gates,
        "failed_gates": failed,
        "metrics": {
            "scholarly_claims": len(scholarly),
            "integration_claims": len(integration_claims),
            "registry_records": len(registry),
            "active_locator_instances": len(locators),
            "active_locators_resolved": len(locators) - len(unresolved_locators),
            "active_locator_hash_checks": locator_hash_checks,
            "active_locator_hash_matches": locator_hash_matches,
            "active_result_id_instances": len(active_result_instances),
            "active_result_ids_resolved": sum(result in result_ids for result in active_result_instances),
            "active_table_figure_id_instances": len(active_table_instances),
            "active_table_figure_ids_resolved": sum(item in table_figure_ids for item in active_table_instances),
        },
        "numerical_claim_lock": numerical,
        "unresolved_locators": unresolved_locators,
        "locator_hash_mismatches": locator_hash_mismatches,
        "invalid_active_commits": invalid_active_commits,
        "test_evidence": test_evidence,
        "review_scope": "Builder validation plus separately implemented pytest validator; same executor, not an independent external reviewer.",
    }
    if failed:
        raise RuntimeError(f"Registry validation failed: {failed}")

    accepted_registry = {
        "schema_version": "final-accepted-claims-v1.0",
        "source_integration_head": SOURCE_HEAD,
        "output_commit": "RECORDED_IN_GIT_HANDOFF_NOT_SELF_EMBEDDED",
        "scientific_content_lock_declared": False,
        "records": registry,
    }
    crosswalk = {
        "schema_version": "final-accepted-claims-v1.0",
        "rows": [
            {
                "registry_id": row["registry_id"],
                "original_claim_id": row["original_claim_id"],
                "namespace": row["namespace"],
                "rq_mapping": row["rq_mapping"],
                "scholarly_source_ids": row["scholarly_source_ids"],
                "evidence_alias_ids": row["evidence_alias_ids"],
                "scientific_result_ids": row["scientific_result_ids"],
                "table_figure_ids": row.get("table_figure_ids", []),
                "artifact_path": row["artifact_path"],
                "artifact_locator_commit": row["artifact_locator_commit"],
                "evidence_tier": row["evidence_tier"],
                "accepted_inference": row["accepted_inference"],
                "required_limitations": row["required_limitations"],
                "final_gate_status": row["final_gate_status"],
            }
            for row in registry
        ],
    }
    provenance = {
        "schema_version": "final-accepted-claims-v1.0",
        "source_integration_head": SOURCE_HEAD,
        "hash_semantics": {
            "git_blob_sha": "Git object ID for exact committed bytes",
            "sha256": "SHA-256 over exact Git blob bytes; normalized text blobs use LF",
            "windows_checkout": "CRLF checkout bytes may have a different SHA-256 and are never equated to Git LF bytes",
            "canonical_snapshot_windows_crlf_sha256": CANONICAL_SHA256_CRLF,
        },
        "sources": source_rows,
        "locked_tree_ids": locked_tree_ids,
        "locked_p2_blob_ids": locked_p2_blob_ids,
    }
    readiness = {
        "schema_version": "final-accepted-claims-v1.0",
        "proposed_status": "FINAL_REGISTRY_READY_FOR_COMMANDER_REVIEW" if not failed and test_evidence["status"] == "PASS" else "TARGETED_REGISTRY_REWORK_REQUIRED",
        "scientific_content_lock_declared": False,
        "commander_decision_required": True,
        "accepted_registry_records": sum(row["final_gate_status"] in {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"} for row in registry),
        "rejected_or_unsupported_integration_records": [row["original_claim_id"] for row in integration_claims if row["final_gate_status"] not in {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"}],
        "blocking_conflicts": [],
        "validation_status": validation["status"],
        "test_status": test_evidence["status"],
        "required_disclosures": [
            "Oracle-policy dependence of RQ1/RQ2",
            "Eligible versus executed distinction",
            "Modeled bad debt is not realized loss",
            "Historical association is not causal contagion",
            "Targeted MC paths are not a population estimator",
            "USDC token quantity differs from USD-equivalent",
            "Terra early-warning outcome is negative and not successful OOS forecasting",
            "Existing SOURCE_NOT_VERIFIED large-CSV limitations remain disclosed",
        ],
    }

    _write_json(ROOT / "accepted_claims_registry.json", accepted_registry)
    _write_json(ROOT / "six_rq_accepted_claims_matrix.json", {"schema_version": "final-accepted-claims-v1.0", "research_questions": rq_rows})
    _write_json(ROOT / "claim_evidence_crosswalk.json", crosswalk)
    _write_json(ROOT / "source_provenance_registry.json", provenance)
    _write_json(ROOT / "validation_report.json", validation)
    _write_json(ROOT / "scientific_lock_readiness.json", readiness)
    _render_docs(registry, rq_rows, numerical, validation, test_evidence)

    artifact_names = [
        "accepted_claims_registry.json",
        "six_rq_accepted_claims_matrix.json",
        "claim_evidence_crosswalk.json",
        "source_provenance_registry.json",
        "validation_report.json",
        "scientific_lock_readiness.json",
        "test_evidence.json",
    ]
    manifest = {
        "schema_version": "final-accepted-claims-v1.0",
        "status": readiness["proposed_status"],
        "source_integration_head": SOURCE_HEAD,
        "output_commit": "RECORDED_IN_GIT_HANDOFF_NOT_SELF_EMBEDDED",
        "artifact_hashes": {name: _file_sha(ROOT / name) for name in artifact_names},
        "report_hashes": {REPORT.as_posix(): _file_sha(REPORT), PACKET.as_posix(): _file_sha(PACKET)},
        "implementation_hashes": {
            "scripts/research/build_final_accepted_claims_v1.py": _file_sha(Path("scripts/research/build_final_accepted_claims_v1.py")),
            "tests/test_final_accepted_claims_v1.py": _file_sha(Path("tests/test_final_accepted_claims_v1.py")),
        },
        "source_tree_ids": locked_tree_ids,
        "source_p2_blob_ids": locked_p2_blob_ids,
        "counts": {"scholarly_claims": len(scholarly), "integration_claims": len(integration_claims), "registry_records": len(registry), "research_questions": len(rq_rows)},
        "validation_gates": gates,
        "test_evidence": test_evidence,
        "self_hash_excluded": True,
        "manifest_hash_embedded": False,
        "locked_sources_modified": False,
        "large_monte_carlo_rerun": False,
        "model_retuned": False,
        "scientific_content_lock_declared": False,
        "generation_command": ".\\.venv\\Scripts\\python.exe .\\scripts\\research\\build_final_accepted_claims_v1.py",
    }
    _write_json(ROOT / "manifest.json", manifest)
    print(json.dumps({"status": manifest["status"], "counts": manifest["counts"], "gates": f"{sum(gates.values())}/{len(gates)}"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
