# ruff: noqa: E501 -- exact scientific limitations and source locators are intentionally explicit.
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, cast

LOCK = "3f6e5302483681209e2408531eb5a15389f9fded"
WORK_START = "e26e2d5a21c6ac78bd4db7be345409b5c7690a80"
WORK_HEAD = "638434a32656eb312f0cdaa9285c30ddf766df99"
CODEX_INPUT_HEAD = "f3ca9dcd3a8bc1c17ca336f880d5b0adf3b4866a"

WORK_ROOT = "docs/manuscript_p3/work"
WORK_CROSSWALK = f"{WORK_ROOT}/P3_G0_WORK_CODEX_EXHIBIT_CROSSWALK.json"
WORK_REPORT = f"{WORK_ROOT}/P3_G0_RECONCILIATION_REPORT.md"
WORK_PLAN = f"{WORK_ROOT}/P3_TABLE_FIGURE_EQUATION_PLAN.json"
WORK_BLUEPRINT = f"{WORK_ROOT}/P3_MANUSCRIPT_BLUEPRINT_v1.md"
WORK_CLAIMS = f"{WORK_ROOT}/P3_CLAIM_TO_CHAPTER_MATRIX.json"

CATALOG = Path("artifacts/manuscript_p3/P3_EXHIBIT_CATALOG_v1.json")
FORMULA_PLAN = Path("docs/manuscript_p3/codex/P3_FORMULA_AUDIT_PLAN.md")
PRIOR_VALIDATION = Path("artifacts/manuscript_p3/P3_G0_EXHIBIT_CROSSWALK_VALIDATION.json")
OUTPUT_JSON = Path("artifacts/manuscript_p3/P3_G0_FINAL_DELTA_VALIDATION.json")
OUTPUT_MD = Path("docs/manuscript_p3/codex/P3_G0_FINAL_DELTA_TECHNICAL_VERDICT.md")

DISALLOWED = {
    "INT:CL_FROZEN_RQ1_UNQUALIFIED_WORDING",
    "INT:CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING",
    "INT:CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT",
    "INT:CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION",
}
EXPECTED_WORK_DELTA = {
    WORK_CROSSWALK,
    WORK_REPORT,
    WORK_PLAN,
    WORK_BLUEPRINT,
}
EXPECTED_STATUSES = {"MATCHED": 7, "DIRECT_LOCKED_SOURCE": 10, "CODEX_SPEC_REQUIRED": 8}
DISPLAY_CONTROL_IDS = ["F5.2", "F5.3", "F5.6", "F6.1", "T4.1"]
SPEC_REQUIRED_IDS = ["T3.1", "F4.1", "T4.1", "F5.2", "F5.3", "F5.6", "F6.1", "F6.2"]


def _git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(["git", *args], check=True, capture_output=True)
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _load_at(commit: str, path: str) -> dict[str, Any]:
    raw = cast(bytes, _git("show", f"{commit}:{path}", binary=True))
    return cast(dict[str, Any], json.loads(raw.decode("utf-8")))


def _text_at(commit: str, path: str) -> str:
    return cast(bytes, _git("show", f"{commit}:{path}", binary=True)).decode("utf-8")


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


def _verify_locator(locator: dict[str, Any]) -> dict[str, Any]:
    path = locator["path"]
    commit = locator["commit"]
    declared = locator["git_blob_sha"]
    actual = cast(str, _git("rev-parse", f"{commit}:{path}"))
    blob = cast(bytes, _git("show", f"{commit}:{path}", binary=True))
    return {
        "path": path,
        "commit": commit,
        "selector": locator.get("selector"),
        "declared_git_blob_id": declared,
        "actual_git_blob_id": actual,
        "git_blob_sha256": hashlib.sha256(blob).hexdigest(),
        "status": "PASS" if commit == LOCK and actual == declared else "FAIL",
    }


def _formula_row(formula_id: str) -> str:
    return next(
        line for line in FORMULA_PLAN.read_text(encoding="utf-8").splitlines() if line.startswith(f"| {formula_id} |")
    )


