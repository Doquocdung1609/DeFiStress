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
from sim.terra.calibration_v2 import TerraCalibrationV2, calibrate_v2
from sim.terra.datasets import CalibrationDatasetView
from sim.terra.early_warning import calculate_early_warning
from sim.terra.schemas import AgentEvent, ModelInputState, ModelRun, SimulationState

D = Decimal
TERRA_MODEL_VERSION = "2.1.0-terra-replay-v2"


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


def _decimal_default(
    parameters: dict[str, Any],
    name: str,
    default: Decimal,
) -> Decimal:
    return D(str(parameters[name])) if name in parameters else default


def _impact_beta(
    parameters: dict[str, Any],
    profile: TerraCalibrationV2,
) -> Decimal:
    if "price_impact_beta" in parameters:
        return max(D("0"), D(str(parameters["price_impact_beta"])))
    return max(D("0"), profile.price_impact_beta or D("0"))


def _execution_market_impact(
    sell_amount: Decimal,
    execution_depth: Decimal,
    beta: Decimal,
    cap: Decimal,
) -> Decimal:
    if sell_amount <= 0 or execution_depth <= 0 or beta <= 0:
        return D("0")
    pressure = max(D("0"), sell_amount / execution_depth)
    return min(max(D("0"), cap), beta * pressure.sqrt())


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
        self.profile = calibrate_v2(calibration)
        self.coefficients = {
            "intercept": self.profile.aggregate_exit_baseline,
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
        execution_capacity = max(initial.terra_dex_liquidity, D("1"))
        execution_depth = max(initial.terra_dex_depth, D("1"))
        shock = _decimal_default(parameters, "initial_withdrawal_shock_pct", self.profile.initial_shock_pct)
        beta = _impact_beta(parameters, self.profile)
        impact_cap = _decimal(parameters, "impact_cap", "0.10")
        utilization = D("0")
        states: list[SimulationState] = []

        for index, timestamp in enumerate(timestamps):
            depeg = max(D("0"), D("1") - state.ust_price)
            backing_stress = max(D("0"), D("1") - min(D("1"), state.backing_ratio))
            liquidity_stress = min(D("1"), max(D("0"), utilization))
            hazard = (
                self.coefficients["intercept"]
                + self.coefficients["depeg"] * depeg
                + self.coefficients["backing_stress"] * backing_stress
                + self.coefficients["liquidity_stress"] * liquidity_stress
                + self.coefficients["large_holder_intensity"] * initial.top10_anchor_share * shock
            )
            if index == 0:
                hazard += shock
            hazard = min(D("0.35"), max(D("0"), hazard))

            withdrawal = min(state.anchor_total_deposits, state.anchor_total_deposits * hazard)
            sell = withdrawal * D("0.50")
            utilization = sell / execution_capacity
            impact = _execution_market_impact(sell, execution_depth, beta, impact_cap)

            state.anchor_total_deposits -= withdrawal
            state.anchor_withdrawal_flow = withdrawal
            state.terra_dex_liquidity = initial.terra_dex_liquidity
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
            "AGGREGATE_DISCRETE_HAZARD_V2",
            {
                **parameters,
                "coefficients": coefficients,
                "calibrated_initial_shock_pct": float(shock),
                "price_impact_beta": float(beta),
            },
            {
                "warning": (
                    "Wallet event durations are unavailable; Cox PH was not fit. "
                    "Aggregate discrete hazard fallback used."
                ),
                "price_impact_identified_pre_cutoff": self.profile.price_impact_identified,
                "calibration": self.profile.diagnostics,
                "hazard_ratios": {
                    key: float(value.exp()) for key, value in self.coefficients.items() if key != "intercept"
                },
                "standard_errors": "UNAVAILABLE",
                "proportional_hazards_check": "NOT_APPLICABLE_TO_FALLBACK",
            },
        )


