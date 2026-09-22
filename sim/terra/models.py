from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from random import Random
from typing import Any, Protocol

from sim.terra.agents import (
    ArbitrageurAgent,
    ReserveDefenderAgent,
    TerraProtocolAgent,
    depositor_exit_probability,
)
from sim.terra.datasets import CalibrationDatasetView
from sim.terra.early_warning import calculate_early_warning
from sim.terra.schemas import AgentEvent, ModelInputState, ModelRun, SimulationState

D = Decimal
TERRA_MODEL_VERSION = "2.0.0-terra-replay"


class TerraModel(Protocol):
    name: str

    def run(
        self,
        initial: ModelInputState,
        timestamps: tuple[datetime, ...],
        parameters: dict[str, Any],
        seed: int,
    ) -> ModelRun: ...


def _decimal(parameters: dict[str, Any], name: str, default: str) -> Decimal:
    return D(str(parameters.get(name, default)))


def _initial_state(initial: ModelInputState) -> SimulationState:
    return SimulationState(
        timestamp=initial.timestamp,
        ust_price=initial.ust_price,
        luna_price=initial.luna_price,
        ust_supply=initial.ust_supply,
        luna_supply=initial.luna_supply,
        anchor_total_deposits=initial.anchor_total_deposits,
        anchor_withdrawal_flow=D("0"),
        redemption_volume=D("0"),
        terra_dex_liquidity=initial.terra_dex_liquidity,
        backing_ratio=initial.backing_ratio,
        risk_score=D("0"),
        collapse_signal=False,
    )


def _updated_backing(state: SimulationState) -> Decimal:
    if state.ust_supply <= 0:
        return D("0")
    return state.luna_price * state.luna_supply / state.ust_supply


class ThresholdBaseline:
    name = "THRESHOLD"

    def run(
        self,
        initial: ModelInputState,
        timestamps: tuple[datetime, ...],
        parameters: dict[str, Any],
        seed: int,
    ) -> ModelRun:
        del seed
        state = _initial_state(initial)
        depeg_threshold = _decimal(parameters, "depeg_threshold_bps", "50")
        backing_threshold = _decimal(parameters, "backing_ratio_threshold", "0.8")
        alert = (D("1") - initial.ust_price) * D("10000") > depeg_threshold or initial.backing_ratio < backing_threshold
        states: list[SimulationState] = []
        for timestamp in timestamps:
            if alert:
                state.ust_price = max(D("0.5"), state.ust_price - D("0.006"))
                state.luna_price = max(D("0.01"), state.luna_price * D("0.985"))
            state.timestamp = timestamp
            state.risk_score = D("80") if alert else D("10")
            state.collapse_signal = state.ust_price < D("0.90")
            state.backing_ratio = _updated_backing(state)
            states.append(replace(state))
        return ModelRun(
            self.name,
            TERRA_MODEL_VERSION,
            tuple(states),
            (),
            "PRE_SPECIFIED_THRESHOLDS",
            {"depeg_threshold_bps": float(depeg_threshold), "backing_ratio_threshold": float(backing_threshold)},
        )


