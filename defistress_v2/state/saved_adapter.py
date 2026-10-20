"""Bounded, offline-only adapter for registered Phase 01-B saved state."""

from __future__ import annotations

import hashlib
import json
import re
import zlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from defistress_v2.contracts.canonical import ExplicitBool, FrozenMap
from defistress_v2.contracts.errors import ContractError, DigestMismatchError, TypeContractError
from defistress_v2.contracts.evidence import (
    ArtifactBytesSha256,
    DecodedBytesSha256,
    DeterministicContentSha256,
    EvidenceRef,
    GitBlobSha1,
    OriginKind,
    SourceKind,
)
from defistress_v2.contracts.identity import BlockRef
from defistress_v2.contracts.snapshot import (
    ComponentKind,
    ComponentSnapshot,
    CoverageStatus,
    HistoricalSnapshot,
    SnapshotProvenance,
    TimePrecision,
)
from defistress_v2.contracts.state import Blocked, Ok, Rejected

_COMMIT = re.compile(r"[0-9a-f]{40}")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_ADDRESS = re.compile(r"0x[0-9a-fA-F]{40}")
_POOLS = {
    "P3000": "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8",
    "P500": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
}
_USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
_WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
_AAVE_POOL = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"


@dataclass(frozen=True, slots=True)
class ResourceLimits:
    max_input_bytes: int = 8 * 1024 * 1024
    max_decoded_bytes: int = 64 * 1024 * 1024
    max_decoded_pack_bytes: int = 256 * 1024 * 1024
    max_json_depth: int = 128
    max_manifest_entries: int = 512
    max_ticks_per_pool: int = 10_000
    max_portfolios: int = 64
    max_reserves_per_portfolio: int = 128
    max_discovery_headers: int = 2_048


DEFAULT_LIMITS = ResourceLimits()


@dataclass(frozen=True, slots=True)
class SnapshotSelection:
    block_number: int
    read_pass: int
    pool_ids: tuple[str, ...] = ("P3000", "P500")
    require_complete: bool = True

    def __post_init__(self) -> None:
        if type(self.block_number) is not int or self.block_number < 0:
            raise TypeContractError("block_number must be a nonnegative exact integer")
        if self.read_pass not in (1, 2):
            raise TypeContractError("read_pass must be 1 or 2")
        if type(self.pool_ids) is not tuple or not self.pool_ids or len(set(self.pool_ids)) != len(self.pool_ids):
            raise TypeContractError("pool_ids must be a nonempty unique tuple")
        if any(item not in {"P3000", "P500"} for item in self.pool_ids):
            raise TypeContractError("only registered pool identifiers may be selected")
        if type(self.require_complete) is not bool:
            raise TypeContractError("require_complete must be bool")

    def to_canonical(self) -> object:
        return {
            "block_number": str(self.block_number),
            "pool_ids": self.pool_ids,
            "read_pass": str(self.read_pass),
            "require_complete": ExplicitBool(self.require_complete),
        }


@dataclass(frozen=True, slots=True)
class ManifestEntry:
    path: str
    raw_sha256: str
    raw_size: int
    decoded_sha256: str
    decoded_size: int

    def to_canonical(self) -> object:
        return {
            "decoded_sha256": self.decoded_sha256,
            "decoded_size": str(self.decoded_size),
            "path": self.path,
            "raw_sha256": self.raw_sha256,
            "raw_size": str(self.raw_size),
        }


@dataclass(frozen=True, slots=True)
class SavedPack:
    name: str
    root: str
    source_commit: str
    collected_at_s: int
    entries: tuple[ManifestEntry, ...]
    catalog: FrozenMap

    def to_canonical(self) -> object:
        return {
            "catalog": self.catalog,
            "collected_at_s": str(self.collected_at_s),
            "entries": self.entries,
            "name": self.name,
            "root": self.root,
            "source_commit": self.source_commit,
        }


@dataclass(frozen=True, slots=True)
class SavedPackManifest:
    repository_root: str
    artifact_git_ref: str
    full: SavedPack
    borrower_repair: SavedPack

    def to_canonical(self) -> object:
        return {
            "artifact_git_ref": self.artifact_git_ref,
            "borrower_repair": self.borrower_repair,
            "full": self.full,
            "repository_root": self.repository_root,
        }


