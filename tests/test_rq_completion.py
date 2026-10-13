from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from decimal import Decimal

import pytest

from sim.engine import run_simulation
from sim.fixtures import FIXTURE_PRICE, fixture_dex, fixture_positions, fixture_snapshot
from sim.lending import plan_liquidation
from sim.research.rq_completion import (
    CAPITAL_RATIOS,
    run_capital_constraint_sensitivity,
    run_ltv_capital_efficiency_analysis,
    run_reaction_delay_sensitivity,
)
from sim.schemas import BorrowerPosition, Scenario

D = Decimal


def test_usdc_price_one_is_backward_compatible_and_other_debt_is_not_repriced() -> None:
    positions = fixture_positions()
    legacy = run_simulation(positions, fixture_dex(), FIXTURE_PRICE, Scenario(), run_id="same").to_dict()
    explicit = run_simulation(
        positions,
        fixture_dex(),
        FIXTURE_PRICE,
        replace(Scenario(), usdc_price_usd=D("1.0")),
        run_id="same",
    ).to_dict()

    assert legacy == explicit
    position = BorrowerPosition("borrower", D("1"), D("100"), D("0.8"), other_debt_usd=D("50"))
    assert position.debt_value(D("1.1")) == D("160")
    assert position.debt_value(D("0.9")) == D("140")


def test_usdc_debt_valuation_has_directionally_correct_health_factor() -> None:
    position = BorrowerPosition("borrower", D("1"), D("1000"), D("0.8"), other_debt_usd=D("200"))
    baseline = position.health_factor(D("1600"), usdc_price_usd=D("1"))

    assert position.health_factor(D("1600"), usdc_price_usd=D("1.1")) < baseline
    assert position.health_factor(D("1600"), usdc_price_usd=D("0.9")) > baseline


def test_delay_preserves_initial_state_and_cannot_execute_early() -> None:
    positions = fixture_positions()
    before = deepcopy(positions)
    scenario = replace(Scenario(), liquidator_delay_steps=2)
    result = run_simulation(positions, fixture_dex(), FIXTURE_PRICE, scenario)

    assert positions == before
    assert all(event.step >= 3 for event in result.events if event.event_type == "LIQUIDATION")
    with pytest.raises(ValueError, match="delays cannot be negative"):
        replace(Scenario(), liquidator_delay_steps=-1).validate()


def test_delay_zero_preserves_professor_result() -> None:
    base = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario(), run_id="base")
    study = run_reaction_delay_sensitivity(fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario())
    zero = study["rows"][0]

    assert zero["total_liquidated_debt"] == float(base.metrics["total_liquidated_debt"])
    assert zero["bad_debt"] == float(base.metrics["bad_debt"])


def test_capital_levels_derive_from_reference_and_never_overspend() -> None:
    study = run_capital_constraint_sensitivity(
        fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario()
    )
    reference = D(str(study["required_capital_reference_usdc"]))

    assert [D(str(row["capital_ratio"])) for row in study["rows"]] == list(CAPITAL_RATIOS)
    for row, ratio in zip(study["rows"], CAPITAL_RATIOS, strict=True):
        assert float(row["capital_usdc"]) == pytest.approx(float(reference * ratio))
        assert row["capital_spent_within_limit"] is True
    assert study["rows"][-1]["total_liquidated_debt"] == study["unconstrained_reference"][
        "total_liquidated_debt"
    ]


def test_liquidation_threshold_override_does_not_reweight_other_collateral() -> None:
    position = BorrowerPosition(
        "borrower",
        D("1"),
        D("2000"),
        D("0.75"),
        other_collateral_usd=D("1000"),
    )

    assert position.health_factor(D("1000"), D("0.9")) == D("0.825")


def test_liquidation_bonus_reaches_seizure_and_profit_economics() -> None:
    position = BorrowerPosition("borrower", D("3"), D("10000"), D("0.8"))
    lower = plan_liquidation(position, D("4000"), D("1.03"))
    higher = plan_liquidation(position, D("4000"), D("1.07"))

    assert higher.collateral_to_seize > lower.collateral_to_seize


def test_ltv_analysis_does_not_mutate_debt_or_label_above_capacity_liquidatable() -> None:
    positions = fixture_positions()
    debts_before = [position.debt_usdc for position in positions]
    study = run_ltv_capital_efficiency_analysis(
        positions,
        FIXTURE_PRICE,
        fixture_snapshot(),
    )

    assert [position.debt_usdc for position in positions] == debts_before
    assert all(row["liquidatable_interpretation"] == "NOT_INFERRED_FROM_LTV" for row in study["rows"])
