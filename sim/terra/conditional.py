from __future__ import annotations

import math
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from decimal import Decimal
from random import Random
from statistics import median
from typing import Any

from sim.terra.datasets import ResearchDataset
from sim.terra.schemas import AgentEvent, TerraObservation

CONDITIONAL_MODEL_VERSION = "4.0.0-conditional-mechanism-replay"
TRIGGER_THRESHOLD = 0.99
MAIN_CALIBRATION_HOURS = 12
QUARANTINED_VARIABLES = (
    "ust_dex_sell_volume",
    "luna_minted_from_redemption",
    "luna_burned",
    "bridge_outflow_terra_to_ethereum",
    "bridge_inflow_ethereum_to_terra",
    "curve_ust_price",
    "curve_ust_liquidity",
    "curve_pool_imbalance",
)
PROXY_FIELDS = ("terra_dex_liquidity", "terra_dex_depth")
COHORT_SHARES = {"WHALE": 0.23, "LARGE": 0.28, "MEDIUM": 0.31, "SMALL": 0.18}
COHORT_MULTIPLIERS = {"WHALE": 2.4, "LARGE": 1.2, "MEDIUM": 0.7, "SMALL": 0.4}


def _positive_median(values: list[float], default: float = 0.0) -> float:
    positive = [value for value in values if math.isfinite(value) and value > 0]
    return median(positive) if positive else default


def _quantile(values: list[float], probability: float, default: float = 0.0) -> float:
    finite = sorted(value for value in values if math.isfinite(value))
    if not finite:
        return default
    position = (len(finite) - 1) * probability
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return finite[lower]
    weight = position - lower
    return finite[lower] * (1 - weight) + finite[upper] * weight


def _through_origin_beta(x_values: list[float], y_values: list[float]) -> float:
    pairs = [(x, y) for x, y in zip(x_values, y_values, strict=True) if x > 0 and y >= 0]
    denominator = sum(x * x for x, _ in pairs)
    return 0.0 if denominator <= 0 else max(0.0, sum(x * y for x, y in pairs) / denominator)


def _transform(name: str, value: float) -> float:
    safe = max(0.0, value)
    if name == "LINEAR_BOUNDED":
        return safe
    if name == "SQUARE_ROOT":
        return math.sqrt(safe)
    if name == "LOG_IMPACT":
        return math.log1p(safe)
    if name == "ELASTICITY":
        return safe / (1.0 + safe)
    raise ValueError(f"unknown impact form: {name}")


def _select_luna_impact_form(pressure: list[float], downside_returns: list[float]) -> tuple[str, float, dict[str, Any]]:
    candidates: dict[str, dict[str, float | int]] = {}
    for name in ("LINEAR_BOUNDED", "SQUARE_ROOT", "LOG_IMPACT", "ELASTICITY"):
        transformed = [_transform(name, value) for value in pressure]
        beta = _through_origin_beta(transformed, downside_returns)
        errors: list[float] = []
        for origin in range(4, len(transformed)):
            rolling_beta = _through_origin_beta(transformed[:origin], downside_returns[:origin])
            errors.append(downside_returns[origin] - rolling_beta * transformed[origin])
        rolling_rmse = math.sqrt(sum(item * item for item in errors) / len(errors)) if errors else math.inf
        fitted = [min(0.70, beta * value) for value in transformed]
        calibration_rmse = math.sqrt(
            sum((actual - predicted) ** 2 for actual, predicted in zip(downside_returns, fitted, strict=True))
            / max(1, len(fitted))
        )
        candidates[name] = {
            "beta": beta,
            "rolling_origin_rmse": rolling_rmse,
            "calibration_rmse": calibration_rmse,
            "observations": len(transformed),
        }
    selected = min(candidates, key=lambda name: (float(candidates[name]["rolling_origin_rmse"]), name))
    return selected, float(candidates[selected]["beta"]), {"candidates": candidates, "selection": selected}


