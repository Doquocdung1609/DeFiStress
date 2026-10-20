"""Work controls independently written against accepted P02-02 requirements."""

from __future__ import annotations

import copy
import dataclasses
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.contracts.state import Ok, Rejected
from defistress_v2.state import ResourceLimits, SnapshotSelection, load_registered_manifest, load_snapshot
from defistress_v2.state.saved_adapter import _strict_json, _validate_borrowers, _validate_oracle, _validate_pool

ROOT = Path(__file__).resolve().parents[2]
BASE = "817b0f85547963939841e8bc7181e55b2b84d86f"
BLOCK = 26045352


@pytest.fixture(scope="module")
def accepted_snapshot():
    manifest = load_registered_manifest(ROOT, BASE)
    assert isinstance(manifest, Ok)
    result = load_snapshot(SnapshotSelection(BLOCK, 1), manifest.payload, adapter_source_commit=BASE)
    assert isinstance(result, Ok)
    return result.payload


@pytest.mark.parametrize(
    "field,value",
    [
        ("capabilities", ["POOL_SLOT0_READ"]),
        ("effective_at_s", True),
        ("origin", "OBSERVED"),
        ("capabilities", ("EXECUTION_INPUT_COMPLETE",)),
    ],
)
def test_review_component_dto_rejects_mutable_or_untyped_values(accepted_snapshot, field, value):
    with pytest.raises(TypeContractError):
        dataclasses.replace(accepted_snapshot.components[0], **{field: value})


@pytest.mark.parametrize(
    "field,value", [("components", []), ("read_pass", True), ("complete", True), ("canonicality_evidence", None)]
)
def test_review_snapshot_dto_rejects_untyped_or_unlinked_values(accepted_snapshot, field, value):
    with pytest.raises(TypeContractError):
        dataclasses.replace(accepted_snapshot, **{field: value})


def test_review_content_changes_when_economic_state_changes(accepted_snapshot):
    from defistress_v2.contracts import FrozenMap

    component = accepted_snapshot.components[0]
    payload = dict(component.payload.items())
    payload["active_liquidity_raw"] = "0"
    changed_component = dataclasses.replace(component, payload=FrozenMap.from_mapping(payload))
    changed = dataclasses.replace(accepted_snapshot, components=(changed_component, *accepted_snapshot.components[1:]))
    assert changed.content_sha256 != accepted_snapshot.content_sha256


def test_review_canonicality_and_unsupported_round_are_explicit(accepted_snapshot):
    assert accepted_snapshot.canonicality_evidence.block_ref == accepted_snapshot.block_ref
    assert accepted_snapshot.canonicality_evidence.locator == "/0/passes/0/identity/data"
    oracle = next(c for c in accepted_snapshot.components if c.component_id == "oracle")
    assert oracle.field_availability["/assets/0/trace/round"]["status"] == "UNSUPPORTED"
    assert oracle.field_availability["/assets/0/freshness"]["status"] == "MISSING"
    assert oracle.field_origins["/assets/*/trace/round"] == "RECONSTRUCTED"


def test_review_forged_root_cannot_reanchor_its_own_catalog(tmp_path):
    phase = tmp_path / "docs/research_v2/phase01b"
    shutil.copytree(ROOT / "docs/research_v2/phase01b", phase)
    catalog = phase / "evidence/full/validation_catalog.json"
    rows = json.loads(catalog.read_bytes())
    rows[0]["passes"][0]["identity"]["data"]["chain_id"] = 2
    catalog.write_text(json.dumps(rows), encoding="utf-8")
    provenance = phase / "EVIDENCE_PROVENANCE.json"
    document = json.loads(provenance.read_bytes())
    for row in document["files"]:
        if row["path"] == "evidence/full/validation_catalog.json":
            row["size_bytes"] = catalog.stat().st_size
            row["sha256"] = hashlib.sha256(catalog.read_bytes()).hexdigest()
    provenance.write_text(json.dumps(document), encoding="utf-8")
    result = load_registered_manifest(tmp_path, BASE)
    assert isinstance(result, Rejected)
    assert "anchor" in result.reason


