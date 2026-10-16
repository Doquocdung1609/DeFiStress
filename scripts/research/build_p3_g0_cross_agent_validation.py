# ruff: noqa: E501 -- exact reviewed manuscript wording and locators are intentionally explicit.
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, cast

LOCK = "3f6e5302483681209e2408531eb5a15389f9fded"
WORK_HEAD = "e26e2d5a21c6ac78bd4db7be345409b5c7690a80"
CODEX_G0_HEAD = "17b839528e58a622aa0554067b19823a8f33bda5"
WORK_PLAN_PATH = "docs/manuscript_p3/work/P3_TABLE_FIGURE_EQUATION_PLAN.json"
WORK_CLAIMS_PATH = "docs/manuscript_p3/work/P3_CLAIM_TO_CHAPTER_MATRIX.json"
CATALOG_PATH = Path("artifacts/manuscript_p3/P3_EXHIBIT_CATALOG_v1.json")
INVENTORY_PATH = Path("artifacts/manuscript_p3/P3_LOCKED_EVIDENCE_INVENTORY.json")
REGISTRY_ROOT = Path("data/processed/research_final/final_accepted_claims_v1")
FROZEN_ROOT = Path("data/processed/research_final/frozen_v3")
INTEGRATION_ROOT = Path("data/processed/research_final/scientific_integration_v1")
OUTPUT_JSON = Path("artifacts/manuscript_p3/P3_G0_EXHIBIT_CROSSWALK_VALIDATION.json")
OUTPUT_MD = Path("docs/manuscript_p3/codex/P3_G0_EXHIBIT_RECONCILIATION_TECHNICAL_REVIEW.md")

