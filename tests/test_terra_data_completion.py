from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from scripts.terra import complete_historical_data as completion


@pytest.fixture(scope="module")
def built() -> tuple[pd.DataFrame, dict[str, object]]:
    return completion.build_hourly_state()


def test_exact_extended_window_and_no_duplicate_timestamps(
    built: tuple[pd.DataFrame, dict[str, object]],
) -> None:
    frame, _ = built
    assert len(frame) == 1776
    assert frame["timestamp"].iloc[0] == completion.START
    assert frame["timestamp"].iloc[-1] == completion.END
    assert frame["timestamp"].is_monotonic_increasing
    assert not frame["timestamp"].duplicated().any()


def test_backward_state_mapping_has_no_future_leakage() -> None:
    source_index = pd.DatetimeIndex(
        ["2022-03-01T00:00:00Z", "2022-03-02T00:00:00Z", "2022-03-03T00:00:00Z"]
    )
    target = pd.date_range("2022-03-01", "2022-03-03", freq="h", tz="UTC")
    used = completion.source_timestamp_asof(source_index, target).dropna()
    assert (pd.to_datetime(used, utc=True) <= used.index).all()


def test_daily_state_is_carried_forward_but_stops_at_validity_boundary() -> None:
    source = pd.Series(
        [10.0, 20.0],
        index=pd.DatetimeIndex(["2022-03-01T00:00:00Z", "2022-03-02T00:00:00Z"]),
    )
    target = pd.date_range("2022-03-01", "2022-03-03", freq="h", tz="UTC")
    carried = completion.carry_state_backward(
        source,
        target,
        valid_through=pd.Timestamp("2022-03-02T23:00:00Z"),
    )
    assert carried.loc["2022-03-01T23:00:00Z"] == 10.0
    assert carried.loc["2022-03-02T23:00:00Z"] == 20.0
    assert np.isnan(carried.loc["2022-03-03T00:00:00Z"])


def test_event_flows_are_never_forward_filled() -> None:
    target = pd.date_range("2022-05-05T23:00:00Z", periods=4, freq="h")
    events = pd.DataFrame(
        {"time": [pd.Timestamp("2022-05-06T00:12:00Z")], "flow": [7.0]}
    )
    result = completion.aggregate_event_flows(
        events,
        timestamp_column="time",
        value_columns=["flow"],
        target=target,
        coverage_start=pd.Timestamp("2022-05-06T00:00:00Z"),
        coverage_end=pd.Timestamp("2022-05-06T02:00:00Z"),
    )
    assert np.isnan(result.loc["2022-05-05T23:00:00Z", "flow"])
    assert result.loc["2022-05-06T00:00:00Z", "flow"] == 7.0
    assert result.loc["2022-05-06T01:00:00Z", "flow"] == 0.0
    assert result.loc["2022-05-06T02:00:00Z", "flow"] == 0.0


def test_native_swap_hourly_aggregation_and_gross_issuance_formula(
    built: tuple[pd.DataFrame, dict[str, object]],
) -> None:
    frame, _ = built
    swaps = completion.build_native_swaps()
    assert np.allclose(
        swaps["gross_luna_issuance"], swaps["swap_amount"] + swaps["fee_amount"]
    )
    expected = swaps.set_index("timestamp").loc["2022-05-07T00:00:00Z":"2022-05-07T00:59:59Z"]
    row = frame.set_index("timestamp").loc["2022-05-07T00:00:00Z"]
    assert row["ust_native_redemption_volume"] == pytest.approx(expected["offer_amount"].sum())
    assert row["gross_luna_issuance_from_native_swaps"] == pytest.approx(
        (expected["swap_amount"] + expected["fee_amount"]).sum()
    )


def test_unit_scaling_and_partial_missingness(
    built: tuple[pd.DataFrame, dict[str, object]],
) -> None:
    frame, _ = built
    indexed = frame.set_index("timestamp")
    assert 1e9 < indexed.loc["2022-03-01T00:00:00Z", "ust_supply"] < 1e11
    assert 1e9 < indexed.loc["2022-03-01T00:00:00Z", "anchor_total_deposits"] < 1e11
    assert 0 < indexed.loc["2022-03-01T00:00:00Z", "top10_anchor_share"] < 1
    assert indexed.loc[:"2022-04-30T23:00:00Z", "luna_supply"].isna().all()
    assert indexed.loc[:"2022-05-05T23:00:00Z", "anchor_deposit_flow"].isna().all()
    assert indexed.loc[:"2022-05-06T23:00:00Z", "ust_native_redemption_volume"].isna().all()


def test_no_new_proxy_is_silently_created(
    built: tuple[pd.DataFrame, dict[str, object]],
) -> None:
    frame, _ = built
    forbidden = {
        "terra_dex_liquidity",
        "terra_dex_depth",
        "bridge_outflow_terra_to_ethereum",
        "bridge_inflow_ethereum_to_terra",
        "reserve_intervention_volume",
    }
    assert forbidden.isdisjoint(frame.columns)


def test_duplicate_detector_catches_known_bad_mapping() -> None:
    frame = pd.DataFrame(
        {
            "bridge_outflow": [1.0, 2.0, 3.0],
            "bridge_inflow": [1.0, 2.0, 3.0],
            "independent": [3.0, 1.0, 2.0],
        }
    )
    findings = completion.detect_duplicate_mappings(frame)
    pairs = {(item["left"], item["right"]) for item in findings}
    assert ("bridge_outflow", "bridge_inflow") in pairs
    assert ("bridge_outflow", "independent") not in pairs


def test_quality_labels_are_explicit_and_preserved() -> None:
    lineage = completion.source_lineage()
    assert lineage
    assert {item["quality"] for item in lineage} <= completion.QUALITY_CLASSES
    assert all(item["quality"] != "QUALITY_WARNING" for item in lineage)


def test_provenance_inputs_are_deterministic() -> None:
    first = json.dumps(completion.source_lineage(), sort_keys=True, ensure_ascii=False)
    second = json.dumps(completion.source_lineage(), sort_keys=True, ensure_ascii=False)
    assert first == second
    paths = completion._source_paths()
    assert completion.sha256_file(paths["native_swaps"]) == completion.sha256_file(paths["native_swaps"])
