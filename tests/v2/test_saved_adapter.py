"""P02-02 saved-state adapter tests; all reads are offline and repository-bounded."""

from __future__ import annotations

import ast
import dataclasses
import gzip
import hashlib
from pathlib import Path

import pytest

from defistress_v2.contracts import ExplicitBool, FrozenMap, HistoricalSnapshot
from defistress_v2.contracts.errors import DigestMismatchError, TypeContractError
from defistress_v2.contracts.state import Blocked, Ok, Rejected
from defistress_v2.state import (
    ResourceLimits,
    SavedPackManifest,
    SnapshotSelection,
    load_registered_manifest,
    load_registered_snapshot,
    load_snapshot,
)
from defistress_v2.state.saved_adapter import (
    ManifestEntry,
    SavedPack,
    _bounded_gzip,
    _load_component,
    _safe_path,
    _strict_json,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "817b0f85547963939841e8bc7181e55b2b84d86f"
BLOCKS = (26045352, 26038152, 26030952)


@pytest.fixture(scope="module")
def manifest() -> SavedPackManifest:
    result = load_registered_manifest(ROOT, SOURCE_COMMIT)
    assert isinstance(result, Ok)
    return result.payload


@pytest.mark.parametrize("block_number", BLOCKS)
@pytest.mark.parametrize("read_pass", (1, 2))
def test_registered_smoke_loads_each_block_pass(block_number: int, read_pass: int) -> None:
    result = load_registered_snapshot(
        ROOT,
        SnapshotSelection(block_number, read_pass),
        SOURCE_COMMIT,
        SOURCE_COMMIT,
    )
    assert isinstance(result, Ok)
    assert isinstance(result.payload, HistoricalSnapshot)
    assert result.payload.block_ref.number == block_number
    assert result.payload.read_pass == read_pass
    assert result.payload.complete == ExplicitBool(True)
    assert [item.component_id for item in result.payload.components] == ["P3000", "P500", "borrowers", "oracle"]
    assert len(result.payload.content_sha256.value) == 64


def test_snapshot_is_deeply_immutable(manifest: SavedPackManifest) -> None:
    result = load_snapshot(SnapshotSelection(BLOCKS[0], 1), manifest, adapter_source_commit=SOURCE_COMMIT)
    assert isinstance(result, Ok)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.payload.read_pass = 2  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.payload.components[0].payload["pool"] = "changed"  # type: ignore[index]


def test_content_hash_is_deterministic_and_ignores_adapter_checkout_provenance(
    manifest: SavedPackManifest,
) -> None:
    one = load_snapshot(SnapshotSelection(BLOCKS[0], 1), manifest, adapter_source_commit="1" * 40)
    two = load_snapshot(SnapshotSelection(BLOCKS[0], 1), manifest, adapter_source_commit="2" * 40)
    assert isinstance(one, Ok) and isinstance(two, Ok)
    assert one.payload.content_sha256 == two.payload.content_sha256
    assert one.payload.to_canonical() != two.payload.to_canonical()


@pytest.mark.parametrize(
    ("block", "read_pass"),
    ((-1, 1), (1, 0), (1, 3)),
)
def test_selection_rejects_invalid_block_or_pass(block: int, read_pass: int) -> None:
    with pytest.raises(TypeContractError):
        SnapshotSelection(block, read_pass)


def test_selection_rejects_unknown_or_duplicate_pool() -> None:
    with pytest.raises(TypeContractError):
        SnapshotSelection(BLOCKS[0], 1, ("P3000", "P3000"))
    with pytest.raises(TypeContractError):
        SnapshotSelection(BLOCKS[0], 1, ("P10000",))


def test_unregistered_block_is_rejected(manifest: SavedPackManifest) -> None:
    result = load_snapshot(SnapshotSelection(1, 1), manifest, adapter_source_commit=SOURCE_COMMIT)
    assert isinstance(result, Rejected)
    assert result.code == "QUARANTINED_SAVED_STATE"


def test_low_input_limit_rejects_pack() -> None:
    result = load_registered_manifest(ROOT, SOURCE_COMMIT, ResourceLimits(max_input_bytes=8))
    assert isinstance(result, Rejected)


def test_low_decoded_limit_quarantines_component(manifest: SavedPackManifest) -> None:
    result = load_snapshot(
        SnapshotSelection(BLOCKS[0], 1),
        manifest,
        ResourceLimits(max_decoded_bytes=32),
        adapter_source_commit=SOURCE_COMMIT,
    )
    assert isinstance(result, Rejected)
    assert result.code == "QUARANTINED_SAVED_STATE"


def test_low_tick_limit_quarantines_pool(manifest: SavedPackManifest) -> None:
    result = load_snapshot(
        SnapshotSelection(BLOCKS[0], 1),
        manifest,
        ResourceLimits(max_ticks_per_pool=1),
        adapter_source_commit=SOURCE_COMMIT,
    )
    assert isinstance(result, Rejected)
    assert "tick count" in result.reason


def test_low_portfolio_limit_quarantines_borrowers(manifest: SavedPackManifest) -> None:
    result = load_snapshot(
        SnapshotSelection(BLOCKS[0], 1),
        manifest,
        ResourceLimits(max_portfolios=1),
        adapter_source_commit=SOURCE_COMMIT,
    )
    assert isinstance(result, Rejected)
    assert "portfolio count" in result.reason


def test_explicit_blocked_repair_source_never_falls_back(manifest: SavedPackManifest) -> None:
    catalog = FrozenMap.from_mapping(
        {
            "records": (
                FrozenMap.from_mapping(
                    {
                        "block": FrozenMap.from_mapping(
                            {
                                "expected_hash": "0x4dffe3bdf7bbaf24fd1e3b6c3f4795687dccfd3189cbfb61f4dbaf926722220a",
                                "number": str(BLOCKS[0]),
                                "timestamp_unix": "1790229035",
                            }
                        ),
                        "passes": (
                            FrozenMap.from_mapping({"kind": "PROVIDER_CAPABILITY_LIMIT", "status": "BLOCKED"}),
                            FrozenMap.from_mapping({"kind": "PROVIDER_CAPABILITY_LIMIT", "status": "BLOCKED"}),
                        ),
                    }
                ),
            )
        }
    )
    blocked_pack = dataclasses.replace(manifest.borrower_repair, catalog=catalog)
    changed = dataclasses.replace(manifest, borrower_repair=blocked_pack)
    result = load_snapshot(SnapshotSelection(BLOCKS[0], 1), changed, adapter_source_commit=SOURCE_COMMIT)
    assert isinstance(result, Blocked)
    assert result.code == "SOURCE_UNSUPPORTED"
    assert "fallback" in result.reason.lower()


def test_strict_json_rejects_duplicate_keys_float_nonfinite_and_depth() -> None:
    for raw in (b'{"a":1,"a":2}', b'{"a":1.5}', b'{"a":NaN}'):
        with pytest.raises(TypeContractError):
            _strict_json(raw, ResourceLimits())
    deep = ("[" * 130 + "0" + "]" * 130).encode()
    with pytest.raises(TypeContractError):
        _strict_json(deep, ResourceLimits(max_json_depth=128))


def test_bounded_gzip_rejects_trailing_and_multiple_members() -> None:
    member = gzip.compress(b'{"ok":true}', mtime=0)
    assert _bounded_gzip(member, 100) == b'{"ok":true}'
    with pytest.raises(TypeContractError):
        _bounded_gzip(member + b"trailing", 100)
    with pytest.raises(TypeContractError):
        _bounded_gzip(member + member, 100)


def test_safe_path_rejects_traversal_and_absolute(tmp_path: Path) -> None:
    (tmp_path / "value.json").write_text("{}", encoding="utf-8")
    assert _safe_path(tmp_path, "value.json").name == "value.json"
    with pytest.raises(TypeContractError):
        _safe_path(tmp_path, "../value.json")
    with pytest.raises(TypeContractError):
        _safe_path(tmp_path, str((tmp_path / "value.json").resolve()))


def test_component_raw_tamper_is_detected(tmp_path: Path) -> None:
    pack_root = tmp_path / "pack"
    pack_root.mkdir()
    decoded = b'{"data":{},"status":"PASS"}'
    raw = gzip.compress(decoded, mtime=0)
    path = pack_root / "component.json.gz"
    path.write_bytes(raw + b"x")
    entry = ManifestEntry(
        "component.json.gz",
        hashlib.sha256(raw).hexdigest(),
        len(raw),
        hashlib.sha256(decoded).hexdigest(),
        len(decoded),
    )
    pack = SavedPack("synthetic", "pack", "1" * 40, 1, (entry,), FrozenMap.from_mapping({"records": ()}))
    with pytest.raises(DigestMismatchError):
        _load_component(tmp_path, pack, entry.path, ResourceLimits())


def test_manifest_provenance_tamper_is_rejected(tmp_path: Path) -> None:
    phase = tmp_path / "docs" / "research_v2" / "phase01b"
    phase.mkdir(parents=True)
    (phase / "EVIDENCE_PROVENANCE.json").write_text('{"files":[]}', encoding="utf-8")
    result = load_registered_manifest(tmp_path, SOURCE_COMMIT)
    assert isinstance(result, Rejected)


def test_adapter_has_no_network_or_collector_dependency() -> None:
    source = (ROOT / "defistress_v2" / "state" / "saved_adapter.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not imported.intersection({"requests", "httpx", "web3", "socket", "collector", "verify_saved"})
    assert "ETH_RPC_URL" not in source
    assert "os.environ" not in source


def test_adapter_does_not_recompute_hf_or_execute_models() -> None:
    source = (ROOT / "defistress_v2" / "state" / "saved_adapter.py").read_text(encoding="utf-8")
    forbidden = ("liquidate(", "sell_weth(", "arbitrage_toward(", "health_factor(", "MonteCarlo")
    assert all(token not in source for token in forbidden)


def test_protected_phase01b_tree_remains_clean() -> None:
    # This test's source tree is intentionally read-only; production workflow also uses git diff.
    assert (ROOT / "docs/research_v2/phase01b/EVIDENCE_PROVENANCE.json").is_file()
    assert (ROOT / "docs/research_v2/program_control/CODEX_NEXT_WORK_PACKAGE.md").is_file()


def test_source_health_factor_and_liquidity_units_are_retained(manifest: SavedPackManifest) -> None:
    result = load_snapshot(SnapshotSelection(BLOCKS[0], 1), manifest, adapter_source_commit=SOURCE_COMMIT)
    assert isinstance(result, Ok)
    parts = {item.component_id: item for item in result.payload.components}
    borrower = parts["borrowers"].payload
    portfolios = borrower["portfolios"]
    assert isinstance(portfolios, tuple)
    first = portfolios[0]
    assert isinstance(first, FrozenMap)
    reconstruction = first["hf_reconstruction"]
    assert isinstance(reconstruction, FrozenMap)
    assert reconstruction["contract_hf_raw"] == reconstruction["hf_raw"]
    pool = parts["P3000"].payload
    assert isinstance(pool["active_liquidity_raw"], str)
    ticks = pool["ticks"]
    assert isinstance(ticks, tuple) and isinstance(ticks[0], FrozenMap)
    assert isinstance(ticks[0]["gross"], str) and isinstance(ticks[0]["net"], str)
    assert parts["borrowers"].field_origins["/portfolios/*/hf_reconstruction"] == "RECONSTRUCTED"
    assert "EXECUTION_INPUT_COMPLETE" not in parts["borrowers"].capabilities


def test_catalog_legacy_hash_is_labeled_not_promoted(manifest: SavedPackManifest) -> None:
    result = load_snapshot(SnapshotSelection(BLOCKS[0], 1), manifest, adapter_source_commit=SOURCE_COMMIT)
    assert isinstance(result, Ok)
    assert all(item.source_declared_content_sha256 for item in result.payload.components)
    assert "SOURCE_DECLARED_CONTENT_HASH_IS_LEGACY_PRODUCER_METADATA" in result.payload.limitations