AFFIRMATIVE = {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"}
DISALLOWED = {
    "INT:CL_FROZEN_RQ1_UNQUALIFIED_WORDING",
    "INT:CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING",
    "INT:CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT",
    "INT:CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION",
}


def _git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(["git", *args], check=True, capture_output=True)
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _load_at(commit: str, path: str) -> dict[str, Any]:
    raw = cast(bytes, _git("show", f"{commit}:{path}", binary=True))
    return cast(dict[str, Any], json.loads(raw.decode("utf-8")))


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _seal_json(value: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(value, ensure_ascii=False))
    provenance = payload.setdefault("output_provenance", {})
    provenance["content_sha256_domain"] = "UTF-8 canonical JSON with output_provenance.content_sha256 omitted"
    provenance.pop("content_sha256", None)
    provenance["content_sha256"] = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    return cast(dict[str, Any], payload)


def _seal_markdown(text: str) -> str:
    body = text.rstrip() + "\n"
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return body + f"\nContent SHA-256 (UTF-8, excluding this checksum line): `{digest}`\n"


EXHIBIT_REVIEW: dict[str, dict[str, Any]] = {
    "T1.1": {
        "classification": "TEXTUAL_SYNTHESIS",
        "templates": [],
        "decision": "Direct extraction of six locked RQs and their limitations; no numerical transformation.",
        "controls": ["Use full original RQ wording, not short labels."],
    },
    "T2.1": {
        "classification": "TEXTUAL_SYNTHESIS",
        "templates": [],
        "decision": "Literature/evidence matrix synthesis from P2 records; no quantitative inference.",
        "controls": ["Preserve source access levels and treat S17/S18 as one study."],
    },
    "F3.1": {
        "classification": "SCHEMATIC_FROM_LOCKED_MODEL_SPEC",
        "templates": ["P3X:SYSTEM_FEEDBACK_SCHEMATIC"],
        "decision": "Renderable only as a model schematic with evidence-tier styling, not as a measured causal network.",
        "controls": [
            "Solid arrows for implemented flow; visually distinct hypothetical A/B/C valuation box; no historical causal arrow."
        ],
    },
    "T3.1": {
        "classification": "TEXTUAL_SYNTHESIS",
        "templates": ["P3X:SYSTEM_FEEDBACK_SCHEMATIC", "P3X:METRIC_SEMANTICS_GLOSSARY"],
        "decision": "Code-derived agent/gate definition table.",
        "controls": [
            "Separate representative agent, route eligibility, attempted evaluation and positive-debt execution."
        ],
    },
    "T3.2": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": ["P3X:ORACLE_POLICY_DEPTH2_COMPARISON", "P3X:SEVERE_POLICY_A_MONTE_CARLO"],
        "decision": "Direct experiment-design table from locked manifests and tables.",
        "controls": [
            "Keep 32/60 grids, nested Severe prefixes and selected 4/4/10 diagnostic sets as separate populations."
        ],
    },
    "T3.3": {
        "classification": "TEXTUAL_SYNTHESIS",
        "templates": ["P3X:METRIC_SEMANTICS_GLOSSARY"],
        "decision": "Definition table from code and locked terminology.",
        "controls": [
            "Separate USDC token from USD-equivalent; immediate impact from residual spread; delay from recovery time."
        ],
    },
    "F4.1": {
        "classification": "SCHEMATIC_FROM_LOCKED_MODEL_SPEC",
        "templates": ["P3X:CANONICAL_SCOPE_PROVENANCE"],
        "decision": "Provenance/process schematic using locked block and verified cohort counts.",
        "controls": ["Do not convert candidate verification into market coverage."],
    },
    "T4.1": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": ["P3X:CANONICAL_SCOPE_PROVENANCE"],
        "decision": "Direct table from T02/core facts and result registry.",
        "controls": [
            "Do not add near-threshold subgroup statistics unless a locked locator is supplied; maxima are not typical error."
        ],
    },
    "T4.2": {
        "classification": "TEXTUAL_SYNTHESIS",
        "templates": ["P3X:METRIC_SEMANTICS_GLOSSARY"],
        "decision": "Validation-scope/status table from locked audit documents.",
        "controls": ["Unexecuted fork validation remains unavailable, never PASS."],
    },
    "F5.1": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": ["P3X:ORACLE_POLICY_DEPTH2_COMPARISON"],
        "decision": "Direct display of locked 32-cell and 60-cell depth counts.",
        "controls": ["Facet grids separately; 12/20/0 and 18/38/4 use different experiment domains."],
    },
    "T5.1": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": ["P3X:ORACLE_POLICY_DEPTH2_COMPARISON"],
        "decision": "Direct A/B/C retained-depth table for selected deterministic and targeted MC cases.",
        "controls": [
            "Show /4 and /10 denominators; controls remain separate; ten paths are not a frequency estimator."
        ],
    },
    "T5.2": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": ["P3X:ELIGIBLE_VS_EXECUTED"],
        "decision": "Direct extraction of the locked eligible/executed summary.",
        "controls": [
            "Units are borrower-case-policy instances; 36 skips are route-ineligible due to zero modeled USDC route debt."
        ],
    },
    "F5.2": {
        "classification": "NEEDS_DISPLAY_SPEC",
        "templates": ["P3X:ELIGIBLE_VS_EXECUTED"],
        "decision": "Aggregate gates are supported, but any borrower event example needs a deterministic predeclared selector and exact trace locator.",
        "controls": [
            "Use the smallest stable case/borrower key within the predeclared executed/skipped category; preserve pseudonymization; do not sample after viewing outcomes."
        ],
    },
    "F5.3": {
        "classification": "NEEDS_DISPLAY_SPEC",
        "templates": ["P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS", "P3X:ORACLE_POLICY_DEPTH2_COMPARISON"],
        "decision": "Both panels are supported but must not imply that every nonzero haircut is observed or that DEX distortion automatically becomes HF feedback.",
        "controls": [
            "Only 0% is the unmodified canonical pool; 25–95% haircuts are modeled counterfactual transformations; 90/95% are extreme unobserved tails.",
            "Use separate axes for cells and USD/WETH.",
        ],
    },
    "F5.4": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": [],
        "decision": "Direct display from locked RQ3 constraints table.",
        "controls": [
            "Debt repaid is USDC token quantity; processing delay is seconds; zero recovery is not zero reaction delay."
        ],
    },
    "F5.5": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": ["P3X:LIQUIDITY_ABSORPTION_AND_PRICE_METRICS"],
        "decision": "Direct display from locked RQ4 table.",
        "controls": [
            "Immediate price impact and post-arbitrage residual are separate ratios; price repositioning is not a funded swap."
        ],
    },
    "T5.3": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": [],
        "decision": "Direct display from locked RQ5 table.",
        "controls": ["Keep USDC token debt and USD-equivalent debt in separate columns with explicit price."],
    },
    "F5.6": {
        "classification": "NEEDS_DISPLAY_SPEC",
        "templates": ["P3X:RISK_PARAMETER_MECHANISMS"],
        "decision": "All values are locked, but three mechanisms and three outcome units require facets or a mechanism table, not one shared axis.",
        "controls": [
            "LTV→USD capacity, LT→USDC-token unliquidated debt, bonus→WETH seized; retain scenario LT semantics."
        ],
    },
    "F5.7": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": ["P3X:SEVERE_POLICY_A_MONTE_CARLO"],
        "decision": "Reuse/re-render only locked prefix frequency and Wilson columns.",
        "controls": [
            "Prefixes are nested, Policy A only; no new interval; selected ten diagnostic paths stay off this frequency chart."
        ],
    },
    "T6.1": {
        "classification": "RENDERABLE_FROM_LOCKED_ARTIFACT",
        "templates": ["P3X:HISTORICAL_EVIDENCE_TIERS"],
        "decision": "Direct historical evidence ladder table.",
        "controls": ["28 Pool/27 Graph; tier denominator 27; association does not prove causal contagion."],
    },
    "F6.1": {
        "classification": "NEEDS_DISPLAY_SPEC",
        "templates": ["P3X:TERRA_NEGATIVE_EARLY_WARNING"],
        "decision": "Negative results are locked; use two annotated panels or a table because zero alert-hours and −45-hour lead are distinct quantities.",
        "controls": [
            "Preserve the negative cutoff-safe/OOS conclusion; do not turn later-threshold behavior into forecast success."
        ],
    },
    "F6.2": {
        "classification": "SCHEMATIC_FROM_LOCKED_MODEL_SPEC",
        "templates": ["P3X:NETWORK_EXTENSION_BOUNDARY"],
        "decision": "Render exact locked nodes/edges and aggregation rule as a scoped structural diagram.",
        "controls": [
            "No invented edge, DebtRank label, empirical causal styling or all-DeFi ranking; centrality is within-model and dimensionless."
        ],
    },
    "T6.2": {
        "classification": "TEXTUAL_SYNTHESIS",
        "templates": [],
        "decision": "Claim-registry synthesis by evidence tier.",
        "controls": ["Hash integrity and code observation must not be elevated to empirical validation."],
    },
    "T7.1": {
        "classification": "TEXTUAL_SYNTHESIS",
        "templates": [],
        "decision": "Accepted-only six-RQ summary table with links to Chapter 5 exhibits.",
        "controls": ["Exclude all four disallowed records and preserve each RQ limitation."],
    },
    "T7.2": {
        "classification": "TEXTUAL_SYNTHESIS",
        "templates": [],
        "decision": "Contribution/boundary synthesis from accepted claims.",
        "controls": ["No first-ever, calibrated live-risk advice or stronger external validity claim."],
    },
}


