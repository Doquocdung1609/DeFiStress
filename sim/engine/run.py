from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from uuid import uuid4

from sim.agents import Arbitrageur, Liquidator
from sim.dex import V3Pool
from sim.lending import plan_liquidation
from sim.metrics.risk import bad_debt, cascade_amplification, unliquidated_debt
from sim.schemas import BorrowerPosition, DexState, Scenario, SimulationEvent, SimulationResult, TimePoint

D = Decimal
MODEL_VERSION = "0.1.0-aave-v3.7-approx"


def run_simulation(
    positions: list[BorrowerPosition],
    dex_state: DexState,
    initial_reference_price: Decimal,
    scenario: Scenario,
    run_id: str | None = None,
) -> SimulationResult:
    scenario.validate()
    run_id = run_id or str(uuid4())
    borrowers = deepcopy(positions)
    pool = V3Pool(dex_state)
    pool.apply_liquidity_haircut(scenario.liquidity_haircut_pct)
    reference_price = initial_reference_price * (D(1) + scenario.shock_pct / D(100))
    # The exogenous market shock establishes the new pre-liquidation DEX/reference level.
    # Subsequent divergence is therefore endogenous forced-selling impact, not the shock itself.
    pool.arbitrage_toward(reference_price, D(100))
    valuation_price = reference_price
    bonus = scenario.liquidation_bonus_override or scenario.liquidation_bonus
    lt_override = scenario.liquidation_threshold_override
    liquidator = Liquidator(
        capital_limit=scenario.liquidator_capital_usdc,
        capacity_per_step=scenario.liquidator_capacity_usdc,
        minimum_profit=scenario.liquidator_min_profit_usdc,
        gas_multiplier=scenario.gas_multiplier,
    )
    arbitrageur = Arbitrageur(scenario.arbitrage_capacity_pct)
    events: list[SimulationEvent] = []
    timeseries: list[TimePoint] = []
    attempted: set[str] = set()

    initial_eligible = [p for p in borrowers if p.health_factor(reference_price, lt_override) < 1]
    liquidation_at_risk = sum((p.debt_value() for p in initial_eligible), D(0))
    initial_depth = pool.depth_to_price_drop_usdc(D("2"))
    timeseries.append(
        TimePoint(
            0,
            0,
            reference_price,
            pool.spot_price,
            len(initial_eligible),
            D(0),
            D(0),
            bad_debt(borrowers, valuation_price),
        )
    )

    total_liquidated = D(0)
    direct_liquidated = D(0)
    total_forced_weth = D(0)
    max_impact = abs(pool.spot_price - reference_price) / reference_price
    completed_waves = 0

    # Delay advances simulated time while retaining Wave 1 as the direct-shock cohort.
    for delay_step in range(1, min(scenario.liquidator_delay_steps, scenario.horizon_steps) + 1):
        timeseries.append(
            TimePoint(
                delay_step,
                0,
                reference_price,
                pool.spot_price,
                len(initial_eligible),
                D(0),
                D(0),
                bad_debt(borrowers, valuation_price),
            )
        )

    available_steps = max(0, scenario.horizon_steps - scenario.liquidator_delay_steps)
    for wave in range(1, min(scenario.max_waves, available_steps) + 1):
        step = scenario.liquidator_delay_steps + wave
        eligible = [
            p
            for p in borrowers
            if p.borrower_hash not in attempted and p.health_factor(valuation_price, lt_override) < 1
        ]
        if not eligible:
            break
        eligible.sort(key=lambda p: (p.health_factor(valuation_price, lt_override), -p.debt_value()))
        wave_liquidated = D(0)
        wave_forced = D(0)
        remaining_capacity = scenario.liquidator_capacity_usdc

        for position in eligible:
            hf_before = position.health_factor(valuation_price, lt_override)
            plan = plan_liquidation(position, valuation_price, bonus, lt_override)
            liquidator.capacity_per_step = remaining_capacity
            decision = liquidator.evaluate(plan, pool)
            if not decision.execute:
                if decision.reason != "CAPACITY_EXCEEDED":
                    attempted.add(position.borrower_hash)
                events.append(
                    SimulationEvent(
                        run_id=run_id,
                        step=step,
                        wave=wave,
                        event_type="LIQUIDATION_SKIPPED",
                        agent="liquidator-0",
                        borrower_hash=position.borrower_hash,
                        expected_profit=decision.expected_profit,
                        reference_price=reference_price,
                        health_factor_before=hf_before,
                        health_factor_after=hf_before,
                        timestamp_sim=step * scenario.timestep_seconds,
                        payload={"reason": decision.reason},
                    )
                )
                continue

            attempted.add(position.borrower_hash)
            quote = pool.sell_weth(plan.collateral_to_seize)
            position.debt_usdc = max(D(0), position.debt_usdc - plan.debt_to_repay)
            position.collateral_weth = max(D(0), position.collateral_weth - plan.collateral_to_seize)
            if position.debt_value() <= 0:
                position.status = "CLOSED"
            remaining_capacity -= plan.debt_to_repay
            liquidator.capital_limit = max(D(0), liquidator.capital_limit - plan.debt_to_repay)
            total_liquidated += plan.debt_to_repay
            wave_liquidated += plan.debt_to_repay
            total_forced_weth += plan.collateral_to_seize
            wave_forced += plan.collateral_to_seize
            if wave == 1:
                direct_liquidated += plan.debt_to_repay
            hf_after = position.health_factor(min(reference_price, pool.spot_price), lt_override)
            events.append(
                SimulationEvent(
                    run_id=run_id,
                    step=step,
                    wave=wave,
                    event_type="LIQUIDATION",
                    agent="liquidator-0",
                    borrower_hash=position.borrower_hash,
                    debt_asset="USDC",
                    collateral_asset="WETH",
                    debt_repaid=plan.debt_to_repay,
                    collateral_seized=plan.collateral_to_seize,
                    forced_sell_amount=plan.collateral_to_seize,
                    gas_cost=decision.gas_cost,
                    expected_profit=decision.expected_profit,
                    execution_price=quote.execution_price,
                    reference_price=reference_price,
                    slippage=quote.slippage,
                    dex_price_before=quote.price_before,
                    dex_price_after=quote.price_after,
                    health_factor_before=hf_before,
                    health_factor_after=hf_after,
                    timestamp_sim=step * scenario.timestep_seconds,
                    payload={"close_factor": float(plan.close_factor), "ticks_crossed": quote.ticks_crossed},
                )
            )

        arb = arbitrageur.act(pool, reference_price) if wave > scenario.arbitrage_delay_steps else None
        if arb is not None:
            arb_before, arb_after = arb
            events.append(
                SimulationEvent(
                    run_id=run_id,
                    step=step,
                    wave=wave,
                    event_type="ARBITRAGE",
                    agent="arbitrageur-0",
                    reference_price=reference_price,
                    dex_price_before=arb_before,
                    dex_price_after=arb_after,
                    timestamp_sim=step * scenario.timestep_seconds,
                    payload={"capacity_pct": float(scenario.arbitrage_capacity_pct)},
                )
            )

        valuation_price = min(reference_price, pool.spot_price)
        current_bad_debt = bad_debt(borrowers, valuation_price)
        remaining_eligible = sum(
            1
            for p in borrowers
            if p.borrower_hash not in attempted and p.health_factor(valuation_price, lt_override) < 1
        )
        timeseries.append(
            TimePoint(
                step,
                wave,
                reference_price,
                pool.spot_price,
                remaining_eligible,
                wave_liquidated,
                wave_forced,
                current_bad_debt,
            )
        )
        if wave_liquidated > 0:
            completed_waves = wave
        max_impact = max(max_impact, abs(pool.spot_price - reference_price) / reference_price)
        if wave_liquidated <= 0:
            break

    final_bad_debt = bad_debt(borrowers, valuation_price)
    spread = abs(pool.spot_price - reference_price) / reference_price
    elapsed_steps = scenario.liquidator_delay_steps + completed_waves
    recovery_time = elapsed_steps * scenario.timestep_seconds if spread <= D("0.005") else None
    metrics: dict[str, Decimal | int | None] = {
        "liquidation_at_risk": liquidation_at_risk,
        "total_liquidated_debt": total_liquidated,
        "direct_shock_liquidated_debt": direct_liquidated,
        "cascade_amplification": cascade_amplification(total_liquidated, direct_liquidated),
        "max_price_impact": max_impact,
        "bad_debt": final_bad_debt,
        "unliquidated_debt": unliquidated_debt(borrowers, valuation_price),
        "cascade_depth": completed_waves,
        "time_to_recovery_seconds": recovery_time,
        "liquidity_coverage_ratio_model": None
        if total_forced_weth <= 0
        else initial_depth / (total_forced_weth * initial_reference_price),
        "forced_weth_sold": total_forced_weth,
        "final_dex_price": pool.spot_price,
        "final_reference_price": reference_price,
    }
    return SimulationResult(run_id, MODEL_VERSION, scenario.seed, scenario, metrics, events, timeseries, borrowers)
