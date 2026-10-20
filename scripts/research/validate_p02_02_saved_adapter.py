"""Run the registered offline smoke and emit deterministic P02-02 evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from defistress_v2.contracts.canonical import canonical_json_bytes
from defistress_v2.contracts.state import Ok
from defistress_v2.state import SnapshotSelection, load_registered_snapshot

BLOCKS = (26045352, 26038152, 26030952)
ALL_TEST_IDS = tuple(
    [f"P02-T01-{number:02d}" for number in range(1, 9)]
    + [f"P02-T02-{number:02d}" for number in range(1, 10)]
    + [f"P02-T03-{number:02d}" for number in range(1, 11)]
    + [f"P02-T04-{number:02d}" for number in range(1, 11)]
    + [f"P02-T05-{number:02d}" for number in range(1, 10)]
)


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None  # Missing controls already produce explicit failed snapshot rows.


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--adapter-source-commit")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    adapter_source_commit = args.adapter_source_commit or args.source_commit
    rows: list[dict[str, object]] = []
    failures = 0
    for block in BLOCKS:
        for read_pass in (1, 2):
            result = load_registered_snapshot(
                args.repository_root,
                SnapshotSelection(block, read_pass),
                args.source_commit,
                adapter_source_commit,
            )
            if not isinstance(result, Ok):
                failures += 1
                rows.append(
                    {
                        "block_number": block,
                        "read_pass": read_pass,
                        "status": result.status.value,
                        "code": result.code,
                        "reason": result.reason,
                        "component_count": 0,
                    }
                )
                continue
            snapshot = result.payload
            rows.append(
                {
                    "block_hash": snapshot.block_ref.hash,
                    "block_number": block,
                    "component_count": len(snapshot.components),
                    "component_ids": [item.component_id for item in snapshot.components],
                    "content_sha256": snapshot.content_sha256.value,
                    "read_pass": read_pass,
                    "status": "PASS",
                    "components": [
                        {
                            "id": item.component_id,
                            "coverage": item.coverage.value,
                            "origin": item.origin.value,
                            "capabilities": list(item.capabilities),
                            "source_status": item.source_declared_status,
                            "raw_sha256": item.evidence.raw_sha256.value,
                            "decoded_sha256": item.evidence.decoded_sha256.value
                            if item.evidence.decoded_sha256
                            else None,
                            "git_blob_sha1": item.evidence.git_blob_sha1.value if item.evidence.git_blob_sha1 else None,
                            "available_time_precision": item.available_time_precision.value,
                            "quarantines": len(item.quarantines),
                            "field_availability": json.loads(canonical_json_bytes(item.field_availability)),
                            "measurement": (
                                {
                                    "tick_records": len(item.payload["ticks"]),
                                    "lower_tick": item.payload["required_lower_tick"],
                                    "upper_tick": item.payload["required_upper_tick"],
                                }
                                if item.kind.value == "POOL"
                                else {
                                    "selected_portfolios": len(item.payload["portfolios"]),
                                    "source_declared_reserves_count": item.payload["reserves_count"],
                                }
                                if item.kind.value == "BORROWERS"
                                else {"assets": len(item.payload["assets"])}
                            ),
                        }
                        for item in snapshot.components
                    ],
                }
            )
    implemented = {
        "P02-T01-01": "IMPLEMENTED_ADAPTER_POSITIVE_AND_BOUNDARY",
        "P02-T01-02": "IMPLEMENTED_INTEGRATION_IDENTITY_GUARDS",
        "P02-T01-03": "IMPLEMENTED_INTEGRATION_NUMERIC_SCHEMA_GUARDS",
        "P02-T01-04": "IMPLEMENTED_INTEGRATION_NO_FILL_SEMANTICS",
        "P02-T01-05": "IMPLEMENTED_INTEGRATION_RAW_DECODED_GIT_HASH_DOMAINS",
        "P02-T01-06": "IMPLEMENTED_INTEGRATION_SAME_BLOCK_NO_LOOKAHEAD_GUARDS",
        "P02-T01-07": "IMPLEMENTED_ADAPTER_COVERAGE_AND_CAPABILITY",
        "P02-T01-08": "IMPLEMENTED_INTEGRATION_ORIGIN_AND_NOT_REPLAYABLE_GUARDS",
    }
    dispositions = [
        {
            "disposition": "PARTIAL_SAVED_ADAPTER_SCOPE"
            if test_id in implemented
            else "NOT_IMPLEMENTED_OUTSIDE_P02_02_AUTHORIZATION",
            "implemented_facets": implemented.get(test_id, "NONE"),
            "remaining": (
                "Registered saved schema only; no generic acquisition/partial loader/"
                "native profile or execution validation"
            )
            if test_id in implemented
            else "Future module outside P02-02",
            "test_id": test_id,
        }
        for test_id in ALL_TEST_IDS
    ]
    root = args.repository_root
    report = {
        "overall_status": ("FAIL" if any(row["status"] == "REJECTED" for row in rows) else "BLOCKED")
        if failures
        else "PASS",
        "failed_or_blocked_snapshot_views": failures,
        "adapter_scope": "READ_ONLY_REGISTERED_SAVED_HISTORICAL_STATE",
        "adapter_source_commit": adapter_source_commit,
        "artifact_git_ref": args.source_commit,
        "commit_identity_verification": "CALLER_DECLARED;PAIR_WITH_CI_CHECKOUT_TREE_AND_CODE_BYTE_HASHES",
        "adapter_code_sha256": {
            path: _sha256(args.repository_root / path)
            for path in (
                "defistress_v2/contracts/snapshot.py",
                "defistress_v2/state/saved_adapter.py",
                "defistress_v2/state/source_validation.py",
                "scripts/research/validate_p02_02_saved_adapter.py",
            )
        },
        "coverage": {
            "blocks": len(BLOCKS),
            "component_views": sum(int(row["component_count"]) for row in rows),
            "read_passes_per_block": 2,
            "snapshot_views": len(rows),
        },
        "input_hashes": {
            "borrower_repair_catalog_sha256_checkout_bytes": _sha256(
                root / "docs/research_v2/phase01b/evidence/borrower_repair/borrower_repair_catalog.json"
            ),
            "evidence_provenance_sha256_checkout_bytes": _sha256(
                root / "docs/research_v2/phase01b/EVIDENCE_PROVENANCE.json"
            ),
            "full_catalog_sha256_checkout_bytes": _sha256(
                root / "docs/research_v2/phase01b/evidence/full/validation_catalog.json"
            ),
        },
        "limitations": [
            "REGISTERED_THREE_BLOCK_TWO_PASS_SAMPLE_ONLY",
            "POOL_TICKS_REGISTERED_BAND_ONLY",
            "BORROWERS_SELECTED_REPAIR_SAMPLE_NOT_MARKET_COVERAGE",
            "SOURCE_HEALTH_FACTOR_RETAINED_NOT_RECOMPUTED",
            "NO_EXECUTION_OR_SIMULATION_AUTHORIZED",
        ],
        "network_calls": 0,
        "origin_classes_used_in_successful_snapshots": [
            "OBSERVED_IDENTITY_AND_RAW_FIELDS",
            "RECONSTRUCTED_ASSEMBLED_VIEW_AND_SOURCE_DERIVATIONS",
        ],
        "scientific_status": ("GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED"),
        "snapshots": rows,
        "test_spec_dispositions": dispositions,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return (1 if report["overall_status"] == "FAIL" else 2) if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