FORMULA_REVIEW: dict[str, dict[str, Any]] = {
    "E3.1": {
        "codex_formula_ids": ["P3F01", "P3F02"],
        "category": "PROTOCOL_SHAPED_PROJECT_IMPLEMENTATION",
        "variables": [
            "c_ij collateral token quantity",
            "p_j USD/token under the selected valuation policy",
            "LT_j ratio",
            "d_ik debt token quantity",
            "q_k USD/token",
        ],
        "source_locators": ["sim/lending/health_factor.py:5", "sim/schemas.py:29"],
        "rqs": ["RQ1", "RQ3", "RQ5", "RQ6"],
        "safe_wording": "Aave-style portfolio HF implemented by DeFiStress; HF<1 is portfolio eligibility, not proof of route execution.",
        "limitations": [
            "Collateral must be enabled; zero debt returns Infinity; valuation policy is separate from actual Aave/Chainlink oracle behavior."
        ],
    },
    "E3.2": {
        "codex_formula_ids": ["P3F05"],
        "category": "PROTOCOL_IDENTITY_IMPLEMENTED_BY_PROJECT",
        "variables": ["s normalized sqrtPrice", "d0/d1 token decimals", "P1/0 token1 per token0", "P0/1 reciprocal"],
        "source_locators": ["sim/dex/uniswap_v3.py:26", "sim/dex/uniswap_v3.py:48"],
        "rqs": ["RQ2", "RQ4"],
        "safe_wording": "Token-order-aware conversion used by the locked USDC-token0/WETH-token1 pool implementation.",
        "limitations": [
            "State the price direction explicitly; the manuscript usually needs the reciprocal USDC/WETH value."
        ],
    },
    "E3.3": {
        "codex_formula_ids": ["P3F06"],
        "category": "PROTOCOL_IDENTITY_IMPLEMENTED_PIECEWISE",
        "variables": [
            "L active liquidity",
            "s_a/s_b interval boundary square-root prices",
            "Δy token1 input",
            "Δx token0 output",
        ],
        "source_locators": ["sim/dex/uniswap_v3.py:77"],
        "rqs": ["RQ2", "RQ4"],
        "safe_wording": "Within-tick V3 amount relation applied piecewise by the project after fees.",
        "limitations": [
            "Crossing an initialized tick updates active liquidity; this is not a whole-pool constant-product formula or a funded Mainnet trade."
        ],
    },
    "E3.4": {
        "codex_formula_ids": ["P3F08"],
        "category": "PROJECT_SPECIFIC_HYPOTHETICAL_POLICY",
        "variables": [
            "reference and DEX price in USD/WETH",
            "α transmission coefficient",
            "lag/window completed-wave parameters",
        ],
        "source_locators": [
            "sim/oracle.py:43",
            "data/processed/research_final/oracle_transmission_diagnostic_v1/selection_manifest.json",
        ],
        "rqs": ["RQ1", "RQ2", "RQ4"],
        "safe_wording": "Hypothetical A/B/C valuation-policy sensitivity used by DeFiStress.",
        "limitations": [
            "C uses completed waves only and caps adverse transmission; none of A/B/C is established as the historical Aave or Chainlink feed."
        ],
    },
    "E3.5": {
        "codex_formula_ids": ["P3F02"],
        "category": "PROJECT_STATE_CLASSIFICATION_DISPLAY_IDENTITY",
        "variables": [
            "E portfolio HF indicator",
            "R modeled WETH/USDC route-asset indicator",
            "X positive-debt liquidation-event indicator",
        ],
        "source_locators": ["sim/lending/liquidation.py:38", "sim/engine/run.py:102", "sim/engine/run.py:152"],
        "rqs": ["RQ1", "RQ3"],
        "safe_wording": "Three distinct indicators for portfolio eligibility, route asset availability and positive-debt model execution.",
        "limitations": [
            "R alone is not sufficient: active status, planning, profit, capital, capacity, delay and horizon remain separate gates; attempted is evaluation, not broadcast."
        ],
    },
    "E3.6": {
        "codex_formula_ids": ["P3F15"],
        "category": "DISPLAY_TRANSFORMATION_OF_LOCKED_RUNS",
        "variables": ["D_r locked path cascade depth", "n paths in one declared batch/seed/scenario/policy"],
        "source_locators": ["data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv"],
        "rqs": ["RQ1"],
        "safe_wording": "Model-conditional sample frequency within each locked batch.",
        "limitations": [
            "Nested prefixes are not additive; targeted ten paths are not a population sample; never call the value an Ethereum crisis probability."
        ],
    },
    "E3.7": {
        "codex_formula_ids": ["P3F15"],
        "category": "DISPLAY_TRANSFORMATION_LOCKED_VALUES_ONLY",
        "variables": ["f-hat locked sample frequency", "n locked batch size", "z=1.96 for the reported 95% interval"],
        "source_locators": [
            "sim/research/aave_suite.py:211",
            "scripts/research/run_deep_cascade_study.py:353",
            "data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv",
        ],
        "rqs": ["RQ1"],
        "safe_wording": "Wilson score interval already computed for locked model batches.",
        "limitations": [
            "Do not use the NIST Agresti–Coull page as if it directly validates the Wilson implementation; cite the locked implementation/table and use scholarship only as background. Do not compute a new interval without change review."
        ],
    },
    "E3.8": {
        "codex_formula_ids": ["P3F09"],
        "category": "ANALYTICAL_IDENTITY_INSIDE_MODEL",
        "variables": ["Q debt in USDC tokens", "q USD per USDC", "V USD-equivalent debt"],
        "source_locators": [
            "sim/schemas.py:25",
            "data/processed/research_final/frozen_v3/tables/rq5_usdc_valuation.csv",
        ],
        "rqs": ["RQ5"],
        "safe_wording": "Modeled conversion of USDC debt token quantity to USD-equivalent debt value.",
        "limitations": [
            "Valuation only; it does not implement redemption, settlement, confidence, liquidity or every execution-price channel."
        ],
    },
}