@dataclass(frozen=True, slots=True)
class ConditionalParameters:
    anchor_exit_rate: float
    external_exit_rate: float
    arbitrage_hourly_capacity: float
    redemption_friction: float
    mint_efficiency: float
    ust_impact_beta: float
    luna_impact_beta: float
    luna_impact_form: str
    mint_to_market_fraction: float
    confidence_sensitivity: float
    execution_depth_proxy: float
    execution_capacity_proxy: float
    ust_impact_cap: float = 0.12
    luna_impact_cap: float = 0.70
    price_floor_ust: float = 0.005
    price_floor_luna: float = 0.00000001
    reserve_capacity: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConditionalCalibration:
    trigger_timestamp: datetime
    calibration_start: datetime
    calibration_end: datetime
    evaluation_start: datetime
    evaluation_end: datetime
    calibration_rows: int
    evaluation_rows: int
    initial_state: TerraObservation
    parameters: ConditionalParameters
    diagnostics: dict[str, Any]
    dataset_version: str
    dataset_status: str
    calibration_hours: int
    label: str = "CONDITIONAL_HISTORICAL_REPLAY"
    not_prediction: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "not_prediction": self.not_prediction,
            "trigger_rule": f"first ust_price < {TRIGGER_THRESHOLD}",
            "trigger_timestamp": self.trigger_timestamp.isoformat().replace("+00:00", "Z"),
            "calibration_start": self.calibration_start.isoformat().replace("+00:00", "Z"),
            "calibration_end_inclusive": self.calibration_end.isoformat().replace("+00:00", "Z"),
            "evaluation_start": self.evaluation_start.isoformat().replace("+00:00", "Z"),
            "evaluation_end": self.evaluation_end.isoformat().replace("+00:00", "Z"),
            "calibration_hours": self.calibration_hours,
            "calibration_rows": self.calibration_rows,
            "evaluation_rows": self.evaluation_rows,
            "dataset_version": self.dataset_version,
            "dataset_status": self.dataset_status,
            "quarantined_variables": list(QUARANTINED_VARIABLES),
            "proxy_fields": list(PROXY_FIELDS),
            "parameters": self.parameters.to_dict(),
            "initial_state": self.initial_state.to_dict(),
            "diagnostics": self.diagnostics,
        }


