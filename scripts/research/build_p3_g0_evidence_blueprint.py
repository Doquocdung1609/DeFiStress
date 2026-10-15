# ruff: noqa: E501 -- reviewed Vietnamese scientific wording must remain explicit.
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

SOURCE_LOCK = "3f6e5302483681209e2408531eb5a15389f9fded"
ROOT = Path("data/processed/research_final/final_accepted_claims_v1")
FROZEN = Path("data/processed/research_final/frozen_v3")
ORACLE = Path("data/processed/research_final/oracle_transmission_diagnostic_v1")
INTEGRATION = Path("data/processed/research_final/scientific_integration_v1")
ARTIFACT_ROOT = Path("artifacts/manuscript_p3")
DOC_ROOT = Path("docs/manuscript_p3/codex")

INVENTORY_PATH = ARTIFACT_ROOT / "P3_LOCKED_EVIDENCE_INVENTORY.json"
CATALOG_PATH = ARTIFACT_ROOT / "P3_EXHIBIT_CATALOG_v1.json"
HANDOFF_PATH = ARTIFACT_ROOT / "P3_WORK_CODEX_EVIDENCE_HANDOFF.json"
BASELINE_PATH = DOC_ROOT / "P3_TECHNICAL_MANUSCRIPT_BASELINE_AUDIT.md"
FORMULA_PATH = DOC_ROOT / "P3_FORMULA_AUDIT_PLAN.md"
REPRO_PATH = DOC_ROOT / "P3_EXHIBIT_REPRODUCIBILITY_PLAN.md"

AFFIRMATIVE_STATUSES = {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"}
DISALLOWED_IDS = {
    "INT:CL_FROZEN_RQ1_UNQUALIFIED_WORDING",
    "INT:CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING",
    "INT:CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT",
    "INT:CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION",
}
RQ_ORDER = [f"RQ{index}" for index in range(1, 7)]

LOCKED_PACKAGE_PATHS = [
    ROOT / "manifest.json",
    ROOT / "accepted_claims_registry.json",
    ROOT / "six_rq_accepted_claims_matrix.json",
    ROOT / "claim_evidence_crosswalk.json",
    ROOT / "source_provenance_registry.json",
    ROOT / "validation_report.json",
    ROOT / "scientific_lock_readiness.json",
    FROZEN / "manifest.json",
    FROZEN / "results_registry.json",
    FROZEN / "evidence_source_matrix.json",
    ORACLE / "manifest.json",
    ORACLE / "comparison_matrix.csv",
    ORACLE / "selection_manifest.json",
    ORACLE / "scientific_interpretation.json",
    INTEGRATION / "manifest.json",
    INTEGRATION / "integration_result_registry.json",
    INTEGRATION / "eligible_vs_executed_summary.csv",
    INTEGRATION / "eligible_vs_executed_audit.csv",
    INTEGRATION / "table_figure_registry.json",
    Path("docs/research_final/LITERATURE_VERIFIED.md"),
    Path("docs/research_final/REFERENCE_EVIDENCE_MATRIX.md"),
    Path("docs/research_final/APA_REFERENCES_VERIFIED.md"),
    Path("docs/research_final/TERMINOLOGY_VI.md"),
    Path("docs/research_final/P2_VERSION_RECONCILIATION.md"),
    Path("docs/research_final/P2_ORACLE_RECONCILIATION.md"),
    Path("docs/research_final/P2_CLAIM_EVIDENCE_CROSSWALK.json"),
]

FORMULA_SOURCE_PATHS = [
    Path("sim/lending/health_factor.py"),
    Path("sim/lending/liquidation.py"),
    Path("sim/agents/liquidator.py"),
    Path("sim/oracle.py"),
    Path("sim/dex/uniswap_v3.py"),
    Path("sim/engine/run.py"),
    Path("sim/metrics/risk.py"),
    Path("sim/network/metrics.py"),
    Path("sim/schemas.py"),
]

SUPPORTING_LOCKED_PATHS = [
    Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json"),
    Path("data/processed/research_final/validation_audit/corrected_run_v2/manifest.json"),
    Path("data/processed/research_final/level3_extension/manifest.json"),
    Path("data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json"),
    Path("data/processed/research_final/level3_p1_targeted_repair/manifest.json"),
    Path("data/processed/research_final/terra/audit/reproducibility_manifest.json"),
    Path("data/processed/research_final/validation_audit/corrected_run_v2/network/structural_graph.json"),
]

DOCX_BASELINE = [
    {
        "file_name": "DeFiStress_BAO_CAO_NCKH_HOAN_CHINH.docx",
        "sha256": "9c8486027efcd35fe8fbcb8ba4c9fd6cfb714d2785f40ca6a64c247627dceb96",
        "size_bytes": 3_820_731,
        "rendered_pages": 33,
        "paragraphs": 349,
        "tables": 22,
        "sections": 3,
        "inline_images": 16,
        "heading_style_counts": {"Heading 1": 5, "Heading 2": 40, "Heading 3": 12},
        "caption_style_paragraphs": 31,
        "source_note_style_paragraphs": 31,
        "word_fields": {"TOC": 1, "PAGE": 1, "SEQ": 0, "REF": 0},
        "omml_equations": 0,
        "comments": 0,
        "tracked_insertions": 0,
        "tracked_deletions": 0,
        "accessibility_findings": {"high": 16, "medium": 22, "low": 0},
        "table_geometry_findings": 229,
        "visual_review": "ALL_33_PAGES_REVIEWED_READ_ONLY",
        "role": "HISTORICAL_FIVE_CHAPTER_BASELINE_NOT_SCHOOL_TEMPLATE_TRUTH",
    },
    {
        "file_name": "DeFi_Stress_Lab_Mo_Dau_Tong_Quan_Nghien_Cuu.docx",
        "sha256": "582d489189a156f00a563d22b6db36caab8094d7a3581d220b96d8b3f1aebdd5",
        "size_bytes": 52_834,
        "rendered_pages": 13,
        "paragraphs": 106,
        "tables": 8,
        "sections": 1,
        "inline_images": 0,
        "heading_style_counts": {"Heading 1": 11, "Heading 2": 12, "Heading 3": 0},
        "caption_style_paragraphs": 0,
        "source_note_style_paragraphs": 0,
        "word_fields": {"TOC": 0, "PAGE": 1, "SEQ": 0, "REF": 0},
        "omml_equations": 0,
        "comments": 0,
        "tracked_insertions": 0,
        "tracked_deletions": 0,
        "accessibility_findings": {"high": 0, "medium": 4, "low": 0},
        "table_geometry_findings": 36,
        "visual_review": "ALL_13_PAGES_REVIEWED_READ_ONLY",
        "role": "HISTORICAL_INTRODUCTION_AND_LITERATURE_BASELINE_NOT_SCHOOL_TEMPLATE_TRUTH",
    },
]


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git(*args: str, binary: bool = False) -> bytes | str:
    completed = subprocess.run(["git", *args], check=True, capture_output=True)
    return completed.stdout if binary else completed.stdout.decode("utf-8").strip()


def _git_blob(path: Path) -> tuple[str, bytes]:
    name = path.as_posix()
    blob_id = cast(str, _git("rev-parse", f"{SOURCE_LOCK}:{name}"))
    blob_bytes = cast(bytes, _git("cat-file", "blob", blob_id, binary=True))
    return blob_id, blob_bytes


def _canonical_json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _seal_json(value: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(value, ensure_ascii=False))
    metadata = payload.setdefault("output_provenance", {})
    metadata["content_sha256_domain"] = "UTF-8 canonical JSON with output_provenance.content_sha256 omitted"
    metadata.pop("content_sha256", None)
    metadata["content_sha256"] = _sha256_bytes(_canonical_json_bytes(payload))
    return cast(dict[str, Any], payload)


def _seal_markdown(text: str) -> str:
    body = text.rstrip() + "\n"
    digest = _sha256_bytes(body.encode("utf-8"))
    return body + f"\nContent SHA-256 (UTF-8, excluding this checksum line): `{digest}`\n"


def _cardinality(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            rows = sum(1 for _ in csv.reader(handle))
        return {"kind": "CSV data rows", "value": max(0, rows - 1)}
    if path.suffix.lower() == ".jsonl":
        return {
            "kind": "JSONL non-empty rows",
            "value": sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line),
        }
    if path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, list):
            return {"kind": "top-level list records", "value": len(value)}
        if isinstance(value, dict):
            for key in ("records", "results", "rows", "claims", "research_questions", "events", "figures", "tables"):
                if isinstance(value.get(key), list):
                    return {"kind": f"JSON {key} records", "value": len(value[key])}
            return {"kind": "top-level object keys", "value": len(value)}
    return {"kind": "NOT_APPLICABLE", "value": None}