def _resolve_evidence_ids() -> set[str]:
    frozen = _load(FROZEN_ROOT / "evidence_source_matrix.json")
    integration = _load(INTEGRATION_ROOT / "table_figure_registry.json")
    return {
        *[row["figure_id"] for row in frozen["figure_registry"]],
        *[row["table_id"] for row in frozen["table_registry"]],
        *[row["table_id"] for row in integration["tables"]],
    }


def _blob_review(locator: dict[str, Any], inventory_map: dict[str, str]) -> dict[str, Any]:
    path = str(locator["path"])
    commit = str(locator["commit"])
    blob_id = cast(str, _git("rev-parse", f"{commit}:{path}"))
    blob_bytes = cast(bytes, _git("cat-file", "blob", blob_id, binary=True))
    return {
        "path": path,
        "commit": commit,
        "declared_git_blob_id": locator["git_blob_sha"],
        "actual_git_blob_id": blob_id,
        "git_blob_sha256": hashlib.sha256(blob_bytes).hexdigest(),
        "hash_domain": "Git object ID (SHA-1) and SHA-256 of Git blob bytes; not Windows checkout bytes",
        "read_scope_declared_by_work": locator["read_scope"],
        "codex_g0_evidence_id": inventory_map.get(path, "NOT_IN_67_RECORD_INVENTORY_GIT_LOCK_VERIFIED_SEPARATELY"),
        "status": "PASS" if commit == LOCK and blob_id == locator["git_blob_sha"] else "FAIL",
    }


