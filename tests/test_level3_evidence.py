from __future__ import annotations

import csv
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path("data/processed/research_final/level3_extension")
CANONICAL = Path("data/processed/mainnet/aave_uniswap_snapshot_26045352.json")
CANONICAL_SHA256 = "553e93a345642dd4ef655dbcd883c12180d83327e9c9b917ff83c58dd9a3af99"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_canonical_snapshot_is_still_bit_identical() -> None:
    assert hashlib.sha256(CANONICAL.read_bytes()).hexdigest() == CANONICAL_SHA256


def test_historical_population_is_exactly_preregistered_and_rpc_verified() -> None:
    payload = _load(ROOT / "historical" / "raw_event_index.json")
    events = payload["events"]
    assert len(events) == 27
    assert all(event["status"] == "PASS" and event["chain_id"] == 1 for event in events)
    assert all(1_788_220_800 <= event["timestamp"] < 1_788_825_600 for event in events)
    assert len({(event["tx_hash"], event["log_index"]) for event in events}) == len(events)
    assert all(event["receipt_status"] == 1 for event in events)
    serialized = json.dumps(payload).lower()
    assert "liquidatee" not in serialized
    assert "raw_address" not in serialized


def test_historical_linkage_tiers_and_compressed_swap_evidence() -> None:
    rows = _load(ROOT / "historical" / "observation_linkage.json")["rows"]
    counts = {tier: sum(row["tier"] == tier for row in rows) for tier in {row["tier"] for row in rows}}
    assert counts == {
        "DIRECT_TRANSACTION_LINK": 3,
        "SAME_BLOCK_ASSOCIATION": 23,
        "TIME_WINDOW_ASSOCIATION": 1,
    }
    with gzip.open(ROOT / "historical" / "raw_swap_index.json.gz", "rt", encoding="utf-8") as handle:
        swaps = json.load(handle)["swaps"]
    assert len(swaps) == 31_489
    assert all(swap["chain_id"] == 1 for swap in swaps)


def test_invalid_epoch_attempt_is_excluded() -> None:
    payload = _load(ROOT / "historical_invalid_epoch_attempt" / "summary.json")
    assert payload["status"] == "FAIL_INVALID_PRE_REGISTRATION_EPOCH"
    assert "excluded" in payload["invalid_reason"]


def test_deep_stress_caps_counts_and_invariants() -> None:
    diagnostics = _load(ROOT / "deep_stress" / "numerical_diagnostics.json")
    assert diagnostics["largest_configured_wave_cap"] == 100
    assert diagnostics["largest_horizon_steps"] == 120
    assert diagnostics["max_deterministic_observed_depth"] == 2
    assert diagnostics["max_monte_carlo_observed_depth"] == 2
    assert diagnostics["numerical_floor_or_cap_artifacts"] == 0
    assert all(item["all_finite"] for item in diagnostics["monte_carlo_invariants"])
    assert all(item["no_duplicate_borrower_all_paths"] for item in diagnostics["monte_carlo_invariants"])
    caps = list(csv.DictReader((ROOT / "deep_stress" / "wave_cap_comparison.csv").open()))
    assert [int(row["max_waves"]) for row in caps] == [12, 24, 48, 100]
    assert [int(row["cascade_depth"]) for row in caps] == [1, 1, 1, 1]


def test_primary_monte_carlo_completed_10000_without_false_depth_claim() -> None:
    batches = _load(ROOT / "deep_stress" / "monte_carlo_batches.json")["batches"]
    primary = next(batch for batch in batches if batch["seed"] == 20_260_914 and batch["actual_runs"] == 10_000)
    assert primary["target_runs"] == primary["actual_runs"] == 10_000
    assert primary["cascade_frequencies"]["2"]["successes"] == 280
    assert primary["cascade_frequencies"]["3"]["successes"] == 0
    assert primary["max_observed_cascade_depth"] == 2
    assert primary["invariants"]["cap_hits"] == 0


def test_manifest_hashes_match_all_level3_artifacts() -> None:
    manifest = _load(ROOT / "manifest.json")
    for relative, expected in manifest["artifact_hashes"].items():
        path = ROOT / relative
        assert path.exists(), relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    for relative, expected in manifest["report_hashes"].items():
        path = Path(relative)
        assert path.exists(), relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
