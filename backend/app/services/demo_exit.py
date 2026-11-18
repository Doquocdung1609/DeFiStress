"""Exact, illustrative exit arithmetic over user-declared assumptions."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal, localcontext
from typing import Any

from backend.app.schemas import ExitDemoRequest


def _string(value: Decimal) -> str:
    whole, _, fraction = format(value, "f").partition(".")
    fraction = fraction.rstrip("0")
    return f"{whole}.{fraction}" if fraction else whole


def run_exit_demo(request: ExitDemoRequest) -> dict[str, Any]:
    with localcontext() as context:
        context.prec = 80  # 28-digit inputs can multiply to 56 significant digits.
        return _calculate(request)


def _calculate(request: ExitDemoRequest) -> dict[str, Any]:
    quantity = Decimal(request.quantity_ust)
    price = Decimal(request.price_usd)
    warning_price = Decimal(request.warning_price_usd)
    capacity = None if request.capacity_ust is None else Decimal(request.capacity_ust)
    if capacity is None:
        execution_status = "NOT_VERIFIABLE"
        filled = None
        unfilled = None
        gross = None
        fee = None
        slippage = None
        net = None
    else:
        filled = min(quantity, capacity)
        unfilled = quantity - filled
        gross = filled * price
        fee = gross * Decimal(request.fee_percent) / 100
        slippage = gross * Decimal(request.slippage_percent) / 100
        net = gross - fee - slippage
        execution_status = "CAPACITY_ASSUMED_PARTIAL" if unfilled else "CAPACITY_ASSUMED_FULL"
    return {
        "status": "COMPLETE", "mode": "ILLUSTRATIVE_EXIT", "origin": "SYNTHETIC",
        "execution_status": execution_status, "source": "USER_DECLARED_ASSUMPTIONS",
        "assumptions": request.model_dump(mode="json"),
        "calculation": {
            "requested_ust": _string(quantity),
            "filled_ust": None if filled is None else _string(filled),
            "unfilled_ust": None if unfilled is None else _string(unfilled),
            "gross_usd": None if gross is None else _string(gross),
            "fee_usd": None if fee is None else _string(fee),
            "slippage_usd": None if slippage is None else _string(slippage),
            "net_usd": None if net is None else _string(net),
            "latency_minutes": request.latency_minutes,
            "warning_timestamp": request.warning_timestamp.isoformat().replace("+00:00", "Z"),
            "estimated_execution_time": (
                request.warning_timestamp + timedelta(minutes=request.latency_minutes)
            ).isoformat().replace("+00:00", "Z"),
            "warning_price_usd": _string(warning_price),
            "price_move_percent": _string((price / warning_price - 1) * 100),
            "modeled_loss_usd": None if net is None or filled is None else _string(filled * warning_price - net),
        },
        "scientific_status": "ILLUSTRATIVE_ONLY_NO_MARKET_DEPTH_OR_FILL_GUARANTEE",
    }