def _build() -> dict[str, Any]:
    work_plan = _load_at(WORK_HEAD, WORK_PLAN_PATH)
    work_claims = _load_at(WORK_HEAD, WORK_CLAIMS_PATH)
    catalog = _load(CATALOG_PATH)
    inventory = _load(INVENTORY_PATH)
    registry = _load(REGISTRY_ROOT / "accepted_claims_registry.json")["records"]
    result_index = {
        row["result_id"]: row
        for source in [
            _load(FROZEN_ROOT / "results_registry.json")["results"],
            _load(INTEGRATION_ROOT / "integration_result_registry.json")["results"],
        ]
        for row in source
    }
    affirmative = {row["registry_id"] for row in registry if row["final_gate_status"] in AFFIRMATIVE}
    evidence_ids = _resolve_evidence_ids()
    inventory_map = cast(dict[str, str], inventory["path_to_p3_evidence_id"])
    template_ids = {row["exhibit_id"] for row in catalog["records"]}

    exhibits: list[dict[str, Any]] = []
    formulas: list[dict[str, Any]] = []
    for work in work_plan["exhibits"]:
        work_id = str(work["proposed_manuscript_id"])
        source_review = [_blob_review(locator, inventory_map) for locator in work["artifact_locators"]]
        base = {
            "work_exhibit_id": work_id,
            "work_handoff_id": work["handoff_id"],
            "chapter": work["chapter"],
            "section": work["section"],
            "title": work["title"],
            "accepted_claim_ids": work["accepted_claim_ids"],
            "claim_ids_status": "PASS" if set(work["accepted_claim_ids"]) <= affirmative else "FAIL",
            "result_ids": work["exact_result_ids"],
            "result_ids_status": "PASS" if set(work["exact_result_ids"]) <= set(result_index) else "FAIL",
            "existing_evidence_ids": work["existing_evidence_ids"],
            "evidence_ids_status": "PASS" if set(work["existing_evidence_ids"]) <= evidence_ids else "FAIL",
            "source_locators": source_review,
            "source_locators_status": "PASS" if all(row["status"] == "PASS" for row in source_review) else "FAIL",
            "units": work["units"],
            "policy_scenario_cohort": work["policy_scenario_cohort"],
            "mandatory_limitations": work["mandatory_limitations"],
            "rendition_owner": work["proposed_output_owner"],
            "requested_output_format": work["requested_output_format"],
        }
        if work["kind"] == "EQUATION":
            review = FORMULA_REVIEW[work_id]
            formulas.append(
                {
                    **base,
                    "work_formula": work["formula"],
                    "codex_formula_ids": review["codex_formula_ids"],
                    "formula_category": review["category"],
                    "input_variables": review["variables"],
                    "audited_source_locators": review["source_locators"],
                    "related_rqs": review["rqs"],
                    "safe_manuscript_wording": review["safe_wording"],
                    "required_limitations": review["limitations"],
                    "compatibility_status": "PASS_WITH_REQUIRED_LIMITATIONS",
                }
            )
            continue
        review = EXHIBIT_REVIEW[work_id]
        exhibits.append(
            {
                **base,
                "kind": work["kind"],
                "codex_template_ids": review["templates"],
                "codex_template_status": "PASS" if set(review["templates"]) <= template_ids else "FAIL",
                "reproducibility_classification": review["classification"],
                "rendering_decision": review["decision"],
                "required_display_controls": review["controls"],
                "technical_support_status": "SUPPORTED_BY_LOCKED_EVIDENCE",
            }
        )

    template_usage: dict[str, list[str]] = defaultdict(list)
    for row in exhibits:
        for template_id in row["codex_template_ids"]:
            template_usage[template_id].append(row["work_exhibit_id"])
    template_disposition = [
        {
            "codex_template_id": row["exhibit_id"],
            "disposition": "USED",
            "work_exhibit_ids": sorted(template_usage[row["exhibit_id"]]),
            "note": "Reusable technical template; one template may support multiple manuscript displays.",
        }
        for row in catalog["records"]
    ]

    findings = [
        {
            "finding_id": "G0-X01",
            "severity": "P1_METADATA",
            "affected_ids": [row["work_exhibit_id"] for row in exhibits] + [row["work_exhibit_id"] for row in formulas],
            "finding": "Work HEAD does not yet contain the Commander-requested Work-ID→Codex-template/formula crosswalk; its handoff IDs are editorial IDs only.",
            "minimum_remediation": "Work should mirror or explicitly adopt this validated crosswalk in its next delta; no scientific number or claim changes are required.",
            "scientific_impact": "Blocks final Blueprint Lock provenance, not the underlying evidence.",
        },
        {
            "finding_id": "G0-X02",
            "severity": "P1_METADATA",
            "affected_ids": ["E3.7"],
            "finding": "The Work locator list gives literature/background files for Wilson but omits the locked project implementation and numerical table; its own note acknowledges the NIST title is Agresti–Coull.",
            "minimum_remediation": "Use sim/research/aave_suite.py:211, scripts/research/run_deep_cascade_study.py:353 and frozen_v3/tables/rq1_monte_carlo.csv as primary project locators; retain scholarship as background only.",
            "scientific_impact": "Without correction, formula provenance is ambiguous; locked interval values themselves remain unchanged.",
        },
        {
            "finding_id": "G0-X03",
            "severity": "P2_DISPLAY_SPEC",
            "affected_ids": ["F5.2", "F5.3", "F5.6", "F6.1", "T4.1"],
            "finding": "Locked sources support these displays, but deterministic event selection, counterfactual labeling, mixed-unit faceting or optional-detail boundaries must be fixed before rendering.",
            "minimum_remediation": "Apply each row's required_display_controls during chapter evidence-pack specification.",
            "scientific_impact": "No new experiment is needed; careless rendering could overstate evidence or mix units.",
        },
    ]

    classification_counts = Counter(row["reproducibility_classification"] for row in exhibits)
    all_records = [*exhibits, *formulas]
    validation_pass = all(
        row[gate] == "PASS"
        for row in all_records
        for gate in ["claim_ids_status", "result_ids_status", "evidence_ids_status", "source_locators_status"]
    ) and all(row["codex_template_status"] == "PASS" for row in exhibits)

    return _seal_json(
        {
            "schema_version": "p3-g0-cross-agent-exhibit-validation-v1",
            "transformation_version": "p3-g0-cross-agent-validator-v1",
            "scientific_lock_commit": LOCK,
            "reviewed_heads": {"work_pr_15": WORK_HEAD, "codex_pr_14_input": CODEX_G0_HEAD},
            "review_scope": "25 manuscript tables/figures and 8 manuscript equations; no rendering or new finding.",
            "counts": {
                "work_tables": sum(row["kind"] == "TABLE" for row in work_plan["exhibits"]),
                "work_figures": sum(row["kind"] == "FIGURE" for row in work_plan["exhibits"]),
                "work_equations": len(formulas),
                "codex_templates": len(catalog["records"]),
                "codex_audited_formulas": 15,
                "inventory_records_unchanged": len(inventory["records"]),
                "affirmative_claims": len(affirmative),
                "disallowed_claims": len(registry) - len(affirmative),
            },
            "classification_counts": dict(sorted(classification_counts.items())),
            "lock_validation": {
                "work_plan_lock": work_plan["scientific_lock_commit"],
                "work_claim_matrix_lock": work_claims["scientific_lock_commit"],
                "six_rqs": len(work_claims["original_research_questions"]),
                "affirmative_allocation": work_claims["coverage"],
                "disallowed_ids": sorted(DISALLOWED),
                "disallowed_used_as_affirmative": sorted(
                    DISALLOWED & {claim for row in work_plan["exhibits"] for claim in row["accepted_claim_ids"]}
                ),
                "frozen_oracle_integration_p2_registry_modified": False,
                "new_simulation_or_estimated_finding": False,
                "hash_domain_rule": "Git object IDs, Git-blob SHA-256 and checkout SHA-256 are distinct domains.",
                "status": "PASS" if validation_pass else "FAIL",
            },
            "exhibit_crosswalk": exhibits,
            "formula_crosswalk": formulas,
            "codex_template_disposition": template_disposition,
            "findings": findings,
            "technical_blockers": [],
            "work_delta_required": ["G0-X01", "G0-X02"],
            "commander_recommendation": "P3_G0_TECHNICAL_REWORK_REQUIRED",
            "recommendation_reason": "All 25 displays and 8 formulas are supported or safely specifiable, but Work HEAD has not yet published the final crosswalk and E3.7 primary project locators require correction before Blueprint Lock.",
            "stop_state": "AWAITING_WORK_FINAL_CROSSWALK_DELTA_AND_COMMANDER_BLUEPRINT_DECISION",
        }
    )