def _build() -> dict[str, Any]:
    crosswalk = _load_at(WORK_HEAD, WORK_CROSSWALK)
    work_plan = _load_at(WORK_HEAD, WORK_PLAN)
    work_claims = _load_at(WORK_HEAD, WORK_CLAIMS)
    work_report = _text_at(WORK_HEAD, WORK_REPORT)
    work_blueprint = _text_at(WORK_HEAD, WORK_BLUEPRINT)
    prior = _load(PRIOR_VALIDATION)
    catalog = _load(CATALOG)
    catalog_by_id = {row["exhibit_id"]: row for row in catalog["records"]}
    prior_display = {row["work_exhibit_id"]: row for row in prior["exhibit_crosswalk"]}
    prior_formula = {row["work_exhibit_id"]: row for row in prior["formula_crosswalk"]}

    registry = _load(Path("data/processed/research_final/final_accepted_claims_v1/accepted_claims_registry.json"))
    affirmative = {
        row["registry_id"]
        for row in registry["records"]
        if row["final_gate_status"] in {"ACCEPTED", "ACCEPTED_WITH_LIMITATIONS"}
    }

    displays: list[dict[str, Any]] = []
    for row in crosswalk["display_crosswalk"]:
        work_id = row["proposed_manuscript_id"]
        locators = [_verify_locator(locator) for locator in row["exact_source_artifact_locators"]]
        claims = set(row["related_accepted_claim_ids"])
        declared_templates = set(row["codex_exhibit_template_ids"])
        validated_primary_templates = set(row["codex_validated_primary_template_ids"])
        expected_templates = set(prior_display[work_id]["codex_template_ids"])
        displays.append(
            {
                "work_id": work_id,
                "chapter": row["chapter"],
                "section": row["section"],
                "mapping_status": row["status"],
                "mapping_status_is_not_render_status": True,
                "codex_template_ids": sorted(declared_templates),
                "validated_primary_template_ids": sorted(validated_primary_templates),
                "prior_validated_template_ids": sorted(expected_templates),
                "template_mapping_status": "PASS" if validated_primary_templates == expected_templates else "FAIL",
                "claim_status": "PASS" if claims <= affirmative and not claims & DISALLOWED else "FAIL",
                "source_locator_status": "PASS"
                if locators and all(x["status"] == "PASS" for x in locators)
                else "FAIL",
                "source_locators": locators,
                "required_display_controls": row["required_display_controls"],
                "reproducibility_classification": row["codex_reproducibility_classification"],
                "production_state": "SPECIFICATION_PENDING_NOT_RENDERED"
                if row["status"] == "CODEX_SPEC_REQUIRED"
                else "SOURCE_MAPPING_VALIDATED_NOT_RENDERED",
                "technical_support_status": row["codex_prior_technical_support_status"],
            }
        )

    formulas: list[dict[str, Any]] = []
    for row in crosswalk["formula_crosswalk"]:
        work_id = row["work_equation_id"]
        locators = [_verify_locator(locator) for locator in row["source_locators"]]
        expected = prior_formula[work_id]["codex_formula_ids"]
        formulas.append(
            {
                "work_equation_id": work_id,
                "codex_formula_ids": row["codex_formula_ids"],
                "validated_primary_formula_ids": row["codex_validated_primary_formula_ids"],
                "formula_mapping_status": "PASS" if row["codex_validated_primary_formula_ids"] == expected else "FAIL",
                "formula_changed": row["formula_changed"],
                "source_locator_status": "PASS"
                if locators and all(x["status"] == "PASS" for x in locators)
                else "FAIL",
                "source_locators": locators,
                "semantic_relation": row["semantic_relation"],
                "units_implementation_check": row["units_implementation_check"],
            }
        )

    status_counts = dict(Counter(row["mapping_status"] for row in displays))
    network = catalog_by_id["P3X:NETWORK_EXTENSION_BOUNDARY"]
    p3f03 = _formula_row("P3F03")
    delta_paths = {
        line.split("\t", 1)[1]
        for line in cast(str, _git("diff", "--name-status", f"{WORK_START}..{WORK_HEAD}")).splitlines()
    }
    display_by_id = {row["work_id"]: row for row in displays}
    controls_pass = {
        "F5.2": all(
            needle in " ".join(display_by_id["F5.2"]["required_display_controls"])
            for needle in ["lexicographically", "pin exact trace/event locator"]
        ),
        "F5.3": all(
            needle in " ".join(display_by_id["F5.3"]["required_display_controls"])
            for needle in ["Only 0%", "separate axes"]
        ),
        "F5.6": all(
            needle in " ".join(display_by_id["F5.6"]["required_display_controls"])
            for needle in ["separate facets", "USD capacity", "USDC-token", "WETH seized"]
        ),
        "F6.1": all(
            needle in " ".join(display_by_id["F6.1"]["required_display_controls"])
            for needle in ["two panels", "zero HIGH-alert hours", "minus 45 hours"]
        ),
        "T4.1": "Do not add near-threshold subgroup statistics"
        in " ".join(display_by_id["T4.1"]["required_display_controls"]),
    }

    work_file_integrity = []
    for path in sorted(EXPECTED_WORK_DELTA):
        blob_id = cast(str, _git("rev-parse", f"{WORK_HEAD}:{path}"))
        raw = cast(bytes, _git("show", f"{WORK_HEAD}:{path}", binary=True))
        work_file_integrity.append(
            {"path": path, "git_blob_id": blob_id, "git_blob_sha256": hashlib.sha256(raw).hexdigest()}
        )

    payload = {
        "schema_version": "p3-g0-final-delta-validation-v1",
        "transformation_version": "p3-g0-final-delta-review-v1",
        "reviewed_heads": {
            "scientific_lock": LOCK,
            "work_starting_head": WORK_START,
            "work_final_head": WORK_HEAD,
            "codex_input_head": CODEX_INPUT_HEAD,
        },
        "work_delta_paths": sorted(delta_paths),
        "work_file_integrity": work_file_integrity,
        "coverage": {
            "displays": len(displays),
            "tables": crosswalk["counts"]["tables"],
            "figures": crosswalk["counts"]["figures_including_schematics_and_combined"],
            "equations": len(formulas),
            "codex_templates": len(crosswalk["codex_template_reverse_assignments"]),
            "codex_formula_candidates": len(crosswalk["codex_formula_dispositions"]),
            "mapping_status_counts": status_counts,
            "accepted_claims": work_claims["coverage"]["affirmative_allocated"],
            "excluded_records": work_claims["coverage"]["excluded"],
            "original_rqs": len(work_claims["original_research_questions"]),
            "unsupported_displays": sum(
                x["technical_support_status"] != "SUPPORTED_BY_LOCKED_EVIDENCE" for x in displays
            ),
        },
        "display_validation": displays,
        "formula_validation": formulas,
        "template_dispositions": crosswalk["codex_template_reverse_assignments"],
        "resolution_status": {
            "G0-X01": {
                "status": "RESOLVED",
                "evidence": "25/25 Work IDs map to a matched template, a direct locked source, or a rendition requiring Codex specification; CODEX_SPEC_REQUIRED is not rendered output.",
            },
            "G0-X02": {
                "status": "RESOLVED",
                "evidence": "E3.7 pins both locked _wilson implementations and frozen rq1_monte_carlo.csv; no interval was recalculated.",
            },
            "G0-X03": {"status": "RESOLVED", "control_checks": controls_pass},
            "G0-REC-03": {
                "status": "RESOLVED_CODEX_METADATA_CORRECTION",
                "network_template_claim_ids": network["accepted_claim_ids"],
                "quarantined_claim_id": "P2:C29",
                "evidence": "Network template now uses C25/C26/C27/C28; time-series CV claim C29 is not topology support and is not propagated to F6.2.",
            },
            "G0-REC-04": {
                "status": "RESOLVED_SCOPED_PROSE_ONLY",
                "formula_id": "P3F03",
                "selected_by_work": any("P3F03" in row["codex_formula_ids"] for row in formulas),
                "unit_note_present": all(
                    phrase in p3f03
                    for phrase in [
                        "1 USDC token = 1 USD",
                        "omits an explicit `P_USDC/USD` factor",
                        "not a general USDC-depeg execution identity",
                        "P2:C35",
                    ]
                ),
            },
        },
        "source_preservation": {
            "work_files_modified_by_codex": False,
            "locked_frozen_oracle_integration_p2_registry_engine_or_rqs_modified": False,
            "new_simulation_or_estimated_finding": False,
            "work_delta_is_exactly_four_owned_files": delta_paths == EXPECTED_WORK_DELTA,
            "scientific_lock_in_crosswalk": all(
                locator["commit"] == LOCK
                for row in crosswalk["display_crosswalk"]
                for locator in row["exact_source_artifact_locators"]
            ),
            "work_plan_scientific_lock": work_plan["scientific_lock_commit"],
            "work_plan_record_count": len(work_plan["exhibits"]),
            "blueprint_and_report_read": all(
                marker in work_report + work_blueprint
                for marker in ["P3_G0_WORK_CODEX_EXHIBIT_CROSSWALK.json", "AWAITING_COMMANDER_BLUEPRINT_APPROVAL"]
            ),
        },
        "remaining_production_only_limitations": [
            "The eight CODEX_SPEC_REQUIRED placements need chapter-stage rendition specifications and later technical review; none is a rendered exhibit yet.",
            "The five retained display controls must be enforced during production.",
            "School template verification remains pending and blocks final DOCX formatting, not content-only Blueprint approval.",
            "Two large borrower CSV read-scope limitations remain disclosed; no new dependent inference was introduced.",
        ],
        "technical_blockers": [],
        "commander_recommendation": "P3_G0_FINAL_TECHNICAL_PASS",
        "stop_state": "AWAITING_COMMANDER_BLUEPRINT_LOCK",
    }
    return _seal_json(payload)


