"""Deterministic P04-02 saved-metadata smoke and evidence report CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from defistress_v2.contracts import canonical_json_bytes
from defistress_v2.terra_pit.loader import (
    P04_01_PIT_MANIFEST,
    P04_01_REGISTRY,
    P04_01_SOURCE_COMMIT,
    MetadataPin,
    load_saved_terra_audit_metadata,
)
from defistress_v2.terra_pit.temporal import TERRA_PIT_SCHEMA_VERSION

REGISTRY_GIT_SHA256 = "09302fa53609651c61488c622862e6e1b3ea74747cc6e3cc2366cbbdd3e218f5"
PIT_MANIFEST_GIT_SHA256 = "90604d78d158d493bf00eed8be7fecde145bec6e14f3b6a6d472ba50b9b1ff29"
SCIENTIFIC_STATUS = "GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED"


def validate(repository_root: Path, implementation_commit: str) -> dict[str, object]:
    """Validate only registered metadata bytes; historical rows never enter temporal functions."""

    metadata = load_saved_terra_audit_metadata(
        repository_root,
        MetadataPin(P04_01_REGISTRY, REGISTRY_GIT_SHA256),
        MetadataPin(P04_01_PIT_MANIFEST, PIT_MANIFEST_GIT_SHA256),
    )
    content_payload = {
        "cleared_predictive_fields": str(metadata.cleared_predictive_fields),
        "field_count": str(metadata.field_count),
        "gate_statuses": metadata.gate_statuses,
        "point_in_time_status": metadata.point_in_time_status,
        "source_commit": metadata.source_commit,
        "verified_input_count": str(metadata.verified_input_count),
    }
    content_hash = hashlib.sha256(
        canonical_json_bytes(content_payload, schema_version=TERRA_PIT_SCHEMA_VERSION)
    ).hexdigest()
    return {
        "schema": "defistress-terra-p04-02-validation/1",
        "implementation_commit": implementation_commit,
        "p04_01_source_commit": P04_01_SOURCE_COMMIT,
        "scope": "SAVED_METADATA_AUDIT_AND_SYNTHETIC_PIT_CONTRACTS_ONLY",
        "status": "PASS",
        "source_integrity": {
            "registry_raw_git_bytes_sha256": metadata.registry_raw_sha256,
            "pit_manifest_raw_git_bytes_sha256": metadata.pit_manifest_raw_sha256,
            "decoded_content_sha256": content_hash,
            "hash_domains_distinct": True,
        },
        "coverage": {
            "verified_saved_inputs": metadata.verified_input_count,
            "registered_historical_fields": metadata.field_count,
            "cleared_historical_predictive_fields": metadata.cleared_predictive_fields,
            "terra_acceptance_statuses": len(metadata.gate_statuses),
        },
        "terra_acceptance_statuses": dict(metadata.gate_statuses),
        "point_in_time_eligibility": metadata.point_in_time_status,
        "historical_signal_generation_executed": False,
        "historical_backtest_executed": False,
        "exit_simulation_executed": False,
        "risk_score_status": "NOT_IMPLEMENTED",
        "scientific_status": SCIENTIFIC_STATUS,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = validate(args.repository_root, args.implementation_commit)
        exit_code = 0
    except Exception as exc:  # failure evidence must survive validation failures
        report = {
            "schema": "defistress-terra-p04-02-validation/1",
            "implementation_commit": args.implementation_commit,
            "p04_01_source_commit": P04_01_SOURCE_COMMIT,
            "scope": "SAVED_METADATA_AUDIT_AND_SYNTHETIC_PIT_CONTRACTS_ONLY",
            "status": "FAIL",
            "failure_type": type(exc).__name__,
            "failure_reason": str(exc),
            "point_in_time_eligibility": "BLOCKED_NOT_CLEARED_FOR_FORECAST",
            "historical_backtest_executed": False,
            "scientific_status": SCIENTIFIC_STATUS,
        }
        exit_code = 1
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        print(json.dumps({"status": "REPORT_WRITE_FAILED", "reason": str(exc)}, sort_keys=True))
        return 2
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