def calibrate_conditional(
    dataset: ResearchDataset,
    calibration_hours: int = MAIN_CALIBRATION_HOURS,
    trigger_threshold: float = TRIGGER_THRESHOLD,
) -> ConditionalCalibration:
    if calibration_hours < 4:
        raise ValueError("conditional calibration needs at least four hourly observations")
    rows = dataset.observations
    trigger_index = next((index for index, row in enumerate(rows) if float(row.ust_price) < trigger_threshold), None)
    if trigger_index is None:
        raise ValueError(f"no conditional trigger found below UST {trigger_threshold}")
    calibration_rows = rows[trigger_index : trigger_index + calibration_hours]
    if len(calibration_rows) != calibration_hours:
        raise ValueError("conditional calibration window is incomplete")
    evaluation_rows = rows[trigger_index + calibration_hours :]
    if not evaluation_rows:
        raise ValueError("conditional evaluation window is empty")

    withdrawals: list[float] = []
    external_exit_rates: list[float] = []
    gross_sell: list[float] = []
    redemptions: list[float] = []
    net_sell: list[float] = []
    downside_ust: list[float] = []
    gross_mint: list[float] = []
    supply_delta: list[float] = []
    downside_luna: list[float] = []
    previous = calibration_rows[0]
    for row in calibration_rows:
        deposit_stock = max(float(row.anchor_total_deposits), 1.0)
        withdrawal = max(0.0, float(row.anchor_withdrawal_flow))
        withdrawals.append(withdrawal / deposit_stock)
        previous_outside = max(0.0, float(previous.ust_supply - previous.anchor_total_deposits))
        current_outside = max(0.0, float(row.ust_supply - row.anchor_total_deposits))
        external_outflow = max(0.0, previous_outside - current_outside)
        external_exit_rates.append(external_outflow / max(previous_outside, 1.0))
        sell = withdrawal * 0.68 + external_outflow
        redemption = max(0.0, float(row.ust_native_redemption_volume))
        gross_sell.append(sell)
        redemptions.append(redemption)
        net_sell.append(max(0.0, sell - redemption))
        downside_ust.append(
            max(0.0, -math.log(max(float(row.ust_price), 1e-12) / max(float(previous.ust_price), 1e-12)))
        )
        implied_mint = redemption / max(float(row.luna_price), 1e-12)
        gross_mint.append(implied_mint)
        supply_delta.append(max(0.0, float(row.luna_supply - previous.luna_supply)))
        downside_luna.append(
            max(0.0, -math.log(max(float(row.luna_price), 1e-12) / max(float(previous.luna_price), 1e-12)))
        )
        previous = row

    execution_depth = max(float(calibration_rows[-1].terra_dex_depth), 1.0)
    ust_pressure = [math.sqrt(value / execution_depth) for value in net_sell]
    ust_beta_rows = [
        price_move / pressure
        for price_move, pressure in zip(downside_ust, ust_pressure, strict=True)
        if price_move > 0 and pressure > 0
    ]
    ust_beta = _positive_median(ust_beta_rows)
    efficiency_rows = [
        delta / mint for delta, mint in zip(supply_delta, gross_mint, strict=True) if delta > 0 and mint > 0
    ]
    mint_efficiency = min(1.0, _positive_median(efficiency_rows, 1.0))
    mint_to_market = 0.50
    mint_pressure = [
        mint_to_market * mint * mint_efficiency / max(float(row.luna_supply), 1.0)
        for mint, row in zip(gross_mint, calibration_rows, strict=True)
    ]
    impact_form, luna_beta, candidate_diagnostics = _select_luna_impact_form(mint_pressure, downside_luna)

    parameters = ConditionalParameters(
        anchor_exit_rate=_positive_median(withdrawals),
        external_exit_rate=_positive_median(external_exit_rates),
        arbitrage_hourly_capacity=_quantile(redemptions, 0.90),
        redemption_friction=0.02,
        mint_efficiency=mint_efficiency,
        ust_impact_beta=ust_beta,
        luna_impact_beta=luna_beta,
        luna_impact_form=impact_form,
        mint_to_market_fraction=mint_to_market,
        confidence_sensitivity=1.0,
        execution_depth_proxy=execution_depth,
        execution_capacity_proxy=max(float(calibration_rows[-1].terra_dex_liquidity), 1.0),
    )
    diagnostics = {
        "parameter_policy": "12h post-trigger calibration only; no May 8 10:00 onward observations were used",
        "ust_impact_driver": "net sell pressure = Anchor/external sell - arbitrage absorption",
        "redemption_role": "UST absorption and protocol LUNA issuance; not direct UST sell pressure",
        "mint_efficiency_rows": len(efficiency_rows),
        "ust_impact_beta_rows": len(ust_beta_rows),
        "luna_impact_candidate_selection": candidate_diagnostics,
        "mint_to_market_fraction_policy": "pre-specified 0.50; varied in sensitivity, not selected on holdout",
        "redemption_provenance": "PROVENANCE_SUPPORTED_WITH_EXTRACT_LIMITATION",
    }
    return ConditionalCalibration(
        trigger_timestamp=calibration_rows[0].timestamp,
        calibration_start=calibration_rows[0].timestamp,
        calibration_end=calibration_rows[-1].timestamp,
        evaluation_start=evaluation_rows[0].timestamp,
        evaluation_end=evaluation_rows[-1].timestamp,
        calibration_rows=len(calibration_rows),
        evaluation_rows=len(evaluation_rows),
        initial_state=calibration_rows[-1],
        parameters=parameters,
        diagnostics=diagnostics,
        dataset_version=dataset.manifest.dataset_version,
        dataset_status=dataset.manifest.status.value,
        calibration_hours=calibration_hours,
    )


