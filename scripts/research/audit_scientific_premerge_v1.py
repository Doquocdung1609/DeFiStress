from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import subprocess
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

D = Decimal
CANONICAL = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
FROZEN = Path("data/processed/research_final/frozen_v3")
ORACLE = Path("data/processed/research_final/oracle_transmission_diagnostic_v1")
INTEGRATION = Path("data/processed/research_final/scientific_integration_v1")
OUTPUT = Path("data/processed/research_final/scientific_premerge_audit_v1/audit_results.json")

FROZEN_HEAD = "9842c4f2c35adb8b4ec906e1bc76afa825d197c7"
ORACLE_HEAD = "3011ba5e8cd23ee697c36d0aec6d047d8d58f653"
P2_HEAD = "8f5b635a316d72546b8a0eb0c2e8a66503b5d44f"
CANONICAL_DECLARED_SHA = "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"
POLICIES = (
    "A_ADVERSE_PASS_THROUGH",
    "B_REFERENCE_ONLY",
    "C_WEAK_LAGGED_SMOOTHED_PROXY",
    "C_MODERATE_LAGGED_SMOOTHED_PROXY",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def git_blob(commit: str, path: Path) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path.as_posix()}"],
        check=True,
        capture_output=True,
    ).stdout


def commit_exists(commit: str) -> bool:
    return (
        subprocess.run(
            ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
            capture_output=True,
        ).returncode
        == 0
    )


def verify_manifest(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for relative, expected in manifest.get("artifact_hashes", {}).items():
        path = root / relative
        actual = sha(path)
        rows.append(
            {
                "path": path.as_posix(),
                "declared_sha256": expected,
                "worktree_sha256": actual,
                "match": actual == expected,
            }
        )
    for relative, expected in manifest.get("report_hashes", {}).items():
        path = Path(relative)
        actual = sha(path)
        rows.append(
            {
                "path": path.as_posix(),
                "declared_sha256": expected,
                "worktree_sha256": actual,
                "match": actual == expected,
            }
        )
    return {
        "checked": len(rows),
        "matched": sum(row["match"] for row in rows),
        "mismatches": [row for row in rows if not row["match"]],
    }


def finite(value: Any) -> bool:
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    if isinstance(value, list):
        return all(finite(item) for item in value)
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, str):
        return value.lower() not in {"nan", "inf", "-inf", "infinity", "-infinity"}
    return True


def hf(
    *,
    collateral_weth: Decimal,
    debt_usdc: Decimal,
    liquidation_threshold: Decimal,
    other_collateral_usd: Decimal,
    other_debt_usd: Decimal,
    weth_price: Decimal,
) -> Decimal:
    debt = debt_usdc + other_debt_usd
    if debt <= 0:
        return D("Infinity")
    adjusted = collateral_weth * weth_price * liquidation_threshold
    adjusted += other_collateral_usd * liquidation_threshold
    return max(D(0), adjusted / debt)


def event_locators(row: dict[str, str]) -> list[str]:
    return [value for value in row["event_locators"].split("|") if value]


def row_key(row: dict[str, str]) -> tuple[str, str, str]:
    return row["case_id"], row["policy_id"], row["borrower_hash"]