class SystemDynamicsModel:
    name = "SYSTEM_DYNAMICS"

    def __init__(self, calibration: CalibrationDatasetView):
        self.profile = calibrate_v2(calibration)

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
        redemption_fraction = _decimal(parameters, "arbitrage_capacity", "0.55")
        initial_shock = _decimal_default(
            parameters,
            "initial_withdrawal_shock_pct",
            self.profile.initial_shock_pct,
        )
        baseline = self.profile.aggregate_exit_baseline
        beta = _impact_beta(parameters, self.profile)
        impact_cap = _decimal(parameters, "impact_cap", "0.10")
        execution_capacity = max(initial.terra_dex_liquidity, D("1"))
        execution_depth = max(initial.terra_dex_depth, D("1"))
        hourly_redemption_capacity = _decimal_default(
            parameters,
            "arbitrage_hourly_capacity",
            execution_capacity,
        )
        utilization = D("0")
        states: list[SimulationState] = []

        for index, timestamp in enumerate(timestamps):
            depeg = max(D("0"), D("1") - state.ust_price)
            backing_stress = max(D("0"), D("1") - min(D("1"), state.backing_ratio))
            liquidity_stress = min(D("1"), max(D("0"), utilization))

            intensity = min(
                D("0.25"),
                baseline
                + (initial_shock if index == 0 else D("0"))
                + confidence * (depeg + backing_stress * D("0.25") + liquidity_stress * D("0.10")),
            )
            withdrawal = min(state.anchor_total_deposits, state.anchor_total_deposits * intensity)
            anchor_sell = withdrawal * D("0.60")

            outside_anchor_ust = max(D("0"), protocol.ust_supply - state.anchor_total_deposits)
            external_exit_intensity = min(
                D("0.25"),
                confidence * (depeg * D("0.32") + backing_stress * D("0.22") + liquidity_stress * D("0.16")),
            )
            external_sell = outside_anchor_ust * external_exit_intensity
            total_sell = anchor_sell + external_sell
            utilization = total_sell / execution_capacity

            arbitrage_edge = max(D("0"), D("1") - state.ust_price)
            redemption = D("0")
            if arbitrage_edge > _decimal(parameters, "redemption_friction", "0.02"):
                redemption = min(total_sell * redemption_fraction, hourly_redemption_capacity)

            minted = protocol.redeem(redemption, state.luna_price)
            impact = _execution_market_impact(total_sell, execution_depth, beta, impact_cap)
            supply_dilution = minted / max(protocol.luna_supply, D("1"))

            state.anchor_total_deposits -= withdrawal
            state.anchor_withdrawal_flow = withdrawal
            state.redemption_volume = redemption
            state.ust_supply = protocol.ust_supply
            state.luna_supply = protocol.luna_supply
            state.terra_dex_liquidity = initial.terra_dex_liquidity
            state.ust_price = max(D("0.01"), state.ust_price * (D("1") - impact))
            state.luna_price = max(
                D("0.0001"),
                state.luna_price * (D("1") - min(D("0.75"), supply_dilution * D("8") + impact)),
            )
            state.timestamp = timestamp
            state.backing_ratio = _updated_backing(state)
            state.risk_score = min(
                D("100"),
                (depeg + backing_stress + liquidity_stress + intensity) * D("90"),
            )
            state.collapse_signal = state.ust_price < D("0.90") and state.luna_supply > initial.luna_supply * D("2")
            states.append(replace(state))

        return ModelRun(
            self.name,
            TERRA_MODEL_VERSION,
            tuple(states),
            (),
            "CALIBRATED_PRE_CUTOFF_V2",
            {
                **parameters,
                "calibrated_exit_baseline": float(baseline),
                "calibrated_initial_shock_pct": float(initial_shock),
                "price_impact_beta": float(beta),
                "arbitrage_hourly_capacity": float(hourly_redemption_capacity),
            },
            {
                "price_impact_identified_pre_cutoff": self.profile.price_impact_identified,
                "calibration": self.profile.diagnostics,
            },
        )