def test_review_manifest_catalog_replacement_is_not_verified_data():
    from defistress_v2.contracts import FrozenMap

    manifest = load_registered_manifest(ROOT, BASE)
    assert isinstance(manifest, Ok)
    records = list(manifest.payload.full.catalog["records"])
    first = dict(records[0].items())
    passes = list(first["passes"])
    changed_pass = dict(passes[0].items())
    components = dict(changed_pass["components"].items())
    changed_row = dict(components["P3000"].items())
    changed_row["file"] = "components/26045352-pass2-P3000.json.gz"
    components["P3000"] = FrozenMap.from_mapping(changed_row)
    changed_pass["components"] = FrozenMap.from_mapping(components)
    passes[0] = FrozenMap.from_mapping(changed_pass)
    first["passes"] = tuple(passes)
    records[0] = FrozenMap.from_mapping(first)
    pack = dataclasses.replace(manifest.payload.full, catalog=FrozenMap.from_mapping({"records": tuple(records)}))
    modified = dataclasses.replace(manifest.payload, full=pack)
    result = load_snapshot(SnapshotSelection(BLOCK, 1), modified, adapter_source_commit=BASE)
    assert isinstance(result, Rejected)


def test_review_symlink_escape(tmp_path):
    from defistress_v2.state.saved_adapter import _safe_path

    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "root"
    root.mkdir()
    (outside / "value").write_text("{}")
    try:
        (root / "link").symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"OS does not permit symlink creation: {exc}")
    with pytest.raises(TypeContractError):
        _safe_path(root, "link/value")


def test_review_malformed_gzip_has_typed_failure():
    from defistress_v2.state.saved_adapter import _bounded_gzip

    with pytest.raises(TypeContractError):
        _bounded_gzip(b"invalid gzip", 100)


def test_review_smoke_cli_preserves_distinct_commits_and_emits_failure_report(tmp_path):
    script = ROOT / "scripts/research/validate_p02_02_saved_adapter.py"
    output = tmp_path / "smoke.json"
    command = [
        sys.executable,
        str(script),
        "--repository-root",
        str(ROOT),
        "--source-commit",
        BASE,
        "--adapter-source-commit",
        "1" * 40,
        "--output",
        str(output),
    ]
    run = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT) + os.pathsep + os.environ.get("PYTHONPATH", "")},
    )
    assert run.returncode == 0, run.stderr
    report = json.loads(output.read_bytes())
    assert report["artifact_git_ref"] == BASE
    assert report["adapter_source_commit"] == "1" * 40
    assert report["coverage"]["component_views"] == 24
    assert all(r["status"] == "PASS" for r in report["snapshots"])
    empty = tmp_path / "empty"
    empty.mkdir()
    command[command.index("--repository-root") + 1] = str(empty)
    run = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": str(ROOT) + os.pathsep + os.environ.get("PYTHONPATH", "")},
    )
    assert run.returncode == 1
    failed = json.loads(output.read_bytes())
    assert failed["overall_status"] == "FAIL"
    assert failed["failed_or_blocked_snapshot_views"] == 6


def source(part):
    path = (
        ROOT
        / "docs/research_v2/phase01b/evidence"
        / ("borrower_repair" if part == "borrowers" else "full")
        / "components"
        / f"{BLOCK}-pass1-{part}.json.gz"
    )
    return json.loads(gzip.decompress(path.read_bytes()))["data"]


def test_review_selection_bool_is_not_read_pass():
    with pytest.raises(TypeContractError):
        SnapshotSelection(BLOCK, True)


@pytest.mark.parametrize("kind", ["zero_active_liquidity", "zero_debt_sentinel"])
def test_review_zero_values_are_not_missing(kind, accepted_snapshot):
    if kind == "zero_active_liquidity":
        data = source("P3000")
        data["active_liquidity_raw"] = "0"
        assert _validate_pool(data, "P3000", ResourceLimits()).value == "COMPLETE_REGISTERED_SCOPE"
    else:
        data = source("borrowers")
        account = data["portfolios"][0]
        account["account_raw"][1] = 0
        account["account_raw"][5] = 2**256 - 1
        account["hf_reconstruction"]["contract_hf_raw"] = str(2**256 - 1)
        account["hf_reconstruction"]["zero_debt_hf"] = "UINT256_MAX_SENTINEL"
        assert (
            _validate_borrowers(data, accepted_snapshot.block_ref, ResourceLimits()).value
            == "COMPLETE_REGISTERED_SCOPE"
        )