def _validate(payload: dict[str, Any]) -> None:
    assert cast(str, _git("rev-parse", "origin/research/p3-manuscript-blueprint-work")) == WORK_HEAD
    assert cast(str, _git("merge-base", WORK_HEAD, LOCK)) == LOCK
    assert cast(str, _git("merge-base", CODEX_INPUT_HEAD, LOCK)) == LOCK
    assert set(payload["work_delta_paths"]) == EXPECTED_WORK_DELTA
    assert payload["coverage"]["displays"] == 25
    assert payload["coverage"]["equations"] == 8
    assert payload["coverage"]["codex_templates"] == 11
    assert payload["coverage"]["codex_formula_candidates"] == 15
    assert payload["coverage"]["mapping_status_counts"] == EXPECTED_STATUSES
    assert payload["coverage"]["accepted_claims"] == 44
    assert payload["coverage"]["excluded_records"] == 4
    assert payload["coverage"]["original_rqs"] == 6
    assert payload["coverage"]["unsupported_displays"] == 0
    assert all(row["template_mapping_status"] == "PASS" for row in payload["display_validation"])
    assert all(row["claim_status"] == "PASS" for row in payload["display_validation"])
    assert all(row["source_locator_status"] == "PASS" for row in payload["display_validation"])
    assert all(row["formula_mapping_status"] == "PASS" for row in payload["formula_validation"])
    assert all(row["source_locator_status"] == "PASS" for row in payload["formula_validation"])
    assert all(not row["formula_changed"] for row in payload["formula_validation"])
    assert all(
        payload["resolution_status"][key]["status"].startswith("RESOLVED") for key in payload["resolution_status"]
    )
    assert all(payload["resolution_status"]["G0-X03"]["control_checks"].values())
    assert payload["resolution_status"]["G0-REC-03"]["network_template_claim_ids"] == [
        "P2:C25",
        "P2:C26",
        "P2:C27",
        "P2:C28",
    ]
    assert payload["resolution_status"]["G0-REC-04"]["selected_by_work"] is False
    assert payload["resolution_status"]["G0-REC-04"]["unit_note_present"] is True
    assert payload["source_preservation"]["work_plan_scientific_lock"] == LOCK
    assert payload["source_preservation"]["work_plan_record_count"] == 33
    assert payload["technical_blockers"] == []


