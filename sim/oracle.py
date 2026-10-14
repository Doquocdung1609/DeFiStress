from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

D = Decimal


class OraclePolicyKind(StrEnum):
    ADVERSE_PASS_THROUGH = "A_ADVERSE_PASS_THROUGH"
    REFERENCE_ONLY = "B_REFERENCE_ONLY"
    LAGGED_SMOOTHED_PROXY = "C_LAGGED_SMOOTHED_PROXY"


@dataclass(frozen=True, slots=True)
class OraclePolicy:
    """Borrower-valuation policy for isolated sensitivity experiments.

    The default preserves the historical engine behavior. The lagged/smoothed
    policy is a hypothetical causal proxy and is not an implementation of an
    Aave or Chainlink oracle.
    """

    policy_id: str
    kind: OraclePolicyKind
    transmission_coefficient: Decimal = D("1")
    lag_steps: int = 1
    smoothing_window: int = 1

    def validate(self) -> None:
        if not D("0") <= self.transmission_coefficient <= D("1"):
            raise ValueError("transmission_coefficient must be between 0 and 1")
        if self.lag_steps < 1:
            raise ValueError("lag_steps must be at least 1")
        if self.smoothing_window < 1:
            raise ValueError("smoothing_window must be at least 1")

    def initial_valuation_price(self, reference_price: Decimal) -> Decimal:
        self.validate()
        return reference_price

    def next_valuation_price(
        self,
        reference_price: Decimal,
        completed_wave_dex_prices: list[Decimal],
    ) -> Decimal:
        """Return the valuation available after completed waves only.

        A lag of one uses observations through the immediately preceding
        completed wave. Larger lags exclude the newest completed observations.
        No in-progress or future-wave value can enter this calculation.
        """

        self.validate()
        if self.kind == OraclePolicyKind.ADVERSE_PASS_THROUGH:
            return min(reference_price, completed_wave_dex_prices[-1])
        if self.kind == OraclePolicyKind.REFERENCE_ONLY:
            return reference_price
        end = len(completed_wave_dex_prices) - (self.lag_steps - 1)
        if end <= 0:
            return reference_price
        start = max(0, end - self.smoothing_window)
        observations = completed_wave_dex_prices[start:end]
        if not observations:
            return reference_price
        smoothed = sum(observations, D(0)) / D(len(observations))
        proxy = reference_price + self.transmission_coefficient * (smoothed - reference_price)
        return min(reference_price, proxy)

    def intrawave_reporting_price(
        self,
        reference_price: Decimal,
        current_dex_price: Decimal,
        current_valuation_price: Decimal,
    ) -> Decimal:
        if self.kind == OraclePolicyKind.ADVERSE_PASS_THROUGH:
            return min(reference_price, current_dex_price)
        if self.kind == OraclePolicyKind.REFERENCE_ONLY:
            return reference_price
        return current_valuation_price


ADVERSE_PASS_THROUGH = OraclePolicy(
    policy_id="A_ADVERSE_PASS_THROUGH",
    kind=OraclePolicyKind.ADVERSE_PASS_THROUGH,
)
REFERENCE_ONLY = OraclePolicy(
    policy_id="B_REFERENCE_ONLY",
    kind=OraclePolicyKind.REFERENCE_ONLY,
)


def lagged_smoothed_proxy(
    *,
    policy_id: str,
    transmission_coefficient: Decimal,
    lag_steps: int,
    smoothing_window: int,
) -> OraclePolicy:
    policy = OraclePolicy(
        policy_id=policy_id,
        kind=OraclePolicyKind.LAGGED_SMOOTHED_PROXY,
        transmission_coefficient=transmission_coefficient,
        lag_steps=lag_steps,
        smoothing_window=smoothing_window,
    )
    policy.validate()
    return policy
