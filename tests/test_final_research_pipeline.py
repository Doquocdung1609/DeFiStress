from __future__ import annotations

from pathlib import Path

import pytest

from scripts.research.package_builder import Registry, build_claims
from sim.research.aave_suite import CANONICAL_SNAPSHOT, _wilson, load_canonical_snapshot, snapshot_quality


def test_canonical_aave_snapshot_is_real_mainnet_same_block() -> None:
    snapshot = load_canonical_snapshot(CANONICAL_SNAPSHOT)
    quality = snapshot_quality(snapshot, CANONICAL_SNAPSHOT)

    assert quality["mode"] == "REAL_MAINNET"
    assert quality["chain_id"] == 1
    assert quality["block_number"] == 26045352
    assert quality["verified_borrowers"] > 0
    assert quality["weth_usdc_cohort"] > 0
    assert "not total-market coverage" in quality["candidate_verification_rate_boundary"]


@pytest.mark.parametrize(("successes", "runs"), [(0, 200), (100, 200), (200, 200)])
def test_wilson_interval_is_bounded_and_contains_sample_frequency(successes: int, runs: int) -> None:
    interval = _wilson(successes, runs)

    assert 0 <= interval["lower"] <= successes / runs
    assert successes / runs <= interval["upper"] <= 1
    assert interval["confidence"] == pytest.approx(0.95)


def test_registry_rejects_non_finite_numbers() -> None:
    registry = Registry()

    with pytest.raises(ValueError, match="non-finite"):
        registry.add("BAD", "TEST", "bad", float("nan"), "ratio", "artifact.json", "", "")


def test_claim_builder_rejects_missing_result_ids() -> None:
    with pytest.raises(ValueError, match="missing result IDs"):
        build_claims(Registry())


def test_research_entrypoint_exists() -> None:
    assert Path("scripts/run_full_research_pipeline.py").is_file()
