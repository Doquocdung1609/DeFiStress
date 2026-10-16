from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, cast

LOCK = "3f6e5302483681209e2408531eb5a15389f9fded"
WORK_HEAD = "638434a32656eb312f0cdaa9285c30ddf766df99"
CODEX_INPUT_HEAD = "f3ca9dcd3a8bc1c17ca336f880d5b0adf3b4866a"
OUTPUT_JSON = Path("artifacts/manuscript_p3/P3_G0_FINAL_DELTA_VALIDATION.json")
OUTPUT_MD = Path("docs/manuscript_p3/codex/P3_G0_FINAL_DELTA_TECHNICAL_VERDICT.md")
CATALOG = Path("artifacts/manuscript_p3/P3_EXHIBIT_CATALOG_v1.json")
FORMULA_PLAN = Path("docs/manuscript_p3/codex/P3_FORMULA_AUDIT_PLAN.md")


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def test_exact_heads_and_lock_are_reviewed() -> None:
    assert _git("rev-parse", "origin/research/p3-manuscript-blueprint-work") == WORK_HEAD
    assert _git("merge-base", WORK_HEAD, LOCK) == LOCK
    assert _git("merge-base", CODEX_INPUT_HEAD, LOCK) == LOCK


def test_final_coverage_and_mapping_statuses() -> None:
    payload = _load(OUTPUT_JSON)
    assert payload["coverage"] == {
        "accepted_claims": 44,
        "codex_formula_candidates": 15,
        "codex_templates": 11,
        "displays": 25,
        "equations": 8,
        "excluded_records": 4,
        "figures": 11,
        "mapping_status_counts": {"CODEX_SPEC_REQUIRED": 8, "DIRECT_LOCKED_SOURCE": 10, "MATCHED": 7},
        "original_rqs": 6,
        "tables": 14,
        "unsupported_displays": 0,
    }
    assert all(row["template_mapping_status"] == "PASS" for row in payload["display_validation"])
    assert all(row["claim_status"] == "PASS" for row in payload["display_validation"])
    assert all(row["source_locator_status"] == "PASS" for row in payload["display_validation"])
    assert all(row["formula_mapping_status"] == "PASS" for row in payload["formula_validation"])


def test_display_controls_and_spec_state_are_explicit() -> None:
    payload = _load(OUTPUT_JSON)
    assert all(payload["resolution_status"]["G0-X03"]["control_checks"].values())
    specs = [row for row in payload["display_validation"] if row["mapping_status"] == "CODEX_SPEC_REQUIRED"]
    assert len(specs) == 8
    assert all(row["production_state"] == "SPECIFICATION_PENDING_NOT_RENDERED" for row in specs)


def test_network_claim_association_is_corrected_without_changing_claims() -> None:
    catalog = _load(CATALOG)
    network = next(row for row in catalog["records"] if row["exhibit_id"] == "P3X:NETWORK_EXTENSION_BOUNDARY")
    assert network["accepted_claim_ids"] == ["P2:C25", "P2:C26", "P2:C27", "P2:C28"]
    assert "P2:C29" not in network["accepted_claim_ids"]
    resolution = _load(OUTPUT_JSON)["resolution_status"]["G0-REC-03"]
    assert resolution["status"] == "RESOLVED_CODEX_METADATA_CORRECTION"
    assert resolution["quarantined_claim_id"] == "P2:C29"


def test_p3f03_is_scoped_and_not_selected() -> None:
    row = next(line for line in FORMULA_PLAN.read_text(encoding="utf-8").splitlines() if line.startswith("| P3F03 |"))
    for phrase in [
        "1 USDC token = 1 USD",
        "omits an explicit `P_USDC/USD` factor",
        "not a general USDC-depeg execution identity",
        "not selected among the eight Work manuscript equations",
        "P2:C35",
    ]:
        assert phrase in row
    resolution = _load(OUTPUT_JSON)["resolution_status"]["G0-REC-04"]
    assert resolution["selected_by_work"] is False
    assert resolution["unit_note_present"] is True


def test_wilson_primary_locators_are_exact_and_no_formula_changed() -> None:
    formulas = {row["work_equation_id"]: row for row in _load(OUTPUT_JSON)["formula_validation"]}
    assert [row["path"] for row in formulas["E3.7"]["source_locators"]] == [
        "sim/research/aave_suite.py",
        "scripts/research/run_deep_cascade_study.py",
        "data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv",
    ]
    assert all(row["source_locator_status"] == "PASS" for row in formulas.values())
    assert all(row["formula_changed"] is False for row in formulas.values())


def test_generated_outputs_have_valid_self_checksums() -> None:
    payload = _load(OUTPUT_JSON)
    expected = payload["output_provenance"].pop("content_sha256")
    assert hashlib.sha256(_canonical_bytes(payload)).hexdigest() == expected
    raw = OUTPUT_MD.read_text(encoding="utf-8")
    body, checksum_line = raw.rsplit("\nContent SHA-256 (UTF-8, excluding this checksum line): `", 1)
    assert hashlib.sha256(body.encode()).hexdigest() == checksum_line.removesuffix("`\n")


def test_builder_is_deterministic_and_scope_is_clean() -> None:
    subprocess.run(
        [str(Path(".venv/Scripts/python.exe")), "scripts/research/build_p3_g0_final_delta_validation.py", "--check"],
        check=True,
    )
    status = _git("status", "--short")
    assert "docs/manuscript_p3/work/" not in status
    for path in [
        "data/processed/research_final/frozen_v3/",
        "data/processed/research_final/oracle_transmission_diagnostic_v1/",
        "data/processed/research_final/scientific_integration_v1/",
        "data/processed/research_final/final_accepted_claims_v1/",
        "sim/",
    ]:
        assert path not in status