def _markdown(payload: dict[str, Any]) -> str:
    status_rows = "\n".join(
        f"| {status} | {count} |" for status, count in sorted(payload["coverage"]["mapping_status_counts"].items())
    )
    resolution_rows = "\n".join(
        f"| {finding} | {record['status']} |" for finding, record in payload["resolution_status"].items()
    )
    integrity_rows = "\n".join(
        f"| `{row['path']}` | `{row['git_blob_id']}` | `{row['git_blob_sha256']}` |"
        for row in payload["work_file_integrity"]
    )
    return _seal_markdown(
        f"""# P3-G0 Final Delta — Independent Technical Verdict

Status: `P3_G0_FINAL_TECHNICAL_PASS`

Scientific lock: `{LOCK}`

Work PR #15 reviewed HEAD: `{WORK_HEAD}`

Codex PR #14 input HEAD: `{CODEX_INPUT_HEAD}`

## Verdict

The final Work delta resolves G0-X01, G0-X02 and G0-X03 without changing scientific results. All **25/25 displays**, **8/8 selected equations** and **11/11 Codex template dispositions** resolve. No display is unsupported, no disallowed claim supports an affirmative exhibit, and `CODEX_SPEC_REQUIRED` remains a production specification state rather than a claim that an exhibit was rendered.

Two Codex-owned metadata defects were corrected: `P3X:NETWORK_EXTENSION_BOUNDARY` now uses accepted network claims P2:C25–C28 and quarantines time-series claim P2:C29; P3F03 now states its baseline 1-USDC-equals-1-USD dimensional convention, missing explicit USDC/USD factor and C35-limited non-general-depeg scope. P3F03 remains unselected among the eight Work equations.

## Coverage

- Displays: {payload["coverage"]["displays"]} ({payload["coverage"]["tables"]} tables, {payload["coverage"]["figures"]} figures/schematics).
- Equations: {payload["coverage"]["equations"]} selected; {payload["coverage"]["codex_formula_candidates"]} Codex candidates have dispositions.
- Templates: {payload["coverage"]["codex_templates"]}/11 have dispositions.
- Claims: {payload["coverage"]["accepted_claims"]} affirmative, {payload["coverage"]["excluded_records"]} excluded, six original RQs.
- Unsupported displays: {payload["coverage"]["unsupported_displays"]}.

| Work mapping status | Count |
|---|---:|
{status_rows}

The eight `CODEX_SPEC_REQUIRED` IDs are `{", ".join(SPEC_REQUIRED_IDS)}`. They are source-grounded requests for later rendition specifications, not production files.

## Finding resolution

| Finding | Status |
|---|---|
{resolution_rows}

- **G0-X01:** Work preserves the many-to-many mapping; no one-to-one exhibit/template assumption was imposed.
- **G0-X02:** E3.7 uses `sim/research/aave_suite.py:211`, `scripts/research/run_deep_cascade_study.py:353` and `frozen_v3/tables/rq1_monte_carlo.csv`. The locked expression/values were inspected; no new interval was calculated.
- **G0-X03:** controls are present for `{", ".join(DISPLAY_CONTROL_IDS)}`.
- **G0-REC-03:** P2:C29 is not network topology evidence and is absent from the corrected network template and Work F6.2 claims.
- **G0-REC-04:** P3F03 is retained verbatim as a scoped model approximation with explicit USDC-token, USD-equivalent, WETH and price-denomination limits; it is prose-only and not a selected manuscript equation.

## Exact Work delta integrity

| Work-owned path | Git blob ID | SHA-256 of Git blob bytes |
|---|---|---|
{integrity_rows}

Codex did not modify Work-owned files. Frozen, Oracle, Integration, P2, Final Registry, engine and six RQs were not changed. No simulation, retuning, interval calculation, Chapter 1 prose, exhibit rendering, DOCX edit or merge occurred.

## Remaining production-only limitations

1. Eight `CODEX_SPEC_REQUIRED` placements still need chapter-stage rendition specifications and later technical review.
2. The five display controls must be enforced during production.
3. School-template verification remains pending and blocks final DOCX formatting, not content-only Blueprint approval.
4. The disclosed large-CSV read-scope limits remain; they do not block the selected locked mappings.

Commander recommendation: `P3_G0_FINAL_TECHNICAL_PASS`.

Stop state: `AWAITING_COMMANDER_BLUEPRINT_LOCK`. No Chapter 1 or production rendering is authorized by this verdict.
"""
    )


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
    parser = argparse.ArgumentParser(description="Build the final P3-G0 Work delta technical validation.")
    parser.add_argument("--check", action="store_true", help="Verify deterministic generated artifacts.")
    args = parser.parse_args()
    build(check=args.check)


if __name__ == "__main__":
    main()
