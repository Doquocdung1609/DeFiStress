from __future__ import annotations

from decimal import Decimal

from backend.app.services.snapshots import simulation_inputs
from scripts.research.run_oracle_transmission_diagnostic import _finite_delta, _finite_or_none
from sim.engine.run import run_simulation
from sim.oracle import ADVERSE_PASS_THROUGH, REFERENCE_ONLY, lagged_smoothed_proxy
from sim.research.aave_suite import load_canonical_snapshot
from sim.schemas import Scenario

D = Decimal


def test_default_policy_is_explicit_adverse_pass_through() -> None:
    positions, dex, price = simulation_inputs(load_canonical_snapshot())
    scenario = Scenario(
        name="oracle-default-regression",
        shock_pct=D("-40"),
        liquidity_haircut_pct=D("90"),
        max_waves=100,
        horizon_steps=120,
    )
    default = run_simulation(positions, dex, price, scenario, run_id="default")
    explicit = run_simulation(
        positions,
        dex,
        price,
        scenario,
        run_id="default",
        oracle_policy=ADVERSE_PASS_THROUGH,
    )
    assert default.to_dict() == explicit.to_dict()
    assert default.metrics["cascade_depth"] == 2


def test_reference_only_removes_dex_spot_from_later_wave_eligibility() -> None:
    positions, dex, price = simulation_inputs(load_canonical_snapshot())
    scenario = Scenario(
        name="oracle-reference-only",
        shock_pct=D("-40"),
        liquidity_haircut_pct=D("90"),
        max_waves=100,
        horizon_steps=120,
    )
    result = run_simulation(
        positions,
        dex,
        price,
        scenario,
        run_id="reference-only",
        oracle_policy=REFERENCE_ONLY,
    )
    assert result.metrics["cascade_depth"] == 1
    assert not any(event.wave >= 2 for event in result.events if event.event_type == "LIQUIDATION")


def test_lagged_proxy_is_causal_and_uses_only_completed_observations() -> None:
    policy = lagged_smoothed_proxy(
        policy_id="C_TEST",
        transmission_coefficient=D("0.5"),
        lag_steps=1,
        smoothing_window=2,
    )
    reference = D("100")
    history_after_wave1 = [D("100"), D("80")]
    assert policy.next_valuation_price(reference, history_after_wave1) == D("95")
    # A future wave price is invisible until it is appended by the caller.
    same_history = list(history_after_wave1)
    assert policy.next_valuation_price(reference, same_history) == D("95")
    assert policy.next_valuation_price(reference, [*same_history, D("60")]) == D("85")


def test_lagged_proxy_rejects_invalid_parameters() -> None:
    try:
        lagged_smoothed_proxy(
            policy_id="bad",
            transmission_coefficient=D("1.1"),
            lag_steps=1,
            smoothing_window=2,
        )
    except ValueError as exc:
        assert "transmission_coefficient" in str(exc)
    else:
        raise AssertionError("invalid transmission coefficient was accepted")


def test_debt_free_health_factor_is_serialized_without_non_finite_values() -> None:
    assert _finite_or_none(D("Infinity")) is None
    assert _finite_delta(None, None) is None
    assert _finite_delta(D("1.25"), D("1.00")) == D("0.25")
