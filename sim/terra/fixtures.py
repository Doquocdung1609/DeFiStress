from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sim.terra.datasets import DatasetManifest, ResearchDataset, dataset_hash, quality_report
from sim.terra.schemas import DataStatus, TerraObservation

D = Decimal
FIXTURE_VERSION = "terra_fixture_v1"


def terra_fixture_dataset() -> ResearchDataset:
    """Deterministic synthetic data for offline tests; never historical evidence."""
    start = datetime(2022, 5, 1, tzinfo=UTC)
    end = datetime(2022, 5, 13, 23, tzinfo=UTC)
    observations: list[TerraObservation] = []
    hours = int((end - start).total_seconds() // 3600) + 1
    for index in range(hours):
        timestamp = start + timedelta(hours=index)
        evaluation_hour = max(0, int((timestamp - datetime(2022, 5, 7, tzinfo=UTC)).total_seconds() // 3600))
        luna_supply: float
        anchor: float
        withdrawal: float
        redemption: float
        dex_liquidity: float
        if timestamp < datetime(2022, 5, 7, tzinfo=UTC):
            ust_price = 1 - 0.0012 * (1 + math.sin(index / 11)) / 2
            luna_price = 82 + 4 * math.sin(index / 18)
            luna_supply = float(350_000_000 + index * 15_000)
            anchor = float(14_000_000_000 - index * 2_000_000)
            withdrawal = 18_000_000 + 4_000_000 * (1 + math.sin(index / 8))
            redemption = 2_000_000.0
            dex_liquidity = float(1_500_000_000 - index * 400_000)
        else:
            acceleration = 1 / (1 + math.exp(-(evaluation_hour - 62) / 13))
            ust_price = max(0.055, 1 - 0.95 * acceleration)
            luna_price = max(0.0002, 78 * math.exp(-evaluation_hour / 27))
            luna_supply = 355_000_000 * (1 + 18_000 * acceleration**4)
            anchor = max(120_000_000, 13_700_000_000 * (1 - 0.985 * acceleration))
            withdrawal = 25_000_000 + 1_100_000_000 * acceleration
            redemption = 8_000_000 + 850_000_000 * acceleration
            dex_liquidity = max(35_000_000, 1_420_000_000 * (1 - 0.96 * acceleration))
        minted = redemption / max(luna_price, 0.0002)
        observations.append(
            TerraObservation(
                timestamp=timestamp,
                block_height=7_450_000 + index * 600,
                ust_price=D(str(ust_price)),
                luna_price=D(str(luna_price)),
                ust_supply=D("18500000000") - D(str(min(index * 700_000, 6_000_000_000))),
                luna_supply=D(str(luna_supply)),
                anchor_total_deposits=D(str(anchor)),
                anchor_deposit_flow=D("12000000") if timestamp < datetime(2022, 5, 7, tzinfo=UTC) else D("1000000"),
                anchor_withdrawal_flow=D(str(withdrawal)),
                ust_native_redemption_volume=D(str(redemption)),
                luna_minted_from_redemption=D(str(minted)),
                luna_burned=D("0"),
                ust_dex_sell_volume=D(str(withdrawal * 0.42)),
                terra_dex_liquidity=D(str(dex_liquidity)),
                terra_dex_depth=D(str(dex_liquidity * 0.12)),
                top10_anchor_share=D("0.23"),
                top100_anchor_share=D("0.51"),
                curve_ust_liquidity=None,
                curve_pool_imbalance=None,
                curve_ust_price=None,
                source_name="DeFiStress deterministic Terra fixture",
                source_type="SYNTHETIC_TEST_FIXTURE",
                chain_id="columbus-5-fixture",
                raw_reference="fixture://terra_fixture_v1",
                quality_flag="FIXTURE",
            )
        )
    rows = tuple(observations)
    manifest = DatasetManifest(
        dataset_version=FIXTURE_VERSION,
        status=DataStatus.FIXTURE,
        row_count=len(rows),
        start_timestamp=rows[0].timestamp,
        end_timestamp=rows[-1].timestamp,
        dataset_hash=dataset_hash(rows),
        source_manifest={
            "primary": {
                "source": "Deterministic generated fixture",
                "chain": "Terra Classic semantics fixture",
                "priority": "TEST_ONLY",
                "historical_evidence": False,
            },
            "external_historical_sources": {"status": "UNAVAILABLE", "reason": "No archival endpoint configured"},
        },
        quality_report=quality_report(rows),
        transformation_version="terra-fixture-generator-1",
        git_commit="TEST_FIXTURE",
    )
    return ResearchDataset(manifest, rows)