@dataclass(frozen=True, slots=True)
class ConditionalState:
    timestamp: datetime
    ust_price: float
    luna_price: float
    ust_supply: float
    luna_supply: float
    anchor_total_deposits: float
    anchor_withdrawal_flow: float
    external_ust_sell: float
    gross_ust_sell: float
    arbitrage_absorption: float
    reserve_support: float
    net_ust_sell: float
    redemption_volume: float
    minted_luna: float
    backing_ratio: float
    confidence_stress: float
    execution_utilization: float
    ust_impact: float
    luna_impact: float
    collapse_signal: bool
    cap_flags: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp.isoformat().replace("+00:00", "Z")
        payload["cap_flags"] = list(self.cap_flags)
        return payload


@dataclass(frozen=True, slots=True)
class ConditionalRun:
    model_name: str
    model_version: str
    seed: int
    states: tuple[ConditionalState, ...]
    events: tuple[AgentEvent, ...]
    parameters: ConditionalParameters
    diagnostics: dict[str, Any]
    label: str = "CONDITIONAL_HISTORICAL_REPLAY"
    not_prediction: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "not_prediction": self.not_prediction,
            "model": self.model_name,
            "model_version": self.model_version,
            "seed": self.seed,
            "parameters": self.parameters.to_dict(),
            "diagnostics": self.diagnostics,
            "simulated_timeseries": [state.to_dict() for state in self.states],
            "agent_events": [event.to_dict() for event in self.events],
        }


class DepositorBehavior:
    def withdraw(
        self,
        deposits: float,
        base_rate: float,
        stress: float,
        rng: Random,
        heterogeneous: bool,
    ) -> tuple[float, list[tuple[str, float]]]:
        bounded_feedback = 1.0 + 2.0 * math.tanh(max(0.0, stress))
        multipliers = COHORT_MULTIPLIERS if heterogeneous else {name: 1.0 for name in COHORT_SHARES}
        normalization = sum(COHORT_SHARES[name] * multipliers[name] for name in COHORT_SHARES)
        withdrawals: list[tuple[str, float]] = []
        total = 0.0
        for cohort, share in COHORT_SHARES.items():
            rate = min(0.20, base_rate * multipliers[cohort] / max(normalization, 1e-12) * bounded_feedback)
            amount = min(deposits * share, deposits * share * rate * rng.uniform(0.85, 1.15))
            total += amount
            withdrawals.append((cohort, amount))
        return min(deposits, total), withdrawals


class ExternalHolderBehavior:
    def sell(self, outside_ust: float, base_rate: float, stress: float, enabled: bool) -> float:
        if not enabled:
            return 0.0
        rate = min(0.15, base_rate * (1.0 + 2.0 * math.tanh(max(0.0, stress))))
        return min(outside_ust, outside_ust * rate)


class ArbitrageThroughput:
    def absorb(
        self,
        gross_sell: float,
        ust_price: float,
        parameters: ConditionalParameters,
        enabled: bool,
        capacity_multiplier: float,
    ) -> float:
        if not enabled:
            return 0.0
        # Only the executable hourly tranche incurs immediate slippage. Applying the
        # whole gross queue here double-counts congestion and suppresses arbitrage.
        executable = min(gross_sell, parameters.arbitrage_hourly_capacity * max(0.0, capacity_multiplier))
        slippage = min(0.02, executable / max(parameters.execution_depth_proxy, 1.0) * 0.003)
        expected_edge = 1.0 - ust_price - parameters.redemption_friction - 0.0037 - slippage
        if expected_edge <= 0:
            return 0.0
        hourly_capacity = parameters.arbitrage_hourly_capacity * max(0.0, capacity_multiplier)
        return min(gross_sell, hourly_capacity)


class TerraProtocolMechanism:
    def redeem(
        self,
        ust_supply: float,
        luna_supply: float,
        redemption: float,
        luna_price: float,
        mint_efficiency: float,
    ) -> tuple[float, float, float]:
        accepted = min(max(0.0, redemption), ust_supply)
        minted = accepted / max(luna_price, 1e-12) * min(1.0, max(0.0, mint_efficiency))
        return max(0.0, ust_supply - accepted), luna_supply + minted, minted