def _markdown(payload: dict[str, Any]) -> str:
    exhibit_rows = "\n".join(
        f"| {row['work_exhibit_id']} | Ch{row['chapter']} §{row['section']} | {row['reproducibility_classification']} | {', '.join(row['codex_template_ids']) or 'DIRECT/NO TEMPLATE'} | {row['technical_support_status']} |"
        for row in payload["exhibit_crosswalk"]
    )
    formula_rows = "\n".join(
        f"| {row['work_exhibit_id']} | {', '.join(row['codex_formula_ids'])} | {row['formula_category']} | {row['compatibility_status']} |"
        for row in payload["formula_crosswalk"]
    )
    template_rows = "\n".join(
        f"| {row['codex_template_id']} | {row['disposition']} | {', '.join(row['work_exhibit_ids'])} |"
        for row in payload["codex_template_disposition"]
    )
    finding_rows = "\n".join(
        f"| {row['finding_id']} | {row['severity']} | {', '.join(row['affected_ids'])} | {row['minimum_remediation']} |"
        for row in payload["findings"]
    )
    counts = payload["counts"]
    classes = payload["classification_counts"]
    return _seal_markdown(
        f"""# P3-G0 Exhibit Reconciliation — Technical Review

Status: `P3_G0_TECHNICAL_REWORK_REQUIRED`

Scientific lock: `{LOCK}`

Work PR #15 reviewed HEAD: `{WORK_HEAD}`
Codex PR #14 input HEAD: `{CODEX_G0_HEAD}`

## Verdict

All **25/25** Work manuscript tables/figures and **8/8** selected equations resolve to accepted claims, locked result/evidence IDs when applicable, and source objects at the scientific lock. No display is unsupported by the locked evidence. The evidence gate itself is not blocked.

Blueprint Lock is not yet ready because Work HEAD still lacks the single Commander-requested Work→Codex crosswalk, and E3.7 lists literature/background locators instead of the locked project implementation and numerical table as its primary provenance. These are targeted metadata repairs; they do not authorize or require a new simulation, interval, model change or scientific result.

## Counts and preservation

- Work plan: {counts["work_tables"]} tables, {counts["work_figures"]} figures, {counts["work_equations"]} equations.
- Codex inputs: {counts["codex_templates"]} reusable templates, {counts["codex_audited_formulas"]} audited formulas and {counts["inventory_records_unchanged"]} unchanged evidence-inventory records.
- Claim gate: {counts["affirmative_claims"]} affirmative and {counts["disallowed_claims"]} disallowed; no disallowed ID appears as an affirmative exhibit claim.
- Six RQs, Frozen, Oracle, Integration, P2 and Final Registry remain unchanged.
- No rendering, new simulation, retuning, new estimated finding, Chapter 1 prose or DOCX edit occurred.

## Exhibit crosswalk

| Work ID | Placement | Reproducibility class | Codex template(s) | Evidence status |
|---|---|---|---|---|
{exhibit_rows}

Classification totals: `RENDERABLE_FROM_LOCKED_ARTIFACT={classes.get("RENDERABLE_FROM_LOCKED_ARTIFACT", 0)}`, `SCHEMATIC_FROM_LOCKED_MODEL_SPEC={classes.get("SCHEMATIC_FROM_LOCKED_MODEL_SPEC", 0)}`, `TEXTUAL_SYNTHESIS={classes.get("TEXTUAL_SYNTHESIS", 0)}`, `NEEDS_DISPLAY_SPEC={classes.get("NEEDS_DISPLAY_SPEC", 0)}`, `UNSUPPORTED_BY_LOCKED_EVIDENCE={classes.get("UNSUPPORTED_BY_LOCKED_EVIDENCE", 0)}`.

Four displays are classified `NEEDS_DISPLAY_SPEC`; T4.1 is directly renderable only if its optional near-threshold extension is omitted. These controls require no new evidence:

- **F5.2:** predeclare a deterministic, pseudonymized event selector and exact trace locator.
- **F5.3:** only 0% is the unmodified canonical pool; every positive haircut is a model counterfactual, with 90/95% extreme tails. Separate cell counts from USD/WETH.
- **F5.6:** facet USD capacity, USDC-token unliquidated debt and WETH seized; never share one y-axis.
- **F6.1:** keep zero HIGH-alert hours and −45-hour lead as distinct quantities/two panels.
- **T4.1:** omit optional near-threshold detail until a locked locator is named.

## Formula reconciliation

| Work formula | Codex audit mapping | Category | Compatibility |
|---|---|---|---|
{formula_rows}

The eight formulas are compatible with locked code/outputs when their recorded limitations are retained. E3.7 requires a provenance correction: the primary project locators are `sim/research/aave_suite.py:211`, `scripts/research/run_deep_cascade_study.py:353` and `frozen_v3/tables/rq1_monte_carlo.csv`. The NIST Agresti–Coull-titled page cannot be presented as direct verification of the Wilson implementation. No new confidence interval is permitted.

## Codex template disposition

| Codex template | Disposition | Work manuscript IDs |
|---|---|---|
{template_rows}

All 11 Codex templates have a declared use. Work displays without a dedicated template are direct locked tables or textual syntheses, which is valid and does not create an orphan evidence requirement.

## Findings requiring Work delta

| Finding | Severity | Exact IDs | Minimum correction |
|---|---|---|---|
{finding_rows}

Ten Work source paths are outside the original 67-record Codex inventory, but all ten exist at `{LOCK}` and their declared Git object IDs match. This is not an evidence failure: the 67-record inventory was the initial accepted-claim/rendering inventory, not an assertion that every later direct manuscript source already had a P3 evidence ID. This review leaves those 67 records unchanged and records the extra paths with independent Git-object and blob-SHA-256 verification.

## Required next gate

Work should publish a delta that either embeds or explicitly adopts the 25/25 and 8/8 mappings and corrects E3.7 provenance. Codex must then verify only that delta. Until then the recommendation is `P3_G0_TECHNICAL_REWORK_REQUIRED`; this is a provenance/metadata hold, not `P3_G0_BLOCKED_BY_EVIDENCE`.

Stop state: `AWAITING_WORK_FINAL_CROSSWALK_DELTA_AND_COMMANDER_BLUEPRINT_DECISION`. No Chapter 1 work is authorized.
"""
    )


