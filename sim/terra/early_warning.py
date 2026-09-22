from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sim.terra.datasets import CalibrationDatasetView

D = Decimal


@dataclass(frozen=True, slots=True)
class EarlyWarningScore:
    score: Decimal
    contributions: dict[str, Decimal]
    calibration_policy: str

    def to_dict(self) -> dict[str, object]:
        return {
            "score": float(self.score),
            "contributions": {key: float(value) for key, value in self.contributions.items()},
            "calibration_policy": self.calibration_policy,
            "label": "Model-implied risk signal — not a price prediction",
        }


def calculate_early_warning(calibration: CalibrationDatasetView) -> EarlyWarningScore:
    latest = calibration.observations[-1]
    previous = calibration.observations[max(0, len(calibration.observations) - 25)]
    deposit_base = max(previous.anchor_total_deposits, D("1"))
    liquidity_base = max(previous.terra_dex_liquidity, D("1"))
    outflow_rate = latest.anchor_withdrawal_flow / max(latest.anchor_total_deposits, D("1"))
    liquidity_loss = max(D("0"), D("1") - latest.terra_dex_liquidity / liquidity_base)
    backing_stress = max(D("0"), D("1") - min(D("1"), latest.backing_ratio))
    whale_intensity = latest.top10_anchor_share * outflow_rate
    persistence = sum(1 for row in calibration.observations[-24:] if row.ust_price < D("0.995")) / 24
    contributions = {
        "depeg_persistence": min(D("25"), D(str(persistence)) * D("25")),
        "anchor_outflow": min(D("22"), outflow_rate * D("220")),
        "backing_deterioration": min(D("20"), backing_stress * D("20")),
        "liquidity_stress": min(D("18"), liquidity_loss * D("18")),
        "large_holder_withdrawals": min(D("15"), whale_intensity * D("150")),
    }
    # A decline in deposits is observable at T0 and may strengthen, but never reduce, the signal.
    deposit_loss = max(D("0"), D("1") - latest.anchor_total_deposits / deposit_base)
    contributions["anchor_outflow"] = min(D("22"), contributions["anchor_outflow"] + deposit_loss * D("10"))
    return EarlyWarningScore(
        min(D("100"), sum(contributions.values(), D("0"))),
        contributions,
        "Pre-specified weights version ew-1; all inputs are at or before the experiment cutoff.",
    )