def _data_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "RAW_OR_DERIVED_TABULAR_CSV"
    if suffix == ".jsonl":
        return "EVENT_TRACE_JSONL"
    if suffix == ".json":
        return "STRUCTURED_JSON"
    if suffix == ".png":
        return "LOCKED_RASTER_FIGURE"
    if suffix == ".py":
        return "SOURCE_CODE"
    if suffix == ".md":
        return "DOCUMENTATION"
    return suffix.removeprefix(".").upper() or "UNKNOWN"


def _hash_domain(path: Path, blob_bytes: bytes) -> dict[str, Any]:
    checkout = path.read_bytes()
    normalized = (
        checkout.replace(b"\r\n", b"\n")
        if path.suffix.lower() in {".csv", ".json", ".jsonl", ".md", ".py"}
        else checkout
    )
    return {
        "git_blob_sha256": _sha256_bytes(blob_bytes),
        "checkout_sha256": _sha256_bytes(checkout),
        "normalized_lf_sha256": _sha256_bytes(normalized),
        "checkout_line_endings": "CRLF_OR_MIXED" if b"\r\n" in checkout else "LF_OR_BINARY",
    }


def _resolve_table_figures() -> dict[str, dict[str, Any]]:
    frozen = _load(FROZEN / "evidence_source_matrix.json")
    resolved: dict[str, dict[str, Any]] = {}
    for row in frozen["figure_registry"]:
        resolved[row["figure_id"]] = {**row, "path": row["path"]}
    for row in frozen["table_registry"]:
        resolved[row["table_id"]] = {**row, "path": str(FROZEN / row["path"])}
    for row in _load(INTEGRATION / "table_figure_registry.json")["tables"]:
        resolved[row["table_id"]] = row
    return resolved


def _locked_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    records = cast(list[dict[str, Any]], _load(ROOT / "accepted_claims_registry.json")["records"])
    affirmative = [row for row in records if row["final_gate_status"] in AFFIRMATIVE_STATUSES]
    results = [
        *cast(list[dict[str, Any]], _load(FROZEN / "results_registry.json")["results"]),
        *cast(list[dict[str, Any]], _load(INTEGRATION / "integration_result_registry.json")["results"]),
    ]
    return records, affirmative, {row["result_id"]: row for row in results}


def _build_inventory() -> dict[str, Any]:
    records, affirmative, result_index = _locked_records()
    claim_by_result: dict[str, set[str]] = defaultdict(set)
    claim_by_path: dict[str, set[str]] = defaultdict(set)
    for claim in affirmative:
        for result_id in claim.get("scientific_result_ids", []):
            claim_by_result[result_id].add(claim["registry_id"])
        for locator in claim.get("active_artifact_locators", []):
            if isinstance(locator, dict) and locator.get("path"):
                claim_by_path[str(locator["path"])].add(claim["registry_id"])
        for path in claim.get("primary_evidence_paths", []):
            claim_by_path[str(path)].add(claim["registry_id"])

    accepted_result_ids = sorted(claim_by_result)
    result_paths = {Path(result_index[result_id]["source_path"]) for result_id in accepted_result_ids}
    table_figure_index = _resolve_table_figures()
    accepted_table_figure_ids = sorted({item for row in affirmative for item in row.get("table_figure_ids", [])})
    table_figure_paths = {Path(table_figure_index[item]["path"]) for item in accepted_table_figure_ids}
    paths = sorted(
        {
            *LOCKED_PACKAGE_PATHS,
            *FORMULA_SOURCE_PATHS,
            *SUPPORTING_LOCKED_PATHS,
            *result_paths,
            *table_figure_paths,
        },
        key=lambda item: item.as_posix(),
    )

    inventory: list[dict[str, Any]] = []
    path_to_evidence: dict[str, str] = {}
    for index, path in enumerate(paths, start=1):
        if not path.is_file():
            raise FileNotFoundError(path)
        blob_id, blob_bytes = _git_blob(path)
        path_key = path.as_posix()
        result_ids = sorted(
            result_id for result_id in accepted_result_ids if result_index[result_id]["source_path"] == path_key
        )
        table_figure_ids = sorted(
            item for item in accepted_table_figure_ids if table_figure_index[item]["path"] == path_key
        )
        for item in table_figure_ids:
            result_ids = sorted({*result_ids, *table_figure_index[item].get("result_ids", [])})
        accepted_claim_ids = sorted(
            {
                *claim_by_path[path_key],
                *(claim for result_id in result_ids for claim in claim_by_result.get(result_id, set())),
            }
        )
        result_rows = [result_index[result_id] for result_id in result_ids if result_id in result_index]
        evidence_id = f"P3E:{index:03d}"
        path_to_evidence[path_key] = evidence_id
        tiers = sorted({str(row.get("evidence_type") or row.get("evidence_tier")) for row in result_rows})
        units = sorted({str(row.get("unit")) for row in result_rows if row.get("unit") is not None})
        populations = sorted({str(row.get("population")) for row in result_rows if row.get("population")})
        policies = sorted({str(row.get("policy_id")) for row in result_rows if row.get("policy_id")})
        conditions = sorted({str(row.get("conditions")) for row in result_rows if row.get("conditions")})
        limitations = sorted(
            {str(row.get("interpretation_limit")) for row in result_rows if row.get("interpretation_limit")}
        )
        source_commits = sorted({str(row.get("source_commit")) for row in result_rows if row.get("source_commit")})
        hash_info = _hash_domain(path, blob_bytes)
        hash_info["git_blob_id"] = blob_id
        readiness = "SOURCE_VERIFIED_TRANSFORMATION_SPEC_REQUIRED"
        if path.suffix.lower() == ".png":
            readiness = "EXISTING_RENDERED_LOCKED_REUSE_REQUIRES_CAPTION_REVIEW"
        elif path.suffix.lower() == ".py":
            readiness = "FORMULA_OR_IMPLEMENTATION_SOURCE_ONLY"
        elif path in LOCKED_PACKAGE_PATHS:
            readiness = "PROVENANCE_OR_REGISTRY_SOURCE"
        inventory.append(
            {
                "evidence_id": evidence_id,
                "result_ids": result_ids,
                "table_figure_ids": table_figure_ids,
                "original_artifact_path": path_key,
                "scientific_lock_commit": SOURCE_LOCK,
                "original_source_commits": source_commits or [SOURCE_LOCK],
                "git_blob_id": blob_id,
                "checksums": hash_info,
                "checksum_domain": "Git blob LF bytes and local checkout bytes reported separately",
                "evidence_tier": tiers or ["LOCKED_PROVENANCE_OR_CODE_OBSERVATION"],
                "data_type": _data_type(path),
                "units": units or ["NOT_APPLICABLE"],
                "cardinality": _cardinality(path),
                "cohort": populations or ["NOT_APPLICABLE_OR_DEFINED_BY_SOURCE"],
                "scenario": conditions or ["NOT_APPLICABLE_OR_DEFINED_BY_SOURCE"],
                "policy": policies or ["NOT_APPLICABLE_OR_DEFINED_BY_SOURCE"],
                "read_verification_level": "BYTE_HASH_AND_GIT_BLOB_VERIFIED_AT_SOURCE_LOCK",
                "corresponding_accepted_claim_ids": accepted_claim_ids,
                "mandatory_limitations": limitations or ["Use only within the locked claim and source scope."],
                "rendering_readiness": readiness,
            }
        )

    for offset, docx in enumerate(DOCX_BASELINE, start=1):
        inventory.append(
            {
                "evidence_id": f"P3EXT:DOCX{offset}",
                "result_ids": [],
                "table_figure_ids": [],
                "original_artifact_path": f"external://Downloads/{docx['file_name']}",
                "scientific_lock_commit": "NOT_APPLICABLE_EXTERNAL_FILE",
                "original_source_commits": ["NOT_VERSIONED_IN_REPOSITORY"],
                "git_blob_id": "NOT_APPLICABLE",
                "checksums": {"external_binary_sha256": docx["sha256"]},
                "checksum_domain": "External DOCX binary bytes",
                "evidence_tier": ["TECHNICAL_MANUSCRIPT_BASELINE_ONLY"],
                "data_type": "DOCX_BASELINE",
                "units": ["pages", "tables", "figures", "styles", "fields"],
                "cardinality": {"kind": "rendered pages", "value": docx["rendered_pages"]},
                "cohort": ["NOT_APPLICABLE"],
                "scenario": ["NOT_APPLICABLE"],
                "policy": ["NOT_APPLICABLE"],
                "read_verification_level": docx["visual_review"],
                "corresponding_accepted_claim_ids": [],
                "mandatory_limitations": [
                    "Historical manuscript baseline only; not a locked numerical source and not verified as the official school template."
                ],
                "rendering_readiness": "READ_ONLY_BASELINE_AUDITED_NOT_APPROVED_FOR_REUSE",
                "technical_summary": docx,
            }
        )

    return _seal_json(
        {
            "schema_version": "p3-g0-locked-evidence-inventory-v1",
            "transformation_version": "p3-g0-builder-v1",
            "stage": "P3-G0_TECHNICAL_BLUEPRINT_ONLY",
            "source_lock_commit": SOURCE_LOCK,
            "scope": "Accepted-claim evidence, approved historical/model artifacts, formula sources and read-only manuscript baselines.",
            "counts": {
                "inventory_records": len(inventory),
                "accepted_claims": len(affirmative),
                "disallowed_claims": len(records) - len(affirmative),
                "accepted_result_ids": len(accepted_result_ids),
                "accepted_table_figure_ids": len(accepted_table_figure_ids),
                "research_questions": 6,
            },
            "locked_claim_counts": {
                "scholarly": sum(row["namespace"] == "SCHOLARLY_P2" for row in records),
                "integration_scientific": sum(row["namespace"] == "INTEGRATION_SCIENTIFIC" for row in records),
                "affirmative": len(affirmative),
                "disallowed": len(records) - len(affirmative),
            },
            "records": inventory,
            "path_to_p3_evidence_id": path_to_evidence,
            "limitations": [
                "P3 evidence IDs are technical rendering locators, not new scientific result IDs.",
                "Modeled counterfactuals are not Mainnet observations.",
                "External DOCX files are manuscript baselines only and are outside the scientific lock.",
            ],
        }
    )