def test_review_opaque_string_bool_zero_and_missing_stay_distinct():
    from defistress_v2.contracts import ExplicitBool
    from defistress_v2.state.saved_adapter import _freeze_source

    value = _freeze_source({"opaque": "001", "flag": False, "balance": 0, "missing": None})
    assert value["opaque"] == "001"
    assert value["flag"] == ExplicitBool(False)
    assert value["balance"] == "0"
    assert value["missing"] is None


@pytest.mark.parametrize("name", ["max_input_bytes", "max_json_depth", "max_manifest_entries"])
def test_review_invalid_resource_bounds(name):
    with pytest.raises(TypeContractError):
        ResourceLimits(**{name: -1})


@pytest.mark.parametrize("raw", [("[" * 2000 + "0" + "]" * 2000).encode(), ('{"x":' + "9" * 5000 + "}").encode()])
def test_review_malformed_deep_and_huge_json_has_typed_failure(raw):
    with pytest.raises(TypeContractError):
        _strict_json(raw, ResourceLimits())


@pytest.mark.parametrize(
    "mutation",
    ["spacing", "sqrt", "duplicate_ticks", "missing_ticks", "missing_bitmap", "coverage_flag", "negative_gross"],
)
def test_review_pool_guards(mutation):
    d = source("P3000")
    if mutation == "spacing":
        d["spacing"] = 0
    if mutation == "sqrt":
        d["sqrt_price_x96"] = "NaN"
    if mutation == "duplicate_ticks":
        d["ticks"].append(copy.deepcopy(d["ticks"][0]))
    if mutation == "missing_ticks":
        d["missing_ticks"] = [d["ticks"][0]["tick"]]
    if mutation == "missing_bitmap":
        d["bitmaps"].pop()
    if mutation == "coverage_flag":
        d["full_legal_pool_tick_coverage"] = True
    if mutation == "negative_gross":
        d["ticks"][0]["gross"] = "-1"
    with pytest.raises(TypeContractError):
        _validate_pool(d, "P3000", ResourceLimits())


@pytest.mark.parametrize(
    "mutation", ["duplicate_asset", "wrong_config", "future_round", "wrong_decimals", "native_round_promotion"]
)
def test_review_oracle_guards(mutation):
    d = source("oracle")
    if mutation == "duplicate_asset":
        d["assets"].append(copy.deepcopy(d["assets"][0]))
    if mutation == "wrong_config":
        d["configuration"]["pool"] = "0x" + "1" * 40
    if mutation == "future_round":
        d["assets"][1]["trace"]["round"]["updated_at"] = 2_000_000_000
    if mutation == "wrong_decimals":
        d["assets"][0]["source_decimals"] = True
    if mutation == "native_round_promotion":
        d["assets"][0]["trace"]["round_status"] = "PASS"
    with pytest.raises(TypeContractError):
        _validate_oracle(d)


@pytest.mark.parametrize(
    "mutation", ["empty", "duplicate_borrower", "duplicate_reserve", "wrong_decimals", "missing_flags", "future_header"]
)
def test_review_borrower_guards(mutation):
    d = source("borrowers")
    m = load_registered_manifest(ROOT, BASE)
    assert isinstance(m, Ok)
    s = load_snapshot(SnapshotSelection(BLOCK, 1), m.payload, adapter_source_commit=BASE)
    assert isinstance(s, Ok)
    if mutation == "empty":
        d["portfolios"] = []
    if mutation == "duplicate_borrower":
        d["portfolios"].append(copy.deepcopy(d["portfolios"][0]))
    if mutation == "duplicate_reserve":
        d["portfolios"][0]["reserves"].append(copy.deepcopy(d["portfolios"][0]["reserves"][0]))
    if mutation == "wrong_decimals":
        d["portfolios"][0]["reserves"][0]["decimals"] = False
    if mutation == "missing_flags":
        d["portfolios"][0]["missing_data_flags"] = ["MISSING_PRICE"]
    if mutation == "future_header":
        d["discovery_coverage"]["contiguous_headers"][-1]["timestamp"] = 2_000_000_000
    with pytest.raises(TypeContractError):
        _validate_borrowers(d, s.payload.block_ref, ResourceLimits())
