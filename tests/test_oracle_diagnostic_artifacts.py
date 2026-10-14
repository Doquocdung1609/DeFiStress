from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path("data/processed/research_final/oracle_transmission_diagnostic_v1")
FROZEN_MANIFEST = Path("data/processed/research_final/frozen_v3/manifest.json")
CANONICAL = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
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


def _assert_no_nonfinite(value: Any) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _assert_no_nonfinite(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_nonfinite(item)
    elif isinstance(value, str):
        assert value.lower() not in {"nan", "infinity", "-infinity", "inf", "-inf"}


def test_oracle_diagnostic_preserves_locked_inputs_and_reproduces_policy_a() -> None:
    selection = _load(ROOT / "selection_manifest.json")
    baseline = _load(ROOT / "baseline_reproduction.json")
    assert selection["status"] == "PRE_REGISTERED_BEFORE_POLICY_B_C_EXECUTION"
    assert baseline["status"] == "PASS"
    assert len(baseline["deterministic_checks"]) == 8
    assert len(baseline["monte_carlo_checks"]) == 10
    assert all(row["status"] == "PASS" for row in baseline["deterministic_checks"])
    assert all(row["status"] == "PASS" for row in baseline["monte_carlo_checks"])
    assert _sha(FROZEN_MANIFEST) == selection["input_hashes"]["frozen_v3_manifest"]["sha256"]
    assert _sha(CANONICAL) == selection["input_hashes"]["canonical_snapshot"]["sha256"]


def test_oracle_comparison_matrix_has_locked_cardinality_and_policy_findings() -> None:
    rows = _load(ROOT / "comparison_matrix.json")["rows"]
    assert len(rows) == 72
    assert len({row["result_id"] for row in rows}) == 72
    assert Counter(row["policy_id"] for row in rows) == {policy: 18 for policy in POLICIES}
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_case[row["case_id"]].append(row)
        assert row["deterministic_repeat_match"] is True
        assert row["post_wave1_dex_state_matches_a"] is True
        assert row["all_numeric_finite"] is True
    assert len(by_case) == 18
    assert all({row["policy_id"] for row in case_rows} == POLICIES for case_rows in by_case.values())

    depth2_cases = {"DET_D2_M40_H90", "DET_D2_M40_H95", "DET_D2_M50_H90", "DET_D2_M50_H95"}
    for case_id in depth2_cases:
        depth_by_policy = {row["policy_id"]: row["cascade_depth"] for row in by_case[case_id]}
        assert depth_by_policy["A_ADVERSE_PASS_THROUGH"] == 2
        assert {depth_by_policy[policy] for policy in POLICIES - {"A_ADVERSE_PASS_THROUGH"}} == {1}
    _assert_no_nonfinite(rows)


def test_borrower_evidence_uses_redacted_ids_and_common_direct_shock_hf() -> None:
    with (ROOT / "borrower_level_evidence.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 18 * 4 * 454
    assert not any(re.fullmatch(r"0x[0-9a-fA-F]{40}", row["borrower_hash"]) for row in rows)
    assert not any(
        value.lower() in {"nan", "infinity", "-infinity", "inf", "-inf"}
        for row in rows
        for value in row.values()
    )

    direct_hf: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        direct_hf[(row["case_id"], row["borrower_hash"])].add(row["direct_shock_hf"])
    assert all(len(values) == 1 for values in direct_hf.values())


def test_oracle_diagnostic_manifest_hashes_resolve() -> None:
    manifest = _load(ROOT / "manifest.json")
    assert manifest["scientific_pass_declared"] is False
    assert manifest["scientific_content_lock_declared"] is False
    assert manifest["test_evidence"]["status"] == "PASS"
    for relative, expected in manifest["artifact_hashes"].items():
        assert _sha(ROOT / relative) == expected
    for path, expected in manifest["report_hashes"].items():
        assert _sha(Path(path)) == expected