def _catalog_specs() -> list[dict[str, Any]]:
    awaiting = "PROPOSED_AWAITING_WORK_BLUEPRINT_AND_COMMANDER_APPROVAL"
    return [
        {
            "exhibit_id": "P3X:SYSTEM_FEEDBACK_SCHEMATIC",
            "type": "SCHEMATIC_DIAGRAM",
            "working_title": "Vòng phản hồi mô hình Aave–Uniswap và vị trí chính sách định giá",
            "purpose": "Phân biệt bán bắt buộc, trạng thái DEX, chính sách định giá phản thực và eligibility vòng tiếp theo.",
            "accepted_claim_ids": [
                "P2:C19",
                "P2:C32",
                "INT:CL_INT_RQ1_POLICY_CONDITIONAL",
                "INT:CL_INT_RQ2_TWO_CHANNELS",
            ],
            "result_ids": [],
            "source_paths": ["sim/engine/run.py", "sim/oracle.py", "sim/agents/liquidator.py", "sim/dex/uniswap_v3.py"],
            "specification": "Directed schematic; solid arrows for implemented model flow, dashed enclosure for hypothetical A/B/C valuation policies; no empirical causal styling.",
            "units": ["NOT_APPLICABLE"],
            "denominators": ["NOT_APPLICABLE"],
            "policy_scenario": ["A/B/C are hypothetical valuation-policy sensitivity cases"],
            "evidence_tier": "CODE_OBSERVATION_AND_MODEL_DESIGN",
            "output_formats": ["SVG", "PNG", "PDF_VECTOR"],
            "caption_requirement": "State that this is a model schematic, not an observed historical causal chain.",
            "limitations": ["Policy A is not established as the actual Aave or Chainlink oracle."],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:ORACLE_POLICY_DEPTH2_COMPARISON",
            "type": "COMPARISON_TABLE",
            "working_title": "Depth-2 retained under selected oracle-transmission policies",
            "purpose": "Show policy dependence without pooling incompatible selected samples.",
            "accepted_claim_ids": ["P2:C32", "INT:CL_INT_RQ1_POLICY_CONDITIONAL"],
            "result_ids": [
                "INT_A_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4",
                "INT_B_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4",
                "INT_C_WEAK_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4",
                "INT_C_MODERATE_DETERMINISTIC_DEPTH2_RETAINED_COUNT_OF_4",
                "INT_A_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10",
                "INT_B_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10",
                "INT_C_WEAK_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10",
                "INT_C_MODERATE_SELECTED_MC_DEPTH2_RETAINED_COUNT_OF_10",
            ],
            "source_paths": [
                "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv",
                "data/processed/research_final/oracle_transmission_diagnostic_v1/comparison_matrix.csv",
            ],
            "specification": "Two panels: four selected deterministic depth-2 cases and ten deliberately selected MC depth-2-under-A paths; show counts 4/0/0/0 and 10/0/0/2 with denominators in labels.",
            "units": ["selected cases", "selected paths"],
            "denominators": [
                "4 preselected deterministic Policy-A depth-2 cases",
                "10 deliberately selected MC paths with depth-2 under Policy A",
            ],
            "policy_scenario": ["A", "B", "C weak", "C moderate"],
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
            "output_formats": ["CSV", "MARKDOWN_TABLE", "SVG"],
            "caption_requirement": "State that the ten paths are deliberately selected and are not a probability sample.",
            "limitations": ["No claim of a policy-independent cascade threshold."],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:ELIGIBLE_VS_EXECUTED",
            "type": "COMPARISON_TABLE",
            "working_title": "Portfolio-HF newly eligible versus route-specific Wave-2 execution",
            "purpose": "Prevent conflation of portfolio eligibility, attempted route processing and positive-debt execution.",
            "accepted_claim_ids": ["P2:C03", "P2:C33", "INT:CL_INT_ELIGIBLE_NOT_EXECUTED"],
            "result_ids": [
                "INT_A_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES",
                "INT_A_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES",
                "INT_A_NEWLY_ELIGIBLE_SKIPPED_INSTANCES",
                "INT_B_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES",
                "INT_B_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES",
                "INT_B_NEWLY_ELIGIBLE_SKIPPED_INSTANCES",
                "INT_C_WEAK_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES",
                "INT_C_WEAK_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES",
                "INT_C_WEAK_NEWLY_ELIGIBLE_SKIPPED_INSTANCES",
                "INT_C_MODERATE_NEWLY_ELIGIBLE_BORROWER_CASE_INSTANCES",
                "INT_C_MODERATE_NEWLY_ELIGIBLE_EXECUTED_WAVE2_INSTANCES",
                "INT_C_MODERATE_NEWLY_ELIGIBLE_SKIPPED_INSTANCES",
            ],
            "source_paths": [
                "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_summary.csv",
                "data/processed/research_final/scientific_integration_v1/eligible_vs_executed_audit.csv",
            ],
            "specification": "Rows A/B/C weak/C moderate; columns newly eligible, executed positive-debt Wave 2 and skipped; fixed locked values 35/14/21, 0/0/0, 6/0/6, 11/2/9.",
            "units": ["borrower-case-policy instances"],
            "denominators": ["18 selected cases × 4 policies × 454 verified borrowers; counts are not unique wallets"],
            "policy_scenario": ["selected diagnostic cases only"],
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL",
            "output_formats": ["CSV", "MARKDOWN_TABLE"],
            "caption_requirement": "Explain that 36 skipped instances lack modeled USDC debt on the WETH/USDC route; do not attribute them to gas, capital or profitability.",
            "limitations": ["Portfolio HF eligibility differs from route eligibility and execution."],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS",
            "type": "MECHANISM_TABLE",
            "working_title": "DEX absorption, immediate price impact and post-arbitrage residual",
            "purpose": "Separate DEX depth, forced-sale impact and stabilization residual before relating them to HF policy.",
            "accepted_claim_ids": [
                "P2:C07",
                "P2:C13",
                "P2:C34",
                "INT:CL_INT_RQ2_TWO_CHANNELS",
                "INT:CL_INT_RQ4_PRESERVED",
            ],
            "result_ids": [
                "RQ2_CANONICAL_DEPTH_2PCT",
                "RQ4_IMMEDIATE_PRICE_IMPACT",
                "RQ4_SPREAD_ARB0",
                "RQ4_SPREAD_ARB100",
            ],
            "source_paths": [
                "data/processed/research_final/validation_audit/corrected_run_v2/aave/research_summary.json",
                "data/processed/research_final/validation_audit/corrected_run_v2/aave/deterministic_scenarios.csv",
                "data/processed/research_final/frozen_v3/figures/F04_arbitrage_impact_and_residual_spread.png",
            ],
            "specification": "Prefer a table or two-scale panel only after Work selects the narrative; retain exact locked units and distinguish immediate impact from residual spread.",
            "units": ["USDC executable depth", "ratio or percent of reference price"],
            "denominators": ["canonical WETH/USDC 0.3% pool at one block", "one locked −20%/40% scenario"],
            "policy_scenario": ["single pool; modeled price repositioning"],
            "evidence_tier": "OBSERVED_POOL_STATE_PLUS_MODEL_COMPUTED_COUNTERFACTUAL",
            "output_formats": ["CSV", "MARKDOWN_TABLE", "SVG"],
            "caption_requirement": "State that price repositioning is not a funded executable arbitrage swap.",
            "limitations": ["One pool/block; no multi-venue routing; 90/95% haircuts are extreme counterfactuals."],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:SEVERE_POLICY_A_MONTE_CARLO",
            "type": "LOCKED_FIGURE_OR_TABLE",
            "working_title": "Severe Policy-A depth≥2 frequency across locked prefixes",
            "purpose": "Present 280/10,000 with its conditional sampling scope and already locked uncertainty only.",
            "accepted_claim_ids": ["P2:C23", "INT:CL_INT_RQ1_POLICY_CONDITIONAL"],
            "result_ids": [
                "RQ1_MC_SEVERE_DEPTH2_COUNT",
                "RQ1_MC_SEVERE_DEPTH2_FREQUENCY",
                "MC_INDEPENDENT_PATHS_VALIDATED",
            ],
            "source_paths": [
                "data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json",
                "data/processed/research_final/level3_p1_targeted_repair/monte_carlo/checkpoint_validation.json",
                "data/processed/research_final/frozen_v3/figures/F02_severe_mc_prefix_convergence.png",
            ],
            "specification": "Reuse locked prefix figure only if caption is updated to Policy A and nested-prefix semantics; do not recompute a new interval in G0.",
            "units": ["paths", "model-conditional frequency"],
            "denominators": ["10,000 Severe Policy-A paths; nested prefixes are not additive"],
            "policy_scenario": ["Severe, Policy A, seed 20260914"],
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL_AND_CHECKPOINT_AUDIT",
            "output_formats": ["PNG_REUSE", "CSV", "MARKDOWN_TABLE"],
            "caption_requirement": "Not an Ethereum crisis probability; targeted ten-path diagnostic is not the denominator.",
            "limitations": [
                "No depth≥3 in the locked reported sample; model frequency does not include structural uncertainty."
            ],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:HISTORICAL_EVIDENCE_TIERS",
            "type": "EVIDENCE_TABLE",
            "working_title": "Historical Aave liquidation census and association tiers",
            "purpose": "Report the 28/27 census and 1/2/23/1 evidence tiers without causal arrows.",
            "accepted_claim_ids": ["P2:C09", "P2:C10", "INT:CL_INT_HISTORICAL_TIERS_PRESERVED"],
            "result_ids": [
                "HIST_RPC_CENSUS_EVENTS",
                "HIST_GRAPH_MATCHED_EVENTS",
                "HIST_DIRECT_TRANSFER_PATHS",
                "HIST_SAME_TX_COOCCURRENCE",
                "HIST_SAME_BLOCK_ASSOCIATION",
                "HIST_TIME_WINDOW_ASSOCIATION",
            ],
            "source_paths": [
                "data/processed/research_final/level3_p1_targeted_repair/historical/census_reconciliation.json",
                "data/processed/research_final/level3_p1_targeted_repair/historical/linkage_route_audit.json",
                "data/processed/research_final/frozen_v3/tables/historical_evidence.csv",
            ],
            "specification": "Evidence ladder table; no Sankey or causal network rendering.",
            "units": ["LiquidationCall events"],
            "denominators": [
                "Aave V3 Pool, 2026-09-01 through 2026-09-07 UTC; 27 Graph-matched events for tier allocation"
            ],
            "policy_scenario": ["historical observation; no oracle policy"],
            "evidence_tier": "ONCHAIN_HISTORICAL_OBSERVATION",
            "output_formats": ["CSV", "MARKDOWN_TABLE"],
            "caption_requirement": "Same transaction/block/time-window association does not establish historical causal contagion.",
            "limitations": ["One preregistered week; Graph missed one census event."],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:TERRA_NEGATIVE_EARLY_WARNING",
            "type": "NEGATIVE_FINDING_TABLE",
            "working_title": "Terra cutoff-safe early-warning result",
            "purpose": "Preserve the negative pre-initial-depeg warning finding and distinguish retrospective reconstruction from forecasting.",
            "accepted_claim_ids": ["P2:C30", "INT:CL_INT_TERRA_NEGATIVE_PRESERVED"],
            "result_ids": ["TERRA_PRE_DEPEG_HIGH_ALERT_HOURS", "TERRA_INITIAL_DEPEG_HIGH_LEAD"],
            "source_paths": [
                "data/processed/research_final/validation_audit/phase5_terra_early_warning_audit.json",
                "data/processed/research_final/frozen_v3/tables/terra_limitations.csv",
            ],
            "specification": "Compact table; zero pre-depeg high-alert hours and −45-hour lead reported as a negative result, not a success chart.",
            "units": ["hours"],
            "denominators": ["1,630 pre-initial-depeg hours; UST<0.995 event"],
            "policy_scenario": ["cutoff-safe historical-validation design"],
            "evidence_tier": "DERIVED_HISTORICAL_VALIDATION_RESULT",
            "output_formats": ["CSV", "MARKDOWN_TABLE"],
            "caption_requirement": "No genuine out-of-sample forecasting claim is supported.",
            "limitations": [
                "Design choices were event-informed; lower-frequency price carry and feature availability limit inference."
            ],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:NETWORK_EXTENSION_BOUNDARY",
            "type": "BOUNDARY_SCHEMATIC",
            "working_title": "Typed graph extension versus full multilayer contagion",
            "purpose": "Show what the structural graph represents and what it does not implement.",
            "accepted_claim_ids": ["P2:C26", "P2:C27", "P2:C29"],
            "result_ids": [],
            "source_paths": [
                "sim/network/metrics.py",
                "data/processed/research_final/validation_audit/corrected_run_v2/network/structural_graph.json",
            ],
            "specification": "Conceptual boundary diagram with explicit labels: typed aggregate graph, structural centrality, no DebtRank, no empirical full multilayer contagion.",
            "units": ["NOT_APPLICABLE"],
            "denominators": ["locked typed network scope"],
            "policy_scenario": ["structural extension only"],
            "evidence_tier": "CODE_OBSERVATION_WITH_SCOPED_MODEL_LIMITATION",
            "output_formats": ["SVG", "PNG", "PDF_VECTOR"],
            "caption_requirement": "Do not label any metric as DebtRank or causal contagion.",
            "limitations": ["No supra-adjacency validation, calibrated exposures or full multilayer contagion model."],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:RISK_PARAMETER_MECHANISMS",
            "type": "MECHANISM_TABLE",
            "working_title": "Distinct roles of LTV, liquidation threshold and liquidation bonus",
            "purpose": "Prevent parameter substitution in RQ6 reporting.",
            "accepted_claim_ids": ["P2:C04", "P2:C12", "INT:CL_INT_RQ6_PRESERVED"],
            "result_ids": [
                "RQ6_LTV0755_CAPACITY",
                "RQ6_LTV0825_CAPACITY",
                "RQ6_LT083_UNLIQUIDATED",
                "RQ6_BONUS103_SEIZED",
                "RQ6_BONUS107_SEIZED",
            ],
            "source_paths": [
                "data/processed/research_final/frozen_v3/tables/rq6_policy.csv",
                "sim/lending/liquidation.py",
                "sim/schemas.py",
            ],
            "specification": "Three-row mechanism table: ex-ante borrowing limit; HF/eligibility; incentive and collateral transfer. Numeric examples remain in separate locked columns.",
            "units": ["USD", "USDC token quantity", "WETH"],
            "denominators": ["109-position frozen cohort or executed locked test scenario as specified per result"],
            "policy_scenario": ["locked RQ6 counterfactuals"],
            "evidence_tier": "MODEL_COMPUTED_COUNTERFACTUAL_AND_CODE_OBSERVATION",
            "output_formats": ["CSV", "MARKDOWN_TABLE"],
            "caption_requirement": "LTV is not the liquidation trigger; LT and bonus have different mechanisms.",
            "limitations": ["Frozen cohort; no borrower behavior or re-underwriting response."],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:CANONICAL_SCOPE_PROVENANCE",
            "type": "PROVENANCE_TABLE",
            "working_title": "Canonical Mainnet snapshot, verification population and research cohort",
            "purpose": "Keep block, borrower population and WETH/USDC cohort denominators explicit.",
            "accepted_claim_ids": ["P2:C03", "P2:C17", "INT:CL_INT_RQ3_PRESERVED"],
            "result_ids": [],
            "source_paths": [
                "data/processed/mainnet/aave_uniswap_snapshot_26045352.json",
                "data/processed/research_final/frozen_v3/manifest.json",
            ],
            "specification": "Provenance table: block 26045352, snapshot hash, 454 verified borrowers, 109 WETH-collateral-enabled/USDC-debt cohort; never label candidate verification as market coverage.",
            "units": ["block", "borrowers", "positions"],
            "denominators": ["454 verified borrowers; 109-position target cohort"],
            "policy_scenario": ["canonical snapshot"],
            "evidence_tier": "ONCHAIN_SAME_BLOCK_STATE_AND_VERIFICATION_RECORD",
            "output_formats": ["MARKDOWN_TABLE", "CSV"],
            "caption_requirement": "The 454 borrowers are the verified sample, not complete Aave market coverage.",
            "limitations": ["One fixed block, one pool and one target cohort."],
            "status": awaiting,
        },
        {
            "exhibit_id": "P3X:METRIC_SEMANTICS_GLOSSARY",
            "type": "DEFINITION_TABLE",
            "working_title": "Locked metric semantics and prohibited interpretations",
            "purpose": "Align every manuscript table and caption with engine definitions.",
            "accepted_claim_ids": [
                "P2:C24",
                "P2:C35",
                "INT:CL_INT_RQ3_PRESERVED",
                "INT:CL_INT_RQ4_PRESERVED",
                "INT:CL_INT_RQ5_PRESERVED",
            ],
            "result_ids": [],
            "source_paths": [
                "sim/engine/run.py",
                "sim/metrics/risk.py",
                "sim/schemas.py",
                "docs/research_final/TERMINOLOGY_VI.md",
            ],
            "specification": "Rows for bad debt, unliquidated debt, liquidation at risk, cascade depth/amplification, immediate impact, residual spread, delay and recovery; include unit and forbidden wording.",
            "units": ["metric-specific"],
            "denominators": ["metric-specific"],
            "policy_scenario": ["locked model semantics"],
            "evidence_tier": "PROJECT_METRIC_DEFINITION",
            "output_formats": ["MARKDOWN_TABLE", "CSV"],
            "caption_requirement": "Modeled bad debt is not realized financial loss; delay is not recovery time.",
            "limitations": [
                "Definitions describe this model and must not be promoted to external empirical estimates."
            ],
            "status": awaiting,
        },
    ]