def _strict_json(raw: bytes, limits: ResourceLimits) -> object:
    def pairs(pairs_value: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs_value:
            if key in result:
                raise TypeContractError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_float(value: str) -> object:
        raise TypeContractError(f"floating/non-finite JSON number is forbidden: {value}")

    try:
        value = json.loads(
            raw.decode("utf-8", errors="strict"),
            object_pairs_hook=pairs,
            parse_float=reject_float,
            parse_constant=reject_float,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise TypeContractError("saved input is not strict UTF-8 JSON") from exc

    stack: list[tuple[object, int]] = [(value, 1)]
    while stack:
        node, depth = stack.pop()
        if depth > limits.max_json_depth:
            raise TypeContractError("saved JSON exceeds the depth limit")
        if isinstance(node, dict):
            stack.extend((item, depth + 1) for item in node.values())
        elif isinstance(node, list):
            stack.extend((item, depth + 1) for item in node)
    return value


def _safe_path(root: Path, relative: str) -> Path:
    logical = PurePosixPath(relative)
    if logical.is_absolute() or ".." in logical.parts or "\\" in relative:
        raise TypeContractError("unsafe saved-artifact path")
    resolved_root = root.resolve(strict=True)
    candidate = root.joinpath(*logical.parts)
    cursor = resolved_root
    for part in logical.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise TypeContractError("saved-artifact path traverses a symbolic link")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(resolved_root):
        raise TypeContractError("saved-artifact path escapes its pack root")
    return resolved


def _bounded_read(path: Path, maximum: int) -> bytes:
    size = path.stat().st_size
    if size > maximum:
        raise TypeContractError("saved artifact exceeds the compressed/input size limit")
    with path.open("rb") as handle:
        raw = handle.read(maximum + 1)
    if len(raw) != size or len(raw) > maximum:
        raise TypeContractError("saved artifact changed during bounded read or exceeded its limit")
    return raw


def _bounded_gzip(raw: bytes, maximum: int) -> bytes:
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    output = bytearray()
    for offset in range(0, len(raw), 64 * 1024):
        output.extend(decoder.decompress(raw[offset : offset + 64 * 1024], maximum + 1 - len(output)))
        if len(output) > maximum or decoder.unconsumed_tail:
            raise TypeContractError("decoded artifact exceeds its size limit")
    output.extend(decoder.flush(maximum + 1 - len(output)))
    if len(output) > maximum:
        raise TypeContractError("decoded artifact exceeds its size limit")
    if not decoder.eof or decoder.unused_data:
        raise TypeContractError("gzip must contain exactly one complete member and no trailing bytes")
    return bytes(output)


def _freeze_source(value: object) -> object:
    if value is None or type(value) is str:
        return value
    if type(value) is bool:
        return ExplicitBool(value)
    if type(value) is int:
        return str(value)
    if isinstance(value, list):
        return tuple(_freeze_source(item) for item in value)
    if isinstance(value, dict):
        return FrozenMap.from_mapping({key: _freeze_source(item) for key, item in value.items()})
    raise TypeContractError(f"unsupported source JSON type: {type(value).__name__}")


def _dict(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeContractError(f"{label} must be a JSON object")
    return value


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise TypeContractError(f"{label} must be a JSON array")
    return value


def _exact_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise TypeContractError(f"{label} must be an exact JSON integer")
    return value


def _parse_time(text: object) -> int:
    if type(text) is not str:
        raise TypeContractError("collected_at_utc must be an ISO timestamp")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise TypeContractError("collected_at_utc is invalid") from exc
    if parsed.tzinfo is None:
        raise TypeContractError("collected_at_utc must include a timezone")
    return int(parsed.timestamp())


def _manifest_entries(document: dict[str, Any], limits: ResourceLimits) -> tuple[ManifestEntry, ...]:
    rows = _list(document.get("files"), "manifest files")
    if len(rows) > limits.max_manifest_entries:
        raise TypeContractError("manifest exceeds its entry limit")
    entries: list[ManifestEntry] = []
    for row_value in rows:
        row = _dict(row_value, "manifest entry")
        path = row.get("path")
        raw_hash = row.get("sha256")
        decoded_hash = row.get("uncompressed_sha256", raw_hash)
        if type(path) is not str or type(raw_hash) is not str or type(decoded_hash) is not str:
            raise TypeContractError("manifest entry lacks typed path or hashes")
        if _SHA256.fullmatch(raw_hash) is None or _SHA256.fullmatch(decoded_hash) is None:
            raise TypeContractError("manifest entry has an invalid SHA-256")
        entries.append(
            ManifestEntry(
                path,
                raw_hash,
                _exact_int(row.get("size_bytes"), "size_bytes"),
                decoded_hash,
                _exact_int(row.get("uncompressed_size", row.get("size_bytes")), "uncompressed_size"),
            )
        )
    if len({entry.path for entry in entries}) != len(entries):
        raise TypeContractError("manifest contains duplicate paths")
    return tuple(sorted(entries, key=lambda item: item.path))


def _load_json_file(root: Path, relative: str, limits: ResourceLimits) -> tuple[bytes, object]:
    raw = _bounded_read(_safe_path(root, relative), limits.max_input_bytes)
    return raw, _strict_json(raw, limits)


def _verify_registered_bytes(provenance: dict[str, Any], relative: str, raw: bytes) -> None:
    rows = _list(provenance.get("files"), "evidence provenance files")
    matches = [row for row in rows if isinstance(row, dict) and row.get("path") == relative]
    if len(matches) != 1:
        raise TypeContractError("control file is not uniquely pinned by EVIDENCE_PROVENANCE")
    row = matches[0]
    normalized = raw.replace(b"\r\n", b"\n")
    raw_matches = row.get("size_bytes") == len(raw) and row.get("sha256") == hashlib.sha256(raw).hexdigest()
    lf_matches = (
        row.get("size_bytes") == len(normalized)
        and row.get("sha256") == hashlib.sha256(normalized).hexdigest()
    )
    if not raw_matches and not lf_matches:
        raise DigestMismatchError("control file bytes differ from EVIDENCE_PROVENANCE")


def _load_pack(
    repo_root: Path,
    relative: str,
    catalog_name: str,
    name: str,
    limits: ResourceLimits,
    provenance: dict[str, Any],
) -> SavedPack:
    pack_root = _safe_path(repo_root, relative)
    if not pack_root.is_dir():
        raise TypeContractError("saved pack root must be a directory")
    manifest_raw, manifest_value = _load_json_file(pack_root, "collection_manifest.json", limits)
    catalog_raw, catalog_value = _load_json_file(pack_root, catalog_name, limits)
    provenance_prefix = relative.removeprefix("docs/research_v2/phase01b/")
    _verify_registered_bytes(provenance, f"{provenance_prefix}/collection_manifest.json", manifest_raw)
    _verify_registered_bytes(provenance, f"{provenance_prefix}/{catalog_name}", catalog_raw)
    manifest = _dict(manifest_value, "collection manifest")
    commit = manifest.get("source_commit")
    if type(commit) is not str or _COMMIT.fullmatch(commit) is None:
        raise TypeContractError("pack source_commit must be a full Git SHA")
    catalog = _freeze_source(catalog_value)
    if type(catalog) is not tuple:
        raise TypeContractError("catalog must be a JSON array")
    return SavedPack(
        name=name,
        root=relative,
        source_commit=commit,
        collected_at_s=_parse_time(manifest.get("collected_at_utc")),
        entries=_manifest_entries(manifest, limits),
        catalog=FrozenMap.from_mapping({"records": catalog}),
    )


def load_registered_manifest(
    repository_root: Path, artifact_git_ref: str, limits: ResourceLimits = DEFAULT_LIMITS
) -> Ok[SavedPackManifest] | Rejected:
    """Load the two explicitly registered packs; never discovers/falls back to another source."""

    synthetic = EvidenceRef.synthetic("p02-02-manifest-loader", b"registered pack manifest")
    try:
        if _COMMIT.fullmatch(artifact_git_ref) is None:
            raise TypeContractError("artifact_git_ref must be a full Git commit")
        root = repository_root.resolve(strict=True)
        provenance_raw, provenance_value = _load_json_file(
            root, "docs/research_v2/phase01b/EVIDENCE_PROVENANCE.json", limits
        )
        if not provenance_raw:
            raise TypeContractError("evidence provenance file is empty")
        provenance = _dict(provenance_value, "evidence provenance")
        full = _load_pack(
            root,
            "docs/research_v2/phase01b/evidence/full",
            "validation_catalog.json",
            "full",
            limits,
            provenance,
        )
        repair = _load_pack(
            root,
            "docs/research_v2/phase01b/evidence/borrower_repair",
            "borrower_repair_catalog.json",
            "borrower_repair",
            limits,
            provenance,
        )
        return Ok(SavedPackManifest(str(root), artifact_git_ref, full, repair))
    except (OSError, ContractError) as exc:
        return Rejected("SAVED_MANIFEST_REJECTED", str(exc), (synthetic,))


def _thaw_catalog(pack: SavedPack) -> list[dict[str, Any]]:
    def thaw(value: object) -> object:
        if isinstance(value, FrozenMap):
            return {key: thaw(item) for key, item in value.items()}
        if isinstance(value, tuple):
            return [thaw(item) for item in value]
        if isinstance(value, ExplicitBool):
            return value.value
        if type(value) is str and re.fullmatch(r"0|[1-9][0-9]*", value):
            return int(value)
        return value

    result = thaw(pack.catalog["records"])
    assert isinstance(result, list)
    return result


def _select_catalog(pack: SavedPack, block_number: int, read_pass: int) -> tuple[dict[str, Any], dict[str, Any]]:
    matches = [row for row in _thaw_catalog(pack) if row.get("block", {}).get("number") == block_number]
    if len(matches) != 1:
        raise TypeContractError(f"{pack.name} catalog does not contain exactly one selected block")
    block = _dict(matches[0].get("block"), "catalog block")
    passes = _list(matches[0].get("passes"), "catalog passes")
    if len(passes) != 2:
        raise TypeContractError("catalog must contain exactly two read passes")
    return block, _dict(passes[read_pass - 1], "catalog pass")


def _entry(pack: SavedPack, relative: str) -> ManifestEntry:
    matches = [item for item in pack.entries if item.path == relative]
    if len(matches) != 1:
        raise TypeContractError("selected component is missing or duplicated in its manifest")
    return matches[0]


def _load_component(
    repo_root: Path,
    pack: SavedPack,
    relative: str,
    limits: ResourceLimits,
) -> tuple[bytes, bytes, dict[str, Any], ManifestEntry, Path]:
    entry = _entry(pack, relative)
    if entry.raw_size > limits.max_input_bytes or entry.decoded_size > limits.max_decoded_bytes:
        raise TypeContractError("manifest-declared component size exceeds resource limits")
    pack_root = _safe_path(repo_root, pack.root)
    path = _safe_path(pack_root, relative)
    raw = _bounded_read(path, limits.max_input_bytes)
    if len(raw) != entry.raw_size or hashlib.sha256(raw).hexdigest() != entry.raw_sha256:
        raise DigestMismatchError("component raw bytes do not match manifest")
    decoded = _bounded_gzip(raw, limits.max_decoded_bytes)
    if len(decoded) != entry.decoded_size or hashlib.sha256(decoded).hexdigest() != entry.decoded_sha256:
        raise DigestMismatchError("component decoded bytes do not match manifest")
    return raw, decoded, _dict(_strict_json(decoded, limits), "component"), entry, path


def _validate_pool(data: dict[str, Any], pool_id: str, limits: ResourceLimits) -> CoverageStatus:
    required = {
        "pool", "token0", "token1", "decimals", "fee_millionths", "spacing", "sqrt_price_x96",
        "current_tick", "active_liquidity_raw", "ticks", "coverage_status", "required_lower_tick",
        "required_upper_tick", "full_legal_pool_tick_coverage", "outside_status",
    }
    if not required.issubset(data):
        raise TypeContractError("pool component is missing required state fields")
    if type(data["pool"]) is not str or _ADDRESS.fullmatch(data["pool"]) is None:
        raise TypeContractError("pool address is invalid")
    if data["pool"].lower() != _POOLS[pool_id]:
        raise TypeContractError("pool address identity mismatch")
    if str(data["token0"]).lower() != _USDC or str(data["token1"]).lower() != _WETH:
        raise TypeContractError("pool token identity mismatch")
    if data["decimals"] != [6, 18]:
        raise TypeContractError("pool token decimal identity mismatch")
    if pool_id == "P3000" and data["fee_millionths"] != 3000:
        raise TypeContractError("P3000 fee identity mismatch")
    if pool_id == "P500" and data["fee_millionths"] != 500:
        raise TypeContractError("P500 fee identity mismatch")
    ticks = _list(data["ticks"], "pool ticks")
    if len(ticks) > limits.max_ticks_per_pool:
        raise TypeContractError("pool tick count exceeds resource limit")
    for tick_value in ticks:
        tick = _dict(tick_value, "tick")
        if not {"tick", "gross", "net"}.issubset(tick):
            raise TypeContractError("tick lacks liquidity fields")
        _exact_int(tick["tick"], "tick index")
        if type(tick["gross"]) is not str or type(tick["net"]) is not str:
            raise TypeContractError("tick gross/net liquidity must remain source integer strings")
    return CoverageStatus.COMPLETE_REGISTERED_SCOPE


def _validate_oracle(data: dict[str, Any]) -> CoverageStatus:
    if data.get("observation_type") != "HISTORICAL_AAVE_ORACLE_OBSERVATION_NOT_DEX_OR_COUNTERFACTUAL_POLICY":
        raise TypeContractError("oracle observation is not explicitly historical block-bound")
    assets = _list(data.get("assets"), "oracle assets")
    if {item.get("symbol") for item in assets if isinstance(item, dict)} != {"USDC", "WETH"}:
        raise TypeContractError("oracle assets differ from the registered scope")
    for asset_value in assets:
        asset = _dict(asset_value, "oracle asset")
        if type(asset.get("aave_price_raw")) is not str or type(asset.get("source_answer_raw")) is not str:
            raise TypeContractError("oracle raw values must remain exact integer strings")
        _exact_int(asset.get("source_decimals"), "oracle source decimals")
        expected_asset = _USDC if asset.get("symbol") == "USDC" else _WETH
        if str(asset.get("asset", "")).lower() != expected_asset:
            raise TypeContractError("oracle asset identity mismatch")
    return CoverageStatus.COMPLETE_REGISTERED_SCOPE


def _validate_borrowers(data: dict[str, Any], block: BlockRef, limits: ResourceLimits) -> CoverageStatus:
    configuration = _dict(data.get("configuration"), "borrower configuration")
    if str(configuration.get("pool", "")).lower() != _AAVE_POOL:
        raise TypeContractError("borrower source Aave Pool identity mismatch")
    portfolios = _list(data.get("portfolios"), "borrower portfolios")
    if len(portfolios) > limits.max_portfolios:
        raise TypeContractError("borrower portfolio count exceeds resource limit")
    logs = _list(data.get("discovery_logs"), "borrower discovery logs")
    if len(logs) > limits.max_discovery_headers:
        raise TypeContractError("borrower discovery header/log count exceeds resource limit")
    for portfolio_value in portfolios:
        portfolio = _dict(portfolio_value, "borrower portfolio")
        if portfolio.get("block_number") != block.number or str(portfolio.get("block_hash", "")).lower() != block.hash:
            raise TypeContractError("borrower portfolio block identity mismatch")
        address = portfolio.get("address")
        if type(address) is not str or _ADDRESS.fullmatch(address) is None:
            raise TypeContractError("borrower address is invalid")
        reserves = _list(portfolio.get("reserves"), "borrower reserves")
        if len(reserves) > limits.max_reserves_per_portfolio:
            raise TypeContractError("borrower reserve count exceeds resource limit")
        account = _list(portfolio.get("account_raw"), "borrower account raw")
        if len(account) != 6 or any(type(value) is not int or value < 0 for value in account):
            raise TypeContractError("source Pool.getUserAccountData vector or health factor is invalid")
        reconstruction = _dict(portfolio.get("hf_reconstruction"), "health-factor reconstruction")
        if type(reconstruction.get("contract_hf_raw")) is not str:
            raise TypeContractError("source health-factor trace is missing")
    return CoverageStatus.COMPLETE_REGISTERED_SCOPE


def _evidence(
    pack: SavedPack,
    relative: str,
    entry: ManifestEntry,
    raw: bytes,
    decoded: bytes,
    block: BlockRef,
    repo_root: Path,
) -> EvidenceRef:
    artifact_path = f"{pack.root}/{relative}"
    _safe_path(repo_root, artifact_path)
    return EvidenceRef(
        evidence_id=f"phase01b:{pack.name}:{block.number}:{relative}",
        origin=OriginKind.OBSERVED,
        source_kind=SourceKind.SAVED_ARTIFACT,
        source_commit=pack.source_commit,
        artifact_path=artifact_path,
        locator="/data",
        source_schema="defistress-phase01b-saved-component/1",
        verification_scope="V2_ADAPTER_NATIVE_RAW_DECODED_IDENTITY_AND_SCHEMA_VALIDATION",
        retrieved_at_s=pack.collected_at_s,
        raw_sha256=ArtifactBytesSha256.from_bytes(raw),
        decoded_sha256=DecodedBytesSha256.from_bytes(decoded),
        git_blob_sha1=GitBlobSha1.from_bytes(raw),
        block_ref=block,
    )


def load_snapshot(
    selection: SnapshotSelection,
    manifest: SavedPackManifest,
    limits: ResourceLimits = DEFAULT_LIMITS,
    *,
    adapter_source_commit: str,
) -> Ok[HistoricalSnapshot] | Blocked | Rejected:
    """Build one immutable same-block view from explicit full + repaired-borrower sources."""

    fallback_ref = EvidenceRef.synthetic("p02-02-selection", b"saved snapshot selection")
    try:
        if _COMMIT.fullmatch(adapter_source_commit) is None:
            raise TypeContractError("adapter_source_commit must be a full Git SHA")
        repo_root = Path(manifest.repository_root)
        full_block, full_pass = _select_catalog(manifest.full, selection.block_number, selection.read_pass)
        repair_block, repair_pass = _select_catalog(
            manifest.borrower_repair, selection.block_number, selection.read_pass
        )
        for other in (repair_block,):
            if (
                other.get("number") != full_block.get("number")
                or str(other.get("expected_hash", "")).lower() != str(full_block.get("expected_hash", "")).lower()
                or other.get("timestamp_unix") != full_block.get("timestamp_unix")
            ):
                raise TypeContractError("full and borrower-repair catalogs disagree on block identity")
        available_at = max(manifest.full.collected_at_s, manifest.borrower_repair.collected_at_s)
        block = BlockRef(
            chain_id=1,
            number=_exact_int(full_block.get("number"), "block number"),
            hash=str(full_block.get("expected_hash", "")),
            timestamp_s=_exact_int(full_block.get("timestamp_unix"), "block timestamp"),
            canonicality_evidence_id=f"phase01b:catalog:block:{selection.block_number}",
            canonicality_observed_at_s=available_at,
        )
        component_rows = _dict(full_pass.get("components"), "full pass components")
        requested: list[tuple[str, ComponentKind, SavedPack, dict[str, Any]]] = []
        for pool_id in selection.pool_ids:
            requested.append((pool_id, ComponentKind.POOL, manifest.full, _dict(component_rows.get(pool_id), pool_id)))
        requested.append(("oracle", ComponentKind.ORACLE, manifest.full, _dict(component_rows.get("oracle"), "oracle")))
        requested.append(("borrowers", ComponentKind.BORROWERS, manifest.borrower_repair, repair_pass))
        components: list[ComponentSnapshot] = []
        decoded_total = 0
        for component_id, kind, pack, row in requested:
            status = row.get("status")
            if status != "PASS":
                unavailable_code = "SOURCE_UNSUPPORTED" if row.get("kind") else "SOURCE_MISSING"
                return Blocked(
                    unavailable_code,
                    f"{component_id} is source-declared {status}; no implicit fallback is permitted",
                    (fallback_ref,),
                )
            relative = row.get("file")
            if type(relative) is not str:
                raise TypeContractError("catalog component file must be a string")
            raw, decoded, document, entry, _ = _load_component(repo_root, pack, relative, limits)
            decoded_total += len(decoded)
            if decoded_total > limits.max_decoded_pack_bytes:
                raise TypeContractError("selected decoded pack exceeds aggregate resource limit")
            if document.get("status") != "PASS":
                raise TypeContractError("component body status disagrees with selected PASS catalog row")
            data = _dict(document.get("data"), "component data")
            capabilities: tuple[str, ...]
            if kind is ComponentKind.POOL:
                coverage = _validate_pool(data, component_id, limits)
                field_origins = FrozenMap.from_mapping(
                    {
                        "/active_liquidity_raw": OriginKind.OBSERVED,
                        "/liquidity_audit": OriginKind.RECONSTRUCTED,
                        "/ticks": OriginKind.OBSERVED,
                    }
                )
                capabilities = ("ACTIVE_LIQUIDITY_READ", "POOL_SLOT0_READ", "REGISTERED_TICK_BAND_READ")
            elif kind is ComponentKind.ORACLE:
                coverage = _validate_oracle(data)
                field_origins = FrozenMap.from_mapping(
                    {
                        "/assets/*/aave_price_raw": OriginKind.OBSERVED,
                        "/assets/*/trace": OriginKind.OBSERVED,
                    }
                )
                capabilities = ("AAVE_ORACLE_PRICE_READ", "SOURCE_TRACE_READ")
            else:
                coverage = _validate_borrowers(data, block, limits)
                field_origins = FrozenMap.from_mapping(
                    {
                        "/portfolios/*/account_raw": OriginKind.OBSERVED,
                        "/portfolios/*/hf_reconstruction": OriginKind.RECONSTRUCTED,
                        "/portfolios/*/reserves": OriginKind.OBSERVED,
                    }
                )
                capabilities = (
                    "HF_RECONSTRUCTION_TRACE_READ",
                    "SELECTED_PORTFOLIO_READ",
                    "SOURCE_HEALTH_FACTOR_READ",
                )
            source_hash = row.get("content_sha256")
            if type(source_hash) is not str or _SHA256.fullmatch(source_hash) is None:
                raise TypeContractError("source-declared legacy content hash is invalid")
            evidence = _evidence(pack, relative, entry, raw, decoded, block, repo_root)
            frozen = _freeze_source(data)
            assert isinstance(frozen, FrozenMap)
            components.append(
                ComponentSnapshot(
                    component_id,
                    kind,
                    OriginKind.OBSERVED,
                    coverage,
                    str(status),
                    source_hash,
                    block.timestamp_s,
                    pack.collected_at_s,
                    TimePrecision.COLLECTION_END_UPPER_BOUND,
                    frozen,
                    field_origins,
                    capabilities,
                    evidence,
                )
            )
        components.sort(key=lambda item: item.component_id)
        complete = all(item.coverage is CoverageStatus.COMPLETE_REGISTERED_SCOPE for item in components)
        if selection.require_complete and not complete:
            return Blocked("INCOMPLETE_REQUIRED_VIEW", "required registered scope is incomplete", (fallback_ref,))
        selection_hash = DeterministicContentSha256.from_payload(selection)
        snapshot = HistoricalSnapshot(
            block,
            selection.read_pass,
            tuple(components),
            ExplicitBool(complete),
            SnapshotProvenance(
                manifest.artifact_git_ref,
                adapter_source_commit,
                manifest.full.source_commit,
                manifest.borrower_repair.source_commit,
                selection_hash,
            ),
            (
                "REGISTERED_HISTORICAL_SAMPLE_ONLY",
                "POOL_TICKS_COVER_REGISTERED_BAND_NOT_FULL_LEGAL_RANGE",
                "SOURCE_HEALTH_FACTOR_RETAINED_NOT_RECOMPUTED",
                "SOURCE_DECLARED_CONTENT_HASH_IS_LEGACY_PRODUCER_METADATA",
                "NO_LIQUIDATION_AMM_OR_ORACLE_POLICY_EXECUTION",
            ),
        )
        return Ok(snapshot)
    except (OSError, ContractError) as exc:
        return Rejected("QUARANTINED_SAVED_STATE", str(exc), (fallback_ref,))


def load_registered_snapshot(
    repository_root: Path,
    selection: SnapshotSelection,
    artifact_git_ref: str,
    adapter_source_commit: str,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> Ok[HistoricalSnapshot] | Blocked | Rejected:
    manifest_result = load_registered_manifest(repository_root, artifact_git_ref, limits)
    if isinstance(manifest_result, Rejected):
        return manifest_result
    return load_snapshot(
        selection,
        manifest_result.payload,
        limits,
        adapter_source_commit=adapter_source_commit,
    )