class MarketImpact:
    def ust(self, net_sell: float, parameters: ConditionalParameters, depth_multiplier: float) -> tuple[float, bool]:
        pressure = net_sell / max(1.0, parameters.execution_depth_proxy * max(depth_multiplier, 1e-6))
        raw = parameters.ust_impact_beta * math.sqrt(max(0.0, pressure))
        return min(parameters.ust_impact_cap, raw), raw > parameters.ust_impact_cap

    def luna(self, minted: float, supply: float, parameters: ConditionalParameters) -> tuple[float, bool]:
        sell_pressure = parameters.mint_to_market_fraction * minted / max(supply, 1.0)
        raw = parameters.luna_impact_beta * _transform(parameters.luna_impact_form, sell_pressure)
        return min(parameters.luna_impact_cap, raw), raw > parameters.luna_impact_cap


class ConfidenceFeedback:
    def score(
        self,
        ust_price: float,
        backing_ratio: float,
        initial_backing: float,
        utilization: float,
        sensitivity: float,
        enabled: bool,
    ) -> float:
        if not enabled:
            return 0.0
        depeg = max(0.0, (TRIGGER_THRESHOLD - ust_price) / max(1e-6, 1.0 - TRIGGER_THRESHOLD))
        backing = max(0.0, 1.0 - backing_ratio / max(initial_backing, 1e-12))
        raw = sensitivity * (0.45 * depeg + 0.35 * backing + 0.20 * max(0.0, utilization))
        return math.tanh(max(0.0, raw))