def _build_catalog(inventory: dict[str, Any]) -> dict[str, Any]:
    path_to_evidence = inventory["path_to_p3_evidence_id"]
    evidence_by_path = {row["original_artifact_path"]: row for row in inventory["records"]}
    records: list[dict[str, Any]] = []
    for spec in _catalog_specs():
        missing = [path for path in spec["source_paths"] if path not in path_to_evidence]
        if missing:
            raise AssertionError(f"Catalog sources missing from inventory: {missing}")
        records.append(
            {
                **spec,
                "proposed_chapter": "WORK_TO_ASSIGN_AFTER_BLUEPRINT",
                "proposed_section": "WORK_TO_ASSIGN_AFTER_BLUEPRINT",
                "source_artifact_locators": [
                    {
                        "path": path,
                        "p3_evidence_id": path_to_evidence[path],
                        "source_commit": SOURCE_LOCK,
                        "input_git_blob_id": evidence_by_path[path]["git_blob_id"],
                        "input_git_blob_sha256": evidence_by_path[path]["checksums"]["git_blob_sha256"],
                    }
                    for path in spec["source_paths"]
                ],
                "reproducibility_method": "Deterministic extraction/display transformation from locked artifacts; independent denominator/unit validator before rendering.",
                "dependency_on_work_blueprint": True,
                "commander_approval_state": "PENDING",
            }
        )
    return _seal_json(
        {
            "schema_version": "p3-exhibit-catalog-v1",
            "transformation_version": "p3-g0-builder-v1",
            "stage": "P3-G0_CATALOG_ONLY_NO_FULL_RENDERING",
            "source_lock_commit": SOURCE_LOCK,
            "records": records,
            "catalog_rules": [
                "No exhibit may use a disallowed affirmative claim.",
                "No proposed chapter assignment is final before the Work blueprint and Commander approval.",
                "Display transformations may not create a new estimated finding.",
            ],
        }
    )