class DiscreteHazardModel:
    name = "HAZARD"

    def __init__(self, calibration: CalibrationDatasetView):
        ratios = [
            row.anchor_withdrawal_flow / max(row.anchor_total_deposits, D("1")) for row in calibration.observations
        ]
        baseline = sum(ratios, D("0")) / D(len(ratios))
        self.coefficients = {
            "intercept": baseline,
            "depeg": D("2.2"),
            "backing_stress": D("0.35"),
            "liquidity_stress": D("0.45"),
            "large_holder_intensity": D("0.25"),
        }

    def run(
        self,
        initial: ModelInputState,
        timestamps: tuple[datetime, ...],
        parameters: dict[str, Any],
        seed: int,
    ) -> ModelRun:
        del seed
        state = _initial_state(initial)
        initial_liquidity = max(initial.terra_dex_liquidity, D("1"))
        shock = _decimal(parameters, "initial_withdrawal_shock_pct", "0.004")
        states: list[SimulationState] = []
        for index, timestamp in enumerate(timestamps):
            depeg = max(D("0"), D("1") - state.ust_price)
            backing_stress = max(D("0"), D("1") - min(D("1"), state.backing_ratio))
            liquidity_stress = max(D("0"), D("1") - state.terra_dex_liquidity / initial_liquidity)
            hazard = (
                self.coefficients["intercept"]
                + self.coefficients["depeg"] * depeg
                + self.coefficients["backing_stress"] * backing_stress
                + self.coefficients["liquidity_stress"] * liquidity_stress
                + self.coefficients["large_holder_intensity"] * initial.top10_anchor_share * shock
            )
            hazard = min(D("0.35"), max(D("0"), hazard + (shock if index == 0 else D("0"))))
            withdrawal = min(state.anchor_total_deposits, state.anchor_total_deposits * hazard)
            sell = withdrawal * D("0.50")
            impact = sell / max(state.terra_dex_liquidity, D("1")) * D("0.14")
            state.anchor_total_deposits -= withdrawal
            state.anchor_withdrawal_flow = withdrawal
            state.terra_dex_liquidity = max(D("1"), state.terra_dex_liquidity - sell * D("0.03"))
            state.ust_price = max(D("0.01"), state.ust_price * (D("1") - impact))
            state.luna_price = max(D("0.0001"), state.luna_price * (D("1") - impact * D("0.8")))
            state.timestamp = timestamp
            state.backing_ratio = _updated_backing(state)
            state.risk_score = min(D("100"), hazard * D("300"))
            state.collapse_signal = state.ust_price < D("0.90")
            states.append(replace(state))
        coefficients = {key: float(value) for key, value in self.coefficients.items()}
        return ModelRun(
            self.name,
            TERRA_MODEL_VERSION,
            tuple(states),
            (),
            "AGGREGATE_DISCRETE_HAZARD_FALLBACK",
            {**parameters, "coefficients": coefficients},
            {
                "warning": (
                    "Wallet event durations are unavailable; Cox PH was not fit. "
                    "Aggregate discrete hazard fallback used."
                ),
                "hazard_ratios": {
                    key: float(value.exp()) for key, value in self.coefficients.items() if key != "intercept"
                },
                "standard_errors": "UNAVAILABLE",
                "proportional_hazards_check": "NOT_APPLICABLE_TO_FALLBACK",
            },
        )


class SystemDynamicsModel:
    name = "SYSTEM_DYNAMICS"

    def run(
        self,
        initial: ModelInputState,
        timestamps: tuple[datetime, ...],
        parameters: dict[str, Any],
        seed: int,
    ) -> ModelRun:
        del seed
        state = _initial_state(initial)
        protocol = TerraProtocolAgent(
            state.ust_supply,
            state.luna_supply,
            _decimal(parameters, "redemption_friction", "0.02"),
        )
        confidence = _decimal(parameters, "confidence_sensitivity", "1.15")
        price_impact = _decimal(parameters, "price_impact_coefficient", "0.22")
        arbitrage_capacity = _decimal(parameters, "arbitrage_capacity", "0.55")
        initial_shock = _decimal(parameters, "initial_withdrawal_shock_pct", "0.012")
        states: list[SimulationState] = []
        for index, timestamp in enumerate(timestamps):
            depeg = max(D("0"), D("1") - state.ust_price)
            backing_stress = max(D("0"), D("1") - min(D("1"), state.backing_ratio))
            intensity = min(
                D("0.55"),
                initial_shock * (D("1") if index == 0 else D("0.12"))
                + confidence * (depeg + backing_stress * D("0.25")),
            )
            withdrawal = min(state.anchor_total_deposits, state.anchor_total_deposits * intensity)
            sell = withdrawal * D("0.60")
            redemption = sell * arbitrage_capacity
            minted = protocol.redeem(redemption, state.luna_price)
            liquidity_ratio = sell / max(state.terra_dex_liquidity, D("1"))
            ust_impact = min(D("0.45"), liquidity_ratio * price_impact + backing_stress * D("0.035"))
            supply_dilution = minted / max(protocol.luna_supply, D("1"))
            state.anchor_total_deposits -= withdrawal
            state.anchor_withdrawal_flow = withdrawal
            state.redemption_volume = redemption
            state.ust_supply = protocol.ust_supply
            state.luna_supply = protocol.luna_supply
            state.terra_dex_liquidity = max(D("1"), state.terra_dex_liquidity - sell * D("0.045"))
            state.ust_price = max(D("0.01"), state.ust_price * (D("1") - ust_impact))
            state.luna_price = max(
                D("0.0001"), state.luna_price * (D("1") - min(D("0.75"), supply_dilution * D("8") + ust_impact))
            )
            state.timestamp = timestamp
            state.backing_ratio = _updated_backing(state)
            state.risk_score = min(D("100"), (depeg + backing_stress + intensity) * D("90"))
            state.collapse_signal = state.ust_price < D("0.90") and state.luna_supply > initial.luna_supply * D("2")
            states.append(replace(state))
        return ModelRun(self.name, TERRA_MODEL_VERSION, tuple(states), (), "CALIBRATED_PRE_CUTOFF", parameters)


