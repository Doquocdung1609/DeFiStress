from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sim.terra.datasets import CalibrationDatasetView

D = Decimal

COHORT_SHARES = {
    "WHALE": D("0.23"),
    "LARGE": D("0.28"),
    "MEDIUM": D("0.31"),
    "SMALL": D("0.18"),
}

RELATIVE_BASELINES = {
    "WHALE": D("0.055"),
    "LARGE": D("0.022"),
    "MEDIUM": D("0.010"),
    "SMALL": D("0.005"),
}


@dataclass(frozen=True, slots=True)
class TerraCalibrationV2:
    aggregate_exit_baseline: Decimal
    initial_shock_pct: Decimal
    cohort_baselines: dict[str, Decimal]
    execution_capacity: Decimal
    execution_depth: Decimal
    external_ust_share: Decimal
    price_impact_beta: Decimal | None
    price_impact_identified: bool
    diagnostics: dict[str, Any]


def _quantile(values: list[Decimal], q: Decimal) -> Decimal:
    if not values:
        return D("0")
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    position = D(len(xs) - 1) * q
    lo = int(position)
    hi = min(lo + 1, len(xs) - 1)
    fraction = position - D(lo)
    return xs[lo] + (xs[hi] - xs[lo]) * fraction


def calibrate_v2(calibration: CalibrationDatasetView) -> TerraCalibrationV2:
    rows = calibration.observations
    if not rows:
        raise ValueError("calibration dataset is empty")

    effective_rates: list[Decimal] = []
    sell_impact_betas: list[Decimal] = []

    previous = None
    for row in rows:
        withdrawal_rate = row.anchor_withdrawal_flow / max(row.anchor_total_deposits, D("1"))
        deposit_drop_rate = D("0")
        if previous is not None and previous.anchor_total_deposits > 0:
            deposit_drop_rate = max(
                D("0"),
                D("1") - row.anchor_total_deposits / previous.anchor_total_deposits,
            )
        effective_rates.append(max(D("0"), withdrawal_rate, deposit_drop_rate))

        if previous is not None and previous.ust_price > 0 and row.ust_dex_sell_volume > 0:
            downside_return = max(D("0"), D("1") - row.ust_price / previous.ust_price)
            pressure = row.ust_dex_sell_volume / max(row.terra_dex_depth, D("1"))
            if downside_return > 0 and pressure > 0:
                sell_impact_betas.append(downside_return / pressure.sqrt())
        previous = row

    positive_rates = [x for x in effective_rates if x > 0]
    aggregate_exit_baseline = (
        _quantile(positive_rates, D("0.50"))
        if positive_rates
        else sum(effective_rates, D("0")) / D(max(1, len(effective_rates)))
    )
    q95 = _quantile(effective_rates, D("0.95"))
    initial_shock_pct = max(D("0"), q95 - aggregate_exit_baseline)

    weighted_v1 = sum(COHORT_SHARES[name] * RELATIVE_BASELINES[name] for name in COHORT_SHARES)
    scale = D("0") if weighted_v1 <= 0 else aggregate_exit_baseline / weighted_v1
    cohort_baselines = {name: RELATIVE_BASELINES[name] * scale for name in COHORT_SHARES}

    latest = rows[-1]
    external_ust_share = max(
        D("0"),
        D("1") - latest.anchor_total_deposits / max(latest.ust_supply, D("1")),
    )

    price_impact_identified = bool(sell_impact_betas)
    price_impact_beta = _quantile(sell_impact_betas, D("0.50")) if sell_impact_betas else None

    return TerraCalibrationV2(
        aggregate_exit_baseline=aggregate_exit_baseline,
        initial_shock_pct=initial_shock_pct,
        cohort_baselines=cohort_baselines,
        execution_capacity=max(latest.terra_dex_liquidity, D("1")),
        execution_depth=max(latest.terra_dex_depth, D("1")),
        external_ust_share=external_ust_share,
        price_impact_beta=price_impact_beta,
        price_impact_identified=price_impact_identified,
        diagnostics={
            "calibration_rows": len(rows),
            "cutoff_timestamp": calibration.cutoff_timestamp.isoformat(),
            "positive_exit_rate_rows": len(positive_rates),
            "price_impact_rows": len(sell_impact_betas),
            "price_impact_policy": (
                "PRE_CUTOFF_IDENTIFIED" if price_impact_identified else "UNIDENTIFIED_PRE_CUTOFF_DEFAULT_ZERO"
            ),
        },
    )