def _build_handoff(catalog: dict[str, Any]) -> dict[str, Any]:
    requests = []
    for exhibit in catalog["records"]:
        requests.append(
            {
                "chapter_id": "WORK_TO_ASSIGN",
                "section_id": "WORK_TO_ASSIGN",
                "exhibit_request_id": exhibit["exhibit_id"],
                "claim_ids": exhibit["accepted_claim_ids"],
                "result_ids": exhibit["result_ids"],
                "requested_interpretation": exhibit["purpose"],
                "source_commit": SOURCE_LOCK,
                "current_status": "SOURCE_VERIFIED",
                "blocking_issues": ["Awaiting Work chapter blueprint and Commander exhibit approval."],
                "work_review_state": "AWAITING_BLUEPRINT",
                "codex_validation_state": "G0_SOURCE_AND_LOCATOR_VERIFIED",
                "commander_approval_state": "PENDING",
            }
        )
    return _seal_json(
        {
            "schema_version": "p3-work-codex-evidence-handoff-v1",
            "transformation_version": "p3-g0-builder-v1",
            "source_lock_commit": SOURCE_LOCK,
            "allowed_statuses": [
                "REQUESTED",
                "SOURCE_VERIFIED",
                "PRODUCED",
                "TECHNICAL_REVIEW_PASS",
                "ACADEMIC_REVIEW_PASS",
                "BLOCKED",
                "CHAPTER_LOCKED",
            ],
            "stage_rule": "No record may be set to CHAPTER_LOCKED without Commander approval.",
            "requests": requests,
        }
    )


