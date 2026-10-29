"""Independent synthetic controls for PR55; no saved historical valuation."""

from __future__ import annotations

import dataclasses

import pytest

from defistress_v2.contracts import BlockRef, Ok, QuantityKind
from defistress_v2.contracts.errors import ContractError
from defistress_v2.contracts.valuation import PriceSlot, ValuationPurpose
from defistress_v2.valuation import (
    RationalPrice,
    advance_policy,
    policy_a,
    policy_b,
    policy_c_weak,
    reporting_price,
    validate_price_observation,
    value_portfolio,
)
from tests.v2.test_valuation import (
    FIXTURE,
    USD8,
    USDC,
    WETH,
    amount,
    context,
    dex,
    policy_state,
    portfolio,
    position,
    price,
    price_set,
    rational_price,
    unwrap,
)


def test_ir01_price_slot_rejects_conflicting_decimals() -> None:
    wrong = dataclasses.replace(USDC, decimals=18)
    with pytest.raises(ContractError):
        PriceSlot(wrong, price(USDC, USD8.scale))


def test_ir01_reserve_amount_rejects_conflicting_decimals() -> None:
    wrong = dataclasses.replace(USDC, decimals=18)
    with pytest.raises(ContractError):
        dataclasses.replace(position(USDC), variable_debt=amount(wrong, 10**6, QuantityKind.DEBT))


def test_ir01_portfolio_price_join_rejects_conflicting_decimals() -> None:
    wrong = dataclasses.replace(USDC, decimals=18)
    result = value_portfolio(portfolio(position(wrong, debt=10**6)), price_set(price(USDC, USD8.scale)), context())
    assert not isinstance(result, Ok), "same token address with decimals18 versus6 must not be valued"


def test_ir01_policy_price_join_rejects_conflicting_decimals() -> None:
    wrong = dataclasses.replace(WETH, decimals=6)
    ref = RationalPrice.from_int(wrong, USD8, 100)
    result = advance_policy(policy_state(policy_b()), ref, (), checkpoint_id="next", decision_at_s=20)
    assert not isinstance(result, Ok)


@pytest.mark.parametrize("kind", ["future_block", "future_canonicality"])
def test_ir02_future_block_evidence_rejected(kind: str) -> None:
    block = BlockRef(1, 10, "0x" + "ab" * 32, 200 if kind == "future_block" else 90, "fixture", 201)
    evidence = dataclasses.replace(FIXTURE, block_ref=block, retrieved_at_s=201)
    observed = price(WETH, 100, block_ref=block, evidence=evidence)
    assert not isinstance(validate_price_observation(observed, 100), Ok)


def test_ir02_same_hash_conflicting_block_timestamps_rejected() -> None:
    a = BlockRef(1, 10, "0x" + "cd" * 32, 80, "fixture", 90)
    b = dataclasses.replace(a, timestamp_s=81)
    p = price(WETH, 100, block_ref=a, evidence=dataclasses.replace(FIXTURE, block_ref=a, retrieved_at_s=90))
    q = price(USDC, 100, block_ref=b, evidence=dataclasses.replace(FIXTURE, block_ref=b, retrieved_at_s=90))
    with pytest.raises(ContractError):
        price_set(p, q)


def test_ir02_policy_advance_cannot_precede_parent_checkpoint() -> None:
    result = advance_policy(policy_state(policy_b()), rational_price(100), (), checkpoint_id="next", decision_at_s=19)
    assert not isinstance(result, Ok)


def test_ir03_new_policy_history_must_enter_eligibility_hash() -> None:
    state = policy_state(policy_c_weak())
    a = unwrap(
        advance_policy(
            state, rational_price(100), (dex(0, 100), dex(1, 80), dex(2, 60)), checkpoint_id="next", decision_at_s=20
        )
    )
    b = unwrap(
        advance_policy(
            state, rational_price(100), (dex(0, 100), dex(1, 70), dex(2, 70)), checkpoint_id="next", decision_at_s=20
        )
    )
    assert a.valuation_price == b.valuation_price
    assert a.state.content_hash != b.state.content_hash
    assert a.state.eligibility_context_hash != b.state.eligibility_context_hash