class AgentBasedModel:
    name = "ABM"

    def __init__(self, calibration: CalibrationDatasetView):
        self.profile = calibrate_v2(calibration)

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

        execution_capacity = max(initial.terra_dex_liquidity, D("1"))
        execution_depth = max(initial.terra_dex_depth, D("1"))
        arbitrageur = ArbitrageurAgent(
            _decimal_default(parameters, "arbitrage_hourly_capacity", execution_capacity),
            _decimal(parameters, "minimum_arbitrage_profit", "1000"),
        )
        defender = ReserveDefenderAgent(
            _decimal(parameters, "reserve_capacity", "0"),
            _decimal(parameters, "reserve_threshold", "0.985"),
            _decimal(parameters, "reserve_efficiency", "0.65"),
        )

        confidence = _decimal(parameters, "confidence_sensitivity", "1.20")
        beta = _impact_beta(parameters, self.profile)
        impact_cap = _decimal(parameters, "impact_cap", "0.10")
        initial_shock = _decimal_default(
            parameters,
            "initial_withdrawal_shock_pct",
            self.profile.initial_shock_pct,
        )
        reaction_delay = int(parameters.get("reaction_delay_hours", 0))
        arbitrage_enabled = bool(parameters.get("arbitrage_enabled", True))
        liquidity_feedback = bool(parameters.get("liquidity_feedback", True))
        confidence_feedback = bool(parameters.get("confidence_feedback", True))
        whale_heterogeneity = bool(parameters.get("whale_heterogeneity", True))
        reserve_enabled = bool(parameters.get("reserve_intervention_enabled", False))

        calibrated = self.profile.cohort_baselines
        pooled_baseline = self.profile.aggregate_exit_baseline
        cohorts = (
            ("WHALE", D("0.23"), calibrated["WHALE"] if whale_heterogeneity else pooled_baseline),
            ("LARGE", D("0.28"), calibrated["LARGE"]),
            ("MEDIUM", D("0.31"), calibrated["MEDIUM"]),
            ("SMALL", D("0.18"), calibrated["SMALL"]),
        )

        states: list[SimulationState] = []
        events: list[AgentEvent] = []
        utilization = D("0")

        for index, timestamp in enumerate(timestamps):
            total_withdrawal = D("0")
            large_holder_flow = D("0")
            depeg = max(D("0"), D("1") - state.ust_price)
            backing_stress = max(D("0"), D("1") - min(D("1"), state.backing_ratio))
            liquidity_stress = min(D("1"), max(D("0"), utilization)) if liquidity_feedback else D("0")

            for cohort, share, baseline in cohorts:
                if index < reaction_delay and cohort != "WHALE":
                    probability, explanation = D("0"), {"reaction_delay": D("1")}
                else:
                    probability, explanation = depositor_exit_probability(
                        depeg if confidence_feedback else D("0"),
                        backing_stress if confidence_feedback else D("0"),
                        large_holder_flow,
                        liquidity_stress,
                        confidence,
                        baseline + (initial_shock if index == 0 else D("0")),
                    )

                stochastic = D(str(0.85 + rng.random() * 0.30))
                amount = min(
                    state.anchor_total_deposits * share,
                    state.anchor_total_deposits * share * probability * stochastic,
                )
                total_withdrawal += amount
                if cohort in {"WHALE", "LARGE"}:
                    large_holder_flow += amount / max(state.anchor_total_deposits, D("1"))
                if amount > 0:
                    events.append(
                        AgentEvent(
                            timestamp,
                            f"cohort-{cohort.lower()}",
                            cohort,
                            "WITHDRAW_AND_SELL",
                            amount,
                            explanation,
                        )
                    )

            total_withdrawal = min(state.anchor_total_deposits, total_withdrawal)
            anchor_sell = total_withdrawal * D("0.68")

            outside_anchor_ust = max(D("0"), protocol.ust_supply - state.anchor_total_deposits)
            external_probability, _ = depositor_exit_probability(
                depeg if confidence_feedback else D("0"),
                backing_stress if confidence_feedback else D("0"),
                large_holder_flow,
                liquidity_stress,
                confidence,
                D("0"),
            )
            external_sell = outside_anchor_ust * external_probability

            requested_sell = anchor_sell + external_sell
            reserve_support = (
                defender.intervene(state.ust_price, requested_sell * D("0.25")) if reserve_enabled else D("0")
            )
            net_sell = max(D("0"), requested_sell - reserve_support)
            utilization = net_sell / execution_capacity

            slippage_bps = min(D("5000"), net_sell / execution_depth * D("10000"))
            arb = (
                arbitrageur.evaluate(
                    state.ust_price,
                    net_sell * D("0.58"),
                    slippage_bps,
                )
                if arbitrage_enabled
                else None
            )
            redemption = arb.amount if arb and arb.execute else D("0")
            minted = protocol.redeem(redemption, state.luna_price)

            if arb and arb.execute:
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

            impact = _execution_market_impact(net_sell, execution_depth, beta, impact_cap)
            dilution = minted / max(protocol.luna_supply, D("1"))

            state.anchor_total_deposits -= total_withdrawal
            state.anchor_withdrawal_flow = total_withdrawal
            state.redemption_volume = redemption
            state.ust_supply = protocol.ust_supply
            state.luna_supply = protocol.luna_supply
            state.terra_dex_liquidity = initial.terra_dex_liquidity

            state.ust_price = min(
                D("1"),
                max(
                    D("0.005"),
                    state.ust_price * (D("1") - impact) + reserve_support / execution_capacity * D("0.1"),
                ),
            )
            state.luna_price = max(
                D("0.000001"),
                state.luna_price * (D("1") - min(D("0.82"), impact + dilution * D("10"))),
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
            "HETEROGENEOUS_COHORT_ABM_V2",
            {
                **parameters,
                "calibrated_exit_baseline": float(self.profile.aggregate_exit_baseline),
                "calibrated_initial_shock_pct": float(initial_shock),
                "cohort_baselines": {key: float(value) for key, value in self.profile.cohort_baselines.items()},
                "price_impact_beta": float(beta),
                "arbitrage_hourly_capacity": float(arbitrageur.hourly_capacity),
                "external_ust_share_at_cutoff": float(self.profile.external_ust_share),
            },
            {
                "agent_mode": "VECTORIZED_COHORTS",
                "configured_agents": int(parameters.get("agent_count", 10_000)),
                "price_impact_identified_pre_cutoff": self.profile.price_impact_identified,
                "price_impact_policy": self.profile.diagnostics["price_impact_policy"],
                "execution_capacity_semantics": (
                    "QUALITY_WARNING market execution-capacity proxy; not observed DEX reserve"
                ),
                "calibration": self.profile.diagnostics,
            },
        )


def build_model(name: str, calibration: CalibrationDatasetView) -> TerraModel:
    normalized = name.upper().replace("-", "_").replace(" ", "_")
    if normalized == "THRESHOLD":
        return ThresholdBaseline()
    if normalized in {"HAZARD", "COX", "DISCRETE_HAZARD"}:
        return DiscreteHazardModel(calibration)
    if normalized in {"SYSTEM_DYNAMICS", "SYSTEMDYNAMICS"}:
        return SystemDynamicsModel(calibration)
    if normalized in {"ABM", "AGENT_BASED_MODEL"}:
        return AgentBasedModel(calibration)
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