class ConditionalABM:
    def __init__(self) -> None:
        self.depositors = DepositorBehavior()
        self.external_holders = ExternalHolderBehavior()
        self.arbitrage = ArbitrageThroughput()
        self.protocol = TerraProtocolMechanism()
        self.impact = MarketImpact()
        self.confidence = ConfidenceFeedback()

    def run(
        self,
        calibration: ConditionalCalibration,
        timestamps: tuple[datetime, ...],
        seed: int = 20220506,
        overrides: dict[str, Any] | None = None,
    ) -> ConditionalRun:
        if not timestamps or timestamps[0] != calibration.evaluation_start:
            raise ValueError("conditional evaluation must start immediately after the frozen calibration window")
        if any(timestamp < calibration.evaluation_start for timestamp in timestamps):
            raise ValueError("evaluation timestamps overlap conditional calibration")
        options = {
            "whale_heterogeneity": True,
            "arbitrage_enabled": True,
            "liquidity_feedback": True,
            "confidence_feedback": True,
            "external_holders_enabled": True,
            "reserve_intervention_enabled": False,
            "execution_depth_multiplier": 1.0,
            "execution_capacity_multiplier": 1.0,
        }
        options.update(overrides or {})
        parameter_overrides: dict[str, Any] = {
            key: value for key, value in options.items() if key in ConditionalParameters.__dataclass_fields__
        }
        parameters = replace(calibration.parameters, **parameter_overrides)
        rng = Random(seed)
        initial = calibration.initial_state
        ust_price = float(initial.ust_price)
        luna_price = float(initial.luna_price)
        ust_supply = float(initial.ust_supply)
        luna_supply = float(initial.luna_supply)
        deposits = float(initial.anchor_total_deposits)
        reserve_remaining = parameters.reserve_capacity
        initial_backing = luna_price * luna_supply / max(ust_supply, 1.0)
        previous_utilization = 0.0
        states: list[ConditionalState] = []
        events: list[AgentEvent] = []
        cap_counts: dict[str, int] = {}

        for timestamp in timestamps:
            backing = luna_price * luna_supply / max(ust_supply, 1.0)
            confidence_stress = self.confidence.score(
                ust_price,
                backing,
                initial_backing,
                previous_utilization if bool(options["liquidity_feedback"]) else 0.0,
                parameters.confidence_sensitivity,
                bool(options["confidence_feedback"]),
            )
            total_withdrawal, cohort_withdrawals = self.depositors.withdraw(
                deposits,
                parameters.anchor_exit_rate,
                confidence_stress,
                rng,
                bool(options["whale_heterogeneity"]),
            )
            for cohort, amount in cohort_withdrawals:
                if amount > 0:
                    events.append(
                        AgentEvent(
                            timestamp,
                            f"conditional-{cohort.lower()}",
                            cohort,
                            "WITHDRAW_AND_SELL",
                            _decimal(amount),
                            {"bounded_confidence_stress": _decimal(confidence_stress)},
                        )
                    )
            outside_ust = max(0.0, ust_supply - deposits)
            external_sell = self.external_holders.sell(
                outside_ust,
                parameters.external_exit_rate,
                confidence_stress,
                bool(options["external_holders_enabled"]),
            )
            anchor_sell = total_withdrawal * 0.68
            gross_sell = anchor_sell + external_sell
            reserve_support = 0.0
            if bool(options["reserve_intervention_enabled"]) and ust_price < 0.985:
                reserve_support = min(reserve_remaining, gross_sell * 0.25)
                reserve_remaining -= reserve_support
            after_reserve = max(0.0, gross_sell - reserve_support)
            absorption = self.arbitrage.absorb(
                after_reserve,
                ust_price,
                parameters,
                bool(options["arbitrage_enabled"]),
                float(options["execution_capacity_multiplier"]),
            )
            net_sell = max(0.0, after_reserve - absorption)
            ust_supply, luna_supply, minted = self.protocol.redeem(
                ust_supply,
                luna_supply,
                absorption,
                luna_price,
                parameters.mint_efficiency,
            )
            ust_impact, ust_capped = self.impact.ust(
                net_sell,
                parameters,
                float(options["execution_depth_multiplier"]),
            )
            luna_impact, luna_capped = self.impact.luna(minted, luna_supply, parameters)
            flags: list[str] = []
            if ust_capped:
                flags.append("UST_IMPACT_CAP")
            if luna_capped:
                flags.append("LUNA_IMPACT_CAP")
            deposits = max(0.0, deposits - total_withdrawal)
            ust_price = max(parameters.price_floor_ust, ust_price * math.exp(-ust_impact))
            luna_price = max(parameters.price_floor_luna, luna_price * math.exp(-luna_impact))
            backing = luna_price * luna_supply / max(ust_supply, 1.0)
            previous_utilization = gross_sell / max(parameters.execution_capacity_proxy, 1.0)
            collapse = ust_price < 0.90 and luna_supply > float(initial.luna_supply) * 2.0
            if ust_price == parameters.price_floor_ust:
                flags.append("UST_PRICE_FLOOR")
            if luna_price == parameters.price_floor_luna:
                flags.append("LUNA_PRICE_FLOOR")
            for flag in flags:
                cap_counts[flag] = cap_counts.get(flag, 0) + 1
            states.append(
                ConditionalState(
                    timestamp,
                    ust_price,
                    luna_price,
                    ust_supply,
                    luna_supply,
                    deposits,
                    total_withdrawal,
                    external_sell,
                    gross_sell,
                    absorption,
                    reserve_support,
                    net_sell,
                    absorption,
                    minted,
                    backing,
                    confidence_stress,
                    previous_utilization,
                    ust_impact,
                    luna_impact,
                    collapse,
                    tuple(flags),
                )
            )

        diagnostics = {
            "model_status": "POST_HOC_CONDITIONAL_MECHANISM_REPLAY_NOT_PREDICTION",
            "quarantined_variables_consumed": [],
            "proxy_fields": list(PROXY_FIELDS),
            "cap_counts": cap_counts,
            "component_modules": [
                "DepositorBehavior",
                "ExternalHolderBehavior",
                "ArbitrageThroughput",
                "TerraProtocolMechanism",
                "MarketImpact",
                "ConfidenceFeedback",
            ],
            "options": options,
        }
        return ConditionalRun(
            "CONDITIONAL_ABM_FINAL",
            CONDITIONAL_MODEL_VERSION,
            seed,
            tuple(states),
            tuple(events),
            parameters,
            diagnostics,
        )


def _decimal(value: float) -> Decimal:
    return Decimal(str(value))