def test_ir03_decision_time_must_enter_eligibility_hash() -> None:
    state = policy_state(policy_b())
    a = unwrap(advance_policy(state, rational_price(100), (), checkpoint_id="next", decision_at_s=20))
    b = unwrap(advance_policy(state, rational_price(100), (), checkpoint_id="next", decision_at_s=21))
    assert a.state.eligibility_context_hash != b.state.eligibility_context_hash


def test_ir03_reporting_output_retains_selected_evidence_lineage() -> None:
    state = policy_state(policy_a())
    a = dex(0, 70)
    b = dataclasses.replace(a, evidence=dataclasses.replace(a.evidence, locator="/different-selected-input"))
    x = unwrap(reporting_price(state, rational_price(100), a, reporting_at_s=20))
    y = unwrap(reporting_price(state, rational_price(100), b, reporting_at_s=20))
    assert x.eligibility_context_hash == y.eligibility_context_hash
    assert x.to_canonical() != y.to_canonical(), "reporting lineage is distinct from frozen eligibility lineage"


def test_ir04_freshness_flag_requires_exact_bool() -> None:
    with pytest.raises(ContractError):
        validate_price_observation(price(WETH, 100), 100, require_native_freshness="false")  # type: ignore[arg-type]


def test_ir04_result_origin_requires_enum() -> None:
    result = unwrap(value_portfolio(portfolio(position(WETH, debt=1)), price_set(price(WETH, 100)), context()))
    with pytest.raises(ContractError):
        dataclasses.replace(result, origin="SYNTHETIC")


def test_ir_control_reporting_and_eligibility_context_hashes_differ() -> None:
    positions = portfolio(position(WETH, debt=1))
    prices = price_set(price(WETH, 100))
    eligibility = unwrap(value_portfolio(positions, prices, context()))
    reporting = unwrap(value_portfolio(positions, prices, context(purpose=ValuationPurpose.REPORTING_AFTER_TRADE)))
    assert eligibility.context_hash != reporting.context_hash
    assert eligibility.health_factor_wad == reporting.health_factor_wad


def test_ir_control_stable_and_variable_debt_both_participate() -> None:
    row = dataclasses.replace(position(USDC, debt=3 * 10**6), stable_debt=amount(USDC, 2 * 10**6, QuantityKind.DEBT))
    result = unwrap(value_portfolio(portfolio(row), price_set(price(USDC, USD8.scale)), context()))
    assert result.total_debt_base_raw == str(5 * USD8.scale)


def test_ir_control_nonparticipating_extra_asset_is_blocked() -> None:
    result = value_portfolio(
        portfolio(position(WETH, debt=1)), price_set(price(WETH, 100), price(USDC, 100)), context()
    )
    assert not isinstance(result, Ok)


def test_ir_control_multi_collateral_effective_lt_profile() -> None:
    collateral = position(WETH, supplied=10**18, enabled=True, lt=8000)
    stablecoin = dataclasses.replace(
        position(USDC, supplied=1000 * 10**6, debt=400 * 10**6, enabled=True, lt=9000),
        stable_debt=amount(USDC, 100 * 10**6, QuantityKind.DEBT),
    )
    prices = price_set(price(WETH, 2000 * USD8.scale), price(USDC, USD8.scale))
    base = unwrap(value_portfolio(portfolio(collateral, stablecoin), prices, context()))
    resolved = dataclasses.replace(collateral, effective_lt_bps=9000)
    declared = dataclasses.replace(
        context(), assumptions=("SYNTHETIC resolved effective LT9000; no historical/native eMode inference",)
    )
    toy = unwrap(value_portfolio(portfolio(resolved, stablecoin), prices, declared))
    assert base.health_factor_wad == "5000000000000000000"
    assert toy.health_factor_wad == "5400000000000000000"