def _baseline_markdown() -> str:
    return _seal_markdown(
        f"""# P3 Technical Manuscript Baseline Audit

Status: `P3-G0 — TECHNICAL BLUEPRINT ONLY`

Scientific source lock: `{SOURCE_LOCK}`
Transformation version: `p3-g0-builder-v1`

## Scope and method

Both supplied historical DOCX files were opened read-only, exported through Microsoft Word to PDF, rasterized at 100 DPI and visually reviewed on every rendered page (33 + 13 pages). Structural checks used OOXML/python-docx plus the bundled heading, field, section, image, table-geometry, style, accessibility, comments and footnote audit helpers. LibreOffice was unavailable on PATH, so the fallback export route is disclosed. Neither DOCX was edited.

## Baseline 1 — five-chapter report

`DeFiStress_BAO_CAO_NCKH_HOAN_CHINH.docx` has SHA-256 `9c8486027efcd35fe8fbcb8ba4c9fd6cfb714d2785f40ca6a64c247627dceb96`, 33 rendered pages, 3 sections, 349 body paragraphs, 22 tables and 16 inline images. Heading styles are present (5/40/12 at levels 1/2/3), and the visible structure is five chapters plus front matter, references and appendices.

- A live TOC field and PAGE field exist; no SEQ caption fields, REF cross-reference fields, LOT/LOF fields or bookmarks were found.
- Thirty-one `Caption`-style and 31 `Nguồn`-style paragraphs are plain text. They are not field-backed numbering/cross-references.
- No OMML equation objects were found; displayed formulas are text/direct formatting.
- No comments, tracked insertions/deletions, footnotes or endnotes were found.
- The accessibility audit reports 16 high findings (all inline images lack alt text) and 22 medium findings (table header rows are not marked). The table geometry helper reports 229 structural width/indent/grid findings.
- Visual review found no gross clipping or unreadable overlap, but page 33 is nearly empty except for the tail of the reproducibility paragraph, indicating an avoidable pagination/orphan issue.
- The manuscript contains pre-lock numerical narratives: the original 32-cell grid conclusion and a 0/200 Monte Carlo table conflict with the locked version precedence. Those tables/figures must not be reused without rebuilding from locked evidence.

## Baseline 2 — introduction/literature proposal

`DeFi_Stress_Lab_Mo_Dau_Tong_Quan_Nghien_Cuu.docx` has SHA-256 `582d489189a156f00a563d22b6db36caab8094d7a3581d220b96d8b3f1aebdd5`, 13 rendered pages, 1 section, 106 body paragraphs and 8 tables. It has 11 Heading 1 and 12 Heading 2 paragraphs.

- It has a PAGE field but no TOC, SEQ, REF, LOT/LOF, bookmark or OMML equation structures.
- The visual flow is readable and consistent, but the file is a proposal/introductory baseline rather than the locked seven-chapter manuscript.
- Four tables lack marked header rows. The table geometry helper reports 36 structural findings.
- No comments or tracked changes were found.

## Existing research figures/tables

The repository contains legacy `A01–A22`, `T01–T12`, `C01` and other pre-lock outputs. Presence is not sufficient provenance. Only artifacts resolved through Final Accepted Claims Registry v1.1, its active result IDs and locked source locators are eligible for the proposed P3 catalog. Existing Frozen v3 figures F01–F04 may be reused only after caption/policy/denominator review.

## Technical gaps before manuscript production

1. Work has not yet supplied the Commander-approved seven-chapter blueprint, so no exhibit is assigned to a final chapter or section.
2. No official school template was provided or verified. The two historical DOCX files are not treated as template truth.
3. Caption numbering, cross-references, LOT and LOF need a field-backed Word implementation in a later approved stage.
4. Figure alt text, table header semantics and table geometry need remediation in the final manuscript, not in these read-only source files.
5. Equations require a consistent OMML/Word-equation workflow; current baselines use plain text.
6. Bibliography formatting is visually present but was not treated as authoritative because P2 literature files, not these DOCX files, are the locked scholarly source.

## G0 conclusion

The historical five-chapter manuscript is useful only as a layout/content baseline. It is numerically superseded in material places and cannot serve as the P3 evidence source. School-template compliance remains `NOT_VERIFIED — TEMPLATE_NOT_PROVIDED`.
"""
    )