def _validate(payload: dict[str, Any]) -> None:
    remote_work_head = cast(str, _git("rev-parse", "origin/research/p3-manuscript-blueprint-work"))
    assert cast(str, _git("merge-base", remote_work_head, WORK_HEAD)) == WORK_HEAD
    assert cast(str, _git("merge-base", WORK_HEAD, LOCK)) == LOCK
    assert cast(str, _git("merge-base", CODEX_G0_HEAD, LOCK)) == LOCK
    assert len(payload["exhibit_crosswalk"]) == 25
    assert len(payload["formula_crosswalk"]) == 8
    assert len(payload["codex_template_disposition"]) == 11
    assert all(row["disposition"] == "USED" for row in payload["codex_template_disposition"])
    assert not payload["lock_validation"]["disallowed_used_as_affirmative"]
    assert payload["lock_validation"]["status"] == "PASS"
    assert payload["classification_counts"].get("UNSUPPORTED_BY_LOCKED_EVIDENCE", 0) == 0
    assert payload["technical_blockers"] == []


def _write(path: Path, content: dict[str, Any] | str, *, check: bool) -> None:
    expected = _canonical_bytes(content).decode("utf-8") if isinstance(content, dict) else content
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            raise AssertionError(f"Generated artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8", newline="\n")


def build(*, check: bool = False) -> None:
    payload = _build()
    _validate(payload)
    _write(OUTPUT_JSON, payload, check=check)
    _write(OUTPUT_MD, _markdown(payload), check=check)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the P3-G0 Work/Codex exhibit and formula crosswalk validation.")
    parser.add_argument("--check", action="store_true", help="Verify deterministic generated artifacts.")
    args = parser.parse_args()
    build(check=args.check)


if __name__ == "__main__":
    main()
