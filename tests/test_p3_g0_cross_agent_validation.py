from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, cast

from sim.research.aave_suite import _wilson

LOCK = "3f6e5302483681209e2408531eb5a15389f9fded"
WORK_HEAD = "e26e2d5a21c6ac78bd4db7be345409b5c7690a80"
CODEX_HEAD = "17b839528e58a622aa0554067b19823a8f33bda5"
OUTPUT_JSON = Path("artifacts/manuscript_p3/P3_G0_EXHIBIT_CROSSWALK_VALIDATION.json")
OUTPUT_MD = Path("docs/manuscript_p3/codex/P3_G0_EXHIBIT_RECONCILIATION_TECHNICAL_REVIEW.md")
DISALLOWED = {
    "INT:CL_FROZEN_RQ1_UNQUALIFIED_WORDING",
    "INT:CL_FROZEN_RQ2_DIRECT_ELIGIBILITY_WORDING",
    "INT:CL_UNSUPPORTED_AAVE_USES_UNISWAP_SPOT",
    "INT:CL_UNSUPPORTED_HISTORICAL_CAUSAL_CONTAGION",
}


def _load(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def test_reviewed_heads_descend_from_scientific_lock() -> None:
    assert _git("rev-parse", "origin/research/p3-manuscript-blueprint-work") == WORK_HEAD
    assert _git("merge-base", WORK_HEAD, LOCK) == LOCK
    assert _git("merge-base", CODEX_HEAD, LOCK) == LOCK


def test_all_work_exhibits_formulas_and_codex_templates_are_reconciled() -> None:
    payload = _load(OUTPUT_JSON)
    assert payload["counts"] == {
        "affirmative_claims": 44,
        "codex_audited_formulas": 15,
        "codex_templates": 11,
        "disallowed_claims": 4,
        "inventory_records_unchanged": 67,
        "work_equations": 8,
        "work_figures": 11,
        "work_tables": 14,
    }
    assert len(payload["exhibit_crosswalk"]) == 25
    assert len(payload["formula_crosswalk"]) == 8
    assert len(payload["codex_template_disposition"]) == 11
    assert all(row["disposition"] == "USED" for row in payload["codex_template_disposition"])
    assert payload["classification_counts"] == {
        "NEEDS_DISPLAY_SPEC": 4,
        "RENDERABLE_FROM_LOCKED_ARTIFACT": 10,
        "SCHEMATIC_FROM_LOCKED_MODEL_SPEC": 3,
        "TEXTUAL_SYNTHESIS": 8,
    }


def test_every_crosswalk_locator_and_locked_id_resolves() -> None:
    payload = _load(OUTPUT_JSON)
    for row in [*payload["exhibit_crosswalk"], *payload["formula_crosswalk"]]:
        assert row["claim_ids_status"] == "PASS"
        assert row["result_ids_status"] == "PASS"
        assert row["evidence_ids_status"] == "PASS"
        assert row["source_locators_status"] == "PASS"
        for locator in row["source_locators"]:
            assert locator["commit"] == LOCK
            assert locator["actual_git_blob_id"] == locator["declared_git_blob_id"]
            assert len(locator["git_blob_sha256"]) == 64
    assert all(row["codex_template_status"] == "PASS" for row in payload["exhibit_crosswalk"])
    assert payload["technical_blockers"] == []


def test_claim_gate_keeps_disallowed_records_out_of_affirmative_exhibits() -> None:
    payload = _load(OUTPUT_JSON)
    used = {
        claim
        for row in [*payload["exhibit_crosswalk"], *payload["formula_crosswalk"]]
        for claim in row["accepted_claim_ids"]
    }
    assert not used & DISALLOWED
    assert payload["lock_validation"]["disallowed_used_as_affirmative"] == []
    assert payload["lock_validation"]["six_rqs"] == 6
    assert payload["lock_validation"]["status"] == "PASS"


def test_formula_mapping_and_required_wilson_provenance_are_exact() -> None:
    formulas = {row["work_exhibit_id"]: row for row in _load(OUTPUT_JSON)["formula_crosswalk"]}
    assert {key: row["codex_formula_ids"] for key, row in formulas.items()} == {
        "E3.1": ["P3F01", "P3F02"],
        "E3.2": ["P3F05"],
        "E3.3": ["P3F06"],
        "E3.4": ["P3F08"],
        "E3.5": ["P3F02"],
        "E3.6": ["P3F15"],
        "E3.7": ["P3F15"],
        "E3.8": ["P3F09"],
    }
    assert formulas["E3.7"]["audited_source_locators"] == [
        "sim/research/aave_suite.py:211",
        "scripts/research/run_deep_cascade_study.py:353",
        "data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv",
    ]
    assert all(row["compatibility_status"] == "PASS_WITH_REQUIRED_LIMITATIONS" for row in formulas.values())


def test_locked_wilson_values_recompute_without_creating_new_intervals() -> None:
    with Path("data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        interval = _wilson(int(row["depth_ge_2_successes"]), int(row["actual_runs"]))
        assert abs(interval["lower"] - float(row["depth_ge_2_wilson_lower"])) < 1e-15
        assert abs(interval["upper"] - float(row["depth_ge_2_wilson_upper"])) < 1e-15


def test_reconciliation_outputs_have_valid_self_checksums() -> None:
    payload = _load(OUTPUT_JSON)
    expected = payload["output_provenance"].pop("content_sha256")
    assert hashlib.sha256(_canonical_bytes(payload)).hexdigest() == expected
    raw = OUTPUT_MD.read_text(encoding="utf-8")
    body, checksum_line = raw.rsplit("\nContent SHA-256 (UTF-8, excluding this checksum line): `", 1)
    assert hashlib.sha256(body.encode()).hexdigest() == checksum_line.removesuffix("`\n")


def test_builder_check_is_deterministic_and_does_not_touch_work_or_locked_sources() -> None:
    subprocess.run(
        [str(Path(".venv/Scripts/python.exe")), "scripts/research/build_p3_g0_cross_agent_validation.py", "--check"],
        check=True,
    )
    status = subprocess.run(["git", "status", "--short"], check=True, capture_output=True, text=True).stdout
    assert "docs/manuscript_p3/work/" not in status
    assert "data/processed/research_final/frozen_v3/" not in status
    assert "data/processed/research_final/oracle_transmission_diagnostic_v1/" not in status
    assert "data/processed/research_final/scientific_integration_v1/" not in status
    assert "data/processed/research_final/final_accepted_claims_v1/" not in status