def _formula_markdown() -> str:
    return _seal_markdown(
        """# P3 Formula Audit Plan

Status: `P3-G0 — FORMULA INVENTORY, NOT MANUSCRIPT PROSE`

Scientific source lock: `__SOURCE_LOCK__`
Transformation version: `p3-g0-builder-v1`

The classifications below prevent a project approximation from being presented as a protocol formula. Variables and units must be repeated in the eventual equation caption or adjacent text.

| Formula ID | Classification | LaTeX display | Variables / units | Conditions and source locator | RQ | Simplification / required limitation |
|---|---|---|---|---|---|---|
| P3F01 | Protocol-shaped project implementation | `$HF_i(t)=\\frac{\\sum_j q^C_{ij}P^C_j(t)LT_j}{\\sum_k q^D_{ik}P^D_k(t)}$` | `q`: token quantity; `P`: USD/token; `LT`: ratio; HF dimensionless | `sim/lending/health_factor.py:5`; portfolio implementation `sim/schemas.py:29` | RQ1, RQ3, RQ5, RQ6 | Aave-style aggregate; project cohort has WETH/USDC route plus aggregate other collateral/debt. Oracle policy is separate. |
| P3F02 | Project route eligibility rule | `$Eligible_i = [HF_i<1]\\land[D^{USDC}_i>0]\\land[C^{WETH}_i>0]$` | Boolean; modeled USDC debt and WETH collateral quantities | `sim/lending/liquidation.py:38` | RQ1, RQ3 | Portfolio HF eligibility is not route eligibility, attempted processing or positive-debt execution. |
| P3F03 | Protocol-shaped project liquidation mapping | `$q_{repay}=CF(HF,D,C)D^{USDC};\\quad q_{seize}=q_{repay}\\,b/P_{WETH}$` | USDC token, WETH, USD/WETH; `b` is liquidation-bonus multiplier | `sim/lending/liquidation.py:26`, `:38` | RQ3, RQ6 | Close-factor and dust rules are the implemented approximation; not contract-fork execution evidence. |
| P3F04 | Project-specific liquidator decision | `$\\Pi=Q_{USDC}^{out}-q_{repay}-Gas-Funding-Risk$`; execute if eligible, within capital/capacity and `$\\Pi>\\Pi_{min}$` | USDC-equivalent modeled quantities | `sim/agents/liquidator.py:33` | RQ3 | One representative liquidator, fixed cost/risk rules, no capital recycling or competitive bot market. |
| P3F05 | Uniswap V3 identity used by the project | `$\\sqrt{P}_{X96}=2^{96}\\sqrt{10^{d_1-d_0}/P_{WETH}}$`; `$tick=\\lfloor\\log_{1.0001}((\\sqrt{P}_{X96}/2^{96})^2)\\rfloor$` | `P`: USDC/WETH; token decimals; tick integer | `sim/dex/uniswap_v3.py:26`, `:35` | RQ2, RQ4 | Token ordering is USDC token0/WETH token1. Tick rounding is the project implementation. |
| P3F06 | Project swap calculation across initialized ticks | `$\\Delta y=L(\\sqrt{P_b}-\\sqrt{P_a});\\quad \\Delta x=L(1/\\sqrt{P_a}-1/\\sqrt{P_b})$` | raw token1 in and token0 out; active liquidity `L` | `sim/dex/uniswap_v3.py:77` | RQ2, RQ4 | Applied piecewise with fee and liquidityNet tick crossing; quotes are model outputs, not funded Mainnet swaps. |
| P3F07 | Display transformation | `$Impact_{sale}=|P_{DEX,post-sale}-P_{ref}|/P_{ref}$`; `$Residual_{arb}=|P_{DEX,post-arb}-P_{ref}|/P_{ref}$` | dimensionless ratio, normally displayed as percent | `sim/engine/run.py:143`, `:248`, metrics `:278`–`:282` | RQ2, RQ4 | Immediate impact and residual spread are distinct; deprecated `max_price_impact` aliases residual spread. |
| P3F08 | Hypothetical model policy | `$P_A=\\min(P_{ref},P_{DEX});\\ P_B=P_{ref};\\ P_C=P_{ref}+\\alpha(\\overline{P}_{DEX,lag}-P_{ref})$`, capped adverse | USD/WETH; alpha ratio; lag/window steps | `sim/oracle.py:43` | RQ1, RQ2, RQ4 | A/B/C are sensitivity policies, not verified Aave or Chainlink feeds. C is causal in time and uses completed waves only. |
| P3F09 | Analytical identity inside the model | `$D_{USD}=q_{USDC}P_{USDC/USD}+D_{other,USD}$` | USDC token quantity, USD/USDC, USD | `sim/schemas.py:25` | RQ5 | Isolates debt valuation only; no redemption, settlement, confidence or stablecoin-liquidity channel. |
| P3F10 | Project metric definition | `$BadDebt=\\sum_i\\max(0,D_{i,USD}-C_{i,USD})$` | USD-equivalent modeled uncovered debt | `sim/metrics/risk.py:9` | RQ2, RQ5 | Not realized financial loss. It excludes execution and recovery economics not represented in the formula. |
| P3F11 | Project metric definition | `$UnliquidatedDebt=\\sum_{i:HF_i(LT^*)<1}D_{i,USD}$` | USD-equivalent debt | `sim/metrics/risk.py:20`; call with scenario LT `sim/engine/run.py:262` | RQ3, RQ6 | Use scenario LT when overridden; the legacy recorded-LT value is comparison-only. |
| P3F12 | Analytical identity inside the model | `$Amplification=L_{total}/L_{direct}$` when `$L_{direct}>0$` | ratio; liquidated debt numerator/denominator use the same unit | `sim/metrics/risk.py:36` | RQ1, RQ2 | Undefined when direct liquidation is zero; not a multiplier of realized loss. |
| P3F13 | Project event/time definition | `$Depth=\\max(wave\\ with\\ positive\\ repaid\\ debt)$`; recovery is the first post-exceedance wave-end time with residual `≤0.5%` | waves; seconds | `sim/engine/run.py:246`–`:287` | RQ1, RQ3, RQ4 | Max-waves=100 is a cap, not observed depth. Delay and time-to-recovery are different measures. |
| P3F14 | Policy mechanism identity | `$BorrowCapacity=\\sum_j C_j LTV_j$`; LT enters HF; bonus enters seized collateral and expected profit | USD, ratios, WETH/USDC | `sim/schemas.py:17`; `sim/lending/liquidation.py:38`; locked RQ6 results | RQ6 | LTV, liquidation threshold and bonus must never be substituted for one another. Frozen cohort omits behavioral response. |
| P3F15 | Display-only statistical formula, approval required | `$\\hat p=k/n$`; Wilson score interval only for locked `k/n` pairs | count/paths and dimensionless interval | P2:C23; `data/processed/research_final/level3_extension/deep_stress/monte_carlo_batches.json` | RQ1 | G0 will not calculate a new CI. Any manuscript interval must reproduce an already locked pair and remain model-conditional. |

## Formula gate

Every produced equation must carry: formula class, source locator, variable dictionary, units, cohort/scenario/policy and the simplification text above. A missing field blocks chapter technical sign-off.
""".replace("__SOURCE_LOCK__", SOURCE_LOCK)
    )