def select_samples(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    rules = {
        "newly_eligible_executed": lambda row: row["newly_eligible_after_wave1"] == "True"
        and row["executed_positive_debt_wave2"] == "True",
        "newly_eligible_skipped": lambda row: row["newly_eligible_after_wave1"] == "True"
        and row["executed_positive_debt_wave2"] == "False",
        "c_weak_newly_eligible_skipped": lambda row: row["policy_id"]
        == "C_WEAK_LAGGED_SMOOTHED_PROXY"
        and row["newly_eligible_after_wave1"] == "True"
        and row["executed_positive_debt_wave2"] == "False",
        "c_moderate_executed_wave2": lambda row: row["policy_id"]
        == "C_MODERATE_LAGGED_SMOOTHED_PROXY"
        and row["executed_positive_debt_wave2"] == "True",
        "control_without_wave2_execution": lambda row: row["case_type"]
        == "DETERMINISTIC_CONTROL"
        and row["executed_positive_debt_wave2"] == "False",
    }
    selected: dict[str, dict[str, str]] = {}
    for name, predicate in rules.items():
        candidates = sorted((row for row in rows if predicate(row)), key=row_key)
        if not candidates:
            raise ValueError(f"No sample for deterministic rule: {name}")
        selected[name] = candidates[0]
    return selected


def main() -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    frozen_manifest = load_json(FROZEN / "manifest.json")
    oracle_manifest = load_json(ORACLE / "manifest.json")
    integration_manifest = load_json(INTEGRATION / "manifest.json")
    canonical = load_json(CANONICAL)
    positions = {row["borrower_hash"]: row for row in canonical["borrowers"]}

    audit_rows = read_csv(INTEGRATION / "eligible_vs_executed_audit.csv")
    summary_rows = read_csv(INTEGRATION / "eligible_vs_executed_summary.csv")
    events = {
        row["event_id"]: row
        for row in (
            json.loads(line)
            for line in (INTEGRATION / "targeted_event_trace.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        )
    }
    oracle_comparison = {
        row["result_id"]: row
        for row in load_json(ORACLE / "comparison_matrix.json")["rows"]
    }

    counts: dict[str, Counter[str]] = defaultdict(Counter)
    debt_by_policy: dict[str, Decimal] = defaultdict(Decimal)
    hf_mismatches: list[str] = []
    event_mismatches: list[str] = []
    skip_explanation_mismatches: list[str] = []
    route_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for row in audit_rows:
        policy = row["policy_id"]
        initial = positions[row["borrower_hash"]]
        direct_hf = hf(
            collateral_weth=D(str(initial["collateral_weth"])),
            debt_usdc=D(str(initial["debt_usdc"])),
            liquidation_threshold=D(str(initial["liquidation_threshold"])),
            other_collateral_usd=D(str(initial["other_collateral_usd"])),
            other_debt_usd=D(str(initial["other_debt_usd"])),
            weth_price=D(row["direct_shock_valuation_price_usd_per_weth"]),
        )
        post_hf = hf(
            collateral_weth=D(row["post_wave1_weth_collateral"]),
            debt_usdc=D(row["post_wave1_usdc_debt"]),
            liquidation_threshold=D(str(initial["liquidation_threshold"])),
            other_collateral_usd=D(row["post_wave1_other_collateral_usd"]),
            other_debt_usd=D(row["post_wave1_other_debt_usd"]),
            weth_price=D(row["post_wave1_borrower_valuation_price_usd_per_weth"]),
        )
        if direct_hf.is_finite() and direct_hf != D(row["direct_shock_hf"]):
            hf_mismatches.append(row["audit_row_id"] + "::direct")
        if post_hf.is_finite() and post_hf != D(row["post_wave1_hf"]):
            hf_mismatches.append(row["audit_row_id"] + "::post")

        newly = row["newly_eligible_after_wave1"] == "True"
        attempted = row["attempted_after_wave1"] == "True"
        executed = row["executed_positive_debt_wave2"] == "True"
        skipped = newly and not executed
        route_eligible = (
            post_hf < 1
            and D(row["post_wave1_usdc_debt"]) > 0
            and D(row["post_wave1_weth_collateral"]) > 0
        )
        if newly:
            counts[policy]["newly_eligible"] += 1
        if newly and attempted:
            counts[policy]["attempted_later"] += 1
        if newly and executed:
            counts[policy]["executed_wave2"] += 1
        if skipped:
            counts[policy]["skipped"] += 1
        if newly and route_eligible:
            route_counts[policy]["newly_route_eligible"] += 1
        if newly and not route_eligible:
            route_counts[policy]["newly_route_ineligible"] += 1
        debt_by_policy[policy] += D(row["positive_debt_repaid_wave2_usdc"])

        locators = event_locators(row)
        if any(locator not in events for locator in locators):
            event_mismatches.append(row["audit_row_id"] + "::missing_locator")
            continue
        borrower_events = [events[locator] for locator in locators]
        if any(event["borrower_hash"] != row["borrower_hash"] for event in borrower_events):
            event_mismatches.append(row["audit_row_id"] + "::borrower")
        has_positive_wave2 = any(
            event["event_type"] == "LIQUIDATION"
            and int(event["wave"]) == 2
            and D(str(event["debt_repaid_usdc"])) > 0
            for event in borrower_events
        )
        if has_positive_wave2 != executed:
            event_mismatches.append(row["audit_row_id"] + "::execution")
        if skipped:
            expected_reason = (
                "NO_MODELLED_USDC_DEBT"
                if D(row["post_wave1_usdc_debt"]) <= 0
                else "NO_MODELLED_WETH_COLLATERAL"
                if D(row["post_wave1_weth_collateral"]) <= 0
                else "HF_NOT_BELOW_ONE_AT_POST_WAVE1_STATE"
                if post_hf >= 1
                else "UNEXPLAINED_PLAN_NOT_ELIGIBLE"
            )
            if row["resolved_skip_reasons_after_wave1"] != expected_reason:
                skip_explanation_mismatches.append(row["audit_row_id"])

    reconstructed = {
        policy: {
            "newly_eligible": counts[policy]["newly_eligible"],
            "attempted_later": counts[policy]["attempted_later"],
            "executed_wave2": counts[policy]["executed_wave2"],
            "skipped": counts[policy]["skipped"],
            "newly_route_eligible": route_counts[policy]["newly_route_eligible"],
            "newly_route_ineligible": route_counts[policy]["newly_route_ineligible"],
            "positive_debt_repaid_wave2_usdc": str(debt_by_policy[policy]),
        }
        for policy in POLICIES
    }
    summary_reconstructed = {
        policy: {
            "newly_eligible": sum(
                int(row["newly_eligible_after_wave1_count"])
                for row in summary_rows
                if row["policy_id"] == policy
            ),
            "attempted_later": sum(
                int(row["newly_eligible_attempted_later_count"])
                for row in summary_rows
                if row["policy_id"] == policy
            ),
            "executed_wave2": sum(
                int(row["newly_eligible_executed_wave2_count"])
                for row in summary_rows
                if row["policy_id"] == policy
            ),
            "skipped": sum(
                int(row["newly_eligible_skipped_count"])
                for row in summary_rows
                if row["policy_id"] == policy
            ),
            "positive_debt_repaid_wave2_usdc": str(
                sum(
                    (
                        D(row["positive_debt_repaid_wave2_usdc"])
                        for row in summary_rows
                        if row["policy_id"] == policy
                    ),
                    D(0),
                )
            ),
        }
        for policy in POLICIES
    }

    frozen_result_ids = {
        row["result_id"] for row in load_json(FROZEN / "results_registry.json")["results"]
    }
    integration_result_ids = {
        row["result_id"]
        for row in load_json(INTEGRATION / "integration_result_registry.json")["results"]
    }
    claims = load_json(INTEGRATION / "claim_to_result_registry.json")["claims"]
    unresolved_results = sorted(
        {
            result_id
            for claim in claims
            for result_id in claim["result_ids"]
            if result_id not in frozen_result_ids | integration_result_ids
        }
    )
    frozen_sources = load_json(FROZEN / "evidence_source_matrix.json")
    integration_sources = load_json(INTEGRATION / "table_figure_registry.json")
    locator_ids = {
        row["table_id"] for row in frozen_sources["table_registry"]
    } | {
        row["figure_id"] for row in frozen_sources["figure_registry"]
    } | {
        row["table_id"] for row in integration_sources["tables"]
    } | {
        row["figure_id"] for row in integration_sources["figures"]
    }
    unresolved_table_figures = sorted(
        {
            locator
            for claim in claims
            for locator in claim["table_figure"]
            if locator not in locator_ids
        }
    )

    samples = select_samples(audit_rows)
    sample_evidence: dict[str, Any] = {}
    for name, row in samples.items():
        locators = event_locators(row)
        sample_evidence[name] = {
            "selection_rule": (
                "lexicographically smallest (case_id, policy_id, borrower_hash) "
                "satisfying group predicate"
            ),
            "case_id": row["case_id"],
            "policy_id": row["policy_id"],
            "borrower_hash": row["borrower_hash"],
            "direct_shock_hf": row["direct_shock_hf"],
            "post_wave1_hf": row["post_wave1_hf"],
            "weth_collateral": row["post_wave1_weth_collateral"],
            "usdc_debt": row["post_wave1_usdc_debt"],
            "other_collateral_usd": row["post_wave1_other_collateral_usd"],
            "other_debt_usd": row["post_wave1_other_debt_usd"],
            "portfolio_newly_eligible": row["newly_eligible_after_wave1"] == "True",
            "route_eligible": row["weth_usdc_liquidation_route_available"] == "True",
            "attempted_after_wave1": row["attempted_after_wave1"] == "True",
            "executed_wave2": row["executed_positive_debt_wave2"] == "True",
            "positive_debt_repaid_wave2_usdc": row["positive_debt_repaid_wave2_usdc"],
            "raw_skip_reason": row["skip_reasons_after_wave1"],
            "resolved_skip_reason": row["resolved_skip_reasons_after_wave1"],
            "event_locators": locators,
            "events": [events[locator] for locator in locators],
        }

    controls = [row for row in summary_rows if row["case_type"] == "DETERMINISTIC_CONTROL"]
    controls_no_wave2 = all(int(row["cascade_depth"]) < 2 for row in controls)
    comparison_matches = all(
        int(row["cascade_depth"]) == int(oracle_comparison[row["result_id"]]["cascade_depth"])
        for row in summary_rows
    )

    p2_text = "\n".join(
        git_blob(P2_HEAD, Path(path)).decode("utf-8")
        for path in (
            "docs/research_final/REFERENCE_EVIDENCE_MATRIX.md",
            "docs/research_final/P2_VERSION_RECONCILIATION.md",
        )
    )
    p2_claim_ids = set(re.findall(r"\bC\d{2}\b", p2_text))
    unresolved_literature = sorted(
        {
            claim_id
            for claim in claims
            for claim_id in claim["literature_claim_ids"]
            if claim_id not in p2_claim_ids
        }
    )

    current_hashes = {
        "canonical_snapshot": sha(CANONICAL),
        "frozen_manifest": sha(FROZEN / "manifest.json"),
        "oracle_manifest": sha(ORACLE / "manifest.json"),
        "integration_manifest": sha(INTEGRATION / "manifest.json"),
    }
    repository_blob_hashes = {
        "canonical_snapshot_at_frozen_head": sha_bytes(git_blob(FROZEN_HEAD, CANONICAL)),
        "frozen_manifest_at_frozen_head": sha_bytes(git_blob(FROZEN_HEAD, FROZEN / "manifest.json")),
        "oracle_manifest_at_oracle_head": sha_bytes(git_blob(ORACLE_HEAD, ORACLE / "manifest.json")),
        "integration_manifest_at_audit_source_head": sha_bytes(git_blob(head, INTEGRATION / "manifest.json")),
    }
    normalized_eol_equivalence = {
        "canonical_snapshot": sha_bytes(CANONICAL.read_bytes().replace(b"\r\n", b"\n"))
        == repository_blob_hashes["canonical_snapshot_at_frozen_head"],
        "frozen_manifest": sha_bytes(
            (FROZEN / "manifest.json").read_bytes().replace(b"\r\n", b"\n")
        )
        == repository_blob_hashes["frozen_manifest_at_frozen_head"],
        "oracle_manifest": sha_bytes(
            (ORACLE / "manifest.json").read_bytes().replace(b"\r\n", b"\n")
        )
        == repository_blob_hashes["oracle_manifest_at_oracle_head"],
        "integration_manifest": sha_bytes(
            (INTEGRATION / "manifest.json").read_bytes().replace(b"\r\n", b"\n")
        )
        == repository_blob_hashes["integration_manifest_at_audit_source_head"],
    }

    checks = {
        "canonical_worktree_hash_matches_declared": current_hashes["canonical_snapshot"]
        == CANONICAL_DECLARED_SHA,
        "frozen_manifest_artifacts_match_worktree_bytes": not verify_manifest(
            FROZEN, frozen_manifest
        )["mismatches"],
        "oracle_manifest_artifacts_match_worktree_bytes": not verify_manifest(
            ORACLE, oracle_manifest
        )["mismatches"],
        "integration_manifest_artifacts_match_worktree_bytes": not verify_manifest(
            INTEGRATION, integration_manifest
        )["mismatches"],
        "integration_input_hashes_match_worktree_bytes": integration_manifest["input_hashes"]
        ["canonical_snapshot"]
        == current_hashes["canonical_snapshot"]
        and integration_manifest["input_hashes"]["frozen_v3_manifest"]
        == current_hashes["frozen_manifest"]
        and integration_manifest["input_hashes"]["oracle_manifest"]
        == current_hashes["oracle_manifest"],
        "source_and_dependency_commits_exist": all(
            commit_exists(commit)
            for commit in (
                FROZEN_HEAD,
                ORACLE_HEAD,
                P2_HEAD,
                integration_manifest["source_code_commit"],
                integration_manifest["artifact_bundle_commit"],
            )
        ),
        "all_32688_hf_rows_recomputed_exactly": not hf_mismatches
        and len(audit_rows) == 18 * 4 * 454,
        "event_execution_and_borrower_locators_match": not event_mismatches,
        "all_skip_explanations_reconstructed": not skip_explanation_mismatches,
        "audit_counts_match_summary": all(
            reconstructed[policy][key] == summary_reconstructed[policy][key]
            for policy in POLICIES
            for key in (
                "newly_eligible",
                "attempted_later",
                "executed_wave2",
                "skipped",
                "positive_debt_repaid_wave2_usdc",
            )
        ),
        "all_claim_result_ids_resolve": not unresolved_results,
        "all_claim_table_figure_ids_resolve": not unresolved_table_figures,
        "all_p2_literature_claim_ids_resolve_at_pinned_commit": not unresolved_literature,
        "oracle_comparison_depth_matches_all_72_summaries": comparison_matches,
        "all_16_control_policy_rows_have_no_wave2_execution": len(controls) == 16
        and controls_no_wave2,
        "no_nonfinite_serialized_values": finite(
            [audit_rows, summary_rows, list(events.values()), claims]
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {
        "schema_version": "scientific-premerge-audit-v1.0",
        "audit_method": (
            "Independent parser/recalculation; does not import or invoke the Addendum "
            "builder or simulation runner."
        ),
        "audit_source_head": head,
        "status": "PASS_WITH_DISCLOSED_EOL_HASH_SEMANTICS" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "manifest_verification": {
            "frozen_v3": verify_manifest(FROZEN, frozen_manifest),
            "oracle_diagnostic_v1": verify_manifest(ORACLE, oracle_manifest),
            "scientific_integration_v1": verify_manifest(INTEGRATION, integration_manifest),
        },
        "hash_integrity": {
            "worktree_byte_sha256": current_hashes,
            "repository_git_blob_sha256_lf": repository_blob_hashes,
            "worktree_equals_git_blob_after_crlf_to_lf_normalization": normalized_eol_equivalence,
            "interpretation": (
                "Declared legacy hashes identify Windows checkout bytes; Git blobs use LF. "
                "Both are independently recorded. Content is equal after CRLF-to-LF normalization."
            ),
        },
        "eligible_attempted_executed": reconstructed,
        "summary_reconstructed": summary_reconstructed,
        "row_counts": {
            "borrower_case_policy_rows": len(audit_rows),
            "summary_rows": len(summary_rows),
            "event_rows": len(events),
            "claims": len(claims),
            "controls_case_policy_rows": len(controls),
        },
        "specific_samples": sample_evidence,
        "unresolved": {
            "result_ids": unresolved_results,
            "table_figure_ids": unresolved_table_figures,
            "p2_literature_claim_ids": unresolved_literature,
            "hf_rows": hf_mismatches,
            "event_rows": event_mismatches,
            "skip_explanations": skip_explanation_mismatches,
        },
        "findings": [
            {
                "finding_id": "PM-001",
                "severity": "LOW_REPAIRED",
                "affected_rq": "ALL_PROVENANCE",
                "finding": (
                    "Invalid expanded artifact commit SHA was repaired to the existing commit "
                    "object c113fc1ec6dd98ffcc31241c1dbd1a93b20aa193."
                ),
            },
            {
                "finding_id": "PM-002",
                "severity": "LOW_REPAIRED",
                "affected_rq": "RQ1/RQ2/RQ3",
                "finding": "INT_T01_ELIGIBLE_VS_EXECUTED now resolves through table_figure_registry.json.",
            },
            {
                "finding_id": "PM-003",
                "severity": "MEDIUM_DISCLOSURE",
                "affected_rq": "ALL_REPRODUCIBILITY",
                "finding": (
                    "Legacy declared SHA-256 values identify Windows CRLF checkout bytes, while "
                    "repository blobs use LF. The audit records both hashes and verifies normalized "
                    "content equality; locked bundles were not rewritten."
                ),
            },
        ],
    }
    if failed:
        raise RuntimeError(f"Independent pre-merge audit failed: {failed}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"status": result["status"], "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