class AgentBasedModel:
    name = "ABM"

    def run(
        self,
        initial: ModelInputState,
        timestamps: tuple[datetime, ...],
        parameters: dict[str, Any],
        seed: int,
    ) -> ModelRun:
        rng = Random(seed)
        state = _initial_state(initial)
        protocol = TerraProtocolAgent(
            state.ust_supply,
            state.luna_supply,
            _decimal(parameters, "redemption_friction", "0.02"),
        )
        arbitrageur = ArbitrageurAgent(
            _decimal(parameters, "arbitrage_capital", "900000000"),
            _decimal(parameters, "minimum_arbitrage_profit", "1000"),
        )
        defender = ReserveDefenderAgent(
            _decimal(parameters, "reserve_capacity", "0"),
            _decimal(parameters, "reserve_threshold", "0.985"),
            _decimal(parameters, "reserve_efficiency", "0.65"),
        )
        confidence = _decimal(parameters, "confidence_sensitivity", "1.20")
        price_impact = _decimal(parameters, "price_impact_coefficient", "0.24")
        initial_shock = _decimal(parameters, "initial_withdrawal_shock_pct", "0.014")
        reaction_delay = int(parameters.get("reaction_delay_hours", 0))
        arbitrage_enabled = bool(parameters.get("arbitrage_enabled", True))
        liquidity_feedback = bool(parameters.get("liquidity_feedback", True))
        confidence_feedback = bool(parameters.get("confidence_feedback", True))
        whale_heterogeneity = bool(parameters.get("whale_heterogeneity", True))
        reserve_enabled = bool(parameters.get("reserve_intervention_enabled", False))
        cohorts = (
            ("WHALE", D("0.23"), D("0.055") if whale_heterogeneity else D("0.012")),
            ("LARGE", D("0.28"), D("0.022")),
            ("MEDIUM", D("0.31"), D("0.010")),
            ("SMALL", D("0.18"), D("0.005")),
        )
        states: list[SimulationState] = []
        events: list[AgentEvent] = []
        initial_liquidity = max(state.terra_dex_liquidity, D("1"))
        for index, timestamp in enumerate(timestamps):
            total_withdrawal = D("0")
            large_holder_flow = D("0")
            depeg = max(D("0"), D("1") - state.ust_price)
            backing_stress = max(D("0"), D("1") - min(D("1"), state.backing_ratio))
            liquidity_stress = max(D("0"), D("1") - state.terra_dex_liquidity / initial_liquidity)
            for cohort, share, baseline in cohorts:
                if index < reaction_delay and cohort != "WHALE":
                    probability, explanation = D("0"), {"reaction_delay": D("1")}
                else:
                    probability, explanation = depositor_exit_probability(
                        depeg if confidence_feedback else D("0"),
                        backing_stress if confidence_feedback else D("0"),
                        large_holder_flow,
                        liquidity_stress if liquidity_feedback else D("0"),
                        confidence,
                        baseline + (initial_shock if index == 0 else D("0")),
                    )
                stochastic = D(str(0.85 + rng.random() * 0.30))
                amount = min(
                    state.anchor_total_deposits * share, state.anchor_total_deposits * share * probability * stochastic
                )
                total_withdrawal += amount
                if cohort in {"WHALE", "LARGE"}:
                    large_holder_flow += amount / max(state.anchor_total_deposits, D("1"))
                if amount > 0:
                    events.append(
                        AgentEvent(
                            timestamp, f"cohort-{cohort.lower()}", cohort, "WITHDRAW_AND_SELL", amount, explanation
                        )
                    )
            total_withdrawal = min(state.anchor_total_deposits, total_withdrawal)
            sell = total_withdrawal * D("0.68")
            slippage_bps = min(D("5000"), sell / max(state.terra_dex_liquidity, D("1")) * D("10000"))
            arb = arbitrageur.evaluate(state.ust_price, sell * D("0.58"), slippage_bps) if arbitrage_enabled else None
            redemption = arb.amount if arb and arb.execute else D("0")
            minted = protocol.redeem(redemption, state.luna_price)
            if arb and arb.execute:
                arbitrageur.capital = max(D("0"), arbitrageur.capital - arb.amount * state.ust_price)
                events.append(
                    AgentEvent(
                        timestamp,
                        "arbitrageur-aggregate",
                        "ARBITRAGEUR",
                        "BUY_AND_REDEEM_UST",
                        redemption,
                        {"expected_profit": arb.expected_profit},
                    )
                )
            reserve_support = defender.intervene(state.ust_price, sell * D("0.25")) if reserve_enabled else D("0")
            net_sell = max(D("0"), sell - reserve_support)
            liquidity_ratio = net_sell / max(state.terra_dex_liquidity, D("1"))
            impact = min(D("0.60"), liquidity_ratio * price_impact + backing_stress * D("0.04"))
            dilution = minted / max(protocol.luna_supply, D("1"))
            state.anchor_total_deposits -= total_withdrawal
            state.anchor_withdrawal_flow = total_withdrawal
            state.redemption_volume = redemption
            state.ust_supply = protocol.ust_supply
            state.luna_supply = protocol.luna_supply
            if liquidity_feedback:
                state.terra_dex_liquidity = max(D("1"), state.terra_dex_liquidity - net_sell * D("0.055"))
            state.ust_price = min(
                D("1"),
                max(
                    D("0.005"),
                    state.ust_price * (D("1") - impact)
                    + reserve_support / max(state.terra_dex_liquidity, D("1")) * D("0.1"),
                ),
            )
            state.luna_price = max(
                D("0.000001"), state.luna_price * (D("1") - min(D("0.82"), impact + dilution * D("10")))
            )
            state.timestamp = timestamp
            state.backing_ratio = _updated_backing(state)
            state.risk_score = min(
                D("100"),
                (
                    depeg
                    + backing_stress
                    + liquidity_stress
                    + total_withdrawal / max(state.anchor_total_deposits, D("1"))
                )
                * D("75"),
            )
            state.collapse_signal = state.ust_price < D("0.90") and state.luna_supply > initial.luna_supply * D("2")
            states.append(replace(state))
        return ModelRun(
            self.name,
            TERRA_MODEL_VERSION,
            tuple(states),
            tuple(events),
            "HETEROGENEOUS_COHORT_ABM",
            parameters,
            {"agent_mode": "VECTORIZED_COHORTS", "configured_agents": int(parameters.get("agent_count", 10_000))},
        )


