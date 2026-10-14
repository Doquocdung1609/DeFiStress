from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

ROOT = Path("data/processed/research_final/frozen_v3")
CANONICAL = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
CANONICAL_SHA = "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(item) for item in value.values())
    if isinstance(value, list):
        return all(_finite(item) for item in value)
    return True


def test_frozen_v3_registry_and_claim_graph() -> None:
    registry = _load(ROOT / "results_registry.json")["results"]
    ledger = _load(ROOT / "claim_ledger.json")["claims"]
    sources = _load(ROOT / "evidence_source_matrix.json")
    result_ids = {row["result_id"] for row in registry}
    evidence_ids = {row["evidence_id"] for row in sources["sources"]}
    table_ids = {row["table_id"] for row in sources["table_registry"]}
    figure_ids = {row["figure_id"] for row in sources["figure_registry"]}
    assert len(result_ids) == len(registry)
    assert all(set(claim["result_ids"]) <= result_ids for claim in ledger)
    assert all(set(claim["evidence_ids"]) <= evidence_ids for claim in ledger)
    assert all(set(claim["table_ids"]) <= table_ids for claim in ledger)
    assert all(set(claim["figure_ids"]) <= figure_ids for claim in ledger)
    assert _finite(registry)


def test_frozen_v3_locked_facts_and_version_precedence() -> None:
    assert hashlib.sha256(CANONICAL.read_bytes()).hexdigest() == CANONICAL_SHA
    results = {row["result_id"]: row["value"] for row in _load(ROOT / "results_registry.json")["results"]}
    assert results["AAVE_VERIFIED_BORROWERS"] == 454
    assert results["AAVE_WETH_USDC_COHORT"] == 109
    assert results["RQ1_GRID60_DEPTH0"] == 18
    assert results["RQ1_GRID60_DEPTH1"] == 38
    assert results["RQ1_GRID60_DEPTH2"] == 4
    assert results["RQ1_MC_SEVERE_DEPTH2_COUNT"] == 280
    assert results["RQ1_MC_SEVERE_DEPTH3_COUNT"] == 0
    assert results["HIST_RPC_CENSUS_EVENTS"] == 28
    assert results["HIST_GRAPH_MATCHED_EVENTS"] == 27
    assert [row["version"] for row in _load(ROOT / "version_precedence.json")["versions"]] == [
        "Original",
        "P0 corrected v2",
        "Level-3",
        "Level-3 targeted repair",
        "Frozen v3",
    ]


def test_frozen_v3_tables_match_registry() -> None:
    results = {row["result_id"]: row for row in _load(ROOT / "results_registry.json")["results"]}
    with (ROOT / "tables" / "core_facts.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        expected = results[row["result_id"]]["value"]
        assert str(expected) == row["value"]
        assert results[row["result_id"]]["unit"] == row["unit"]
    with (ROOT / "tables" / "rq1_deterministic_depth.csv").open(encoding="utf-8", newline="") as handle:
        depth_rows = list(csv.DictReader(handle))
    assert sum(int(row["count"]) for row in depth_rows if row["grid"] == "60") == 60
    assert next(int(row["count"]) for row in depth_rows if row["grid"] == "60" and row["depth"] == "2") == 4


def test_frozen_v3_figures_have_scientific_captions() -> None:
    figures = _load(ROOT / "figures" / "figure_registry.json")["figures"]
    required = {"noi_dung_do", "loai_du_lieu", "mau_so_don_vi", "co_the_ket_luan", "khong_the_ket_luan"}
    assert len(figures) == 4
    for figure in figures:
        assert required == set(figure["caption_vi"])
        assert Path(figure["path"]).is_file()
        assert Path(figure["path"]).stat().st_size > 1_000


def test_frozen_v3_has_no_raw_addresses_or_secrets() -> None:
    paths = [*ROOT.rglob("*.json"), *ROOT.rglob("*.csv")]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert re.search(r"0x[a-fA-F0-9]{40}\b", text) is None
    assert re.search(r"(?i)(api[_-]?key|authorization)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{12,}", text) is None


def test_frozen_v3_manifest_hashes_and_pending_state() -> None:
    manifest = _load(ROOT / "manifest.json")
    assert manifest["status"] == "P1_NUMERICAL_READY — AWAITING_P2_CITATION_RECONCILIATION"
    assert manifest["scientific_content_lock_declared"] is False
    assert manifest["large_research_rerun"] is False
    assert all(manifest["quality_gate"].values())
    for relative, expected in manifest["artifact_hashes"].items():
        path = ROOT / relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    for relative, expected in manifest["report_hashes"].items():
        path = Path(relative)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
