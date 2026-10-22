"""Bounded, read-only loading of saved P04-01 metadata (never historical feature rows)."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from defistress_v2.contracts.errors import TypeContractError

P04_01_SOURCE_COMMIT = "9207ead7db3acf1332b34cebcd19981c2f7bd9cc"
P04_01_REGISTRY = "docs/research_v2/terra_early_warning/p04_01/P04_01_DATASET_REGISTRY.json"
P04_01_PIT_MANIFEST = "docs/research_v2/terra_early_warning/p04_01/P04_01_POINT_IN_TIME_MANIFEST.json"
MAX_METADATA_FILE_BYTES = 2_000_000
MAX_METADATA_PACK_BYTES = 4_000_000
MAX_JSON_DEPTH = 64
MAX_JSON_ITEMS = 20_000
EXPECTED_FIELD_NAMES = (
    "timestamp",
    "block_height",
    "ust_price",
    "luna_price",
    "ust_supply",
    "luna_supply",
    "anchor_total_deposits",
    "anchor_deposit_flow",
    "anchor_withdrawal_flow",
    "ust_native_redemption_volume",
    "gross_luna_issuance_from_native_swaps",
    "backing_ratio",
    "top10_anchor_share",
    "top100_anchor_share",
)
EXPECTED_GATE_STATUSES = {
    "BACKTEST_PROTOCOL_APPROVED": "NOT_APPROVED_PROPOSAL_ONLY",
    "DATA_AUDITED": "SCOPED_PASS_35_BYTES_304_PATHS",
    "EXIT_FEASIBILITY_EVALUATED": "NOT_EXECUTED_NOT_VERIFIABLE_CURRENT_DEPTH_INPUTS",
    "FALSE_ALARM_RISK_EVALUATED": "NOT_EVALUATED_IN_NEW_PROGRAM",
    "HISTORICAL_BACKTEST_EXECUTED": "NOT_EXECUTED",
    "INDEPENDENTLY_REVIEWED": "NOT_REVIEWED_WORK_SELF_AUDIT_ONLY",
    "MODEL_IMPLEMENTED": "V2_NOT_IMPLEMENTED_V1_CODE_EXISTS",
    "POINT_IN_TIME_ELIGIBLE": "BLOCKED_AVAILABILITY_AND_INTERVAL_TIMING",
    "PRE_EVENT_ALERT_DEMONSTRATED": "NOT_DEMONSTRATED_IN_NEW_PROGRAM",
}
EXPECTED_GATE_STATUSES_TUPLE = tuple(sorted(EXPECTED_GATE_STATUSES.items()))
_SHA256 = re.compile(r"[0-9a-f]{64}")
_SHA1 = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True, slots=True)
class MetadataPin:
    relative_path: str
    sha256_git_bytes: str

    def __post_init__(self) -> None:
        if type(self.relative_path) is not str or not self.relative_path:
            raise TypeContractError("metadata pin path must be nonempty")
        if type(self.sha256_git_bytes) is not str or _SHA256.fullmatch(self.sha256_git_bytes) is None:
            raise TypeContractError("metadata pin SHA-256 must be lowercase hexadecimal")


@dataclass(frozen=True, slots=True)
class SavedTerraAuditMetadata:
    source_commit: str
    verified_input_count: int
    field_count: int
    cleared_predictive_fields: int
    point_in_time_status: str
    gate_statuses: tuple[tuple[str, str], ...]
    registry_raw_sha256: str
    pit_manifest_raw_sha256: str

    def __post_init__(self) -> None:
        if self.source_commit != P04_01_SOURCE_COMMIT:
            raise TypeContractError("saved metadata source commit is not the registered P04-01 anchor")
        if self.verified_input_count != 35:
            raise TypeContractError("P04-01 metadata must retain exactly 35 verified inputs")
        if self.cleared_predictive_fields != 0 or self.point_in_time_status != "BLOCKED_NOT_CLEARED_FOR_FORECAST":
            raise TypeContractError("saved historical fields must remain blocked")
        if self.field_count != len(EXPECTED_FIELD_NAMES):
            raise TypeContractError("P04-01 metadata field inventory changed")
        if self.gate_statuses != EXPECTED_GATE_STATUSES_TUPLE:
            raise TypeContractError("Terra acceptance gate identities or statuses changed")


def _safe_path(root: Path, relative: str) -> Path:
    if type(relative) is not str or not relative or "\\" in relative:
        raise TypeContractError("metadata path must be a nonempty POSIX relative path")
    pure = PurePosixPath(relative)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise TypeContractError("metadata path escapes its repository root")
    root_real = root.resolve(strict=True)
    candidate = root_real.joinpath(*pure.parts)
    try:
        candidate_real = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise TypeContractError("metadata path is missing or unresolvable") from exc
    if os.path.commonpath((str(root_real), str(candidate_real))) != str(root_real):
        raise TypeContractError("metadata path resolves outside repository root")
    cursor = root_real
    for part in pure.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise TypeContractError("metadata path traverses a symlink")
    if not candidate_real.is_file():
        raise TypeContractError("metadata path is not a regular file")
    return candidate_real


def _bounded_bytes(path: Path, maximum: int = MAX_METADATA_FILE_BYTES) -> bytes:
    if type(maximum) is not int or maximum < 0:
        raise TypeContractError("metadata byte bound must be a nonnegative integer")
    before = path.stat()
    size = before.st_size
    if type(size) is not int or size < 0 or size > maximum:
        raise TypeContractError("metadata file exceeds its byte bound")
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    after = path.stat()
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if identity_before != identity_after:
        raise TypeContractError("metadata file changed during bounded read")
    if len(data) > maximum:
        raise TypeContractError("metadata file exceeds its byte bound")
    if len(data) != size:
        raise TypeContractError("metadata file changed during bounded read")
    return data


def _strict_json(raw: bytes) -> object:
    def pairs(pairs_value: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs_value:
            if key in result:
                raise TypeContractError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject(value: str) -> object:
        raise TypeContractError(f"unsupported JSON number: {value}")

    try:
        result = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs, parse_constant=reject)
    except TypeContractError:
        raise
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise TypeContractError("metadata is not strict UTF-8 JSON") from exc
    count = 0

    def walk(value: object, depth: int) -> None:
        nonlocal count
        if depth > MAX_JSON_DEPTH:
            raise TypeContractError("metadata JSON exceeds depth bound")
        count += 1
        if count > MAX_JSON_ITEMS:
            raise TypeContractError("metadata JSON exceeds item bound")
        if isinstance(value, dict):
            for child in value.values():
                walk(child, depth + 1)
        elif isinstance(value, list):
            for child in value:
                walk(child, depth + 1)

    walk(result, 0)
    return result


def _read_pinned(root: Path, pin: MetadataPin) -> tuple[dict[str, Any], str]:
    path = _safe_path(root, pin.relative_path)
    raw = _bounded_bytes(path)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != pin.sha256_git_bytes:
        raise TypeContractError(f"raw Git-byte SHA-256 mismatch for {pin.relative_path}")
    parsed = _strict_json(raw)
    if not isinstance(parsed, dict):
        raise TypeContractError("metadata root must be a JSON object")
    return parsed, digest


def load_saved_terra_audit_metadata(
    root: Path, registry_pin: MetadataPin, pit_pin: MetadataPin
) -> SavedTerraAuditMetadata:
    if not isinstance(root, Path):
        raise TypeContractError("repository root must be pathlib.Path")
    sizes = []
    for pin in (registry_pin, pit_pin):
        sizes.append(_safe_path(root, pin.relative_path).stat().st_size)
    if sum(sizes) > MAX_METADATA_PACK_BYTES:
        raise TypeContractError("metadata pack exceeds aggregate byte bound")
    registry, registry_hash = _read_pinned(root, registry_pin)
    pit, pit_hash = _read_pinned(root, pit_pin)
    if registry.get("schema") != "defistress-terra-p04-01-source-audit/1":
        raise TypeContractError("unsupported P04-01 registry schema")
    if pit.get("schema") != "defistress-terra-pit-admission/1":
        raise TypeContractError("unsupported P04-01 PIT schema")
    if registry.get("source_commit") != P04_01_SOURCE_COMMIT or pit.get("source_commit") != P04_01_SOURCE_COMMIT:
        raise TypeContractError("P04-01 metadata source commit mismatch")
    verified = registry.get("verified_inputs")
    fields = pit.get("field_admission")
    if not isinstance(verified, list) or not isinstance(fields, list):
        raise TypeContractError("P04-01 metadata lists are missing")
    paths: list[str] = []
    for row in verified:
        if not isinstance(row, dict):
            raise TypeContractError("P04-01 verified input record is malformed")
        path = row.get("path")
        size_bytes = row.get("size_bytes")
        sha256 = row.get("sha256_git_bytes")
        blob_sha1 = row.get("git_blob_sha1")
        if (
            type(path) is not str
            or not path
            or type(size_bytes) is not int
            or size_bytes < 0
            or type(sha256) is not str
            or _SHA256.fullmatch(sha256) is None
            or type(blob_sha1) is not str
            or _SHA1.fullmatch(blob_sha1) is None
            or row.get("status") != "FULL_BYTES_VERIFIED"
        ):
            raise TypeContractError("P04-01 verified input identity or integrity metadata is malformed")
        paths.append(path)
    if len(paths) != len(set(paths)):
        raise TypeContractError("P04-01 verified input paths are malformed or duplicated")
    field_names: list[str] = []
    for row in fields:
        if not isinstance(row, dict) or type(row.get("field")) is not str:
            raise TypeContractError("P04-01 field admission record is malformed")
        field_names.append(row["field"])
        if row.get("approved_forecast_use") is not False:
            raise TypeContractError("historical field was unexpectedly promoted")
        if not str(row.get("point_in_time_status", "")).startswith("BLOCKED_"):
            raise TypeContractError("historical field lacks a blocked PIT status")
    if tuple(field_names) != EXPECTED_FIELD_NAMES:
        raise TypeContractError("P04-01 field admission identities or order changed")
    cleared = pit.get("cleared_predictive_fields")
    status = pit.get("status")
    gates = pit.get("gates")
    if type(cleared) is not int or type(status) is not str or not isinstance(gates, dict):
        raise TypeContractError("P04-01 PIT summary fields have invalid types")
    gate_statuses = tuple(sorted(gates.items()))
    if gate_statuses != EXPECTED_GATE_STATUSES_TUPLE:
        raise TypeContractError("P04-01 gate identities or statuses changed")
    return SavedTerraAuditMetadata(
        source_commit=P04_01_SOURCE_COMMIT,
        verified_input_count=len(verified),
        field_count=len(fields),
        cleared_predictive_fields=cleared,
        point_in_time_status=status,
        gate_statuses=gate_statuses,
        registry_raw_sha256=registry_hash,
        pit_manifest_raw_sha256=pit_hash,
    )