def _repro_markdown(inventory: dict[str, Any], catalog: dict[str, Any]) -> str:
    return _seal_markdown(
        f"""# P3 Exhibit Reproducibility Plan

Status: `P3-G0 — NO FULL EXHIBIT RENDERING`

Scientific source lock: `{SOURCE_LOCK}`
Transformation version: `p3-g0-builder-v1`

## Boundary

This plan authorizes deterministic extraction and display transformation only. It does not authorize new simulation runs, interpolation, retuning, synthetic borrowers, new oracle assumptions, cohort changes or new statistical findings.

## Proposed pipeline after blueprint approval

1. Pin checkout to `{SOURCE_LOCK}` and verify the Frozen, Oracle, Integration, P2 and Final Registry objects.
2. Resolve the approved exhibit's accepted claim IDs, result IDs and source paths through `P3_LOCKED_EVIDENCE_INVENTORY.json`.
3. Extract only declared rows/fields. Record filters, grouping and ordering as the exhibit transformation specification.
4. Independently recompute counts, units, denominators, cohort, scenario and policy from the locked source without reusing the renderer's aggregation function.
5. Render deterministically to CSV/Markdown and SVG; derive PNG/PDF only from the verified vector source where practical.
6. Attach a per-exhibit manifest with input commit/hash, transformation version, output checksum, units, policy, denominator and limitations.
7. Obtain Codex technical review, Work academic interpretation review and Commander approval before `CHAPTER_LOCKED`.

## Hash semantics

- Git blob IDs and SHA-256 of Git blob bytes identify committed LF-normalized content.
- Checkout SHA-256 is recorded separately; Windows text may be CRLF.
- A CRLF/LF difference is not a scientific change when normalized content and Git provenance match.
- JSON outputs in G0 include a canonical-content SHA-256 with the checksum field omitted. Markdown outputs include a checksum of UTF-8 bytes preceding the checksum line. No self-referential hash is claimed.

## Deterministic rendering constraints

- Stable row ordering by explicit keys; stable legend/category order from the approved spec.
- No timestamps, random IDs, ambient locale or filesystem paths in output bytes.
- Fixed decimal display rules; raw locked values remain available in CSV/JSON provenance.
- Accessible, grayscale-safe palette; no 3D or truncated axes; schematic diagrams labeled as schematic.
- Caption must state evidence type, population/denominator, units, policy/scenario, permitted conclusion and prohibited inference.
- Existing PNGs are not silently modified. A display-only rerender receives a new P3 exhibit ID and manifest.

## Static scientific invariants

- Registry: 35 scholarly + 13 Integration records; 44 affirmative; 4 disallowed; six RQs.
- Oracle counts: A 35/14, B 0/0, C weak 6/0, C moderate 11/2; 36 skipped are route-ineligible due to absent modeled USDC debt.
- Severe: 280/10,000 depth≥2 is Policy A only; ten targeted paths are selected, not a population estimator.
- Haircuts 90/95% are extreme counterfactuals.
- Historical: 28 Pool, 27 Graph-matched, tiers 1/2/23/1; no causal historical contagion.
- Bad debt is modeled uncovered debt, not realized loss. USDC token quantity and USD-equivalent remain distinct.
- Terra negative cutoff-safe/OOS finding is preserved. Network output is a typed graph extension, not full multilayer contagion or DebtRank.
- Arbitrage price repositioning is not a funded executable swap.

## G0 coverage and tests

- Evidence inventory records: {len(inventory["records"])}.
- Proposed catalog entries: {len(catalog["records"])}.
- All catalog source paths must resolve to a P3 evidence ID and all catalog claims must be affirmative.
- Tests verify source-lock identity, locked tree/blob preservation, claim/result/table/figure resolution, exact six-RQ order, numerical invariants and deterministic regeneration.

## Change control

If an exhibit requires an unregistered statistic, source-tier elevation, strengthened causal statement or data not present in the locked inventory, create `EVIDENCE_CHANGE_REQUEST` and stop. G0 ends at `AWAITING_COMMANDER_BLUEPRINT_APPROVAL`.
"""
    )


def _validate_docx_inputs(docx_root: Path | None) -> None:
    if docx_root is None:
        return
    for record in DOCX_BASELINE:
        path = docx_root / cast(str, record["file_name"])
        if not path.is_file():
            raise FileNotFoundError(path)
        if _sha256(path) != record["sha256"]:
            raise AssertionError(f"DOCX hash changed: {path}")


def _validate_outputs(inventory: dict[str, Any], catalog: dict[str, Any], handoff: dict[str, Any]) -> None:
    records, affirmative, result_index = _locked_records()
    assert cast(str, _git("merge-base", "HEAD", SOURCE_LOCK)) == SOURCE_LOCK
    assert len(records) == 48
    assert len(affirmative) == 44
    assert sum(row["namespace"] == "SCHOLARLY_P2" for row in records) == 35
    assert sum(row["namespace"] == "INTEGRATION_SCIENTIFIC" for row in records) == 13
    assert {
        row["registry_id"] for row in records if row["final_gate_status"] not in AFFIRMATIVE_STATUSES
    } == DISALLOWED_IDS
    rqs = _load(ROOT / "six_rq_accepted_claims_matrix.json")["research_questions"]
    assert [row["rq"] for row in rqs] == RQ_ORDER
    assert all(row["required_limitations"] for row in rqs)
    expected_trees = _load(ROOT / "manifest.json")["source_tree_ids"]
    assert cast(str, _git("rev-parse", f"{SOURCE_LOCK}:{FROZEN.as_posix()}")) == expected_trees["frozen_v3"]
    assert cast(str, _git("rev-parse", f"{SOURCE_LOCK}:{ORACLE.as_posix()}")) == expected_trees["oracle_diagnostic_v1"]
    assert (
        cast(str, _git("rev-parse", f"{SOURCE_LOCK}:{INTEGRATION.as_posix()}"))
        == expected_trees["scientific_integration_v1"]
    )
    all_claims = {row["registry_id"] for row in records}
    affirmative_ids = {row["registry_id"] for row in affirmative}
    for exhibit in catalog["records"]:
        assert set(exhibit["accepted_claim_ids"]) <= affirmative_ids
        assert not set(exhibit["accepted_claim_ids"]) & DISALLOWED_IDS
        assert set(exhibit["result_ids"]) <= set(result_index)
        assert exhibit["proposed_chapter"] == "WORK_TO_ASSIGN_AFTER_BLUEPRINT"
        assert exhibit["status"] == "PROPOSED_AWAITING_WORK_BLUEPRINT_AND_COMMANDER_APPROVAL"
        assert all(locator["p3_evidence_id"] for locator in exhibit["source_artifact_locators"])
    assert all_claims >= affirmative_ids
    assert all(row["current_status"] == "SOURCE_VERIFIED" for row in handoff["requests"])
    assert all(row["commander_approval_state"] == "PENDING" for row in handoff["requests"])
    lock = _load(ROOT / "validation_report.json")["numerical_claim_lock"]
    assert lock["eligible_vs_executed"] == {
        "A": {"executed_wave2": 14, "newly_eligible": 35, "skipped": 21},
        "B": {"executed_wave2": 0, "newly_eligible": 0, "skipped": 0},
        "C_MODERATE": {"executed_wave2": 2, "newly_eligible": 11, "skipped": 9},
        "C_WEAK": {"executed_wave2": 0, "newly_eligible": 6, "skipped": 6},
    }
    assert lock["severe_policy_a"]["depth_gte_2"] == 280
    assert lock["severe_policy_a"]["denominator"] == 10_000
    assert lock["historical"]["graph_matched_events"] == 27
    assert lock["historical"]["pool_events"] == 28
    assert lock["historical"]["tiers_direct_same_tx_same_block_time"] == [1, 2, 23, 1]
    assert lock["terra_negative"] == {
        "initial_depeg_high_lead_hours": -45.0,
        "pre_depeg_high_alert_hours": 0,
        "successful_oos_forecast_established": False,
    }
    assert len(inventory["records"]) == len({row["evidence_id"] for row in inventory["records"]})


def _write(path: Path, value: str | dict[str, Any], *, check: bool) -> None:
    expected = value if isinstance(value, str) else _canonical_json_bytes(value).decode("utf-8")
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            raise AssertionError(f"Generated artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8", newline="\n")


def build(*, check: bool = False, docx_root: Path | None = None) -> None:
    _validate_docx_inputs(docx_root)
    inventory = _build_inventory()
    catalog = _build_catalog(inventory)
    handoff = _build_handoff(catalog)
    _validate_outputs(inventory, catalog, handoff)
    outputs: dict[Path, str | dict[str, Any]] = {
        INVENTORY_PATH: inventory,
        CATALOG_PATH: catalog,
        HANDOFF_PATH: handoff,
        BASELINE_PATH: _baseline_markdown(),
        FORMULA_PATH: _formula_markdown(),
        REPRO_PATH: _repro_markdown(inventory, catalog),
    }
    for path, value in outputs.items():
        _write(path, value, check=check)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the P3-G0 locked-evidence technical blueprint.")
    parser.add_argument(
        "--check", action="store_true", help="Verify committed outputs match deterministic regeneration."
    )
    parser.add_argument(
        "--docx-root", type=Path, help="Optional directory containing the two read-only baseline DOCX files."
    )
    args = parser.parse_args()
    build(check=args.check, docx_root=args.docx_root)


if __name__ == "__main__":
    main()