def build_model(name: str, calibration: CalibrationDatasetView) -> TerraModel:
    normalized = name.upper().replace("-", "_").replace(" ", "_")
    if normalized == "THRESHOLD":
        return ThresholdBaseline()
    if normalized in {"HAZARD", "COX", "DISCRETE_HAZARD"}:
        return DiscreteHazardModel(calibration)
    if normalized in {"SYSTEM_DYNAMICS", "SYSTEMDYNAMICS"}:
        return SystemDynamicsModel()
    if normalized in {"ABM", "AGENT_BASED_MODEL"}:
        return AgentBasedModel()
    raise ValueError(f"unknown Terra model: {name}")


def model_definitions(calibration: CalibrationDatasetView) -> dict[str, dict[str, Any]]:
    return {
        "THRESHOLD": {"purpose": "Pre-specified crisis alert rule", "calibration": "PRE_SPECIFIED"},
        "HAZARD": {
            "purpose": "Aggregate withdrawal hazard",
            "calibration": "PRE_CUTOFF",
            "fallback": "DISCRETE_HAZARD",
        },
        "SYSTEM_DYNAMICS": {"purpose": "Aggregate feedback benchmark", "calibration": "PRE_CUTOFF_OR_PRE_SPECIFIED"},
        "ABM": {"purpose": "Heterogeneous cohort mechanism model", "calibration": "PRE_CUTOFF_OR_PRE_SPECIFIED"},
    }


def early_warning_for(calibration: CalibrationDatasetView) -> dict[str, object]:
    return calculate_early_warning(calibration).to_dict()
